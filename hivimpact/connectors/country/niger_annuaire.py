"""
Niger, health yearbook connector: people on antiretroviral treatment by region (to-source,
parse-only, sub-national).

Source: the Niger health ministry publishes a yearly "Annuaire des statistiques sanitaires",
and `scripts/survey_wca_yearbooks.py` cached the 12 editions for 2013 to 2024 from
stat-niger.org into `data/raw/niger/ins`. Every one of the 12 editions carries one table
counting people on antiretroviral treatment at 31 December by prescribing site, health
district and region, citing the national HIV and hepatitis programme (PNLSH) as its source.
This connector reads the eight region total rows and the national total row of that one
table, and nothing else in the yearbook. The PDFs are born-digital, so there is no OCR here.

This connector only PARSES what is already cached. It makes no network request. The survey
script owns discovery and download, and the researcher runs the survey script.

WHICH EDITION OWNS WHICH YEAR
-----------------------------
Each edition reports its own year only, so every year comes from exactly one edition and no
two editions can collide on the duplicate-row key. The editions are read by explicit
allow-list (`_EDITIONS`), keyed by the cached filename. About 120 other PDFs sit in the same
directory (other INS publications, and older yearbooks whose ART table has not been read by
a human), and `fetch` logs one INFO line counting them instead of reading them.

    edition  table         pages     cells  row labels
    2013     Tableau CXI   282       5      bare region names, "Ensemble (Niger)" national
    2014     Tableau 129   315       5      bare region names, "TOTAL NIGER"
    2015     Tableau 126   291-292   5      "Sous total X", "Total Niger"
    2016     Tableau 139   322-323   5      "Sous total X", "TOTAL NIGER"
    2017     Tableau 61    116-117   5      "Région X", "Niger"
    2018     Tableau 72    162-165   5      "Région d'X", "Niger"
    2019     Tableau 109   156-159   5      "Région X", "NIGER"
    2020     Tableau 104   189-194   7      three-line "Total Région / numbers / d'X" rows
    2021     Tableau 118   200-203   7      "Total Région d'X" with a leading site count
    2022     Tableau 110   217-223   4      "Région X", "Niger"
    2023     Tableau 104   174-176   4      "Total Région X", "TOTAL NIGER"
    2024     Tableau 123   201-204   4      "Région X" with a leading site count, "Niger"

Five cells are Homme, Femme, < 15 ans, >= 15 ans and the total. Seven cells are M, F and the
total under 15, M, F and the total 15 and over, and "Enfants & Adultes". Four cells are
19 and under, 20 to 24, 25 and over, and the total. Table numbers are recorded in `extra` as
provenance and never used to find a table, because the numbers change between editions.

PARSING
-------
The table is found by CAPTION TEXT ("Tableau ... Répartition des patients sous ARV ...", with
"par région" on the caption line or the next line), searched within five pages of the page
the caption was read on by hand, then by COLUMN HEADER. The header must name exactly the
bands the edition is mapped to, in the order the cells are read, and the seven-cell header
must print M, F, M, F. A caption whose printed year ("31 décembre YYYY") differs from the
allow-list refuses the edition. The 2021 caption prints no year, so the 2021 edition's year
is checked against the caption page's footer, "Niger 2021".

Numbers are rebuilt from word positions by `_pdf_text.number_readings`, never by
`_pdf_text.columns`. The yearbooks have no empty band between the gap inside a number and
the gap between two cells: the 2020 edition prints Niamey's under-15 total "271" at x 352.8
to 366.5 and the next cell "2 308" as "2" at x 373.2 and "308" at x 380.2, a 6.7-point gap
between cells against thousands gaps of 1.9 to 4.6 points, so `columns()` reads "2712308".
`number_readings` lists every way the words can form whole numbers, and a row is accepted
only when exactly one reading has the number of cells the header promises and satisfies the
row's printed arithmetic.

The word "ARV" printed among the figures (the header's "Total sous ARV" falls onto the 2013
Agadez row, giving "1 ARV 076", and onto the 2019 Diffa row) is dropped before the numbers
are read. Any other word among the figures makes the line unreadable, and a region or
national row that cannot be read refuses the edition.

INTEGRITY GATES (any failure refuses the whole edition with a WARNING naming the reason)
----------------------------------------------------------------------------------------
  * exactly one caption passes the caption, year and header gates;
  * the table ends at a "Source" line within eight pages, and no other "Tableau" caption
    appears before the Source line;
  * exactly eight regions, each found once, and exactly one national row;
  * inside every row the sex cells and the age cells each sum to the row's total;
  * the eight regions sum exactly to the printed national row in every column.

One source defect is allowed, by name. The 2016 edition prints its national total as 15,265,
while the row's own men and women (5,525 + 9,741) and under-15 and 15-and-over (1,003 +
14,263) each sum to 15,266, as do the eight regions. `_KNOWN_DEFECTS` holds that one edition,
that one row and that one-unit gap, so any other failure still refuses. The row is emitted as
printed, 15,265, with `extra["source_defect"]`, and is never adjusted.

WHAT THIS CONNECTOR REFUSES TO EMIT, AND WHY
--------------------------------------------
  * THE 2022 AGE SPLIT. The 2022 edition's age columns hold almost one age profile in every
    site row: over the 72 rows with 50 or more patients, the share aged 19 and under runs
    from 0.078 to 0.098 and the share aged 20 to 24 from 0.091 to 0.105, where the 2023
    edition's same shares run from 0 to 0.404 and from 0 to 0.461. A national ratio applied
    to each site's total produces exactly the 2022 pattern, so only the nine 2022 totals are
    emitted. The 2022 age cells are still read and still have to pass the row and table
    arithmetic.
  * ANY ALL-AGES FIGURE FOR MEN OR WOMEN IN 2020 AND 2021, which those two tables do not
    print. Nothing here is computed that the table does not print.
  * THE SITE AND DISTRICT ROWS, which are read only as lines to skip.
  * The other HIV tables in the yearbooks (PMTCT, TB and HIV, exposed infants, Spectrum
    estimates), recorded in RESUME.md item 46 as deferred or refused.

LABELS
------
`admin1` carries the region names in ASCII without accents (Agadez, Diffa, Dosso, Maradi,
Niamey, Tahoua, Tillaberi, Zinder), following the Cameroon connectors. The document's own
spelling goes into `extra["admin1_source_label"]`. The 2020, 2022 and 2023 editions print
"Mardi" for Maradi, and only those three editions accept the misspelling.

The panel's age labels are reused: under 15 is `0-14` and 15 and over is `15+`. The 2022 to
2024 bands become `0-19`, `20-24` and `25+`, where `0-19` is the yearbook's "≤ 19 ans" band
and is a new label in the panel.

RECONCILIATION
--------------
The national rows equal WHO GHO exactly in seven of 12 years and the Global Fund's reported
result exactly in five of the eight years both report, which is one programme count published
several times and not independent corroboration. `hivimpact/reconcile.py` declares the
`who_gho`, `unaids_aidsinfo` and `global_fund` pairs `derived` for that reason. No other
source in the panel held Niger region counts when this connector was built (checked
2 October 2026).

TAGGING: source_type = routine_programme_record (PNLSH programme reports and DHIS2, per the
tables' own "Source" lines).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from ...connector_base import BaseConnector
from ...schema import AGE_ALL, PanelRow, SourceType
from ._pdf_text import is_number_word, lines as _lines, norm as _norm, number_readings

log = logging.getLogger("hivimpact")

_STAT = "http://stat-niger.org/wp-content/uploads"


def _ed(year: int, url: str, page: int, layout: int, prefix: str, national: Sequence[str], *,
        triplet: Sequence[str] = (), region_sites: bool = False, national_sites: bool = False,
        mardi: bool = False, caption_year: bool = True, totals_only: bool = False) -> Dict:
    """One allow-listed edition. Every field was read off the cached PDF by hand.

    `page` is the 1-based page the caption was read on, used only to centre the search.
    `layout` is the number of cells per row. `prefix` is the normalised word or words that
    open a region row ("" for bare region names). `national` is the set of normalised labels
    the national row may carry. `triplet` names the label lines that open a row printed over
    three text lines. `region_sites` and `national_sites` say whether those rows open with a
    count of sites. `caption_year` is False only where the caption prints no year.
    """
    return {"year": year, "url": url, "page": page, "layout": layout, "prefix": prefix,
            "national": frozenset(national), "triplet": frozenset(triplet),
            "region_sites": region_sites, "national_sites": national_sites, "mardi": mardi,
            "caption_year": caption_year, "totals_only": totals_only}


# -- the allow-list: cached filename -> edition. URLs are as the survey script recorded them.
_EDITIONS: Dict[str, Dict] = {
    "2020_06_Annuaire-statistiques-2013.pdf": _ed(
        2013, "https://www.stat-niger.org/wp-content/uploads/2020/06/"
              "Annuaire-statistiques-2013.pdf",
        282, 5, "", ("ensemble niger",), triplet=("ensemble",)),
    "annuaire_bulletin_annuaire_annuaire_sante_2014.pdf": _ed(
        2014, f"{_STAT}/annuaire_bulletin/annuaire/annuaire_sante_2014.pdf",
        315, 5, "", ("total niger",)),
    "2020_06_Annuaire_Statistiques_2015_DS-MSP.pdf": _ed(
        2015, f"{_STAT}/2020/06/Annuaire_Statistiques_2015_DS-MSP.pdf",
        291, 5, "sous total", ("total niger",)),
    "2020_06_Annuaire_statistiques_2016.pdf": _ed(
        2016, f"{_STAT}/2020/06/Annuaire_statistiques_2016.pdf",
        322, 5, "sous total", ("total niger",)),
    "publication_sectorielle_annuaire_sante_Annuaire_Statistiques_2017_final.pdf": _ed(
        2017, f"{_STAT}/publication_sectorielle/annuaire/sante/"
              "Annuaire_Statistiques_2017_final.pdf",
        116, 5, "region", ("niger",)),
    "publication_sectorielle_annuaire_sante_Annuaire_Statistiques_2018_final.pdf": _ed(
        2018, f"{_STAT}/publication_sectorielle/annuaire/sante/"
              "Annuaire_Statistiques_2018_final.pdf",
        162, 5, "region", ("niger",)),
    "publication_sectorielle_annuaire_sante_MSPPAS_Annuaire_Statistiques_2019_V20092021.pdf": _ed(
        2019, f"{_STAT}/publication_sectorielle/annuaire/sante/"
              "MSPPAS_Annuaire_Statistiques_2019_V20092021.pdf",
        156, 5, "region", ("niger",)),
    "publication_sectorielle_annuaire_sante_MSPPAS_Annuaire_Statistiques_2020_V02032022.pdf": _ed(
        2020, f"{_STAT}/publication_sectorielle/annuaire/sante/"
              "MSPPAS_Annuaire_Statistiques_2020_V02032022.pdf",
        189, 7, "total region", ("total niger",), triplet=("total region", "total"),
        region_sites=True, mardi=True),
    "annuaire_bulletin_annuaire_ministere_sante_Annuaire_2021_23102022.pdf": _ed(
        2021, f"{_STAT}/annuaire_bulletin/annuaire/ministere_sante/Annuaire_2021_23102022.pdf",
        200, 7, "total region", ("total niger",), region_sites=True, national_sites=True,
        caption_year=False),
    "annuaire_bulletin_annuaire_ministere_sante_Annuaire_2022_V09_11_2023.pdf": _ed(
        2022, f"{_STAT}/annuaire_bulletin/annuaire/ministere_sante/Annuaire_2022_V09_11_2023.pdf",
        217, 4, "region", ("niger",), mardi=True, totals_only=True),
    "annuaire_bulletin_annuaire_ministere_sante_Annuaire_Statistiques_Sanitaire_2023.pdf": _ed(
        2023, f"{_STAT}/annuaire_bulletin/annuaire/ministere_sante/"
              "Annuaire_Statistiques_Sanitaire_2023.pdf",
        174, 4, "total region", ("total niger",), mardi=True),
    "annuaire_bulletin_annuaire_ministere_sante_Annuaire_Statistiques_Sanitaire_2024.pdf": _ed(
        2024, f"{_STAT}/annuaire_bulletin/annuaire/ministere_sante/"
              "Annuaire_Statistiques_Sanitaire_2024.pdf",
        201, 4, "region", ("niger",), region_sites=True, national_sites=True),
}

# Normalised region name -> admin1. "mardi" is handled per edition in `_match_place`.
_REGIONS: Dict[str, str] = {
    "agadez": "Agadez",
    "diffa": "Diffa",
    "dosso": "Dosso",
    "maradi": "Maradi",
    "niamey": "Niamey",
    "tahoua": "Tahoua",
    "tillaberi": "Tillaberi",
    "zinder": "Zinder",
}

# -- the three row layouts ------------------------------------------------------------------
# columns: (key, sex, age_group, the header the cell sits under). tokens: the header tokens
# the header must name, no more and no fewer. order: the tokens in the order the cells are
# read, which one header line must print. mf: the M/F sub-header the seven-cell tables print.
_LAYOUTS: Dict[int, Dict] = {
    5: {
        "columns": (("homme", "male", AGE_ALL, "Homme"),
                    ("femme", "female", AGE_ALL, "Femme"),
                    ("moins15", "all", "0-14", "< 15 ans"),
                    ("15plus", "all", "15+", "≥ 15 ans"),
                    ("total", "all", AGE_ALL, "Total sous ARV")),
        "tokens": frozenset({"homme", "femme", "<15", ">=15"}),
        "order": ("homme", "femme", "<15", ">=15"),
        "mf": None,
        "integrity": ("Homme + Femme = Total and < 15 ans + ≥ 15 ans = Total on this row, and the "
                      "eight region rows sum exactly to the printed national row in all five "
                      "columns"),
    },
    7: {
        "columns": (("moins15_m", "male", "0-14", "< 15 ans, M"),
                    ("moins15_f", "female", "0-14", "< 15 ans, F"),
                    ("moins15_total", "all", "0-14", "Total < 15 ans"),
                    ("15plus_m", "male", "15+", "≥ 15 ans, M"),
                    ("15plus_f", "female", "15+", "≥ 15 ans, F"),
                    ("15plus_total", "all", "15+", "Total ≥ 15 ans"),
                    ("total", "all", AGE_ALL, "Enfants & Adultes")),
        "tokens": frozenset({"<15", ">=15", "enfants"}),
        "order": ("<15", ">=15", "enfants"),
        "mf": ("M", "F", "M", "F"),
        "integrity": ("M + F = the band total in both age bands and the two band totals sum to "
                      "Enfants & Adultes on this row, and the eight region rows sum exactly to "
                      "the printed national row in all seven columns"),
    },
    4: {
        "columns": (("19moins", "all", "0-19", "≤ 19 ans"),
                    ("20_24", "all", "20-24", "20-24 ans"),
                    ("25plus", "all", "25+", "25 ans et +"),
                    ("total", "all", AGE_ALL, "Enfants & Adultes")),
        "tokens": frozenset({"<=19", "20-24", ">=25", "enfants"}),
        "order": ("<=19", "20-24", ">=25", "enfants"),
        "mf": None,
        "integrity": ("the three age bands sum to the total on this row, and the eight region "
                      "rows sum exactly to the printed national row in all four columns"),
    },
}


def _residuals(layout: int, c: Sequence[int]) -> Tuple[int, ...]:
    """The row's printed identities as differences, all zero on a row that adds up."""
    if layout == 5:
        h, f, u, o, t = c
        return (h + f - t, u + o - t)
    if layout == 7:
        mu, fu, tu, mo, fo, to, t = c
        return (mu + fu - tu, mo + fo - to, tu + to - t)
    a, b, d, t = c
    return (a + b + d - t,)


