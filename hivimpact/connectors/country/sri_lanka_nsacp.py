"""
Sri Lanka, National STD/AIDS Control Programme (NSACP), HIV cases reported in the year,
nationally, 2010 to 2025 (to-source, routine programme, national).

The NSACP of the Sri Lankan Ministry of Health publishes a yearly annual report on
aidscontrol.gov.lk. Figure 2.6 of the 2025 annual report ("Reporting of HIV Cases by Age and Sex")
prints a data table of the HIV cases reported in every year from 2010 to 2025, with rows for
children aged 0 to 14, women over 15, men over 15 and the total. The report is born-digital, so the
connector reads the pdfplumber text layer and uses no optical character recognition (OCR), under
ruling R25 of research/rulings_2026-10-15.md.

    year   2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025
    cases   121  144  186  196  228  235  249  285  350  439  363  411  607  693  824  874

WHY THE ANNUAL REPORT AND NOT THE QUARTERLY RETURNS
---------------------------------------------------
The NSACP also publishes a quarterly return of reported HIV cases. Ruling R8 refuses a yearly row
built by adding sub-year counts together, so the quarterly returns serve as a cross-check only and
never enter the panel. The quarterly sums differ from the 2025 table by one or two cases in five
years (2011, 144 in the table and 146 in the quarters, 2014, 228 and 229, 2015, 235 and 234, 2021,
411 and 410, and 2023, 693 and 694). For 2021 and 2023 the annual reports of the same year print the
table value (411 and 693), so the table holds the later NSACP figure. One table from one report
keeps every year on a single vintage of the count.

THE FILES
---------
  ar2025   the 2025 annual report, Figure 2.6, the source of every emitted value.
  q*       16 quarterly returns (the fourth quarter of 2010, 2011, 2012, 2013, 2014, 2016 to 2025,
           and the second quarter of 2026). Every return prints a table for the year before and a
           table for the year of the return, with one row per quarter giving the cumulative count
           at the start of the quarter, the cases reported in the quarter and the cumulative count
           at the end of the quarter.

The connector downloads every file once into `raw_dir`, and every later run reads the cached
copies. A cached copy whose size or sha256 differs from the copy read on 16 October 2026 is logged
as a WARNING and still parsed, because every gate below runs on the text.

WHAT THE COUNT IS
-----------------
The emitted value is the count of HIV cases the NSACP received reports of in the calendar year,
across Sri Lanka, as the 2025 annual report prints the count. The rows carry sex "all". The table
splits the count into children aged 0 to 14 of any sex, women over 15 and men over 15. For 2025 the
gender figure of the report reads 759 male, 112 female and three transgender cases, and the men
over 15 row (762) equals the male and transgender cases together, so a male row would count
transgender people as men, and the connector emits no row by sex. The
three table rows travel in extra for reference. Cumulative counts are refused under ruling R14.

INTEGRITY GATES
---------------
  * The 2025 report prints at least one Figure 2.6 table, every printed copy of the table is
    identical, every table row holds 16 whole numbers, and a line of the year words 2010 to 2025
    sits within three lines above the first table row.
  * For every year, children plus women plus men equals the total.
  * The prose under Figure 2.6 names the totals of 2010 and 2025 and the counts of men over 15 for
    2010 and 2025, and every value named equals the table.
  * Every quarterly return prints a table for the year before the return and for the year of the
    return, every table chains (start plus reported equals end, and the end of one quarter equals
    the start of the next), and a table for a full year holds four quarters.
  * Every year printed by two returns reads the same four quarters in every return, and the end of
    the fourth quarter of one year equals the start of the first quarter of the next year.
  * Every year from 2010 to 2025 has a full-year quarterly table, and the quarterly sum of every
    year differs from the table total by at most two cases.

Any failed gate refuses every row with a WARNING naming the reason. Counts unlike the table above
are logged as a WARNING and still emitted, because every gate has passed.

RECONCILIATION
--------------
No other source in the panel held Sri Lankan notified_hiv_cases or new_diagnoses rows when the
connector was built (checked 16 October 2026). Never compare with new_diagnoses (Jason's ruling of
8 October 2026).

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

_BASE = "https://www.aidscontrol.gov.lk/images/"
_NOTES = ("research/phase6_sas/sas_round1_notes.md, Sri Lanka, and ruling R25 of "
          "research/rulings_2026-10-15.md")

_REPORT_KEY = "ar2025"
_REPORT = ("publications/annual_reports/2025/NSACP_Annual_report_Final.pdf",
           "nsacp_annual_report_2025.pdf", (10_002_069, "feb96bbcab12"),
           "NSACP Annual Report 2025")

#: key -> (path under _BASE, local file name, (size, sha256 prefix) of the copy read on
#: 16 October 2026, the year of the return)
_RETURNS: Dict[str, Tuple[str, str, Tuple[int, str], int]] = {
    "q2010_4": ("pdfs/hiv_data/quarter_report/2010_4.pdf", "q2010_4.pdf",
                (88_345, "a822df2a4e3e"), 2010),
    "q2011_4": ("pdfs/hiv_data/quarter_report/2011_4.pdf", "q2011_4.pdf",
                (131_085, "47c03da49c86"), 2011),
    "q2012_4": ("pdfs/hiv_data/quarter_report/2012_4.pdf", "q2012_4.pdf",
                (127_629, "c8f940b7bbf0"), 2012),
    "q2013_4": ("pdfs/hiv_data/quarter_report/2013_4.pdf", "q2013_4.pdf",
                (157_020, "a82db48edda2"), 2013),
    "q2014_4": ("pdfs/hiv_data/quarter_report/2014_4.pdf", "q2014_4.pdf",
                (150_901, "71d2d51c54a6"), 2014),
    "q2016_4": ("pdfs/hiv_data/quarter_report/2016_4.pdf", "q2016_4.pdf",
                (167_061, "ac9f4b1093fd"), 2016),
    "q2017_4": ("HIV-4th-Q-2017_amended.pdf", "q2017_4.pdf", (496_868, "63b97582e513"), 2017),
    "q2018_4": ("HIV-4thQ2018revised.pdf", "q2018_4.pdf", (200_564, "4bdd2c2836b8"), 2018),
    "q2019_4": ("HIV-4th-Q2019.pdf", "q2019_4.pdf", (170_994, "81b8f5745f6f"), 2019),
    "q2020_4": ("HIV-4th-Q2020new.pdf", "q2020_4.pdf", (170_782, "1aa6bf900c59"), 2020),
    "q2021_4": ("pdfs/hiv_data/quarter_report/HIV-4thQ2021-1.pdf", "q2021_4.pdf",
                (170_162, "99aab0ecd29d"), 2021),
    "q2022_4": ("pdfs/hiv_data/quarter_report/HIV_4th_Q_2022docx.pdf", "q2022_4.pdf",
                (175_171, "cd8dcc8432ee"), 2022),
    "q2023_4": ("pdfs/hiv_data/quarter_report/HIV-AIDS_Quarterly_Report_-_4th_Quaretr_2023_V3.pdf",
                "q2023_4.pdf", (171_385, "7128947d1e6d"), 2023),
    "q2024_4": ("pdfs/hiv_data/2024_new_data/HIV-AIDS_Quarterly_Report_-_Q4_Cleaned_data_1.pdf",
                "q2024_4.pdf", (322_658, "72585026f65c"), 2024),
    "q2025_4": ("pdfs/hiv_data/2025/2025_Q4.pdf", "q2025_4.pdf", (323_127, "b1522eae27a5"), 2025),
    "q2026_2": ("pdfs/hiv_data/2026/2026_Q2.pdf", "q2026_2.pdf", (300_599, "79111558e338"), 2026),
}

_YEARS = tuple(range(2010, 2026))
_EXPECTED = dict(zip(_YEARS, (121, 144, 186, 196, 228, 235, 249, 285, 350, 439, 363, 411, 607,
                              693, 824, 874)))
#: The greatest difference in cases between the table total and the quarterly sum of a year.
_QUARTER_TOL = 2
_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")

_ROW_LABELS = (("children", "Children 0-14yr"), ("women", "Women>15yrs"), ("men", "Men>15yrs"),
               ("total", "Total"))
_YEAR_LINE = "".join(str(y) for y in _YEARS)
_PROSE_TOTAL = re.compile(r"rose from (\d{2,4}) in (20\d\d) to a record (\d{2,4}) in (20\d\d)")
_PROSE_MEN = re.compile(r"men over 15 years rising sharply from (\d{2,4}) in (20\d\d) to (\d{2,4}) "
                        r"in (20\d\d)")
_QUARTER = re.compile(r"^(1st|2nd|3rd|4th)\s*(?:Quarter|Quarte)?\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\b")
_HEADING = re.compile(r"(?i:REPORTED HIV/AIDS CASES|NATIONAL STD/AIDS CONTROL PROGRAMME|"
                      r"Reported HIV cases)\s+((?:19|20)\d\d)\s*$")
_ORDER = ("1st", "2nd", "3rd", "4th")


class _Refused(Exception):
    """A gate failed. Every row is refused, never part of the rows."""


def _numbers(rest: str) -> Optional[List[int]]:
    parts = rest.split()
    if not parts or not all(p.isdigit() for p in parts):
        return None
    return [int(p) for p in parts]


def _table(pages: List[str]) -> Dict:
    """Figure 2.6 of the 2025 report, the four rows of 16 counts, with every printed copy checked."""
    copies = []
    for pno, text in enumerate(pages, start=1):
        lines = [ln.strip() for ln in text.splitlines()]
        for i, ln in enumerate(lines):
            if not ln.startswith(_ROW_LABELS[0][1] + " "):
                continue
            rows: Dict[str, List[int]] = {}
            for k, (name, label) in enumerate(_ROW_LABELS):
                line = lines[i + k] if i + k < len(lines) else ""
                vals = _numbers(line[len(label):]) if line.startswith(label + " ") else None
                if vals is None or len(vals) != len(_YEARS):
                    raise _Refused(f"page {pno} of {_REPORT_KEY} prints the row {label!r} as "
                                   f"{line!r}, where 16 whole numbers belong")
                rows[name] = vals
            above = [re.sub(r"\s+", "", x) for x in lines[max(0, i - 3):i]]
            if _YEAR_LINE not in above:
                raise _Refused(f"page {pno} of {_REPORT_KEY} prints no line of the years 2010 to "
                               f"2025 within three lines above the table")
            copies.append((pno, rows))
    if not copies:
        raise _Refused(f"{_REPORT_KEY} prints no Figure 2.6 table of reported HIV cases by age "
                       f"and sex")
    first = copies[0][1]
    for pno, rows in copies[1:]:
        if rows != first:
            raise _Refused(f"the Figure 2.6 table on page {pno} differs from the table on page "
                           f"{copies[0][0]}")
    for i, year in enumerate(_YEARS):
        parts = first["children"][i] + first["women"][i] + first["men"][i]
        if parts != first["total"][i]:
            raise _Refused(f"the Figure 2.6 rows for {year} add to {parts}, where the total "
                           f"prints {first['total'][i]}")
    return {"page": copies[0][0], "copies": len(copies),
            "rows": {name: dict(zip(_YEARS, vals)) for name, vals in first.items()}}


def _prose(pages: List[str], table: Dict) -> int:
    """The sentences under Figure 2.6 naming the totals and the counts of men, checked."""
    text = re.sub(r"\s+", " ", " ".join(pages))
    checked = 0
    for pattern, row in ((_PROSE_TOTAL, "total"), (_PROSE_MEN, "men")):
        hits = list(pattern.finditer(text))
        if not hits:
            raise _Refused(f"{_REPORT_KEY} prints no sentence naming the {row} counts of 2010 and "
                           f"2025")
        for m in hits:
            for value, year in ((m.group(1), m.group(2)), (m.group(3), m.group(4))):
                y = int(year)
                if y not in table["rows"][row] or int(value) != table["rows"][row][y]:
                    raise _Refused(f"the sentence {m.group(0)!r} names {value} for {year}, where "
                                   f"the {row} row prints {table['rows'][row].get(y)}")
                checked += 1
    return checked


def _quarter_tables(key: str, text: str) -> List[Dict]:
    """The yearly tables of one quarterly return, every table chained."""
    tables: List[Dict] = []
    cur: Optional[Dict] = None
    year: Optional[int] = None
    for ln in text.splitlines():
        m = _HEADING.search(ln)
        if m:
            year = int(m.group(1))
        m = _QUARTER.match(ln.strip())
        if not m:
            continue
        start, new, end = (int(x.replace(",", "")) for x in m.group(2, 3, 4))
        if m.group(1) == "1st":
            if year is None:
                raise _Refused(f"{key} prints a quarterly table with no year heading")
            cur = {"year": year, "rows": []}
            tables.append(cur)
            year = None
        if cur is None:
            raise _Refused(f"{key} prints the {m.group(1)} quarter before the first quarter")
        cur["rows"].append((m.group(1), start, new, end))
    want = _RETURNS[key][3]
    if [t["year"] for t in tables] != [want - 1, want]:
        raise _Refused(f"{key} prints tables for {[t['year'] for t in tables]}, where "
                       f"{[want - 1, want]} belong")
    for t in tables:
        rows = t["rows"]
        if tuple(r[0] for r in rows) != _ORDER[:len(rows)]:
            raise _Refused(f"{key} prints the quarters {[r[0] for r in rows]} for {t['year']}")
        for q, start, new, end in rows:
            if start + new != end:
                raise _Refused(f"{key} prints {start} plus {new} as {end} for the {q} quarter of "
                               f"{t['year']}")
        for a, b in zip(rows, rows[1:]):
            if a[3] != b[1]:
                raise _Refused(f"{key} ends the {a[0]} quarter of {t['year']} at {a[3]} and starts "
                               f"the {b[0]} quarter at {b[1]}")
    for prev, nxt in zip(tables, tables[1:]):
        if len(prev["rows"]) == 4 and prev["rows"][-1][3] != nxt["rows"][0][1]:
            raise _Refused(f"{key} ends {prev['year']} at {prev['rows'][-1][3]} and starts "
                           f"{nxt['year']} at {nxt['rows'][0][1]}")
    return tables


def _quarters(texts: Dict[str, str]) -> Dict[int, Dict]:
    """The full-year quarterly tables of every return, with every double reading checked."""
    by_year: Dict[int, Dict] = {}
    for key, text in texts.items():
        for t in _quarter_tables(key, text):
            if len(t["rows"]) != 4:
                if t["year"] == _RETURNS[key][3]:
                    continue        # the year of a return before the fourth quarter
                raise _Refused(f"{key} prints {len(t['rows'])} quarters for {t['year']}")
            seen = by_year.get(t["year"])
            if seen is None:
                by_year[t["year"]] = {"rows": t["rows"], "files": [key]}
            elif seen["rows"] != t["rows"]:
                raise _Refused(f"{key} and {seen['files'][0]} print different quarters for "
                               f"{t['year']}")
            else:
                seen["files"].append(key)
    for year in sorted(by_year):
        nxt = by_year.get(year + 1)
        if nxt and by_year[year]["rows"][-1][3] != nxt["rows"][0][1]:
            raise _Refused(f"the returns end {year} at {by_year[year]['rows'][-1][3]} and start "
                           f"{year + 1} at {nxt['rows'][0][1]}")
    return by_year


def _compare(table: Dict, by_year: Dict[int, Dict]) -> Dict[int, int]:
    sums: Dict[int, int] = {}
    for year in _YEARS:
        if year not in by_year:
            raise _Refused(f"no quarterly return prints four quarters for {year}")
        total = table["rows"]["total"][year]
        qsum = sum(r[2] for r in by_year[year]["rows"])
        if abs(qsum - total) > _QUARTER_TOL:
            raise _Refused(f"the quarters of {year} add to {qsum}, where Figure 2.6 prints {total}")
        if qsum != total:
            log.info("lk_nsacp: the quarters of %d add to %d and Figure 2.6 prints %d", year, qsum,
                     total)
        sums[year] = qsum
    return sums


class SriLankaNSACPConnector(BaseConnector):
    """Sri Lanka, NSACP annual report 2025, HIV cases reported in the year, 2010 to 2025."""

    source_id = "lk_nsacp"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Annual report 2025 of the Sri Lankan National STD/AIDS Control Programme, HIV "
                   "cases reported in the year, nationally, 2010 to 2025 (to-source).")
    country = "LKA"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/sri_lanka_nsacp", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, key: str, rel: str, local: str, known: Tuple[int, str]) -> Path:
        """Local copy of one file, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / local
        if path.exists():
            log.info("lk_nsacp: using cached %s", path)
        else:
            blob = self._request("GET", _BASE + rel).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_BASE + rel} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("lk_nsacp: downloaded %s (%.1f MB) -> %s", key, len(blob) / 1e6, path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == known:
            log.info("lk_nsacp: %s matches the copy read on 16 October 2026 (sha256 %s)", key,
                     digest[:12])
        else:
            log.warning("lk_nsacp: %s differs from the copy read on 16 October 2026 (%d bytes, "
                        "sha256 %s, expected %d bytes, %s), and the text gates still run", key,
                        len(blob), digest[:12], *known)
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
            log.error("lk_nsacp: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            report = self._pdf_path(_REPORT_KEY, _REPORT[0], _REPORT[1], _REPORT[2])
            returns = {key: self._pdf_path(key, rel, local, known)
                       for key, (rel, local, known, _) in _RETURNS.items()}
        except Exception as exc:
            log.warning("lk_nsacp: an NSACP file could not be fetched (%s)", exc)
            return
        try:
            table = self._parse(pdfplumber, report, returns)
        except _Refused as exc:
            log.warning("lk_nsacp: every row refused because %s", exc)
            return
        except Exception as exc:
            log.warning("lk_nsacp: the NSACP files failed to parse (%s)", exc)
            return
        emitted = 0
        for row in self._rows(table, start_year, end_year):
            emitted += 1
            yield row
        log.info("lk_nsacp: emitted %d rows", emitted)

    def _parse(self, pdfplumber, report: Path, returns: Dict[str, Path]) -> Dict:
        with pdfplumber.open(str(report)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        table = _table(pages)
        prose = _prose(pages, table)
        texts: Dict[str, str] = {}
        for key, path in returns.items():
            with pdfplumber.open(str(path)) as pdf:
                texts[key] = "\n".join(p.extract_text() or "" for p in pdf.pages)
        by_year = _quarters(texts)
        sums = _compare(table, by_year)
        for year, want in _EXPECTED.items():
            if table["rows"]["total"][year] != want:
                log.warning("lk_nsacp: %d reads %d cases, where the copy read on 16 October 2026 "
                            "printed %d", year, table["rows"]["total"][year], want)
        n = table["copies"]
        copies = ("%s printed cop%s" % (_WORDS[n] if n < 10 else n, "y" if n == 1 else "ies"))
        log.info("lk_nsacp: Figure 2.6 on page %d of %s (%s), %s prose values checked, every "
                 "gate passed", table["page"], _REPORT_KEY, copies,
                 _WORDS[prose] if prose < 10 else prose)
        return {"table": table, "quarters": by_year, "sums": sums}

    def _rows(self, parsed: Dict, start_year: int, end_year: int) -> Iterator[PanelRow]:
        table, by_year, sums = parsed["table"], parsed["quarters"], parsed["sums"]
        rows = table["rows"]
        for year in _YEARS:
            if not start_year <= year <= end_year:
                continue
            extra: Dict = {
                "edition": _REPORT[3],
                "page": table["page"],
                "caption": "Figure 2.6, Reporting of HIV Cases by Age and Sex",
                "extraction": "text layer, the Total row of the Figure 2.6 data table",
                "children_0_14": rows["children"][year],
                "women_over_15": rows["women"][year],
                "men_over_15": rows["men"][year],
                "quarterly_sum": sums[year],
                "quarterly_returns": by_year[year]["files"],
                "definition": ("HIV cases reported to the National STD/AIDS Control Programme in "
                               "the calendar year across Sri Lanka, as the 2025 annual report "
                               "prints the count, with no split by sex"),
                "integrity": ("children plus women plus men equal the total in every year, the "
                              "prose names the table values, every quarterly return chains, and "
                              "the quarterly sum of every year lies within two cases of the "
                              "total (ruling R8 keeps the quarterly sums out of the panel)"),
                "reconcile_with": (
                    "No other source in the panel held Sri Lankan notified_hiv_cases or "
                    "new_diagnoses rows when the connector was built (checked 16 October 2026). "
                    "Never compare with new_diagnoses (Jason's ruling of 8 October 2026)"),
                "notes": _NOTES,
            }
            yield self.make_row(
                country_iso3="LKA", country_name="Sri Lanka",
                indicator_id="notified_hiv_cases", year=year, value=rows["total"][year],
                unit="count", admin1="",
                source_url=_BASE + _REPORT[0],
                source_indicator_code="nsacp_annual_report_2025.figure2_6.total",
                extra=extra,
            )
