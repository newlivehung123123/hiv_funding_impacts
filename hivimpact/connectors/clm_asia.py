"""
CLM Asia — Community-Led Monitoring connector (Indonesia sentinel; community_led_monitoring).

Source: data.clm-asia.org — the amfAR TREAT Asia / ITPC "Community-Led Monitoring in Asia"
dashboard: a public D3/billboard.js dashboard backed by an UNAUTHENTICATED JSON API
(reverse-engineered 2026-07-19). Community teams survey service users and facilities each
quarter on the AAAQ framework (availability / accessibility / affordability / acceptability /
quality). We take the **Indonesia** slice (SNU1='ID'; the other country covered, India, is
out of SEA scope).

Endpoint (one call per indicator × year × quarter):
  GET https://data.clm-asia.org/api/?component=indicator_data_table&CC=AA&ind=<IND>
      &year=<YYYY>&period=Q<n>&level=FACILITY&case_groups=&snu1=&snu2=
  -> {"chartdata": [ {SNU1, CASEID(=facility), IDCOUNT(=respondents), <option>:count, ...} ]}
     (IDCOUNT equals the sum of the option counts — i.e. the response base for that question.)

For each indicator we pool the Indonesia facilities into a country proportion:
  value(%) = 100 * sum(target_option) / sum(IDCOUNT)   over SNU1='ID' facilities,
with numerator + denominator retained. These are quarterly; we pool across a year's quarters
(sum numerators / sum denominators) into an annual value, recording n_quarters.

IMPORTANT — what this is and isn't:
  * SENTINEL sample — a handful of facilities, mostly around Jakarta — NOT nationally
    representative. A ground-truth service-DISRUPTION signal, tagged
    source_type=community_led_monitoring; NEVER a national cascade. `higher_is` in each row's
    `extra` states whether a rising value is good or bad.
  * The dashboard's facility-count fields (BQ__death_*, BQ__elig_treat_* by key population)
    are DEFINED but UNPOPULATED in the public API (verified empty in every quarter), so they
    are not emitted. If they are populated later, add them as count indicators.
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional

from ..connector_base import BaseConnector
from ..schema import PanelRow, SourceType, POP_ALL

log = logging.getLogger("hivimpact")

_API = "https://data.clm-asia.org/api/"
_SNU = "ID"  # Indonesia (the SEA slice; 'IN' = India, out of scope)

# (canonical_id, source indicator code, target response option, higher_is, label) — VALIDATED
# against the live API 2026-07-19 (option keys confirmed present in the Indonesia data).
_MAP = [
    ("clm_arv_stockout_pct",          "VS__arv_stockout",        "yes", "worse",
     "Left facility without ARV/OI due to stockout, last 3 months"),
    ("clm_treatment_interruption_pct", "VS__stop_arv",           "yes", "worse",
     "Ever stopped antiretroviral treatment"),
    ("clm_out_of_pocket_pct",         "PS__out_of_pocket_pay",   "yes", "worse",
     "Paid out of pocket for medicines/tests, last 6 months"),
    ("clm_facility_open_ontime_pct",  "PS__open_ontime",         "yes", "better",
     "Facility opens and closes on time"),
    ("clm_enough_staff_pct",          "PS__enough_staff",        "yes", "better",
     "Enough staff to meet service-user needs"),
    ("clm_stigma_pct",                "PS__stigma",              "yes", "worse",
     "Faced stigma/discrimination at facility, last 6 months"),
    ("clm_psychosocial_support_pct",  "VS__psychosocial_support", "yes", "better",
     "Psychosocial support available for people living with HIV"),
    ("clm_know_vl_pct",               "PS__know_vl",             "yes", "better",
     "Service user knows their own viral load (VL-testing access proxy)"),
]


class CLMAsiaConnector(BaseConnector):
    source_id = "clm_asia"
    default_source_type = SourceType.COMMUNITY_LED_MONITORING
    description = "CLM Asia (data.clm-asia.org) — Indonesia community-led monitoring (service disruption, sentinel)."
    country = "IDN"
    request_pause = 0.3
    timeout = 45

    def __init__(self, **kw):
        # The API returns a persistent HTTP 500 (not a transient blip) for near-empty early
        # quarters (e.g. 2023-Q1, 2 facilities). Cap retries low so a deterministic 500 costs
        # ~6s of backoff, not ~30s — the quarter is dropped-and-tagged either way.
        kw.setdefault("max_retries", 2)
        super().__init__(**kw)

    def _fetch_quarter(self, ind: str, year: int, quarter: int) -> Optional[List[dict]]:
        params = {
            "component": "indicator_data_table", "CC": "AA", "ind": ind,
            "year": str(year), "period": f"Q{quarter}",
            "case_groups": "", "level": "FACILITY", "snu1": "", "snu2": "",
        }
        try:
            data = self._request("GET", _API, params=params).json()
        except Exception as exc:  # network / non-JSON error page
            log.warning("clm_asia: %s %d-Q%d fetch failed: %s", ind, year, quarter, exc)
            return None
        cd = data.get("chartdata")
        if not cd or not isinstance(cd, list):          # {"chartdata": false} => no data
            return None
        return [r for r in cd if r.get("SNU1") == _SNU]  # Indonesia facilities only

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        if wanted and self.country not in wanted:
            return
        end_year = min(end_year or date.today().year, date.today().year)
        years = range(max(2023, start_year), end_year + 1)   # dashboard starts 2023 Q1

        emitted = 0
        for canonical, ind, opt, higher_is, label in _MAP:
            # year -> [numerator, denominator, {quarters}]
            agg: Dict[int, list] = {}
            for year in years:
                for q in (1, 2, 3, 4):
                    rows = self._fetch_quarter(ind, year, q)
                    if not rows:
                        continue
                    num = sum((r.get(opt) or 0) for r in rows)
                    denom = sum((r.get("IDCOUNT") or 0) for r in rows)
                    if denom <= 0:
                        continue
                    b = agg.setdefault(year, [0, 0, set()])
                    b[0] += num
                    b[1] += denom
                    b[2].add(q)
            n = 0
            for year, (num, denom, quarters) in sorted(agg.items()):
                if denom <= 0:
                    continue
                yield self.make_row(
                    country_iso3="IDN", country_name="Indonesia",
                    indicator_id=canonical, year=year,
                    value=round(100.0 * num / denom, 2), unit="percent",
                    numerator=num, denominator=denom, population_group=POP_ALL,
                    source_url=f"{_API}?component=indicator_data_table&ind={ind}",
                    source_indicator_code=ind,
                    extra={
                        "metric": label,
                        "response_option": opt,
                        "higher_is": higher_is,
                        "quarters_included": sorted(quarters),
                        "n_quarters": len(quarters),
                        "aggregation": "pooled proportion across quarters (sum numerator / sum denominator)",
                        "sample": "CLM sentinel facilities (Jakarta area) — NOT nationally representative",
                        "reconcile_with": "none (community source; complements the aggregator & cascade layers)",
                    },
                )
                n += 1
                emitted += 1
            log.info("clm_asia: %-32s -> %d years (%s)", canonical, n, ind)
        log.info("clm_asia: emitted %d rows (Indonesia CLM sentinel)", emitted)
