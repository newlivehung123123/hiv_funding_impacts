"""
Mongolia, Health Indicators books of the Health Development Center, HIV cases newly registered
in the year, nationally, 2015 to 2025 (to-source, routine programme, national).

The Health Development Center (HDC) of the Mongolian Ministry of Health publishes a yearly book of
health indicators (Эрүүл мэндийн үзүүлэлт, Health Indicators) on hdc.gov.mn, in Mongolian and in
English. The HIV section of every book (section 6.5.2 in the 2024 and 2025 editions) gives the
count of HIV cases registered since the first Mongolian case in 1992 and the count newly
registered in the year. Figure 6.23 of the 2024 English book prints the yearly count and the rate
per 100,000 population for 2015 to 2024. The books are born-digital, so the connector reads the
pdfplumber text layer and uses no optical character recognition (OCR), under ruling R8 of
research/rulings_2026-10-15.md.

    year    2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025
    cases     18   26   25   18   18   25   16   19   23   19   39

THE FIVE BOOKS
--------------
  hi2024_en  Health Indicators 2024, English. Figure 6.23 (counts and rates, 2015 to 2024), the
             prose count for 2024 and the ten-year average.
  hi2025_mn  Health Indicators 2025, Mongolian. The prose count and rate for 2025, the cumulative
             count to the end of 2025 and the distance of 2025 from the ten-year average.
  hi2024_mn  Health Indicators 2024, Mongolian. The prose count for 2024, a cross-check.
  hi2023_en  Health Indicators 2023, English. The prose count for 2022, a cross-check. The 2023
             edition repeats the sentence for 2022 and prints Figure 6.23 with no legible labels.
  hi2019_en  Health Indicators 2019, English. The prose count for 2019, a cross-check.

The connector downloads every book once into `raw_dir`, and every later run reads the cached
copies. A cached copy whose size or sha256 differs from the copy read on 16 October 2026 is logged
as a WARNING and still parsed, because every gate below runs on the text.

WHAT THE COUNT IS
-----------------
The emitted value is the count of HIV cases newly registered in Mongolia in the calendar year by
national case surveillance, as the HDC prints the count. The books print no split by sex for the
yearly count and no aimag (province) count for HIV, so every row is national with sex "all". The
monthly counts of the National Statistics Office (NSO) of Mongolia sum to the same values for 2016
to 2025 and serve as a cross-check only (ruling R8), never as panel rows. The books also print the
cumulative deaths among registered cases (51), a count with no yearly series, which the connector
does not read.

INTEGRITY GATES
---------------
  * Exactly one page of hi2024_en prints the caption of Figure 6.23 for 2015 to 2024, and the first
    line of year words below the caption prints 2015 to 2024 in order.
  * Above every year word, between the caption and the year line, sits exactly one whole-number
    label (the count) and exactly one label with two decimals (the rate per 100,000), every label
    centred within eight points of the year word.
  * Every count and rate pair implies a population between 2.8 and 3.9 million, and the population
    implied by the chart pairs moves by a factor between 0.97 and 1.06 between successive years.
  * The mean of the ten chart counts equals every ten-year average printed after the prose count
    of hi2024_en and hi2024_mn, within 0.05, and hi2024_en prints at least one ten-year average.
  * Every book prints at least one prose sentence giving the cumulative count and the count of the
    year, every sentence in one book names the same year and the same two counts, and the year
    named is the year expected for the book.
  * The prose count of every year from 2015 to 2024 equals the chart count of the same year.
  * The cumulative counts of successive books differ by the sum of the yearly counts between the
    two years (286 at the end of 2019, 346 at the end of 2022, 388 at the end of 2024 and 427 at the
    end of 2025 in the copies of 16 October 2026).
  * The 2025 count minus the mean of the counts for 2016 to 2025 equals the distance from the
    ten-year average printed in hi2025_mn, within 0.05.

Any failed gate refuses every row with a WARNING naming the reason. Counts unlike the table above
are logged as a WARNING and still emitted, because every gate has passed.

RECONCILIATION
--------------
No other source in the panel held Mongolian notified_hiv_cases rows when the connector was built
(checked 16 October 2026). Never compare with new_diagnoses (Jason's ruling of 8 October 2026).

TAGGING. source_type is routine_programme_record (national case surveillance).
"""
from __future__ import annotations

