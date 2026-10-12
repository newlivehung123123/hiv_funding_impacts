"""
Chad, health yearbook connector: people on treatment and viral load by province in 2023, and the
national treatment initiations and PMTCT count in 2022 (to-source, parse-only, sub-national).

Source: INSEED, Chad's national statistics institute, serves the health ministry's "Annuaire des
statistiques sanitaires" through the INSEED publications catalogue, and Jason's survey run of
2 October 2026 cached ten editions in `data/raw/chad/inseed`, with the catalogue record beside the
files in `catalogue_sanitaires.json`. The cached file names carry no edition year, so every
edition's year comes from the catalogue record. The HIV tables cite "PSLSH/IST", the health
ministry's sectoral programme against HIV, viral hepatitis and sexually transmitted infections,
and the PMTCT table cites "DSIS (DHIS2)", the health information system. The PDFs are
born-digital, so there is no OCR here.

This connector only PARSES what is already cached. It makes no network request.

WHICH EDITION OWNS WHICH YEAR (RESUME.md item 48, option D)
-----------------------------------------------------------
Two editions are on the allow-list (`_EDITIONS`), keyed by the cached filename.

    edition  table        pages     emits
    2023     Tableau 306  252       on_art_count 2023, 24 rows (stock at 31/12/2023)
    2023     Tableau 307  253       viral_load_tests_performed and viral_suppression_count 2023,
                                    24 rows each
    2022     Tableau 294  217       art_initiations 2022, nine national cells by sex and age
    2022     Tableau 296  218-219   nothing, the province stock at 31/12/2022 goes into `extra`
    2022     Tableau 299  221       pmtct_arv_count 2022, one national row

The catalogue's `annee` field is the PUBLICATION year (2024 for the 2023 edition), so the edition
year is read from the catalogue title and slug, never from `annee`.

WHAT THIS CONNECTOR REFUSES TO EMIT, AND WHY
--------------------------------------------
The 2022 treatment stock, from either edition. The 2022 edition closes 2022 with 87,983 people on
ART and the 2023 edition opens 2023 at 31/12/22 with 63,703, the same people on the same day,
24,280 apart, and neither yearbook explains the restatement. Both figures go into `extra` on every
2023 stock row. Also refused: the 2023 new inclusions as `art_initiations` (the column most likely
mixes new and returning patients), TB screening in both editions, Tableau 295 of the 2022 edition,
Tableau 308 of the 2023 edition, the PMTCT tables by province, and the other eight editions.
RESUME.md item 48 gives the reasons for each.

PARSING
-------
Tables are found by COLUMN HEADER and ROW LABELS, never by table number or caption. The 2023
caption on Tableau 306 reads "Répartition des cas de VIH dépistés par province en 2023", HIV cases
detected, above a table whose headers name the treatment cohort, so a caption-keyed parser would
load people on treatment as diagnoses. Captions are kept in `extra` as a record only.

Every page of an edition is read into text lines once. A province block is a run of lines whose
row labels name Chad's provinces, ending at the TCHAD row. Page footers are dropped, so a block may
cross a page break, as Tableau 296 does between pages 218 and 219. A label that wraps onto the next
line ("LOGONE" over "OCCIDENTAL") is joined when the first part names no province on its own.

  * Tableaux 306 and 296 are identified by assigning every header word to the nearest column
    centre and requiring each column's header text exactly. The 306 header must print the stock
    "au 31/12/22" and "au 31/12/2023", which ties the table to the 2023 edition.
  * Tableau 307's header is rotated text, which the text layer returns as scattered letters, so
    Tableau 307 is identified by shape (count, count, dot decimal, count, count, dot decimal), by
    the "PSLSH/IST" Source line, by the narrative below the table and by the bound against
    Tableau 306. Tableau 332 of the same edition, a table of scorpion stings and snakebites,
    prints the same six columns with comma decimals and so never matches the shape.
  * Tableau 294 is identified by the "Hommes Femmes Total" header over a band line reading
    "< 15ans, >15ans, Total" three times. Its row labels wrap above and below the numbers, so each
    label fragment is assigned to the nearest line of numbers.
  * Tableau 299 is identified by the "Indicateurs Nombre" header over "STATUT DE MERE".

Numbers are rebuilt from word positions by `_pdf_text.number_readings`. The 2022 edition prints
thousands with a space ("87 983") and the 2023 edition prints none ("63703"). Each value must sit
nearest its own column's centre, and the row's printed arithmetic must leave exactly one reading.

INTEGRITY GATES (RESUME.md item 48)
-----------------------------------
  1. Edition identity. The catalogue title and slug must name the allow-listed year, the file size
     on disk must equal the catalogue's `taille`, and the header years must match the edition.
  2. Tables are found by header and row labels, and exactly one block must pass for each table.
  3. Exactly 23 provinces and the TCHAD row, each found once, and no other label.
  4. The 23 provinces sum exactly to the TCHAD row in every count column of Tableaux 296, 306 and
     307, with a printed dash read as zero.
  5. Tableau 306: no stock at 31/12/2023 exceeds the stock at 31/12/22 plus new inclusions plus
     transfers in.
  6. Tableau 307: the third column equals the second over the first and the sixth equals the fifth
     over the fourth, to two decimals, in every row (0/0 prints 0.00). The narrative's national TB
     and suppression proportions equal the TCHAD row. No viral load count exceeds the province's
     Tableau 306 stock at 31/12/2023.
  7. Tableau 294: the cohort identity closes in all nine columns, every row partitions by sex and
     by age, and Tableau 296's TCHAD stock equals Tableau 294's closing stock.
  8. Tableau 299: women newly started plus women on ARVs before pregnancy equal the printed total,
     and the Source line names the edition year.
  9. Tableau 296's rate equals positives over screened, which also decides between readings.

A failed gate refuses that table with a WARNING. Tableau 307 needs Tableau 306, and Tableau 294
needs Tableau 296. The 2023 stock rows are still emitted when the 2022 edition fails, with
`extra["stock_31dec2022_2022_edition"]` set to None.

LABELS
------
`admin1` carries the province names in ASCII without accents, and the document's own spelling goes
into `extra["admin1_source_label"]`. The editions print "Logone ocidental", "BARH EL GHAZAL",
"MKE", "MKO", "WADI - FIRA" and "N’djamena" with a curly apostrophe, among others. "> 15ans" in
Tableau 294 maps to `15+`, because the two printed age bands sum to every printed total.

RECONCILIATION
--------------
`reconcile.py` compares national rows only, and every national row here shares one year at most
with any other source in the panel, below `reconcile.MIN_CELLS`, so no relationship is declared
(RESUME.md item 48, decision 5). No other source held Chad province rows or Chad viral load rows
when this connector was built (checked 2 October 2026).

TAGGING: source_type = routine_programme_record (the programme's own reporting, per each table's
Source line).
"""
from __future__ import annotations

