"""
Cameroon — NASA/REDES national AIDS spending assessment connector (to-source, financing).

Source: the Comité National de Lutte contre le Sida (CNLS) produces Cameroon's National AIDS
Spending Assessment, and UNAIDS hosts the reports at https://www.unaids.org/. An assessment
reconstructs every franc spent on HIV in the years it covers, by revenue source, by financing
entity, by intervention and by production factor. The assessments are the only published
Cameroonian HIV expenditure accounts that separate domestic public money from domestic
private money and from each named donor, which is exactly the split this project's funding-cut
panel needs and which neither UNAIDS GAM nor PEPFAR publishes for Cameroon.

Six assessments are read, covering nine years. The 2016-2017 and 2020-2021 assessments print
two year columns and are read by the two-year readers below. The 2007, 2009, 2011 and 2012
assessments print a single column of figures and are read by the single-year readers. One
further year, 2010, comes from a year-labelled sentence in the 2011 report, and the exception
section below sets out what makes that sentence readable. Every one of the six reports is
born-digital with a full text layer, so no OCR is used anywhere here.

EVERYTHING IS IN CFA FRANCS, AND NEITHER DOCUMENT PUBLISHES AN EXCHANGE RATE

Every figure in both assessments is printed in FCFA (XAF). Neither document states the rate
it would take to convert, and neither prints a dollar equivalent. This connector therefore
emits LOCAL CURRENCY levels under the `_lcu` indicator ids, with `extra.currency` naming the
currency, plus one currency-free share recomputed from those levels. Converting here would
mean fetching a rate, which is data collection, and inventing a rate would be worse. The
recommendation on the record is to add the World Bank's `PA.NUS.FCRF` (official exchange
rate, LCU per US dollar, period average) to `world_bank.py` so that a later derived step can
produce a dollar series from two traceable panel series instead of a constant buried in a
parser. That change alters an existing connector's output for every country, so it is the
researcher's call and is not made here.

WHY THE TABLE NUMBERS ARE NEVER USED TO FIND A TABLE

The 2020-2021 report's list of tables disagrees with its own body. The list's Tableau 7 is
the body's Tableau 8, the list's Tableau 8 is the body's Tableau 9, the list's Tableau 12 is
the body's Tableau 14, and the list prints two different tables both called Tableau 9. The
body's Tableau 14 then carries a stale caption reading "en 2018 et 2019" above a table whose
own year header says 2020 and 2021. So every block below is located by its CAPTION TEXT, or,
for the unnumbered revenue table, by the text of a row it must contain, and the year for every
block is read from that block's own year header rather than from any caption or table number.
Some lines in the list of tables carry no dotted leader, so a dotted-leader filter is not
enough on its own to keep a contents-page line out; the integrity gates below are what refuse
it, because a contents-page line carries no year header and no figures.

EVERY PRINTED PERCENTAGE IS REFUSED, AND EVERY SHARE IS RECOMPUTED FROM LEVELS

Three different printed values exist in the 2020-2021 report for one quantity, the 2021
international share: 94.1 per cent in Tableau 8, 94.0 per cent in the revenue table and 94.1
per cent in the narrative, against 94.1244 per cent recomputed from the levels the same
document prints. The 2021 domestic public share prints as 4.0 per cent where its own numerator
and denominator give 4.4316 per cent, and the report's key-indicators table prints 4.6 per
cent for the same quantity. That key-indicators table is refused in full: its 2020 public
share of 4.1 per cent reproduces only against the intervention subtotal, while its private and
external shares reproduce against neither denominator. The headline total is taken from the
revenue table, where three independent tables agree on it to the franc.

WHAT IS REFUSED, AND WHY

- The prevention series. The 2016-2017 assessment's "Prévention" (27.5 and 21.3 per cent)
  includes voluntary counselling and testing, which its own prose names as the largest
  prevention pool, while the 2020-2021 assessment separates ASC.02 Conseil et dépistage (10.8
  and 9.9 per cent) from ASC.01 Prévention (6.1 and 6.1 per cent). ASC.01 plus ASC.02 is 16.9
  and 16.0 per cent, so the apparent fall of 21.4 points from 2016 to 2020 and 15.2 points from
  2017 to 2021 becomes 10.6 and 5.3 points once the reclassification is undone, and the published
  categories cannot say whether those 10.6 and 5.3 points are a cut. Treatment is safe and
  is emitted, because both assessments carry a single treatment line covering the same
  activities.
- The rest of the intervention classification, for the same reason.
- The Graphique 8 page's UN-system and other-international rows. The page's international
  components exceed the Tableau 8 international total by 256,845,950 FCFA in 2020 and
  511,464,477 FCFA in 2021, entirely inside "Autre internationaux", and the 2020 UN row
  equals ONUSIDA plus PAM plus OMS exactly while the 2021 UN row excludes the ILO's
  14,225,300 FCFA, so the definition of the UN row shifts between years.
- The Graphique 8 page's Global Fund row for 2017, which prints 29,844,975,030 FCFA against
  the 2016-2017 assessment's own 31,704,143,887 FCFA, a contradiction of 1,859,168,857 FCFA.
  The same row's 2016 figure ties exactly, so the row is used for nothing and the Global Fund
  series comes from the assessments themselves.
- The Graphique 8 page's 2014, 2015, 2018 and 2019 columns, which no assessment in this
  connector's allow-list covers. An assessment contributes only the years it assesses.
- Both graphique data-label sets. Graphique 9's labels on printed page 41 extract in
  descending year order, reversed from the chart's own axis, and the two candidate orderings
  differ by 231,233,448 FCFA. Graphique 6's labels on printed page 37 extract the 2020 row's
  year fused to its first figure as "202015768219402". Neither is readable safely, and the
  `_figures` pattern table below refuses both as a side effect of accepting only the six
  cell-type sequences a real two-year row can produce.
- The revenue table's multilateral line, REV.07.01.02, as a multilateral total. The line is
  not comparable with Tableau 8's FE.03.02: it falls short of FE.03.02 plus FE.03.03 by
  exactly the amount by which REV.07.01.01 plus REV.07.01.02 falls short of REV.07, being
  152,234,707 FCFA in 2020 and 84,910,026 FCFA in 2021. So the revenue table's own disclosed
  0.2 per cent residual sits entirely inside that one line, and the donor components are taken
  from Tableau 8, which ties exactly at all three of its nesting levels.
- The 2007 international level, private level and international share. The 2007 annexe's
  "Fonds privés (sous total)" of 659,288,603 FCFA carries no household line at all, and both
  of its children are named international bodies, being "Organisations internationales à but
  non lucratif et fondations" and "Organisations internationales à but lucratif et
  fondations/corporations". A fourth top-level sub-total of 1,347,369,762 FCFA is
  international on its own label. So 659,288,603 FCFA of 18,049,143,415 FCFA, being 3.65 per
  cent, could sit on either side of the domestic and international divide, and the three
  series that depend on where it sits are all refused for 2007. The domestic public level is
  not affected and is emitted.
- The 2009 Global Fund level, and the 2010 donor rows in full. Neither report's body carries
  a donor split, both printing one "Fonds internationaux" line and stopping there, but both
  reports carry one in an annexe, so the United States and other-bilateral series are
  emitted for 2009 and 2011 and the Global Fund series for 2011. The section on the two
  Annexe 3 donor tables below says what each annexe is and how each is gated. Two refusals
  remain. The Global
  Fund level is refused for 2009, because the 2009 matrix books the whole of the
  international block's public-sector agent column, 17,734,185,491 FCFA, to the Global Fund
  alone, making the printed 20,913,254,871 FCFA public expenditure carrying a Global Fund
  source label and not a Global Fund disbursement, and because that level is more than twice
  what the Global Fund's own IATI activity file and the OECD creditor reporting system each
  report for Cameroon in 2009 at any euro-dollar rate of that year. And all three donor
  series are refused for 2010, which has no annexe of its own and whose three named
  narrative components fall 778,048,854 FCFA short of the 2010 total the same report states.
- The 2012 domestic public and private levels. The 2012 report prints no source-of-financing
  table at all: its captions run from Tableau 1 on population straight to Tableau 2 on
  international funds, so only the international side of 2012 is readable.
- The year 2008, in full. Printed page 27 of the 2012 report shows six annual totals and six
  year ticks, but the renderer sorted the data labels by VALUE and not by year, so print
  order is neither year order nor its reverse. 2007 is known independently to be
  18,049,143,415 FCFA, the smallest of the six, yet 34,636,909,946 prints first, and 2012 is
  known independently to be 25,420,437,252 FCFA, which prints third. The 2011 report's
  equivalent Figure 4 carries no value labels at all. No 2008 figure is recoverable from
  either chart, and none is emitted.

THE TWO ANNEXE 3 DONOR TABLES

The 2009 and 2011 reports each carry a donor table in an annexe, and the two annexes are
different kinds of object, so each has its own reader.

The 2009 report's Annexe 3 is a REDES matrix, printed twice and identically on pdf pages 53
and 54. Every row carries six figure columns, being Secteur public, Secteur privé, Organismes
acquéreurs internationaux, Organismes multilatéraux administrant des ressources externes,
Organisations et fondations internationales à but non lucratif, and Total. Columns four and
five do NOT split a row further. Columns four and five are nested inside column three, and
two rows prove it on their own arithmetic: the UNICEF row prints its 1,480,166,210 FCFA in
column three, again in column four, and once more as its Total, and the Alliance
internationale row prints its 8,549,648 FCFA in column three, again in column five, and once
more as its Total. In both rows the printed Total equals the sum of the first three columns
alone, so the reader adds columns one to three and refuses columns four and five. Five gates
run. Each of the seven rows read closes across its three disjoint agent columns onto its own
printed Total. The Canadian, German, Dutch and American governments sum to the printed
Contributions bilatérales directes of 3,561,988,318 FCFA, which is also what makes the
other-bilateral residual safe, because what is left after removing the American government is
then exactly the other three governments the matrix names. The same four governments sum to
that sub-total down each of the three agent columns taken separately as well. The matrix's own
Fonds publics and Fonds privés rows equal Tableau 1's to the franc. And the seven rows read
from the two printings agree cell for cell.

The 2011 report's Annexe 3 is a plain two-column tree instead, an FS code with its level and
its share of its own parent, on pdf pages 52 and 53, so the single-year table reader reads it
unchanged. The report carries two tables under the heading Annexe 3, one of them a UNGASS
reporting table, so the anchor phrase carries the descriptive words and not the annexe number
alone. Whole-cell label matching is what keeps the tree's levels apart, since a prefix match
on "FS.03.01" would take the American government's "FS.03.01.22" line as well. Four gates
run. The French, German and American governments sum to the printed FS.03.01 of 8,161,414,720
FCFA, which makes the other-bilateral residual exactly the French and German governments. The
nine agencies printed under FS.03.02, the Global Fund among them, sum to the printed FS.03.02
of 5,756,941,865 FCFA, which is why the eight agencies that are emitted for no indicator are
read at all. FS.03.01, FS.03.02 and FS.03.03 sum to the printed FS.03, and FS.01, FS.02 and
FS.03 sum to the printed Total général. And the annexe's FS.01, FS.02, FS.03 and Total
général each equal Tableau 5's to the franc, which is the strongest check available here,
because Annexe 3 and Tableau 5 are two independently typeset tables twenty-five pages apart.

Both readers return None and log a warning where a gate fails or an annexe cannot be found,
and do not refuse their whole edition. The six rows Tableau 1 and Tableau 9 produce for 2009,
and the six Tableau 5 and Tableau 6 produce for 2011, tie to each other to the franc and do
not depend on either annexe, so an annexe that has been redrawn should cost the donor rows
and nothing else.

TWO EXCEPTIONS TO "AN ASSESSMENT CONTRIBUTES ONLY ITS OWN YEARS"

The first exception. The 2016-2017 assessment prints no domestic split at all. The 2020-2021
report's Graphique 8 page carries one, and its public and private rows reproduce the residual to
the franc: 44,996,675,860 minus 39,386,844,702 is 5,609,831,158 for 2016, which is exactly
that page's public 3,058,783,825 plus private 2,551,047,333, and the same identity holds for
2017 at 10,839,249,471. The same page's bilateral row ties exactly to the 2016-2017 bilateral
subtotal in both years, so the year columns cannot have been read in the wrong order: a
reversed read would put 2020's bilateral at 44,858,564,653 against 47,739,877,696 and fail by
2,881,313,043 FCFA. The 2016 and 2017 domestic rows are therefore taken from that page.

The second exception. No assessment covers 2010, but the 2011 report's narrative states the
2010 international total in a sentence that names the year and prints the 2011 figure beside
it for comparison: "une baisse de l'appui des partenaires à la lutte contre le VIH
(19 435 236 054 Fcfa en 2010 contre 17 079 607 502 Fcfa)". Three things make that sentence
readable where the charts are not. The sentence's second figure equals Tableau 5's printed
FS.03 to the franc, which fixes what the sentence is comparing. The next page then names two
2010 components with their shares, 9,831,025,877 FCFA at 50,58 per cent and 4,122,725,247
FCFA at 21,21 per cent, and both shares reproduce against 19,435,236,054 to better than
0.004 percentage points, which no other denominator in either report does. And the 2011 side
of the same passage names three international components that sum to Tableau 5's FS.03
exactly, so the passage's arithmetic is sound where it can be checked. Only the 2010
international total is taken, because the three 2010 components the report names fall
778,048,854 FCFA short of the 2010 total it states, so the 2010 donor split is refused.

The 2010 international level and the 2016 and 2017 domestic rows are the only figures in this
connector that come from a document that does not assess the year.

ONE FRANC OF TOLERANCE, AND WHERE IT IS SPENT

Five independent one-franc gaps exist between a printed subtotal and the sum of the components
printed beside it: Tableau 9's 2020 intervention sum (80,097,077,043 against a printed
80,097,077,042), Tableau 14's 2020 production-factor sum (80,741,729,488 against
80,741,729,487), Tableau 11's treatment sums in both years, and, in the 2007 assessment,
Annexe 2's care and treatment category (outpatient care 7,307,578,435 plus inpatient care
70,799,710 is 7,378,378,145 against a printed 7,378,378,146). Those are rounding in the
source, so `_FRANC_TOL` is one franc. The revenue table's top level, all three of Tableau 8's
nesting levels, the 2016-2017 assessment's two tables, all four nesting levels of the 2012
assessment's donor table, every gate on both of the Annexe 3 donor tables, and every
cross-table identity below tie EXACTLY, with no tolerance at all, and are gated that way.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
# The PDF geometry primitives are shared with `cameroon_cnls.py`. `_pdf_text` carries the
# measurements that justify the line and column tolerances. Number parsing stays local to this
# module, because the two document families use opposite comma conventions: a comma is a
# THOUSANDS separator in the NASA assessments and `_to_franc` below must accept it, while a
# comma is a decimal mark in the CNLS reports and that module's parser must reject it.
from ._pdf_text import (
    COL_GAP as _COL_GAP,
    LINE_TOL as _LINE_TOL,
    columns as _columns,
    lines as _lines,
    match_label as _match_label,
    match_prefix as _match_prefix,
    norm as _norm,
)

log = logging.getLogger("hivimpact")

# -- tolerances -----------------------------------------------------------------------------
# Francs. Spent on four documented one-franc roundings; see the module docstring. Every other
# gate in this module is exact.
_FRANC_TOL = 1
# Percentage points, used only for the optional prose cross-check on the 2016-2017 assessment,
# whose narrative prints the international share to one decimal (87,5% and 83,5%) against
# 87.5328 and 83.4812 recomputed.
_PROSE_TOL = 0.06
# Percentage points, used only for the 2010 recovery, whose two printed shares reproduce to
# 0.0034 and 0.0026 points against the right denominator and to nothing like that against any
# other figure in the 2011 report. A tolerance this tight is what makes the check evidence.
_PCT_TOL_2010 = 0.01
# A year column header is only believed inside this range.
_YEAR_MIN, _YEAR_MAX = 2000, 2030
# Francs. The documented gap between the 2007 Annexe 2 category list and its own printed
# grand total, 0.052 per cent of that total. Disclosed and logged, never silently absorbed;
# see `_read_2007`, which gates the one figure it takes from that annexe a different way.
_A2_2007_GAP = 9_444_575

_CURRENCY = "XAF"
_CURRENCY_NOTE = ("the assessment publishes every figure in FCFA and states no exchange rate, "
                  "so the level is local currency; no conversion is performed here")
_EXTRACTION = ("text layer, caption-anchored, cells delimited by word x-position, cells read "
               "on their level-against-percentage type sequence (extract_tables() drops rows "
               "on these documents, and reading cells by position misfiles a missing cell)")

# -- the allow-list: filename -> (edition key, years, source URL) ---------------------------
# URLs are the UNAIDS document paths the survey script downloaded; its `_local_name()`
# flattens a URL path by replacing "/" with "_", so each filename below is a UNAIDS path
# flattened. The years are cross-checked against each block's own printed year header, and a
# document whose header disagrees is refused rather than emitted under an assumed year.
_UNAIDS_ROOT = "https://www.unaids.org"
_EDITIONS: Dict[str, Tuple[str, Tuple[int, int], str]] = {
    "sites_default_files_media_documents_NASA-2016-2017_cameroun_fr.pdf": (
        "2016-2017", (2016, 2017),
        f"{_UNAIDS_ROOT}/sites/default/files/media_documents/NASA-2016-2017_cameroun_fr.pdf",
    ),
    "sites_default_files_NASAreport_cameroon_2020-2021_fr.pdf": (
        "2020-2021", (2020, 2021),
        f"{_UNAIDS_ROOT}/sites/default/files/NASAreport_cameroon_2020-2021_fr.pdf",
    ),
}

# The four earlier assessments, each printing one column of figures. The filenames were
# checked against `_local_name()` offline: every URL below flattens to exactly the filename
# beside it, including the 2009 path whose space is percent-encoded.
_F2007 = ("en_media_unaids_contentassets_dataimport_pub_report_2009"
          "_20091205_nasa_cameroon_07_fr.pdf")
_F2009 = ("en_media_unaids_contentassets_documents_data-and-analysis_tools_nasa"
          "_NASA_Cameroon__202009_fr.pdf")
_F2011 = "sites_default_files_documents_cameroon_2011_fr.pdf"
_F2012 = "sites_default_files_documents_cameroon_2012_fr.pdf"

# filename -> (edition key, the years that edition contributes, source URL)
_EDITIONS_SINGLE: Dict[str, Tuple[str, Tuple[int, ...], str]] = {
    _F2007: ("2007", (2007,),
             f"{_UNAIDS_ROOT}/en/media/unaids/contentassets/dataimport/pub/report/2009/"
             f"20091205_nasa_cameroon_07_fr.pdf"),
    _F2009: ("2009", (2009,),
             f"{_UNAIDS_ROOT}/en/media/unaids/contentassets/documents/data-and-analysis/"
             f"tools/nasa/NASA_Cameroon_%202009_fr.pdf"),
    # The 2011 report contributes 2010 as well; see the second exception in the docstring.
    _F2011: ("2011", (2010, 2011),
             f"{_UNAIDS_ROOT}/sites/default/files/documents/cameroon_2011_fr.pdf"),
    _F2012: ("2012", (2012,),
             f"{_UNAIDS_ROOT}/sites/default/files/documents/cameroon_2012_fr.pdf"),
}


class _Refused(Exception):
    """Raised when a block fails an integrity gate. The document emits nothing."""


# -- number parsing -------------------------------------------------------------------------
# Strict thousands-group validation. A level is either an ungrouped run of digits, or digit
# groups of exactly three separated by commas, or the same separated by spaces. The grouping
# requirement is what keeps a percentage out of a level column: "0,0" has a one-digit group
# after its comma and is refused, and so is "59,6". A dot is refused outright, because the
# 2020-2021 assessment uses a dot as its DECIMAL mark ("4.0%"), so a cell containing one is a
# percentage whose sign was lost, not a level. The space form survives for safety only, since
# `_columns` concatenates the words of an all-numeric column and has already removed the
# 2016-2017 assessment's thousands spaces by the time a cell reaches here.
_INT_FORMS = (
    re.compile(r"\d+$"),
    re.compile(r"\d{1,3}(,\d{3})+$"),
    re.compile(r"\d{1,3}( \d{3})+$"),
)
_DASHES = ("-", "‐", "‑", "‒", "–", "—")


def _to_franc(cell: str) -> Optional[int]:
    """A column-joined cell to a whole number of francs, or None when the cell is not one."""
    s = str(cell or "").strip()
    if not s or "%" in s or "." in s:
        return None
    if not any(p.match(s) for p in _INT_FORMS):
        return None
    return int(s.replace(",", "").replace(" ", ""))


def _classify(cell: str) -> Optional[str]:
    """One cell to "P" (a percentage), "L" (a level, possibly an explicit dash) or None.

    None means the cell is not a figure at all, which is how `_figures` finds where a row's
    label ends and its figures begin.
    """
    s = str(cell or "").strip()
    if not s:
        return None
    if "%" in s:
        return "P"
    if s in _DASHES:
        return "L"
    return "L" if _to_franc(s) is not None else None


# The only cell-type sequences a genuine two-year row can produce, mapped to the positions of
# the first and second year's LEVELS. None means that year's level is absent from the row.
#
# Both documents print rows with a cell missing, so positions cannot be trusted: the 2016-2017
# assessment's PNUD row extracts as three cells for four columns because its 2016 level is
# blank, and the 2020-2021 assessment's OIT row omits its 2020 level while its PNUD row prints
# a dash there. Reading by position would file PNUD's 2017 figure as 2016. Reading on the type
# sequence cannot, because a percentage is distinguishable from a level by its sign.
#
# "L", "P" is deliberately absent: a two-cell row of one level and one percentage could be
# either year and there is nothing in the row to say which, so it is refused. The sequences a
# chart data label produces are absent for the same reason, which is what refuses Graphique 6's
# fused "202015768219402 | 63527878685 | 1445631400" line and Graphique 9's label sets.
_PATTERNS: Dict[Tuple[str, ...], Tuple[Optional[int], Optional[int]]] = {
    ("L", "P", "L", "P"): (0, 2),   # the complete row
    ("L", "P", "L"): (0, 2),        # second year's percentage wrapped to the next line
    ("L", "P", "P"): (0, None),     # second year's level absent
    ("P", "L", "P"): (None, 1),     # first year's level absent
    ("L", "L"): (0, 1),             # a total row, which the documents print without shares
    ("P", "P"): (None, None),       # both levels absent
}


def _figures(cols: Sequence[str]) -> Optional[Tuple[str, Tuple[Optional[int], Optional[int]]]]:
    """Split a line's columns into its trailing label text and its two year levels.

    Returns None when the line is not a readable two-year row. The label returned is the LAST
    text column on the line, not the first, because the 2016-2017 assessment's Tableau 1 puts a
    merged group heading in the first column and the row's own name in the second: the UNESCO
    row extracts as "affectées | UNESCO | 31377779 | 0,2% | 36818769 | 0,1%".
    """
    kinds: List[str] = []
    vals: List[Optional[int]] = []
    i = len(cols)
    while i > 0:
        k = _classify(cols[i - 1])
        if k is None:
            break
        kinds.append(k)
        vals.append(_to_franc(cols[i - 1]) if k == "L" else None)
        i -= 1
    kinds.reverse()
    vals.reverse()
    spec = _PATTERNS.get(tuple(kinds))
    if spec is None:
        return None
    label = cols[i - 1] if i > 0 else ""
    return label, (None if spec[0] is None else vals[spec[0]],
                   None if spec[1] is None else vals[spec[1]])


def _wide_levels(cols: Sequence[str], n: int) -> Optional[Tuple[str, List[Optional[int]]]]:
    """Split a line into its trailing label text and exactly `n` level cells, or None.

    Used for the Graphique 8 page, whose table is eight year columns of levels with no
    percentage columns at all, so the type-sequence table above does not apply.
    """
    vals: List[Optional[int]] = []
    i = len(cols)
    while i > 0 and len(vals) < n:
        if _classify(cols[i - 1]) != "L":
            break
        vals.append(_to_franc(cols[i - 1]))
        i -= 1
    if len(vals) != n:
        return None
    vals.reverse()
    label = cols[i - 1] if i > 0 else ""
    if not _norm(label):
        return None
    return label, vals


def _year_header(cols: Sequence[str], want: int) -> Optional[List[int]]:
    """A line's columns to the year order the table prints, or None if the line is not one.

    Columns before the first year are skipped, because a header can start with a stub naming
    the row dimension: the 2016-2017 assessment's Tableau 2 heads its first column
    "Intervention/catégorie de dépenses". From the first year onwards every column must be
    either another year or a share column, which is what keeps a narrative paragraph out, and
    `want` fixes how many years the caller expects, so a two-year table cannot be anchored on
    a chart's four-year axis and the eight-year Graphique 8 table cannot be anchored on a
    two-year table header.

    Reading the order from the document rather than assuming it is what makes the Graphique 8
    page safe: that page prints its years DESCENDING, 2021 first, while every other table in
    the same report prints them ascending.
    """
    years: List[int] = []
    for c in cols:
        s = str(c or "").strip()
        if not s:
            continue
        v = _to_franc(s)
        if v is not None and _YEAR_MIN <= v <= _YEAR_MAX:
            years.append(v)
        elif not years:
            continue                 # a stub column to the left of the first year
        elif "%" not in s:
            return None              # anything else after the first year is not a header
    return years if len(years) == want else None


# -- locating a block -----------------------------------------------------------------------
def _caption_pages(pdf, phrase: str) -> List[int]:
    """Page indices whose text contains `phrase`, accents, case and punctuation ignored.

    More than one page can match, because a caption phrase also appears in the list of tables.
    Callers try the matches in document order and keep the first whose block passes its gates,
    so a contents-page match is harmless: a contents line carries no year header and no
    figures, and fails immediately.
    """
    key = _norm(phrase)
    out: List[int] = []
    for i, page in enumerate(pdf.pages):
        try:
            text = page.extract_text() or ""
        except Exception:                                      # pragma: no cover - pdfplumber
            continue
        if key in _norm(text):
            out.append(i)
    return out


def _read_block(
    pdf,
    indices: Sequence[int],
    labels: Dict[str, str],
    *,
    name: str,
    stop_when_complete: bool = True,
) -> Tuple[List[int], Dict[str, Tuple[Optional[int], Optional[int]]],
           List[Tuple[int, int]]]:
    """Read one two-year table off the text layer.

    Returns the year order the table printed, a map of label key to that row's two levels, and
    the levels of every readable row whose label matched nothing. The unmatched rows matter:
    both documents print their grand total as a bare pair of figures with no label at all, and
    the callers below find it by searching those pairs for the one that satisfies the table's
    own arithmetic. Searching for the line that satisfies the arithmetic, instead of guessing
    which line is the total, is what makes the identification provable.

    Nothing is collected before the year header, which keeps the narrative paragraphs above a
    table out of the figures. `stop_when_complete` stops at the last expected row, which keeps
    the narrative BELOW a table out as well.

    A later year header REPLACES an earlier one, up to the first row that matches a label, and
    discards anything read in between. Printed page 41 is why: the Graphique 9 chart above
    Tableau 8 carries its own "2020 | 2021" axis line, so taking the first header on the page
    would take the year order from a chart rather than from the table being read. The two
    happen to agree there, and a parser that depends on that is a parser that works by luck.
    """
    rows: Dict[str, Tuple[Optional[int], Optional[int]]] = {}
    bare: List[Tuple[int, int]] = []
    years: Optional[List[int]] = None
    wanted = set(labels.values())
    prev1 = ""
    prev_had_figures = False
    for idx in indices:
        for ln in _lines(pdf.pages[idx]):
            cols = _columns(ln["words"])
            hdr = _year_header(cols, 2)
            if hdr is not None:
                if not rows:
                    years, bare = hdr, []
                prev1, prev_had_figures = ln["text"], False
                continue
            if years is None:
                prev1, prev_had_figures = ln["text"], False
                continue
            got = _figures(cols)
            if got is None:
                prev1, prev_had_figures = ln["text"], False
                continue
            label_text, pair = got
            key = None
            # A row's label is not always on the row's own line. Tableau 9's ASC.06 prints its
            # figures on a line with no label text at all, between two fragments of the label,
            # and Tableau 11's treatment total prints the label on one line and the figures on
            # the next. The 2016-2017 assessment's "fonds internationaux non classifiés
            # ailleurs" wraps across three lines with the figures on the second.
            #
            # The candidate list stops at the PREVIOUS line, and that line is only borrowed
            # when it carried no figures of its own. Both restrictions were forced by gates
            # that fired. Joining two preceding lines matched the 2016-2017 assessment's
            # bilateral subtotal as the United States row, because the subtotal is printed on
            # an all-numeric line whose two preceding lines read "Gouvernement américain" and
            # "Contributions", which would have claimed 23,486,587,409 FCFA of bilateral money
            # for Washington. Borrowing a previous line that had figures matched Tableau 14's
            # staff-costs row as its parent PF.01, because this connector's label map covers
            # PF.01 and not PF.01.01, so the unmatched child inherited the matched parent's
            # label. A line that carries its own figures owns its own label and lends it to
            # nobody, and every wrapped label in both documents is preceded by a label-only
            # line, so nothing is lost.
            for cand in (label_text, prev1, f"{prev1} {label_text}"):
                if prev_had_figures and cand is not label_text:
                    break
                if _norm(cand):
                    key = _match_prefix(cand, labels)
                    if key:
                        break
            if key is None:
                if pair[0] is not None and pair[1] is not None:
                    bare.append((pair[0], pair[1]))
            elif key in rows:
                if rows[key] != pair:
                    raise _Refused(
                        f"{name}: {key} appears twice with different levels, {rows[key]} and "
                        f"{pair}; refusing the table rather than choosing one")
            else:
                rows[key] = pair
            prev1, prev_had_figures = ln["text"], True
            if stop_when_complete and wanted <= set(rows):
                return years, rows, bare
    if years is None:
        raise _Refused(f"{name}: no two-year column header on the candidate page")
    missing = sorted(wanted - set(rows))
    if missing:
        raise _Refused(f"{name}: rows not found: {', '.join(missing)}")
    return years, rows, bare


def _check_years(years: Sequence[int], expect: Tuple[int, int], name: str) -> None:
    if list(years) != list(expect):
        raise _Refused(f"{name}: the table's own year header reads {list(years)} but the "
                       f"edition allow-list says {list(expect)}")


def _sum(rows: Dict[str, Tuple[Optional[int], Optional[int]]], keys: Iterable[str],
         j: int) -> int:
    """Sum one year's column over several rows, counting an absent level as zero.

    An absent level is zero here and None in the emitted row. The distinction is real: the
    2016-2017 assessment's PNUD row has no 2016 level and the multilateral subtotal printed
    beside it reproduces exactly when that gap counts as zero, so treating it as zero inside a
    gate is correct and is proved by the gate itself.
    """
    return sum((rows[k][j] or 0) for k in keys)


def _find_total(bare: Sequence[Tuple[int, int]], want: Tuple[int, int], name: str,
                tol: int = 0) -> Tuple[int, int]:
    """The unlabelled pair that satisfies the table's own arithmetic, or a refusal."""
    for pair in bare:
        if abs(pair[0] - want[0]) <= tol and abs(pair[1] - want[1]) <= tol:
            return pair
    raise _Refused(f"{name}: no unlabelled row equals the sum of the components, {want}; the "
                   f"candidates were {list(bare)}")


