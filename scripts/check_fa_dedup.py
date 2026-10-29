#!/usr/bin/env python3
"""Ask whether the ForeignAssistance.gov deduplication key is doing anything.

WHY THIS EXISTS

The connector deduplicates transactions on the whole row, which is the activity identifier, the
transaction ref, the transaction date, the value and the receiver organisation narrative
together. That key was chosen over two simpler ones for measured reasons. Deduplicating on the
transaction ref alone moves Nigeria's State FY2012 figure from 623,717 to 551,282 USD and breaks
seven of 13 otherwise-exact State years. USAID publishes five FY2026 Nigeria HIV disbursements
twice, worth 15,851,027 USD together, and the whole-row key removes the repeats.

The full run of 27 September 2026 then reported dropping zero duplicates out of 115,137 kept
disbursements. Zero is a defensible number and zero is also what a key that never fires would
report, and the log cannot separate a real absence of duplicates from a dead key. This script
separates a real absence of duplicates from a dead key.

WHAT IT FOUND, 27 SEPTEMBER 2026, AND THE YEAR WINDOW THAT NEARLY MISLED IT

Run against USAID's 206 Nigeria files over the default window FY2000 to FY2026, on 4,901 HIV
disbursements worth 1,775,318,599 USD gross, the whole-row key drops five transactions worth
15,851,027 USD, the activity identifier with the transaction ref drops the same five, and the
activity identifier alone drops 4,302 transactions worth 1,714,872,573 USD, which is 87.78 per
cent and would leave 60,446,026 USD where the truth is 1.78bn. So an identifier-only key would
be catastrophic, and that question is settled. The whole row and the activity identifier with
the ref agree on Nigeria's USAID files, and the evidence separating those two keys is the State
reconciliation named above and nothing in this script's output.

The first run of this script used a window ending at FY2025 and reported zero for the whole row.
Zero was not evidence that the whole-row key is dormant. The five duplicated USAID transactions
are FY2026, so a window ending at FY2025 excludes the only case in the corpus with a known
answer. The connector's own zero comes from the same cause, because a panel run ends at FY2025
by default. **The default end year here is therefore 2026 and not 2025, so that the case with a
known answer is inside the window.** A run of this script that reports zero for the whole row
should be read against its own --start and --end before anyone concludes the key is doing
nothing.

WHERE THE FIVE REPEATS SIT

Every one of the five duplicated transactions is published twice inside the same file as the
original, and the five pairs are spread across two files and not gathered in one. Four pairs
worth 15,649,184 USD sit in `iati-activities-Multiple_Countries-34.xml` and the fifth pair worth
201,843 USD sits in `iati-activities-Nigeria.xml`. Three of the four pairs in the multi-country
file carry the activity identifier US-GOV-1-AID-OAA-TO-15-00004 and the receiver Remote Medical
International. The `whole row` line below prints the file each repeat came from, which is why
the breakdown reads four and one.

WHAT IT DOES

It reads the XML already cached under data/raw/foreign_assistance/iati/ and writes nothing. For
every HIV disbursement it builds three candidate keys and counts how many transactions and how
many dollars each key would collapse:

    whole row    identifier + ref + date + value + receiver   (what the connector uses)
    id + ref     identifier + ref
    id only      identifier

Reading all 21 publishers takes a while, so start with one. The publisher slugs are the
directory names under data/raw/foreign_assistance/iati/.

USAGE

    python3 scripts/check_fa_dedup.py --org usaid --country NGA
    python3 scripts/check_fa_dedup.py --org usaid --org state --org hhs
    python3 scripts/check_fa_dedup.py                       # every publisher, slow

The country filter takes an ISO3 code and is worth using first, because the Nigeria numbers
above are the ones the key was chosen against and are therefore the ones with a known answer.
"""
from __future__ import annotations

import argparse
import collections
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hivimpact.connectors.foreign_assistance import (  # noqa: E402
    OTHER, REPORTING_ORG_BUCKET, ForeignAssistanceConnector as FA, resolve_country)

XML_DIR = ROOT / "data" / "raw" / "foreign_assistance" / "iati"