import itertools
import json
import logging
import re
import statistics
from pathlib import Path
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
from ._pdf_text import COL_GAP, is_number_word, lines as _lines, norm as _norm, number_readings

log = logging.getLogger("hivimpact")

_HOST = "https://inseed.ssn-tchad.td"
_CATALOGUE = "catalogue_sanitaires.json"

# -- the allow-list: cached filename -> edition year. Everything else about the edition (title,
# slug, size, catalogue path) is read from the catalogue record and checked by gate 1.
_EDITIONS: Dict[str, int] = {
    "publications_publication-1767697502413-53333600.pdf": 2023,
    "publications_publication-1767697651804-421090510.pdf": 2022,
}

# Normalised row label -> admin1, "" for the national row. `norm` turns the curly apostrophe in
# "N’djamena" and the dash in "WADI - FIRA" into spaces. "logone" alone is deliberately absent, so
# the wrapped "LOGONE" / "OCCIDENTAL" label is joined before the label is looked up.
_ALIASES: Dict[str, str] = {
    "barh el gazel": "Barh el Gazel", "barh el ghazal": "Barh el Gazel",
    "barh el gazal": "Barh el Gazel",
    "batha": "Batha",
    "borkou": "Borkou",
    "chari baguirmi": "Chari Baguirmi",
    "ennedi est": "Ennedi Est",
    "ennedi ouest": "Ennedi Ouest",
    "guera": "Guera",
    "hadjer lamis": "Hadjer Lamis",
    "kanem": "Kanem",
    "lac": "Lac",
    "logone occidental": "Logone Occidental", "logone ocidental": "Logone Occidental",
    "logone oriental": "Logone Oriental",
    "mandoul": "Mandoul",
    "mayo kebbi est": "Mayo Kebbi Est", "mke": "Mayo Kebbi Est",
    "mayo kebbi ouest": "Mayo Kebbi Ouest", "mko": "Mayo Kebbi Ouest",
    "moyen chari": "Moyen Chari",
    "n djamena": "N'Djamena",
    "ouaddai": "Ouaddai", "ouddai": "Ouaddai",
    "salamat": "Salamat",
    "sila": "Sila",
    "tandjile": "Tandjile",
    "tibesti": "Tibesti",
    "wadi fira": "Wadi Fira",
    "tchad": "",
}
_PROVINCES: Tuple[str, ...] = tuple(sorted({v for v in _ALIASES.values() if v}))
assert len(_PROVINCES) == 23

_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)
_DASH = re.compile(r"^[-‐–—]$")
_DOT = re.compile(r"^\d+\.\d+$")
_COMMA = re.compile(r"^\d+,\d+$")
_DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
_FOOTER = re.compile(r"\bpage \d+ sur \d+$")
_TABLE_ID = re.compile(r"^tableau (\d+)\b")
_YEAR_AT_END = re.compile(r"(\d{4})\s*$")

#: Tableau 307 proportions are printed to two decimals. The tolerance is half the last printed
#: digit, plus a hair for float error.
_RATIO_TOL = 0.005 + 1e-9


class _Refused(Exception):
    """A gate failed. The table is refused, never part of the table."""


# -- reading the text layer ---------------------------------------------------------------------

def _scan(pdf) -> List[List[Dict]]:
    """Every page's text lines, footers removed, so a table may run on across a page break."""
    pages = []
    for page in pdf.pages:
        pages.append([ln for ln in _lines(page) if not _FOOTER.search(_norm(ln["text"]))])
    return pages


def _split(words: Sequence[Dict]) -> Tuple[str, List[Dict], List[Dict]]:
    """Classify a line as ("row", label, cells), ("label", label, []) or ("other", [], []).

    The label is the leading words that carry a letter, plus a lone dash standing between two
    such words ("WADI - FIRA"). The cells are everything after the label, and every one of them
    must be a whole-number word, a lone dash or a decimal.
    """
    k = 0
    while k < len(words):
        t = words[k]["text"]
        if _LETTER.search(t):
            k += 1
        elif (_DASH.match(t) and k > 0 and k + 1 < len(words)
              and _LETTER.search(words[k + 1]["text"])):
            k += 1
        else:
            break
    label, cells = list(words[:k]), list(words[k:])
    if not label:
        return "other", [], []
    if not cells:
        return "label", label, []
    if all(is_number_word(w["text"]) or _DOT.match(w["text"]) or _COMMA.match(w["text"])
           for w in cells):
        return "row", label, cells
    return "other", [], []


def _text(words: Sequence[Dict]) -> str:
    return " ".join(w["text"] for w in words)


def _centre(words: Sequence[Dict]) -> float:
    return (words[0]["x0"] + words[-1]["x1"]) / 2.0


def _blocks(pages: List[List[Dict]]) -> List[Dict]:
    """Every run of province rows that ends at a TCHAD row, anywhere in the edition."""
    out: List[Dict] = []
    cur: Optional[Dict] = None
    for pno, lns in enumerate(pages, 1):
        for idx, ln in enumerate(lns):
            kind, label, cells = _split(ln["words"])
            if kind == "row":
                raw = _text(label)
                admin1 = _ALIASES.get(_norm(raw))
                if cur is None:
                    if not admin1:
                        continue
                    cur = {"rows": [], "page": pno, "idx": idx}
                cur["rows"].append({"raw": raw, "admin1": admin1, "label": label,
                                    "cells": cells, "page": pno, "idx": idx})
            elif kind == "label" and cur is not None and cur["rows"][-1]["admin1"] is None:
                last = cur["rows"][-1]
                raw = f"{last['raw']} {_text(label)}"
                admin1 = _ALIASES.get(_norm(raw))
                if admin1 is None:
                    cur = None
                    continue
                last.update(raw=raw, admin1=admin1)
            else:
                cur = None
                continue
            if cur is not None and cur["rows"][-1]["admin1"] == "":
                out.append(cur)
                cur = None
    return out