import bisect
import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_BASE = "https://hdc.gov.mn/"
_NOTES = ("research/phase7_eap/eap_round1_notes.md, Mongolia, and ruling R8 of "
          "research/rulings_2026-10-15.md")

#: key -> (path on hdc.gov.mn, local file name, (size, sha256 prefix) of the copy read on
#: 16 October 2026, the year the prose count names, the title of the book)
_BOOKS: Dict[str, Tuple[str, str, Tuple[int, str], int, str]] = {
    "hi2024_en": ("media/files/health%20indicator-2024___2025-10-13%20edited%20by.pdf",
                  "health_indicators_2024_en.pdf", (21_175_612, "15ad7a6b8363"), 2024,
                  "Health Indicators 2024 (English edition)"),
    "hi2025_mn": ("media/uploads/2026_10/9ddeb3596240483eb70d3429ba1e1a52.pdf",
                  "health_indicators_2025_mn.pdf", (25_797_875, "8e000f5dc0ea"), 2025,
                  "Эрүүл мэндийн үзүүлэлт 2025 (Health Indicators 2025, Mongolian edition)"),
    "hi2024_mn": ("media/files/2025%20uzuulelt-2025-07-04.pdf",
                  "health_indicators_2024_mn.pdf", (20_734_022, "56384349c10b"), 2024,
                  "Эрүүл мэндийн үзүүлэлт 2024 (Health Indicators 2024, Mongolian edition)"),
    "hi2023_en": ("media/files/last_eruul%20mendiin%20uzuulelt%202023_english_laast-8.13_8lAJzIZ.pdf",
                  "health_indicators_2023_en.pdf", (14_504_310, "ca4c33b2f710"), 2022,
                  "Health Indicators 2023 (English edition)"),
    "hi2019_en": ("media/files/2019%20eng.pdf",
                  "health_indicators_2019_en.pdf", (11_840_991, "e9771effe1ee"), 2019,
                  "Health Indicators 2019 (English edition)"),
}
_CHART_BOOK = "hi2024_en"
_LATEST_BOOK = "hi2025_mn"

_CHART_YEARS = tuple(range(2015, 2025))
_LATEST_YEAR = 2025
_YEARS = _CHART_YEARS + (_LATEST_YEAR,)
_EXPECTED = dict(zip(_YEARS, (18, 26, 25, 18, 18, 25, 16, 19, 23, 19, 39)))
#: The NSO monthly counts read on 16 October 2026, summed by year. Documentation only, never
#: fetched and never emitted (ruling R8).
_NSO_SUMS = {2016: 26, 2017: 25, 2018: 18, 2019: 18, 2020: 25, 2021: 16, 2022: 19, 2023: 23,
             2024: 19, 2025: 39}

_CHART_CAPTION = "Figure 6.23. Number of HIV and per 10 000 population, 2015-2024"
_EN_A = re.compile(r"(\d{2,4}) cases registered by the end of (20\d\d), of which (\d{1,3}) were "
                   r"(?:newly )?registered in (20\d\d)")
_EN_B = re.compile(r"a total of (\d{2,4}) cases have been reported by the end of (20\d\d), with "
                   r"(\d{1,3}) new cases registered during that year")
_MN_A = re.compile(r"(20\d\d) оны жилийн эцсийн байдлаар ХДХВ/ДОХ-ын нийт (\d{2,4}) тохиолдол "
                   r"бүртгэгдэж, үүнээс (\d{1,3}) тохиолдол нь (?:\(энэ онд\) |энэ онд )?шинээр "
                   r"бүртгэгдсэн")
_MN_B = re.compile(r"(20\d\d) оны жилийн эцсийн байдлаар ХДХВ/ДОХ-ын нийт (\d{2,4}) тохиолдол "
                   r"бүртгэгдсэн байна\. Энэ онд (\d{1,3}) тохиолдол \(100 000 хүнд (\d+\.\d+)\) "
                   r"шинээр бүртгэгдсэн")
