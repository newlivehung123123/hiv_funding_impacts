"""
Write the assembled panel to disk (CSV + Parquet + SQLite) and run light validation.

No cloud DB: a country-year panel is a research artifact, so flat files are
zero-cost, reproducible, and git-diffable. SQLite is included for convenient querying.
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd

from .normalize import name_for
from .schema import PanelRow, PANEL_COLUMNS, utc_now_iso

log = logging.getLogger("hivimpact")


def rows_to_frame(rows: Iterable[PanelRow]) -> pd.DataFrame:
    df = pd.DataFrame([r.to_dict() for r in rows])
    if df.empty:
        return pd.DataFrame(columns=PANEL_COLUMNS)
    for col in PANEL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    # Canonical country_name, derived from the ISO3 identity key. Sources disagree with each
    # other (Burma/Myanmar, Viet Nam/Vietnam, Lao PDR/Lao People's Democratic Republic/Laos)
    # and two of them (WHO GHO, OECD CRS) key purely on ISO3 and supply no name at all. Naming
    # every country once, from one authority, keeps country_name safe to group on; ISO3 remains
    # the join key and no value is altered.
    iso = df["country_iso3"].fillna("").astype(str)
    df["country_name"] = iso.map(lambda c: name_for(c) if c.strip() else "")
    return df[PANEL_COLUMNS]


# Series identity for the two panel-wide checks below: everything except the year.
_SERIES_KEY = ["country_iso3", "admin1", "indicator_id", "population_group",
               "sex", "age_group", "unit", "source_id"]

# A value this many times its own series median is not growth. Gabon's 2024 TB/HIV
# expenditure sits 33,000x its own median because the country reported that row in CFA
# francs into a file whose every other row is USD, and the file carries no currency
# column to catch it. Timor-Leste's 2025 Global Fund budget is 98x its median for the
# same reason.
#
# But a flat ratio cannot be the whole test, and the first version of this check proved
# it by flagging 1,723 rows of the 2026-08-15 panel. Donor disbursement series are
# spiky by nature — Afghanistan's HIV ODA is 17,406 USD in one year and tens of millions
# in another, and neither figure is an error. The check only has power where a series is
# regular enough to have a scale at all, so it now measures that first: the spread is
# taken in log space with a median absolute deviation, and a row has to sit outside the
# series' own habits, not outside a constant. Where a series is genuinely spiky the MAD
# is large and the check stays quiet, which is the correct behaviour and not a miss.
UNIT_OUTLIER_RATIO = 25.0          # the floor: 25x on an otherwise perfectly flat series
UNIT_OUTLIER_MADS = 4.0            # ...or this many MADs out, whichever is wider
MIN_SERIES_FOR_OUTLIER = 5

# ...and the series has to have a stable scale before any of that means anything. A MAD
# of 0.5 in log10 is a typical year-to-year deviation of about three-fold; past that the
# series has no characteristic size and a unit error is indistinguishable from an
# ordinary year. Donor disbursement series live here: OECD CRS reports Afghanistan's HIV
# ODA at 17,406 USD in one year and 9.1m in another, and both are correct. Scaling the
# threshold by the MAD is not enough on its own, because a series with a few real small
# values still has a tight middle — the second version of this check flagged 1,371 rows
# for exactly that reason. So the check declines to speak on an irregular series, the
# same way reconcile.py declines to classify a pair below MIN_CELLS. A missed unit error
# in a spiky series is the price of not burying a real one in a thousand false ones.
SCALE_STABLE_MAD = 0.5

# ...and it has to be a break, not a climb. Distance from the series median cannot tell a
# currency error from a programme that grew: Chad's ART cohort runs 420 -> 50,400 over nine
# years, so its first year sits 120x below its own median and reads as an outlier when it is
# the honest beginning of a scale-up. What separates the two is the year next door. A CFA
# figure in a USD column is 600x its neighbour and the series returns to normal on either
# side of it; a cohort that grows never moves more than a few-fold in one step. So a flagged
# row also has to be a discontinuity against the nearest year in its own series.
#
# A source that switched currency and stayed switched breaks this test after its first bad
# year, because the second bad year's neighbour is the first. That is accepted: the first
# year still flags, the warning names the country, indicator and source, and a human reading
# it will look at the whole series rather than the one row.
UNIT_OUTLIER_STEP = UNIT_OUTLIER_RATIO

# A year-on-year total can fall because values fell or because reporters left, and the
# two look identical in an aggregate. WHO's TB budget file reports USAID funding from 76
# countries in 2024 and 65 in 2025; totalling both gives a 58% fall, while the countries
# that reported in both years fell 35%. The difference is not a rounding matter — it is
# the difference between a finding and an artefact.
REPORTER_DROP_SHARE = 0.15
MIN_REPORTERS = 8

# One exact value repeated across a continuous series is a publication floor wearing the
# costume of a measurement. UNAIDS censors small figures for display — `<100`, `<500`,
# `<0.1`, `>98` — and whoever strips the sign is left with the threshold itself. In the
# 2026-08-15 panel this accounted for twelve series across three sources: 1,294 World Bank
# prevalence rows at exactly 0.1, 1,185 WHO GHO AIDS-death rows at exactly 100 (every one
# of them with value_lower also exactly 100, and Albania's whole early series reading
# lower = value = upper = 100, which is not an interval any model produces), and 273
# UNAIDS expenditure rows at exactly 100 US dollars — South Africa among them, against an
# other-year median of 2.42 billion.
#
# The AIDSinfo connector can fix its own share, because the CSV exports still carry the
# `<`. The WHO and World Bank APIs return the floored number and drop the notation before
# it reaches us, so for those two this warning is the only defence there is: the panel
# stays faithful to what the API returned, and the check says what it means.
#
# Zeros are excluded from the search for the repeated value. A zero repeats legitimately
# all over count data, and the panel already has a rule for reading it (a GAM zero means
# "not reported", not "none").
#
# Excluding zeros from the search but not from the test is what the first version got
# wrong. Dropping them left the smallest printable count as the most common value in every
# small-count series, so the check fired on three WHO TME columns that are not censored at
# all: tbhiv_deaths reads 461 zeros, 315 ones, 179 twos and 98 threes, which is what a
# series of genuinely small counts looks like.
#
# The condition that separates the two shapes is the presence of zeros in the series at
# all. A source that suppresses values below a threshold cannot also print zero, because
# zero is below any positive threshold, and a source that does print zero has already
# published the smallest value there is, so nothing under the repeated value was hidden.
# Measured over the panel, every genuine floor series contains no zeros whatsoever, while
# the three WHO TME columns are between a tenth and a quarter zeros. A small tolerance is
# allowed so that one stray zero cannot switch the check off. The exact tolerance decides
# nothing today, because no series that meets the other two conditions sits between the
# two groups: anything from 1 per cent to 10 per cent gives the same 12 warnings. It is
# set at the tight end deliberately, since a floor that goes unwarned reaches an analysis
# silently while a false warning costs a minute of checking.
#
# One other discriminator was measured and rejected. Censoring piles the suppressed values
# onto the threshold, so it seemed that a floor should stand far above the next value up
# while a small-count series decays smoothly into it. The two classes overlap: UNAIDS
# new_infections is a real floor at 100 whose count is 2.74 times the count at 200, and
# WHO GHO new_infections 2.08 times, against 2.2 for tbhiv_on_art, which is not censored.
# Any threshold that keeps the real floors admits the false ones.
FLOOR_SHARE = 0.05
FLOOR_MIN_COUNTRIES = 5
FLOOR_MIN_ROWS = 50
FLOOR_MAX_ZERO_SHARE = 0.01  # a censoring source does not print zero


def _unit_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Rows whose value is out of scale with the rest of their own series.

    Everything happens in log space, because a unit error is multiplicative: reporting
    CFA francs into a USD column multiplies by roughly 600 whatever the underlying
    figure was. The median and the median absolute deviation are the reference because
    both survive the outlier they are being used to find.

    Both directions are checked, and the returned frame says which one in `_direction`,
    because the two do not mean the same thing. A row far above its own series is the
    unit error this check was written for. A row far below it almost never is: in the
    WHO TME money and cascade columns the low side is a partial report or a rounding
    floor — South Africa's 2021 TB/HIV figures are 42 and 37 against a normal 150,000,
    which is a reporting collapse in the second COVID year and not a currency mistake.
    Both belong in the warnings; calling both a unit mismatch sends the reader to look
    for the wrong fault.

    Three conditions have to hold together, and each one exists to silence a class of
    false positive the previous version produced: the series must have a stable scale,
    the row must sit outside that scale, and it must be a break from the year next door
    rather than a point on a trend.
    """
    import numpy as np

    d = df.copy()
    d["_v"] = pd.to_numeric(d["value"], errors="coerce")
    # Negatives are left alone. In OECD CRS a negative disbursement is a reflow or a
    # correction, which is a real thing the source published and not a unit error, and
    # taking its absolute value here would file it as one.
    d = d[d["_v"] > 0]
    if d.empty:
        return d.iloc[0:0]

    d = d.sort_values(_SERIES_KEY + ["year"])
    d["_l"] = np.log10(d["_v"])
    keys = [d[c] for c in _SERIES_KEY]
    g = d.groupby(_SERIES_KEY, dropna=False)["_l"]
    med = g.transform("median")
    n = g.transform("size")
    dev = (d["_l"] - med).abs()
    # MAD of the series, expressed in the same log units as dev.
    mad = dev.groupby(keys, dropna=False).transform("median")

    # Distance to the nearest year on either side, within the series. A row at the end of
    # a series has one neighbour; the fillna keeps it comparable to rows that have two.
    back = (d["_l"] - g.shift(1)).abs()
    fwd = (d["_l"] - g.shift(-1)).abs()
    step = pd.concat([back, fwd], axis=1).min(axis=1, skipna=True)

    floor = np.log10(UNIT_OUTLIER_RATIO)
    threshold = np.maximum(floor, UNIT_OUTLIER_MADS * mad)
    hit = ((n >= MIN_SERIES_FOR_OUTLIER)
           & (mad <= SCALE_STABLE_MAD)          # the series has a scale to depart from
           & (dev > threshold)                  # the row departs from it
           & (step > np.log10(UNIT_OUTLIER_STEP)))  # and it is a break, not a climb
    out = d[hit].copy()
    out["_direction"] = np.where(out["_l"] > med[hit], "high", "low")
    return out


