"""
UNICEF HIV/AIDS dataset connector, connector 29, PMTCT coverage, the vertical transmission
rate and the age-group counts of people living with HIV, new HIV infections and AIDS-related
deaths from the UNAIDS 2026 estimates round, for every country and year.

UNICEF (the United Nations Children's Fund) publishes the dataset UNICEF,HIV_AIDS,1.0 through a
public SDMX (Statistical Data and Metadata eXchange) service at
https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/, with no sign-in and no key. The dataset has
seven dimensions (REF_AREA, INDICATOR, AGE, SEX, WEALTH_QUINTILE, RESIDENCE and DATA_SOURCE) and
19 HIV indicators. UNICEF republishes the UNAIDS estimates, and the DATA_SOURCE label of every
PMTCT (prevention of mother-to-child transmission) value read on 14 October 2026 names the
UNAIDS 2026 estimates, one round newer than the AIDSinfo exports behind unaids_aidsinfo, whose
year columns stop at 2024.

Coverage read on 14 October 2026 from the API answer (research/aggregator_sweep_notes.md).

  HVA_PMTCT_ARV_CVG, pregnant women with HIV who received antiretroviral medicine for PMTCT,
  per cent. DATA_SOURCE "Global AIDS Monitoring and UNAIDS 2026 estimates", 1,365 country values
  for 2010 to 2025, with a lower and an upper bound on every value. 174 values read ">95" and
  one reads "<1".
  HVA_PMTCT_MTCT, the vertical transmission rate, HIV-exposed infants who acquire HIV per 100.
  DATA_SOURCE "UNAIDS 2026 estimates", 1,371 country values for 2010 to 2025, with a lower and
  an upper bound on every value and no censored value. The published bounds of all 1,371 values
  sit on a scale 10 times the value and exclude the value (ruling R30 of
  research/rulings_2026-10-15.md). Kyrgyzstan 2010 reads 46.1 with bounds of 440 and 486, and
  the published bounds divided by 10 bracket the value in all 1,371 values. The connector does
  not convert a bound, so the 1,371 values enter the panel without bounds, and the published
  bounds stay in extra under bounds_refused. Kyrgyzstan 2012 reads 106.1 per 100 and is kept as
  published, beside the 98 of the AIDSinfo export of the previous round.
  HVA_EPI_LHIV, HVA_EPI_INF_ANN and HVA_EPI_DTH_ANN, people living with HIV, new HIV infections
  and AIDS-related deaths by age group, read on 15 October 2026 (ruling R17 of
  research/rulings_2026-10-15.md). DATA_SOURCE "UNAIDS 2026 estimates" on every value, for 138
  countries and the years 2010 to 2025, with a lower and an upper bound on every value. The
  answer gives 16,861 country values for people living with HIV over 10 age groups, 13,599 for
  new infections over eight age groups, with no value for ages 5 to 9 or 10 to 14, and 16,429
  for AIDS-related deaths over 10 age groups. 27,730 of the 46,889 values are censored, 17,929
  reading "<100", 5,736 reading "<500" and 4,065 reading "<200". Where no part is censored, the
  narrower age groups add up to the wider age groups within 7.5 per cent, the rounding of
  figures printed to two significant figures. The answer of 15 October 2026 holds the same
  counts of PMTCT values as the answer of 14 October, 1,365 for coverage and 1,371 for vertical
  transmission.
  The answer of 15 October 2026 also holds a female value and a male value beside every total
  for all sexes of the three age-group counts, 46,889 female values and 46,889 male values over
  the same countries, years and age groups, read on 16 October 2026 (ruling R23 of
  research/rulings_2026-10-15.md). In the 13,669 sets of total, female and male values with no
  censored value, the female and male values add up to the total within the rounding of three
  figures printed to two significant figures in every set, with a median gap of zero and a
  largest gap of 7.5 per cent. In the 33,220 sets with a censored value ("<100", "<200" or
  "<500"), no uncensored value breaks the printed thresholds.

Why the whole series and not only the country-years AIDSinfo lacks. The 2026 round revises
earlier years, so a series that joins AIDSinfo values to UNICEF values mixes two rounds and can
report a change in the wrong direction. Madagascar's coverage reads 30 for 2024 in AIDSinfo,
while the 2026 round reads 20 for 2024 and 27 for 2025. Joining AIDSinfo 2024 to UNICEF 2025
shows a fall of three points, and the 2026 round alone shows a rise of seven points. 2025 is the
first year after the cuts to United States funding, so the change from 2024 to 2025 has to come
from one round. The panel keeps every source's own figure (hivimpact/reconcile.py), and the
connector emits the full 2026-round series under source_id unicef_hiv. who_gho already carries
the 2026 round beside unaids_aidsinfo for other indicators, with 2025 values AIDSinfo lacks, and
the two rounds differ by more than half a per cent in 2,220 of 3,442 shared values for people
living with HIV in the panel of 14 October 2026 (Madagascar 2024 reads 130,000 in who_gho and
90,000 in AIDSinfo).

The answer covers 88 countries for coverage and 86 for vertical transmission. Against the
AIDSinfo exports saved on 18 July 2026, 2,242 of the 2,736 UNICEF values fall on a country and year
AIDSinfo also holds, and 1,667 of the 2,242 differ by more than half a point or 2 per cent,
whichever is larger. The other 494 UNICEF values hold no AIDSinfo counterpart, 239 coverage
values over 84 countries and 255 vertical transmission values over 85 countries, 167 of the 494
for 2025.
  - Azerbaijan, Bangladesh, Indonesia, Jamaica, Mauritius, Nigeria, Trinidad and Tobago,
    Uruguay and Venezuela hold no AIDSinfo value in any year for coverage or vertical transmission. Uzbekistan
    holds no AIDSinfo coverage value, and Australia and Liberia hold no AIDSinfo vertical
    transmission value. Jamaica's UNICEF vertical transmission series stops at 2022.
  - Algeria lacks AIDSinfo values for 2020 to 2024 on coverage and vertical transmission, Bolivia and Libya lack
    2024 coverage, Colombia and the Netherlands lack 2024 vertical transmission, and Somalia
    lacks 2023 and 2024 vertical transmission.
Against the AIDSinfo age-group exports, 13,045 UNICEF age values fall on a country, year and age
group AIDSinfo also holds, all in the age groups 0-14, 10-19 and 15-24. The 5,785 shared values
with no censoring in UNICEF or AIDSinfo differ by a median of 8.3 per cent, and 43 per cent of the
5,785 differ by more than 10 per cent. Colombia's new infections at ages 10 to 19 read 2,400 for
2012 in the 2026 round against 620 in the 2025 round, while the all-ages count reads 11,000 in the
2025 round and the 2026 round, so the Colombia revision falls on the split between age groups and
not on the all-ages count. Of the 33,844 UNICEF age values with no AIDSinfo counterpart, 31,759
fall in the seven age groups with no AIDSinfo export (0-4, 5-9, 0-9, 10-14, 0-19, 15-19 and 20-24),
and 2,085 fall in the age groups 0-14, 10-19 and 15-24 on a country and year with no AIDSinfo
value, 2025 included.
reconcile.DECLARED_RELATIONSHIPS declares the unaids_aidsinfo and unicef_hiv pair derived for
pmtct_coverage_pct, vertical_transmission_pct, plhiv, new_infections and aids_deaths, so a
revision between rounds never counts as two measurements disagreeing.

What the connector emits.
  - pmtct_coverage_pct and vertical_transmission_pct, for all sexes, all ages and the whole
    population, with LOWER_BOUND and UPPER_BOUND in value_lower and value_upper.
  - plhiv, new_infections and aids_deaths for the UNICEF age groups, with the age range in
    age_group (Y0T4 as 0-4, Y5T9 as 5-9, Y0T9 as 0-9, Y10T14 as 10-14, Y0T14 as 0-14, Y10T19 as
    10-19, Y0T19 as 0-19, Y15T19 as 15-19, Y20T24 as 20-24 and Y15T24 as 15-24), for all sexes
    and the whole population, with the bounds in value_lower and value_upper. A value with an
    AGE code outside the mapping is not emitted, and the log names the code.
  - The female and male values of the three age-group counts under ruling R23, with sex
    "female" or "male" and the bounds of the female or male value. The site build keeps sex
    "all" and age_group "all" for the national charts, and reconcile keys on sex, so a female or
    male row never enters a total.
  - A censored value goes through unaids_aidsinfo._censored_row, so ">95" keeps 95 as the value
    with the source's lower bound and no upper bound, and "<1" keeps 1 as the value with a lower
    bound of zero. A "<100" on a count keeps 100 as the value with a lower bound of zero in the
    same way. extra.censored records the notation.
  - extra carries the DATA_SOURCE label, the estimates round, OBS_STATUS (E for estimate),
    COVERAGE_TIME and any OBS_FOOTNOTE.

What the connector refuses, and why.
  - The 16 regional codes (UNICEF_* and AU_AFRICA) are not countries, and code_to_iso3 refuses
    any code outside ISO 3166.
  - HVA_PED_ART_CVG, HVA_PED_ART_NUM and HVA_PMTCT_ARV_NUM. who_gho and unaids_aidsinfo already
    hold every country and year of the three UNICEF series. Children's ART coverage equals
    who_gho in all 1,364 shared values, and the UNICEF counts are rounded to two significant
    figures (Thailand 2023 children on ART reads 1,200 against 1,175 in who_gho).
  - A female or male value with no total for all sexes beside the female or male value, a
    female value with no male value, a male value with no female value, and a female and male
    pair whose values cannot add up to the total, given the rounding to two significant figures
    and the censoring thresholds. The gate refuses the female and male pair and keeps the
    total, and the log counts the refused pairs. The answer of 15 October 2026 held no refused
    value and no refused pair.
  - A female or male value of the two PMTCT indicators or of an all-ages count.
  - HVA_PED_LOST_AIDS, the AIDS orphans, a modelled consequence and not a service count, the
    reason unaids_aidsinfo.DECLARED_UNMAPPED gives for the AIDSinfo orphan export.
  - The seven survey indicators (HVA_PREV_*). No survey indicator in the dataset is a panel
    indicator (research/phase5_lac/lac_round1_notes.md, the UNICEF SDMX section).
  - Two values for one country, indicator and year under different DATA_SOURCE labels give one
    row, the first, and the log counts the repeats. The answers of 14 and 15 October 2026 held
    no repeat.
"""
from __future__ import annotations

