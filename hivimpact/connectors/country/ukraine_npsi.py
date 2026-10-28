"""
Ukraine, notified HIV cases from the HIV monitoring portal of the Public Health Centre of the
Ministry of Health of Ukraine (PHC), connector 58.

Source. The PHC publishes "Моніторинг ВІЛ-інфекції в Україні" (HIV monitoring in Ukraine) at
https://npsi.phc.org.ua, and the portal page reads an open JSON service with no sign-in and no
key. POST /Portal/GetHIVMonitoring with the body null returns the indicator catalogue (494
entries on 20 October 2026, every entry with a name, a parent group, a unit and a
description), and POST /Portal/GetHIVIndicatorValues?id=N with the body null returns the
values of indicator N by year and region, with the region, sex and age labels in RefViews. The connector sends the
same anonymous requests the public page sends and touches no account route.

Indicators read, all from table 2000 "Офіційно зареєстровані випадки ВІЛ-інфекції" (officially
registered cases of HIV infection) of the annual reporting form No. 2-ВІЛ/СНІД.
  456 "Кількість ЛЖВ, вперше взятих на облік", people taken under medical supervision in the
  reporting year with a first-in-life HIV diagnosis, nationally and for 25 regions (24 oblasts
  and Kyiv city). The description excludes HIV-exposed children under monitoring and counts only
  children with a confirmed diagnosis.
  448, 449, 450 and 451, the age groups "0-14", "15-24", "25-49" and "> 50" under parent 225
  "Вікові групи", national only. The four groups add to the count of 456 in every year, so
  "> 50" holds ages 50 and over and is written as age_group "50+".
  226 "Чоловіки" and 452 "Жінки" under parent 224 "Стать (15+)", men and women aged 15 and
  over, written as sex "male" and "female" with age_group "15+".

What the connector emits, all under notified_hiv_cases, and only when the counts around the
row agree.
  A national row of 456 needs the four age groups of the same year to add to the national
  count. On the answers of 20 October 2026 the four groups add exactly in every year from 2016
  to 2024, and the portal prints no age group for 2025, so the 2025 count of 8,024 emits no
  row. The home page of the portal says the update of the indicators for the results of 2025
  has started ("Розпочате оновлення даних для показників за результатами 2025 року").
  An age row needs the same check.
  A sex row needs men 15+ plus women 15+ plus the age group 0-14 to equal the national count of
  the same year, which holds in every year from 2016 to 2024.
  A region row needs the 25 regions of the same year to add to the national count, which holds
  for 2017 to 2024. The regions add to one case below the national count for 2016 and to two
  below for 2025, a year with no Luhansk entry. A region row further needs the region to name a
  whole oblast for the year (ruling R32). The PHC description of indicator 481 (PLHIV on the
  register of the same table 2000) says the register covers the territories under the control
  of the Government of Ukraine and names Crimea, Sevastopol and the Donetsk, Luhansk,
  Zaporizhzhia and Kherson oblasts as territories with incomplete counts, and the portal lists
  no region for Crimea or Sevastopol. The connector therefore refuses Donetsk and Luhansk in
  every year (the government-controlled part of the oblast only, since 2014), and refuses every
  region row from 2022, the year of the full-scale invasion, because occupation during 2022
  reached oblasts the PHC list does not name, and the portal does not say which oblast counts
  cover a whole oblast for which year. The description of 456 asks for the counts of the last
  three years to be read with the migration, the temporary occupation and the difficulty of
  collecting data which followed the invasion.
  Region names follow the spelling of the PEPFAR rows already in the panel (for example
  "Kharkivska Oblast", "Kyiv city"), and the Ukrainian name as printed travels in extra.

Check against the panel (read from data/panel/hiv_panel.csv on 20 October 2026). who_europe_hfa
holds Ukrainian notified_hiv_cases for 2010 to 2019 from measure HFA_350, with the WHO note
which says the counts exclude Crimea and Sevastopol for 2014 to 2016 and parts of the
non-government-controlled territories for 2015 and 2016. The PHC count equals the HFA_350
count for 2019 (16,357) and exceeds the HFA_350 count by 93 for 2016, 55 for 2017 and 63 for
2018, 0.35 to 0.65 per cent. The PHC adds 2020 to 2024 (15,658, 15,360, 12,212, 11,658 and
10,038), the first Ukrainian notified counts by age and sex in the panel, and the first oblast
rows of notified cases.

Not carried (ruling R34 of research/rulings_2026-10-15.md).
  440 "Нові випадки" of AIDS (table 3000). The 440 counts equal HFA_348 for 2016 to 2019, and
  indicator 672 prints the same counts as people with an AIDS diagnosis among the newly
  registered. A share of 62 per cent with AIDS among the 14,334 people registered in 2016 is
  not compatible with indicator 488 (4,226 people with a CD4 count below 200 among the 12,573
  tested at registration), and the count falls from 7,511 for 2019 to 4,139 for 2020 with no
  note. The definition behind 440 therefore changes without a note (ruling R31 precedent).
  202 "Смерть від СНІД", deaths from AIDS (table 3002), because aids_deaths_reported counts
  deaths from any cause among people ever reported with AIDS (ruling R7).
  Indicators 206 and 327, which print the national counts of 456 again from other tables.

Source type. routine_programme_record, the national HIV case register as the PHC publishes the
register.
"""
from __future__ import annotations

