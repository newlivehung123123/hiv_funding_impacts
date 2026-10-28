"""
Kyrgyzstan, notified HIV cases from the half-year situation report of the Republican Centre for
the Control of Blood-borne Viral Hepatitis and HIV of the Ministry of Health of the Kyrgyz
Republic (aidscenter.kg), connector 60.

Source. The centre publishes a short PDF report, "Ситуация во ВИЧ в КР на 01.07.2026" (the HIV
situation in the Kyrgyz Republic on 1 July 2026), at
https://aidscenter.kg/uploads/topics/17853979831150.pdf, 155,511 bytes, born-digital, read on 20
October 2026. No sign-in and no key. The connector downloads the report once into `raw_dir`,
every later run reads the cached copy, and the connector reads the pdfplumber text layer with
no optical character recognition.

Table read. Page 1, the HIV cases registered among citizens of the Kyrgyz Republic by region and
by year of registration. The first column holds the cumulative count for 1987 to 2012, the next
14 columns hold 2013 to 2026, and the last two columns hold the total and the share. Nine region
rows (Batken, Bishkek city, Osh city, Jalal-Abad, Issyk-Kul, Naryn, Osh, Talas and Chui) add to
the row "Общий итог" (overall total). Below the overall total the page prints the rate per
100,000 people, the row "Дети" (children) and the row "Иностр. гр." (foreign citizens), cases
registered in the Kyrgyz Republic among foreign citizens. The page header reads "Всего - 15994,
из них гр. КР- 15043, иностр. гр. - 951", meaning 15,994 registered in all, of whom 15,043
citizens of the Kyrgyz Republic and 951 foreign citizens.

Gates. The report enters only when every check below passes, because two published figures
disagreeing leave the true figure unknown.
  The nine region rows add to the overall total in every column, the cumulative column and the
  total column included.
  In every region row, in the overall total and in the foreign-citizens row, the cumulative count
  plus the yearly counts equals the total of the row.
  The overall total equals the header count of citizens, the foreign-citizens total equals the
  header count of foreign citizens, and citizens plus foreign citizens equals the header total.
A further check reads the age table of page 2, "Распределение выявленных ЛЖВ по возрастам"
(people living with HIV registered, by age, citizens of the Kyrgyz Republic), whose overall total
row holds 1996 to 2014 together and then 2015 to 2026. A year whose age-table total differs from
the overall total of page 1 enters no row. On the copy of 20 October 2026 every year from 2015 to
2025 agrees, and the age-table count for 1996 to 2014 equals the page 1 count for 1987 to 2014.

What the connector emits. National notified_hiv_cases, age group and sex "all", for every year of
page 1 before the year of the report date, 2013 to 2025 on the copy of 20 October 2026, as the
overall total for citizens plus the count for foreign citizens. The sum covers everyone
registered with HIV in the Kyrgyz Republic in the year, which is the population of the national
counts reported to the joint ECDC and WHO Europe surveillance. The citizens count and the
foreign-citizens count travel in extra. The year of the report date (2026 on the copy of 20
October 2026) covers half a year and enters no row.

Check against other sources (read on 20 October 2026). Citizens plus foreign citizens equals
Table 1 of the joint ECDC and WHO Europe report HIV/AIDS surveillance in Europe 2025
(ecdc_hiv_report) for 2015, 2016, 2017, 2020, 2022 and 2023, and differs by one case for 2018,
2019 and 2021 and by two for 2024. Against measure HFA_350 of the WHO Europe Health for All
database (who_europe_hfa) for 2013 to 2019 the counts read 500 and 503, 647 and 649, 619 and
653, 748 and 764, 836 and 840, 867 and 876, and 842 and 850, within two per cent in five of the
seven years. The report of 1 January 2026 (https://aidscenter.kg/uploads/topics/17706325639491.pdf)
prints 1,087 citizens for 2025, and the report of 1 July 2026 prints 1,086 after the Naryn count
for 2025 fell from 18 to 17, so the latest year can still change by a case or two.

Not carried.
  The region rows, the age table and the transmission tables, which count citizens only and so
  differ in population from the national count, and no panel id holds notified cases by age
  group or by transmission category.
  The children row, because the reports of 1 January 2026 and 1 July 2026 print different
  counts for years long closed.
  The rate per 100,000 people, which no panel id holds.
  The cumulative counts, the deaths since 1987 and the deaths from AIDS since 1987, which no
  panel id holds (ruling R31 of research/rulings_2026-10-15.md).
  The cascade of page 2 (11,015 people living with HIV registered, 7,962 on antiretroviral
  therapy and 7,366 with viral suppression on 1 July 2026). The report states no population for
  the cascade, and the count on treatment differs from the who_gho count of 7,596 for 2025, so
  the cascade counts cannot be placed under a panel definition.

Source type. routine_programme_record, the national HIV case register.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_URL = "https://aidscenter.kg/uploads/topics/17853979831150.pdf"
_LOCAL = "kg_aidscenter_situation_2026-07-01.pdf"
_KNOWN = (155_511, "1cb790432d6f")       # size and sha256 prefix of the copy read on 20 October 2026

_TITLE = re.compile(r"Ситуация во ВИЧ в КР на (\d{2})\.(\d{2})\.(\d{4})")
_HEAD_CITIZENS = re.compile(r"гр\.\s*КР\s*-\s*(\d+)")
_HEAD_FOREIGN = re.compile(r"иностр\.\s*гр\.\s*-\s*(\d+)")
_HEAD_ALL = re.compile(r"Всего\s*-\s*(\d+)")
_YEAR_LINE = re.compile(r"^Область((?:\s+\d{4})+)\s+%\s*$")
_AGE_YEAR_LINE = re.compile(r"^ВИЧ((?:\s+\d{4})+)\s+итог\s+%\s*$")
_SHARE = re.compile(r"\d+(?:,\d+)?")

_REGIONS = ("Баткен", "г.Бишкек", "г.Ош", "Жалал-Абад", "Иссык-Куль", "Нарынская", "Ошская",
            "Таласская", "Чуйская")
_TOTAL = "Общий итог"
_FOREIGN = "Иностр. гр."

_DEFINITION = ("HIV cases registered in the Kyrgyz Republic in the year, citizens of the Kyrgyz "
               "Republic (the row \"Общий итог\" of page 1) plus foreign citizens (the row "
               "\"Иностр. гр.\"), from the half-year situation report of the Republican Centre "
               "for the Control of Blood-borne Viral Hepatitis and HIV")
_RECONCILE = ("ecdc_hiv_report Table 1, equal for 2015, 2016, 2017, 2020, 2022 and 2023 and up "
              "to two cases apart in the other years from 2015 to 2024, and who_europe_hfa "
              "HFA_350, within two per cent in five of the seven years from 2013 to 2019. "
              "Never compare with new_diagnoses (Jason's ruling of 8 October 2026)")
_NOT_CARRIED = ("the region rows, the age table and the transmission tables (citizens only), the "
                "children row (the reports of 1 January 2026 and 1 July 2026 disagree), the rate "
                "per 100,000 people, the cumulative counts and deaths, and the cascade of page 2 "
                "(population not stated)")


def _row(lines: List[str], label: str, n_counts: int, with_share: bool) -> List[int]:
    """The counts of the single line which starts with `label`, checked for length and form."""
    hits = [ln for ln in lines if ln.startswith(label + " ")]
    if len(hits) != 1:
        raise ValueError(f"{len(hits)} lines start with {label!r}, expected one")
    tokens = hits[0][len(label):].split()
    if len(tokens) != n_counts + (1 if with_share else 0):
        raise ValueError(f"the row {label!r} holds {len(tokens)} entries, expected "
                         f"{n_counts + (1 if with_share else 0)}")
    counts, share = tokens[:n_counts], tokens[n_counts:]
    if not all(re.fullmatch(r"\d+", t) for t in counts):
        raise ValueError(f"the row {label!r} holds an entry which is not a count: {counts}")
    if share and not _SHARE.fullmatch(share[0]):
        raise ValueError(f"the row {label!r} ends in {share[0]!r}, which is not a share")
    return [int(t) for t in counts]


def parse_page1(text: str) -> Dict:
    """Page 1 as {report_date, report_year, years, regions, total, foreign, header}, after the
    gates of the module docstring. Raises ValueError when any gate fails."""
    title = _TITLE.search(text)
    if not title:
        raise ValueError("the report title with the report date was not found")
    day, month, year = title.groups()
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    year_lines = [m for m in (_YEAR_LINE.match(ln) for ln in lines) if m]
    if len(year_lines) != 1:
        raise ValueError(f"{len(year_lines)} year header lines start with 'Область', expected one")
    years = [int(y) for y in year_lines[0].group(1).split()]
    if years != list(range(years[0], years[0] + len(years))):
        raise ValueError(f"the year header is not a run of consecutive years: {years}")
    n = 1 + len(years) + 1           # the cumulative column, the years and the total
    regions = {r: _row(lines, r, n, True) for r in _REGIONS}
    total = _row(lines, _TOTAL, n, True)
    foreign = _row(lines, _FOREIGN, n, False)
    for label, counts in list(regions.items()) + [(_TOTAL, total), (_FOREIGN, foreign)]:
        if sum(counts[:-1]) != counts[-1]:
            raise ValueError(f"the row {label!r} adds to {sum(counts[:-1])} against the printed "
                             f"total of {counts[-1]}")
    for i in range(n):
        column = sum(c[i] for c in regions.values())
        if column != total[i]:
            raise ValueError(f"the regions add to {column} in column {i + 1} against the "
                             f"overall total of {total[i]}")
    header = {}
    for key, pattern in (("citizens", _HEAD_CITIZENS), ("foreign", _HEAD_FOREIGN),
                         ("all", _HEAD_ALL)):
        found = pattern.findall(text)
        if len(found) != 1:
            raise ValueError(f"the header count {key!r} was found {len(found)} times, expected once")
        header[key] = int(found[0])
    if header["citizens"] != total[-1] or header["foreign"] != foreign[-1] \
            or header["all"] != header["citizens"] + header["foreign"]:
        raise ValueError(f"the header counts {header} do not match the overall total of "
                         f"{total[-1]} and the foreign-citizens total of {foreign[-1]}")
    return {
        "report_title": title.group(0),
        "report_date": f"{year}-{month}-{day}",
        "report_year": int(year),
        "years": years,
        "regions": regions,
        "total": dict(zip(years, total[1:-1])),
        "foreign": dict(zip(years, foreign[1:-1])),
        "cumulative_first": (years[0] - 1, total[0]),
        "header": header,
    }


def age_table_years(text: str, page1: Dict) -> Tuple[Dict[int, str], str]:
    """The age-table check of page 2 per year, and a note on the cumulative column.

    Returns {year: "agrees" or a disagreement text}, and an empty dictionary with a note when
    the age table is not found."""
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    heads = [m for m in (_AGE_YEAR_LINE.match(ln) for ln in lines) if m]
    if len(heads) != 1:
        return {}, f"the age table was not found on page 2 ({len(heads)} year header lines)"
    printed = [int(y) for y in heads[0].group(1).split()]
    # the first printed year closes the label of the cumulative column ("1996- 2014")
    last_cumulative, years = printed[0], printed[1:]
    try:
        counts = _row(lines, _TOTAL, 1 + len(years) + 1, True)
    except ValueError as exc:
        return {}, f"the age table total row did not parse ({exc})"
    out: Dict[int, str] = {}
    for year, count in zip(years, counts[1:-1]):
        own = page1["total"].get(year)
        if own is None:
            continue
        out[year] = ("agrees" if own == count else
                     f"the age table prints {count} against {own} on page 1")
    first_year, first_count = page1["cumulative_first"]
    cumulative = first_count + sum(v for y, v in page1["total"].items() if y <= last_cumulative)
    note = (f"the age-table count to {last_cumulative} ({counts[0]}) "
            + ("equals" if cumulative == counts[0] else "differs from")
            + f" the page 1 count to {last_cumulative} ({cumulative}), and the age-table total "
            + f"({counts[-1]}) " + ("equals" if counts[-1] == sum(counts[:-1]) else "differs from")
            + " the sum of the age-table row")
    return out, note


class KyrgyzstanAidsCenterConnector(BaseConnector):
    """Half-year situation report of aidscenter.kg, notified HIV cases in Kyrgyzstan, national."""

    source_id = "kg_aidscenter"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Republican Centre for the Control of Blood-borne Viral Hepatitis and HIV of "
                   "the Kyrgyz Republic, situation report of 1 July 2026, HIV cases registered "
                   "in the year among citizens and foreign citizens, national, 2013 to 2025 "
                   "(to-source).")
    country = "KGZ"
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/kg_aidscenter", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the report, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("kg_aidscenter: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("kg_aidscenter: downloaded the report (%d bytes) -> %s", len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("kg_aidscenter: the report matches the copy read on 20 October 2026 "
                     "(sha256 %s)", digest[:12])
        else:
            log.warning("kg_aidscenter: the report differs from the copy read on 20 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s), and the gates still run",
                        len(blob), digest[:12], *_KNOWN)
        return path

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
            import pdfplumber
        except ImportError:
            log.error("kg_aidscenter: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
        except Exception as exc:
            log.warning("kg_aidscenter: the report could not be fetched (%s)", exc)
            return
        try:
            with pdfplumber.open(str(path)) as pdf:
                texts = [p.extract_text() or "" for p in pdf.pages[:2]]
            page1 = parse_page1(texts[0])
        except Exception as exc:
            log.warning("kg_aidscenter: page 1 failed a gate (%s), no row emitted", exc)
            return
        ages, age_note = age_table_years(texts[1] if len(texts) > 1 else "", page1)
        if not ages:
            log.warning("kg_aidscenter: %s, the age-table check is not run", age_note)
        emitted = 0
        for year in page1["years"]:
            if year >= page1["report_year"]:
                log.info("kg_aidscenter: %d is the year of the report date %s and covers part "
                         "of the year, no row emitted", year, page1["report_date"])
                continue
            if not start_year <= year <= end_year:
                continue
            check = ages.get(year)
            if check is not None and check != "agrees":
                log.warning("kg_aidscenter: %d, %s, no row emitted", year, check)
                continue
            citizens, foreign = page1["total"][year], page1["foreign"][year]
            emitted += 1
            yield self.make_row(
                country_iso3="KGZ", country_name="Kyrgyzstan", admin1="",
                indicator_id="notified_hiv_cases", year=year, value=float(citizens + foreign),
                unit="count", population_group=POP_ALL, sex=SEX_ALL, age_group=AGE_ALL,
                source_url=_URL,
                source_indicator_code="aidscenter_kg:situation:citizens+foreign",
                extra={
                    "report_title": page1["report_title"],
                    "report_date": page1["report_date"],
                    "citizens": citizens,
                    "foreign_citizens": foreign,
                    "definition": _DEFINITION,
                    "region_check": ("the nine region rows add to the overall total in every "
                                     "column, and every row adds to the printed total"),
                    "header_check": (f"the header prints {page1['header']['citizens']} citizens, "
                                     f"{page1['header']['foreign']} foreign citizens and "
                                     f"{page1['header']['all']} in all, equal to the totals of "
                                     f"the rows"),
                    "age_table_check": ("the age table of page 2 prints the same count of "
                                        "citizens" if check == "agrees" else
                                        "no age-table count for the year"),
                    "age_table_note": age_note,
                    "revision_note": ("the report of 1 January 2026 printed 1,087 citizens for "
                                      "2025 and the report of 1 July 2026 prints 1,086, so the "
                                      "latest year can still change by a case or two"),
                    "reconcile_with": _RECONCILE,
                    "not_carried": _NOT_CARRIED,
                },
            )
        log.info("kg_aidscenter: report of %s, emitted %d national rows", page1["report_date"],
                 emitted)