# -- the 2016-2017 assessment ---------------------------------------------------------------
# Tableau 1 is a breakdown of INTERNATIONAL funds only, which is why the grand total comes
# from Tableau 2 and the two tables have to be read together. The bilateral and multilateral
# subtotals are not read: both are printed on a line whose only text is a fragment of a merged
# group heading ("administrant des"), so they are derived from the components instead and
# checked against the grand total through the unlabelled international total. Deriving loses
# nothing, because both printed subtotals were confirmed by hand to equal their components
# exactly in both years.
_A1_LABELS = {
    "gouvernement francais": "bil_fr",
    "gouvernement allemand": "bil_de",
    "gouvernement americain": "bil_us",
    "union europeenne": "mul_eu",
    "fonds mondial": "mul_gf",
    "onusida": "mul_unaids",
    "unicef": "mul_unicef",
    "pnud": "mul_undp",
    "unesco": "mul_unesco",
    "unfpa": "mul_unfpa",
    "pam": "mul_wfp",
    "oms": "mul_who",
    "non classifies ailleurs": "nca",
}
_A1_BIL = ("bil_fr", "bil_de", "bil_us")
_A1_MUL = ("mul_eu", "mul_gf", "mul_unaids", "mul_unicef", "mul_undp", "mul_unesco",
           "mul_unfpa", "mul_wfp", "mul_who")

