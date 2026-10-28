"""
DHS Program (Demographic and Health Surveys) connector.

API (VERIFIED 2026-07-18): https://api.dhsprogram.com/rest/dhs/data
  ?indicatorIds=<id>&f=json&perpage=1000&page=N
  -> {TotalPages, Data:[{CountryName, SurveyYear, Value, IndicatorId, ...}]}

DHS is a SURVEY source (source_type=survey), an independent measurement of HIV prevalence
with no model behind the figures, and the DHS rows triangulate the UNAIDS and WHO modelled
estimates. Adrian named DHS in section 4. HIV biomarker coverage in Southeast Asia is thin
(Cambodia 2005), so DHS gives few rows for the Southeast Asia pilot and many for Phase 3
(Africa).

Sub-national rows (added 13 October 2026, Jason's approval of the same day, on condition of
unchanged national rows). The national pass below is untouched. A second pass asks
the same three indicators with breakdown=subnational and writes the survey regions into
admin1, with the DHS confidence interval in value_lower and value_upper.
  - Only regions of DHS level rank 1 are written. A survey's level-rank-1 regions are the
    survey's own first regional level, which can differ from the country's administrative
    first level (Haiti splits the West department into the metropolitan area and "Rest of
    West", Tanzania's level-rank-1 rows are zones, with the regions at level rank 2).
  - Level-rank-2 rows are skipped, because in Tanzania and Sierra Leone the level-rank-2 rows
    are nested inside level-rank-1 regions, and in Guinea the level-rank-2 rows are a second
    grouping of the same sample (natural regions beside administrative regions). Writing the
    level-rank-2 rows would count the same respondents twice.
  - Rows with no level rank are skipped. The DHS API leaves the level rank empty on groupings
    of level-rank-1 regions (Haiti "Grande-Anse/Nippes"), on regions of an earlier boundary
    ("Northern (before 2017)") and on strata outside the regional design (Haiti 2012 "Camps").
  - The leading dots DHS uses to indent child regions ("..Grande-Anse") are stripped.
  - In some surveys the level-rank-1 regions cover less than the national sample. The DRC
    survey of 2007 has Kinshasa alone at level rank 1, with the other provinces in
    groupings of no level rank, and the India survey of 2006 has six states.
    extra.denominator_unweighted carries the number of people tested in every region.

Region check (added 15 October 2026 under research/rulings_2026-10-15.md, ruling R9, for the
prevalence regions and the testing regions alike). The national DHS value carries the label
"Total 15-49", the region rows carry no age label, and the men's samples of many surveys run to
54, 59 or 64. The breakdown=all answer for men tested in the past 12 months holds a "Total 15-49"
row beside a "Total" row of every man interviewed, so a DHS tabulation can cover ages outside 15
to 49. The connector checks the age range of the region rows through the unweighted
denominators, the whole counts of respondents behind every value, so every comparison is exact.
The level-rank-1 rows of a survey and indicator enter in three cases, and extra.age_basis names
the case.
  - The level-rank-1 regions hold every respondent of the national 15-49 row.
  - The level-rank-1 regions hold fewer respondents, and the top-level region rows (the rows
    the API prints with no leading dots, at any level rank) hold every respondent of the
    national 15-49 row, so the region tabulation divides the 15-49 sample. Haiti 2012 passes
    the top-level test, with the camps at no level rank, and so does Chad 2014, with N'Djamena and
    eight zones at no level rank above the provinces, for prevalence and for testing. For
    prevalence the Democratic Republic of the Congo 2007 passes with Kinshasa beside three
    groupings at no level rank, the Democratic Republic of the Congo 2023 passes for women and
    for women and men together, and Burundi 2016, Ghana 2014, Mali 2006 and Senegal 2005, 2010
    and 2017 pass for men, where the API answers no prevalence row for some regions (for example
    Kanem and Barh El Gazal in Chad 2014).
  - The level-rank-1 regions hold fewer respondents and the survey interviewed ages 15 to 49
    only (women and men for the prevalence rows of women and men together), so no region value
    can cover other ages. Cambodia 2005 passes the 15-49 test, and for women Angola 2023, India
    2006, Kenya 2003 and Niger 2012.
Every other survey gives no region row for the indicator. With the DHS API answers of 15
October 2026 the check refuses 146 prevalence region rows, where the regions hold fewer
respondents than the national row in a survey of wider ages and the top-level rows do not add up
to the national row. 30 rows are for women and men together (Angola 2023, India 2006 and Kenya
2003) and 116 rows are for men (Angola 2015 and 2023, Burkina Faso 2003, the Democratic Republic
of the Congo 2013 and 2023, Ethiopia 2005 and 2016, Guinea 2005, India 2006, Kenya 2003 and Niger
2012). Every women's prevalence region passes the check. For testing the check refuses the
regions of India 2020, where the level-rank-1 rows hold the region "Jammu, Kashmir & Ladakh"
beside the regions "..Jammu & Kashmir" and "..Ladakh" and so count 3,738 women and 3,201 men
twice, the men's regions of Uganda 2006, holding twice the respondents of the national row, and
the regions of Mali 2023, holding fewer respondents than the national row in a survey of ages 15
to 64 with no top-level proof, for women and for men.
  - Mislabelled regions. The Sierra Leone 2013 survey answers three level-rank-1 regions,
    Eastern, Northern (before 2017) and Southern, holding every respondent of the national row,
    with no row for the Western Area, which holds the capital Freetown and has a row in the 2008
    and 2019 surveys, and no row for Moyamba district. A Sierra Leone 2013 region label therefore
    covers a part of the country the label does not name, and _REGIONS_REFUSED keeps every
    Sierra Leone 2013 region row out of the panel, for prevalence and for testing.
The national prevalence rows stay unchanged.

Testing in the past 12 months with the result received (added 15 October 2026 under
research/rulings_2026-10-15.md, ruling R9). DHS indicators HA_CPHT_W_T1R (women) and
HA_CPHT_M_T1R (men), "Percentage of women (men) who received an HIV test in the 12 months
preceding the interview and received the test results", with the denominator "Women
interviewed" ("Men interviewed"), enter hiv_tested_12m_result_survey_pct, national and at level
rank 1 under the region check above. The rules of the testing pass, from the DHS API answers of
15 October 2026.
  - Age. The national value the API returns by default carries the label "Total 15-49" in all
    147 women's and 148 men's rows, although the men's samples of 116 surveys run to 54, 59 or 64.
    The connector writes the age range of the label into age_group and requires the survey's own
    age range for the sex (MinAgeWomen and MaxAgeWomen, MinAgeMen and MaxAgeMen in the DHS
    surveys list) to cover the label range. extra.survey_age_range carries the survey's own range.
  - Sample universe. A survey interviewing ever-married respondents only (UniverseOfWomen
    "Ever Married Women", UniverseOfMen "Ever Married Men") gives a share of ever-married
    respondents and not a share of all respondents, so the connector writes no row for the
    survey and sex. Afghanistan 2015 and Pakistan 2017 are refused for women and for men.
  - Region rows of a survey with no national 15-49 row written are refused, because the age
    range cannot be checked (women's rows for Sierra Leone 2013 and Uganda 2006).
  - Two surveys in a single year. Uganda carries a DHS survey and an AIDS Indicator Survey
    (AIS) for 2011, with 41.7% of women tested in the DHS survey against 24.2% in the AIS, and
    30.7% of men against 23.2%. The panel key holds no survey column, so a country-year with two
    surveys gives no national row and no region row for the sex. The Uganda 2011 DHS regions
    also hold about twice the respondents of the national row.
  - The DHS API publishes no confidence interval for the national or region testing values, so
    value_lower and value_upper stay empty, and extra.denominator_weighted and
    extra.denominator_unweighted carry the sample sizes.

Rows from the DHS API answers of 15 October 2026, in an offline test with the network blocked.
252 national prevalence rows, equal to the panel, and 2,115 prevalence region rows, 155 fewer
than the panel of 15 October 2026 (146 under the region check and nine for Sierra Leone 2013).
287 national testing rows (143 women, 144 men) and 2,959 testing region rows (1,505 women,
1,454 men), all with age_group 15-49, from 2003 to 2025.

Knowledge and condom use (added 16 October 2026 under research/rulings_2026-10-15.md, ruling
R22, for consistency with the Pacific Data Hub connector pacific_data_hub). Six DHS indicators
enter the two survey ids of ruling R22 through the testing pass above, with the same rules for
age, sample universe, two surveys in a single year and region rows.
  - hiv_comprehensive_knowledge_survey_pct takes HA_CKNA_W_CKA and HA_CKNA_M_CKA
    ("Comprehensive correct knowledge about AIDS", denominators "Women interviewed" and "Men
    interviewed", national label "Total 15-49") and HA_CKNY_W_CKA and HA_CKNY_M_CKA (the same
    measure among young women and men, denominators "Women age 15-24" and "Men age 15-24"). The
    national rows of HA_CKNY carry the bare label "Total", so DHS_SURVEY_INDICATORS gives the
    age range 15-24 from the denominator, and a HA_CKNY row with any other label gives no row.
    The DHS API answers no region row for HA_CKNY.
  - condom_last_higher_risk_sex_survey_pct takes HA_HRSX_W_CND and HA_HRSX_M_CND ("Condom use
    at last higher risk sex (with a non-marital, non-cohabiting partner)", denominators women
    and men who had sex with a non-marital, non-cohabiting partner in the last 12 months).
  - Sample size. DHS reports print a value on 25 to 49 unweighted cases in parentheses and
    suppress a value on fewer than 25 cases. A value on fewer than 25 cases gives no row, and a
    value on 25 to 49 cases carries extra.dhs_precision. The DHS API answers of 16 October 2026
    hold no value on fewer than 25 cases, and 391 condom values on 25 to 49 cases (seven
    national values for women and 384 region values). No prevalence or testing row rests on fewer
    than 50 cases, so the rule changes no earlier row.
  - The Pacific Demographic and Health Surveys of the pacific_data_hub connector are outside the
    DHS API, which holds Papua New Guinea 2017 and Timor-Leste 2009 and 2016 for the Pacific, so
    the two sources share no country.
Offline test on the DHS API answers of 16 October 2026 with the network blocked, 6,438 new rows
over 66 countries from 2000 to 2025 and no repeated key. Knowledge gives 593 national rows (145
women and 132 men at ages 15-49, 166 women and 150 men at ages 15-24) and 2,842 region rows
(1,551 women, 1,291 men, all at ages 15-49). Condom use gives 335 national rows (174 women, 161
men, at ages 15-49) and 2,668 region rows (1,459 women, 1,209 men). The prevalence and testing
rows are identical to the rows before the change.
"""
from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, Iterator, Optional

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_BASE = "https://api.dhsprogram.com/rest/dhs/data"

