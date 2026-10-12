"""
Reconciliation layer — source-aware triangulation over the assembled panel.

The panel deliberately keeps every source's own figure instead of collapsing to one "best"
value. This module compares them, and its central design decision is that **a comparison is
worthless until you know what kind of comparison it is**.

Three relationships exist between two sources reporting the same country-indicator-year:

  derived      Both publish the same underlying estimate. UNAIDS, WHO GHO and the World Bank
               largely republish the same Spectrum output, so agreement between them is
               arithmetic, not corroboration. Counting these as triangulation would
               manufacture confidence the data does not support.
  subset       One measures a part of what the other measures (PEPFAR reports its own
               programme footprint, not the national total). A gap here is expected by
               construction and is not a contradiction.
  independent  Separate measurement systems, with nothing in common upstream (a national
               programme register against a modelled estimate; OECD donor reporting against
               US self-reporting). Only here does a divergence carry information.

A classification is inferred from the data wherever the provenance of the two figures is not
known, and declared in DECLARED_RELATIONSHIPS wherever the provenance is known, because the
numbers alone cannot say whether two figures come from one accounting record. Every
classification is written out with the evidence behind it (cell count, median relative
difference, agreement share, direction consistency) and with a `basis` column saying whether
the verdict was declared or inferred, so the call can be audited or overridden.

Outputs (data/panel/):
  reconciliation_pairs.csv  one row per indicator x source-pair: the relationship map
  reconciliation_cells.csv  cell-level comparisons for INDEPENDENT pairs, divergences flagged
  reconciliation_summary.txt  headline counts

Scope: national rows only (admin1 == ""), matched on country, indicator, population group,
sex, age group and year. Sub-national rows are excluded so regional detail is never compared
against national totals.
"""
from __future__ import annotations

import itertools
import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

log = logging.getLogger("hivimpact")

# --- classification thresholds (explicit, and reported alongside every verdict) ------------
DERIVED_MEDIAN_RELDIFF = 0.01   # near-identical on the typical cell
DERIVED_AGREE_SHARE = 0.90      # ...and near-identical almost everywhere
DERIVED_AGREE_BAND = 0.02
SUBSET_MEDIAN_RATIO = 0.90      # one side systematically smaller
SUBSET_DIRECTION_SHARE = 0.90   # ...consistently, not sporadically
MIN_CELLS = 3                   # below this, decline to classify
DIVERGENCE_FLAG = 0.10          # |relative difference| worth surfacing on an independent pair

# A relative difference is only meaningful when both figures are positive and materially
# sized. Funding series contain zeros, reversals (negative disbursements) and trivial sums;
# comparing $49,423 against $348, or +$14m against -$25m, produces a large ratio that carries
# no information. Such cells are separated out instead of counted as disagreements.
MATERIALITY = {"USD": 1_000_000.0, "count": 100.0, "percent": 1.0}
MATERIALITY_DEFAULT = 0.0

_KEY = ["country_iso3", "indicator_id", "population_group", "sex", "age_group", "year"]