_A2_LABELS = {
    "prevention": "prevention",
    "soins et traitement": "treatment",
    "orphelins et autres enfants": "oev",
    "gestion et administration": "admin",
    "protection sociale et services sociaux": "social",
    "environnement favorable": "environment",
    "recherche liee au vih": "research",
    "total general": "total",
}
_A2_PARTS = ("prevention", "treatment", "oev", "admin", "social", "environment", "research")

_PROSE_SHARE = re.compile(r"respectivement\s+(\d+[.,]\d+)\s*%\s+et\s+(\d+[.,]\d+)\s*%")


def _read_assessment_a(pdf, years: Tuple[int, int]) -> Dict:
    """The 2016-2017 assessment: the international breakdown and the intervention table."""
    gates: List[str] = []

    t1 = None
    for idx in _caption_pages(pdf, "Decomposition des fonds internationaux"):
        try:
            yrs, rows, bare = _read_block(pdf, [idx], _A1_LABELS, name="Tableau 1",
                                          stop_when_complete=False)
            _check_years(yrs, years, "Tableau 1")
            bil = [_sum(rows, _A1_BIL, j) for j in (0, 1)]
            mul = [_sum(rows, _A1_MUL, j) for j in (0, 1)]
            nca = [rows["nca"][j] or 0 for j in (0, 1)]
            intl = _find_total(bare, (bil[0] + mul[0] + nca[0], bil[1] + mul[1] + nca[1]),
                               "Tableau 1")
            t1 = {"page": idx + 1, "rows": rows, "bil": bil, "mul": mul, "intl": list(intl)}
            break
        except _Refused as exc:
            log.debug("cm_nasa: page %d rejected as Tableau 1 (%s)", idx + 1, exc)
    if t1 is None:
        raise _Refused("Tableau 1 (Decomposition des fonds internationaux) not found")
    gates.append("Tableau 1: the three bilateral governments, the nine multilateral agencies "
                 "and the unclassified row sum EXACTLY to the printed international total in "
                 "both years")

    t2 = None
    for idx in _caption_pages(pdf, "Repartition des depenses par intervention"):
        try:
            yrs, rows, _ = _read_block(pdf, [idx], _A2_LABELS, name="Tableau 2")
            _check_years(yrs, years, "Tableau 2")
            for j in (0, 1):
                got, printed = _sum(rows, _A2_PARTS, j), rows["total"][j]
                if printed is None or got != printed:
                    raise _Refused(f"Tableau 2: the seven interventions sum to {got} for "
                                   f"{yrs[j]} against a printed total of {printed}")
            t2 = {"page": idx + 1, "rows": rows}
            break
        except _Refused as exc:
            log.debug("cm_nasa: page %d rejected as Tableau 2 (%s)", idx + 1, exc)
    if t2 is None:
        raise _Refused("Tableau 2 (Repartition des depenses par intervention) not found")
    gates.append("Tableau 2: the seven intervention rows sum EXACTLY to the printed Total "
                 "general in both years")

    total = [t2["rows"]["total"][j] for j in (0, 1)]
    share = [100.0 * t1["intl"][j] / total[j] for j in (0, 1)]

    # An independent check that the two tables belong to the same assessment: the narrative
    # above Tableau 1 states the international share to one decimal, and that sentence is
    # computed from a numerator in Tableau 1 and a denominator in Tableau 2. Optional, because
    # a redrafted sentence should not refuse a document whose arithmetic ties.
    prose = None
    try:
        prose = _PROSE_SHARE.search(pdf.pages[t1["page"] - 1].extract_text() or "")
    except Exception:                                          # pragma: no cover - pdfplumber
        prose = None
    if prose:
        printed = [float(g.replace(",", ".")) for g in prose.groups()]
        for j in (0, 1):
            if abs(share[j] - printed[j]) > _PROSE_TOL:
                raise _Refused(
                    f"the narrative prints an international share of {printed[j]}% for "
                    f"{years[j]} against {share[j]:.4f}% recomputed from Tableau 1 over "
                    f"Tableau 2; the two tables may not belong to the same assessment")
        gates.append(f"the narrative's printed international shares, {printed[0]}% and "
                     f"{printed[1]}%, reproduce from Tableau 1 over Tableau 2 to within "
                     f"{_PROSE_TOL} percentage points")
    else:
        log.warning("cm_nasa: the 2016-2017 narrative share sentence was not found, so the "
                    "independent prose cross-check on Tableau 1 over Tableau 2 was not run; "
                    "the arithmetic gates on both tables still passed")

    out: Dict[int, Dict[str, Tuple]] = {}
    for j, year in enumerate(years):
        t1p, t2p = t1["page"], t2["page"]
        out[year] = {
            "total": (total[j], f"Tableau 2, printed page {t2p}", "tableau2.total_general"),
            "intl": (t1["intl"][j], f"Tableau 1, printed page {t1p}",
                     "tableau1.total_international"),
            "us": (t1["rows"]["bil_us"][j], f"Tableau 1, printed page {t1p}",
                   "tableau1.gouvernement_americain"),
            "gf": (t1["rows"]["mul_gf"][j], f"Tableau 1, printed page {t1p}",
                   "tableau1.fonds_mondial"),
            "other_bilateral": (t1["bil"][j] - (t1["rows"]["bil_us"][j] or 0),
                                f"Tableau 1, printed page {t1p}",
                                "tableau1.bilateral_hors_etats_unis"),
            "treatment": (t2["rows"]["treatment"][j], f"Tableau 2, printed page {t2p}",
                          "tableau2.soins_et_traitement"),
            "share": (round(share[j], 4), f"Tableau 1 over Tableau 2, printed pages {t1p} "
                                          f"and {t2p}", "derived.part_international"),
        }
    return {"years": list(years), "series": out, "gates": gates,
            "total": total, "intl": t1["intl"], "bil": t1["bil"],
            "gf": [t1["rows"]["mul_gf"][j] for j in (0, 1)]}


# -- the 2020-2021 assessment ---------------------------------------------------------------
# The revenue table is unnumbered, so it is anchored on the text of a row it must contain
# rather than on a caption, and it spans two printed pages.
_REV_LABELS = {
    "rev 01": "public",
    "rev 06": "private",
    "rev 07 transferts etrangers directs": "international",
    "rev 07 01 01": "bilateral",
    "rev 07 01 02": "multilateral",
}
_REV_ANCHOR = "REV.07 Transferts etrangers directs"

_T8_LABELS = {
    "fe 03 entites internationales": "fe03",
    "fe 03 01 etats fournissant": "fe0301",
    "fe 03 01 09": "de",
    "fe 03 01 30": "us",
    "fe 03 02 organisations": "fe0302",
    "fe 03 02 04": "ilo",
    "fe 03 02 07": "gf",
    "fe 03 02 08": "unaids",
    "fe 03 02 11": "undp",
    "fe 03 02 19": "wfp",
    "fe 03 02 20": "who",
    "fe 03 03 organisations et fondations": "fe0303",
    "fe 03 03 31": "unf",
    "fe 03 03 99": "other_nonprofit",
}
_T8_BIL = ("de", "us")
_T8_MUL = ("ilo", "gf", "unaids", "undp", "wfp", "who")
_T8_NP = ("unf", "other_nonprofit")

_T9_LABELS = {
    "asc 01": "prevention",
    "asc 02": "testing",
    "asc 03": "treatment",
    "asc 04": "social",
    "asc 06": "systems",
    "autres recherche synergie": "other",
}
_T11_LABELS = {
    "asc 03 soins et traitement": "treatment",
    "asc 03 01": "art",
    "asc 03 02": "adherence",
    "asc 03 03": "laboratory",
    "asc 03 04": "coinfection",
}
_T14_LABELS = {
    "pf 01 depenses courantes": "current",
    "pf 02 depenses en capital": "capital",
    "total": "total",
}
_G8_LABELS = {
    "fonds des organisations bilaterales": "bilateral",
    "fonds mondial": "global_fund",
    "fonds publics": "public",
    "fonds prives": "private",
    "systeme des nations unis": "un_system",
    "autre internationaux": "other_international",
}