import html
import logging
import re
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_API = "https://npsi.phc.org.ua/Portal"
_PAGE = "https://npsi.phc.org.ua/"

_TOTAL = 456
_AGE_IDS = {448: "0-14", 449: "15-24", 450: "25-49", 451: "50+"}
_SEX_IDS = {226: "male", 452: "female"}

# Names as the portal prints the names on 20 October 2026. A changed name stops the indicator.
_NAMES = {456: "Кількість ЛЖВ, вперше взятих на облік", 448: "0-14", 449: "15-24",
          450: "25-49", 451: "> 50", 226: "Чоловіки", 452: "Жінки"}
_PARENTS = {448: 225, 449: 225, 450: 225, 451: 225, 226: 224, 452: 224}
_TABLE = "таблиця 2000"

_NATIONAL = 9
_ALL_CODE = 9          # Gender 9 "Обидві статі", AgeCategory 9 "-Всі вікові категорії"
_VALUE_TYPE = 1        # "Основне"

# Ukrainian region names as printed, with the spelling of the PEPFAR rows in the panel
_REGIONS = {
    "Вінницька область": "Vinnytska Oblast",
    "Волинська область": "Volynska Oblast",
    "Дніпропетровська область": "Dnipropetrovska Oblast",
    "Донецька область": "Donetska Oblast",
    "Житомирська область": "Zhytomyrska Oblast",
    "Закарпатська область": "Zakarpatska Oblast",
    "Запорізька область": "Zaporizka Oblast",
    "Івано-Франківська область": "Ivano-Frankivska Oblast",
    "Київська область": "Kyivska Oblast",
    "м. Київ": "Kyiv city",
    "Кіровоградська область": "Kirovohradska Oblast",
    "Луганська область": "Luhanska Oblast",
    "Львівська область": "Lvivska Oblast",
    "Миколаївська область": "Mykolaivska Oblast",
    "Одеська область": "Odeska Oblast",
    "Полтавська область": "Poltavska Oblast",
    "Рівненська область": "Rivnenska Oblast",
    "Сумська область": "Sumska Oblast",
    "Тернопільська область": "Ternopilska Oblast",
    "Харківська область": "Kharkivska Oblast",
    "Херсонська область": "Khersonska Oblast",
    "Хмельницька область": "Khmelnytska Oblast",
    "Черкаська область": "Cherkaska Oblast",
    "Чернівецька область": "Chernivetska Oblast",
    "Чернігівська область": "Chernihivska Oblast",
}
# Ruling R32 and R34. The register holds the government-controlled part of the oblast only.
_PARTIAL_ALWAYS = {"Донецька область", "Луганська область"}
_FULL_SCALE_INVASION = 2022

_DEFINITION = ("People taken under medical supervision in Ukraine in the reporting year with a "
               "first-in-life HIV diagnosis, PHC indicator 456 from table 2000 of form No. "
               "2-ВІЛ/СНІД, HIV-exposed children counted only once the diagnosis is confirmed")
_TERRITORY = ("Territories under the control of the Government of Ukraine. The PHC names "
              "Crimea, Sevastopol and the Donetsk, Luhansk, Zaporizhzhia and Kherson oblasts as "
              "territories with incomplete counts (description of PHC indicator 481), and the "
              "portal lists no region for Crimea or Sevastopol")
_WAR_NOTE = ("The PHC description of indicator 456 asks for the counts of the last three years "
             "to be read with the migration, temporary occupation, destroyed infrastructure and "
             "difficulty of collecting data which followed the full-scale invasion of 2022")