def _floor_values(df: pd.DataFrame) -> List[str]:
    """Series where one exact non-zero value recurs often enough to be a publication limit.

    A repeated value on its own is not evidence of censoring, so two things have to hold
    together: the value has to be common across countries, and the series must not contain
    zeros. The reasoning behind the second condition, and the measurement that set it, are
    with the constants above.

    Where the repeated value sits in its own series decides what the repetition means, and
    for eight months this check called every one of them a floor. AIDSinfo censors at both
    ends. `<100` puts a display floor under a small count, and `>98` puts a ceiling over a
    cascade percentage that reached its target, so 148 rows of WHO GHO viral suppression at
    exactly 98 and 141 rows of UNAIDS PMTCT coverage at exactly 98 were reported as floors
    when 98 is the largest value either series contains. A reader who believed the label
    would have concluded those countries were being rounded up from nothing.

    The three cases separate completely on the panel of 2026-09-05. The repeated value is
    the series minimum (censoring floor), or its maximum (reporting ceiling), or neither,
    which is UNAIDS stacking two notations in one file: on_art_count repeats 500 with 167
    rows below it, because `<100` and `<500` are both in use.
    """
    out: List[str] = []
    d = df.copy()
    d["_v"] = pd.to_numeric(d["value"], errors="coerce")
    d = d[d["_v"].notna()]
    if d.empty:
        return out

    found = []
    for (ind, src), whole in d.groupby(["indicator_id", "source_id"], dropna=False):
        # Zeros count towards the series but never towards the candidate value.
        zero_share = float((whole["_v"] == 0).mean())
        part = whole[whole["_v"] != 0]
        if len(part) < FLOOR_MIN_ROWS or zero_share > FLOOR_MAX_ZERO_SHARE:
            continue
        counts = part["_v"].value_counts()
        val, cnt = counts.index[0], int(counts.iloc[0])
        share = cnt / len(part)
        n_countries = part.loc[part["_v"] == val, "country_iso3"].nunique()
        if share >= FLOOR_SHARE and n_countries >= FLOOR_MIN_COUNTRIES:
            if val == part["_v"].min():
                kind = "a censoring floor"
            elif val == part["_v"].max():
                kind = "a reporting ceiling"
            else:
                kind = "a censoring limit with other values below it"
            found.append((share, cnt, len(part), n_countries, ind, src, val, kind))

    for share, cnt, total, n_countries, ind, src, val, kind in sorted(found, reverse=True):
        out.append(
            f"{ind}/{src}: value {val:g} repeats {cnt} times ({share:.0%} of {total} rows, "
            f"{n_countries} countries) — likely {kind}, not a measurement"
        )
    return out


