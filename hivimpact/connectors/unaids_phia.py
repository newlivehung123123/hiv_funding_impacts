"""
PHIA connector, connector 32, national values for ages 15 to 49 from the Population-based HIV
Impact Assessment (PHIA) surveys, read from the Power BI model behind the UNAIDS Inequalities
dashboard.

UNAIDS (the Joint United Nations Programme on HIV/AIDS) publishes the Inequalities dashboard at
aidsinfo.unaids.org/inequalities as a public Power BI report. The report's model 367430 holds
survey estimates from several survey programmes, and the PHIA surveys sit in the model as 18
databases named by country and survey year, from CIV2018PHIA to ZWE2020PHIA. The anonymous
querydata route paho_core, paho_hiv, unaids_services and unaids_databook call answered every
query of 15 October 2026 (research/aggregator_sweep_notes.md). The model was last refreshed on
27 November 2024.

What the connector reads.
  - The Source table, filtered to the source "PHIA", for the list of PHIA databases and for the
    dashboard footnote and tabulation plan link of every PHIA measure.
  - The Indicator table, for the dashboard unit and definition of the measures in
    _MEASURES.
  - The Data table, filtered to the national rows of the reviewed PHIA databases for ages 15 to
    49 (Age Domain ID 15_49 with Age ID UNKNOWN) with no split by residence, wealth, education
    or key population. A national row carries the subnational unit id
    "{database} | {ISO3} | UNKNOWN".

Panel indicators and dashboard measures.
  hiv_prevalence_15_49                    HIV_PREVALENCE (PHIA measure hivstatus), age_group
                                          all, because the id name carries the age range, the
                                          rule dhs, unaids_aidsinfo, unaids_naomi and
                                          world_bank follow
  art_coverage_survey_pct                 ART_COVERAGE (PHIA measure art), age_group 15-49
  community_viral_suppression_survey_pct  VLS (PHIA measure vls), age_group 15-49
  hiv_incidence_survey_per_1000           HIV_INCIDENCE (PHIA measure recent_prev), age_group
                                          15-49, with no interval and the standard error in
                                          extra.standard_error

Checks before a row enters the panel.
  - The dashboard unit and definition of the measure must match the unit and definition read on
    15 October 2026 word for word (_DEFINITIONS). A changed definition gives no row for the
    measure, and the connector logs the new wording.
  - The PHIA measure name in the Source Indicator ID column must be the PHIA measure _MEASURES
    names for the dashboard measure.
  - The year must be the year in the database id. The dashboard Year column repeated the year
    in the database id for all 18 databases on 15 October 2026, and the panel year is the year in the database id.
  - The dashboard row with Gender ID UNKNOWN, labelled "Unknown" on the dashboard, enters as
    sex all only where the unweighted observations of the row equal the sum of the unweighted
    observations of the female row and the male row of the same survey and measure. On 15
    October 2026 the sum held for all 85 national survey measures, and every value for females
    and males together lay between the female value and the male value.
  - The interval enters value_lower and value_upper only where the value lies inside the
    interval, the rule of the dhs connector.
  - A survey measure the dashboard lists twice with different values gives no row, and a blank
    estimate gives no row.

What the connector refuses, and why (research/rulings_2026-10-15.md, ruling R13).
  - Ethiopia 2018 (ETH2018PHIA), because the PHIA project records the Ethiopian survey as a
    survey of urban areas only, and an urban survey is not a national value.
  - A PHIA database outside _SURVEYS, which the connector logs, because a new survey needs the
    review the surveys in _SURVEYS had before a value enters the panel.
  - HTS_TEST_RECVRES_1, tested for HIV in the past 12 months with the result received, refused
    under ruling R9 on 16 October 2026. The dashboard definition reads "Percentage of people who
    received an HIV test in the 12 months preceding the survey and received the test results".
    Table 7.3.A of the PHIA tabulation plan removes a respondent with no testing answer from the
    denominator, where the DHS Guide to DHS Statistics keeps the respondent in the denominator of
    HA_CPHT_W_T1R and HA_CPHT_M_T1R as not tested, so a PHIA row would put a second
    denominator under hiv_tested_12m_result_survey_pct. Five surveys (LSO2020, MOZ2021,
    MWI2020, SWZ2021 and ZWE2020) carry no testing value on the dashboard.
  - Ages 15 and over (Age Domain ID 15_AND_UP) and the five-year age groups (SPECIFIED),
    because ruling R13 carries ages 15 to 49, the age range of hiv_prevalence_15_49 and of the
    DHS national testing rows.
  - The splits by wealth, residence and education, the PHIA sampling regions and the KPA (Key
    Populations Atlas) study-site rows, for the reasons ruling R13 records.

The dashboard definition of incidence reads "in the reporting period", and the panel id names
an annual rate. Tables 5.3.A and 5.3.B of the PHIA tabulation plan the dashboard links
(extra.tabulation_plan) print "Annual HIV incidence", which confirms the annual basis (read on
16 October 2026, ruling R13).
"""
from __future__ import annotations

