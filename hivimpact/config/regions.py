"""
Regional grouping of low- and middle-income countries, used by the site build.

The panel itself is keyed on ISO3 and knows nothing about regions. This module supplies
the regional layer the interface needs: which countries belong to each region, which
regions are published, and which regions are still to be assessed.

Regions follow the UNAIDS reporting groupings, with two departures made for this project.
Asia and the Pacific is split into Southeast Asia, South Asia, and East Asia and the
Pacific, because Southeast Asia is the pilot and needs to stand on its own. High-income
countries are excluded throughout, since the project concerns low- and middle-income
settings.

Each list states the countries in scope for that region, not every territory a statistical
agency might assign to it. The counts shown in the interface are counts of these lists.

STATUS values
  live        a curated regional view exists and country-level connectors have been built
  planned     the aggregator connectors already return these countries, but no country-level
              feasibility assessment has been carried out and no regional view is published
"""
from __future__ import annotations

from typing import Dict, List

from .countries import SEA_ISO3

LIVE = "live"
PLANNED = "planned"


REGIONS: List[Dict] = [
    {
        "slug": "southeast-asia",
        "name": "Southeast Asia",
        "status": LIVE,
        "phase": "Phase 1.1",
        "iso3": list(SEA_ISO3),
        "note": ("Cambodia, the Philippines and Thailand are read at source, and Indonesia "
                 "has reports from community-led monitoring."),
    },
    {
        "slug": "south-asia",
        "name": "South Asia",
        "status": PLANNED,
        "phase": "Phase 3",
        "iso3": ["AFG", "BGD", "BTN", "IND", "MDV", "NPL", "PAK", "LKA"],
        "note": "No country in the region has yet been assessed for national sources.",
    },
    {
        "slug": "east-asia-and-the-pacific",
        "name": "East Asia and the Pacific",
        "status": PLANNED,
        "phase": "Phase 3",
        "iso3": ["CHN", "MNG", "PRK", "PNG", "FJI", "SLB", "VUT", "WSM", "TON",
                 "KIR", "TUV", "FSM", "MHL"],
        "note": "No country in the region has yet been assessed for national sources.",
    },
    {
        "slug": "eastern-and-southern-africa",
        "name": "Eastern and Southern Africa",
        "status": LIVE,
        "phase": "Phase 3",
        "iso3": ["AGO", "BWA", "BDI", "COM", "ERI", "SWZ", "ETH", "KEN", "LSO", "MDG",
                 "MWI", "MUS", "MOZ", "NAM", "RWA", "SOM", "ZAF", "SSD", "TZA", "UGA",
                 "ZMB", "ZWE"],
        "note": ("South Africa is read at source, through the Thembisa model of the "
                 "University of Cape Town."),
    },
    {
        "slug": "western-and-central-africa",
        "name": "Western and Central Africa",
        "status": LIVE,
        "phase": "Phase 4",
        "iso3": ["BEN", "BFA", "CPV", "CMR", "CAF", "TCD", "COG", "COD", "CIV", "GNQ",
                 "GAB", "GMB", "GHA", "GIN", "GNB", "LBR", "MLI", "MRT", "NER", "NGA",
                 "STP", "SEN", "SLE", "TGO"],
        "note": "Nigeria, Cameroon, Niger, Guinea and Chad are read at source.",
    },
    {
        "slug": "latin-america-and-the-caribbean",
        "name": "Latin America and the Caribbean",
        "status": PLANNED,
        "phase": "Phase 3",
        "iso3": ["ARG", "BLZ", "BOL", "BRA", "COL", "CRI", "CUB", "DOM", "ECU", "SLV",
                 "GTM", "GUY", "HTI", "HND", "JAM", "MEX", "NIC", "PAN", "PRY", "PER",
                 "SUR", "TTO", "VEN"],
        "note": "No country in the region has yet been assessed for national sources.",
    },
    {
        "slug": "middle-east-and-north-africa",
        "name": "Middle East and North Africa",
        "status": PLANNED,
        "phase": "Phase 3",
        "iso3": ["DZA", "DJI", "EGY", "IRN", "IRQ", "JOR", "LBN", "LBY", "MAR", "SDN",
                 "SYR", "TUN", "PSE", "YEM"],
        "note": "No country in the region has yet been assessed for national sources.",
    },
    {
        "slug": "eastern-europe-and-central-asia",
        "name": "Eastern Europe and Central Asia",
        "status": PLANNED,
        "phase": "Phase 3",
        "iso3": ["ALB", "ARM", "AZE", "BLR", "BIH", "GEO", "KAZ", "KGZ", "MDA", "MNE",
                 "MKD", "SRB", "TJK", "TKM", "TUR", "UKR", "UZB"],
        "note": "No country in the region has yet been assessed for national sources.",
    },
]


def region_by_slug(slug: str) -> Dict:
    for r in REGIONS:
        if r["slug"] == slug:
            return r
    raise KeyError(slug)


def region_for_iso3(iso3: str) -> Dict | None:
    iso3 = iso3.upper()
    for r in REGIONS:
        if iso3 in r["iso3"]:
            return r
    return None