def _above(pages: List[List[Dict]], pno: int, idx: int) -> Tuple[Optional[str], List[Dict]]:
    """The caption and header lines above a line, up to the nearest "Tableau" line on the page."""
    lns = pages[pno - 1]
    hdr: List[Dict] = []
    for j in range(idx - 1, -1, -1):
        if _norm(lns[j]["text"]).startswith("tableau"):
            return lns[j]["text"], hdr[::-1]
        hdr.append(lns[j])
    return None, hdr[::-1]


def _table_id(caption: Optional[str]) -> str:
    m = _TABLE_ID.match(_norm(caption or ""))
    return m.group(1) if m else "unnumbered"


def _source_after(pages: List[List[Dict]], blk: Dict) -> Tuple[Optional[str], List[Dict]]:
    """The line straight after the TCHAD row when the line is a Source line, and the lines after."""
    last = blk["rows"][-1]
    rest = pages[last["page"] - 1][last["idx"] + 1:]
    if rest and _norm(rest[0]["text"]).startswith("source"):
        return rest[0]["text"], rest[1:]
    return None, rest


# -- reading the cells of a province block ------------------------------------------------------
#
# A reading is a list of items (kind, value, centre, printed), kind "n" for a whole number (a dash
# reads as 0), "d" for a dot decimal and "c" for a comma decimal.

def _run_readings(ws: List[Dict]) -> List[List[Tuple]]:
    """Every reading of a run of number words, with each value's word group recovered."""
    out = []
    for values, dashes in number_readings(ws):
        items, pos = [], 0
        for i, v in enumerate(values):
            if i in dashes:
                grp = [ws[pos]]
                pos += 1
            else:
                grp, s = [], ""
                while s != str(v):
                    if pos >= len(ws) or len(s) >= len(str(v)):
                        raise ValueError(f"cannot place {v} among {_text(ws)!r}")
                    s += ws[pos]["text"]
                    grp.append(ws[pos])
                    pos += 1
            items.append(("n", v, _centre(grp), _text(grp)))
        out.append(items)
    return out


def _readings(cells: List[Dict]) -> List[List[Tuple]]:
    """Every reading of a row's cells: number-word runs expanded, decimals taken as printed."""
    options: List[List[List[Tuple]]] = []
    run: List[Dict] = []
    for w in cells + [None]:
        if w is not None and is_number_word(w["text"]):
            run.append(w)
            continue
        if run:
            options.append(_run_readings(run))
            run = []
        if w is not None:
            kind = "d" if _DOT.match(w["text"]) else "c"
            options.append([[(kind, float(w["text"].replace(",", ".")), _centre([w]),
                              w["text"])]])
    return [[item for part in combo for item in part] for combo in itertools.product(*options)]


def _shape(blk: Dict, kinds: Sequence[str], optional_last: bool = False) -> Optional[Dict]:
    """The block's readings of the expected kinds and the column centres, or None.

    None means the block is not this table's shape: some row has no reading of the expected
    kinds, or some column has no row read unambiguously. Column centres are the median centre
    of each column over the rows with exactly one reading of the expected kinds.
    """
    allowed = {tuple(kinds)}
    if optional_last:
        allowed.add(tuple(kinds[:-1]))
    per_row = []
    for r in blk["rows"]:
        try:
            rs = [rd for rd in _readings(r["cells"]) if tuple(i[0] for i in rd) in allowed]
        except ValueError:
            return None
        if not rs:
            return None
        per_row.append(rs)
    cols: List[List[float]] = [[] for _ in kinds]
    for rs in per_row:
        if len(rs) == 1:
            for j, item in enumerate(rs[0]):
                cols[j].append(item[2])
    if any(not c for c in cols):
        return None
    label_centre = statistics.median(_centre(r["label"]) for r in blk["rows"])
    return {"per_row": per_row, "centres": [statistics.median(c) for c in cols],
            "label_centre": label_centre}


def _choose(blk: Dict, shape: Dict, check: Optional[Callable[[List[float]], bool]],
            what: str) -> Dict[str, List[Tuple]]:
    """One reading per row, placed under the right columns and passing the row's arithmetic."""
    centres = shape["centres"]
    out: Dict[str, List[Tuple]] = {}
    for r, rs in zip(blk["rows"], shape["per_row"]):
        placed = [rd for rd in rs
                  if all(min(range(len(centres)), key=lambda j: abs(it[2] - centres[j])) == i
                         for i, it in enumerate(rd))]
        ok = [rd for rd in placed if check is None or check([it[1] for it in rd])]
        if len(ok) != 1:
            raise _Refused(f"{what}: the row {r['raw']!r} has {len(rs)} reading(s) of the "
                           f"expected shape, {len(placed)} placed under the right columns and "
                           f"{len(ok)} satisfying the row's printed arithmetic, where exactly "
                           f"one must remain")
        out[r["raw"]] = ok[0]
    return out


def _header_texts(hdr: List[Dict], shape: Dict) -> List[str]:
    """Each column's header as printed: the label column first, then one per data column."""
    allc = [shape["label_centre"]] + shape["centres"]
    cols: List[List[str]] = [[] for _ in allc]
    for ln in hdr:
        for w in ln["words"]:
            c = (w["x0"] + w["x1"]) / 2.0
            cols[min(range(len(allc)), key=lambda k: abs(c - allc[k]))].append(w["text"])
    return [" ".join(c) for c in cols]


def _provinces(blk: Dict, what: str) -> None:
    """Gate 3. Exactly 23 provinces and TCHAD, each once, and no other label."""
    seen = set()
    for r in blk["rows"]:
        if r["admin1"] is None:
            raise _Refused(f"{what}: the row label {r['raw']!r} names no Chad province")
        if r["admin1"] in seen:
            raise _Refused(f"{what}: {r['admin1'] or 'TCHAD'} appears twice")
        seen.add(r["admin1"])
    missing = sorted(set(_PROVINCES) - seen)
    if missing:
        raise _Refused(f"{what}: province(s) not found: {missing}")