# The one source defect allowed, keyed (edition year, admin1) with "" for the national row.
# `residuals` is what `_residuals` returns on the printed row, and `gaps` is the eight regions'
# sum minus the printed national row, column by column. Anything else still refuses.
_KNOWN_DEFECTS: Dict[Tuple[int, str], Dict] = {
    (2016, ""): {"residuals": (1, 1), "gaps": (0, 0, 0, 0, 1)},
}

# -- caption and header ---------------------------------------------------------------------
_CAPTION_KEY = "repartition des patients sous arv"
_TABLE_ID = re.compile(r"^tableau\s*([0-9]+|[ivxlcdm]+)\b")
_DEC_YEAR = re.compile(r"31 decembre (\d{4})")
#: a list-of-tables line ends in its page number after a run of dots
_DOTTED_LEADER = re.compile(r"\.{4,}")
#: pages either side of the hand-read caption page searched first
_CAPTION_WINDOW = 5
#: pages a table may run over before its Source line; the longest, 2022, runs over seven
_MAX_TABLE_PAGES = 8
#: points. The 2013 and 2020 three-line rows step 5.0 to 6.3 points between lines.
_TRIPLET_STEP = 8.0

# Read from a header line lowercased with every space removed, so "≥ 15 ans" and "≥15 ans"
# read alike. "<(?!=)15" keeps "< =19" (the 2024 edition's spelling of "≤ 19") from reading
# as under 15.
_HEADER_TOKEN = re.compile(
    r"homme|femme|<(?!=)15|(?:≥|>=)15|(?:≤|<=)19|20-24|(?:≥|>=)25|25anset\+|enfant")