_AVG_EN = re.compile(r"Last decade average year (\d+\.\d)")
_AVG_MN = re.compile(r"Сүүлийн 10 жилийн дунджаар (\d+\.\d) \(100 000 хүнд")
_GAP_MN = re.compile(r"Сүүлийн 10 жилийн дунджаас (\d+\.\d) тохиолдлоор")
#: Characters after a prose match searched for the ten-year average or the distance from the
#: average. The distance sentence of hi2025_mn sits 85 characters after the prose match, across a
#: page footer, in the copy of 16 October 2026.
_WINDOW = 400

_COUNT = re.compile(r"^\d{1,3}$")
_RATE = re.compile(r"^\d\.\d\d$")
#: The greatest offset in points between the centre of a chart label and the centre of the year
#: word below the label (measured offset at most 1.1 points, and the axis labels sit 32 points
#: or more from the nearest year word).
_CENTRE_TOL = 8.0
#: Words whose tops differ by at most two points share a line.
_LINE_TOL = 2.0
_POP_RANGE = (2_800_000, 3_900_000)
_STEP_RANGE = (0.97, 1.06)
_MEAN_TOL = 0.05


class _Refused(Exception):
    """A gate failed. Every row is refused, never part of the rows."""


def _flatten(pdf) -> Tuple[str, List[int]]:
    """The text of the whole book on one line, with the offset where every page starts."""
    parts: List[str] = []
    starts: List[int] = []
    at = 0
    for page in pdf.pages:
        starts.append(at)
        flat = re.sub(r"\s+", " ", page.extract_text() or "").strip() + " "
        parts.append(flat)
        at += len(flat)
    return "".join(parts), starts


def _page_of(starts: List[int], offset: int) -> int:
    return bisect.bisect_right(starts, offset)


def _prose(key: str, text: str, starts: List[int]) -> Dict:
    """The prose sentences of one book giving the cumulative count and the count of the year."""
    found = []
    for m in _EN_A.finditer(text):
        if m.group(2) != m.group(4):
            raise _Refused(f"{key} names the end of {m.group(2)} and the year {m.group(4)} in one "
                           f"sentence, {m.group(0)!r}")
        found.append((int(m.group(2)), int(m.group(1)), int(m.group(3)), None, m))
    for m in _EN_B.finditer(text):
        found.append((int(m.group(2)), int(m.group(1)), int(m.group(3)), None, m))
    for m in _MN_A.finditer(text):
        found.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), None, m))
    for m in _MN_B.finditer(text):
        found.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4), m))
    if not found:
        raise _Refused(f"{key} prints no sentence giving the cumulative HIV count and the count of "
                       f"the year")
    triples = {(year, cum, new) for year, cum, new, _, _ in found}
    if len(triples) != 1:
        raise _Refused(f"the sentences of {key} disagree, reading (year, cumulative, new) as "
                       f"{sorted(triples)}")
    year, cum, new = triples.pop()
    want = _BOOKS[key][3]
    if year != want:
        raise _Refused(f"the sentences of {key} name the year {year}, where {want} belongs")
    rates = {r for _, _, _, r, _ in found if r is not None}
    if len(rates) > 1:
        raise _Refused(f"the sentences of {key} print the rates {sorted(rates)} for {year}")
    first = min(found, key=lambda f: f[4].start())
    return {"year": year, "cumulative": cum, "new": new, "rate": rates.pop() if rates else None,
            "sentences": len(found), "page": _page_of(starts, first[4].start()),
            "sentence": first[4].group(0), "matches": [f[4] for f in found]}


def _after(text: str, matches, pattern: re.Pattern) -> List[float]:
    """Every value of `pattern` within _WINDOW characters after a prose match."""
    values = []
    for m in matches:
        hit = pattern.search(text, m.end(), m.end() + _WINDOW)
        if hit:
            values.append(float(hit.group(1)))
    return values


