#!/usr/bin/env python3
"""
Turn the ForeignAssistance.gov Complete Data Set into the small frozen history the
foreign_assistance connector reads for the years the IATI route cannot supply.

RUN THIS ONCE. The output belongs in the repository and the 3.7 gigabyte input does not.

WHY THE FILE EXISTS

foreignassistance.gov answers every non-browser client with HTTP 403 and the header
`cf-mitigated: challenge`, so the Complete Data Set can only be downloaded by hand. The
connector now reads the same transactions as IATI XML from Amazon S3 instead, which is
outside the challenge and needs no manual step. The S3 route reproduces
ForeignAssistance.gov's own API exactly for the State Department from FY2012, for Health and
Human Services from FY2012, and for USAID from FY2020, and falls short before those years.
So the early years come from the hand-downloaded file, extracted once into something small
enough to commit, and after that nothing is downloaded by hand again.

WHAT IT KEEPS

Disbursements only, never obligations. HIV rows by the same test the XML parser uses, which
is ForeignAssistance.gov's own sector name HIV/AIDS or the DAC purpose code 13040. The test
matters: for FY2024 disbursements 75 rows worth 62.3m USD carry the HIV/AIDS sector name
without the DAC code, and 131 rows worth 103.9m carry the DAC code under a sector name of
Malaria, Tuberculosis, Maternal and Child Health or Direct Administrative Costs. Either test
alone loses money the other keeps.

Managing agency, never funding agency. PEPFAR is appropriated to the State Department's
Global Health Programs account, so a split on funding agency puts 102bn USD under State and
separates nothing.

WHY THE BUCKET IS THE WHOLE DEPARTMENT

This CSV carries a managing sub-agency column and could separate CDC (38.5bn USD) from the
rest of Health and Human Services. The IATI files carry no sub-agency at all, so the
connector's Health and Human Services bucket is the whole department. This script buckets at
department level too, deliberately discarding a distinction the input could support, because
the two halves of the series have to be the same measurement or the join invents a break in
2012 that no agency made.

OUTPUT

    data/raw/foreign_assistance/history_fa_gov.csv   country_iso3, fiscal_year, bucket,
                                                     amount_usd
    data/raw/foreign_assistance/history_fa_gov.json  what was read and when

Nominal current US dollars, matching the XML, which publishes no constant-dollar figure.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hivimpact.normalize import code_to_iso3, to_iso3  # noqa: E402

DEFAULT_SOURCE = Path.home() / "Desktop" / "us_foreign_aid_complete_2026-07-18.csv"
DEFAULT_OUT = Path("data/raw/foreign_assistance/history_fa_gov.csv")

COLUMNS = [
    "Country Code", "Country Name", "Managing Agency Acronym",
    "International Purpose Code", "US Sector Name",
    "Transaction Type Name", "Fiscal Year", "Current Dollar Amount",
]

# the same two tests the XML parser applies, written in this file's column names
HIV_SECTOR_NAME = "HIV/AIDS"
HIV_PURPOSE_CODE = "13040"

# managing agency acronym -> the bucket the connector emits. Matched on the whole acronym,
# and everything unlisted pools into other_agency so the four buckets still partition the
# country total.
AGENCY_BUCKET = {"USAID": "usaid", "HHS": "hhs", "STATE": "state"}
OTHER = "other_agency"

CHUNK = 500_000


def extract(source: Path, out: Path, chunk: int = CHUNK) -> dict:
    totals: dict = {}
    counts = {"rows": 0, "hiv_disbursements": 0, "no_country": 0, "unreadable_amount": 0}
    iso_cache: dict = {}
    started = time.time()

    reader = pd.read_csv(source, dtype=str, usecols=COLUMNS, chunksize=chunk,
                         low_memory=False)
    for n, frame in enumerate(reader, start=1):
        counts["rows"] += len(frame)

        hiv = (frame["US Sector Name"].str.strip().str.upper() == HIV_SECTOR_NAME) | \
              (frame["International Purpose Code"].str.strip() == HIV_PURPOSE_CODE)
        disbursed = frame["Transaction Type Name"].str.contains("disburs", case=False,
                                                                na=False)
        rows = frame[hiv & disbursed]
        if rows.empty:
            print(f"  chunk {n:>4}  {counts['rows']:>12,} rows read", flush=True)
            continue

        amount = pd.to_numeric(
            rows["Current Dollar Amount"].str.replace(r"[,$]", "", regex=True),
            errors="coerce")
        year = pd.to_numeric(rows["Fiscal Year"].str.slice(0, 4), errors="coerce")
        counts["unreadable_amount"] += int((amount.isna() | year.isna()).sum())
        keep = amount.notna() & year.notna()

        for code, name, agency, fy, value in zip(
                rows["Country Code"][keep], rows["Country Name"][keep],
                rows["Managing Agency Acronym"][keep], year[keep], amount[keep]):
            code = str(code).strip()
            if code not in iso_cache:
                iso_cache[code] = code_to_iso3(code) or to_iso3(str(name).strip())
            iso3 = iso_cache[code]
            if not iso3:
                # regions and Worldwide, which the panel has no row for and the XML route
                # drops the same way
                counts["no_country"] += 1
                continue
            bucket = AGENCY_BUCKET.get(str(agency).strip().upper(), OTHER)
            key = (iso3, int(fy), bucket)
            totals[key] = totals.get(key, 0.0) + float(value)
            counts["hiv_disbursements"] += 1

        print(f"  chunk {n:>4}  {counts['rows']:>12,} rows read, "
              f"{counts['hiv_disbursements']:>9,} HIV disbursements kept", flush=True)

    out.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(
        [{"country_iso3": i, "fiscal_year": y, "bucket": b, "amount_usd": round(v, 2)}
         for (i, y, b), v in sorted(totals.items())])
    frame.to_csv(out, index=False)

    stat = source.stat()
    meta = {
        "source_file": str(source),
        "source_bytes": stat.st_size,
        "source_modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stat.st_mtime)),
        "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seconds": round(time.time() - started, 1),
        "hiv_test": "US Sector Name == 'HIV/AIDS' or International Purpose Code == '13040'",
        "transaction_type": "Disbursements only",
        "agency_basis": "Managing Agency Acronym, department level, no sub-agency split",
        "currency": "nominal current USD",
        "output_rows": len(frame),
        "countries": int(frame["country_iso3"].nunique()) if len(frame) else 0,
        "fiscal_years": (f"{int(frame['fiscal_year'].min())}-{int(frame['fiscal_year'].max())}"
                         if len(frame) else ""),
        "counts": counts,
    }
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2))
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                        help="the hand-downloaded Complete Data Set CSV")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--chunk", type=int, default=CHUNK)
    args = parser.parse_args()

    if not args.source.exists():
        print(f"not found: {args.source}\n\nForeignAssistance.gov sits behind a Cloudflare "
              f"challenge that answers 403 to every non-browser client, so this file has to "
              f"be downloaded by hand from https://foreignassistance.gov/data, Complete Data "
              f"Set. Downloading it again is only necessary if this repository has no "
              f"history_fa_gov.csv.", file=sys.stderr)
        return 1

    print(f"reading {args.source} ({args.source.stat().st_size / 1e9:.2f} GB)", flush=True)
    meta = extract(args.source, args.out, args.chunk)
    print(f"\nwrote {args.out}")
    print(f"  {meta['output_rows']:,} country-year-agency figures, "
          f"{meta['countries']} countries, FY{meta['fiscal_years']}")
    print(f"  from {meta['counts']['rows']:,} rows in {meta['seconds']:.0f}s, "
          f"{meta['counts']['hiv_disbursements']:,} HIV disbursements kept, "
          f"{meta['counts']['no_country']:,} dropped for naming a region and not a country")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
