"""
India, the India HIV Estimates 2025 by State and Union Territory, from the seventh edition of
Sankalak, the yearly status report of the National AIDS Control Organisation (NACO,
https://naco.mohfw.gov.in/sankalak/), connector 64.

Source. NACO estimates the HIV burden of India with the Spectrum model UNAIDS recommends, and
Sankalak: Status of National AIDS & STD Response (2025), the seventh edition, prints the 2024
results of the round India HIV Estimates 2025 by State and Union Territory in Table 2.2.
NACO published the seventh edition twice. The Sankalak page of the NACO site links the version
"as on 30.01.2026" (uploaded 28 June 2026), whose Table 2.2 sits on a page rotated a quarter
turn, and the NACO media library holds a revised version, R_1 (modified 31 July 2026, uploaded
3 August 2026), with Table 2.2 printed upright and some figure labels of page 44 corrected.
The two files were read on 21 October 2026 (research/phase6_sas/sas_round1_notes.md, India).
No sign-in and no key. The connector downloads the two files once into `raw_dir`, every later
run reads the cached copies, and the connector reads the pdfplumber text layer with no optical
character recognition.

Table read. Table 2.2, "State/UT-wise HIV prevalence, incidence, mortality, PLHIV Size, IPR
and IMR, 2024", gives 34 States and Union Territories and India, every row with the adult
(15-49) HIV prevalence, the PLHIV size, the new HIV infections and the annual AIDS-related
deaths, every figure with an uncertainty bound. Jammu and Kashmir and Ladakh share one row.
Lakshadweep has no row.

Gates. The table enters only when every check below passes, because two published figures
disagreeing leave the true figure unknown.
  Every version prints the Table 2.2 heading once outside the contents, for the year 2024.
  Every version prints the 34 State and Union Territory rows of the expected names, in the
  expected order, and an India row.
  Every figure of every row lies inside the uncertainty bound printed with the figure.
  The 34 State and Union Territory counts of people living with HIV, of new infections and of
  AIDS-related deaths add up to the India count exactly (2,561,161, 64,465 and 32,162).
  The two versions print the same figures and bounds in every row.
  Table 2.1 of R_1 prints the India figures of Table 2.2 in lakh and thousand, 25.61 lakh
  (21.89 to 30.67) people living with HIV, 64.47 thousand (42.96 to 105.11) new infections,
  32.16 thousand (21.47 to 49.95) AIDS-related deaths and an adult prevalence of 0.20 per cent
  (0.17 to 0.24).

What the connector emits. For 2024, plhiv, new_infections and aids_deaths as counts and
hiv_prevalence_15_49 as a percentage, age group and sex "all", with the uncertainty bound in
value_lower and value_upper, for India (admin1 empty) and for the 34 States and Union
Territories in admin1 (140 rows). Every figure is carried as published. The national row is
the India row of Table 2.2 and never a sum of admin1 rows (ruling R14 of
research/rulings_2026-10-15.md), and the State and Union Territory bounds never add up to the
India bound.

Admin1 names. Table 2.2 abbreviates three names, written out in admin1. "A&N Islands" is the
Andaman and Nicobar Islands, "DNH&DD" is Dadra and Nagar Haveli and Daman and Diu, and the
shared row of Jammu and Kashmir and Ladakh takes the DHS name "Jammu, Kashmir & Ladakh". Delhi
keeps the NACO name, where DHS writes "New Delhi".

One round. Every Sankalak edition prints the latest round of the India HIV Estimates, and
Sankalak says the latest round replaces the earlier rounds because every round updates the
modelling tools. The connector reads one round, and an earlier edition, which would put
another round of the same years beside the 2025 round, is not read.

Not carried. The incidence per 1,000 uninfected population, the AIDS deaths per 1,00,000
population, the declines since 2010, the incidence-prevalence ratio (IPR) and the
incidence-mortality ratio (IMR), which the panel has no id for.

Source type. modelled_estimate, the Spectrum estimates of NACO. UNAIDS publishes the India
estimates NACO submits, and the AIDSinfo figures for India of 2024 equal the Table 2.2 India
figures rounded to two significant figures (ruling R44).
"""
from __future__ import annotations

import hashlib
import logging
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_SITE = "https://naco.mohfw.gov.in"
_PAGE = _SITE + "/sankalak/"
# version: (file path, local name, size and sha256 prefix of the copy read on 21 October 2026)
_FILES = {
    "R_1": ("/wp-content/uploads/2026/08/Sankalak-Booklet_Seventh-Edition_R_1.pdf",
            "in_naco_sankalak7_r1.pdf", 26_851_772, "ddccf701207f"),
    "January": ("/wp-content/uploads/2026/06/Sankalak-Booklet_Seventh-Edition-As-per-NACO-"
                "website-as-on-30.01.2026.pdf", "in_naco_sankalak7_jan.pdf", 9_727_542,
                "6accef6c8b66"),
}
_YEAR = 2024
_HEADING = re.compile(r"^Table 2\.2\. State/UT-wise HIV prevalence, incidence, mortality, "
                      r"PLHIV Size, IPR and IMR, (\d{4})$")
