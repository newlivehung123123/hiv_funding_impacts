"""Offline check of the `iati` connector. Reads no network and writes nothing.

Part one exercises the connector's pure functions, the registration and the indicator specs.
Part one needs no data and always runs.

Part two runs the real `_publisher_rows` over cached publisher XML, with the page source and
the exchange rates stubbed, and reports what the allocation produced. Part two needs a
directory of publisher XML and skips itself when no such directory is there. The default
directory is the connector's own cache, `data/raw/iati`, which holds one gzipped page per
publisher and offset once Jason has run the connector. A flat directory of `<ref>.xml` files
also works, which is the shape the survey probes left behind.

THE MONEY TOTALS PART TWO PRINTS ARE NOT PANEL NUMBERS. The exchange rates are invented
constants, so the totals exist to show that the arithmetic runs and that the allocation, the
exclusions and the country resolution behave. Only a real run produces a real figure.

    python3 scripts/check_iati.py
    python3 scripts/check_iati.py --sample data/raw/iati
"""
import argparse
import collections
import gzip
import logging
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from hivimpact.connectors import CONNECTORS, IATIConnector          # noqa: E402
from hivimpact.connectors import iati as M                          # noqa: E402
from hivimpact.config.indicators import CANONICAL_INDICATORS        # noqa: E402

fails = []


def ok(label, got, want):
    flag = "ok  " if got == want else "FAIL"
    if got != want:
        fails.append(label)
    print(f"  {flag} {label:<58} got {got!r}")


def load_pages(sample_dir):
    """Map publisher reference -> list of XML page bodies, from either cache shape."""
    bodies = collections.OrderedDict()
    if not sample_dir or not os.path.isdir(sample_dir):
        return bodies
    for entry in sorted(os.listdir(sample_dir)):
        path = os.path.join(sample_dir, entry)
        if os.path.isdir(path):
            pages = []
            for page in sorted(os.listdir(path)):
                if page.endswith(".xml.gz"):
                    pages.append(gzip.decompress(open(path + "/" + page, "rb").read()))
                elif page.endswith(".xml"):
                    pages.append(open(path + "/" + page, "rb").read())
            if pages:
                bodies[entry] = pages
        elif entry.endswith(".xml"):
            bodies[entry[:-4]] = [open(path, "rb").read()]
        elif entry.endswith(".xml.gz"):
            bodies[entry[:-7]] = [gzip.decompress(open(path, "rb").read())]
    return bodies