def _chart(pdf, text: str, starts: List[int]) -> Dict:
    """Figure 6.23 of hi2024_en, the count and the rate above every year word from 2015 to 2024."""
    pages = sorted({_page_of(starts, m.start()) for m in re.finditer(re.escape(_CHART_CAPTION), text)})
    if len(pages) != 1:
        raise _Refused(f"{len(pages)} pages of {_CHART_BOOK} print the caption {_CHART_CAPTION!r}, "
                       f"on pages {pages}, where exactly one must")
    pno = pages[0]
    words = pdf.pages[pno - 1].extract_words()
    caption = [w for w in words if w["text"] == "2015-2024"]
    caption = [w for w in caption
               if any(v["text"] == "6.23." and abs(v["top"] - w["top"]) <= _LINE_TOL for v in words)]
    if len(caption) != 1:
        raise _Refused(f"page {pno} of {_CHART_BOOK} holds {len(caption)} caption lines of Figure "
                       f"6.23, where exactly one must")
    cap_bottom = caption[0]["bottom"]

    wanted = {str(y) for y in _CHART_YEARS}
    year_words = sorted((w for w in words if w["text"] in wanted and w["top"] > cap_bottom),
                        key=lambda w: w["top"])
    if not year_words:
        raise _Refused(f"page {pno} of {_CHART_BOOK} prints no year word below the caption")
    top = year_words[0]["top"]
    line = sorted((w for w in year_words if abs(w["top"] - top) <= _LINE_TOL), key=lambda w: w["x0"])
    if tuple(w["text"] for w in line) != tuple(str(y) for y in _CHART_YEARS):
        raise _Refused(f"the first line of year words below the caption on page {pno} reads "
                       f"{' '.join(w['text'] for w in line)!r}, where 2015 to 2024 belong")

    def centre(w: Dict) -> float:
        return (w["x0"] + w["x1"]) / 2.0

    counts: Dict[int, int] = {}
    rates: Dict[int, str] = {}
    for yw in line:
        year = int(yw["text"])
        above = [w for w in words if cap_bottom < w["top"] < yw["top"]
                 and abs(centre(w) - centre(yw)) <= _CENTRE_TOL]
        n = [w["text"] for w in above if _COUNT.match(w["text"])]
        r = [w["text"] for w in above if _RATE.match(w["text"])]
        if len(n) != 1 or len(r) != 1:
            raise _Refused(f"above the year {year} on page {pno} sit the whole numbers {n} and the "
                           f"rates {r}, where exactly one of every kind belongs")
        counts[year] = int(n[0])
        rates[year] = r[0]
    return {"page": pno, "counts": counts, "rates": rates}


def _implied(count: int, rate: str) -> Tuple[float, float, float]:
    """The population a count and a printed rate per 100,000 imply, as (low, middle, high)."""
    value = float(rate)
    half = 0.5 * 10 ** -len(rate.split(".")[1])
    if value - half <= 0:
        raise _Refused(f"a rate of {rate} sits beside a count of {count}")
    return count * 1e5 / (value + half), count * 1e5 / value, count * 1e5 / (value - half)


