"""
UNAIDS sub-national estimates connector, connector 31, the Naomi model's December estimates for
31 countries, at the national level and at the first administrative level below the country.

Naomi is the small-area model UNAIDS (the Joint United Nations Programme on HIV/AIDS) and the
country teams run beside Spectrum, the model behind the national estimates, to split a country's
estimates across provinces and districts. UNAIDS publishes the results in the viewer "HIV
sub-national estimates viewer" (https://naomi-spectrum.unaids.org/), a React page whose script
names the API https://nmviewerserver.azurewebsites.net/api/v1 and the client release of
10 August 2026. The API answers plain GET calls with JSON and no sign-in. The page builds a
download link on the route /data, and the connector reads the JSON route /areas the map uses.

What the API holds, read on 14 October 2026 (research/aggregator_sweep_notes.md).
  - /countries lists 31 countries, 30 in sub-Saharan Africa and Haiti. Two codes fall outside
    ISO 3166. Zimbabwe is listed under ZIM, and the areas of Zimbabwe carry the ISO code ZWE.
    Eswatini is listed under ESW, and the ISO code for Eswatini is SWZ. The connector maps both
    codes after checking the country name the API gives.
  - /options lists, for every country, 25 indicators, 33 age groups, three sex values (both,
    male, female), the area levels and the periods. Malawi lists two further indicators,
    art_report ("Reported ART number") and art_report_rel_bias ("ART reporting bias
    (relative)"). Every country lists the period 2025-4, the fourth quarter of 2025, followed by
    the projections 2026-3 and 2027-3, and Malawi and South Africa add 2028-3. Every country also
    lists one or two earlier periods, the quarters of the household surveys the model was fitted
    to (2016-1 and 2020-3 for Malawi, 2018-4 for Kenya).
  - /areas returns, for one country, indicator, age group, period, sex and area level, the
    national value and the value of every area at the level asked for, each with lower, mean
    and upper. For all 31 countries the means of the level-1 areas add up to the national mean
    of PLHIV in December 2025, within one part in 10,000, and the connector logs every count
    whose areas do not add up.
  - The API refused about one connection in 18 on 14 October 2026 (seven of 126 requests), and
    a second attempt succeeded every time. BaseConnector retries a refused connection.

The national values are the 2026 estimates round. Malawi's national December 2025 values match
who_gho for 2025, with 896,938 people on ART in both sources, PLHIV of 1,006,959 against the
rounded 1,000,000, new infections of 14,225 against 14,000, ART coverage of 89.07% against 89%
and knowledge of status of 95.64% against 96%.

The offline test of 14 October 2026 read saved answers for Malawi, Kenya, Tanzania and Chad,
and compared the national rows with the panel.
  - on_art_count equals who_gho in all six country-years tested (Malawi 2025, Kenya 2018 and
    2025, Tanzania 2022 and 2025, Chad 2025).
  - plhiv, new_infections, art_coverage_pct and know_status_pct sit within the rounding of
    who_gho in 22 of the 24 country-years and indicators tested. who_gho holds 3,300 new
    infections for Chad in 2025 against Naomi's 3,072, and 85% knowledge of status for Kenya in
    2018 against Naomi's 86.3%.
  - The unaids_aidsinfo rows for Kenya in 2018 come from an earlier estimates round and differ
    from Naomi and who_gho alike (25,000 new infections against Naomi's 31,645, and 95%
    knowledge of status against 86.3%).
  - Kenya's prevalence for ages 15 to 49 in December 2018 is 4.70% in Naomi against 4.1% in
    unaids_aidsinfo and world_bank. Tanzania's December 2022 prevalence of 3.89% matches the
    3.9% in both sources.
  - population_total differs from world_bank by up to 3% (Kenya 2018, 48.7 million against
    50.2 million), because Naomi carries the Spectrum population.
  - Area names follow Naomi's spelling and the panel holds no name crosswalk. The 47 Kenyan
    county names lack the suffix " County" the PEPFAR rows carry. Seven Chadian names and
    "Dar-es-salaam" differ from the panel's spellings in hyphens and capital letters (Naomi's
    "Mayo-kebbi Est" against "Mayo Kebbi Est" in the dhs and td_annuaire rows), and the dhs and
    td_annuaire rows already spell Barh el Gazel and Hadjer-Lamis differently from each other.
  - At Tanzania's 31 regions, on_art_count is within 5% of the PEPFAR SNU count for eight
    regions in 2022 and 20 regions in 2025. PEPFAR counts only the people the programme
    supports.

What the connector reads.
  - The December periods only, the periods whose quarter is four, from the first December period
    to the last December period the country lists. A period after the last December period is a
    projection of the model and gives no row. A survey quarter outside December gives no row,
    because a value for March 2016 would sit in the panel beside year-end values for 2016. The
    log counts every period refused, by country.
  - Seven indicators, all with sex both, male and female.
      plhiv                   plhiv, all ages
      new_infections          infections, all ages
      hiv_prevalence_15_49    prevalence, ages 15 to 49, as a percentage
      know_status_pct         aware_plhiv_prop, all ages, as a percentage
      art_coverage_pct        art_coverage, all ages, as a percentage
      on_art_count            art_current, people on ART attending facilities in the area, all
                              ages. The national mean equals the country's programme count, and
                              the areas share the count out by where people collect treatment.
      population_total        population, all ages, the population of the Spectrum model and
                              not the World Bank series
    Every row is a modelled estimate, the on_art_count rows included, and keeps lower and upper as
    value_lower and value_upper.
  - The first administrative level below the country. The connector reads Naomi's area level 1
    in 29 countries. Kenya's level 1 is the eight former provinces, and the connector reads level 2,
    the 47 counties, as the panel's PEPFAR rows do. Tanzania's level 1 is Mainland and Zanzibar
    and level 2 is seven zones, and the connector reads level 3, the 31 regions, as the panel's
    DHS (Demographic and Health Surveys) and PEPFAR rows do.
  - Area names as published, with surrounding spaces removed. Three Chadian names arrive with
    the accent broken (Guã©ra, Ouaddaã¯, Tandjilã©), and the connector writes Guéra, Ouaddaï and
    Tandjilé, keeping the published spelling in extra.name_as_published.

What the connector refuses, and why.
  - The 18 indicators of the common list the connector does not map, and Malawi's two further
    indicators. Incidence per 1,000 has no panel indicator. The ART catchment series, the
    counts of PLHIV aware, unaware and untreated, and the ART count by residence describe the
    same people as the indicators read. The nine antenatal series have no panel indicator.
    Malawi's "Reported ART number" carries a range of its own and does not equal the programme
    count (934,943 in December 2025 against 896,938), and the viewer does not define the
    series or the reporting bias.
  - Every age group other than all ages, and ages 15 to 49 for prevalence. Rows for age groups
    wait on the decision Jason holds on age-group rows for the whole panel.
  - Area levels below the first administrative level. The panel holds one subnational column,
    admin1, and a district would sit beside the province holding the district.

Panel rows. The national row has no admin1, and every area row names the area in admin1. extra
records the Naomi area code, the area level, the Naomi period, indicator and age group.
"""
from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional, Tuple
from urllib.parse import urlencode

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..normalize import code_to_iso3
from ..schema import PanelRow, SourceType, POP_ALL, AGE_ALL

