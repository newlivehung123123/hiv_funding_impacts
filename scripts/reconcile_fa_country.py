#!/usr/bin/env python3
"""Trace one country's disagreement between the IATI files on Amazon S3 and FA.gov's own API.

WHY THIS EXISTS

The ForeignAssistance.gov connector reads US HIV disbursements from the IATI XML each US agency
publishes on Amazon S3, because ForeignAssistance.gov itself answers every non-browser client
with HTTP 403 and the header `cf-mitigated: challenge`. The S3 route was proved correct by
reconciling it against ForeignAssistance.gov's own Data API for one country, Nigeria, on 26 and
27 September 2026. That reconciliation is what `PROVEN_WINDOW` records, namely FY2020 onward for
USAID and FY2012 onward for State and for Health and Human Services.

Nigeria is one country. The run of 27 September 2026 found 14 country-years inside a proven
window where the S3 files and the frozen extract of the Complete Data Set disagree by more than
2 per cent, and the 14 are not scattered evenly. Three consecutive USAID years belong to
Nicaragua (FY2020, FY2021, FY2022) and three consecutive HHS years belong to Trinidad and Tobago
(FY2021, FY2022, FY2023). A run of three consecutive years in one bucket in one country is the
shape of a systematic fault and not of rounding, so Nicaragua and Trinidad and Tobago are the
second and third reconciliation targets after Nigeria, and this script is what reads them.
Nigeria is the control: run this script on NGA first and see the agreement, then run it on the
two targets and see where the agreement breaks.

WHY THIS CAN BE ANSWERED WITHOUT TOUCHING FOREIGNASSISTANCE.GOV

`data/raw/foreign_assistance/history_fa_gov.csv` is an extract of ForeignAssistance.gov's own
Complete Data Set, downloaded on 18 July 2026 and frozen. The extract is the API's output, so
comparing the cached XML against the extract compares the S3 route against ForeignAssistance.gov
without sending a request to a site that refuses Python. The one question the extract cannot
settle is whether ForeignAssistance.gov has restated a figure since 18 July 2026, and answering
that needs the Data API read in a browser at
https://foreignassistance.gov/api/data-api/complete-data.json, which is how the Nigeria
reconciliation was done.

WHAT IT DOES

It reads the XML already cached under data/raw/foreign_assistance/iati/ and writes nothing. For
one country it rebuilds the connector's own figure for every fiscal year and managing agency,
using the connector's own sector test, country resolution, fiscal year, deduplication key and
State subtraction, then prints that figure beside the frozen extract's figure, the difference
between the two and whether the fiscal year is inside the window the Nigeria reconciliation
proved for that agency. For every bucket-year the two sources disagree about, it then prints the
files and the activities behind the S3 figure, largest first, so a disagreement can be traced to
a file and an activity and taken back to the publisher.

Every figure comes from the connector's own helpers rather than from a second implementation of
them, so what this script measures is the connector's behaviour. The one place it cannot follow
the connector exactly is the attribution of a dropped duplicate. The connector deduplicates
across the whole corpus in the order the files are parsed, and this script reads the same files
in the same sorted order, but the corpus order comes from the registry, so which of two identical
transactions keeps the credit can differ. The bucket-year sums are unaffected, because the two
copies carry the same value, and only the `from` list in the detail block can move.

USAGE

    python3 scripts/reconcile_fa_country.py --country NGA        # the control
    python3 scripts/reconcile_fa_country.py --country NIC        # the USAID cluster
    python3 scripts/reconcile_fa_country.py --country TTO        # the HHS cluster
    python3 scripts/reconcile_fa_country.py --country NIC --details all --activities 20

Reading all 21 publishers takes several minutes because the corpus is 2,723 megabytes. Narrow it
with --org where the question is about one agency, remembering that a country's money also
arrives in multi-country files, so narrowing by publisher is safe and narrowing by filename is
not.

HOW TO READ THE OUTPUT

A row marked `proven` is a fiscal year the Nigeria reconciliation covered for that agency, and a
difference there is the finding. A row marked `unproven` is outside that window, where the
connector takes the frozen extract and not the S3 figure, so a difference there is expected and
is why the window exists. A `history` column reading `none` means the extract has no figure for
that agency, country and fiscal year at all, which for a year the S3 files do cover is itself
worth following up.
"""
from __future__ import annotations

