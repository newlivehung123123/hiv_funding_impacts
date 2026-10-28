"""
Papua New Guinea, National Department of Health provincial HIV dashboard, connector 35. HIV tests,
positive HIV test results, people on antiretroviral therapy (ART), people newly started on ART and
mothers on ART under PMTCT (prevention of mother-to-child transmission) for the 22 provinces in 2022
and 2023 (to-source, routine programme, sub-national).

Source. The home page of the National Department of Health (NDoH), www.health.gov.pg, links
"PNG Provincial HIV Dashboard v.8.0", a public Power BI report. The report key names tenant
c2e1cf9b, the tenant of the dashboards of UNAIDS (the Joint United Nations Programme on HIV/AIDS)
read by unaids_databook and unaids_services, and
the dashboard model answers on the north-europe host through the anonymous querydata route
called by paho_core, paho_hiv, unaids_services and unaids_databook, with no sign-in. Model 367486,
"2024 PNG Provincial HIV Dashboard v.8.0", was last refreshed on 13 June 2025, read on 15 October
2026 (research/phase7_eap/eap_round1_notes.md, section Papua New Guinea).

What the connector reads. Table hiv_prog_data, summed by year (column Yr, a date at 31 December
sent as epoch milliseconds) and province (column ADM1_EN), in a single query. The district column
ADM2_EN reads "District Total" on every row of the programme table, so the province is the finest
level the dashboard gives. The 22 provinces are 20 provinces, National Capital District and the
Autonomous Region of Bougainville. The admin1 labels are the dashboard labels as published, the
labels pepfar_snu and pepfar_agency_snu use for Madang Province and National Capital District.

Panel indicators and dashboard columns.
  hiv_tests_performed   ProgramTotalHIVTest
  new_diagnoses         ProgramTotalHIVTestPositive, positive HIV test results recorded by the
                        national programme (research/rulings_2026-10-15.md, ruling R2)
  on_art_count          ProgramPLHIVonART, with the age groups 0-14 and 15+ from
                        ProgramPLHIVonART0_14 and ProgramPLHIVonART15+
  art_initiations       ProgramNewOnART
  pmtct_arv_count       ProgramPMTCTMothersOnART

The age groups of people on ART. ProgramPLHIVonART0_14 plus ProgramPLHIVonART15+ equals
ProgramPLHIVonART in all 44 province-years on 15 October 2026. The connector emits the age rows
of a province-year only where the two age columns add up to the total, and logs any province-year
where the age columns do not. The share of children under 15 among people on ART runs from 0.2
per cent in New Ireland Province for 2023 to 23.9 per cent in National Capital District for
2022, so the age split is a count by province and not a national ratio.

National rows. The connector also emits a national row (admin1 empty) for every indicator, age
group and year, the sum of the provinces, as ph_doh_cascade does for the Philippine regions.
extra.national_basis records the sum, and extra.provinces_without_value names any province with
no value for the year. A national row needs the full list of 22 provinces in the answer for the
year, and a national age row also needs the age columns to add up in every province.

National sums against data/panel/hiv_panel.csv, read on 15 October 2026.
  - HIV tests sum to 128,297 for 2022 and 172,875 for 2023. The 2023 sum equals unaids_aidsinfo,
    who_gho and who_hts. The 2022 sum is 17,489 above the 110,808 of unaids_aidsinfo, who_gho
    and who_hts, and the cause of the 17,489 extra tests for 2022 is NOT YET KNOWN.
  - Positive HIV test results sum to 4,284 for 2022 and 5,794 for 2023, with a value in all 22
    provinces for both years. The who_gho national count of tests times the who_gho positivity
    share gives 5,794 for 2023 (172,875 tests at 3.3516 per cent), equal to the dashboard sum, and
    3,938 for 2022 (110,808 tests at 3.5539 per cent), 346 below the dashboard sum, in the year of
    the 17,489 extra tests. The 2022 national row carries the Global AIDS Monitoring (GAM)
    comparison in extra.gam_comparison. pepfar_modality and pepfar_panorama count 600 positive
    tests for 2022 and 559 for 2023 at PEPFAR-supported sites only, a count from a different
    programme that is never added to the dashboard count.
  - People on ART sum to 43,816 for 2022 and 48,951 for 2023. The 2022 sum equals global_fund and
    who_gho. The 2023 sum falls short of the who_gho count of 48,952 by a single person and
    sits 1,185 above the global_fund count of 47,766. unaids_aidsinfo prints the rounded 44,000 and 49,000.
  - Children under 15 on ART sum to 2,147 for 2022 and 2,200 for 2023, the who_gho counts for
    the same years.
  - People newly started on ART sum to 7,615 for 2022 and 7,424 for 2023, above the who_tme counts
    of 6,175 and 6,095. pepfar_panorama counts 1,568 and 1,608 at sites supported by
    PEPFAR (the United States President's Emergency Plan for AIDS Relief) only.
  - Mothers on ART under PMTCT sum to 1,239 for 2022 and 1,515 for 2023, the unaids_aidsinfo
    and who_gho counts for the same years. Manus, New Ireland and West Sepik (Sandaun) carry no PMTCT value
    for 2023. global_fund reads 1,420 for 2022 and 1,515 for 2023.

Province rows against PEPFAR. National Capital District reads 3,165 people on ART for 2022 and
4,474 for 2023 in the dashboard, below the 6,839 and 7,712 people on ART at sites supported by
the United States Agency for International Development (USAID) in National Capital District,
carried by pepfar_agency_snu as on_art_count_usaid. People newly started on ART in National
Capital District read 696 and 679, below the USAID counts of 1,568 and 1,608 (art_initiations_usaid).
The cause of the lower dashboard counts for National Capital District is NOT YET KNOWN. The
dashboard may count people by province of residence, or the PEPFAR unit for National Capital
District may include sites outside the district. Positive tests in National Capital District read
1,016 for 2022 and 1,829 for 2023 in the dashboard, above the USAID counts of 600 and 559
(new_diagnoses_usaid in pepfar_agency_snu). No other source in the panel held a province row of
HIV tests, positive tests, people on ART, people newly started on ART or mothers on ART under PMTCT
for 2022 or 2023 on 15 October 2026.

What the connector refuses, and why.
  - The sex columns. ProgramPLHIVonARTMale plus ProgramPLHIVonARTFemale equals the 15+ column in
    every province-year, and the male share of the 15+ count lies between 38.1 and 38.5 per cent
    in all 22 provinces for 2022 and between 36.7 and 38.7 per cent for 2023. A share held so
    close to constant over 22 provinces points to a national ratio applied to every province,
    and a split computed from a ratio is not a count. The viral-load sex columns show the same
    pattern, with a male share between 39.3 and 40.4 per cent in every province with more than 50
    viral-load tests in 2022. ProgramNewARTMale plus ProgramNewARTFemale differs from
    ProgramNewOnART in 16 of the 44 province-years. ProgramHIVTestMale plus ProgramHIVTestFemale
    equals ProgramTotalHIVTest in all 22 provinces for 2022 and in no province for 2023, where the
    male count alone exceeds the total in Gulf, Northern (Oro), West New Britain and West Sepik
    (Sandaun), although the 2023 national sums still add up to 172,875. The 2022 test split by sex
    covers all ages, while who_hts and who_gho split tests by sex for ages 15 and over only.
  - The age split of people newly started on ART. The share of children under 15 in
    ProgramNewOnART lies between 1.4 and 2.3 per cent in every province for 2022 and between zero
    and 1.4 per cent for 2023, within the rounding of a single national share, although the share
    of children among people on ART runs from 0.2 to 23.9 per cent. The dashboard therefore splits
    the new starts by a ratio and does not count children.
  - The age columns of HIV tests. ProgramTotalHIVTest0_14 and ProgramTotalHIVTest15_64 are empty
    in every province-year, with zeros for Milne Bay Province in 2022.
  - Viral-load tests and suppressed viral loads (ProgramTotalViralLoadTestingDone and
    ProgramPLHIVSuppressedViralLoad). The viral-load counts exceed the count of people on ART in
    the same province-year for National Capital District (18,547 tests and 16,667 people suppressed
    against 3,165 on ART for 2022, 17,403 and 15,741 against 4,474 for 2023) and for Western
    Highlands Province (5,840 and 5,310 against 2,936 for 2022, 5,533 and 5,047 against 3,642 for
    2023). The panel ids viral_load_tests_performed and viral_suppression_count count people on ART,
    so the province of the viral-load columns is not the province of the ART count. The province
    may be the province of the testing laboratory, which is NOT YET KNOWN. Five provinces for 2022
    and eight for 2023 carry no viral-load value, so a national sum covers part of the country only
    (33,740 tests and 30,496 suppressed for 2022, 31,184 and 28,331 for 2023).
    ProgramViralLoadTestingUnknown reads -5 for Chimbu (Simbu) Province in 2023. No viral-load
    row enters the panel, province or national (research/rulings_2026-10-15.md, ruling R1).
  - The seven entry-point columns of positive tests. The panel holds no id for positive tests by
    the entry point of testing, and ProgramTotalHIVTestPositive gives the total.
  - Tests at the antenatal entry point (ProgramHIVTestEntryPointANC). The panel holds the share
    anc_hiv_testing_pct and no count id for antenatal tests, and the dashboard gives no count of
    pregnant women attending antenatal care, so no share can come from the dashboard (ruling R3).
  - key_pop_data and hiv_prev_data, the provincial size estimates of key populations and the
    condom counts. The size estimates sum to 195,360 female sex workers, 3.7 times the 52,200 sex
    workers in unaids_aidsinfo, and give the same national sums for 2022 and 2023. The condom
    counts cover nine provinces for 2022 only, in round thousands, and the column name does not
    say whether female condoms are counted (ruling R4).
  - spectrum_proj_data and CountryPrevalance_Incidence, provincial Spectrum estimates from an
    earlier estimate round than the UNAIDS round in the panel. A superseded modelled round stays
    out of the panel, for the reason recorded for EPW_11 in hivimpact/connectors/who_europe_hfa.py.
  - health_data, Demograph_data and Consolidated_data. health_data holds the health workforce and
    the shares of facility births and antenatal care, for which the panel holds no id.
    Demograph_data holds population estimates, and the panel takes population from world_bank.
    Consolidated_data repeats columns of the other tables.

Rows from the answer of 15 October 2026, in an offline test with the network blocked.
The connector emits 319 rows for 2022 and 2023. The 305 province rows are 44 rows of HIV tests,
44 rows of positive HIV test results, 44 rows of people on ART at all ages, 44 rows of children
under 15 on ART, 44 rows of people aged 15 and over on ART, 44 rows of people newly started on
ART and 41 rows of mothers on ART under PMTCT. The 14 national rows cover two years for every
indicator and age group, and the national sums equal the figures listed above. The run of 15
October 2026 before positive tests were added emitted 273 rows (261 province rows and 12
national rows). Altered copies of the answer confirmed the gates. A negative value gives no
row. An age split not adding up to the total gives no age row for the province-year
and no national age row for the year. A province appearing twice in the answer, or a province
missing from the answer, gives no national row for the year. A zero gives a row.

Source type. routine_programme_record, for the programme counts the ministry publishes.
"""
from __future__ import annotations

