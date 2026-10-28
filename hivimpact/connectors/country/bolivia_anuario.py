"""
Bolivia, MSyD epidemiology yearbook 2016: notified HIV cases by department, 2016
(to-source, routine programme, sub-national).

Source: Bolivia's Ministry of Health and Sports (MSyD, Ministerio de Salud y Deportes) posts an
epidemiology yearbook, the Anuario Epidemiología 2016, in the Folletos Epidemiológicos category
of the file store on www.minsalud.gob.bo. The site serves the file under the name
ANUARIO_2017_EPIDEMIOLOGIA.pdf. The chapter of the national programme for STIs, HIV/AIDS and
viral hepatitis (Programa Nacional ITS/VIH/SIDA-HV) prints, on PDF page 82, Tabla N°2, "Número
de casos de VIH/SIDA acumulados por departamento, Bolivia, 1984 - 2016". The table has one row
for each of Bolivia's nine departments, a Total row and six columns: cumulative cases for 1984
to 2016 (total, with HIV, in the AIDS phase, and the AIDS share in per cent) and cases notified
in 2016 (with HIV, in the AIDS phase). The PDF is born-digital, so there is no OCR here.

The yearbook is downloaded once into `raw_dir` and read from the cached copy after that. A cached
copy whose size or sha256 differs from the copy read on 8 October 2026 is logged as a WARNING and
still parsed, because every gate below runs on the table itself.

    yearbook  table       PDF page  notified 2016 with HIV  in the AIDS phase  all cases
    2016      Tabla N°2   82        1,920                   459                2,379

WHAT THE COUNT IS
-----------------
The emitted value is the cases notified in 2016, the cases notified with HIV plus the cases
notified in the AIDS phase. The yearbook splits every notified case into the two categories
("17.871 casos de VIH/SIDA de los cuales 14.501 son casos de VIH y 3.370 en fase SIDA", page
79), so the sum counts each case once. The research check of 8 October 2026 found Tabla N°3 on
the same page splitting the same 2,379 cases of 2016 into 1,661 men and 718 women, with no case
of unknown sex (research/phase5_lac/lac_round1_notes.md, section r2v). The split into cases with
HIV and cases in the AIDS phase travels in `extra` while an AIDS-case indicator is held. Jason
ruled on 8 October 2026 that a ministry's own count of HIV cases goes under
`notified_hiv_cases` and is never merged with or compared to `new_diagnoses`.

ONE YEAR ONLY
-------------
The file store holds the yearbooks of 2015 and 2016 only. The 2015 yearbook prints its 2014
department table as an image with no text layer, and the 2016 yearbook revises the national
2014 counts, so no other department year is read. A department count for 2015 found by
subtracting the cumulative columns of the two yearbooks would carry a gap of 42 cases and the
2014 revision, so none is derived.

PARSING
-------
The table is found by CAPTION TEXT. A caption is a line reading "Tabla N°N. Número de casos de
VIH/SIDA", followed by a line reading "acumulados por departamento" and a line reading "Bolivia,
1984 - 2016". Tabla N°3 on the same page shares the first words of the caption and is set aside
because the caption line continues "por Sexo y Grupo Etario". The header lines between the title
and the first department row must hold the period line "1984 - 2016 Notificados 2016", the line
"Departamento" and the column line "Total VIH SIDA % sida VIH SIDA", and at most six header lines
are allowed.

Cells are delimited on the gap between words, as `_pdf_text.columns` does. Gaps between columns
in Tabla N°2 measured 25 points or more and gaps inside a department name 2.5 points, measured
13 October 2026, so the 10-point default sits in the empty range between the two. Every cell of
the table is one word, so a cell printed as several words refuses the yearbook.

INTEGRITY GATES
---------------
  * exactly one caption in the yearbook passes the caption gate;
  * every line from the first department row to the Total row is one of the nine departments or
    the Total row, each found exactly once, with exactly six cells;
  * in every row the cumulative total equals the cumulative cases with HIV plus the cumulative
    cases in the AIDS phase, the printed AIDS share equals the cumulative AIDS cases over the
    cumulative total to the nearest whole per cent, and the 2016 counts do not exceed the
    cumulative counts of the same category;
  * the nine departments sum exactly to the Total row in all five count columns.

Any failed gate refuses the yearbook with a WARNING naming the reason. A Total row that differs
from the figures in the table above is logged as a WARNING and still emitted, since the gates
have passed.

LABELS
------
`admin1` carries the department names with their Spanish accents (Potosí), and the yearbook's
own spelling ("Potosi" in Tabla N°2) goes into `extra.admin1_source_label`. The Total row is the
national row, admin1 "".

RECONCILIATION
--------------
No other source in the panel held Bolivian department rows of any indicator when this connector
was built (checked 13 October 2026). `paho_core` holds national Bolivian `notified_hiv_cases`
rows for 1995 to 2025 from PAHO Core Indicator 93, reported by the same ministry. The PAHO row
for 2016 reads 2,445 cases (731 women, 1,714 men) and was last modified on the PAHO dashboard on
23 July 2024, against 2,379 cases (718 women, 1,661 men) in the yearbook, a difference of 66.
The two sources stay separate rows, and the national row records the difference in
`extra.reconcile_with`.

TAGGING: source_type = routine_programme_record (the national programme's case notification,
per the table's own source line).
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

_URL = ("https://www.minsalud.gob.bo/component/jdownloads/send/9-folletos-epidemiologicos/"
        "99-anuario-epidemiologia-2016?Itemid=465")
_LOCAL = "anuario_epidemiologia_2016.pdf"
_SERVED_AS = "ANUARIO_2017_EPIDEMIOLOGIA.pdf"
_NOTES = "research/phase5_lac/lac_round1_notes.md, section r2v"

#: The yearbook read on 8 October 2026: (size, sha256 prefix), the year of the notified columns,
#: the 1-based page the table was read on by hand (provenance only) and the Total row, checked as
#: a fingerprint only.
_KNOWN = (7_192_405, "37058ec803ca")
_YEAR = 2016
_PAGE = 82
_TOTAL = {"cum_total": 17_871, "cum_hiv": 14_501, "cum_aids": 3_370, "hiv": 1_920, "aids": 459}

#: Normalised row label -> admin1, "" for the national Total row.
_ROWS: Dict[str, str] = {
    "beni": "Beni",
    "chuquisaca": "Chuquisaca",
    "cochabamba": "Cochabamba",
    "la paz": "La Paz",
    "oruro": "Oruro",
    "pando": "Pando",
    "potosi": "Potosí",
    "santa cruz": "Santa Cruz",
    "tarija": "Tarija",
    "total": "",
}

_CAPTION = re.compile(r"^tabla n (\d+) numero de casos de vih sida$")
_CAPTION_2 = "acumulados por departamento"
_TITLE = "bolivia 1984 {year}"
#: The header lines, compared with every character but letters and digits removed (the period
#: line prints "Notifi cados", split at the ligature) or normalised.
_HEADER_PERIOD = "19842016notificados{year}"
_HEADER_LABEL = "departamento"
_HEADER_COLS = "total vih sida sida vih sida"
_COLS = ("cum_total", "cum_hiv", "cum_aids", "pct_aids", "hiv", "aids")
_NUMERIC = re.compile(r"^[\d.,]+%?$")
_COUNT = re.compile(r"^(?:\d{1,3}(?:\.\d{3})+|\d+)$")
_PCT = re.compile(r"^(\d{1,3})%$")
_MAX_HEADER_LINES = 6
#: The printed share is a whole per cent, so 100 x AIDS / total may sit up to 0.5 from it.
_PCT_TOL = 0.5 + 1e-9


class _Refused(Exception):
    """A gate failed. The whole yearbook is refused, never part of it."""


def _compact(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _norm(s))


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
    """The six cells of one row, as integers, the AIDS share in whole per cent."""
    if len(groups) != len(_COLS):
        raise _Refused(f"the row {raw!r} has {len(groups)} cells where six belong")
    out: Dict[str, int] = {}
    for col, group in zip(_COLS, groups):
        texts = [w["text"] for w in group]
        if len(texts) != 1:
            raise _Refused(f"the row {raw!r} prints {' '.join(texts)!r} as one cell, where every "
                           f"cell of the table is one word")
        text = texts[0]
        if col == "pct_aids":
            m = _PCT.match(text)
            if not m:
                raise _Refused(f"the row {raw!r} prints {text!r} where a whole per cent belongs")
            out[col] = int(m.group(1))
        else:
            if not _COUNT.match(text):
                raise _Refused(f"the row {raw!r} prints {text!r} where a count belongs")
            out[col] = int(text.replace(".", ""))
    return out


def _check_row(raw: str, r: Dict[str, int]) -> None:
    if r["cum_total"] != r["cum_hiv"] + r["cum_aids"]:
        raise _Refused(f"the row {raw!r} prints a cumulative total of {r['cum_total']:,} where "
                       f"{r['cum_hiv']:,} with HIV and {r['cum_aids']:,} in the AIDS phase add to "
                       f"{r['cum_hiv'] + r['cum_aids']:,}")
    if r["cum_total"] <= 0 or abs(100.0 * r["cum_aids"] / r["cum_total"] - r["pct_aids"]) > _PCT_TOL:
        raise _Refused(f"the row {raw!r} prints an AIDS share of {r['pct_aids']}%, where "
                       f"{r['cum_aids']:,} over {r['cum_total']:,} does not round to it")
    if r["hiv"] > r["cum_hiv"] or r["aids"] > r["cum_aids"]:
        raise _Refused(f"the row {raw!r} prints more cases in {_YEAR} than in the cumulative "
                       f"columns")


def _parse(pdf, year: int = _YEAR) -> Dict:
    """Find the one department table in the yearbook and read its ten rows."""
    found = []
    for pno in range(1, len(pdf.pages) + 1):
        lns = _lines(pdf.pages[pno - 1])
        for i, ln in enumerate(lns):
            m = _CAPTION.match(_norm(ln["text"]))
            if not m:
                continue
            nxt = [_norm(lns[j]["text"]) for j in (i + 1, i + 2) if j < len(lns)]
            if nxt != [_CAPTION_2, _TITLE.format(year=year)]:
                log.info("bo_anuario: caption on page %d set aside, the two lines below read %s",
                         pno, nxt)
                continue
            found.append((pno, i, lns, m.group(1)))
    if len(found) != 1:
        raise _Refused(f"{len(found)} captions passed the caption gate, on pages "
                       f"{[f[0] for f in found]}, where exactly one must")
    pno, i, lns, table_id = found[0]
    caption = " / ".join(lns[j]["text"] for j in (i, i + 1, i + 2))
    if table_id != "2":
        log.warning("bo_anuario: the table is numbered Tabla N°%s where Tabla N°2 was read by "
                    "hand", table_id)

    header: List[str] = []
    rows: Dict[str, Dict] = {}
    source_line: Optional[str] = None
    k = i + 3
    while k < len(lns):
        ln = lns[k]
        k += 1
        raw, groups = _split(ln)
        key = _norm(raw)
        if key not in _ROWS or not groups:
            if rows:
                raise _Refused(f"the line {ln['text']!r} on page {pno} sits inside the table and "
                               f"is not one of the ten expected rows")
            header.append(ln["text"])
            if len(header) > _MAX_HEADER_LINES:
                raise _Refused(f"more than {_MAX_HEADER_LINES} lines between the caption and the "
                               f"first department row on page {pno}")
            continue
        admin1 = _ROWS[key]
        if admin1 in rows:
            raise _Refused(f"the row {raw!r} appears twice")
        cells = _read_row(raw, groups)
        _check_row(raw, cells)
        rows[admin1] = {"source_label": raw, "source_line_text": ln["text"], **cells}
        if admin1 == "":
            if k < len(lns) and _norm(lns[k]["text"]).startswith("fuente"):
                source_line = lns[k]["text"]
            break
    else:
        raise _Refused(f"no Total row below the caption on page {pno}")

    missing = sorted(a or "Total" for a in _ROWS.values() if a not in rows)
    if missing:
        raise _Refused(f"row(s) not found: {missing}")
    if _HEADER_PERIOD.format(year=year) not in {_compact(h) for h in header}:
        raise _Refused(f"no header line on page {pno} reads '1984 - 2016 Notificados {year}', so "
                       f"the notified columns are not those of {year}")
    normed = {_norm(h) for h in header}
    for want in (_HEADER_LABEL, _HEADER_COLS):
        if want not in normed:
            raise _Refused(f"no header line on page {pno} reads {want!r}, so the table is not the "
                           f"one read by hand")

    for col in ("cum_total", "cum_hiv", "cum_aids", "hiv", "aids"):
        depts = sum(r[col] for a, r in rows.items() if a)
        if depts != rows[""][col]:
            raise _Refused(f"the nine departments sum to {depts:,} in the column {col}, where the "
                           f"Total row prints {rows[''][col]:,}")

    total = {col: rows[""][col] for col in _TOTAL}
    if total != _TOTAL:
        log.warning("bo_anuario: the Total row reads %s, where the copy read on 8 October 2026 "
                    "printed %s", total, _TOTAL)
    log.info("bo_anuario: Tabla N°%s on page %d, ten rows read, %s cases notified in %d "
             "nationally", table_id, pno, f"{total['hiv'] + total['aids']:,}", year)
    return {"rows": rows, "table_id": table_id, "page": pno, "caption": caption,
            "header": " / ".join(header), "source_line": source_line}


class BoliviaAnuarioConnector(BaseConnector):
    """Bolivia MSyD epidemiology yearbook 2016: notified HIV cases by department, 2016."""

    source_id = "bo_anuario"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Bolivia MSyD epidemiology yearbook 2016 (Anuario Epidemiología): HIV cases "
                   "notified in 2016, with HIV and in the AIDS phase, by department and "
                   "nationally (to-source).")
    country = "BOL"
    timeout = 180

    def __init__(self, raw_dir: str = "data/raw/bolivia_anuario", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the yearbook, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("bo_anuario: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("bo_anuario: downloaded the 2016 yearbook (%.1f MB) -> %s", len(blob) / 1e6,
                     path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("bo_anuario: the yearbook matches the copy read on 8 October 2026 (sha256 "
                     "%s)", digest[:12])
        else:
            log.warning("bo_anuario: the yearbook differs from the copy read on 8 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s); the table gates still run",
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
            log.error("bo_anuario: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
        except Exception as exc:
            log.warning("bo_anuario: the 2016 yearbook could not be fetched (%s)", exc)
            return
        try:
            with pdfplumber.open(str(path)) as pdf:
                table = _parse(pdf)
        except _Refused as exc:
            log.warning("bo_anuario: the 2016 yearbook refused because %s", exc)
            return
        except Exception as exc:
            log.warning("bo_anuario: the 2016 yearbook failed to parse (%s)", exc)
            return
        emitted = 0
        for row in self._rows(table):
            emitted += 1
            yield row
        log.info("bo_anuario: emitted %d rows", emitted)

    def _rows(self, table: Dict) -> Iterator[PanelRow]:
        order = sorted(a for a in table["rows"] if a) + [""]
        nat = table["rows"][""]
        for admin1 in order:
            rec = table["rows"][admin1]
            extra: Dict = {
                "edition": "Anuario Epidemiología 2016",
                "edition_file": _SERVED_AS,
                "table": f"Tabla N°{table['table_id']}",
                "page": table["page"],
                "caption": table["caption"],
                "source_line": table["source_line"],
                "column_header": table["header"],
                "extraction": ("text layer, caption-anchored, cells split on the measured gap "
                               "between words"),
                "source_row": rec["source_line_text"],
                "admin1_source_label": rec["source_label"],
                "hiv_cases": rec["hiv"],
                "aids_phase_cases": rec["aids"],
                "cumulative_1984_2016": {"total": rec["cum_total"], "hiv": rec["cum_hiv"],
                                         "aids_phase": rec["cum_aids"],
                                         "aids_pct_printed": rec["pct_aids"]},
                "definition": ("HIV cases notified to the national STI/HIV/AIDS and viral "
                               "hepatitis programme in 2016, the cases notified with HIV plus the "
                               "cases notified in the AIDS phase, the two categories into which "
                               "the yearbook splits every case"),
                "aids_phase_note": ("the split into cases with HIV and cases in the AIDS phase "
                                    "stays in extra while an AIDS-case indicator is held "
                                    f"({_NOTES})"),
                "integrity": ("the nine department rows sum exactly to the Total row in all five "
                              "count columns, every cumulative total equals cases with HIV plus "
                              "cases in the AIDS phase, and every printed AIDS share rounds "
                              "correctly"),
                "other_years": ("none read. The 2015 yearbook prints the 2014 department table as "
                                "an image with no text layer, and no 2015 department count is "
                                f"derived from the cumulative columns ({_NOTES})"),
            }
            if table["source_line"] is None:
                extra["source_line_note"] = "the yearbook prints no source line under this table"
            if admin1:
                extra["reconcile_with"] = (
                    "none. No other source in the panel held Bolivian department rows of any "
                    "indicator when this connector was built (checked 13 October 2026)")
            else:
                extra["sex_split_note"] = (
                    "Tabla N°3 on the same page splits the 2,379 cases of 2016 into 1,661 men "
                    "and 718 women, with no case of unknown sex, per the research check of 8 "
                    f"October 2026 ({_NOTES}). This connector does not read Tabla N°3")
                extra["reconcile_with"] = (
                    "paho_core holds the national 2016 row from PAHO Core Indicator 93, reported "
                    "by the same ministry and last modified on the PAHO dashboard on 23 July "
                    "2024, at 2,445 cases (731 women, 1,714 men), 66 more than the "
                    f"{nat['hiv'] + nat['aids']:,} cases in the yearbook as read here. The two "
                    "rounds stay separate rows and are not merged. Never compare with "
                    "new_diagnoses (Jason's ruling of 8 October 2026)")
            yield self.make_row(
                country_iso3="BOL", country_name="Bolivia",
                indicator_id="notified_hiv_cases", year=_YEAR, value=rec["hiv"] + rec["aids"],
                unit="count", admin1=admin1,
                source_url=_URL,
                source_indicator_code=f"anuario_epidemiologia.{_YEAR}.tabla{table['table_id']}",
                extra=extra,
            )