import logging
import math
import re
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..normalize import code_to_iso3
from ..schema import AGE_ALL, PanelRow, SourceType, POP_ALL, SEX_ALL
from .unaids_aidsinfo import _bound, _censored_row, _parse_cell

log = logging.getLogger("hivimpact")

_BASE = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,HIV_AIDS,1.0/"
_ACCEPT = "application/vnd.sdmx.data+json;version=1.0.0"

# UNICEF indicator code -> panel indicator
_MAP = {
    "HVA_PMTCT_ARV_CVG": "pmtct_coverage_pct",
    "HVA_PMTCT_MTCT": "vertical_transmission_pct",
    "HVA_EPI_LHIV": "plhiv",
    "HVA_EPI_INF_ANN": "new_infections",
    "HVA_EPI_DTH_ANN": "aids_deaths",
}
_TOTAL = "_T"   # the UNICEF code for all ages, all sexes, every wealth quintile and residence
_TOTAL_DIMS = ("WEALTH_QUINTILE", "RESIDENCE")
# UNICEF SEX code -> panel sex, for the age-group counts under ruling R23 of
# research/rulings_2026-10-15.md. Every other value keeps SEX at the total code only.
_SEX = {"F": "female", "M": "male"}
# UNICEF AGE code -> panel age_group, for the three modelled counts under ruling R17 of
# research/rulings_2026-10-15.md. The two PMTCT indicators keep AGE at the total code only.
_AGE = {
    "Y0T4": "0-4", "Y5T9": "5-9", "Y0T9": "0-9", "Y10T14": "10-14", "Y0T14": "0-14",
    "Y10T19": "10-19", "Y0T19": "0-19", "Y15T19": "15-19", "Y20T24": "20-24", "Y15T24": "15-24",
}
_AGE_IDS = ("plhiv", "new_infections", "aids_deaths")


