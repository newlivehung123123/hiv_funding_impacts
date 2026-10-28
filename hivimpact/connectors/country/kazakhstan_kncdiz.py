"""
Kazakhstan, HIV prevalence among people who inject drugs from the survey reports of the Kazakh
Scientific Centre of Dermatology and Infectious Diseases of the Ministry of Health of Kazakhstan
(Казахский научный центр дерматологии и инфекционных заболеваний, KNCDIZ, kncdiz.kz), connector 66.

Source. KNCDIZ publishes two survey reports among people who inject drugs. "Отчет по результатам
эпидемиологического слежения за распространенностью ВИЧ-инфекции среди людей, употребляющих
инъекционные наркотики РК, 2022 год" (report on the sentinel surveillance of HIV prevalence
among people who inject drugs, Kazakhstan, 2022, Almaty 2023) is at
https://kncdiz.kz/files/00019909.pdf, 1,690,128 bytes. "Отчет по результатам биоповеденческого
исследования среди людей, употребляющих инъекционные наркотики РК, 2024 год" (report on the
bio-behavioural survey among people who inject drugs, Kazakhstan, 2024, Almaty 2025) is at
https://kncdiz.kz/files/00019805.pdf, 1,872,847 bytes. The two files were read on 21 October
2026. No sign-in and no key. The connector downloads the two files once into `raw_dir`, every
later run reads the cached copies, and the connector reads the pdfplumber text layer with no
optical character recognition.

Survey design, as the two reports print the design. A cross-sectional survey at sentinel sites (23
sites in 2022, 24 in 2024) with respondent-driven sampling (RDS), at most three recruits per
participant, people aged 18 and over who injected drugs in the last 12 months, linked anonymous
testing for HIV, hepatitis C and syphilis, and ethics approval IRB-A042 of 12 December 2013. The
2022 sample holds 4,554 respondents and the 2024 sample 3,944. The reports weight the answers in
RDS-Analyst and print the weighted figure as the HIV prevalence of the population of people who
inject drugs in Kazakhstan, beside the share of the sample. The 2024 report names a new survey
method ("при внедрении новой методики") when the report explains the fall in hepatitis C
prevalence, and the report keeps the design, the eligibility rule and the weighting of 2022.

Table read. Table 6 of every report (Таблица 6, a comparison of the HIV, hepatitis C and syphilis
prevalence of the survey round and the round before) prints for every round the sample share
with the 95 per cent interval and, on a row headed "взвешенные" (weighted), the weighted
prevalence. Only the HIV column enters.

Gates. The two reports enter only when every check below passes in the two reports, because
two published figures disagreeing leave the true figure unknown.
  The title page names people who inject drugs and the survey year, and Table 6 compares the
  survey year with the round two years earlier.
  Table 6 prints exactly two rounds, every sample share lies inside the printed interval, and
  every weighted figure is printed with a per cent sign.
  The text after Figure 22 prints the weighted prevalence of Kazakhstan for the survey year and,
  in brackets, for the round before, equal to Table 6 ("Взвешенный показатель
  распространенности по РК составил 7,2% (2020г.-8,3%)" in the 2022 report).
  The conclusions print the weighted prevalence of the survey year, equal to Table 6.
  The HIV-positive and HIV-negative respondents printed beside the hepatitis C results add to the
  sample size the methods print, and the positives over the sample round to the sample share of
  Table 6 (348 of 4,554 in 2022 and 283 of 3,944 in 2024).
  The two reports print the same 2022 round in Table 6 (sample share 7.6, interval 6.9 to 8.4,
  weighted 7.2).

What the connector emits. National kp_hiv_prevalence, population_group pwid, sex "all", age
group "18+" (the eligibility rule of the survey), the weighted prevalence for 2020 (8.3 per cent,
from the 2022 report), 2022 (7.2 per cent) and 2024 (6.4 per cent), stamped with the survey year
(as ruling R24 stamps unodc_pwid). value_lower and value_upper stay blank, because the reports
print no interval for the weighted figure. The sample share and the 95 per cent interval of the
sample share travel in extra, with the sample size and the HIV-positive respondents for 2022 and
2024 (ruling R47).

Check against other sources (read on 21 October 2026). unaids_aidsinfo carries 7.2 per cent for
Kazakhstan, stamped 2024 (the compile year), with age group "all". The 7.2 equals the 2022
weighted prevalence, the 2024 sample share and the figure the introduction of the 2024 report
prints for 2024, so the UNAIDS row cannot be tied to one survey round, and the different age
group keeps the UNAIDS row and the kz_kncdiz rows apart in reconcile. unodc_pwid holds no Kazakh
row.

Not carried.
  The sample shares as values, which describe the sample and not the population (in extra).
  The 2020 sample size, printed as 4,661 in Figure 20 and as 4,761 in other charts of the 2024
  report.
  The sample shares of Figure 20 for 2010 to 2018, printed without a weighted figure.
  The hepatitis C and syphilis prevalence, for which the panel holds no indicator, and which the
  2022 conclusions print as 69.2 and 8 per cent against 66.1 and 8.3 per cent in Table 6.
  The site figures (admin1, read from charts), the behaviour and coverage indicators, and the
  country reports, activity reports and Optima analyses of KNCDIZ (ruling R46).

Source type. survey, an RDS bio-behavioural survey.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_PWID, SEX_ALL

log = logging.getLogger("hivimpact")

_SITE = "https://kncdiz.kz/files/"
# survey year -> (file on the site, local name, size, sha256 prefix of the copy read on 21 October 2026)
_FILES = {
    2022: ("00019909.pdf", "kz_kncdiz_pwid_2022.pdf", 1_690_128, "b26c252bae2a"),
    2024: ("00019805.pdf", "kz_kncdiz_pwid_2024.pdf", 1_872_847, "f8a91b5fa582"),
}

_NUM = r"(\d+,\d+)"
_P_TITLE = re.compile(r"Отчет по результатам .{0,120}?среди людей, употребляющих инъекционные "
                      r"наркотики РК, (\d{4}) год")
_P_TABLE = re.compile(r"Таблица 6\. Сравнительная таблица серологических показателей \(ВИЧ, ВГС, "
                      r"сифилис\) за (\d{4})/(\d{4}) ?гг\.(.*?)Таблица 7\.")
_P_ROW = re.compile(r"(\d{4}) год " + _NUM + " " + _NUM + "-" + _NUM + r"[\d,.\- ]*?взвешенные "
                    + _NUM + "%")
_P_TEXT = re.compile(r"Взвешенный показатель распространенности по РК составил " + _NUM +
                     r"% \((\d{4}) ?г\.? ?- ?" + _NUM + r"%\)")
_P_CONCLUSION = re.compile(r"Взвешенный показатель распространенности ВИЧ-инфекции ?[–-] ?" +
                           _NUM + " ?%")
_P_POSITIVE = re.compile(r"В (\d{4}) году ВГС выявлен\w* у [\d.,]+ ?% ВИЧ-позитивных \((\d+) из "
                         r"(\d+)[,)].{0,80}?ВИЧ- ?негативных \((\d+) из (\d+)[,)]")
_P_SAMPLE = re.compile(r"Размер выборки ?[–-] ?(\d+) респондент")

_DEFINITION = ("HIV prevalence among people aged 18 and over who injected drugs in the last 12 "
               "months, weighted in RDS-Analyst, from the respondent-driven sampling survey at "
               "the sentinel sites of Kazakhstan, Table 6 of the KNCDIZ survey report")
_RECONCILE = ("unaids_aidsinfo carries 7.2 per cent stamped 2024 with age group 'all', equal to "
              "the 2022 weighted prevalence and to the 2024 sample share, so the UNAIDS row "
              "cannot be tied to one survey round. unodc_pwid holds no Kazakh row")
_NOT_CARRIED = ("the sample shares as values (in extra), the 2020 sample size (printed as 4,661 "
                "and 4,761), the Figure 20 sample shares for 2010 to 2018, the hepatitis C and "
                "syphilis prevalence, the site figures, the behaviour and coverage indicators, "
                "and the country reports, activity reports and Optima analyses of KNCDIZ "
                "(ruling R46)")

Round = Dict[str, object]


def _flat(pages: List[str]) -> str:
    """The text layer of every page as one line, with every run of white space as one space."""
    return re.sub(r"\s+", " ", " ".join(pages)).strip()


def _pct(token: str) -> float:
    return float(token.replace(",", "."))


def _one(text: str, pattern: re.Pattern, what: str) -> re.Match:
    found = list(pattern.finditer(text))
    if len(found) != 1:
        raise ValueError(f"the report prints {what} {len(found)} times, expected once")
    return found[0]


def parse_report(pages: List[str], expected_year: int) -> Dict[int, Round]:
    """Table 6 of one survey report as {round year: {sample, lower, upper, weighted, ...}}, after
    the gates of the module docstring. Raises ValueError when any gate fails."""
    text = _flat(pages)
    title = _P_TITLE.search(_flat(pages[:1]))
    if not title or int(title.group(1)) != expected_year:
        raise ValueError(f"the title page does not name people who inject drugs in "
                         f"{expected_year} (found {title.group(1) if title else None})")
    year = expected_year
    table = _one(text, _P_TABLE, "the Table 6 caption")
    if (int(table.group(1)), int(table.group(2))) != (year - 2, year):
        raise ValueError(f"Table 6 compares {table.group(1)} with {table.group(2)}, expected "
                         f"{year - 2} with {year}")
    rows = list(_P_ROW.finditer(table.group(3)))
    if [int(m.group(1)) for m in rows] != [year - 2, year]:
        raise ValueError(f"Table 6 prints the rounds {[m.group(1) for m in rows]}, expected "
                         f"{year - 2} and {year}")
    rounds: Dict[int, Round] = {}
    for m in rows:
        sample, lower, upper, weighted = (_pct(m.group(i)) for i in range(2, 6))
        if not lower <= sample <= upper:
            raise ValueError(f"the {m.group(1)} sample share {sample} lies outside the printed "
                             f"interval {lower} to {upper}")
        rounds[int(m.group(1))] = {"sample": sample, "lower": lower, "upper": upper,
                                   "weighted": weighted}

    after = _one(text, _P_TEXT, "the weighted prevalence of Kazakhstan after Figure 22")
    if _pct(after.group(1)) != rounds[year]["weighted"] or int(after.group(2)) != year - 2 or \
            _pct(after.group(3)) != rounds[year - 2]["weighted"]:
        raise ValueError(f"the text after Figure 22 prints {after.group(1)} ({after.group(2)}: "
                         f"{after.group(3)}), against {rounds[year]['weighted']} and "
                         f"{rounds[year - 2]['weighted']} in Table 6")
    conclusion = _one(text, _P_CONCLUSION, "the weighted prevalence in the conclusions")
    if _pct(conclusion.group(1)) != rounds[year]["weighted"]:
        raise ValueError(f"the conclusions print {conclusion.group(1)}, against "
                         f"{rounds[year]['weighted']} in Table 6")

    pos = _one(text, _P_POSITIVE, "the HIV-positive and HIV-negative respondents")
    positive, negative = int(pos.group(3)), int(pos.group(5))
    size = int(_one(text, _P_SAMPLE, "the sample size").group(1))
    if int(pos.group(1)) != year or positive + negative != size:
        raise ValueError(f"{positive} HIV-positive and {negative} HIV-negative respondents in "
                         f"{pos.group(1)} do not add to the sample of {size}")
    if round(100 * positive / size, 1) != rounds[year]["sample"]:
        raise ValueError(f"{positive} of {size} is {100 * positive / size:.2f} per cent, against "
                         f"the sample share {rounds[year]['sample']} of Table 6")
    rounds[year].update(respondents=size, hiv_positive=positive)
    return rounds


def merge_reports(reports: Dict[int, Dict[int, Round]]) -> Dict[int, Tuple[int, Round]]:
    """{round year: (report year, round)}, with every round printed by two reports kept only when
    the two Table 6 entries agree, and taken from the earlier report. Raises ValueError
    otherwise."""
    merged: Dict[int, Tuple[int, Round]] = {}
    for report_year in sorted(reports):
        for year, rnd in reports[report_year].items():
            if year in merged:
                earlier_year, earlier = merged[year]
                if any(earlier[k] != rnd[k] for k in ("sample", "lower", "upper", "weighted")):
                    raise ValueError(f"the {year} round differs between the {earlier_year} and "
                                     f"{report_year} reports")
                continue
            merged[year] = (report_year, rnd)
    return merged


class KazakhstanKNCDIZConnector(BaseConnector):
    """Survey reports of KNCDIZ among people who inject drugs, weighted HIV prevalence."""

    source_id = "kz_kncdiz"
    default_source_type = SourceType.SURVEY
    description = ("Kazakh Scientific Centre of Dermatology and Infectious Diseases, surveys "
                   "among people who inject drugs 2022 and 2024, weighted HIV prevalence, "
                   "national, 2020, 2022 and 2024 (to-source).")
    country = "KAZ"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/kz_kncdiz", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, year: int) -> Path:
        """Local copy of the `year` report, downloading only if not cached."""
        file_name, name, size, prefix = _FILES[year]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / name
        if path.exists():
            log.info("kz_kncdiz: using cached %s", path)
        else:
            blob = self._request("GET", _SITE + file_name).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_SITE + file_name} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("kz_kncdiz: downloaded the %d report (%d bytes) -> %s", year, len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (size, prefix):
            log.info("kz_kncdiz: the %d report matches the copy read on 21 October 2026 (sha256 "
                     "%s)", year, digest[:12])
        else:
            log.warning("kz_kncdiz: the %d report differs from the copy read on 21 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s), and the gates still run",
                        year, len(blob), digest[:12], size, prefix)
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
            log.error("kz_kncdiz: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            paths = {year: self._pdf_path(year) for year in _FILES}
        except Exception as exc:
            log.warning("kz_kncdiz: a report could not be fetched (%s)", exc)
            return
        try:
            reports = {}
            for year, path in paths.items():
                with pdfplumber.open(str(path)) as pdf:
                    reports[year] = parse_report([p.extract_text() or "" for p in pdf.pages], year)
            merged = merge_reports(reports)
        except Exception as exc:
            log.warning("kz_kncdiz: a report failed a gate (%s), no row emitted", exc)
            return
        base = {
            "definition": _DEFINITION,
            "table_check": ("Table 6 equals the text after Figure 22 and the conclusions, the "
                            "HIV-positive respondents over the sample round to the sample share, "
                            "and the 2022 and 2024 reports print the same 2022 round"),
            "reconcile_with": _RECONCILE,
            "not_carried": _NOT_CARRIED,
        }
        emitted = 0
        for year in sorted(merged):
            if not start_year <= year <= end_year:
                continue
            report_year, rnd = merged[year]
            file_name = _FILES[report_year][0]
            extra = dict(base, report=f"KNCDIZ survey report among people who inject drugs, "
                                      f"{report_year}, Table 6",
                         sample_share=rnd["sample"], sample_share_lower=rnd["lower"],
                         sample_share_upper=rnd["upper"])
            for key in ("respondents", "hiv_positive"):
                if key in rnd:
                    extra[key] = rnd[key]
            emitted += 1
            yield self.make_row(
                country_iso3="KAZ", country_name="Kazakhstan", admin1="",
                indicator_id="kp_hiv_prevalence", year=year, value=rnd["weighted"],
                unit="percent", population_group=POP_PWID, sex=SEX_ALL, age_group="18+",
                source_url=_SITE + file_name,
                source_indicator_code=f"kncdiz_kz:{file_name}:table6:weighted_hiv",
                extra=extra,
            )
        log.info("kz_kncdiz: emitted %d rows", emitted)
