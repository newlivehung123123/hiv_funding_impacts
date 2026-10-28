"""
Fiji, people newly registered with HIV nationally, by division, by sex and by age, with the
diagnosed people living with HIV and the people with a suppressed viral load, from the public
HIV surveillance workbook of the Ministry of Health and Medical Services, connector 72.

Source. The page https://www.health.gov.fj/fiji-hiv-surveillance-report-2025/ of the Ministry of
Health and Medical Services (MOHMS) links the public workbook "Fiji HIV Surveillance Data 2025"
(Fiji_HIV_Surveillance_Data_2025_Public-1.xlsx) and the summary report of the "2025 National HIV
Statistics" (2025_HIV_Summary_Report_Final_02042026.pdf) under wp-content/uploads/2026/05/, with
the workbook and the summary report last modified on 1 May 2026 and read on 14 October 2026. No
sign-in and no key. The connector downloads the workbook and the summary report once into
`raw_dir`, every later run reads the cached copies, the workbook is read with
openpyxl (cached cell values) and the summary report with the pdfplumber text layer, with no
optical character recognition. The workbook source line reads "National HIV Database, Ministry
of Health and Medical Services, Fiji".

Sheets read. "Cases" (new cases by year of diagnosis, 1989 to 2025, with a cumulative column),
"Divisions" (new cases from 2018 to 2025 by division, Central / Eastern, Western and Northern, by
sex, M, F and TG, and for adults and for children under 15 years), "Gender" (new cases by sex from
2019), "Age" (new cases by age group, 2022 to 2025), "Ethnicity" (totals only, as a check) and
"Treatment Cascade" (the national rows PLHIV, On ART and Viral suppression, 2020 to 2025).

Gates. A figure enters only when every check below passes, because two printed figures
disagreeing leave the true figure unknown.
  Every header the connector reads prints exactly as described above.
  The Cases sheet runs without a gap from 1989, and the cumulative column equals the running sum
  of the new cases in every year.
  In the Divisions sheet the nine figures of every row add to the printed row total, where a
  blank entry counts as zero only because the printed figures already add to the total (the
  paediatric row of 2024 prints eight of the nine figures). The three divisions add to the Cases count in every
  year from 2018 to 2025.
  The Gender sheet totals equal the Cases count from 2019, and men plus women plus transgender
  people plus unknown sex equal the printed total, and a disagreement drops the year. Where the
  Gender sheet and the Divisions sheet give a different count of men, women or transgender people
  for a year, the year gets no row for the sex concerned, nationally and in every division, and
  keeps the totals and the age rows. The 2021 Gender sheet prints 79 men and 71 women against 80
  men and 70 women in the Divisions sheet, with 151 cases on the Gender sheet and on the
  Divisions sheet, and 2021 therefore gets no row for men or women.
  The Ethnicity sheet totals equal the Cases count from 2022 to 2025.
  An age group year of the Age sheet enters only when the age groups add to the Cases count and
  the three age groups under 15 years add to the paediatric rows of the Divisions sheet. The age
  groups of 2023 add to 419 against 415 in the Cases sheet, and 2023 therefore gets no age group
  row.
  When the summary report reads, Table 1 of the summary report (2025 by division for adults and
  children) equals the workbook, and a disagreement drops the 2025 case rows. A 2025 count of
  men, women or transgender people in the summary report which disagrees with the workbook drops
  the 2025 rows for the sex concerned.
  The diagnosed people living with HIV enter only when the summary report reads, prints the
  end-2025 counts of the workbook (3,535 people living with HIV and 1,979 on ART), and prints,
  for every year from 2022 to 2025, the ART coverage the workbook gives (on ART divided by people
  living with HIV, rounded to a whole per cent, 54, 42, 68 and 56). The people with a suppressed
  viral load enter only when the diagnosed people living with HIV enter, the summary report
  prints the 288 people with documented viral suppression of the workbook, and the workbook row
  prints a figure for every year from 2022 to 2025 and for no earlier year. A failure in the
  Treatment Cascade sheet removes the cascade rows and keeps the case rows.

What the connector emits.
  notified_hiv_cases, nationally, all sexes and ages, for every year of the Cases sheet.
  notified_hiv_cases, nationally, men and women (sex male and female) and transgender people
  (population group transgender), and children under 15 years and people aged 15 years or more
  (age groups 0-14 and 15+), from the Divisions sheet, 2018 to 2025, with no row for men or
  women in 2021.
  notified_hiv_cases, nationally, by the age groups 0-4, 5-9, 10-14, 15-19, 20-24, 25-29, 30-34,
  35-39, 40-44, 45-49 and 50+ of the Age sheet, for 2022, 2024 and 2025.
  notified_hiv_cases, admin1 rows for the three divisions (Central/Eastern, Western, Northern),
  all, men, women, transgender people, 0-14 and 15+, 2018 to 2025, with no row for men or women
  in 2021.
  know_status_count, nationally, the "PLHIV" row of the Treatment Cascade sheet, people living
  with HIV reported in Fiji by the end of the year (the division blocks of the same sheet head the
  breakdown of the row "Knowledge of Status"), 2020 to 2025.
  viral_suppression_count, nationally, the "Viral suppression" row (viral load under 1,000
  copies/mL), 2022 to 2025, the years the summary report gives for the trend of ART coverage and
  viral suppression.

Not carried (ruling R66 of research/rulings_2026-10-15.md).
  The national On ART row, a DUPLICATE of who_gho on_art_count, with three disagreements (574
  against 568 for 2022, 580 against 711 for 2023, 1,979 against 2,003 for 2025).
  The division blocks of the Treatment Cascade sheet, which print West, Central and North where
  the case sheets print Central / Eastern, Western and Northern, and whose 2025 on-ART rows do not
  add to the printed division totals.
  The deaths (the Fiji deaths ruling), the ethnicity rows, the mode of transmission and the care
  status at diagnosis, which have no panel indicator.
  The key population split of the Key Pops sheet for 2025 (144 men who have sex with men and 362
  people who inject drugs), because 1,164 of the 2,016 cases of 2025 carry an unknown key
  population, which makes every key population count a lower bound.
  The screening tests and the positivity rate of the summary report, because the summary report
  counts screening tests conducted, repeat tests of people already diagnosed among the screening
  tests, while hiv_tests_performed counts tests with the result returned to the person.
  The full surveillance report (Fiji_HIV_Surveillance_Report_2025_FINAL.pdf), whose case, cascade,
  death and test tables repeat the workbook and the summary report. The CD4 count table of 2025
  (table 7, page 54) is not carried under late_hiv_diagnosis_pct, because page 56 of the report
  calls the 2025 CD4 data a partial picture, and page 60 dates interruptions to CD4 testing at
  Labasa Hospital from February 2025.

Source type. routine_programme_record, the case register of the national HIV programme.
"""
from __future__ import annotations