def _read_assessment_b(pdf, years: Tuple[int, int]) -> Dict:
    """The 2020-2021 assessment: the revenue table, Tableau 8, Tableau 9, 11 and 14."""
    gates: List[str] = []

    # -- the unnumbered revenue table, which carries the headline total -------------------
    rev = None
    anchor = _norm(_REV_ANCHOR)
    for i, page in enumerate(pdf.pages):
        try:
            text = page.extract_text() or ""
        except Exception:                                      # pragma: no cover - pdfplumber
            continue
        if anchor not in _norm(text):
            continue
        pages = [i - 1, i] if i > 0 else [i]
        try:
            yrs, rows, bare = _read_block(pdf, pages, _REV_LABELS, name="revenue table",
                                          stop_when_complete=False)
            _check_years(yrs, years, "revenue table")
            want = tuple((rows["public"][j] or 0) + (rows["private"][j] or 0)
                         + (rows["international"][j] or 0) for j in (0, 1))
            total = _find_total(bare, want, "revenue table")
            rev = {"page": i + 1, "rows": rows, "total": list(total)}
            break
        except _Refused as exc:
            log.debug("cm_nasa: pages %s rejected as the revenue table (%s)", pages, exc)
    if rev is None:
        raise _Refused("the unnumbered revenue table was not found")
    gates.append("revenue table: domestic public plus domestic private plus direct foreign "
                 "transfers equals the printed headline EXACTLY in both years")

    # -- Tableau 8, the international breakdown -------------------------------------------
    t8 = None
    for idx in _caption_pages(pdf, "Description des financements internationaux"):
        try:
            yrs, rows, _ = _read_block(pdf, [idx], _T8_LABELS, name="Tableau 8")
            _check_years(yrs, years, "Tableau 8")
            for j in (0, 1):
                for parts, parent, what in ((_T8_BIL, "fe0301", "the two bilateral states"),
                                            (_T8_MUL, "fe0302", "the six multilateral bodies"),
                                            (_T8_NP, "fe0303", "the two non-profit rows")):
                    got, printed = _sum(rows, parts, j), rows[parent][j]
                    if printed is None or got != printed:
                        raise _Refused(f"Tableau 8: {what} sum to {got} for {yrs[j]} against a "
                                       f"printed {parent} of {printed}")
                got = _sum(rows, ("fe0301", "fe0302", "fe0303"), j)
                if got != rows["fe03"][j]:
                    raise _Refused(f"Tableau 8: the three branches sum to {got} for {yrs[j]} "
                                   f"against a printed FE.03 of {rows['fe03'][j]}")
            t8 = {"page": idx + 1, "rows": rows}
            break
        except _Refused as exc:
            log.debug("cm_nasa: page %d rejected as Tableau 8 (%s)", idx + 1, exc)
    if t8 is None:
        raise _Refused("Tableau 8 (Description des financements internationaux) not found")
    gates.append("Tableau 8: all three nesting levels tie EXACTLY in both years, the two "
                 "bilateral states to FE.03.01, the six multilateral bodies to FE.03.02, the "
                 "two non-profit rows to FE.03.03 and the three branches to FE.03")

    # The two tables are independent reads of the same money, so their agreement is a real
    # cross-check and not a restatement of either table's own arithmetic.
    for j in (0, 1):
        if t8["rows"]["fe03"][j] != rev["rows"]["international"][j]:
            raise _Refused(f"Tableau 8's FE.03 is {t8['rows']['fe03'][j]} for {years[j]} "
                           f"against REV.07's {rev['rows']['international'][j]}")
        if t8["rows"]["fe0301"][j] != rev["rows"]["bilateral"][j]:
            raise _Refused(f"Tableau 8's FE.03.01 is {t8['rows']['fe0301'][j]} for {years[j]} "
                           f"against REV.07.01.01's {rev['rows']['bilateral'][j]}")
    gates.append("cross-table: Tableau 8's FE.03 equals the revenue table's REV.07 and its "
                 "FE.03.01 equals REV.07.01.01, EXACTLY, in both years")

    # -- Tableau 9, the intervention split, read for treatment and for its own total ------
    t9 = None
    for idx in _caption_pages(pdf, "selon les domaines d'intervention"):
        try:
            # Read to the end of the page: Tableau 9's subtotal is an unlabelled pair printed
            # BELOW its last labelled row, so stopping at completeness would never reach it.
            yrs, rows, bare = _read_block(pdf, [idx], _T9_LABELS, name="Tableau 9",
                                          stop_when_complete=False)
            _check_years(yrs, years, "Tableau 9")
            want = tuple(_sum(rows, _T9_LABELS.values(), j) for j in (0, 1))
            sub = _find_total(bare, want, "Tableau 9", tol=_FRANC_TOL)
            t9 = {"page": idx + 1, "rows": rows, "subtotal": list(sub)}
            break
        except _Refused as exc:
            log.debug("cm_nasa: page %d rejected as Tableau 9 (%s)", idx + 1, exc)
    if t9 is None:
        raise _Refused("Tableau 9 (the intervention split) not found")
    gates.append(f"Tableau 9: the six intervention rows sum to the printed subtotal to within "
                 f"{_FRANC_TOL} franc in both years")

    # -- Tableau 11, which independently reprints the treatment total ---------------------
    t11 = None
    for idx in _caption_pages(pdf, "Ressources allouees aux soins et au traitement"):
        try:
            yrs, rows, _ = _read_block(pdf, [idx], _T11_LABELS, name="Tableau 11")
            _check_years(yrs, years, "Tableau 11")
            for j in (0, 1):
                got, printed = _sum(rows, ("art", "adherence", "laboratory", "coinfection"), j), \
                    rows["treatment"][j]
                if printed is None or abs(got - printed) > _FRANC_TOL:
                    raise _Refused(f"Tableau 11: the four treatment components sum to {got} "
                                   f"for {yrs[j]} against a printed {printed}")
                if printed != t9["rows"]["treatment"][j]:
                    raise _Refused(f"Tableau 11 reprints treatment for {yrs[j]} as {printed} "
                                   f"against Tableau 9's {t9['rows']['treatment'][j]}")
            t11 = {"page": idx + 1, "rows": rows}
            break
        except _Refused as exc:
            log.debug("cm_nasa: page %d rejected as Tableau 11 (%s)", idx + 1, exc)
    if t11 is None:
        raise _Refused("Tableau 11 (the treatment detail) not found")
    gates.append("Tableau 11: the four treatment components sum to its own printed treatment "
                 "total, and that total equals Tableau 9's treatment row EXACTLY, in both "
                 "years, so the treatment series has two independent readings")

    # -- Tableau 14, a third independent reading of the headline total --------------------
    t14 = None
    for idx in _caption_pages(pdf, "par facteurs de production"):
        try:
            yrs, rows, _ = _read_block(pdf, [idx], _T14_LABELS, name="Tableau 14")
            _check_years(yrs, years, "Tableau 14")
            for j in (0, 1):
                got, printed = _sum(rows, ("current", "capital"), j), rows["total"][j]
                if printed is None or abs(got - printed) > _FRANC_TOL:
                    raise _Refused(f"Tableau 14: current plus capital is {got} for {yrs[j]} "
                                   f"against a printed Total of {printed}")
                if printed != rev["total"][j]:
                    raise _Refused(f"Tableau 14's Total is {printed} for {years[j]} against "
                                   f"the revenue table's {rev['total'][j]}")
            t14 = {"page": idx + 1, "rows": rows}
            break
        except _Refused as exc:
            log.debug("cm_nasa: page %d rejected as Tableau 14 (%s)", idx + 1, exc)
    if t14 is None:
        raise _Refused("Tableau 14 (the production-factor split) not found")
    gates.append("Tableau 14: its Total equals the revenue table's headline EXACTLY in both "
                 "years, which is a third agreeing source for the national total; the table's "
                 "caption says 2018 and 2019 and is stale, so the years come from its own "
                 "column header")

    # -- the Graphique 8 page, used for its 2016 and 2017 domestic rows -------------------
    g8 = _read_graphique_8(pdf)
    for j, year in enumerate(years):
        for key, src, what in (("bilateral", t8["rows"]["fe0301"][j], "Tableau 8's FE.03.01"),
                               ("public", rev["rows"]["public"][j],
                                "the revenue table's REV.01"),
                               ("private", rev["rows"]["private"][j],
                                "the revenue table's REV.06")):
            got = g8["rows"][key].get(year)
            if got != src:
                raise _Refused(f"the Graphique 8 page's {key} row reads {got} for {year} "
                               f"against {what}'s {src}")
        if g8["rows"]["global_fund"].get(year) != t8["rows"]["gf"][j]:
            raise _Refused(f"the Graphique 8 page's Global Fund row reads "
                           f"{g8['rows']['global_fund'].get(year)} for {year} against Tableau "
                           f"8's {t8['rows']['gf'][j]}")
    gates.append("the Graphique 8 page: its bilateral, public, private and Global Fund rows "
                 "all reproduce Tableau 8 and the revenue table EXACTLY for 2020 and 2021, "
                 "which is what licenses reading its 2016 and 2017 domestic rows")

    share = [100.0 * (rev["rows"]["international"][j] or 0) / rev["total"][j] for j in (0, 1)]
    out: Dict[int, Dict[str, Tuple]] = {}
    for j, year in enumerate(years):
        rp, t8p, t9p = rev["page"], t8["page"], t9["page"]
        out[year] = {
            "total": (rev["total"][j], f"unnumbered revenue table, printed page {rp}",
                      "revenue.total"),
            "intl": (rev["rows"]["international"][j],
                     f"unnumbered revenue table, printed page {rp}", "revenue.rev_07"),
            "us": (t8["rows"]["us"][j], f"Tableau 8, printed page {t8p}",
                   "tableau8.fe_03_01_30"),
            "gf": (t8["rows"]["gf"][j], f"Tableau 8, printed page {t8p}",
                   "tableau8.fe_03_02_07"),
            "other_bilateral": ((t8["rows"]["fe0301"][j] or 0) - (t8["rows"]["us"][j] or 0),
                                f"Tableau 8, printed page {t8p}",
                                "tableau8.fe_03_01_hors_etats_unis"),
            "public": (rev["rows"]["public"][j], f"unnumbered revenue table, printed page {rp}",
                       "revenue.rev_01"),
            "private": (rev["rows"]["private"][j],
                        f"unnumbered revenue table, printed page {rp}", "revenue.rev_06"),
            "treatment": (t9["rows"]["treatment"][j], f"Tableau 9, printed page {t9p}",
                          "tableau9.asc_03"),
            "share": (round(share[j], 4), f"the revenue table's REV.07 over its headline, "
                                          f"printed page {rp}", "derived.part_international"),
        }
    return {"years": list(years), "series": out, "gates": gates, "g8": g8}


def _read_graphique_8(pdf) -> Dict:
    """The eight-year financing table above the Graphique 8 caption.

    Read for one purpose: the 2016 and 2017 domestic public and private rows, which the
    2016-2017 assessment does not print. The year order is taken from the table's own header,
    which runs DESCENDING on this page, and every row this connector uses is gated against a
    table that assesses the year.
    """
    for idx in _caption_pages(pdf, "Evolution des financements par principale source"):
        years: Optional[List[int]] = None
        rows: Dict[str, Dict[int, Optional[int]]] = {}
        prev1 = ""
        prev_had_figures = False
        for ln in _lines(pdf.pages[idx]):
            cols = _columns(ln["words"])
            hdr = _year_header(cols, 8)
            if hdr is not None:
                if not rows:
                    years = hdr
                prev1, prev_had_figures = ln["text"], False
                continue
            if years is None:
                prev1, prev_had_figures = ln["text"], False
                continue
            got = _wide_levels(cols, len(years))
            if got is None:
                prev1, prev_had_figures = ln["text"], False
                continue
            label_text, levels = got
            key = None
            for cand in (label_text, prev1, f"{prev1} {label_text}"):
                if prev_had_figures and cand is not label_text:
                    break
                if _norm(cand):
                    key = _match_prefix(cand, _G8_LABELS)
                    if key:
                        break
            if key is not None and key not in rows:
                rows[key] = dict(zip(years, levels))
            prev1, prev_had_figures = ln["text"], True
            if set(_G8_LABELS.values()) <= set(rows):
                return {"page": idx + 1, "years": years, "rows": rows}
        log.debug("cm_nasa: page %d rejected as the Graphique 8 table (header %s, rows %s)",
                  idx + 1, years, sorted(rows))
    raise _Refused("the Graphique 8 financing table was not found")


def _cross_assessment_gates(a: Dict, b: Dict) -> List[str]:
    """Check the Graphique 8 page against the assessment that actually assesses 2016 and 2017.

    This is what licenses the one exception to "an assessment contributes only its own years".
    The Global Fund row is checked and the contradiction is reported, not tolerated: that row
    is used for nothing, so a mismatch is logged rather than refusing the document.
    """
    gates: List[str] = []
    g8 = b["g8"]["rows"]
    for j, year in enumerate(a["years"]):
        got, src = g8["bilateral"].get(year), a["bil"][j]
        if got != src:
            raise _Refused(f"the Graphique 8 page's bilateral row reads {got} for {year} "
                           f"against the 2016-2017 assessment's {src}; the year columns cannot "
                           f"be trusted and the domestic rows are not read")
        residual = a["total"][j] - a["intl"][j]
        domestic = (g8["public"].get(year) or 0) + (g8["private"].get(year) or 0)
        if domestic != residual:
            raise _Refused(f"the Graphique 8 page's domestic rows sum to {domestic} for {year} "
                           f"against the 2016-2017 assessment's residual of {residual}")
    gates.append("cross-assessment: the Graphique 8 page's bilateral row equals the 2016-2017 "
                 "assessment's bilateral subtotal EXACTLY in both years, and its domestic "
                 "public plus private rows reproduce that assessment's domestic residual "
                 "EXACTLY in both years")
    for j, year in enumerate(a["years"]):
        got, src = g8["global_fund"].get(year), a["gf"][j]
        if got != src:
            log.warning("cm_nasa: the Graphique 8 page's Global Fund row reads %s for %d "
                        "against the %d assessment's %s, a contradiction of %s FCFA. The "
                        "Global Fund series comes from the assessments, so nothing emitted "
                        "here depends on that row.", f"{got:,}" if got else got, year, year,
                        f"{src:,}" if src else src, f"{abs((got or 0) - (src or 0)):,}")
    return gates


# -- the single-year assessments ------------------------------------------------------------
# The four earlier reports print one column of figures, so `_year_header` has nothing to find
# and `_figures` has no pair to build. The machinery below is the one-column equivalent. A
# line is a readable row only when EXACTLY ONE of its cells converts through `_to_franc`, and
# a block is anchored on a caption LINE's vertical midpoint and stopped at the first
# caption-shaped line beneath it.
#
# The stop is not cosmetic, and three separate hazards need it. The 2009 report prints
# Tableau 2 and Tableau 3 on one page, both ending in a row labelled "Total", so without the
# stop the first table's reader would take the second table's 28,530,525,154 FCFA for its own
# 5,240,861,092 FCFA. The 2012 report prints Tableau 3 and Tableau 4 on one page the same way.
# And several anchor phrases also match the section heading printed a few lines ABOVE the
# caption, as "4.1.1 Sources de financement" does on the 2009 report's page 23; a reader
# starting from the heading meets the caption first and stops with nothing, which is what
# makes the wrong starting point fail instead of quietly reading the right table from too high
# up the page.
_CAPTION_LINE = re.compile(r"^(tableau|annexe|graphique|figure)\s*\d")


def _single_figures(cols: Sequence[str]) -> Optional[Tuple[str, int]]:
    """A one-column row's label text and its single level, or None.

    Exactly one converting cell is the whole test. Two means the line carries a level and
    something else, which on these documents is a bare integer percentage, and the line is
    not a single-year row. Zero means a heading or a line of prose. The label is everything
    to the LEFT of the converting cell, which drops any percentage column printed to its
    right, as the 2011 report's Tableau 5 prints "19,1" beside its public figure.
    """
    hits = [i for i, c in enumerate(cols) if _to_franc(c) is not None]
    if len(hits) != 1:
        return None
    value = _to_franc(cols[hits[0]])
    if value is None:                                          # pragma: no cover - unreachable
        return None
    return " ".join(cols[:hits[0]]).strip(), value


def _matrix_row(cols: Sequence[str]) -> Optional[Tuple[str, List[int]]]:
    """A REDES matrix row's label text and every figure cell on the line, or None.

    `_single_figures` cannot serve a REDES matrix, which prints several figure columns on
    every row and needs all of them: the last column is the row's own Total and the columns
    before it are the agents that have to add up to it. An explicit dash counts as a zero
    here, because the matrix prints a dash wherever an agent spent nothing and `_to_franc`
    returns None for a dash. The label is everything to the LEFT of the first figure cell,
    and every cell from the first figure to the end of the line must itself be a figure, so
    a line of prose and a line carrying only the tail of a wrapped label both return None.
    """
    cells_in = [str(c) for c in cols if str(c).strip()]
    kinds = [_classify(c) for c in cells_in]
    first = next((i for i, k in enumerate(kinds) if k == "L"), None)
    if first is None or any(k != "L" for k in kinds[first:]):
        return None
    out: List[int] = []
    for cell in cells_in[first:]:
        if cell.strip() in _DASHES:
            out.append(0)
            continue
        value = _to_franc(cell)
        if value is None:                                      # pragma: no cover - unreachable
            return None
        out.append(value)
    return " ".join(cells_in[:first]).strip(), out


def _caption_hits(pdf, phrase: str) -> List[Tuple[int, float]]:
    """Every (page index, line midpoint) whose LINE contains `phrase`.

    `_caption_pages` returns pages, which is enough for a two-year table because that table's
    year header marks where the table starts. A single-year table has no header, so the reader
    needs the caption's own vertical position on the page.
    """
    key = _norm(phrase)
    out: List[Tuple[int, float]] = []
    for i, page in enumerate(pdf.pages):
        try:
            text = page.extract_text() or ""
        except Exception:                                      # pragma: no cover - pdfplumber
            continue
        if key not in _norm(text):
            continue
        for ln in _lines(page):
            if key in _norm(ln["text"]):
                out.append((i, ln["mid"]))
    return out