log = logging.getLogger("hivimpact")

_API = "https://nmviewerserver.azurewebsites.net/api/v1"

# Naomi indicator, Naomi age group, panel indicator, multiplier. Naomi publishes proportions,
# and the panel's percentages are out of 100.
_SPECS: List[Tuple[str, str, str, float]] = [
    ("plhiv", "Y000_999", "plhiv", 1.0),
    ("infections", "Y000_999", "new_infections", 1.0),
    ("prevalence", "Y015_049", "hiv_prevalence_15_49", 100.0),
    ("aware_plhiv_prop", "Y000_999", "know_status_pct", 100.0),
    ("art_coverage", "Y000_999", "art_coverage_pct", 100.0),
    ("art_current", "Y000_999", "on_art_count", 1.0),
    ("population", "Y000_999", "population_total", 1.0),
]

_SEXES = {"both": "all", "male": "male", "female": "female"}

# Naomi area level holding the first administrative level, where level 1 is not that level.
# Kenya's level 1 is the eight former provinces and level 2 the 47 counties. Tanzania's level 1
# is Mainland and Zanzibar, level 2 seven zones and level 3 the 31 regions.
_ADMIN1_LEVEL = {"KEN": 2, "TZA": 3}

# Naomi's country codes outside ISO 3166, checked against the country name the API gives.
_CODE_ALIASES = {"ZIM": ("ZWE", "zimbabwe"), "ESW": ("SWZ", "eswatini")}