def _canon(tok: str) -> str:
    if tok in ("homme", "femme", "20-24", "<15"):
        return tok
    if tok == "enfant":
        return "enfants"
    if tok.endswith("15"):
        return ">=15"
    if tok.endswith("19"):
        return "<=19"
    return ">=25"


def _header_tokens(text: str) -> List[str]:
    return [_canon(t) for t in _HEADER_TOKEN.findall(re.sub(r"\s+", "", text.lower()))]


def _dedup(seq: Sequence[str]) -> List[str]:
    out: List[str] = []
    for t in seq:
        if not out or out[-1] != t:
            out.append(t)
    return out


def _contains_run(seq: Sequence[str], run: Sequence[str]) -> bool:
    n = len(run)
    return any(tuple(seq[i:i + n]) == tuple(run) for i in range(len(seq) - n + 1))


class _Refused(Exception):
    """A gate failed. The whole edition is refused, never part of it."""


# -- reading one text line ------------------------------------------------------------------
def _parse_line(ln: Dict, page_no: int) -> Dict:
    """Split a text line into its label words and its number words.

    The label is every word before the first number word. After the first number word, an
    "ARV" is dropped (see the module docstring) and any other word sets `trailing`, which
    makes the line unreadable as a table row.
    """
    label_words: List[Dict] = []
    nums: List[Dict] = []
    trailing = False
    for w in ln["words"]:
        t = w["text"]
        if is_number_word(t):
            nums.append(w)
        elif not nums:
            label_words.append(w)
        elif t.upper() == "ARV":
            continue
        else:
            trailing = True
    raw = " ".join(w["text"] for w in label_words)
    return {"page": page_no, "mid": ln["mid"], "text": ln["text"], "words": ln["words"],
            "raw": raw, "label": _norm(raw), "nums": nums, "trailing": trailing}


