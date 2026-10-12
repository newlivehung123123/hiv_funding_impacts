"""
Shared text-layer table primitives for the country PDF connectors.

WHY THESE EXIST AT ALL

`pdfplumber.extract_tables()` is unsafe on the national reports this package reads. On page
79 of the Cameroon CNLS 2024 annual report it fragments one 11-row table into single-row
"tables" and returns six of the 11 rows, silently dropping Centre, Extreme-Nord, Nord, Ouest
and Sud-Ouest, because the alternating row shading is what it detects as table edges. The
same page's `extract_text()` returns every row exactly. A connector that loses five of ten
regions and still emits a plausible-looking national total is the worst failure this project
can have, so every table here is read off the text layer instead, and cells are delimited by
word x-position.

WHY CELLS CANNOT BE DELIMITED BY WHITESPACE

The documents print thousands separators inconsistently, including within one table. The
CNLS 2024 edition prints "17 377" in one column and "8346" in the next; the 2023 edition
prints no intra-number spaces at all; the Cameroon NASA 2016-2017 assessment uses a space as
its thousands separator throughout ("23 486 587 409") while the 2020-2021 assessment uses a
comma ("80,741,729,487"). Splitting the CNLS 2024 national viral-load row on whitespace
yields nine tokens for six columns. Cleaning the numbers before delimiting the cells is worse
still: the regex that strips a thousands space, run over a whole line, turns the 2023 row
"25365 806" into "25365806" and merges two columns into one. So cells are delimited by x
position FIRST and cleaned SECOND, which is the order `_columns` imposes.

THE TWO MEASURED CONSTANTS

Measured on the Cameroon CNLS target tables, 2026-10-01, and re-checked against the NASA
assessments.

`_LINE_TOL` (4.0 points). Row pitch is about 13 points. The worst intra-row baseline jitter
is 1.4 points, where the 2023 edition's Adamaoua label sits in a 9.96-point font against
11.04 points for its own numbers, giving top edges 509.253 and 507.885. Those two differ by
1.368 at the top edge but only 0.83 at the vertical midpoint, which is why `_lines` clusters
on the midpoint. A top-edge cluster at this tolerance splits that row in two.

`_COL_GAP` (10.0 points). Gaps between the digit groups of one number measured 2.3 to 2.9
points (n=45, median 2.4) and gaps between columns measured 25.5 to 124.4 points (n=222),
with nothing at all in between. 10.0 sits in the middle of that empty band, so the threshold
is justified by the distribution rather than assumed. A wrong threshold cannot fail quietly
in either direction, because each caller checks the column count it expects and then checks
the table's own printed arithmetic.

Both are defaults a caller may override, because a document measured differently should say
so at the call site instead of changing a constant every other caller depends on.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional, Sequence, Tuple

#: see the module docstring. Points, measured, not assumed.
LINE_TOL = 4.0
COL_GAP = 10.0


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or ""))
                   if not unicodedata.combining(c))


def norm(s: str) -> str:
    """Normalise a row label for matching: accents, case, hyphens and spacing all ignored.

    Needed because spelling differs WITHIN one document. The CNLS 2024 edition's Table 38
    prints "Extreme-Nord", "Nord-Ouest" and "Sud-Ouest" while its own Table 42 prints
    "Extreme-nord", "Nord-ouest" and "Sud-ouest", nine pages apart.
    """
    s = strip_accents(s).lower()
    s = s.replace("-", " ").replace("–", " ").replace("—", " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def to_pct(cell: str) -> Optional[float]:
    """A column-joined percentage cell to a float, or None.

    Accepts both decimal marks, because one document uses both: the Cameroon NASA 2020-2021
    assessment prints "94.1%" in its Tableau 8 and "54,9%" in its Tableau 9.
    """
    s = str(cell or "").strip()
    if not s or s in ("-", "‐", "–", "—"):
        return None
    s = re.sub(r"[\s   %]", "", s).replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def lines(page, line_tol: float = LINE_TOL) -> List[Dict]:
    """Group a page's words into visual lines, each sorted left to right.

    Clusters on the vertical midpoint rather than the top edge; see the module docstring for
    the measurement that forces it. Returns one dict per line with `mid`, `words` and `text`.
    """
    words = page.extract_words(x_tolerance=1.0, y_tolerance=2.0)
    rows: List[Dict] = []
    for w in sorted(words, key=lambda w: ((w["top"] + w["bottom"]) / 2.0, w["x0"])):
        mid = (w["top"] + w["bottom"]) / 2.0
        if rows and abs(mid - rows[-1]["mid"]) <= line_tol:
            rows[-1]["words"].append(w)
        else:
            rows.append({"mid": mid, "words": [w]})
    for r in rows:
        r["words"].sort(key=lambda w: w["x0"])
        r["text"] = " ".join(w["text"] for w in r["words"])
    return rows


_NUMERIC_WORD = re.compile(r"^[\d.,%]+$")


def columns(words: Sequence[Dict], col_gap: float = COL_GAP) -> List[str]:
    """Join a line's words into table columns on the measured inter-column gap.

    Words inside one column are concatenated with NO separator when every one of them is
    numeric, which is what repairs a number split across words ("17" + "377" -> "17377"),
    and with a space otherwise, so a two-word row label survives as two words and still
    matches. Joining every column with "" instead would turn "Nord Ouest" into "NordOuest".
    """
    cols: List[List[Dict]] = []
    for w in words:
        if cols and (w["x0"] - cols[-1][-1]["x1"]) < col_gap:
            cols[-1].append(w)
        else:
            cols.append([w])
    out: List[str] = []
    for c in cols:
        sep = "" if all(_NUMERIC_WORD.match(w["text"]) for w in c) else " "
        out.append(sep.join(w["text"] for w in c))
    return out


def match_label(text: str, table: Dict[str, str]) -> Optional[str]:
    """Look a row label up in a label map, ignoring accents, case, hyphens and spacing."""
    key = norm(text)
    if key in table:
        return table[key]
    squashed = key.replace(" ", "")
    for k, v in table.items():
        if k.replace(" ", "") == squashed:
            return v
    return None


def match_prefix(text: str, table: Dict[str, str]) -> Optional[str]:
    """Like `match_label`, but matches a label map key against the START of a line.

    The NASA assessments print a row label and its figures on one line, and some labels wrap
    onto a second line, so an exact whole-cell match is not available the way it is for the
    CNLS region tables. Longest key first, so "soins et traitement du vih" is preferred over
    a shorter key that is also a prefix of it.
    """
    key = norm(text)
    for k in sorted(table, key=len, reverse=True):
        if key.startswith(k):
            return table[k]
    return None


# -- reading numbers when no gap threshold separates the cells ------------------------------
#
# `columns()` assumes an empty band between intra-number gaps and inter-column gaps. The Niger
# health yearbooks (2013 to 2024 editions, measured 2026-10-02) have no such band. Thousands
# gaps there run 1.9 to 4.6 points, and the narrowest gap between two cells is 6.7 points: the
# 2020 edition prints Niamey's under-15 total "271" at x 352.8-366.5 and the next cell "2 308"
# as "2" at x 373.2 and "308" at x 380.2, so `columns()` reads "2712308". `number_readings`
# does not decide from the gap alone. It lists every way the words could form whole numbers,
# and the caller keeps the one reading that satisfies the table's own printed arithmetic.

#: Points. Two numeric words can belong to one number only when the gap between the two words
#: is below this value. Set above every measured thousands gap (at most 4.6 points) so that no
#: real join is ever excluded; a cell gap below the threshold only adds a reading for the
#: caller's arithmetic to reject.
JOIN_GAP = 8.0
#: The most candidate joins one line may carry, so the enumeration stays at 4,096 readings or
#: fewer. A line with more is refused by raising, not read on a guess.
MAX_JOINS = 12

_DIGIT_WORD = re.compile(r"^\d+$")
_DASH_WORD = re.compile(r"^[-‐–—]$")


def is_number_word(text: str) -> bool:
    """True for a word `number_readings` accepts, being plain digits or a lone dash."""
    return bool(_DIGIT_WORD.match(text) or _DASH_WORD.match(text))


def number_readings(words: Sequence[Dict], join_gap: float = JOIN_GAP,
                    max_joins: int = MAX_JOINS) -> List[Tuple[Tuple[int, ...], Tuple[int, ...]]]:
    """Every reading of a line's numeric words as a sequence of whole numbers.

    `words` are the line's number words in left-to-right order, each a pdfplumber word dict,
    and every one must pass `is_number_word`. A word may join the word before it only when
    the earlier word has one to three digits, the later word has exactly three digits and the
    gap between the two is below `join_gap`, which is how a thousands group looks. Every
    combination of the candidate joins is tried. A reading is dropped when a number in the
    reading starts with a zero and has more than one digit, because "036" on its own or
    "0 123" joined is not a count any table prints.

    A lone dash is read as 0, and the dash's position in the reading is returned beside the
    values, so a caller can refuse a dash or confirm the zero against the row's arithmetic.

    Returns a list of `(values, dash_positions)` pairs, without duplicates, in no particular
    order. The caller chooses among the readings by the count of cells the header promises
    and by the row's printed arithmetic, and must refuse a row left with no reading or with
    more than one.
    """
    ws = list(words)
    for w in ws:
        if not is_number_word(w["text"]):
            raise ValueError(f"not a number word: {w['text']!r}")
    joins = [i for i in range(len(ws) - 1)
             if _DIGIT_WORD.match(ws[i]["text"]) and _DIGIT_WORD.match(ws[i + 1]["text"])
             and len(ws[i]["text"]) <= 3 and len(ws[i + 1]["text"]) == 3
             and (ws[i + 1]["x0"] - ws[i]["x1"]) < join_gap]
    if len(joins) > max_joins:
        raise ValueError(f"{len(joins)} candidate joins on one line, more than {max_joins}")
    seen = set()
    out: List[Tuple[Tuple[int, ...], Tuple[int, ...]]] = []
    for mask in range(1 << len(joins)):
        joined = {joins[b] for b in range(len(joins)) if (mask >> b) & 1}
        groups: List[List[str]] = []
        for i, w in enumerate(ws):
            if (i - 1) in joined:
                groups[-1].append(w["text"])
            else:
                groups.append([w["text"]])
        values: List[int] = []
        dashes: List[int] = []
        valid = True
        for g in groups:
            head = g[0]
            if _DASH_WORD.match(head):
                dashes.append(len(values))
                values.append(0)
                continue
            if (len(g) > 1 or len(head) > 1) and head.startswith("0"):
                valid = False
                break
            values.append(int("".join(g)))
        if not valid:
            continue
        reading = (tuple(values), tuple(dashes))
        if reading not in seen:
            seen.add(reading)
            out.append(reading)
    return out