# Names published with a broken accent, the UTF-8 bytes read as Latin-1 and then lower-cased.
_NAME_REPAIRS = {"Guã©ra": "Guéra", "Ouaddaã¯": "Ouaddaï", "Tandjilã©": "Tandjilé"}

_PERIOD = re.compile(r"^(\d{4})-([1-4])$")


def _iso3(code: str, name: str) -> Optional[str]:
    iso = code_to_iso3(code)
    if iso:
        return iso
    alias = _CODE_ALIASES.get(str(code).upper())
    if alias and alias[1] in str(name).lower():
        return alias[0]
    return None


def _december_periods(periods: List[str]) -> Tuple[List[Tuple[str, int]], List[str]]:
    """Split a country's periods into the December periods the connector reads, each with the
    period's year, and the periods refused, the projections after the last December period and
    the survey quarters outside December."""
    parsed = []
    for p in periods:
        m = _PERIOD.match(str(p))
        if m:
            parsed.append((str(p), int(m.group(1)), int(m.group(2))))
    decembers = [(p, y) for p, y, q in parsed if q == 4]
    if not decembers:
        return [], [p for p, _y, _q in parsed]
    last = max(y for _p, y in decembers)
    kept = [(p, y) for p, y in decembers if y <= last]
    refused = [p for p, y, q in parsed if q != 4 or y > last]
    return kept, refused


def _clean_name(name: str) -> str:
    stripped = str(name).strip()
    return _NAME_REPAIRS.get(stripped, stripped)


