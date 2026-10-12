"""
Survey probe for the Global Fund's financial datasets — the evidence behind section 6's
queued decision on whether those datasets belong in the panel.

The panel's `global_fund` connector reads `AllProgrammaticIndicators` and `Geographies` and
nothing else. The same service lists 32 financial indicators over 16 datasets in the entity
`AllFinancialIndicators`, among them disbursements, commitments, grant budgets, expenditure
by intervention, allocations and pledges, and no connector reads any of them. That count of
32 over 16 came out of the IATI survey of 21 September 2026 as a list of names, so what the
datasets contain, whether any of them resolves to a country and a year, and whether any of
them separates HIV money from malaria and tuberculosis money are all unmeasured.

This probe measures those things and writes nothing outside its own output directory. It
does not touch `data/panel/`, it emits no PanelRow, and it is not a connector. Every
response it receives is saved raw, so the survey can be read back and designed against
offline without asking the service a second time.

Four questions decide whether a financial dataset can enter the panel at all, and the probe
is arranged around them.

  1. Does the dataset resolve to a country. A row keyed on a grant, a principal recipient
     or a donor is not a country-year row, and the four CSVs already sitting in
     data/raw/global_fund/ are all of that kind, so none of them could be used. The probe
     reports which geography fields each dataset carries and how many of the values resolve
     to a country through the connector's own `geographies()` map.

  2. Does the dataset resolve to a year. An amount covering a three-year grant period is
     not an annual figure, and splitting one across years is an assumption the panel does
     not get to make silently.

  3. Does the dataset separate HIV from the other two diseases. The Global Fund's component
     vocabulary includes "TB/HIV", and an amount on a combined grant cannot be attributed to
     HIV without a stated assumption. The probe reports the component distribution and the
     money sitting in each component, so the size of that problem is known before anything
     is built rather than after.

  4. Does the dataset repeat what the panel already holds. The Global Fund publishes to IATI
     as well, and the panel's 2,577 Global Fund country-years come from d-portal's reading of
     that IATI publication. A financial dataset that restates the same disbursements adds a
     second copy of one reading and not a second reading, which is the trap item 27 of
     RESUME.md records for the reconciliation layer. The probe pulls one named grant,
     NGA-H-NACA, where the service and IATI are already known to differ by 3.9 per cent for
     reasons nobody has established, and reports the service's own disbursement figures for
     that grant so the gap can be chased.

Three traps this service has already sprung on the panel, all of them handled here.

  * `$expand` returns HTTP 200 with an empty value array instead of an error, so a request
     that joins through a navigation property reads as a dataset with no data in it. The
     probe never uses `$expand` and joins on ids the way the connector does.

  * Retired API versions answer with an Azure Front Door page reading "The request is
     blocked." on an HTTP 403, including the bare root, so a wrong path reads as a source
     that has closed its door. The probe records the status and the opening bytes of every
     response rather than treating a failure as an absence.

  * A paged response is served with an `@odata.nextLink` and no warning. The probe reports
     the link wherever one appears, so nothing here is mistaken for a complete count.

Usage:
    python scripts/survey_global_fund_financials.py
    python scripts/survey_global_fund_financials.py --out /some/other/directory
    python scripts/survey_global_fund_financials.py --sample 500

Everything the probe receives lands in the output directory, by default
data/raw/global_fund/survey_<date>/, together with survey.json holding the whole report.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hivimpact.connectors.global_fund import GlobalFundConnector, _BASE  # noqa: E402

#: The grant the IATI survey of 21 September 2026 left with an unexplained 3.9 per cent gap
#: between the Global Fund's own data service and the Global Fund's IATI publication.
_GRANT = "NGA-H-NACA"

#: A four-digit run anywhere in a value, used to find a year in a date of any format.
_YEAR_RUN = re.compile(r"\d{4}")

#: Field names that could carry a dataset discriminator, a geography, a year, a component,
#: a currency or an amount. The probe looks for these as substrings, case insensitively, and
#: reports what it finds instead of assuming any particular one exists.
_LOOKS_LIKE = {
    "dataset": ("dataset",),
    "geography": ("geograph", "country", "recordid", "region", "location"),
    "year": ("year", "period", "date", "startdate", "enddate"),
    "component": ("component", "disease", "module", "intervention"),
    "currency": ("currency",),
    "amount": ("amount", "value", "budget", "disburs", "expend", "pledge", "contribut"),
    "grant": ("grant", "principalrecipient", "implement"),
}


def _classify(field_names: List[str]) -> Dict[str, List[str]]:
    """Group a dataset's field names under the six things the survey needs to find."""
    out: Dict[str, List[str]] = {k: [] for k in _LOOKS_LIKE}
    for name in field_names:
        low = name.lower().replace("_", "")
        for kind, needles in _LOOKS_LIKE.items():
            if any(n in low for n in needles):
                out[kind].append(name)
    return out