import argparse
import collections
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hivimpact.connectors.foreign_assistance import (  # noqa: E402
    BUCKETS, HISTORY_AGREEMENT_TOLERANCE, HISTORY_FILE, OTHER, PROVEN_WINDOW,
    REPORTING_ORG_BUCKET, ForeignAssistanceConnector as FA, resolve_country)
from hivimpact.normalize import name_for  # noqa: E402

RAW_DIR = ROOT / "data" / "raw" / "foreign_assistance"
XML_DIR = RAW_DIR / "iati"


def transactions(path: Path, org: str, country: str, start_year: int, end_year: int):
    """Every HIV disbursement for one country in one file, using the connector's own tests.

    The sector test, the country resolution, the fiscal year, the receiver narrative and the
    award number all come from the connector, so that this script measures the connector and
    not a second implementation of the connector.
    """
    try:
        stream = ET.iterparse(str(path), events=("end",))
        for _, activity in stream:
            if FA._local_name(activity.tag) != "iati-activity":
                continue
            identifier = ""
            title = ""
            reporting_ref = ""
            default_currency = (activity.get("default-currency") or "").upper()
            for child in activity:
                name = FA._local_name(child.tag)
                if name == "iati-identifier":
                    identifier = (child.text or "").strip()
                elif name == "reporting-org":
                    reporting_ref = (child.get("ref") or "").strip()
                elif name == "title" and not title:
                    title = " ".join("".join(child.itertext()).split())
            bucket = REPORTING_ORG_BUCKET.get(reporting_ref, OTHER)
            activity_countries = FA._countries(activity)
            activity_hiv = FA._is_hiv(activity)

            for transaction in activity:
                if FA._local_name(transaction.tag) != "transaction":
                    continue
                fields = {FA._local_name(c.tag): c for c in transaction}
                kind = fields.get("transaction-type")
                if kind is None or (kind.get("code") or "") != "3":
                    continue
                hiv = FA._is_hiv(transaction)
                if hiv is None:
                    hiv = activity_hiv
                if not hiv:
                    continue
                codes = FA._countries(transaction) or activity_countries
                if len(codes) != 1:
                    continue
                iso3 = resolve_country(codes[0])
                if iso3 != country:
                    continue
                date_element = fields.get("transaction-date")
                iso_date = ((date_element.get("iso-date") or "")
                            if date_element is not None else "")
                year = FA.fiscal_year(iso_date)
                if year is None or not (start_year <= year <= end_year):
                    continue
                value_element = fields.get("value")
                if value_element is None:
                    continue
                currency = (value_element.get("currency") or default_currency or "USD").upper()
                if currency != "USD":
                    continue
                try:
                    value = float((value_element.text or "").strip())
                except ValueError:
                    continue
                yield {
                    "org": org, "file": path.name, "bucket": bucket, "year": year,
                    "identifier": identifier, "title": title, "ref": transaction.get("ref"),
                    "date": iso_date, "value": value,
                    "receiver": FA._receiver(transaction),
                    "award": FA._award_number(identifier, bucket),
                }
            activity.clear()
    except ET.ParseError as exc:
        print(f"  ! {org}/{path.name} is not readable XML ({exc})")


def read_history(country: str) -> Dict[Tuple[int, str], float]:
    """The frozen extract's figures for one country, keyed by fiscal year and bucket."""
    path = RAW_DIR / HISTORY_FILE
    history: Dict[Tuple[int, str], float] = {}
    if not path.exists():
        print(f"no frozen extract at {path}, so nothing to compare against")
        return history
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("country_iso3") != country:
                continue
            try:
                key = (int(row["fiscal_year"]), row["bucket"])
                history[key] = history.get(key, 0.0) + float(row["amount_usd"])
            except (KeyError, TypeError, ValueError):
                continue
    return history