def _values(blk: Dict, chosen: Dict[str, List[Tuple]]) -> Dict[str, Dict]:
    """admin1 -> {"raw", "values", "printed"} for a block whose provinces passed gate 3."""
    return {r["admin1"]: {"raw": r["raw"], "values": [it[1] for it in chosen[r["raw"]]],
                          "printed": [it[3] for it in chosen[r["raw"]]]}
            for r in blk["rows"]}


def _sums(rows: Dict[str, Dict], cols: Iterable[int], what: str) -> None:
    """Gate 4. The 23 provinces sum exactly to the TCHAD row in each count column."""
    for j in cols:
        total = sum(r["values"][j] for a, r in rows.items() if a)
        if total != rows[""]["values"][j]:
            raise _Refused(f"{what}: the provinces sum to {total:,} in column {j + 1}, where the "
                           f"TCHAD row prints {rows['']['values'][j]:,}")


def _source_year_ok(line: Optional[str], year: int) -> bool:
    m = _YEAR_AT_END.search(_norm(line or ""))
    return bool(m) and int(m.group(1)) == year


# -- the 2023 edition ---------------------------------------------------------------------------

def _t306(pages: List[List[Dict]], blocks: List[Dict], year: int) -> Dict:
    """Tableau 306, the treatment cohort by province, identified by the four column headers."""
    yy = f"{(year - 1) % 100:02d}"
    want = [f"pvv sous tarv au 31 12 {yy}", "nouvelles inclusions sous tarv",
            "transfert entrant", f"pvv sous tarv au 31 12 {year}"]
    found = []
    for blk in blocks:
        shape = _shape(blk, ["n"] * 4)
        if shape is None:
            continue
        caption, hdr = _above(pages, blk["page"], blk["idx"])
        texts = _header_texts(hdr, shape)
        if [_norm(t) for t in texts[1:]] == want:
            found.append((blk, shape, caption, texts))
    if len(found) != 1:
        raise _Refused(f"the treatment cohort table: {len(found)} province blocks carry the "
                       f"headers {want}, on pages {[f[0]['page'] for f in found]}, where exactly "
                       f"one must")
    blk, shape, caption, texts = found[0]
    what = f"Tableau {_table_id(caption)} (page {blk['page']})"
    _provinces(blk, what)
    rows = _values(blk, _choose(blk, shape, None, what))
    _sums(rows, range(4), what)
    for a, r in rows.items():
        a0, b, c, d = r["values"]
        if d > a0 + b + c:
            raise _Refused(f"{what}: {r['raw']!r} prints {d:,} on ART at 31/12/{year}, more than "
                           f"{a0:,} + {b:,} + {c:,}")
    source_line, _ = _source_after(pages, blk)
    if source_line is None or "pslsh ist" not in _norm(source_line) \
            or not _source_year_ok(source_line, year):
        raise _Refused(f"{what}: the line below the TCHAD row is {source_line!r}, not a "
                       f"PSLSH/IST Source line for {year}")
    log.info("td_annuaire: %d edition, %s identified by its headers, 23 provinces and TCHAD read, "
             "every column sums and every row bound holds", year, what)
    return {"rows": rows, "page": blk["page"], "caption": caption, "table_id": _table_id(caption),
            "headers": texts[1:], "label_header": texts[0], "source_line": source_line}


def _t307(pages: List[List[Dict]], blocks: List[Dict], year: int, t306: Dict) -> Dict:
    """Tableau 307, TB screening and viral load by province, identified by shape and checks."""
    def ratios(v: List[float]) -> bool:
        for num, den, pct in ((v[1], v[0], v[2]), (v[4], v[3], v[5])):
            want = 0.0 if den == 0 else num / den * 100.0
            if den == 0 and num != 0:
                return False
            if abs(pct - want) > _RATIO_TOL:
                return False
        return True

    passed, reasons = [], []
    for blk in blocks:
        shape = _shape(blk, ["n", "n", "d", "n", "n", "d"])
        if shape is None:
            continue
        caption, _ = _above(pages, blk["page"], blk["idx"])
        what = f"Tableau {_table_id(caption)} (page {blk['page']})"
        try:
            _provinces(blk, what)
            rows = _values(blk, _choose(blk, shape, ratios, what))
            _sums(rows, (0, 1, 3, 4), what)
            source_line, after = _source_after(pages, blk)
            if source_line is None or "pslsh ist" not in _norm(source_line) \
                    or not _source_year_ok(source_line, year):
                raise _Refused(f"{what}: the line below the TCHAD row is {source_line!r}, not a "
                               f"PSLSH/IST Source line for {year}")
            narrative = _norm(" ".join(ln["text"] for ln in after))
            nat = rows[""]["printed"]
            for phrase in (f"tuberculose est de {nat[2]}", f"supprimee est de {nat[5]}"):
                if _norm(phrase.replace(".", ",")) not in narrative:
                    raise _Refused(f"{what}: the narrative below the table does not read "
                                   f"{phrase.replace('.', ',')!r}")
            for a, r in rows.items():
                stock = t306["rows"][a]["values"][3]
                if r["values"][3] > stock:
                    raise _Refused(f"{what}: {r['raw']!r} prints {r['values'][3]:,} viral load "
                                   f"tests against {stock:,} on ART at 31/12/{year}")
            passed.append({"rows": rows, "page": blk["page"], "caption": caption,
                           "table_id": _table_id(caption), "source_line": source_line})
        except _Refused as exc:
            reasons.append(str(exc))
    for r in reasons:
        log.info("td_annuaire: %d edition, a block of the viral load shape was set aside: %s",
                 year, r)
    if len(passed) != 1:
        raise _Refused(f"the viral load table: {len(passed)} province blocks passed the shape, "
                       f"Source, narrative, ratio and Tableau 306 checks, where exactly one must")
    t = passed[0]
    log.info("td_annuaire: %d edition, Tableau %s (page %d) identified by shape, Source line, "
             "narrative and ratios, 23 provinces and TCHAD read, every count column sums",
             year, t["table_id"], t["page"])
    return t


# -- the 2022 edition ---------------------------------------------------------------------------

