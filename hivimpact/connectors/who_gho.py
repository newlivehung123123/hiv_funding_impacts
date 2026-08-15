"""
WHO Global Health Observatory (GHO) OData API connector.

API (confirmed): base https://ghoapi.azureedge.net/api
  - /Indicator                      -> catalogue of {IndicatorCode, IndicatorName}
  - /{IndicatorCode}                -> observations with fields:
        SpatialDimType ('COUNTRY'), SpatialDim (ISO3), TimeDim (year),
        Dim1Type/Dim1 (e.g. SEX), NumericValue, Low, High, Value (display string)

Guessing indicator codes is the exact failure mode that broke GrantGlobe repeatedly,
so this connector does NOT hardcode WHO codes. Instead it resolves each canonical
indicator to a code by matching the *documented indicator name* against the live
catalogue, and logs every resolution so you can lock exact codes afterwards (run
scripts/list_who_hiv_indicators.py to dump the catalogue for review).

Once codes are locked, pass an explicit {canonical: who_code} map to the constructor
for the reliable, unambiguous path.
"""
from __future__ import annotations

import logging
from typing import Dict, Iterable, Iterator, List, Optional

from ..connector_base import BaseConnector
from ..normalize import name_for
from ..schema import PanelRow, SourceType
from ..config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_BASE = "https://ghoapi.azureedge.net/api"

# Verified against the live GHO catalogue (docs/who_hiv_indicators.csv, 2026-07-18).
# This explicit map is the reliable path; NAME_HINTS below is only a fallback for codes
# not listed here.
DEFAULT_WHO_CODES: Dict[str, str] = {
    "plhiv": "HIV_0000000001",              # Estimated number of people (all ages) living with HIV
    "new_infections": "HIV_0000000026",     # Number of new HIV infections
    "aids_deaths": "HIV_0000000006",        # Number of people dying from HIV-related causes
    "art_coverage_pct": "HIV_ARTCOVERAGE",  # Estimated ART coverage among PLHIV (%)
    "know_status_pct": "HIV_STATUSKNOWNHIV", # % of PLHIV who know their HIV status (1st 95)
    "viral_suppression_pct": "HIV_VIRALLOADSUPPRESSEDART",   # % on ART virally suppressed (3rd 95)
    "community_viral_suppression_pct": "HIV_VIRALLOADSUPPRESSED",  # % of ALL PLHIV suppressed
}

# canonical_id -> name substrings to look for in the GHO catalogue (any-match, lowercased).
# Fallback auto-resolution only, for canonicals not in DEFAULT_WHO_CODES.
NAME_HINTS: Dict[str, List[str]] = {
    "plhiv": ["number of people living with hiv"],
    "new_infections": ["number of new hiv infections"],
    "aids_deaths": ["number of aids-related deaths", "number of deaths due to hiv"],
    "art_coverage_pct": ["antiretroviral therapy coverage among people living with hiv",
                          "art coverage"],
    "know_status_pct": ["people living with hiv who know their status",
                        "knowledge of hiv status"],
    "viral_suppression_pct": ["viral suppression", "virally suppressed"],
}


class WHOGHOConnector(BaseConnector):
    source_id = "who_gho"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = "WHO Global Health Observatory (OData) — HIV epidemic & cascade estimates."
    request_pause = 0.2

    def __init__(self, indicator_map: Optional[Dict[str, str]] = None, **kw):
        super().__init__(**kw)
        # explicit {canonical: who_code}; defaults to the verified map. Pass {} to force
        # catalogue auto-resolution instead.
        self.indicator_map = DEFAULT_WHO_CODES if indicator_map is None else indicator_map

    # -- catalogue --------------------------------------------------------------
    def list_hiv_indicators(self) -> List[dict]:
        url = f"{_BASE}/Indicator?$filter=contains(IndicatorName,'HIV')"
        return self.get_json(url).get("value", [])

    def _resolve_codes(self) -> Dict[str, str]:
        if self.indicator_map:
            return self.indicator_map
        catalogue = self.list_hiv_indicators()
        resolved: Dict[str, str] = {}
        for canonical, hints in NAME_HINTS.items():
            best = None
            for entry in catalogue:
                name = (entry.get("IndicatorName") or "").lower()
                if any(h in name for h in hints):
                    # prefer the shortest name (usually the headline series)
                    if best is None or len(name) < len(best[1]):
                        best = (entry["IndicatorCode"], name)
            if best:
                resolved[canonical] = best[0]
                log.info("who_gho resolved %-22s -> %s (%s)", canonical, best[0], best[1][:60])
            else:
                log.warning("who_gho could NOT resolve %s from catalogue", canonical)
        return resolved

    # -- data -------------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None
        codes = self._resolve_codes()

        for canonical, who_code in codes.items():
            spec = CANONICAL_INDICATORS.get(canonical)
            unit = spec.unit if spec else ""
            url = f"{_BASE}/{who_code}?$filter=SpatialDimType eq 'COUNTRY'"
            observations = self.get_json(url).get("value", [])
            for o in observations:
                iso3 = (o.get("SpatialDim") or "").strip().upper()
                if len(iso3) != 3:
                    continue
                if wanted and iso3 not in wanted:
                    continue
                try:
                    year = int(o.get("TimeDim"))
                except (TypeError, ValueError):
                    continue
                if year < start_year or year > end_year:
                    continue
                value = o.get("NumericValue")
                sex = "all"
                if (o.get("Dim1Type") or "").upper() == "SEX":
                    sex = {"MLE": "male", "FMLE": "female", "BTSX": "all"}.get(o.get("Dim1"), o.get("Dim1") or "all")
                yield self.make_row(
                    country_iso3=iso3,
                    country_name=name_for(iso3),   # GHO returns ISO3 only (SpatialDim)
                    indicator_id=canonical,
                    year=year,
                    value=float(value) if value is not None else None,
                    value_lower=_num(o.get("Low")),
                    value_upper=_num(o.get("High")),
                    sex=sex,
                    unit=unit,
                    source_url=f"{_BASE}/{who_code}",
                    source_indicator_code=who_code,
                )


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