def collect(country: str, orgs: List[str], start_year: int, end_year: int) -> List[dict]:
    """Every kept HIV disbursement for one country, deduplicated as the connector does."""
    seen: Set[tuple] = set()
    kept: List[dict] = []
    dropped = 0
    for org in orgs:
        directory = XML_DIR / org
        if not directory.is_dir():
            print(f"no such publisher directory: {directory}")
            continue
        files = sorted(p for p in directory.iterdir() if p.is_file())
        before = len(kept)
        for path in files:
            for row in transactions(path, org, country, start_year, end_year):
                key = (row["identifier"], row["ref"], row["date"], row["value"],
                       row["receiver"])
                if key in seen:
                    dropped += 1
                    continue
                seen.add(key)
                kept.append(row)
        print(f"  {org}: {len(files)} files, {len(kept) - before} kept disbursements")
    print(f"\n{len(kept)} kept disbursements, {dropped} duplicates dropped")
    return kept


def subtract_overlap(totals: Dict[Tuple[int, str], float],
                     awards: Dict[Tuple[int, str], Set[str]],
                     country: str) -> Dict[Tuple[int, str], float]:
    """Apply the connector's State subtraction to one country, through the connector itself.

    The USAID file reports State's transactions as well as USAID's from FY2025, and
    ForeignAssistance.gov reports the USAID figure net of the State figure. Comparing an
    unadjusted USAID figure against the extract would therefore report a disagreement the
    connector does not have, so the connector's own `_subtract_overlap` is called here.
    """
    connector = FA()
    keyed = {(country, year, bucket): value for (year, bucket), value in totals.items()}
    keyed_awards = {(country, year, bucket): names
                    for (year, bucket), names in awards.items()}
    adjusted = connector._subtract_overlap(keyed, keyed_awards)
    return {(year, bucket): value for (_, year, bucket), value in adjusted.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True,
                        help="ISO3 code. NGA is the control, NIC and TTO are the targets.")
    parser.add_argument("--org", action="append", default=[],
                        help="publisher slug, repeatable; default every publisher on disk")
    parser.add_argument("--start", type=int, default=2000)
    parser.add_argument("--end", type=int, default=2025)
    parser.add_argument("--details", choices=("disagreeing", "all", "none"),
                        default="disagreeing",
                        help="which bucket-years to break down by file and activity")
    parser.add_argument("--activities", type=int, default=10,
                        help="how many activities to name in a breakdown, largest first")
    args = parser.parse_args()

    if not XML_DIR.exists():
        print(f"no cached XML at {XML_DIR} — run the connector once first")
        return 1
    country = args.country.upper()
    orgs = args.org or sorted(d.name for d in XML_DIR.iterdir() if d.is_dir())

    print(f"{name_for(country) or country} ({country}), FY{args.start} to FY{args.end}")
    print(f"IATI XML cached under {XML_DIR}")
    print(f"compared against {RAW_DIR / HISTORY_FILE}, the frozen extract of "
          f"ForeignAssistance.gov's Complete Data Set\n")

    rows = collect(country, orgs, args.start, args.end)
    history = read_history(country)

    raw: Dict[Tuple[int, str], float] = {}
    awards: Dict[Tuple[int, str], Set[str]] = {}
    for row in rows:
        key = (row["year"], row["bucket"])
        raw[key] = raw.get(key, 0.0) + row["value"]
        if row["award"]:
            awards.setdefault(key, set()).add(row["award"])
    totals = subtract_overlap(raw, awards, country)

    compare(totals, raw, history, args.start, args.end)
    if args.details != "none":
        breakdown(rows, totals, raw, history, args.details, args.activities)
    return 0


def window(year: int, bucket: str) -> bool:
    """Whether the Nigeria reconciliation proved the S3 route for this agency and year."""
    opens = PROVEN_WINDOW.get(bucket)
    return opens is not None and year >= opens


def disagrees(from_s3: Optional[float], from_history: Optional[float]) -> bool:
    if from_s3 is None or from_history is None:
        return False
    scale = max(abs(from_s3), abs(from_history))
    return scale > 0 and abs(from_s3 - from_history) / scale > HISTORY_AGREEMENT_TOLERANCE