def _check(chart: Dict, prose: Dict[str, Dict], averages: List[Tuple[str, float]],
           gap: float) -> Dict[int, float]:
    counts = dict(chart["counts"])
    latest = prose[_LATEST_BOOK]
    counts[_LATEST_YEAR] = latest["new"]

    mids: Dict[int, float] = {}
    pairs = [(y, chart["counts"][y], chart["rates"][y]) for y in _CHART_YEARS]
    if latest["rate"] is None:
        raise _Refused(f"{_LATEST_BOOK} prints no rate beside the count for {_LATEST_YEAR}")
    pairs.append((_LATEST_YEAR, latest["new"], latest["rate"]))
    for year, n, rate in pairs:
        lo, mid, hi = _implied(n, rate)
        if hi < _POP_RANGE[0] or lo > _POP_RANGE[1]:
            raise _Refused(f"the pair for {year} ({n} cases at {rate} per 100,000) implies a "
                           f"population of {mid:,.0f}, outside {_POP_RANGE}")
        mids[year] = mid
    for prev, year in zip(_CHART_YEARS, _CHART_YEARS[1:]):
        step = mids[year] / mids[prev]
        if not _STEP_RANGE[0] <= step <= _STEP_RANGE[1]:
            raise _Refused(f"the population implied by the chart pairs moves by a factor of "
                           f"{step:.3f} from {prev} to {year}")

    mean = sum(chart["counts"].values()) / len(_CHART_YEARS)
    if not any(src == _CHART_BOOK for src, _ in averages):
        raise _Refused(f"{_CHART_BOOK} prints no ten-year average after the prose count")
    for src, avg in averages:
        if abs(avg - mean) > _MEAN_TOL:
            raise _Refused(f"{src} prints a ten-year average of {avg}, where the chart counts "
                           f"average {mean:.2f}")

    for key, rec in prose.items():
        year = rec["year"]
        if year in chart["counts"] and rec["new"] != chart["counts"][year]:
            raise _Refused(f"{key} prints {rec['new']} cases for {year}, where the chart prints "
                           f"{chart['counts'][year]}")

    ends = sorted({(rec["year"], rec["cumulative"]) for rec in prose.values()})
    if len({y for y, _ in ends}) != len(ends):
        raise _Refused(f"two books print different cumulative counts for one year, {ends}")
    for (y1, c1), (y2, c2) in zip(ends, ends[1:]):
        between = sum(counts[y] for y in range(y1 + 1, y2 + 1))
        if c2 - c1 != between:
            raise _Refused(f"the cumulative count rises from {c1} at the end of {y1} to {c2} at "
                           f"the end of {y2}, where the yearly counts add {between}")

    recent = [counts[y] for y in range(_LATEST_YEAR - 9, _LATEST_YEAR + 1)]
    distance = counts[_LATEST_YEAR] - sum(recent) / len(recent)
    if abs(distance - gap) > _MEAN_TOL:
        raise _Refused(f"{_LATEST_BOOK} prints {_LATEST_YEAR} as {gap} cases above the ten-year "
                       f"average, where the counts give {distance:.2f}")
    return mids


