#!/usr/bin/env python3
"""
Run the Phase-1 aggregator connectors and assemble the panel.

  >>> YOU run this (research-data collection stays with the researcher).

Examples:
    python scripts/run_all.py                       # SEA slice (Phase 1.1), 2000-2025, all sources
    python scripts/run_all.py --countries all       # every country the sources publish
    python scripts/run_all.py --sources world_bank,who_gho --countries sea
    python scripts/run_all.py --start 2010 --end 2025 --out data/panel

Each connector is isolated: if one source fails, the others still produce a panel.
UNAIDS requires you to first export CSVs into data/raw/unaids/ (see that connector's
docstring / README). Without those files the UNAIDS connector simply contributes
nothing (and says so) instead of failing the run.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hivimpact.connectors import CONNECTORS
from hivimpact.config.countries import resolve_country_set
from hivimpact.writers import rows_to_frame, write_frame
from hivimpact import mou_tracker
from hivimpact import reconcile


def _align_dtypes(a: pd.DataFrame, b: pd.DataFrame):
    """Give an all-empty column the dtype its counterpart already has.

    read_csv types a column that is blank in every row as float64, while a connector that
    never fills it hands back objects full of None (`value_lower`, `numerator` and
    `denominator` are the usual ones). Concatenating those two is what raises pandas'
    "empty or all-NA entries" FutureWarning on every partial run. Nothing here changes a
    value — an all-empty column has none — it only settles which dtype the merged column
    gets, now and not when pandas changes the default under us.
    """
    a, b = a.copy(), b.copy()
    for col in set(a.columns) & set(b.columns):
        if a[col].dtype == b[col].dtype:
            continue
        if a[col].isna().all():
            a[col] = a[col].astype(b[col].dtype)
        elif b[col].isna().all():
            b[col] = b[col].astype(a[col].dtype)
    return [a, b]


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble the HIV-impact aggregator panel (Phase 1).")
    ap.add_argument("--sources", default="all",
                    help="comma list of source_ids or 'all' (%s)" % ",".join(CONNECTORS))
    ap.add_argument("--countries", default="sea", help="'sea' | 'all' | comma list of ISO3")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2025)
    ap.add_argument("--out", default="data/panel")
    ap.add_argument("--basename", default="hiv_panel")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )
    log = logging.getLogger("hivimpact")
    log.setLevel(logging.INFO)

    countries = resolve_country_set(args.countries)
    source_ids = list(CONNECTORS) if args.sources == "all" else [s.strip() for s in args.sources.split(",")]

    all_rows = []
    per_source = {}
    for sid in source_ids:
        cls = CONNECTORS.get(sid)
        if cls is None:
            log.warning("unknown source '%s' — skipping (known: %s)", sid, ", ".join(CONNECTORS))
            continue
        log.info("=== %s : %s ===", sid, cls.description)
        try:
            rows = list(cls().fetch(countries=countries, start_year=args.start, end_year=args.end))
        except Exception as exc:
            log.exception("connector %s failed: %s", sid, exc)
            per_source[sid] = "FAILED"
            continue
        per_source[sid] = len(rows)
        all_rows.extend(rows)
        log.info("%s produced %d rows", sid, len(rows))

    # Before anything is written: keep one step back, and work out what this run is about to
    # remove from the panel.
    new_df = rows_to_frame(all_rows)
    ran_clean = {sid for sid, n in per_source.items() if n != "FAILED"}
    lost_series: list[tuple[str, int]] = []   # sources that had rows on disk and returned none
    panel_csv = Path(args.out) / f"{args.basename}.csv"
    prev_csv = panel_csv.with_suffix(".prev.csv")
    prev = pd.read_csv(panel_csv, low_memory=False) if panel_csv.exists() else None

    if prev is not None:
        # One step back before anything is overwritten, whether this run is partial or full.
        # Re-collecting the whole panel costs a slow pass over several APIs and a 3.5 GB file
        # scan, so the previous state is worth a megabyte on disk.
        prev.to_csv(prev_csv, index=False)

        # A source that used to carry rows and now carries none is either a withdrawn series or
        # an upstream outage, and from here the two look the same. OECD's SDMX service returning
        # 500 for every dataflow would empty the external-financing series without a single
        # error, so it gets said in the summary and not only in a log line that scrolls past.
        for sid in sorted(ran_clean):
            had = int((prev["source_id"] == sid).sum())
            now = int((new_df["source_id"] == sid).sum()) if not new_df.empty else 0
            if had and not now:
                lost_series.append((sid, had))
                log.warning("%s returned 0 rows but the panel on disk held %d — those rows are "
                            "being DROPPED. If this is an upstream outage and not a withdrawn "
                            "series, restore from %s before using the panel.", sid, had, prev_csv)

    # A run that names only some sources must not replace the panel with its own rows alone.
    # `--sources pepfar_agency` means "refresh this one source", and every other source's rows
    # have to survive it. So a partial run merges: the rows of the sources that just ran are
    # replaced, and everything else on disk is kept. A source that RAISED keeps its old rows,
    # because a timed-out API is not evidence that the data is gone.
    if args.sources != "all" and prev is not None:
        keep = prev[~prev["source_id"].isin(ran_clean)]
        log.info("partial run (%s): merging into the %d rows already in %s; previous panel "
                 "saved to %s", ",".join(sorted(ran_clean)), len(prev), panel_csv.name,
                 prev_csv.name)
        # Concatenating an empty frame is how a source that returned nothing gets merged, and
        # pandas warns that it will stop inferring dtypes from the non-empty side. Drop the
        # empty side instead of relying on behaviour that is on its way out.
        parts = [p for p in (keep, new_df) if not p.empty]
        if len(parts) == 2:
            parts = _align_dtypes(*parts)
        new_df = pd.concat(parts, ignore_index=True) if parts else new_df.iloc[0:0]

    df = write_frame(new_df, args.out, args.basename)

    # Policy-exposure table, written alongside the panel (separate file: an MOU is a dated
    # EVENT with committed amounts, not a country-indicator-year measurement). Join on
    # country_iso3. Failure here must never invalidate the panel above.
    mou_path = None
    try:
        log.info("=== mou_tracker : America First bilateral global-health MOUs (policy exposure) ===")
        mou_path = mou_tracker.run(args.out)
    except Exception as exc:
        log.warning("mou_tracker failed: %s", exc)

    # The reconciliation tables are a reading of the panel, so a panel written without them
    # rewritten leaves the two disagreeing and nothing says so. They sat at 20 July 2026 while
    # the panel moved on through four connectors, and the site kept publishing the July verdicts
    # beside a September panel. Regenerate here, where the panel has just been written, rather
    # than trusting anyone to remember a second command. Failure must not invalidate the panel.
    recon_stats = None
    try:
        log.info("=== reconcile : which sources measure the same thing, declared where the "
                 "provenance is known and inferred from the numbers where it is not ===")
        recon_stats = reconcile.run(str(panel_csv), args.out)
    except Exception as exc:
        log.warning("reconcile failed, so the tables in %s are older than the panel: %s",
                    args.out, exc)

    # -- summary ---------------------------------------------------------------
    print("\n================ RUN SUMMARY ================")
    print(f"countries : {args.countries}   years: {args.start}-{args.end}")
    for sid in source_ids:
        print(f"  {sid:18s}: {per_source.get(sid, 0)} rows")

    # Loud, and above the row counts a reader skims past. A source silently going to zero is the
    # failure mode that does the most damage here, because the panel still looks well formed.
    if lost_series:
        print("\n  *** SERIES LOST THIS RUN ***")
        for sid, had in lost_series:
            print(f"  {sid:18s}: returned 0 rows, {had} rows dropped from the panel")
        print(f"  previous panel kept at {prev_csv} — restore it if this was an upstream outage")
    print(f"  TOTAL             : {len(df)} rows")
    if not df.empty:
        print("\nrows by indicator:")
        for ind, n in df.groupby("indicator_id").size().sort_values(ascending=False).items():
            print(f"  {ind:24s} {n}")
        print(f"\ncountries covered: {df['country_iso3'].nunique()}   "
              f"years: {df['year'].min()}-{df['year'].max()}")
    print(f"\nwritten to: {args.out}/{args.basename}.[csv|parquet|sqlite]")
    if mou_path:
        print(f"policy exposure: {mou_path} (join to the panel on country_iso3)")
    if recon_stats is not None:
        pairs_df = recon_stats["pairs"]
        counts = pairs_df["relationship"].value_counts().to_dict()
        print("\nreconciliation: {} source pairs — {}".format(
            len(pairs_df), ", ".join(f"{n} {rel}" for rel, n in sorted(counts.items(),
                                                                      key=lambda x: -x[1]))))
        # A `derived` pair is one source reprinting another, so counting it as agreement between
        # two sources is the error this table exists to prevent.
        der = pairs_df[pairs_df["relationship"] == "derived"]
        for _, r in der.iterrows():
            print(f"  derived, so NOT corroboration: {r['indicator_id']} "
                  f"({r['source_a']} = {r['source_b']}, {int(r['n_cells'])} cells)")
    else:
        print("reconciliation: NOT regenerated this run, so the tables in "
              f"{args.out} are older than the panel")
    print("validation: see {}/{}.validation.txt".format(args.out, args.basename))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