def compare(totals: Dict[Tuple[int, str], float], raw: Dict[Tuple[int, str], float],
            history: Dict[Tuple[int, str], float], start_year: int, end_year: int) -> None:
    """One line per fiscal year and agency, S3 beside the extract."""
    years = sorted({y for y, _ in totals} | {y for y, _ in history})
    years = [y for y in years if start_year <= y <= end_year]
    print(f"\n{'FY':>6}  {'agency':<13}{'S3 files':>18}{'frozen extract':>18}"
          f"{'difference':>18}{'rel':>9}  window")
    print("  " + "-" * 90)
    checked = agreed = 0
    for year in years:
        for bucket in BUCKETS:
            from_s3 = totals.get((year, bucket))
            from_history = history.get((year, bucket))
            if from_s3 is None and from_history is None:
                continue
            proven = window(year, bucket)
            bad = proven and disagrees(from_s3, from_history)
            if proven and from_s3 is not None and from_history is not None:
                checked += 1
                agreed += 0 if bad else 1
            s3_text = f"{from_s3:>18,.0f}" if from_s3 is not None else f"{'none':>18}"
            history_text = (f"{from_history:>18,.0f}" if from_history is not None
                            else f"{'none':>18}")
            if from_s3 is None or from_history is None:
                difference_text, rel_text = f"{'':>18}", f"{'':>9}"
            else:
                difference = from_s3 - from_history
                scale = max(abs(from_s3), abs(from_history))
                difference_text = f"{difference:>18,.0f}"
                rel_text = f"{100 * difference / scale:>8.1f}%" if scale > 0 else f"{'':>9}"
            mark = "  <-- disagrees" if bad else ""
            print(f"{year:>6}  {bucket:<13}{s3_text}{history_text}{difference_text}{rel_text}"
                  f"  {'proven' if proven else 'unproven'}{mark}")
            if bucket == "usaid" and raw.get((year, bucket)) != from_s3:
                print(f"{'':>6}  {'':<13}{raw[(year, bucket)]:>18,.0f}"
                      f"{'':>18}{'':>18}{'':>9}  USAID before the State subtraction")
    if checked:
        print(f"\n{agreed} of {checked} agency-years inside a proven window agree with the "
              f"frozen extract to within {100 * HISTORY_AGREEMENT_TOLERANCE:.0f} per cent")
    else:
        print("\nno agency-year inside a proven window has a figure from both sources")


def breakdown(rows: List[dict], totals: Dict[Tuple[int, str], float],
              raw: Dict[Tuple[int, str], float], history: Dict[Tuple[int, str], float],
              which: str, limit: int) -> None:
    """The files and activities behind the S3 figure, so a difference can be traced."""
    by_key: Dict[Tuple[int, str], List[dict]] = collections.defaultdict(list)
    for row in rows:
        by_key[(row["year"], row["bucket"])].append(row)

    wanted = []
    for key in sorted(by_key):
        year, bucket = key
        if which == "all":
            wanted.append(key)
        elif window(year, bucket) and disagrees(totals.get(key), history.get(key)):
            wanted.append(key)
    if not wanted:
        print("\nno bucket-year to break down")
        return

    for year, bucket in wanted:
        entries = by_key[(year, bucket)]
        from_history = history.get((year, bucket))
        print(f"\nFY{year} {bucket}: {raw[(year, bucket)]:,.0f} USD from the S3 files over "
              f"{len(entries)} disbursements, extract "
              + (f"{from_history:,.0f}" if from_history is not None else "none"))
        by_file: Dict[str, List[float]] = collections.defaultdict(list)
        for entry in entries:
            by_file[f"{entry['org']}/{entry['file']}"].append(entry["value"])
        for filename, values in sorted(by_file.items(), key=lambda kv: -sum(kv[1])):
            print(f"    {sum(values):>16,.0f} over {len(values):>4} from {filename}")
        by_activity: Dict[str, List[float]] = collections.defaultdict(list)
        titles: Dict[str, str] = {}
        for entry in entries:
            by_activity[entry["identifier"]].append(entry["value"])
            titles.setdefault(entry["identifier"], entry["title"])
        ranked = sorted(by_activity.items(), key=lambda kv: -abs(sum(kv[1])))
        for identifier, values in ranked[:limit]:
            title = titles.get(identifier, "")
            print(f"    {sum(values):>16,.0f} over {len(values):>4} {identifier} "
                  f"{title[:60]}")
        if len(ranked) > limit:
            rest = sum(sum(v) for _, v in ranked[limit:])
            print(f"    {rest:>16,.0f} over {len(ranked) - limit} further activities")


if __name__ == "__main__":
    raise SystemExit(main())