def part_one(bodies):
    print("=" * 78)
    print("registration")
    print("=" * 78)
    ok("source_id registered", "iati" in CONNECTORS, True)
    ok("registry maps to the class", CONNECTORS.get("iati") is IATIConnector, True)
    ok("source_type", IATIConnector.default_source_type.value, "expenditure_account")

    for ind in ("global_fund_hiv_disbursements", "external_hiv_bilateral_other",
                "external_hiv_multilateral_other", "external_hiv_foundation"):
        ok(f"spec exists: {ind}", ind in CANONICAL_INDICATORS, True)
        ok(f"  unit is USD: {ind}", CANONICAL_INDICATORS[ind].unit, "USD")
        ok(f"  domain is financing: {ind}", CANONICAL_INDICATORS[ind].domain, "financing")
    ok("global fund description names iati",
       "iati" in CANONICAL_INDICATORS["global_fund_hiv_disbursements"].notes, True)

    print()
    print("=" * 78)
    print("the strict country resolver, which is the trap that once cost this panel 59.9bn")
    print("=" * 78)
    ok("ZA -> ZAF", M._alpha2_to_iso3("ZA"), "ZAF")
    ok("za lowercase -> ZAF", M._alpha2_to_iso3("za"), "ZAF")
    ok("XK -> XKX (Kosovo, no ISO entry)", M._alpha2_to_iso3("XK"), "XKX")
    ok("998 refused", M._alpha2_to_iso3("998"), None)
    ok("empty refused", M._alpha2_to_iso3(""), None)
    ok("'Scotland' refused, no fuzzy pass", M._alpha2_to_iso3("Scotland"), None)
    ok("SDN alpha-3 through _any_code_to_iso3", M._any_code_to_iso3("SDN"), "SDN")
    ok("ZA alpha-2 through _any_code_to_iso3", M._any_code_to_iso3("ZA"), "ZAF")
    ok("689 refused by _any_code_to_iso3", M._any_code_to_iso3("689"), None)

    print()
    print("=" * 78)
    print("Global Fund component letters, both identifier shapes")
    print("=" * 78)
    ok("5 parts, H at index 2", M._is_hc_grant("47045-GIN-H-MOH-1"), True)
    ok("7 parts, H at index 4", M._is_hc_grant("47045-NMB-202-G01-H-00-1"), True)
    ok("C counted", M._is_hc_grant("47045-MWI-C-MOH-2"), True)
    ok("Z not counted", M._is_hc_grant("47045-ZWE-Z-UNDP-1"), False)
    ok("T not counted", M._is_hc_grant("47045-KEN-T-TNT-1"), False)
    ok("a G-number is not mistaken for a letter",
       M._is_hc_grant("47045-NMB-202-G01-T-00-1"), False)

    print()
    print("=" * 78)
    print("the sector share")
    print("=" * 78)
    c = IATIConnector.__new__(IATIConnector)

    def sectors(*spec):
        out = []
        for code, pct, vocab in spec:
            e = ET.Element("sector", {"code": code})
            if pct is not None:
                e.set("percentage", str(pct))
            if vocab is not None:
                e.set("vocabulary", vocab)
            out.append(e)
        return out

    ok("one 13040, no percentage -> 1.0",
       c._sector_share(sectors(("13040", None, None)), "13040"), 1.0)
    ok("one 12110, no percentage -> 0.0",
       c._sector_share(sectors(("12110", None, None)), "13040"), 0.0)
    ok("60/40 split -> 0.6",
       c._sector_share(sectors(("13040", 60, "1"), ("12110", 40, "1")), "13040"), 0.6)
    ok("percentages summing to 99 still allocate the whole",
       round(c._sector_share(sectors(("13040", 88, "1"), ("12110", 7, "1"), ("12263", 4, "1")),
                             "13040"), 6), round(88 / 99, 6))
    ok("a publisher's own vocabulary is refused",
       c._sector_share(sectors(("13040", 100, "99")), "13040"), None)
    ok("vocabulary 99 alongside vocabulary 1 is ignored in the pool",
       c._sector_share(sectors(("13040", 50, "1"), ("13040", 50, "99")), "13040"), 1.0)
    ok("no sector at all", c._sector_share([], "13040"), None)

    print()
    print("=" * 78)
    print("the geography split")
    print("=" * 78)

    def geo(kind, *spec):
        out = []
        for code, pct in spec:
            e = ET.Element(kind)
            if code is not None:
                e.set("code", code)
            if pct is not None:
                e.set("percentage", str(pct))
            out.append(e)
        return out

    ok("one country, no percentage, no region",
       c._geography(geo("recipient-country", ("ZA", None)), []),
       ([("ZA", 1.0)], 0.0, 0.0, None))
    ok("one country at 100",
       c._geography(geo("recipient-country", ("ZA", 100)), []),
       ([("ZA", 1.0)], 0.0, 0.0, None))
    shares, region, unnamed, why = c._geography(
        geo("recipient-country", ("ZA", 60), ("KE", 20)), geo("recipient-region", ("298", 20)))
    ok("region money stays with the region",
       ([(k, round(v, 4)) for k, v in shares], round(region, 4), unnamed, why),
       ([("ZA", 0.6), ("KE", 0.2)], 0.2, 0.0, None))
    ok("region only, nothing written",
       c._geography([], geo("recipient-region", ("298", 100))), ([], 1.0, 0.0, None))
    shares, _r, _u, why = c._geography(geo("recipient-country", ("ZA", None), ("KE", None)), [])
    ok("several countries, no percentages, refused",
       (shares, why), ([], "several countries, none with a percentage"))
    shares, _r, _u, why = c._geography(geo("recipient-country", ("ZA", 60), ("KE", None)), [])
    ok("several countries, only some with a percentage, refused",
       (shares, why), ([], "several countries, only some with a percentage"))
    shares, _r, _u, why = c._geography([], [])
    ok("no geography at all", (shares, why), ([], "no geography stated"))
    # UNICEF's shape, a recipient-country element carrying a percentage and no code.
    ok("UNICEF's codeless recipient, all unnamed",
       c._geography(geo("recipient-country", (None, 100)), geo("recipient-region", (None, 0))),
       ([], 0.0, 1.0, None))
    shares, _r, unnamed, why = c._geography(
        geo("recipient-country", ("KE", 50), (None, 50)), [])
    ok("a codeless element does NOT inflate the named country",
       ([(k, round(v, 4)) for k, v in shares], round(unnamed, 4), why),
       ([("KE", 0.5)], 0.5, None))

    print()
    print("=" * 78)
    print("the funder matcher and the pass-through rule")
    print("=" * 78)
    ok("US-USAGOV matched", IATIConnector._is_us_gov("US-USAGOV", ""), True)
    ok("US-GOV-14 matched by prefix", IATIConnector._is_us_gov("US-GOV-14", ""), True)
    ok("US-EIN charity not matched",
       IATIConnector._is_us_gov("US-EIN-135562162", "CARE USA"), False)
    ok("USAID matched by name", IATIConnector._is_us_gov("", "USAID SOUTHERN AFRICA"), True)
    ok("Global Fund by bare DAC number", IATIConnector._is_global_fund("47045", ""), True)
    ok("Global Fund by XM-DAC form", IATIConnector._is_global_fund("XM-DAC-47045", ""), True)
    ok("Global Fund by name",
       IATIConnector._is_global_fund("", "THE GLOBAL FUND TO FIGHT AIDS"), True)
    ok("Sweden not matched", IATIConnector._is_global_fund("SE-0", "SWEDEN"), False)

    if not bodies:
        print("  --   no cached XML, the funder-list sweep and the rule counts are skipped")
        return

    seen = 0
    excluded = 0
    alone = 0
    per_pub = collections.defaultdict(lambda: [0, 0, 0])
    for ref, pages in bodies.items():
        for body in pages:
            try:
                root = ET.fromstring(body)
            except ET.ParseError:
                continue
            for act in root:
                reporter = next(iter(M._children(act, "reporting-org")), None)
                if reporter is None:
                    continue
                rref = (reporter.get("ref") or "").strip().upper()
                funders = IATIConnector._funders(act, rref)
                if any(r == rref for r, _n in funders):
                    fails.append("a publisher was left in its own funder list")
                seen += 1
                per_pub[ref][0] += 1
                hits = [(r, n) for r, n in funders
                        if IATIConnector._is_global_fund(r, n) or IATIConnector._is_us_gov(r, n)]
                if not hits:
                    continue
                excluded += 1
                per_pub[ref][1] += 1
                if len(hits) == len(funders):
                    alone += 1
                    per_pub[ref][2] += 1
    print(f"  ok   the reporter is never in its own funder list ({seen} activities)")
    print()
    print(f"  the pass-through rule over {seen} cached activities")
    print(f"    excluded by the rule as approved                       {excluded}"
          f"  ({100.0 * excluded / seen:.1f} per cent)" if seen else "")
    print(f"    of which the excluded funder is the only funder named  {alone}")
    print(f"    of which another funder is named alongside             {excluded - alone}"
          "   <- the narrower rule would keep these")
    print(f"    {'publisher':<22} {'activities':>10} {'excluded':>9} {'excl. alone':>12}")
    for ref, (n, h, a) in sorted(per_pub.items(), key=lambda kv: -kv[1][1]):
        if h:
            print(f"    {ref:<22} {n:>10} {h:>9} {a:>12}")