import json
import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...config.indicators import CANONICAL_INDICATORS
from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL
from ..paho_core import decode_dsr

log = logging.getLogger("hivimpact")

_QUERY_URL = ("https://wabi-north-europe-p-primary-api.analysis.windows.net"
              "/public/reports/querydata?synchronous=true")
# the ministry page linking the report, written into source_url for a human reader
_PAGE_URL = "https://www.health.gov.pg/"

# "2024 PNG Provincial HIV Dashboard v.8.0", read from modelsAndExploration on 15 October 2026
_REPORT = {
    "key": "41aa6d1a-a469-48e3-93f5-aabcdae5e041",
    "model_id": 367486,
    "dataset_id": "a6234972-c4ac-4f9e-b1ec-0aff921bd775",
    "report_id": "c3fa6aec-0c29-4abe-be97-3ecce6e9c450",
}
_MODEL_NAME = "2024 PNG Provincial HIV Dashboard v.8.0"
_MODEL_REFRESHED = "13 June 2025"
_TABLE = "hiv_prog_data"

# dashboard column -> (panel indicator, age group), in the order of the query's Select after
# year and province
_COLUMNS: List[Tuple[str, str, str]] = [
    ("ProgramTotalHIVTest", "hiv_tests_performed", "all"),
    ("ProgramPLHIVonART", "on_art_count", "all"),
    ("ProgramPLHIVonART0_14", "on_art_count", "0-14"),
    ("ProgramPLHIVonART15+", "on_art_count", "15+"),
    ("ProgramNewOnART", "art_initiations", "all"),
    ("ProgramPMTCTMothersOnART", "pmtct_arv_count", "all"),
    ("ProgramTotalHIVTestPositive", "new_diagnoses", "all"),
]
# the age rows of people on ART are emitted only where the two age columns add up to the total
_AGE_TOTAL = "ProgramPLHIVonART"
_AGE_PARTS = ("ProgramPLHIVonART0_14", "ProgramPLHIVonART15+")

