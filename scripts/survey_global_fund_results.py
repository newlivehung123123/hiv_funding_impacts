"""
Survey probe three for the Global Fund, why no country reports an HIV testing result for 2025.

Item 33 of RESUME.md records what the panel run of 1 October 2026 showed. The series
`hiv_tests_performed` reports 53, 61, 67, 66, 68, 68, 71 and 65 countries for the years 2017 to
2024 and reports no country at all for 2025, while every other Global Fund series the panel
carries keeps reporting into 2025. `on_art_count` goes from 95 countries to 92, `tbhiv_on_art`
from 72 to 67, `kp_reached` from 70 to 67, `kp_tested` from 66 to 62, `pmtct_arv_count` from 54
to 53, `tpt_initiations` holds at 59 and `prep_recipients` rises from 35 to 43. Counted tests
run 85,834,670 in 2017, then 119,646,182, 121,913,665, 96,724,521, 67,225,600, 48,316,978,
48,117,233 and 41,029,772 in 2024, and then stop.

A fall from 41 million counted tests to none is not a finding the panel can publish without
knowing the cause, because a publisher's reporting gap and a real collapse in testing would be
written up as opposite findings. The offline evidence cannot separate the causes, because
`hivimpact/connectors/global_fund.py` keeps no copy of the rows the connector reads and drops.
The run of 1 October 2026 read 17,538 `Annual_Results` rows, emitted 6,789 and dropped the rest
without saving any of them, so a 2025 testing row that was dropped is invisible on disk today.
The saved `data/raw/global_fund/annual-results.csv`, downloaded by hand on 18 July 2026, holds
one year only, being 2024, so that file cannot answer the question either.

This probe makes one request, saves every row the request returns and then answers the question
offline. Five causes would each produce the same silence in the panel, and the five are
separated here by name rather than pooled.

  1. The Global Fund has published no 2025 testing row of any kind. A reporting gap, and the
     panel's job is then to say so in the series note and leave 2025 empty.

  2. The 2025 testing rows exist at a `geographicCoverage` other than National. The connector
     emits National rows only, for the reason its own docstring gives, which is that a grant's
     catchment wears a country's code and a subnational count would read as a national one. The
     run of 1 October dropped 2,328 subnational rows across all years and all indicators, and
     whether any of the 2,328 is a 2025 testing row is exactly what cause two asks.

  3. The 2025 testing rows exist at National coverage and carry an empty `resultValueNumerator`.
     The connector drops a row whose numerator will not read as a number, which is correct for a
     row that states no value, but a row reported without a value yet is a different fact from a
     row never reported, and the series note should say which.

  4. The indicator was renamed, so the 2025 rows carry a name `_SERIES` does not map.
     `hiv_tests_performed` is fed by one name alone, being `Total number of HIV tests`, so a
     rename would take the whole series to nothing in one year while leaving the underlying
     counts untouched. The new-name warning on the run of 1 October named one unmapped name not
     there when the connector was written, being `TB patients with DST result for at least
     Rifampicin` with 15 rows, and 15 rows is far too few to be 65 countries of testing, so
     cause four is the least likely of the five. Least likely is not ruled out, because a
     renamed series could also have landed on a name the connector already knows and ignores,
     and `_KNOWN_UNMAPPED` would then absorb the rename in silence. This probe prints the row
     count by year for every unmapped name as well, so a rename into a known-ignored name is
     visible.

  5. The 2025 testing rows exist at National coverage with a numerator and should have been
     emitted. Cause five would mean the loss happened after the connector read the row, and the
     search would move to `hivimpact/writers.py` and the merge, not to the Global Fund.

What the probe does not do. The probe reads the service and writes under
`data/raw/global_fund/`, and the probe writes nothing under `data/panel/`, so no panel row
moves and no run of `scripts/run_all.py` is implied by running the probe.

Run

    python3 scripts/survey_global_fund_results.py

Written 1 October 2026, to be run by Jason.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# The indicator map, the ignore list and the dataset name are imported and not copied, so that
# this probe cannot read one service name differently from the connector whose silence it is
# explaining. The same reason keeps the Global Fund country-code map in one module, which the
# comment above GF_CODE_ALIASES in the connector sets out.
from hivimpact.connectors.global_fund import (  # noqa: E402
    _BASE, _DATASET, _KNOWN_UNMAPPED, _SERIES, GlobalFundConnector,
)

#: The one service name that feeds hiv_tests_performed, read back out of the connector's map so
#: that a later edit to the map cannot leave this probe asking about a name nobody maps.
_TESTING_NAMES = sorted(n for n, s in _SERIES.items() if s.canonical == "hiv_tests_performed")

#: The year the series stops, and the year before, which is the comparison every finding below
#: is stated against.
_GAP_YEAR = 2025
_LAST_YEAR = 2024


class Probe(GlobalFundConnector):
    """The connector's own session, user agent, timeout and retries, with one change.

    A 400 is not retried, because OData answers 400 when a property named in a filter does not
    exist and retrying a question the service has already answered wastes half a minute.
    """

    RETRYABLE_STATUS = (429, 500, 502, 503, 504)


def fetch_rows(conn: Probe, out: pathlib.Path, page_cap: int) -> List[dict]:
    """GET the whole Annual_Results dataset, following paging, and save every row."""
    url = f"{_BASE}/AllProgrammaticIndicators?$filter=programmaticDataSet eq '{_DATASET}'"
    rows: List[dict] = []
    pages = 0
    print(f"== one request to {_BASE}")
    print(f"   {url}")
    while url and pages < page_cap:
        resp = conn._request("GET", url)
        payload = resp.json()
        rows.extend(payload.get("value") or [])
        nxt = payload.get("@odata.nextLink")
        if nxt and not str(nxt).lower().startswith("http"):
            nxt = f"{_BASE}/{str(nxt).lstrip('/')}"
        url = nxt
        pages += 1
    truncated = bool(url)
    path = out / f"dataset_{_DATASET}.json"
    path.write_text(json.dumps(rows, indent=1, default=str))
    print(f"   {len(rows):,} rows over {pages} page(s) -> {path.name}"
          + (f"  TRUNCATED at the {page_cap}-page cap" if truncated else ""))
    if truncated:
        print("   the saved copy is partial, so every count below is a floor and not a total")
    return rows


def _coverage(r: dict) -> str:
    return str(r.get("geographicCoverage") or "").strip() or "(empty)"


def _year(r: dict):
    try:
        return int(r.get("resultValueYear"))
    except (TypeError, ValueError):
        return None


def _has_value(r: dict) -> bool:
    try:
        float(r.get("resultValueNumerator"))
        return True
    except (TypeError, ValueError):
        return False


def report(rows: List[dict], out: pathlib.Path) -> Dict[str, Any]:
    """Answer the five causes offline and print each answer in its own words."""
    finding: Dict[str, Any] = {"probed_at": dt.datetime.now().isoformat(timespec="seconds"),
                               "rows_read": len(rows), "dataset": _DATASET,
                               "testing_names_in_the_connector_map": _TESTING_NAMES}

    years = Counter(y for y in (_year(r) for r in rows) if y is not None)
    print("\n== rows by year, every indicator and every coverage")
    for y in sorted(years):
        print(f"   {y}  {years[y]:>6,}")
    finding["rows_by_year"] = {str(k): v for k, v in sorted(years.items())}

    # -- cause one and cause two, together -------------------------------------
    testing = [r for r in rows if str(r.get("indicatorName") or "").strip() in _TESTING_NAMES]
    print(f"\n== the testing rows, being every row named {' or '.join(repr(n) for n in _TESTING_NAMES)}")
    print(f"   {len(testing):,} rows in the dataset")
    grid: Dict[Any, Counter] = defaultdict(Counter)
    for r in testing:
        grid[_year(r)][_coverage(r)] += 1
    print("   year   coverage breakdown")
    for y in sorted(grid, key=lambda v: (v is None, v)):
        parts = ", ".join(f"{cov} {n}" for cov, n in sorted(grid[y].items()))
        print(f"   {y if y is not None else 'no year':<6} {parts}")
    finding["testing_rows_by_year_and_coverage"] = {
        str(y): dict(sorted(grid[y].items()))
        for y in sorted(grid, key=lambda v: (v is None, v))}

    # -- cause four is measured before the verdict, because a rename and a publisher's gap
    # -- look identical from the mapped name alone and only the rename evidence tells them
    # -- apart. A gained name is a candidate rename when the name is one the connector does
    # -- not emit, being either new or known and ignored, and when the name carries at least
    # -- half as many National rows in the gap year as the testing series carried in the year
    # -- before. Half is a floor and not a test of identity, and the printed table below is
    # -- what settles identity, because only a person reading the two names can say whether
    # -- one name replaced the other.
    def names_in(y: int) -> set:
        return {str(r.get("indicatorName") or "").strip() for r in rows if _year(r) == y}

    def national_rows(name: str, y: int) -> int:
        return sum(1 for r in rows if _year(r) == y and _coverage(r) == "National"
                   and str(r.get("indicatorName") or "").strip() == name)

    gained = sorted(names_in(_GAP_YEAR) - names_in(_LAST_YEAR))
    lost = sorted(names_in(_LAST_YEAR) - names_in(_GAP_YEAR))
    testing_before = sum(national_rows(n, _LAST_YEAR) for n in _TESTING_NAMES)
    candidates = [n for n in gained
                  if n not in _SERIES
                  and national_rows(n, _GAP_YEAR) >= max(1, testing_before // 2)]

    gap_rows = [r for r in testing if _year(r) == _GAP_YEAR]
    if not gap_rows and candidates:
        print(f"\n   CAUSE FOUR. The service publishes no {_GAP_YEAR} row under the name the "
              f"connector maps, and {len(candidates)} name(s) the connector does not emit "
              f"appear in {_GAP_YEAR} carrying enough National rows to be the same series "
              f"renamed. Read the two names below before concluding anything, and if one name "
              f"has replaced the other then the fix is a line in _SERIES and a rerun of the "
              f"global_fund connector.")
        for n in candidates:
            where = "known and ignored" if n in _KNOWN_UNMAPPED else "new and unmapped"
            print(f"      candidate, {national_rows(n, _GAP_YEAR)} National rows "
                  f"[{where}]  {n}")
        finding["cause"] = "four, the series is probably renamed"
        finding["rename_candidates"] = candidates
    elif not gap_rows:
        print(f"\n   CAUSE ONE. The service publishes no {_GAP_YEAR} testing row of any "
              f"coverage, and no name the connector leaves out carries enough {_GAP_YEAR} "
              f"National rows to be the same series renamed. The gap is the publisher's and "
              f"the panel states the gap in the series note.")
        finding["cause"] = "one, no row published at any coverage"
    else:
        cov = Counter(_coverage(r) for r in gap_rows)
        national = [r for r in gap_rows if _coverage(r) == "National"]
        print(f"\n   {len(gap_rows)} testing row(s) exist for {_GAP_YEAR}, by coverage "
              + ", ".join(f"{k} {v}" for k, v in sorted(cov.items())))
        if not national:
            print(f"   CAUSE TWO. Every {_GAP_YEAR} testing row sits at a coverage other than "
                  f"National, so the connector dropped the rows by design and the panel states "
                  f"that the {_GAP_YEAR} reporting is subnational only.")
            finding["cause"] = "two, published only at a coverage other than National"
        else:
            valued = [r for r in national if _has_value(r)]
            print(f"   National coverage on {len(national)} of the {_GAP_YEAR} testing rows, "
                  f"and a number on {len(valued)} of the National rows")
            if not valued:
                print(f"   CAUSE THREE. Every National {_GAP_YEAR} testing row states no "
                      f"value, so the countries have reported without a count, and the panel "
                      f"says reported-without-a-value and not never-reported.")
                finding["cause"] = "three, National rows published with no numerator"
            else:
                print(f"   CAUSE FIVE. {len(valued)} National {_GAP_YEAR} row(s) carry a "
                      f"number and the panel holds no {_GAP_YEAR} testing row at all, so the "
                      f"loss is downstream of the connector and the next place to look is "
                      f"hivimpact/writers.py and the merge.")
                finding["cause"] = "five, rows are emittable and the panel lost them later"
                finding["countries_on_the_lost_rows"] = sorted(
                    {str(r.get("recordId")) for r in valued})

    # -- the rename evidence in full, every gained and every lost name, whether or not one of
    # -- the gained names cleared the candidate floor above ---------------------------
    print(f"\n== cause four, a rename. {len(gained)} name(s) appear in {_GAP_YEAR} and not in "
          f"{_LAST_YEAR}, and {len(lost)} name(s) appear in {_LAST_YEAR} and not in {_GAP_YEAR}")
    for n in gained:
        n_rows = sum(1 for r in rows if _year(r) == _GAP_YEAR
                     and str(r.get("indicatorName") or "").strip() == n)
        where = ("mapped" if n in _SERIES else
                 "known and ignored" if n in _KNOWN_UNMAPPED else "NEW AND UNMAPPED")
        print(f"   gained  {n_rows:>5} rows  [{where}]  {n}")
    for n in lost:
        n_rows = sum(1 for r in rows if _year(r) == _LAST_YEAR
                     and str(r.get("indicatorName") or "").strip() == n)
        where = ("mapped" if n in _SERIES else
                 "known and ignored" if n in _KNOWN_UNMAPPED else "new and unmapped")
        print(f"   lost    {n_rows:>5} rows  [{where}]  {n}")
    finding["names_gained_in_the_gap_year"] = gained
    finding["names_lost_after_the_last_year"] = lost

    # -- the whole picture, so the five causes can be read against every series ------
    print(f"\n== every indicator name, National rows in {_LAST_YEAR} and in {_GAP_YEAR}")
    all_names = sorted({str(r.get("indicatorName") or "").strip() for r in rows})
    per_name: Dict[str, Dict[str, int]] = {}
    for n in all_names:
        a = sum(1 for r in rows if _year(r) == _LAST_YEAR and _coverage(r) == "National"
                and str(r.get("indicatorName") or "").strip() == n)
        b = sum(1 for r in rows if _year(r) == _GAP_YEAR and _coverage(r) == "National"
                and str(r.get("indicatorName") or "").strip() == n)
        per_name[n] = {str(_LAST_YEAR): a, str(_GAP_YEAR): b}
        if a or b:
            flag = "  <- stops" if a and not b else ("  <- starts" if b and not a else "")
            mapped = "map" if n in _SERIES else ("ign" if n in _KNOWN_UNMAPPED else "NEW")
            print(f"   [{mapped}] {a:>4} -> {b:>4}  {n}{flag}")
    finding["national_rows_by_name"] = per_name

    path = out / "results_probe.json"
    path.write_text(json.dumps(finding, indent=1, default=str))
    print(f"\nreport written to {path}")
    return finding


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Global Fund Annual_Results, probe three, the 2025 HIV testing gap")
    ap.add_argument("--out", default=None,
                    help="output directory, default data/raw/global_fund/results_probe_<today>")
    ap.add_argument("--page-cap", type=int, default=40,
                    help="stop following @odata.nextLink after this many pages, default 40")
    args = ap.parse_args()

    out = pathlib.Path(args.out) if args.out else (
        ROOT / "data" / "raw" / "global_fund"
        / f"results_probe_{dt.date.today().strftime('%Y%m%d')}")
    out.mkdir(parents=True, exist_ok=True)
    print(f"output directory {out}")

    conn = Probe()
    rows = fetch_rows(conn, out, args.page_cap)
    if not rows:
        print("no rows returned, so nothing can be concluded")
        return 1
    report(rows, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