def transactions(path: Path, start_year: int, end_year: int, country: str | None):
    """Every HIV disbursement in one file, as a dict, using the connector's own tests.

    The sector test, the country resolution, the fiscal year and the receiver narrative all come
    from the connector so that this script measures the connector's behaviour and not a second
    implementation of it.
    """
    try:
        stream = ET.iterparse(str(path), events=("end",))
        for _, activity in stream:
            if FA._local_name(activity.tag) != "iati-activity":
                continue
            identifier = ""
            reporting_ref = ""
            default_currency = (activity.get("default-currency") or "").upper()
            for child in activity:
                name = FA._local_name(child.tag)
                if name == "iati-identifier":
                    identifier = (child.text or "").strip()
                elif name == "reporting-org":
                    reporting_ref = (child.get("ref") or "").strip()
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
                iso3 = resolve_country(codes[0], reporting_ref)
                if not iso3 or (country and iso3 != country):
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
                    "file": path.name, "bucket": bucket, "iso3": iso3, "year": year,
                    "identifier": identifier, "ref": transaction.get("ref"),
                    "date": iso_date, "value": value,
                    "receiver": FA._receiver(transaction),
                }
            activity.clear()
    except ET.ParseError as exc:
        print(f"  ! {path.parent.name}/{path.name} is not readable XML ({exc})")


KEYS = {
    "whole row": lambda t: (t["identifier"], t["ref"], t["date"], t["value"], t["receiver"]),
    "id + ref ": lambda t: (t["identifier"], t["ref"]),
    "id only  ": lambda t: (t["identifier"],),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--org", action="append", default=[],
                        help="publisher slug, repeatable; default every publisher on disk")
    parser.add_argument("--country", default=None, help="ISO3 code, for example NGA")
    parser.add_argument("--start", type=int, default=2000)
    parser.add_argument("--end", type=int, default=2026,
                        help="2026 and not 2025, because the five duplicated USAID Nigeria "
                             "transactions are FY2026 and a window ending at 2025 excludes the "
                             "one case with a known answer")
    args = parser.parse_args()

    if not XML_DIR.exists():
        print(f"no cached XML at {XML_DIR} — run the connector once first")
        return 1
    orgs = args.org or sorted(d.name for d in XML_DIR.iterdir() if d.is_dir())
    country = args.country.upper() if args.country else None

    grand: list[dict] = []
    for org in orgs:
        directory = XML_DIR / org
        if not directory.is_dir():
            print(f"no such publisher directory: {directory}")
            continue
        files = sorted(p for p in directory.iterdir() if p.is_file())
        rows: list[dict] = []
        for path in files:
            rows.extend(transactions(path, args.start, args.end, country))
        print(f"\n{org}: {len(files)} files, {len(rows)} HIV disbursements"
              + (f" in {country}" if country else ""))
        if not rows:
            continue
        report(rows)
        grand.extend(rows)

    if len(orgs) > 1 and grand:
        print(f"\nall {len(orgs)} publishers together: {len(grand)} HIV disbursements")
        report(grand)
    return 0


def report(rows: list[dict]) -> None:
    """For each candidate key, how many transactions and how many dollars it collapses."""
    total = sum(r["value"] for r in rows)
    print(f"  gross before any deduplication: {total:,.0f} USD over {len(rows)} transactions")
    for label, build in KEYS.items():
        seen: set = set()
        dropped = 0
        dropped_value = 0.0
        by_file: collections.Counter = collections.Counter()
        for row in rows:
            key = build(row)
            if key in seen:
                dropped += 1
                dropped_value += row["value"]
                by_file[row["file"]] += 1
                continue
            seen.add(key)
        share = 100 * dropped / len(rows)
        print(f"  {label}  drops {dropped:6d} of {len(rows)} ({share:5.2f}%), "
              f"{dropped_value:>16,.0f} USD, leaving {total - dropped_value:,.0f}")
        if dropped and label.strip() == "whole row":
            for filename, count in by_file.most_common(5):
                print(f"               {count:6d} from {filename}")


if __name__ == "__main__":
    raise SystemExit(main())
