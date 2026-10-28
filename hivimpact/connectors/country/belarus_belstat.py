"""
Belarus, notified HIV cases from the data portal of the National Statistical Committee of the
Republic of Belarus (Belstat), connector 57.

Source. Belstat publishes the interactive information and analytical system for official
statistics at https://dataportal.belstat.gov.by, with an open JSON service under
/osids-public-api. No sign-in and no key. The page reads the view configuration of an
indicator with GET /indicator/indicatorViewCfgGet/{code} and the values with POST
/indicator/indicatorValuesSearch, and the service refuses a values query over more than 10
years ("Data can be viewed for a period of no more than 10 years."), as checked on 20 October
2026. The connector therefore asks for the years in windows of 10.

Table read. Indicator 10104000078, "Primary incidence of HIV infection in the population by
age groups across the territory of the Republic of Belarus", persons, yearly from 2000. The
metadata (POST /indicator/indicatorMetadataGet) define the count as "The number of cases of
HIV infection newly identified in the reporting year", name the Demographic Statistics and
Population Census Department of Belstat as the contact, and give the last update as 8 June
2026. Three dimensions. Territory, the Republic of Belarus and the six regions and Minsk city.
Gender, Total, Males and Females. Age composition, "By all age" and five groups, "up to 15
years", "15 to 19 years of age", "20 to 29 years of age", "30 to 39 years of age" and "40
years and over". The territory rows below the national row carry "By all age" only.

What the connector emits, all under notified_hiv_cases.
  National rows for every sex and every age group, with "up to 15 years" written as age_group
  "0-14", because Belstat indicator 10104000066 (newly reported HIV cases among people aged 0
  to 19) prints the same counts under "0-14 years" in every year from 2005 to 2025.
  Region and Minsk city rows for every sex, all ages, with admin1 as Belstat prints the
  territory name (for example "Brest region", "Minsk city", "Minsk region").
  A row enters only when the counts around the row agree. Males plus females must equal the
  total of the same territory and age group. A national age-group row needs the five groups
  to add to the all-age count of the same sex. A region row needs the six regions and Minsk
  city to add to the national count of the same sex. Every check reads an empty entry as
  zero, because indicator 10104000066 prints 0 for the women under 15 of 2025, where indicator
  10104000078 leaves the entry empty. An empty entry itself emits no row. On the answers of 20
  October 2026 every check passes in every year from 2000 to 2025, and five national entries
  under 15 are empty (all sexes 2003, males 2002 and 2003, females 2003 and 2025).

Check against the panel (read from data/panel/hiv_panel.csv on 20 October 2026). who_europe_hfa
holds Belarusian notified_hiv_cases for 2000 to 2019 from measure HFA_350, the new HIV
diagnoses of the joint ECDC and WHO Europe surveillance reports. The Belstat national count
equals the HFA_350 value in 19 of the 20 years. For 2018 Belstat prints 2,353 (and the six
regions and Minsk city add to 2,353) and HFA_350 holds 2,386. Belstat adds 2020 to 2025 (1,427,
1,496, 1,644, 1,463, 1,228 and 1,088), the split by sex and age, and the regions, which no
other source in the panel holds for Belarus.

Not carried (ruling R33 of research/rulings_2026-10-15.md).
  Indicator 10104000068, "Percentage of mother-to-child transmission of HIV", the cases of
  transmission as a percentage of the children born to mothers with HIV. The panel id
  vertical_transmission_pct holds the modelled UNAIDS estimate, and an observed programme
  rate under the same id would put two definitions under one series.
  Indicator 10104000066, because the counts repeat the age groups under 15 and 15 to 19 of
  indicator 10104000078 and add nothing.

Source type. routine_programme_record, the national HIV case register as Belstat publishes
the register.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_API = "https://dataportal.belstat.gov.by/osids-public-api"
_PAGE = "https://dataportal.belstat.gov.by/osids/indicator-info/{code}"
_CODE = "10104000078"
_WINDOW = 10

# Labels as Belstat prints the labels in English on 20 October 2026
_NATIONAL = "Republic of Belarus"
_SEXES = {"Total": SEX_ALL, "Males": "male", "Females": "female"}
_AGES = {
    "By all age": AGE_ALL,
    "up to 15 years": "0-14",
    "15 to 19 years of age": "15-19",
    "20 to 29 years of age": "20-29",
    "30 to 39 years of age": "30-39",
    "40 years and over": "40+",
}

_DEFINITION = ("HIV cases newly identified in Belarus in the reporting year, Belstat indicator "
               "10104000078, Primary incidence of HIV infection in the population by age groups")
_RECONCILE = ("who_europe_hfa HFA_350, the new HIV diagnoses Belarus reports to the joint ECDC "
              "and WHO Europe surveillance, equal in 19 of the 20 years from 2000 to 2019, with "
              "Belstat at 2,353 and HFA_350 at 2,386 for 2018. Never compare with new_diagnoses "
              "(Jason's ruling of 8 October 2026)")

Table = Dict[Tuple[str, str, str], Dict[int, Optional[int]]]


def _count(cell: Optional[str]) -> Optional[int]:
    """A printed count as an integer, or None for an empty entry. Belstat separates thousands
    with a no-break space. Any other text raises, because a value the connector cannot read is a
    change in the table and not a gap."""
    if cell is None:
        return None
    text = re.sub(r"[\s ]", "", cell)
    if text == "":
        return None
    if not re.fullmatch(r"\d+", text):
        raise ValueError(f"unexpected entry {cell!r}")
    return int(text)


def parse_values(answers: List[dict]) -> Table:
    """The values answers of every window as {(territory, gender, age): {year: count}}."""
    out: Table = {}
    for answer in answers:
        years = [int(y) for y in answer["tableHeader"][-1]]
        dims = answer["tableHeaderDimColumns"]
        if len(dims) != 3:
            raise ValueError(f"expected three dimensions, read {dims!r}")
        for tr in answer["tableRows"]:
            key = tuple((c["value"] or "").strip() for c in tr[:3])
            cells = tr[3:]
            if len(cells) != len(years):
                raise ValueError(f"row {key!r} holds {len(cells)} values for {len(years)} years")
            for year, cell in zip(years, cells):
                out.setdefault(key, {})[year] = _count(cell["value"])
    for territory, gender, age in out:
        if gender not in _SEXES or age not in _AGES:
            raise ValueError(f"unexpected label in row {(territory, gender, age)!r}")
    if not any(k[0] == _NATIONAL for k in out):
        raise ValueError("no national row")
    return out


def _z(v: Optional[int]) -> int:
    return 0 if v is None else v


def checks(cells: Table) -> Dict[Tuple[str, str, str, int], str]:
    """{(territory, gender, age, year): check text} for every printed count whose checks pass.

    A failing check logs a warning and keeps the row out."""
    passed: Dict[Tuple[str, str, str, int], str] = {}
    regions = sorted({k[0] for k in cells if k[0] != _NATIONAL})
    years = sorted({y for v in cells.values() for y in v})
    ages = [a for a in _AGES if a != "By all age"]
    for (territory, gender, age), values in cells.items():
        for year, n in values.items():
            if n is None:
                continue
            notes: List[str] = []
            if gender != "Total":
                total = cells.get((territory, "Total", age), {}).get(year)
                m = cells.get((territory, "Males", age), {}).get(year)
                f = cells.get((territory, "Females", age), {}).get(year)
                if total is None or _z(m) + _z(f) != total:
                    log.warning("by_belstat: %s %s %s %d, males plus females is %d against a "
                                "total of %s, no row emitted", territory, gender, age, year,
                                _z(m) + _z(f), total)
                    continue
                notes.append(f"males plus females equals the total of {total}")
            if territory == _NATIONAL and age != "By all age":
                parts = [cells.get((territory, gender, a), {}).get(year) for a in ages]
                whole = cells.get((territory, gender, "By all age"), {}).get(year)
                if whole is None or sum(_z(p) for p in parts) != whole:
                    log.warning("by_belstat: %s %d, the five age groups add to %d against %s "
                                "for all ages, no row emitted", gender, year,
                                sum(_z(p) for p in parts), whole)
                    continue
                notes.append(f"the five age groups add to the all-age count of {whole}")
            if territory != _NATIONAL:
                if age != "By all age":
                    log.warning("by_belstat: %s carries the age group %r, no row emitted",
                                territory, age)
                    continue
                parts = [cells.get((r, gender, age), {}).get(year) for r in regions]
                whole = cells.get((_NATIONAL, gender, age), {}).get(year)
                if whole is None or sum(_z(p) for p in parts) != whole:
                    log.warning("by_belstat: %s %d, the regions and Minsk city add to %d "
                                "against a national count of %s, no row emitted", gender, year,
                                sum(_z(p) for p in parts), whole)
                    continue
                notes.append(f"the six regions and Minsk city add to the national count of "
                             f"{whole}")
            passed[(territory, gender, age, year)] = (", and ".join(notes) if notes else
                                                      "no sum check applies to the national "
                                                      "count of men and women together at all ages")
    log.info("by_belstat: %d printed counts over %d years pass the checks", len(passed),
             len(years))
    return passed


class BelarusBelstatConnector(BaseConnector):
    """Belstat data portal, notified HIV cases in Belarus, national by sex and age, and by region."""

    source_id = "by_belstat"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("National Statistical Committee of the Republic of Belarus (Belstat) data "
                   "portal, HIV cases newly identified in the year, 2000 onwards, nationally by "
                   "sex and age group and by region, where the published sums agree (to-source).")
    country = "BLR"
    request_pause = 1.0

    def _get(self, path: str):
        return self.get_json(_API + path, headers={"Accept-Language": "en"})

    def _post(self, path: str, **kw):
        headers = {"Accept-Language": "en", **kw.pop("headers", {})}
        return self._request("POST", _API + path, headers=headers, **kw)

    def _metadata(self) -> Dict[str, str]:
        """Metadata fields by code, for example "2.6" for the last update."""
        try:
            md = self._post("/indicator/indicatorMetadataGet", data=_CODE.encode(),
                            headers={"Content-Type": "text/plain"}).json()
        except Exception as exc:
            log.warning("by_belstat: the metadata were not read (%s)", exc)
            return {}
        out: Dict[str, str] = {}

        def walk(node):
            if isinstance(node, dict):
                if node.get("code") and node.get("value"):
                    out[str(node["code"])] = str(node["value"]).strip()
                for v in node.values():
                    if isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        walk(md)
        return out

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
        try:
            cfg = self._get(f"/indicator/indicatorViewCfgGet/{_CODE}")
            st = cfg["indicatorStructure"]
            params = {d["code"]: _enabled(d.get("nodes") or []) for d in st["dimensions"]}
            units = [u["code"] for u in (st.get("units") or {}).get("nodes") or []]
            years = sorted(y for y in st["years"] if start_year <= y <= end_year)
        except Exception as exc:
            log.warning("by_belstat: the view configuration was not read (%s)", exc)
            return
        answers: List[dict] = []
        title = ""
        for i in range(0, len(years), _WINDOW):
            window = years[i:i + _WINDOW]
            body = {"indicatorCode": _CODE, "valuesFilter": {
                "years": window, "periodicities": [], "units": units,
                "dimensionOrder": [d["code"] for d in st["dimensions"]],
                "dimensionParams": params, "simbolsAfterComma": 0}}
            try:
                answer = self._post("/indicator/indicatorValuesSearch", json=body).json()
            except Exception as exc:
                log.warning("by_belstat: the values for %d to %d were not read (%s), no row "
                            "emitted", window[0], window[-1], exc)
                return
            title = answer.get("tableName", title)
            answers.append(answer)
        try:
            cells = parse_values(answers)
        except (ValueError, KeyError, TypeError) as exc:
            log.warning("by_belstat: the values did not parse (%s), no row emitted", exc)
            return
        passed = checks(cells)
        md = self._metadata()
        emitted = 0
        for (territory, gender, age, year), note in sorted(passed.items(),
                                                           key=lambda kv: (kv[0][3], kv[0][0] != _NATIONAL, kv[0])):
            value = cells[(territory, gender, age)][year]
            extra: Dict = {
                "belstat_indicator": _CODE,
                "belstat_title": title,
                "belstat_definition": md.get("3.1", ""),
                "belstat_last_update": md.get("2.6", ""),
                "belstat_organisation": md.get("1.1", ""),
                "territory_as_printed": territory,
                "sex_as_printed": gender,
                "age_as_printed": age,
                "sum_check": note,
                "definition": _DEFINITION,
                "reconcile_with": _RECONCILE,
            }
            if age == "up to 15 years":
                extra["age_note"] = ("Belstat indicator 10104000066 prints the same counts under "
                                     "0-14 years for 2005 to 2025")
            emitted += 1
            yield self.make_row(
                country_iso3="BLR", country_name="Belarus",
                admin1="" if territory == _NATIONAL else territory,
                indicator_id="notified_hiv_cases", year=year, value=float(value), unit="count",
                population_group=POP_ALL, sex=_SEXES[gender], age_group=_AGES[age],
                source_url=_PAGE.format(code=_CODE),
                source_indicator_code=f"belstat:{_CODE}:{gender}:{age}",
                extra=extra,
            )
        log.info("by_belstat: emitted %d rows", emitted)


def _enabled(nodes: List[dict]) -> List[str]:
    """Every selectable value code of a dimension tree, parents before children."""
    out: List[str] = []
    for n in nodes:
        if n.get("isEnabled"):
            out.append(n["code"])
        out += _enabled(n.get("childrens") or [])
    return out