# --- declared provenance -------------------------------------------------------------------
# Item 27. `classify_pairs` reads the relationship off the numbers, and the numbers cannot say
# where a figure came from. Two publications of one accounting record that differ in scope or
# in dating disagree widely enough to fall through the derived and subset tests and land on
# `independent`, which is the verdict that tells a reader the divergence carries information.
# On the panel of 30 September 2026 the Global Fund's own two returns did exactly that, and
# 2,002 cells were counted as independent evidence of a disagreement between one reporter and
# itself.
#
# So a pair whose provenance is known is declared here and read instead of inferred. The key
# is the indicator and the two source identifiers in the order `build_comparisons` sorts them
# into, and the entry carries the reason in prose beside the verdict. Every classified pair
# also reports whether the verdict was declared or inferred, so that a reader can tell one
# from the other without reading this file.
#
# Only what is known goes in. The two `unaids_gam_expenditure` pairs look independent and have
# not been established as independent, so no entry claims either way and both keep an inferred
# verdict until Adrian Smith and the UNAIDS documentation settle the question.
DECLARED_RELATIONSHIPS: Dict[tuple, tuple] = {
    ("global_fund_hiv_disbursements", "iati", "oecd_crs"): (
        "derived",
        "The Global Fund publishes the same disbursements to the IATI registry and to the "
        "OECD Creditor Reporting System, where the Global Fund is reporter 9OTH012, so the "
        "iati and oecd_crs figures for this indicator are two publications of one accounting "
        "record and agreement between them is arithmetic. The two figures differ because the "
        "IATI reading dates money by transaction date while the OECD CRS reading dates money "
        "by reporting year, and because the IATI connector counts the whole value of an H or "
        "C grant where the OECD CRS return carries purpose code 13040 alone. A difference "
        "produced by two treatments of one record is not two measurements disagreeing.",
    ),
    # RESUME.md item 46. Read from data/panel/hiv_panel.csv on 2 October 2026.
    ("on_art_count", "ne_annuaire", "who_gho"): (
        "derived",
        "The Niger health yearbook's national count of people on ART equals the WHO GHO figure "
        "exactly in seven of 12 years from 2013 to 2024, and an exact match on a five-digit "
        "count cannot come from two separate counts. Both figures are the one count of the "
        "national HIV and hepatitis programme (PNLSH), printed in the health ministry's "
        "yearbook and reported to WHO, so agreement is duplication and not corroboration. "
        "RESUME.md item 46 records as findings the years the two publications differ, with "
        "WHO GHO lower in 2016, 2017, 2021 and 2022 and higher by 14 in 2024.",
    ),
    ("on_art_count", "global_fund", "ne_annuaire"): (
        "derived",
        "The Global Fund's reported result for Niger equals the Niger health yearbook's national "
        "count of people on ART exactly in five of the eight years both report from 2017 to "
        "2024, so both figures are the one count of the national HIV and hepatitis programme "
        "(PNLSH), printed in the health ministry's yearbook and reported to the Global Fund as "
        "a grant result. The "
        "Global Fund figure is lower by 4,426 in 2018, higher by 842 in 2022 and lower by 12 in "
        "2024, and RESUME.md item 46 records those three years as findings.",
    ),
    ("on_art_count", "ne_annuaire", "unaids_aidsinfo"): (
        "derived",
        "The UNAIDS AIDSinfo count of people on ART in Niger is the WHO GHO count rounded to the "
        "nearest thousand in every year from 2013 to 2024, and the WHO GHO count is the Niger "
        "health yearbook's national count in seven of those 12 years. The UNAIDS figure is "
        "therefore the national programme's one count, rounded, and agreement with the yearbook "
        "is duplication and not corroboration.",
    ),
    # RESUME.md item 47. Read from data/panel/hiv_panel.csv on 2 October 2026.
    ("pmtct_arv_count", "gn_annuaire", "unaids_aidsinfo"): (
        "derived",
        "The Guinea statistics yearbook's 2023 national count of pregnant women on ARVs, 3,802, "
        "equals the UNAIDS AIDSinfo figure exactly, and an exact four-digit match cannot come "
        "from two separate counts, so both figures are the national health information "
        "system's one count. The evidence is thinner than for Niger, with three shared years, "
        "and the yearbook sits 6 per cent above UNAIDS in 2022 and 16 per cent above UNAIDS in "
        "2024. RESUME.md item 47 records both gaps as findings, because declaring the pair "
        "derived keeps the gaps out of the divergence report.",
    ),
    ("pmtct_arv_count", "gn_annuaire", "who_gho"): (
        "derived",
        "WHO GHO prints the same Guinea count of pregnant women on ARVs as UNAIDS AIDSinfo in "
        "every Guinea year, and the Guinea statistics yearbook's 2023 national count, 3,802, "
        "equals the WHO GHO figure exactly. The WHO GHO pair therefore carries the same single "
        "count as the UNAIDS pair, with the same 2022 and 2024 gaps recorded in RESUME.md item "
        "47. The Global Fund pair is left inferred, because the Global Fund's Guinea results "
        "match the yearbook in no year.",
    ),
}