class MongoliaHDCConnector(BaseConnector):
    """Mongolia, HDC Health Indicators books, HIV cases newly registered in the year, 2015 to 2025."""

    source_id = "mn_hdc"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Health Indicators books of the Mongolian Health Development Center, HIV cases "
                   "newly registered in the year, nationally, 2015 to 2025 (to-source).")
    country = "MNG"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/mongolia_hdc", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, key: str) -> Path:
        """Local copy of one book, downloading only if not cached."""
        rel, local, known, _, _ = _BOOKS[key]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / local
        if path.exists():
            log.info("mn_hdc: using cached %s", path)
        else:
            blob = self._request("GET", _BASE + rel).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_BASE + rel} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("mn_hdc: downloaded %s (%.1f MB) -> %s", key, len(blob) / 1e6, path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == known:
            log.info("mn_hdc: %s matches the copy read on 16 October 2026 (sha256 %s)", key,
                     digest[:12])
        else:
            log.warning("mn_hdc: %s differs from the copy read on 16 October 2026 (%d bytes, sha256 "
                        "%s, expected %d bytes, %s), and the text gates still run", key, len(blob),
                        digest[:12], *known)
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
            log.error("mn_hdc: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            paths = {key: self._pdf_path(key) for key in _BOOKS}
        except Exception as exc:
            log.warning("mn_hdc: a Health Indicators book could not be fetched (%s)", exc)
            return
        try:
            table = self._parse(pdfplumber, paths)
        except _Refused as exc:
            log.warning("mn_hdc: every row refused because %s", exc)
            return
        except Exception as exc:
            log.warning("mn_hdc: the Health Indicators books failed to parse (%s)", exc)
            return
        emitted = 0
        for row in self._rows(table, start_year, end_year):
            emitted += 1
            yield row
        log.info("mn_hdc: emitted %d rows", emitted)

    def _parse(self, pdfplumber, paths: Dict[str, Path]) -> Dict:
        prose: Dict[str, Dict] = {}
        averages: List[Tuple[str, float]] = []
        gap: Optional[float] = None
        chart: Optional[Dict] = None
        for key, path in paths.items():
            with pdfplumber.open(str(path)) as pdf:
                text, starts = _flatten(pdf)
                prose[key] = _prose(key, text, starts)
                if key == _CHART_BOOK:
                    chart = _chart(pdf, text, starts)
            if key == _CHART_BOOK:
                averages += [(key, v) for v in _after(text, prose[key]["matches"], _AVG_EN)]
            if key == "hi2024_mn":
                averages += [(key, v) for v in _after(text, prose[key]["matches"], _AVG_MN)]
            if key == _LATEST_BOOK:
                gaps = sorted(set(_after(text, prose[key]["matches"], _GAP_MN)))
                if len(gaps) != 1:
                    raise _Refused(f"{key} prints the distance of {_LATEST_YEAR} from the ten-year "
                                   f"average as {gaps}, where exactly one value belongs")
                gap = gaps[0]
            log.info("mn_hdc: %s, %d sentence(s) name %d cases in %d and %d by the end of %d, "
                     "page %d", key, prose[key]["sentences"], prose[key]["new"], prose[key]["year"],
                     prose[key]["cumulative"], prose[key]["year"], prose[key]["page"])
        mids = _check(chart, prose, averages, gap)

        values = dict(chart["counts"])
        values[_LATEST_YEAR] = prose[_LATEST_BOOK]["new"]
        for year, want in _EXPECTED.items():
            if values[year] != want:
                log.warning("mn_hdc: %d reads %d cases, where the copies read on 16 October 2026 "
                            "printed %d", year, values[year], want)
        log.info("mn_hdc: Figure 6.23 on page %d of %s, every gate passed", chart["page"],
                 _CHART_BOOK)
        return {"chart": chart, "prose": prose, "averages": averages, "gap": gap, "mids": mids,
                "values": values}

    def _rows(self, table: Dict, start_year: int, end_year: int) -> Iterator[PanelRow]:
        chart, prose = table["chart"], table["prose"]
        cumulative = {rec["year"]: rec["cumulative"] for rec in prose.values()}
        for year in _YEARS:
            if not start_year <= year <= end_year:
                continue
            readings: Dict[str, int] = {}
            if year in chart["counts"]:
                key = _CHART_BOOK
                readings[f"{key} Figure 6.23 page {chart['page']}"] = chart["counts"][year]
                rate = chart["rates"][year]
                extraction = ("text layer, Figure 6.23 caption-anchored, the whole-number label "
                              "above the year word")
                caption = _CHART_CAPTION
                page = chart["page"]
            else:
                key = _LATEST_BOOK
                rate = prose[key]["rate"]
                extraction = "text layer, the sentence of section 6.5.2 naming the year"
                caption = prose[key]["sentence"]
                page = prose[key]["page"]
            for k, rec in prose.items():
                if rec["year"] == year:
                    readings[f"{k} prose page {rec['page']}"] = rec["new"]
            rel, _, _, _, title = _BOOKS[key]
            extra: Dict = {
                "edition": title,
                "page": page,
                "caption": caption,
                "extraction": extraction,
                "readings": readings,
                "rate_per_100k_printed": rate,
                "implied_population": round(table["mids"][year]),
                "definition": ("HIV cases newly registered in Mongolia in the calendar year by "
                               "national case surveillance, as the Health Development Center "
                               "prints the count, with no split by sex"),
                "integrity": ("every chart count sits under a rate implying a population between "
                              "2.8 and 3.9 million, the chart counts average the printed ten-year "
                              "average, the prose counts equal the chart counts, and the "
                              "cumulative counts of 2019, 2022, 2024 and 2025 rise by the yearly "
                              "counts"),
                "reconcile_with": (
                    "none. No other source in the panel held Mongolian notified_hiv_cases rows "
                    "when the connector was built (checked 16 October 2026). Never compare with "
                    "new_diagnoses (Jason's ruling of 8 October 2026)"),
                "notes": _NOTES,
            }
            if year in cumulative:
                extra["cumulative_registered_since_1992"] = cumulative[year]
            if year in _NSO_SUMS:
                extra["nso_monthly_sum_read_16_october_2026"] = _NSO_SUMS[year]
            yield self.make_row(
                country_iso3="MNG", country_name="Mongolia",
                indicator_id="notified_hiv_cases", year=year, value=table["values"][year],
                unit="count", admin1="",
                source_url=_BASE + rel,
                source_indicator_code=(f"hdc_health_indicators.{key}."
                                       + ("figure6_23" if key == _CHART_BOOK else "section6_5_2")),
                extra=extra,
            )