class Survey:
    def __init__(self, out_dir: pathlib.Path, sample: int) -> None:
        self.out = out_dir
        self.sample = sample
        self.conn = GlobalFundConnector()
        self.report: Dict[str, Any] = {
            "probed_at": dt.datetime.now().isoformat(timespec="seconds"),
            "base": _BASE,
            "sample_size": sample,
            "requests": [],
            "datasets": {},
            "notes": [],
        }

    # -- one request, recorded whatever happens --------------------------------
    def _get(self, label: str, path: str, save_as: Optional[str] = None) -> Optional[Any]:
        """GET one URL, save the body, and record the outcome. Returns parsed JSON or None.

        A failure is recorded and returned as None. Nothing here raises, because a survey
        that stops on the first refusal tells us less than a survey that reports the refusal
        and carries on to the next question.
        """
        url = f"{_BASE}/{path}"
        entry: Dict[str, Any] = {"label": label, "url": url}
        try:
            resp = self.conn._request("GET", url)
        except Exception as exc:  # noqa: BLE001 - a refusal is a finding, not a crash
            entry["outcome"] = "failed"
            entry["error"] = f"{type(exc).__name__}: {exc}"[:400]
            self.report["requests"].append(entry)
            print(f"  ! {label}: {entry['error']}")
            return None

        body = resp.content
        entry["status"] = resp.status_code
        entry["bytes"] = len(body)
        entry["content_type"] = resp.headers.get("Content-Type", "")
        entry["opening_bytes"] = body[:180].decode("utf-8", "replace")

        name = save_as or (label.replace(" ", "_").replace("/", "_") + ".json")
        (self.out / name).write_bytes(body)
        entry["saved_as"] = name

        if "json" not in entry["content_type"]:
            entry["outcome"] = "not json"
            self.report["requests"].append(entry)
            print(f"  . {label}: {entry['bytes']:,} bytes of {entry['content_type']} "
                  f"-> {name}")
            return None

        payload = resp.json()
        entry["outcome"] = "ok"
        if isinstance(payload, dict):
            entry["odata_count"] = payload.get("@odata.count")
            entry["next_link"] = payload.get("@odata.nextLink")
            entry["rows_returned"] = len(payload.get("value") or [])
        self.report["requests"].append(entry)
        print(f"  ok {label}: {entry.get('rows_returned', 0):,} rows, "
              f"{entry['bytes']:,} bytes"
              + (f", count={entry['odata_count']:,}" if entry.get("odata_count") else "")
              + (", PAGED" if entry.get("next_link") else "")
              + f" -> {name}")
        return payload

    # -- question zero, what the service says it holds -------------------------
    def service_map(self) -> None:
        """The entity list and the property-level metadata, which is the cheapest map."""
        print("\n== what the service says it holds")
        self._get("service root", "?$format=json", "service_root.json")
        self._get("metadata", "$metadata", "metadata.xml")

    # -- questions one to three, per financial dataset -------------------------
    def financial_datasets(self) -> List[str]:
        """Name every financial dataset and count the rows in each one."""
        print("\n== the financial datasets")
        counted = self._get("financial indicators count",
                            "AllFinancialIndicators?$count=true&$top=0",
                            "financial_count.json")
        total = counted.get("@odata.count") if isinstance(counted, dict) else None
        self.report["financial_total_rows"] = total

        sample = self._get("financial indicators sample",
                           f"AllFinancialIndicators?$top={self.sample}",
                           "financial_sample.json")
        rows = (sample or {}).get("value") or []
        if not rows:
            self.report["notes"].append(
                "AllFinancialIndicators returned no rows, so either the entity name has "
                "changed or the service refused the request. Read the saved response.")
            print("  ! no rows came back, nothing below can be measured")
            return []

        fields = sorted({k for r in rows for k in r.keys()})
        kinds = _classify(fields)
        self.report["financial_fields"] = fields
        self.report["financial_field_kinds"] = kinds
        print(f"  {len(fields)} fields on the sample rows")
        for kind, found in kinds.items():
            print(f"    {kind:10s} {', '.join(found) or 'nothing that looks like it'}")

        # The dataset discriminator, whatever the service calls it.
        disc = kinds["dataset"][0] if kinds["dataset"] else None
        self.report["dataset_field"] = disc
        if not disc:
            self.report["notes"].append(
                "No field name on AllFinancialIndicators looks like a dataset "
                "discriminator, so the 16 datasets are named somewhere else. Read "
                "metadata.xml and financial_sample.json.")
            print("  ! no dataset field found, read metadata.xml")
            return []

        # Ask the service to group, and fall back to counting the sample if $apply is
        # unsupported, which is reported either way rather than assumed.
        grouped = self._get(
            "groupby dataset",
            f"AllFinancialIndicators?$apply=groupby(({disc}),aggregate($count as rows))",
            "financial_by_dataset.json")
        names: List[str] = []
        if grouped and (grouped.get("value") or []):
            for r in grouped["value"]:
                names.append(str(r.get(disc)))
            self.report["dataset_counts"] = {
                str(r.get(disc)): r.get("rows") for r in grouped["value"]}
            print(f"  $apply groupby works, {len(names)} datasets named by the service")
        else:
            seen = Counter(str(r.get(disc)) for r in rows)
            names = sorted(seen)
            self.report["dataset_counts_from_sample"] = dict(seen)
            self.report["notes"].append(
                "The service did not answer $apply=groupby, so the dataset names below "
                "are the ones present in a sample of "
                f"{len(rows)} rows and are not the whole list of 16.")
            print(f"  $apply refused, {len(names)} dataset names in the sample only")
        for n in sorted(names):
            print(f"    {n}")
        return sorted(names)

    def dataset_detail(self, disc: str, name: str) -> None:
        """For one dataset, what it is keyed on, which years it covers, and its components."""
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)
        payload = self._get(
            f"dataset {name}",
            f"AllFinancialIndicators?$filter={disc} eq '{name}'&$top={self.sample}"
            f"&$count=true",
            f"dataset_{safe}.json")
        rows = (payload or {}).get("value") or []
        info: Dict[str, Any] = {
            "rows_total": (payload or {}).get("@odata.count"),
            "rows_sampled": len(rows),
        }
        if not rows:
            self.report["datasets"][name] = info
            return

        fields = sorted({k for r in rows for k in r.keys()})
        kinds = _classify(fields)
        info["fields"] = fields
        info["field_kinds"] = kinds

        # Question one. Does anything here resolve to a country.
        geo = self.conn.geographies()
        for field in kinds["geography"]:
            vals = [str(r.get(field)) for r in rows if r.get(field) not in (None, "")]
            hits = sum(1 for v in vals if v in geo)
            iso3 = sorted({geo[v][0] for v in vals if v in geo})
            info.setdefault("geography_resolution", {})[field] = {
                "values_present": len(vals),
                "distinct_values": len(set(vals)),
                "resolving_to_a_country": hits,
                "countries": iso3[:25],
                "country_count": len(iso3),
            }

        # Question two. Does anything here resolve to a year.
        for field in kinds["year"]:
            vals = [r.get(field) for r in rows if r.get(field) not in (None, "")]
            years = Counter()
            for v in vals:
                # Any four-digit run anywhere in the value, because the service's own CSV
                # exports write a date as "20 Mar 2017" and an ISO date as "2017-03-20", and
                # reading the first four characters would find the year in one and the day
                # in the other.
                for token in _YEAR_RUN.findall(str(v)):
                    if 1990 <= int(token) <= 2040:
                        years[int(token)] += 1
            info.setdefault("year_resolution", {})[field] = {
                "values_present": len(vals),
                "years_found": dict(sorted(years.items())),
                "example": str(vals[0])[:40] if vals else None,
            }

        # Question three. Does anything here separate HIV from the other two diseases.
        amount_field = kinds["amount"][0] if kinds["amount"] else None
        info["amount_field_used"] = amount_field
        for field in kinds["component"]:
            counts = Counter(str(r.get(field)) for r in rows)
            money: Dict[str, float] = defaultdict(float)
            if amount_field:
                for r in rows:
                    try:
                        money[str(r.get(field))] += float(r.get(amount_field) or 0)
                    except (TypeError, ValueError):
                        pass
            info.setdefault("components", {})[field] = {
                "rows": dict(counts.most_common()),
                "money_sampled": {k: round(v, 2) for k, v in sorted(
                    money.items(), key=lambda kv: -kv[1])},
            }

        # Currency, because a figure in an unstated currency is item 30 all over again.
        for field in kinds["currency"]:
            info.setdefault("currencies", {})[field] = dict(
                Counter(str(r.get(field)) for r in rows).most_common())

        info["example_row"] = rows[0]
        self.report["datasets"][name] = info

    # -- question four, does this repeat what the panel already holds ----------
    def overlap(self, disc: Optional[str]) -> None:
        """Pull one named grant, so the service can be compared against IATI by hand."""
        print(f"\n== the one grant with a known unexplained gap, {_GRANT}")
        for field in ("grantAgreementImplementationPeriodId", "grant", "grantAgreementNumber",
                      "grantAgreementId", "grantAgreementImplementationPeriodNumber"):
            payload = self._get(
                f"grant by {field}",
                f"AllFinancialIndicators?$filter={field} eq '{_GRANT}'&$top={self.sample}"
                f"&$count=true",
                f"grant_{field}.json")
            rows = (payload or {}).get("value") or []
            if rows:
                self.report["grant_probe"] = {
                    "field_that_worked": field,
                    "rows": len(rows),
                    "rows_total": (payload or {}).get("@odata.count"),
                    "by_dataset": dict(Counter(
                        str(r.get(disc)) for r in rows)) if disc else None,
                    "example_row": rows[0],
                }
                print(f"  {field} matches {_GRANT}, {len(rows)} rows returned")
                return
        self.report["grant_probe"] = {"field_that_worked": None}
        self.report["notes"].append(
            f"No field tried matched the grant {_GRANT} by name, so the overlap against "
            "IATI has to be done on whatever identifier the saved dataset responses carry.")
        print(f"  no field tried matched {_GRANT} by name")

    # -- run ------------------------------------------------------------------
    def run(self) -> int:
        print(f"Global Fund financial datasets survey")
        print(f"service {_BASE}")
        print(f"output  {self.out}")
        self.service_map()
        names = self.financial_datasets()
        disc = self.report.get("dataset_field")
        if names and disc:
            print(f"\n== each dataset, keyed on {disc}")
            for name in names:
                self.dataset_detail(disc, name)
        self.overlap(disc)

        path = self.out / "survey.json"
        path.write_text(json.dumps(self.report, indent=1, default=str))
        print(f"\n{len(self.report['requests'])} requests made, "
              f"{len(self.report['datasets'])} datasets described")
        for note in self.report["notes"]:
            print(f"NOTE {note}")
        print(f"\nreport -> {path}")
        print("Nothing under data/panel/ was read or written by this probe.")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__ and __doc__.splitlines()[1])
    ap.add_argument("--out", default=None,
                    help="output directory, default data/raw/global_fund/survey_<date>/")
    ap.add_argument("--sample", type=int, default=200,
                    help="rows to pull per dataset, default 200")
    args = ap.parse_args()

    stamp = dt.date.today().isoformat().replace("-", "")
    out = pathlib.Path(args.out) if args.out else (
        ROOT / "data" / "raw" / "global_fund" / f"survey_{stamp}")
    out.mkdir(parents=True, exist_ok=True)
    return Survey(out, args.sample).run()


if __name__ == "__main__":
    sys.exit(main())