def load_panel(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "admin1" in df.columns:                      # national totals only
        df = df[df["admin1"].fillna("") == ""]
    df = df[df["value"].notna()].copy()
    for c in ("population_group", "sex", "age_group"):
        if c in df.columns:
            df[c] = df[c].fillna("all")
    return df


def build_comparisons(df: pd.DataFrame) -> pd.DataFrame:
    """Every pairwise comparison of two sources reporting the same cell."""
    rows: List[dict] = []
    for key, g in df.groupby(_KEY, dropna=False):
        g = g.drop_duplicates(subset=["source_id"], keep="first")
        if len(g) < 2:
            continue
        recs = g.set_index("source_id")["value"].to_dict()
        units = g.set_index("source_id")["unit"].to_dict()
        for a, b in itertools.combinations(sorted(recs), 2):
            va, vb = float(recs[a]), float(recs[b])
            denom = (abs(va) + abs(vb)) / 2.0
            rows.append({
                **dict(zip(_KEY, key)),
                "source_a": a, "source_b": b,
                "value_a": va, "value_b": vb,
                "unit": units.get(a) or units.get(b) or "",
                "abs_diff": va - vb,
                "rel_diff": (va - vb) / denom if denom > 0 else None,
                "ratio": (va / vb) if vb not in (0,) else None,
            })
    return pd.DataFrame(rows)


def classify_pairs(cmp_df: pd.DataFrame) -> pd.DataFrame:
    """Infer the relationship for each (indicator, source_a, source_b), with its evidence."""
    out: List[dict] = []
    if cmp_df.empty:
        return pd.DataFrame(out)
    for (ind, a, b), g in cmp_df.groupby(["indicator_id", "source_a", "source_b"]):
        rel = g["rel_diff"].dropna().abs()
        n = len(g)
        med_rel = float(rel.median()) if len(rel) else None
        agree_share = float((rel <= DERIVED_AGREE_BAND).mean()) if len(rel) else None
        ratio = g["ratio"].dropna()
        med_ratio = float(ratio.median()) if len(ratio) else None
        # is one side consistently the smaller one?
        a_smaller = float((g["value_a"] < g["value_b"]).mean())
        direction = max(a_smaller, 1 - a_smaller)

        declared = DECLARED_RELATIONSHIPS.get((ind, a, b))
        if declared is not None:
            verdict = declared[0]
            why = f"declared, not inferred. {declared[1]}"
        elif n < MIN_CELLS:
            verdict, why = "insufficient", f"only {n} overlapping cell(s)"
        elif med_rel is not None and agree_share is not None \
                and med_rel <= DERIVED_MEDIAN_RELDIFF and agree_share >= DERIVED_AGREE_SHARE:
            verdict = "derived"
            why = (f"agree within {DERIVED_AGREE_BAND:.0%} on {agree_share:.0%} of {n} cells "
                   f"(median rel. diff {med_rel:.2%}); same underlying estimate, not corroboration")
        elif med_ratio is not None and direction >= SUBSET_DIRECTION_SHARE and (
                med_ratio <= SUBSET_MEDIAN_RATIO or (med_ratio and 1 / med_ratio <= SUBSET_MEDIAN_RATIO)):
            smaller = a if a_smaller >= 0.5 else b
            verdict = "subset"
            why = (f"{smaller} is smaller in {direction:.0%} of {n} cells "
                   f"(median ratio a/b {med_ratio:.2f}); different scope, gap expected")
        else:
            verdict = "independent"
            why = (f"{n} cells, median rel. diff {med_rel:.1%}; separate measurement systems, "
                   f"divergence is informative")
        out.append({
            "indicator_id": ind, "source_a": a, "source_b": b, "n_cells": n,
            "median_rel_diff": med_rel, "agree_share_within_2pct": agree_share,
            "median_ratio_a_over_b": med_ratio, "direction_consistency": direction,
            "relationship": verdict, "basis": "declared" if declared else "inferred",
            "evidence": why,
        })
    return pd.DataFrame(out).sort_values(["relationship", "indicator_id", "source_a", "source_b"])


def flag_divergences(cmp_df: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Cell-level comparisons for independent pairs only, with material divergences flagged."""
    if cmp_df.empty or pairs.empty:
        return pd.DataFrame()
    indep = pairs[pairs["relationship"] == "independent"][["indicator_id", "source_a", "source_b"]]
    cells = cmp_df.merge(indep, on=["indicator_id", "source_a", "source_b"], how="inner").copy()
    if cells.empty:
        return cells

    floor = cells["unit"].map(lambda u: MATERIALITY.get(u, MATERIALITY_DEFAULT))
    magnitude = cells[["value_a", "value_b"]].abs().max(axis=1)
    opposed = (cells["value_a"] <= 0) | (cells["value_b"] <= 0)

    cells["comparison_status"] = "comparable"
    cells.loc[magnitude < floor, "comparison_status"] = "immaterial"
    cells.loc[opposed, "comparison_status"] = "zero_or_negative"

    # only a comparable cell can be a genuine disagreement
    cells["divergent"] = (cells["comparison_status"] == "comparable") & \
                         (cells["rel_diff"].abs() > DIVERGENCE_FLAG)
    cells = cells.sort_values(["divergent", "rel_diff"],
                              key=lambda s: s.abs() if s.name == "rel_diff" else s,
                              ascending=[False, False])
    return cells


def run(panel: str | Path = "data/panel/hiv_panel.csv",
        outdir: str | Path = "data/panel") -> Dict[str, object]:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = load_panel(panel)
    cmp_df = build_comparisons(df)
    pairs = classify_pairs(cmp_df)
    cells = flag_divergences(cmp_df, pairs)

    pairs.to_csv(outdir / "reconciliation_pairs.csv", index=False)
    if len(cells):
        cells.to_csv(outdir / "reconciliation_cells.csv", index=False)

    # headline counts: how much of the panel's apparent multi-source depth is real
    by_rel = (cmp_df.merge(pairs[["indicator_id", "source_a", "source_b", "relationship"]],
                           on=["indicator_id", "source_a", "source_b"], how="left")
              .groupby("relationship").size().to_dict()) if len(cmp_df) else {}
    n_div = int(cells["divergent"].sum()) if len(cells) else 0
    by_status = cells["comparison_status"].value_counts().to_dict() if len(cells) else {}

    lines = [
        "Reconciliation summary",
        f"panel: {panel}",
        f"national cells compared (pairwise): {len(cmp_df)}",
        "",
        "comparisons by relationship:",
        *[f"  {k:14s} {v}" for k, v in sorted(by_rel.items(), key=lambda x: -x[1])],
        "",
        f"independent pairs: {int((pairs['relationship'] == 'independent').sum())}",
        f"pairs whose relationship was declared and not inferred: "
        f"{int((pairs['basis'] == 'declared').sum())}",
        "",
        "independent-pair cells by comparability:",
        *[f"  {k:18s} {v}" for k, v in sorted(by_status.items(), key=lambda x: -x[1])],
        f"material divergences flagged (comparable cells, |rel diff| > {DIVERGENCE_FLAG:.0%}): {n_div}",
        "",
        "Note: 'derived' comparisons are the same underlying estimate republished and must not",
        "be counted as corroboration. 'subset' comparisons measure different scopes.",
    ]
    (outdir / "reconciliation_summary.txt").write_text("\n".join(lines) + "\n")
    for ln in lines:
        log.info("reconcile: %s", ln)
    return {"comparisons": cmp_df, "pairs": pairs, "cells": cells, "by_relationship": by_rel}


if __name__ == "__main__":   # python -m hivimpact.reconcile
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
