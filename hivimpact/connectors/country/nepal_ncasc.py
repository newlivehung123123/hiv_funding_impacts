"""
Nepal, National Centre for AIDS and STD Control (NCASC), HIV positive results at the HIV testing
and counselling sites in the year, nationally, 2008 to 2018 (to-source, routine programme,
national).

The NCASC of the Nepalese Ministry of Health and Population published a set of factsheets for every
World AIDS Day. Factsheet 3 ("HIV Testing and Counseling") of the sets of 2012 to 2017, and the HIV
testing and counselling section of the combined factsheets of 2018 and 2019, print Table 1 with the
clients tested for HIV and the clients with an HIV positive result in every calendar year from 2008,
2009 or 2010 up to July of the year of the edition. The rebuild of www.ncasc.gov.np in May 2025
removed the older file paths, so the connector reads Wayback Machine captures of six editions, under
ruling R67 of research/rulings_2026-10-15.md. The factsheets are born-digital, so the connector
reads the pdfplumber text layer and uses no optical character recognition (OCR).

    year       2008  2009  2010  2011  2012  2013  2014  2015  2016  2017  2018
    positive  2,387 2,110 2,015 2,060 2,433 2,426 1,907 1,610 2,144 1,842 2,226

WHICH CAPTURES
--------------
  key      captured           edition                                       columns of Table 1
  2014fs3  18 April 2025      Factsheet 3 of 2014                            2008 to July 2014
  2015fs3  20 April 2025      Factsheet 3 of 2015                            2008 to July 2015
  2016fs3  2 May 2025         Factsheet 3 of 2016, a draft by the file name  2008 to July 2016
  2017fs3  25 November 2018   Factsheet 3 of 2017                            2009 to July 2017
  2018     18 August 2022     combined factsheet of 2018, page 5             2009 to July 2018
  2019b    6 December 2021    combined factsheet of 2019, page 5             2010 to July 2019

Every emitted year comes from the latest edition which prints the year as a full calendar year and
whose file name does not mark the edition as a draft. 2008 therefore comes from 2015fs3, 2009 from
2018, and 2010 to 2018 from 2019b. The other editions travel in extra.editions as cross-checks.
Factsheet 3 of 2012 prints chart labels between the rows of Table 1, and the text layer of
Factsheet 3 of 2013 holds unreadable character identifiers, so the 2012 file and the 2013 file never
enter the connector. The 2019 capture of 18 August 2022 and every capture of the factsheets of 2020
and 2021 stop at 1,048,576 bytes with no end-of-file marker, and the connector reads the 2019
capture of 6 December 2021, which is complete.

The connector downloads every capture once into `raw_dir`, and every later run reads the cached
copies. A cached copy whose size or sha256 differs from the copy read on 25 October 2026 is logged
as a WARNING and still parsed, because every gate below runs on the text.

WHAT THE COUNT IS
-----------------
The emitted value is the HIV positive row of Table 1, the count of clients with an HIV positive
result at the NCASC HIV testing and counselling sites in the calendar year. Factsheet 2 of 2012
prints the reported HIV infections by age group for 2009 to 2011, and the age groups add to 2,110,
2,015 and 2,060, the HIV positive row of Table 1 for the same three years. Factsheet 7 of 2019 says
the routine case reporting of HIV runs from the HIV testing and counselling sites and the sites for
the prevention of mother-to-child transmission (PMTCT). The NCASC therefore reports the HIV positive
results of Table 1 as the reported HIV cases of the year, and the rows carry notified_hiv_cases with
sex "all" and age "all". The last column of every edition covers January to July only and never
enters. The Tested for HIV row counts clients tested and not tests with the result returned, so the
Tested for HIV row never enters hiv_tests_performed and travels in extra.clients_tested for
reference.

INTEGRITY GATES
---------------
  * Every file starts with %PDF and ends with %%EOF, so a truncated capture never parses.
  * Every edition prints exactly one Table 1 title, the title ends on the year of the edition, the
    year words between the title and the first row equal the columns listed above, a July marker
    names the last column as a part year, and exactly one Tested for HIV row and one HIV positive
    row follow, every row with one whole number per column.
  * In every column the HIV positive count is below the Tested for HIV count.
  * Every full year printed by two or more editions reads the same Tested for HIV count and the
    same HIV positive count in every edition, with one known revision. The 2018 edition prints
    1,856 HIV positive results for 2017 and the 2019 edition prints 1,842, and the later count
    enters.

Any failed gate refuses every row with a WARNING naming the reason. Counts unlike the table above
are logged as a WARNING and still emitted, because every gate has passed.

RECONCILIATION
--------------
No other source in the panel held Nepalese notified_hiv_cases rows when the connector was built
(checked 25 October 2026). The Nepalese new_diagnoses rows come from PEPFAR for 2020 to 2025 only.
Never compare with new_diagnoses (Jason's ruling of 8 October 2026).

TAGGING. source_type is routine_programme_record (national case reporting).
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_WAYBACK = "https://web.archive.org/web/{ts}id_/{url}"
_NOTES = ("research/phase6_sas/sas_round1_notes.md, Nepal, and ruling R67 of "
          "research/rulings_2026-10-15.md")

# key -> (capture timestamp, archived address, (bytes, sha256 prefix) read on 25 October 2026,
#         columns of Table 1 with the part year last, draft by the file name, edition label)
_EDITIONS: Dict[str, Tuple[str, str, Tuple[int, str], Tuple[int, ...], bool, str]] = {
    "2014fs3": ("20250418165357",
                "https://ncasc.gov.np/uploads/frontend/tabData/"
                "2014_Factsheet_3_HIV_Testing_And_Counseling_2014.pdf",
                (154061, "23ac8f5697bf"), tuple(range(2008, 2015)), False,
                "Factsheet 3, HIV Testing and Counseling, World AIDS Day 2014"),
    "2015fs3": ("20250420062059",
                "https://ncasc.gov.np/uploads/frontend/tabData/"
                "Factsheet%203%20HIV%20testing%20and%20counseling_2015.pdf",
                (398419, "dcb2c18c8770"), tuple(range(2008, 2016)), False,
                "Factsheet 3, HIV testing and counseling, World AIDS Day 2015"),
    "2016fs3": ("20250502111155",
                "http://www.ncasc.gov.np/uploads/frontend/tabData/"
                "Draft_Factsheet_3_HIV_testing_and_counseling_2016.pdf",
                (957900, "73c8d9bd7ec8"), tuple(range(2008, 2017)), True,
                "Draft Factsheet 3, HIV testing and counseling, World AIDS Day 2016"),
    "2017fs3": ("20181125195029",
                "http://ncasc.gov.np:80/WAD2017/FACTSHEET-2017-FINAL/"
                "Factsheet-3-HIV-testing-and-counseling-2017.pdf",
                (1065618, "39776047f7c1"), tuple(range(2009, 2018)), False,
                "Factsheet 3, HIV testing and counseling, World AIDS Day 2017"),
    "2018": ("20220818205251",
             "https://ncasc.gov.np/wad-2018/file/Factsheet-2018-final.pdf",
             (904305, "c7c50a578d09"), tuple(range(2009, 2019)), False,
             "Factsheet 2018, World AIDS Day, Fact sheet 3"),
    "2019b": ("20211206002910",
              "http://www.ncasc.gov.np/WAD2019/Factsheet2019.pdf",
              (1119569, "c880c39f5114"), tuple(range(2010, 2020)), False,
              "Factsheet 2019, World AIDS Day, Factsheet 3"),
}
_YEARS = tuple(range(2008, 2019))
_EXPECTED = dict(zip(_YEARS, (2387, 2110, 2015, 2060, 2433, 2426, 1907, 1610, 2144, 1842, 2226)))
# (edition, year) -> the HIV positive count the earlier edition prints where a later edition
# revised the count. Any other disagreement between editions refuses every row.
_REVISIONS = {("2018", 2017): 1856}
_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")

_TITLE = re.compile(r"^Table 1: HIV Testing and Counseling\s*(\d{4})\s*[-‐–]\s*"
                    r"(?:July\s*)?(\d{4})\b")
_ROW = re.compile(r"^(Tested for HIV|HIV positive) (\d.*)$")
_NUMBER = re.compile(r"^(?:\d{1,3}(?:,\d{3})+|\d{1,3})$")
_YEAR_WORD = re.compile(r"(?<![\d,])((?:19|20)\d\d)(?![\d,])")
_LABELLED_NUMBERS = re.compile(r"^[A-Za-z][A-Za-z \-‐+]*\s(?:[\d,]+\s*)+$")
_JULY = re.compile(r"\bJul(?:y)?\b")


class _Refused(Exception):
    """A gate failed. Every row is refused, never part of the rows."""


def _num(n: int) -> str:
    return _WORDS[n] if 0 <= n < 10 else str(n)


def _numbers(rest: str) -> Optional[List[int]]:
    parts = rest.split()
    if not parts or not all(_NUMBER.match(p) for p in parts):
        return None
    return [int(p.replace(",", "")) for p in parts]


def _table(key: str, pages: List[str]) -> Dict:
    """Table 1 of one edition, as {"page", "title", "tested", "positive"} keyed by column year."""
    columns = _EDITIONS[key][3]
    found = []
    for page_no, text in enumerate(pages, start=1):
        lines = [ln.strip() for ln in text.splitlines()]
        for i, line in enumerate(lines):
            m = _TITLE.match(line)
            if m:
                found.append((page_no, lines, i, m))
    if len(found) != 1:
        raise _Refused(f"{key} prints {_num(len(found))} Table 1 titles where one was expected")
    page_no, lines, start, m = found[0]
    if int(m.group(2)) != columns[-1]:
        raise _Refused(f"the Table 1 title of {key} ends on {m.group(2)} where {columns[-1]} "
                       "was expected")
    header: List[str] = []
    rows: Dict[str, List[List[int]]] = {"Tested for HIV": [], "HIV positive": []}
    for line in lines[start + 1:start + 13]:
        row = _ROW.match(line)
        if row:
            values = _numbers(row.group(2))
            if values is None:
                raise _Refused(f"the {row.group(1)} row of {key} holds a value which is not a "
                               "whole number")
            rows[row.group(1)].append(values)
        elif not any(rows.values()) and not (_LABELLED_NUMBERS.match(line)
                                             and not line.startswith("Indicators")):
            header.append(line)
    years = sorted(int(y) for y in _YEAR_WORD.findall(" ".join(header)))
    if tuple(years) != columns:
        raise _Refused(f"the Table 1 header of {key} prints the years {years} where "
                       f"{list(columns)} were expected")
    if not _JULY.search(" ".join(header)):
        raise _Refused(f"the Table 1 header of {key} names no July part year")
    out: Dict = {"page": page_no, "title": lines[start]}
    for label, found_rows in rows.items():
        if len(found_rows) != 1:
            raise _Refused(f"{key} prints {_num(len(found_rows))} {label} rows under Table 1 "
                           "where one was expected")
        if len(found_rows[0]) != len(columns):
            raise _Refused(f"the {label} row of {key} holds {_num(len(found_rows[0]))} values "
                           f"where {_num(len(columns))} were expected")
        out[label] = dict(zip(columns, found_rows[0]))
    for year in columns:
        if not out["HIV positive"][year] < out["Tested for HIV"][year]:
            raise _Refused(f"{key} prints {out['HIV positive'][year]} HIV positive results for "
                           f"{year} against {out['Tested for HIV'][year]} clients tested")
    return out


def _source_edition(year: int) -> str:
    keys = [k for k, ed in _EDITIONS.items() if year in ed[3][:-1] and not ed[4]]
    return keys[-1]


def _compare(tables: Dict[str, Dict]) -> Dict[int, Dict]:
    """Cross-check every full year across the editions and pick the source edition."""
    by_year: Dict[int, Dict] = {}
    for year in _YEARS:
        source = _source_edition(year)
        want = {label: tables[source][label][year] for label in ("Tested for HIV", "HIV positive")}
        editions: Dict[str, int] = {}
        for key, ed in _EDITIONS.items():
            if year not in ed[3][:-1]:
                continue
            for label in ("Tested for HIV", "HIV positive"):
                got = tables[key][label][year]
                allowed = want[label]
                if label == "HIV positive" and (key, year) in _REVISIONS:
                    allowed = _REVISIONS[(key, year)]
                if got != allowed:
                    raise _Refused(f"{key} prints {got} for {label} in {year} where {source} "
                                   f"prints {want[label]}")
            editions[key] = tables[key]["HIV positive"][year]
        by_year[year] = {"source": source, "positive": want["HIV positive"],
                         "tested": want["Tested for HIV"], "editions": editions}
    return by_year


class NepalNCASCConnector(BaseConnector):
    """Nepal, NCASC World AIDS Day factsheets, HIV positive results in the year, 2008 to 2018."""

    source_id = "np_ncasc"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("World AIDS Day factsheets of the Nepalese National Centre for AIDS and STD "
                   "Control, read from Wayback captures, HIV positive results at the HIV testing "
                   "and counselling sites in the year, nationally, 2008 to 2018 (to-source).")
    country = "NPL"
    timeout = 300
    # The Wayback Machine refused the ni_mapasalud runs of October 2026 with HTTP 429 at short
    # pauses, so the connector keeps the ni_mapasalud pacing. The connector pauses 30 seconds
    # after every capture, tries a capture four times, and waits 10, 15 and 15 minutes after a 429
    # or a network error.
    request_pause = 30.0

    def __init__(self, raw_dir: str = "data/raw/nepal_ncasc", **kw):
        kw.setdefault("max_retries", 4)
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _retry_wait(self, attempt: int, status: Optional[int]) -> float:
        if attempt >= self.max_retries:
            return 0
        if status in (429, None):
            return 600 if attempt == 1 else 900
        return super()._retry_wait(attempt, status)

    def _pdf(self, key: str) -> Path:
        """Local copy of one capture, downloading only if not cached."""
        ts, url, known = _EDITIONS[key][:3]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / f"{key}_{ts}.pdf"
        if path.exists():
            log.info("np_ncasc: using cached %s", path)
        else:
            capture = _WAYBACK.format(ts=ts, url=url)
            blob = self._request("GET", capture).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{capture} did not return a PDF (got {blob[:16]!r})")
            if not blob.rstrip().endswith(b"%%EOF"):
                raise RuntimeError(f"{capture} returned {len(blob)} bytes with no end-of-file "
                                   "marker, a truncated copy")
            path.write_bytes(blob)
            log.info("np_ncasc: downloaded the %s capture of %s (%d bytes) -> %s", key, ts,
                     len(blob), path)
        blob = path.read_bytes()
        if not blob.startswith(b"%PDF") or not blob.rstrip().endswith(b"%%EOF"):
            raise _Refused(f"the cached {key} copy is not a complete PDF ({len(blob)} bytes)")
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) != known:
            log.warning("np_ncasc: the %s capture differs from the copy read on 25 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s). The table gates still run",
                        key, len(blob), digest[:12], *known)
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
        if end_year < _YEARS[0] or start_year > _YEARS[-1]:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("np_ncasc: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            paths = {key: self._pdf(key) for key in _EDITIONS}
        except _Refused as exc:
            log.warning("np_ncasc: every row refused because %s", exc)
            return
        except Exception as exc:
            log.warning("np_ncasc: an NCASC capture could not be fetched (%s)", exc)
            return
        try:
            by_year = self._parse(pdfplumber, paths)
        except _Refused as exc:
            log.warning("np_ncasc: every row refused because %s", exc)
            return
        except Exception as exc:
            log.warning("np_ncasc: the NCASC captures failed to parse (%s)", exc)
            return
        emitted = 0
        for row in self._rows(by_year, start_year, end_year):
            emitted += 1
            yield row
        log.info("np_ncasc: emitted %d rows", emitted)

    def _parse(self, pdfplumber, paths: Dict[str, Path]) -> Dict:
        tables: Dict[str, Dict] = {}
        for key, path in paths.items():
            with pdfplumber.open(str(path)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            tables[key] = _table(key, pages)
        by_year = _compare(tables)
        for year, want in _EXPECTED.items():
            if by_year[year]["positive"] != want:
                log.warning("np_ncasc: %d reads %d HIV positive results, where the copy read on "
                            "25 October 2026 printed %d", year, by_year[year]["positive"], want)
        for year in by_year:
            by_year[year]["page"] = tables[by_year[year]["source"]]["page"]
            by_year[year]["title"] = tables[by_year[year]["source"]]["title"]
        log.info("np_ncasc: Table 1 read from %s editions, every gate passed", _num(len(tables)))
        return by_year

    def _rows(self, by_year: Dict[int, Dict], start_year: int, end_year: int) -> Iterator[PanelRow]:
        for year in _YEARS:
            if not start_year <= year <= end_year:
                continue
            got = by_year[year]
            ts, url, _, _, _, label = _EDITIONS[got["source"]]
            extra: Dict = {
                "edition": label,
                "page": got["page"],
                "caption": got["title"],
                "page_url": url,
                "capture_url": _WAYBACK.format(ts=ts, url=url),
                "captured": f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}",
                "extraction": "text layer, the HIV positive row of Table 1",
                "clients_tested": got["tested"],
                "editions": got["editions"],
                "definition": ("clients with an HIV positive result at the HIV testing and "
                               "counselling sites of the NCASC in the calendar year across Nepal, "
                               "which the NCASC reports as the reported HIV cases of the year"),
                "integrity": ("every capture is a complete PDF, the Table 1 header of every "
                              "edition prints the expected years with a July part year last, "
                              "and every full year agrees across the editions except the known "
                              "revision of 2017 from 1,856 (2018 edition) to 1,842 (2019 "
                              "edition)"),
                "reconcile_with": (
                    "No other source in the panel held Nepalese notified_hiv_cases rows when the "
                    "connector was built (checked 25 October 2026). Never compare with "
                    "new_diagnoses, which PEPFAR carries for 2020 to 2025 (Jason's ruling of "
                    "8 October 2026)"),
                "notes": _NOTES,
            }
            yield self.make_row(
                country_iso3="NPL", country_name="Nepal",
                indicator_id="notified_hiv_cases", year=year, value=got["positive"],
                unit="count", admin1="",
                source_url=url,
                source_indicator_code="ncasc_factsheet3.table1.hiv_positive",
                extra=extra,
            )