STUB_RATES = {"SEK": 0.095, "GBP": 1.27, "EUR": 1.08, "AUD": 0.66, "CAD": 0.74,
              "CHF": 1.13, "NZD": 0.61, "DKK": 0.145, "NOK": 0.093, "JPY": 0.0067}


def part_two(bodies, start_year, end_year):
    print()
    print("=" * 78)
    print("running the real allocation over the cached XML (stubbed rates)")
    print("=" * 78)
    if not bodies:
        print("  --   no cached XML, part two is skipped")
        return

    conn = IATIConnector(raw_dir=os.path.join(ROOT, "data", "raw", "iati"))
    conn._rates_mean = dict(STUB_RATES)

    def fake_pages(ref, first_page_only=False):
        for body in bodies.get(ref, []):
            yield None, body
            if first_page_only:
                return

    conn._xml_pages = fake_pages

    buckets = collections.defaultdict(dict)
    detail = collections.defaultdict(dict)
    tally = collections.defaultdict(float)
    for ref in bodies:
        conn._publisher_rows(ref, None, start_year, end_year, buckets, detail, tally)

    print()
    print("=" * 78)
    print("what came out")
    print("=" * 78)
    rows = collections.Counter()
    money = collections.Counter()
    countries = collections.defaultdict(set)
    years = collections.defaultdict(set)
    for (iso3, series, year) in buckets:
        rows[series] += 1
        money[series] += detail[(iso3, series, year)].get("value", 0.0)
        countries[series].add(iso3)
        years[series].add(year)
    for s in sorted(rows):
        print(f"  {s:<34} {rows[s]:>5} country-year rows, "
              f"{len(countries[s]):>3} countries, years {min(years[s])}-{max(years[s])}, "
              f"{money[s]:>18,.0f} illustrative USD")
    if not buckets:
        fails.append("the allocation produced nothing at all")
        return

    try:
        import pycountry
    except ImportError:
        pycountry = None
    codes = sorted({i for i, _s, _y in buckets})
    print()
    print("  every ISO3 produced, checked against pycountry")
    if pycountry is None:
        print("    pycountry is not installed, so the ISO3 check is skipped")
    else:
        unknown = [i for i in codes
                   if i not in ("XKX",) and not pycountry.countries.get(alpha_3=i)]
        print(f"    {len(codes)} distinct ISO3 codes, {len(unknown)} not resolvable")
        if unknown:
            fails.append(f"unresolvable ISO3 emitted: {unknown}")
    for trap in ("GBR", "USA"):
        hits = [k for k in buckets if k[0] == trap]
        print(f"    {trap} rows: {len(hits)}"
              + ("   <- check this is recipient money and not a fuzzy match" if hits else ""))

    print()
    print("=" * 78)
    print("the largest emitted row, built through the real make_row and serialised")
    print("=" * 78)
    key = max(buckets, key=lambda k: detail[k].get("value", 0.0))
    iso3, series, year = key
    row = conn.make_row(
        country_iso3=iso3, country_name=M.name_for(iso3), indicator_id=series, year=year,
        value=detail[key]["value"], unit="USD",
        source_url="https://d-portal.org/q.xml?from=act,sector&sector_code=13040",
        source_indicator_code=f"IATI.13040.{series}",
        extra={"note": "check", "related_16064_usd": 0.0,
               "by_publisher": {k: round(v, 2) for k, v in buckets[key].items()},
               "do_not_add_to": "external_hiv_oda_total"})
    d = row.to_dict()
    for field in ("country_iso3", "indicator_id", "year", "value", "unit", "source_id",
                  "source_type", "source_indicator_code"):
        print(f"  {field:<24} {d.get(field)!r}")
    print(f"  {'extra':<24} {str(d.get('extra'))[:140]}")
    if d.get("source_id") != "iati":
        fails.append("source_id is not iati")
    if d.get("source_type") != "expenditure_account":
        fails.append("source_type is wrong")
    if not isinstance(d.get("extra"), str):
        fails.append("extra did not serialise to a string")

    print()
    print("=" * 78)
    print("the duplicate-key test the panel validator will apply")
    print("=" * 78)
    emitted = [(iso3, series, year) for (iso3, series, year) in buckets
               if series != "external_hiv_foundation" or M._WRITE_FOUNDATION]
    counted = collections.Counter(emitted)
    dupes = [k for k, n in counted.items() if n > 1]
    print(f"  {len(emitted)} rows would reach the panel, {len(buckets) - len(emitted)} held "
          f"back, {len(dupes)} duplicate country/series/year keys")
    print("  the bucket key is the panel key, so a duplicate here means one publisher's "
          "money reached\n  two buckets rather than one")
    if dupes:
        fails.append(f"duplicate keys: {dupes[:5]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", default=os.path.join(ROOT, "data", "raw", "iati"),
                    help="directory of cached publisher XML (default data/raw/iati)")
    ap.add_argument("--start", type=int, default=2000)
    ap.add_argument("--end", type=int, default=2026)
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print the connector's own per-publisher log lines")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="%(message)s")
    bodies = load_pages(args.sample)
    print(f"cached XML read from {args.sample}, {len(bodies)} publisher(s)"
          if bodies else f"no cached XML under {args.sample}, data-dependent parts skip")
    print()
    part_one(bodies)
    part_two(bodies, args.start, args.end)

    print()
    print("=" * 78)
    print("ALL CHECKS PASS" if not fails else "FAILURES: " + "; ".join(fails))
    print("  (any money above is illustrative, the exchange rates are invented constants)")
    print("=" * 78)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
