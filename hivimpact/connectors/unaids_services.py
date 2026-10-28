"""
UNAIDS service continuation dashboard connector, connector 30, the monthly HIV service counts
countries have reported to UNAIDS since October 2024, turned into calendar-year rows.

UNAIDS (the Joint United Nations Programme on HIV/AIDS) set up a monthly reporting round after
the cuts to United States funding in January 2025, and AIDSinfo shows the reports on the page
"Service continuation" (https://aidsinfo.unaids.org/services). The page embeds a public Power BI
report whose model is named "Mini-GAM_Data visualization_01Dec2025" (GAM being Global AIDS
Monitoring, the annual UNAIDS reporting round). The model was last refreshed on 19 August 2026.
The report answers the same anonymous querydata call as paho_core and paho_hiv, with the
resource key of the public link and no sign-in.

What the dashboard holds, read on 14 October 2026 (research/aggregator_sweep_notes.md).
  - FactTable, one value per country, period and attribute. 19,105 values for 30 countries,
    monthly from October 2024 to December 2025 and quarterly from January 2026. The report's
    own note says quarterly values cover three months and are not comparable with single months.
    The model lists 2026-Q2 as a period, and no value falls in 2026-Q2 at the read.
  - 221 attributes, the treatment cascade (people on ART, initiations, returns to treatment,
    viral load tests and suppressed results, multi-month dispensing), HIV testing and positives,
    PrEP (pre-exposure prophylaxis), circumcisions, antenatal testing and PMTCT (prevention of
    mother-to-child transmission), early infant diagnosis, TB preventive treatment, programmes
    for key populations, sexual and gender-based violence services, and the share of facilities
    reporting in every programme area.
  - Pepfar_funding and Pepfar_funding_response, a yes or no answer per country for eight
    programme codes (pepfar_funding_95, pepfar_funding_prep and six other codes). The page does
    not define the codes, so the connector copies the answers into extra as published. 12
    pairs of country and code hold a yes in some periods and a no in other periods, and
    extra.pepfar_funding_reported lists every answer a country gave for a code.
  - PEPFARcountryList, 206 countries, 43 of them marked FormerPEPFAR.

Reporting thins out over 2025. 1,475 values fall in January 2025 and 534 in November 2025. No
mapped attribute holds all 12 months of 2025 in more than six countries, and the six countries
with a full year of any mapped count are Botswana, Burundi, Haiti, Mozambique, Ukraine and
Zimbabwe.

How a year is built.
  - People on ART is a count of people at a date. The year's row is the December value, or the
    fourth-quarter value once the round is quarterly. December 2024 falls before the cuts of
    January 2025, so the 2024 row is the baseline.
  - Every other count is a count of events in a period. The year's row is the total of the 12
    months or of the four quarters, and a year that misses any period gives no row, because a
    partial total would read as a fall in services. October to December 2024 never makes a year,
    so the counts of events start in 2025.
  - Positivity, TB preventive treatment among people newly on ART, antenatal testing and viral
    suppression are ratios of two summed counts, with both sums in numerator and denominator.
    A year whose summed numerator exceeds the summed denominator gives no row, because a
    numerator larger than the denominator cannot count the same people as the denominator. Haiti's suppressed count runs near 75,000 a month
    against near 10,000 viral load results a month, which reads as people suppressed in the last
    12 months against results in the month, and Haiti's 2025 suppression rate is refused. A row
    whose year holds a month with the numerator above the denominator keeps the year and lists
    the month in extra.periods_numerator_above_denominator.
  - Every row carries the whole monthly series of the attribute in extra.series, the share of
    facilities reporting in the programme area for each period of the year, and any comment the
    country attached to a period of the year.

Panel indicators and dashboard attributes.
  on_art_count                  num_artall, people currently on ART
  art_initiations               num_initall, people newly started on ART
  hiv_tests_performed           den_ageall, the testing volume
  new_diagnoses                 num_ageall, positive results
  hiv_test_positivity_pct       num_ageall over den_ageall
  circumcisions_performed       num_vmmctotal
  pmtct_arv_count               num_pmtctdata_value, women who delivered and received ARVs
  viral_suppression_pct         num_vl_suppressedall over num_vl_testedall, suppressed viral
                                load results over viral load results
  tpt_initiation_new_pct        numeratorall over denominatorall, people newly on ART who
                                started TB preventive treatment
  anc_hiv_testing_pct           numeratorall_pregnant over facility_denall_pregnant, women at
                                antenatal care or delivery who were tested or knew their status
The suppression rate follows nigeria_ndr. The dashboard counts viral load results in a month,
so a total of 12 months counts a person tested twice in the year twice. The panel defines
viral_load_tests_performed and viral_suppression_count as counts of people, and the connector
emits neither count. The rate of suppressed results over all results carries both totals as
numerator and denominator, and extra.denominator_basis records that the denominator is viral
load results and not people on ART.

What the connector refuses, and why.
  - PrEP for the whole population and for key populations (prep_alltotal, number_rec_prep*).
    The dashboard counts people who received PrEP at least once in the month, so one person on
    PrEP all year counts 12 times in a total of the months, and no annual figure can be built.
  - TB preventive treatment among people currently on ART (num_cur_enrol*). The denominator is
    the ART count of the month, and a total of 12 monthly ART counts is not a population.
  - Multi-month dispensing, early infant diagnosis counts, returns to treatment, condoms, needle
    and syringe programmes, opioid substitution, programme reach for key populations, the
    violence services and the LEN monitoring data (lenacapavir). No panel indicator holds a
    matching annual figure.
  - Every sex and age breakdown (the *female_gte_15, *male_gte_15, *age_lt_15_if, *ado_15_24
    and other_as_* attributes), and the dashboard's own adult series (calculated_*_15+). Rows for
    age groups wait on the decision Jason holds on age-group rows for the whole panel.
  - The viral load counts as counts of people, for the reason given with the suppression rate.
  - Countries with no value. FactTable lists every country of PEPFARcountryList with empty
    rows for the period "-", and only 30 countries hold a value. A code outside ISO 3166, with
    Kosovo's dashboard code 002 among the codes, gives no row because code_to_iso3 refuses the
    code.

Rows from the saved answers of 14 October 2026, in an offline test with the network blocked.
65 rows. on_art_count gives 20 rows for 2024 and six rows for 2025. The 2025 totals give six
rows for art_initiations, five rows for hiv_tests_performed, new_diagnoses,
hiv_test_positivity_pct and tpt_initiation_new_pct, four rows for pmtct_arv_count and
anc_hiv_testing_pct, three rows for viral_suppression_pct and two rows for
circumcisions_performed (Botswana and Zimbabwe).

Reconciliation against the panel of 14 October 2026, national rows for all sexes and ages.
  - 11 of the 20 December 2024 counts of people on ART equal a panel value exactly, six fall
    within half a per cent of a panel value, and the counts for Haiti, Malawi and Rwanda differ
    from every panel source by more than half a per cent. Zimbabwe's 1,232,472 equals
    global_fund, who_gho and who_tme.
  - Four of the six December 2025 counts equal a panel value exactly, Burundi and Mozambique
    with global_fund and Haiti and Zimbabwe with who_gho. Ukraine falls within half a per cent of
    global_fund, and Uganda's 1,492,545 differs from every panel source (global_fund 1,506,037).
  - No panel source holds a 2025 value for positivity, TB preventive treatment among people
    newly on ART, antenatal testing or circumcisions in the countries the connector covers.
  - The 2025 testing totals run four to eight times the PEPFAR values for the same country,
    because PEPFAR counts tests at sites PEPFAR supports (Mozambique 13,148,659 against
    2,836,359 in pepfar_modality and pepfar_panorama).
  - Mozambique's 2025 initiations total 243,597 against 193,673 in global_fund.
The equal December values show that countries send the same national register counts to the
Global Fund, to WHO and to UNAIDS, and the unequal values show that the reports do not always
match. reconcile.py infers the relationship of every unaids_services pair, and no relationship
is declared.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from collections import defaultdict
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..normalize import code_to_iso3
from ..schema import PanelRow, SourceType, POP_ALL
from .paho_core import _col, decode_dsr

log = logging.getLogger("hivimpact")

_QUERY_URL = ("https://wabi-north-europe-p-primary-api.analysis.windows.net"
              "/public/reports/querydata?synchronous=true")
# the AIDSinfo page the report is embedded in, written into source_url for a human reader
_PAGE_URL = "https://aidsinfo.unaids.org/services"

# "Mini-GAM_Data visualization_01Dec2025", read from modelsAndExploration on 14 October 2026
_REPORT = {
    "key": "9d8e7f34-29df-4d27-b900-cfb3c49bf5e2",
    "model_id": 684644,
    "dataset_id": "d460f4ab-3072-4392-bb79-27a72f4531b3",
    "report_id": "cf0a8701-5c32-4e30-913a-ba6906ffed5c",
}

_FACT_COLUMNS = ["country_code", "time_period", "Attribute", "Value", "comments", "addtl_info"]

# panel indicator -> (dashboard attribute, how the year is built)
#   "stock" takes the December or fourth-quarter value
#   "total" adds the 12 months or the four quarters and needs every period of the year
_COUNTS = {
    "on_art_count": ("num_artall", "stock"),
    "art_initiations": ("num_initall", "total"),
    "hiv_tests_performed": ("den_ageall", "total"),
    "new_diagnoses": ("num_ageall", "total"),
    "circumcisions_performed": ("num_vmmctotal", "total"),
    "pmtct_arv_count": ("num_pmtctdata_value", "total"),
}
# panel percentage -> (numerator attribute, denominator attribute), both added over the year
_RATIOS = {
    "hiv_test_positivity_pct": ("num_ageall", "den_ageall"),
    "tpt_initiation_new_pct": ("numeratorall", "denominatorall"),
    "anc_hiv_testing_pct": ("numeratorall_pregnant", "facility_denall_pregnant"),
    "viral_suppression_pct": ("num_vl_suppressedall", "num_vl_testedall"),
}
# dashboard attribute -> the programme area of the per_reporting* attribute, the share of
# facilities that reported in the period
_AREA = {
    "num_artall": "hiv_treatment", "num_initall": "hiv_treatment",
    "den_ageall": "hiv_testing", "num_ageall": "hiv_testing",
    "num_vl_testedall": "vl_testing", "num_vl_suppressedall": "vl_testing",
    "num_pmtctdata_value": "pmtct", "numeratorall": "tpt_newly_enrolled",
    "denominatorall": "tpt_newly_enrolled", "numeratorall_pregnant": "anc_testing",
    "facility_denall_pregnant": "anc_testing",
}
_COUNT_BASIS = {
    "hiv_tests_performed": "tests in the year, the dashboard's testing volume",
}
_DENOMINATOR_BASIS = {
    "viral_suppression_pct": ("viral load results in the year and not people on ART, so a person "
                              "tested twice counts twice in numerator and denominator"),
}

_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
_QUARTER = re.compile(r"^(\d{4})-Q([1-4])$")


def _period(text) -> Optional[Tuple[int, str, int]]:
    """"2025-03" -> (2025, "month", 3), "2026-Q1" -> (2026, "quarter", 1), anything else None."""
    s = str(text or "").strip()
    m = _MONTH.match(s)
    if m and 1 <= int(m.group(2)) <= 12:
        return int(m.group(1)), "month", int(m.group(2))
    q = _QUARTER.match(s)
    if q:
        return int(q.group(1)), "quarter", int(q.group(2))
    return None


def _year_periods(series: Dict[str, float], year: int) -> Tuple[Dict[int, float], Dict[int, float]]:
    """The months and the quarters of one year that hold a value, keyed by month or quarter number."""
    months: Dict[int, float] = {}
    quarters: Dict[int, float] = {}
    for text, v in series.items():
        p = _period(text)
        if p is None or p[0] != year:
            continue
        (months if p[1] == "month" else quarters)[p[2]] = v
    return months, quarters


def _year_value(series: Dict[str, float], year: int, how: str) -> Tuple[Optional[float], str, List[str]]:
    """The value of one year, a short account of how the value was built, and the periods used.

    A None value comes with the reason the year was refused.
    """
    months, quarters = _year_periods(series, year)
    if how == "stock":
        if 12 in months:
            return months[12], "the December value", [f"{year}-12"]
        if 4 in quarters:
            return quarters[4], "the fourth-quarter value", [f"{year}-Q4"]
        return None, "no December or fourth-quarter value", []
    if months and quarters:
        return None, "monthly and quarterly values mixed in one year", []
    if len(months) == 12:
        return sum(months.values()), "the total of 12 months", [f"{year}-{m:02d}" for m in range(1, 13)]
    if len(quarters) == 4:
        return sum(quarters.values()), "the total of four quarters", [f"{year}-Q{q}" for q in range(1, 5)]
    held = len(months) or len(quarters)
    unit = "months" if months else "quarters"
    return None, f"{held} {unit} of the year hold a value", []


def _number(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else f


def _count(prop: str) -> dict:
    """CountNonNull of one column, function 5 in the Power BI semantic query."""
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "t"}},
                                                      "Property": prop}},
                            "Function": 5},
            "Name": f"CountNonNull(t.{prop})"}


def _equals(prop: str, text: str) -> list:
    literal = "'" + str(text).replace("'", "''") + "'"
    return [{"Condition": {"In": {
        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": prop}}],
        "Values": [[{"Literal": {"Value": literal}}]]}}}]


def _note(v) -> str:
    s = " ".join(str(v).split()) if v is not None else ""
    return "" if s in ("-", "NULL") else s


class UNAIDSServicesConnector(BaseConnector):
    source_id = "unaids_services"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("UNAIDS service continuation dashboard, monthly service counts 30 countries "
                   "reported from October 2024, as December values and calendar-year totals.")
    request_pause = 1.0
    timeout = 120

    def _query(self, entity: str, select: list, where: Optional[list] = None) -> List[list]:
        query = {"Version": 2, "From": [{"Name": "t", "Entity": entity, "Type": 0}],
                 "Select": select}
        if where:
            query["Where"] = where
        body = {
            "version": "1.0.0",
            "queries": [{
                "Query": {"Commands": [{"SemanticQueryDataShapeCommand": {
                    "Query": query,
                    "Binding": {"Primary": {"Groupings": [{"Projections": list(range(len(select)))}]},
                                "DataReduction": {"DataVolume": 4,
                                                  "Primary": {"Window": {"Count": 30000}}},
                                "Version": 1}}}]},
                "QueryId": "",
                "ApplicationContext": {"DatasetId": _REPORT["dataset_id"],
                                       "Sources": [{"ReportId": _REPORT["report_id"]}]},
            }],
            "cancelQueries": [],
            "modelId": _REPORT["model_id"],
        }
        headers = {"X-PowerBI-ResourceKey": _REPORT["key"],
                   "Content-Type": "application/json;charset=UTF-8",
                   "ActivityId": str(uuid.uuid4()), "RequestId": str(uuid.uuid4())}
        resp = self._request("POST", _QUERY_URL, data=json.dumps(body), headers=headers)
        return decode_dsr(resp.json())

    def _countries(self) -> Dict[str, str]:
        """Dashboard country code -> country name, for every code holding at least one value."""
        rows = self._query("FactTable", [_col("country_code"), _col("country_name"), _count("Value")])
        return {code: name for code, name, n in rows if code and n}

    def _former_pepfar(self) -> Dict[str, bool]:
        rows = self._query("PEPFARcountryList", [_col("ISO3"), _col("FormerPEPFAR")])
        return {str(iso).upper(): str(flag or "").strip().lower() == "yes" for iso, flag in rows if iso}

    def _pepfar_funding(self) -> Dict[str, Dict[str, List[str]]]:
        """Dashboard country code -> programme code -> every answer the country gave, sorted."""
        rows = self._query("FactTable", [_col("country_code"), _col("Pepfar_funding"),
                                         _col("Pepfar_funding_response"), _count("Value")])
        out: Dict[str, Dict[str, set]] = defaultdict(lambda: defaultdict(set))
        for code, area, answer, _n in rows:
            if code and _note(area) and _note(answer):
                out[code][area].add(str(answer))
        return {c: {a: sorted(v) for a, v in areas.items()} for c, areas in out.items()}

    def _country_values(self, code: str) -> List[dict]:
        rows = self._query("FactTable", [_col(c) for c in _FACT_COLUMNS], _equals("country_code", code))
        return [dict(zip(_FACT_COLUMNS, r)) for r in rows]

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2024,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        end_year = min(end_year or date.today().year, date.today().year)
        start_year = max(start_year, 2024)

        names = self._countries()
        skipped_codes = sorted(c for c in names if code_to_iso3(c) is None)
        codes = {c: code_to_iso3(c) for c in names if code_to_iso3(c)}
        if wanted:
            codes = {c: iso for c, iso in codes.items() if iso in wanted}
        if not codes:
            log.info("unaids_services: no dashboard country matches the request")
            return
        former = self._former_pepfar()
        funding = self._pepfar_funding()

        emitted: Dict[str, int] = defaultdict(int)
        refused: Dict[str, int] = defaultdict(int)
        above: Dict[str, List[str]] = defaultdict(list)
        for code, iso3 in sorted(codes.items()):
            series: Dict[str, Dict[str, float]] = defaultdict(dict)
            notes: Dict[str, Dict[str, str]] = defaultdict(dict)
            for rec in self._country_values(code):
                attr = rec.get("Attribute")
                period = str(rec.get("time_period") or "").strip()
                if not attr or _period(period) is None:
                    continue
                # a comment can sit on a period with no value and explain the missing value
                text = "; ".join(t for t in (_note(rec.get("comments")), _note(rec.get("addtl_info"))) if t)
                if text:
                    notes[attr][period] = text
                v = _number(rec.get("Value"))
                if v is not None:
                    series[attr][period] = v

            def context(attrs: List[str], periods: List[str]) -> dict:
                ctx: dict = {}
                for a in attrs:
                    area = _AREA.get(a)
                    if area:
                        share = {p: series.get("per_reporting" + area, {}).get(p) for p in periods}
                        ctx.setdefault("facilities_reporting_pct", {})[a] = share
                    said = {p: notes[a][p] for p in periods if p in notes.get(a, {})}
                    if said:
                        ctx.setdefault("comments", {})[a] = said
                ctx["former_pepfar_country"] = former.get(iso3)
                if funding.get(code):
                    ctx["pepfar_funding_reported"] = dict(sorted(funding[code].items()))
                return ctx

            for year in range(start_year, end_year + 1):
                for canonical, (attr, how) in _COUNTS.items():
                    if attr not in series:
                        continue
                    value, basis, periods = _year_value(series[attr], year, how)
                    if value is None:
                        if _year_periods(series[attr], year) != ({}, {}):
                            refused[canonical] += 1
                        continue
                    spec = CANONICAL_INDICATORS[canonical]
                    extra = {"year_basis": basis, "periods": periods,
                             "series": dict(sorted(series[attr].items()))}
                    if canonical in _COUNT_BASIS:
                        extra["count_basis"] = _COUNT_BASIS[canonical]
                    extra.update(context([attr], periods))
                    yield self.make_row(
                        country_iso3=iso3, country_name=names[code], indicator_id=canonical,
                        year=year, value=value, population_group=POP_ALL, unit=spec.unit,
                        source_url=_PAGE_URL, source_indicator_code=attr, extra=extra,
                    )
                    emitted[canonical] += 1

                for canonical, (num_attr, den_attr) in _RATIOS.items():
                    if num_attr not in series or den_attr not in series:
                        continue
                    num, basis, periods = _year_value(series[num_attr], year, "total")
                    den, den_basis, den_periods = _year_value(series[den_attr], year, "total")
                    if num is None or den is None or periods != den_periods or not den:
                        if (_year_periods(series[num_attr], year) != ({}, {})
                                or _year_periods(series[den_attr], year) != ({}, {})):
                            refused[canonical] += 1
                        continue
                    if num > den:
                        # the two counts cannot cover the same people or results
                        above[canonical].append(f"{iso3} {year}")
                        continue
                    high = [p for p in periods if series[num_attr][p] > series[den_attr][p]]
                    spec = CANONICAL_INDICATORS[canonical]
                    extra = {"year_basis": f"numerator and denominator are each {basis}",
                             "periods": periods,
                             "series_numerator": dict(sorted(series[num_attr].items())),
                             "series_denominator": dict(sorted(series[den_attr].items()))}
                    if canonical in _DENOMINATOR_BASIS:
                        extra["denominator_basis"] = _DENOMINATOR_BASIS[canonical]
                    if high:
                        extra["periods_numerator_above_denominator"] = high
                    extra.update(context([num_attr, den_attr], periods))
                    yield self.make_row(
                        country_iso3=iso3, country_name=names[code], indicator_id=canonical,
                        year=year, value=round(100.0 * num / den, 2), numerator=num, denominator=den,
                        population_group=POP_ALL, unit=spec.unit, source_url=_PAGE_URL,
                        source_indicator_code=f"{num_attr}/{den_attr}", extra=extra,
                    )
                    emitted[canonical] += 1

        for canonical in list(_COUNTS) + list(_RATIOS):
            log.info("unaids_services: %-28s -> %d country-years, %d country-years refused as "
                     "incomplete", canonical, emitted.get(canonical, 0), refused.get(canonical, 0))
        for canonical, where in sorted(above.items()):
            log.info("unaids_services: %s refused where the year's numerator exceeds the year's "
                     "denominator (%s)", canonical, ", ".join(where))
        log.info("unaids_services: %d country codes outside ISO 3166 were skipped (%s)",
                 len(skipped_codes), ", ".join(skipped_codes))