def _read_single(
    pdf,
    idx: int,
    start_mid: float,
    labels: Dict[str, str],
    *,
    name: str,
    pages: int = 1,
) -> Tuple[Dict[str, int], List[int]]:
    """Read one single-year table below a caption, matching labels on the WHOLE cell.

    Whole-cell matching, not the prefix matching the two-year tables use. The 2007 annexe
    prints "PREVENTION" as a category sub-total and again as the first word of several of its
    own children, and the 2012 report prints "ASC.02 Soins et traitement" above
    "ASC.02.01 Soins ambulatoires", so a prefix match would hand a parent's key to its child.

    Returns the matched rows and the levels of every readable row that matched no label. The
    unmatched levels matter for 2012, whose Tableau 3 and Tableau 5 each print their total as
    a bare figure with no label at all; `_find_single_total` identifies those by arithmetic.
    """
    rows: Dict[str, int] = {}
    bare: List[int] = []
    prev1 = ""
    prev_had_figures = False
    for p in range(idx, min(idx + pages, len(pdf.pages))):
        for ln in _lines(pdf.pages[p]):
            if p == idx and ln["mid"] <= start_mid:
                continue
            if _CAPTION_LINE.match(_norm(ln["text"])):
                return rows, bare
            got = _single_figures(_columns(ln["words"]))
            if got is None:
                prev1, prev_had_figures = ln["text"], False
                continue
            label_text, value = got
            # Two of the 2007 Annexe 2 categories wrap their label onto a second line and
            # print the figure on that second line. "RESSOURCES HUMAINES, RECRUTEMENT ET
            # INCITATION A LA" carries nothing and "RETENTION- CAPITAL HUMAIN 1 316 694 794"
            # carries the level, and the research category wraps the same way. Both preceding
            # lines carry no figures of their own, so the restriction `_read_block` documents
            # applies here unchanged: a line that carries its own figures owns its own label
            # and lends it to nobody.
            cands = [label_text]
            if not prev_had_figures:
                cands.append(f"{prev1} {label_text}")
            key = None
            for cand in cands:
                if _norm(cand):
                    key = _match_label(cand, labels)
                    if key:
                        break
            if key is None:
                bare.append(value)
            elif key in rows:
                if rows[key] != value:
                    raise _Refused(
                        f"{name}: {key} appears twice with different levels, {rows[key]:,} "
                        f"and {value:,}; refusing the table rather than choosing one")
            else:
                rows[key] = value
            prev1, prev_had_figures = ln["text"], True
    return rows, bare


def _find_single_total(bare: Sequence[int], want: int, name: str) -> int:
    """The unlabelled level that satisfies the table's own arithmetic, or a refusal."""
    for value in bare:
        if value == want:
            return value
    raise _Refused(f"{name}: no unlabelled row equals the sum of the components, {want:,}; "
                   f"the candidates were {[format(v, ',') for v in bare]}")


def _single_table(pdf, phrase: str, labels: Dict[str, str], *, name: str,
                  pages: int = 1) -> Tuple[int, Dict[str, int], List[int]]:
    """The first caption hit whose block yields every label, with that block's page number.

    The page number is the PDF page, one-based. For three of the four reports that is also
    the folio printed at the foot of the page, and for the 2009 report the printed folio runs
    one behind, so `source_table` below says "pdf page" and means it.
    """
    last: Optional[_Refused] = None
    for idx, mid in _caption_hits(pdf, phrase):
        try:
            rows, bare = _read_single(pdf, idx, mid, labels, name=name, pages=pages)
            missing = sorted(set(labels.values()) - set(rows))
            if missing:
                raise _Refused(f"{name}: rows not found: {', '.join(missing)}")
            return idx + 1, rows, bare
        except _Refused as exc:
            last = exc
            log.debug("cm_nasa: pdf page %d rejected as %s (%s)", idx + 1, name, exc)
    tail = f"; the last candidate failed because {last}" if last else ""
    raise _Refused(f"{name} ({phrase}) not found{tail}")


def _joined(pdf, first: int, count: int = 2) -> str:
    """`count` pages from the one-based `first`, whitespace collapsed, for the prose checks."""
    out: List[str] = []
    for i in range(first - 1, min(first - 1 + count, len(pdf.pages))):
        try:
            out.append(pdf.pages[i].extract_text() or "")
        except Exception:                                      # pragma: no cover - pdfplumber
            continue
    return re.sub(r"\s+", " ", " ".join(out))


# -- the 2007 assessment --------------------------------------------------------------------
# All five of the 2007 annexes share their descriptive caption text word for word, so the
# descriptive phrase alone cannot find Annexe 1 and the annexe NUMBER has to be part of the
# anchor. That is the one place in this module where a printed table number is trusted, and
# the reason is that the 2007 report has no other way to tell its annexes apart. The contents
# page carries both phrases too, and both contents hits fail at once, because the line below
# Annexe 1's contents entry is Annexe 2's contents entry and the line below Annexe 2's is
# Annexe 3's, all of them caption-shaped.
_P07_A1 = "Annexe 1 : Répartition détaillée du montant estimé de la dépense"
_P07_A2 = "Annexe 2 : Répartition détaillée du montant estimé de la dépense"

_S07_A1 = {
    "fonds public sous total": "public",
    "fonds prives sous total": "private_cat",
    "fonds internationaux sous total": "intl_cat",
    "organisations internationales a but non lucratives et fondations sous total": "ngo_cat",
    "organismes bilateraux": "bilateral",
    "agences multilaterales": "multilateral",
    "gouvernement des etats unis d amerique": "us",
    "the global fund to fight aids tuberculosis and malaria": "gf",
    "total": "total",
}
_S07_A1_PARTS = ("public", "private_cat", "intl_cat", "ngo_cat")

# "soin" and "soins" are both singular-looking in this annexe's own spelling, and the two
# wrapped keys below are the previous line joined to the figure line, exactly as the document
# breaks them.
_S07_A2 = {
    "prevention": "prevention",
    "soin et traitement": "treatment",
    "soins externe": "outpatient",
    "soins internes": "inpatient",
    "orphelins et enfants vulnerables oev": "oev",
    "gestion de programmes et renforcement de l administration": "admin",
    "ressources humaines recrutement et incitation a la retention capital humain": "hr",
    "asc 6 protection sociale et services sociaux excluant oev": "social",
    "environnement favorable et developpement communautaire": "environment",
    "recherche sur le vih sida excluant la recherche operationnelle": "research",
    "total": "total",
}
_S07_A2_PARTS = ("prevention", "treatment", "oev", "admin", "hr", "social", "environment",
                 "research")


def _read_2007(pdf) -> Dict:
    """The 2007 assessment: Annexe 1 by source and by donor, Annexe 2 by category."""
    gates: List[str] = []

    p1, a1, _ = _single_table(pdf, _P07_A1, _S07_A1, name="Annexe 1", pages=2)
    got = sum(a1[k] for k in _S07_A1_PARTS)
    if got != a1["total"]:
        raise _Refused(f"Annexe 1: the four top-level sub-totals sum to {got:,} against a "
                       f"printed total of {a1['total']:,}")
    gates.append(f"Annexe 1: the public, private, international and international-NGO "
                 f"sub-totals sum EXACTLY to the printed total of {a1['total']:,} FCFA")
    components = a1["bilateral"] + a1["multilateral"]
    if components != a1["intl_cat"]:
        raise _Refused(f"Annexe 1: the bilateral and multilateral sub-totals sum to "
                       f"{components:,} against a printed international sub-total of "
                       f"{a1['intl_cat']:,}")
    gates.append("Annexe 1: the bilateral and multilateral sub-totals sum EXACTLY to the "
                 "printed international sub-total, so the United States row and the "
                 "derived other-bilateral row sit inside a total that reproduces")

    p2, a2, _ = _single_table(pdf, _P07_A2, _S07_A2, name="Annexe 2", pages=2)
    if a2["total"] != a1["total"]:
        raise _Refused(f"Annexe 2's printed total of {a2['total']:,} disagrees with Annexe "
                       f"1's {a1['total']:,}; the two annexes may not belong together")
    gates.append("cross-annexe: Annexe 2's printed total equals Annexe 1's EXACTLY")
    children = a2["outpatient"] + a2["inpatient"]
    if abs(children - a2["treatment"]) > _FRANC_TOL:
        raise _Refused(f"Annexe 2: outpatient care {a2['outpatient']:,} plus inpatient care "
                       f"{a2['inpatient']:,} is {children:,} against a printed care and "
                       f"treatment total of {a2['treatment']:,}")
    gates.append(f"Annexe 2: the care and treatment category of {a2['treatment']:,} FCFA, "
                 f"the one figure this edition takes from Annexe 2, reproduces from its own "
                 f"two children, outpatient care and inpatient care, to within "
                 f"{abs(children - a2['treatment'])} franc")

    # Disclosed and logged, deliberately not a gate on the emitted figure. The eight ASC
    # categories fall short of the printed grand total, and no single category is
    # responsible: every one of the eight reproduces from its own listed children, six of
    # them to the franc and two within one franc of rounding. The gap happens to equal the
    # "Traitement des infections opportunistes" leaf of 9,444,575 FCFA, but that leaf sits
    # inside inpatient care, which the gate above has already shown is counted in the care
    # and treatment total to within a franc, so the equality is arithmetic coincidence and
    # not a diagnosis.
    cats = sum(a2[k] for k in _S07_A2_PARTS)
    gap = a2["total"] - cats
    if abs(gap) > _A2_2007_GAP:
        raise _Refused(f"Annexe 2: the eight categories sum to {cats:,}, which is {gap:,} "
                       f"from the printed total of {a2['total']:,}; the documented gap is "
                       f"{_A2_2007_GAP:,} FCFA and anything larger is a different defect")
    if gap:
        log.warning("cm_nasa: the 2007 Annexe 2 categories sum to %s FCFA against a printed "
                    "total of %s, a gap of %s FCFA (%.3f per cent) that no single category "
                    "accounts for, since each of the eight reproduces from its own children. "
                    "Care and treatment is the only figure taken from this annexe and that "
                    "figure reproduces from its own two children to within one franc.",
                    f"{cats:,}", f"{a2['total']:,}", f"{gap:,}", 100.0 * gap / a2["total"])

    w1, w2 = f"Annexe 1, pdf page {p1}", f"Annexe 2, pdf page {p2}"
    series = {
        "total": (a1["total"], w1, "annexe1.total"),
        "public": (a1["public"], w1, "annexe1.fonds_publics"),
        "us": (a1["us"], w1, "annexe1.gouvernement_etats_unis"),
        "gf": (a1["gf"], w1, "annexe1.global_fund"),
        "other_bilateral": (a1["bilateral"] - a1["us"],
                            f"{w1}, the bilateral sub-total less the United States row",
                            "annexe1.bilateral_hors_etats_unis"),
        "treatment": (a2["treatment"], w2, "annexe2.soin_et_traitement"),
    }
    return {"years": [2007], "series": {2007: series}, "gates": gates}


# -- the 2009 assessment --------------------------------------------------------------------
_P09_T1 = "Sources de financement"
_P09_T9 = "Situation globale des depenses par intervention"

_S09_T1 = {
    "fonds publics": "public",
    "fonds prives": "private",
    "fonds internationaux": "intl",
    "total": "total",
}
_S09_T9 = {
    "prevention": "prevention",
    "soins et traitement": "treatment",
    "orphelins et autres enfants rendus vulnerables oev": "oev",
    "gestion et administration de programme": "admin",
    "ressources humaines": "hr",
    "protection sociale et services sociaux": "social",
    "environnement favorable": "environment",
    "recherche liee au vih a l exception de la recherche operationnelle": "research",
    "total": "total",
}
_S09_T9_PARTS = ("prevention", "treatment", "oev", "admin", "hr", "social", "environment",
                 "research")

# Tableau 1 stops at the three revenue sources. The REDES matrix in Annexe 3 goes one level
# deeper and names the financing bodies, and this block exists to read two of them, being the
# American government and the other-bilateral residual. The matrix prints six figure columns,
# being Secteur public, Secteur privé, Organismes acquéreurs internationaux, Organismes
# multilatéraux administrant des ressources externes, Organisations et fondations
# internationales à but non lucratif, and Total.
#
# Columns four and five are NOT a further split of a row. Columns four and five are nested
# inside column three, and two rows of the matrix prove it on their own arithmetic: the
# UNICEF row prints "‐ ~ ‐ ~ 1480166210 ~ 1480166210 ~ ‐ ~ 1480166210", where column four
# repeats column three, and the Alliance internationale row prints
# "‐ ~ ‐ ~ 8549648 ~ ‐ ~ 8549648 ~ 8549648", where column five repeats column three. In both
# rows the printed Total equals the sum of the first three columns alone. The across-row gate
# below therefore adds columns one to three and stops there, and columns four and five are
# refused rather than read.
_P09_A3 = "Source de financement et Agents de financements"
_A3_09_COLS = 6
_A3_09_AGENTS = 3

_S09_A3 = {
    "fonds publics": "public",
    "fonds prives": "private",
    "contributions bilaterales directes": "bilateral",
    "gouvernement canadien": "bil_ca",
    "gouvernement allemand": "bil_de",
    "gouvernement neerlandais": "bil_nl",
    "gouvernement americain": "bil_us",
}
# The four governments the matrix prints under the bilateral sub-total. Reading all four,
# when only the American government is emitted, is what lets the sub-total be checked from
# below as well as from the side.
_S09_A3_GOVTS = ("bil_ca", "bil_de", "bil_nl", "bil_us")


def _read_matrix_2009(pdf, page_idx: int,
                      start_mid: float) -> Tuple[Dict[str, List[int]], List[List[int]]]:
    """One page of the 2009 REDES matrix below `start_mid`, by label and then unlabelled.

    The unlabelled rows are returned because the matrix prints its grand total with no label
    at all, and that row is what exposes the excess disclosed in `_read_annexe3_2009`.
    """
    rows: Dict[str, List[int]] = {}
    bare: List[List[int]] = []
    for ln in _lines(pdf.pages[page_idx]):
        if ln["mid"] <= start_mid:
            continue
        if _CAPTION_LINE.match(_norm(ln["text"])):
            break
        got = _matrix_row(_columns(ln["words"]))
        if got is None:
            continue
        label, cells = got
        if len(cells) != _A3_09_COLS:
            continue
        key = _match_label(label, _S09_A3) if _norm(label) else None
        if key is None:
            bare.append(cells)
        elif key in rows and rows[key] != cells:
            raise _Refused(f"Annexe 3: the {key} row is printed twice on pdf page "
                           f"{page_idx + 1} with different figures")
        else:
            rows[key] = cells
    return rows, bare