class UNICEFHIVConnector(BaseConnector):
    source_id = "unicef_hiv"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = ("UNICEF HIV/AIDS dataset (SDMX API), PMTCT coverage, vertical transmission "
                   "and the age-group counts of people living with HIV, new infections and "
                   "AIDS-related deaths, for all sexes, females and males, from the UNAIDS 2026 "
                   "estimates round.")
    request_pause = 0.5
    timeout = 90

    def _query(self, start_year: int, end_year: int) -> List[dict]:
        """One SDMX-JSON request for every indicator in _MAP, flattened to one dict per value."""
        key = "." + "+".join(_MAP) + "....."   # seven key parts, REF_AREA left open
        params = {"startPeriod": str(start_year), "endPeriod": str(end_year),
                  "dimensionAtObservation": "AllDimensions"}
        data = self._request("GET", _BASE + key, params=params,
                             headers={"Accept": _ACCEPT}).json()
        return _flatten(data)

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        end_year = min(end_year or date.today().year, date.today().year)
        start_year = max(start_year, 2000)

        seen = set()
        skipped_areas = set()
        repeats = 0
        emitted: Dict[str, int] = {}
        refused_ages: Dict[str, int] = {}
        refused_sexes: Dict[str, int] = {}
        bounds_refused: Dict[str, int] = {}
        pending = []   # (key, make_row arguments), in the order of the answer
        parsed = {}    # key -> (printed value, censored notation), for the split gate of R23
        for o in self._query(start_year, end_year):
            canonical = _MAP.get(o.get("INDICATOR"))
            if canonical is None:
                continue
            if any(o.get(d) != _TOTAL for d in _TOTAL_DIMS):
                continue
            age_code = o.get("AGE")
            if age_code == _TOTAL:
                age = AGE_ALL
            elif canonical in _AGE_IDS and age_code in _AGE:
                age = _AGE[age_code]
            else:
                refused_ages[f"{o.get('INDICATOR')} {age_code}"] = (
                    refused_ages.get(f"{o.get('INDICATOR')} {age_code}", 0) + 1)
                continue
            sex_code = o.get("SEX")
            if sex_code == _TOTAL:
                sex = SEX_ALL
            elif age != AGE_ALL and sex_code in _SEX:
                sex = _SEX[sex_code]
            else:
                label = f"{o.get('INDICATOR')} {age_code} {sex_code}"
                refused_sexes[label] = refused_sexes.get(label, 0) + 1
                continue
            iso3 = code_to_iso3(o.get("REF_AREA"))
            if iso3 is None:
                skipped_areas.add(o.get("REF_AREA"))
                continue
            if wanted and iso3 not in wanted:
                continue
            year = int(str(o.get("TIME_PERIOD"))[:4])
            if not start_year <= year <= end_year:
                continue
            value, censored = _parse_cell(o.get("value"))
            if value is None:
                continue
            key = (canonical, iso3, year, age, sex)
            if key in seen:
                repeats += 1
                continue
            seen.add(key)
            parsed[key] = (value, censored)

            spec = CANONICAL_INDICATORS[canonical]
            lo = _bound(o.get("LOWER_BOUND"), True)
            hi = _bound(o.get("UPPER_BOUND"), False)
            source_label = o.get("DATA_SOURCE_name") or o.get("DATA_SOURCE") or ""
            rnd = re.search(r"UNAIDS (\d{4}) estimates", source_label)
            extra = {
                "data_source": source_label,
                "estimates_round": f"UNAIDS {rnd.group(1)} estimates" if rnd else None,
                "obs_status": o.get("OBS_STATUS"),
                "coverage_time": o.get("COVERAGE_TIME"),
                "reconcile_with": "unaids_aidsinfo (the same UNAIDS model, one round newer, "
                                  "declared derived in reconcile.DECLARED_RELATIONSHIPS)",
            }
            if o.get("OBS_FOOTNOTE"):
                extra["obs_footnote"] = o["OBS_FOOTNOTE"]
            if censored:
                value, lo, hi = _censored_row(value, censored, spec.unit, lo, hi)
                extra["censored"] = censored
            if (lo is not None and lo > value) or (hi is not None and hi < value):
                # Ruling R30. Bounds which exclude the value of the same row are not an
                # interval around the value, and the connector does not convert a bound.
                extra["bounds_refused"] = " to ".join(
                    "missing" if c is None or not str(c).strip() else str(c).strip()
                    for c in (o.get("LOWER_BOUND"), o.get("UPPER_BOUND")))
                lo = hi = None
                bounds_refused[canonical] = bounds_refused.get(canonical, 0) + 1
            sex_part = "" if sex == SEX_ALL else sex_code
            pending.append((key, dict(
                country_iso3=iso3, country_name=o.get("REF_AREA_name") or iso3,
                indicator_id=canonical, year=year, value=value,
                value_lower=lo, value_upper=hi, population_group=POP_ALL, age_group=age, sex=sex,
                unit=spec.unit, source_type=spec.default_source_type.value,
                source_url=(_BASE + "." + o["INDICATOR"] + "." + str(age_code) + "." + sex_part
                            + "..."),
                source_indicator_code=o["INDICATOR"],
                extra=extra,
            )))

        # Ruling R23. A female and male pair enters only beside the total for all sexes of the
        # same indicator, country, year and age group, and only when the female and male values
        # can add up to the total. A refused pair leaves the total in place.
        split_refused = set()
        for k in parsed:
            if k[4] == SEX_ALL:
                continue
            parts = [parsed.get(k[:4] + (s,)) for s in (SEX_ALL, "female", "male")]
            if None in parts or not _split_agrees(*parts):
                split_refused.add(k[:4])
        by_sex: Dict[str, int] = {}
        for k, args in pending:
            if k[4] != SEX_ALL and k[:4] in split_refused:
                continue
            yield self.make_row(**args)
            emitted[k[0]] = emitted.get(k[0], 0) + 1
            by_sex[k[4]] = by_sex.get(k[4], 0) + 1

        for canonical in _MAP.values():
            log.info("unicef_hiv: %-28s -> %d rows", canonical, emitted.get(canonical, 0))
        for canonical, n in sorted(bounds_refused.items()):
            log.info("unicef_hiv: %s, %d values have published bounds which exclude the value, "
                     "and the values enter without bounds under ruling R30", canonical, n)
        log.info("unicef_hiv: rows by sex, %s",", ".join(f"{s} {n}" for s, n in sorted(by_sex.items())))
        log.info("unicef_hiv: %d female and male pairs were refused under ruling R23, because the "
                 "pair lacked a total, lacked a female or male value or could not add up to the "
                 "total", len(split_refused))
        if refused_sexes:
            log.info("unicef_hiv: values with a SEX code outside the R23 mapping were not emitted, %s",
                     ", ".join(f"{k} ({n})" for k, n in sorted(refused_sexes.items())))
        if refused_ages:
            log.info("unicef_hiv: values with an AGE code outside the R17 mapping were not emitted, %s",
                     ", ".join(f"{k} ({n})" for k, n in sorted(refused_ages.items())))
        log.info("unicef_hiv: %d repeated keys were not emitted, %d regional codes were skipped (%s)",
                 repeats, len(skipped_areas), ", ".join(sorted(str(a) for a in skipped_areas)))


