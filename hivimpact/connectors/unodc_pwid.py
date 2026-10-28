"""
UNODC estimates of people who inject drugs and of HIV among people who inject drugs, ruling R24
(research/rulings_2026-10-15.md).

Source: table 4.1 of the statistical annex of the World Drug Report 2026 of UNODC (the United
Nations Office on Drugs and Crime), the workbook
    https://www.unodc.org/documents/data-and-analysis/WDR_2026/Annex/
        4.1_people_who_inject_drugs_and_prevalence_of_diseases.xlsx
Two sheets of the workbook enter the panel, with population_group pwid:
    "HIV among PWID"  HIV prevalence among people who inject drugs   -> kp_hiv_prevalence (percent)
    "PWID"            the number of people who inject drugs          -> kp_size_estimate (count)
The low and high estimates become value_lower and value_upper, and the year is the year of
estimate printed by UNODC. The hepatitis C and hepatitis B sheets stay outside the panel.

Why the year of estimate: unaids_aidsinfo carries the same two measures stamped 2024, the year
UNAIDS compiled the figure, while UNODC prints the year of the survey behind the estimate.

A row enters only when
  * the geographical coverage reads exactly "National" (spaces collapsed), so a coverage with a
    qualifier, for example the Kenya survey of four counties, stays out;
  * the year of estimate is a single four-digit year;
  * the medium estimate is a number;
  * the gender reads "Both" or is blank;
  * the reference and the source name neither UNAIDS nor GARPR (the Global AIDS Response Progress
    Reporting of UNAIDS), because a UNODC row citing UNAIDS republishes a figure the panel already
    carries from unaids_aidsinfo;
  * the method class printed by UNODC (the classification of Mathers and colleagues, 2008, on the
    Notes sheet) is a class carried for the sheet, so a prevalence from the registration or
    notification of cases at treatment services (class B) or from self-reported HIV status
    (class C), and a number taken from treatment or other registers of drug users (class C), stay
    out, because a register describes the people known to services and not the whole key
    population, and a row with no method printed stays out too;
  * the definition of injecting names no lifetime injecting ("lifetime" or "ever"), because a
    count or a prevalence over everyone who ever injected takes in people who stopped injecting
    years before, while a blank definition and every recent period (past month, past six months,
    past year, current, active) are carried, with the period in extra;
  * the country name maps to an ISO3 code through normalize.to_iso3.
A row whose low estimate exceeds the medium estimate, or whose medium estimate exceeds the high
estimate, is refused, and so is every row of a country printed twice among the rows kept.
sex and age_group stay "all", as in the unaids_aidsinfo rows of the same two indicators, and the
definition of injecting, the age group, the gender, the coverage, the reference, the method and
the source go into extra as printed, with the method class in extra["method_class"]. source_type
is survey for every row, as the indicator catalogue declares for both indicators.

Gates. A header of either sheet that differs from the header read on 16 October 2026 refuses the
whole sheet.

The workbook downloads once into `raw_dir`, and every later run reads the cached copy. A copy whose
size or sha256 differs from the copy read on 16 October 2026 is logged, and the gates still run.
"""
from __future__ import annotations

import hashlib
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..connector_base import BaseConnector
from ..normalize import name_for, to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_URL = ("https://www.unodc.org/documents/data-and-analysis/WDR_2026/Annex/"
        "4.1_people_who_inject_drugs_and_prevalence_of_diseases.xlsx")
_LOCAL = "4.1_people_who_inject_drugs_and_prevalence_of_diseases.xlsx"
#: (size, sha256) of the copy read on 16 October 2026
_KNOWN = (169407, "e6ef72dd47256b4d7a5fa9aba3cf0e2fda0d0e8b051e5e4e27557f522b07dc5a")
_FIRST_DATA_ROW = 5