def _t296(pages: List[List[Dict]], blocks: List[Dict], year: int) -> Dict:
    """Tableau 296, people on ART and TB screening by province, identified by its headers."""
    want = ["pvv sous tarv dans la periode", "pvv chez qui la tb a ete recherchee",
            "pvv decalres positifs a la tb", "taux d incidence de la tb chez les patients vih"]

    def rate(v: List[float]) -> bool:
        if len(v) == 3:
            return v[1] == 0 and v[2] == 0
        return v[1] > 0 and abs(v[3] - v[2] / v[1] * 100.0) <= _RATIO_TOL

    found = []
    for blk in blocks:
        shape = _shape(blk, ["n", "n", "n", "c"], optional_last=True)
        if shape is None:
            continue
        caption, hdr = _above(pages, blk["page"], blk["idx"])
        texts = _header_texts(hdr, shape)
        if [_norm(t) for t in texts[1:]] == want:
            found.append((blk, shape, caption, texts))
    if len(found) != 1:
        raise _Refused(f"the province ART and TB table: {len(found)} province blocks carry the "
                       f"headers {want}, where exactly one must")
    blk, shape, caption, texts = found[0]
    pages_used = sorted({r["page"] for r in blk["rows"]})
    what = f"Tableau {_table_id(caption)} (pages {pages_used})"
    _provinces(blk, what)
    rows = _values(blk, _choose(blk, shape, rate, what))
    _sums(rows, range(3), what)
    source_line, _ = _source_after(pages, blk)
    log.info("td_annuaire: %d edition, %s identified by its headers, 23 provinces and TCHAD read, "
             "every count column sums and every rate equals positives over screened",
             year, what)
    return {"rows": rows, "pages": pages_used, "caption": caption, "table_id": _table_id(caption),
            "headers": texts[1:], "source_line": source_line}


_BAND = ["<15ans", ">15ans", "total"] * 3
_SEXES = (("hommes", "male"), ("femmes", "female"), ("total", "all"))
_AGES = ("0-14", "15+", "all")
_NC_ROW = 1


def _t294_labels(year: int) -> List[str]:
    return [f"nombre des pvv au 31 12 {year - 1}", "nombre de nc sous arv", "transfert entrant",
            "pvv perdues de vues retrouvees", "transfert sortant", "nombre de pvv decedees",
            "nombre pvv perdue de vue", f"nombre pvv sous arv au 31 12 {year}"]


def _groups(words: Sequence[Dict]) -> List[List[Dict]]:
    gs: List[List[Dict]] = []
    for w in words:
        if gs and (w["x0"] - gs[-1][-1]["x1"]) < COL_GAP:
            gs[-1].append(w)
        else:
            gs.append([w])
    return gs


def _t294(pages: List[List[Dict]], year: int) -> Dict:
    """Tableau 294, the national treatment cohort by sex and age, from 31/12/(year-1) to year."""
    found = []
    for pno, lns in enumerate(pages, 1):
        for i, ln in enumerate(lns):
            if _norm(ln["text"]) != "hommes femmes total":
                continue
            for j in range(i + 1, min(i + 4, len(lns))):
                gs = _groups(lns[j]["words"])
                if ["".join(w["text"] for w in g).lower() for g in gs] == _BAND:
                    found.append((pno, i, j, gs))
                    break
            else:
                log.info("td_annuaire: %d edition, a 'Hommes Femmes Total' line on page %d set "
                         "aside, no age band line below it", year, pno)
    if len(found) != 1:
        raise _Refused(f"the cohort table: {len(found)} 'Hommes Femmes Total' headers sit over an "
                       f"age band line, where exactly one must")
    pno, i, j, band = found[0]
    lns = pages[pno - 1]
    caption, _ = _above(pages, pno, i)
    what = f"Tableau {_table_id(caption)} (page {pno})"
    for k, w in enumerate(lns[i]["words"]):
        lo, hi = band[3 * k][0]["x0"], band[3 * k + 2][-1]["x1"]
        if not lo <= _centre([w]) <= hi:
            raise _Refused(f"{what}: the sex header {w['text']!r} does not sit over its three "
                           f"age bands")
    band_centres = [_centre(g) for g in band]

    data: List[Dict] = []
    frags: List[Tuple[float, str]] = []
    end_line = None
    for ln in lns[j + 1:]:
        ws = ln["words"]
        k = len(ws)
        while k > 0 and is_number_word(ws[k - 1]["text"]):
            k -= 1
        prefix, nums = ws[:k], ws[k:]
        if len(nums) >= 9 and all(_LETTER.search(w["text"]) for w in prefix) \
                and not any(is_number_word(w["text"]) for w in prefix):
            data.append({"mid": ln["mid"], "prefix": _text(prefix), "nums": nums})
        elif not nums and all(_LETTER.search(w["text"]) or _DATE.match(w["text"]) for w in ws):
            frags.append((ln["mid"], ln["text"]))
        else:
            end_line = ln["text"]
            break
    if len(data) != 8:
        raise _Refused(f"{what}: {len(data)} lines of nine numbers below the band header, where "
                       f"eight must be (the table ends at {end_line!r})")
    pieces: List[List[Tuple[float, str]]] = [[(d["mid"], d["prefix"])] if d["prefix"] else []
                                             for d in data]
    for mid, text in frags:
        dist = sorted((abs(mid - d["mid"]), n) for n, d in enumerate(data))
        if abs(dist[0][0] - dist[1][0]) < 0.5:
            raise _Refused(f"{what}: the label fragment {text!r} sits midway between two rows")
        pieces[dist[0][1]].append((mid, text))
    labels = [" ".join(t for _, t in sorted(p)) for p in pieces]
    want = _t294_labels(year)
    if [_norm(lb) for lb in labels] != want:
        raise _Refused(f"{what}: the row labels read {[_norm(lb) for lb in labels]}, where "
                       f"{want} must")

    def partitions(v: Sequence[int]) -> bool:
        return all(v[3 * s] + v[3 * s + 1] == v[3 * s + 2] for s in range(3)) and \
            all(v[a] + v[a + 3] == v[a + 6] for a in range(3))

    rows: List[List[int]] = []
    for d, label in zip(data, labels):
        rs = [rd for rd in _run_readings(d["nums"]) if len(rd) == 9]
        placed = [rd for rd in rs
                  if all(min(range(9), key=lambda c: abs(it[2] - band_centres[c])) == n
                         for n, it in enumerate(rd))]
        ok = [rd for rd in placed if partitions([it[1] for it in rd])
              and not any(_DASH.match(it[3]) for it in rd)]
        if len(ok) != 1:
            raise _Refused(f"{what}: the row {label!r} has {len(rs)} reading(s) of nine numbers, "
                           f"{len(placed)} placed under the age bands and {len(ok)} partitioning "
                           f"by sex and by age, where exactly one must remain")
        rows.append([it[1] for it in ok[0]])
    start, nc, tin, back, tout, dead, ltfu, end = rows
    for c in range(9):
        if start[c] + nc[c] + tin[c] + back[c] - tout[c] - dead[c] - ltfu[c] != end[c]:
            raise _Refused(f"{what}: the cohort identity fails in column {c + 1}")
    sexes = [w["text"] for w in lns[i]["words"]]
    if [_norm(s) for s in sexes] != [s for s, _ in _SEXES]:
        raise _Refused(f"{what}: the sex header reads {sexes}")
    log.info("td_annuaire: %d edition, %s identified by its sex and age header, eight rows read, "
             "the cohort identity closes and every row partitions by sex and by age", year, what)
    return {"rows": rows, "labels": labels, "page": pno, "caption": caption,
            "table_id": _table_id(caption), "sex_labels": sexes,
            "age_labels": [_text(g) for g in band[:3]]}


