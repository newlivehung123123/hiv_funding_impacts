"""
The health workers and other staff PEPFAR paid for in fiscal year 2025, by country, from the
human resources for health inventory.

`HRH_Inventory_Public_Dataset` lists the staff whose pay PEPFAR's implementing partners reported
in the annual human resources for health inventory, one row per operating unit, country, staff
category, cadre, programme, sub-programme and interaction type. The file holds 2,974 rows,
1,223,427,353 dollars of spend, 274,456 in the `Individual Count` column and 175,844.14 full-time
equivalents, all in fiscal year 2025, over 33 operating units and 57 names in the country column.
Partners complete the inventory in the same return as expenditure reporting, and the Financial
Classifications Reference Guide asks partners to convert currency the same way in the inventory
and in the expenditure report (page 16 of the guide dated 16 April 2025). No other source in the
panel counts PEPFAR-funded staff, so the connector reconciles against no series already in the
panel and is checked against the partner file instead, under the last heading below.

The connector emits three series.

    pepfar_hrh_spend                  `Actual Annual Spend` summed over every row of the
                                      country, in nominal dollars
    pepfar_hrh_fte                    `Annual Full Time Equivalent` summed over every row of the
                                      country
    pepfar_hrh_fte_service_delivery   `Annual Full Time Equivalent` summed over the rows whose
                                      `Interaction Type` is `Service Delivery`

The service-delivery series is part of the full-time-equivalent series and must never be added to
the full-time-equivalent series.

THE FILE HOLDS ONE YEAR, AND THE YEAR SPANS THE FREEZE

Every row carries fiscal year 2025, which runs from October 2024 to September 2025 and so contains
the freeze of January 2025. A single year cannot show a change, and the file cannot separate the
staff paid before the freeze from the staff paid after the freeze. The series give the level of
PEPFAR-funded staffing in the year of the cut. A later release carrying a second year would let
the series show a change, and the connector reads every year the file carries.

WHAT THE STAFF CATEGORIES MEAN

The file sorts staff into three categories, `HCW: Clinical`, `HCW: Ancillary` and `Other Staff`.
The guide classifies a position by the employment terms of the PEPFAR-funded post and not by
the worker's qualification, so a qualified nurse employed as a manager counts as other staff
(page 65 of the guide). Other staff hold 63.9 per cent of the spend, clinical workers 22.7 per
cent and ancillary workers 13.4 per cent. In full-time equivalents the order changes, with 82,262
ancillary, 47,634 other staff and 45,948 clinical. Service Delivery rows hold 36.2 per cent of the
spend and 128,306 full-time equivalents, and Non Service Delivery rows hold 47,538. Every row
under the programmes ASP and PM is Non Service Delivery, and other staff fall almost entirely
under Non Service Delivery, in 1,730 rows against 26. Every row carries the split by category,
programme and interaction type in `extra`, and the full-time-equivalent rows also carry the split
by cadre.

HEADCOUNT IS NOT EMITTED, BECAUSE ONE PERSON MAY SIT ON SEVERAL ROWS

The file splits staff by cadre, programme, sub-programme and interaction type. The guide defers
the rules of the inventory to an HRH Inventory Handbook, which is not on disk, and the guide does
not say whether a person whose time is split between two programmes appears on two rows. The
full-time equivalents on a row never exceed the row's `Individual Count`, and the ratio of the
two has a median of 0.664 and a tenth percentile of 0.11. A person split over several rows would
produce low ratios, and so would part-time staff, and the file cannot tell the two apart. A
full-time-equivalent total adds correctly across rows in either case. A total of `Individual
Count` adds correctly only if no person appears on two rows, so the headcount rides in
`extra.individual_count` with a warning in `extra.individual_count_warning` and enters no
indicator.

ONE COUNTRY'S INVENTORY IS TOO SMALL TO BE COMPLETE, AND IS WITHHELD

Ukraine carries one row in the file, `IM Program Management` under Other Staff, with 766,678.95
dollars of spend, 11 people and 0.21 full-time equivalents. The partner file records 40,722,026
dollars of PEPFAR expenditure in Ukraine in 2025, so the inventory accounts for 1.9 per cent of
the expenditure. Among the other 54 countries the lowest share is 27.5 per cent, for Nigeria,
followed by the Democratic Republic of the Congo at 28.9 per cent. Emitted, Ukraine would read as
PEPFAR paying almost no staff in Ukraine, when the file lists one row of programme managers. A
country-year is withheld from every series when the country's inventory spend is below 10 per
cent of the partner file's `Total Expenditure` for the same country and year, and the log names
every withheld country-year with the share. Any threshold between 2 and 27 per cent withholds
the same country in the current file. The check needs the partner file, and when the partner
file is absent the log says that no country-year could be checked and nothing is withheld.

A rule withholding every country with no Service Delivery row would be the wrong rule. Cambodia
carries 13 rows and 73.14 full-time equivalents, all of them other staff under ASP and PM, which
are systems work above the level of the clinic, and the inventory spend is 54.9 per cent of
Cambodia's expenditure. Cambodia's service-delivery series is emitted as zero, marked
`extra.no_service_delivery_rows`, because an inventory listing staff and no service-delivery staff
settles the zero.

FORTY ROWS NAME NO COUNTRY, AND ARE DROPPED

Thirty-one rows under the Central Asia Region name `Central Asia Region` in the country column,
656,618 dollars in all. Nine rows read `Data not provided at this geographic level`, one under the
Central and South America Region, five under West Africa Region 1 and three under West Africa
Region 2. The 40 rows hold 738,825 dollars, 282 in the headcount column and 73.6 full-time
equivalents. A country-year panel has nowhere to put the rows, so the rows are dropped and counted
in the log and not spread over a region. The staff on the dropped rows may work in the
countries of the operating unit, so every country under an operating unit with a dropped row says
in `extra.coverage_warning` that the country's figures may be a floor.

SEVEN OPERATING UNITS COVER MORE THAN ONE COUNTRY

An operating unit counts as regional when the operating unit covers more than one country in the
file, which is a property of the file and not of the operating unit's name. The seven regional
operating units are the Caribbean, Central Asia, Central and South America, Pacific, South and
Southeast Asia, West Africa Region 1 and West Africa Region 2, holding 788 rows and 74,572,975
dollars, the 40 rows naming no country included. The 29 countries under the seven regional
operating units carry `extra.funded_through_regional_ou`, and every row names the country's
operating unit in `extra.operating_unit`. Nineteen of the 29 countries sit under an operating unit
with a dropped row and carry the `coverage_warning` described above.

SMALL ROWS WITH LARGE SPEND PER FULL-TIME EQUIVALENT ARE KEPT

Thirty rows carry no full-time equivalents and 23,580 dollars of spend. Eight rows carry more than
500,000 dollars per full-time equivalent, 1,179,430 dollars in all, and no one of the eight
carries more than 0.38 full-time equivalents. Ukraine's single row is one of the eight. The rows
are kept, because a small fraction of a post can carry a stipend or a contract that the file does
not break down, and the log counts both groups on every run.

CHECKED AGAINST THE PARTNER FILE

Every country-year's inventory spend is compared with the partner file's `Total Expenditure` for
the same country-year, with partner rows placed by the `Country` column wherever the `Country`
column and the `ISO3` column name different countries (ACCESS_LADDER §9t). Inventory spend above
the country's whole expenditure would be a defect in one file or the other, and the log names any
country-year where the inventory spend is larger. Over the 54 countries emitted for 2025 the
share has a median of 0.515 and an overall value of 0.444, the highest share is Jamaica's at
0.762, and no country's inventory spend exceeds the country's expenditure. Every country with
PEPFAR expenditure in the partner file for 2025 has rows in the inventory. Every spend row
carries the partner file's figure in `extra.partner_file_expenditure` and the share in
`extra.share_of_partner_file_expenditure`.

The partner file's `Human Resources for Health` column measures a different quantity and must not
be compared with the inventory. The guide defines the programme area as above-site work to
strengthen the health workforce, such as pre-service training and national workforce planning
(pages 50 and 51 of the guide). Over the partner rows placed in a country, the column totals
19,829,631 dollars in 2025 and is filled for 39 of the 54 countries emitted, and the inventory
spend is a median 40 times the column's value for the same country. The log repeats the ratio on
every run.

TAGGING: PEPFAR-funded staff reported by implementing partners, not the national health
workforce. Spend in nominal USD, not deflated. source_type = expenditure_account.
"""
from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