import hashlib
import io
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_BASE = "https://www.health.gov.fj/wp-content/uploads/2026/05/"
_PAGE = "https://www.health.gov.fj/fiji-hiv-surveillance-report-2025/"
# key -> (file name, size, sha256 prefix of the copy read on 14 October 2026, magic bytes)
_FILES = {
    "workbook": ("Fiji_HIV_Surveillance_Data_2025_Public-1.xlsx", 118_422, "9a7a07eceee9",
                 b"PK\x03\x04"),
    "summary": ("2025_HIV_Summary_Report_Final_02042026.pdf", 462_412, "92068e52f92c", b"%PDF"),
}

_DIVISIONS = {"central/eastern": "Central/Eastern", "western": "Western", "northern": "Northern"}
_SEXES = ("m", "f", "tg")
_BANDS = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49",
          "50+"]
_CHILD_BANDS = ("0-4", "5-9", "10-14")

_DEF_CASES = ("People newly registered with HIV in the year by year of diagnosis in the National "
              "HIV Database of the Ministry of Health and Medical Services of Fiji, the public "
              "workbook \"Fiji HIV Surveillance Data 2025\"")
_DEF_KNOW = ("People living with HIV reported in Fiji by the end of the year according to the "
             "national HIV database and treatment monitoring systems, the \"PLHIV\" row of the "
             "Treatment Cascade sheet, whose division breakdown the sheet heads \"Knowledge of "
             "Status\"")