def _periodic_stride(years: List[int]) -> Optional[int]:
    """The stride of a series published on a cycle longer than a year, else None.

    An allocation cycle is the case this exists for. The Global Fund communicates one
    allocation per country per three-year cycle, so `global_fund_hiv_allocation_cycle`
    holds 2017, 2020, 2023 and 2026 and holds nothing in between, and the empty years are
    correct and not a reporting gap. Three observed years are the fewest that can establish
    a stride, because two years establish a distance and nothing more, and a series whose
    observed years are unevenly spaced is read as annual with gaps.
    """
    if len(years) < 3:
        return None
    steps = {b - a for a, b in zip(years[:-1], years[1:])}
    if len(steps) == 1:
        step = steps.pop()
        if step > 1:
            return step
    return None


def _source_current_years(d: pd.DataFrame) -> Dict[str, int]:
    """The latest year more than half of each source's own series reach.

    The plain maximum will not do. WHO's TB data publishes four forward-looking budget
    series a year ahead of every measured series, so the plain maximum for `who_tme` is
    2025 while 13 of 17 `who_tme` series stop at 2024, and reading 2025 as that source's
    current year would report all 13 as withdrawn. A majority of the source's series is the
    test, so one series published ahead of the rest cannot make the rest look truncated.
    """
    now: Dict[str, int] = {}
    for src, part in d.groupby("source_id", dropna=False):
        n_series = int(part["indicator_id"].nunique())
        per_year = part.groupby("year")["indicator_id"].nunique()
        reached = [int(y) for y, n in per_year.items() if int(n) * 2 > n_series]
        now[src] = max(reached) if reached else int(part["year"].max())
    return now


