#!/usr/bin/env python3
"""The Global Fund's own grant table, read against the Global Fund rows already in the panel.

  >>> Read only. This script fetches nothing and writes nothing unless --out is passed.

WHAT THIS ANSWERS. The panel holds the Global Fund's money twice, once through OECD CRS as
donor 9OTH012 and once through the Global Fund's own IATI filing, and section 6 of RESUME.md
reclassified that pair from independent to derived by argument alone in September 2026. The
Global Fund also publishes a grant table of 1,589 grants through its OData service, and every
grant in that table carries the IATI activity identifier the Global Fund files under. Matching
the panel's identifiers against the grant table turns the argument into a count, and the same
match answers two more questions the write-up needs.

  1. ARE THE TWO READINGS THE SAME MONEY. Every Global Fund activity identifier in the panel's
     iati rows either does or does not name a grant the Global Fund itself lists. A complete
     match means the panel is reading one institution's filing by two routes, and agreement
     between the two is not corroboration.

  2. IS THE COMPONENT LETTER RULE RIGHT. `hivimpact/connectors/iati.py:_is_hc_grant` decides
     whether a Global Fund activity is HIV money by reading the component letter out of the
     grant code, which is this project's own rule and not the publisher's. The grant table
     carries the Global Fund's own component label for every grant, so the rule can be checked
     against the label row by row.

  3. HOW MUCH COUNTRY-ATTRIBUTABLE GRANT MONEY THE PANEL MISSES. Any HIV or TB/HIV grant whose
     identifier is absent from the panel is money the panel does not see. A Multicountry or
     Subnational grant absent from the panel is absent by design, because neither can be
     attributed to one country without this project inventing a geography, so the number that
     matters is the country-level one.

HOW THE PANEL'S IDENTIFIERS ARE READ. The `extra` column is parsed as JSON and the keys
`grant_identifiers` and `grants_seen_but_not_hiv_coded` are read out of it. Item 31 dropped
`grants_seen_but_not_hiv_coded` from the connector on 1 October 2026, because the key held the
identical list the same row already carries under `grant_identifiers`. The name stays in the
pair below so this script reads a panel written before that repair and a panel written after
it alike, and a panel written after the repair simply carries nothing under the second name.
An earlier pass
scraped the column with the pattern `47045-[A-Za-z0-9\\-]+` instead, which stops at a space,
and one Global Fund identifier contains a space, being `47045-CMR-C-CARE Cameroon-1`. That
pattern reported 1,489 of 1,491 and counted Cameroon's CARE grant as absent. Nothing here
scrapes the column with a pattern.

A panel identifier carries one more trailing numeric segment than the grant table's
`iatI_ActivityIdentifier` does, so one trailing `-<digits>` is stripped before matching.

    python3 scripts/verify_global_fund_grants.py
    python3 scripts/verify_global_fund_grants.py --out /tmp/gf_grants.json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
csv.field_size_limit(sys.maxsize)

#: The grant table and its two lookup tables, as probe two saved them. A directory rather than
#: three paths, because the three have to come from one fetch or the ids will not line up.
DEFAULT_LOOKUPS = ROOT / "data" / "raw" / "global_fund" / "survey2_20261001"
DEFAULT_PANEL = ROOT / "data" / "panel" / "hiv_panel.csv"

#: The HIV components of the grant table. TB/HIV is one grant funding both diseases, which the
#: Global Fund does not split at grant level, so a TB/HIV grant counts as HIV money here and
#: the tuberculosis share inside it is a caveat the write-up states rather than a number this
#: project can compute.
HIV_COMPONENTS = ("HIV", "TB/HIV")

#: What the run of 1 October 2026 measured, so a later run says whether anything moved rather
#: than quietly printing a different number into the same write-up.
EXPECTED = {
    "panel_identifiers": 2583,
    "panel_identifiers_stripped": 1491,
    "stripped_matching_a_grant": 1491,
    "hiv_grants": 724,
    "hiv_grants_in_panel": 663,
    "all_grants": 1589,
    "all_grants_in_panel": 1491,
    "absent_hiv_grants": 61,
    "letter_rule_disagreements": 0,
    "country_level_absent": 3,
}


def _strip_suffix(identifier: str) -> str:
    """Drop the one trailing numeric segment the panel's identifiers carry."""
    return re.sub(r"-\d+$", "", identifier.strip())


def load_lookups(d: Path) -> Dict[str, list]:
    tables = {}
    for name in ("Grants", "ActivityAreas", "Geographies"):
        path = d / f"lookup_{name}.json"
        if not path.exists():
            raise SystemExit(f"missing {path}. Run scripts/survey_global_fund_financials2.py "
                             f"first, or point --lookups at a directory that holds the three "
                             f"lookup_*.json files.")
        tables[name] = json.loads(path.read_text())
    return tables