_DEF_VS = ("People on ART with documented viral suppression (viral load under 1,000 copies/mL) "
           "at the end of the year, the \"Viral suppression\" row of the Treatment Cascade sheet")
_RECONCILE = ("No other source carries notified_hiv_cases for Fiji. Never compare with "
              "new_diagnoses (Jason's ruling of 8 October 2026)")
_NOT_CARRIED = ("the national On ART row (a DUPLICATE of who_gho, 574 against 568 for 2022, 580 "
                "against 711 for 2023, 1,979 against 2,003 for 2025), the division blocks of the "
                "Treatment Cascade sheet, the deaths, ethnicity, mode of transmission, key "
                "population and care status, the screening tests and positivity of the summary "
                "report, and the full surveillance report, with the CD4 count table of 2025 "
                "(ruling R66)")


def _norm(v) -> str:
    """Lower-case text of a cell with every space removed, '' for a blank cell."""
    return "" if v is None else re.sub(r"\s+", "", str(v)).lower()


def _int(v) -> Optional[int]:
    """The whole number in a cell, None for a blank cell. Raises ValueError for anything else."""
    if v is None or (isinstance(v, str) and v.strip() == ""):
        return None
    if isinstance(v, bool):
        raise ValueError(f"cell {v!r} is not a count")
    if isinstance(v, (int, float)) and float(v).is_integer():
        return int(v)
    if isinstance(v, str) and re.fullmatch(r"\d[\d,]*", v.strip()):
        return int(v.strip().replace(",", ""))
    raise ValueError(f"cell {v!r} is not a count")


def _find_row(rows: List[tuple], labels: List[str], sheet: str) -> Tuple[int, Dict[str, int]]:
    """(row index, {label: column}) of the single row printing every label. Raises ValueError
    unless exactly one row prints every label, and every label once in that row."""
    want = [_norm(x) for x in labels]
    found = []
    for i, row in enumerate(rows):
        cells = [_norm(v) for v in row]
        if all(cells.count(w) == 1 for w in want):
            found.append((i, {w: cells.index(w) for w in want}))
    if len(found) != 1:
        raise ValueError(f"{sheet}: the header {labels} prints {len(found)} times, expected once")
    return found[0]


def parse_cases(rows: List[tuple]) -> Dict[int, int]:
    """{year: new cases} from the Cases sheet, after the cumulative check."""
    i, col = _find_row(rows, ["Year", "New Cases", "Cumulative Cases"], "Cases")
    out: Dict[int, int] = {}
    running = 0
    for row in rows[i + 1:]:
        year = row[col["year"]] if len(row) > col["year"] else None
        if not isinstance(year, (int, float)) or not 1980 <= int(year) <= 2100:
            break
        year = int(year)
        new, cum = _int(row[col["newcases"]]), _int(row[col["cumulativecases"]])
        if new is None or cum is None:
            raise ValueError(f"Cases: {year} prints a blank count")
        if out and year != max(out) + 1:
            raise ValueError(f"Cases: {year} follows {max(out)}")
        running += new
        if cum != running:
            raise ValueError(f"Cases: the cumulative count of {year} reads {cum}, against the "
                             f"running sum {running}")
        out[year] = new
    if not out or min(out) != 1989:
        raise ValueError("Cases: the series does not start in 1989")
    return out