def _read_annexe3_2009(pdf, t1: Dict[str, int], gates: List[str]) -> Optional[Dict]:
    """The 2009 American and other-bilateral levels from the Annexe 3 matrix, or None.

    None rather than a refusal, for the reason `_read_2010` gives: Tableau 1 and Tableau 9
    tie to each other to the franc, and an annexe that has been redrawn should not take away
    the six rows that do not depend on the annexe. Every gate below has to pass before either
    donor level is believed, and a gate that fails drops both donor levels and nothing else.
    """
    hits = _caption_hits(pdf, _P09_A3)
    if not hits:
        log.warning("cm_nasa: the 2009 Annexe 3 REDES matrix was not found, so no 2009 donor "
                    "row is emitted. The six rows Tableau 1 and Tableau 9 produce are "
                    "unaffected.")
        return None
    idx, mid = hits[0]
    page = idx + 1
    rows, bare = _read_matrix_2009(pdf, idx, mid)
    missing = sorted(set(_S09_A3.values()) - set(rows))
    if missing:
        log.warning("cm_nasa: the 2009 Annexe 3 matrix on pdf page %d does not carry the "
                    "rows %s, so no 2009 donor row is emitted.", page, ", ".join(missing))
        return None

    # Gate 1, every row read closes across its own three disjoint agent columns.
    for key in sorted(rows):
        across = sum(rows[key][:_A3_09_AGENTS])
        if across != rows[key][-1]:
            log.warning("cm_nasa: in the 2009 Annexe 3 matrix on pdf page %d the %s row's "
                        "three agent columns sum to %s FCFA against its own printed Total of "
                        "%s. No 2009 donor row is emitted.",
                        page, key, f"{across:,}", f"{rows[key][-1]:,}")
            return None
    gates.append(f"Annexe 3, pdf page {page}: each of the {len(rows)} rows read sums EXACTLY "
                 f"across its three disjoint agent columns to its own printed Total")

    # Gate 2, the four governments sum up to the bilateral sub-total. Passing this gate is
    # also what makes the emitted other-bilateral residual safe, because the residual left
    # after removing the American government is then exactly the Canadian, German and Dutch
    # governments the matrix names, and no unnamed body hides inside it.
    govts = sum(rows[k][-1] for k in _S09_A3_GOVTS)
    if govts != rows["bilateral"][-1]:
        log.warning("cm_nasa: in the 2009 Annexe 3 matrix on pdf page %d the four named "
                    "governments sum to %s FCFA against a printed bilateral sub-total of %s. "
                    "No 2009 donor row is emitted.",
                    page, f"{govts:,}", f"{rows['bilateral'][-1]:,}")
        return None
    gates.append(f"Annexe 3: the Canadian, German, Dutch and American governments sum EXACTLY "
                 f"to the printed Contributions bilatérales directes of "
                 f"{rows['bilateral'][-1]:,} FCFA, so the residual left after removing the "
                 f"American government is exactly the other three governments the matrix "
                 f"names")

    # Gate 3, the same sum taken down each agent column separately, which is a check the
    # across-row gate and the sub-total gate cannot stand in for.
    for col in range(_A3_09_AGENTS):
        down = sum(rows[k][col] for k in _S09_A3_GOVTS)
        if down != rows["bilateral"][col]:
            log.warning("cm_nasa: in the 2009 Annexe 3 matrix on pdf page %d the four named "
                        "governments sum to %s FCFA in agent column %d against the bilateral "
                        "sub-total's own %s. No 2009 donor row is emitted.",
                        page, f"{down:,}", col + 1, f"{rows['bilateral'][col]:,}")
            return None
    gates.append("Annexe 3: the four governments sum EXACTLY to the bilateral sub-total in "
                 "every one of the three agent columns taken separately, as well as in the "
                 "Total column")

    # Gate 4, the matrix and Tableau 1 are the same accounts. Fonds internationaux is left
    # out of this gate because the matrix prints that row's Total on a line of its own,
    # leaving the row five cells wide, so `_read_matrix_2009` does not return it.
    for key, printed in (("public", "Fonds publics"), ("private", "Fonds privés")):
        if rows[key][-1] != t1[key]:
            log.warning("cm_nasa: the 2009 Annexe 3 matrix on pdf page %d prints %s of %s "
                        "FCFA against Tableau 1's %s. No 2009 donor row is emitted.",
                        page, printed, f"{rows[key][-1]:,}", f"{t1[key]:,}")
            return None
    gates.append("cross-table: Annexe 3's Fonds publics and Fonds privés rows each equal "
                 "Tableau 1's EXACTLY, so the matrix and the summary table are the same "
                 "accounts")

    # Gate 5, the matrix is printed twice and the two printings have to agree. Opportunistic,
    # because a report that printed the matrix once should still yield its donor rows.
    second: Dict[str, List[int]] = {}
    if idx + 1 < len(pdf.pages):
        second, _ = _read_matrix_2009(pdf, idx + 1, 0.0)
    shared = sorted(set(rows) & set(second))
    if shared:
        disagree = [k for k in shared if rows[k] != second[k]]
        if disagree:
            log.warning("cm_nasa: the 2009 Annexe 3 matrix is printed twice, on pdf pages %d "
                        "and %d, and the two printings disagree on %s. No 2009 donor row is "
                        "emitted.", page, page + 1, ", ".join(disagree))
            return None
        gates.append(f"Annexe 3: the matrix is printed twice, on pdf pages {page} and "
                     f"{page + 1}, and the {len(shared)} rows read from both printings agree "
                     f"cell for cell")
    else:
        log.warning("cm_nasa: the 2009 Annexe 3 matrix was found once only, on pdf page %d, "
                    "so the duplicate-printing check did not run. The five arithmetic gates "
                    "on the bilateral block still passed.", page)

    # Disclosed, affecting nothing emitted. The matrix's unlabelled grand-total row does not
    # close across its own agent columns, and the excess is the same amount by which the
    # three children of Fonds internationaux overshoot their parent.
    for cells in bare:
        if cells[-1] != t1["total"]:
            continue
        across = sum(cells[:_A3_09_AGENTS])
        if across != cells[-1]:
            log.warning("cm_nasa: the 2009 Annexe 3 matrix's grand-total row on pdf page %d "
                        "sums to %s FCFA across its three agent columns against its own "
                        "printed Total of %s, an excess of %s FCFA. The excess arises in the "
                        "multilateral block, above and beside the bilateral rows, and the "
                        "bilateral block closes in three independent directions of its own, "
                        "so the American and other-bilateral levels are emitted and the "
                        "Global Fund level is refused.",
                        page, f"{across:,}", f"{cells[-1]:,}", f"{across - cells[-1]:,}")
        break

    return {
        "page": page,
        "us": rows["bil_us"][-1],
        "other_bilateral": rows["bilateral"][-1] - rows["bil_us"][-1],
    }


def _read_2009(pdf) -> Dict:
    """The 2009 assessment: Tableau 1 by source, Tableau 9 by intervention, Annexe 3 by body."""
    gates: List[str] = []

    p1, t1, _ = _single_table(pdf, _P09_T1, _S09_T1, name="Tableau 1")
    got = t1["public"] + t1["private"] + t1["intl"]
    if got != t1["total"]:
        raise _Refused(f"Tableau 1: the three sources sum to {got:,} against a printed total "
                       f"of {t1['total']:,}")
    gates.append(f"Tableau 1: the public, private and international sources sum EXACTLY to "
                 f"the printed total of {t1['total']:,} FCFA")

    p9, t9, _ = _single_table(pdf, _P09_T9, _S09_T9, name="Tableau 9")
    got9 = sum(t9[k] for k in _S09_T9_PARTS)
    if got9 != t9["total"]:
        raise _Refused(f"Tableau 9: the eight interventions sum to {got9:,} against a printed "
                       f"total of {t9['total']:,}")
    gates.append("Tableau 9: the eight intervention rows sum EXACTLY to the printed total")
    if t9["total"] != t1["total"]:
        raise _Refused(f"Tableau 9's printed total of {t9['total']:,} disagrees with Tableau "
                       f"1's {t1['total']:,}; the two tables may not belong together")
    gates.append("cross-table: Tableau 9's printed total equals Tableau 1's EXACTLY, so the "
                 "source side and the intervention side of this assessment agree to the franc")

    # Disclosed, affecting nothing emitted. The narrative on the Tableau 1 page states a
    # national total two billion francs above the table printed beneath the sentence.
    prose = re.search(r"(\d[\d ]*\d)\s*FCFA", _joined(pdf, p1, 1), re.I)
    if prose:
        stated = _to_franc(prose.group(1))
        if stated is not None and stated != t1["total"] and abs(stated - t1["total"]) < 10**10:
            log.warning("cm_nasa: the 2009 narrative on pdf page %d states a national total "
                        "of %s FCFA against its own Tableau 1 total of %s, a difference of "
                        "%s FCFA. The tables tie to each other exactly and nothing emitted "
                        "depends on the sentence.",
                        p1, f"{stated:,}", f"{t1['total']:,}",
                        f"{abs(stated - t1['total']):,}")

    share = 100.0 * t1["intl"] / t1["total"]
    w1, w9 = f"Tableau 1, pdf page {p1}", f"Tableau 9, pdf page {p9}"
    series = {
        "total": (t1["total"], w1, "tableau1.total"),
        "public": (t1["public"], w1, "tableau1.fonds_publics"),
        "private": (t1["private"], w1, "tableau1.fonds_prives"),
        "intl": (t1["intl"], w1, "tableau1.fonds_internationaux"),
        "treatment": (t9["treatment"], w9, "tableau9.soins_et_traitement"),
        "share": (round(share, 4), f"{w1}, international over total",
                  "derived.part_internationale"),
    }

    a3 = _read_annexe3_2009(pdf, t1, gates)
    if a3 is not None:
        w3 = f"Annexe 3 REDES matrix, pdf page {a3['page']}"
        series["us"] = (a3["us"], w3, "annexe3.gouvernement_americain")
        series["other_bilateral"] = (
            a3["other_bilateral"],
            f"{w3}, Contributions bilatérales directes less the American government",
            "derived.autres_bilateraux")

    return {"years": [2009], "series": {2009: series}, "gates": gates}


# -- the 2011 assessment, which also carries 2010 ---------------------------------------------
_P11_T5 = "Repartition des depenses par source de financement en 2011"
_P11_T6 = "Repartition des depenses par chapitre d'intervention en 2011"

_S11_T5 = {
    "fs 01 fonds publics": "public",
    "fs 02 fonds prives": "private",
    "fs 03 fonds internationaux": "intl",
    "total general": "total",
}
_S11_T6 = {
    "asc 01 prevention": "prevention",
    "asc 02 soins et traitement": "treatment",
    "asc 03 orphelins et autres enfants rendus vulnerables oev": "oev",
    "asc 04 gestion et administration de programmes": "admin",
    "asc 05 ressources humaines": "hr",
    "asc 06 protection sociale et services sociaux": "social",
    "asc 07 environnement favorable": "environment",
    "asc 08 recherche liee au vih a l exception de la recherche operationnelle": "research",
    "total general": "total",
}
_S11_T6_PARTS = ("prevention", "treatment", "oev", "admin", "hr", "social", "environment",
                 "research")

# The 2011 narrative, read over the Tableau 5 page and the page after it. `_joined` has
# already collapsed every run of whitespace to one space, so the thousands spaces inside a
# figure are ordinary spaces by the time these patterns run.
_P11_COMPONENT = re.compile(r"pour un montant de\s+(\d[\d ]*\d)")
_P11_TOTAL = re.compile(r"pour le montant total de\s+(\d[\d ]*\d)\s*Fcfa", re.I)
_P2010_TOTAL = re.compile(r"(\d[\d ]*\d)\s*Fcfa\s+en\s+2010\s+contre\s+(\d[\d ]*\d)\s*Fcfa",
                          re.I)
_P2010_PART = re.compile(
    r"contre\s+(\d[\d ]*\d)\s*F\s*CFA\s*\(\s*(\d+[.,]\d+)\s*%\s*\)\s*en\s+2010", re.I)

# The 2011 report carries two tables under the heading Annexe 3, one of them the UNGASS
# reporting table and the other the source-of-financing tree this block reads, so the anchor
# has to carry the descriptive words and not the annexe number alone.
#
# Unlike the 2009 matrix this table is a plain two-column tree, an FS code with its level and
# its share of its own parent, so `_single_table` reads it unchanged. Whole-cell label
# matching is what keeps the tree's levels apart, because a prefix match on "FS.03.01" would
# take the American government's "FS.03.01.22" line as well.
_P11_A3 = "Annexe 3 : Repartition par source de financement"

_S11_A3 = {
    "fs 01 fonds publics": "public",
    "fs 02 fonds prives": "private",
    "fs 03 fonds internationaux": "intl",
    "fs 03 01 contributions bilaterales directes": "bilateral",
    "fs 03 01 07 gouvernement francais": "bil_fr",
    "fs 03 01 08 gouvernement allemand": "bil_de",
    "fs 03 01 22 gouvernement americain": "bil_us",
    "fs 03 02 organismes multilateraux administrant des subventions pre affectees": "multi",
    "fs 03 02 04 organisation internationale du travail oit": "mul_ilo",
    "fs 03 02 07 fonds mondial de lutte contre le sida la tuberculose et le paludisme": "gf",
    "fs 03 02 08 secretariat de l onusida": "mul_unaids",
    "fs 03 02 09 fonds des nations unies pour l enfance unicef": "mul_unicef",
    "fs 03 02 11 programme des nations unies pour le developpement pnud": "mul_undp",
    "fs 03 02 12 organisation des nations unies pour l education la science et la culture "
    "unesco": "mul_unesco",
    "fs 03 02 13 haut commissariat des nations unies pour les refugies hcr": "mul_unhcr",
    # The report spells the population fund UNPFA, not UNFPA, so the key follows the report.
    "fs 03 02 17 fonds des nations unies pour la population unpfa": "mul_unfpa",
    "fs 03 02 20 organisation mondiale de la sante oms": "mul_who",
    "fs 03 03 organisations et fondations internationales a but non lucratif": "ngo",
    "total general": "total",
}
_S11_A3_GOVTS = ("bil_fr", "bil_de", "bil_us")
# All nine agencies the annexe prints under FS.03.02. Only the Global Fund is emitted, and
# the other eight are read so that the Global Fund's level can be checked as one of nine that
# reproduce their printed parent, which is a stronger test than containment inside it.
_S11_A3_MULTI = ("mul_ilo", "gf", "mul_unaids", "mul_unicef", "mul_undp", "mul_unesco",
                 "mul_unhcr", "mul_unfpa", "mul_who")
_S11_A3_INTL = ("bilateral", "multi", "ngo")