# DHS indicator id -> (canonical_id, sex). All are survey-measured HIV prevalence (%).
DHS_INDICATORS: Dict[str, tuple] = {
    "HA_HIVP_B_HIV": ("hiv_prevalence_15_49", "all"),
    "HA_HIVP_W_HIV": ("hiv_prevalence_15_49", "female"),
    "HA_HIVP_M_HIV": ("hiv_prevalence_15_49", "male"),
}

# DHS indicator id -> (canonical_id, sex, the sex word in the DHS survey fields, the DHS
# denominator, the age range of an indicator whose national row carries the bare label "Total"),
# rulings R9 and R22. The age range is None where the national row names the range ("Total 15-49").
DHS_SURVEY_INDICATORS: Dict[str, tuple] = {
    "HA_CPHT_W_T1R": ("hiv_tested_12m_result_survey_pct", "female", "Women",
                      "Women interviewed", None),
    "HA_CPHT_M_T1R": ("hiv_tested_12m_result_survey_pct", "male", "Men",
                      "Men interviewed", None),
    "HA_CKNA_W_CKA": ("hiv_comprehensive_knowledge_survey_pct", "female", "Women",
                      "Women interviewed", None),
    "HA_CKNA_M_CKA": ("hiv_comprehensive_knowledge_survey_pct", "male", "Men",
                      "Men interviewed", None),
    "HA_CKNY_W_CKA": ("hiv_comprehensive_knowledge_survey_pct", "female", "Women",
                      "Women age 15-24", (15, 24)),
    "HA_CKNY_M_CKA": ("hiv_comprehensive_knowledge_survey_pct", "male", "Men",
                      "Men age 15-24", (15, 24)),
    "HA_HRSX_W_CND": ("condom_last_higher_risk_sex_survey_pct", "female", "Women",
                      "Women who had sex with a non-marital, non-cohabiting partner in the last "
                      "12 months", None),
    "HA_HRSX_M_CND": ("condom_last_higher_risk_sex_survey_pct", "male", "Men",
                      "Men who had sex with a non-marital, non-cohabiting partner in the last "
                      "12 months", None),
}
# DHS reports print a value on 25 to 49 unweighted cases in parentheses and suppress a value on
# fewer than 25 cases. The DHS API answers of 16 October 2026 hold no value on fewer than 25 cases.
_FEW_CASES = 25
_CAUTION_CASES = 50
_SURVEYS = "https://api.dhsprogram.com/rest/dhs/surveys?f=json&perpage=1000"