_RECONCILE = ("who_europe_hfa HFA_350, the new HIV diagnoses Ukraine reports to the joint ECDC "
              "and WHO Europe surveillance, equal for 2019 and 0.35 to 0.65 per cent below the "
              "PHC count for 2016 to 2018. Never compare with new_diagnoses (Jason's ruling of "
              "8 October 2026)")

Series = Dict[Tuple[int, str], int]       # {(year, region as printed): count}


def parse_values(answer: dict, indicator: int) -> Series:
    """The values answer of one indicator as {(year, region as printed): count}.

    Every record must carry the indicator asked for, men and women together, all ages and the
    main value type, and a whole number. Anything else raises, because a record the connector cannot read
    is a change in the service and not a gap."""
    if str(answer.get("IsOK")) != "True":
        raise ValueError(f"indicator {indicator} answered IsOK={answer.get('IsOK')!r}")
    regions = {int(k): v for k, v in answer["RefViews"]["Country_regions"].items()}
    out: Series = {}
    for rec in answer["Data"]:
        if (rec["Indicator"], rec["Gender"], rec["AgeCategory"], rec["ValueType"]) != (
                indicator, _ALL_CODE, _ALL_CODE, _VALUE_TYPE):
            raise ValueError(f"unexpected record {rec!r}")
        v = rec["Value"]
        if v is None or float(v) != int(v) or v < 0:
            raise ValueError(f"unexpected value in {rec!r}")
        region = rec["Region"]
        name = "" if region == _NATIONAL else regions[region].strip()
        if name and name not in _REGIONS:
            raise ValueError(f"unexpected region {name!r}")
        key = (int(rec["Year"]), name)
        if key in out:
            raise ValueError(f"indicator {indicator} repeats {key!r}")
        out[key] = int(v)
    return out


def checks(series: Dict[int, Series]) -> Dict[Tuple[int, int, str], str]:
    """{(indicator, year, region as printed): check text} for every count which passes.

    A failing check logs a warning and keeps the row out."""
    total = {y: n for (y, r), n in series.get(_TOTAL, {}).items() if r == ""}
    ages = {i: {y: n for (y, r), n in series.get(i, {}).items() if r == ""} for i in _AGE_IDS}
    sexes = {i: {y: n for (y, r), n in series.get(i, {}).items() if r == ""} for i in _SEX_IDS}
    passed: Dict[Tuple[int, int, str], str] = {}

    age_ok: Dict[int, str] = {}
    for year, whole in sorted(total.items()):
        parts = [ages[i].get(year) for i in _AGE_IDS]
        if any(p is None for p in parts):
            log.warning("ua_npsi: %d, the portal prints %d of the four age groups, so the national "
                        "count of %d cannot be checked, no row emitted for %d",
                        year, sum(p is not None for p in parts), whole, year)
            continue
        if sum(parts) != whole:
            log.warning("ua_npsi: %d, the four age groups add to %d against a national count of "
                        "%d, no row emitted for %d", year, sum(parts), whole, year)
            continue
        age_ok[year] = f"the four age groups add to the national count of {whole}"
        passed[(_TOTAL, year, "")] = age_ok[year]
        for i in _AGE_IDS:
            passed[(i, year, "")] = age_ok[year]

    for year in sorted(age_ok):
        m, f, young = sexes[226].get(year), sexes[452].get(year), ages[448][year]
        if m is None or f is None or m + f + young != total[year]:
            log.warning("ua_npsi: %d, men 15+ plus women 15+ plus age 0-14 is %s against a "
                        "national count of %d, no sex row emitted", year,
                        None if m is None or f is None else m + f + young, total[year])
            continue
        note = (f"men 15+ plus women 15+ plus the {young} children aged 0-14 equal the national "
                f"count of {total[year]}")
        passed[(226, year, "")] = note
        passed[(452, year, "")] = note
    unchecked = sorted({y for i in _SEX_IDS for (y, r) in series.get(i, {})
                        if r == "" and y not in age_ok})
    for year in unchecked:
        log.warning("ua_npsi: %d, the national count is unchecked, no sex row emitted", year)

    by_year: Dict[int, Dict[str, int]] = {}
    for (year, region), n in series.get(_TOTAL, {}).items():
        if region:
            by_year.setdefault(year, {})[region] = n
    for year, rows in sorted(by_year.items()):
        whole = total.get(year)
        if whole is None or sum(rows.values()) != whole or len(rows) != len(_REGIONS):
            log.warning("ua_npsi: %d, %d regions add to %d against a national count of %s, no "
                        "region row emitted for %d", year, len(rows), sum(rows.values()), whole,
                        year)
            continue
        for region in rows:
            if region in _PARTIAL_ALWAYS:
                continue
            if year >= _FULL_SCALE_INVASION:
                continue
            passed[(_TOTAL, year, region)] = (f"the {len(rows)} regions add to the national "
                                              f"count of {whole}")
    refused = sorted({y for y in by_year if y >= _FULL_SCALE_INVASION})
    if refused:
        log.info("ua_npsi: region rows for %s refused under ruling R34, the portal does not say "
                 "which oblast counts cover a whole oblast after the full-scale invasion",
                 ", ".join(str(y) for y in refused))
    log.info("ua_npsi: %d counts pass the checks", len(passed))
    return passed