def _data_like(p: Dict) -> bool:
    """A line that reads as a table row: three or more digit words and nothing after them."""
    return not p["trailing"] and sum(1 for w in p["nums"] if w["text"].isdigit()) >= 3


def _merge_triplets(parsed: List[Dict], starts: frozenset) -> List[Dict]:
    """Join rows printed over three text lines on one page into one line.

    The 2020 edition prints each region total as "Total Région", the figures on the next
    line, and "d'Agadez" on the line after, and the 2013 national row the same way as
    "Ensemble", the figures, "(Niger)". A merge needs a label line with no figures whose label
    is in `starts`, then a figures line with no label and nothing after the figures, then a
    label line with no figures, each step under `_TRIPLET_STEP` points.
    """
    if not starts:
        return parsed
    out: List[Dict] = []
    i = 0
    while i < len(parsed):
        a = parsed[i]
        if a["label"] in starts and not a["nums"] and i + 2 < len(parsed):
            b, c = parsed[i + 1], parsed[i + 2]
            if (not b["label"] and b["nums"] and not b["trailing"] and c["label"]
                    and not c["nums"] and b["mid"] - a["mid"] < _TRIPLET_STEP
                    and c["mid"] - b["mid"] < _TRIPLET_STEP):
                out.append({**b, "label": f"{a['label']} {c['label']}",
                            "raw": f"{a['raw']} {c['raw']}",
                            "text": f"{a['text']} / {b['text']} / {c['text']}"})
                i += 3
                continue
        out.append(a)
        i += 1
    return out