# Surveys whose level-rank-1 region labels do not match the samples the labels describe.
_REGIONS_REFUSED = {
    "SL2013DHS": "no Western Area row and no Moyamba district row, while the three regions "
                 "Eastern, Northern (before 2017) and Southern hold every respondent of the "
                 "national row",
}
_TOTAL_LABEL = re.compile(r"^Total (\d+)-(\d+)$")


class DHSConnector(BaseConnector):
    source_id = "dhs"
    default_source_type = SourceType.SURVEY
    description = ("DHS Program API, survey-measured HIV prevalence, HIV testing in the past 12 "
                   "months with the result received, comprehensive HIV knowledge and condom use "
                   "at last higher-risk sex, national and by survey region.")
    request_pause = 0.3

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None
        national: Dict[tuple, tuple] = {}

        for dhs_id, (canonical, sex) in DHS_INDICATORS.items():
            page = 1
            while True:
                url = f"{_BASE}?indicatorIds={dhs_id}&f=json&perpage=1000&page={page}"
                payload = self.get_json(url)
                data = payload.get("Data", [])
                for r in data:
                    national[(dhs_id, r.get("SurveyId", ""))] = (
                        r.get("CharacteristicLabel") or "", _num(r.get("DenominatorUnweighted")))
                    iso3 = to_iso3(r.get("CountryName", ""))
                    if not iso3 or (wanted and iso3 not in wanted):
                        continue
                    try:
                        year = int(r["SurveyYear"])
                        value = float(r["Value"])
                    except (TypeError, ValueError, KeyError):
                        continue
                    if year < start_year or year > end_year:
                        continue
                    yield self.make_row(
                        country_iso3=iso3,
                        country_name=r.get("CountryName", ""),
                        indicator_id=canonical,
                        year=year,
                        value=value,
                        sex=sex,
                        unit="percent",
                        source_url=url,
                        source_indicator_code=dhs_id,
                        extra={"survey": r.get("SurveyType", ""), "dhs_indicator": r.get("Indicator", "")},
                    )
                if page >= int(payload.get("TotalPages", 1) or 1):
                    break
                page += 1

        surveys = {r.get("SurveyId"): r for r in self.get_json(_SURVEYS).get("Data", [])}
        yield from self._fetch_subnational(wanted, start_year, end_year, national, surveys)
        yield from self._fetch_survey_measures(wanted, start_year, end_year, surveys)

    def _fetch_subnational(self, wanted, start_year: int, end_year: int,
                           national: Dict[tuple, tuple], surveys: Dict[str, dict]
                           ) -> Iterator[PanelRow]:
        """Survey regions of DHS level rank 1, one row per region, survey and indicator."""
        skipped: Counter = Counter()
        for dhs_id, (canonical, sex) in DHS_INDICATORS.items():
            url = f"{_BASE}?indicatorIds={dhs_id}&breakdown=subnational&f=json&perpage=1000"
            by_survey: Dict[str, list] = defaultdict(list)
            for r in self._pages(url):
                iso3 = to_iso3(r.get("CountryName", ""))
                if not iso3 or (wanted and iso3 not in wanted):
                    continue
                if r.get("CharacteristicCategory") != "Region":
                    skipped["not a region"] += 1
                    continue
                by_survey[r.get("SurveyId", "")].append(r)
            words = {"female": ("Women",), "male": ("Men",), "all": ("Women", "Men")}[sex]
            for survey_id, rows in sorted(by_survey.items()):
                ranked = [r for r in rows if _rank(r) == "1"]
                for r in rows:
                    if _rank(r) != "1":
                        skipped[f"level rank {_rank(r) or 'empty'}"] += 1
                if not ranked:
                    continue
                if survey_id in _REGIONS_REFUSED:
                    skipped["survey with mislabelled regions"] += len(ranked)
                    continue
                label, nat_unweighted = national.get((dhs_id, survey_id), ("", None))
                if label != "Total 15-49":
                    skipped["survey with no national 15-49 row"] += len(ranked)
                    continue
                survey = surveys.get(survey_id) or {}
                only = all(_ages(survey, w) == (15, 49) for w in words)
                refusal, basis = _region_check(rows, nat_unweighted, only, "15-49")
                if refusal:
                    skipped[refusal] += len(ranked)
                    log.info("dhs: %s %s gives no region row, %s", survey_id, dhs_id, refusal)
                    continue
                for r in ranked:
                    region = (r.get("CharacteristicLabel") or "").lstrip(".").strip()
                    if not region:
                        skipped["no region name"] += 1
                        continue
                    try:
                        year = int(r["SurveyYear"])
                        value = float(r["Value"])
                    except (TypeError, ValueError, KeyError):
                        skipped["no value"] += 1
                        continue
                    if year < start_year or year > end_year:
                        continue
                    lower, upper = _num(r.get("CILow")), _num(r.get("CIHigh"))
                    if lower is None or upper is None or not lower <= value <= upper:
                        if lower is not None or upper is not None:
                            skipped["interval dropped, value outside or one bound missing"] += 1
                        lower = upper = None
                    yield self.make_row(
                        country_iso3=to_iso3(r.get("CountryName", "")),
                        country_name=r.get("CountryName", ""),
                        admin1=region,
                        indicator_id=canonical,
                        year=year,
                        value=value,
                        value_lower=lower,
                        value_upper=upper,
                        sex=sex,
                        unit="percent",
                        source_url=url,
                        source_indicator_code=dhs_id,
                        extra={"survey": r.get("SurveyType", ""),
                               "dhs_indicator": r.get("Indicator", ""),
                               "dhs_survey_id": r.get("SurveyId", ""),
                               "dhs_region_id": r.get("RegionId", ""),
                               "dhs_level_rank": 1,
                               "denominator_unweighted": _num(r.get("DenominatorUnweighted")),
                               "age_basis": basis},
                    )
        if skipped:
            log.info("dhs: sub-national rows not written, %s",
                     ", ".join(f"{k} {n}" for k, n in sorted(skipped.items())))

    def _pages(self, url: str) -> Iterator[dict]:
        """Every record of a DHS data query, over all pages."""
        page = 1
        while True:
            payload = self.get_json(f"{url}&page={page}")
            yield from payload.get("Data", [])
            if page >= int(payload.get("TotalPages", 1) or 1):
                break
            page += 1

    def _fetch_survey_measures(self, wanted, start_year: int, end_year: int,
                               surveys: Dict[str, dict]) -> Iterator[PanelRow]:
        """The indicators of DHS_SURVEY_INDICATORS, national and level rank 1 (rulings R9 and R22)."""
        skipped: Dict[str, Counter] = defaultdict(Counter)
        for dhs_id, (canonical, sex, word, denominator, fixed) in DHS_SURVEY_INDICATORS.items():
            skip = skipped[canonical]
            url = f"{_BASE}?indicatorIds={dhs_id}&f=json&perpage=1000"
            national: Dict[str, tuple] = {}
            candidates = []
            for r in self._pages(url):
                iso3 = to_iso3(r.get("CountryName", ""))
                if not iso3 or (wanted and iso3 not in wanted):
                    continue
                survey_id = r.get("SurveyId", "")
                text = r.get("CharacteristicLabel") or ""
                ages = _TOTAL_LABEL.match(text)
                if fixed is None and ages:
                    low, high = int(ages.group(1)), int(ages.group(2))
                elif fixed is not None and text == "Total":
                    low, high = fixed
                else:
                    skip["national row with a label unlike the age range of the indicator"] += 1
                    log.info("dhs: %s %s refused, national label %r", survey_id, dhs_id, text)
                    continue
                survey = surveys.get(survey_id)
                if survey is None:
                    skip["survey not in the DHS surveys list"] += 1
                    continue
                universe = survey.get(f"UniverseOf{word}") or ""
                if universe != f"All {word}":
                    skip[f"universe {universe or 'empty'}"] += 1
                    log.info("dhs: %s %s refused, the sample universe is %r", survey_id, dhs_id,
                             universe)
                    continue
                s_low, s_high = _num(survey.get(f"MinAge{word}")), _num(survey.get(f"MaxAge{word}"))
                if s_low is None or s_high is None or not (s_low <= low and high <= s_high):
                    skip["survey age range does not cover the label range"] += 1
                    continue
                cases = _num(r.get("DenominatorUnweighted"))
                if cases is None or cases < _FEW_CASES:
                    skip["fewer than 25 unweighted cases or no case count"] += 1
                    continue
                try:
                    year = int(r["SurveyYear"])
                    value = float(r["Value"])
                except (TypeError, ValueError, KeyError):
                    skip["no value"] += 1
                    continue
                if year < start_year or year > end_year:
                    continue
                candidates.append((iso3, year, value, (low, high), r, survey))
            per_year = Counter((c[0], c[1]) for c in candidates)
            same_year = set()
            for iso3, year, value, label, r, survey in candidates:
                survey_id = r.get("SurveyId", "")
                age_group = f"{label[0]}-{label[1]}"
                if per_year[(iso3, year)] > 1:
                    same_year.add(survey_id)
                    skip["national row of a country-year with two surveys"] += 1
                    log.info("dhs: %s %s refused, %s has %d surveys in %d", survey_id, dhs_id,
                             iso3, per_year[(iso3, year)], year)
                    continue
                national[survey_id] = (label, _ages(survey, word), _num(r.get("DenominatorUnweighted")))
                yield self.make_row(
                    country_iso3=iso3, country_name=r.get("CountryName", ""),
                    indicator_id=canonical, year=year, value=value,
                    sex=sex, age_group=age_group, unit="percent",
                    source_url=url, source_indicator_code=dhs_id,
                    extra=self._survey_extra(r, survey, word, denominator),
                )

            regions: Dict[str, list] = defaultdict(list)
            sub_url = f"{_BASE}?indicatorIds={dhs_id}&breakdown=subnational&f=json&perpage=5000"
            for r in self._pages(sub_url):
                if r.get("CharacteristicCategory") == "Region":
                    regions[r.get("SurveyId", "")].append(r)
            for survey_id, all_rows in sorted(regions.items()):
                rows = [r for r in all_rows if _rank(r) == "1"]
                if not rows:
                    continue
                if survey_id in same_year:
                    skip["region rows of a country-year with two surveys"] += len(rows)
                    continue
                if survey_id in _REGIONS_REFUSED:
                    skip["region rows of a survey with mislabelled regions"] += len(rows)
                    continue
                if survey_id not in national:
                    skip["region rows of a survey with no national row written"] += len(rows)
                    continue
                label, ages, nat_unweighted = national[survey_id]
                age_group = f"{label[0]}-{label[1]}"
                refusal, basis = _region_check(all_rows, nat_unweighted, ages == label, age_group)
                if refusal:
                    skip[refusal] += len(rows)
                    log.info("dhs: %s %s gives no region row, %s", survey_id, dhs_id, refusal)
                    continue
                survey = surveys[survey_id]
                for r in rows:
                    iso3 = to_iso3(r.get("CountryName", ""))
                    region = (r.get("CharacteristicLabel") or "").lstrip(".").strip()
                    if not iso3 or not region:
                        skip["no country or region name"] += 1
                        continue
                    cases = _num(r.get("DenominatorUnweighted"))
                    if cases is None or cases < _FEW_CASES:
                        skip["region row on fewer than 25 unweighted cases or no case count"] += 1
                        continue
                    try:
                        year = int(r["SurveyYear"])
                        value = float(r["Value"])
                    except (TypeError, ValueError, KeyError):
                        skip["no value"] += 1
                        continue
                    if year < start_year or year > end_year:
                        continue
                    extra = self._survey_extra(r, survey, word, denominator)
                    extra.update({"dhs_region_id": r.get("RegionId", ""), "dhs_level_rank": 1,
                                  "age_basis": basis})
                    yield self.make_row(
                        country_iso3=iso3, country_name=r.get("CountryName", ""),
                        admin1=region, indicator_id=canonical, year=year, value=value,
                        sex=sex, age_group=age_group, unit="percent",
                        source_url=sub_url, source_indicator_code=dhs_id, extra=extra,
                    )
        for canonical, skip in skipped.items():
            if skip:
                log.info("dhs: %s rows not written, %s", canonical,
                         ", ".join(f"{k} {n}" for k, n in sorted(skip.items())))

    @staticmethod
    def _survey_extra(r: dict, survey: dict, word: str, denominator: str) -> dict:
        extra = {"survey": r.get("SurveyType", ""),
                 "dhs_indicator": r.get("Indicator", ""),
                 "dhs_survey_id": r.get("SurveyId", ""),
                 "dhs_denominator": denominator,
                 "sample_universe": survey.get(f"UniverseOf{word}", ""),
                 "survey_age_range": f"{survey.get(f'MinAge{word}')}-{survey.get(f'MaxAge{word}')}",
                 "denominator_weighted": _num(r.get("DenominatorWeighted")),
                 "denominator_unweighted": _num(r.get("DenominatorUnweighted"))}
        if (extra["denominator_unweighted"] or 0) < _CAUTION_CASES:
            extra["dhs_precision"] = "25 to 49 unweighted cases, printed in parentheses in DHS reports"
        return extra