def parse_divisions(rows: List[tuple]) -> Tuple[Dict[int, Dict[str, Dict[str, Dict[str, int]]]],
                                                   List[str]]:
    """({year: {"adults"|"children": {admin1: {sex: count}}}}, blank cells), after the row
    total check."""
    labels = ["Year", "Population", "Central / Eastern", "Western", "Northern", "Total"]
    i, col = _find_row(rows, labels, "Divisions")
    sub = [_norm(v) for v in rows[i + 1]]
    for key in _DIVISIONS:
        c = col[_norm(key)]
        if sub[c:c + 3] != list(_SEXES):
            raise ValueError(f"Divisions: the sex header under {key} reads {sub[c:c + 3]}")
    out: Dict[int, Dict[str, Dict[str, Dict[str, int]]]] = {}
    blanks: List[str] = []
    year = None
    for row in rows[i + 2:]:
        row = tuple(row) + (None,) * (len(labels) + 12 - len(row))
        if isinstance(row[col["year"]], (int, float)):
            year = int(row[col["year"]])
        pop = _norm(row[col["population"]])
        if pop == "" and all(v is None for v in row):
            continue
        if pop == "adults":
            group = "adults"
        elif pop in ("paeds", "pediatrics", "paediatrics"):
            group = "children"
        else:
            break
        if year is None or group in out.get(year, {}):
            raise ValueError(f"Divisions: the {group} row after {year} has no year of its own")
        cells: Dict[str, Dict[str, int]] = {}
        printed = 0
        for key, admin1 in _DIVISIONS.items():
            c = col[_norm(key)]
            cells[admin1] = {}
            for k, sex in enumerate(_SEXES):
                v = _int(row[c + k])
                if v is None:
                    blanks.append(f"{year} {group} {admin1} {sex.upper()}")
                    v = 0
                cells[admin1][sex] = v
                printed += v
        total = _int(row[col["total"]])
        if total != printed:
            raise ValueError(f"Divisions: the {year} {group} cells add to {printed}, against the "
                             f"printed total {total}")
        out.setdefault(year, {})[group] = cells
    for year, rec in out.items():
        if set(rec) != {"adults", "children"}:
            raise ValueError(f"Divisions: {year} prints {sorted(rec)}, expected adults and "
                             f"children")
    return out, blanks


def parse_gender(rows: List[tuple]) -> Dict[int, Dict[str, int]]:
    """{year: {"m", "f", "tg", "unknown", "total"}} for the yearly rows of the Gender sheet."""
    labels = ["Period / Year", "Male", "Female", "Transgender", "Unknown", "Total"]
    i, col = _find_row(rows, labels, "Gender")
    out: Dict[int, Dict[str, int]] = {}
    for row in rows[i + 1:]:
        year = row[col["period/year"]] if len(row) > col["period/year"] else None
        if isinstance(year, str) and re.match(r"1989\s*-", year.strip()) and not out:
            continue  # the cumulative row "1989-Dec. 2018"
        if isinstance(year, str) and year.strip().isdigit():
            year = int(year.strip())
        if not isinstance(year, (int, float)):
            break
        year = int(year)
        rec = {"m": _int(row[col["male"]]), "f": _int(row[col["female"]]),
               "tg": _int(row[col["transgender"]]), "unknown": _int(row[col["unknown"]]),
               "total": _int(row[col["total"]])}
        if any(v is None for v in rec.values()):
            raise ValueError(f"Gender: {year} prints a blank count")
        if rec["m"] + rec["f"] + rec["tg"] + rec["unknown"] != rec["total"]:
            raise ValueError(f"Gender: the {year} sexes do not add to the printed total")
        out[year] = rec
    return out