import json
import logging
import uuid
from collections import Counter, defaultdict
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..normalize import code_to_iso3, name_for
from ..schema import AGE_ALL, SEX_ALL, PanelRow, SourceType
from .paho_core import decode_dsr

log = logging.getLogger("hivimpact")

_QUERY_URL = ("https://wabi-north-europe-p-primary-api.analysis.windows.net"
              "/public/reports/querydata?synchronous=true")
# the AIDSinfo page the report is embedded in, written into source_url for a human reader
_PAGE_URL = "https://aidsinfo.unaids.org/inequalities"

# the Inequalities model, read from modelsAndExploration on 15 October 2026
_REPORT = {
    "key": "fc2621c7-afca-4577-92fb-3bc378488766",
    "model_id": 367430,
    "dataset_id": "ce7f4ee3-dc02-4fba-aea5-57993cc405a3",
    "report_id": "be36f762-23b9-491a-ad2f-b5c2662f4007",
}

# PHIA databases reviewed under ruling R13 on 15 October 2026
_SURVEYS = (
    "CIV2018PHIA", "CMR2017PHIA", "KEN2018PHIA", "LSO2017PHIA", "LSO2020PHIA", "MOZ2021PHIA",
    "MWI2016PHIA", "MWI2020PHIA", "NAM2017PHIA", "RWA2019PHIA", "SWZ2017PHIA", "SWZ2021PHIA",
    "TZA2017PHIA", "UGA2017PHIA", "ZMB2016PHIA", "ZWE2016PHIA", "ZWE2020PHIA",
)
_REFUSED = {
    "ETH2018PHIA": "the PHIA project records the Ethiopian survey as a survey of urban areas only",
}
_HELD = {
    "HTS_TEST_RECVRES_1": "refused under ruling R9, because the PHIA tabulation plan removes a "
                          "respondent with no testing answer from the denominator and the DHS "
                          "definition keeps the respondent as not tested",
}

# dashboard measure -> (PHIA measure, panel indicator, age_group)
_MEASURES: Dict[str, Tuple[str, str, str]] = {
    "HIV_PREVALENCE": ("hivstatus", "hiv_prevalence_15_49", AGE_ALL),
    "ART_COVERAGE": ("art", "art_coverage_survey_pct", "15-49"),
    "VLS": ("vls", "community_viral_suppression_survey_pct", "15-49"),
    "HIV_INCIDENCE": ("recent_prev", "hiv_incidence_survey_per_1000", "15-49"),
}
# dashboard measure -> (unit, definition), read from the Indicator table on 15 October 2026
_DEFINITIONS: Dict[str, Tuple[str, str]] = {
    "HIV_PREVALENCE": ("Percent", "Percentage of people who are HIV positive."),
    "ART_COVERAGE": ("Percent", "Percentage of the people living with HIV on antiretroviral "
                                "therapy."),
    "VLS": ("Percent", "Percentage of the people living with HIV with viral load suppression."),
    "HIV_INCIDENCE": ("Per 1000", "Number of people newly infected with HIV in the reporting "
                                  "period per 1000 uninfected population."),
}
_SEX = {"UNKNOWN": SEX_ALL, "FEMALES": "female", "MALES": "male"}
_SPLITS = ("Residence ID", "Wealth ID", "Education ID", "Key Population ID")

# the Data columns of the query, in the order of the query's Select
_DATA_COLUMNS = (
    "Source Database ID", "Year", "Country ISO3", "Indicator ID", "Source Indicator ID",
    "Age ID", "Age Domain ID", "Gender ID", "Estimate", "CI L", "CI U", "SE", "CI Level",
    "CI Method", "Unweighted Observations", "SNU ID",
) + _SPLITS


def _col(alias: str, prop: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop},
            "Name": f"{alias}.{prop}"}