def _match_place(label: str, cfg: Dict) -> Optional[str]:
    """The admin1 a row label names, "" for the national row, None for any other line."""
    if label in cfg["national"]:
        return ""
    prefix = cfg["prefix"]
    if prefix:
        if not label.startswith(prefix + " "):
            return None
        rest = label[len(prefix) + 1:]
        for infix in ("de ", "d "):
            if rest.startswith(infix):
                rest = rest[len(infix):]
                break
    else:
        rest = label
    if rest == "mardi":
        return "Maradi" if cfg["mardi"] else None
    return _REGIONS.get(rest)


# -- locating the table ---------------------------------------------------------------------
def _header_lines(pdf, cap: Dict) -> List[Dict]:
    """The lines from just below the caption down to the first line that reads as a row."""
    hdr: List[Dict] = []
    last = min(cap["page"] + 1, len(pdf.pages))
    for pno in range(cap["page"], last + 1):
        lns = cap["lines"] if pno == cap["page"] else _lines(pdf.pages[pno - 1])
        start = cap["index"] + 1 if pno == cap["page"] else 0
        for ln in lns[start:]:
            p = _parse_line(ln, pno)
            if _data_like(p):
                return hdr
            hdr.append(p)
    return []


def _header_fault(hdr: List[Dict], layout: int) -> Optional[str]:
    """Why a header does not match the layout the edition is mapped to, or None."""
    if not hdr:
        return "no table row within two pages of the caption"
    spec = _LAYOUTS[layout]
    per_line = [_header_tokens(p["text"]) for p in hdr]
    named = {t for toks in per_line for t in toks}
    if named != spec["tokens"]:
        return (f"the header names {sorted(named)}, where a {layout}-cell table must name "
                f"exactly {sorted(spec['tokens'])}")
    if not any(_contains_run(_dedup(toks), spec["order"]) for toks in per_line):
        return f"no header line prints the bands in the order {list(spec['order'])}"
    if spec["mf"]:
        mf = tuple(w["text"] for p in hdr for w in p["words"] if w["text"] in ("M", "F"))
        if mf != spec["mf"]:
            return f"the sex sub-header reads {list(mf)}, not {list(spec['mf'])}"
    return None