_DEFINITIONS = {
    "ProgramTotalHIVTest": "HIV tests recorded by the national programme in the province",
    "ProgramPLHIVonART": "people living with HIV on ART in the province",
    "ProgramPLHIVonART0_14": "children under 15 living with HIV on ART in the province",
    "ProgramPLHIVonART15+": "people aged 15 and over living with HIV on ART in the province",
    "ProgramNewOnART": "people newly started on ART in the province during the year",
    "ProgramPMTCTMothersOnART": "mothers on ART under PMTCT in the province",
    "ProgramTotalHIVTestPositive": ("positive HIV test results recorded by the national programme "
                                    "in the province, a count of positive tests and not a count "
                                    "of people"),
}

# the 22 provinces the dashboard gave on 15 October 2026, as published
_PROVINCES = (
    "Autonomous Region of Bougainville", "Central Province", "Chimbu (Simbu) Province",
    "East New Britain Province", "East Sepik Province", "Eastern Highlands Province",
    "Enga Province", "Gulf Province", "Hela Province", "Jiwaka Province", "Madang Province",
    "Manus Province", "Milne Bay Province", "Morobe Province", "National Capital District",
    "New Ireland Province", "Northern (Oro) Province", "Southern Highlands Province",
    "West New Britain Province", "West Sepik (Sandaun) Province", "Western Highlands Province",
    "Western Province",
)

