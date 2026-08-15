"""
World Bank Indicators API connector.

Primary role: **denominators** (total population) needed to interpret coverage and
incidence. Also pulls HIV prevalence (15-49) as a convenience series — but note WB's
HIV data is itself UNAIDS-derived, so it is a *triangulation duplicate*, not an
independent source; it is tagged accordingly and should never be treated as a check
on UNAIDS.

API (confirmed): https://api.worldbank.org/v2/country/{iso3;iso3}/indicator/{code}
                 ?date=START:END&format=json&per_page=N   -> [meta, [rows]]
Only World Bank indicator codes we are confident about are wired in here.
"""
from __future__ import annotations

import logging
from typing import Iterable, Iterator, Optional

from ..connector_base import BaseConnector
from ..normalize import code_to_iso3
from ..schema import PanelRow, SourceType
from ..config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

# canonical_id -> World Bank indicator code  (only confident codes)
WB_CODES = {
    "population_total": "SP.POP.TOTL",
    "hiv_prevalence_15_49": "SH.DYN.AIDS.ZS",
}

_BASE = "https://api.worldbank.org/v2"


class WorldBankConnector(BaseConnector):
    source_id = "world_bank"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = "World Bank Indicators API — population denominators + HIV prevalence (UNAIDS-derived)."
    request_pause = 0.1
    # An all-country page is ~200 countries x 26 years and the API regularly takes over a
    # minute to build one. On 60s the 2026-08-03 global run timed out four times on the same
    # page and lost the whole source.
    timeout = 180

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        country_path = ";".join(c.lower() for c in countries) if countries else "all"
        wanted = set(c.upper() for c in countries) if countries else None

        for canonical, wb_code in WB_CODES.items():
            spec = CANONICAL_INDICATORS.get(canonical)
            unit = spec.unit if spec else ""
            page = 1
            emitted = 0
            skipped: dict[str, int] = {}
            while True:
                url = (f"{_BASE}/country/{country_path}/indicator/{wb_code}"
                       f"?date={start_year}:{end_year}&format=json&per_page=1000&page={page}")
                try:
                    payload = self.get_json(url)
                except Exception as exc:
                    # One page timing out used to raise, which failed the connector and took
                    # every row of every indicator with it — an outage on page 3 of 6 cost the
                    # panel all 11,129 World Bank rows, including the population denominators
                    # the coverage indicators are read against. Keep what came back and say
                    # loudly that the series is short; a missing country is visible, a missing
                    # source is not.
                    log.error("world_bank: %s (%s) page %d failed after %d attempts: %s — "
                              "SERIES INCOMPLETE for this run (%d rows kept from pages 1-%d). "
                              "Re-run `--sources world_bank` before using the denominators.",
                              canonical, wb_code, page, self.max_retries, exc, emitted, page - 1)
                    break
                if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
                    log.warning("world_bank: no data for %s (%s)", canonical, wb_code)
                    break
                meta, rows = payload[0], payload[1]
                for r in rows:
                    # World Bank aggregates carry three-letter alphabetic codes of their own
                    # — WLD is the world, SSA is Sub-Saharan Africa, LDC the least-developed
                    # countries — so a check on the SHAPE of the code lets every one of them
                    # in as a country. The 2026-08-03 all-country run put 44 of them in the
                    # panel, the world's own population among them. Only an ISO3 country
                    # passes now.
                    iso3 = code_to_iso3(r.get("countryiso3code"))
                    if iso3 is None:
                        code = (r.get("countryiso3code") or "").strip().upper()
                        if code:
                            skipped[code] = skipped.get(code, 0) + 1
                        continue
                    if wanted and iso3 not in wanted:
                        continue
                    if r.get("value") is None:
                        continue
                    try:
                        year = int(r["date"])
                        value = float(r["value"])
                    except (TypeError, ValueError):
                        continue
                    yield self.make_row(
                        country_iso3=iso3,
                        country_name=(r.get("country") or {}).get("value", ""),
                        indicator_id=canonical,
                        year=year,
                        value=value,
                        unit=unit,
                        source_type=(spec.default_source_type.value if spec
                                     else self.default_source_type.value),
                        source_url=url,
                        source_indicator_code=wb_code,
                        extra={"wb_note": "HIV series are UNAIDS-derived"} if canonical.startswith("hiv_") else {},
                    )
                    emitted += 1
                if page >= int(meta.get("pages", 1)):
                    break
                page += 1
            if skipped:
                # Named, not just counted, for the same reason as in oecd_crs: this list is
                # where a real country coded outside ISO3 would show itself.
                log.info("world_bank: %s — %d non-country code(s) skipped: %s",
                         canonical, sum(skipped.values()),
                         ", ".join(f"{c}({k})" for c, k in sorted(skipped.items())))