class UNAIDSNaomiConnector(BaseConnector):
    source_id = "unaids_naomi"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = ("UNAIDS Naomi sub-national estimates, December values by province or region "
                   "with ranges (viewer API)")
    request_pause = 0.3
    timeout = 60

    def _areas_url(self, code: str, indicator: str, age: str, period: str, sex: str,
                   level: int) -> str:
        query = urlencode({"country": code, "indicator": indicator, "ageGroup": age,
                           "period": period, "sex": sex, "areaLevel": level})
        return f"{_API}/areas?{query}"

    def _countries(self) -> List[dict]:
        return self.get_json(f"{_API}/countries")

    def _options(self, code: str) -> dict:
        return self.get_json(f"{_API}/options?{urlencode({'country': code})}")

    def _areas(self, url: str) -> List[dict]:
        return self.get_json(url)

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        end_year = min(end_year or date.today().year, date.today().year)

        listed = self._countries()
        skipped_codes = sorted(str(c.get("code")) for c in listed
                               if _iso3(c.get("code"), c.get("name")) is None)
        chosen = [(c["code"], _iso3(c["code"], c.get("name")), c.get("name")) for c in listed
                  if _iso3(c.get("code"), c.get("name"))]
        if wanted:
            chosen = [c for c in chosen if c[1] in wanted]
        if not chosen:
            log.info("unaids_naomi: no Naomi country matches the request")
            return

        emitted: Dict[str, int] = defaultdict(int)
        refused_periods: Dict[str, List[str]] = {}
        unmatched_sums: List[str] = []
        missing_specs: Dict[str, List[str]] = defaultdict(list)
        empty_values = 0

        for code, iso3, country_name in chosen:
            options = self._options(code)
            level = _ADMIN1_LEVEL.get(iso3, 1)
            if level not in options.get("areaLevels", []):
                log.warning("unaids_naomi: %s lists no area level %d and gives no row", iso3, level)
                continue
            periods, refused = _december_periods(options.get("periods", []))
            if refused:
                refused_periods[iso3] = refused
            periods = [(p, y) for p, y in periods if start_year <= y <= end_year]
            indicators = {i.get("code") for i in options.get("indicators", [])}
            ages = {a.get("code") for a in options.get("ageGroups", [])}
            sexes = set(options.get("sexes", []))

            for naomi, age, canonical, multiplier in _SPECS:
                if naomi not in indicators or age not in ages:
                    missing_specs[iso3].append(naomi)
                    continue
                spec = CANONICAL_INDICATORS[canonical]
                for period, year in periods:
                    for sex_code, sex in _SEXES.items():
                        if sex_code not in sexes:
                            continue
                        url = self._areas_url(code, naomi, age, period, sex_code, level)
                        areas = self._areas(url)
                        national = [a for a in areas if a.get("areaLevel") == 0]
                        units = [a for a in areas if a.get("areaLevel") == level]
                        names = Counter(_clean_name(a.get("name", "")) for a in units)
                        repeated = sorted(n for n, k in names.items() if k > 1)
                        if len(national) != 1 or repeated:
                            log.warning("unaids_naomi: %s %s %s %s refused, %d national values "
                                        "and repeated area names %s", iso3, naomi, period,
                                        sex_code, len(national), repeated)
                            continue
                        if multiplier == 1.0 and national[0].get("mean") is not None:
                            total = sum(a.get("mean") or 0.0 for a in units)
                            if abs(total - national[0]["mean"]) > 0.001 * abs(national[0]["mean"]) + 1:
                                unmatched_sums.append(f"{iso3} {naomi} {period} {sex_code}")
                        for area in national + units:
                            mean = area.get("mean")
                            if mean is None:
                                empty_values += 1
                                continue
                            is_national = area.get("areaLevel") == 0
                            published = str(area.get("name", ""))
                            admin1 = None if is_national else _clean_name(published)
                            digits = 2 if multiplier == 1.0 else 3

                            def scaled(x):
                                return None if x is None else round(float(x) * multiplier, digits)

                            extra = {
                                "naomi_area_code": area.get("code"),
                                "naomi_area_level": area.get("areaLevel"),
                                "naomi_period": period,
                                "naomi_indicator": naomi,
                                "naomi_age_group": age,
                            }
                            if admin1 is not None and admin1 != published:
                                extra["name_as_published"] = published
                            yield self.make_row(
                                country_iso3=iso3, country_name=country_name,
                                indicator_id=canonical, year=year, value=scaled(mean),
                                value_lower=scaled(area.get("lower")),
                                value_upper=scaled(area.get("upper")),
                                admin1=admin1, population_group=POP_ALL, sex=sex,
                                age_group=AGE_ALL, unit=spec.unit, source_url=url,
                                source_indicator_code=f"{naomi}|{age}", extra=extra,
                            )
                            emitted[canonical] += 1

        for _naomi, _age, canonical, _m in _SPECS:
            log.info("unaids_naomi: %-22s -> %d rows", canonical, emitted.get(canonical, 0))
        for iso3, refused in sorted(refused_periods.items()):
            log.info("unaids_naomi: %s periods refused, survey quarters outside December and "
                     "projections (%s)", iso3, ", ".join(refused))
        for iso3, specs in sorted(missing_specs.items()):
            log.info("unaids_naomi: %s does not list %s", iso3, ", ".join(specs))
        if unmatched_sums:
            log.warning("unaids_naomi: %d area sums differ from the national value (%s)",
                        len(unmatched_sums), "; ".join(unmatched_sums[:20]))
        log.info("unaids_naomi: %d area values without a mean were skipped", empty_values)
        log.info("unaids_naomi: %d Naomi country codes outside ISO 3166 were skipped (%s)",
                 len(skipped_codes), ", ".join(skipped_codes))
