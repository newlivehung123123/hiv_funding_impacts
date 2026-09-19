"""
PEPFAR commodity procurement plans by country, from COP18 to COP24, which are the implementation
years 2019 to 2025.

`PEPFAR_OU_Commodities_Procurements` lists every commodity a Country Operational Plan sets out to
buy, one line per item, with the planned budget and the planned quantity. The file holds 8,902
lines and 5,537,274,918 dollars. The country column carries 55 names, and one of the 55 names is
a region rather than a country. No other source in the panel measures what PEPFAR planned to buy,
as distinct from what PEPFAR planned to spend in total, so the connector reconciles against no
series already in the panel and is checked against the partner file instead, under the last
heading below.

The connector emits four series, all in nominal dollars of planned budget.

    pepfar_commodity_budget   the like-for-like total defined under the headings below
    pepfar_arv_budget         the ARV major category, which includes PrEP from 2020
    pepfar_rtk_budget         the RTKs major category, which is rapid test kits, including
                              self-testing, recency testing and tests for conditions other
                              than HIV
    pepfar_lab_budget         the Laboratory major category

The ARV, RTK and Laboratory series are parts of the like-for-like total and must never be added
to the like-for-like total. Each category series covers the same country-years as the like-for-like
total, with a zero where the plan lists nothing in the category, as set out below.

EVERY PLAN IN THIS FILE WAS DRAWN UP BEFORE THE JANUARY 2025 FREEZE

COP24 sets the plan for implementation year 2025 and was written in 2024. The file therefore
cannot show the 2025 cut. The file shows how much each country was set to receive going into
2025, and the trend in plans before the freeze.

The number of countries with a plan changes from year to year, so a trend is read over the same
countries at both ends. Over the 23 countries with a plan in both 2019 and 2025, the like-for-like
total falls from 861.8m dollars to 542.3m, and ARV falls from 506.7m to 220.2m. Over the 34
countries with a plan in both 2020 and 2025, the like-for-like total falls from 827.8m to 549.5m,
and ARV falls from 487.9m to 223.6m. Planned ARV spending was therefore falling well before the
freeze. The file cannot separate a fall in the number of people supplied with ARVs from a fall in
the price of a regimen, or from another funder, such as the Global Fund or a national government,
taking over part of the purchase. Across all countries, Laboratory holds between 199.6m and
255.2m in every year.

QUANTITIES ARE NOT EMITTED, BECAUSE THE UNIT A QUANTITY COUNTS CHANGES BETWEEN YEARS

The file does not name the unit of `Item Quantity`. The same country buying the same item in
two consecutive years should pay a similar price per unit, and in the file the price per unit
often moves tenfold or more between consecutive years. In the current file, 260 of 1,694 pairs of
the same item in the same country in consecutive years move more than tenfold, including 161 of
630 Laboratory pairs and 66 of 272 RTK pairs, against two of 329 ARV pairs. The runtime log
repeats the count on every run. The name of a single regimen also changes across years.
Tenofovir, lamivudine and dolutegravir in one tablet appears under at least four spellings, in
packs of 30, 90 and 180 tablets. A quantity series built from the `Item Quantity` column would
record changes of unit as changes in supply, so only the budget is emitted.

FOUR COST CATEGORIES APPEAR IN SOME YEARS ONLY, AND ENTER NO INDICATOR

In-Country Logistics carries budget from 2023, Quality Assurance from 2023 and Procurement
Management from 2024. A major category labelled `Not Specified` carries budget in 2019 only, as
distribution and warehousing lines. In-Country Logistics, Quality Assurance, Procurement
Management and `Not Specified`, called the cost categories here, together hold 223,952,936
dollars in 794 lines, or 4.04 per cent of the file. Before 2023 the cost of moving, checking and
managing goods either sat somewhere the file does not show or sat inside the item lines, and the
file does not say where the cost sat. A total that includes the cost categories therefore changes
basis in 2023 and again in 2024. Every indicator here excludes the cost categories. The total row
carries the cost-category amounts in `extra.cost_categories`, so a user who wants the cost of
delivery can add the cost-category amounts back.

CONDOM BUDGETS RECORD WHICH PLAN CARRIES THE COST, NOT WHAT WAS BOUGHT

Condoms and Lubricant holds 69,031,329 dollars in 346 lines, or 1.25 per cent of the file. In
2019 every one of the 40 condom lines carries a budget of zero, against 422.7 million condoms
over 14 countries, with 103,662,024 condoms for Zambia and 86,471,950 for Mozambique. Five
country-years in 2021 (Haiti, Lesotho, Malawi, Mozambique and Tanzania) and two in 2022 (Angola
and Tanzania) also list condoms against a budget of zero, which makes 21 country-years and
462,389,641 condoms in all. A condom budget in the file therefore records which country's plan
carries the cost of the condoms, and a country's plan can list a hundred million condoms against
a budget of zero. Condoms enter no indicator. The total row carries the condom budget in
`extra.condom_budget`, and `extra.condoms_listed_without_budget` marks a country-year whose plan
lists condoms with no money attached.

The partner file's `Condoms: Commodities` column agrees with the Condoms and Lubricant category to
within half of one per cent in 103 of the 118 country-years that both files fill. The files
disagree in 15 country-years, all in 2021 or 2022, and the partner file carries the smaller
figure in all 15 disagreements. In eight of the 15 country-years where the files disagree, the
partner file gives the condom total divided by the number of condom lines, which is the average
of the lines where the sum belongs. Cote d'Ivoire 2022 carries three condom lines summing to
749,967 dollars in the commodities file and 249,989 in the partner file. The seven other
disagreements, Democratic Republic of the Congo 2021, Lesotho 2022, Sierra Leone 2021, Eswatini
2022, Ukraine 2022, Zambia 2021 and Zimbabwe 2021, fit no rule the files settle. Five
country-years carry condom budget in the commodities file and none in the partner file. The
panel does not read the partner file's `Condoms: Commodities` column, so neither the averaged
figures nor the unexplained disagreements reach any indicator. The averaging does not reach the
partner file's `Total Planned Funding` either. Each averaged country-year books the condoms on one
GHSC-PSM row whose planned funding is at least the full condom total, and the partner file's
planned funding equals the OU budget file in every country-year from 2021 to 2025 once the
Peace Corps rows the partner file labels USA are placed in the countries the rows name
(ACCESS_LADDER §9s and §9t).

ONE COUNTRY-YEAR LISTS QUANTITIES WITH NO MONEY, AND IS WITHHELD

Lesotho 2024 carries 29 lines. Every line under Laboratory, RTKs and VMMC carries a budget of zero
against a stated quantity, 907,443, 1,510 and 30,200 units respectively, and the only money in
the country-year is 194,999.93 dollars on condoms and 5,000 on quality assurance. The like-for-
like total for Lesotho is 5.94m dollars in 2023 and 5.80m in 2025. Emitted as a zero, 2024 would
read as Lesotho's commodity plan collapsing for one year, when the file shows a plan listing
goods with no money attached. A country-year is withheld from every indicator when any major
category that enters the like-for-like total carries a quantity and no budget, and the log names
every withheld country-year. Lesotho 2024 is the only withheld country-year in the current file.

NINE COUNTRIES MISS A YEAR INSIDE THE COUNTRY'S OWN SERIES

Nine countries have no like-for-like total for a year between the country's first and last year
in the file. Colombia misses 2022 and 2023, Laos 2021 and 2022, Lesotho 2024, Peru 2022 and
2023, Papua New Guinea 2021 and 2022, Senegal 2023, Sierra Leone 2022, South Sudan 2020, 2022
and 2023, and Thailand 2021 and 2022. Of the 17 missing country-years, 14 carry no line at all.
Senegal 2023 carries only condoms and quality assurance, 99,924 dollars in two lines, and Sierra
Leone 2022 carries only condoms, 71,000 dollars in two lines, so neither country-year has money
in any category the like-for-like total includes. Lesotho 2024 is the withheld country-year
described above. The file does not say whether a country with a missing year filed no plan or
planned no commodities. A missing year stays missing and is never filled with a zero, because an
analysis of funding cuts would read a zero as a cut. Every row of a country with a missing year
names the missing years in `extra.series_gap_years`.

THE SERIES OF 12 COUNTRIES END BEFORE 2025

The like-for-like total series of 12 countries end before 2025. Guyana, India and Nicaragua end in
2021, Ghana and Liberia in 2022, Guatemala, Honduras, Panama and El Salvador in 2023, and
Colombia, Peru and Senegal in 2024. The file does not say whether PEPFAR stopped planning
commodities for the 12 countries or planned the commodities somewhere the file does not show, and
an analysis of funding cuts would read the end of a series as a cut. The log names every end on
every run.

Guatemala, Honduras, Panama and El Salvador sit under the Central and South America Region. In
2024 the Central and South America Region carries no line for Guatemala, Honduras, Panama or El
Salvador, and carries one line naming `Western Hemisphere Region (pre-FY24)` in place of a
country, 436,870 dollars of PrEP tablets. The file does not settle whether PEPFAR stopped planning
commodities for the four Central American countries or began planning the commodities at regional
level. Whenever a country under a regional operating unit ends in the year before the operating
unit carries a line naming a region, the country's rows say so in `extra.coverage_warning`. In the
current file the rule applies to Guatemala, Honduras, Panama and El Salvador.

A CATEGORY THE PLAN DOES NOT LIST IS EMITTED AS ZERO

A country-year with a like-for-like total and no line in a category carries a zero in the
category's series, marked with `extra.category_not_in_plan`. A procurement plan that lists no ARV
line plans to buy no ARVs, so the file settles the zero. Mali 2024 is the clearest case. Mali's
plan carries 489,495 dollars of Essential Meds, Laboratory and RTKs and no ARV line, between about
29,000 dollars of ARVs in 2023 and about 98,000 in 2025. The current file holds 84 zero rows for
ARV, 65 for Laboratory and 31 for RTKs, and the log counts the zero rows on every run. A zero ARV
plan can mean that another funder buys the country's ARVs, and the file does not say which funder.
A country-year with no like-for-like total carries no row in any series, under the two headings
above.

EXACT DUPLICATE LINES ARE KEPT

The file holds 326 lines that repeat an earlier line in every column, carrying 22,420,358
dollars, or 0.40 per cent of the file. The duplicate share is highest in 2020, at 1.51 per cent,
and below half of one per cent in every other year. The largest duplicate is Uganda 2020, where
one Roche viral-load line of 4,064,808 dollars appears twice, and one set of identical lines runs
to 33 copies. The file has no mechanism or partner column, so two implementing mechanisms
planning the same purchase at the same cost produce two identical lines, and the file cannot
tell two mechanisms planning the same purchase apart from a line entered twice. The duplicates
are kept. Every row carries `extra.duplicate_lines` and `extra.duplicate_usd` for the row's own
country, year and category, so a user who prefers to remove duplicates can subtract the amount.

PREP ENTERS THE ARV CATEGORY IN 2020

The minor category `ARVs for PrEP` carries no budget in 2019 and 2.9m dollars in 2020, rising to
46.1m in 2021. An ARV series compared from 2019 therefore changes basis in 2020 as well as
amount. ARV rows carry the PrEP amount in `extra.prep_budget`, and ARV rows in years before PrEP
first appears name the absent minor category in `extra.categories_absent`.

THE COUNTRY COUNT MEASURES WHICH OPERATING UNITS FILED A PLAN

An operating unit counts as regional here when the operating unit covers more than one country,
which is a property of the file rather than of the operating unit's name. The file holds seven
regional operating units, covering 29 countries in total, and no regional operating unit appears
in the file for 2019.

The like-for-like total covers 23 countries in 2019 and 38 in 2020. In 2020, 16 countries enter
and South Sudan leaves. Of the 16 entering countries, 15 sit under a regional operating unit,
so the rise in 2020 records the regional operating units' plans entering the file, not PEPFAR
beginning to buy commodities in the 15 countries. The file does not say what the regional
operating units planned for 2019. Angola, planned under an operating unit covering Angola alone,
also enters in 2020, and the file does not settle why Angola enters. The countries funded through
a regional operating unit carry `extra.funded_through_regional_ou` and `extra.coverage_warning`,
and an absent 2019 for a regional country means the file does not say, never that PEPFAR planned
nothing.

The count rises again from 38 in 2020 to 47 in 2021, as 12 countries enter and Laos, Papua New
Guinea and Thailand leave. Of the 12 entering countries, ten sit under a regional operating unit,
and the file does not settle whether the ten countries are new to PEPFAR commodity plans or
newly listed in the file. The log reports both rises on every run.

WHAT IS DISCARDED, AND WHY

One line names `Western Hemisphere Region (pre-FY24)` as the country, which is not a country and
maps to no ISO3. The line carries 436,870 dollars in 2024. A country-year panel has nowhere to
put the line, so the line is dropped and counted in the log rather than spread over a region.
The log reports every discard in the same line as what was used, with every amount given as a
share of the whole file over the years emitted, on the same basis of planned budget. The used
lines hold 94.70 per cent of the file, the cost categories 4.04 per cent, condoms 1.25 per cent
and the line with no ISO3 0.01 per cent, and the 25 withheld lines of Lesotho 2024 carry no money.
Every line falls in exactly one class, so no dollar is counted twice and the used and discarded
amounts sum to the file total.

CHECKED AGAINST THE PARTNER FILE

`Public_Partner_Budgets_and_Expenditures` is the source of `pepfar_planned_funding` for 2021 to
2025. Every country-year's full commodity plan, all categories included, is compared with the
partner file's `Total Planned Funding` for the same country-year. A commodity plan larger than
the country's whole planned funding would be a defect in one file or the other, and the log names
any country-year where the commodity plan is larger. Across 2021 to 2025 the full commodity plan
is between 15.8 and 17.9 per cent of planned funding in every year, over 228 country-years. The
highest single share is 0.408, for the Democratic Republic of the Congo in 2023, and no
country-year's commodity plan exceeds the country's planned funding. The partner file's `ISO3`
column labels 106 Peace Corps rows USA in 2022 to 2025 while the `Country` column names the
country, so the check places a partner row by the `Country` column wherever the `Country` column
and the `ISO3` column name different countries, as `pepfar_expenditure` does (ACCESS_LADDER §9t).
Keyed on the `ISO3` column alone, the range was 15.9 to 17.9 per cent. The comparison runs only
when the partner file sits in the same folder, and the log says when the comparison was skipped.

TAGGING: PEPFAR commodity procurement plans, not spending and not national HIV expenditure.
Nominal USD, not deflated. source_type = expenditure_account.
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

TOTAL = "pepfar_commodity_budget"

# The three major categories with an indicator of their own, by the name the file uses. Essential
# Meds, VMMC and TB enter the total and have no series of their own, because each is small and
# none maps onto a service the panel measures elsewhere.
CATEGORY_INDICATORS = (
    ("arv", "pepfar_arv_budget", "ARV"),
    ("rtks", "pepfar_rtk_budget", "RTKs"),
    ("laboratory", "pepfar_lab_budget", "Laboratory"),
)

# The major categories that enter the like-for-like total. A major category missing from this
# list and from the two exclusion lists below is new to the file, and the log says so rather than
# letting the category change what the total covers without notice.
TOTAL_CATEGORIES = ("arv", "rtks", "laboratory", "essential meds", "vmmc", "tb")

# Costs of moving, checking and managing goods, booked in some years only. In-Country Logistics
# and Quality Assurance begin in 2023, Procurement Management in 2024, and `Not Specified` carries
# distribution and warehousing lines in 2019 only.
COST_CATEGORIES = ("in-country logistics", "quality assurance", "procurement management",
                   "not specified")

# Condom lines record which plan carries the cost. In 2019 every condom line carries a budget of
# zero against 422.7 million condoms.
CONDOMS = "condoms and lubricant"

PREP_MINOR = "arvs for prep"

# A country total within this many dollars of the year before is a repeat of that year.
REPEAT_TOLERANCE_USD = 2.0

# The price per unit of one item in one country moving by more than this factor between
# consecutive years is counted as the quantity column changing unit.
UNIT_PRICE_JUMP = 10.0

# Two figures for the same country-year agree when the two differ by less than this share.
MATCH_TOLERANCE = 0.005

# a one-year rise in the number of countries carrying a total at least this large is reported
COUNTRY_RISE_SHARE = 0.25

# A rise is attributed to regional operating units entering the file only when most of the
# countries entering sit under a regional operating unit and no regional operating unit of those
# countries appears in the year before.
ATTRIBUTION_ENTRANT_SHARE = 0.5

SOURCE_URL = "https://data.pepfar.gov/datasets"

INTERPRETATION = (
    "PEPFAR's planned purchase of commodities for the country in the implementation year, as set "
    "in the Country Operational Plan a year ahead. A plan, not spending, and not national HIV "
    "expenditure. Nominal USD. Every plan in this file, COP24 for 2025 included, was drawn up "
    "before the January 2025 freeze, so no figure here shows the 2025 cut. The figures show what "
    "each country was set to receive going into 2025 and the trend before the freeze. "
    "In-Country Logistics, Quality Assurance, Procurement Management and the 2019 `Not "
    "Specified` lines are excluded from every value, because the file books those costs in some "
    "years only, and the amounts are in `cost_categories` on the total row. Condoms are excluded "
    "because the file lists condoms with a budget of zero in 2019 and in several later "
    "country-years, so a condom budget records which plan carries the cost rather than what was "
    "bought, and the amount is in `condom_budget` on the total row. Quantities are not emitted, "
    "because the unit a quantity counts changes between years for the same item. Exact "
    "duplicate lines are kept, since the file has no mechanism column to tell two mechanisms "
    "planning the same purchase from a line entered twice, and the amount is in "
    "`duplicate_usd`. ARV rows include PrEP from 2020, and the amount is in `prep_budget`. A "
    "category row of zero marked `category_not_in_plan` means the plan has a total and lists "
    "nothing in the category, and a zero ARV plan can mean that another funder buys the "
    "country's ARVs. A series that ends before 2025 does not show that PEPFAR stopped planning "
    "commodities for the country, and `coverage_warning` names the countries whose plan may "
    "have moved to regional level. A "
    "fall in planned ARV spending can come from a lower price per regimen or from another funder "
    "taking over part of the purchase, as well as from fewer people supplied, and the file cannot "
    "tell which cause is at work. A year missing inside a country's series is left missing, "
    "never filled with a zero, and the missing years are named in `series_gap_years`."
)


def _num(cell) -> float:
    """Blank means nothing on this line. Every blank in `Total Budget` and `Item Quantity` sits on
    a line whose other column is filled, so a blank is not a missing plan."""
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


def _m(usd: float) -> str:
    return f"{usd / 1e6:,.1f}m"


def _lines(n: int) -> str:
    return f"{n:,} line" + ("" if n == 1 else "s")


def _and(items: List[str]) -> str:
    items = list(items)
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


class PEPFARCommoditiesConnector(BaseConnector):
    source_id = "pepfar_commodities"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("PEPFAR commodity procurement plans by country, COP18 to COP24, as planned "
                   "budget for ARVs, rapid tests and laboratory goods.")

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _read_frame(self) -> Optional[pd.DataFrame]:
        if not self.raw_dir.exists():
            log.warning("pepfar_commodities: %s does not exist. Download "
                        "PEPFAR_OU_Commodities_Procurements from data.pepfar.gov", self.raw_dir)
            return None

        candidates = [p for p in sorted(self.raw_dir.glob("*.zip")) if "commodit" in p.name.lower()]
        if not candidates:
            log.warning("pepfar_commodities: no PEPFAR_OU_Commodities_Procurements zip in %s",
                        self.raw_dir)
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
                    log.info("pepfar_commodities: read %s from %s. Not read: %s", members[0],
                             path.name, [m for m in z.namelist() if m != members[0]] or "nothing")
                    return df
            except Exception as exc:
                log.warning("pepfar_commodities: error reading %s: %s", path.name, exc)
        return None

    def _read_partner(self) -> Optional[pd.DataFrame]:
        """The four columns of the partner-level budget file that the checks need, and the
        `Country` column, which decides the country of a row wherever the `ISO3` column names a
        different country. The partner file is read here for checking only, and nothing in the
        partner file is emitted."""
        paths = [p for p in sorted(self.raw_dir.glob("*.zip"))
                 if "public_partner" in p.name.lower() and "budget" in p.name.lower()]
        need = {"iso3", "implementation year", "total planned funding", "condoms: commodities"}
        want = need | {"country"}
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
                log.warning("pepfar_commodities: error reading %s for the check against the "
                            "partner file: %s", path.name, exc)
        return None

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
            "cycle": _ci(cols, "planning cycle"),
            "year": _ci(cols, "implementation year"),
            "major": _ci(cols, "major category"),
            "minor": _ci(cols, "minor category"),
            "item": _ci(cols, "commodity item"),
            "budget": _ci(cols, "total budget"),
            "qty": _ci(cols, "item quantity"),
        }
        missing = [k for k, c in need.items() if c is None]
        if missing:
            log.warning("pepfar_commodities: file lacks the columns %s, so the file is not this "
                        "dataset and nothing is emitted", ", ".join(missing))
            return

        f = pd.DataFrame({k: df[c].astype(str).str.strip() for k, c in need.items()})
        f["year"] = pd.to_numeric(f["year"].str[:4], errors="coerce")
        f["budget"] = df[need["budget"]].map(_num)
        f["qty"] = df[need["qty"]].map(_num)
        f["major_l"] = f["major"].str.lower()
        f["minor_l"] = f["minor"].str.lower()
        iso_of = {c: to_iso3(c) for c in f["country"].unique()}
        f["iso3"] = f["country"].map(iso_of)
        # An extra copy of a line identical in every column of the file. The first copy is not
        # marked, so the flag counts the lines a reader removing duplicates would remove.
        f["dup"] = df.duplicated(keep="first").values

        no_year = int(f["year"].isna().sum())
        if no_year:
            log.warning("pepfar_commodities: %d lines carry no readable Implementation Year and "
                        "are dropped", no_year)
        f = f[f["year"].notna()].copy()
        f["year"] = f["year"].astype(int)
        f = f[(f["year"] >= start_year) & (f["year"] <= end_year)].copy()
        if f.empty:
            log.info("pepfar_commodities: no line falls inside %d-%d", start_year, end_year)
            return

        unknown = sorted(set(f["major_l"]) - set(TOTAL_CATEGORIES) - set(COST_CATEGORIES)
                         - {CONDOMS})
        if unknown:
            log.warning("pepfar_commodities: major categories new to this connector, excluded "
                        "from every indicator until someone decides where the categories "
                        "belong: %s (%s USD)", ", ".join(unknown),
                        f"{f.loc[f['major_l'].isin(unknown), 'budget'].sum():,.0f}")

        # Every line falls in exactly one class, taken in this order, so no dollar is counted
        # twice and the used and discarded amounts sum to the file total over the years read.
        f["cls"] = "used"
        f.loc[f["major_l"].isin(unknown), "cls"] = "unknown"
        f.loc[f["major_l"] == CONDOMS, "cls"] = "condoms"
        f.loc[f["major_l"].isin(COST_CATEGORIES), "cls"] = "cost"
        f.loc[f["iso3"].isna(), "cls"] = "no_iso3"

        withheld = self._withheld(f)
        f.loc[(f["cls"] == "used")
              & pd.Series(list(zip(f["iso3"], f["year"])), index=f.index).isin(withheld),
              "cls"] = "withheld"

        regional, regional_ous, ou_years = self._regional(f)
        agg = self._aggregate(f)
        gaps = self._interior_gaps(agg)
        repeats = self._repeats(agg)
        prep_first = self._first_year(f[(f["minor_l"] == PREP_MINOR) & (f["budget"] > 0)])

        self._report_discards(f, agg)
        self._report_withheld(f, withheld)
        self._report_duplicates(f)
        self._report_cost_categories(f)
        self._report_condoms(f)
        self._report_prep(f, prep_first)
        self._report_composition(agg, f, regional, regional_ous, ou_years)
        exits = self._exits(agg, f, regional, gaps)
        self._report_repeats(agg, repeats)
        self._report_unit_prices(f)
        self._check_partner(f)

        yield from self._emit(agg, f, wanted, regional, regional_ous, ou_years, gaps, repeats,
                              prep_first, exits)

    # -- classifying ------------------------------------------------------------
    @staticmethod
    def _withheld(f: pd.DataFrame) -> set:
        """Country-years in which a major category entering the total lists a quantity with no
        money attached. The total for such a country-year understates the plan by an amount the
        file does not give, and in Lesotho 2024 the understatement is the whole plan."""
        used = f[f["cls"] == "used"]
        g = used.groupby(["iso3", "year", "major_l"])[["budget", "qty"]].sum()
        hit = g[(g["budget"] <= 0) & (g["qty"] > 0)]
        return {(i, int(y)) for i, y, _ in hit.index}

    @staticmethod
    def _regional(f: pd.DataFrame):
        """An operating unit is regional when the operating unit covers more than one country in
        this file. Both maps are built over every country in the file rather than the countries a
        run asks for, because whether an operating unit is regional is a property of the file."""
        named = f[f["iso3"].notna()]
        ou_countries = named.groupby("ou")["iso3"].agg(lambda s: set(s)).to_dict()
        regional_ous = {ou for ou, cs in ou_countries.items() if len(cs) > 1}
        regional: Dict[str, set] = {}
        for ou in regional_ous:
            for iso3 in ou_countries[ou]:
                regional.setdefault(iso3, set()).add(ou)
        ou_years = f.groupby("ou")["year"].agg(lambda s: set(int(y) for y in s)).to_dict()
        return regional, regional_ous, ou_years

    @staticmethod
    def _first_year(frame: pd.DataFrame) -> Optional[int]:
        return int(frame["year"].min()) if not frame.empty else None

    @staticmethod
    def _aggregate(f: pd.DataFrame) -> Dict[tuple, dict]:
        """(iso3, year) -> the country-year, built over every country in the file so that the
        composition, repeat and gap checks describe the file whatever countries a run asks for.
        The country filter applies at emission only."""
        agg: Dict[tuple, dict] = {}
        named = f[f["iso3"].notna()]
        for (iso3, year), g in named.groupby(["iso3", "year"]):
            used = g[g["cls"] == "used"]
            a = {
                "name": g["country"].iloc[0],
                "cycle": g["cycle"].iloc[0],
                "withheld": bool((g["cls"] == "withheld").any()),
                "total": float(used["budget"].sum()),
                "all_budget": float(g["budget"].sum()),
                "by_major": used.groupby("major")["budget"].sum().to_dict(),
                "by_major_l": used.groupby("major_l")["budget"].sum().to_dict(),
                "majors_present": set(used["major_l"]),
                "by_minor": {k: grp.groupby("minor")["budget"].sum().to_dict()
                             for k, grp in used.groupby("major_l")},
                "dup": {k: (int(grp["dup"].sum()), float(grp.loc[grp["dup"], "budget"].sum()))
                        for k, grp in used.groupby("major_l")},
                "prep": float(used.loc[used["minor_l"] == PREP_MINOR, "budget"].sum()),
                "cost": g[g["cls"] == "cost"].groupby("major")["budget"].sum().to_dict(),
            }
            condoms = g[g["cls"] == "condoms"]
            if not condoms.empty:
                a["condom_budget"] = float(condoms["budget"].sum())
                a["condom_lines"] = len(condoms)
                a["condoms_without_budget"] = bool(condoms["budget"].sum() <= 0
                                                   and condoms["qty"].sum() > 0)
            agg[(iso3, int(year))] = a
        return agg

    # -- reporting --------------------------------------------------------------
    @staticmethod
    def _report_discards(f: pd.DataFrame, agg: Dict[tuple, dict]) -> None:
        """One line, carrying what was used and every discard as a share of the whole file over
        the years read, on the one basis of planned budget. The denominator is the whole file
        and not the countries a run asks for, because the line with no ISO3 can never be reached
        by a country filter."""
        whole = float(f["budget"].sum())
        by = f.groupby("cls")["budget"].sum()
        lines = f.groupby("cls").size()

        def part(cls: str, label: str = "") -> str:
            usd = float(by.get(cls, 0.0))
            return (f"{label}{_lines(int(lines.get(cls, 0)))} and {usd:,.0f} USD "
                    f"({_pct(usd, whole):.4f}%)")

        discards = [part("cost", "as cost categories "), part("condoms", "as condoms "),
                    part("no_iso3", "for naming no country "),
                    part("withheld", "as withheld country-years ")]
        if "unknown" in by:
            discards.append(part("unknown", "as unknown categories "))
        used_cy = sum(1 for a in agg.values() if a["total"] > 0 and not a["withheld"])
        log.info(
            "pepfar_commodities: %s and %s USD read over %d-%d. Used %s over %d country-years. "
            "Discarded %s. Shares are of the whole file",
            _lines(len(f)), f"{whole:,.0f}", int(f["year"].min()), int(f["year"].max()),
            part("used"), used_cy, _and(discards),
        )
        if "no_iso3" in by:
            for name, g in f[f["cls"] == "no_iso3"].groupby("country"):
                log.info("pepfar_commodities: `%s` maps to no ISO3, %s and %s USD in %s",
                         name or "(blank)", _lines(len(g)), f"{g['budget'].sum():,.0f}",
                         _and([str(y) for y in sorted(g["year"].unique())]))

    @staticmethod
    def _report_withheld(f: pd.DataFrame, withheld: set) -> None:
        for iso3, year in sorted(withheld):
            g = f[(f["iso3"] == iso3) & (f["year"] == year)]
            empty = g[g["cls"] == "withheld"].groupby("major")[["budget", "qty"]].sum()
            empty = empty[(empty["budget"] <= 0) & (empty["qty"] > 0)]
            elsewhere = g[g["cls"].isin(["cost", "condoms"])].groupby("major")["budget"].sum()
            log.info(
                "pepfar_commodities: %s %d is withheld from every indicator. The plan lists "
                "quantities with a budget of zero under %s, and the country-year's only money is "
                "%s, all of it in categories no indicator includes. Emitted as a zero, the year "
                "would read as the country's commodity plan collapsing",
                iso3, year,
                _and([f"{m} ({q:,.0f} units)" for m, q in empty["qty"].items()]),
                _and([f"{v:,.2f} USD on {m}" for m, v in elsewhere.items() if v]) or "nothing",
            )

    @staticmethod
    def _report_duplicates(f: pd.DataFrame) -> None:
        dup = f[f["dup"]]
        if dup.empty:
            return
        whole = float(f["budget"].sum())
        dup_by_year = dup.groupby("year")["budget"].sum()
        all_by_year = f.groupby("year")["budget"].sum()
        per_year = ", ".join(f"{y} {_pct(dup_by_year.get(y, 0.0), all_by_year[y]):.2f}%"
                             for y in all_by_year.index)
        log.info("pepfar_commodities: %d lines repeat an earlier line in every column and carry "
                 "%s USD (%.2f%% of the file, by year %s). The duplicates are kept, because the "
                 "file has no mechanism column to tell two mechanisms planning the same purchase "
                 "from a line entered twice. Every row carries `duplicate_lines` and "
                 "`duplicate_usd` for its own scope",
                 len(dup), f"{dup['budget'].sum():,.0f}", _pct(dup["budget"].sum(), whole),
                 per_year)

    @staticmethod
    def _report_cost_categories(f: pd.DataFrame) -> None:
        cost = f[f["cls"] == "cost"]
        if cost.empty:
            return
        all_years = sorted(f["year"].unique())
        parts = []
        for major, g in cost.groupby("major"):
            yrs = sorted(int(y) for y in g.loc[g["budget"] > 0, "year"].unique())
            if not yrs:
                continue
            span = (f"from {yrs[0]}" if yrs == [y for y in all_years if y >= yrs[0]]
                    else "in " + ", ".join(str(y) for y in yrs))
            amounts = " ".join(_m(g.loc[g["year"] == y, "budget"].sum()) for y in yrs)
            parts.append(f"{major} {span} ({amounts})")
        if not parts:
            return
        log.info("pepfar_commodities: the file books budget under %s. A category booked in some "
                 "years only changes what a total covers across the years, so no indicator "
                 "includes the cost categories, and the amounts ride on the total row in "
                 "`cost_categories`", _and(parts))

    @staticmethod
    def _report_condoms(f: pd.DataFrame) -> None:
        c = f[f["cls"] == "condoms"]
        if c.empty:
            return
        cy = c.groupby(["iso3", "year"])[["budget", "qty"]].sum()
        empty = cy[(cy["budget"] <= 0) & (cy["qty"] > 0)]
        by_year = empty.groupby(level="year").size()
        log.info("pepfar_commodities: condoms hold %d lines and %s USD, and %d country-years list "
                 "condoms with a budget of zero (%s), %s condoms in all. A condom budget in this "
                 "file records which plan carries the cost rather than what was bought, so "
                 "condoms enter no indicator, and the amount rides on the total row in "
                 "`condom_budget`",
                 len(c), f"{c['budget'].sum():,.0f}", len(empty),
                 ", ".join(f"{n} in {y}" for y, n in by_year.items()) or "none",
                 f"{empty['qty'].sum():,.0f}")

    @staticmethod
    def _report_prep(f: pd.DataFrame, prep_first: Optional[int]) -> None:
        if prep_first is None or prep_first <= int(f["year"].min()):
            return
        arv = f[(f["cls"] == "used") & (f["major_l"] == "arv")]
        first = arv.loc[(arv["year"] == prep_first) & (arv["minor_l"] == PREP_MINOR), "budget"]
        log.info("pepfar_commodities: `ARVs for PrEP` first carries budget in %d (%s USD), so "
                 "the ARV series changes basis in %d as well as amount. ARV rows carry "
                 "`prep_budget`, and ARV rows before %d name the minor category in "
                 "`categories_absent`",
                 prep_first, f"{first.sum():,.0f}", prep_first, prep_first)

    @staticmethod
    def _report_composition(agg: Dict[tuple, dict], f: pd.DataFrame, regional: Dict[str, set],
                            regional_ous: set, ou_years: Dict[str, set]) -> None:
        """A sharp rise in the number of countries carrying a total means a total compared across
        the step covers two different sets of countries. The log adds a cause only where the
        file settles the cause, which is when most of the countries entering sit under a regional
        operating unit and none of those operating units appears in the year before."""
        present: Dict[int, set] = {}
        for (iso3, year), a in agg.items():
            if a["total"] > 0 and not a["withheld"]:
                present.setdefault(year, set()).add(iso3)
        absent_years = sorted(y for y in present
                              if not any(y in ou_years.get(ou, set()) for ou in regional_ous))
        if absent_years and regional_ous:
            yrs = ", ".join(str(y) for y in absent_years)
            log.info("pepfar_commodities: %d operating units cover more than one country, %d "
                     "countries between them (%s), and no such operating unit appears in the "
                     "file for %s. For those countries an absent %s means the file does not say "
                     "what the country was planned to receive",
                     len(regional_ous), len(regional), ", ".join(sorted(regional_ous)), yrs, yrs)
        for year in sorted(present)[1:]:
            before, now = present.get(year - 1), present[year]
            if not before:
                continue
            entered, left = now - before, before - now
            if len(entered) / len(before) < COUNTRY_RISE_SHARE:
                continue
            from_regional = {i for i in entered if i in regional}
            their_ous = {ou for i in from_regional for ou in regional[i]}
            attributed = (len(from_regional) >= ATTRIBUTION_ENTRANT_SHARE * len(entered)
                          and not any(year - 1 in ou_years.get(ou, set()) for ou in their_ous))
            others = sorted(entered - from_regional)
            because = (
                f"No regional operating unit of those countries appears in the file for "
                f"{year - 1}, so the rise is the regional operating units' plans entering the "
                f"file, not PEPFAR beginning to buy commodities in those countries in {year}"
                if attributed else
                "The file does not settle whether those countries are new to PEPFAR commodity "
                "plans or newly filed in this file"
            )
            rest = (f". The file does not settle the entry of {_and(others)}, planned under an "
                    "operating unit covering one country" if attributed and others else "")
            log.info(
                "pepfar_commodities: countries carrying a total rise from %d in %d to %d in %d, "
                "%d entering and %d leaving (%s), and %d of the countries entering sit under a "
                "regional operating unit. %s%s",
                len(before), year - 1, len(now), year, len(entered), len(left),
                _and(sorted(left)) or "none", len(from_regional), because, rest,
            )

    @staticmethod
    def _exits(agg: Dict[tuple, dict], f: pd.DataFrame, regional: Dict[str, set],
               gaps: Dict[str, List[int]]) -> Dict[str, str]:
        """Countries whose total series stops, for a year or for good. An analysis of funding cuts
        reads a series that stops as a cut, so every stop is logged. A country under a regional
        operating unit whose series ends in the year before that operating unit carries a line
        naming a region rather than a country gets a sentence on the country's rows, because the
        file then does not settle whether the plan ended or moved to regional level."""
        present: Dict[str, List[int]] = {}
        for (iso3, year), a in agg.items():
            if a["total"] > 0 and not a["withheld"]:
                present.setdefault(iso3, []).append(year)
        if not present:
            return {}
        last_year = max(max(yrs) for yrs in present.values())
        ends = {i: max(yrs) for i, yrs in present.items() if max(yrs) < last_year}

        if gaps:
            log.info("pepfar_commodities: %d countries miss a year inside the country's own "
                     "series and return later (%s). The rows name the missing years in "
                     "`series_gap_years`, and no missing year is filled with a zero",
                     len(gaps), ", ".join(f"{i} {_and([str(y) for y in ys])}"
                                          for i, ys in sorted(gaps.items())))
        if not ends:
            return {}
        by_end: Dict[int, List[str]] = {}
        for i, y in ends.items():
            by_end.setdefault(y, []).append(i)
        log.info("pepfar_commodities: the total series of %d countries end before %d (%s). "
                 "The file does not say whether PEPFAR stopped planning commodities for "
                 "those countries or planned the countries' commodities somewhere the file does "
                 "not show", len(ends), last_year,
                 "; ".join(f"after {y} {_and(sorted(cs))}" for y, cs in sorted(by_end.items())))

        region_lines = f[f["cls"] == "no_iso3"].groupby(["ou", "year"])
        out: Dict[str, str] = {}
        for (ou, year), g in region_lines:
            left = sorted(i for i, y in ends.items() if y == year - 1 and ou in regional.get(i, ()))
            if not left:
                continue
            names = _and([f"`{n}`" for n in sorted(g["country"].unique())])
            sentence = (f"The country's series ends in {year - 1}. In {year} the country's "
                        f"operating unit, {ou}, carries a line naming {names} rather than a "
                        "country, so the file does not settle whether PEPFAR stopped planning "
                        "commodities for the country or planned the commodities at regional "
                        "level.")
            for i in left:
                out[i] = f"{out[i]} {sentence}" if i in out else sentence
            log.info("pepfar_commodities: %s leave after %d, and in %d the countries' operating "
                     "unit, %s, carries %s (%s USD) in place of a country. The file does not "
                     "settle whether PEPFAR stopped planning commodities for those countries or "
                     "planned the commodities at regional level, and the countries' rows say so "
                     "in `coverage_warning`", _and(left), year - 1, year, ou, names,
                     f"{g['budget'].sum():,.0f}")
        return out

    @staticmethod
    def _repeats(agg: Dict[tuple, dict]) -> set:
        out = set()
        for (iso3, year), a in agg.items():
            prev = agg.get((iso3, year - 1))
            if (a["total"] > 0 and prev and prev["total"] > 0
                    and abs(a["total"] - prev["total"]) <= REPEAT_TOLERANCE_USD):
                out.add((iso3, year))
        return out

    @staticmethod
    def _report_repeats(agg: Dict[tuple, dict], repeats: set) -> None:
        pairs = sum(1 for (i, y), a in agg.items()
                    if a["total"] > 0 and agg.get((i, y - 1), {}).get("total", 0.0) > 0)
        if not repeats:
            log.info("pepfar_commodities: no country total repeats the year before to within "
                     "%.0f USD, over %d pairs of consecutive country-years",
                     REPEAT_TOLERANCE_USD, pairs)
            return
        log.info("pepfar_commodities: %d of %d country totals repeat the year before to within "
                 "%.0f USD (%s). A repeated total is not evidence that the plan was held, and "
                 "the rows carry `repeats_previous_year`",
                 len(repeats), pairs, REPEAT_TOLERANCE_USD,
                 ", ".join(f"{i} {y}" for i, y in sorted(repeats)))

    @staticmethod
    def _report_unit_prices(f: pd.DataFrame) -> None:
        """The price per unit of one item in one country, compared across consecutive years. The
        count is the reason quantities are not emitted, so the count is measured on every run."""
        used = f[(f["cls"] == "used") & (f["budget"] > 0) & (f["qty"] > 0)]
        g = used.groupby(["iso3", "major", "item", "year"])[["budget", "qty"]].sum()
        price = (g["budget"] / g["qty"]).rename("p").reset_index()
        nxt = price.assign(year=price["year"] - 1)
        pairs = price.merge(nxt, on=["iso3", "major", "item", "year"], suffixes=("", "_next"))
        if pairs.empty:
            return
        ratio = pairs[["p", "p_next"]].max(axis=1) / pairs[["p", "p_next"]].min(axis=1)
        jumps = pairs[ratio > UNIT_PRICE_JUMP]
        by_major = ", ".join(
            f"{m} {int((jumps['major'] == m).sum())} of {int((pairs['major'] == m).sum())}"
            for m in sorted(pairs["major"].unique()))
        log.info("pepfar_commodities: of %s pairs of the same item in the same country in "
                 "consecutive years, %d change price per unit more than %.0f-fold (%s). The file "
                 "does not name the unit of `Item Quantity`, and a change that size is more "
                 "likely a change of unit than of price, so quantities are not emitted",
                 f"{len(pairs):,}", len(jumps), UNIT_PRICE_JUMP, by_major)

    # -- checking ---------------------------------------------------------------
    def _check_partner(self, f: pd.DataFrame) -> None:
        """Two checks against the partner-level budget file, which is the source of
        `pepfar_planned_funding` for 2021 onward. The full commodity plan of a country-year should
        never exceed the country's whole planned funding, and the condom category should match
        the partner file's `Condoms: Commodities` column."""
        p = self._read_partner()
        if p is None or p.empty:
            log.info("pepfar_commodities: no Public_Partner_Budgets_and_Expenditures zip in %s, "
                     "so the check against the partner file was skipped", self.raw_dir)
            return
        cols = list(p.columns)
        iso_of = {c: to_iso3(c) for c in p[_ci(cols, "iso3")].unique()}
        iso3 = p[_ci(cols, "iso3")].map(iso_of)
        cn = _ci(cols, "country")
        if cn:
            # placed as pepfar_expenditure places the rows, by the Country column wherever the
            # ISO3 column names a different country (ACCESS_LADDER §9t)
            name_of = {c: to_iso3(c) for c in p[cn].unique()}
            iso3 = p[cn].map(name_of).where(iso3.notna()).fillna(iso3)
        q = pd.DataFrame({
            "iso3": iso3,
            "year": pd.to_numeric(p[_ci(cols, "implementation year")].str[:4], errors="coerce"),
            "planned": p[_ci(cols, "total planned funding")].map(_num),
            "condoms": p[_ci(cols, "condoms: commodities")].map(_num),
        }).dropna(subset=["iso3", "year"])
        q["year"] = q["year"].astype(int)
        theirs = q.groupby(["iso3", "year"])[["planned", "condoms"]].sum()

        named = f[f["iso3"].notna()]
        ours = named.groupby(["iso3", "year"])["budget"].sum().rename("commodities")
        both = pd.concat([ours, theirs["planned"]], axis=1, join="inner")
        both = both[both["planned"] > 0]
        if both.empty:
            log.info("pepfar_commodities: the partner file shares no country-year with this file, "
                     "so the check against planned funding was skipped")
            return
        both["share"] = both["commodities"] / both["planned"]
        years = sorted(both.index.get_level_values("year").unique())
        sums = both.groupby(level="year")[["commodities", "planned"]].sum()
        per_year = ", ".join(f"{y} {_pct(sums.loc[y, 'commodities'], sums.loc[y, 'planned']):.1f}%"
                             for y in years)
        over = both[both["share"] > 1]
        log.info("pepfar_commodities: against the partner file's Total Planned Funding, the full "
                 "commodity plan is %s of planned funding by year, over %d country-years, with "
                 "a highest share of %.3f in %s %d. %s",
                 per_year, len(both), both["share"].max(), *both["share"].idxmax(),
                 ("No commodity plan exceeds the country's planned funding" if over.empty else
                  "Commodity plans exceed planned funding in " + ", ".join(
                      f"{i} {y} ({s:.2f})" for (i, y), s in over["share"].items())))

        c = named[named["cls"] == "condoms"].groupby(["iso3", "year"]).agg(
            ours=("budget", "sum"), lines=("budget", "size"))
        span = (theirs.index.get_level_values("year").min(),
                theirs.index.get_level_values("year").max())
        c = c[(c.index.get_level_values("year") >= span[0])
              & (c.index.get_level_values("year") <= span[1])]
        cc = c.join(theirs["condoms"].rename("theirs"), how="outer").fillna(0.0)
        cc = cc[(cc["ours"] > 0) | (cc["theirs"] > 0)]
        filled = cc[(cc["ours"] > 0) & (cc["theirs"] > 0)]

        def close(a: pd.Series, b: pd.Series) -> pd.Series:
            return (a - b).abs() <= MATCH_TOLERANCE * pd.concat([a, b], axis=1).max(axis=1)

        match = close(filled["ours"], filled["theirs"])
        averaged = ~match & close(filled["ours"] / filled["lines"], filled["theirs"])
        other = filled[~match & ~averaged]
        miss = filled[~match]
        smaller = int((miss["theirs"] < miss["ours"]).sum())
        log.info("pepfar_commodities: condoms against the partner file's `Condoms: Commodities` "
                 "column. The two agree within %.1f%% in %d of %d country-years both files fill. "
                 "In %d of the %d disagreements (in %s), the partner file gives the condom total "
                 "divided by the number of condom lines, which is the average where the sum "
                 "belongs. %d disagree by no rule the files settle%s. The partner file carries "
                 "the smaller figure in %d of the %d disagreements (%s). %d country-years carry "
                 "condoms in this file only and %d in the partner file only. No indicator "
                 "includes condoms, and the panel does not read the partner file's column",
                 MATCH_TOLERANCE * 100, int(match.sum()), len(filled), int(averaged.sum()),
                 len(miss), _and(sorted({str(y) for _, y in filled[averaged].index})) or "no year",
                 len(other),
                 (" (" + _and([f"{i} {y}" for i, y in other.index]) + ")") if len(other) else "",
                 smaller, len(miss),
                 _and(sorted({str(y) for _, y in miss.index.tolist()})) or "no year",
                 int(((cc["ours"] > 0) & (cc["theirs"] <= 0)).sum()),
                 int(((cc["ours"] <= 0) & (cc["theirs"] > 0)).sum()))

    # -- composition ------------------------------------------------------------
    @staticmethod
    def _interior_gaps(agg: Dict[tuple, dict]) -> Dict[str, List[int]]:
        """Years missing from the middle of a country's total series. An analysis measuring the
        effect of a funding cut reads a hole as a cut, so the missing years are named on the row
        rather than left for the reader to notice."""
        seen: Dict[str, List[int]] = {}
        for (iso3, year), a in agg.items():
            if a["total"] > 0 and not a["withheld"]:
                seen.setdefault(iso3, []).append(year)
        gaps = {}
        for iso3, yrs in seen.items():
            missing = [y for y in range(min(yrs), max(yrs) + 1) if y not in yrs]
            if missing:
                gaps[iso3] = missing
        return gaps

    def _emit(self, agg: Dict[tuple, dict], f: pd.DataFrame, wanted, regional: Dict[str, set],
              regional_ous: set, ou_years: Dict[str, set], gaps: Dict[str, List[int]],
              repeats: set, prep_first: Optional[int], exits: Dict[str, str]) -> List[PanelRow]:
        rows: List[PanelRow] = []
        # The file's own spelling of each major category, for naming absent categories.
        spelled = f.drop_duplicates("major_l").set_index("major_l")["major"].to_dict()
        not_in_plan = {label: 0 for _, _, label in CATEGORY_INDICATORS}
        file_years = sorted(int(y) for y in f["year"].unique())
        silent_years = [y for y in file_years
                        if not any(y in ou_years.get(ou, set()) for ou in regional_ous)]
        warning = None
        if silent_years:
            yrs = ", ".join(str(y) for y in silent_years)
            warning = (
                "This country is planned through an operating unit covering more than one "
                f"country, and no such operating unit appears in this file for {yrs}. An absent "
                f"{yrs} means the file does not say what the country was planned to receive, "
                "not that PEPFAR planned nothing. Do not read the first year present as the "
                "start of commodity procurement."
            )

        for (iso3, year), a in sorted(agg.items()):
            if wanted and iso3 not in wanted:
                continue
            if a["withheld"] or a["total"] <= 0:
                continue
            base: Dict[str, object] = {
                "note": ("PEPFAR commodity procurement plan, NOT spending and NOT national HIV "
                         "expenditure. Nominal USD."),
                "grain": ("country within an operating-unit plan, no mechanism or funding-agency "
                          "column in this file"),
                "interpretation": INTERPRETATION,
                "planning_cycle": a["cycle"],
            }
            if iso3 in regional:
                base["funded_through_regional_ou"] = True
                said = " ".join(w for w in (warning, exits.get(iso3)) if w)
                if said:
                    base["coverage_warning"] = said
            if iso3 in gaps:
                base["series_gap_years"] = gaps[iso3]

            extra = dict(base)
            extra["by_major_category"] = {k: v for k, v in
                                          sorted(a["by_major"].items(), key=lambda kv: -kv[1])}
            absent = [spelled.get(c, c) for c in TOTAL_CATEGORIES if c not in a["majors_present"]]
            if absent:
                extra["categories_absent"] = absent
            if a["cost"]:
                extra["cost_categories"] = a["cost"]
            if "condom_budget" in a:
                extra["condom_budget"] = a["condom_budget"]
                if a["condoms_without_budget"]:
                    extra["condoms_listed_without_budget"] = True
            n_dup = sum(n for n, _ in a["dup"].values())
            if n_dup:
                extra["duplicate_lines"] = n_dup
                extra["duplicate_usd"] = sum(v for _, v in a["dup"].values())
            if (iso3, year) in repeats:
                extra["repeats_previous_year"] = True
            rows.append(self.make_row(
                country_iso3=iso3, country_name=a["name"], indicator_id=TOTAL, year=year,
                value=a["total"], unit="USD", source_url=SOURCE_URL,
                source_indicator_code=("PEPFAR OU Commodities Procurements — Total Budget, "
                                       "excluding cost categories and condoms"),
                extra=extra,
            ))

            for key, indicator, label in CATEGORY_INDICATORS:
                value = float(a["by_major_l"].get(key, 0.0))
                extra = dict(base)
                if value <= 0:
                    # The plan has a total and buys none of the category. Lines with a quantity
                    # and no budget cannot reach here, because the lines withhold the whole
                    # country-year above, so a listed category here lists nothing at all.
                    if key in a["majors_present"]:
                        extra["category_listed_without_budget_or_quantity"] = True
                    else:
                        extra["category_not_in_plan"] = True
                    not_in_plan[label] += 1
                    rows.append(self.make_row(
                        country_iso3=iso3, country_name=a["name"], indicator_id=indicator,
                        year=year, value=0.0, unit="USD", source_url=SOURCE_URL,
                        source_indicator_code=("PEPFAR OU Commodities Procurements — Total "
                                               "Budget, " + label),
                        extra=extra,
                    ))
                    continue
                extra["by_minor_category"] = {k: v for k, v in sorted(
                    a["by_minor"].get(key, {}).items(), key=lambda kv: -kv[1])}
                n, usd = a["dup"].get(key, (0, 0.0))
                if n:
                    extra["duplicate_lines"] = n
                    extra["duplicate_usd"] = usd
                if key == "arv":
                    if a["prep"]:
                        extra["prep_budget"] = a["prep"]
                    elif prep_first is not None and year < prep_first:
                        extra["categories_absent"] = ["ARVs for PrEP"]
                rows.append(self.make_row(
                    country_iso3=iso3, country_name=a["name"], indicator_id=indicator,
                    year=year, value=value, unit="USD", source_url=SOURCE_URL,
                    source_indicator_code=("PEPFAR OU Commodities Procurements — Total Budget, "
                                           + label),
                    extra=extra,
                ))

        if any(not_in_plan.values()):
            log.info("pepfar_commodities: a country-year with a total and no line in a category "
                     "is emitted as zero with `category_not_in_plan`, because the plan then buys "
                     "none of the category (%s)",
                     ", ".join(f"{k} {v}" for k, v in not_in_plan.items()))
        emitted = {r.country_iso3 for r in rows}
        log.info("pepfar_commodities: emitted %d rows over %d countries", len(rows), len(emitted))
        return rows