#: sheet -> indicator, unit, the column of every field, and the header read on 16 October 2026
#: as {(row, column): text}
_SHEETS: Dict[str, Dict] = {
    "HIV among PWID": {
        "indicator": "kp_hiv_prevalence", "unit": "percent",
        "code": "WDR 2026 annex table 4.1, HIV among PWID, prevalence (%)",
        "cols": dict(low=4, mid=5, high=6, year=7, definition=8, age_group=9, gender=10,
                     coverage=11, sample_size=12, reference=13, method=14, source=15),
        # A seroprevalence study (A1 multi-site, A2 single sample type), D1 official government
        # estimate or modelling study. B registration and C self-reported status are not carried.
        "classes": {"A", "A1", "A2", "D1"},
        "header": {(0, 2): "Country/Territory", (0, 4): "HIV Among People Who Inject Drugs",
                   (2, 4): "Prevalence (%)", (2, 7): "Year of estimate",
                   (2, 8): "Definition of injecting", (2, 9): "Age group", (2, 10): "Gender",
                   (2, 11): "Geographical coverage", (2, 12): "Sample size", (2, 13): "Reference",
                   (2, 14): "Method", (2, 15): "Source", (3, 4): "low", (3, 5): "medium",
                   (3, 6): "high"},
    },
    "PWID": {
        "indicator": "kp_size_estimate", "unit": "count",
        "code": "WDR 2026 annex table 4.1, PWID, number",
        "cols": dict(low=7, mid=8, high=9, year=10, definition=11, age_group=12, gender=13,
                     coverage=14, reference=15, method=16, source=17),
        # A indirect estimate, B1 mapping and enumeration, B2 general population survey, D1 official
        # government estimate, expert judgement, modelling or consensus. C registers are not carried.
        "classes": {"A", "B1", "B2", "D1"},
        "header": {(0, 2): "Country/Territory", (0, 4): "People Who Inject Drugs",
                   (2, 4): "Prevalence (%)", (2, 7): "Number", (2, 10): "Year of esimate",
                   (2, 11): "Definition of injecting", (2, 12): "Age group", (2, 13): "Gender",
                   (2, 14): "Geographical coverage", (2, 15): "Reference", (2, 16): "Method",
                   (2, 17): "Source", (3, 7): "low", (3, 8): "medium", (3, 9): "high"},
    },
}
_LIFETIME = re.compile(r"\b(lifetime|ever)\b", re.I)
_EXTRA_FIELDS = ("definition", "age_group", "gender", "coverage", "sample_size", "reference",
                 "method", "source")


def _num(x) -> Optional[float]:
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def _text(x) -> str:
    return " ".join(str(x).split()) if x is not None else ""


def _method_class(method: str) -> str:
    """The class code before the first semicolon or colon, for example "A" of "A: Indirect Estimates"."""
    head = method.replace(":", ";").split(";", 1)[0].strip().upper()
    return head if head and len(head) <= 2 and " " not in head else ""


def _header_ok(sheet: str, rows: List[tuple]) -> bool:
    for (r, c), want in _SHEETS[sheet]["header"].items():
        got = _text(rows[r][c]) if r < len(rows) and c < len(rows[r]) else ""
        if got != want:
            log.warning("unodc_pwid: sheet %r refused, the header at row %d, column %d reads %r and "
                        "not %r", sheet, r, c, got, want)
            return False
    return True