SPEND = "pepfar_hrh_spend"
FTE = "pepfar_hrh_fte"
FTE_SD = "pepfar_hrh_fte_service_delivery"

# The value of `Interaction Type` that the service-delivery series counts. The other value in the
# file is `Non Service Delivery`, and a value new to the file is logged and not guessed at.
SERVICE_DELIVERY = "service delivery"
INTERACTION_TYPES = (SERVICE_DELIVERY, "non service delivery")

# A country-year whose inventory spend falls below this share of the partner file's expenditure
# for the same country-year is withheld. In the current file Ukraine sits at 0.019 and the next
# lowest country, Nigeria, at 0.275.
WITHHOLD_SHARE = 0.10

# rows above this spend per full-time equivalent are counted in the log
SPEND_PER_FTE_FLAG = 500_000.0

SOURCE_URL = "https://data.pepfar.gov/datasets"

INTERPRETATION = (
    "Staff whose pay PEPFAR's implementing partners reported in the human resources for health "
    "inventory for the fiscal year, summed over every staff category, cadre, programme and "
    "interaction type in the country. PEPFAR-funded staff only, not the national health "
    "workforce. Spend in nominal USD. The file holds fiscal year 2025 only, which runs from "
    "October 2024 to September 2025 and contains the freeze of January 2025, so no figure here "
    "shows a change, and the file cannot separate staff paid before the freeze from staff paid "
    "after the freeze. A post is classified by the employment terms of the PEPFAR-funded "
    "position and not by qualification, so a nurse employed as a manager counts as other "
    "staff. The service-delivery series is part of the full-time-equivalent series and must "
    "never be added to the full-time-equivalent series. `individual_count` is not a count of "
    "people, because one person whose time is split between programmes may appear on several "
    "rows. Do not compare the spend with the partner file's `Human Resources for Health` "
    "column, which measures above-site work to strengthen the workforce and not staff pay."
)

