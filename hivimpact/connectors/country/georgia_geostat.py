"""
Georgia, notified HIV cases from the PxWeb database of the National Statistics Office of Georgia
(Geostat), connector 56.

Source. Geostat publishes the PC-Axis database at https://pc-axis.geostat.ge with an open PxWeb
API (/PXWeb/api/v1/en/Database/...). No sign-in and no key. The API answers a table address only
with a closing slash (for example .../Morbidity_of_patients_with_HIVAIDS.px/), and answers a data
query only when every variable carries an explicit selection, as checked on 20 October 2026.
The SOURCE field of the tables names the Ministry of Internally Displaced Persons From The
Occupied Territories, Labour, Health and Social Affairs of Georgia, and the CONTACT field names
Geostat.

Tables read.
  Social Statistics / Health / Morbidity_of_patients_with_HIVAIDS.px, "Morbidity of patients
  with HIV/AIDS and Number of Deaths", 2002 to 2025, last updated 28 July 2026. Four rows. The
  Georgian labels read "registered cases, total (cumulative)", "of which new cases in the
  reporting year", "deaths (cumulative)" and "of which deaths in the reporting year". The English
  label of the fourth row reads "o.w. number of deaths from new cases", and the cumulative deaths
  rise every year by the fourth row, so the Georgian label is the right reading. The NOTEX field
  says Georgia joined the ECDC HIV/AIDS surveillance system (TESSy) in 2008 and 2009, changed the
  HIV/AIDS definition and the reporting method, and revised the earlier data retrospectively.
  Gender Statistics / Health Care / 05_New_Cases_of_HIV_Infection.px, "New Cases of HIV
  Infection (persons)", 2010 to 2025 by sex and seven transmission categories, last updated 5
  August 2026.

What the connector emits, all national, under notified_hiv_cases.
  sex "all". The row "of which new cases in the reporting year", 2002 to 2025. A year enters
  only when the cumulative registered count rises from the year before by exactly the new
  cases of the year, because two published figures disagreeing leave the true figure unknown.
  The first year, 2002, has no year before and carries extra.cumulative_check "first year of
  the table". On the answers of 20 October 2026 every year from 2003 to 2025 agrees.
  sex "female" and "male". The Total transmission category of table 05, only for a year where
  women plus men equals the new cases of the morbidity table (ruling R31 of
  research/rulings_2026-10-15.md). Geostat labels the two sex categories "Women (age 15+)" and
  "Men (age 15+)" (Georgian ქალი (ასაკი 15+) and კაცი (ასაკი 15+)), yet women plus men equals
  the all-age total of the morbidity table in every year from 2012 to 2025, and the table
  counts transmission from mother to child among women and among men, so the rows carry age_group
  "all" and the Geostat label travels in extra.source_sex_label. Women plus men falls 28 short
  of the total for 2010 and 226 short for 2011, so 2010 and 2011 carry no sex rows. The seven
  transmission categories travel in extra.transmission_as_printed, as printed, with a dash
  for an empty category.

Check against the panel (read from data/panel/hiv_panel.csv on 20 October 2026). who_europe_hfa
holds Georgian notified_hiv_cases for 2000 to 2019 from measure HFA_350, the new HIV diagnoses
of the joint ECDC and WHO Europe surveillance reports. The Geostat totals equal the HFA_350
values in every year from 2009 to 2019 and differ by four, five, five, one, four, two and seven
for 2002 to 2008, the years Geostat revised after joining TESSy. Geostat adds 2020 to 2025 (530,
530, 617, 612, 615 and 562), which no other source in the panel holds.

Not carried.
  Table 04_New_Cases_of_HIVAIDS.px, "New Cases of HIV/AIDS (persons)" by sex, 1999 to 2025.
  Women plus men equals the HFA_348 AIDS cases for 2012 to 2017 and 2019, equals the new HIV
  cases for 2009 and for 2023 to 2025, differs from the AIDS cases and from the new HIV cases
  in every other year to 2019, and meets no check for 2020 to 2022, so the table changes
  definition without a note and no year can be read with a known definition.
  The cumulative registered cases and the cumulative deaths, which match no panel id.
  The deaths in the reporting year among registered cases, because aids_deaths_reported counts
  deaths among people ever reported with AIDS and the Geostat row counts deaths among everyone
  registered with HIV, with no cause named.
  The transmission categories as separate rows, because no panel id holds notified cases by
  transmission category.

Source type. routine_programme_record, the national HIV case register.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_API = "https://pc-axis.geostat.ge/PXWeb/api/v1/en/Database"
_PAGE = "https://pc-axis.geostat.ge/PXWeb/pxweb/en/Database/Database__{folder}/{table}/"

_MORBIDITY = ("Social Statistics/Health", "Morbidity_of_patients_with_HIVAIDS.px")
_BY_SEX = ("Gender Statistics/Health Care", "05_New_Cases_of_HIV_Infection.px")

# English labels as Geostat prints the labels on 20 October 2026, matched case-blind on the words below
_LABEL_CUMULATIVE = "registered patients"
_LABEL_NEW = "of which new cases"
_LABEL_TOTAL_ROUTE = "Total"
_SEXES = {"women": "female", "men": "male"}

_DEFINITION = ("HIV cases newly registered in Georgia in the reporting year, the row \"of which "
               "new cases in the reporting year\" of the Geostat table Morbidity of patients with "
               "HIV/AIDS and Number of Deaths, from the ministry of health case register")
_RECONCILE = ("who_europe_hfa HFA_350, the new HIV diagnoses Georgia reports to the joint ECDC "
              "and WHO Europe surveillance, equal in every year from 2009 to 2019 and up to "
              "seven apart for 2002 to 2008, which Geostat revised after Georgia joined TESSy. "
              "Never compare with new_diagnoses (Jason's ruling of 8 October 2026)")


def _url(folder: str, table: str) -> str:
    return f"{_API}/{folder.replace(' ', '%20')}/{table}/"


def _count(cell: str) -> Optional[int]:
    """A printed count as an integer, or None for a dash, an empty cell or any other text."""
    cell = (cell or "").strip()
    return int(cell) if re.fullmatch(r"\d+", cell) else None


def parse_table(meta: dict, answer: dict) -> Dict[Tuple[str, ...], Dict[int, str]]:
    """A PxWeb json answer as {labels of the non-year variables: {year: printed value}}.

    The year variable is the variable whose code starts with "year", case-blind."""
    labels = {v["code"]: dict(zip(v["values"], v["valueTexts"])) for v in meta["variables"]}
    codes = [c["code"] for c in answer["columns"] if c.get("type") != "c"]
    year_code = next(c for c in codes if c.lower().startswith("year"))
    out: Dict[Tuple[str, ...], Dict[int, str]] = {}
    for rec in answer["data"]:
        key = dict(zip(codes, rec["key"]))
        name = tuple(labels[c][key[c]] for c in codes if c != year_code)
        out.setdefault(name, {})[int(labels[year_code][key[year_code]])] = rec["values"][0]
    return out


def _query(meta: dict, fmt: str) -> dict:
    return {"query": [{"code": v["code"], "selection": {"filter": "item", "values": v["values"]}}
                      for v in meta["variables"]],
            "response": {"format": fmt}}


def _px_field(px_text: str, field: str) -> str:
    """A keyword of a PX file, with a value wrapped over several quoted lines joined into one."""
    m = re.search(rf'(?ms)^{field}=(.*?);\s*$', px_text)
    return re.sub(r'"\s*"', "", m.group(1)).strip().strip('"') if m else ""


def _row_by_label(table: Dict[Tuple[str, ...], Dict[int, str]], words: str) -> Optional[Dict[int, str]]:
    hits = [v for k, v in table.items() if len(k) == 1 and words.lower() in k[0].lower()]
    return hits[0] if len(hits) == 1 else None


def national_counts(morbidity: Dict[Tuple[str, ...], Dict[int, str]]
                    ) -> Tuple[Dict[int, int], Dict[int, str]]:
    """The new cases of every year which passes the cumulative check, and the check text per year."""
    new = _row_by_label(morbidity, _LABEL_NEW)
    cumulative = _row_by_label(morbidity, _LABEL_CUMULATIVE)
    if new is None or cumulative is None:
        raise ValueError("the morbidity table holds no single new-cases row and no single "
                         "cumulative row under the expected labels")
    kept: Dict[int, int] = {}
    checks: Dict[int, str] = {}
    for year in sorted(new):
        n = _count(new[year])
        if n is None:
            log.warning("ge_geostat: %d, the new-cases cell reads %r, no row emitted", year, new[year])
            continue
        before, now = _count(cumulative.get(year - 1, "")), _count(cumulative.get(year, ""))
        if year - 1 not in cumulative:
            checks[year] = "first year of the table"
        elif before is None or now is None:
            log.warning("ge_geostat: %d, the cumulative count is not printed for %d and %d, no "
                        "row emitted", year, year - 1, year)
            continue
        elif now - before != n:
            log.warning("ge_geostat: %d, the cumulative registered count rises by %d and the "
                        "new cases read %d, no row emitted", year, now - before, n)
            continue
        else:
            checks[year] = (f"the cumulative registered count rises from {before} to {now}, "
                            f"by the {n} new cases")
        kept[year] = n
    return kept, checks


def sex_counts(by_sex: Dict[Tuple[str, ...], Dict[int, str]], totals: Dict[int, int]
               ) -> Dict[int, Dict[str, Tuple[int, str, Dict[str, str]]]]:
    """{year: {sex: (count, Geostat sex label, transmission categories as printed)}} for the years
    where women plus men equals the national total (ruling R31)."""
    per_sex: Dict[str, Tuple[str, Dict[int, str], Dict[str, Dict[int, str]]]] = {}
    for (sex_label, route), values in by_sex.items():
        word = sex_label.split("(")[0].strip().lower()
        sex = _SEXES.get(word)
        if sex is None:
            raise ValueError(f"unexpected sex label {sex_label!r} in table 05")
        label, total_row, routes = per_sex.setdefault(sex, (sex_label, {}, {}))
        if route.strip() == _LABEL_TOTAL_ROUTE:
            total_row.update(values)
        else:
            routes[re.sub(r"\s+", " ", route).strip()] = values
    if set(per_sex) != set(_SEXES.values()):
        raise ValueError("table 05 does not hold women and men")
    out: Dict[int, Dict[str, Tuple[int, str, Dict[str, str]]]] = {}
    years = sorted(set(per_sex["female"][1]) & set(per_sex["male"][1]))
    for year in years:
        f, m = _count(per_sex["female"][1][year]), _count(per_sex["male"][1][year])
        if f is None or m is None:
            log.warning("ge_geostat: %d, a sex total of table 05 is not a count, no sex rows", year)
            continue
        if year not in totals:
            log.warning("ge_geostat: %d, no national total passed the checks, no sex rows", year)
            continue
        if f + m != totals[year]:
            log.warning("ge_geostat: %d, women plus men in table 05 is %d against the national "
                        "total of %d, no sex rows (ruling R31)", year, f + m, totals[year])
            continue
        out[year] = {sex: (count, per_sex[sex][0],
                           {route: vals.get(year, "") for route, vals in per_sex[sex][2].items()})
                     for sex, count in (("female", f), ("male", m))}
    return out


class GeorgiaGeostatConnector(BaseConnector):
    """Geostat PxWeb tables, notified HIV cases in Georgia, national, by sex where consistent."""

    source_id = "ge_geostat"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("National Statistics Office of Georgia (Geostat) PxWeb tables, HIV cases newly "
                   "registered in the year, national, 2002 onwards, by sex from 2012 where "
                   "women plus men equals the total (to-source).")
    country = "GEO"
    request_pause = 1.0

    def _table(self, folder: str, table: str) -> Tuple[dict, dict, str]:
        url = _url(folder, table)
        meta = self.get_json(url)
        answer = json.loads(self._request("POST", url, json=_query(meta, "json")).content
                            .decode("utf-8-sig"))
        px = self._request("POST", url, json=_query(meta, "px")).content.decode("utf-8-sig")
        return meta, answer, px

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
            m_meta, m_answer, m_px = self._table(*_MORBIDITY)
        except Exception as exc:
            log.warning("ge_geostat: the morbidity table was not read (%s)", exc)
            return
        try:
            totals, checks = national_counts(parse_table(m_meta, m_answer))
        except (ValueError, KeyError, StopIteration) as exc:
            log.warning("ge_geostat: the morbidity table did not parse (%s), no row emitted", exc)
            return
        try:
            s_meta, s_answer, s_px = self._table(*_BY_SEX)
            by_sex = sex_counts(parse_table(s_meta, s_answer), totals)
        except Exception as exc:
            log.warning("ge_geostat: table 05 was not read (%s), national totals only", exc)
            s_px, by_sex = "", {}
        emitted = 0
        for year, n in sorted(totals.items()):
            if not start_year <= year <= end_year:
                continue
            emitted += 1
            yield self._row(year, SEX_ALL, n, _MORBIDITY, m_meta, m_px, {
                "cumulative_check": checks[year],
                "source_row": "of which new cases in the reporting year",
            })
            for sex, (count, label, routes) in sorted(by_sex.get(year, {}).items()):
                emitted += 1
                yield self._row(year, sex, count, _BY_SEX, s_meta, s_px, {
                    "source_sex_label": label,
                    "age_note": ("Geostat labels the sex category age 15+, and women plus men "
                                 "equals the all-age national total of the year, with "
                                 "transmission from mother to child counted among women "
                                 "and among men, so the row covers all ages (ruling R31)"),
                    "sex_check": (f"women plus men equals the national total of {totals[year]} "
                                  f"in the morbidity table"),
                    "transmission_as_printed": routes,
                })
        log.info("ge_geostat: %d national years and %d years with a sex split, emitted %d rows",
                 len(totals), len(by_sex), emitted)

    def _row(self, year: int, sex: str, value: int, table: Tuple[str, str], meta: dict,
             px: str, extra_in: Dict) -> PanelRow:
        folder, name = table
        extra: Dict = {
            "geostat_table": name,
            "geostat_title": meta.get("title", ""),
            "geostat_last_updated": _px_field(px, "LAST-UPDATED"),
            "geostat_source_field": _px_field(px, "SOURCE"),
            "definition": _DEFINITION,
            "reconcile_with": _RECONCILE,
        }
        note = _px_field(px, "NOTEX")
        if note:
            extra["geostat_note"] = note
        extra.update(extra_in)
        code = "new_cases" if sex == SEX_ALL else f"{sex}.total"
        return self.make_row(
            country_iso3="GEO", country_name="Georgia", admin1="",
            indicator_id="notified_hiv_cases", year=year, value=float(value), unit="count",
            population_group=POP_ALL, sex=sex, age_group=AGE_ALL,
            source_url=_PAGE.format(folder=folder.replace(" ", "%20").replace("/", "__"), table=name),
            source_indicator_code=f"geostat:{name}:{code}",
            extra=extra,
        )