_NO_PROVINCE_SOURCE = ("none. No other source in the panel held a PNG province row of the same "
                       "indicator for 2022 or 2023 on 15 October 2026")

# (indicator, age group) -> the national comparison, from data/panel/hiv_panel.csv on 15 October 2026
_NATIONAL_NOTES: Dict[Tuple[str, str], str] = {
    ("hiv_tests_performed", "all"): (
        "unaids_aidsinfo, who_gho and who_hts hold the national count. The 2023 sum of the 22 "
        "provinces, 172,875, equals unaids_aidsinfo, who_gho and who_hts, and the 2022 sum, "
        "128,297, is 17,489 above the 110,808 of unaids_aidsinfo, who_gho and who_hts. The cause "
        "of the 17,489 extra tests for 2022 is NOT YET KNOWN"),
    ("on_art_count", "all"): (
        "global_fund, unaids_aidsinfo and who_gho hold the national count. The 2022 sum of the 22 "
        "provinces, 43,816, equals global_fund and who_gho. The 2023 sum, 48,951, falls short of "
        "the who_gho count of 48,952 by a single person and sits 1,185 above the global_fund count of 47,766. "
        "unaids_aidsinfo prints the rounded 44,000 and 49,000"),
    ("on_art_count", "0-14"): (
        "who_gho holds the national count of children under 15 on ART, and the sums of the 22 "
        "provinces equal who_gho for 2022 (2,147) and 2023 (2,200)"),
    ("on_art_count", "15+"): (
        "none. No other source in the panel held a national PNG count of people aged 15 and over "
        "on ART on 15 October 2026"),
    ("art_initiations", "all"): (
        "who_tme holds the national count, 6,175 for 2022 and 6,095 for 2023, below the sums of "
        "the 22 provinces (7,615 and 7,424). pepfar_panorama counts people newly started on ART "
        "at PEPFAR-supported sites only (1,568 and 1,608)"),
    ("pmtct_arv_count", "all"): (
        "unaids_aidsinfo and who_gho hold the national count, and the sums of the provinces equal "
        "unaids_aidsinfo and who_gho for 2022 (1,239) and 2023 (1,515). global_fund reads 1,420 "
        "for 2022 and 1,515 for 2023"),
    ("new_diagnoses", "all"): (
        "No other source in the panel held a national count of positive HIV tests from the PNG "
        "national programme on 15 October 2026. pepfar_modality and pepfar_panorama count "
        "positive tests at PEPFAR-supported sites only (600 for 2022 and 559 for 2023), a count "
        "from a different programme that is never added to the dashboard count. The who_gho "
        "count of tests times the who_gho positivity share gives 3,938 for 2022 and 5,794 for "
        "2023, against the sums of the 22 provinces of 4,284 and 5,794"),
}

