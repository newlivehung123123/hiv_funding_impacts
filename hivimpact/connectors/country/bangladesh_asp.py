"""
Bangladesh, notified HIV cases from the World AIDS Day files of the AIDS/STD Programme (ASP) of
the Directorate General of Health Services (https://asp.gov.bd/), connector 62.

Source. The ASP page of the Bangladesh national portal has one page for every World AIDS Day
from 2016 to 2025, and every World AIDS Day page links one born-digital PDF file on the Oracle
cloud object store of the portal. The file names are 32-character hashes, so the year of a file
comes from the ASP page which links the file (research/phase6_sas/sas_round1_notes.md,
Bangladesh). The 10 files were read on 21 October 2026. No sign-in and no key. The connector
downloads every file once into `raw_dir`, every later run reads the cached copies, and the
connector reads the pdfplumber text layer with no optical character recognition.

Table read. Every file prints a table of new cases, "Reported Cases-2017" from 2017 and "New
HIV and Death Cases" in 2016, with the people newly reported HIV positive in the reporting year
and the cumulative count since 1989, and from 2017 a line naming the Forcibly Displaced Myanmar
Nationals (FDMN, the Rohingya refugees of Cox's Bazar) among the new cases.

Reporting year. The ASP reporting year runs from 1 November of the year before to 31 October,
and the World AIDS Day file of the year states the period ("(November, 2016- October, 2017)",
and in 2016 "Reporting Period: 1st Nov, 2015 to 31st Oct, 2016"). The row year is the year in
which the reporting year ends, and extra.reporting_period names the 12 months (ruling R42 of
research/rulings_2026-10-15.md). The 2018 and 2019 annual reports of the ASP repeat the counts of
the World AIDS Day files (869 and 919) although the 2019 annual report says the report covers
January to December 2019, so the World AIDS Day period statement is the authority.

Gates. The series enters only when every check below passes, because two published figures
disagreeing leave the true figure unknown.
  Every file states a reporting period from 1 November of the year before to 31 October of the
  World AIDS Day year.
  Every file prints one count line, and the line after the "New Cases in" heading starts with
  the World AIDS Day year.
  From 2017 every file prints one FDMN count, no larger than the new cases.
  The cumulative count of every year equals the cumulative count of the year before plus the
  new cases of the year, from 2016 to 2025.

What the connector emits. National notified_hiv_cases, age group and sex "all", for 2016 to
2025, as the people newly reported HIV positive in the ASP reporting year, FDMN cases included.
The cumulative count and the FDMN count travel in extra.

Not carried.
  The deaths, because the 2024 and 2025 files add deaths of the year before to the cumulative
  count, so the yearly death counts do not chain (2,086 in 2023 plus 195 in 2024 gives 2,281,
  where the 2024 note gives 2,412).
  The split by sex and by age, printed as shares and charts alone.
  The yearly chart labels before 2016, whose reporting period no file states.
  The testing and screening counts, which mix tests and screenings across programmes.

Source type. routine_programme_record, the national HIV case reports of the ASP.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_BASE = ("https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/"
         "o/office-asp/2024/12/")
# World AIDS Day year: (ASP page id, file name, size and sha256 prefix of the copy read on
# 21 October 2026)
_FILES = {
    2016: ("6922e11d933eb65569e2a4b0", "8d4112c2e32d4ebd900c976abb987c11.pdf", 1_469_357, "b7a5c5eb4594"),
    2017: ("6922e121933eb65569e2a685", "1c7161515f904894b33c9a3ca45b4f49.pdf", 855_140, "6ede2dc7dcf6"),
    2018: ("6922ddaa933eb65569e15cb6", "c6bbf88499ba45a1a8857517712f1a40.pdf", 1_163_567, "22d165f212c9"),
    2019: ("6922dbfa933eb65569e0dc38", "a78f0b95cf174cdd8b5e79200f4bd5dd.pdf", 1_207_097, "e5ef860c7176"),
    2020: ("6922dee9933eb65569e1e544", "788b26dbb9b0423d9a2003539d49809b.pdf", 1_473_040, "e7e1eaa483b8"),
    2021: ("6922e11d933eb65569e2a4d8", "72fcbf5439fe40ef92f0a44e340a7ed8.pdf", 1_042_208, "8d88520194f4"),
    2022: ("6922dcf8933eb65569e12fb6", "f1ae11518ac947828bfffdecd1d3b0a4.pdf", 1_696_168, "5ab7727b87a8"),
    2023: ("6922e038933eb65569e260d0", "763d813b862d47c199b8ff5d7b979d28.pdf", 1_350_391, "4bd9f4df3e92"),
    2024: ("6922e0a9933eb65569e28118", "a30b7bb8bb6844c69bf7319d88084183.pdf", 1_886_421, "637e00246400"),
    2025: ("695b9afdc4774958d7b7092e", "82940dfa3995443e919f89587c073d1b.pdf", 1_171_656, "85375e1a334f"),
}

_PERIOD = re.compile(r"\(November,\s*(\d{4})\s*-\s*October,\s*(\d{4})\)")
_PERIOD_2016 = re.compile(r"Reporting Period:\s*1st Nov,\s*(\d{4})\s*to\s*31st Oct,\s*(\d{4})")
_COUNT_LINE = re.compile(r"^HIV(?: positive)? ([\d,]+) ([\d,]+)$")
_HEADING = re.compile(r"New Cases in\b")
_FDMN = re.compile(r"\((?:Rohingya|FDMN)\) cases = ([\d,]+)")

_DEFINITION = ("people newly reported HIV positive in Bangladesh in the reporting year of the "
               "AIDS/STD Programme, 1 November of the year before to 31 October, FDMN cases "
               "included, the row \"HIV positive\" of the new-case table of the World AIDS Day "
               "file of the year")
_RECONCILE = ("No other source in the panel held Bangladeshi notified_hiv_cases rows when "
              "the connector was built (checked 21 October 2026). A calendar-year count would "
              "differ by the cases of November and December. Never compare with new_diagnoses "
              "(Jason's ruling of 8 October 2026)")
_NOT_CARRIED = ("the deaths (the 2024 and 2025 files add deaths of the year before to the "
                "cumulative count), the split by sex and by age (shares and charts alone), the "
                "chart labels before 2016 (no stated reporting period), and the testing and "
                "screening counts")


def _n(token: str) -> int:
    return int(token.replace(",", ""))


def _lines(text: str) -> List[str]:
    return [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]


def parse_file(text: str, wad_year: int) -> Dict:
    """The new-case table of one World AIDS Day file as {period, new, cumulative, fdmn}, after
    the gates of the module docstring which concern a single file. Raises ValueError when any
    gate fails."""
    periods = {(int(a), int(b)) for a, b in _PERIOD.findall(text)}
    if not periods:
        periods = {(int(a), int(b)) for a, b in _PERIOD_2016.findall(text)}
    if periods != {(wad_year - 1, wad_year)}:
        raise ValueError(f"{wad_year}, the file states the reporting periods {sorted(periods)}, "
                         f"expected November {wad_year - 1} to October {wad_year} alone")
    lines = _lines(text)
    counts = [m for m in (_COUNT_LINE.match(ln) for ln in lines) if m]
    if len(counts) != 1:
        raise ValueError(f"{wad_year}, the file prints {len(counts)} count lines, expected one")
    heads = [i for i, ln in enumerate(lines) if _HEADING.search(ln)]
    if len(heads) != 1 or not lines[heads[0] + 1].startswith(str(wad_year)):
        raise ValueError(f"{wad_year}, the heading 'New Cases in' does not name {wad_year}")
    new, cumulative = _n(counts[0].group(1)), _n(counts[0].group(2))
    fdmn: Optional[int] = None
    found = _FDMN.findall(text)
    if wad_year >= 2017:
        if len(found) != 1:
            raise ValueError(f"{wad_year}, the file prints {len(found)} FDMN counts, expected one")
        fdmn = _n(found[0])
        if fdmn > new:
            raise ValueError(f"{wad_year}, the FDMN count of {fdmn} exceeds the {new} new cases")
    return {"period": (wad_year - 1, wad_year), "new": new, "cumulative": cumulative,
            "fdmn": fdmn}


def check_chain(series: Dict[int, Dict]) -> None:
    """Raises ValueError unless the years run without a gap and every cumulative count equals
    the cumulative count of the year before plus the new cases of the year."""
    years = sorted(series)
    if years != list(range(years[0], years[-1] + 1)):
        raise ValueError(f"the World AIDS Day years do not run without a gap: {years}")
    for year in years[1:]:
        expected = series[year - 1]["cumulative"] + series[year]["new"]
        if series[year]["cumulative"] != expected:
            raise ValueError(f"{year}, the cumulative count of {series[year]['cumulative']} "
                             f"differs from {series[year - 1]['cumulative']} + "
                             f"{series[year]['new']}")


class BangladeshASPConnector(BaseConnector):
    """World AIDS Day files of the Bangladesh AIDS/STD Programme, notified HIV cases."""

    source_id = "bd_asp"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("AIDS/STD Programme of Bangladesh, World AIDS Day files 2016 to 2025, people "
                   "newly reported HIV positive in the reporting year from November to October, "
                   "national, 2016 to 2025 (to-source).")
    country = "BGD"
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/bd_asp", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, wad_year: int) -> Path:
        """Local copy of the World AIDS Day file of `wad_year`, downloading only if not cached."""
        _, name, size, prefix = _FILES[wad_year]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / f"bd_asp_wad_{wad_year}.pdf"
        if path.exists():
            log.info("bd_asp: using cached %s", path)
        else:
            blob = self._request("GET", _BASE + name).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_BASE + name} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("bd_asp: downloaded the %d file (%d bytes) -> %s", wad_year, len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (size, prefix):
            log.info("bd_asp: the %d file matches the copy read on 21 October 2026 (sha256 %s)",
                     wad_year, digest[:12])
        else:
            log.warning("bd_asp: the %d file differs from the copy read on 21 October 2026 (%d "
                        "bytes, sha256 %s, expected %d bytes, %s), and the gates still run",
                        wad_year, len(blob), digest[:12], size, prefix)
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
        try:
            import pdfplumber
        except ImportError:
            log.error("bd_asp: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            paths = {year: self._pdf_path(year) for year in _FILES}
        except Exception as exc:
            log.warning("bd_asp: a World AIDS Day file could not be fetched (%s)", exc)
            return
        try:
            series: Dict[int, Dict] = {}
            for year, path in paths.items():
                with pdfplumber.open(str(path)) as pdf:
                    text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                series[year] = parse_file(text, year)
            check_chain(series)
        except Exception as exc:
            log.warning("bd_asp: the World AIDS Day files failed a gate (%s), no row emitted", exc)
            return
        emitted = 0
        for year, row in sorted(series.items()):
            if not start_year <= year <= end_year:
                continue
            page_id, name, _, _ = _FILES[year]
            extra = {
                "definition": _DEFINITION,
                "reporting_period": f"1 November {year - 1} to 31 October {year}",
                "edition": f"World AIDS Day {year} file of the AIDS/STD Programme, ASP page {page_id}",
                "cumulative_since_1989": row["cumulative"],
                "chain_check": ("the cumulative count of every year from 2016 to 2025 equals the "
                                "cumulative count of the year before plus the new cases"),
                "reconcile_with": _RECONCILE,
                "not_carried": _NOT_CARRIED,
            }
            if row["fdmn"] is not None:
                extra["fdmn_cases"] = row["fdmn"]
            emitted += 1
            yield self.make_row(
                country_iso3="BGD", country_name="Bangladesh", admin1="",
                indicator_id="notified_hiv_cases", year=year, value=float(row["new"]),
                unit="count", population_group=POP_ALL, sex=SEX_ALL, age_group=AGE_ALL,
                source_url=_BASE + name,
                source_indicator_code=f"asp_bd:wad{year}:hiv_positive_new",
                extra=extra,
            )
        log.info("bd_asp: World AIDS Day files 2016 to 2025, emitted %d rows", emitted)