def panel_identifiers(panel: Path) -> Set[str]:
    """Every Global Fund activity identifier the panel's iati rows name, read as JSON."""
    found: Set[str] = set()
    with panel.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("source_id") != "iati":
                continue
            raw = row.get("extra") or ""
            if "47045" not in raw:
                continue
            try:
                extra = json.loads(raw)
            except (TypeError, ValueError):
                continue
            for key in ("grant_identifiers", "grants_seen_but_not_hiv_coded"):
                for identifier in extra.get(key) or []:
                    text = str(identifier).strip()
                    if text.startswith("47045-"):
                        found.add(text)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lookups", default=str(DEFAULT_LOOKUPS),
                    help="directory holding lookup_Grants.json, lookup_ActivityAreas.json "
                         "and lookup_Geographies.json")
    ap.add_argument("--panel", default=str(DEFAULT_PANEL))
    ap.add_argument("--out", default=None,
                    help="optional path for a JSON copy of every number printed below")
    args = ap.parse_args()

    panel = Path(args.panel)
    if not panel.exists():
        raise SystemExit(f"no panel at {panel}")
    tables = load_lookups(Path(args.lookups))

    from hivimpact.connectors.iati import _is_hc_grant

    grants = tables["Grants"]
    area_by_id = {str(a["id"]): a for a in tables["ActivityAreas"] if a.get("id")}
    geo_by_id = {str(g["id"]): g for g in tables["Geographies"] if g.get("id")}

    def component_of(grant: dict) -> Optional[str]:
        area = area_by_id.get(str(grant.get("activityAreaId")))
        return area.get("name") if area else None

    def level_of(grant: dict) -> Optional[str]:
        geo = geo_by_id.get(str(grant.get("geographyId")))
        return geo.get("level") if geo else None

    def disbursed(grant: dict) -> float:
        try:
            return float(grant.get("totalDisbursedAmount_ReferenceRate") or 0.0)
        except (TypeError, ValueError):
            return 0.0

    hiv_grants = [g for g in grants if component_of(g) in HIV_COMPONENTS]
    hiv_ids = {str(g["iatI_ActivityIdentifier"]).strip() for g in hiv_grants
               if g.get("iatI_ActivityIdentifier")}
    all_ids = {str(g["iatI_ActivityIdentifier"]).strip() for g in grants
               if g.get("iatI_ActivityIdentifier")}

    found = panel_identifiers(panel)
    stripped = {_strip_suffix(i) for i in found}

    measured: Dict[str, object] = {
        "panel": str(panel),
        "lookups": str(Path(args.lookups)),
        "panel_identifiers": len(found),
        "panel_identifiers_stripped": len(stripped),
        "all_grants": len(all_ids),
        "hiv_grants": len(hiv_grants),
    }

    print("The Global Fund grant table against the panel")
    print("=============================================")
    print(f"grant table      {len(grants):,} grants, {len(all_ids):,} carrying an IATI "
          f"activity identifier")
    print(f"                 components " + ", ".join(
        f"{name} {n}" for name, n in Counter(
            component_of(g) or "unresolved" for g in grants).most_common()))
    print(f"panel            {len(found):,} Global Fund activity identifiers in the iati rows, "
          f"{len(stripped):,} after one suffix strip")

    # -- 1. the same money, by count ---------------------------------------------------
    print()
    print("1. Are the two Global Fund readings the same money")
    print("--------------------------------------------------")
    matched = stripped & all_ids
    unmatched = sorted(stripped - all_ids)
    measured["stripped_matching_a_grant"] = len(matched)
    measured["stripped_matching_no_grant"] = unmatched
    print(f"  panel identifiers naming a grant the Global Fund lists: "
          f"{len(matched):,} of {len(stripped):,}")
    for identifier in unmatched[:20]:
        print(f"    names no grant  {identifier}")
    if len(unmatched) > 20:
        print(f"    ... and {len(unmatched) - 20} more")

    in_panel_hiv = hiv_ids & stripped
    in_panel_all = all_ids & stripped
    measured["hiv_grants_in_panel"] = len(in_panel_hiv)
    measured["all_grants_in_panel"] = len(in_panel_all)
    print(f"  HIV and TB/HIV grants present in the panel: {len(in_panel_hiv):,} of "
          f"{len(hiv_ids):,} ({100 * len(in_panel_hiv) / max(len(hiv_ids), 1):.1f} per cent)")
    print(f"  grants of any component present in the panel: {len(in_panel_all):,} of "
          f"{len(all_ids):,} ({100 * len(in_panel_all) / max(len(all_ids), 1):.1f} per cent)")
    if unmatched:
        print("  VERDICT: some panel identifiers name no grant, so the two readings are not "
              "a complete overlap. Read the identifiers above before writing anything.")
    else:
        print("  VERDICT: every panel identifier names a grant the Global Fund lists, so the "
              "iati reading and the OECD CRS donor-9OTH012 reading are one institution's "
              "filing reaching the panel by two routes. Agreement between the two is NOT "
              "corroboration, and reconcile.py classifies the pair as derived.")

    # -- 2. the component letter rule --------------------------------------------------
    print()
    print("2. The component letter rule against the Global Fund's own label")
    print("----------------------------------------------------------------")
    label: Dict[str, str] = {}
    for g in grants:
        identifier = str(g.get("iatI_ActivityIdentifier") or "").strip()
        component = component_of(g)
        if identifier and component:
            label[identifier] = component
    agreements = 0
    disagreements: List[dict] = []
    unlabelled = 0
    for identifier in sorted(found):
        key = _strip_suffix(identifier)
        if key not in label:
            unlabelled += 1
            continue
        rule_says = bool(_is_hc_grant(identifier))
        publisher_says = label[key] in HIV_COMPONENTS
        if rule_says == publisher_says:
            agreements += 1
        else:
            disagreements.append({"identifier": identifier, "component": label[key],
                                  "rule_says_hiv": rule_says})
    measured["letter_rule_agreements"] = agreements
    measured["letter_rule_disagreements"] = len(disagreements)
    measured["letter_rule_unlabelled"] = unlabelled
    print(f"  panel identifiers reaching a labelled grant: {agreements + len(disagreements):,}")
    print(f"  agreements {agreements:,}, disagreements {len(disagreements)}, "
          f"identifiers reaching no labelled grant {unlabelled}")
    for d in disagreements[:20]:
        print(f"    disagreement  {d['identifier']}  Global Fund says {d['component']}, "
              f"_is_hc_grant says {'HIV' if d['rule_says_hiv'] else 'not HIV'}")
    if not disagreements:
        print("  VERDICT: the letter rule in hivimpact/connectors/iati.py agrees with the "
              "publisher's own component on every identifier, so the tuberculosis share "
              "caveat is a real property of the Global Fund's combined TB/HIV grants and is "
              "not a misclassification by this project.")

    # -- 3. the coverage statement -----------------------------------------------------
    print()
    print("3. What the panel's Global Fund reading misses")
    print("----------------------------------------------")
    absent = [g for g in hiv_grants
              if str(g.get("iatI_ActivityIdentifier") or "").strip() not in stripped]
    total_money = sum(disbursed(g) for g in hiv_grants)
    absent_money = sum(disbursed(g) for g in absent)
    by_level = Counter(level_of(g) or "unresolved" for g in absent)
    country_absent = [g for g in absent if level_of(g) == "Country"]
    country_money = sum(disbursed(g) for g in country_absent)
    measured.update({
        "absent_hiv_grants": len(absent),
        "absent_hiv_money_usd": round(absent_money, 2),
        "hiv_money_usd": round(total_money, 2),
        "absent_by_level": dict(by_level),
        "country_level_absent": len(country_absent),
        "country_level_absent_money_usd": round(country_money, 2),
    })
    print(f"  HIV and TB/HIV grants absent from the panel: {len(absent)} of {len(hiv_grants)}, "
          f"carrying {absent_money:,.0f} USD of {total_money:,.0f} "
          f"({100 * absent_money / max(total_money, 1):.2f} per cent)")
    print(f"  their geography levels: " + ", ".join(
        f"{lvl} {n}" for lvl, n in by_level.most_common()))
    print("  Multicountry and Subnational grants are absent BY DESIGN, because neither can be "
          "attributed to\n  one country without this project inventing a geography. The "
          "country-level ones are the gap:")
    for g in sorted(country_absent, key=lambda x: -disbursed(x)):
        geo = geo_by_id.get(str(g.get("geographyId"))) or {}
        print(f"    {str(g.get('code')):22s} {str(geo.get('name') or ''):18s} "
              f"{disbursed(g):>14,.0f} USD  {component_of(g)}")
    print(f"  SO: the panel's reading of Global Fund HIV money misses {country_money:,.0f} USD "
          f"of country-attributable\n      grant money out of {total_money:,.0f}.")

    # -- did anything move since 1 October 2026 ----------------------------------------
    print()
    print("Against the run of 1 October 2026")
    print("---------------------------------")
    moved = []
    for key, was in EXPECTED.items():
        now = measured.get(key)
        if now != was:
            moved.append((key, was, now))
    if not moved:
        print("  every count above is what the run of 1 October 2026 measured.")
    else:
        print("  SOMETHING MOVED. A changed count is either a rebuilt panel or a changed grant")
        print("  table, and the two are different facts, so check which before writing.")
        for key, was, now in moved:
            print(f"    {key:32s} was {was}, now {now}")

    if args.out:
        Path(args.out).write_text(json.dumps(measured, indent=1, default=str))
        print(f"\nwritten to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
