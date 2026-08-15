"""
DHS Program (Demographic and Health Surveys) connector.

API (VERIFIED 2026-07-18): https://api.dhsprogram.com/rest/dhs/data
  ?indicatorIds=<id>&f=json&perpage=1000&page=N
  -> {TotalPages, Data:[{CountryName, SurveyYear, Value, IndicatorId, ...}]}

DHS is a SURVEY source (source_type=survey) — an independent, non-modelled measurement
of HIV prevalence, so it triangulates the UNAIDS/WHO modelled estimates. Named by Adrian
in section 4. Note: HIV biomarker coverage in Southeast Asia is thin (e.g. Cambodia
2005), so this is a low-yield source for the SEA pilot but valuable in Phase 3 (Africa).
"""
from __future__ import annotations

import logging
from typing import Dict, Iterable, Iterator, Optional

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_BASE = "https://api.dhsprogram.com/rest/dhs/data"

# DHS indicator id -> (canonical_id, sex). All are survey-measured HIV prevalence (%).
DHS_INDICATORS: Dict[str, tuple] = {
    "HA_HIVP_B_HIV": ("hiv_prevalence_15_49", "all"),
    "HA_HIVP_W_HIV": ("hiv_prevalence_15_49", "female"),
    "HA_HIVP_M_HIV": ("hiv_prevalence_15_49", "male"),
}


class DHSConnector(BaseConnector):
    source_id = "dhs"
    default_source_type = SourceType.SURVEY
    description = "DHS Program — survey-measured HIV prevalence (triangulates modelled estimates)."
    request_pause = 0.3

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        for dhs_id, (canonical, sex) in DHS_INDICATORS.items():
            page = 1
            while True:
                url = f"{_BASE}?indicatorIds={dhs_id}&f=json&perpage=1000&page={page}"
                payload = self.get_json(url)
                data = payload.get("Data", [])
                for r in data:
                    iso3 = to_iso3(r.get("CountryName", ""))
                    if not iso3 or (wanted and iso3 not in wanted):
                        continue
                    try:
                        year = int(r["SurveyYear"])
                        value = float(r["Value"])
                    except (TypeError, ValueError, KeyError):
                        continue
                    if year < start_year or year > end_year:
                        continue
                    yield self.make_row(
                        country_iso3=iso3,
                        country_name=r.get("CountryName", ""),
                        indicator_id=canonical,
                        year=year,
                        value=value,
                        sex=sex,
                        unit="percent",
                        source_url=url,
                        source_indicator_code=dhs_id,
                        extra={"survey": r.get("SurveyType", ""), "dhs_indicator": r.get("Indicator", "")},
                    )
                if page >= int(payload.get("TotalPages", 1) or 1):
                    break
                page += 1
