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
  planned     the aggregator connectors already return these countries, but no regional view
              is published

PHASE values are the work phases of the README, numbered in the order the work began. Phase 1
built the aggregator connectors for every region. Southeast Asia is Phase 2, the phase of the
first country-level connectors. A region with no phase assigned yet carries an empty string.
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
        "phase": "Phase 2",
        "iso3": list(SEA_ISO3),
        "note": ("Cambodia, the Philippines and Thailand are read at source, and Indonesia "
                 "has reports from community-led monitoring."),
    },
    {
        "slug": "south-asia",
        "name": "South Asia",
        "status": LIVE,
        "phase": "Phase 6",
        "iso3": ["AFG", "BGD", "BTN", "IND", "MDV", "NPL", "PAK", "LKA"],
        "note": ("Bangladesh, India, the Maldives, Nepal and Sri Lanka are read at source, "
                 "India through the HIV estimates of the National AIDS Control Organisation."),
    },
    {
        "slug": "east-asia-and-the-pacific",
        "name": "East Asia and the Pacific",
        "status": LIVE,
        "phase": "Phase 7",
        "iso3": ["CHN", "MNG", "PRK", "PNG", "FJI", "SLB", "VUT", "WSM", "TON",
                 "KIR", "TUV", "FSM", "MHL"],
        "note": ("China, Mongolia, North Korea, Papua New Guinea, the Solomon Islands and "
                 "Vanuatu are read at source."),
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
        "status": LIVE,
        "phase": "Phase 5",
        "iso3": ["ARG", "BLZ", "BOL", "BRA", "COL", "CRI", "CUB", "DOM", "ECU", "SLV",
                 "GTM", "GUY", "HTI", "HND", "JAM", "MEX", "NIC", "PAN", "PRY", "PER",
                 "SUR", "TTO", "VEN"],
        "note": ("Argentina, Belize, Bolivia, Haiti, Nicaragua, Paraguay and Peru are read "
                 "at source."),
    },
    {
        "slug": "middle-east-and-north-africa",
        "name": "Middle East and North Africa",
        "status": LIVE,
        "phase": "Phase 9",
        "iso3": ["DZA", "DJI", "EGY", "IRN", "IRQ", "JOR", "LBN", "LBY", "MAR", "SDN",
                 "SYR", "TUN", "PSE", "YEM"],
        "note": "Lebanon is read at source.",
    },
    {
        "slug": "eastern-europe-and-central-asia",
        "name": "Eastern Europe and Central Asia",
        "status": LIVE,
        "phase": "Phase 8",
        "iso3": ["ALB", "ARM", "AZE", "BLR", "BIH", "GEO", "KAZ", "KGZ", "MDA", "MNE",
                 "MKD", "SRB", "TJK", "TKM", "TUR", "UKR", "UZB"],
        "note": ("Armenia, Belarus, Georgia, Kazakhstan, Kyrgyzstan, Montenegro, Tajikistan "
                 "and Ukraine are read at source."),
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