# (indicator, age group, year) -> more extra for the national row of the year
_NATIONAL_YEAR_EXTRA: Dict[Tuple[str, str, int], Dict[str, str]] = {
    ("new_diagnoses", "all", 2022): {
        "gam_comparison": (
            "The Global AIDS Monitoring (GAM) figures carried by who_gho give 110,808 tests at a "
            "positivity of 3.5539 per cent, an implied 3,938 positive tests, 346 below the sum of "
            "the 22 provinces. The dashboard sum of tests, 128,297, sits 17,489 above the GAM "
            "count, and the cause of the 17,489 extra tests and of the 346 extra positive tests "
            "is NOT YET KNOWN"),
    },
    ("new_diagnoses", "all", 2023): {
        "gam_comparison": (
            "The Global AIDS Monitoring (GAM) figures carried by who_gho give 172,875 tests at a "
            "positivity of 3.3516 per cent, an implied 5,794 positive tests, equal to the sum of "
            "the 22 provinces"),
    },
}

# (province, indicator, age group) -> the province comparison with PEPFAR
_PROVINCE_NOTES: Dict[Tuple[str, str, str], str] = {
    ("National Capital District", "on_art_count", "all"): (
        "pepfar_agency_snu holds people on ART at USAID-supported sites in National Capital "
        "District (on_art_count_usaid), 6,839 for 2022 and 7,712 for 2023, above the dashboard "
        "counts of 3,165 and 4,474. The cause of the lower dashboard count is NOT YET KNOWN. The "
        "dashboard may count people by province of residence, or the PEPFAR unit for National "
        "Capital District may include sites outside the district"),
    ("National Capital District", "art_initiations", "all"): (
        "pepfar_agency_snu holds people newly started on ART at USAID-supported sites in National "
        "Capital District (art_initiations_usaid), 1,568 for 2022 and 1,608 for 2023, above the "
        "dashboard counts of 696 and 679. The cause of the lower dashboard count is NOT YET KNOWN"),
    ("National Capital District", "new_diagnoses", "all"): (
        "pepfar_agency_snu holds positive tests at USAID-supported sites in National Capital "
        "District (new_diagnoses_usaid), 600 for 2022 and 559 for 2023, below the dashboard "
        "counts of 1,016 and 1,829. The USAID count and the dashboard count come from different "
        "programmes and are never added"),
}