def _read_annexe3_2011(pdf, t5: Dict[str, int], gates: List[str]) -> Optional[Dict]:
    """The 2011 American, Global Fund and other-bilateral levels from Annexe 3, or None.

    None rather than a refusal, on the same reasoning as `_read_annexe3_2009`: Tableau 5 and
    Tableau 6 tie to each other to the franc, so an annexe that cannot be read should cost
    the three donor rows and nothing else.
    """
    try:
        page, a3, _ = _single_table(pdf, _P11_A3, _S11_A3, name="Annexe 3", pages=2)
    except _Refused as exc:
        log.warning("cm_nasa: the 2011 Annexe 3 source-of-financing table could not be read "
                    "(%s), so no 2011 donor row is emitted. The six rows Tableau 5 and "
                    "Tableau 6 produce are unaffected.", exc)
        return None

    # The tree has to close at every level that carries an emitted figure. Passing the first
    # of these gates is also what makes the emitted other-bilateral residual safe: with the
    # three named governments adding up to their printed parent, the residual left after
    # removing the American government is exactly the French and German governments.
    closes = (
        ("the French, German and American governments", sum(a3[k] for k in _S11_A3_GOVTS),
         a3["bilateral"], "FS.03.01 Contributions bilatérales directes"),
        ("the nine multilateral agencies", sum(a3[k] for k in _S11_A3_MULTI), a3["multi"],
         "FS.03.02 Organismes multilatéraux administrant des subventions pré-affectées"),
        ("FS.03.01, FS.03.02 and FS.03.03", sum(a3[k] for k in _S11_A3_INTL), a3["intl"],
         "FS.03 Fonds internationaux"),
        ("FS.01, FS.02 and FS.03", a3["public"] + a3["private"] + a3["intl"], a3["total"],
         "Total général"),
    )
    for what, got, want, printed in closes:
        if got != want:
            log.warning("cm_nasa: in the 2011 Annexe 3 on pdf page %d, %s sum to %s FCFA "
                        "against a printed %s of %s. No 2011 donor row is emitted.",
                        page, what, f"{got:,}", printed, f"{want:,}")
            return None
    gates.append(f"Annexe 3, pdf page {page}: the French, German and American governments sum "
                 f"EXACTLY to the printed FS.03.01 of {a3['bilateral']:,} FCFA, so the "
                 f"residual left after removing the American government is exactly the French "
                 f"and German governments")
    gates.append(f"Annexe 3: the nine agencies printed under FS.03.02, the Global Fund among "
                 f"them, sum EXACTLY to the printed FS.03.02 of {a3['multi']:,} FCFA")
    gates.append("Annexe 3: FS.03.01, FS.03.02 and FS.03.03 sum EXACTLY to the printed FS.03, "
                 "and FS.01, FS.02 and FS.03 sum EXACTLY to the printed Total général")

    # Annexe 3 and Tableau 5 are two independently typeset tables twenty-odd pages apart, so
    # agreement between them at all four levels is the strongest check available here.
    for key, printed in (("public", "FS.01"), ("private", "FS.02"), ("intl", "FS.03"),
                         ("total", "Total général")):
        if a3[key] != t5[key]:
            log.warning("cm_nasa: the 2011 Annexe 3 on pdf page %d prints %s of %s FCFA "
                        "against Tableau 5's %s. No 2011 donor row is emitted.",
                        page, printed, f"{a3[key]:,}", f"{t5[key]:,}")
            return None
    gates.append("cross-table: Annexe 3's FS.01, FS.02, FS.03 and Total général each equal "
                 "Tableau 5's EXACTLY, so the donor tree and the summary table are the same "
                 "accounts")

    return {
        "page": page,
        "us": a3["bil_us"],
        "gf": a3["gf"],
        "other_bilateral": a3["bilateral"] - a3["bil_us"],
    }


def _read_2011(pdf) -> Dict:
    """The 2011 assessment: Tableau 5 by source, Tableau 6 by chapter, Annexe 3 by body, and
    the 2010 sentence."""
    gates: List[str] = []

    p5, t5, _ = _single_table(pdf, _P11_T5, _S11_T5, name="Tableau 5")
    got = t5["public"] + t5["private"] + t5["intl"]
    if got != t5["total"]:
        raise _Refused(f"Tableau 5: the three sources sum to {got:,} against a printed total "
                       f"of {t5['total']:,}")
    gates.append(f"Tableau 5: the public, private and international sources sum EXACTLY to "
                 f"the printed Total général of {t5['total']:,} FCFA")

    p6, t6, _ = _single_table(pdf, _P11_T6, _S11_T6, name="Tableau 6")
    got6 = sum(t6[k] for k in _S11_T6_PARTS)
    if got6 != t6["total"]:
        raise _Refused(f"Tableau 6: the eight chapters sum to {got6:,} against a printed "
                       f"total of {t6['total']:,}")
    gates.append("Tableau 6: the eight intervention chapters sum EXACTLY to the printed "
                 "Total général")
    if t6["total"] != t5["total"]:
        raise _Refused(f"Tableau 6's printed total of {t6['total']:,} disagrees with Tableau "
                       f"5's {t5['total']:,}; the two tables may not belong together")
    gates.append("cross-table: Tableau 6's printed total equals Tableau 5's EXACTLY")

    text = _joined(pdf, p5, 2)

    # The narrative's three international components tie exactly to Tableau 5's FS.03, which
    # is what makes the same passage's 2010 sentence worth reading. Optional in the sense
    # that a redrafted sentence should not refuse a document whose tables tie, but blocking
    # once the three components are found and do not add up.
    parts = [_to_franc(m) for m in _P11_COMPONENT.findall(text)]
    if len(parts) == 3 and all(p is not None for p in parts):
        total_parts = sum(p for p in parts if p is not None)
        if total_parts != t5["intl"]:
            raise _Refused(f"the 2011 narrative's three international components sum to "
                           f"{total_parts:,} against Tableau 5's printed FS.03 of "
                           f"{t5['intl']:,}; the narrative and the table disagree")
        gates.append("the narrative's three international components, multilateral, "
                     "bilateral and international non-governmental, sum EXACTLY to Tableau "
                     "5's printed FS.03")
    else:
        log.warning("cm_nasa: the 2011 narrative's three international components were not "
                    "found, so that cross-check did not run; Tableau 5 and Tableau 6 still "
                    "tie to each other exactly.")

    # Disclosed, affecting nothing emitted.
    stated = _P11_TOTAL.search(text)
    if stated:
        value = _to_franc(stated.group(1))
        if value is not None and value != t5["total"]:
            log.warning("cm_nasa: the 2011 narrative states a national total of %s FCFA "
                        "against Tableau 5's %s, a difference of %s FCFA. Tableau 5's own "
                        "three sources reproduce its total exactly and Tableau 6 agrees "
                        "with it, so the table is taken and the sentence is not.",
                        f"{value:,}", f"{t5['total']:,}", f"{abs(value - t5['total']):,}")

    out: Dict[int, Dict[str, Tuple]] = {}
    intl_2010 = _read_2010(text, t5["intl"], gates)
    if intl_2010 is not None:
        out[2010] = {
            "intl": (intl_2010,
                     f"the 2011 report's narrative beside Tableau 5, pdf pages {p5} and "
                     f"{p5 + 1}, which states the 2010 international total explicitly",
                     "narratif.fonds_internationaux_2010"),
        }

    share = 100.0 * t5["intl"] / t5["total"]
    w5, w6 = f"Tableau 5, pdf page {p5}", f"Tableau 6, pdf page {p6}"
    out[2011] = {
        "total": (t5["total"], w5, "tableau5.total_general"),
        "public": (t5["public"], w5, "tableau5.fs01"),
        "private": (t5["private"], w5, "tableau5.fs02"),
        "intl": (t5["intl"], w5, "tableau5.fs03"),
        "treatment": (t6["treatment"], w6, "tableau6.asc02"),
        "share": (round(share, 4), f"{w5}, FS.03 over Total général",
                  "derived.part_internationale"),
    }

    a3 = _read_annexe3_2011(pdf, t5, gates)
    if a3 is not None:
        wa = f"Annexe 3, pdf page {a3['page']}"
        out[2011]["us"] = (a3["us"], wa, "annexe3.fs03_01_22")
        out[2011]["gf"] = (a3["gf"], wa, "annexe3.fs03_02_07")
        out[2011]["other_bilateral"] = (
            a3["other_bilateral"],
            f"{wa}, FS.03.01 less the American government",
            "derived.autres_bilateraux")

    return {"years": sorted(out), "series": out, "gates": gates}


def _read_2010(text: str, intl_2011: int, gates: List[str]) -> Optional[int]:
    """The 2010 international total from the 2011 report's narrative, or None.

    Returns None rather than refusing, because a 2011 report whose tables tie should still
    emit 2011 when its narrative has been redrafted. Every gate here has to pass before a
    2010 figure is believed, and the gates are set out in the module docstring.
    """
    found = _P2010_TOTAL.search(text)
    if not found:
        log.warning("cm_nasa: the 2011 narrative's 2010 comparison sentence was not found, "
                    "so no 2010 row is emitted. 2011 is unaffected.")
        return None
    value, companion = _to_franc(found.group(1)), _to_franc(found.group(2))
    if value is None or companion is None:
        return None
    if companion != intl_2011:
        log.warning("cm_nasa: the 2011 narrative's 2010 sentence prints %s FCFA beside the "
                    "2010 figure, against Tableau 5's printed FS.03 of %s. The sentence "
                    "cannot be shown to be comparing 2010 with 2011, so no 2010 row is "
                    "emitted.", f"{companion:,}", f"{intl_2011:,}")
        return None

    printed = _P2010_PART.findall(text)
    if len(printed) != 2:
        log.warning("cm_nasa: the 2011 narrative names %d of the two 2010 components with a "
                    "printed share, so the 2010 total of %s FCFA could not be confirmed "
                    "against a second reading and no 2010 row is emitted.",
                    len(printed), f"{value:,}")
        return None
    checked: List[str] = []
    for cell, pct in printed:
        level = _to_franc(cell)
        if level is None:
            return None
        want = float(pct.replace(",", "."))
        got = 100.0 * level / value
        if abs(got - want) > _PCT_TOL_2010:
            log.warning("cm_nasa: the 2011 narrative prints a 2010 share of %s per cent for "
                        "%s FCFA, against %.4f per cent recomputed over the stated 2010 "
                        "total of %s FCFA. No 2010 row is emitted.",
                        pct, f"{level:,}", got, f"{value:,}")
            return None
        checked.append(f"{want} per cent for {level:,} FCFA")
    gates.append(f"the 2011 narrative's 2010 sentence prints Tableau 5's FS.03 of "
                 f"{intl_2011:,} FCFA beside the 2010 total of {value:,} FCFA, and both of "
                 f"the 2010 shares the report prints, {' and '.join(checked)}, reproduce "
                 f"against that 2010 total to within {_PCT_TOL_2010} percentage points")
    return value


# -- the 2012 assessment --------------------------------------------------------------------
_P12_T2 = "Fonds internationaux en 2012"
_P12_T3 = "Repartition des depenses par chapitre d'intervention en 2012"
_P12_T5 = "Decomposition des depenses de soins et de traitement en 2012"

# Every child is read, not only the two donors the panel takes, because reading them all
# turns the donor table into three independent exact identities instead of one.
_S12_T2 = {
    "fs 03 fonds internationaux": "intl",
    "fs 03 01 contributions bilaterales directes": "bilateral",
    "fs 03 01 07 gouvernement francais": "bil_fr",
    "fs 03 01 08 gouvernement allemand": "bil_de",
    "fs 03 01 12 gouvernement japonais": "bil_jp",
    "fs 03 01 22 gouvernement americain": "bil_us",
    "fs 03 02 organismes multilateraux administrant des subventions pre affectees":
        "multilateral",
    "fs 03 02 04 organisation internationale du travail oit": "mul_ilo",
    "fs 03 02 07 fonds mondial de lutte contre le sida la tuberculose et le paludisme":
        "mul_gf",
    "fs 03 02 08 secretariat de l onusida": "mul_unaids",
    "fs 03 02 09 fonds des nations unies pour l enfance unicef": "mul_unicef",
    "fs 03 02 10 fonds de developpement des nations unies pour la femme unifem":
        "mul_unifem",
    "fs 03 02 11 programme des nations unies pour le developpement pnud": "mul_undp",
    "fs 03 02 13 haut commissariat des nations unies pour les refugies hcr": "mul_unhcr",
    "fs 03 02 17 fonds des nations unies pour la population unpfa": "mul_unfpa",
    "fs 03 02 19 programme alimentaire mondial pam": "mul_wfp",
    "fs 03 02 20 organisation mondiale de la sante oms": "mul_who",
    "fs 03 03 organisations et fondations internationales a but non lucratif": "ngo",
    "fs 03 03 20 medecins sans frontieres": "ngo_msf",
    "fs 03 03 25 fondation clinton": "ngo_clinton",
    "fs 03 03 99 autres organisations et fondations internationales a but non lucratif n c a":
        "ngo_nca",
}
_S12_T2_BIL = ("bil_fr", "bil_de", "bil_jp", "bil_us")
_S12_T2_MUL = ("mul_ilo", "mul_gf", "mul_unaids", "mul_unicef", "mul_unifem", "mul_undp",
               "mul_unhcr", "mul_unfpa", "mul_wfp", "mul_who")
_S12_T2_NGO = ("ngo_msf", "ngo_clinton", "ngo_nca")

_S12_T3 = {
    "asc 01 prevention": "prevention",
    "asc 02 soins et traitement": "treatment",
    "asc 03 orphelins et autres enfants rendus vulnerables oev": "oev",
    "asc 04 gestion et administration de programmes": "admin",
    "asc 05 ressources humaines": "hr",
    "asc 06 protection sociale et services sociaux": "social",
    "asc 07 environnement favorable": "environment",
    "asc 08 recherche liee au vih a l exception de la recherche operationnelle": "research",
}
_S12_T3_PARTS = tuple(_S12_T3.values())

_S12_T5 = {
    "asc 02 01 soins ambulatoires": "outpatient",
    "asc 02 01 02 prophylaxie et traitement ambulatoires des infections opportunistes":
        "op_io",
    "asc 02 01 03 therapie antiretrovirale": "op_art",
    "asc 02 01 05 suivi en laboratoire specifique au vih": "op_lab",
    "asc 02 01 07 traitement et services d accompagnement psychologique": "op_psy",
    "asc 02 03 transport des patients et secours d urgence": "transport",
    "asc 02 99 services de soins et de traitement non classifies ailleurs n c a": "nca",
}
_S12_T5_OUT = ("op_io", "op_art", "op_lab", "op_psy")
_S12_T5_PARTS = ("outpatient", "transport", "nca")


