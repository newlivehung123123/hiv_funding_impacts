"""
Country sets for the phased build.

Phase 1 connectors are global by construction (one connector pulls every country).
Phase 1.1 filters to Southeast Asia for the first slice we show Adrian — this list is
just that filter, not a separate build.

SEA set = the LMIC members of Southeast Asia with a meaningful HIV response and
PEPFAR/US exposure. Singapore and Brunei (high-income) are intentionally excluded.
Adjust freely — this is a design choice, not a fixed fact.
"""

# Southeast Asian LMICs (ISO3)
# The 9 LMIC countries of Southeast Asia (excludes high-income Brunei & Singapore).
# PNG is Oceania, not SEA — excluded.
SEA_ISO3 = [
    "THA",  # Thailand
    "VNM",  # Vietnam
    "IDN",  # Indonesia
    "PHL",  # Philippines
    "MMR",  # Myanmar
    "KHM",  # Cambodia
    "LAO",  # Lao PDR
    "MYS",  # Malaysia
    "TLS",  # Timor-Leste
]

# Named country sets selectable from the CLI.
COUNTRY_SETS = {
    "sea": SEA_ISO3,
    "all": None,  # None => every country the source publishes
}


def resolve_country_set(name_or_list):
    """Accept a named set ('sea'/'all'), a comma string of ISO3, or a list; return list|None."""
    if name_or_list is None:
        return None
    if isinstance(name_or_list, str):
        if name_or_list in COUNTRY_SETS:
            return COUNTRY_SETS[name_or_list]
        return [c.strip().upper() for c in name_or_list.split(",") if c.strip()]
    return [str(c).strip().upper() for c in name_or_list]
