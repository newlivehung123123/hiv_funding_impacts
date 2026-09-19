"""
PEPFAR budget and expenditure at operating-unit grain — the sixteen years the partner file
never had.

`pepfar_expenditure` reads `Public_Partner_Budgets_and_Expenditures`, which begins at FY2021.
Its own code excludes this file by name, on the reasoning that the operating-unit file "covers
the same money at a coarser grain with no agency column, so reading both would double count".
That reasoning is correct and this connector does not overturn it. Restricted to rows carrying
an ISO3 code, with the three aggregate layers removed, the operating-unit file reproduces the
panel to the dollar in every year the two files share:

    FY2021 budget       5,036,285,258   both files
    FY2021 expenditure  4,121,559,166   both files
    FY2025 budget       4,281,549,540   both files
    FY2025 expenditure  2,789,722,472   against 2,789,722,474 in the panel, two dollars of
                                        rounding in PEPFAR's own published figures

So the two files are one body of money published at two grains, and nothing between FY2021 and
FY2025 is emitted here. What the exclusion cost the panel is the history. This file carries a
budget column for every year from 2004 and an expenditure column from 2018, and the partner file
has none of it. This connector owns budget for 2005 to 2020 and expenditure for 2018 to 2020,
and declares every later year out of scope in its log line. The 2004 column is read and not
emitted, for the reason given under the next heading.

THE 2004 COLUMN IS NOT A YEAR'S BUDGET

The 2004 column holds 22 rows over 11 countries and 68,991,569 dollars, and every one of those
rows sits under testing or care and treatment. No other programme area carries anything in 2004.
In all 11 countries, testing takes exactly 70 per cent and care and treatment exactly 30 per
cent, from Tanzania at 14,693,227 dollars down to Cote d'Ivoire at 2,709,900. A budget planned
programme by programme does not divide in the same proportion in 11 countries, so the column is
one figure per country divided by a fixed rule. The same 11 countries carry 783,034,013 dollars in
2005, 11.3 times the 2004 figure, and between 4.6 and 33.3 times by country. Emitted as planned
funding, the 2004 column would put an elevenfold rise at the start of every series it touches. The
column is counted in the log, with the split measured on every run, and is never emitted.

THREE AGGREGATE LAYERS SIT ON TOP OF THE DETAIL, AND ALL THREE HAD TO BE FOUND

The file holds 12,062 rows, which are 11,919 detail rows plus 71 country rows carrying
`Program = Total`, plus 71 rows carrying `Applied Pipeline` simultaneously in Program,
Interaction Type, Beneficiary and Sub Beneficiary, plus a single footer row whose only populated
fields are `Operating Unit = Total` and the money. Summing the file without removing all three
returns twice the true figure in every year, which is how the footer row was found: the total of
the non-Total rows came to exactly 2.0000 times the total of the country Total rows, in all
thirty money columns at once, and a ratio that clean is a duplicated layer rather than an error
of degree.

Applied Pipeline is unspent money from earlier years applied to the current year, it appears
only in the budget columns for 2014 to 2019, and PEPFAR's own country Total row includes it
(across the whole file, regional rows included, 1,210m in 2014, 705m in 2015, 389m in 2016,
612m in 2017, 861m in 2018 and 510m in 2019). The budget this connector emits therefore includes
it as well, and carries it separately in `extra.applied_pipeline` so anyone who wants new money
alone can subtract it. Leaving it out is what makes FY2018 appear to spend 111 per cent of its
budget.

The reconstruction is checked rather than trusted. Detail plus Applied Pipeline reproduces
PEPFAR's own country Total row exactly in 770 of the 773 country-years that carry a budget, and
the remaining three differ by more than a dollar but by far less than one per cent. The runtime
check runs on every country-year at a half of one per cent and logs whatever trips it, so a
future download that breaks the reconstruction says so rather than passing quietly.

MANAGEMENT AND OPERATIONS BREAKS EVERY EXECUTION RATE THAT INCLUDES IT

Rows whose `Record Type` is Management and Operations hold roughly half a billion dollars of
budget in every recent year and almost no expenditure at all, 317m of budget against a
near-empty expenditure column in 2018 and 518m against 12m in 2025. The pattern is flat across
every year that carries expenditure, 2018 to 2025, so it is a property of how PEPFAR books its
own running costs and not an artefact of any one year. Any execution rate computed over the
whole file therefore carries half a billion in its denominator that the numerator structurally
cannot contain, which understates execution by about ten points:

    FY2018   0.897 including Management and Operations, 0.966 excluding it
    FY2019   0.861                                      0.939
    FY2020   0.808                                      0.902

Both figures are carried on the row, as `execution_ratio` and
`execution_ratio_excl_mgmt_ops`. The second is the one to read.

WHAT THE FILE SAYS ABOUT FY2025, WHICH THIS CONNECTOR DOES NOT EMIT

The finding belongs to `pepfar_expenditure` and is recorded here only because this file reaches
it by a different route and agrees. FY2025 execution is 0.652 against a range of 0.808 to 0.897
in every earlier year, and the shortfall is not spread evenly across programmes. Care and
treatment, the activity the January 2025 waiver covered, runs at 0.77. Prevention runs at 0.45
and surveillance and survey work at 0.35, with testing at 0.80, above-site programme support at
0.66 and programme management at 0.56. A file published late shrinks every programme by roughly
the same fraction. An ordering that tracks which activities were allowed to continue does not
come from a reporting lag, and `pepfar_expenditure` reaches the same conclusion from the
mechanism reporting rates, which this file cannot compute because it has no mechanism column.

That is agreement, not corroboration. Both readings come from the same expenditure reports.

WHAT IS DISCARDED, AND WHY

Rows carrying no ISO3 code belong to regional operating units that PEPFAR does not resolve to a
country, the Caribbean, Central Asia, Central and South America, the Pacific and two West Africa
regions, together with a bucket labelled `Invalid`. There are 463 such rows, 455 detail rows and
eight Applied Pipeline rows. Over 2005 to 2020, the years this connector emits, those rows hold
623,079,124 dollars of budget against the 57,308,862,383 dollars this connector emits, or 1.08
per cent of the dropped and emitted budget together, and 120,451,355 dollars of expenditure over
2018 to 2020 against 11,712,716,512, or 1.02 per cent of the dropped and emitted expenditure
together. Of the discarded budget, 39,714,294 dollars sits under `Invalid`, which is a
bucket for rows PEPFAR could not attribute rather than a region, and 81,305,868 dollars is
Applied Pipeline rather than money appropriated in the year it appears. A country-year panel has
nowhere to put any of it, so it is dropped and counted in the log line rather than distributed
across the countries of a region.

Both figures in each of those comparisons are measured over the years this connector emits and
on the same basis, budget including Applied Pipeline against budget including Applied Pipeline.
A discard reported for a year the connector leaves to another connector, or against a total
built on a different basis, describes something the connector never emits.

TWO BUDGET CATEGORIES BEGIN IN 2014, SO THE BUDGET CHANGES BASIS THERE

Management and Operations and Applied Pipeline carry no budget in any year before 2014. On country
rows in 2014, Management and Operations holds 295,636,956 dollars and Applied Pipeline
1,180,230,636. The emitted budget rises from 3,213,039,728 dollars in 2013 to 4,780,573,818 in
2014, and 1,475,867,592 of that 1,567,534,090 rise is the two categories that 2013 does not carry.
The file does not state whether management costs sat inside programme lines before 2014, so the
rise cannot be split further. Budget rows from 2005 to 2013 name the two absent categories in
`extra.categories_absent`, and later rows carry the amounts in `mgmt_ops_budget` and
`applied_pipeline`, so a comparison across the step can subtract the categories from the later
year first.

SOME YEARS REPEAT THE YEAR BEFORE TO THE DOLLAR, IN TWO DIFFERENT WAYS

In 2010, every one of the 28 countries present in both 2009 and 2010 repeats its 2009 budget to
the dollar in every programme area. The file does not say whether PEPFAR copied the 2009 plan
into 2010 or planned 2010 at exactly 2009 levels in all 28 countries, so a change of zero from
2009 to 2010 is not evidence that funding was held. In 2016, 2017 and 2018, 24 country budgets
repeat the year before's total while the split between programme areas and Applied Pipeline
moves, often at a round figure such as 17,700,000 dollars for Angola in every year from 2015 to
2018. A split that moves inside an unchanged total is an envelope PEPFAR held flat, so for those
countries the total really was held, although new money inside the envelope can still fall.
PEPFAR's own Total row gives Mozambique 337,075,909 dollars in both 2016 and 2017, while the
Mozambique budget net of Applied Pipeline falls from 330,523,501 to 310,403,040. Every repeating
row carries `extra.repeats_previous_year`, which says whether the whole breakdown or only the
total repeats.

THE COUNTRY COUNT MEASURES ATTRIBUTION, NOT WHERE PEPFAR WORKED

The budget series runs from 14 countries in 2005 to 53 in 2020, and the step from 31 in 2019 to
53 in 2020 is not PEPFAR reaching 22 new countries. Every one of the 22 sits under an operating
unit covering several countries that was already in the file, and the operating unit does not
change across the step. What changes is that PEPFAR starts writing an ISO3 on those rows. Across
the same step the budget on those operating units that carries no ISO3 falls from 79,647,757 to
8,956,546, while the budget on the same operating units that does carry one rises from
46,654,139 to 194,948,927.

An operating unit is treated as regional here when it covers more than one country, which is a
property of the file rather than of the name. Defining regional as an operating unit that
somewhere appears with no ISO3 misses South and Southeast Asia Region, which covers six
countries and carries an ISO3 on every one of its 519 rows, and Thailand is one of the six.

Thailand shows the pattern at country level. The file gives Thailand a budget for 2010 to 2013,
nothing at all for 2014 to 2019, and 21,141,451 in 2020, all of it under the same South and
Southeast Asia Region operating unit. Thailand did not lose its PEPFAR programme in 2014 and
regain it in 2020. Guyana has the same shape, present 2010 to 2016, absent 2017 to 2019, back in
2020, and Myanmar is missing 2015 alone. Those three are the only countries whose emitted series
has a hole in the middle, and the missing years are named on every row of the country in
`extra.series_gap_years`.

Not every rise in the country count is an attribution change. The early rises, from 14 countries
in 2005 to 19 in 2006 and 28 in 2007, look different from the 2020 rise. Eleven of the 14
countries entering in 2006 and 2007 sit under their own single-country operating unit, and rows
with no ISO3 carry no budget at all from 2005 to 2010, so no regional money is waiting to be
attributed. The file still does not say whether those countries were new PEPFAR programmes, so
the log reports the early rises without giving a cause. The runtime log reports every one-year
rise of a quarter or more, because a total compared across such a step covers two different sets
of countries either way, and it adds the attribution reading only where most of the countries
entering are already funded through a regional operating unit and the budget stranded on regional
rows falls across the same step. Of the three rises in the emitted years, only 2019 to 2020 meets
both conditions.

The consequence for this project is direct. An analysis measuring the effect of a funding cut
reads an absent year as a cut, and for the 28 of 55 countries funded through a regional operating
unit an absent year before 2020 means the file does not say. Those countries carry
`extra.funded_through_regional_ou` and `extra.coverage_warning`. The 20 countries that first
appear in 2020 having never appeared before must not be read as programme starts. The two other
countries entering in 2020, Guyana and Thailand, had been present earlier and are the interior
gaps above.

TAGGING: PEPFAR programme spending, not national HIV expenditure. Nominal USD, not deflated.
source_type = expenditure_account.
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

PLANNED = "pepfar_planned_funding"
SPENT = "pepfar_expenditure"

# `pepfar_expenditure` owns FY2021 onward from the partner-level file, which carries the funding
# agency and the mechanism reporting rate that this file cannot supply. The two files are the
# same money, verified to the dollar, so this connector stops where that one starts.
LAST_YEAR = 2020
FIRST_EXPENDITURE_YEAR = 2018

# The 2004 budget column is not a year's budget. It holds 22 rows over 11 countries in two
# programme areas only, and in every one of the 11 countries 70 per cent sits under testing and
# 30 per cent under care and treatment, which is one figure per country divided by a fixed rule.
# Read as planned funding it would show the same 11 countries growing elevenfold in a year.
# Columns before this year are counted and reported in the log, and never emitted.
FIRST_BUDGET_YEAR = 2005

# A budget within this many dollars of the year before is a repeat of that year. The rebuilt
# budget is detail plus Applied Pipeline, each rounded separately in PEPFAR's file, so a country
# total PEPFAR held at exactly 10,000,000 can rebuild as 9,999,999.
REPEAT_TOLERANCE_USD = 2.0

# the three aggregate layers, each identified by the column that gives it away
FOOTER_OU = "total"
TOTAL_PROGRAM = "total"
PIPELINE_PROGRAM = "applied pipeline"

MGMT_OPS = "management and operations"

# PEPFAR's own label for rows it could not attribute to any operating unit. `Invalid` is a
# data-quality bucket, not a region, so the log names the amount separately from real regions.
INVALID_OU = "invalid"

# a reconstruction that misses PEPFAR's own country Total row by more than this share is logged
TOTAL_ROW_TOLERANCE = 0.005

# a one-year rise in the number of countries carrying a budget at least this large is reported,
# because a budget total compared across a step that size covers two different sets of countries
COUNTRY_RISE_SHARE = 0.25

# a rise is attributed to PEPFAR beginning to write an ISO3 on regional rows only when most of
# the countries entering are funded through a regional operating unit and the budget stranded on
# regional rows falls across the same step. The early rises, from 14 countries in 2005 to 28 in
# 2007, meet neither condition, and the file does not say what caused those rises.
ATTRIBUTION_ENTRANT_SHARE = 0.5

# From this year PEPFAR attributes regional-programme money to individual countries. Before it,
# most regional money sits on rows carrying no ISO3, which a country-year panel has to drop. So
# for a country funded through a regional operating unit, absence before this year means the file
# does not say, and never means PEPFAR spent nothing there.
ATTRIBUTION_YEAR = 2020

REGIONAL_WARNING = (
    "This country is funded through a regional operating unit. PEPFAR only began attributing "
    f"regional-programme money to individual countries in {ATTRIBUTION_YEAR}, so any year before "
    f"{ATTRIBUTION_YEAR} in which this country is absent from the series means the file does not "
    "say what it received, not that it received nothing. Do not read the first year present as a "
    "programme start, and do not read an absent year as a cut."
)

INTERPRETATION = (
    "PEPFAR programme spending, not national HIV expenditure, and nominal USD. Budget includes "
    "Applied Pipeline, which is unspent money carried from earlier years and is given separately "
    "in `applied_pipeline`. Read `execution_ratio_excl_mgmt_ops` rather than `execution_ratio`: "
    "Management and Operations holds budget with almost no matching expenditure and drags the "
    "raw ratio down by about ten points. The number of countries present in a year measures how "
    "far PEPFAR attributed regional-programme money to individual countries that year, not where "
    "PEPFAR worked, so an absent year is not evidence of no funding and the first year present is "
    "not a programme start. `categories_absent` names the budget categories the file does not book "
    "in that year at all, so a comparison with a later year should first subtract those categories "
    "from the later year (`mgmt_ops_budget`, `applied_pipeline`). `repeats_previous_year` marks a "
    "budget identical to the dollar to the year before and says which kind of repeat it is. Where "
    "every programme area repeats as well, the file does not distinguish the year from a copied "
    "plan and a change of zero is not evidence that funding was held. Where only the total "
    "repeats, PEPFAR held the country's envelope flat, and new money inside the envelope can still "
    "move as Applied Pipeline moves, which `planned_excl_pipeline` shows."
)

REPEAT_KINDS = {
    "breakdown": "every programme area and Applied Pipeline repeat the year before to the dollar",
    "total": "the total repeats the year before while the split across programme areas changes",
}

# the budget categories that appear partway through the file, by the name the row field uses
LATE_CATEGORIES = (("mgmt_ops", "Management and Operations"), ("pipeline", "Applied Pipeline"))


def _num(cell) -> float:
    """Blank means nothing on this line, not a missing observation. Every money column in this
    file is populated only for the years and programmes a row actually covers."""
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


def _year_columns(cols: List[str]) -> Dict[str, Dict[int, str]]:
    """`2019 BUDGET` and `2019 EXPENDITURE` -> {'budget': {2019: ...}, 'expenditure': {...}}.
    The file is wide and the year lives in the header, so the header is where the period is
    read from. Nothing about the period is inferred from how many columns happen to be present.
    """
    out: Dict[str, Dict[int, str]] = {"budget": {}, "expenditure": {}}
    for c in cols:
        parts = str(c).strip().split()
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        kind = parts[1].lower()
        if kind in out:
            out[kind][int(parts[0])] = c
    return out


class PEPFAROUBudgetsConnector(BaseConnector):
    source_id = "pepfar_ou_budgets"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("PEPFAR budget from 2005 and expenditure from 2018 at operating-unit grain — "
                   "the years before the partner-level file begins.")

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _read_frame(self) -> Optional[pd.DataFrame]:
        if not self.raw_dir.exists():
            log.warning("pepfar_ou_budgets: %s does not exist — download "
                        "PEPFAR_OU_Budgets_and_Expenditures from data.pepfar.gov", self.raw_dir)
            return None

        candidates = [p for p in sorted(self.raw_dir.glob("*.zip"))
                      if "budget" in p.name.lower() and "public_partner" not in p.name.lower()]
        if not candidates:
            log.warning("pepfar_ou_budgets: no PEPFAR_OU_Budgets_and_Expenditures zip in %s",
                        self.raw_dir)
            return None

        for path in candidates:
            try:
                with zipfile.ZipFile(path) as z:
                    members = [m for m in z.namelist()
                               if m.lower().endswith(".txt") and "budget" in m.lower()]
                    skipped = [m for m in z.namelist() if m not in members]
                    if not members:
                        continue
                    with z.open(members[0]) as fh:
                        df = pd.read_csv(fh, sep="\t", dtype=str, on_bad_lines="skip",
                                         low_memory=False)
                    log.info("pepfar_ou_budgets: read %s from %s. Not read: %s",
                             members[0], path.name, skipped or "nothing")
                    return df
            except Exception as exc:
                log.warning("pepfar_ou_budgets: error reading %s: %s", path.name, exc)
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
        ou_c = _ci(cols, "operating unit")
        iso_c = _ci(cols, "iso3")
        cn_c = _ci(cols, "country")
        pg_c = _ci(cols, "program")
        rt_c = _ci(cols, "record type")
        if not (ou_c and iso_c and pg_c):
            log.warning("pepfar_ou_budgets: file lacks Operating Unit / ISO3 / Program — not this "
                        "dataset, nothing emitted")
            return

        years = _year_columns(cols)
        if not years["budget"]:
            log.warning("pepfar_ou_budgets: no `YYYY BUDGET` columns in the header, nothing emitted")
            return

        prog = df[pg_c].fillna("").str.strip().str.lower()
        is_footer = df[ou_c].fillna("").str.strip().str.lower() == FOOTER_OU
        is_total = prog == TOTAL_PROGRAM
        is_pipe = prog == PIPELINE_PROGRAM
        detail = df[~(is_footer | is_total | is_pipe)]
        pipeline = df[is_pipe & ~is_footer]
        totals = df[is_total & ~is_footer]

        # (iso3, year) -> the aggregate. Regional rows carry no ISO3 and a country-year panel has
        # nowhere to put them, so they are counted and dropped rather than spread over a region.
        agg: Dict[tuple, dict] = {}
        names: Dict[str, str] = {}
        dropped_rows = 0
        # The discard has to be measured over the years this connector emits. Counting it in a
        # year left to `pepfar_expenditure` describes a period this connector never reports, and
        # the regional share is not flat across the file: close to 2 per cent from 2014 to 2019
        # and about 0.15 per cent from 2020 on.
        dropped_budget: Dict[int, float] = {}
        dropped_spent: Dict[int, float] = {}
        dropped_invalid = 0.0
        dropped_pipeline = 0.0
        # The share the discard represents has to be measured against the whole file, not against
        # the countries a run happens to ask for. The dropped rows carry no ISO3, so no country
        # filter can reach them, and dividing a file-wide numerator by a filtered denominator
        # would report a different discard for every run.
        file_budget = 0.0
        # which operating units each country is funded through, and which countries each
        # operating unit covers. Both are built over every country in the file rather than the
        # countries a run asks for, because whether an operating unit is regional is a property
        # of the file.
        country_ous: Dict[str, set] = {}
        ou_countries: Dict[str, set] = {}
        # budget columns before FIRST_BUDGET_YEAR, counted file-wide so the log can say what they
        # hold: year -> rows, USD, and each country's budget by programme area
        early: Dict[int, dict] = {}
        # the year each late category first carries budget on a country row, file-wide
        late_first: Dict[str, int] = {}
        late_usd: Dict[str, Dict[int, float]] = {k: {} for k, _ in LATE_CATEGORIES}

        def budget_year(year: int) -> bool:
            return (FIRST_BUDGET_YEAR <= year <= LAST_YEAR
                    and start_year <= year <= end_year)

        def spent_year(year: int) -> bool:
            return year <= LAST_YEAR and start_year <= year <= end_year

        def bucket(iso3: str, year: int) -> dict:
            return agg.setdefault((iso3, year), {
                "planned": 0.0, "spent": 0.0, "pipeline": 0.0,
                "mo_planned": 0.0, "mo_spent": 0.0, "programs": {}, "planned_programs": {},
            })

        for frame, is_pipeline in ((detail, False), (pipeline, True)):
            for _, r in frame.iterrows():
                iso3 = to_iso3(r[iso_c]) if pd.notna(r[iso_c]) else None
                ou_raw = str(r[ou_c]).strip() if pd.notna(r[ou_c]) else ""
                pname = (str(r[pg_c]).strip() or "Not Specified") if not is_pipeline else None

                # the columns before FIRST_BUDGET_YEAR, whether the row has a country or not
                for year, col in years["budget"].items():
                    if year >= FIRST_BUDGET_YEAR or year < start_year or year > end_year:
                        continue
                    v = _num(r[col])
                    if not v:
                        continue
                    e = early.setdefault(year, {"rows": 0, "usd": 0.0, "by_country": {}})
                    e["rows"] += 1
                    e["usd"] += v
                    if iso3 and pname:
                        progs = e["by_country"].setdefault(iso3, {})
                        progs[pname] = progs.get(pname, 0.0) + v

                if not iso3:
                    # Detail and Applied Pipeline are disjoint frames, so both are counted here.
                    # Eight Applied Pipeline rows carry no ISO3 and hold 81,305,868 USD of budget,
                    # which an earlier version of this branch dropped without counting.
                    dropped_rows += 1
                    ou_name = ou_raw.lower()
                    for year, col in years["budget"].items():
                        if not budget_year(year):
                            continue
                        v = _num(r[col])
                        dropped_budget[year] = dropped_budget.get(year, 0.0) + v
                        if is_pipeline:
                            dropped_pipeline += v
                        if ou_name == INVALID_OU:
                            dropped_invalid += v
                    # Applied Pipeline rows carry nothing in any expenditure column, in this file
                    # and on the emitted side alike, so expenditure is read from detail rows only.
                    if not is_pipeline:
                        for year, col in years["expenditure"].items():
                            if not spent_year(year):
                                continue
                            dropped_spent[year] = dropped_spent.get(year, 0.0) + _num(r[col])
                    continue

                is_mo = bool(rt_c and str(r[rt_c]).strip().lower() == MGMT_OPS)

                # everything from here to the country filter is a property of the file and is
                # recorded for every country in it, not only for the countries this run emits
                if ou_raw:
                    country_ous.setdefault(iso3, set()).add(ou_raw)
                    ou_countries.setdefault(ou_raw, set()).add(iso3)
                for year, col in years["budget"].items():
                    if budget_year(year):
                        file_budget += _num(r[col])
                    # When a category first carries budget is a property of the file, so it is
                    # read over every emitted column whatever years this run asks for.
                    late = "pipeline" if is_pipeline else ("mgmt_ops" if is_mo else None)
                    if late and FIRST_BUDGET_YEAR <= year <= LAST_YEAR:
                        v = _num(r[col])
                        if v:
                            late_usd[late][year] = late_usd[late].get(year, 0.0) + v
                            late_first[late] = min(late_first.get(late, year), year)

                if wanted and iso3 not in wanted:
                    continue
                if cn_c and pd.notna(r[cn_c]):
                    names.setdefault(iso3, str(r[cn_c]).strip())

                for year, col in years["budget"].items():
                    if not budget_year(year):
                        continue
                    v = _num(r[col])
                    if not v:
                        continue
                    a = bucket(iso3, year)
                    a["planned"] += v
                    if is_pipeline:
                        a["pipeline"] += v
                    else:
                        a["planned_programs"][pname] = a["planned_programs"].get(pname, 0.0) + v
                        if is_mo:
                            a["mo_planned"] += v

                if is_pipeline:
                    continue
                for year, col in years["expenditure"].items():
                    if not spent_year(year):
                        continue
                    v = _num(r[col])
                    if not v:
                        continue
                    a = bucket(iso3, year)
                    a["spent"] += v
                    if is_mo:
                        a["mo_spent"] += v
                    if pname:
                        a["programs"][pname] = a["programs"].get(pname, 0.0) + v

        self._check_against_total_rows(totals, iso_c, years, agg, wanted, budget_year)

        # An operating unit is regional when it covers more than one country. Defining it as an
        # operating unit that somewhere appears without an ISO3 misses South and Southeast Asia
        # Region, which covers six countries and carries an ISO3 on every one of its 519 rows,
        # and Thailand is one of the six.
        regional_ou_names = {ou for ou, cs in ou_countries.items() if len(cs) > 1}
        regional = {iso3 for iso3, ous in country_ous.items() if ous & regional_ou_names}

        repeats = self._repeats(agg)
        emitted = self._emit(agg, names, regional, self._interior_gaps(agg), late_first, repeats)
        out_of_scope = sorted(y for y in years["budget"] if y > LAST_YEAR)

        drop_b = sum(dropped_budget.values())
        drop_s = sum(dropped_spent.values())
        span = f"{min(y for _, y in agg)}-{max(y for _, y in agg)}" if agg else "no years"
        log.info(
            "pepfar_ou_budgets: %d detail rows read, %d regional rows dropped for having no ISO3 "
            "(%s USD of budget and %s USD of expenditure over %s, %.2f%% of the budget the file "
            "gives countries), %d year columns left to pepfar_expenditure (%s)",
            len(detail), dropped_rows, f"{drop_b:,.0f}", f"{drop_s:,.0f}", span,
            (drop_b / (drop_b + file_budget) * 100) if (drop_b + file_budget) else 0.0,
            len(out_of_scope), ", ".join(str(y) for y in out_of_scope) or "none",
        )
        if dropped_invalid or dropped_pipeline:
            log.info(
                "pepfar_ou_budgets: of that dropped budget, %s USD sits under an operating unit "
                "PEPFAR names `Invalid`, which is a bucket for rows PEPFAR could not attribute "
                "rather than a region, and %s USD is Applied Pipeline carried from earlier years "
                "rather than money appropriated in the year it appears",
                f"{dropped_invalid:,.0f}", f"{dropped_pipeline:,.0f}",
            )
        shown = {i for i, _ in agg}
        flagged = regional & shown
        if flagged:
            log.info(
                "pepfar_ou_budgets: %d of the %d countries emitted are funded through an "
                "operating unit covering more than one country (%s). Their rows carry a warning "
                "that an absent year before %d means the file does not say, not that PEPFAR spent "
                "nothing",
                len(flagged), len(shown),
                ", ".join(sorted({ou for i in flagged for ou in country_ous[i] & regional_ou_names})),
                ATTRIBUTION_YEAR,
            )
        self._report_early_columns(early)
        self._report_late_categories(late_first, late_usd)
        self._report_composition_changes(agg, dropped_budget, regional)
        self._report_repeats(agg, repeats)
        yield from emitted

    # -- basis ------------------------------------------------------------------
    @staticmethod
    def _report_early_columns(early: Dict[int, dict]) -> None:
        """The budget columns before FIRST_BUDGET_YEAR are not emitted, and the log says what
        they hold rather than leaving them out silently. Whether a column is one figure per
        country split by a fixed rule is measured on every run, so a corrected download that
        carries a real programme breakdown shows up here as a spread of shares."""
        for year in sorted(early):
            e = early[year]
            progs = sorted({p for c in e["by_country"].values() for p in c})
            lead = [max(c.values()) / sum(c.values())
                    for c in e["by_country"].values() if sum(c.values())]
            if len(progs) > 1 and lead and max(lead) - min(lead) < 0.001:
                split = (f"the largest programme area takes {min(lead) * 100:.1f}% of every "
                         "country's total, which is one figure per country divided by a fixed "
                         "rule rather than a year's budget")
            elif lead:
                split = (f"the largest programme area takes between {min(lead) * 100:.1f}% and "
                         f"{max(lead) * 100:.1f}% of a country's total")
            else:
                split = "no row in the column carries a country"
            log.info("pepfar_ou_budgets: the %d budget column is not emitted. The %d column holds "
                     "%d rows over %d countries and %s USD, in %d programme areas (%s), and %s",
                     year, year, e["rows"], len(e["by_country"]), f"{e['usd']:,.0f}",
                     len(progs), ", ".join(progs), split)

    @staticmethod
    def _report_late_categories(late_first: Dict[str, int],
                                late_usd: Dict[str, Dict[int, float]]) -> None:
        """A category the file books only from some year on changes what a budget total covers
        from that year. Management and Operations and Applied Pipeline both begin in 2014, so a
        budget compared across 2013 to 2014 changes basis as well as amount."""
        parts = [f"{label} from {late_first[key]} ({late_usd[key][late_first[key]]:,.0f} USD in "
                 f"{late_first[key]})"
                 for key, label in LATE_CATEGORIES
                 if late_first.get(key, FIRST_BUDGET_YEAR) > FIRST_BUDGET_YEAR]
        if not parts:
            return
        log.info("pepfar_ou_budgets: the file books budget under %s, and books no budget under "
                 "those categories in any earlier year. The file does not state whether earlier "
                 "years carried those costs inside programme lines, so a budget compared across "
                 "the step changes basis as well as amount. Rows before the step name the absent "
                 "categories in `categories_absent`, and later rows carry the amounts in "
                 "`mgmt_ops_budget` and `applied_pipeline` wherever the amount is not zero",
                 " and ".join(parts))

    @staticmethod
    def _repeats(agg: Dict[tuple, dict]) -> Dict[tuple, str]:
        """Country-years whose budget equals the year before to within REPEAT_TOLERANCE_USD, by
        what repeats. `breakdown` means every programme area and the Applied Pipeline repeat as
        well, which is how every one of the 28 countries present in both 2009 and 2010 looks,
        and the file does not say whether PEPFAR copied the 2009 plan or planned 2010 at exactly
        2009 levels in every programme area. `total` means the country total repeats while the
        split across programme areas and Applied Pipeline moves, which is PEPFAR holding a
        country's envelope flat, often at a round figure such as 17,700,000 for Angola in every
        year from 2015 to 2018. An analysis measuring the effect of a funding cut reads a change of zero as
        funding held, and only the second kind settles that the envelope was held. New money
        inside a held envelope can still move, because the envelope includes Applied Pipeline."""
        def same(x: float, y: float) -> bool:
            return abs(x - y) <= REPEAT_TOLERANCE_USD

        out: Dict[tuple, str] = {}
        for (iso3, year), a in agg.items():
            prev = agg.get((iso3, year - 1))
            if not (a["planned"] > 0 and prev and prev["planned"] > 0
                    and same(a["planned"], prev["planned"])):
                continue
            progs = set(a["planned_programs"]) | set(prev["planned_programs"])
            copied = same(a["pipeline"], prev["pipeline"]) and all(
                same(a["planned_programs"].get(p, 0.0), prev["planned_programs"].get(p, 0.0))
                for p in progs)
            out[(iso3, year)] = "breakdown" if copied else "total"
        return out

    @staticmethod
    def _report_repeats(agg: Dict[tuple, dict], repeats: Dict[tuple, str]) -> None:
        if not repeats:
            return

        def steps(kind: str) -> str:
            parts = []
            for year in sorted({y for (_, y), k in repeats.items() if k == kind}):
                n = sum(1 for (_, y), k in repeats.items() if y == year and k == kind)
                both = sum(1 for (i, y), a in agg.items()
                           if y == year and a["planned"] > 0
                           and agg.get((i, year - 1), {}).get("planned", 0.0) > 0)
                parts.append(f"{year} in {n} of the {both} countries present in both "
                             f"{year - 1} and {year}")
            return ", ".join(parts)

        copied = sum(1 for k in repeats.values() if k == "breakdown")
        held = len(repeats) - copied
        if copied:
            log.info("pepfar_ou_budgets: %d country budgets repeat the year before to the dollar "
                     "in every programme area and in Applied Pipeline (%s). The file does not say "
                     "whether PEPFAR copied the earlier plan or planned the later year at exactly "
                     "the same levels, so a change of zero across the step is not evidence that "
                     "funding was held. The rows carry `repeats_previous_year`",
                     copied, steps("breakdown"))
        if held:
            log.info("pepfar_ou_budgets: %d further country budgets hold the year before's total "
                     "to the dollar while the split across programme areas and Applied Pipeline "
                     "changes (%s). A split that moves inside an unchanged total is a country "
                     "envelope held flat, so a change of zero across the step is the envelope "
                     "held. New money inside the envelope can still fall or rise as Applied "
                     "Pipeline moves, which `planned_excl_pipeline` shows. The rows carry "
                     "`repeats_previous_year` naming the kind",
                     held, steps("total"))

    # -- composition ------------------------------------------------------------
    @staticmethod
    def _interior_gaps(agg: Dict[tuple, dict]) -> Dict[str, List[int]]:
        """Years missing from the middle of a country's budget series, between its first and its
        last. A hole is not a country PEPFAR had not reached yet, because money resumes after it.
        An analysis measuring the effect of a funding cut reads a hole as a cut, so the years are
        named on the row rather than left for the reader to notice."""
        seen: Dict[str, List[int]] = {}
        for (iso3, year), a in agg.items():
            if a["planned"]:
                seen.setdefault(iso3, []).append(year)
        gaps = {}
        for iso3, yrs in seen.items():
            missing = [y for y in range(min(yrs), max(yrs) + 1) if y not in yrs]
            if missing:
                gaps[iso3] = missing
        return gaps

    @staticmethod
    def _report_composition_changes(agg: Dict[tuple, dict], dropped_budget: Dict[int, float],
                                    regional: set) -> None:
        """A sharp one-year rise in the number of countries carrying a budget means a total
        compared across the step covers two different sets of countries. The validation harness
        warns when coverage falls between years and says nothing when coverage rises, so every
        such rise is reported here.

        Why the rise happened is a separate question and the log answers it only when the
        evidence in this file settles it. In the early rises, from 14 countries in 2005 to 28 in
        2007, 11 of the 14 entrants sit under their own single-country operating units and no
        regional money is waiting to be attributed, and the file says nothing about why those
        countries entered. In the 2019 to 2020 rise, most of the countries entering are already
        funded through an operating unit covering several countries, and the budget stranded on
        regional rows falls across the same step, which is PEPFAR beginning to write an ISO3 on
        rows whose operating unit does not change. The attribution sentence is added only when
        both of those conditions hold."""
        per_year: Dict[int, dict] = {}
        for (iso3, year), a in agg.items():
            if not a["planned"]:
                continue
            s = per_year.setdefault(year, {"countries": set(), "budget": 0.0})
            s["countries"].add(iso3)
            s["budget"] += a["planned"]

        def regional_share(y: int) -> float:
            r = dropped_budget.get(y, 0.0)
            total = r + per_year.get(y, {}).get("budget", 0.0)
            return (r / total * 100) if total else 0.0

        for year in sorted(per_year)[1:]:
            before, now = per_year.get(year - 1), per_year[year]
            if not before or not before["countries"]:
                continue
            entered = now["countries"] - before["countries"]
            if len(entered) / len(before["countries"]) < COUNTRY_RISE_SHARE:
                continue

            from_regional = len(entered & regional)
            was, is_now = regional_share(year - 1), regional_share(year)
            attributed = (from_regional >= ATTRIBUTION_ENTRANT_SHARE * len(entered)
                          and is_now < was)
            because = (
                "Most of the countries entering were already funded through an operating unit "
                f"covering several countries, and the budget stranded on regional rows falls from "
                f"{was:.2f}% to {is_now:.2f}% across the same step. PEPFAR began writing an ISO3 "
                f"on those rows, so the countries entering in {year} are not countries PEPFAR "
                f"reached in {year}."
                if attributed else
                "Whether those countries are new to PEPFAR or newly attributed to a country in "
                "this file is not settled by the file, so a total compared across the step should "
                "be read over the countries present in both years."
            )
            log.info(
                "pepfar_ou_budgets: countries carrying a budget rise from %d in %d to %d in %d, "
                "%d entering, %d of them funded through an operating unit covering more than one "
                "country. %s",
                len(before["countries"]), year - 1, len(now["countries"]), year,
                len(entered), from_regional, because,
            )

    # -- checking ---------------------------------------------------------------
    @staticmethod
    def _check_against_total_rows(totals, iso_c, years, agg, wanted, budget_year) -> None:
        """PEPFAR publishes its own country total on a `Program = Total` row. The budget this
        connector builds should reproduce it, and where it does not the miss is logged with its
        size rather than passed over."""
        misses = 0
        for _, r in totals.iterrows():
            iso3 = to_iso3(r[iso_c]) if pd.notna(r[iso_c]) else None
            if not iso3 or (wanted and iso3 not in wanted):
                continue
            for year, col in years["budget"].items():
                if not budget_year(year):
                    continue
                theirs = _num(r[col])
                mine = agg.get((iso3, year), {}).get("planned", 0.0)
                if theirs <= 0 and mine <= 0:
                    continue
                base = max(theirs, mine)
                if abs(mine - theirs) / base > TOTAL_ROW_TOLERANCE:
                    misses += 1
                    log.warning("pepfar_ou_budgets: %s %d budget rebuilt as %s against "
                                "PEPFAR's own total row of %s",
                                iso3, year, f"{mine:,.0f}", f"{theirs:,.0f}")
        if not misses:
            log.info("pepfar_ou_budgets: every rebuilt country budget matches PEPFAR's own "
                     "Total row within %.1f%%", TOTAL_ROW_TOLERANCE * 100)

    def _emit(self, agg: Dict[tuple, dict], names: Dict[str, str], regional: set,
              gaps: Dict[str, List[int]], late_first: Dict[str, int],
              repeats: set) -> List[PanelRow]:
        rows: List[PanelRow] = []
        for (iso3, year), a in sorted(agg.items()):
            country_name = names.get(iso3, "")
            base: Dict[str, object] = {
                "note": "PEPFAR programme spending, NOT national HIV expenditure. Nominal USD.",
                "grain": "operating unit, no funding-agency split available in this file",
                "interpretation": INTERPRETATION,
            }
            if iso3 in regional:
                base["funded_through_regional_ou"] = True
                base["coverage_warning"] = REGIONAL_WARNING
            if iso3 in gaps:
                base["series_gap_years"] = gaps[iso3]

            if a["planned"] > 0:
                extra = dict(base)
                extra["meaning"] = "budget approved for the year, not money spent"
                if a["pipeline"]:
                    extra["applied_pipeline"] = a["pipeline"]
                    extra["planned_excl_pipeline"] = a["planned"] - a["pipeline"]
                if a["mo_planned"]:
                    extra["mgmt_ops_budget"] = a["mo_planned"]
                absent = [label for key, label in LATE_CATEGORIES
                          if key in late_first and year < late_first[key]]
                if absent:
                    extra["categories_absent"] = absent
                if (iso3, year) in repeats:
                    extra["repeats_previous_year"] = REPEAT_KINDS[repeats[(iso3, year)]]
                rows.append(self.make_row(
                    country_iso3=iso3, country_name=country_name,
                    indicator_id=PLANNED, year=year, value=a["planned"], unit="USD",
                    source_url="https://data.pepfar.gov/datasets",
                    source_indicator_code="PEPFAR OU Budgets and Program Expenditures — BUDGET",
                    extra=extra,
                ))

            if year >= FIRST_EXPENDITURE_YEAR and a["spent"] > 0:
                extra = dict(base)
                if a["mo_spent"] or a["mo_planned"]:
                    extra["mgmt_ops_budget"] = a["mo_planned"]
                    extra["mgmt_ops_expenditure"] = a["mo_spent"]
                if a["planned"] > 0:
                    extra["execution_ratio"] = round(a["spent"] / a["planned"], 3)
                    net_p = a["planned"] - a["mo_planned"]
                    if net_p > 0:
                        extra["execution_ratio_excl_mgmt_ops"] = round(
                            (a["spent"] - a["mo_spent"]) / net_p, 3)
                if a["programs"]:
                    extra["by_program"] = {k: v for k, v in
                                           sorted(a["programs"].items(), key=lambda kv: -kv[1])}
                rows.append(self.make_row(
                    country_iso3=iso3, country_name=country_name,
                    indicator_id=SPENT, year=year, value=a["spent"], unit="USD",
                    source_url="https://data.pepfar.gov/datasets",
                    source_indicator_code="PEPFAR OU Budgets and Program Expenditures — EXPENDITURE",
                    extra=extra,
                ))
        log.info("pepfar_ou_budgets: emitted %d rows over %d countries",
                 len(rows), len({k[0] for k in agg}))
        return rows