def _rank(r: dict) -> str:
    return str(r.get("LevelRank", "") or "").strip()


def _ages(survey: dict, word: str) -> Optional[tuple]:
    """The survey's own age range for women or men, from the DHS surveys list."""
    low, high = _num(survey.get(f"MinAge{word}")), _num(survey.get(f"MaxAge{word}"))
    return None if low is None or high is None else (int(low), int(high))


def _region_check(rows, nat_unweighted, ages_match_label: bool, age_group: str):
    """(refusal, age basis) for the region rows of a survey and indicator.

    rows holds every region row of the survey at every level rank. The unweighted denominators
    are whole counts of respondents, so every comparison is exact. The refusal is None when the
    level-rank-1 rows enter.
    """
    ranked = [r for r in rows if _rank(r) == "1"]
    counts = [_num(r.get("DenominatorUnweighted")) for r in ranked]
    if nat_unweighted is None or any(c is None for c in counts):
        return "an unweighted denominator is missing", ""
    total = sum(counts)
    if total == nat_unweighted:
        return None, (f"the level-rank-1 regions hold every respondent of the national "
                      f"{age_group} row")
    if total > nat_unweighted:
        return "region denominators above the national denominator", ""
    top = [_num(r.get("DenominatorUnweighted")) for r in rows
           if not (r.get("CharacteristicLabel") or "").startswith(".")]
    if top and None not in top and sum(top) == nat_unweighted:
        return None, (f"the top-level region rows hold every respondent of the national "
                      f"{age_group} row")
    if ages_match_label:
        return None, f"the survey interviewed ages {age_group} only"
    return "region denominators below the national denominator with no proof of the age range", ""


def _num(x) -> Optional[float]:
    """A DHS numeric field as a float, or None when the field is empty or not a number."""
    try:
        return None if x in (None, "") else float(x)
    except (TypeError, ValueError):
        return None
