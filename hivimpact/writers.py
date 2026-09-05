"""
Write the assembled panel to disk (CSV + Parquet + SQLite) and run light validation.

No cloud DB: a country-year panel is a research artifact, so flat files are
zero-cost, reproducible, and git-diffable. SQLite is included for convenient querying.
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Iterable, List

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
# Zeros are excluded. A zero repeats legitimately all over count data, and the panel
# already has a rule for reading it (a GAM zero means "not reported", not "none").
FLOOR_SHARE = 0.05
FLOOR_MIN_COUNTRIES = 5
FLOOR_MIN_ROWS = 50


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
    """Series where one exact non-zero value recurs often enough to be a publication floor."""
    out: List[str] = []
    d = df.copy()
    d["_v"] = pd.to_numeric(d["value"], errors="coerce")
    d = d[d["_v"].notna() & (d["_v"] != 0)]
    if d.empty:
        return out

    found = []
    for (ind, src), part in d.groupby(["indicator_id", "source_id"], dropna=False):
        if len(part) < FLOOR_MIN_ROWS:
            continue
        counts = part["_v"].value_counts()
        val, cnt = counts.index[0], int(counts.iloc[0])
        share = cnt / len(part)
        n_countries = part.loc[part["_v"] == val, "country_iso3"].nunique()
        if share >= FLOOR_SHARE and n_countries >= FLOOR_MIN_COUNTRIES:
            found.append((share, cnt, len(part), n_countries, ind, src, val))

    for share, cnt, total, n_countries, ind, src, val in sorted(found, reverse=True):
        out.append(
            f"{ind}/{src}: value {val:g} repeats {cnt} times ({share:.0%} of {total} rows, "
            f"{n_countries} countries) — likely a censoring floor, not a measurement"
        )
    return out


def _reporter_drops(df: pd.DataFrame) -> List[str]:
    """Series where the set of reporting countries shrinks sharply between two years.

    Reported as a warning and not a correction: the panel keeps what each source
    published, and it is the comparison that has to be made on a balanced set, not the
    data that has to be trimmed. The warning exists so nobody totals two years of a
    changed reporter set and reads the difference as a change in the world.
    """
    out: List[str] = []
    d = df.dropna(subset=["value"])
    if d.empty:
        return out
    for (ind, src), part in d.groupby(["indicator_id", "source_id"], dropna=False):
        counts = part.groupby("year")["country_iso3"].nunique().sort_index()
        for prev_year, this_year in zip(counts.index[:-1], counts.index[1:]):
            before, after = int(counts[prev_year]), int(counts[this_year])
            if before < MIN_REPORTERS or after >= before:
                continue
            if (before - after) / before >= REPORTER_DROP_SHARE:
                out.append(
                    f"{ind}/{src}: reporting countries {before} ({prev_year}) -> "
                    f"{after} ({this_year}); compare on the {after} reporting both years"
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
