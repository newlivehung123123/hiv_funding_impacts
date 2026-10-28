"""
Maldives, notified HIV cases from the Maldives Health Statistics of the Ministry of Health
(https://health.gov.mv/en/publications), connector 63.

Source. The Ministry of Health publishes the Maldives Health Statistics as born-digital PDF
files on the publications pages of the ministry site. The 2014 edition (the eighth in the
series) and the 2015-16 edition (the ninth) print a table of the HIV positive cases detected
by nationality, from the SEARO Integrated Data Analysis System (SIDAS) of the Health
Protection Agency (HPA), with the programme records of the National AIDS Programme of the
HPA. The two files were read on 21 October 2026 (research/phase6_sas/sas_round1_notes.md,
Maldives). No sign-in and no key. The connector downloads every file once into `raw_dir`,
every later run reads the cached copies, and the connector reads the pdfplumber text layer
with no optical character recognition.

Tables read. Table 2.11 of the 2014 edition covers 2005 to 2014, and Table 3-57 of the
2015-16 edition covers 2007 to 2016, every table with a line for Maldivians, a line for
expatriates and a line for the total. The 2014 edition says the publication represents data
from January to December 2014, and the counts of 2007 to 2014 agree in the two editions, so
every row counts a calendar year.

Gates. The series enters only when every check below passes, because two published figures
disagreeing leave the true figure unknown.
  Every edition prints the table heading once outside the contents, with the year range of
  the heading equal to the years of the table, 10 consecutive years.
  Every year of every table has a Maldivian count plus an expatriate count equal to the total.
  The 2014 edition states the period from January to December 2014.
  The Maldivian count, the expatriate count and the total of every year from 2007 to 2014
  agree in the two editions.
  The 2014 quick facts give two Maldivian and seven expatriate cases, equal to Table 2.11 for
  2014.
  Table 3-11 of the 2015-16 edition gives the same total, Maldivian count and expatriate count
  for 2015 and 2016 as Table 3-57.

Narrative text. The narrative pages of the two editions differ from the tables in places, and
the tables are the authority (ruling R43 of research/rulings_2026-10-15.md). The 2014 and the
2015-16 narratives say the highest Maldivian count (three) came in 2013, where Table 2.11 and
Table 3-57 give three in 2012 and one in 2013. The 2015-16 narrative says two Maldivian cases
came in 2016, where Tables 3-11 and 3-57 give two in 2015 and zero in 2016, and gives an
expatriate range of seven (in 2015) to 16 (in 2007), where Table 3-57 gives seven in 2014 and
25 in 2007. The 2015-16 narrative repeats the 2014 narrative with the years changed, and
extra.narrative_differs records the differences on every row.

What the connector emits. National notified_hiv_cases, age group and sex "all", for 2005 to
2016, as the HIV positive cases detected in the Maldives in the calendar year, expatriates
included. The Maldivian and the expatriate counts travel in extra. Every year from 2007
comes from the 2015-16 edition, and 2005 and 2006 come from the 2014 edition.

Not carried.
  The individuals screened for HIV, a count of people screened, which differs from the tests
  counted under hiv_tests_performed.
  The 2017-18 edition, a scanned file with no text layer.
  The 2020 edition, whose single count of six counts screening test results notified for
  confirmatory testing, a different definition.
  The 2021 edition, whose link on the ministry page answered an error page on 21 October 2026.

Source type. routine_programme_record, the national HIV case reports of the HPA.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_SITE = "https://health.gov.mv"
# edition: (publication page, file path, size and sha256 prefix of the copy read on
# 21 October 2026)
_FILES = {
    "2014": ("/en/publications/the-maldives-health-statistics-2014-1",
             "/storage/uploads/xRwX7DoW/cnba141l.pdf", 13_580_004, "41016dd8702b"),
    "2015-16": ("/en/publications/the-maldives-health-statistics-2015-2016",
                "/storage/uploads/Arovzboj/fbwwmryf.pdf", 7_440_377, "23562712de91"),
}
# edition: (table name, heading pattern, first year, last year)
_TABLES = {
    "2014": ("Table 2.11", re.compile(
        r"^Table 2\.11\. Total Number of HIV Positive Cases Detected by Nationality - "
        r"Maldives- (\d{4})- (\d{4})f?$"), 2005, 2014),
    "2015-16": ("Table 3-57", re.compile(
        r"^Table 3-57: Total Number of HIV Positive Cases Detected by Nationality , "
        r"Maldives, (\d{4}) - (\d{4})$"), 2007, 2016),
}
_PERIOD_2014 = "represents data from January to December 2014"
_QUICK_2014 = re.compile(r"Total Number of New HIV positive cases (\d+) \(([\d.]+)%\)")
_T311_HEAD = "Table 3-11: HIV cases in Maldives, 2015-2016"
_T311_LINE = re.compile(r"positive cases detected (\d+) (\d+)$")

_DEFINITION = ("HIV positive cases detected in the Maldives in the calendar year, Maldivians "
               "and expatriates, from SIDAS of the Health Protection Agency, the row \"Total\" "
               "of the table of HIV positive cases detected by nationality in the Maldives "
               "Health Statistics")
_RECONCILE = ("No other source in the panel held Maldivian notified_hiv_cases or "
              "new_diagnoses rows when the connector was built (checked 21 October 2026). "
              "Never compare with new_diagnoses (Jason's ruling of 8 October 2026)")
_NARRATIVE = ("The narrative pages differ from the tables, and the tables are the authority. "
              "The 2014 and the 2015-16 narratives say the highest Maldivian count (three) came "
              "in 2013, where Table 2.11 and Table 3-57 give three in 2012. The 2015-16 "
              "narrative says two Maldivian cases came in 2016, where Tables 3-11 and 3-57 give "
              "two in 2015 and zero in 2016")
_NOT_CARRIED = ("the individuals screened for HIV, the scanned 2017-18 edition, the 2020 "
                "screening test count, and the 2021 edition, whose link answered an error page")


def _lines(text: str) -> List[str]:
    return [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]


def _ints(line: str, label: str, n: int) -> List[int]:
    """The `n` integers after `label` at the start of `line`. Raises ValueError otherwise."""
    if not line.startswith(label + " "):
        raise ValueError(f"expected a line starting {label!r}, got {line[:60]!r}")
    tokens = line[len(label):].split()
    if len(tokens) != n or not all(t.isdigit() for t in tokens):
        raise ValueError(f"the {label} line {line!r} does not hold {n} counts")
    return [int(t) for t in tokens]


def parse_table(text: str, edition: str) -> Dict[int, Tuple[int, int, int]]:
    """The table of HIV positive cases detected by nationality in one edition, as
    {year: (maldivians, expatriates, total)}, after the gates of the module docstring which
    concern a single table. Raises ValueError when any gate fails."""
    name, heading, first, last = _TABLES[edition]
    lines = _lines(text)
    heads = [i for i, ln in enumerate(lines) if heading.match(ln)]
    if len(heads) != 1:
        raise ValueError(f"the {edition} edition prints the {name} heading {len(heads)} times "
                         f"outside the contents, expected once")
    i = heads[0]
    span = tuple(int(y) for y in heading.match(lines[i]).groups())
    years = _ints(lines[i + 1], "Year/", 10)
    if span != (first, last) or years != list(range(first, last + 1)):
        raise ValueError(f"{name} of the {edition} edition covers {span} and prints the years "
                         f"{years}, expected {first} to {last}")
    local = _ints(lines[i + 2], "Maldivians", 10)
    expat = _ints(lines[i + 3], "Expatriates", 10)
    total = _ints(lines[i + 4], "Total", 10)
    out = {}
    for year, a, b, t in zip(years, local, expat, total):
        if a + b != t:
            raise ValueError(f"{name} of the {edition} edition, {year}, {a} Maldivians plus {b} "
                             f"expatriates differ from the total of {t}")
        out[year] = (a, b, t)
    return out


def check_2014(text: str, table: Dict[int, Tuple[int, int, int]]) -> None:
    """Raises ValueError unless the 2014 edition states the calendar year 2014 and the quick
    facts give the Maldivian and expatriate counts of Table 2.11 for 2014."""
    if _PERIOD_2014 not in " ".join(_lines(text)):
        raise ValueError("the 2014 edition does not state the period January to December 2014")
    quick = [int(n) for n, _ in _QUICK_2014.findall(" ".join(_lines(text)))]
    if quick != [table[2014][0], table[2014][1]]:
        raise ValueError(f"the 2014 quick facts give {quick}, Table 2.11 gives "
                         f"{list(table[2014][:2])} for 2014")


def check_2015_16(text: str, table: Dict[int, Tuple[int, int, int]]) -> None:
    """Raises ValueError unless Table 3-11 of the 2015-16 edition gives the total, the
    Maldivian and the expatriate counts of Table 3-57 for 2015 and 2016."""
    lines = _lines(text)
    heads = [i for i, ln in enumerate(lines) if ln.endswith(_T311_HEAD)]
    if len(heads) != 1:
        raise ValueError(f"the 2015-16 edition prints the Table 3-11 heading {len(heads)} times")
    found = [_T311_LINE.search(ln) for ln in lines[heads[0]:heads[0] + 20]]
    counts = [(int(m.group(1)), int(m.group(2))) for m in found if m]
    expected = [(table[2015][k], table[2016][k]) for k in (2, 0, 1)]
    if counts != expected:
        raise ValueError(f"Table 3-11 gives {counts}, Table 3-57 gives {expected} for the total, "
                         f"the Maldivians and the expatriates of 2015 and 2016")


def check_overlap(old: Dict[int, Tuple[int, int, int]], new: Dict[int, Tuple[int, int, int]]) -> None:
    """Raises ValueError unless the two editions agree on every year printed in both."""
    shared = sorted(set(old) & set(new))
    if shared != list(range(2007, 2015)):
        raise ValueError(f"the two editions share the years {shared}, expected 2007 to 2014")
    for year in shared:
        if old[year] != new[year]:
            raise ValueError(f"{year}, the 2014 edition gives {old[year]} and the 2015-16 "
                             f"edition gives {new[year]}")


class MaldivesMoHConnector(BaseConnector):
    """Maldives Health Statistics of the Ministry of Health, notified HIV cases."""

    source_id = "mv_moh"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Ministry of Health of the Maldives, Maldives Health Statistics 2014 and "
                   "2015-16, HIV positive cases detected, Maldivians and expatriates, national, "
                   "2005 to 2016 (to-source).")
    country = "MDV"
    timeout = 180

    def __init__(self, raw_dir: str = "data/raw/mv_moh", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, edition: str) -> Path:
        """Local copy of the `edition` file, downloading only if not cached."""
        _, file_path, size, prefix = _FILES[edition]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / f"mv_moh_mhs_{edition.replace('-', '_')}.pdf"
        if path.exists():
            log.info("mv_moh: using cached %s", path)
        else:
            blob = self._request("GET", _SITE + file_path).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_SITE + file_path} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("mv_moh: downloaded the %s edition (%d bytes) -> %s", edition, len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (size, prefix):
            log.info("mv_moh: the %s edition matches the copy read on 21 October 2026 (sha256 %s)",
                     edition, digest[:12])
        else:
            log.warning("mv_moh: the %s edition differs from the copy read on 21 October 2026 (%d "
                        "bytes, sha256 %s, expected %d bytes, %s), and the gates still run",
                        edition, len(blob), digest[:12], size, prefix)
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
            log.error("mv_moh: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            paths = {edition: self._pdf_path(edition) for edition in _FILES}
        except Exception as exc:
            log.warning("mv_moh: an edition could not be fetched (%s)", exc)
            return
        try:
            texts = {}
            for edition, path in paths.items():
                with pdfplumber.open(str(path)) as pdf:
                    texts[edition] = "\n".join(p.extract_text() or "" for p in pdf.pages)
            tables = {edition: parse_table(texts[edition], edition) for edition in _FILES}
            check_2014(texts["2014"], tables["2014"])
            check_2015_16(texts["2015-16"], tables["2015-16"])
            check_overlap(tables["2014"], tables["2015-16"])
        except Exception as exc:
            log.warning("mv_moh: the editions failed a gate (%s), no row emitted", exc)
            return
        series = {year: ("2014", row) for year, row in tables["2014"].items()}
        series.update({year: ("2015-16", row) for year, row in tables["2015-16"].items()})
        emitted = 0
        for year, (edition, (local, expat, total)) in sorted(series.items()):
            if not start_year <= year <= end_year:
                continue
            page, file_path, _, _ = _FILES[edition]
            name = _TABLES[edition][0]
            extra = {
                "definition": _DEFINITION,
                "edition": (f"Maldives Health Statistics {edition}, {name}, publication page "
                            f"{_SITE + page}"),
                "maldivians": local,
                "expatriates": expat,
                "narrative_differs": _NARRATIVE,
                "reconcile_with": _RECONCILE,
                "not_carried": _NOT_CARRIED,
            }
            if 2007 <= year <= 2014:
                extra["cross_check"] = ("Table 2.11 of the 2014 edition gives the same Maldivian "
                                        "count, expatriate count and total")
            emitted += 1
            yield self.make_row(
                country_iso3="MDV", country_name="Maldives", admin1="",
                indicator_id="notified_hiv_cases", year=year, value=float(total),
                unit="count", population_group=POP_ALL, sex=SEX_ALL, age_group=AGE_ALL,
                source_url=_SITE + file_path,
                source_indicator_code=(f"moh_mv:mhs{edition.replace('-', '_')}:"
                                       f"{re.sub(r'[ .-]', '_', name).lower()}:total"),
                extra=extra,
            )
        log.info("mv_moh: Maldives Health Statistics 2014 and 2015-16, emitted %d rows", emitted)
