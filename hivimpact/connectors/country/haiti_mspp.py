"""
Haiti, MSPP annual statistical reports: notified HIV cases by department, 2020 to 2023
(to-source, routine programme, sub-national).

Source: Haiti's Ministry of Public Health and Population (MSPP, Ministère de la Santé Publique
et de la Population) publishes an annual statistical report, the Rapport Statistique, at
www.mspp.gouv.ht. The HIV section of each report carries a positivity table headed "Taux de
séropositivité par département géographique", with one row for each of Haiti's ten
departments, a TOTAL row and three columns: people tested who know the result, people who
tested HIV positive and know the result, and the positivity rate. The source line under the
table names the national AIDS programme (MSPP-PNLS, Programme National de Lutte contre le
VIH/SIDA) and the MESI reporting site (www.mesi.ht), and from 2022 also SALVH. The PDFs are
born-digital, so there is no OCR here.

The four reports are downloaded once into `raw_dir` and read from the cached copies after
that. A cached copy whose size or sha256 differs from the copy read on 8 October 2026 is
logged as a WARNING and still parsed, because every gate below runs on the table itself.

    report  table        PDF page  people tested  HIV positive
    2020    Tableau 45   81        547,694        18,666
    2021    Tableau 42   69        415,602        14,695
    2022    Tableau 50   80        404,843        11,973
    2023    Tableau 53   94        411,497        13,940

WHAT THE COUNT IS, AND WHY THE INDICATOR IS notified_hiv_cases
---------------------------------------------------------------
The emitted value is the HIV-positive column: people the ministry counts as testing HIV
positive in the report year and knowing the result. Jason ruled on 8 October 2026 that a
ministry's own count of HIV cases goes under `notified_hiv_cases` and is never merged with or
compared to `new_diagnoses`, which holds the donor programme counts of positive test results
(research/phase5_lac/lac_round1_notes.md, section r2s and the ruling of 8 October 2026). The
people-tested column and the printed rate travel in `extra` and are not emitted as rows.

THE 2022 SERIES BREAK
---------------------
The 2022 report states, above Tableau 50, that the 2022 count of HIV-positive people was
deduplicated with a matching algorithm, so the 2022 figures count unique people. The same
report attributes the fall in new ARV enrolments from 14,622 in 2021 to 11,873 in 2022 to the
removal of duplicates. The 2020 and 2021 reports say nothing about deduplication, and the 2022
report explains the lower 2022 positivity by the new deduplication, so the 2020 and 2021
counts are read as including duplicates. The 2023 report says nothing about deduplication and
prints the same source line as the 2022 report, so whether the 2023 count is deduplicated is
NOT VERIFIED. Every row carries `extra.deduplication` and `extra.series_break`, and the fall
from 14,695 cases in 2021 to 11,973 in 2022 must not be read as a fall in diagnoses.

THE 2020 HEADER
---------------
The 2020 table prints the case header first and the people-tested header second, while the
numbers print people tested first. The column meaning is therefore never taken from the
printed header. Each row's printed rate must equal the smaller count over the larger to one
decimal, and that arithmetic decides which column holds the cases, in every edition. The 2020
rows carry `extra.header_note`.

PARSING
-------
The table is found by CAPTION TEXT. A caption is a line starting "Taux de séropositivité par
département géographique" directly below a line reading only "Tableau N", which leaves the
table of contents out because the contents lines start with "Tableau". The caption may end in
"en YYYY", and the line below the caption must read "MSPP, Année YYYY", with both years equal
to the report year. The header lines between that line and the first department row must
contain the words the report printed when the connector was built (`header_words`), and at
most 12 header lines are allowed.

Cells are delimited on the gap between words, as `_pdf_text.columns` does. Thousands gaps in
these four tables measured about 3 points and gaps between columns 28 points or more, measured
13 October 2026, so the 10-point default sits in the empty range between the two. The tables
print some thousands with a space and some without ("10756" and "4758"), which the join
handles either way. A count printed in several words must look like a thousands grouping, one
to three digits followed by groups of exactly three.

INTEGRITY GATES
---------------
  * exactly one caption in the report passes the caption gate, and the year lines agree;
  * every line from the first department row to the TOTAL row is one of the ten departments
    or the TOTAL row, each found exactly once, with exactly three columns;
  * in every row, including TOTAL, the larger count exceeds the smaller and the printed rate
    equals 100 times the smaller over the larger within 0.05, with the same column order in
    every row;
  * the ten departments sum exactly to the TOTAL row in people tested and in cases.

Any failed gate refuses the whole report with a WARNING naming the reason, and the other
reports are still read. A TOTAL row that differs from the figures in the table above is logged
as a WARNING and still emitted, since the gates have passed. The 2021 table prints no source
line, so `extra.source_line` is None for 2021.

LABELS
------
`admin1` carries the department names the panel already uses for Haiti (Artibonite, Centre,
Grande-Anse, Nippes, Nord, Nord-Est, Nord-Ouest, Ouest, Sud, Sud-Est), and the report's own
spelling ("Grande Anse" in the 2021 table) goes into `extra.admin1_source_label`. The TOTAL row is the national row, admin1 "".

RECONCILIATION
--------------
No other source in the panel held Haiti `notified_hiv_cases` rows when this connector was
built (checked 13 October 2026), and `paho_core` holds no Haiti row. The `new_diagnoses` rows
of pepfar_snu, pepfar_modality, pepfar_panorama and global_fund count positive test results
under donor definitions and are never compared. The PAHO HIV dashboard shows Haiti for 2018 to
2024 outside the panel, and the research notes record a dashboard figure of 13,940 for 2021,
equal to this connector's 2023 count, so whether the dashboard years align with the report
years is NOT VERIFIED.

TAGGING: source_type = routine_programme_record (the ministry's programme reporting, per the
tables' own source lines).
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

_URL = "https://www.mspp.gouv.ht/sites/default/files/publications/"

_NOTES = "research/phase5_lac/lac_round1_notes.md, section r2s"

_DEDUP_BEFORE = ("not deduplicated. The 2020 and 2021 reports say nothing about deduplication, "
                 "and the 2022 report explains the lower 2022 positivity by the new "
                 "deduplication of the 2022 count, so the 2020 and 2021 counts include people "
                 "counted more than once")

# -- the allow-list: report year -> edition. `known` is (size, sha256 prefix) of the copy read on
# 8 October 2026. `page` is the 1-based page the table was read on by hand, kept as provenance.
# `total` is (people tested, HIV positive) on the TOTAL row, checked as a fingerprint only.
_EDITIONS: Dict[int, Dict] = {
    2020: {
        "file": "Rapport%20Statistique%20MSPP%202020.pdf",
        "local": "rapport_statistique_mspp_2020.pdf",
        "known": (3_060_944, "a68eb34c8850"), "table": "45", "page": 81,
        "total": (547_694, 18_666),
        "header_words": ("cas", "diagnostiques", "notifies", "realise", "test", "connaissent",
                         "seropositivite"),
        "deduplication": _DEDUP_BEFORE,
        "header_note": ("The 2020 table prints the case header ('Cas VIH diagnostiqués et "
                        "notifiés') first and the people-tested header second, while the numbers "
                        "print people tested first. The column meaning here comes from the "
                        "arithmetic, the printed rate equals the second number over the first in "
                        "every row, and the research check of 8 October 2026 found the first "
                        "column equal to the totals of Tableau 44, the 2020 testing table "
                        f"({_NOTES})."),
    },
    2021: {
        "file": "Rapport%20Statistique%20MSPP%202021_web.pdf",
        "local": "rapport_statistique_mspp_2021.pdf",
        "known": (2_756_588, "f73f1df895a6"), "table": "42", "page": 69,
        "total": (415_602, 14_695),
        "header_words": ("nombre", "personnes", "testees", "connaissent", "statut",
                         "seropositivite"),
        "deduplication": _DEDUP_BEFORE,
    },
    2022: {
        "file": "Rapport%20Statistique%20MSPP%202022.pdf",
        "local": "rapport_statistique_mspp_2022.pdf",
        "known": (2_299_058, "94412fa46f06"), "table": "50", "page": 80,
        "total": (404_843, 11_973),
        "header_words": ("nombre", "personnes", "testees", "connaissent", "statut",
                         "seropositivite"),
        "deduplication": ("deduplicated. The 2022 report states above Tableau 50 that the count "
                          "of HIV-positive people was deduplicated with an algorithm matching "
                          "people seen at more than one testing site, so the 2022 count is of "
                          "unique people"),
    },
    2023: {
        "file": "Rapport%20Statistique%20MSPP%202023_web.pdf",
        "local": "rapport_statistique_mspp_2023.pdf",
        "known": (1_821_690, "f8db4c6609a3"), "table": "53", "page": 94,
        "total": (411_497, 13_940),
        "header_words": ("total", "personnes", "testees", "statut", "connu", "seropositivite"),
        "deduplication": ("NOT VERIFIED. The 2023 report says nothing about deduplication, and "
                          "prints the same source line as the 2022 report (MSPP-PNLS, SALVH et "
                          "www.mesi.ht)"),
    },
}

#: Normalised row label -> admin1, "" for the national TOTAL row.
_ROWS: Dict[str, str] = {
    "artibonite": "Artibonite",
    "centre": "Centre",
    "grande anse": "Grande-Anse",
    "nippes": "Nippes",
    "nord": "Nord",
    "nord est": "Nord-Est",
    "nord ouest": "Nord-Ouest",
    "ouest": "Ouest",
    "sud": "Sud",
    "sud est": "Sud-Est",
    "total": "",
}

_CAPTION_KEY = "taux de seropositivite par departement geographique"
_TABLE_LINE = re.compile(r"^tableau (\d+)$")
_YEAR_LINE = re.compile(r"^mspp annee (\d{4})$")
_NUMERIC = re.compile(r"^[\d.,]+$")
_RATE = re.compile(r"^\d{1,3}[.,]\d$")
_MAX_HEADER_LINES = 12
#: The printed rate has one decimal, so 100 x cases / tested may sit up to 0.05 from the rate.
_RATE_TOL = 0.05 + 1e-9

_SERIES_BREAK = ("The MSPP removed duplicate records from the 2022 count of HIV-positive people, "
                 "per the 2022 report text above Tableau 50, so the fall from 14,695 in 2021 to "
                 "11,973 in 2022 is partly the removal of duplicates and not only a fall in "
                 "diagnoses. A change across 2021 and 2022 is not a change in diagnoses.")


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


def _count(group: List[Dict], raw: str) -> int:
    texts = [w["text"] for w in group]
    if not all(t.isdigit() for t in texts):
        raise _Refused(f"the row {raw!r} prints {' '.join(texts)!r} where a count belongs")
    if len(texts) > 1 and not (len(texts[0]) <= 3 and all(len(t) == 3 for t in texts[1:])):
        raise _Refused(f"the row {raw!r} prints {' '.join(texts)!r}, which is not one number "
                       f"grouped in thousands")
    return int("".join(texts))


def _rate(group: List[Dict], raw: str) -> float:
    texts = [w["text"] for w in group]
    if len(texts) != 1 or not _RATE.match(texts[0]):
        raise _Refused(f"the row {raw!r} prints {' '.join(texts)!r} where a rate with one "
                       f"decimal belongs")
    return float(texts[0].replace(",", "."))


def _read_row(raw: str, groups: List[List[Dict]]) -> Tuple[int, int, float]:
    """The two counts, in printed order, and the rate of one row."""
    if len(groups) != 3:
        raise _Refused(f"the row {raw!r} has {len(groups)} columns where three belong")
    a, b, rate = _count(groups[0], raw), _count(groups[1], raw), _rate(groups[2], raw)
    return a, b, rate


def _order(a: int, b: int, rate: float, raw: str) -> str:
    """Which printed column holds the people tested, decided by the row's own arithmetic."""
    if a > b > 0 and abs(100.0 * b / a - rate) <= _RATE_TOL:
        return "tested_first"
    if b > a > 0 and abs(100.0 * a / b - rate) <= _RATE_TOL:
        return "cases_first"
    raise _Refused(f"the row {raw!r} prints {a:,}, {b:,} and {rate}, and the rate is neither "
                   f"count over the other to one decimal")


