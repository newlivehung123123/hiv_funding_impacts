"""
Survey probe two for the Global Fund's financial datasets — the join, the HIV component and
the overlap against IATI.

Probe one, `scripts/survey_global_fund_financials.py`, run on 30 September 2026, established
that `AllFinancialIndicators` holds 1,269,005 rows over exactly 16 datasets carrying exactly
32 indicator names, that `Disbursement_ReferenceRate` is annual and entirely in US dollars,
and that each financial fact is published twice, once at a reference rate and once in the
implementation period's own currency. Probe one also established what it could not do. Every
identifier on a financial row is a bare GUID, no field on a financial row names a country, no
field names a disease, and no field carries a grant code, so five attempts to filter by grant
name returned HTTP 400 because no such property exists.

The saved `$metadata` says where the missing information lives. The service exposes 22 entity
sets, and `Grants` carries `geographyId`, `activityAreaId`, `code`, `iatI_ActivityIdentifier`
and the four grant totals, while `ActivityAreas` carries `name`, `code` and `iatI_Code`. So a
country, a disease and an IATI activity identifier are all reachable by a join, and this probe
fetches the tables that join needs and then tests the join rather than assuming it.

Four things this probe settles.

  1. What each identifier on a financial row points at. `recordId`, `providerRecordId`,
     `recieverRecordId`, `activityAreaId` and `financialCategoryId` are tested against grant
     ids, against funding request ids, against geography ids at every level and not only the
     country level probe one tested, and against the coordinating mechanism and donor tables.
     The answer decides whether a financial row can be attributed to a country at all, and
     probe one's finding that none of the identifiers resolves through the connector's own
     country map is not yet an answer, because that map holds only the geographies the
     service grades as Country. The test runs separately over each of the 16 datasets probe
     one sampled, because a disbursement row and a pledge row carry different kinds of thing
     in the same `recordId` field and a pooled test would average the two.

  2. How the Global Fund itself maps its components to IATI sector codes. `ActivityArea` has
     an `iatI_Code` field, so the panel does not have to assume that the HIV component is
     sector 13040, and the combined tuberculosis and HIV component, if the service publishes
     one, can be read rather than guessed at. That assumption is the open TB share caveat, so
     reading the publisher's own mapping settles the caveat with the publisher's own statement.

  3. Whether a financial dataset restates the IATI publication the panel already holds.
     `Grant.iatI_ActivityIdentifier` is the Global Fund's own crosswalk between a grant and
     the IATI activity the panel reads through d-portal, so the overlap can be measured
     exactly and not inferred. Anything that matches an identifier already in the panel's
     `extra.grant_identifiers` is a second copy of one reading and not a second reading, which
     is the trap item 27 of RESUME.md records.

  4. The one grant with a known unexplained gap. `NGA-H-NACA` is resolved through
     `Grants?$filter=code eq ...` to its id, and the financial rows carrying that id are
     pulled and printed by year, so the 3.9 per cent difference between the service and IATI
     that the survey of 21 September 2026 left open can be chased against both readings.

Two changes from probe one, both learned from probe one.

  * HTTP 400 is no longer retried. OData answers 400 when a property does not exist, so probe
    one spent 30 seconds backing off five times over a question the service had already
    answered. A 400 is now reported once, with the body the service returned, which usually
    names the offending property.

  * A paged response is followed. Probe one reported an `@odata.nextLink` and stopped. This
    probe follows the link up to a stated page cap and says how many pages it read, so a
    lookup table arrives whole or arrives with the truncation stated.

Read-only in the sense that matters. Every response is saved raw under the output directory,
nothing under `data/panel/` is read or written, and no PanelRow is emitted. The lookup tables
are saved whole on purpose, so that every further question can be answered offline against
the saved copies without asking the service again.

Usage:
    python scripts/survey_global_fund_financials2.py
    python scripts/survey_global_fund_financials2.py --out /some/other/directory
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hivimpact.connectors.global_fund import GlobalFundConnector, _BASE  # noqa: E402

_GRANT = "NGA-H-NACA"

#: Lookup tables fetched whole, so every further question is answerable offline. Every name
#: below was checked against the saved `metadata.xml` on 1 October 2026 and every name is one
#: of the service's 22 entity sets. `FundingRequests` is here because an allocation row and a
#: C19RM row have no grant to point at, so a funding request is the likeliest thing
#: `recordId` names on those datasets, and the identifier test cannot rule a table out
#: without holding that table's ids.
_LOOKUPS = ["ActivityAreas", "ActivityAreasGrouped", "FinancialCategories", "Geographies",
            "Grants", "FundingRequests", "OrganizationTypes", "Statuses",
            "CoordinatingMechanisms", "Donors", "FinancialIndicatorsList"]

#: The key property of each lookup table, read from the saved `metadata.xml`. Most tables key
#: on `id`, and the ones that do not would silently contribute an empty or a wrong id set to
#: the identifier test, which would read as "this table matched nothing" when the truth is
#: that the test never looked at the right column. `FinancialIndicatorsList` keys on a dataset
#: name and an indicator name together and holds no GUID at all, so no identifier on a
#: financial row could point at it and the identifier test leaves the table out by design.
#:
#: A tuple registers one id set per key, so a table reached through more than one column is
#: tested under each column and the report says which column matched. `FinancialCategories`
#: needs that, because the run of 1 October 2026 reported `financialCategoryId` as matching no
#: table when `financialCategoryId` in fact resolves to `FinancialCategories.hierarchyId` and
#: resolves 39 of 39. The miss was this map assuming `id`, not a gap in the service.
_KEYS: Dict[str, Any] = {"Statuses": "statusId", "FinancialIndicatorsList": None,
                         "FinancialCategories": ("id", "hierarchyId")}

#: Probe one's output lives beside probe two's, whatever `--out` says, so the saved samples
#: are found even when the output is written somewhere else.
_PROBE1_DIR = ROOT / "data" / "raw" / "global_fund"

#: The financial datasets probe one found to be annual, in US dollars and carrying an activity
#: area, which are the only ones that could become a country-year HIV series.
_CANDIDATE_DATASETS = ["Disbursement_ReferenceRate", "Commitment_ReferenceRate",
                       "Expenditure_Intervention_ReferenceRate", "GrantBudget_ReferenceRate"]


class Probe(GlobalFundConnector):
    """The connector's own session, UA, timeout and retries, with one change.

    A 400 is not retried. OData answers 400 when a property in a $filter does not exist, and
    retrying a question the service has already answered wastes half a minute per question.
    """

    RETRYABLE_STATUS = (429, 500, 502, 503, 504)


class Survey2:
    def __init__(self, out_dir: pathlib.Path, page_cap: int) -> None:
        self.out = out_dir
        self.page_cap = page_cap
        self.conn = Probe()
        self.tables: Dict[str, List[dict]] = {}
        self.report: Dict[str, Any] = {
            "probed_at": dt.datetime.now().isoformat(timespec="seconds"),
            "base": _BASE,
            "requests": [],
            "notes": [],
        }

    # -- one request, following paging, recording whatever happens -------------
    def _get_all(self, label: str, path: str, save_as: str) -> List[dict]:
        """GET a URL and follow @odata.nextLink up to the page cap. Returns the rows."""
        url = f"{_BASE}/{path}"
        rows: List[dict] = []
        pages = 0
        entry: Dict[str, Any] = {"label": label, "first_url": url}
        while url and pages < self.page_cap:
            try:
                resp = self.conn._request("GET", url)
            except Exception as exc:  # noqa: BLE001 - a refusal is a finding
                entry["outcome"] = "failed"
                entry["error"] = f"{type(exc).__name__}: {exc}"[:300]
                body = getattr(getattr(exc, "response", None), "text", "") or ""
                entry["service_said"] = body[:400]
                entry["rows_before_the_failure"] = len(rows)
                if rows:  # a part-read table is still worth keeping
                    (self.out / save_as).write_text(json.dumps(rows, indent=1, default=str))
                    entry["saved_as"] = save_as
                self.report["requests"].append(entry)
                print(f"  ! {label}: {entry['error']}")
                if body:
                    print(f"    service said: {body[:200]}")
                return rows
            payload = resp.json()
            rows.extend(payload.get("value") or [])
            if pages == 0:
                entry["odata_count"] = payload.get("@odata.count")
            url = payload.get("@odata.nextLink")
            if url and not str(url).lower().startswith("http"):
                url = f"{_BASE}/{str(url).lstrip('/')}"
            pages += 1

        entry["outcome"] = "ok"
        entry["pages"] = pages
        entry["rows"] = len(rows)
        entry["truncated"] = bool(url)
        (self.out / save_as).write_text(json.dumps(rows, indent=1, default=str))
        entry["saved_as"] = save_as
        self.report["requests"].append(entry)
        print(f"  ok {label}: {len(rows):,} rows over {pages} page(s)"
              + (f", count={entry['odata_count']:,}" if entry.get("odata_count") else "")
              + (f"  TRUNCATED at the {self.page_cap}-page cap" if url else "")
              + f" -> {save_as}")
        if url:
            self.report["notes"].append(
                f"{label} hit the {self.page_cap}-page cap, so the saved copy is partial and "
                "any count taken from it is a floor and not a total.")
        return rows

    # -- the lookup tables ----------------------------------------------------
    def lookups(self) -> None:
        print("\n== the lookup tables, fetched whole")
        for name in _LOOKUPS:
            rows = self._get_all(name, f"{name}?$count=true", f"lookup_{name}.json")
            self.tables[name] = rows

    # -- question two, the Global Fund's own component to IATI mapping --------
    def activity_areas(self) -> None:
        print("\n== the activity areas, with the service's own IATI sector codes")
        areas = self.tables.get("ActivityAreas") or []
        if not areas:
            print("  ! no activity areas came back, nothing below can be joined")
            return
        by_id = {str(a.get("id")): a for a in areas}
        listed = []
        for a in sorted(areas, key=lambda x: (str(x.get("type")), str(x.get("name")))):
            parent = by_id.get(str(a.get("parentId")))
            row = {
                "id": str(a.get("id")),
                "type": a.get("type"),
                "name": a.get("name"),
                "code": a.get("code"),
                "iati_code": a.get("iatI_Code"),
                "parent": (parent or {}).get("name"),
            }
            listed.append(row)
            print(f"  {str(a.get('type'))[:22]:22s} {str(a.get('name'))[:40]:40s} "
                  f"code={str(a.get('code'))[:12]:12s} iati={str(a.get('iatI_Code')):8s} "
                  f"parent={str((parent or {}).get('name'))[:24]}")
        self.report["activity_areas"] = listed
        hiv = [r for r in listed if "HIV" in str(r["name"]).upper()
               or str(r["iati_code"]) == "13040"]
        self.report["activity_areas_touching_hiv"] = hiv
        print(f"\n  {len(hiv)} activity area(s) name HIV or map to IATI sector 13040")
        for r in hiv:
            print(f"    {r['name']}  code={r['code']}  iati={r['iati_code']}  id={r['id']}")

    # -- the geography table, at every level ----------------------------------
    def geography_levels(self) -> None:
        """Count the geographies by level, because the connector keeps only one level."""
        geos = self.tables.get("Geographies") or []
        if not geos:
            return
        levels = Counter(str(g.get("level") or "unlabelled") for g in geos)
        countries = [g for g in geos
                     if str(g.get("level")) == "Country"
                     and len(str(g.get("code") or "").strip()) == 3]
        self.report["geography_levels"] = dict(levels.most_common())
        self.report["geographies_the_connector_keeps"] = len(countries)
        print("\n== the geography table, at every level")
        for lvl, n in levels.most_common():
            print(f"  {lvl:24s} {n:>5}")
        print(f"  the connector keeps {len(countries)} of {len(geos)}, the three-letter "
              "Country rows, so any financial row attached to another level has no country")

    # -- question one, what each identifier points at -------------------------
    def identify_ids(self) -> None:
        """Test every identifier field on a financial row against every table fetched.

        Probe one saved a 200-row sample of each of the 16 financial datasets, so the test
        runs over all 16 offline and no second fetch is made. Running the test per dataset
        and not over one pooled sample is the point. A disbursement row and a pledge row
        almost certainly carry different kinds of thing in the same `recordId` field, and a
        pooled test would average the two into an answer that is true of neither.
        """
        print("\n== what each identifier on a financial row points at, per dataset")
        saved = sorted(_PROBE1_DIR.glob("survey_*/dataset_*.json"))
        if not saved:
            self.report["notes"].append(
                "Probe one's saved dataset samples were not found under "
                "data/raw/global_fund/survey_*/, so the identifier test was skipped. Run "
                "scripts/survey_global_fund_financials.py first.")
            print("  ! probe one's saved dataset samples not found, skipping")
            return

        id_sets: Dict[str, set] = {}
        for name, tbl in self.tables.items():
            spec = _KEYS.get(name, "id")
            if spec is None:  # a table holding no GUID, left out by design
                continue
            keys = spec if isinstance(spec, tuple) else (spec,)
            for key in keys:
                # A table tested under one key is labelled by the table alone, and a table
                # tested under several is labelled by table and key, so a reader of the report
                # sees which column a financial row's identifier actually reached.
                label = name if len(keys) == 1 else f"{name}.{key}"
                ids = {str(r.get(key)) for r in tbl if r.get(key)}
                if ids:
                    id_sets[label] = ids
                else:
                    self.report["notes"].append(
                        f"{name} contributed no ids under the key {key}, so the identifier "
                        f"test could not look at {name} under {key}.")
        # Distinct ids and fetched rows are printed together, because the two differ whenever a
        # key repeats and a lone id count then reads as rows missing a key. The run of 1 October
        # 2026 printed 61 for FinancialCategories against 67 fetched rows, and all 67 rows carry
        # an id. The 61 is the number of distinct values, because `hierarchyId` repeats down the
        # hierarchy, and nothing was missing.
        print("  tables held: " + ", ".join(
            f"{n} {len(s):,} distinct of {len(self.tables[n.split('.')[0]]):,} rows"
            for n, s in id_sets.items()))

        fields = ("recordId", "providerRecordId", "recieverRecordId", "activityAreaId",
                  "financialCategoryId")
        out: Dict[str, Any] = {}
        for src in saved:
            ds = src.name[len("dataset_"):-len(".json")]
            rows = json.loads(src.read_text()).get("value") or []
            per: Dict[str, Any] = {"rows_sampled": len(rows)}
            print(f"\n  {ds}  ({len(rows)} sampled rows)")
            for field in fields:
                distinct = {str(r.get(field)) for r in rows if r.get(field)}
                if not distinct:
                    per[field] = {"distinct_values": 0, "matches": {}}
                    print(f"    {field:22s}    0 distinct -> the field is empty on every row")
                    continue
                hits = {n: len(distinct & ids) for n, ids in id_sets.items()}
                best = sorted(hits.items(), key=lambda kv: -kv[1])
                per[field] = {"distinct_values": len(distinct),
                              "matches": {n: c for n, c in hits.items() if c}}
                top = ", ".join(f"{n} {c}/{len(distinct)}" for n, c in best[:3] if c)
                print(f"    {field:22s} {len(distinct):>4} distinct -> "
                      f"{top or 'NO TABLE MATCHED'}")
            out[ds] = per
        self.report["identifier_resolution"] = out

    # -- the join, and what it yields -----------------------------------------
    def join_to_countries(self) -> None:
        """Resolve the candidate datasets' rows to a country and an activity area."""
        grants = {str(g.get("id")): g for g in (self.tables.get("Grants") or [])}
        geos = {str(g.get("id")): g for g in (self.tables.get("Geographies") or [])}
        areas = {str(a.get("id")): a for a in (self.tables.get("ActivityAreas") or [])}
        if not grants or not geos:
            print("\n  ! no grants or no geographies, the join cannot be tested")
            return

        print(f"\n== the join, tested on probe one's samples "
              f"({len(grants):,} grants, {len(geos):,} geographies)")
        joined: Dict[str, Any] = {}
        for ds in _CANDIDATE_DATASETS:
            found = sorted(_PROBE1_DIR.glob(f"survey_*/dataset_{ds}.json"))
            if not found:
                continue
            rows = json.loads(found[-1].read_text()).get("value") or []
            ok = 0
            countries: Counter = Counter()
            area_names: Counter = Counter()
            for r in rows:
                g = grants.get(str(r.get("recordId")))
                if not g:
                    continue
                geo = geos.get(str(g.get("geographyId")))
                if not geo:
                    continue
                ok += 1
                countries[f"{geo.get('code')} ({geo.get('level')})"] += 1
                a = areas.get(str(r.get("activityAreaId"))) or {}
                area_names[str(a.get("name"))] += 1
            joined[ds] = {
                "rows_sampled": len(rows),
                "resolved_to_a_grant_and_a_geography": ok,
                "countries": dict(countries.most_common(12)),
                "activity_areas": dict(area_names.most_common(12)),
            }
            print(f"  {ds}")
            print(f"    {ok} of {len(rows)} sampled rows reach a grant and a geography")
            print(f"    geographies: {', '.join(list(countries)[:10])}")
            print(f"    activity areas: {', '.join(list(area_names)[:6])}")
        self.report["join_test"] = joined

    # -- question three, the IATI crosswalk -----------------------------------
    def iati_crosswalk(self) -> None:
        print("\n== the Global Fund's own crosswalk to its IATI activities")
        grants = self.tables.get("Grants") or []
        if not grants:
            return
        with_id = [g for g in grants if str(g.get("iatI_ActivityIdentifier") or "").strip()]
        areas = {str(a.get("id")): a for a in (self.tables.get("ActivityAreas") or [])}
        hiv_ids = {r["id"] for r in self.report.get("activity_areas_touching_hiv", [])}
        hiv_grants = [g for g in grants if str(g.get("activityAreaId")) in hiv_ids]
        hiv_with_id = [g for g in hiv_grants
                       if str(g.get("iatI_ActivityIdentifier") or "").strip()]
        self.report["iati_crosswalk"] = {
            "grants": len(grants),
            "grants_naming_an_iati_activity": len(with_id),
            "hiv_grants": len(hiv_grants),
            "hiv_grants_naming_an_iati_activity": len(hiv_with_id),
            "examples": [{"code": g.get("code"),
                          "iati": g.get("iatI_ActivityIdentifier"),
                          "area": (areas.get(str(g.get("activityAreaId"))) or {}).get("name")}
                         for g in hiv_with_id[:10]],
        }
        print(f"  {len(grants):,} grants, {len(with_id):,} of them name an IATI activity")
        print(f"  {len(hiv_grants):,} grants sit in an HIV activity area, "
              f"{len(hiv_with_id):,} of those name an IATI activity")
        for e in self.report["iati_crosswalk"]["examples"][:6]:
            print(f"    {str(e['code']):18s} {str(e['iati']):34s} {e['area']}")

    # -- question four, the one grant with a known gap ------------------------
    def the_grant(self) -> None:
        print(f"\n== {_GRANT}, resolved through the grant table this time")
        grants = self.tables.get("Grants") or []
        hits = [g for g in grants if str(g.get("code") or "").upper() == _GRANT]
        if not hits:
            near = [str(g.get("code")) for g in grants
                    if "NACA" in str(g.get("code") or "").upper()]
            self.report["the_grant"] = {"found": False, "codes_containing_NACA": near[:20]}
            print(f"  no grant has the code {_GRANT}. Codes containing NACA: {near[:12]}")
            return
        geos = {str(g.get("id")): g for g in (self.tables.get("Geographies") or [])}
        areas = {str(a.get("id")): a for a in (self.tables.get("ActivityAreas") or [])}
        info = []
        for g in hits:
            geo = geos.get(str(g.get("geographyId"))) or {}
            area = areas.get(str(g.get("activityAreaId"))) or {}
            print(f"  id={g.get('id')}  {geo.get('code')} {area.get('name')}  "
                  f"{g.get('periodFrom')} to {g.get('periodTo')}")
            print(f"    IATI activity  {g.get('iatI_ActivityIdentifier')}")
            print(f"    totals, reference rate: signed {g.get('totalSignedAmount_ReferenceRate')}, "
                  f"committed {g.get('totalCommitmentAmount_ReferenceRate')}, "
                  f"disbursed {g.get('totalDisbursedAmount_ReferenceRate')}")
            rows = self._get_all(
                f"financial rows for {_GRANT}",
                f"AllFinancialIndicators?$filter=recordId eq {g.get('id')}&$count=true",
                f"grant_{_GRANT}_{str(g.get('id'))[:8]}.json")
            by = defaultdict(float)
            for r in rows:
                if r.get("financialDataSet") == "Disbursement_ReferenceRate":
                    by[str(r.get("periodFrom"))] += float(r.get("actualAmount") or 0)
            if by:
                print("    disbursements at the reference rate, by year")
                for y in sorted(by):
                    print(f"      {y}  {by[y]:>18,.2f}")
                print(f"      {'total':4s}  {sum(by.values()):>18,.2f}")
            info.append({
                "id": str(g.get("id")),
                "geography": geo.get("code"),
                "activity_area": area.get("name"),
                "iati_activity": g.get("iatI_ActivityIdentifier"),
                "period": f"{g.get('periodFrom')}-{g.get('periodTo')}",
                "totals_reference_rate": {
                    "signed": g.get("totalSignedAmount_ReferenceRate"),
                    "committed": g.get("totalCommitmentAmount_ReferenceRate"),
                    "disbursed": g.get("totalDisbursedAmount_ReferenceRate"),
                },
                "financial_rows": len(rows),
                "datasets_present": dict(Counter(
                    str(r.get("financialDataSet")) for r in rows).most_common()),
                "disbursements_by_year": {k: round(v, 2) for k, v in sorted(by.items())},
            })
        self.report["the_grant"] = {"found": True, "implementation_periods": info}

    # -- run ------------------------------------------------------------------
    def run(self) -> int:
        print("Global Fund financial datasets, survey probe two")
        print(f"service {_BASE}")
        print(f"output  {self.out}")
        self.lookups()
        self.activity_areas()
        self.geography_levels()
        self.identify_ids()
        self.join_to_countries()
        self.iati_crosswalk()
        self.the_grant()

        path = self.out / "survey2.json"
        path.write_text(json.dumps(self.report, indent=1, default=str))
        print(f"\n{len(self.report['requests'])} requests made")
        for note in self.report["notes"]:
            print(f"NOTE {note}")
        print(f"\nreport -> {path}")
        print("Nothing under data/panel/ was read or written by this probe.")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Global Fund financial datasets, probe two")
    ap.add_argument("--out", default=None,
                    help="output directory, default data/raw/global_fund/survey2_<date>/")
    ap.add_argument("--pages", type=int, default=40,
                    help="page cap when following @odata.nextLink, default 40")
    args = ap.parse_args()

    stamp = dt.date.today().isoformat().replace("-", "")
    out = pathlib.Path(args.out) if args.out else (
        ROOT / "data" / "raw" / "global_fund" / f"survey2_{stamp}")
    out.mkdir(parents=True, exist_ok=True)
    return Survey2(out, args.pages).run()


if __name__ == "__main__":
    sys.exit(main())