def parse_by_year_columns(rows: List[tuple], first: str, years: List[int], sheet: str,
                          stop: str) -> Dict[str, Dict[int, Optional[int]]]:
    """{row label: {year: count}} for a sheet whose header prints `first` and the years, down to
    the row labelled `stop` (included)."""
    i, col = _find_row(rows, [first] + [str(y) for y in years], sheet)
    lab = col[_norm(first)]
    out: Dict[str, Dict[int, Optional[int]]] = {}
    for row in rows[i + 1:]:
        name = _norm(row[lab]) if len(row) > lab else ""
        if name == "":
            break
        out[name] = {y: _int(row[col[str(y)]]) for y in years}
        if name == _norm(stop):
            return out
    raise ValueError(f"{sheet}: no {stop!r} row under the header")


def parse_cascade(rows: List[tuple]) -> Dict[str, Dict[int, Optional[int]]]:
    """{"plhiv"|"onart"|"viralsuppression": {year: count}} from the first block of the Treatment
    Cascade sheet, under the first row printing the six years."""
    years = list(range(2020, 2026))
    want = [str(y) for y in years]
    heads = [i for i, row in enumerate(rows) if all([_norm(v) for v in row].count(w) == 1
                                                     for w in want)]
    if not heads:
        raise ValueError("Treatment Cascade: no row prints the years 2020 to 2025")
    i = heads[0]
    cells = [_norm(v) for v in rows[i]]
    col = {w: cells.index(w) for w in want}
    out: Dict[str, Dict[int, Optional[int]]] = {}
    for row in rows[i + 1:i + 4]:
        label = next((_norm(v) for v in row if v is not None), "")
        out[label] = {y: _int(row[col[str(y)]]) for y in years}
    if list(out) != ["plhiv", "onart", "viralsuppression"]:
        raise ValueError(f"Treatment Cascade: the rows under the year header read {list(out)}")
    for y in years:
        p, a, s = (out[k][y] for k in ("plhiv", "onart", "viralsuppression"))
        if p is None or a is None or a > p or (s is not None and s > a):
            raise ValueError(f"Treatment Cascade: {y} reads {p} people with HIV, {a} on ART "
                             f"and {s} suppressed")
    return out


def _n(s: str) -> int:
    return int(s.replace(",", ""))


def parse_summary(text: str) -> Dict[str, object]:
    """The 2025 figures of the summary report the gates use. Raises ValueError when a figure does
    not print exactly once."""
    t = re.sub(r"\s+", " ", text)
    pct = r"\([\d.]+%\)"
    pats = {
        "adults": rf"Adults \(aged 15 years ([\d,]+) {pct} ([\d,]+) {pct} ([\d,]+) {pct} ([\d,]+)",
        "children": rf"Paediatric \(aged under ([\d,]+) {pct} ([\d,]+) {pct} ([\d,]+) {pct} "
                    rf"([\d,]+)",
        "sex": r"male at [\d.]+% \(([\d,]+)\), while females accounted for [\d.]+% \(([\d,]+)\) "
               r"and transgender individuals made up [\d.]+% \(([\d,]+)\)",
        "plhiv": r"a total of ([\d,]+) people living with HIV \(PLHIV\) had been reported in Fiji "
                 r"by the end of 2025",
        "onart": r"([\d,]+) people were receiving antiretroviral therapy \(ART\)",
        "vs": r"([\d,]+) individuals had documented viral suppression",
        "coverage": r"ART coverage among reported PLHIV varied as follows: (\d+)% \(2022\), "
                    r"(\d+)% \(2023\), (\d+)% \(2024\), and (\d+)% \(2025\)",
    }
    if "Central/Eastern Northern Western Total" not in t:
        raise ValueError("summary report: Table 1 does not print the division header")
    out: Dict[str, object] = {}
    for key, pat in pats.items():
        found = re.findall(pat, t)
        if len(found) != 1:
            raise ValueError(f"summary report: {key} prints {len(found)} times, expected once")
        g = found[0] if isinstance(found[0], tuple) else (found[0],)
        out[key] = [_n(x) for x in g]
    return out


