"""
Country-name / code normalization to ISO 3166-1 alpha-3.

World Bank and WHO GHO already emit ISO3; UNAIDS CSV exports and OECD CRS emit
country *names*, which must be mapped. We use `pycountry` when available (handles
fuzzy names and historical spellings) and fall back to an explicit override map for
the names those libraries get wrong or that appear in AIDSinfo/OECD exports.

Never silently drop an unmapped country — return None and let the caller log it, so
coverage gaps are visible and not hidden.

THE FUZZY TRAP
--------------
`pycountry.search_fuzzy` matches SUBDIVISION names as well as country names, and it
always returns its best guess. "OHR" is a municipality of North Macedonia and "WI" a
district of England, so an unguarded fuzzy pass answers a donor's regional aggregate
code with a country and books a region's money to it. That is not hypothetical: the
first all-country run of the panel made the United Kingdom the largest recipient of US
HIV aid in the world, at 59.9bn USD, because OECD CRS aggregate recipient codes were
fuzzy-matched into GBR and MKD.

So a fuzzy hit is now only accepted when the query actually contains the matched
country's name (`_fuzzy_ok`), and sources that publish *codes*, not names, should
call `code_to_iso3`, which does no fuzzy matching at all. A code either is an ISO3
country or is not one, and guessing at the difference is how aggregates get in.
"""
from __future__ import annotations

import re
from typing import Optional

try:
    import pycountry  # type: ignore
    _HAS_PYCOUNTRY = True
except Exception:  # pragma: no cover - pycountry is optional
    _HAS_PYCOUNTRY = False

# Names as they commonly appear in UNAIDS AIDSinfo / OECD CRS exports that pycountry
# either misses or spells differently. Extend this as real exports reveal new spellings.
_OVERRIDES = {
    "bolivia (plurinational state of)": "BOL",
    "bolivia": "BOL",
    "cote d'ivoire": "CIV",
    "côte d'ivoire": "CIV",
    "cote d ivoire": "CIV",
    "democratic republic of the congo": "COD",
    "dr congo": "COD",
    "congo dem. rep.": "COD",
    "congo, dem. rep.": "COD",
    # The DHS Program's own spelling. Without this line every DHS row for DR Congo was
    # dropped silently, including the CD2023 survey — the most recent HIV-testing survey
    # in West and Central Africa, in the region's second-largest epidemic. Found while
    # desk-researching WCA, by comparing the DHS country list against this mapping.
    "congo democratic republic": "COD",
    "congo": "COG",
    "congo, rep.": "COG",
    "iran (islamic republic of)": "IRN",
    "iran": "IRN",
    "lao people's democratic republic": "LAO",
    "lao pdr": "LAO",
    "laos": "LAO",
    "republic of moldova": "MDA",
    "moldova": "MDA",
    "united republic of tanzania": "TZA",
    "tanzania": "TZA",
    "venezuela (bolivarian republic of)": "VEN",
    "venezuela": "VEN",
    "viet nam": "VNM",
    "vietnam": "VNM",
    "syrian arab republic": "SYR",
    "syria": "SYR",
    "republic of korea": "KOR",
    "korea, rep.": "KOR",
    "democratic people's republic of korea": "PRK",
    "north korea": "PRK",
    "russian federation": "RUS",
    "türkiye": "TUR",
    "turkiye": "TUR",
    "turkey": "TUR",
    "cabo verde": "CPV",
    "cape verde": "CPV",
    "russia": "RUS",
    "brunei": "BRN",
    # ForeignAssistance.gov spells these without the accent / long form, and the fuzzy
    # pass used to answer Curaçao with the NETHERLANDS and Kosovo with SERBIA — two
    # countries' aid merged into a third's series.
    "curacao": "CUW",
    "curaçao": "CUW",
    # Kosovo has no ISO 3166-1 code; XKX is the user-assigned code the World Bank and
    # most panels use. Filing it under Serbia would be a political claim, not a mapping.
    "kosovo": "XKX",
    "eswatini": "SWZ",
    "swaziland": "SWZ",
    "myanmar": "MMR",
    "burma": "MMR",
    # ForeignAssistance.gov's own spellings. Without these the US disbursement series
    # simply has no Myanmar and no China in it — 111.8m and 69.0m USD of HIV
    # disbursements that read as an absence of aid instead of an unmatched string. Its
    # "... Region" and "(former)" labels are aggregates and historical states, and stay
    # unmapped on purpose.
    "burma (myanmar)": "MMR",
    "china (p.r.c.)": "CHN",
    "china (hong kong, s.a.r., p.r.c.)": "HKG",
    "china (macau, s.a.r., p.r.c.)": "MAC",
    "korea, democratic republic of": "PRK",
    "kiribati, republic of": "KIR",
    "west bank and gaza": "PSE",
    "st. kitts and nevis": "KNA",
    "st. lucia": "LCA",
    "st. vincent and grenadines": "VCT",
    "the gambia": "GMB",
    "gambia": "GMB",
    "kyrgyzstan": "KGZ",
    "kyrgyz republic": "KGZ",
    "micronesia (federated states of)": "FSM",
    "micronesia": "FSM",
    "papua new guinea": "PNG",
    "timor-leste": "TLS",
    "east timor": "TLS",
    "philippines": "PHL",
    "brunei darussalam": "BRN",
}


