"""
Guinea, statistical yearbook connector: HIV-positive pregnant women who received ARVs, by region,
2022 to 2024 (to-source, parse-only, sub-national).

Source: Guinea's national statistics institute (INS) publishes a general statistical yearbook,
the Annuaire statistique, and Jason's survey cached the editions in `data/raw/guinea/ins`. The
health chapter carries a table headed "Nombre de femmes enceintes infectées par le VIH ayant reçu
des ARV par région", with one row for each of the eight regions, a Guinée row, and one column for
every year since 2014. The tables cite "BSD Santé/SNIS/Ministère de la Santé", the health
ministry's statistics office and health information system. The PDFs are born-digital, so there
is no OCR here.

This connector only PARSES what is already cached. It makes no network request.

WHICH EDITION OWNS WHICH YEAR
-----------------------------
Two editions are on the allow-list (`_EDITIONS`), keyed by the cached filename.

    edition  table          page  year columns  role
    2024     Tableau 12.14  171   2014 to 2024  emits 2022, 2023 and 2024
    2022     Tableau 7.19   145   2014 to 2022  cross-checks the 2022 column, emits nothing

The 2024 edition's cover reads "Annuaire statistique 2024, Octobre 2025", while some of the
edition's page footers, page 171 among them, still read "Annuaire statistique 2022 de l'INS".
The footers are a template left over from the earlier edition, so the edition is identified by
its filename and its year header and never by a footer.

WHAT THIS CONNECTOR REFUSES TO EMIT, AND WHY (RESUME.md item 47)
----------------------------------------------------------------
Every year from 2014 to 2021. The 2017 to 2021 values are impossible as counts of women: the
yearbook prints 22,590 women on ARVs for 2018, four and a half times the 5,070 pregnant women the
same yearbook counts as testing HIV positive that year, against an estimated 5,900 to 6,300
pregnant women living with HIV in every year from 2014 to 2021. The 2017 edition prints Kindia's
2014 figure as 297 where every later edition prints 927, and each edition's own total matches
its own regions, so a 630-woman error passes every arithmetic gate. The 2018 to 2021 editions
cite the national PMTCT programme (PNPCSP) and the 2022 and 2024 editions cite the health
information system, and the 2020 column prints "nd". A series joined across 2021 and 2022 would
show PMTCT collapsing by 87 per cent inside the funding-cuts window when the fall marks a change
of source, so the whole PNPCSP series is refused together. The 2014 to 2021 cells are still read,
to place every column, and never emitted.

Also refused: the testing tables 12.12 and 12.13, which carry no definitions, and the reprinted
DHS prevalence tables, which the panel's `dhs` source already holds.

PARSING
-------
The table is found by CAPTION TEXT, and the line below the caption must be the year header,
reading "Région" and then exactly the edition's years in order. Every line between the year
header and the table's "Source" line must be one of the nine expected rows, so an extra row, a
wrapped label or a footnote refuses the edition.

Cells are delimited on the gap between words, as `_pdf_text.columns` does. Unlike the Niger
yearbooks, these two tables have a clean empty band between the gap inside a number and the gap
between cells: thousands gaps measured 2.5 points in the 2024 table (n=38) and 2.6 points in the
2022 table (n=30), and gaps between cells measured 12.7 to 30.9 and 17.3 to 35.7 points (n=90 and
n=72), measured 2 October 2026. The 10-point default sits inside that band. The tables print
some thousands with a space and some without ("1 659" and "1169" in one row), which the join
handles either way. Each cell is then placed under a year by its right edge, which must lie
nearer to its own year header's right edge than to any other, so a cell cannot slide into the
neighbouring year unnoticed.

"nd" (non disponible, not available) is read as missing and NEVER as zero.

INTEGRITY GATES
---------------
  * exactly one caption in the document passes the caption and year-header gates;
  * exactly eight regions, each found once, and one Guinée row, and nothing else;
  * every row has one cell under each year header, and no cell sits nearer another header;
  * no "nd" in 2022, 2023 or 2024;
  * the eight regions sum exactly to the Guinée row in each of 2022, 2023 and 2024;
  * the 2022 column of the 2022 edition equals the 2022 column of the 2024 edition in all nine
    rows. Where the 2022 edition is missing, refused or different, the 2022 rows are refused and
    the 2023 and 2024 rows are still emitted.

Any failure in the 2024 edition refuses everything, with a WARNING naming the reason.

LABELS
------
`admin1` carries the region names in ASCII without accents (Boke, Conakry, Faranah, Kankan,
Kindia, Labe, Mamou, Nzerekore), and the document's own spelling goes into
`extra["admin1_source_label"]`. The indicator is `pmtct_arv_count` with population group, sex and
age group all `all`, as every existing `pmtct_arv_count` row in the panel is labelled.

RECONCILIATION
--------------
The 2023 national figure, 3,802, equals UNAIDS and WHO GHO exactly, and WHO GHO equals UNAIDS in
every Guinea year, so `hivimpact/reconcile.py` declares the `unaids_aidsinfo` and `who_gho` pairs
`derived`. The 2024 figure sits 16 per cent above UNAIDS and is recorded in RESUME.md item 47 as
a finding. The Global Fund's reported results match the yearbook in no year and are left
undeclared. No other source in the panel held Guinea region rows when this connector was built
(checked 2 October 2026).

TAGGING: source_type = routine_programme_record (the health information system, per the table's
own "Source" line).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
from ._pdf_text import COL_GAP, lines as _lines, norm as _norm

log = logging.getLogger("hivimpact")

_URL = "https://www.stat-guinee.org/images/Documents/Publications/INS/annuelles/annuaire/"

# -- the allow-list: cached filename -> edition. `page` is the 1-based page the caption was read
# on by hand, recorded as provenance and used only to report where the table was found.
_EDITIONS: Dict[str, Dict] = {
    "images_Documents_Publications_INS_annuelles_annuaire_Annuaire_Statistique_2024_INS_VF1.pdf": {
        "edition_year": 2024, "url": f"{_URL}Annuaire_Statistique_2024_INS_VF1.pdf", "page": 171,
        "years": tuple(range(2014, 2025)), "role": "read",
    },
    "images_Documents_Publications_INS_annuelles_annuaire_Annuaire_Statistique_2022_VF_INS.pdf": {
        "edition_year": 2022, "url": f"{_URL}Annuaire_Statistique_2022_VF_INS.pdf", "page": 145,
        "years": tuple(range(2014, 2023)), "role": "check",
    },
}

#: the years emitted, all from the "read" edition
_KEEP_YEARS: Tuple[int, ...] = (2022, 2023, 2024)
#: the year the "check" edition must print identically in all nine rows
_CHECK_YEAR = 2022

# Normalised row label -> admin1, "" for the national row. `norm` turns the apostrophe in
# "N'Zérékoré" into a space.
_ROWS: Dict[str, str] = {
    "boke": "Boke",
    "conakry": "Conakry",
    "faranah": "Faranah",
    "kankan": "Kankan",
    "kindia": "Kindia",
    "labe": "Labe",
    "mamou": "Mamou",
    "n zerekore": "Nzerekore",
    "guinee": "",
}

_CAPTION_KEY = "nombre de femmes enceintes infectees par le vih ayant recu des arv par region"
_TABLE_ID = re.compile(r"^tableau (\d+) (\d+)\b")
_CELL = re.compile(r"^(\d+|nd)$")
_LABEL_WORD = re.compile(r"[^\W\d_]", re.UNICODE)


class _Refused(Exception):
    """A gate failed. The whole edition is refused, never part of it."""


def _year_header(ln: Dict, years: Tuple[int, ...]) -> Optional[List[Dict]]:
    """The year words of a "Région 2014 ... 2024" line, or None when the line is not that."""
    ws = ln["words"]
    if not ws or _norm(ws[0]["text"]) not in ("region", "regions"):
        return None
    rest = ws[1:]
    if [w["text"] for w in rest] != [str(y) for y in years]:
        return None
    return rest


def _row_cells(ln: Dict, hdr: List[Dict],
               years: Tuple[int, ...]) -> Tuple[str, Dict[int, Optional[int]], float]:
    """Split a row into its label and one cell per year, placed by right edge.

    Returns the raw label, {year: value or None for "nd"} and the largest distance between a
    cell's right edge and its year header's right edge, kept for the log.
    """
    words = ln["words"]
    k = 0
    while k < len(words) and not _CELL.match(words[k]["text"]):
        k += 1
    label_words, cell_words = words[:k], words[k:]
    raw = " ".join(w["text"] for w in label_words)
    if not label_words or not all(_LABEL_WORD.search(w["text"]) for w in label_words):
        raise _Refused(f"the line {ln['text']!r} has no row label")
    for w in cell_words:
        if not _CELL.match(w["text"]):
            raise _Refused(f"the row {raw!r} carries {w['text']!r} among its cells")
    # Group the cell words on the measured gap, as `columns()` does, keeping each group's words
    # so the group's right edge can be placed under a year header. Digit words in one group are
    # joined with no separator ("1" + "659" -> "1659"); a group mixing "nd" with digits keeps a
    # space and is refused below.
    groups: List[List[Dict]] = []
    for w in cell_words:
        if groups and (w["x0"] - groups[-1][-1]["x1"]) < COL_GAP:
            groups[-1].append(w)
        else:
            groups.append([w])
    texts = ["".join(w["text"] for w in g) if all(w["text"].isdigit() for w in g)
             else " ".join(w["text"] for w in g) for g in groups]
    if len(texts) != len(years):
        raise _Refused(f"the row {raw!r} has {len(texts)} cells under {len(years)} year headers")
    cells: Dict[int, Optional[int]] = {}
    worst = 0.0
    hdr_x1 = [h["x1"] for h in hdr]
    for i, (text, grp) in enumerate(zip(texts, groups)):
        x1 = grp[-1]["x1"]
        nearest = min(range(len(hdr_x1)), key=lambda j: abs(x1 - hdr_x1[j]))
        if nearest != i:
            raise _Refused(f"the row {raw!r} cell {text!r} sits nearer the {years[nearest]} header "
                           f"than its own {years[i]} header")
        worst = max(worst, abs(x1 - hdr_x1[i]))
        if text == "nd":
            cells[years[i]] = None
        elif text.isdigit():
            cells[years[i]] = int(text)
        else:
            raise _Refused(f"the row {raw!r} cell {text!r} under {years[i]} is not a count or 'nd'")
    return raw, cells, worst


def _parse_edition(pdf, cfg: Dict) -> Dict:
    """Find the one table in the edition and read its nine rows."""
    years = cfg["years"]
    found = []
    for pno in range(1, len(pdf.pages) + 1):
        lns = _lines(pdf.pages[pno - 1])
        for i, ln in enumerate(lns):
            n = _norm(ln["text"])
            if not n.startswith("tableau") or _CAPTION_KEY not in n:
                continue
            hdr = _year_header(lns[i + 1], years) if i + 1 < len(lns) else None
            if hdr is None:
                log.info("gn_annuaire: %d edition, caption on page %d set aside, the next line "
                         "is not a year header reading 'Région' and %d to %d", cfg["edition_year"],
                         pno, years[0], years[-1])
                continue
            found.append((pno, i, lns, hdr))
    if len(found) != 1:
        raise _Refused(f"{len(found)} captions passed the caption and year-header gates, on pages "
                       f"{[f[0] for f in found]}, where exactly one must")
    pno, i, lns, hdr = found[0]
    caption = lns[i]["text"]
    m = _TABLE_ID.match(_norm(caption))
    table_id = f"{m.group(1)}.{m.group(2)}" if m else "unnumbered"

    rows: Dict[str, Dict] = {}
    source_line = None
    worst = 0.0
    for ln in lns[i + 2:]:
        n = _norm(ln["text"])
        if n.startswith("source"):
            source_line = ln["text"]
            break
        raw, cells, off = _row_cells(ln, hdr, years)
        key = _norm(raw)
        if key not in _ROWS:
            raise _Refused(f"the row {raw!r} on page {pno} is not one of the nine expected rows")
        admin1 = _ROWS[key]
        if admin1 in rows:
            raise _Refused(f"the row {raw!r} appears twice")
        rows[admin1] = {"source_label": raw, "cells": cells}
        worst = max(worst, off)
    if source_line is None:
        raise _Refused(f"no Source line below the table on page {pno}")
    missing = sorted(a or "Guinée" for a in _ROWS.values() if a not in rows)
    if missing:
        raise _Refused(f"row(s) not found: {missing}")
    log.info("gn_annuaire: %d edition, Tableau %s on page %d, nine rows read, cells within %.1f "
             "points of their year headers", cfg["edition_year"], table_id, pno, worst)
    return {"rows": rows, "table_id": table_id, "page": pno, "caption": caption,
            "source_line": source_line}


def _check_years(table: Dict, years: Iterable[int], edition_year: int) -> None:
    """No "nd" in the years kept, and the eight regions sum to the Guinée row in each year."""
    rows = table["rows"]
    for y in years:
        nd = [a or "Guinée" for a, r in rows.items() if r["cells"][y] is None]
        if nd:
            raise _Refused(f"the {edition_year} edition prints 'nd' for {y} in {sorted(nd)}")
        regions = sum(r["cells"][y] for a, r in rows.items() if a)
        national = rows[""]["cells"][y]
        if regions != national:
            raise _Refused(f"the eight regions sum to {regions:,} in {y}, where the Guinée row "
                           f"prints {national:,}")


class GuineaAnnuaireConnector(BaseConnector):
    """Guinea INS statistical yearbook: pregnant women receiving ARVs by region, 2022 to 2024.

    Parse-only by design: the survey cached the yearbooks, and this connector reads what is
    already in `raw_dir`.
    """

    source_id = "gn_annuaire"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Guinea INS statistical yearbook (Annuaire statistique): HIV-positive pregnant "
                   "women who received ARVs, by region and nationally, 2022 to 2024 "
                   "(to-source, parse-only).")
    country = "GIN"

    def __init__(self, raw_dir: str = "data/raw/guinea/ins", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _read(self, pdfplumber, name: str, cfg: Dict) -> Optional[Dict]:
        path = self.raw_dir / name
        if not path.exists():
            log.warning("gn_annuaire: %s, the %d edition, is not in %s", name,
                        cfg["edition_year"], self.raw_dir)
            return None
        try:
            with pdfplumber.open(str(path)) as pdf:
                return _parse_edition(pdf, cfg)
        except _Refused as exc:
            log.warning("gn_annuaire: %s refused because %s", name, exc)
        except Exception as exc:
            log.warning("gn_annuaire: %s failed to parse (%s)", name, exc)
        return None

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
        years = [y for y in _KEEP_YEARS if start_year <= y <= end_year]
        if not years:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("gn_annuaire: pdfplumber not installed (pip install pdfplumber)")
            return
        if not self.raw_dir.exists():
            log.warning("gn_annuaire: %s does not exist; the Guinea yearbooks are not cached",
                        self.raw_dir)
            return

        others = {p.name for p in self.raw_dir.glob("*.pdf")} - set(_EDITIONS)
        if others:
            log.info("gn_annuaire: %d other PDF(s) in %s are not on the edition allow-list and are "
                     "not read", len(others), self.raw_dir)

        (read_name, read_cfg), = [(n, c) for n, c in _EDITIONS.items() if c["role"] == "read"]
        (check_name, check_cfg), = [(n, c) for n, c in _EDITIONS.items() if c["role"] == "check"]

        table = self._read(pdfplumber, read_name, read_cfg)
        if table is None:
            log.warning("gn_annuaire: nothing emitted, the %d edition was not read",
                        read_cfg["edition_year"])
            return
        try:
            _check_years(table, _KEEP_YEARS, read_cfg["edition_year"])
        except _Refused as exc:
            log.warning("gn_annuaire: %s refused because %s; nothing emitted", read_name, exc)
            return

        cross_check = None
        if _CHECK_YEAR in years:
            check = self._read(pdfplumber, check_name, check_cfg)
            if check is not None:
                try:
                    _check_years(check, (_CHECK_YEAR,), check_cfg["edition_year"])
                    diff = {a or "Guinée": (check["rows"][a]["cells"][_CHECK_YEAR],
                                            table["rows"][a]["cells"][_CHECK_YEAR])
                            for a in _ROWS.values()
                            if check["rows"][a]["cells"][_CHECK_YEAR]
                            != table["rows"][a]["cells"][_CHECK_YEAR]}
                    if diff:
                        raise _Refused(f"the two editions print different {_CHECK_YEAR} figures, "
                                       f"(2022 edition, 2024 edition) = {diff}")
                    cross_check = (f"equals the {check_cfg['edition_year']} edition's Tableau "
                                   f"{check['table_id']} (page {check['page']}) in all nine rows "
                                   f"for {_CHECK_YEAR}")
                except _Refused as exc:
                    log.warning("gn_annuaire: %s cross-check failed because %s", check_name, exc)
            if cross_check is None:
                log.warning("gn_annuaire: the %d rows are refused, because the %d edition could "
                            "not confirm them", _CHECK_YEAR, check_cfg["edition_year"])
                years = [y for y in years if y != _CHECK_YEAR]

        emitted = 0
        order = sorted(a for a in table["rows"] if a) + [""]
        for y in years:
            for admin1 in order:
                rec = table["rows"][admin1]
                extra: Dict = {
                    "edition": read_name,
                    "edition_year": read_cfg["edition_year"],
                    "table": f"Tableau {table['table_id']}",
                    "page": table["page"],
                    "caption": table["caption"],
                    "source_line": table["source_line"],
                    "extraction": ("text layer, caption- and year-header-anchored; cells split on "
                                   "the measured gap between words and placed under a year by "
                                   "right edge"),
                    "admin1_source_label": rec["source_label"],
                    "column": str(y),
                    "integrity": ("the eight region rows sum exactly to the Guinée row in each of "
                                  "2022, 2023 and 2024, and no kept cell prints 'nd'"),
                    "note": ("2014 to 2021 are refused as one series (the PNPCSP figures, "
                             "RESUME.md item 47); 2022 to 2024 come from the health information "
                             "system"),
                }
                if y == _CHECK_YEAR:
                    extra["cross_check"] = cross_check
                if admin1:
                    extra["reconcile_with"] = (
                        "none; no other source in the panel held Guinea region rows when this "
                        "connector was built (checked 2 October 2026)")
                else:
                    extra["reconcile_with"] = (
                        "unaids_aidsinfo and who_gho national counts, declared derived in "
                        "reconcile.DECLARED_RELATIONSHIPS because the 2023 figure equals both "
                        "exactly; global_fund matches in no year and is left undeclared")
                yield self.make_row(
                    country_iso3="GIN", country_name="Guinea",
                    indicator_id="pmtct_arv_count", year=y, value=rec["cells"][y],
                    unit="count", admin1=admin1,
                    source_url=read_cfg["url"],
                    source_indicator_code=f"annuaire.{read_cfg['edition_year']}."
                                          f"tableau{table['table_id']}.{y}",
                    extra=extra,
                )
                emitted += 1
        log.info("gn_annuaire: emitted %d rows for %s", emitted, ", ".join(map(str, years)))