def check_summary(summary: Dict[str, object], divisions: Dict,
                  cascade: Optional[Dict]) -> Dict[str, object]:
    """{"cases": Table 1 agrees, "sexes": the sexes whose 2025 count disagrees, "know": the
    people living with HIV, on ART and coverage agree, "vs": the 2025 viral suppression count
    agrees}."""
    order = ["Central/Eastern", "Northern", "Western"]
    out: Dict[str, object] = {"cases": True, "sexes": set(), "know": False, "vs": False}
    if 2025 not in divisions:
        out["cases"] = False
        return out
    for group in ("adults", "children"):
        mine = [sum(divisions[2025][group][a].values()) for a in order]
        if summary[group] != mine + [sum(mine)]:
            log.warning("fj_mohms: Table 1 of the summary report prints %s for the 2025 %s, "
                        "against %s in the workbook", summary[group], group, mine)
            out["cases"] = False
    for k, sex in enumerate(_SEXES):
        mine = sum(divisions[2025][g][a][sex] for g in ("adults", "children") for a in order)
        if summary["sex"][k] != mine:
            log.warning("fj_mohms: the summary report prints %s for the 2025 %s count, against "
                        "%s in the workbook", summary["sex"][k], sex.upper(), mine)
            out["sexes"].add(sex)
    if cascade is None:
        return out
    shares = [int(100 * cascade["onart"][y] / cascade["plhiv"][y] + 0.5) for y in range(2022, 2026)]
    out["know"] = (summary["plhiv"] == [cascade["plhiv"][2025]]
                   and summary["onart"] == [cascade["onart"][2025]]
                   and summary["coverage"] == shares)
    out["vs"] = out["know"] and summary["vs"] == [cascade["viralsuppression"][2025]]
    if not out["know"]:
        log.warning("fj_mohms: the summary report prints %s people with HIV, %s on ART and "
                    "coverage %s, against the workbook %s, %s and %s, no cascade row",
                    summary["plhiv"], summary["onart"], summary["coverage"],
                    cascade["plhiv"][2025], cascade["onart"][2025], shares)
    elif not out["vs"]:
        log.warning("fj_mohms: the summary report prints %s people with a suppressed viral "
                    "load for 2025, against %s, no viral_suppression_count row", summary["vs"],
                    cascade["viralsuppression"][2025])
    return out