def _reporter_drops(df: pd.DataFrame) -> List[str]:
    """Three ways a series loses reporters, all of them walked along the calendar.

    Reported as warnings and not corrections: the panel keeps what each source published,
    and it is the comparison that has to be made on a balanced set, not the data that has to
    be trimmed. The warnings exist so nobody totals two years of a changed reporter set and
    reads the difference as a change in the world.

    A fall is a year-on-year drop in the reporting countries. An interior gap is a year the
    series skips entirely and then resumes after. A stopped series is one that ends while the
    source it comes from goes on publishing.

    The walk is along the calendar and not along the years the series happens to hold, and
    the difference matters three times over. A missing year raises nothing at all under a
    walk over the years present, which is how the Global Fund's absent 2025 HIV testing
    result reached the panel without a single warning. Two years either side of a gap print
    as though the years were adjacent, which is how `late_hiv_diagnosis_pct/unaids_aidsinfo`
    came to report 70 countries in 2020 falling to 19 in 2024 with no mention of 2021, 2022
    and 2023 holding nothing. A series that simply stops is invisible to a walk over the
    years present, because a walk over the years present has nowhere left to step.
    """
    out: List[str] = []
    d = df.dropna(subset=["value"])
    if d.empty:
        return out
    source_now = _source_current_years(d)
    for (ind, src), part in d.groupby(["indicator_id", "source_id"], dropna=False):
        counts = part.groupby("year")["country_iso3"].nunique().sort_index()
        have = {int(y): int(counts[y]) for y in counts.index}
        years = sorted(have)
        stride = _periodic_stride(years)
        step = stride or 1
        first, last = years[0], years[-1]

        for prev_year in range(first, last, step):
            this_year = prev_year + step
            before, after = have.get(prev_year, 0), have.get(this_year, 0)
            if before < MIN_REPORTERS:
                continue
            if after == 0:
                # The gap runs to the next year the series holds, and the count on the far
                # side of the gap is stated because a gap can hide a fall. The warning above
                # about late_hiv_diagnosis_pct is exactly that case.
                resumes = next((y for y in years if y > this_year), None)
                if resumes is None:  # a trailing gap, handled after the walk
                    continue
                empty = (f"{this_year}" if resumes - this_year == step
                         else f"{this_year} to {resumes - step}")
                out.append(
                    f"{ind}/{src}: {before} reporting countries in {prev_year}, none in "
                    f"{empty}, {have[resumes]} again in {resumes}, so the years either side "
                    f"of the gap are not comparable and the gap is not a fall"
                )
                continue
            if after >= before:
                continue
            if (before - after) / before >= REPORTER_DROP_SHARE:
                out.append(
                    f"{ind}/{src}: reporting countries {before} ({prev_year}) -> "
                    f"{after} ({this_year}); compare on the {after} reporting both years"
                )

        now = source_now.get(src, last)
        if now - last >= step and have[last] >= MIN_REPORTERS:
            out.append(
                f"{ind}/{src}: {have[last]} reporting countries in {last} and nothing after "
                f"{last}, while {src} reaches {now} across most of its series, so check "
                f"whether the series was withdrawn, renamed or published on a later calendar"
            )
    return out