HEADCOUNT_WARNING = (
    "The sum of `Individual Count` over the rows of the country. The file splits staff by cadre, "
    "programme, sub-programme and interaction type, and the guide on disk does not say whether "
    "a person whose time is split between two programmes appears on two rows, so the sum may "
    "count one person more than once. Use the full-time equivalents, which add correctly "
    "across rows either way."
)


def _num(cell) -> float:
    """Blank means nothing on this row. The current file has no blank in any of the three
    numeric columns."""
    if cell is None:
        return 0.0
    s = str(cell).strip().replace(",", "").replace("$", "")
    if s in ("", "nan", "NaN", "NA", "N/A", ".", "..."):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _ci(cols: List[str], *names: str) -> Optional[str]:
    low = {c.lower().strip(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    return None


def _pct(part: float, whole: float) -> float:
    return (part / whole * 100) if whole else 0.0


def _rows(n: int) -> str:
    return f"{n:,} row" + ("" if n == 1 else "s")


def _and(items: List[str]) -> str:
    items = list(items)
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def _desc(d: Dict[str, float]) -> Dict[str, float]:
    return {k: round(float(v), 2) for k, v in sorted(d.items(), key=lambda kv: -kv[1])}


class PEPFARHRHConnector(BaseConnector):
    source_id = "pepfar_hrh"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("PEPFAR-funded staff by country from the human resources for health "
                   "inventory, fiscal year 2025, as spend, full-time equivalents and "
                   "service-delivery full-time equivalents.")

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _read_frame(self) -> Optional[pd.DataFrame]:
        if not self.raw_dir.exists():
            log.warning("pepfar_hrh: %s does not exist. Download HRH_Inventory_Public_Dataset "
                        "from data.pepfar.gov", self.raw_dir)
            return None

        candidates = [p for p in sorted(self.raw_dir.glob("*.zip"))
                      if "hrh" in p.name.lower() and "inventory" in p.name.lower()]
        if not candidates:
            log.warning("pepfar_hrh: no HRH_Inventory_Public_Dataset zip in %s", self.raw_dir)
            return None

        for path in candidates:
            try:
                with zipfile.ZipFile(path) as z:
                    members = [m for m in z.namelist() if m.lower().endswith(".txt")]
                    if not members:
                        continue
                    with z.open(members[0]) as fh:
                        df = pd.read_csv(fh, sep="\t", dtype=str, keep_default_na=False,
                                         on_bad_lines="skip", low_memory=False)
                    log.info("pepfar_hrh: read %s from %s. Not read: %s", members[0], path.name,
                             [m for m in z.namelist() if m != members[0]] or "nothing")
                    return df
            except Exception as exc:
                log.warning("pepfar_hrh: error reading %s: %s", path.name, exc)
        return None

    def _read_partner(self) -> Optional[pd.DataFrame]:
        """The columns of the partner-level budget file that the withholding rule and the checks
        need, and the `Country` column, which decides the country of a row wherever the `ISO3`
        column names a different country. Nothing in the partner file is emitted."""
        paths = [p for p in sorted(self.raw_dir.glob("*.zip"))
                 if "public_partner" in p.name.lower() and "budget" in p.name.lower()]
        need = {"iso3", "implementation year", "total expenditure"}
        want = need | {"country", "human resources for health"}
        for path in paths:
            try:
                with zipfile.ZipFile(path) as z:
                    members = [m for m in z.namelist() if m.lower().endswith(".txt")]
                    if not members:
                        continue
                    with z.open(members[0]) as fh:
                        df = pd.read_csv(fh, sep="\t", dtype=str, keep_default_na=False,
                                         usecols=lambda c: c.lower().strip() in want,
                                         on_bad_lines="skip", low_memory=False)
                if need <= {c.lower().strip() for c in df.columns}:
                    return df
            except Exception as exc:
                log.warning("pepfar_hrh: error reading %s for the check against the partner "
                            "file: %s", path.name, exc)
        return None

    def _partner_by_country_year(self) -> Optional[pd.DataFrame]:
        """(iso3, year) -> the partner file's expenditure and `Human Resources for Health`
        column, with rows placed as pepfar_expenditure places the rows, by the `Country` column
        wherever the `ISO3` column names a different country (ACCESS_LADDER §9t)."""
        p = self._read_partner()
        if p is None or p.empty:
            return None
        cols = list(p.columns)
        iso_of = {c: to_iso3(c) for c in p[_ci(cols, "iso3")].unique()}
        iso3 = p[_ci(cols, "iso3")].map(iso_of)
        cn = _ci(cols, "country")
        if cn:
            name_of = {c: to_iso3(c) for c in p[cn].unique()}
            iso3 = p[cn].map(name_of).where(iso3.notna()).fillna(iso3)
        hr = _ci(cols, "human resources for health")
        q = pd.DataFrame({
            "iso3": iso3,
            "year": pd.to_numeric(p[_ci(cols, "implementation year")].str[:4], errors="coerce"),
            "expenditure": p[_ci(cols, "total expenditure")].map(_num),
            "hr_column": p[hr].map(_num) if hr else 0.0,
        }).dropna(subset=["iso3", "year"])
        q["year"] = q["year"].astype(int)
        return q.groupby(["iso3", "year"])[["expenditure", "hr_column"]].sum()

    # -- emitting ---------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        df = self._read_frame()
        if df is None or df.empty:
            return

        cols = list(df.columns)
        need = {
            "ou": _ci(cols, "operating unit"),
            "country": _ci(cols, "country"),
            "category": _ci(cols, "category"),
            "cadre": _ci(cols, "cadre"),
            "programme": _ci(cols, "program"),
            "sub_programme": _ci(cols, "sub program"),
            "interaction": _ci(cols, "interaction type"),
            "year": _ci(cols, "fiscal year"),
            "spend": _ci(cols, "actual annual spend"),
            "count": _ci(cols, "individual count"),
            "fte": _ci(cols, "annual full time equivalent"),
        }
        missing = [k for k, c in need.items() if c is None]
        if missing:
            log.warning("pepfar_hrh: file lacks the columns %s, so the file is not this dataset "
                        "and nothing is emitted", ", ".join(missing))
            return

        f = pd.DataFrame({k: df[c].astype(str).str.strip() for k, c in need.items()})
        f["year"] = pd.to_numeric(f["year"].str[:4], errors="coerce")
        for k in ("spend", "count", "fte"):
            f[k] = df[need[k]].map(_num)
        f["interaction_l"] = f["interaction"].str.lower()
        iso_of = {c: to_iso3(c) for c in f["country"].unique()}
        f["iso3"] = f["country"].map(iso_of)

        no_year = int(f["year"].isna().sum())
        if no_year:
            log.warning("pepfar_hrh: %d rows carry no readable Fiscal Year and are dropped",
                        no_year)
        f = f[f["year"].notna()].copy()
        f["year"] = f["year"].astype(int)
        f = f[(f["year"] >= start_year) & (f["year"] <= end_year)].copy()
        if f.empty:
            log.info("pepfar_hrh: no row falls inside %d-%d", start_year, end_year)
            return

        unknown = sorted(set(f["interaction_l"]) - set(INTERACTION_TYPES))
        if unknown:
            log.warning("pepfar_hrh: interaction types new to this connector (%s), counted in the "
                        "full-time-equivalent series and not in the service-delivery series "
                        "until someone decides where the types belong", ", ".join(unknown))

        partner = self._partner_by_country_year()

        # Every row falls in exactly one class, so no dollar is counted twice and the used and
        # discarded amounts sum to the file total over the years read.
        f["cls"] = "used"
        f.loc[f["iso3"].isna(), "cls"] = "no_iso3"
        withheld = self._withheld(f, partner)
        f.loc[(f["cls"] == "used")
              & pd.Series(list(zip(f["iso3"], f["year"])), index=f.index).isin(set(withheld)),
              "cls"] = "withheld"

        regional = self._regional(f)
        floors = self._floors(f, regional)
        agg = self._aggregate(f)

        self._report_discards(f, agg)
        self._report_withheld(withheld)
        self._report_regional(f, regional, floors)
        self._report_small_rows(f)
        self._report_headcount(f)
        self._report_no_service_delivery(agg)
        self._check_partner(agg, partner, withheld)

        yield from self._emit(agg, wanted, regional, floors, partner)

    # -- classifying ------------------------------------------------------------
    @staticmethod
    def _withheld(f: pd.DataFrame, partner: Optional[pd.DataFrame]) -> Dict[tuple, dict]:
        """Country-years whose inventory spend is below WITHHOLD_SHARE of the partner file's
        expenditure. An inventory that small lists a fraction of the staff PEPFAR paid for, and
        emitted it would read as PEPFAR paying almost no staff in the country."""
        if partner is None:
            log.warning("pepfar_hrh: no Public_Partner_Budgets_and_Expenditures zip in the "
                        "folder, so no country-year's inventory could be checked against the "
                        "country's expenditure and nothing is withheld")
            return {}
        used = f[f["cls"] == "used"]
        ours = used.groupby(["iso3", "year"]).agg(spend=("spend", "sum"), fte=("fte", "sum"),
                                                  count=("count", "sum"), rows=("spend", "size"))
        out: Dict[tuple, dict] = {}
        for (iso3, year), r in ours.iterrows():
            key = (iso3, int(year))
            if key not in partner.index:
                continue
            exp = float(partner.loc[key, "expenditure"])
            if exp > 0 and r["spend"] / exp < WITHHOLD_SHARE:
                out[key] = {"spend": float(r["spend"]), "fte": float(r["fte"]),
                            "count": float(r["count"]), "rows": int(r["rows"]),
                            "expenditure": exp, "share": float(r["spend"] / exp)}
        return out

    @staticmethod
    def _regional(f: pd.DataFrame) -> Dict[str, str]:
        """iso3 -> operating unit, for every country under an operating unit that covers more
        than one country in this file. Built over the whole file, because whether an operating
        unit is regional is a property of the file and not of the countries a run asks for."""
        named = f[f["iso3"].notna()]
        ou_countries = named.groupby("ou")["iso3"].agg(lambda s: set(s)).to_dict()
        out: Dict[str, str] = {}
        for ou, cs in ou_countries.items():
            if len(cs) > 1:
                for iso3 in cs:
                    out[iso3] = ou
        return out

    @staticmethod
    def _floors(f: pd.DataFrame, regional: Dict[str, str]) -> Dict[str, str]:
        """iso3 -> a sentence, for every country under an operating unit that also carries rows
        naming no country. The staff on those rows may work in the country, so the country's
        figures may be a floor."""
        dropped = f[f["cls"] == "no_iso3"]
        out: Dict[str, str] = {}
        for ou, g in dropped.groupby("ou"):
            names = _and([f"`{n}`" for n in sorted(g["country"].unique())])
            sentence = (f"The country's operating unit, {ou}, also carries {_rows(len(g))} "
                        f"naming {names} in place of a country, {g['spend'].sum():,.0f} USD and "
                        f"{g['fte'].sum():,.1f} full-time equivalents. The staff on those rows "
                        "may work in this country, so the country's figures may be a floor.")
            for iso3, unit in regional.items():
                if unit == ou:
                    out[iso3] = sentence
        return out

    @staticmethod
    def _aggregate(f: pd.DataFrame) -> Dict[tuple, dict]:
        """(iso3, year) -> the country-year over the used rows, built over every country in the
        file. The country filter applies at emission only."""
        agg: Dict[tuple, dict] = {}
        used = f[f["cls"] == "used"]
        for (iso3, year), g in used.groupby(["iso3", "year"]):
            sd = g[g["interaction_l"] == SERVICE_DELIVERY]
            agg[(iso3, int(year))] = {
                "name": g["country"].iloc[0],
                "ou": g["ou"].iloc[0],
                "rows": len(g),
                "spend": float(g["spend"].sum()),
                "fte": float(g["fte"].sum()),
                "count": float(g["count"].sum()),
                "sd_rows": len(sd),
                "sd_fte": float(sd["fte"].sum()),
                "sd_count": float(sd["count"].sum()),
                "zero_fte_rows": int((g["fte"] <= 0).sum()),
                "spend_by": {k: g.groupby(c)["spend"].sum().to_dict()
                             for k, c in (("category", "category"), ("programme", "programme"),
                                          ("interaction_type", "interaction"))},
                "fte_by": {k: g.groupby(c)["fte"].sum().to_dict()
                           for k, c in (("category", "category"), ("cadre", "cadre"),
                                        ("programme", "programme"),
                                        ("interaction_type", "interaction"))},
                "sd_fte_by": {k: sd.groupby(c)["fte"].sum().to_dict()
                              for k, c in (("category", "category"), ("cadre", "cadre"),
                                           ("programme", "programme"))},
            }
        return agg

    # -- reporting --------------------------------------------------------------
    @staticmethod
    def _report_discards(f: pd.DataFrame, agg: Dict[tuple, dict]) -> None:
        """One line, carrying what was used and every discard as a share of the whole file over
        the years read. The denominator is the whole file and not the countries a run asks for,
        because the rows naming no country can never be reached by a country filter."""
        whole = float(f["spend"].sum())
        by = f.groupby("cls")[["spend", "fte"]].sum()
        n = f.groupby("cls").size()

        def part(cls: str, label: str = "") -> str:
            usd = float(by["spend"].get(cls, 0.0))
            fte = float(by["fte"].get(cls, 0.0))
            return (f"{label}{_rows(int(n.get(cls, 0)))}, {usd:,.0f} USD "
                    f"({_pct(usd, whole):.4f}%) and {fte:,.2f} FTE")

        years = sorted(int(y) for y in f["year"].unique())
        log.info(
            "pepfar_hrh: %s, %s USD and %s FTE read for %s. Used %s over %d country-years. "
            "Discarded %s and %s. Shares are of the whole file's spend",
            _rows(len(f)), f"{whole:,.0f}", f"{f['fte'].sum():,.2f}",
            _and([str(y) for y in years]), part("used"), len(agg),
            part("no_iso3", "for naming no country "),
            part("withheld", "as withheld country-years "),
        )
        for (ou, name), g in f[f["cls"] == "no_iso3"].groupby(["ou", "country"]):
            log.info("pepfar_hrh: `%s` under %s maps to no ISO3, %s, %s USD, %s in the headcount "
                     "column and %s FTE", name or "(blank)", ou, _rows(len(g)),
                     f"{g['spend'].sum():,.0f}", f"{g['count'].sum():,.0f}",
                     f"{g['fte'].sum():,.2f}")

    @staticmethod
    def _report_withheld(withheld: Dict[tuple, dict]) -> None:
        for (iso3, year), w in sorted(withheld.items()):
            log.info(
                "pepfar_hrh: %s %d is withheld from every series. The inventory lists %s, %s USD, "
                "%s in the headcount column and %s FTE, which is %.3f of the %s USD of PEPFAR "
                "expenditure the partner file records for the country-year, below the %.2f "
                "threshold. Emitted, the country-year would read as PEPFAR paying almost no staff "
                "in the country",
                iso3, year, _rows(w["rows"]), f"{w['spend']:,.2f}", f"{w['count']:,.0f}",
                f"{w['fte']:,.2f}", w["share"], f"{w['expenditure']:,.0f}", WITHHOLD_SHARE,
            )

    @staticmethod
    def _report_regional(f: pd.DataFrame, regional: Dict[str, str],
                         floors: Dict[str, str]) -> None:
        ous = sorted(set(regional.values()))
        if not ous:
            return
        rows = f[f["ou"].isin(ous)]
        log.info("pepfar_hrh: %d operating units cover more than one country (%s), holding %s "
                 "and %s USD. The %d countries under the operating units carry "
                 "`funded_through_regional_ou`, and the %d countries under an operating unit with "
                 "a row naming no country carry a `coverage_warning` that the country's figures "
                 "may be a floor", len(ous), _and(ous), _rows(len(rows)),
                 f"{rows['spend'].sum():,.0f}", len(regional), len(floors))

    @staticmethod
    def _report_small_rows(f: pd.DataFrame) -> None:
        """Counted over the whole file, whatever class each row falls in."""
        zero = f[f["fte"] <= 0]
        big = f[(f["fte"] > 0) & (f["spend"] / f["fte"].where(f["fte"] > 0)
                                  > SPEND_PER_FTE_FLAG)]
        log.info("pepfar_hrh: %s carry no FTE and %s USD of spend, and %s carry more than %s USD "
                 "per FTE, %s USD in all, with at most %.2f FTE on any one row. The rows are kept, "
                 "because a small fraction of a post can carry a stipend or a contract that the "
                 "file does not break down",
                 _rows(len(zero)), f"{zero['spend'].sum():,.0f}", _rows(len(big)),
                 f"{SPEND_PER_FTE_FLAG:,.0f}", f"{big['spend'].sum():,.0f}",
                 float(big["fte"].max()) if len(big) else 0.0)

    @staticmethod
    def _report_headcount(f: pd.DataFrame) -> None:
        """The ratio of full-time equivalents to headcount on each row. A median well below one
        fits staff split over rows as well as part-time staff, and the file cannot tell the two
        apart, which is why the headcount enters no series."""
        r = f[f["count"] > 0]
        ratio = r["fte"] / r["count"]
        over = int((r["fte"] > r["count"] + 1e-9).sum())
        log.info("pepfar_hrh: the headcount column sums to %s and the FTE column to %s. FTE per "
                 "head has a median of %.3f and a tenth percentile of %.2f, and %d rows carry "
                 "more FTE than heads. One person whose time is split between programmes may sit "
                 "on several rows, so the headcount rides in `individual_count` and enters no "
                 "series", f"{f['count'].sum():,.0f}", f"{f['fte'].sum():,.2f}",
                 ratio.median(), ratio.quantile(0.1), over)

    @staticmethod
    def _report_no_service_delivery(agg: Dict[tuple, dict]) -> None:
        none = sorted(f"{i} {y} ({a['rows']} rows, {a['fte']:,.2f} FTE)"
                      for (i, y), a in agg.items() if a["sd_rows"] == 0)
        if none:
            log.info("pepfar_hrh: the inventory of %s lists staff and no Service Delivery row, so "
                     "the service-delivery series is emitted as zero with "
                     "`no_service_delivery_rows`", _and(none))

    # -- checking ---------------------------------------------------------------
    @staticmethod
    def _check_partner(agg: Dict[tuple, dict], partner: Optional[pd.DataFrame],
                       withheld: Dict[tuple, dict]) -> None:
        """Inventory spend against the partner file's `Total Expenditure` for the same
        country-year, over the country-years emitted. Inventory spend above the whole expenditure
        would be a defect in one file or the other. The partner file's `Human Resources for
        Health` column is reported beside the check to show, on every run, that the column
        measures something else."""
        if partner is None:
            log.info("pepfar_hrh: no partner file, so the check against expenditure was skipped")
            return
        keys = sorted(agg)
        ours = pd.DataFrame({"spend": [agg[k]["spend"] for k in keys]},
                            index=pd.MultiIndex.from_tuples(keys, names=["iso3", "year"]))
        both = ours.join(partner, how="inner")
        both = both[both["expenditure"] > 0]
        if both.empty:
            log.info("pepfar_hrh: the partner file shares no country-year with the inventory, so "
                     "the check against expenditure was skipped")
            return
        both["share"] = both["spend"] / both["expenditure"]
        top = both["share"].idxmax()
        low = both["share"].nsmallest(3)
        over = both[both["share"] > 1]
        log.info("pepfar_hrh: against the partner file's Total Expenditure, inventory spend over "
                 "%d country-years has a median share of %.3f and an overall share of %.3f, "
                 "highest in %s %d at %.3f and lowest in %s. %s",
                 len(both), both["share"].median(), both["spend"].sum() / both["expenditure"].sum(),
                 top[0], top[1], both["share"].max(),
                 _and([f"{i} {y} at {s:.3f}" for (i, y), s in low.items()]),
                 ("No country-year's inventory spend exceeds the country's expenditure"
                  if over.empty else "Inventory spend exceeds expenditure in " + _and(
                      [f"{i} {y} ({s:.2f})" for (i, y), s in over["share"].items()])))

        spent = partner[partner["expenditure"] > 0]
        years = set(both.index.get_level_values("year"))
        absent = sorted(f"{i} {y}" for i, y in spent.index
                        if y in years and (i, y) not in agg and (i, y) not in withheld)
        if absent:
            log.info("pepfar_hrh: %d country-years with PEPFAR expenditure in the partner file "
                     "have no used row in the inventory (%s)", len(absent), _and(absent))
        else:
            log.info("pepfar_hrh: every country-year with PEPFAR expenditure in the partner file "
                     "for %s has used rows in the inventory, withheld country-years aside",
                     _and([str(y) for y in sorted(years)]))

        hr = both[both["hr_column"] > 0]
        if not hr.empty:
            ratio = hr["spend"] / hr["hr_column"]
            yrs = sorted(years)
            total = partner.loc[partner.index.get_level_values("year").isin(yrs), "hr_column"]
            log.info("pepfar_hrh: the partner file's `Human Resources for Health` column totals %s "
                     "USD for %s, and inventory spend is a median %.0f times the column over the "
                     "%d country-years where the column is filled. The column measures above-site "
                     "work to strengthen the workforce, not staff pay, and is never compared with "
                     "the inventory", f"{total.sum():,.0f}", _and([str(y) for y in yrs]),
                     ratio.median(), len(hr))

    # -- composition ------------------------------------------------------------
    def _emit(self, agg: Dict[tuple, dict], wanted, regional: Dict[str, str],
              floors: Dict[str, str], partner: Optional[pd.DataFrame]) -> List[PanelRow]:
        rows: List[PanelRow] = []
        for (iso3, year), a in sorted(agg.items()):
            if wanted and iso3 not in wanted:
                continue
            base: Dict[str, object] = {
                "note": ("PEPFAR-funded staff from the human resources for health inventory, NOT "
                         "the national health workforce. Spend in nominal USD."),
                "grain": ("country within an operating unit, summed over staff category, cadre, "
                          "programme, sub-programme and interaction type, no mechanism or "
                          "funding-agency column in this file"),
                "interpretation": INTERPRETATION,
                "operating_unit": a["ou"],
                "inventory_rows": a["rows"],
            }
            if iso3 in regional:
                base["funded_through_regional_ou"] = True
                if iso3 in floors:
                    base["coverage_warning"] = floors[iso3]

            extra = dict(base)
            extra["by_category"] = _desc(a["spend_by"]["category"])
            extra["by_programme"] = _desc(a["spend_by"]["programme"])
            extra["by_interaction_type"] = _desc(a["spend_by"]["interaction_type"])
            if partner is not None and (iso3, year) in partner.index:
                exp = float(partner.loc[(iso3, year), "expenditure"])
                if exp > 0:
                    extra["partner_file_expenditure"] = exp
                    extra["share_of_partner_file_expenditure"] = round(a["spend"] / exp, 4)
            rows.append(self.make_row(
                country_iso3=iso3, country_name=a["name"], indicator_id=SPEND, year=year,
                value=a["spend"], unit="USD", source_url=SOURCE_URL,
                source_indicator_code="PEPFAR HRH Inventory, Actual Annual Spend",
                extra=extra,
            ))

            extra = dict(base)
            extra["by_category"] = _desc(a["fte_by"]["category"])
            extra["by_cadre"] = _desc(a["fte_by"]["cadre"])
            extra["by_programme"] = _desc(a["fte_by"]["programme"])
            extra["by_interaction_type"] = _desc(a["fte_by"]["interaction_type"])
            extra["individual_count"] = a["count"]
            extra["individual_count_warning"] = HEADCOUNT_WARNING
            if a["zero_fte_rows"]:
                extra["rows_without_fte"] = a["zero_fte_rows"]
            rows.append(self.make_row(
                country_iso3=iso3, country_name=a["name"], indicator_id=FTE, year=year,
                value=a["fte"], unit="count", source_url=SOURCE_URL,
                source_indicator_code="PEPFAR HRH Inventory, Annual Full Time Equivalent",
                extra=extra,
            ))

            extra = dict(base)
            if a["sd_rows"]:
                extra["by_category"] = _desc(a["sd_fte_by"]["category"])
                extra["by_cadre"] = _desc(a["sd_fte_by"]["cadre"])
                extra["by_programme"] = _desc(a["sd_fte_by"]["programme"])
                extra["individual_count"] = a["sd_count"]
                extra["individual_count_warning"] = HEADCOUNT_WARNING
            else:
                extra["no_service_delivery_rows"] = True
            rows.append(self.make_row(
                country_iso3=iso3, country_name=a["name"], indicator_id=FTE_SD, year=year,
                value=a["sd_fte"], unit="count", source_url=SOURCE_URL,
                source_indicator_code=("PEPFAR HRH Inventory, Annual Full Time Equivalent, "
                                       "Service Delivery"),
                extra=extra,
            ))

        emitted = {r.country_iso3 for r in rows}
        log.info("pepfar_hrh: emitted %d rows over %d countries", len(rows), len(emitted))
        return rows
