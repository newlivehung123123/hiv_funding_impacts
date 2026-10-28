"""
Montenegro, notified HIV cases from the annual HIV report of the Institute of Public Health of
Montenegro (Institut za javno zdravlje Crne Gore, www.ijzcg.me), connector 61.

Source. The institute publishes "HIV/AIDS - Godišnji izvještaj o HIV/AIDS-u u Crnoj Gori za 2025.
godinu" (the annual report on HIV and AIDS in Montenegro for 2025, Podgorica, May 2026) at
https://api.ijzcg.me/media/files/1784726176-godisnji-hiv-za-2025.pdf, 1,098,408 bytes,
born-digital, read on 20 October 2026. The public report list of the institute
(https://api.ijzcg.me/v1/reports, report 18, "Godišnji izvještaji o kretanju HIV/AIDS-a u Crnoj
Gori") links the 2025, 2024 and 2023 editions. No sign-in and no key. The connector downloads the
2025 edition once into `raw_dir`, every later run reads the cached copy, and the connector reads
the pdfplumber text layer with no optical character recognition.

Table read. Tabela 5, "Prijavljivanje HIV infekcije, AIDS-a i smrti od AIDS-a u periodu od
2001-2025. godine" (HIV infections, AIDS and AIDS deaths reported, 2001 to 2025). Every year row
holds five counts, the total registered with HIV ("Ukupan broj registrovanih HIV/AIDS
slučajeva"), people newly diagnosed at the HIV stage, people newly diagnosed at the AIDS stage,
people first registered in Montenegro in the year after an HIV diagnosis made in the country of
origin, and deaths from AIDS. The row "UKUPNO" holds the sums for 2001 to 2025. Tabela 1 splits
the people registered in 2025 by sex, and Tabela 2 splits the people newly diagnosed in 2025 by
municipality.

Gates. The report enters only when every check below passes, because two published figures
disagreeing leave the true figure unknown.
  The year rows run without a gap and end in the year of the report title.
  In every year row the total registered equals the newly diagnosed at the HIV stage plus the
  newly diagnosed at the AIDS stage plus the people diagnosed abroad, a dash read as zero.
  The year rows add to the row "UKUPNO" in every column.
  Men plus women in Tabela 1 equal the row of the report year in Tabela 5 in every column.
  The municipalities of Tabela 2 add to the printed total, and the printed total equals the newly
  diagnosed of the report year at the HIV stage plus the AIDS stage.

What the connector emits. National notified_hiv_cases, age group and sex "all", for 2001 to
2025, as the total registered with HIV in the year, which includes the people diagnosed abroad
and first registered in Montenegro in the year. The newly diagnosed counts and the count of
people diagnosed abroad travel in extra. For the year of the report (2025) the connector also
emits men and women from Tabela 1.

Check against other sources (read on 20 October 2026). The total registered equals measure
HFA_350 of the WHO Europe Health for All database (who_europe_hfa) in every year from 2001 to
2019 and Table 1 of the joint ECDC and WHO Europe report HIV/AIDS surveillance in Europe 2025
(ecdc_hiv_report) in every year from 2015 to 2024, the years 2022 to 2024 with the people
diagnosed abroad included. Tabela 5 of the 2024 edition
(https://api.ijzcg.me/media/files/1748853812-godisnji-izvjestaj-o-hiv-aids-u-u-crnoj-gori-za-2024-godinu.pdf)
prints the same five counts for every year from 2001 to 2024.

Not carried.
  The deaths from AIDS, a count of deaths caused by AIDS, which differs from the deaths from any
  cause among people reported with AIDS under aids_deaths_reported.
  The newly diagnosed at the AIDS stage, which counts people diagnosed late and differs from the
  people newly reported with AIDS under aids_cases_reported.
  The municipality counts of Tabela 2 and Tabela 6, which cover the newly diagnosed only and so
  differ in population from the national count.
  The age groups of Tabela 1, which no panel id holds for notified cases at five-year ages.
  The testing counts of Tabela 3 and Tabela 4, persons tested outside private laboratories and
  blood donors, which differ from the tests counted under hiv_tests_performed.
  The count on antiretroviral therapy at the end of 2025 (330 people), which who_gho already
  carries for 2025 as 331.

Source type. routine_programme_record, the national HIV register of the institute.
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

_URL = "https://api.ijzcg.me/media/files/1784726176-godisnji-hiv-za-2025.pdf"
_LOCAL = "me_ijzcg_hiv_annual_2025.pdf"
_KNOWN = (1_098_408, "a07b778e406a")     # size and sha256 prefix of the copy read on 20 October 2026

_TITLE = re.compile(r"ZA\s+(\d{4})\s*\.\s*GODINU")
_COUNT = r"(\d+|-)"
_YEAR_ROW = re.compile(r"^(\d{4})" + (r"\s+" + _COUNT) * 5 + r"$")
_SUM_ROW = re.compile(r"^UKUPNO" + (r"\s+" + _COUNT) * 5 + r"$")
_MEN = re.compile(r"^Pol\s+muški" + (r"\s+" + _COUNT) * 4 + r"$")
_WOMEN = re.compile(r"^ženski" + (r"\s+" + _COUNT) * 4 + r"$")
_PLACE_ROW = re.compile(r"^(\D+?)\s+(\d+)\s+\d+,\d%$")
_PLACE_SUM = re.compile(r"^UKUPNO\s+(\d+)\s+100%$")

_COLUMNS = ("total_registered", "new_hiv_stage", "new_aids_stage", "diagnosed_abroad",
            "aids_deaths")

_DEFINITION = ("people registered with HIV in Montenegro in the year, the newly diagnosed plus "
               "the people first registered after an HIV diagnosis made in the country of "
               "origin, the column \"Ukupan broj registrovanih HIV/AIDS slučajeva\" of Tabela 5 "
               "of the annual HIV report of the Institute of Public Health of Montenegro")
_RECONCILE = ("who_europe_hfa HFA_350, equal in every year from 2001 to 2019, and "
              "ecdc_hiv_report Table 1, equal in every year from 2015 to 2024. Never compare "
              "with new_diagnoses (Jason's ruling of 8 October 2026)")
_NOT_CARRIED = ("the deaths from AIDS (cause of death, not aids_deaths_reported), the newly "
                "diagnosed at the AIDS stage (not aids_cases_reported), the municipality "
                "counts (newly diagnosed only), the five-year age groups, the testing counts of "
                "Tabela 3 and Tabela 4, and the count on treatment (already in who_gho)")


def _n(token: str) -> int:
    return 0 if token == "-" else int(token)


def _lines(text: str) -> List[str]:
    return [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]


def parse_report(text: str) -> Dict:
    """Tabela 5, Tabela 1 and Tabela 2 as {report_year, rows, sum_row, men, women, places}, after
    the gates of the module docstring. Raises ValueError when any gate fails."""
    title = _TITLE.search(text)
    if not title:
        raise ValueError("the report title with the report year was not found")
    report_year = int(title.group(1))
    lines = _lines(text)
    start = [i for i, ln in enumerate(lines) if ln.startswith("Tabela 5.")]
    if len(start) != 1:
        raise ValueError(f"{len(start)} lines start with 'Tabela 5.', expected one")
    rows: Dict[int, List[int]] = {}
    sum_row: Optional[List[int]] = None
    for ln in lines[start[0]:]:
        m = _YEAR_ROW.match(ln)
        if m:
            year = int(m.group(1))
            if year in rows:
                raise ValueError(f"Tabela 5 prints {year} twice")
            rows[year] = [_n(t) for t in m.groups()[1:]]
            continue
        m = _SUM_ROW.match(ln)
        if m:
            sum_row = [_n(t) for t in m.groups()]
            break
    if not rows or sum_row is None:
        raise ValueError("Tabela 5 holds no year rows or no row 'UKUPNO'")
    years = sorted(rows)
    if years != list(range(years[0], report_year + 1)):
        raise ValueError(f"the years of Tabela 5 do not run without a gap to {report_year}: "
                         f"{years}")
    for year, counts in rows.items():
        if counts[0] != counts[1] + counts[2] + counts[3]:
            raise ValueError(f"{year}, the total registered of {counts[0]} differs from "
                             f"{counts[1]} + {counts[2]} + {counts[3]}")
    for i, column in enumerate(_COLUMNS):
        added = sum(c[i] for c in rows.values())
        if added != sum_row[i]:
            raise ValueError(f"the column {column!r} adds to {added} against the row "
                             f"'UKUPNO' of {sum_row[i]}")
    men = [m for m in (_MEN.match(ln) for ln in lines) if m]
    women = [m for m in (_WOMEN.match(ln) for ln in lines) if m]
    if len(men) != 1 or len(women) != 1:
        raise ValueError(f"Tabela 1 holds {len(men)} rows for men and {len(women)} rows for "
                         f"women, expected one row for each sex")
    men_n = [_n(t) for t in men[0].groups()]
    women_n = [_n(t) for t in women[0].groups()]
    # Tabela 1 holds the HIV stage, the AIDS stage, the people diagnosed abroad and the deaths
    own = rows[report_year][1:]
    if [a + b for a, b in zip(men_n, women_n)] != own:
        raise ValueError(f"men {men_n} plus women {women_n} in Tabela 1 differ from the row "
                         f"{report_year} of Tabela 5 ({own})")
    t2 = [i for i, ln in enumerate(lines) if ln.startswith("Tabela 2.")]
    if len(t2) != 1:
        raise ValueError(f"{len(t2)} lines start with 'Tabela 2.', expected one")
    places: Dict[str, int] = {}
    place_sum: Optional[int] = None
    for ln in lines[t2[0]:]:
        m = _PLACE_SUM.match(ln)
        if m:
            place_sum = int(m.group(1))
            break
        m = _PLACE_ROW.match(ln)
        if m:
            places[m.group(1)] = int(m.group(2))
    if place_sum is None or sum(places.values()) != place_sum:
        raise ValueError(f"the municipalities of Tabela 2 add to {sum(places.values())} against "
                         f"the printed total of {place_sum}")
    if place_sum != rows[report_year][1] + rows[report_year][2]:
        raise ValueError(f"the total of Tabela 2 ({place_sum}) differs from the newly diagnosed "
                         f"of {report_year} in Tabela 5")
    return {
        "report_title": title.group(0),
        "report_year": report_year,
        "rows": rows,
        "sum_row": sum_row,
        "men": men_n,
        "women": women_n,
        "places": places,
    }


class MontenegroIjzcgConnector(BaseConnector):
    """Annual HIV report of the Institute of Public Health of Montenegro, notified HIV cases."""

    source_id = "me_ijzcg"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Institute of Public Health of Montenegro, annual HIV report for 2025, people "
                   "registered with HIV in the year, national, 2001 to 2025, with men and women "
                   "for 2025 (to-source).")
    country = "MNE"
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/me_ijzcg", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the report, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("me_ijzcg: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("me_ijzcg: downloaded the report (%d bytes) -> %s", len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("me_ijzcg: the report matches the copy read on 20 October 2026 "
                     "(sha256 %s)", digest[:12])
        else:
            log.warning("me_ijzcg: the report differs from the copy read on 20 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s), and the gates still run",
                        len(blob), digest[:12], *_KNOWN)
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
            log.error("me_ijzcg: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
        except Exception as exc:
            log.warning("me_ijzcg: the report could not be fetched (%s)", exc)
            return
        try:
            with pdfplumber.open(str(path)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            report = parse_report(text)
        except Exception as exc:
            log.warning("me_ijzcg: the report failed a gate (%s), no row emitted", exc)
            return
        base = {
            "report_title": report["report_title"],
            "definition": _DEFINITION,
            "table_check": ("every year row of Tabela 5 adds to the total registered, and the "
                            "year rows add to the row 'UKUPNO' in every column"),
            "reconcile_with": _RECONCILE,
            "not_carried": _NOT_CARRIED,
        }
        emitted = 0
        for year, counts in sorted(report["rows"].items()):
            if not start_year <= year <= end_year:
                continue
            emitted += 1
            yield self.make_row(
                country_iso3="MNE", country_name="Montenegro", admin1="",
                indicator_id="notified_hiv_cases", year=year, value=float(counts[0]),
                unit="count", population_group=POP_ALL, sex=SEX_ALL, age_group=AGE_ALL,
                source_url=_URL,
                source_indicator_code="ijzcg_me:tabela5:total_registered",
                extra=dict(base, new_hiv_stage=counts[1], new_aids_stage=counts[2],
                           diagnosed_abroad=counts[3]),
            )
        year = report["report_year"]
        if start_year <= year <= end_year:
            for sex, counts in (("male", report["men"]), ("female", report["women"])):
                emitted += 1
                yield self.make_row(
                    country_iso3="MNE", country_name="Montenegro", admin1="",
                    indicator_id="notified_hiv_cases", year=year,
                    value=float(counts[0] + counts[1] + counts[2]),
                    unit="count", population_group=POP_ALL, sex=sex, age_group=AGE_ALL,
                    source_url=_URL,
                    source_indicator_code="ijzcg_me:tabela1:hiv+aids+abroad",
                    extra=dict(base, new_hiv_stage=counts[0], new_aids_stage=counts[1],
                               diagnosed_abroad=counts[2],
                               sex_check=("men plus women in Tabela 1 equal the row of the "
                                          "report year in Tabela 5 in every column")),
                )
        log.info("me_ijzcg: report for %d, emitted %d rows", year, emitted)
