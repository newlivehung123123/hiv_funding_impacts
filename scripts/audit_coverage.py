#!/usr/bin/env python3
"""What each connector was given, and what each connector actually read.

A clean pipeline run and a rising row count say nothing about whether a connector read
everything it was handed. The failure this script exists to catch is the silent skip, in which
a connector receives a set of inputs, processes the ones it can name, and discards the rest
without reporting a count. The UNAIDS AIDSinfo connector was found reading 32 of 146 exports
while every log line and every validation check stayed green, and the PEPFAR national connector
was found mapping 2 of the 71 indicators inside the one file the connector opens, one of the 69
being TX_NEW, the count of people newly started on antiretroviral therapy, which is the
indicator the whole project is built to measure.

Connectors fail in three different ways and so are audited three different ways.

A DIRECTORY READER is handed a folder and opens the files whose names the connector recognises.
The universe is every file in the folder, the used set is what the connector's own selection
rule returns, and the gap is a list of filenames a person can read.

A WIDE FILE PICKER opens one file holding many indicators and keeps the columns or the indicator
codes named in a dictionary. The universe is every distinct code in the file, the used set is
the dictionary, and the gap is the codes nobody has looked at.

A PULL BY NAME CONNECTOR asks a remote interface for a fixed list of series codes. Such a
connector cannot skip anything, because the connector never sees the catalogue. The blindness is
the reverse one, not knowing what else the publisher offers, and no local measurement can
detect it. Those connectors are listed with the size of the request so the number is at least
visible, and checking the catalogue stays a manual job.

Nothing here fetches anything or writes anything outside the report. Run it as often as the
panel is rebuilt.

    python3 scripts/audit_coverage.py
    python3 scripts/audit_coverage.py --deep    # also opens the large PEPFAR archives
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RAW = ROOT / "data" / "raw"

# Files that document a source rather than carry data. A reference guide left unread is not a
# skip, so naming the extensions here keeps the report free of noise a reader has to dismiss.
DOC_SUFFIXES = {".pdf", ".docx", ".doc", ".txt~", ".md"}


def _fmt_size(n: int) -> str:
    for unit in ("B", "K", "M", "G"):
        if n < 1024 or unit == "G":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}G"


def _rule(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


# --------------------------------------------------------------------------------------
# archetype 1, the directory reader
# --------------------------------------------------------------------------------------

def audit_directory(name: str, subdir: str, used: Iterable[str],
                    note: str = "",
                    declared: Optional[Dict[str, str]] = None) -> Tuple[int, int]:
    """Compare every file in a raw directory against the files a connector opens.

    `used` holds filenames, not patterns, because a pattern is what hides the skip in the first
    place. Writing the names out forces the audit to state which files the connector reads.

    `declared` maps a file nobody reads to the reason it is refused, the way
    unaids_aidsinfo._declared_reason does for exports. A refused file is a decision on the record
    and an unread file is a decision nobody has made, so only the unexamined count needs anyone's
    attention.
    """
    d = RAW / subdir
    if not d.exists():
        print(f"{name:22s} directory {d} absent, nothing to audit")
        return (0, 0)
    files = sorted(p for p in d.iterdir()
                   if p.is_file() and not p.name.startswith(".")
                   and p.suffix.lower() not in DOC_SUFFIXES)
    used_set = set(used)
    declared = declared or {}
    # A file both read and refused is a contradiction in this script, not in the data.
    both = used_set & set(declared)
    if both:
        raise ValueError(f"{name}: named as read and as refused: {sorted(both)}")
    present = {p.name for p in files}
    read = [p for p in files if p.name in used_set]
    refused = [p for p in files if p.name in declared]
    unread = [p for p in files if p.name not in used_set and p.name not in declared]
    print(f"{name:22s} {len(read):3d} of {len(files):3d} files read, {len(refused)} declared "
          f"out of scope, {len(unread)} unexamined" + (f"   [{note}]" if note else ""))
    for p in unread:
        print(f"    unexamined  {p.name}  ({_fmt_size(p.stat().st_size)})")
    for p in refused:
        print(f"    declared  {p.name}  {declared[p.name]}")
    for m in sorted((used_set | set(declared)) - present):
        print(f"    NAMED BUT ABSENT  {m}")
    return (len(read), len(files))


# --------------------------------------------------------------------------------------
# archetype 2, the wide file picker
# --------------------------------------------------------------------------------------

def audit_codes(name: str, codes_present: Counter, mapped: Set[str],
                declared_unmapped: Optional[Set[str]] = None,
                show: int = 25) -> Tuple[int, int]:
    """Compare the codes inside a file against the codes a connector's dictionary names.

    A connector that already lists what the connector deliberately ignores is not silently
    skipping, so `declared_unmapped` is subtracted before anything is reported. Declaring the
    ignored codes is the fix this audit is asking for, and a connector that has done the work
    should not be flagged for having done it.
    """
    declared = declared_unmapped or set()
    unmapped = [(c, n) for c, n in codes_present.most_common()
                if c not in mapped and c not in declared]
    print(f"{name:22s} {len(mapped & set(codes_present)):3d} of {len(codes_present):3d} "
          f"codes mapped, {len(declared & set(codes_present))} declared out of scope, "
          f"{len(unmapped)} unexamined")
    for c, n in unmapped[:show]:
        print(f"    unexamined  {c:44s} {n:8,d} rows")
    if len(unmapped) > show:
        print(f"    ... and {len(unmapped) - show} more")
    return (len(mapped & set(codes_present)), len(codes_present))


def zip_code_counts(path: Path, column: str, sep: str = "\t") -> Counter:
    """Distinct values of one column inside the first data member of a zip archive."""
    import pandas as pd
    cnt: Counter = Counter()
    with zipfile.ZipFile(path) as z:
        members = [m for m in z.namelist()
                   if m.lower().endswith((".txt", ".csv")) and not m.startswith("__")]
        if not members:
            return cnt
        with z.open(members[0]) as fh:
            for chunk in pd.read_csv(fh, sep=sep, dtype=str, usecols=[column],
                                     chunksize=200_000, low_memory=False,
                                     on_bad_lines="skip"):
                cnt.update(chunk[column].dropna())
    return cnt


# --------------------------------------------------------------------------------------
# archetype 3, the pull by name connector
# --------------------------------------------------------------------------------------

def audit_pull(name: str, requested: int, catalogue_note: str) -> None:
    print(f"{name:22s} asks for {requested:3d} named series. "
          f"Catalogue not visible locally: {catalogue_note}")


# --------------------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deep", action="store_true",
                    help="open the large PEPFAR archives to count indicator codes")
    args = ap.parse_args()

    from hivimpact.connectors import (clm_asia, dhs, global_fund, oecd_crs, pepfar_agency,
                                      pepfar_panorama, pepfar_snu, unaids_aidsinfo,
                                      unaids_gam_expenditure, who_gho, who_tme, world_bank)

    print("Connector input coverage")
    print("========================")
    print("Every count below is what the connector was handed against what the connector read.")

    _rule("Directory readers")

    # unaids_aidsinfo classifies by filename stem, so the connector's own rule decides. The
    # connector also names the exports the connector deliberately leaves alone, the way
    # global_fund names the series global_fund leaves alone, so a declared file is reported as
    # a decision rather than counted as a gap. Only the third number needs anyone's attention.
    ua = RAW / "unaids"
    if ua.exists():
        exports = sorted(p for p in ua.iterdir()
                         if p.is_file() and p.suffix.lower() in (".csv", ".xlsx")
                         and not p.name.startswith("."))
        read = [p for p in exports if unaids_aidsinfo._classify(p.stem) is not None]
        rest = [p for p in exports if unaids_aidsinfo._classify(p.stem) is None]
        declared = [p for p in rest if unaids_aidsinfo._declared_reason(p.stem)]
        undecided = [p for p in rest if not unaids_aidsinfo._declared_reason(p.stem)]
        print(f"{'unaids_aidsinfo':22s} {len(read):3d} of {len(exports):3d} exports read, "
              f"{len(declared)} declared out of scope, {len(undecided)} unexamined")
        for p in undecided:
            print(f"    unexamined  {p.name}")
        reasons: Counter = Counter(unaids_aidsinfo._declared_reason(p.stem) for p in declared)
        for reason, n in reasons.most_common():
            print(f"    declared  {n:3d} file(s)  {reason}")

    # Each refusal below rests on a comparison of the file's national totals with the files the
    # panel already reads, for TX_CURR, TX_NEW, HTS_TST and HTS_TST_POS, recorded in
    # docs/ACCESS_LADDER.md section 9w. A file whose totals equal a series already in the panel
    # is a split of that series and adds no new measurement of the country.
    audit_directory(
        "pepfar_*", "pepfar",
        used=["Public_Partner_MER_TopLine.zip",           # pepfar_panorama, pepfar_agency
              "Public_Partner_Budgets_and_Expenditures.zip",  # pepfar_expenditure
              # pepfar_snu, and pepfar_panorama for the check on its national totals
              "Enhanced_Geographical_Analysis.zip",
              "Country_Level_Results_by_Modality_Coarse_Age_and_Sex.zip",  # pepfar_modality
              "PEPFAR_OU_Budgets_and_Expenditures.zip",   # pepfar_ou_budgets
              "PEPFAR_OU_Commodities_Procurements.zip",   # pepfar_commodities
              "HRH_Inventory_Public_Dataset.zip",         # pepfar_hrh
              "Voluntary_Male_Medical_Circumcisions_Results_by_Operating_Unit.zip"],  # pepfar_vmmc
        declared={
            "Operating_Unit_by_Fine_Age_and_Sex.zip":
                "age and sex split of the geographic file's national totals, equal to them "
                "exactly in 1,466 of 1,466 country-indicator-years",
            "Clinical_Cascade_Results_by_Coarse_Age_and_Sex.zip":
                "age and sex split of the geographic file below the country, equal to it "
                "exactly in 1,756 of 2,012 country-indicator-years, every mismatch in FY2016 "
                "to FY2018",
            "Clinical_Cascade_Results_by_Fine_Age_and_Sex.zip":
                "the coarse Cascade file's totals in finer age bands, and the fine bands are "
                "defined differently in different years",
            "Public_Partner_MER_AgeSex.zip":
                "age and sex split of TopLine, equal to pepfar_panorama in 401 of 406 TX_CURR "
                "country-years, and the eight codes TopLine lacks are orphan and vulnerable "
                "children codes that pepfar_panorama declares outside the HIV cascade",
            "Site_Performance_2016-2020.zip":
                "facility split of the geographic file, equal to it exactly in 903 of 934 "
                "country-indicator-years",
            "Site_Performance_2021_plus.zip":
                "facility split of the geographic file, equal to it exactly in 1,080 of 1,080 "
                "country-indicator-years, and a facility that stops reporting cannot be told "
                "apart from one handed to the national government",
        },
        note="nine connectors share one directory")

    audit_directory("foreign_assistance", "foreign_assistance",
                    used=["us_foreign_aid_complete.csv"], note="reads every CSV present")
    audit_directory("south_africa_thembisa", "thembisa", used=["ProvOutputs5_0.xlsx"])

    # data/raw/global_fund holds four manual downloads and no connector opens any of them. The
    # Global Fund connector reads the OData API instead, so calling these files skipped would
    # misdescribe the situation. They are unattached downloads, which is a different problem
    # with the same cause, namely material sitting on disk that nobody decided about.
    audit_directory("(no connector)", "global_fund", used=[],
                    note="global_fund reads the OData API, not this directory")

    _rule("Wide file pickers")

    topline = RAW / "pepfar" / "Public_Partner_MER_TopLine.zip"
    if topline.exists():
        codes = zip_code_counts(topline, "Indicator")
        audit_codes("pepfar_panorama", codes, set(pepfar_panorama.MER_INDICATORS),
                    set(pepfar_panorama.DECLARED_UNMAPPED))
        audit_codes("pepfar_agency", codes, set(pepfar_agency.MER_INDICATORS),
                    set(pepfar_agency.DECLARED_UNMAPPED), show=0)
        # The reasons, tallied, because 60 declared codes are not one decision repeated 60 times.
        # A reader who disagrees with a whole group can find the group here rather than reading
        # the dictionary. "needs a canonical definition" is the group with work left in it.
        groups: Counter = Counter()
        for code in codes:
            reason = pepfar_panorama.DECLARED_UNMAPPED.get(code)
            if reason and code not in pepfar_panorama.MER_INDICATORS:
                if "part of" in reason or "split of" in reason or "leg of" in reason:
                    groups["a part of a code already read, or of one left for a decision"] += 1
                elif "percentage" in reason:
                    groups["canonical is a percentage, needs the Denominator rows"] += 1
                elif "outside the HIV" in reason:
                    groups["outside the HIV testing and treatment cascade"] += 1
                else:
                    groups["needs a canonical definition before it can be mapped"] += 1
        for reason, n in groups.most_common():
            print(f"    declared  {n:3d} code(s)  {reason}")

    # One workbook holding 299 distinct programme labels, of which the connector reads 17.
    # The other 282 answer to declared_reason, so the third number is the only one that
    # needs a decision. Reading the workbook costs a few seconds, the same order as the
    # PEPFAR archive above, and the audit is worth less if it only runs under --deep.
    gam_dir = RAW / "unaids_gam"
    gam_files = sorted(gam_dir.glob("*ProgrammeExpenditures*.xlsx")) if gam_dir.exists() else []
    if gam_files:
        frame = unaids_gam_expenditure.read_workbook(gam_files[-1])
        labels: Counter = Counter(frame["label"])
        read = [lab for lab in labels
                if lab in unaids_gam_expenditure._PROGRAMME or lab == unaids_gam_expenditure._GRAND]
        rest = [lab for lab in labels if lab not in read]
        declared = [lab for lab in rest if unaids_gam_expenditure.declared_reason(lab)]
        undecided = [lab for lab in rest if not unaids_gam_expenditure.declared_reason(lab)]
        print(f"{'unaids_gam_expenditure':22s} {len(read):3d} of {len(labels):3d} programme labels "
              f"read, {len(declared)} declared out of scope, {len(undecided)} unexamined")
        for lab in undecided:
            print(f"    unexamined  {lab[:70]}  ({labels[lab]} rows)")
        reasons = Counter(unaids_gam_expenditure.declared_reason(lab) for lab in declared)
        for reason, n in reasons.most_common():
            print(f"    declared  {n:3d} label(s)  {reason}")

    snu = RAW / "pepfar" / "Enhanced_Geographical_Analysis.zip"
    if snu.exists() and args.deep:
        codes = zip_code_counts(snu, "Indicator")
        audit_codes("pepfar_snu", codes, set(pepfar_snu.MER))

    # global_fund is the model this audit is asking the other connectors to copy. The connector
    # names 24 series, lists the 45 it deliberately leaves alone, and tallies anything that
    # matches neither at run time, so a new indicator appearing in the API is reported instead
    # of dropped. Nothing here can be measured offline and nothing needs to be.
    print(f"{'global_fund':22s} maps {len(global_fund._SERIES):3d} series and declares "
          f"{len(global_fund._UNMAPPED_HIV) + len(global_fund._UNMAPPED_OTHER_DISEASE):3d} "
          f"out of scope.\n{'':22s} Counts the rest at run time. This is the pattern to copy.")

    print(f"{'who_tme':22s} maps {len(who_tme.COLUMNS):3d} columns. The source files download "
          f"at run time, so\n{'':22s} the unmapped column count is not measurable offline. "
          f"Check the WHO TME\n{'':22s} data dictionary by hand.")

    _rule("Pull by name, where the catalogue is invisible by construction")

    audit_pull("who_gho", len(who_gho.GHO_SERIES),
               "GHO publishes roughly 2,000 indicator codes")
    audit_pull("world_bank", len(world_bank.WB_CODES),
               "the World Development Indicators hold about 1,400 series")
    audit_pull("oecd_crs", len(oecd_crs._SERIES),
               "CRS purpose codes are a fixed published list")
    audit_pull("dhs", len(dhs.DHS_INDICATORS),
               "the DHS API exposes several thousand indicator ids")
    audit_pull("clm_asia", len(clm_asia._MAP),
               "the site publishes one dashboard per country")

    print()
    print("What to do with a number in this report")
    print("---------------------------------------")
    print("An unread file is not automatically a loss. An unread file is a decision nobody has")
    print("made yet. Record the decision where the connector lives, the way global_fund records")
    print("the indicators the connector deliberately leaves alone, so the next run of this")
    print("audit reports a choice instead of a gap.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