def _parse_edition(pdf, year: int, cfg: Dict) -> Dict:
    """Find the one positivity table in the report and read its eleven rows."""
    found = []
    for pno in range(1, len(pdf.pages) + 1):
        lns = _lines(pdf.pages[pno - 1])
        for i, ln in enumerate(lns):
            if not _norm(ln["text"]).startswith(_CAPTION_KEY):
                continue
            prev = _norm(lns[i - 1]["text"]) if i > 0 else ""
            m = _TABLE_LINE.match(prev)
            if not m:
                log.info("ht_mspp: %d report, caption on page %d set aside, the line above is not "
                         "a 'Tableau N' line", year, pno)
                continue
            found.append((pno, i, lns, m.group(1)))
    if len(found) != 1:
        raise _Refused(f"{len(found)} captions passed the caption gate, on pages "
                       f"{[f[0] for f in found]}, where exactly one must")
    pno, i, lns, table_id = found[0]
    caption = lns[i]["text"]

    rest = _norm(caption)[len(_CAPTION_KEY):].strip()
    if rest and rest != f"en {year}":
        raise _Refused(f"the caption {caption!r} on page {pno} ends in {rest!r}, where only "
                       f"'en {year}' or nothing may follow")
    if i + 1 >= len(lns):
        raise _Refused(f"nothing follows the caption on page {pno}")
    year_line = lns[i + 1]["text"]
    m = _YEAR_LINE.match(_norm(year_line))
    if not m or int(m.group(1)) != year:
        raise _Refused(f"the line below the caption reads {year_line!r}, where 'MSPP, Année "
                       f"{year}' belongs")
    if table_id != cfg["table"]:
        log.warning("ht_mspp: %d report, the table is numbered Tableau %s where Tableau %s was "
                    "read by hand", year, table_id, cfg["table"])

    header: List[str] = []
    rows: Dict[str, Dict] = {}
    orders = set()
    source_line: Optional[str] = None
    k = i + 2
    while k < len(lns):
        ln = lns[k]
        k += 1
        raw, groups = _split(ln)
        key = _norm(raw)
        if key not in _ROWS:
            if rows:
                raise _Refused(f"the line {ln['text']!r} on page {pno} sits inside the table and "
                               f"is not one of the eleven expected rows")
            header.append(ln["text"])
            if len(header) > _MAX_HEADER_LINES:
                raise _Refused(f"more than {_MAX_HEADER_LINES} lines between the caption and the "
                               f"first department row on page {pno}")
            continue
        admin1 = _ROWS[key]
        if admin1 in rows:
            raise _Refused(f"the row {raw!r} appears twice")
        a, b, rate = _read_row(raw, groups)
        order = _order(a, b, rate, raw)
        orders.add(order)
        tested, cases = (a, b) if order == "tested_first" else (b, a)
        rows[admin1] = {"source_label": raw, "tested": tested, "cases": cases, "rate": rate,
                        "source_line_text": ln["text"]}
        if admin1 == "":
            if k < len(lns) and _norm(lns[k]["text"]).startswith("source"):
                source_line = lns[k]["text"]
            break
    else:
        raise _Refused(f"no TOTAL row below the caption on page {pno}")

    missing = sorted(a or "TOTAL" for a in _ROWS.values() if a not in rows)
    if missing:
        raise _Refused(f"row(s) not found: {missing}")
    if len(orders) != 1:
        raise _Refused("the rows disagree on which column holds the people tested")
    header_words = set(_norm(" ".join(header)).split())
    if not any(_norm(h).split()[:1] == ["departement"] for h in header if _norm(h)):
        raise _Refused(f"no header line starting 'Département' above the rows on page {pno}")
    absent = [w for w in cfg["header_words"] if w not in header_words]
    if absent:
        raise _Refused(f"the header on page {pno} lacks the words {absent}, so the table is not "
                       f"the one read by hand")

    for col in ("tested", "cases"):
        depts = sum(r[col] for a, r in rows.items() if a)
        if depts != rows[""][col]:
            raise _Refused(f"the ten departments sum to {depts:,} {col}, where the TOTAL row "
                           f"prints {rows[''][col]:,}")

    total = (rows[""]["tested"], rows[""]["cases"])
    if total != cfg["total"]:
        log.warning("ht_mspp: %d report, the TOTAL row reads %s people tested and %s cases, where "
                    "the copy read on 8 October 2026 printed %s and %s", year,
                    f"{total[0]:,}", f"{total[1]:,}", f"{cfg['total'][0]:,}",
                    f"{cfg['total'][1]:,}")
    (order,) = orders
    log.info("ht_mspp: %d report, Tableau %s on page %d, eleven rows read, columns %s, "
             "%s cases nationally", year, table_id, pno, order.replace("_", " "),
             f"{total[1]:,}")
    return {"rows": rows, "table_id": table_id, "page": pno, "caption": caption,
            "year_line": year_line, "header": " / ".join(header), "order": order,
            "source_line": source_line}


