"""
Paraguay, MERCOSUR HIV epidemiological bulletin 2012: new HIV diagnoses by sex, 2000 to 2009
(to-source, routine programme, national).

The health ministries of Argentina, Brazil, Paraguay and Uruguay published a joint HIV bulletin
in 2012 through the intergovernmental HIV/AIDS commission of the MERCOSUR (Southern Common Market)
health ministers' meeting. The Uruguayan Ministry of Public Health (Ministerio de Salud Pública,
MSP) serves the bulletin on gub.uy as "Boletin epidemiologico VIH 2012 Mercosur_0.pdf". On PDF
page 17 the bulletin prints Tabela 3.2, "Taxa anual de novos casos diagnosticados de HIV por
sexo/100 mil habitantes, 2000-2009", with a block for men (Homens) and a block for women
(Mulheres). Every block holds one row per country, and every row holds a pair of figures for
every year from 2000 to 2009, the count of new diagnoses (Nº) and the rate per 100,000
population (Tx). The PDF is born-digital, so the connector uses no optical character recognition
(OCR).

The connector downloads the bulletin once into `raw_dir`, and every later run reads the cached
copy. A cached copy whose size or sha256 differs from the copy read on 13 October 2026 is logged
as a WARNING and still parsed, because every gate below runs on the table itself.

    year       2000  2001  2002  2003  2004  2005  2006  2007  2008  2009
    men         227   250   333   375   284   330   444   401   508   544
    women       126   146   212   251   169   225   308   273   434   380

WHAT THE COUNT IS
-----------------
The emitted value is the count of new HIV diagnoses in Paraguay in the year, by sex, as the
Paraguayan national programme reported the count to the MERCOSUR commission. The source line
under the table names, for Paraguay, the notification sheet and the cross-matching of counselling,
laboratory and integrated care records, with population from the DGEEC (Dirección General de
Estadística, Encuestas y Censos, the national statistics office) for the rates. The table prints
no count for men and women together, and the connector derives no total. Jason ruled on 8
October 2026 that a ministry's own count of HIV cases goes under `notified_hiv_cases` and is never
merged with or compared to `new_diagnoses`.

ONLY PARAGUAY
-------------
The Uruguay rows of Tabela 3.2 nearly equal the `paho_core` rows for the same years, the
Argentine rows are an earlier release of the SNVS count that `ar_snvs` reads from source, and
Brazil is closed (research/phase5_lac/lac_round1_notes.md, MERCOSUR section). The text layer also
reads one Uruguay rate for men as "1021,6" and garbles the Argentine row for women. The connector
reads only the Paraguay row for men and the Paraguay row for women.

PARSING
-------
Page 17 carries chart text placed over the table, some of the chart text outside the page edge,
so whole-line matching is not available. The table is found by CAPTION TEXT, a line reading
"Tabela 3.2 - Taxa anual de novos casos diagnosticados de HIV por sexo/100 mil habitantes,
2000-2009", and ends at the caption of Gráfico 3.2 below the table. Between the Tabela caption
and the Gráfico caption the block label Homens must come before the upper PARAGUAI row and the
block label Mulheres between the upper PARAGUAI row and the lower PARAGUAI row. A PARAGUAI row is
the word PARAGUAI at the left margin of the table and every word to the right of PARAGUAI on the
same line.

The year header of the table reads 2002 to 2009 in clear, while chart year labels printed over
the header garble the years 2000 and 2001 ("22000070" and "22000019"). The legible header years
must sit over the column pairs of 2002 to 2009. The chart data printed beside Gráfico 3.2 lists
the Paraguay rates by sex under explicit year labels from 2000 to 2007, and the chart rates must
equal the table rates of the column pairs of 2000 to 2007, which fixes the years of the column
pairs that the garbled header labels.

INTEGRITY GATES
---------------
  * Exactly one caption of Tabela 3.2 in the bulletin, and exactly one caption of Gráfico 3.2
    below the Tabela caption on the same page.
  * Exactly two PARAGUAI rows between the Tabela caption and the Gráfico caption, with the block
    label Homens above the upper PARAGUAI row and the block label Mulheres between the upper and
    the lower PARAGUAI row.
  * Every PARAGUAI row holds exactly 20 words, alternating a whole count and a rate with at most
    one decimal, and the counts of the row for men and the row for women line up within three
    points.
  * The header line above the upper PARAGUAI row prints exactly 2002 to 2009, every year over the
    column pair of the same year.
  * Every Paraguay chart data block on the page prints, under the years from 2000, the same rates
    as the table, and the page holds at least one Paraguay chart data block.
  * The population implied by every count and rate pair (count x 100,000 / rate, allowing for the
    rounding of the rate) lies between two and four million, falls by less than three per cent and
    rises by less than six per cent from one year to the next, and differs between men and women
    by less than 10 per cent in every year.

Any failed gate refuses the bulletin with a WARNING naming the reason. Counts that differ from the
table above are logged as a WARNING and still emitted, because every gate has passed.

LABELS
------
National rows only, admin1 "", sex "male" and "female".

RECONCILIATION
--------------
No other source in the panel held Paraguayan `notified_hiv_cases` or `new_diagnoses` rows for
2000 to 2009 when the connector was built (checked 14 October 2026). `paho_core` holds national
Paraguayan `notified_hiv_cases` rows from 2014, so the MERCOSUR rows and the `paho_core` rows
share no year.

TAGGING. source_type is routine_programme_record (the national programme's case notification,
per the source line of the table).
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
from ._pdf_text import lines as _lines, norm as _norm

log = logging.getLogger("hivimpact")

_URL = ("https://www.gub.uy/ministerio-salud-publica/sites/ministerio-salud-publica/files/"
        "documentos/publicaciones/Boletin%20epidemiologico%20VIH%202012%20Mercosur_0.pdf")
_LOCAL = "boletin_epidemiologico_vih_2012_mercosur.pdf"
_SERVED_AS = "Boletin epidemiologico VIH 2012 Mercosur_0.pdf"
_NOTES = "research/phase5_lac/lac_round1_notes.md, MERCOSUR HIV epidemiological bulletin 2012"

#: The bulletin read on 13 October 2026: (size, sha256 prefix), the 1-based page of Tabela 3.2
#: in the copy of 13 October 2026 and the counts, all checked as a fingerprint only.
_KNOWN = (4_842_592, "f09a298b7b63")
_PAGE = 17
_YEARS = tuple(range(2000, 2010))
_EXPECTED = {
    "male": (227, 250, 333, 375, 284, 330, 444, 401, 508, 544),
    "female": (126, 146, 212, 251, 169, 225, 308, 273, 434, 380),
}

_CAPTION = ("tabela 3 2 taxa anual de novos casos diagnosticados de hiv por sexo 100 mil "
            "habitantes 2000 2009")
_CHART_CAPTION = ("grafico 3 2 taxa anual de novos casos diagnosticados de hiv por sexo 100 mil "
                  "habitantes 2000 2009")
_ROW_LABEL = "PARAGUAI"
_CHART_LABEL = "Paraguai"
_CHART_SEXES = {"Homem": "male", "Mulher": "female"}
_BLOCK_LABELS = ("Homens", "Mulheres")
_LEGIBLE_YEARS = tuple(str(y) for y in range(2002, 2010))
_COUNT = re.compile(r"^\d{1,3}(?:\.\d{3})?$")
_RATE = re.compile(r"^(\d{1,2})(?:,(\d))?$")
#: The word PARAGUAI sits at x 40 in the copy read on 14 October 2026.
_LEFT_MARGIN = (30.0, 50.0)
#: The greatest offset in points between a count of the row for men and the count of the same
#: year in the row for women (measured offset 0.0).
_ALIGN_TOL = 3.0
#: The greatest offset in points between a chart sex label and the chart label Paraguai.
_CHART_TOL = 5.0
#: Gates on the population implied by every count and rate pair.
_POP_RANGE = (2_000_000, 4_000_000)
_STEP_RANGE = (0.97, 1.06)
_SEX_RATIO_MAX = 1.10


class _Refused(Exception):
    """A gate failed. The whole bulletin is refused, never part of the bulletin."""


def _rate(text: str) -> float:
    m = _RATE.match(text)
    if not m:
        raise _Refused(f"{text!r} sits where a rate with at most one decimal belongs")
    return float(m.group(1) + "." + (m.group(2) or "0"))


def _row_words(ln: Dict, label_word: Dict) -> Tuple[List[int], List[float], List[Dict]]:
    """The ten counts, the ten rates and the 20 words of one PARAGUAI row."""
    words = [w for w in ln["words"] if w["x0"] > label_word["x1"]]
    texts = [w["text"] for w in words]
    if len(words) != 2 * len(_YEARS):
        raise _Refused(f"the PARAGUAI row reads {' '.join(texts)!r}, {len(words)} words where "
                       f"{2 * len(_YEARS)} belong")
    counts: List[int] = []
    rates: List[float] = []
    for k in range(len(_YEARS)):
        n, tx = words[2 * k], words[2 * k + 1]
        if not _COUNT.match(n["text"]):
            raise _Refused(f"the PARAGUAI row prints {n['text']!r} where a count belongs")
        counts.append(int(n["text"].replace(".", "")))
        rates.append(_rate(tx["text"]))
    return counts, rates, words


def _implied(count: int, rate: float) -> Tuple[float, float, float]:
    """The population a count and a printed rate imply, as (low, middle, high)."""
    if rate <= 0:
        raise _Refused(f"a rate of {rate} sits beside a count of {count}")
    lo = count * 1e5 / (rate + 0.05)
    hi = count * 1e5 / max(rate - 0.05, 1e-9)
    return lo, count * 1e5 / rate, hi


def _check_rates(rows: Dict[str, Dict]) -> None:
    mids: Dict[str, List[float]] = {}
    for sex, rec in rows.items():
        mids[sex] = []
        for year, n, tx in zip(_YEARS, rec["counts"], rec["rates"]):
            lo, mid, hi = _implied(n, tx)
            if hi < _POP_RANGE[0] or lo > _POP_RANGE[1]:
                raise _Refused(f"the {sex} pair for {year} ({n} cases at {tx} per 100,000) "
                               f"implies a population of {mid:,.0f}, outside {_POP_RANGE}")
            mids[sex].append(mid)
        for k in range(1, len(_YEARS)):
            step = mids[sex][k] / mids[sex][k - 1]
            if not _STEP_RANGE[0] <= step <= _STEP_RANGE[1]:
                raise _Refused(f"the population implied by the {sex} pairs moves by a factor of "
                               f"{step:.3f} from {_YEARS[k - 1]} to {_YEARS[k]}")
    for k, year in enumerate(_YEARS):
        ratio = max(mids["male"][k], mids["female"][k]) / min(mids["male"][k], mids["female"][k])
        if ratio > _SEX_RATIO_MAX:
            raise _Refused(f"the populations implied for men and for women in {year} differ by a "
                           f"factor of {ratio:.3f}")


def _check_header(header_lines: List[Dict], count_words: List[Dict], rate_words: List[Dict],
                  pno: int) -> str:
    """The legible header years, every year over the column pair of the same year."""
    first = _YEARS.index(int(_LEGIBLE_YEARS[0]))
    for ln in header_lines:
        years = [w for w in ln["words"] if w["x0"] >= count_words[first]["x0"] - 20]
        if tuple(w["text"] for w in years) != _LEGIBLE_YEARS:
            continue
        for k, w in enumerate(years, start=first):
            centre = (w["x0"] + w["x1"]) / 2.0
            if not count_words[k]["x0"] <= centre <= rate_words[k]["x1"]:
                raise _Refused(f"the header year {w['text']} on page {pno} sits at x {centre:.0f}, "
                               f"outside the column pair of {_YEARS[k]}")
        return " ".join(w["text"] for w in years)
    raise _Refused(f"no header line on page {pno} prints {' '.join(_LEGIBLE_YEARS)} over the "
                   f"column pairs of {_LEGIBLE_YEARS[0]} to {_LEGIBLE_YEARS[-1]}")


def _chart_blocks(lns: List[Dict]) -> List[Dict[str, Tuple[float, ...]]]:
    """Every Paraguay chart data block on the page, as {sex: rates from 2000 onwards}."""
    blocks = []
    for i, ln in enumerate(lns):
        for j, w in enumerate(ln["words"]):
            if w["text"] != _CHART_LABEL:
                continue
            years: List[str] = []
            for v in ln["words"][j + 1:]:
                if v["text"] != str(_YEARS[0] + len(years)):
                    break
                years.append(v["text"])
            if len(years) < 2:
                continue
            block: Dict[str, Tuple[float, ...]] = {}
            for nxt in lns[i + 1:i + 3]:
                for m, v in enumerate(nxt["words"]):
                    if v["text"] in _CHART_SEXES and abs(v["x0"] - w["x0"]) <= _CHART_TOL:
                        vals = [u["text"] for u in nxt["words"][m + 1:m + 1 + len(years)]]
                        if len(vals) != len(years):
                            raise _Refused(f"the Paraguay chart data ({v['text']}) prints "
                                           f"{len(vals)} rates under {len(years)} years")
                        block[_CHART_SEXES[v["text"]]] = tuple(_rate(t) for t in vals)
            if set(block) != {"male", "female"}:
                raise _Refused(f"the Paraguay chart data at x {w['x0']:.0f} lacks a Homem line or "
                               f"a Mulher line")
            blocks.append(block)
    return blocks


def _parse(pdf) -> Dict:
    """Find Tabela 3.2 in the bulletin and read the two PARAGUAI rows."""
    found = []
    for pno in range(1, len(pdf.pages) + 1):
        lns = _lines(pdf.pages[pno - 1])
        for i, ln in enumerate(lns):
            if _norm(ln["text"]) == _CAPTION:
                found.append((pno, i, lns))
    if len(found) != 1:
        raise _Refused(f"{len(found)} captions of Tabela 3.2 found, on pages "
                       f"{[f[0] for f in found]}, where exactly one must")
    pno, i, lns = found[0]
    caption = lns[i]["text"]
    ends = [k for k in range(i + 1, len(lns)) if _norm(lns[k]["text"]) == _CHART_CAPTION]
    if len(ends) != 1:
        raise _Refused(f"{len(ends)} captions of Gráfico 3.2 found below Tabela 3.2 on page {pno}, "
                       f"where exactly one must")
    body = lns[i + 1:ends[0]]

    marks: List[Tuple[int, str, Dict]] = []
    for k, ln in enumerate(body):
        for w in ln["words"]:
            if w["text"] == _ROW_LABEL and _LEFT_MARGIN[0] <= w["x0"] <= _LEFT_MARGIN[1]:
                marks.append((k, _ROW_LABEL, w))
            elif w["text"] in _BLOCK_LABELS:
                marks.append((k, w["text"], w))
    kinds = [m[1] for m in marks]
    if kinds != [_BLOCK_LABELS[0], _ROW_LABEL, _BLOCK_LABELS[1], _ROW_LABEL]:
        raise _Refused(f"the block labels and PARAGUAI rows between the Tabela caption and the "
                       f"Gráfico caption on page {pno} come in the order {kinds}, where Homens, "
                       f"PARAGUAI, Mulheres, PARAGUAI belong")

    rows: Dict[str, Dict] = {}
    words_by_sex: Dict[str, List[Dict]] = {}
    for (k, _, label_word), sex in zip((marks[1], marks[3]), ("male", "female")):
        counts, rates, words = _row_words(body[k], label_word)
        rows[sex] = {"counts": counts, "rates": rates,
                     "source_row": " ".join([label_word["text"]] + [w["text"] for w in words])}
        words_by_sex[sex] = words

    men, women = words_by_sex["male"], words_by_sex["female"]
    for k in range(len(_YEARS)):
        gap = abs(men[2 * k]["x0"] - women[2 * k]["x0"])
        if gap > _ALIGN_TOL:
            raise _Refused(f"the counts of {_YEARS[k]} in the PARAGUAI row for men and the "
                           f"PARAGUAI row for women sit {gap:.1f} points apart")
    header = _check_header(body[:marks[1][0]], men[0::2], men[1::2], pno)

    blocks = _chart_blocks(lns)
    if not blocks:
        raise _Refused(f"page {pno} holds no Paraguay chart data, so the years of the column "
                       f"pairs under the garbled header labels are not confirmed")
    for block in blocks:
        for sex, chart in block.items():
            table = tuple(rows[sex]["rates"][:len(chart)])
            if chart != table:
                raise _Refused(f"the Paraguay chart data prints the {sex} rates {chart} from 2000 "
                               f"onwards, where the table prints {table}")
    chart_years = min(len(c) for b in blocks for c in b.values())

    _check_rates(rows)

    if pno != _PAGE:
        log.warning("py_mercosur: Tabela 3.2 sits on page %d, where the copy read on 13 October "
                    "2026 printed Tabela 3.2 on page %d", pno, _PAGE)
    for sex, want in _EXPECTED.items():
        got = tuple(rows[sex]["counts"])
        if got != want:
            log.warning("py_mercosur: the %s counts read %s, where the copy read on 13 October "
                        "2026 printed %s", sex, got, want)
    log.info("py_mercosur: Tabela 3.2 on page %d, two PARAGUAI rows read, %d Paraguay chart data "
             "block(s) confirm the years 2000 to %d", pno, len(blocks),
             _YEARS[0] + chart_years - 1)
    return {"rows": rows, "page": pno, "caption": caption, "header": header,
            "chart_blocks": len(blocks), "chart_years": chart_years}


class ParaguayMercosurConnector(BaseConnector):
    """Paraguay, MERCOSUR HIV bulletin 2012: new HIV diagnoses by sex, 2000 to 2009."""

    source_id = "py_mercosur"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("MERCOSUR HIV epidemiological bulletin 2012 (served by the Uruguayan Ministry "
                   "of Public Health): new HIV diagnoses in Paraguay by sex, 2000 to 2009, "
                   "national (to-source).")
    country = "PRY"
    timeout = 180

    def __init__(self, raw_dir: str = "data/raw/paraguay_mercosur", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the bulletin, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("py_mercosur: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("py_mercosur: downloaded the 2012 bulletin (%.1f MB) -> %s", len(blob) / 1e6,
                     path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("py_mercosur: the bulletin matches the copy read on 13 October 2026 (sha256 "
                     "%s)", digest[:12])
        else:
            log.warning("py_mercosur: the bulletin differs from the copy read on 13 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s), and the table gates still "
                        "run", len(blob), digest[:12], *_KNOWN)
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
            log.error("py_mercosur: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
        except Exception as exc:
            log.warning("py_mercosur: the 2012 bulletin could not be fetched (%s)", exc)
            return
        try:
            with pdfplumber.open(str(path)) as pdf:
                table = _parse(pdf)
        except _Refused as exc:
            log.warning("py_mercosur: the 2012 bulletin refused because %s", exc)
            return
        except Exception as exc:
            log.warning("py_mercosur: the 2012 bulletin failed to parse (%s)", exc)
            return
        emitted = 0
        for row in self._rows(table, start_year, end_year):
            emitted += 1
            yield row
        log.info("py_mercosur: emitted %d rows", emitted)

    def _rows(self, table: Dict, start_year: int, end_year: int) -> Iterator[PanelRow]:
        for sex in ("male", "female"):
            rec = table["rows"][sex]
            for year, n, tx in zip(_YEARS, rec["counts"], rec["rates"]):
                if not start_year <= year <= end_year:
                    continue
                extra: Dict = {
                    "edition": "Boletim epidemiológico HIV MERCOSUL 2012",
                    "edition_file": _SERVED_AS,
                    "table": "Tabela 3.2",
                    "page": table["page"],
                    "caption": table["caption"],
                    "column_header_legible": table["header"],
                    "extraction": ("text layer, caption-anchored, the PARAGUAI rows only, every "
                                   "row read as alternating count and rate words"),
                    "source_row": rec["source_row"],
                    "rate_per_100k_printed": tx,
                    "definition": ("new HIV diagnoses in Paraguay in the year, by sex, as the "
                                   "national programme reported the count to the MERCOSUR "
                                   "HIV/AIDS commission. The source line names the notification "
                                   "sheet and the cross-matching of counselling, laboratory and "
                                   "integrated care records, and DGEEC population for the rates"),
                    "year_check": (f"the header prints 2002 to 2009 over the column pairs of "
                                   f"2002 to 2009, and {table['chart_blocks']} Paraguay chart data "
                                   f"block(s) beside Gráfico 3.2 print the table rates under the "
                                   f"years 2000 to {_YEARS[0] + table['chart_years'] - 1}"),
                    "integrity": ("every count and rate pair implies a population between two "
                                  "and four million that moves smoothly from year to year and "
                                  "agrees between men and women within 10 per cent"),
                    "sexes_note": ("the table prints no count for men and women together, and "
                                   "the connector derives no total"),
                    "reconcile_with": (
                        "none. No other source in the panel held Paraguayan notified_hiv_cases "
                        "or new_diagnoses rows for 2000 to 2009 when the connector was built "
                        "(checked 14 October 2026). paho_core holds Paraguay from 2014. Never "
                        "compare with new_diagnoses (Jason's ruling of 8 October 2026)"),
                    "notes": _NOTES,
                }
                yield self.make_row(
                    country_iso3="PRY", country_name="Paraguay",
                    indicator_id="notified_hiv_cases", year=year, value=n, unit="count",
                    admin1="", sex=sex,
                    source_url=_URL,
                    source_indicator_code=f"mercosur_boletim_hiv.2012.tabela3_2.{sex}",
                    extra=extra,
                )