class FijiMOHMSConnector(BaseConnector):
    """Public HIV surveillance workbook of the Fijian Ministry of Health and Medical Services."""

    source_id = "fj_mohms"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Ministry of Health and Medical Services of Fiji, public HIV surveillance "
                   "workbook 2025 and summary report, people newly registered with HIV by year, "
                   "division, sex and age, diagnosed people living with HIV and viral "
                   "suppression (to-source).")
    country = "FJI"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/fj_mohms", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _file(self, key: str) -> bytes:
        """The cached copy of `key`, downloading only if not cached."""
        name, size, prefix, magic = _FILES[key]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / name
        if path.exists():
            log.info("fj_mohms: using cached %s", path)
        else:
            blob = self._request("GET", _BASE + name).content
            if not blob.startswith(magic):
                raise RuntimeError(f"{_BASE + name} did not return the expected file "
                                   f"(got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("fj_mohms: downloaded %s (%d bytes) -> %s", name, len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (size, prefix):
            log.info("fj_mohms: %s matches the copy read on 14 October 2026 (sha256 %s)",
                     name, digest[:12])
        else:
            log.warning("fj_mohms: %s differs from the copy read on 14 October 2026 (%d bytes, "
                        "sha256 %s, expected %d bytes), and the gates still run",
                        name, len(blob), digest[:12], size)
        return blob

    def _row(self, indicator: str, year: int, value: int, code: str, definition: str,
             admin1: Optional[str] = None, sex: str = "all", age: str = "all",
             pop: str = "all", source: str = "workbook", **extra) -> PanelRow:
        info = {"definition": definition, "report": code, "not_carried": _NOT_CARRIED}
        if indicator == "notified_hiv_cases":
            info["reconcile_with"] = _RECONCILE
        info.update(extra)
        return self.make_row(
            country_iso3="FJI", country_name="Fiji", admin1=admin1, indicator_id=indicator,
            year=year, value=float(value), unit="count", population_group=pop, sex=sex,
            age_group=age, source_url=_BASE + _FILES[source][0],
            source_indicator_code=f"fj_mohms:{code}", extra=info)

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
            import openpyxl
        except ImportError:
            log.error("fj_mohms: openpyxl not installed")
            return
        try:
            wb = openpyxl.load_workbook(io.BytesIO(self._file("workbook")), data_only=True)
            sheet = lambda name: [tuple(r) for r in wb[name].iter_rows(values_only=True)]
            cases = parse_cases(sheet("Cases"))
            divisions, blanks = parse_divisions(sheet("Divisions"))
            gender = parse_gender(sheet("Gender"))
            eth_years = [2022, 2023, 2024, 2025]
            eth = parse_by_year_columns(sheet("Ethnicity"), "Ethnicity", eth_years, "Ethnicity",
                                        "Total")
            age = parse_by_year_columns(sheet("Age"), "Age Group", eth_years, "Age", "Total")
        except Exception as exc:
            log.warning("fj_mohms: the workbook failed (%s), no row emitted", exc)
            return
        try:
            cascade = parse_cascade(sheet("Treatment Cascade"))
            vs_years = [y for y, v in cascade["viralsuppression"].items() if v is not None]
            if vs_years != list(range(2022, 2026)):
                log.warning("fj_mohms: the Viral suppression row prints the years %s, against "
                            "2022 to 2025, no viral_suppression_count row", vs_years)
                cascade["viralsuppression"] = {y: None for y in cascade["viralsuppression"]}
        except Exception as exc:
            log.warning("fj_mohms: the Treatment Cascade sheet failed (%s), no cascade row", exc)
            cascade = None
        # cross-sheet gates
        bad: List[int] = []
        bad_sex: Dict[int, set] = {}  # sexes whose count disagrees between two sheets
        for year, rec in divisions.items():
            added = sum(sum(rec[g][a].values()) for g in rec for a in rec[g])
            if cases.get(year) != added:
                log.warning("fj_mohms: the %d divisions add to %d, against %s in Cases", year,
                            added, cases.get(year))
                bad.append(year)
            if year in gender:
                if gender[year]["total"] != cases.get(year):
                    log.warning("fj_mohms: the %d Gender total %s disagrees with Cases %s", year,
                                gender[year]["total"], cases.get(year))
                    bad.append(year)
                for sex in _SEXES:
                    mine = sum(rec[g][a][sex] for g in rec for a in rec[g])
                    if gender[year][sex] != mine:
                        log.warning("fj_mohms: the %d Gender sheet prints %s for %s, against %s "
                                    "in the Divisions sheet, no %s row for %d", year,
                                    gender[year][sex], sex.upper(), mine, sex.upper(), year)
                        bad_sex.setdefault(year, set()).add(sex)
        for year in eth_years:
            if eth["total"][year] != cases.get(year):
                log.warning("fj_mohms: the %d Ethnicity total %s disagrees with Cases %s", year,
                            eth["total"][year], cases.get(year))
                bad.append(year)
        know_ok = vs_ok = False
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(self._file("summary"))) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
            agree = check_summary(parse_summary(text), divisions, cascade)
            know_ok, vs_ok = agree["know"], agree["vs"]
            if not agree["cases"]:
                bad.append(2025)
            if agree["sexes"]:
                bad_sex.setdefault(2025, set()).update(agree["sexes"])
        except Exception as exc:
            log.warning("fj_mohms: the summary report failed (%s), no know_status_count or "
                        "viral_suppression_count row", exc)
        if blanks:
            log.info("fj_mohms: blank cells counted as zero (the row totals print the sum of "
                     "the printed cells): %s", "; ".join(blanks))
        emitted = 0
        keep = lambda y: start_year <= y <= end_year and y not in bad
        for year, value in sorted(cases.items()):
            if keep(year):
                emitted += 1
                more = {"sex_unknown": gender[year]["unknown"]} if year in gender else {}
                yield self._row("notified_hiv_cases", year, value, f"Cases:{year}", _DEF_CASES,
                                **more)
        for year, rec in sorted(divisions.items()):
            if not keep(year):
                continue
            areas = [None] + list(_DIVISIONS.values())
            dropped = bad_sex.get(year, set())
            for admin1 in areas:
                names = list(_DIVISIONS.values()) if admin1 is None else [admin1]
                tot = lambda groups, sexes: sum(rec[g][a][s] for g in groups for a in names
                                                for s in sexes)
                both = ("adults", "children")
                cuts = [("male", "all", "all", tot(both, ("m",))) if "m" not in dropped else None,
                        ("female", "all", "all", tot(both, ("f",))) if "f" not in dropped else None,
                        ("all", "all", "transgender", tot(both, ("tg",)))
                        if "tg" not in dropped else None,
                        ("all", "0-14", "all", tot(("children",), _SEXES)),
                        ("all", "15+", "all", tot(("adults",), _SEXES))]
                cuts = [c for c in cuts if c is not None]
                if admin1 is not None:
                    cuts.insert(0, ("all", "all", "all", tot(both, _SEXES)))
                for sex, age_group, pop, value in cuts:
                    emitted += 1
                    yield self._row("notified_hiv_cases", year, value,
                                    f"Divisions:{year}:{admin1 or 'Fiji'}:{sex}:{age_group}:{pop}",
                                    _DEF_CASES, admin1=admin1, sex=sex, age=age_group, pop=pop,
                                    blank_cells=[b for b in blanks if b.startswith(str(year))]
                                    or None)
        bands = {re.sub(r"\s+", "", k): v for k, v in age.items() if k != "total"}
        if sorted(bands, key=_BANDS.index if set(bands) <= set(_BANDS) else str) != _BANDS:
            log.warning("fj_mohms: the Age sheet prints the age groups %s, no age group row",
                        list(bands))
            bands = {}
        for year in eth_years:
            if not bands or not keep(year):
                continue
            added = sum(bands[b][year] or 0 for b in _BANDS)
            children = sum(bands[b][year] or 0 for b in _CHILD_BANDS)
            div_children = sum(sum(v.values()) for v in divisions[year]["children"].values())
            if added != cases[year] or age["total"][year] != added or children != div_children:
                log.warning("fj_mohms: the %d age groups add to %d (printed total %s), against "
                            "%d in Cases, and the groups under 15 add to %d against %d, no age "
                            "group row for %d", year, added, age["total"][year], cases[year],
                            children, div_children, year)
                continue
            for b in _BANDS:
                emitted += 1
                yield self._row("notified_hiv_cases", year, bands[b][year] or 0,
                                f"Age:{year}:{b}", _DEF_CASES, age=b)
        if know_ok:
            for year in range(2020, 2026):
                if start_year <= year <= end_year:
                    emitted += 1
                    yield self._row("know_status_count", year, cascade["plhiv"][year],
                                    f"Treatment Cascade:PLHIV:{year}", _DEF_KNOW)
                    vs = cascade["viralsuppression"][year]
                    if vs_ok and vs is not None:
                        emitted += 1
                        yield self._row("viral_suppression_count", year, vs,
                                        f"Treatment Cascade:Viral suppression:{year}", _DEF_VS)
        log.info("fj_mohms: emitted %d rows", emitted)
