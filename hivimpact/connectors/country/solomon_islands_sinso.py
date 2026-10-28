"""
Solomon Islands, HIV testing, comprehensive knowledge and condom use from the printed tables of
the Solomon Islands Demographic and Health Surveys (DHS) of 2006-2007 and 2015, published by the
Solomon Islands National Statistics Office (SINSO), connector 67.

Source. "Solomon Islands Demographic and Health Survey 2015" (SINSO and the Ministry of Health
and Medical Services, final report, 488 pages) is at
https://statistics.gov.sb/download/54/dhs_2015/760/final-report_si-demographic-and-health-survey-2015,
12,301,932 bytes. "Solomon Islands Demographic and Health Survey 2006-2007" (SINSO, the
Secretariat of the Pacific Community and Macro International, May 2009, 350 pages) is at
https://catalog.ihsn.org//catalog/2963/download/44676 (the International Household Survey
Network catalogue, file SLB_2006_DHS_Report_EN.pdf), 1,757,342 bytes. The two files were read on
21 October 2026. No sign-in and no key. The connector downloads the two files once into
`raw_dir`, every later run reads the cached copies, and the connector reads the pdfplumber text
layer with no optical character recognition. The DHS Program API holds no Solomon Islands survey,
so the dhs connector carries no Solomon Islands row.

Why the connector exists. pacific_data_hub carries the Solomon Islands survey rows the Pacific
Community publishes (comprehensive knowledge for women aged 15 to 49, men aged 15 and over and
youth, condom use at last higher-risk sex for 2007, sex before 15), and every published value
equals the printed tables of the two reports. pacific_data_hub carries no HIV testing row and no
row for men aged 15 to 49, the age group of every men's row the dhs connector writes. The
connector writes only the testing rows and the rows for men aged 15 to 49, so no row repeats a
pacific_data_hub key.

Tables read.
  2015 Table 13.9.1 and Table 13.9.2 (Coverage of prior HIV testing, women and men), column
  "Percentage who have been tested for HIV in the past 12 months and received the results of the
  last test", where "Never tested" includes "don't know" and missing answers, as DHS indicators
  HA_CPHT_W_T1R and HA_CPHT_M_T1R count a missing answer as not tested.
  2015 Table 13.3.2 (Comprehensive knowledge about AIDS, men), row "Total 15-49".
  2007 Table 13.3.2 (Comprehensive knowledge about AIDS, men), row "Total 15-49".
  2007 Table 13.7.2 (Multiple sexual partners and higher-risk sexual intercourse, men), column
  "Percentage who reported using a condom at last higher-risk intercourse", where the footnote
  of the table defines higher-risk intercourse as "Sexual intercourse with a partner who neither
  was a spouse nor who lived with the respondent".

Gates. A table enters only when every check below passes, because two printed figures
disagreeing leave the true figure unknown.
  The caption names the table and "Solomon Islands" with the survey year, and the definition
  sentence or footnote of the table names the measure above.
  Testing. Received the result, did not receive the result and never tested add to 100 within
  0.3, ever tested equals 100 less never tested within 0.05, the 12-month share is no larger than
  the share ever tested with the result, and the urban and rural rows weighted by the printed
  numbers give the total within 0.1, with numbers adding to the total within two.
  Men. The "Total 15-49" and "50+" rows weighted by the printed numbers give the "Total 15+" row
  within 0.1, the numbers add to the 15+ number within two, and the 15+ number equals the men
  the report text names with the survey's own age range (3,591 men aged 15-54 in 2015, 2,056 men
  aged 15-54 in 2007). The text names exactly one age range for the 15+ number, and the range
  reaches 50 or over whenever the tables print men aged 50 and over.
  Condom use. The share with higher-risk sex times the men who had sex gives the men with
  higher-risk sex within 1.5, the printed value is no suppressed figure, and the "Total 15-49"
  and "50+" numbers add to the "Total men 15+" number within two in every number column of the
  table (ruling R49, which refuses the Kiribati 2009 table on the same test).

What the connector emits. National rows for SLB, population_group "all", age_group "15-49".
  hiv_tested_12m_result_survey_pct, 2015, women 1.5 and men 0.9.
  hiv_comprehensive_knowledge_survey_pct, men, 2007 38.6 and 2015 41.1.
  condom_last_higher_risk_sex_survey_pct, men, 2007 26.0.
The 2006-2007 survey is stamped 2007, as pacific_data_hub stamps the survey. value_lower and
value_upper stay blank, because the sampling-error appendix of the 2015 report holds no HIV
variable, and the men's sampling-error table of the 2006-2007 report (Table B.5) prints no
knowledge variable and no condom variable for higher-risk sex. extra carries the weighted
denominator, the sample universe and the survey's own age range under the keys the dhs
connector uses, and a value printed in parentheses (25 to 49 unweighted cases) carries
extra.dhs_precision (ruling R48).

Not carried.
  Every value pacific_data_hub carries on the same key (women aged 15 to 49, men aged 15 and
  over, youth aged 15 to 24, and sex before 15), equal to the printed tables.
  The 2007 testing variable, because the 2007 report prints no testing table, and the
  sampling-error tables print the variable as 0 with standard error 0 for every domain, which
  marks an empty variable and not a measured zero.
  The 2015 condom table, which counts men and women with two or more partners and not
  higher-risk sex, a different measure from condom_last_higher_risk_sex_survey_pct.
  The region rows, because "Other provinces" pools six provinces, and the men aged 15 and over
  testing row (0.8 per cent), as the dhs connector writes no 15+ testing row.
  The SINSO HIV fact sheet (sol-dhs_7-hiv), which prints the 2007 figures of the report.

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

# survey year -> (URL, local name, size, sha256 prefix of the copy read on 21 October 2026)
_FILES = {
    2015: ("https://statistics.gov.sb/download/54/dhs_2015/760/"
           "final-report_si-demographic-and-health-survey-2015",
           "sb_dhs_2015_report.pdf", 12_301_932, "1dca5cab1889"),
    2007: ("https://catalog.ihsn.org//catalog/2963/download/44676",
           "sb_dhs_2006_2007_report.pdf", 1_757_342, "75edc12c3545"),
}

_D = "[–-]"  # the reports print the en dash and the hyphen in age labels
_TOKEN = r"(\*|\(?\d[\d,]*(?:\.\d+)?\)?)"


def _flat(pages: List[str]) -> str:
    """The text layer of every page as one line, with every run of white space as one space."""
    return re.sub(r"\s+", " ", " ".join(pages)).strip()


def _table(text: str, caption: str, end: str, year: int) -> str:
    """The text of one table, from the caption to the next caption, skipping the contents list
    (where dot leaders follow the caption). Raises ValueError unless the table prints once."""
    found = list(re.finditer(caption + r"(?! ?\.{3})(.*?)" + end, text))
    if len(found) != 1:
        raise ValueError(f"{caption!r} prints {len(found)} times, expected once")
    body = found[0].group(1)
    if f"Solomon Islands {year}" not in body:
        raise ValueError(f"{caption!r} does not name Solomon Islands {year}")
    return body


def _row(body: str, label: str, n: int) -> List[Tuple[Optional[float], bool]]:
    """The `n` figures after the row label, as (value or None for a suppressed '*', printed in
    parentheses). Raises ValueError unless the label prints once."""
    found = list(re.finditer(r"(?<![\w.+])" + label + " " + " ".join([_TOKEN] * n) + r"(?![\d.])",
                             body))
    if len(found) != 1:
        raise ValueError(f"the row {label!r} prints {len(found)} times, expected once")
    out = []
    for tok in found[0].groups():
        if tok == "*":
            out.append((None, False))
        else:
            out.append((float(tok.strip("()").replace(",", "")), tok.startswith("(")))
    return out


def _vals(row) -> List[Optional[float]]:
    return [v for v, _ in row]


def _combine(parts, total, tol: float, what: str) -> None:
    """Weighted mean of (value, number) parts against (value, number) total."""
    number = sum(w for _, w in parts)
    if abs(number - total[1]) > 2:
        raise ValueError(f"{what}: the numbers add to {number}, against {total[1]}")
    mean = sum(v * w for v, w in parts) / number
    if abs(mean - total[0]) > tol:
        raise ValueError(f"{what}: the rows give {mean:.3f}, against the printed {total[0]}")


def _men_named(text: str, number: float, older: float, what: str) -> str:
    """The survey's own age range for men, from the report text naming the men interviewed.
    `older` is the printed number of men aged 50 and over, which the range must hold."""
    named = r"(?<![\d,])(\d[\d,]*) men aged 15" + _D + r" ?(\d\d)"
    ages = {m.group(2) for m in re.finditer(named, text)
            if float(m.group(1).replace(",", "")) == number}
    if len(ages) != 1:
        raise ValueError(f"{what}: the text names {number:,.0f} men with the age ranges "
                         f"{sorted(ages)}, expected one range")
    top = ages.pop()
    if older > 0 and int(top) < 50:
        raise ValueError(f"{what}: the text names men aged 15-{top}, but the tables print "
                         f"{older:,.0f} men aged 50 and over")
    return f"15-{top}"


def _testing(body: str, label: str, men: bool, what: str) -> Dict[str, object]:
    total = _vals(_row(body, label, 8))
    know, received, not_received, never, hundred, ever, tested, number = total
    if hundred != 100 or abs(received + not_received + never - 100) > 0.3:
        raise ValueError(f"{what}: the testing status adds to {received + not_received + never}")
    if abs(100 - never - ever) > 0.05 or tested > received:
        raise ValueError(f"{what}: ever tested {ever} or the 12-month share {tested} disagrees "
                         f"with never tested {never} and received {received}")
    urban, rural = (_vals(_row(body, place, 8)) for place in ("Urban", "Rural"))
    _combine([(urban[6], urban[7]), (rural[6], rural[7])], (tested, number), 0.1,
             f"{what}, urban and rural")
    out = {"value": tested, "number": number}
    if men:
        older, all_men = _vals(_row(body, r"50\+", 8)), _vals(_row(body, r"Total 15\+", 8))
        _combine([(tested, number), (older[6], older[7])], (all_men[6], all_men[7]), 0.1,
                 f"{what}, 15-49 and 50+")
        out["men_15_plus"] = all_men[7]
    return out


def parse_2015(pages: List[str]) -> Dict[Tuple[str, str], Dict[str, object]]:
    """{(indicator, sex): {value, number, ...}} from the 2015 report, after the gates of the
    module docstring. Raises ValueError when any gate fails."""
    text = _flat(pages)
    out: Dict[Tuple[str, str], Dict[str, object]] = {}
    for sex, word, end in (("female", "Women", r"Table 13\.9\.2:"),
                           ("male", "Men", r"Table 13\.10:")):
        body = _table(text, r"Table 13\.9\." + ("1" if sex == "female" else "2") +
                      r": Coverage of prior HIV testing " + _D + " " + word, end, 2015)
        if not re.search(r"who were tested in the 12 months preceding the survey and received "
                         r"the results of the last test", body) or \
                not re.search(r"1 Includes .don.t know", body):
            raise ValueError(f"Table 13.9 ({word}) does not print the definition of the measure")
        out[("hiv_tested_12m_result_survey_pct", sex)] = _testing(
            body, "Total 15" + _D + "49", sex == "male", f"2015 testing, {word.lower()}")
    body = _table(text, r"Table 13\.3\.2: Comprehensive knowledge about AIDS " + _D + " Men",
                  r"Table 13\.4:", 2015)
    out[("hiv_comprehensive_knowledge_survey_pct", "male")] = _knowledge(
        body, r"Total 15\+", "2015 knowledge, men")
    men = out[("hiv_tested_12m_result_survey_pct", "male")]
    knowledge = out[("hiv_comprehensive_knowledge_survey_pct", "male")]
    if knowledge["number"] != men["number"] or knowledge["men_15_plus"] != men["men_15_plus"]:
        raise ValueError("Table 13.3.2 and Table 13.9.2 print different numbers of men")
    ages = _men_named(text, men["men_15_plus"], men["men_15_plus"] - men["number"], "2015")
    for (ind, sex), rec in out.items():
        rec["survey_age_range"] = "15-49" if sex == "female" else ages
    return out


def _knowledge(body: str, all_label: str, what: str) -> Dict[str, object]:
    if not re.search(r"Comprehensive knowledge means knowing that consistent use of condoms? "
                     r"during sexual intercourse and having just one uninfected faithful "
                     r"partner", body):
        raise ValueError(f"{what}: the table does not print the definition of the measure")
    total = _vals(_row(body, "Total 15" + _D + "49", 7))
    older, all_men = _vals(_row(body, r"50\+", 7)), _vals(_row(body, all_label, 7))
    _combine([(total[5], total[6]), (older[5], older[6])], (all_men[5], all_men[6]), 0.1,
             f"{what}, 15-49 and 50+")
    return {"value": total[5], "number": total[6], "men_15_plus": all_men[6]}


def parse_2007(pages: List[str]) -> Dict[Tuple[str, str], Dict[str, object]]:
    """{(indicator, sex): {value, number, ...}} from the 2006-2007 report, after the gates of the
    module docstring. Raises ValueError when any gate fails."""
    text = _flat(pages)
    body = _table(text, r"Table 13\.3\.2: Comprehensive knowledge about AIDS: Men",
                  r"Table 13\.4:", 2007)
    knowledge = _knowledge(body, r"Total men 15\+", "2007 knowledge, men")
    body = _table(text, r"Table 13\.7\.2: Multiple sexual partners and higher-risk sexual "
                  r"intercourse in the past 12 months: Men", r"Table 13\.8:", 2007)
    if not re.search(r"Sexual intercourse with a partner who neither was a spouse nor who lived "
                     r"with the respondent", body):
        raise ValueError("Table 13.7.2 does not print the definition of higher-risk sex")
    row = _row(body, "Total 15" + _D + "49", 9)
    share, had_sex, condom, condom_n = row[1][0], row[2][0], row[5], row[6][0]
    if condom[0] is None or abs(share * had_sex / 100 - condom_n) > 1.5:
        raise ValueError(f"2007 condom use, men: {share} per cent of {had_sex} men against "
                         f"{condom_n} men with higher-risk sex, or a suppressed value")
    all_men = _vals(_row(body, r"Total men 15\+", 9))
    older = _vals(_row(body, r"50\+", 9))
    for col in (2, 4, 6, 8):  # every number column of the table, not only the condom column
        if abs(row[col][0] + older[col] - all_men[col]) > 2:
            raise ValueError(f"2007 condom use, men: the 15-49 and 50+ numbers of column "
                             f"{col + 1} add to {row[col][0] + older[col]}, against "
                             f"{all_men[col]}")
    ages = _men_named(text, knowledge["men_15_plus"],
                      knowledge["men_15_plus"] - knowledge["number"], "2007")
    condom_rec = {"value": condom[0], "number": condom_n, "survey_age_range": ages,
                  "parentheses": condom[1]}
    knowledge["survey_age_range"] = ages
    return {("hiv_comprehensive_knowledge_survey_pct", "male"): knowledge,
            ("condom_last_higher_risk_sex_survey_pct", "male"): condom_rec}


_TABLES = {
    ("hiv_tested_12m_result_survey_pct", 2015): ("Table 13.9.1 (women), Table 13.9.2 (men)",
                                                 "Women interviewed", "Men interviewed"),
    ("hiv_comprehensive_knowledge_survey_pct", 2015): ("Table 13.3.2", "", "Men interviewed"),
    ("hiv_comprehensive_knowledge_survey_pct", 2007): ("Table 13.3.2", "", "Men interviewed"),
    ("condom_last_higher_risk_sex_survey_pct", 2007): (
        "Table 13.7.2", "", "Men who had sex with a non-marital, non-cohabiting partner in the "
        "last 12 months"),
}
_RECONCILE = ("pacific_data_hub carries the women's, men's 15+ and youth rows of the same "
              "reports on other keys, every value equal to the printed tables. No other source "
              "carries a Solomon Islands row on the keys of sb_sinso_dhs")
_NOT_CARRIED = ("every value pacific_data_hub carries on the same key, the 2007 testing "
                "variable (no table, printed as 0 with standard error 0), the 2015 condom table "
                "(two or more partners, a different measure), the region rows, the men 15+ "
                "testing row, and the SINSO HIV fact sheet (ruling R48)")


class SolomonIslandsSINSOConnector(BaseConnector):
    """Printed tables of the Solomon Islands DHS reports of 2006-2007 and 2015."""

    source_id = "sb_sinso_dhs"
    default_source_type = SourceType.SURVEY
    description = ("Solomon Islands National Statistics Office, Demographic and Health Surveys "
                   "2006-2007 and 2015, HIV testing for women and men and knowledge and condom "
                   "use for men aged 15 to 49, national (to-source).")
    country = "SLB"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/sb_sinso_dhs", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, year: int) -> Path:
        """Local copy of the `year` report, downloading only if not cached."""
        url, name, size, prefix = _FILES[year]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / name
        if path.exists():
            log.info("sb_sinso_dhs: using cached %s", path)
        else:
            blob = self._request("GET", url).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{url} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("sb_sinso_dhs: downloaded the %d report (%d bytes) -> %s", year, len(blob),
                     path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (size, prefix):
            log.info("sb_sinso_dhs: the %d report matches the copy read on 21 October 2026 "
                     "(sha256 %s)", year, digest[:12])
        else:
            log.warning("sb_sinso_dhs: the %d report differs from the copy read on 21 October "
                        "2026 (%d bytes, sha256 %s, expected %d bytes), and the gates still run",
                        year, len(blob), digest[:12], size)
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
            log.error("sb_sinso_dhs: pdfplumber not installed (pip install pdfplumber)")
            return
        parsers = {2015: parse_2015, 2007: parse_2007}
        emitted = 0
        for year in sorted(_FILES):
            if not start_year <= year <= end_year:
                continue
            try:
                path = self._pdf_path(year)
                with pdfplumber.open(str(path)) as pdf:
                    records = parsers[year]([p.extract_text() or "" for p in pdf.pages])
            except Exception as exc:
                log.warning("sb_sinso_dhs: the %d report failed (%s), no row emitted for %d",
                            year, exc, year)
                continue
            for (indicator, sex), rec in sorted(records.items()):
                table, women_den, men_den = _TABLES[(indicator, year)]
                code = table if indicator != "hiv_tested_12m_result_survey_pct" else \
                    ("Table 13.9.1" if sex == "female" else "Table 13.9.2")
                extra = {"survey": "DHS",
                         "report": f"Solomon Islands DHS {'2006-2007' if year == 2007 else 2015} "
                                   f"final report, {table}",
                         "dhs_denominator": women_den if sex == "female" else men_den,
                         "sample_universe": "All Women" if sex == "female" else "All Men",
                         "survey_age_range": rec["survey_age_range"],
                         "denominator_weighted": rec["number"],
                         "reconcile_with": _RECONCILE,
                         "not_carried": _NOT_CARRIED}
                if rec.get("parentheses"):
                    extra["dhs_precision"] = ("25 to 49 unweighted cases, printed in parentheses "
                                              "in DHS reports")
                emitted += 1
                yield self.make_row(
                    country_iso3="SLB", country_name="Solomon Islands", admin1="",
                    indicator_id=indicator, year=year, value=rec["value"], unit="percent",
                    population_group="all", sex=sex, age_group="15-49",
                    source_url=_FILES[year][0],
                    source_indicator_code=f"sb_dhs_{year}:{code}:{sex}",
                    extra=extra,
                )
        log.info("sb_sinso_dhs: emitted %d rows", emitted)