_COLUMNS = ("Adult (15-49", "PLHIV Size", "New HIV Infection", "Annual AIDS", "Related Deaths")
_T21_HEADING = "Table 2.1. Overview of HIV epidemic: Global, Asia and the Pacific and India, 2024"
# Table 2.2 label: admin1 name, in the order of the table
_NAMES = (
    ("A&N Islands", "Andaman and Nicobar Islands"),
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chandigarh", "Chandigarh"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("DNH&DD", "Dadra and Nagar Haveli and Daman and Diu"),
    ("Delhi", "Delhi"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jammu & Kashmir Ladakh", "Jammu, Kashmir & Ladakh"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Puducherry", "Puducherry"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("West Bengal", "West Bengal"),
)
_NUM = r"-?\d+(?:\.\d+)?"
_EST = rf"({_NUM}) \(({_NUM})-({_NUM})\)"
_ROW = re.compile(rf"^(?:(?P<name>[A-Za-z&][A-Za-z& ]*?) )?{_EST} {_EST} {_EST} {_EST} "
                  rf"({_NUM}) ({_NUM}) (?:{_EST} )?{_EST} ({_NUM}) ({_NUM})$")
_FRAG_OPEN = re.compile(rf"^({_NUM}) \(({_NUM})-$")
_FRAG_CLOSE = re.compile(rf"^({_NUM})\)$")
# measure: (indicator id, unit, Table 2.2 column, code)
_CARRIED = (
    ("prevalence", "hiv_prevalence_15_49", "percent",
     "Adult (15-49 years) HIV Prevalence (%)"),
    ("plhiv", "plhiv", "count", "PLHIV Size"),
    ("new_infections", "new_infections", "count", "New HIV Infection"),
    ("aids_deaths", "aids_deaths", "count", "Annual AIDS Related Deaths"),
)
_MEASURES = ("prevalence", "plhiv", "incidence", "new_infections", "death_rate", "aids_deaths")

_RECONCILE = ("UNAIDS publishes the India estimates NACO submits, and the AIDSinfo India figures "
              "of 2024 equal the Table 2.2 India figures rounded to two significant figures, so "
              "a comparison with unaids_aidsinfo, unicef_hiv, who_gho or world_bank compares two "
              "publications of one estimate (ruling R44)")
_AGG_WARNING = ("Take the national figure from the admin1 empty row, never from a sum of admin1 "
                "rows (ruling R14). The admin1 counts of Table 2.2 add up to the India count, "
                "and the admin1 bounds never add up to the India bound")
_NOT_CARRIED = ("the incidence per 1,000 uninfected population, the AIDS deaths per 1,00,000 "
                "population, the declines since 2010, the IPR and the IMR")

Estimate = Tuple[float, float, float]


def _lines(text: str) -> List[str]:
    return [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]


def rotated_lines(page) -> List[str]:
    """The text lines of a page rotated a quarter turn anticlockwise. Every line of the rotated
    text is one column of characters at one x position, read from the page bottom upwards."""
    chars = sorted((c for c in page.chars if not c.get("upright")), key=lambda c: c["x0"])
    groups: List[List[dict]] = []
    for c in chars:
        if groups and c["x0"] - groups[-1][-1]["x0"] <= 2.0:
            groups[-1].append(c)
        else:
            groups.append([c])
    out = []
    for group in groups:
        parts, last = [], None
        for c in sorted(group, key=lambda c: -c["bottom"]):
            y = page.height - c["bottom"]
            if last is not None and y - last > 2.5:
                parts.append(" ")
            parts.append(c["text"])
            last = y + (c["bottom"] - c["top"])
        out.append(re.sub(r"\s+", " ", "".join(parts)).strip())
    return out


def _est(groups: Tuple[Optional[str], ...]) -> Estimate:
    return tuple(float(g) for g in groups)  # type: ignore[return-value]


def parse_table(lines: List[str], version: str) -> Dict[str, Dict[str, Optional[Estimate]]]:
    """Table 2.2 of one version, as {Table 2.2 label: {measure: (value, lower, upper)}}, with the
    India row under "India", after the gates of the module docstring which concern a single
    version. Raises ValueError when any gate fails."""
    heads = [i for i, ln in enumerate(lines) if _HEADING.match(ln)]
    if len(heads) != 1:
        raise ValueError(f"the {version} version prints the Table 2.2 heading {len(heads)} "
                         f"times outside the contents, expected once")
    year = int(_HEADING.match(lines[heads[0]]).group(1))
    if year != _YEAR:
        raise ValueError(f"Table 2.2 of the {version} version is for {year}, expected {_YEAR}")
    body = lines[heads[0] + 1:]
    first = next((i for i, ln in enumerate(body) if _ROW.match(ln)), None)
    if first is None:
        raise ValueError(f"Table 2.2 of the {version} version holds no row")
    header = " ".join(body[:first])
    absent = [col for col in _COLUMNS if col not in header]
    if absent:
        raise ValueError(f"the Table 2.2 header of the {version} version does not name the "
                         f"columns {absent}")
    rows: Dict[str, Dict[str, Optional[Estimate]]] = {}
    order: List[str] = []
    i = first
    while i < len(body):
        ln = body[i]
        m = _ROW.match(ln)
        name_only = not re.search(r"\d", ln)
        if name_only and i + 2 < len(body) and _ROW.match(body[i + 1]) \
                and not _ROW.match(body[i + 1]).group("name") and not re.search(r"\d", body[i + 2]):
            label, m, step = f"{ln} {body[i + 2]}", _ROW.match(body[i + 1]), 3
        elif m and m.group("name"):
            label, step = m.group("name"), 1
        elif _FRAG_OPEN.match(ln) and i + 2 < len(body) and _ROW.match(body[i + 1]) \
                and _FRAG_CLOSE.match(body[i + 2]):
            m = _ROW.match(body[i + 1])
            label, step = m.group("name"), 3
        else:
            raise ValueError(f"Table 2.2 of the {version} version holds a line no row reading "
                             f"explains, {ln[:80]!r}")
        if not label:
            raise ValueError(f"Table 2.2 of the {version} version holds a row with no name")
        g = m.groups()[1:]
        measures: Dict[str, Optional[Estimate]] = {
            "prevalence": _est(g[0:3]), "plhiv": _est(g[3:6]), "incidence": _est(g[6:9]),
            "new_infections": _est(g[9:12]), "aids_deaths": _est(g[17:20]),
        }
        if g[14] is not None:
            measures["death_rate"] = _est(g[14:17])
        elif step == 3 and _FRAG_OPEN.match(ln):
            o, c = _FRAG_OPEN.match(ln), _FRAG_CLOSE.match(body[i + 2])
            measures["death_rate"] = (float(o.group(1)), float(o.group(2)), float(c.group(1)))
        else:
            raise ValueError(f"the {label} row of the {version} version has no AIDS deaths per "
                             f"1,00,000 population")
        measures["declines_and_ratios"] = (float(g[12]), float(g[13]), float(g[20]),
                                           float(g[21]))  # type: ignore[assignment]
        for measure in _MEASURES:
            value, lower, upper = measures[measure]
            if not lower <= value <= upper:
                raise ValueError(f"the {label} {measure} of the {version} version, {value}, lies "
                                 f"outside the printed bound {lower} to {upper}")
        rows[label] = measures
        order.append(label)
        i += step
        if label == "India":
            break
    expected = [label for label, _ in _NAMES] + ["India"]
    if order != expected:
        raise ValueError(f"Table 2.2 of the {version} version prints the rows {order}, expected "
                         f"{expected}")
    return rows


def _rounded(x: float, places: str) -> str:
    return str(Decimal(repr(x)).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def check_table_2_1(text: str, india: Dict[str, Optional[Estimate]]) -> None:
    """Raises ValueError unless Table 2.1 of R_1 prints the India figures of Table 2.2 in lakh
    and thousand."""
    flat = re.sub(r"UB:\s*", "UB:", re.sub(r"\s+", " ", text))
    at = flat.find(_T21_HEADING + " Indicator")
    if at < 0:
        raise ValueError("R_1 does not print Table 2.1 outside the contents")
    flat = flat[at:at + 3000]
    lakh = [_rounded(x / 1e5, "0.01") for x in india["plhiv"]]
    ni = [_rounded(x / 1e3, "0.01") for x in india["new_infections"]]
    de = [_rounded(x / 1e3, "0.01") for x in india["aids_deaths"]]
    pr = [_rounded(x, "0.01") for x in india["prevalence"]]
    wanted = [f"{lakh[0]} lakh (UB:{lakh[1]}-{lakh[2]})", f"{ni[0]} thousand",
              f"(UB:{ni[1]}-{ni[2]})", f"{de[0]} thousand", f"(UB:{de[1]}-{de[2]})",
              f"{pr[0]}% (UB:{pr[1]}-{pr[2]})"]
    missing = [w for w in wanted if w not in flat]
    if missing:
        raise ValueError(f"Table 2.1 of R_1 does not print {missing}, the India figures of "
                         f"Table 2.2")


def check_sums(rows: Dict[str, Dict[str, Optional[Estimate]]]) -> None:
    """Raises ValueError unless the State and Union Territory counts add up to the India count
    for people living with HIV, new infections and AIDS-related deaths."""
    for measure in ("plhiv", "new_infections", "aids_deaths"):
        total = sum(rows[label][measure][0] for label, _ in _NAMES)
        if total != rows["India"][measure][0]:
            raise ValueError(f"the State and Union Territory {measure} counts add up to {total}, "
                             f"the India row prints {rows['India'][measure][0]}")


def check_versions(r1: Dict[str, Dict[str, Optional[Estimate]]],
                   jan: Dict[str, Dict[str, Optional[Estimate]]]) -> None:
    """Raises ValueError unless the two versions print the same figures in every row."""
    for label in r1:
        if r1[label] != jan.get(label):
            raise ValueError(f"the {label} row of R_1 differs from the {label} row of the "
                             f"January version")


class IndiaNACOConnector(BaseConnector):
    """India HIV Estimates 2025 by State and Union Territory, Table 2.2 of Sankalak 2025."""

    source_id = "in_naco"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = ("National AIDS Control Organisation of India, Sankalak 2025 (seventh "
                   "edition), Table 2.2, India HIV Estimates 2025, people living with HIV, new "
                   "infections, AIDS-related deaths and adult prevalence for 2024, national and "
                   "34 States and Union Territories (to-source).")
    country = "IND"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/in_naco", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, version: str) -> Path:
        """Local copy of the `version` file, downloading only if not cached."""
        file_path, name, size, prefix = _FILES[version]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / name
        if path.exists():
            log.info("in_naco: using cached %s", path)
        else:
            blob = self._request("GET", _SITE + file_path).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_SITE + file_path} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("in_naco: downloaded the %s version (%d bytes) -> %s", version, len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (size, prefix):
            log.info("in_naco: the %s version matches the copy read on 21 October 2026 (sha256 "
                     "%s)", version, digest[:12])
        else:
            log.warning("in_naco: the %s version differs from the copy read on 21 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s), and the gates still run",
                        version, len(blob), digest[:12], size, prefix)
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
        if not start_year <= _YEAR <= end_year:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("in_naco: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            paths = {version: self._pdf_path(version) for version in _FILES}
        except Exception as exc:
            log.warning("in_naco: a version could not be fetched (%s)", exc)
            return
        try:
            with pdfplumber.open(str(paths["R_1"])) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            hits = [n for n, text in enumerate(pages)
                    if any(_HEADING.match(ln) for ln in _lines(text))]
            if len(hits) != 1:
                raise ValueError(f"R_1 prints the Table 2.2 heading on {len(hits)} pages, "
                                 f"expected one")
            r1 = parse_table(_lines("\n".join(pages)), "R_1")
            check_table_2_1("\n".join(pages), r1["India"])
            check_sums(r1)
            with pdfplumber.open(str(paths["January"])) as pdf:
                if hits[0] >= len(pdf.pages):
                    raise ValueError("the January version is shorter than R_1")
                jan = parse_table(rotated_lines(pdf.pages[hits[0]]), "January")
            check_versions(r1, jan)
        except Exception as exc:
            log.warning("in_naco: Table 2.2 failed a gate (%s), no row emitted", exc)
            return
        names = dict(_NAMES)
        names["India"] = ""
        emitted = 0
        for label, measures in r1.items():
            admin1 = names[label]
            for measure, indicator, unit, column in _CARRIED:
                value, lower, upper = measures[measure]
                extra = {
                    "estimate_round": "India HIV Estimates 2025",
                    "table": (f"Sankalak: Status of National AIDS & STD Response (2025), Table "
                              f"2.2, column {column}, row {label}"),
                    "cross_check": ("the January version linked from " + _PAGE + " ("
                                    + _SITE + _FILES["January"][0] + ") prints the same "
                                    "figures and bounds in every row of Table 2.2"),
                    "reconcile_with": _RECONCILE,
                    "not_carried": _NOT_CARRIED,
                }
                if admin1:
                    extra["aggregation_warning"] = _AGG_WARNING
                    if label != admin1:
                        extra["table_label"] = label
                emitted += 1
                yield self.make_row(
                    country_iso3="IND", country_name="India", admin1=admin1,
                    indicator_id=indicator, year=_YEAR, value=value,
                    value_lower=lower, value_upper=upper, unit=unit,
                    population_group=POP_ALL, sex=SEX_ALL, age_group=AGE_ALL,
                    source_url=_SITE + _FILES["R_1"][0],
                    source_indicator_code=f"naco:sankalak7:table_2_2:{indicator}",
                    extra=extra,
                )
        log.info("in_naco: Sankalak 2025 Table 2.2, emitted %d rows", emitted)