def parse_sheet(sheet: str, rows: List[tuple]) -> Tuple[List[Dict], Counter]:
    """Apply the R24 entry rules to one sheet, returning the rows kept and the reasons refused."""
    spec = _SHEETS[sheet]
    c = spec["cols"]
    refused: Counter = Counter()
    if not _header_ok(sheet, rows):
        refused["header"] += 1
        return [], refused
    kept: List[Dict] = []
    for r in rows[_FIRST_DATA_ROW:]:
        name = _text(r[2]) if len(r) > 2 else ""
        if not name:
            continue
        cell = lambda k: r[c[k]] if c[k] < len(r) else None
        if _text(cell("coverage")) != "National":
            refused["coverage not National"] += 1
            continue
        year = cell("year")
        if not (isinstance(year, int) and not isinstance(year, bool) and 1000 <= year <= 9999):
            refused["year not a single year"] += 1
            continue
        mid = _num(cell("mid"))
        if mid is None:
            refused["medium estimate not a number"] += 1
            continue
        if _text(cell("gender")) not in ("Both", ""):
            refused["gender not Both or blank"] += 1
            continue
        cited = (_text(cell("reference")) + " " + _text(cell("source"))).lower()
        if "unaids" in cited or "garpr" in cited:
            refused["reference or source names UNAIDS or GARPR"] += 1
            continue
        klass = _method_class(_text(cell("method")))
        if klass not in spec["classes"]:
            refused[f"method class {klass or 'blank'} not carried"] += 1
            continue
        if _LIFETIME.search(_text(cell("definition"))):
            refused["lifetime injecting"] += 1
            continue
        iso3 = to_iso3(name)
        if not iso3:
            refused["country name maps to no ISO3 code"] += 1
            log.info("unodc_pwid: %s, %r maps to no ISO3 code", sheet, name)
            continue
        low, high = _num(cell("low")), _num(cell("high"))
        if (low is not None and low > mid) or (high is not None and mid > high):
            refused["low, medium and high out of order"] += 1
            log.warning("unodc_pwid: %s, %s %d refused, low %s, medium %s, high %s", sheet, iso3,
                        year, low, mid, high)
            continue
        if spec["unit"] == "percent" and not 0 <= mid <= 100:
            refused["percent outside 0 to 100"] += 1
            continue
        if spec["unit"] == "count" and mid <= 0:
            refused["count not positive"] += 1
            continue
        extra = {"sheet": sheet, "country_printed": name, "method_class": klass}
        for k in _EXTRA_FIELDS:
            if k in c and _text(cell(k)):
                extra[k] = _text(cell(k))
        kept.append(dict(iso3=iso3, year=year, value=mid, lower=low, upper=high, extra=extra))
    twice = {k for k, v in Counter(x["iso3"] for x in kept).items() if v > 1}
    if twice:
        refused["country printed twice"] += sum(x["iso3"] in twice for x in kept)
        log.warning("unodc_pwid: %s, every row of %s refused, the country is printed twice", sheet,
                    sorted(twice))
        kept = [x for x in kept if x["iso3"] not in twice]
    return kept, refused


class UNODCPWIDConnector(BaseConnector):
    """UNODC World Drug Report 2026, HIV prevalence among and the number of people who inject drugs."""

    source_id = "unodc_pwid"
    default_source_type = SourceType.SURVEY
    description = ("World Drug Report 2026 of UNODC, annex table 4.1, HIV prevalence among people "
                   "who inject drugs and the number of people who inject drugs, national estimates "
                   "at the year of estimate, with UNAIDS-cited rows not carried.")
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/unodc_pwid", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _path(self) -> Path:
        """Local copy of the workbook, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("unodc_pwid: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"PK"):
                raise RuntimeError(f"{_URL} did not return a workbook (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("unodc_pwid: downloaded %d bytes -> %s", len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest) == _KNOWN:
            log.info("unodc_pwid: the workbook matches the copy read on 16 October 2026 (sha256 %s)",
                     digest[:12])
        else:
            log.warning("unodc_pwid: the workbook differs from the copy read on 16 October 2026 (%d "
                        "bytes, sha256 %s), and the gates still run", len(blob), digest[:12])
        return path

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = {c.upper() for c in countries} if countries else None
        try:
            import openpyxl
        except ImportError:
            log.error("unodc_pwid: openpyxl not installed (pip install openpyxl)")
            return
        try:
            path = self._path()
        except Exception as exc:
            log.warning("unodc_pwid: the workbook could not be fetched (%s)", exc)
            return
        try:
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            sheets = {s: list(wb[s].iter_rows(values_only=True)) for s in _SHEETS}
            wb.close()
        except Exception as exc:
            log.warning("unodc_pwid: the workbook failed to open (%s)", exc)
            return
        for sheet, rows in sheets.items():
            spec = _SHEETS[sheet]
            kept, refused = parse_sheet(sheet, rows)
            emitted = 0
            for k in kept:
                if wanted and k["iso3"] not in wanted:
                    continue
                if not start_year <= k["year"] <= end_year:
                    continue
                emitted += 1
                yield self.make_row(
                    country_iso3=k["iso3"], country_name=name_for(k["iso3"]),
                    indicator_id=spec["indicator"], year=k["year"], value=k["value"],
                    value_lower=k["lower"], value_upper=k["upper"],
                    population_group="pwid", unit=spec["unit"],
                    source_url=_URL, source_indicator_code=spec["code"], extra=k["extra"],
                )
            log.info("unodc_pwid: %s, %d rows kept, %d emitted, refused %s", sheet, len(kept),
                     emitted, dict(refused))
