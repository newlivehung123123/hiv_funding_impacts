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
