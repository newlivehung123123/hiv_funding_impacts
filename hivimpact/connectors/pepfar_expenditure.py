"""
PEPFAR expenditure reporting, split by the US agency that spent the money — the cut in dollars.

`pepfar_agency` recovered the funding-agency column on the service side (people on ART at
USAID-funded partners vs CDC-funded ones). This is the same move on the money side, over a file
that has been sitting in `data/raw/pepfar/` since July and that nothing read:
`Public_Partner_Budgets_and_Expenditures`. Every row names its country, implementation year,
funding agency, implementing partner, mechanism and programme area, and carries two amounts —
`Total Planned Funding` and `Total Expenditure`. FY2021 to FY2025, 59 operating units, 17 of the
22 Eastern and Southern African countries and 12 of the 24 in Western and Central Africa.

Planned versus spent is the point. A budget is a statement of intent made a year ahead; an
expenditure is what happened. When an agency is dismantled part-way through a year the budget
stays on the books and the expenditure does not follow it, so the gap between the two lines is
the event, and it appears a full reporting cycle before any change in the treatment numbers.

WHAT THE FY2025 FILE ACTUALLY SHOWS, AND WHY THE HEADLINE NUMBER IS NOT USABLE ALONE

Reported expenditure globally, USAID against CDC (USD m):

    FY2023   USAID 2,149.0   CDC 1,592.2
    FY2024   USAID 2,060.7   CDC 1,585.2
    FY2025   USAID 1,236.3   CDC 1,428.7

A 40% fall in the arm that was dismantled against a 10% fall in the arm that was not. Read at
face value that is the cut, measured in dollars, and South Africa (-79%), Namibia (-88%),
Cameroon (-78%) and Uganda (-58%) are where it lands hardest.

It cannot be read at face value, and this connector exists as much to say so as to carry the
number. Count mechanisms rather than dollars: of the USAID mechanisms that held a budget,
the share that filed any expenditure at all runs 0.76 to 0.85 in FY2021 to FY2024 and falls to
**0.42** in FY2025. CDC's holds at about 0.85. So the reported USAID decline is a spend decline
and a reporting collapse superimposed, and the file cannot separate them. Every African country
shows it: South Africa's USAID reporting rate goes 0.81 to 0.21, Uganda's 0.75 to 0.22, Malawi's
0.96 to 0.23.

That is not a nuisance to be noted and set aside. Expenditure reports are filed by the staff of
the agency being reported on, so dismantling the agency degrades the instrument measuring it, in
the exact arm under study and in the exact year of interest. Anyone using PEPFAR ER FY2025 as a
spend series without this correction will report a cut whose size is partly an artefact of the
cut. The connector therefore carries on every expenditure row:

  * `mechanisms_budgeted` / `mechanisms_reporting` / `reporting_rate`;
  * `planned_on_silent_mechanisms` — the budget held by mechanisms that filed nothing, which
    bounds what the missing reports could contain;
  * `expenditure_ceiling` = value + that budget, the most generous reading available;
  * `completeness_warning` whenever the reporting rate falls ten points or more year on year.

Kenya FY2025 is the shape of it: 111.6m reported against a 187.0m ceiling, on a reporting rate
of 0.44. The true figure is somewhere in that interval and the file will not narrow it. Saying
so is the finding.

CDC AS A CONTROL, AND WHERE IT STOPS WORKING

Same country, same year, same reporting system, same definition of an expenditure — CDC is the
within-country control for USAID here exactly as it is in `pepfar_agency`. Its reporting rate
holding while USAID's halves is itself the evidence that FY2025 is not simply a late file: a
uniform lag would thin both arms. What CDC does not control for is work transferred between
agencies, which moves both series at once, and a country whose CDC spend rises as its USAID
spend falls needs that excluded before the difference is read as a net loss.

GRAIN AND DOUBLE COUNTING

The three agency series for a country-year are a partition of the country total and sum back to
`pepfar_planned_funding` / `pepfar_expenditure`, which this connector also emits. Anything
totalling the panel must take one level or the other, never both. Programme areas (C&T, PREV,
HTS, ASP, SE) are carried inside `extra.by_program` instead of as rows for the same reason.

The programme split is where the shape of the FY2025 cut shows, and it is not flat. Against
FY2024, USAID's reported spend falls 21% on care and treatment, 76% on prevention, 58% on
above-site programme support and 70% on socio-economic support. Treatment was protected and
everything around it was not — subject, throughout, to the reporting caveat above.

TAGGING: PEPFAR expenditure reporting measures the PEPFAR programme, not national HIV spending.
Amounts are nominal USD, not deflated. source_type = expenditure_account.
"""
from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