_T299_KEYS = ("f e vih nouvellement mise sous arv", "f e sous arv avant la grossesse",
              "total vih mise sous arv")


def _t299(pages: List[List[Dict]], year: int) -> Dict:
    """Tableau 299, the national PMTCT cascade, identified by its header and mother section."""
    found = [(pno, i) for pno, lns in enumerate(pages, 1) for i in range(len(lns) - 1)
             if _norm(lns[i]["text"]) == "indicateurs nombre"
             and _norm(lns[i + 1]["text"]) == "statut de mere"]
    if len(found) != 1:
        raise _Refused(f"the PMTCT table: {len(found)} 'Indicateurs Nombre' headers sit over "
                       f"'STATUT DE MERE', where exactly one must")
    pno, i = found[0]
    lns = pages[pno - 1]
    caption, _ = _above(pages, pno, i)
    what = f"Tableau {_table_id(caption)} (page {pno})"

    def split(ln: Dict) -> Tuple[List[Dict], List[Dict]]:
        ws = ln["words"]
        k = len(ws)
        while k > 0 and is_number_word(ws[k - 1]["text"]):
            k -= 1
        return ws[:k], ws[k:]

    vals: Dict[str, Tuple[str, int]] = {}
    child = None
    for j in range(i + 2, len(lns)):
        if _norm(lns[j]["text"]) == "statut de l enfant":
            child = j
            break
        label, nums = split(lns[j])
        if not label or not nums:
            raise _Refused(f"{what}: the line {lns[j]['text']!r} in the mother section is not a "
                           f"label followed by a count")
        rds = [v for v, d in number_readings(nums) if len(v) == 1 and not d]
        if len(rds) != 1:
            raise _Refused(f"{what}: the row {_text(label)!r} does not read as one count")
        key = _norm(_text(label))
        if key in vals:
            raise _Refused(f"{what}: the row {_text(label)!r} appears twice")
        vals[key] = (_text(label), rds[0][0])
    if child is None:
        raise _Refused(f"{what}: no 'STATUT DE L'ENFANT' line closes the mother section")
    source_line = None
    for ln in lns[child + 1:]:
        if _norm(ln["text"]).startswith("source"):
            source_line = ln["text"]
            break
        label, nums = split(ln)
        if not label or not nums:
            break
    if source_line is None or not _source_year_ok(source_line, year):
        raise _Refused(f"{what}: no Source line naming {year} closes the table")
    missing = [k for k in _T299_KEYS if k not in vals]
    if missing:
        raise _Refused(f"{what}: row(s) not found: {missing}")
    new, before, total = (vals[k][1] for k in _T299_KEYS)
    if new + before != total:
        raise _Refused(f"{what}: {new:,} newly started plus {before:,} on ARVs before pregnancy "
                       f"is {new + before:,}, where the total prints {total:,}")
    log.info("td_annuaire: %d edition, %s identified by its header, %d + %d = %d", year, what,
             new, before, total)
    return {"vals": vals, "page": pno, "caption": caption, "table_id": _table_id(caption),
            "source_line": source_line}


# -- the connector ------------------------------------------------------------------------------