def _col(alias: str, prop: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop},
            "Name": f"{alias}.{prop}"}


def _sum(alias: str, prop: str) -> dict:
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": alias}},
                                                      "Property": prop}},
                            "Function": 0},
            "Name": f"Sum({alias}.{prop})"}


def _number(v) -> Optional[float]:
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else f


def _year(v) -> Optional[int]:
    """Yr arrives as epoch milliseconds at 31 December of the year (1672444800000 is 2022)."""
    try:
        return datetime.fromtimestamp(int(v) / 1000, tz=timezone.utc).year
    except (TypeError, ValueError, OverflowError, OSError):
        return None


class PNGNDoHDashboardConnector(BaseConnector):
    """Papua New Guinea NDoH provincial HIV dashboard, programme counts by province."""

    source_id = "pg_ndoh_dashboard"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Papua New Guinea National Department of Health provincial HIV dashboard "
                   "(Power BI), with HIV tests, positive HIV test results, people on ART by age "
                   "group, ART initiations and mothers on ART under PMTCT for 22 provinces, 2022 "
                   "and 2023 (to-source).")
    country = "PNG"
    request_pause = 1.0
    timeout = 120

    def _query(self, select: list) -> List[list]:
        query = {"Version": 2, "From": [{"Name": "h", "Entity": _TABLE, "Type": 0}],
                 "Select": select}
        body = {"version": "1.0.0",
                "queries": [{"Query": {"Commands": [{"SemanticQueryDataShapeCommand": {
                    "Query": query,
                    "Binding": {"Primary": {"Groupings": [{"Projections": list(range(len(select)))}]},
                                "DataReduction": {"DataVolume": 4,
                                                  "Primary": {"Window": {"Count": 30000}}},
                                "Version": 1}}}]},
                    "QueryId": "",
                    "ApplicationContext": {"DatasetId": _REPORT["dataset_id"],
                                           "Sources": [{"ReportId": _REPORT["report_id"]}]}}],
                "cancelQueries": [], "modelId": _REPORT["model_id"]}
        headers = {"X-PowerBI-ResourceKey": _REPORT["key"],
                   "Content-Type": "application/json;charset=UTF-8",
                   "ActivityId": str(uuid.uuid4()), "RequestId": str(uuid.uuid4())}
        resp = self._request("POST", _QUERY_URL, data=json.dumps(body), headers=headers)
        return decode_dsr(resp.json())

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = {c.upper() for c in countries} if countries else None
        if wanted and self.country not in wanted:
            return
        select = [_col("h", "Yr"), _col("h", "ADM1_EN")] + [_sum("h", c) for c, _, _ in _COLUMNS]
        try:
            raw = self._query(select)
        except Exception as exc:
            log.warning("pg_ndoh_dashboard: the dashboard query failed (%s)", exc)
            return
        table = self._table(raw)
        emitted = 0
        for row in self._rows(table, start_year, end_year):
            emitted += 1
            yield row
        log.info("pg_ndoh_dashboard: emitted %d rows", emitted)

    @staticmethod
    def _table(raw: List[list]) -> Dict[int, Dict[str, Dict[str, Optional[float]]]]:
        """year -> province -> dashboard column -> value, with the gates of the module docstring."""
        table: Dict[int, Dict[str, Dict[str, Optional[float]]]] = defaultdict(dict)
        twice = set()
        for rec in raw:
            if len(rec) != 2 + len(_COLUMNS):
                log.warning("pg_ndoh_dashboard: a row of %d values gives no row (%r)", len(rec), rec)
                continue
            year, province = _year(rec[0]), rec[1]
            if year is None:
                log.warning("pg_ndoh_dashboard: year %r could not be read and gives no row", rec[0])
                continue
            if province not in _PROVINCES:
                log.warning("pg_ndoh_dashboard: province %r is not among the 22 provinces of 15 "
                            "October 2026 and gives no row", province)
                continue
            if province in table[year]:
                twice.add((year, province))
                continue
            table[year][province] = {c: _number(v) for (c, _, _), v in zip(_COLUMNS, rec[2:])}
        for year, province in sorted(twice):
            log.warning("pg_ndoh_dashboard: %s %d appears twice in the answer and gives no row",
                        province, year)
            table[year].pop(province, None)
        return table

    def _rows(self, table: Dict[int, Dict[str, Dict[str, Optional[float]]]],
              start_year: int, end_year: int) -> Iterator[PanelRow]:
        for year in sorted(table):
            if not start_year <= year <= end_year:
                continue
            provinces = table[year]
            full = set(provinces) == set(_PROVINCES)
            if not full:
                log.warning("pg_ndoh_dashboard: %d gives %d of the 22 provinces, so the year gives "
                            "no national row (missing %s)", year, len(provinces),
                            ", ".join(sorted(set(_PROVINCES) - set(provinces))))
            age_ok: Dict[str, bool] = {}
            for province, vals in provinces.items():
                total, parts = vals[_AGE_TOTAL], [vals[c] for c in _AGE_PARTS]
                age_ok[province] = (total is not None and None not in parts
                                    and sum(parts) == total)
                if not age_ok[province] and (total is not None or any(p is not None for p in parts)):
                    log.warning("pg_ndoh_dashboard: %s %d, the age columns of people on ART (%s) "
                                "do not add up to the total (%s), so the province-year gives no "
                                "age row", province, year, parts, total)
            for column, indicator, age in _COLUMNS:
                is_age = column in _AGE_PARTS
                summed, with_value, without_value = 0, 0, []
                for province in _PROVINCES:
                    if province not in provinces:
                        continue
                    value = provinces[province][column]
                    if value is None:
                        without_value.append(province)
                        continue
                    if value < 0:
                        log.warning("pg_ndoh_dashboard: %s %d %s reads %s and gives no row",
                                    province, year, column, value)
                        without_value.append(province)
                        continue
                    if is_age and not age_ok[province]:
                        without_value.append(province)
                        continue
                    summed += value
                    with_value += 1
                    yield self._row(indicator, age, column, year, value, province,
                                    _PROVINCE_NOTES.get((province, indicator, age),
                                                        _NO_PROVINCE_SOURCE), {})
                if not full or not with_value:
                    continue
                if is_age and not all(age_ok.values()):
                    log.warning("pg_ndoh_dashboard: %d %s gives no national row, because the age "
                                "columns do not add up in every province", year, column)
                    continue
                extra = {"national_basis": f"sum of the {with_value} provinces with a value "
                                           "in the dashboard"}
                if without_value:
                    extra["provinces_without_value"] = ", ".join(without_value)
                extra.update(_NATIONAL_YEAR_EXTRA.get((indicator, age, year), {}))
                yield self._row(indicator, age, column, year, summed, "",
                                _NATIONAL_NOTES[(indicator, age)], extra)

    def _row(self, indicator: str, age: str, column: str, year: int, value: float,
             province: str, reconcile_with: str, more: Dict) -> PanelRow:
        spec = CANONICAL_INDICATORS[indicator]
        extra: Dict = {
            "dashboard": _MODEL_NAME,
            "power_bi_model": _REPORT["model_id"],
            "model_refreshed": _MODEL_REFRESHED,
            "table": _TABLE,
            "column": column,
            "definition": _DEFINITIONS[column],
            "reconcile_with": reconcile_with,
        }
        if province:
            extra["admin1_source_label"] = province
        extra.update(more)
        return self.make_row(
            country_iso3="PNG", country_name="Papua New Guinea",
            indicator_id=indicator, year=year, value=value, admin1=province,
            population_group=POP_ALL, age_group=age, unit=spec.unit,
            source_url=_PAGE_URL,
            source_indicator_code=f"{_TABLE}.{column}",
            extra=extra,
        )
