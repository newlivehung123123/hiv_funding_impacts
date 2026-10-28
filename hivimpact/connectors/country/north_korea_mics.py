"""
Democratic People's Republic of Korea (DPRK), comprehensive knowledge about HIV among women from
the printed tables of the DPRK Multiple Indicator Cluster Survey (MICS) of 2009, carried out by
the Central Bureau of Statistics (CBS) of the DPRK with the United Nations Children's Fund
(UNICEF), connector 69.

Source. "Democratic People's Republic of Korea Multiple Indicator Cluster Survey 2009, Final
Report" (CBS and UNICEF, December 2010, 150 pages) is on the website of the United Nations in
the DPRK at https://dprk.un.org/sites/default/files/2019-07/03.10.b_MICS_DPRK_2009.pdf,
2,030,354 bytes, read on 21 October 2026. No sign-in and no key. The connector downloads the
file once into `raw_dir`, every later run reads the cached copy, and the connector reads the
pdfplumber text layer with no optical character recognition. The DHS Program API holds no DPRK
survey, and no other panel source carries a DPRK row on hiv_comprehensive_knowledge_survey_pct.

Tables read.
  Table HA.1 (women aged 15 to 49) and Table HA.2 (women aged 15 to 24), column "Percentage with
  comprehensive knowledge", MICS indicators 9.1 and 9.2, for the 10 provinces and the total.
  The report surveyed all 10 provinces for the first time in 2009. Comprehensive knowledge
  means knowing condom use and a single faithful uninfected partner prevent HIV, knowing a
  healthy-looking person can have HIV, and rejecting the two most common local misconceptions,
  which the report names as transmission by mosquito bites and by sharing food.
  Tables SE.2 and SE.5 to SE.14 (sampling errors for the total and for every province), row
  "Comprehensive knowledge about HIV prevention among young people" (Table HA.2), with the
  printed confidence limits, r minus two standard errors and r plus two standard errors. The
  sampling-error tables print no row for women aged 15 to 49.

Gates. The report enters only when every check below passes, because two printed figures
disagreeing leave the true figure unknown.
  Every table prints once, with the caption, "DPR Korea, 2009" and the MICS indicator footnote.
  Every row prints 10 percentages and a number of women, with the knowledge share no larger
  than the share rejecting the two misconceptions and knowing a healthy-looking person can
  have HIV.
  The province numbers add to the total number exactly in Table HA.1 (8,249) and within five
  in Table HA.2 (2,344), and the province shares weighted by the numbers give the total share
  within 0.1.
  The "15-24" age row of Table HA.1 equals the total row of Table HA.2.
  For the total and every province, the sampling-error weighted count equals the Table HA.2
  number, r times 100 equals the Table HA.2 share within 0.05, and the printed limits equal
  r minus and plus two standard errors within 0.001 and hold r.

What the connector emits. 22 rows for PRK, 2009, hiv_comprehensive_knowledge_survey_pct,
women, population_group "all", a national row (admin1 blank) and 10 province rows (admin1 the
printed province name) for age_group 15-49 from Table HA.1, with no interval, and the same 11
rows for age_group 15-24 from Table HA.2, with value_lower and value_upper the printed
confidence limits times 100. extra carries the weighted denominator, the unweighted
denominator for the 15-24 rows, the sample universe and the survey's own age range under the
keys the dhs connector uses, the MICS indicator, the two misconceptions and the caution of the
report on provincial estimates.

Not carried.
  The other columns of Table HA.1 and Table HA.2, which fit no panel id.
  Table HA.3 (knowledge of mother-to-child transmission) and Table HA.4 (accepting attitudes),
  because the panel holds no id for knowledge of mother-to-child transmission or for accepting
  attitudes.
  The urban, rural, age and education rows, because the panel holds no id for a residence or
  education breakdown and the age rows within 15-24 fit no panel age group.
  The DPRK MICS of 2017 (UNICEF, June 2018), whose report holds no HIV module.

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

_URL = "https://dprk.un.org/sites/default/files/2019-07/03.10.b_MICS_DPRK_2009.pdf"
_NAME, _SIZE, _PREFIX = "dprk_mics2009_report.pdf", 2_030_354, "e07d4d66ca42"

# provinces in the printed order, region number of the sampling-error tables
_PROVINCES = ("Ryanggang", "North Hamgyong", "South Hamgyong", "Kangwon", "Jagang",
              "North Phyongan", "South Phyongan", "North Hwanghae", "South Hwanghae", "Pyongyang")

_PCT = r"(\d{1,3}\.\d)"
_NUM = r"(\d{1,3}(?: \d{3})*)"  # the report prints a space as the thousands separator


def _page(pages: List[str], pattern: str, what: str) -> str:
    """The text of the one page matching `pattern`. Raises ValueError unless one page matches."""
    found = [p for p in pages if re.search(pattern, p)]
    if len(found) != 1:
        raise ValueError(f"{what} prints on {len(found)} pages, expected one")
    return found[0]


def _row(text: str, label: str, what: str) -> Tuple[float, float]:
    """(knowledge share, number of women) of the row `label`, after the row gates."""
    found = re.findall(r"^" + label + " " + " ".join([_PCT] * 10) + " " + _NUM + r"$", text,
                       re.M)
    if len(found) != 1:
        raise ValueError(f"{what}: the row {label!r} prints {len(found)} times, expected once")
    vals = [float(v) for v in found[0][:10]]
    if any(v > 100 for v in vals) or vals[9] > vals[8]:
        raise ValueError(f"{what}: the row {label!r} prints {vals}, with comprehensive "
                         f"knowledge above the share rejecting the misconceptions")
    return vals[9], float(found[0][10].replace(" ", ""))


def _table(pages: List[str], name: str, caption: str,
           footnote: str, tol_n: float) -> Tuple[Dict[str, Tuple[float, float]], str]:
    """({admin1: (share, number)}, page text) of Table HA.1 or HA.2, after the table gates."""
    text = _page(pages, r"\ATable " + name.replace(".", r"\.") + r": Knowledge about HIV "
                 r"transmission", name)
    flat = re.sub(r"\s+", " ", text)
    if caption not in flat or footnote not in text or "DPR Korea, 2009" not in flat:
        raise ValueError(f"{name} does not print the caption, the footnote or DPR Korea, 2009")
    out = {p: _row(text, p, name) for p in _PROVINCES}
    out[""] = _row(text, "Total", name)
    share, number = out[""]
    parts = [out[p] for p in _PROVINCES]
    added = sum(n for _, n in parts)
    if abs(added - number) > tol_n:
        raise ValueError(f"{name}: the province numbers add to {added}, against {number}")
    mean = sum(v * n for v, n in parts) / added
    if abs(mean - share) > 0.1:
        raise ValueError(f"{name}: the provinces give {mean:.3f}, against the printed {share}")
    return out, text


def _sampling(pages: List[str], domain: str) -> Dict[str, float]:
    """The Table HA.2 row of the sampling-error table for `domain` ("Total sample" or
    "Region N - Province")."""
    text = _page(pages, r"\ATable SE\.\d+: Sampling errors: " + re.escape(domain) + r"\n",
                 f"the sampling-error table for {domain}")
    found = re.findall(r"^HA\.2 (\d?\.\d{4}) (\.\d{5}) \S+ \S+ \S+ (\d+) (\d+) (\d\.\d{3}) "
                       r"(\d\.\d{3})$", text, re.M)
    if len(found) != 1 or "Comprehensive knowledge about HIV prevention" not in text:
        raise ValueError(f"the sampling-error table for {domain} prints the HA.2 row "
                         f"{len(found)} times, expected once")
    r, se, weighted, unweighted, lower, upper = (float(v) for v in found[0])
    if abs(r - 2 * se - lower) > 0.001 or abs(r + 2 * se - upper) > 0.001 or \
            not lower <= r <= upper:
        raise ValueError(f"{domain}: the limits {lower} and {upper} disagree with r {r} and "
                         f"se {se}")
    return {"r": r, "weighted": weighted, "unweighted": unweighted, "lower": lower,
            "upper": upper}


def parse(pages: List[str]) -> Dict[Tuple[str, str], Dict[str, object]]:
    """{(admin1, age_group): {value, number, ...}} after the gates of the module docstring.
    admin1 is blank for the national rows. Raises ValueError when any gate fails."""
    women, women_text = _table(pages, "HA.1", "Percentage of women aged 15-49 years who know "
                               "the main ways of preventing HIV transmission",
                               "MICS indicator 9.1", 0)
    young, young_text = _table(pages, "HA.2", "Percentage of young women aged 15-24 years who "
                               "know the main ways of preventing HIV transmission",
                               "MICS indicator 9.2", 5)
    if _row(women_text, "15-24", "HA.1") != young[""]:
        raise ValueError("the 15-24 row of Table HA.1 differs from the total of Table HA.2")
    flat = re.sub(r"\s+", " ", young_text)
    if "transmitted by mosquito bites and by sharing food" not in flat:
        raise ValueError("the report does not name the two misconceptions")
    out: Dict[Tuple[str, str], Dict[str, object]] = {}
    for admin1, (value, number) in women.items():
        out[(admin1, "15-49")] = {"value": value, "number": number, "indicator": "9.1",
                                  "table": "Table HA.1"}
    domains = {"": "Total sample"}
    domains.update({p: f"Region {i} - {p}" for i, p in enumerate(_PROVINCES, start=1)})
    for admin1, (value, number) in young.items():
        se = _sampling(pages, domains[admin1])
        if se["weighted"] != number or abs(se["r"] * 100 - value) > 0.05:
            raise ValueError(f"{domains[admin1]}: the sampling-error row ({se['r']}, "
                             f"{se['weighted']:.0f} women) differs from Table HA.2 ({value}, "
                             f"{number:.0f} women)")
        out[(admin1, "15-24")] = {"value": value, "number": number, "indicator": "9.2",
                                  "table": "Table HA.2", "unweighted": se["unweighted"],
                                  "lower": round(se["lower"] * 100, 1),
                                  "upper": round(se["upper"] * 100, 1)}
    return out


_RECONCILE = "No other source carries a DPRK row on hiv_comprehensive_knowledge_survey_pct"
_NOT_CARRIED = ("the other columns of Tables HA.1 and HA.2, Table HA.3 (mother-to-child "
                "transmission) and Table HA.4 (accepting attitudes), which fit no panel id, the "
                "urban, rural, age and education rows, and the DPRK MICS 2017, whose report "
                "holds no HIV module (ruling R58)")


class NorthKoreaMICSConnector(BaseConnector):
    """Printed tables of the DPRK MICS 2009 report."""

    source_id = "prk_cbs_mics"
    default_source_type = SourceType.SURVEY
    description = ("Central Bureau of Statistics of the DPRK and UNICEF, Multiple Indicator "
                   "Cluster Survey 2009, comprehensive knowledge about HIV among women aged 15 "
                   "to 49 and 15 to 24, national and province (to-source).")
    country = "PRK"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/prk_cbs_mics", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the report, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _NAME
        if path.exists():
            log.info("prk_cbs_mics: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("prk_cbs_mics: downloaded the report (%d bytes) -> %s", len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (_SIZE, _PREFIX):
            log.info("prk_cbs_mics: the report matches the copy read on 21 October 2026 "
                     "(sha256 %s)", digest[:12])
        else:
            log.warning("prk_cbs_mics: the report differs from the copy read on 21 October 2026 "
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
        if (wanted and self.country not in wanted) or not start_year <= 2009 <= end_year:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("prk_cbs_mics: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
            with pdfplumber.open(str(path)) as pdf:
                records = parse([p.extract_text() or "" for p in pdf.pages])
        except Exception as exc:
            log.warning("prk_cbs_mics: the report failed (%s), no row emitted", exc)
            return
        emitted = 0
        for (admin1, age), rec in sorted(records.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            extra = {"survey": "MICS",
                     "report": f"DPR Korea MICS 2009 final report, {rec['table']}",
                     "mics_indicator": rec["indicator"],
                     "sample_universe": "All Women",
                     "survey_age_range": "15-49",
                     "denominator_weighted": rec["number"],
                     "misconceptions": "transmission by mosquito bites and by sharing food",
                     "reconcile_with": _RECONCILE,
                     "not_carried": _NOT_CARRIED}
            if "unweighted" in rec:
                extra["denominator_unweighted"] = rec["unweighted"]
                extra["interval"] = "printed confidence limits r - 2se and r + 2se"
            if admin1:
                extra["report_caution"] = ("the report asks for provincial estimates to be "
                                           "interpreted with some caution")
            emitted += 1
            yield self.make_row(
                country_iso3="PRK", country_name="North Korea",
                admin1=admin1, indicator_id="hiv_comprehensive_knowledge_survey_pct", year=2009,
                value=rec["value"], value_lower=rec.get("lower"), value_upper=rec.get("upper"),
                unit="percent", population_group="all", sex="female", age_group=age,
                source_url=_URL,
                source_indicator_code=f"prk_mics_2009:{rec['table']}:{admin1 or 'national'}",
                extra=extra,
            )
        log.info("prk_cbs_mics: emitted %d rows", emitted)
