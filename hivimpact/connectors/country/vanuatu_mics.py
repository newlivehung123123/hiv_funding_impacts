"""
Vanuatu, comprehensive knowledge about HIV among women from the printed tables of the Vanuatu
Multiple Indicator Cluster Survey (MICS) of 2007, carried out by the Vanuatu National Statistics
Office (VNSO) with the United Nations Children's Fund (UNICEF), connector 74.

Source. "Vanuatu Multiple Indicator Cluster Survey 2007, Final Report" (VNSO and UNICEF, 229
pages in the PDF) was published on the UNICEF childinfo website at
http://www.childinfo.org/files/MICS3_Vanuatu_FinalReport_2007_Eng.pdf. www.childinfo.org no longer
serves the file, so the connector reads the Wayback Machine capture of 22 December 2010
(capture 20101222164918), 3,868,540 bytes, read on 25 October 2026, under ruling R69 of
research/rulings_2026-10-15.md. No sign-in and no key. The connector downloads the capture once
into `raw_dir`, and every later run reads the cached copy. The report is born-digital, so the
connector reads the pdfplumber text layer and uses no optical character recognition (OCR). The
text layer of the sampling-error tables runs backwards, character by character, so the connector
reverses the page string and splits the result on white space, which returns every word the
right way round in reverse order. The reversal is a fixed rearrangement of the characters which
pdfplumber reads, and no figure is recognised from an image.

Tables read.
  Table HA.3 (printed page 115), "Percentage of women aged 15-49 years who have comprehensive
  knowledge of HIV/AIDS transmission, Vanuatu, 2007", column "Have comprehensive knowledge",
  for the national row (women aged 15 to 49) and the 15-24 row (MICS indicator 82, young
  women). Comprehensive knowledge means knowing condom use and a single faithful uninfected
  partner prevent HIV, knowing a healthy-looking person can have HIV, and rejecting the two most
  common misconceptions, which the report names as transmission by mosquito bites and by sharing
  food.
  Table HA.1 (printed page 113) and Table HA.2 (printed page 114), as cross-checks.
  Table SE 01 (printed page 135, sampling errors for the total sample), row "Comprehensive
  knowledge about HIV prevention among young people" (Table HA.3), with the printed confidence
  limits, r minus two standard errors and r plus two standard errors. Table SE 01 prints no row
  for women aged 15 to 49.

Gates. The report enters only when every check below passes, because two printed figures
disagreeing leave the true figure unknown.
  Tables HA.1, HA.2 and HA.3 print once, with the caption and "Vanuatu, 2007", and Table HA.3
  prints the footnote "MICS Indicator 82".
  The eight regions, the urban and rural rows, the seven five-year age rows, the 15-24 row and
  the national row print once in every table, with the same number of women in all three
  tables.
  In every row of Table HA.3 the knowledge share is no larger than the share knowing the two
  ways of prevention or the share identifying the three misconceptions, and the share
  identifying the three misconceptions equals the fourth column of Table HA.2. In every row the
  share knowing the two ways of prevention lies between the Table HA.1 share knowing all three
  ways and the smaller of the Table HA.1 condom and faithful-partner shares.
  The urban and rural numbers add to the national number exactly, the region numbers and the
  five-year age numbers add to the national number within one, the 15-19 and 20-24 numbers add
  to the 15-24 number exactly, and every breakdown weighted by the numbers gives the printed
  total share within 0.1.
  The Table SE 01 row prints once, r times 100 equals the Table HA.3 15-24 share within 0.05,
  and the printed limits equal r minus and plus two standard errors within 0.001 and hold r.
  The text of the report rounds the national share to 16 per cent, and the summary table at the
  front of the report prints the national share against indicator 82.

What the connector emits. Two rows for VUT, 2007, hiv_comprehensive_knowledge_survey_pct,
women, population_group "all", admin1 blank, age_group 15-49 at 16.3 per cent (2,692 women) with
no interval, and age_group 15-24 at 15.4 per cent (1,083 women) with value_lower 12.4 and
value_upper 18.4, the Table SE 01 limits times 100. extra carries the weighted denominator, the
unweighted denominator of the 15-24 row (979), the sample universe and the survey's own age
range under the keys the dhs connector uses, the MICS indicator, the two misconceptions, the
capture and the mislabel of the summary table.

Not carried.
  The other columns of Tables HA.1, HA.2 and HA.3, which fit no panel id.
  The region rows. The report splits Port Vila from Shefa province and Luganville from Sanma
  province, so the eight regions are not the six provinces of Vanuatu and fit no admin1.
  The urban, rural, age, education, wealth and language rows, because the panel holds no id for
  a residence, education, wealth or language breakdown and the age rows within 15-24 fit no
  panel age group.
  Table HA.4 (knowledge of mother-to-child transmission), Table HA.5 (accepting attitudes) and
  Table HA.6 (women tested for HIV), because the panel holds no id for knowledge of
  mother-to-child transmission or for accepting attitudes, and the panel testing ids count tests
  or people and carry no survey share.

Source type. survey, a household survey.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_URL = "http://www.childinfo.org/files/MICS3_Vanuatu_FinalReport_2007_Eng.pdf"
_TS = "20101222164918"
_WAYBACK = "https://web.archive.org/web/{ts}id_/{url}"
_NAME, _SIZE, _PREFIX = "vu_mics2007_report.pdf", 3_868_540, "b72c64515d5e"

# regions in the printed order, with Port Vila and Luganville apart from Shefa and Sanma
_REGIONS = ("Tafea", "Shefa", "Malampa", "Penama", "Sanma", "Torba", "Port Vila", "Luganville")
_AREAS = ("Urban", "Rural")
_AGES = ("15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49")
_SIDE = r"(?:(?:Region|Area|Age) )?"  # the side label printed on the line of one row

_PCT = r"(\d{1,3}\.\d)"
_NUM = r"(\d{1,3}(?:,?\d{3})?)"


def _page(pages: List[str], pattern: str, what: str) -> str:
    """The text of the one page matching `pattern`. Raises ValueError unless one page matches."""
    found = [p for p in pages if re.search(pattern, p, re.M)]
    if len(found) != 1:
        raise ValueError(f"{what} prints on {len(found)} pages, expected one")
    return found[0]


def _rows(text: str, labels: Iterable[str], width: int, what: str) -> Dict[str, Tuple]:
    """{label: (shares..., number)} for the rows `labels`, every row with `width` shares."""
    out: Dict[str, Tuple] = {}
    for label in labels:
        found = re.findall(r"^" + _SIDE + re.escape(label) + " " +
                           " ".join([_PCT] * width) + " " + _NUM + r"$", text, re.M)
        if len(found) != 1:
            raise ValueError(f"{what}: the row {label!r} prints {len(found)} times, expected once")
        vals = tuple(float(v) for v in found[0][:width])
        if any(v > 100 for v in vals):
            raise ValueError(f"{what}: the row {label!r} prints a share above 100 ({vals})")
        out[label] = vals + (float(found[0][width].replace(",", "")),)
    return out


def _table(pages: List[str], name: str, title: str, caption: str, width: int,
           labels: Iterable[str]) -> Tuple[Dict[str, Tuple], str]:
    """({label: (shares..., number)}, page text) of one HA table, after the caption gate."""
    text = _page(pages, r"^Table " + re.escape(name) + ": " + re.escape(title) + "$", name)
    flat = re.sub(r"\s+", " ", text)
    if caption + ", Vanuatu, 2007" not in flat:
        raise ValueError(f"{name} does not print the caption with Vanuatu, 2007")
    return _rows(text, labels, width, name), text


def _adds(parts: List[Tuple[float, float]], share: float, number: float, tol_n: float,
          what: str) -> None:
    """Check the numbers of `parts` add to `number` within `tol_n` and the weighted shares give
    `share` within 0.1."""
    added = sum(n for _, n in parts)
    if abs(added - number) > tol_n:
        raise ValueError(f"{what}: the numbers add to {added:.0f}, against {number:.0f}")
    mean = sum(v * n for v, n in parts) / added
    if abs(mean - share) > 0.1:
        raise ValueError(f"{what}: the rows give {mean:.3f}, against the printed {share}")


def _reversed(page: str) -> str:
    """The words of a page whose text layer runs backwards, the right way round."""
    return " ".join(page[::-1].split())


def _sampling(pages: List[str]) -> Dict[str, float]:
    """The Table HA.3 row of Table SE 01 (total sample), after the interval gates."""
    found = [r for r in (_reversed(p) for p in pages)
             if "Table SE 01: Sampling: Total sample" in r]
    if len(found) != 1:
        raise ValueError(f"Table SE 01 prints on {len(found)} pages, expected one")
    rows = re.findall(r"among young people HA\.3 (\d\.\d{4}) (\d\.\d{5}) \S+ \S+ \S+ "
                      r"(\d{1,3}(?:,\d{3})?) (\d\.\d{4}) (\d\.\d{4}) Comprehensive knowledge "
                      r"about HIV prevention", found[0])
    if len(rows) != 1:
        raise ValueError(f"Table SE 01 prints the HA.3 row {len(rows)} times, expected once")
    r, se, unweighted, lower, upper = rows[0]
    r, se, lower, upper = float(r), float(se), float(lower), float(upper)
    if abs(r - 2 * se - lower) > 0.001 or abs(r + 2 * se - upper) > 0.001 or \
            not lower <= r <= upper:
        raise ValueError(f"Table SE 01: the limits {lower} and {upper} disagree with r {r} and "
                         f"se {se}")
    return {"r": r, "unweighted": float(unweighted.replace(",", "")), "lower": lower,
            "upper": upper}


def parse(pages: List[str]) -> Dict[str, Dict[str, object]]:
    """{age_group: {value, number, ...}} for the national rows, after the gates of the module
    docstring. Raises ValueError when any gate fails."""
    labels = _REGIONS + _AREAS + _AGES + ("National",)
    ha3, ha3_text = _table(pages, "HA.3", "Comprehensive knowledge of HIV/AIDS transmission",
                           "Percentage of women aged 15-49 years who have comprehensive "
                           "knowledge of HIV/AIDS transmission", 3, labels + ("15-24*",))
    ha2, ha2_text = _table(pages, "HA.2", "Identifying misconceptions about HIV/AIDS",
                           "Percentage of women aged 15-49 years who correctly identify "
                           "misconceptions about HIV/AIDS", 5, labels)
    ha1, _ = _table(pages, "HA.1", "Knowledge of preventing HIV transmission",
                    "Percent of women who have comprehensive knowledge of HIV/AIDS "
                    "transmission", 7, labels)
    if "* MICS Indicator 82; MDG Indicator 19b" not in ha3_text:
        raise ValueError("HA.3 does not print the footnote MICS Indicator 82")
    for label, (ways, misc, know, number) in ha3.items():
        if know > min(ways, misc):
            raise ValueError(f"HA.3: the row {label!r} prints comprehensive knowledge {know} "
                             f"above {ways} or {misc}")
        if label == "15-24*":
            continue
        if ha2[label][3] != misc or ha2[label][5] != number:
            raise ValueError(f"HA.2: the row {label!r} prints {ha2[label]}, against "
                             f"{misc} and {number:.0f} women in HA.3")
        all_three, condom_or_partner = ha1[label][4], min(ha1[label][1], ha1[label][2])
        if ha1[label][7] != number or not all_three <= ways <= condom_or_partner:
            raise ValueError(f"HA.1: the row {label!r} prints {ha1[label]}, against "
                             f"{ways} and {number:.0f} women in HA.3")
    share, number = ha3["National"][2], ha3["National"][3]
    _adds([(ha3[a][2], ha3[a][3]) for a in _AREAS], share, number, 0, "HA.3 urban and rural")
    _adds([(ha3[r][2], ha3[r][3]) for r in _REGIONS], share, number, 1, "HA.3 regions")
    _adds([(ha3[a][2], ha3[a][3]) for a in _AGES], share, number, 1, "HA.3 age groups")
    young, young_n = ha3["15-24*"][2], ha3["15-24*"][3]
    _adds([(ha3[a][2], ha3[a][3]) for a in _AGES[:2]], young, young_n, 0, "HA.3 15-24")
    flat = re.sub(r"\s+", " ", ha3_text)
    if f"Overall, {round(share)} percent respondents have comprehensive" not in flat:
        raise ValueError(f"the HA.3 text does not round the national share {share} to "
                         f"{round(share)} per cent")
    if "HIV can be transmitted by mosquito bites, and ii) HIV can be transmitted by sharing " \
            "food" not in re.sub(r"\s+", " ", ha2_text):
        raise ValueError("the report does not name the two misconceptions")
    summary = _page(pages, r"^HIV/AIDS 82 19b Comprehensive knowledge about HIV prevention "
                    r"among young$", "the summary table")
    found = re.findall(r"^knowledge and people (\d{1,3}\.\d) percent$", summary, re.M)
    if found != [f"{share}"]:
        raise ValueError(f"the summary table prints {found} for indicator 82, against the "
                         f"HA.3 national share {share}")
    se = _sampling(pages)
    if abs(se["r"] * 100 - young) > 0.05:
        raise ValueError(f"Table SE 01 prints r {se['r']}, against the HA.3 15-24 share {young}")
    return {"15-49": {"value": share, "number": number},
            "15-24": {"value": young, "number": young_n, "indicator": "82",
                      "unweighted": se["unweighted"], "lower": round(se["lower"] * 100, 1),
                      "upper": round(se["upper"] * 100, 1)}}


_RECONCILE = ("pacific_data_hub carries the Vanuatu Demographic and Health Survey (DHS) of 2013 on "
              "hiv_comprehensive_knowledge_survey_pct and no row for 2007, so the vu_mics rows "
              "overlap no other source (checked 25 October 2026)")
_SUMMARY = ("the summary table at the front of the report prints 16.3 per cent against indicator "
            "82 (comprehensive knowledge among young people), while Table HA.3 prints 16.3 per "
            "cent for women aged 15 to 49 and 15.4 per cent for women aged 15 to 24, and Table "
            "SE 01 confirms 15.4 per cent for young people, so the summary table mislabels the "
            "national share (ruling R69)")
_NOT_CARRIED = ("the other columns of Tables HA.1 to HA.3, the region rows, which split Port Vila "
                "from Shefa and Luganville from Sanma and fit no admin1, the urban, rural, age, "
                "education, wealth and language rows, and Tables HA.4 to HA.6 (mother-to-child "
                "transmission, accepting attitudes and women tested), which fit no panel id "
                "(ruling R69)")


class VanuatuMICSConnector(BaseConnector):
    """Printed tables of the Vanuatu MICS 2007 report, from a Wayback capture."""

    source_id = "vu_mics"
    default_source_type = SourceType.SURVEY
    description = ("Vanuatu National Statistics Office and UNICEF, Multiple Indicator Cluster "
                   "Survey 2007, read from a Wayback capture, comprehensive knowledge about HIV "
                   "among women aged 15 to 49 and 15 to 24, national (to-source).")
    country = "VUT"
    timeout = 300
    # The Wayback Machine refused the ni_mapasalud runs of October 2026 with HTTP 429 at short
    # pauses, so the connector keeps the np_ncasc pacing. The connector tries the capture four
    # times and waits 10, 15 and 15 minutes after a 429 or a network error.
    request_pause = 30.0

    def __init__(self, raw_dir: str = "data/raw/vu_mics", **kw):
        kw.setdefault("max_retries", 4)
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _retry_wait(self, attempt: int, status: Optional[int]) -> float:
        if attempt >= self.max_retries:
            return 0
        if status in (429, None):
            return 600 if attempt == 1 else 900
        return super()._retry_wait(attempt, status)

    def _pdf_path(self) -> Path:
        """Local copy of the capture, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _NAME
        capture = _WAYBACK.format(ts=_TS, url=_URL)
        if path.exists():
            log.info("vu_mics: using cached %s", path)
        else:
            blob = self._request("GET", capture).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{capture} did not return a PDF (got {blob[:16]!r})")
            if not blob.rstrip().endswith(b"%%EOF"):
                raise RuntimeError(f"{capture} returned {len(blob)} bytes with no end-of-file "
                                   "marker, a truncated copy")
            path.write_bytes(blob)
            log.info("vu_mics: downloaded the capture of %s (%d bytes) -> %s", _TS, len(blob),
                     path)
        blob = path.read_bytes()
        if not blob.startswith(b"%PDF") or not blob.rstrip().endswith(b"%%EOF"):
            raise RuntimeError(f"the cached copy is not a complete PDF ({len(blob)} bytes)")
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (_SIZE, _PREFIX):
            log.info("vu_mics: the report matches the copy read on 25 October 2026 (sha256 %s)",
                     digest[:12])
        else:
            log.warning("vu_mics: the report differs from the copy read on 25 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes), and the gates still run",
                        len(blob), digest[:12], _SIZE)
        return path

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = {c.upper() for c in countries} if countries else None
        if (wanted and self.country not in wanted) or not start_year <= 2007 <= end_year:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("vu_mics: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
            with pdfplumber.open(str(path)) as pdf:
                records = parse([p.extract_text() or "" for p in pdf.pages])
        except Exception as exc:
            log.warning("vu_mics: the report failed (%s), no row emitted", exc)
            return
        emitted = 0
        for age in ("15-24", "15-49"):
            rec = records[age]
            extra = {"survey": "MICS",
                     "report": "Vanuatu MICS 2007 final report, Table HA.3",
                     "sample_universe": "All Women",
                     "survey_age_range": "15-49",
                     "denominator_weighted": rec["number"],
                     "misconceptions": "transmission by mosquito bites and by sharing food",
                     "page_url": _URL,
                     "capture_url": _WAYBACK.format(ts=_TS, url=_URL),
                     "captured": f"{_TS[:4]}-{_TS[4:6]}-{_TS[6:8]}",
                     "summary_table": _SUMMARY,
                     "reconcile_with": _RECONCILE,
                     "not_carried": _NOT_CARRIED}
            if "indicator" in rec:
                extra["mics_indicator"] = rec["indicator"]
                extra["denominator_unweighted"] = rec["unweighted"]
                extra["interval"] = "printed confidence limits r - 2se and r + 2se, Table SE 01"
            emitted += 1
            yield self.make_row(
                country_iso3="VUT", country_name="Vanuatu",
                admin1="", indicator_id="hiv_comprehensive_knowledge_survey_pct", year=2007,
                value=rec["value"], value_lower=rec.get("lower"), value_upper=rec.get("upper"),
                unit="percent", population_group="all", sex="female", age_group=age,
                source_url=_URL,
                source_indicator_code=f"vut_mics_2007:Table HA.3:{age}",
                extra=extra,
            )
        log.info("vu_mics: emitted %d rows", emitted)