def _half_unit(x: float) -> float:
    """Half a unit in the second significant figure of x, the largest rounding error of a
    count printed to two significant figures."""
    if x <= 0:
        return 0.5
    return 0.5 * 10 ** (math.floor(math.log10(x)) - 1)


def _split_agrees(total, female, male) -> bool:
    """True when a female value and a male value can add up to the total for all sexes.

    Every argument is a (printed value, censored notation) pair from _parse_cell. UNICEF prints
    every count to two significant figures, and a censored count ("<100", "<200" or "<500")
    is an upper limit at the printed threshold.
    """
    (t, tc), (f, fc), (m, mc) = total, female, male
    if not (tc or fc or mc):
        return abs(f + m - t) <= _half_unit(f) + _half_unit(m) + _half_unit(t) + 1e-9
    for v, c in ((f, fc), (m, mc)):
        if not c and v > t + _half_unit(t) + 1e-9:
            return False
    if not tc:
        slack = _half_unit(t) + (0 if fc else _half_unit(f)) + (0 if mc else _half_unit(m))
        if t > f + m + slack + 1e-9:
            return False
    elif (0 if fc else f) + (0 if mc else m) > t + 1e-9:
        return False
    return True


def _flatten(data: dict) -> List[dict]:
    """SDMX-JSON 1.0 with dimensionAtObservation=AllDimensions, one dict per value.

    A key "i:j:k" indexes the observation dimensions in order, and the list after the key holds
    the value first and then one index per observation attribute. Dimension and attribute ids go
    in under the dimension or attribute id, and the readable names of REF_AREA and DATA_SOURCE go in under
    REF_AREA_name and DATA_SOURCE_name.
    """
    data = data.get("data", data)
    st = data["structure"]
    dims = st["dimensions"]["observation"]
    attrs = st.get("attributes", {}).get("observation", [])
    out: List[dict] = []
    for key, v in data["dataSets"][0].get("observations", {}).items():
        rec: dict = {}
        for d, j in zip(dims, key.split(":")):
            val = d["values"][int(j)]
            rec[d["id"]] = val.get("id")
            if d["id"] in ("REF_AREA", "DATA_SOURCE"):
                rec[d["id"] + "_name"] = val.get("name")
        rec["value"] = v[0] if v else None
        for ai, a in enumerate(attrs):
            idx = v[ai + 1] if len(v) > ai + 1 else None
            if idx is None:
                continue
            av = a["values"][int(idx)] if a.get("values") else None
            if av is not None:
                rec[a["id"]] = av.get("id") if av.get("id") is not None else av.get("name")
        out.append(rec)
    return out