def _find_table(pdf, cfg: Dict, pages: Iterable[int]) -> List[Dict]:
    """Every caption on `pages` that passes the caption, year and header gates."""
    year = cfg["year"]
    found: List[Dict] = []
    for pno in pages:
        lns = _lines(pdf.pages[pno - 1])
        for i, ln in enumerate(lns):
            n = _norm(ln["text"])
            if not n.startswith("tableau") or _CAPTION_KEY not in n:
                continue
            if _DOTTED_LEADER.search(ln["text"]):
                continue
            nxt = _norm(lns[i + 1]["text"]) if i + 1 < len(lns) else ""
            both = f"{n} {nxt}"
            if "par region" not in both:
                continue
            m = _TABLE_ID.match(n)
            cap = {"page": pno, "index": i, "mid": ln["mid"], "text": ln["text"],
                   "table_id": m.group(1).upper() if m else "unnumbered", "lines": lns}
            # The header gate runs before the year rule, so a list-of-tables entry (which
            # prints no year and has no header below it) is set aside instead of refusing
            # the edition. Measured on the 2013 edition, whose page 11 lists the table.
            fault = _header_fault(_header_lines(pdf, cap), cfg["layout"])
            if fault:
                log.info("ne_annuaire: %d edition, caption on page %d set aside, %s",
                         year, pno, fault)
                continue
            printed = [int(y) for y in _DEC_YEAR.findall(both)]
            if any(y != year for y in printed):
                raise _Refused(f"the caption on page {pno} prints 31 December {printed}, but the "
                               f"allow-list calls this file the {year} edition")
            if cfg["caption_year"] and not printed:
                raise _Refused(f"the caption on page {pno} prints no year, where the "
                               f"allow-list expects '31 décembre {year}'")
            if not cfg["caption_year"]:
                page_text = _norm(" ".join(x["text"] for x in lns))
                if f"niger {year}" not in page_text:
                    raise _Refused(f"the caption on page {pno} prints no year and the page "
                                   f"footer does not read 'Niger {year}'")
            found.append(cap)
    return found


def _scan_table(pdf, cap: Dict, cfg: Dict) -> List[Dict]:
    """The table's lines from below the caption to its Source line, triplets merged."""
    rows: List[Dict] = []
    last = min(cap["page"] + _MAX_TABLE_PAGES - 1, len(pdf.pages))
    for pno in range(cap["page"], last + 1):
        lns = cap["lines"] if pno == cap["page"] else _lines(pdf.pages[pno - 1])
        start = cap["index"] + 1 if pno == cap["page"] else 0
        parsed: List[Dict] = []
        for ln in lns[start:]:
            n = _norm(ln["text"])
            if n.startswith("source"):
                rows.extend(_merge_triplets(parsed, cfg["triplet"]))
                return rows
            if n.startswith("tableau"):
                raise _Refused(f"another caption on page {pno} before the table's Source line, "
                               f"{ln['text']!r}")
            parsed.append(_parse_line(ln, pno))
        rows.extend(_merge_triplets(parsed, cfg["triplet"]))
    raise _Refused(f"no Source line within {_MAX_TABLE_PAGES} pages of the caption on page "
                   f"{cap['page']}")


# -- reading the rows -----------------------------------------------------------------------
def _read_row(p: Dict, cfg: Dict, admin1: str) -> Dict:
    """The one reading of a row's number words that satisfies the row's own arithmetic."""
    layout = cfg["layout"]
    keys = [c[0] for c in _LAYOUTS[layout]["columns"]]
    has_sites = cfg["national_sites"] if admin1 == "" else cfg["region_sites"]
    lead = 1 if has_sites else 0
    n = layout + lead
    defect = _KNOWN_DEFECTS.get((cfg["year"], admin1))
    expected = defect["residuals"] if defect else (0,) * len(_residuals(layout, [0] * layout))
    where = f"page {p['page']}, {p['text']!r}"
    try:
        readings = number_readings(p["nums"])
    except ValueError as exc:
        raise _Refused(f"{where}: {exc}")
    passing = [(v, d) for v, d in readings
               if len(v) == n and _residuals(layout, v[-layout:]) == expected]
    if len(passing) != 1:
        raise _Refused(f"{where}: {len(passing)} readings of the figures have {n} numbers and "
                       f"satisfy the row arithmetic, where exactly one must")
    values, dashes = passing[0]
    return {
        "cells": dict(zip(keys, values[-layout:])),
        "sites": values[0] if has_sites else None,
        "site_dash": has_sites and 0 in dashes,
        "dash_columns": [keys[i - lead] for i in dashes if i >= lead],
        "page": p["page"],
        "source_label": p["raw"],
        "residuals": _residuals(layout, values[-layout:]),
    }