def _description(entry: dict) -> str:
    text = re.sub(r"<[^>]+>", " ", entry.get("Description_RTF") or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


class UkraineNPSIConnector(BaseConnector):
    """PHC HIV monitoring portal, notified HIV cases in Ukraine, nationally by age and sex, and by oblast."""

    source_id = "ua_npsi"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Public Health Centre of the Ministry of Health of Ukraine (PHC), HIV "
                   "monitoring portal, people newly registered with HIV in the year, 2016 "
                   "onwards, nationally by age group and by sex at 15+, and by oblast for the "
                   "years before 2022, where the published sums agree (to-source).")
    country = "UKR"
    request_pause = 1.0

    def _post(self, path: str):
        return self._request("POST", _API + path, data=b"null",
                             headers={"Content-Type": "application/json"}).json()

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
            catalogue = {int(e["ID"]): e for e in self._post("/GetHIVMonitoring")["Data"]}
        except Exception as exc:
            log.warning("ua_npsi: the indicator catalogue was not read (%s), no row emitted", exc)
            return
        ids = [_TOTAL, *_AGE_IDS, *_SEX_IDS]
        for i in ids:
            entry = catalogue.get(i)
            name = (entry or {}).get("Name", "").strip()
            if name != _NAMES[i] or (i in _PARENTS and int(entry["Parent_group"]) != _PARENTS[i]):
                log.warning("ua_npsi: indicator %d reads %r under parent %s, expected %r, no row "
                            "emitted", i, name, (entry or {}).get("Parent_group"), _NAMES[i])
                return
        for i in (_TOTAL, 225, 224):
            if _TABLE not in _description(catalogue.get(i, {})).lower():
                log.warning("ua_npsi: the description of indicator %d no longer names %s, no "
                            "row emitted", i, _TABLE)
                return
        series: Dict[int, Series] = {}
        for i in ids:
            try:
                series[i] = parse_values(self._post(f"/GetHIVIndicatorValues?id={i}"), i)
            except Exception as exc:
                log.warning("ua_npsi: the values of indicator %d were not read (%s), no row "
                            "emitted", i, exc)
                return
        passed = checks(series)
        emitted = 0
        for (i, year, region), note in sorted(passed.items(),
                                              key=lambda kv: (kv[0][1], kv[0][2] != "", kv[0])):
            if not start_year <= year <= end_year:
                continue
            value = series[i][(year, region)]
            extra: Dict = {
                "phc_indicator": i,
                "phc_indicator_name": _NAMES[i],
                "phc_parent_name": catalogue[_PARENTS[i]]["Name"] if i in _PARENTS else "",
                "region_as_printed": region or "-Україна",
                "sum_check": note,
                "definition": _DEFINITION,
                "territory_note": _TERRITORY,
                "reconcile_with": _RECONCILE,
            }
            if year >= _FULL_SCALE_INVASION:
                extra["war_note"] = _WAR_NOTE
            if i == 451:
                extra["age_note"] = ("printed as \"> 50\", ages 50 and over, because the four "
                                     "age groups add to the national count")
            emitted += 1
            yield self.make_row(
                country_iso3="UKR", country_name="Ukraine",
                admin1=_REGIONS.get(region, ""),
                indicator_id="notified_hiv_cases", year=year, value=float(value), unit="count",
                population_group=POP_ALL,
                sex=_SEX_IDS.get(i, SEX_ALL),
                age_group=_AGE_IDS.get(i, "15+" if i in _SEX_IDS else AGE_ALL),
                source_url=_PAGE,
                source_indicator_code=f"phc_npsi:{i}",
                extra=extra,
            )
        log.info("ua_npsi: emitted %d rows", emitted)