# PEPFAR's agency labels -> the suffix the canonical id carries. Everything else (DOD, HRSA,
# State's bureaux, Peace Corps) is pooled into "other_agency" so the series still partition
# the country total. Same mapping as pepfar_agency, deliberately.
AGENCY_SUFFIX = {"USAID": "usaid", "HHS/CDC": "cdc"}
OTHER = "other_agency"

PLANNED = "pepfar_planned_funding"
SPENT = "pepfar_expenditure"

# a year-on-year fall of this many points in the share of budgeted mechanisms filing an
# expenditure report is flagged on the row: below it the level is not comparable with last year's
REPORTING_DROP_FLAG = 0.10

INTERPRETATION = (
    "PEPFAR programme spending, not national HIV expenditure, and nominal USD. The FY2025 "
    "expenditure level is confounded with a reporting collapse in the same arm: check "
    "`reporting_rate` and `expenditure_ceiling` on this row before reading a fall as money not "
    "spent. CDC is the within-country control — its reporting rate held while USAID's halved — "
    "but it does not control for work transferred between agencies."
)


def _ci(cols: List[str], *names: str) -> Optional[str]:
    low = {c.lower().strip(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    return None


def _num(cell) -> float:
    """Blank, '.', 'NA' -> 0.0. Blanks here are structural, not missing values: a mechanism
    reports its budget and its expenditure on different disaggregation rows, so a blank means
    'nothing on this line', and whether the mechanism reported at all is decided at mechanism
    level in `_emit`."""
    if cell is None:
        return 0.0
    s = str(cell).strip().replace(",", "").replace("$", "")
    if s in ("", "nan", "NA", "N/A", ".", "..."):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _suffix(agency: str) -> str:
    return AGENCY_SUFFIX.get(str(agency).strip().upper(), OTHER)


class PEPFARExpenditureConnector(BaseConnector):
    source_id = "pepfar_expenditure"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = "PEPFAR planned funding vs expenditure by US funding agency — the cut in dollars."

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _process(
        self,
        chunk: pd.DataFrame,
        mech: Dict[tuple, Dict[str, float]],
        names: Dict[str, str],
        wanted,
        start_year: int,
        end_year: int,
    ) -> bool:
        """Accumulate at (iso3, year, agency, mechanism). The mechanism is the unit that files
        an expenditure report, so completeness has to be judged there and not on the row."""
        cols = list(chunk.columns)
        iso_c = _ci(cols, "iso3")
        yr_c = _ci(cols, "implementation year")
        ag_c = _ci(cols, "funding agency")
        pl_c = _ci(cols, "total planned funding")
        ex_c = _ci(cols, "total expenditure")
        mc_c = _ci(cols, "mechanism code")
        pn_c = _ci(cols, "partner name")
        pg_c = _ci(cols, "program")
        it_c = _ci(cols, "interaction type")
        cn_c = _ci(cols, "country")
        # the agency column and both amounts are the whole point — a file without them is not this
        if not (iso_c and yr_c and ag_c and pl_c and ex_c and mc_c):
            return False

        for _, r in chunk.iterrows():
            iso3 = to_iso3(r[iso_c])
            if not iso3 or (wanted and iso3 not in wanted):
                continue
            try:
                year = int(str(r[yr_c])[:4])
            except (TypeError, ValueError):
                continue
            if year < start_year or year > end_year:
                continue

            key = (iso3, year, _suffix(r[ag_c]), str(r[mc_c]).strip())
            d = mech.setdefault(key, {})
            planned, spent = _num(r[pl_c]), _num(r[ex_c])
            d["planned"] = d.get("planned", 0.0) + planned
            d["spent"] = d.get("spent", 0.0) + spent
            if pn_c:
                pname = str(r[pn_c]).strip()
                if pname and pname.lower() != "nan":
                    d["partner"] = pname
            if pg_c:
                prog = str(r[pg_c]).strip() or "Not Specified"
                d[f"prog::{prog}"] = d.get(f"prog::{prog}", 0.0) + spent
            if it_c and str(r[it_c]).strip().lower().startswith("service delivery"):
                d["service_delivery"] = d.get("service_delivery", 0.0) + spent
            if cn_c:
                names[iso3] = str(r[cn_c])
        return True

    # -- emitting ---------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        if not self.raw_dir.exists():
            log.warning("pepfar_expenditure: %s does not exist — download "
                        "Public_Partner_Budgets_and_Expenditures from data.pepfar.gov", self.raw_dir)
            return
        files = sorted(list(self.raw_dir.glob("*.zip")) + list(self.raw_dir.glob("*.txt"))
                       + list(self.raw_dir.glob("*.csv")))
        # the partner-level budget/expenditure file only. The OU-level file covers the same
        # money at a coarser grain with no agency column, so reading both would double count.
        wanted_files = [f for f in files
                        if "budget" in f.name.lower() and "public_partner" in f.name.lower()]
        if not wanted_files:
            log.warning("pepfar_expenditure: no Public_Partner_Budgets_and_Expenditures file in %s",
                        self.raw_dir)
            return
        if len(wanted_files) < len(files):
            log.info("pepfar_expenditure: reading %d of %d file(s) in %s. Not read: %s",
                     len(wanted_files), len(files), self.raw_dir,
                     [f.name for f in files if f not in wanted_files])

        mech: Dict[tuple, Dict[str, float]] = {}
        names: Dict[str, str] = {}
        for path in wanted_files:
            used = False
            try:
                if path.suffix == ".zip":
                    with zipfile.ZipFile(path) as z:
                        members = [m for m in z.namelist() if m.lower().endswith((".txt", ".csv"))]
                        for member in members:
                            with z.open(member) as fh:
                                sep = "\t" if member.lower().endswith(".txt") else ","
                                for chunk in pd.read_csv(fh, sep=sep, dtype=str, chunksize=200_000,
                                                         on_bad_lines="skip", low_memory=False):
                                    if self._process(chunk, mech, names, wanted, start_year, end_year):
                                        used = True
                                    else:
                                        break
                else:
                    sep = "\t" if path.suffix == ".txt" else ","
                    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=200_000,
                                             on_bad_lines="skip", low_memory=False):
                        if self._process(chunk, mech, names, wanted, start_year, end_year):
                            used = True
                        else:
                            break
            except Exception as exc:
                log.warning("pepfar_expenditure: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_expenditure: %s %s", path.name,
                     "(used)" if used else "(skipped — no Funding Agency / amount columns)")

        yield from self._emit(mech, names)

    # -- aggregation ------------------------------------------------------------
    @staticmethod
    def _roll_up(mech: Dict[tuple, Dict[str, float]]) -> Dict[tuple, dict]:
        """(iso3, year, agency) -> the aggregate, plus the completeness counts that decide
        whether its expenditure figure is comparable with last year's."""
        out: Dict[tuple, dict] = {}
        for (iso3, year, agency, code), d in mech.items():
            for key in ((iso3, year, agency), (iso3, year, "")):  # agency level and country total
                a = out.setdefault(key, {"planned": 0.0, "spent": 0.0, "service_delivery": 0.0,
                                         "budgeted": 0, "reporting": 0, "planned_silent": 0.0,
                                         "programs": {}, "partners": {}})
                a["planned"] += d.get("planned", 0.0)
                a["spent"] += d.get("spent", 0.0)
                a["service_delivery"] += d.get("service_delivery", 0.0)
                # a mechanism holding a budget but filing no expenditure is the silent case;
                # its budget is what the missing report could have contained
                if d.get("planned", 0.0) > 0:
                    a["budgeted"] += 1
                    if d.get("spent", 0.0) > 0:
                        a["reporting"] += 1
                    else:
                        a["planned_silent"] += d["planned"]
                for k, v in d.items():
                    if k.startswith("prog::") and v:
                        a["programs"][k[6:]] = a["programs"].get(k[6:], 0.0) + v
                partner = d.get("partner")
                if partner and d.get("spent", 0.0):
                    a["partners"][partner] = a["partners"].get(partner, 0.0) + d["spent"]
        return out

    def _emit(self, mech: Dict[tuple, Dict[str, float]], names: Dict[str, str]) -> Iterator[PanelRow]:
        agg = self._roll_up(mech)
        n = 0
        for (iso3, year, agency), a in sorted(agg.items()):
            suffix = f"_{agency}" if agency else ""
            country_name = names.get(iso3, "")
            budgeted, reporting = a["budgeted"], a["reporting"]
            rate = (reporting / budgeted) if budgeted else None

            base: Dict[str, object] = {
                "note": "PEPFAR programme spending, NOT national HIV expenditure. Nominal USD.",
                "funding_agency": agency or "all_us_agencies",
                "mechanisms_budgeted": budgeted,
                "mechanisms_reporting": reporting,
            }

            # --- planned funding: a statement of intent, complete by construction ---
            if a["planned"] > 0:
                yield self.make_row(
                    country_iso3=iso3, country_name=country_name,
                    indicator_id=f"{PLANNED}{suffix}", year=year, value=a["planned"], unit="USD",
                    source_url="https://data.pepfar.gov/datasets",
                    source_indicator_code="Public Partner Budgets and Expenditures — Total Planned Funding",
                    extra={**base,
                           "meaning": "budget approved for the year, not money spent",
                           "interpretation": INTERPRETATION},
                )
                n += 1

            # --- expenditure: the measured quantity, and the one that needs the caveat ---
            if a["spent"] > 0 or budgeted:
                extra: Dict[str, object] = {
                    **base,
                    "reporting_rate": round(rate, 3) if rate is not None else None,
                    "planned_on_silent_mechanisms": a["planned_silent"],
                    "expenditure_ceiling": a["spent"] + a["planned_silent"],
                    "interpretation": INTERPRETATION,
                }
                if a["planned"] > 0:
                    extra["execution_ratio"] = round(a["spent"] / a["planned"], 3)
                if a["spent"] > 0:
                    extra["service_delivery_share"] = round(a["service_delivery"] / a["spent"], 3)

                prev = agg.get((iso3, year - 1, agency))
                if prev and prev["budgeted"] and rate is not None:
                    prev_rate = prev["reporting"] / prev["budgeted"]
                    extra["reporting_rate_prev_year"] = round(prev_rate, 3)
                    if prev_rate - rate >= REPORTING_DROP_FLAG:
                        warn = (
                            f"only {reporting}/{budgeted} budgeted mechanisms filed an expenditure "
                            f"report in FY{year} against {prev['reporting']}/{prev['budgeted']} in "
                            f"FY{year - 1}. This level is NOT comparable with FY{year - 1} and a "
                            f"fall between them is part spending and part non-reporting. The "
                            f"reported figure is a floor; the ceiling is "
                            f"{a['spent'] + a['planned_silent']:,.0f} USD."
                        )
                        extra["completeness_warning"] = warn
                        log.warning("pepfar_expenditure: %s %s FY%d — reporting rate %.2f -> %.2f",
                                    iso3, agency or "all", year, prev_rate, rate)

                if a["programs"]:
                    extra["by_program"] = {k: v for k, v in
                                           sorted(a["programs"].items(), key=lambda kv: -kv[1])}
                if a["partners"]:
                    top = sorted(a["partners"].items(), key=lambda kv: -kv[1])[:5]
                    extra["top_partners"] = [{"partner": p, "value": v} for p, v in top]
                    extra["n_partners"] = len(a["partners"])

                yield self.make_row(
                    country_iso3=iso3, country_name=country_name,
                    indicator_id=f"{SPENT}{suffix}", year=year, value=a["spent"], unit="USD",
                    source_url="https://data.pepfar.gov/datasets",
                    source_indicator_code="Public Partner Budgets and Expenditures — Total Expenditure",
                    extra=extra,
                )
                n += 1
        log.info("pepfar_expenditure: emitted %d rows", n)