def _parse_edition(pdf, cfg: Dict) -> Dict:
    year = cfg["year"]
    npages = len(pdf.pages)
    lo = max(1, cfg["page"] - _CAPTION_WINDOW)
    hi = min(npages, cfg["page"] + _CAPTION_WINDOW)
    caps = _find_table(pdf, cfg, range(lo, hi + 1))
    if not caps:
        log.warning("ne_annuaire: %d edition, no caption passed the gates on pages %d to %d; "
                    "searching the whole document", year, lo, hi)
        caps = _find_table(pdf, cfg, range(1, npages + 1))
    if not caps:
        raise _Refused("no caption in the document passed the caption, year and header gates")
    if len(caps) > 1:
        raise _Refused(f"{len(caps)} captions passed every gate, on pages "
                       f"{[c['page'] for c in caps]}, where exactly one must")
    cap = caps[0]

    places: Dict[str, Dict] = {}
    for p in _scan_table(pdf, cap, cfg):
        if not p["label"]:
            continue
        admin1 = _match_place(p["label"], cfg)
        if admin1 is None:
            continue
        name = admin1 or "the national row"
        if p["trailing"] or not p["nums"]:
            raise _Refused(f"{name} on page {p['page']} does not read as a table row, "
                           f"{p['text']!r}")
        if admin1 in places:
            raise _Refused(f"{name} appears twice, on pages {places[admin1]['page']} and "
                           f"{p['page']}")
        places[admin1] = _read_row(p, cfg, admin1)

    missing = sorted(set(_REGIONS.values()) - set(places))
    if missing:
        raise _Refused(f"region row(s) not found: {missing}")
    if "" not in places:
        raise _Refused("no national row found")

    keys = [c[0] for c in _LAYOUTS[cfg["layout"]]["columns"]]
    regions = [r for r in places if r]
    gaps = tuple(sum(places[r]["cells"][k] for r in regions) - places[""]["cells"][k]
                 for k in keys)
    defect = _KNOWN_DEFECTS.get((year, ""))
    expected = defect["gaps"] if defect else (0,) * len(keys)
    if gaps != expected:
        raise _Refused(f"the eight regions minus the printed national row give "
                       f"{dict(zip(keys, gaps))}, where {dict(zip(keys, expected))} is required")
    nat = places[""]["cells"]["total"]
    log.info("ne_annuaire: %d edition, Tableau %s on page %d, eight regions tie to the printed "
             "national row (%s on ART)", year, cap["table_id"], cap["page"], f"{nat:,}")
    return {"places": places, "table_id": cap["table_id"], "caption": cap["text"],
            "caption_page": cap["page"], "gaps": dict(zip(keys, gaps))}


