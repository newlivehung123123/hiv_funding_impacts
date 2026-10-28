"""
Belize, Ministry of Health HIV Surveillance Report 2018: newly diagnosed HIV by district, 2018
(to-source, routine programme, sub-national).

Source: the Epidemiology Unit of Belize's Ministry of Health published the HIV Surveillance
Report 2018 in July 2019, and the National AIDS Commission hosts the file at nacbelize.org as
HIV-stats-report-for-2018.pdf (29 pages). The counts come from HIV case-based surveillance in
BHIS (the Belize Health Information System) for January to December 2018, and the report text
calls the 2018 counts preliminary. Table 4 on PDF page 11, "Newly Diagnosed HIV by District and
Sex 2018", has one row for each of Belize's six districts, an Unknown row and a Grand Total row,
and three columns: Female, Male and Grand Total. The PDF is born-digital, so there is no OCR here.

The report is downloaded once into `raw_dir` and read from the cached copy after that. A cached
copy whose size or sha256 differs from the copy read on 8 October 2026 is logged as a WARNING and
still parsed, because every gate below runs on the table itself.

    report  table    PDF page  female  male  all   district unknown
    2018    Table 4  11        84      170   254   2

WHAT IS EMITTED
---------------
`notified_hiv_cases` for 2018 for the six districts, both sexes together, with the female and
male counts in `extra`. Jason ruled on 8 October 2026 that a ministry's own count of HIV cases
from case surveillance goes under `notified_hiv_cases` and is never merged with or compared to
`new_diagnoses` (research/phase5_lac/lac_round1_notes.md, section on the Belize report of the
download pass of 8 October 2026).

The national Grand Total row is NOT emitted. `paho_core` already holds 254 for Belize 2018 from
PAHO Core Indicator 93, equal to the report, so a second national row would duplicate the PAHO
row. The two cases of unknown district are not emitted either, as the panel has no admin1 value
for an unknown district. Every district row carries the national total and the unknown count in
`extra`, so the six district rows sum to 252 and the gap of two is explained on every row.

PARSING
-------
The table is found by CAPTION TEXT. A caption is a line reading "Table N: Newly Diagnosed HIV by
District and Sex YYYY", followed by a line reading "Newly Diagnosed HIV by District, YYYY", with
both years equal to 2018. No other line of the report matches the caption pattern (checked 13
October 2026, all 29 pages). The header lines between the caption and the first district row
must include "Row Labels Female Male Total", and at most four header lines are allowed.

Cells are delimited on the gap between words, as `_pdf_text.columns` does. Gaps between the
count columns of Table 4 measured 21.27 to 69.12 points and gaps inside a district name 2.95 to
3.04 points (measured 13 October 2026), so the 10-point default sits in the empty range between
the two. Every cell of the
table is one word, so a cell printed as several words refuses the report.

INTEGRITY GATES
---------------
  * exactly one caption in the report passes the caption gate;
  * every line from the first district row to the Grand Total row is one of the six districts,
    the Unknown row or the Grand Total row, each found exactly once, with exactly three cells;
  * in every row, female plus male equals the row total;
  * the six districts and the Unknown row sum exactly to the Grand Total row in all three columns.

Any failed gate refuses the report with a WARNING naming the reason. A Grand Total row that
differs from the figures in the table above is logged as a WARNING, and the rows are still
emitted, since the gates have passed.

LABELS
------
`admin1` carries the district names the panel already uses for Belize in pepfar_snu ("Belize
District", "Cayo District", "Orange Walk District"), with the same pattern for the other three
districts. The report's own label goes into `extra.admin1_source_label`.

RECONCILIATION
--------------
No other source in the panel held Belize district rows of `notified_hiv_cases` when this
connector was built (checked 13 October 2026). The pepfar_snu district rows for 2016 are other
indicators. Nationally, `paho_core` reads 254 for 2018, equal to the report, with 85 women and
169 men against 84 women and 170 men in Table 4. The difference of one in the sex split is
recorded on every row and NOT VERIFIED as to cause.

TAGGING: source_type = routine_programme_record (case-based surveillance in BHIS, per the table's
own source line).
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
from ._pdf_text import COL_GAP, lines as _lines, norm as _norm

log = logging.getLogger("hivimpact")

_URL = "https://nacbelize.org/wp-content/uploads/2015/11/HIV-stats-report-for-2018.pdf"
_LOCAL = "hiv_surveillance_report_2018.pdf"
_NOTES = ("research/phase5_lac/lac_round1_notes.md, the Belize entry of the download pass of 8 "
          "October 2026")

#: The report read on 8 October 2026: (size, sha256 prefix), the report year, the 1-based page the
#: table was read on by hand (provenance only) and the Grand Total row, checked as a fingerprint.
_KNOWN = (1_541_580, "743943e943ed")
_YEAR = 2018
_PAGE = 11
_TOTAL = {"female": 84, "male": 170, "total": 254}

#: Normalised row label -> admin1. "" is the national Grand Total row and None the Unknown row,
#: neither of which is emitted.
_ROWS: Dict[str, Optional[str]] = {
    "belize": "Belize District",
    "cayo": "Cayo District",
    "corozal": "Corozal District",
    "orange walk": "Orange Walk District",
    "stann creek": "Stann Creek District",
    "toledo": "Toledo District",
    "unknown": None,
    "grand total": "",
}

_CAPTION = re.compile(r"^table (\d+) newly diagnosed hiv by district and sex (\d{4})$")
_CAPTION_2 = "newly diagnosed hiv by district {year}"
_HEADER_COLS = "row labels female male total"
_COLS = ("female", "male", "total")
_NUMERIC = re.compile(r"^[\d.,]+$")
_COUNT = re.compile(r"^(?:\d{1,3}(?:,\d{3})+|\d+)$")
_MAX_HEADER_LINES = 4

_PRELIMINARY = ("preliminary. The report text reads 'Preliminary data for 2018, shows that there "
                "were 254 newly diagnosed cases of HIV Infection in Belize'")


class _Refused(Exception):
    """A gate failed. The whole report is refused, never part of it."""


def _split(ln: Dict) -> Tuple[str, List[List[Dict]]]:
    """A line's label (the words before the first numeric word) and its numeric word groups,
    grouped on the measured gap between words."""
    words = ln["words"]
    k = 0
    while k < len(words) and not _NUMERIC.match(words[k]["text"]):
        k += 1
    label = " ".join(w["text"] for w in words[:k])
    groups: List[List[Dict]] = []
    for w in words[k:]:
        if groups and (w["x0"] - groups[-1][-1]["x1"]) < COL_GAP:
            groups[-1].append(w)
        else:
            groups.append([w])
    return label, groups


def _read_row(raw: str, groups: List[List[Dict]]) -> Dict[str, int]:
    if len(groups) != len(_COLS):
        raise _Refused(f"the row {raw!r} has {len(groups)} cells where three belong")
    out: Dict[str, int] = {}
    for col, group in zip(_COLS, groups):
        texts = [w["text"] for w in group]
        if len(texts) != 1:
            raise _Refused(f"the row {raw!r} prints {' '.join(texts)!r} as one cell, where every "
                           f"cell of the table is one word")
        if not _COUNT.match(texts[0]):
            raise _Refused(f"the row {raw!r} prints {texts[0]!r} where a count belongs")
        out[col] = int(texts[0].replace(",", ""))
    if out["female"] + out["male"] != out["total"]:
        raise _Refused(f"the row {raw!r} prints {out['female']} female and {out['male']} male "
                       f"against a total of {out['total']}")
    return out


def _parse(pdf, year: int = _YEAR) -> Dict:
    """Find the one district table in the report and read its eight rows."""
    found = []
    for pno in range(1, len(pdf.pages) + 1):
        lns = _lines(pdf.pages[pno - 1])
        for i, ln in enumerate(lns):
            m = _CAPTION.match(_norm(ln["text"]))
            if not m:
                continue
            nxt = _norm(lns[i + 1]["text"]) if i + 1 < len(lns) else ""
            if int(m.group(2)) != year or nxt != _CAPTION_2.format(year=year):
                log.info("bz_moh: caption on page %d set aside, the caption year is %s and the line "
                         "below reads %r", pno, m.group(2), nxt)
                continue
            found.append((pno, i, lns, m.group(1)))
    if len(found) != 1:
        raise _Refused(f"{len(found)} captions passed the caption gate, on pages "
                       f"{[f[0] for f in found]}, where exactly one must")
    pno, i, lns, table_id = found[0]
    caption = " / ".join(lns[j]["text"] for j in (i, i + 1))
    if table_id != "4":
        log.warning("bz_moh: the table is numbered Table %s where Table 4 was read by hand",
                    table_id)

    header: List[str] = []
    rows: Dict[Optional[str], Dict] = {}
    source_line: Optional[str] = None
    k = i + 2
    while k < len(lns):
        ln = lns[k]
        k += 1
        raw, groups = _split(ln)
        key = _norm(raw)
        if key not in _ROWS or not groups:
            if rows:
                raise _Refused(f"the line {ln['text']!r} on page {pno} sits inside the table and "
                               f"is not one of the eight expected rows")
            header.append(ln["text"])
            if len(header) > _MAX_HEADER_LINES:
                raise _Refused(f"more than {_MAX_HEADER_LINES} lines between the caption and the "
                               f"first district row on page {pno}")
            continue
        admin1 = _ROWS[key]
        if admin1 in rows:
            raise _Refused(f"the row {raw!r} appears twice")
        rows[admin1] = {"source_label": raw, "source_line_text": ln["text"],
                        **_read_row(raw, groups)}
        if admin1 == "":
            if k < len(lns) and _norm(lns[k]["text"]).startswith("source"):
                source_line = lns[k]["text"]
            break
    else:
        raise _Refused(f"no Grand Total row below the caption on page {pno}")

    missing = sorted({"": "Grand Total", None: "Unknown"}.get(a, a) for a in _ROWS.values()
                     if a not in rows)
    if missing:
        raise _Refused(f"row(s) not found: {missing}")
    if _HEADER_COLS not in {_norm(h) for h in header}:
        raise _Refused(f"no header line on page {pno} reads 'Row Labels Female Male Total', so "
                       f"the table is not the one read by hand")
    for col in _COLS:
        parts = sum(r[col] for a, r in rows.items() if a != "")
        if parts != rows[""][col]:
            raise _Refused(f"the six districts and the Unknown row sum to {parts:,} in the column "
                           f"{col}, where the Grand Total row prints {rows[''][col]:,}")

    total = {col: rows[""][col] for col in _COLS}
    if total != _TOTAL:
        log.warning("bz_moh: the Grand Total row reads %s, where the copy read on 8 October 2026 "
                    "printed %s", total, _TOTAL)
    log.info("bz_moh: Table %s on page %d, eight rows read, %d newly diagnosed nationally, %d of "
             "unknown district", table_id, pno, total["total"], rows[None]["total"])
    return {"rows": rows, "table_id": table_id, "page": pno, "caption": caption,
            "header": " / ".join(header), "source_line": source_line}


class BelizeMOHConnector(BaseConnector):
    """Belize Ministry of Health HIV Surveillance Report 2018: newly diagnosed HIV by district."""

    source_id = "bz_moh"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Belize Ministry of Health HIV Surveillance Report 2018: newly diagnosed HIV "
                   "infections by district, 2018 (to-source).")
    country = "BLZ"
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/belize_moh", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the report, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("bz_moh: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("bz_moh: downloaded the 2018 report (%.1f MB) -> %s", len(blob) / 1e6, path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("bz_moh: the report matches the copy read on 8 October 2026 (sha256 %s)",
                     digest[:12])
        else:
            log.warning("bz_moh: the report differs from the copy read on 8 October 2026 (%d "
                        "bytes, sha256 %s, expected %d bytes, %s); the table gates still run",
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
        if not start_year <= _YEAR <= end_year:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("bz_moh: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
        except Exception as exc:
            log.warning("bz_moh: the 2018 report could not be fetched (%s)", exc)
            return
        try:
            with pdfplumber.open(str(path)) as pdf:
                table = _parse(pdf)
        except _Refused as exc:
            log.warning("bz_moh: the 2018 report refused because %s", exc)
            return
        except Exception as exc:
            log.warning("bz_moh: the 2018 report failed to parse (%s)", exc)
            return
        emitted = 0
        for row in self._rows(table):
            emitted += 1
            yield row
        log.info("bz_moh: emitted %d rows", emitted)

    def _rows(self, table: Dict) -> Iterator[PanelRow]:
        nat, unknown = table["rows"][""], table["rows"][None]
        for admin1 in sorted(a for a in table["rows"] if a):
            rec = table["rows"][admin1]
            extra: Dict = {
                "edition": "HIV Surveillance Report 2018, Epidemiology Unit, Ministry of Health",
                "edition_year": _YEAR,
                "table": f"Table {table['table_id']}",
                "page": table["page"],
                "caption": table["caption"],
                "source_line": table["source_line"],
                "column_header": table["header"],
                "extraction": ("text layer, caption-anchored, cells split on the measured gap "
                               "between words"),
                "source_row": rec["source_line_text"],
                "admin1_source_label": rec["source_label"],
                "female": rec["female"],
                "male": rec["male"],
                "definition": ("newly diagnosed HIV infections in 2018 from HIV case-based "
                               "surveillance in BHIS, by district of residence"),
                "data_status": _PRELIMINARY,
                "national_total": nat["total"],
                "unknown_district": unknown["total"],
                "national_note": (f"the national Grand Total of {nat['total']} is not emitted, "
                                  "because paho_core already holds the same figure for Belize "
                                  f"2018, and the {unknown['total']} cases of unknown district "
                                  "are not emitted, so the six district rows sum to "
                                  f"{nat['total'] - unknown['total']}"),
                "integrity": ("female plus male equals the total in every row, and the six "
                              "districts and the Unknown row sum exactly to the Grand Total in "
                              "all three columns"),
                "reconcile_with": (
                    "none at district level. No other source in the panel held Belize district "
                    "notified_hiv_cases rows when this connector was built (checked 13 October "
                    "2026). Nationally paho_core reads 254 for 2018, equal to the report, with 85 "
                    "women and 169 men against 84 women and 170 men in this table, a difference "
                    "of one, cause NOT VERIFIED. Never compare with new_diagnoses (Jason's ruling "
                    "of 8 October 2026)"),
            }
            if table["source_line"] is None:
                extra["source_line_note"] = "the report prints no source line under this table"
            yield self.make_row(
                country_iso3="BLZ", country_name="Belize",
                indicator_id="notified_hiv_cases", year=_YEAR, value=rec["total"],
                unit="count", admin1=admin1,
                source_url=_URL,
                source_indicator_code=f"hiv_surveillance_report.{_YEAR}.table{table['table_id']}",
                extra=extra,
            )