def _in(alias: str, prop: str, values: Iterable[str]) -> dict:
    return {"Condition": {"In": {
        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": alias}},
                                    "Property": prop}}],
        "Values": [[{"Literal": {"Value": "'" + v + "'"}}] for v in values]}}}


def _number(v) -> Optional[float]:
    """A number from the model, which sends the estimates as strings."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f


def _count(v) -> Optional[int]:
    f = _number(v)
    return int(f) if f is not None and f.is_integer() else None


def _national_snu(database: str) -> str:
    return f"{database} | {database[:3]} | UNKNOWN"


class UNAIDSPHIAConnector(BaseConnector):
    source_id = "unaids_phia"
    default_source_type = SourceType.SURVEY
    description = ("PHIA household surveys through the UNAIDS Inequalities dashboard, national "
                   "HIV prevalence, ART coverage, viral suppression and incidence for ages 15-49.")
    request_pause = 1.0
    timeout = 240

    def _query(self, from_: List[Tuple[str, str]], select: list,
               where: Optional[list] = None) -> List[list]:
        query = {"Version": 2,
                 "From": [{"Name": alias, "Entity": entity, "Type": 0} for alias, entity in from_],
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

    def _source_rows(self) -> List[list]:
        """Database, PHIA measure, footnote and tabulation plan link of every PHIA measure."""
        select = [_col("s", p) for p in ("Source Database ID", "Source Indicator ID", "Footnote",
                                         "Link")]
        return self._query([("s", "Source")], select, [_in("s", "Source", ["PHIA"])])

    def _indicator_rows(self) -> List[list]:
        """Dashboard measure, unit and definition of the measures in _MEASURES."""
        select = [_col("i", p) for p in ("Indicator ID", "Unit", "Indicator Description")]
        return self._query([("i", "Indicator")], select,
                           [_in("i", "Indicator ID", sorted(_MEASURES))])

    def _data_rows(self, surveys: List[str], measures: List[str]) -> List[list]:
        """The national rows for ages 15 to 49, in the order of _DATA_COLUMNS."""
        select = [_col("d", p) for p in _DATA_COLUMNS]
        where = [_in("d", "Source Database ID", surveys),
                 _in("d", "Indicator ID", measures),
                 _in("d", "SNU ID", [_national_snu(s) for s in surveys]),
                 _in("d", "Age Domain ID", ["15_49"]),
                 _in("d", "Age ID", ["UNKNOWN"])]
        where += [_in("d", split, ["UNKNOWN"]) for split in _SPLITS]
        return self._query([("d", "Data")], select, where)

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2015,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        end_year = min(end_year or date.today().year, date.today().year)

        # -- the PHIA databases and footnotes ------------------------------------------------
        footnotes: Dict[Tuple[str, str], Tuple[str, str]] = {}
        databases: set = set()
        for database, measure, footnote, link in self._source_rows():
            if not database:
                continue
            databases.add(str(database))
            footnotes[(str(database), str(measure))] = (str(footnote or ""), str(link or ""))
        unreviewed = sorted(databases - set(_SURVEYS) - set(_REFUSED))
        if unreviewed:
            log.warning("unaids_phia: %d PHIA databases outside the reviewed list give no row "
                        "until reviewed (%s)", len(unreviewed), ", ".join(unreviewed))
        absent = sorted(set(_SURVEYS) - databases)
        if absent:
            log.warning("unaids_phia: %d reviewed PHIA databases are missing from the Source "
                        "table (%s)", len(absent), ", ".join(absent))
        for database in sorted(set(_REFUSED) & databases):
            log.info("unaids_phia: %s gives no row, %s", database, _REFUSED[database])
        surveys = [s for s in _SURVEYS if s in databases
                   and (wanted is None or s[:3] in wanted)
                   and start_year <= int(s[3:7]) <= end_year]
        if not surveys:
            log.info("unaids_phia: no reviewed PHIA survey matches the countries and years asked")
            return

        # -- the dashboard definitions -------------------------------------------------------
        read = {str(r[0]): (r[1], r[2]) for r in self._indicator_rows()}
        measures = []
        for measure in sorted(_MEASURES):
            if read.get(measure) != _DEFINITIONS[measure]:
                log.warning("unaids_phia: the dashboard unit and definition of %s read %r "
                            "against the reviewed %r, and the measure gives no row", measure,
                            read.get(measure), _DEFINITIONS[measure])
                continue
            measures.append(measure)
        for measure, reason in _HELD.items():
            log.info("unaids_phia: %s gives no row, %s", measure, reason)
        if not measures:
            return

        # -- the national rows ---------------------------------------------------------------
        skipped: Counter = Counter()
        groups: Dict[Tuple[str, str, str], List[dict]] = defaultdict(list)
        for rec in self._data_rows(surveys, measures):
            r = dict(zip(_DATA_COLUMNS, rec))
            database, measure = str(r["Source Database ID"]), str(r["Indicator ID"])
            if database not in surveys or measure not in measures:
                skipped["database or measure outside the query"] += 1
                continue
            if str(r["Source Indicator ID"]) != _MEASURES[measure][0]:
                skipped["PHIA measure name differs from the reviewed name"] += 1
                continue
            if (r["Age Domain ID"] != "15_49" or r["Age ID"] != "UNKNOWN"
                    or r["SNU ID"] != _national_snu(database)
                    or any(r[split] != "UNKNOWN" for split in _SPLITS)):
                skipped["row outside the national rows for ages 15 to 49"] += 1
                continue
            if r["Country ISO3"] != database[:3] or code_to_iso3(database[:3]) != database[:3]:
                skipped["country code differs from the database id"] += 1
                continue
            if _count(r["Year"]) != int(database[3:7]):
                skipped["year differs from the year in the database id"] += 1
                continue
            if r["Gender ID"] not in _SEX:
                skipped["sex outside females, males and the total of females and males"] += 1
                continue
            groups[(database, measure, str(r["Gender ID"]))].append(r)

        chosen: Dict[Tuple[str, str, str], dict] = {}
        conflicts: List[str] = []
        for key, recs in groups.items():
            if len({(x["Estimate"], x["CI L"], x["CI U"], x["SE"]) for x in recs}) > 1:
                conflicts.append(" ".join(key))
                continue
            chosen[key] = recs[0]

        emitted: Counter = Counter()
        for (database, measure, gender), r in sorted(chosen.items()):
            phia, canonical, age_group = _MEASURES[measure]
            observations = _count(r["Unweighted Observations"])
            if gender == "UNKNOWN":
                female = chosen.get((database, measure, "FEMALES"))
                male = chosen.get((database, measure, "MALES"))
                parts = [None if x is None else _count(x["Unweighted Observations"])
                         for x in (female, male)]
                if observations is None or None in parts or observations != sum(parts):
                    skipped["total row whose respondents differ from the sum of the female and male "
                            "respondents"] += 1
                    continue
            value = _number(r["Estimate"])
            if value is None:
                skipped["blank estimate"] += 1
                continue
            lower, upper = _number(r["CI L"]), _number(r["CI U"])
            if lower is None or upper is None or not lower <= value <= upper:
                if lower is not None or upper is not None:
                    skipped["interval dropped, value outside or a bound missing"] += 1
                lower = upper = None
            footnote, link = footnotes.get((database, phia), ("", ""))
            iso3 = database[:3]
            yield self.make_row(
                country_iso3=iso3, country_name=name_for(iso3), indicator_id=canonical,
                year=int(database[3:7]), value=value, value_lower=lower, value_upper=upper,
                sex=_SEX[gender], age_group=age_group,
                unit=CANONICAL_INDICATORS[canonical].unit, source_url=_PAGE_URL,
                source_indicator_code=f"{database} | {phia}",
                extra={"survey": "PHIA",
                       "phia_database": database,
                       "dashboard_indicator": measure,
                       "phia_indicator": phia,
                       "indicator_definition": _DEFINITIONS[measure][1],
                       "footnote": footnote,
                       "tabulation_plan": link,
                       "ci_level": r["CI Level"],
                       "ci_method": r["CI Method"],
                       "standard_error": _number(r["SE"]),
                       "unweighted_observations": observations,
                       "survey_age_range": "15-49",
                       "year_basis": "the year in the PHIA database id, which the dashboard "
                                     "Year column repeats",
                       "inequalities_model": str(_REPORT["model_id"])},
            )
            emitted[canonical] += 1

        for canonical in sorted({c for _, c, _ in _MEASURES.values()}):
            log.info("unaids_phia: %-38s -> %d rows", canonical, emitted.get(canonical, 0))
        if conflicts:
            log.warning("unaids_phia: %d survey measures listed twice with different values give "
                        "no row (%s)", len(conflicts), ", ".join(conflicts))
        if skipped:
            log.info("unaids_phia: rows not written, %s",
                     ", ".join(f"{k} {n}" for k, n in sorted(skipped.items())))