def _read_2012(pdf) -> Dict:
    """The 2012 assessment: Tableau 2 by donor, Tableau 3 by chapter, Tableau 5 on treatment.

    The 2012 report prints no source-of-financing table, so the headline total comes from the
    intervention table and the domestic split is refused. Both the intervention table and the
    treatment table print their total as a bare figure with no label, and both are identified
    by the arithmetic of the rows above them.
    """
    gates: List[str] = []

    p2, t2, _ = _single_table(pdf, _P12_T2, _S12_T2, name="Tableau 2", pages=2)
    for key, parts, what in (("bilateral", _S12_T2_BIL, "four bilateral governments"),
                             ("multilateral", _S12_T2_MUL, "ten multilateral agencies"),
                             ("ngo", _S12_T2_NGO, "three international non-profits")):
        got = sum(t2[k] for k in parts)
        if got != t2[key]:
            raise _Refused(f"Tableau 2: the {what} sum to {got:,} against a printed "
                           f"{key} sub-total of {t2[key]:,}")
    groups = t2["bilateral"] + t2["multilateral"] + t2["ngo"]
    if groups != t2["intl"]:
        raise _Refused(f"Tableau 2: the three sub-totals sum to {groups:,} against a printed "
                       f"FS.03 of {t2['intl']:,}")
    gates.append(f"Tableau 2: all three donor groups reproduce from their own members "
                 f"EXACTLY, and the three sub-totals sum EXACTLY to the printed FS.03 of "
                 f"{t2['intl']:,} FCFA, so the United States row and the derived "
                 f"other-bilateral row sit inside a table that ties at both levels")

    p3, t3, bare3 = _single_table(pdf, _P12_T3, _S12_T3, name="Tableau 3")
    chapters = sum(t3[k] for k in _S12_T3_PARTS)
    total = _find_single_total(bare3, chapters, "Tableau 3")
    gates.append(f"Tableau 3: the eight intervention chapters sum to {chapters:,} FCFA, "
                 f"which is what identifies the unlabelled row printed beneath them as the "
                 f"grand total; the identification is arithmetic, not positional")

    p5, t5, bare5 = _single_table(pdf, _P12_T5, _S12_T5, name="Tableau 5")
    outpatient = sum(t5[k] for k in _S12_T5_OUT)
    if outpatient != t5["outpatient"]:
        raise _Refused(f"Tableau 5: the four outpatient components sum to {outpatient:,} "
                       f"against a printed ASC.02.01 of {t5['outpatient']:,}")
    treatment = _find_single_total(bare5, sum(t5[k] for k in _S12_T5_PARTS), "Tableau 5")
    if treatment != t3["treatment"]:
        raise _Refused(f"Tableau 5's treatment total of {treatment:,} disagrees with Tableau "
                       f"3's ASC.02 of {t3['treatment']:,}")
    gates.append(f"Tableau 5: the four outpatient components reproduce the printed ASC.02.01 "
                 f"EXACTLY, its three second-level rows identify the unlabelled total "
                 f"beneath them, and that total equals Tableau 3's printed ASC.02 of "
                 f"{t3['treatment']:,} FCFA EXACTLY")

    share = 100.0 * t2["intl"] / total
    w2, w3 = f"Tableau 2, pdf page {p2}", f"Tableau 3, pdf page {p3}"
    series = {
        "total": (total, w3, "tableau3.total"),
        "intl": (t2["intl"], w2, "tableau2.fs03"),
        "us": (t2["bil_us"], w2, "tableau2.fs03.01.22"),
        "gf": (t2["mul_gf"], w2, "tableau2.fs03.02.07"),
        "other_bilateral": (t2["bilateral"] - t2["bil_us"],
                            f"{w2}, the bilateral sub-total less the United States row",
                            "tableau2.bilateral_hors_etats_unis"),
        "treatment": (t3["treatment"], f"{w3}, confirmed by Tableau 5 on pdf page {p5}",
                      "tableau3.asc02"),
        "share": (round(share, 4), f"{w2} over {w3}", "derived.part_internationale"),
    }
    return {"years": [2012], "series": {2012: series}, "gates": gates}


_SINGLE_READERS = {"2007": _read_2007, "2009": _read_2009, "2011": _read_2011,
                   "2012": _read_2012}


# -- emission -------------------------------------------------------------------------------
# series key -> (indicator id, unit, what the figure is)
_SERIES: Dict[str, Tuple[str, str, str]] = {
    "total": ("hiv_expenditure_total_lcu", "LCU",
              "all HIV spending from every source, the assessment's headline"),
    "intl": ("hiv_expenditure_international_lcu", "LCU",
             "HIV spending funded by direct foreign transfers"),
    "us": ("hiv_expenditure_us_gov_lcu", "LCU",
           "HIV spending funded by the United States government"),
    "gf": ("hiv_expenditure_global_fund_lcu", "LCU",
           "HIV spending funded by the Global Fund"),
    "other_bilateral": ("hiv_expenditure_other_bilateral_lcu", "LCU",
                        "HIV spending funded by bilateral donors other than the United "
                        "States, being the bilateral total less the United States row"),
    "public": ("domestic_hiv_spend_lcu", "LCU",
               "HIV spending funded by domestic public revenue"),
    "private": ("hiv_expenditure_domestic_private_lcu", "LCU",
                "HIV spending funded by domestic private revenue, being households, "
                "non-governmental organisations and firms"),
    "treatment": ("hiv_spend_treatment_lcu", "LCU",
                  "HIV spending on care and treatment"),
    "share": ("hiv_expenditure_international_share_pct", "percent",
              "direct foreign transfers as a share of all HIV spending, recomputed from the "
              "two levels because the assessments print three conflicting values for it"),
}

# What the connector refuses, written per edition so that a row says what was refused in the
# document the row came from. Every row carries `_REFUSED_COMMON` and then the clause for its
# own edition, because a reader checking a 2012 figure is not helped by a sentence about the
# 2020-2021 key-indicators table.
_REFUSED_COMMON = (
    "refused from this source: every printed percentage (the 2020-2021 report prints three "
    "different values for the 2021 international share, the 2011 report prints a bilateral "
    "share of 33,1 per cent where its own levels give 47.8 per cent), the prevention series "
    "(the assessments classify counselling and testing differently), the intervention split "
    "beyond treatment, and the data labels printed on every graphique, whose print order is "
    "sorted by value and carries no recoverable mapping to years"
)
_REFUSED_TWO_YEAR = (
    "; and from this edition: the 2020-2021 key-indicators table in full, the Graphique 8 "
    "page's UN-system and other-international rows, its Global Fund row for 2017, and its "
    "2014, 2015, 2018 and 2019 columns"
)
# One clause per single-year edition, each naming what the document itself withholds.
_REFUSED_SINGLE: Dict[str, str] = {
    "2007": ("; and from this edition: the international level and the international share "
             "(Annexe 1's private sub-total of 659,288,603 FCFA has no household line and "
             "both of its children are named international bodies, so the boundary between "
             "domestic private money and international money cannot be placed), the private "
             "level for the same reason, and the whole of 2008, which appears in no "
             "assessment and only in chart data labels"),
    "2009": ("; and from this edition: the Global Fund level, for two independent reasons, "
             "the first being that the Annexe 3 matrix books the whole of the international "
             "block's public-sector agent column, 17,734,185,491 FCFA, to the Global Fund "
             "alone, so the printed 20,913,254,871 FCFA is public money carrying a Global "
             "Fund source label and not a Global Fund disbursement, and the second being "
             "that 20,913,254,871 FCFA is more than twice what the Global Fund's own IATI "
             "activity file and the OECD creditor reporting system each report for Cameroon "
             "in 2009, about 22.2 and 22.3 million dollars, at any euro-dollar rate of that "
             "year, the CFA franc being pegged to the euro at 655.957; the rest of the "
             "matrix's multilateral block, whose 14 named children fall 165,402,500 FCFA "
             "short of their printed FS.03.02 sub-total because the population fund's row "
             "prints no figures at all; the matrix's fourth and fifth agent columns, which "
             "are nested inside its third agent column and do not split a row further; and "
             "the narrative's own national total, which contradicts Tableau 1"),
    "2011": ("; and from this edition: the 2010 donor split, whose three named components "
             "fall 778,048,854 FCFA short of the 2010 total the same report states; every "
             "share printed in Annexe 3, FS.03.03's 13,18 per cent among them, where the "
             "annexe's own levels give 18.51 per cent; the eight agencies Annexe 3 prints "
             "under FS.03.02 beside the Global Fund, which are read for the sub-total gate "
             "and emitted for no indicator; and the narrative's own national total, which "
             "contradicts Tableau 5 by 500,000,000 FCFA"),
    "2012": ("; and from this edition: the domestic public and private levels, because the "
             "report prints no source-of-financing table at all and its Tableau 2 covers "
             "international money only"),
}

# A property of the document rather than a refusal, carried so that a reader comparing this
# panel with a later edition knows which edition the panel read.
_EDITION_NOTES: Dict[str, str] = {
    "2009": ("the title page of this assessment reads PROJET DE RAPPORT, so the figures come "
             "from a draft dated October 2010 and not from a final edition. Every figure "
             "taken from the draft reproduces from its own components, and no final edition "
             "of the 2009 assessment has been found on the UNAIDS site. The Annexe 3 REDES "
             "matrix carries one further defect that affects nothing emitted: the matrix's "
             "grand-total row sums to 34,990,561,584 FCFA across its three disjoint agent "
             "columns against its own printed Total of 34,636,909,946, an excess of "
             "353,651,638 FCFA which arises in the multilateral block. The bilateral rows "
             "the American and other-bilateral levels come from close to the franc in three "
             "independent directions of their own, across each row, down each agent column "
             "and over the four named governments."),
    "2012": ("the report prints no source-of-financing table. The domestic envelope is "
             "recoverable as the total less FS.03, being 25,420,437,252 less 15,256,504,029 "
             "or 10,163,933,223 FCFA, which reproduces the figure the report's own prose "
             "prints, but the panel carries no domestic-envelope indicator and splitting "
             "that envelope into public and private money would mean reading percentages "
             "off a chart."),
}


class CameroonNASAConnector(BaseConnector):
    """Cameroon NASA/REDES — national HIV expenditure by revenue source and by donor.

    Parse-only by design: `scripts/survey_cameroon_reports.py` discovers and downloads the
    assessments, and this connector reads what is already in `raw_dir`. Keeping the fetching in
    one script the researcher runs means this connector makes no network request at all.

    Unlike the CNLS connector, this one reads BOTH documents before emitting anything, because
    the 2016 and 2017 domestic rows live in the 2020-2021 report and are only trustworthy once
    that report's own figures have been checked against the assessment that covers 2016 and
    2017. A document that fails its gates contributes nothing, and the other document still
    emits what it can.
    """

    source_id = "cm_nasa"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("Cameroon NASA/REDES national AIDS spending assessments — HIV expenditure "
                   "by revenue source, by donor and on treatment, in CFA francs (to-source, "
                   "parse-only).")
    country = "CMR"

    def __init__(self, raw_dir: str = "data/raw/cameroon/nasa", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _rows(self, path: Path, edition: str, url: str, year: int,
              series: Dict[str, Tuple], gates: Sequence[str], refused: str,
              only: Optional[Sequence[str]] = None) -> Iterator[PanelRow]:
        for key, (indicator_id, unit, what) in _SERIES.items():
            if only is not None and key not in only:
                continue
            if key not in series:
                continue
            value, where, code = series[key]
            if value is None:
                continue
            extra = {
                "edition": path.name,
                "assessment": edition,
                "source_table": where,
                "measure": what,
                "extraction": _EXTRACTION,
                "integrity": "; ".join(gates),
                "refused": refused,
                "reconcile_with": ("unaids_gam_expenditure (national HIV expenditure by "
                                   "revenue source, reported in US dollars) and, for the "
                                   "United States row, pepfar_agency and foreign_assistance "
                                   "(disbursements, a different accounting basis)"),
            }
            note = _EDITION_NOTES.get(edition)
            if note:
                extra["edition_note"] = note
            if unit == "LCU":
                extra["currency"] = _CURRENCY
                extra["currency_note"] = _CURRENCY_NOTE
            kw: Dict = {}
            if key == "share":
                # The share is recomputed, so its two parents have to be present to be cited.
                # 2007 and 2010 reach this module with one of the two missing, and a share
                # key is never built for a year that cannot carry both; the guard is here so
                # that a future edition cannot slip a share through without its workings.
                if "intl" not in series or "total" not in series:
                    log.warning("cm_nasa: %s %d carries an international share with no "
                                "numerator or denominator to cite; the share is dropped.",
                                edition, year)
                    continue
                kw = {"numerator": float(series["intl"][0]),
                      "denominator": float(series["total"][0])}
            yield self.make_row(
                country_iso3="CMR", country_name="Cameroon",
                indicator_id=indicator_id, year=year, value=float(value), unit=unit,
                source_url=url, source_indicator_code=f"nasa.{edition}.{code}",
                extra=extra, **kw,
            )

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
            log.error("cm_nasa: pdfplumber not installed (pip install pdfplumber)")
            return
        if not self.raw_dir.exists():
            log.warning("cm_nasa: %s does not exist — run "
                        "scripts/survey_cameroon_reports.py to cache the assessments",
                        self.raw_dir)
            return

        read: Dict[str, Dict] = {}
        paths: Dict[str, Path] = {}
        urls: Dict[str, str] = {}
        for path in sorted(self.raw_dir.glob("*.pdf")):
            if path.name in _EDITIONS:
                edition, declared, url = _EDITIONS[path.name]
                single = False
            elif path.name in _EDITIONS_SINGLE:
                edition, declared, url = _EDITIONS_SINGLE[path.name]
                single = True
            else:
                log.warning("cm_nasa: %s is not on the edition allow-list — skipped. The "
                            "assessments' table numbers are not stable, the 2020-2021 "
                            "report's own list of tables disagrees with its body, and the "
                            "2012 report prints two of its totals with no label at all, so "
                            "a new assessment's captions, label maps and gates are read by "
                            "a human and added to _EDITIONS or _EDITIONS_SINGLE.", path.name)
                continue
            paths[edition], urls[edition] = path, url
            try:
                with pdfplumber.open(str(path)) as pdf:
                    if single:
                        reading = _SINGLE_READERS[edition](pdf)
                    else:
                        reader = _read_assessment_a if edition == "2016-2017" \
                            else _read_assessment_b
                        reading = reader(pdf, declared)
                surprise = sorted(set(reading["years"]) - set(declared))
                if surprise:
                    raise _Refused(
                        f"the reader returned {surprise}, which this edition is not "
                        f"declared to cover; the declared years are {list(declared)}")
                read[edition] = reading
            except _Refused as exc:
                log.error("cm_nasa: %s refused — %s. Nothing is emitted for %s.",
                          path.name, exc, edition)
            except Exception as exc:                           # pragma: no cover - pdfplumber
                log.error("cm_nasa: %s could not be read (%s)", path.name, exc)

        a, b = read.get("2016-2017"), read.get("2020-2021")
        cross: List[str] = []
        if a is not None and b is not None:
            try:
                cross = _cross_assessment_gates(a, b)
            except _Refused as exc:
                log.error("cm_nasa: %s. The 2016 and 2017 domestic rows are not emitted; "
                          "everything else is.", exc)
                cross = []
        elif a is not None:
            log.warning("cm_nasa: the 2020-2021 assessment was not read, so the 2016 and 2017 "
                        "domestic public and private rows have no source; the 2016-2017 "
                        "assessment prints no domestic split of its own.")

        emitted = 0
        order = [("2016-2017", a), ("2020-2021", b)]
        order += [(e, read.get(e)) for e in sorted(_SINGLE_READERS)]
        for edition, reading in order:
            if reading is None:
                continue
            refused = _REFUSED_COMMON + _REFUSED_SINGLE.get(edition, _REFUSED_TWO_YEAR)
            for year in reading["years"]:
                if year < start_year or year > end_year:
                    continue
                series = dict(reading["series"][year])
                gates = list(reading["gates"])
                only = None
                if edition == "2016-2017":
                    if cross and b is not None:
                        g8 = b["g8"]
                        page = g8["page"]
                        for key, src in (("public", "Fonds publics"),
                                         ("private", "Fonds prives")):
                            value = g8["rows"][key].get(year)
                            if value is not None:
                                series[key] = (
                                    value,
                                    f"the 2020-2021 report's Graphique 8 page {page}, "
                                    f"{src} row",
                                    f"graphique8.{key}",
                                )
                        gates += cross
                    else:
                        only = [k for k in _SERIES if k not in ("public", "private")]
                for row in self._rows(paths[edition], edition, urls[edition], year,
                                      series, gates, refused, only):
                    emitted += 1
                    yield row
        log.info("cm_nasa: %d rows from %d assessment(s)", emitted, len(read))