class HaitiMSPPConnector(BaseConnector):
    """Haiti MSPP annual statistical reports: HIV-positive people by department, 2020 to 2023."""

    source_id = "ht_mspp"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Haiti MSPP annual statistical reports (Rapport Statistique): people who tested "
                   "HIV positive and know the result, by department and nationally, 2020 to 2023 "
                   "(to-source).")
    country = "HTI"
    timeout = 180

    def __init__(self, raw_dir: str = "data/raw/haiti_mspp", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, year: int, cfg: Dict) -> Path:
        """Local copy of one report, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / cfg["local"]
        url = _URL + cfg["file"]
        if path.exists():
            log.info("ht_mspp: using cached %s", path)
        else:
            blob = self._request("GET", url).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{url} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("ht_mspp: downloaded the %d report (%.1f MB) -> %s", year, len(blob) / 1e6,
                     path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == cfg["known"]:
            log.info("ht_mspp: the %d report matches the copy read on 8 October 2026 (sha256 %s)",
                     year, digest[:12])
        else:
            log.warning("ht_mspp: the %d report differs from the copy read on 8 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s); the table gates still run",
                        year, len(blob), digest[:12], *cfg["known"])
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
        years = [y for y in sorted(_EDITIONS) if start_year <= y <= end_year]
        if not years:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("ht_mspp: pdfplumber not installed (pip install pdfplumber)")
            return

        emitted, refused = 0, []
        for year in years:
            cfg = _EDITIONS[year]
            try:
                path = self._pdf_path(year, cfg)
            except Exception as exc:
                log.warning("ht_mspp: the %d report could not be fetched (%s)", year, exc)
                refused.append(year)
                continue
            try:
                with pdfplumber.open(str(path)) as pdf:
                    table = _parse_edition(pdf, year, cfg)
            except _Refused as exc:
                log.warning("ht_mspp: the %d report refused because %s", year, exc)
                refused.append(year)
                continue
            except Exception as exc:
                log.warning("ht_mspp: the %d report failed to parse (%s)", year, exc)
                refused.append(year)
                continue
            for row in self._rows(year, cfg, table):
                emitted += 1
                yield row
        log.info("ht_mspp: emitted %d rows, %d report(s) refused%s", emitted, len(refused),
                 f" ({', '.join(map(str, refused))})" if refused else "")

    def _rows(self, year: int, cfg: Dict, table: Dict) -> Iterator[PanelRow]:
        url = _URL + cfg["file"]
        order = sorted(a for a in table["rows"] if a) + [""]
        for admin1 in order:
            rec = table["rows"][admin1]
            extra: Dict = {
                "edition": cfg["local"],
                "edition_year": year,
                "table": f"Tableau {table['table_id']}",
                "page": table["page"],
                "caption": table["caption"],
                "year_line": table["year_line"],
                "source_line": table["source_line"],
                "column_header": table["header"],
                "column_order": table["order"],
                "extraction": ("text layer, caption-anchored, columns split on the measured gap "
                               "between words, and the column holding cases decided by the row's "
                               "own arithmetic"),
                "source_row": rec["source_line_text"],
                "admin1_source_label": rec["source_label"],
                "people_tested": rec["tested"],
                "positivity_pct_printed": rec["rate"],
                "definition": ("people who tested HIV positive in the report year and know the "
                               "result, the count in the MSPP positivity table"),
                "integrity": ("the ten department rows sum exactly to the TOTAL row in people "
                              "tested and in cases, and every printed rate equals cases over "
                              "people tested to one decimal"),
                "deduplication": cfg["deduplication"],
                "series_break": _SERIES_BREAK,
            }
            if "header_note" in cfg:
                extra["header_note"] = cfg["header_note"]
            if table["source_line"] is None:
                extra["source_line_note"] = "the report prints no source line under this table"
            if admin1:
                extra["reconcile_with"] = (
                    "none. No other source in the panel held Haiti department notified_hiv_cases "
                    "rows when this connector was built (checked 13 October 2026). The "
                    "pepfar_snu department new_diagnoses rows count positive test results under "
                    "PEPFAR definitions and are never compared (Jason's ruling of 8 October 2026)")
            else:
                extra["reconcile_with"] = (
                    "none in the panel. paho_core holds no Haiti row. Never compare with the "
                    "new_diagnoses rows of pepfar_snu, pepfar_modality, pepfar_panorama or "
                    "global_fund (Jason's ruling of 8 October 2026). The PAHO HIV dashboard shows "
                    "Haiti for 2018 to 2024 outside the panel, and the research notes record a "
                    "dashboard figure of 13,940 for 2021, equal to the MSPP count for 2023, so "
                    f"whether the dashboard years align with the report years is NOT VERIFIED "
                    f"({_NOTES})")
            yield self.make_row(
                country_iso3="HTI", country_name="Haiti",
                indicator_id="notified_hiv_cases", year=year, value=rec["cases"],
                unit="count", admin1=admin1,
                source_url=url,
                source_indicator_code=f"rapport_statistique.{year}.tableau{table['table_id']}",
                extra=extra,
            )