def validate(df: pd.DataFrame) -> List[str]:
    """Return a list of human-readable validation warnings (does not raise)."""
    warns: List[str] = []
    if df.empty:
        return ["panel is empty"]

    missing_prov = df[(df["source_url"].fillna("") == "") | (df["source_id"].fillna("") == "")]
    if len(missing_prov):
        warns.append(f"{len(missing_prov)} rows missing provenance (source_url/source_id)")

    bad_year = df[(df["year"] < 1990) | (df["year"] > 2035)]
    if len(bad_year):
        warns.append(f"{len(bad_year)} rows with implausible year (<1990 or >2035)")

    # percent indicators should sit in [0, 100] (allow small overshoot for rounding)
    pct = df[df["unit"] == "percent"]
    bad_pct = pct[(pd.to_numeric(pct["value"], errors="coerce") < 0)
                  | (pd.to_numeric(pct["value"], errors="coerce") > 105)]
    if len(bad_pct):
        warns.append(f"{len(bad_pct)} percent-unit rows outside [0,105]")

    # bounds sanity: lower <= value <= upper when all present
    b = df.dropna(subset=["value", "value_lower", "value_upper"])
    inverted = b[(pd.to_numeric(b["value_lower"], errors="coerce")
                  > pd.to_numeric(b["value_upper"], errors="coerce"))]
    if len(inverted):
        warns.append(f"{len(inverted)} rows with value_lower > value_upper")

    dups = df.duplicated(
        subset=["country_iso3", "admin1", "indicator_id", "population_group", "sex", "age_group", "year", "source_id"],
        keep=False,
    )
    if dups.any():
        warns.append(f"{int(dups.sum())} duplicate (country,indicator,pop,sex,age,year,source) rows")

    # A row reported in the wrong unit. Grouped by indicator and source rather than listed
    # flat, because what these rows mean depends on how they cluster: a handful scattered
    # across many series is the ordinary small change of donor reporting, while a stack of
    # them in one series is a fault in how that series was read. The clustering is what
    # exposed the censoring floors — 273 flagged rows all in one money series, all with the
    # same value.
    out = _unit_outliers(df)
    for direction, reading in (("high", "possible currency/unit mismatch"),
                               ("low", "possible partial or non-report")):
        part = out[out["_direction"] == direction] if len(out) else out
        if not len(part):
            continue
        warns.append(f"{len(part)} rows far {'above' if direction == 'high' else 'below'} "
                     f"the scale of their own series ({reading}), by series:")
        grouped = (part.groupby(["indicator_id", "source_id"], dropna=False)
                       .size().sort_values(ascending=False))
        for (ind, src), n in grouped.head(10).items():
            ex = part[(part["indicator_id"] == ind) & (part["source_id"] == src)].iloc[0]
            warns.append(f"    {n:>4}  {ind} [{src}]  e.g. {ex['country_iso3']} {ex['year']} "
                         f"= {ex['value']!r} {ex['unit']}")
        if len(grouped) > 10:
            warns.append(f"    ... and {len(grouped) - 10} further series")

    warns.extend(_floor_values(df))
    warns.extend(_reporter_drops(df))

    return warns


def write_panel(rows: Iterable[PanelRow], outdir: str | Path, basename: str = "hiv_panel") -> pd.DataFrame:
    return write_frame(rows_to_frame(rows), outdir, basename)


def write_frame(df: pd.DataFrame, outdir: str | Path, basename: str = "hiv_panel") -> pd.DataFrame:
    """Write an already-assembled panel frame. Kept separate from `write_panel` so a run that
    covers only some sources can merge its rows into the panel already on disk before writing,
    instead of replacing a full panel with a partial one."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # stable sort for reproducible diffs
    if not df.empty:
        df = df.sort_values(
            ["country_iso3", "admin1", "indicator_id", "population_group", "sex", "age_group", "year", "source_id"]
        ).reset_index(drop=True)

    csv_path = outdir / f"{basename}.csv"
    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(outdir / f"{basename}.parquet", index=False)
    except Exception as exc:  # pyarrow missing or serialization issue
        log.warning("parquet write skipped: %s", exc)

    with sqlite3.connect(outdir / f"{basename}.sqlite") as conn:
        df.to_sql("panel", conn, if_exists="replace", index=False)

    warns = validate(df)
    log.info("wrote %d rows to %s (exported_at %s)", len(df), csv_path, utc_now_iso())
    for w in warns:
        log.warning("VALIDATION: %s", w)

    (outdir / f"{basename}.validation.txt").write_text(
        f"exported_at: {utc_now_iso()}\nrows: {len(df)}\n" + "\n".join(f"- {w}" for w in warns) + "\n"
    )
    return df