def _words(text: str) -> set:
    """Distinguishing words of a country name, lowercased. Short words are dropped
    because 'of', 'the' and 'and' identify nothing."""
    return {w for w in re.split(r"[^a-z]+", str(text).lower()) if len(w) >= 4}


def _fuzzy_ok(query: str, rec) -> bool:
    """True when a fuzzy hit is a real name match and not a subdivision accident.

    The test is one-directional on purpose: every distinguishing word of the country's
    own name has to appear in the query. "Micronesia (Federated States of)" keeps its
    match on "Micronesia, Federated States of"; "Africa" does NOT get to be South
    Africa, and "OHR" does not get to be North Macedonia.
    """
    q = _words(query)
    if not q:
        return False
    for attr in ("common_name", "name", "official_name"):
        name = getattr(rec, attr, None)
        if name and _words(name) <= q:
            return True
    return False


# Codes that are real aid recipients but have no ISO 3166-1 entry, so pycountry cannot
# confirm them and the strict path would drop them. Kosovo is a CRS recipient in its own
# right; XKX is the user-assigned code the World Bank and most panels use for it.
_USER_ASSIGNED = {"XKX"}

# Publishers' own codes for the same places, mapped onto the code the panel uses. OECD
# CRS calls Kosovo XKV and the World Bank calls it XKX; left alone the two sit in the
# panel as different countries. The 2026-08-03 run is how XKV was found — it was the one
# real recipient in the list of skipped codes the connector now prints.
_CODE_ALIASES = {"XKV": "XKX"}

# pycountry has no entry to read a name out of for these, so the panel would print the
# code where every other country prints a name.
_USER_ASSIGNED_NAMES = {"XKX": "Kosovo"}


def code_to_iso3(code: str) -> Optional[str]:
    """Strict ISO3 resolution for sources that publish CODES, not names.

    Returns the code when it is an ISO 3166-1 alpha-3 country and None for everything
    else — regional aggregates, "unallocated" buckets, donor mnemonics. No fuzzy
    matching, so the caller can count and log what it skipped instead of finding a
    region's money filed under a country (see THE FUZZY TRAP above).
    """
    if not code:
        return None
    raw = str(code).strip().upper()
    if len(raw) != 3 or not raw.isalpha():
        return None
    raw = _CODE_ALIASES.get(raw, raw)
    if raw in _USER_ASSIGNED:
        return raw
    if not _HAS_PYCOUNTRY:
        return raw
    return raw if pycountry.countries.get(alpha_3=raw) else None


def to_iso3(name_or_code: str) -> Optional[str]:
    """Return an uppercase ISO3 code for a country name or code, or None if unmapped."""
    if not name_or_code:
        return None
    raw = str(name_or_code).strip()

    # Already an ISO3?
    if len(raw) == 3 and raw.isalpha():
        candidate = raw.upper()
        if not _HAS_PYCOUNTRY:
            return candidate
        if pycountry.countries.get(alpha_3=candidate):
            return candidate

    key = raw.lower()
    if key in _OVERRIDES:
        return _OVERRIDES[key]

    # A source publishing a code in its country column still gets the strict answer:
    # "XKX" and OECD's "XKV" are Kosovo, and neither is in pycountry.
    if len(raw) == 3:
        strict = code_to_iso3(raw)
        if strict is not None:
            return strict

    if _HAS_PYCOUNTRY:
        rec = pycountry.countries.get(alpha_3=raw.upper()) if len(raw) == 3 else None
        if rec is None and len(raw) == 2:
            rec = pycountry.countries.get(alpha_2=raw.upper())
        if rec is None:
            rec = pycountry.countries.get(name=raw)
        if rec is None:
            # exact match on any of alpha_2 / alpha_3 / name / official_name /
            # common_name, case-insensitive — everything pycountry can answer without
            # guessing. Only what survives this goes to the fuzzy pass.
            try:
                rec = pycountry.countries.lookup(raw)
            except LookupError:
                rec = None
        if rec is None:
            try:
                matches = pycountry.countries.search_fuzzy(raw)
            except LookupError:
                matches = []
            rec = next((m for m in matches if _fuzzy_ok(raw, m)), None)
        if rec is not None:
            return rec.alpha_3

    return None


def name_for(iso3: str) -> str:
    """Best-effort human-readable country name for an ISO3 code."""
    code = str(iso3).upper()
    if code in _USER_ASSIGNED_NAMES:
        return _USER_ASSIGNED_NAMES[code]
    if _HAS_PYCOUNTRY:
        rec = pycountry.countries.get(alpha_3=code)
        if rec is not None:
            return getattr(rec, "common_name", rec.name)
    return code
