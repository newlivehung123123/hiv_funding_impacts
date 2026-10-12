"""
Cameroon — CNLS annual HIV report connector (national programme, to-source, sub-national).

Source: the Comité National de Lutte contre le Sida (CNLS) publishes an annual
"Rapport annuel des activités de lutte contre le VIH" at https://cnls.cm/. The reports are
BORN-DIGITAL with a full text layer (no OCR anywhere in this connector), and they carry the
only published REGIONAL HIV cascade for Cameroon: the active ART file and the viral-load
cascade for all ten regions, which PEPFAR MER reports at its own SNU grain and UNAIDS does
not report sub-nationally at all.

The PDFs are cached by `scripts/survey_cameroon_reports.py`, which owns discovery and
download. This connector only PARSES what is already in `data/raw/cameroon/cnls/`; it never
makes a network request. One responsibility each, and the fetching stays in the script the
researcher runs.

WHAT IS INGESTED, AND WHICH EDITION OWNS WHICH YEAR
---------------------------------------------------
Only two of the five cached PDFs are ingested, by explicit allow-list (`_EDITIONS`):

    docs_2025-10-21-rapport-annuel-2024-draft-final-24062025.pdf          -> 2024 (French)
    docs_2025-01-02-rapport-annuel-2023-vih-draft-final-latest.pdf        -> 2023

The allow-list is deliberate and is the central safety property of this connector. CNLS
TABLE NUMBERS ARE NOT STABLE ACROSS EDITIONS: the 2024 edition has 50 numbered tables and
the 2023 edition has 67, and the same number means different things in each. In the 2023
edition "Tableau 38" is "Cartographie nationale des Mother Mentors" and "Tableau 42" is
"Cartographie des APS". A parser pinned to "Tableau 38" would read the count of trained
Mother Mentors as the regional ART active file, and the output would still LOOK correct,
being ten regions plus a national total in a seven-column table. So every table here is
located by CAPTION TEXT, never by table number, and a CNLS PDF that is not on the
allow-list is skipped with a warning rather than parsed on the hope that the captions match.
A new edition is a one-line addition here once its captions have been read by a human.

Verified caption map (read page by page on 2026-10-01):

    block                       2024 French edition      2023 edition
    active ART file by region   Tableau 38, page 79      Tableau 43, page 76
    viral-load cascade          Tableau 42, pages 88-89  Tableau 50, page 92
    key populations             Tableau 18, pages 41-42  (not in this form — see REFUSES)

WHY THE OTHER THREE CACHED PDFs ARE NOT INGESTED
------------------------------------------------
  * `docs_2025-10-21-english-rapport-annuel-2024-draft-final-24062025.pdf` — the English
    edition of the SAME 2024 report. Table 38 is cell-for-cell identical to the French
    edition's and the English edition carries the complete run of tables 1 to 50, so it is
    not an abridgement; it is a translation. Ingesting both would collide on the duplicate-row
    key (country, admin1, indicator, population_group, sex, age_group, year, source_id) and
    one of the two would be silently kept. The FRENCH edition owns 2024, because the 2023
    edition exists in French only and one language across the series keeps the region-label
    aliasing to a single verified map.
  * `docs_2024-11-01-rapport-annuel-2016.pdf` — the 2016 edition, excluded on DEFINITIONAL
    grounds, not on parsing grounds. Its regional data sits behind "Annexe N:" headings
    rather than numbered captions, and its Annexe 7 ties exactly at 205,382, but the
    indicator is "Nombre total de PVVIH venus chercher le traitement en déc. 2016" — a
    December dispensation count, not an active file at 31 December. Joining a dispensation
    count to the 2023 and 2024 active file would manufacture a trend. Annexe 2 is refused
    outright: tick marks with no numbers, blank rows for MINEE, MINAC, MINFOP and MINREX
    that are missing values and not zeros, and a template date of 15/01/2015 inside a 2016
    report.
  * `docs_2024-11-01-psn-2021-2023-vesion-francaise.pdf` — the 2021-2023 national strategic
    plan, a planning document and not a results report.

So `cm_cnls` starts at two annual points, 2023 and 2024. The site's chart floor
(`scripts/build_site.py`, `series_for(..., min_points=3)`) is not met until the 2025 edition
is published and allow-listed, which is expected and is not a defect.

PARSING: WHY `extract_tables()` IS NOT USED ANYWHERE HERE
---------------------------------------------------------
`pdfplumber.extract_tables()` is UNSAFE on these documents and was measured to be so. On
page 79 of the 2024 French edition it fragments Table 38 into one-row "tables" and returns
six of the 11 rows, silently dropping Centre, Extrême-Nord, Nord, Ouest and Sud-Ouest. The
alternating row shading is what it detects as table edges. `extract_text()` returns every
row exactly. So every table here is read from the TEXT LAYER, anchored on the caption and on
the region names.

Cells are delimited by WORD X-POSITION, never by splitting on whitespace. The editions print
intra-number spaces inconsistently — the 2024 edition has "17 377" for Femmes and "8346" for
Hommes in the same row, and its national viral-load row reads "449 290 308 861 68,7% 282 328
91,4%", where a whitespace split yields nine tokens for six columns. Measured across the
four target tables on 2026-10-01, the gap distribution is cleanly bimodal and has a wide
empty band: intra-number gaps run 2.3 to 2.9 points and inter-column gaps run 25.5 to 124.4
points, with nothing in between. `_COL_GAP` is set to 10.0 points, in the middle of that
empty band. A line's words are grouped into columns on that threshold and concatenated
within a column, and a table whose column count is not what the caption map expects is
REFUSED rather than guessed at.

Cleaning before delimiting was tried and is wrong: a `(?<=\\d)[ ,](?=\\d{3}\\b)` pass over a
whole line turns the 2023 row "25365 806" into "25365806". Hence delimit first, clean second.

INTEGRITY GATES (every target table carries exact internal checks; all were verified to pass
offline before this connector was written)
-------------------------------------------------------------------------------------------
Active ART file (2024 Table 38 / 2023 Tableau 43):
  * all ten regions present exactly once, plus a printed national row;
  * Femmes + Hommes == Total in all ten regions (ties in both editions);
  * the Femmes, Hommes, Total and Enfants columns each sum to the printed national row
    (2024: 307,130 / 142,160 / 449,290 / 11,131; 2023: 308,298 / 140,520 / 448,818 / 11,348);
  * the printed "% enfants" and "Poids région" columns reproduce from the counts.
Viral-load cascade (2024 Table 42 / 2023 Tableau 50):
  * the "File active" column equals the active-file table's Total column region by region and
    nationally — a CROSS-TABLE check between two independently printed tables, which ties in
    both editions;
  * the tested and suppressed columns sum to the printed national row;
  * the printed coverage and suppression rates reproduce from the counts (2024: 308,861 /
    449,290 = 68.7% and 282,328 / 308,861 = 91.4%; 2023: 203,134 / 448,818 = 45.3% and
    174,593 / 203,134 = 85.9%).
Key populations (2024 Table 18):
  * the four subgroup rows sum to the printed Total row on all three counts
    (135,771 tested, 4,939 positive, 4,768 linked).

Two tolerances, both forced by defects in the sources and both documented where they are
defined. `_COUNT_TOL = 1` exists because the 2023 edition's viral-load tested column sums to
203,135 against a printed 203,134; the connector emits both the regional values and the
printed national value as printed and records the one-unit gap in `extra` rather than
silently reconciling it, and a gap larger than one unit refuses the table. `_RATE_TOL = 0.11`
percentage points exists because the 2024 edition mixes rounding and truncation in the same
table: Table 18 prints 3,006/91,188 = 3.296% as "3,3%" (rounded) and 179/4,493 = 3.984% as
"3,9%" (truncated), and 1,537/1,653 = 92.98% as "92,9%" (truncated).

WHAT THIS CONNECTOR REFUSES TO EMIT, AND WHY
--------------------------------------------
  * THE ENTIRE FINANCING CHAPTER. The 2024 edition's tables 45 to 50 and the 2023 edition's
    equivalents carry budget inscriptions by donor, Global Fund grant execution and
    counterpart-fund spending, and every figure is in CFA FRANCS. Every financing indicator
    in `CANONICAL_INDICATORS` has unit USD, the panel holds no exchange-rate series (and
    `world_bank.py` pulls `SP.POP.TOTL` and `SH.DYN.AIDS.ZS` only, not `PA.NUS.FCRF`), and NO
    CNLS DOCUMENT STATES A DOLLAR RATE — four of the cached documents mention 655, which is
    the fixed CFA-to-euro peg, and none gives a dollar rate. Hard-coding a rate would produce
    Cameroon USD figures that sit beside PEPFAR's in the same series and are traceable to
    nothing in this repository, so the money chapter is refused here. Cameroon's HIV
    expenditure enters the panel through `cm_nasa` instead, in local-currency indicators that
    declare the currency plus currency-free recomputed shares, neither of which needs a rate.
    The CNLS money tables also carry four arithmetic defects found on 2026-10-01 (Table 46's
    printed TOTAL GENERAL omits the 265,000,000 OMS line it lists; Table 47's budget column
    is two francs out; Table 48's RUBRIQUE N°3 ARV row leaves the DISPONIBLE cell blank where
    4,102,139,084 belongs; page 119 restates Table 46's total five francs low and uses the
    degree sign as a thousands separator), which would each need a decision even once a rate
    existed.
  * THE KEY-POPULATION PREVENTION TREND TABLE (Tableau 6 in both editions, "Prévention et
    dépistage au sein des populations clés et vulnérables"), which would give `kp_reached`.
    Designed but not built. Both editions print the SAME table over five years, so only the
    edition's own year column is ingestible without the 2023 and 2024 editions colliding on
    the four years they share, and the rows carry fewer values than there are year columns
    (the 2023 edition's JGNS row prints three values under five year headings), so cells must
    be assigned by matching each cell's x-band to the header year's x-band rather than by
    position. Worth building; needs its own verification pass.
  * THE "UD" ROW wherever it appears. CNLS classifies "UD" (utilisateurs de drogue) as a
    VULNERABLE population and "UDI" (injecting drug users) as a KEY population, and the 2024
    edition reports them in different tables with different totals — 6,873 UD tested in
    Tableau 17 against 4,493 UDI in Tableau 18. Mapping UD onto `POP_PWID` would merge two
    groups the source keeps apart. Only the UDI row becomes `pwid`.
  * THE PRINTED TOTAL ROW of the key-population table, used as an integrity check and not
    emitted. `population_group="all"` means the general population, so emitting a
    key-populations-combined figure under it would be wrong, and the four subgroup rows carry
    the same information. This follows `cambodia_nchads.py`, which skips its aggregate page
    for the same reason.
  * THE "% enfants" AND "Poids région" COLUMNS, which are a region's children as a share of
    its own active file and a region's share of the national active file. No indicator covers
    either, both recompute exactly from counts this connector does emit, and both are used
    here as integrity checks instead.
  * THE VIRAL-LOAD TABLE'S "File active" COLUMN, which reprints the active-file table's Total
    column. Emitting it would duplicate the `on_art_count` row key exactly. It is used as the
    cross-table check instead, which is worth more than a second copy of the same number.
  * ALL PROSE FIGURES. The prose in both editions disagrees with the tables it describes, so
    nothing here is read from a sentence. Measured instances: page 41 of the 2024 edition
    cites "(Tableau 17)" for figures printed in Tableau 18; page 79 says "le tableau 37
    montre" for Table 38's data and then calls Table 39 "le tableau 38"; page 92 of the 2023
    edition cites "tableau 52" for Tableau 50; the 2023 edition's page 76 prose puts children
    at 2.7% of the national file where its own Tableau 43 prints 2.5%, and names Est at 3.1%
    and Nord-Ouest at 3.7% where Tableau 43 prints 2.9% and 3.4%, so that paragraph was not
    updated from an earlier edition; and page 92 of the 2023 edition puts Centre's suppression
    at 71.7% where Tableau 50 prints 72.3%.

ADMIN1 LABELS
-------------
`admin1` carries the ten PEPFAR SNU spellings exactly ("Adamaoua", "Centre", "Est", "Extreme
Nord", "Littoral", "Nord", "Nord Ouest", "Ouest", "Sud", "Sud Ouest"), verified against the
`pepfar_snu` and `pepfar_agency_snu` rows already in the panel, which use all ten and no
others. So the regional rows reconcile against PEPFAR without an alias step downstream. The
document's own spelling goes into `extra["admin1_source_label"]`, because it varies WITHIN one
document: the 2024 edition's Table 38 prints "Extrême-Nord", "Nord-Ouest" and "Sud-Ouest"
while its Table 42 prints "Extrême-nord", "Nord-ouest" and "Sud-ouest". Matching is therefore
accent-insensitive, case-insensitive and hyphen-insensitive, on the whole first-column string.

TAGGING: source_type = routine_programme_record (DHIS2 and reference-laboratory returns,
per the tables' own "Source :" lines).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import (
    PanelRow,
    SourceType,
    POP_GBMSM,
    POP_PWID,
    POP_SEX_WORKERS,
    POP_TRANSGENDER,
)
# The PDF geometry primitives are shared with `cameroon_nasa.py`, which reads a different
# family of Cameroon documents off the same text layer. `_pdf_text` carries the measurements
# that justify the line and column tolerances. Number parsing stays local to this module,
# because the two document families use opposite comma conventions: a comma is a DECIMAL mark
# in the CNLS reports and `_to_int` below must reject it, while the NASA assessments use a
# comma as a thousands separator and must accept it.
from ._pdf_text import (
    COL_GAP as _COL_GAP,
    LINE_TOL as _LINE_TOL,
    columns as _columns,
    lines as _lines,
    match_label as _match_label,
    norm as _norm,
    to_pct as _to_pct,
)

log = logging.getLogger("hivimpact")

# -- measured parsing constants ------------------------------------------------------------
# `_LINE_TOL` (4.0 points) and `_COL_GAP` (10.0 points) are imported above from `_pdf_text`,
# which documents the measurements behind both: row pitch about 13 points against a worst
# intra-row jitter of 1.4 points, and a gap distribution with intra-number gaps of 2.3 to 2.9
# points, inter-column gaps of 25.5 to 124.4 points and nothing in between. The two
# tolerances below are specific to the CNLS reports and stay here.
# Percentage points. The sources mix rounding and truncation of one-decimal percentages
# within a single table, so half-a-unit (0.05) is too tight; see the module docstring.
_RATE_TOL = 0.11
# Units. Exists only for the 2023 edition's viral-load tested column, which sums to 203,135
# against a printed 203,134. A larger gap than this refuses the table.
_COUNT_TOL = 1

# -- the allow-list: filename -> (year, source URL). See the module docstring. --------------
# URLs are the CNLS document paths the survey script downloaded; its `_local_name()` flattens
# a URL path by replacing "/" with "_", so each filename below is "docs/<slug>" flattened.
_CNLS_ROOT = "https://cnls.cm"
_EDITIONS: Dict[str, Tuple[int, str]] = {
    "docs_2025-10-21-rapport-annuel-2024-draft-final-24062025.pdf": (
        2024, f"{_CNLS_ROOT}/docs/2025-10-21-rapport-annuel-2024-draft-final-24062025.pdf"),
    "docs_2025-01-02-rapport-annuel-2023-vih-draft-final-latest.pdf": (
        2023, f"{_CNLS_ROOT}/docs/2025-01-02-rapport-annuel-2023-vih-draft-final-latest.pdf"),
}

# The three cached PDFs that are deliberately not ingested, each with the ground on which the
# decision was taken. See the module docstring for the full reasoning. A file named here is a
# closed question, so `fetch` says so at INFO rather than warning about it on every run; a
# file named nowhere is a genuinely unread edition and still raises a warning.
_SETTLED_REFUSALS: Dict[str, str] = {
    "docs_2025-10-21-english-rapport-annuel-2024-draft-final-24062025.pdf": (
        "this is the English translation of the same 2024 report, carrying the complete run "
        "of tables 1 to 50 with Table 38 cell-for-cell identical to the French edition's, so "
        "ingesting both would collide on the duplicate-row key and one of the two would be "
        "kept silently; the French edition owns 2024 because the 2023 edition exists in "
        "French only"),
    "docs_2024-11-01-rapport-annuel-2016.pdf": (
        "the 2016 edition is refused on definitional grounds and not on parsing grounds, "
        "because its Annexe 7 counts people who came to collect treatment during December "
        "2016 and not the active file at 31 December, so joining the 2016 figure to the 2023 "
        "and 2024 active file would manufacture a trend"),
    "docs_2024-11-01-psn-2021-2023-vesion-francaise.pdf": (
        "the 2021-2023 national strategic plan is a planning document and reports no "
        "results"),
}

# -- captions. Matched on text, never on table number. --------------------------------------
# "par région" is what separates the regional active-file table from its two neighbours: the
# 2024 edition's Tableau 39 is "par sexe et âge" and its Tableau 41 is "de la file active
# régionale", neither of which matches.
_CAP_ACTIVE_FILE = re.compile(
    r"r[eé]partition\s+de\s+la\s+file\s+active\s+par\s+r[eé]gion", re.I)
_CAP_VIRAL_LOAD = re.compile(
    r"couverture\s+et\s+suppression\s+de\s+la\s+cv\s+par\s+r[eé]gion\s+en\s+(20\d\d)", re.I)
_CAP_KEY_POPS = re.compile(
    r"d[eé]pistage\s+et\s+lien\s+au\s+tarv\s+chez\s+les\s+populations\s+cl[eé]s\s+en\s+(20\d\d)",
    re.I)
# The table number as the document itself prints it, kept for provenance only.
_TABLE_NO = re.compile(r"tableau\s*(\d+)", re.I)

# -- row labels -----------------------------------------------------------------------------
# Keys are normalised (lower case, accents stripped, hyphens to spaces); values are the
# PEPFAR SNU spellings already in the panel.
_REGIONS: Dict[str, str] = {
    "adamaoua": "Adamaoua",
    "centre": "Centre",
    "est": "Est",
    "extreme nord": "Extreme Nord",
    "littoral": "Littoral",
    "nord": "Nord",
    "nord ouest": "Nord Ouest",
    "ouest": "Ouest",
    "sud": "Sud",
    "sud ouest": "Sud Ouest",
}
_NATIONAL = {"national", "total", "total national", "cameroun", "ensemble"}

# Key-population row label -> population_group. "ud" is deliberately absent; CNLS counts
# utilisateurs de drogue as a vulnerable population and UDI as a key population, and the two
# have different totals in the same edition.
_KP_ROWS: Dict[str, str] = {
    "ts": POP_SEX_WORKERS,
    "hsh": POP_GBMSM,
    "tg": POP_TRANSGENDER,
    "udi": POP_PWID,
}


def _to_int(cell: str) -> Optional[int]:
    """A column-joined count cell to an int, or None if the cell is not a plain count.

    Runs only AFTER x-position column delimiting, so stripping every space is safe here;
    run over a whole line it would merge adjacent columns. Returns None (never 0) for a cell
    carrying a percent sign or a decimal comma, so a misaligned column fails the row instead
    of coercing a rate into a count.
    """
    s = str(cell or "").strip()
    if s in ("", "-", "‐", "–", "—", "N/A", "n/a", "ND", "nd", "."):
        return None
    if "%" in s or "," in s:
        return None
    s = re.sub(r"[\s   ]", "", s)
    return int(s) if re.fullmatch(r"\d+", s) else None


# -- locating and reading one table ---------------------------------------------------------
#: a line of a contents page ends in its page number after a run of dots. Both editions
#: list every caption twice, once in the list of tables and once over the table itself, and
#: the dotted leader is what separates the two.
_DOTTED_LEADER = re.compile(r"\.{4,}")


def _find_captions(pdf, caption_re: re.Pattern) -> List[Dict]:
    """Every line in the document whose text matches a caption pattern, best candidate first.

    Three things are being handled here, each measured on the two allow-listed editions.

    A list-of-tables line matches the same pattern as the caption it lists (the 2024 edition
    lists all 50 captions on pages 8 and 9, the 2023 edition all 67 on page 11). Those lines
    are dropped on their dotted leader. Dropping them explicitly is better than relying on
    the integrity gates to refuse them, because a contents line would otherwise be the first
    candidate tried on every table in the document.

    A numbered caption is preferred over an unnumbered one. Both editions print a numberless
    section heading immediately above the real caption of the active-file table ("2.4.3.
    Répartition de la file active par région, par sexe et âge" on page 79 of the 2024
    edition, "2.3.3. ..." on page 76 of the 2023 edition), and a scan starting from the
    heading reaches the same table as a scan starting from the caption. Trying the numbered
    caption first means the table number recorded on every emitted row is the number the
    document prints, which is what a reader needs to find the figure again. The number is
    never what identifies the table, because CNLS table numbers are not stable across
    editions; the caption text identifies it and the number is provenance only.

    Page order is kept within each group, so an earlier table still wins over a later one.
    """
    out: List[Dict] = []
    for pi, page in enumerate(pdf.pages):
        for ln in _lines(page):
            m = caption_re.search(ln["text"])
            if not m:
                continue
            if _DOTTED_LEADER.search(ln["text"]):
                continue
            tno = _TABLE_NO.search(ln["text"])
            out.append({
                "page_index": pi,
                "mid": ln["mid"],
                "text": ln["text"],
                "match": m,
                "table_no": int(tno.group(1)) if tno else None,
            })
    out.sort(key=lambda c: (c["table_no"] is None, c["page_index"], c["mid"]))
    return out


def _read_table(pdf, cap: Dict, label_map: Dict[str, str], total_labels: set,
                n_cols: int, max_pages: int = 3) -> Tuple[Dict[str, List[str]], Optional[List[str]]]:
    """Collect one table's labelled rows and its printed total row, following page breaks.

    A line is taken as a data row only when it has EXACTLY the column count the caption map
    expects, its first column matches a known row label, and every other column parses as a
    count or a percentage. Those three conditions together are what reject prose: page 79 of
    the 2024 edition carries the sentence "Sud quant à elles, ont les plus faibles poids,
    soit respectivement 5,7% et 5,8 %.", which starts with a region name and contains
    percentages, and which fails on the column count.

    The 2024 edition's viral-load table runs across pages 88 and 89 with no repeated header,
    so the scan continues onto following pages until every expected label and a total row
    have been seen.
    """
    rows: Dict[str, List[str]] = {}
    total: Optional[List[str]] = None
    start = cap["page_index"]
    for pi in range(start, min(start + max_pages, len(pdf.pages))):
        for ln in _lines(pdf.pages[pi]):
            if pi == start and ln["mid"] <= cap["mid"]:
                continue                                  # above the caption on its own page
            cols = _columns(ln["words"])
            if len(cols) != n_cols:
                continue
            if not all(_to_int(c) is not None or _to_pct(c) is not None for c in cols[1:]):
                continue
            if _norm(cols[0]) in total_labels:
                if total is None:
                    total = cols
                continue
            label = _match_label(cols[0], label_map)
            if label is not None and label not in rows:
                rows[label] = cols
        if total is not None and len(rows) == len(label_map):
            break
    return rows, total


def _close(a: Optional[float], b: Optional[float], tol: float) -> bool:
    return a is not None and b is not None and abs(a - b) <= tol


# -- block A: the regional active ART file ---------------------------------------------------
# Région | Femmes | Hommes | Total | Enfants | % enfants | Poids région
_AF_COLS = 7


def _parse_active_file(pdf, tag: str) -> Optional[Dict]:
    """The regional active ART file, or None if no candidate passes every integrity gate."""
    for cap in _find_captions(pdf, _CAP_ACTIVE_FILE):
        rows, total = _read_table(pdf, cap, _REGIONS, _NATIONAL, _AF_COLS)
        if len(rows) != len(_REGIONS) or total is None:
            continue
        regions: Dict[str, Dict] = {}
        bad = None
        for snu, cols in rows.items():
            femmes, hommes, tot, enfants = (_to_int(cols[1]), _to_int(cols[2]),
                                            _to_int(cols[3]), _to_int(cols[4]))
            if None in (femmes, hommes, tot, enfants):
                bad = f"{snu}: a count cell did not parse"
                break
            if femmes + hommes != tot:
                bad = (f"{snu}: Femmes {femmes:,} + Hommes {hommes:,} = {femmes + hommes:,}, "
                       f"printed Total {tot:,}")
                break
            if not _close(_to_pct(cols[5]), 100.0 * enfants / tot if tot else None, _RATE_TOL):
                bad = f"{snu}: printed % enfants {cols[5]!r} does not reproduce from {enfants}/{tot}"
                break
            regions[snu] = {"femmes": femmes, "hommes": hommes, "total": tot,
                            "enfants": enfants, "source_label": cols[0].strip()}
        if bad:
            log.warning("cm_cnls: %s active-file candidate on page %d rejected — %s",
                        tag, cap["page_index"] + 1, bad)
            continue

        nat = {k: _to_int(total[i]) for k, i in
               (("femmes", 1), ("hommes", 2), ("total", 3), ("enfants", 4))}
        if any(v is None for v in nat.values()):
            continue
        sums = {k: sum(r[k] for r in regions.values()) for k in nat}
        off = {k: sums[k] - nat[k] for k in nat if sums[k] != nat[k]}
        if off:
            log.warning("cm_cnls: %s active-file page %d rejected — regional sums do not tie "
                        "to the printed national row: %s", tag, cap["page_index"] + 1, off)
            continue
        # the printed region weights must reproduce against the printed national total
        for snu, cols in rows.items():
            share = 100.0 * regions[snu]["total"] / nat["total"]
            if not _close(_to_pct(cols[6]), share, _RATE_TOL):
                log.warning("cm_cnls: %s active-file page %d rejected — printed Poids région "
                            "%r for %s does not reproduce from %d/%d", tag,
                            cap["page_index"] + 1, cols[6], snu, regions[snu]["total"],
                            nat["total"])
                break
        else:
            log.info("cm_cnls: %s active file read from Tableau %s, page %d — ten regions tie "
                     "to the printed national row (%s on ART, %s children)", tag,
                     cap["table_no"], cap["page_index"] + 1, f"{nat['total']:,}",
                     f"{nat['enfants']:,}")
            return {"regions": regions, "national": nat, "table_no": cap["table_no"],
                    "page": cap["page_index"] + 1, "caption": cap["text"]}
    return None


# -- block B: the regional viral-load cascade ------------------------------------------------
# Région | File active | Nbre ayant bénéficié de CV | Couverture CV | Nbre ayant supprimé | Taux
_VL_COLS = 6


def _parse_viral_load(pdf, tag: str, active: Dict) -> Optional[Dict]:
    """The regional viral-load cascade, cross-checked against the active-file table.

    The "File active" column is not emitted; it reprints the active-file table's Total column
    and is used here as a cross-table integrity check between two tables printed independently
    nine pages apart.
    """
    for cap in _find_captions(pdf, _CAP_VIRAL_LOAD):
        rows, total = _read_table(pdf, cap, _REGIONS, _NATIONAL, _VL_COLS)
        if len(rows) != len(_REGIONS) or total is None:
            continue
        regions: Dict[str, Dict] = {}
        bad = None
        for snu, cols in rows.items():
            fa, tested, suppressed = _to_int(cols[1]), _to_int(cols[2]), _to_int(cols[4])
            cov, sup = _to_pct(cols[3]), _to_pct(cols[5])
            if None in (fa, tested, suppressed, cov, sup):
                bad = f"{snu}: a cell did not parse"
                break
            if fa != active["regions"][snu]["total"]:
                bad = (f"{snu}: viral-load File active {fa:,} does not match the active-file "
                       f"table's Total {active['regions'][snu]['total']:,}")
                break
            if not _close(cov, 100.0 * tested / fa if fa else None, _RATE_TOL):
                bad = f"{snu}: printed coverage {cols[3]!r} does not reproduce from {tested}/{fa}"
                break
            if not _close(sup, 100.0 * suppressed / tested if tested else None, _RATE_TOL):
                bad = (f"{snu}: printed suppression {cols[5]!r} does not reproduce from "
                       f"{suppressed}/{tested}")
                break
            regions[snu] = {"file_active": fa, "tested": tested, "suppressed": suppressed,
                            "coverage_pct": cov, "suppression_pct": sup,
                            "source_label": cols[0].strip()}
        if bad:
            log.warning("cm_cnls: %s viral-load candidate on page %d rejected — %s",
                        tag, cap["page_index"] + 1, bad)
            continue

        nat = {"file_active": _to_int(total[1]), "tested": _to_int(total[2]),
               "suppressed": _to_int(total[4]), "coverage_pct": _to_pct(total[3]),
               "suppression_pct": _to_pct(total[5])}
        if any(v is None for v in nat.values()):
            continue
        if nat["file_active"] != active["national"]["total"]:
            log.warning("cm_cnls: %s viral-load page %d rejected — national File active %s "
                        "does not match the active-file table's %s", tag, cap["page_index"] + 1,
                        f"{nat['file_active']:,}", f"{active['national']['total']:,}")
            continue
        # The 2023 edition's tested column sums one unit over its printed national value, so a
        # gap of at most _COUNT_TOL is recorded and carried rather than reconciled away; a
        # larger gap refuses the table.
        gaps: Dict[str, int] = {}
        for key in ("tested", "suppressed"):
            diff = sum(r[key] for r in regions.values()) - nat[key]
            if abs(diff) > _COUNT_TOL:
                log.warning("cm_cnls: %s viral-load page %d rejected — the %s column sums to "
                            "%s against a printed national %s", tag, cap["page_index"] + 1, key,
                            f"{sum(r[key] for r in regions.values()):,}", f"{nat[key]:,}")
                gaps = None
                break
            if diff:
                gaps[key] = diff
        if gaps is None:
            continue
        if not _close(nat["coverage_pct"],
                      100.0 * nat["tested"] / nat["file_active"], _RATE_TOL) or \
           not _close(nat["suppression_pct"],
                      100.0 * nat["suppressed"] / nat["tested"], _RATE_TOL):
            log.warning("cm_cnls: %s viral-load page %d rejected — the printed national rates "
                        "do not reproduce from the printed national counts",
                        tag, cap["page_index"] + 1)
            continue
        if gaps:
            log.warning("cm_cnls: %s viral-load Tableau %s — the regional %s column(s) sum "
                        "%s off the printed national row; both are emitted as printed and the "
                        "gap is recorded on the national row", tag, cap["table_no"],
                        ", ".join(gaps), gaps)
        log.info("cm_cnls: %s viral-load cascade read from Tableau %s, page %d — File active "
                 "ties to the active-file table in all ten regions (%s tested, %s suppressed)",
                 tag, cap["table_no"], cap["page_index"] + 1, f"{nat['tested']:,}",
                 f"{nat['suppressed']:,}")
        return {"regions": regions, "national": nat, "table_no": cap["table_no"],
                "page": cap["page_index"] + 1, "caption": cap["text"], "sum_gaps": gaps,
                "year": int(cap["match"].group(1))}
    return None


# -- block C: the national key-population cascade --------------------------------------------
# Populations Clés | dépistés | testés positifs | taux | mis sous traitement | taux de lien
_KP_COLS = 6


def _parse_key_populations(pdf, tag: str) -> Optional[Dict]:
    """The national key-population testing cascade (2024 edition's Tableau 18 only)."""
    for cap in _find_captions(pdf, _CAP_KEY_POPS):
        rows, total = _read_table(pdf, cap, _KP_ROWS, {"total"}, _KP_COLS)
        if len(rows) != len(_KP_ROWS) or total is None:
            continue
        groups: Dict[str, Dict] = {}
        bad = None
        for grp, cols in rows.items():
            tested, positive, linked = _to_int(cols[1]), _to_int(cols[2]), _to_int(cols[4])
            pos_pct, link_pct = _to_pct(cols[3]), _to_pct(cols[5])
            if None in (tested, positive, linked, pos_pct, link_pct):
                bad = f"{grp}: a cell did not parse"
                break
            if not _close(pos_pct, 100.0 * positive / tested if tested else None, _RATE_TOL):
                bad = (f"{grp}: printed positivity {cols[3]!r} does not reproduce from "
                       f"{positive}/{tested}")
                break
            if not _close(link_pct, 100.0 * linked / positive if positive else None, _RATE_TOL):
                bad = (f"{grp}: printed linkage {cols[5]!r} does not reproduce from "
                       f"{linked}/{positive}")
                break
            groups[grp] = {"tested": tested, "positive": positive, "linked": linked,
                           "source_label": cols[0].strip()}
        if bad:
            log.warning("cm_cnls: %s key-population candidate on page %d rejected — %s",
                        tag, cap["page_index"] + 1, bad)
            continue
        nat = {"tested": _to_int(total[1]), "positive": _to_int(total[2]),
               "linked": _to_int(total[4])}
        if any(v is None for v in nat.values()):
            continue
        off = {k: sum(g[k] for g in groups.values()) - nat[k] for k in nat
               if sum(g[k] for g in groups.values()) != nat[k]}
        if off:
            log.warning("cm_cnls: %s key-population page %d rejected — the four subgroup rows "
                        "do not sum to the printed Total row: %s", tag, cap["page_index"] + 1, off)
            continue
        log.info("cm_cnls: %s key populations read from Tableau %s, page %d — four subgroups "
                 "sum to the printed Total (%s tested, %s positive, %s linked)", tag,
                 cap["table_no"], cap["page_index"] + 1, f"{nat['tested']:,}",
                 f"{nat['positive']:,}", f"{nat['linked']:,}")
        return {"groups": groups, "national": nat, "table_no": cap["table_no"],
                "page": cap["page_index"] + 1, "caption": cap["text"],
                "year": int(cap["match"].group(1))}
    return None


class _YearMismatch(Exception):
    """A table caption's year disagrees with the edition allow-list.

    Raised to abandon a whole document, not one table. If the viral-load caption says 2023
    inside the file the allow-list calls the 2024 edition, then either CNLS republished a
    document under the same filename or the allow-list is wrong, and in both cases the year
    on every row from that document is unsafe.
    """


class CameroonCNLSConnector(BaseConnector):
    """Cameroon CNLS annual report — the regional HIV cascade.

    Parse-only by design: `scripts/survey_cameroon_reports.py` discovers and downloads the
    CNLS PDFs, and this connector reads what is already in `raw_dir`. Keeping the fetching in
    one script the researcher runs means this connector makes no network request at all, and
    there is only one copy of the discovery logic to keep correct.
    """

    source_id = "cm_cnls"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Cameroon CNLS annual report — regional ART active file, regional viral-load "
                   "cascade and national key-population testing (to-source, parse-only).")
    country = "CMR"

    def __init__(self, raw_dir: str = "data/raw/cameroon/cnls", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- emission ---------------------------------------------------------------------------
    def _base_extra(self, path: Path, year: int, block: Dict) -> Dict:
        table_no = block["table_no"]
        return {
            "edition": path.name,
            "edition_year": year,
            "table": f"Tableau {table_no}" if table_no else "unnumbered",
            "page": block["page"],
            "caption": block["caption"],
            "extraction": ("text layer, caption-anchored, cells delimited by word x-position "
                           "(extract_tables() drops rows on these documents)"),
        }

    def _active_file_rows(self, path: Path, year: int, url: str, af: Dict) -> Iterator[PanelRow]:
        extra0 = self._base_extra(path, year, af)
        code = f"cnls.{year}.tableau{af['table_no']}"
        units = [("femmes", "female", "all"), ("hommes", "male", "all"),
                 ("total", "all", "all"), ("enfants", "all", "0-14")]
        places = [(snu, r) for snu, r in sorted(af["regions"].items())]
        places.append(("", {**af["national"], "source_label": "National"}))
        for admin1, rec in places:
            for key, sex, age in units:
                extra = dict(extra0)
                extra["admin1_source_label"] = rec["source_label"]
                extra["column"] = key
                extra["integrity"] = (
                    "Femmes + Hommes = Total in all ten regions, and the Femmes, Hommes, Total "
                    "and Enfants columns each sum exactly to the printed national row")
                extra["reconcile_with"] = (
                    "pepfar_snu / pepfar_agency_snu (regional TX_CURR, same ten SNU labels) and "
                    "unaids_aidsinfo (national on-ART count)")
                if key == "enfants":
                    extra["note"] = ("children under 15 on ART, the Enfants column; the source "
                                     "gives no sex split for children")
                yield self.make_row(
                    country_iso3="CMR", country_name="Cameroon",
                    indicator_id="on_art_count", year=year, value=rec[key], unit="count",
                    admin1=admin1, sex=sex, age_group=age,
                    source_url=url, source_indicator_code=f"{code}.{key}", extra=extra,
                )

    def _viral_load_rows(self, path: Path, year: int, url: str, vl: Dict) -> Iterator[PanelRow]:
        extra0 = self._base_extra(path, year, vl)
        code = f"cnls.{year}.tableau{vl['table_no']}"
        places = [(snu, r) for snu, r in sorted(vl["regions"].items())]
        places.append(("", {**vl["national"], "source_label": "National"}))
        for admin1, rec in places:
            common = dict(extra0)
            common["admin1_source_label"] = rec["source_label"]
            common["integrity"] = (
                "the File active column matches the active-file table region by region and "
                "nationally, and the printed coverage and suppression rates reproduce from the "
                "printed counts")
            common["reconcile_with"] = "pepfar_snu (TX_PVLS numerator and denominator by SNU)"
            if admin1 == "" and vl["sum_gaps"]:
                common["source_defect"] = (
                    "the regional rows sum " + ", ".join(
                        f"{d:+d} on {k}" for k, d in sorted(vl["sum_gaps"].items()))
                    + " against this printed national row; both are emitted as printed and "
                      "neither is adjusted")

            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id="viral_load_tests_performed", year=year, value=rec["tested"],
                unit="count", admin1=admin1, source_url=url,
                source_indicator_code=f"{code}.cv_realisee",
                extra={**common, "column": "Nbre de PvVIH ayant bénéficié de CV"},
            )
            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id="viral_suppression_count", year=year, value=rec["suppressed"],
                unit="count", admin1=admin1, source_url=url,
                source_indicator_code=f"{code}.cv_supprimee",
                extra={**common, "column": "Nbre de PvVIH ayant supprimé la CV"},
            )
            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id="viral_load_coverage_pct", year=year, value=rec["coverage_pct"],
                unit="percent", admin1=admin1,
                numerator=rec["tested"], denominator=rec["file_active"],
                source_url=url, source_indicator_code=f"{code}.couverture_cv",
                extra={**common, "column": "Couverture CV",
                       "note": "printed rate, carried as printed; denominator = the active file"},
            )
            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id="viral_suppression_pct", year=year, value=rec["suppression_pct"],
                unit="percent", admin1=admin1,
                numerator=rec["suppressed"], denominator=rec["tested"],
                source_url=url, source_indicator_code=f"{code}.taux_suppression",
                extra={**common, "column": "Taux de suppression",
                       "note": ("printed rate, carried as printed. DENOMINATOR = people with a "
                                "viral-load result, not everyone on ART, so this matches the "
                                "PEPFAR TX_PVLS convention and is NOT like-for-like with a "
                                "third 95 computed over all PLHIV. Cameroon 2024: 91.4% of "
                                "those measured were suppressed while only 68.7% were measured.")},
            )

    def _key_population_rows(self, path: Path, year: int, url: str, kp: Dict) -> Iterator[PanelRow]:
        extra0 = self._base_extra(path, year, kp)
        code = f"cnls.{year}.tableau{kp['table_no']}"
        for grp, rec in sorted(kp["groups"].items()):
            common = dict(extra0)
            common["population_source_label"] = rec["source_label"]
            common["integrity"] = ("the four subgroup rows sum exactly to the printed Total "
                                   "row on all three counts")
            common["reconcile_with"] = "unaids_aidsinfo (key populations), pepfar_panorama"
            common["note"] = ("CNLS counts UD (utilisateurs de drogue) as a VULNERABLE "
                              "population in a separate table and UDI as a KEY population "
                              "here; only the UDI row is mapped to pwid")
            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id="kp_tested", year=year, value=rec["tested"], unit="count",
                population_group=grp, source_url=url,
                source_indicator_code=f"{code}.kp_depistes", extra=dict(common),
            )
            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id="kp_hiv_positive", year=year, value=rec["positive"], unit="count",
                population_group=grp, numerator=rec["positive"], denominator=rec["tested"],
                source_url=url, source_indicator_code=f"{code}.kp_positifs", extra=dict(common),
            )
            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id="kp_art_enrolled", year=year, value=rec["linked"], unit="count",
                population_group=grp, numerator=rec["linked"], denominator=rec["positive"],
                source_url=url, source_indicator_code=f"{code}.kp_lien_tarv", extra=dict(common),
            )

    # -- driver -----------------------------------------------------------------------------
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
            log.error("cm_cnls: pdfplumber not installed (pip install pdfplumber)")
            return
        if not self.raw_dir.exists():
            log.warning("cm_cnls: %s does not exist — run scripts/survey_cameroon_reports.py "
                        "to cache the CNLS reports", self.raw_dir)
            return

        emitted = 0
        editions_read = 0
        for path in sorted(self.raw_dir.glob("*.pdf")):
            if path.name not in _EDITIONS:
                # Three of the five cached PDFs are settled refusals, not unread files, and
                # the warning says which kind the file is. A reader who sees the same three
                # lines on every run should be able to tell at a glance that nothing is
                # waiting to be done about them.
                settled = _SETTLED_REFUSALS.get(path.name)
                if settled:
                    log.info("cm_cnls: %s is not ingested, and the decision is settled, not "
                             "outstanding — %s. No action is needed on this file.",
                             path.name, settled)
                else:
                    log.warning("cm_cnls: %s is not on the edition allow-list — skipped. "
                                "CNLS table numbers are not stable across editions (the "
                                "2023 edition's Tableau 38 is a Mother Mentors map, not the "
                                "ART active file), so a new edition's captions are read by "
                                "a human and added to _EDITIONS.", path.name)
                continue
            year, url = _EDITIONS[path.name]
            if year < start_year or year > end_year:
                continue
            tag = f"{year} edition"
            try:
                with pdfplumber.open(str(path)) as pdf:
                    active = _parse_active_file(pdf, tag)
                    if active is None:
                        log.warning("cm_cnls: %s — no active-file table passed its integrity "
                                    "gates; nothing emitted for %d", path.name, year)
                        continue
                    viral = _parse_viral_load(pdf, tag, active)
                    keypops = _parse_key_populations(pdf, tag)

                    # The viral-load caption carries the data year, so it cross-checks the
                    # allow-list. The 2024 editions have image-only cover pages, which is why
                    # the year is taken from a table caption and not from the title page.
                    for block, label in ((viral, "viral-load"), (keypops, "key-population")):
                        if block is not None and block["year"] != year:
                            log.error("cm_cnls: %s — the %s caption says %d but the allow-list "
                                      "says %d; refusing the whole document rather than "
                                      "emitting a year that cannot be confirmed",
                                      path.name, label, block["year"], year)
                            raise _YearMismatch

                    editions_read += 1
                    for row in self._active_file_rows(path, year, url, active):
                        emitted += 1
                        yield row
                    if viral is not None:
                        for row in self._viral_load_rows(path, year, url, viral):
                            emitted += 1
                            yield row
                    else:
                        log.warning("cm_cnls: %s — no viral-load table passed its integrity "
                                    "gates; the active file is still emitted", path.name)
                    if keypops is not None:
                        for row in self._key_population_rows(path, year, url, keypops):
                            emitted += 1
                            yield row
                    else:
                        log.info("cm_cnls: %s — no key-population table in this edition's "
                                 "Tableau 18 form (expected for the 2023 edition, which reports "
                                 "key populations only as a five-year trend table)", path.name)
            except _YearMismatch:
                continue
            except Exception as exc:
                log.warning("cm_cnls: %s failed to parse (%s) — nothing emitted for %d",
                            path.name, exc, year)
                continue

        log.info("cm_cnls: emitted %d rows from %d edition(s)", emitted, editions_read)