class ChadAnnuaireConnector(BaseConnector):
    """Chad health yearbook: ART and viral load by province in 2023, initiations and PMTCT in 2022.

    Parse-only by design: the survey cached the yearbooks and the catalogue record, and this
    connector reads what is already in `raw_dir`.
    """

    source_id = "td_annuaire"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Chad health statistics yearbook (Annuaire des statistiques sanitaires, via "
                   "INSEED): people on ART, viral load tests and viral suppression by province in "
                   "2023, and national ART initiations by sex and age and PMTCT ARVs in 2022 "
                   "(to-source, parse-only).")
    country = "TCD"
    country_name = "Chad"

    def __init__(self, raw_dir: str = "data/raw/chad/inseed", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _edition(self, catalogue: List[Dict], name: str, year: int) -> Dict:
        """Gate 1 on the catalogue record. Returns the record, or raises _Refused."""
        recs = [r for r in catalogue if r.get("local_name") == name]
        if len(recs) != 1:
            raise _Refused(f"{len(recs)} catalogue records name {name}, where exactly one must")
        rec = recs[0]
        t = _YEAR_AT_END.search(str(rec.get("titre", "")))
        s = re.search(r"-(\d{4})$", str(rec.get("slug", "")))
        if not t or not s or int(t.group(1)) != year or int(s.group(1)) != year:
            raise _Refused(f"the catalogue title {rec.get('titre')!r} and slug "
                           f"{rec.get('slug')!r} do not both name {year}")
        size = (self.raw_dir / name).stat().st_size
        if size != int(rec.get("taille", -1)):
            raise _Refused(f"the file holds {size:,} bytes, where the catalogue gives "
                           f"{rec.get('taille')}")
        return rec

    def _tables(self, pdfplumber, name: str, year: int,
                parsers: Dict[str, Callable]) -> Optional[Dict[str, Optional[Dict]]]:
        """Read one edition and run each table parser, logging every refusal."""
        path = self.raw_dir / name
        try:
            with pdfplumber.open(str(path)) as pdf:
                pages = _scan(pdf)
        except Exception as exc:
            log.warning("td_annuaire: %s, the %d edition, failed to open (%s)", name, year, exc)
            return None
        blocks = _blocks(pages)
        log.info("td_annuaire: %d edition, %d pages read, %d province blocks ending at TCHAD",
                 year, len(pages), len(blocks))
        out: Dict[str, Optional[Dict]] = {}
        for key, fn in parsers.items():
            try:
                out[key] = fn(pages, blocks, out)
            except _Refused as exc:
                log.warning("td_annuaire: %d edition, %s refused because %s", year, key, exc)
                out[key] = None
            except Exception as exc:
                log.warning("td_annuaire: %d edition, %s failed to parse (%s)", year, key, exc)
                out[key] = None
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
        want23 = start_year <= 2023 <= end_year
        want22 = start_year <= 2022 <= end_year
        if not (want22 or want23):
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("td_annuaire: pdfplumber not installed (pip install pdfplumber)")
            return
        if not self.raw_dir.exists():
            log.warning("td_annuaire: %s does not exist; the Chad yearbooks are not cached",
                        self.raw_dir)
            return
        cat_path = self.raw_dir / _CATALOGUE
        try:
            catalogue = json.loads(cat_path.read_text(encoding="utf-8"))
        except Exception as exc:
            log.warning("td_annuaire: %s could not be read (%s); no edition can be identified, "
                        "nothing emitted", cat_path, exc)
            return

        others = {p.name for p in self.raw_dir.glob("*.pdf")} - set(_EDITIONS)
        if others:
            log.info("td_annuaire: %d other PDF(s) in %s are not on the edition allow-list and "
                     "are not read", len(others), self.raw_dir)

        recs: Dict[int, Tuple[str, Dict]] = {}
        for name, year in _EDITIONS.items():
            if not (self.raw_dir / name).exists():
                log.warning("td_annuaire: %s, the %d edition, is not in %s", name, year,
                            self.raw_dir)
                continue
            try:
                recs[year] = (name, self._edition(catalogue, name, year))
            except _Refused as exc:
                log.warning("td_annuaire: %s, the %d edition, refused because %s", name, year,
                            exc)

        t22: Dict[str, Optional[Dict]] = {"t296": None, "t294": None, "t299": None}
        if 2022 in recs:
            def p294(pages, blocks, done):
                if done.get("t296") is None:
                    raise _Refused("Tableau 296 was not read, and Tableau 294 is checked against "
                                   "Tableau 296")
                t = _t294(pages, 2022)
                stock = done["t296"]["rows"][""]["values"][0]
                if t["rows"][-1][8] != stock:
                    raise _Refused(f"the cohort closes at {t['rows'][-1][8]:,}, where Tableau "
                                   f"{done['t296']['table_id']} prints {stock:,} on ART")
                return t
            got = self._tables(pdfplumber, recs[2022][0], 2022, {
                "t296": lambda pages, blocks, done: _t296(pages, blocks, 2022),
                "t294": p294,
                "t299": lambda pages, blocks, done: _t299(pages, 2022),
            })
            if got is not None:
                t22.update(got)

        t23: Dict[str, Optional[Dict]] = {"t306": None, "t307": None}
        if want23 and 2023 in recs:
            def p307(pages, blocks, done):
                if done.get("t306") is None:
                    raise _Refused("Tableau 306 was not read, and Tableau 307 is checked against "
                                   "Tableau 306")
                return _t307(pages, blocks, 2023, done["t306"])
            got = self._tables(pdfplumber, recs[2023][0], 2023, {
                "t306": lambda pages, blocks, done: _t306(pages, blocks, 2023),
                "t307": p307,
            })
            if got is not None:
                t23.update(got)

        emitted = 0
        order = list(_PROVINCES) + [""]
        if want23 and t23["t306"] is not None:
            name, rec = recs[2023]
            base = self._base(name, 2023, rec)
            t306, t296, t307 = t23["t306"], t22["t296"], t23["t307"]
            for admin1 in order:
                r = t306["rows"][admin1]
                a0, b, c, d = r["values"]
                old = t296["rows"][admin1]["values"][0] if t296 is not None else None
                extra = dict(base, **{
                    "table": f"Tableau {t306['table_id']}", "page": t306["page"],
                    "caption": t306["caption"], "column_header": t306["headers"][3],
                    "source_line": t306["source_line"],
                    "extraction": ("text layer, identified by the four column headers and the "
                                   "province labels; numbers rebuilt from word positions"),
                    "admin1_source_label": r["raw"],
                    "integrity": ("the 23 provinces sum exactly to the TCHAD row in all four "
                                  "columns, and no row's stock at 31/12/2023 exceeds its stock at "
                                  "31/12/22 plus new inclusions plus transfers in"),
                    "stock_31dec2022_2023_edition": a0,
                    "stock_31dec2022_2022_edition": old,
                    "new_inclusions_2023": b,
                    "transfers_in_2023": c,
                    "caption_note": ("the caption names HIV cases detected by province, while the "
                                     "column headers name the treatment cohort, so the table is "
                                     "identified by its headers and the caption is kept as a "
                                     "record only"),
                    "restatement_note": ("the 2022 edition (Tableau 296) and the 2023 edition "
                                         "(this table) print different stocks for 31/12/2022, and "
                                         "neither yearbook explains the restatement, so no 2022 "
                                         "stock is emitted (RESUME.md item 48, option D)"),
                    "reconcile_with": self._reconcile_note(admin1, "on_art_count"),
                })
                if t296 is None:
                    extra["stock_31dec2022_2022_edition_note"] = (
                        "the 2022 edition's Tableau 296 was not read, see the run log")
                else:
                    extra["stock_31dec2022_2022_edition_table"] = (
                        f"Tableau {t296['table_id']}, pages {t296['pages']}, column "
                        f"{t296['headers'][0]!r}")
                yield self._row(rec, "on_art_count", 2023, d, admin1,
                                f"annuaire.2023.tableau{t306['table_id']}.col4", extra)
                emitted += 1
            if t307 is not None:
                for ind, col in (("viral_load_tests_performed", 3), ("viral_suppression_count", 4)):
                    for admin1 in order:
                        r = t307["rows"][admin1]
                        extra = dict(base, **{
                            "table": f"Tableau {t307['table_id']}", "page": t307["page"],
                            "caption": t307["caption"],
                            "column_header": ("rotated in the PDF and not read as text; column "
                                              f"{col + 1} of six, fixed by the printed ratio "
                                              "checks and the narrative below the table"),
                            "source_line": t307["source_line"],
                            "extraction": ("text layer, identified by shape (count, count, dot "
                                           "decimal, count, count, dot decimal), the PSLSH/IST "
                                           "Source line, the narrative and the bound against "
                                           "Tableau 306"),
                            "admin1_source_label": r["raw"],
                            "integrity": ("the 23 provinces sum exactly to the TCHAD row in the "
                                          "four count columns, every printed proportion equals "
                                          "its counts to two decimals, the narrative's national "
                                          "TB and suppression proportions equal the TCHAD row, "
                                          "and no viral load count exceeds the province's "
                                          "Tableau 306 stock at 31/12/2023"),
                            "viral_load_tested_2023": r["values"][3],
                            "viral_load_suppressed_2023": r["values"][4],
                            "suppressed_share_as_printed": r["printed"][5],
                            "reconcile_with": self._reconcile_note(admin1, ind),
                        })
                        if ind == "viral_suppression_count":
                            extra["suppression_threshold"] = "not printed"
                        yield self._row(rec, ind, 2023, r["values"][col], admin1,
                                        f"annuaire.2023.tableau{t307['table_id']}.col{col + 1}",
                                        extra)
                        emitted += 1

        if want22 and 2022 in recs:
            name, rec = recs[2022]
            base = self._base(name, 2022, rec)
            t294, t299 = t22["t294"], t22["t299"]
            if t294 is not None:
                nc = t294["rows"][_NC_ROW]
                for s, (_, sex) in enumerate(_SEXES):
                    for g, age in enumerate(_AGES):
                        extra = dict(base, **{
                            "table": f"Tableau {t294['table_id']}", "page": t294["page"],
                            "caption": t294["caption"],
                            "row_label_as_printed": t294["labels"][_NC_ROW],
                            "sex_label_as_printed": t294["sex_labels"][s],
                            "age_label_as_printed": t294["age_labels"][g],
                            "source_line": None,
                            "source_line_note": "no Source line is printed beneath the table",
                            "extraction": ("text layer, identified by the sex header over the age "
                                           "band line; wrapped row labels joined by nearest line; "
                                           "numbers rebuilt from word positions"),
                            "integrity": ("the cohort identity closes in all nine columns, every "
                                          "row partitions by sex and by age, and the closing "
                                          "stock equals Tableau 296's TCHAD row"),
                            "age_note": ("'>15ans' is read as 15 and over, because the two "
                                         "printed age bands sum to every printed total"),
                            "note": ("the 2023 new inclusions (Tableau 306) are not emitted as "
                                     "art_initiations, RESUME.md item 48 decision 2"),
                            "reconcile_with": self._reconcile_note("", "art_initiations"),
                        })
                        yield self._row(rec, "art_initiations", 2022, nc[3 * s + g], "",
                                        f"annuaire.2022.tableau{t294['table_id']}.nc."
                                        f"{sex}.{age}", extra, sex=sex, age_group=age)
                        emitted += 1
            if t299 is not None:
                label, total = t299["vals"][_T299_KEYS[2]]
                extra = dict(base, **{
                    "table": f"Tableau {t299['table_id']}", "page": t299["page"],
                    "caption": t299["caption"], "row_label_as_printed": label,
                    "source_line": t299["source_line"],
                    "extraction": ("text layer, identified by the 'Indicateurs Nombre' header "
                                   "over the 'STATUT DE MERE' section"),
                    "integrity": (f"{t299['vals'][_T299_KEYS[0]][0]!r} "
                                  f"({t299['vals'][_T299_KEYS[0]][1]:,}) plus "
                                  f"{t299['vals'][_T299_KEYS[1]][0]!r} "
                                  f"({t299['vals'][_T299_KEYS[1]][1]:,}) equals the total"),
                    "reconcile_with": self._reconcile_note("", "pmtct_arv_count"),
                })
                yield self._row(rec, "pmtct_arv_count", 2022, total, "",
                                f"annuaire.2022.tableau{t299['table_id']}.total_vih_arv", extra)
                emitted += 1
        log.info("td_annuaire: emitted %d rows", emitted)

    # -- helpers for building rows --------------------------------------------------------------

    @staticmethod
    def _base(name: str, year: int, rec: Dict) -> Dict:
        return {
            "edition": name,
            "edition_year": year,
            "edition_title": rec.get("titre"),
            "catalogue_annee": rec.get("annee"),
            "catalogue_annee_note": "the catalogue's annee is the publication year",
            "serving_address_note": (
                "the survey tried " + ", ".join(rec.get("addresses_tried") or [])
                + " and did not record which address served the file"),
        }

    @staticmethod
    def _reconcile_note(admin1: str, indicator: str) -> str:
        if admin1:
            return ("none; no other source in the panel held Chad province rows when this "
                    "connector was built (checked 2 October 2026)")
        return {
            "on_art_count": ("who_gho, who_tme, unaids_aidsinfo and global_fund national counts, "
                             "each sharing only 2023 with this connector, below "
                             "reconcile.MIN_CELLS, so no relationship is declared"),
            "viral_load_tests_performed": ("none; the panel held no Chad viral load rows when "
                                           "this connector was built (checked 2 October 2026)"),
            "viral_suppression_count": ("none; the panel held no Chad viral suppression rows "
                                        "when this connector was built (checked 2 October 2026)"),
            "art_initiations": ("who_tme national count, sharing only 2022 with this connector, "
                                "below reconcile.MIN_CELLS, so no relationship is declared"),
            "pmtct_arv_count": ("unaids_aidsinfo, who_gho and global_fund national counts, each "
                                "sharing only 2022 with this connector, below reconcile.MIN_CELLS, "
                                "so no relationship is declared"),
        }[indicator]

    def _row(self, rec: Dict, indicator: str, year: int, value: float, admin1: str,
             code: str, extra: Dict, **kw) -> PanelRow:
        return self.make_row(
            country_iso3=self.country, country_name=self.country_name,
            indicator_id=indicator, year=year, value=value, unit="count", admin1=admin1,
            source_url=_HOST + str(rec.get("catalogue_path", "")),
            source_indicator_code=code, extra=extra, **kw,
        )