class NigerAnnuaireConnector(BaseConnector):
    """Niger health yearbooks: people on ART at 31 December by region, 2013 to 2024.

    Parse-only by design: `scripts/survey_wca_yearbooks.py` discovers and downloads the
    yearbooks, and this connector reads what is already in `raw_dir`.
    """

    source_id = "ne_annuaire"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Niger health yearbook (Annuaire des statistiques sanitaires): people on ART "
                   "at 31 December by region and nationally, by sex and age band, 2013 to 2024 "
                   "(to-source, parse-only).")
    country = "NER"

    def __init__(self, raw_dir: str = "data/raw/niger/ins", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- emission ---------------------------------------------------------------------------
    def _rows(self, path: Path, cfg: Dict, table: Dict) -> Iterator[PanelRow]:
        year, url, layout = cfg["year"], cfg["url"], cfg["layout"]
        spec = _LAYOUTS[layout]
        code = f"annuaire.{year}.tableau{table['table_id'].lower()}"
        defect = _KNOWN_DEFECTS.get((year, ""))
        order = sorted(r for r in table["places"] if r) + [""]
        for admin1 in order:
            rec = table["places"][admin1]
            for key, sex, age, header in spec["columns"]:
                if cfg["totals_only"] and key != "total":
                    continue
                extra: Dict = {
                    "edition": path.name,
                    "edition_year": year,
                    "table": f"Tableau {table['table_id']}",
                    "page": rec["page"],
                    "caption": table["caption"],
                    "caption_page": table["caption_page"],
                    "extraction": ("text layer, caption- and header-anchored; numbers rebuilt "
                                   "from word positions and accepted only as the one reading "
                                   "that satisfies the row's printed arithmetic"),
                    "admin1_source_label": rec["source_label"],
                    "column": key,
                    "column_header": header,
                    "integrity": spec["integrity"],
                }
                if rec["sites"] is not None:
                    extra["sites"] = rec["sites"]
                if rec["dash_columns"]:
                    extra["printed_dash_read_as_zero"] = rec["dash_columns"]
                if admin1:
                    extra["reconcile_with"] = (
                        "none; no other source in the panel held Niger region counts when this "
                        "connector was built (checked 2 October 2026)")
                else:
                    extra["reconcile_with"] = (
                        "who_gho, unaids_aidsinfo and global_fund national on-ART counts, "
                        "declared derived in reconcile.DECLARED_RELATIONSHIPS because the "
                        "matches are the national programme's one count published several times")
                if defect and admin1 == "":
                    c = rec["cells"]
                    extra["integrity"] = (
                        "the eight region rows sum exactly to the printed national row in four "
                        "of five columns; the printed national total is the one exception, "
                        "allowed by name in _KNOWN_DEFECTS")
                    extra["source_defect"] = (
                        f"the printed national total, {c['total']:,}, is one below the row's own "
                        f"Homme + Femme ({c['homme']:,} + {c['femme']:,} = "
                        f"{c['homme'] + c['femme']:,}), one below its < 15 ans + ≥ 15 ans "
                        f"({c['moins15']:,} + {c['15plus']:,} = {c['moins15'] + c['15plus']:,}) "
                        f"and one below the eight regions' sum; emitted as printed and not "
                        f"adjusted")
                elif defect:
                    extra["integrity"] = (
                        spec["integrity"].replace(
                            "sum exactly to the printed national row in all five columns",
                            "sum exactly to the printed national row in four of five columns, "
                            "the printed national total being one below the regions' sum "
                            "(a source defect recorded on the national row)"))
                notes: List[str] = []
                if cfg["totals_only"]:
                    notes.append(
                        "only the total is emitted from the 2022 edition; the 2022 age columns "
                        "hold almost one age profile in every site row, the pattern of a "
                        "national ratio applied to each site's total, so the age split is "
                        "refused (RESUME.md item 46)")
                if age == "0-19":
                    notes.append("age_group 0-19 is the yearbook's '≤ 19 ans' band")
                if layout == 7 and key == "total":
                    notes.append("the table prints no all-ages figure for men or for women, so "
                                 "none is emitted")
                if not cfg["caption_year"]:
                    notes.append("the caption prints no year; the edition year was checked "
                                 f"against the caption page's footer, 'Niger {year}'")
                if notes:
                    extra["note"] = "; ".join(notes)
                yield self.make_row(
                    country_iso3="NER", country_name="Niger",
                    indicator_id="on_art_count", year=year, value=rec["cells"][key],
                    unit="count", admin1=admin1, sex=sex, age_group=age,
                    source_url=url, source_indicator_code=f"{code}.{key}", extra=extra,
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
            log.error("ne_annuaire: pdfplumber not installed (pip install pdfplumber)")
            return
        if not self.raw_dir.exists():
            log.warning("ne_annuaire: %s does not exist; run scripts/survey_wca_yearbooks.py to "
                        "cache the Niger yearbooks", self.raw_dir)
            return

        present = {p.name for p in self.raw_dir.glob("*.pdf")}
        others = present - set(_EDITIONS)
        if others:
            log.info("ne_annuaire: %d other PDF(s) in %s are not on the edition allow-list and "
                     "are not read (other INS publications, and yearbooks whose ART table has "
                     "not been read by a human)", len(others), self.raw_dir)

        emitted = 0
        editions_read = 0
        for name, cfg in sorted(_EDITIONS.items(), key=lambda kv: kv[1]["year"]):
            year = cfg["year"]
            if year < start_year or year > end_year:
                continue
            if name not in present:
                log.warning("ne_annuaire: %s, the %d edition, is not in %s; nothing emitted for "
                            "%d", name, year, self.raw_dir, year)
                continue
            path = self.raw_dir / name
            try:
                with pdfplumber.open(str(path)) as pdf:
                    table = _parse_edition(pdf, cfg)
            except _Refused as exc:
                log.warning("ne_annuaire: %s refused, nothing emitted for %d, because %s",
                            name, year, exc)
                continue
            except Exception as exc:
                log.warning("ne_annuaire: %s failed to parse (%s), nothing emitted for %d",
                            name, exc, year)
                continue
            editions_read += 1
            for row in self._rows(path, cfg, table):
                emitted += 1
                yield row

        log.info("ne_annuaire: emitted %d rows from %d edition(s)", emitted, editions_read)
