"""
Thailand — HIV Info Hub "Data Mart" connector (national programme cascade).

Source: the DDC/MOPH HIV Info Hub Data Mart, which serves National AIDS Program (NAP,
NHSO) key-performance indicators. Reverse-engineered endpoint (VERIFIED 2026-07-18):

  POST https://hivhub.ddc.moph.go.th/officer/dashboard/get-rdqa.php   (multipart form)
  fields: indicators (1=HIV testing, 2=on-ART cascade, 3=viral suppression, 5=PrEP, ...),
          report=1 (cumulative as of quarter), zones='' (all) / Z01-Z10,
          provinces='' (all) / code, year (Gregorian 2021-2026), quarter=1-4 (4=full year)
  returns: {Keypop, Groupage, Benefit, Total}. Groupage.data = 77 province rows, each
           [province_name, province_code, ...columns]. Columns are laid out in blocks of
           19 per sub-indicator: [Male 8 age-bands + Male total][Female 8 age-bands +
           Female total][Grand total]; grand total sits at offset 18 within each block.

We take the NATIONAL total = sum of a sub-indicator's grand-total column across the 77
provinces. The (canonical -> indicator, block) map below was validated by reconciling
the national totals against the aggregator layer (e.g. on_art_count 2023 = 441,635 vs
UNAIDS 480,000; know-status 524,523 vs UNAIDS 0.92 x 570k). Rows are tagged so the
reconciliation layer cross-checks them, never trusts them blindly.
"""
from __future__ import annotations

import logging
from typing import Iterable, Iterator, List, Optional

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
from ...config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_URL = "https://hivhub.ddc.moph.go.th/officer/dashboard/get-rdqa.php"
_BLOCK = 19          # columns per sub-indicator block
_GRAND = 18          # grand-total offset within a block
_MALE_TOT = 8        # male-total offset (sum of male 8 age bands)
_FEMALE_TOT = 17     # female-total offset
_YEARS = range(2021, 2027)   # per get-year.php

# (canonical_id, indicator_code, block_index, english_label) — VALIDATED by reconciliation
_MAP = [
    ("on_art_count",            2, 1, "Currently on ART"),
    ("know_status_count",       2, 0, "Know HIV status"),
    ("viral_suppression_count", 3, 1, "VL Suppression"),
    ("new_diagnoses",           1, 1, "HIV Positive (tested positive)"),
    ("prep_recipients",         5, 0, "PrEP current"),
]


def _num(x) -> float:
    return float(x) if isinstance(x, (int, float)) else 0.0


class ThailandHIVHubConnector(BaseConnector):
    source_id = "th_hivhub"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "Thailand HIV Info Hub (NAP/NHSO) — national programme cascade (to-source)."
    country = "THA"
    request_pause = 0.3
    timeout = 60

    def _fetch_year(self, indicator: int, year: int) -> Optional[List[list]]:
        resp = self._request("POST", _URL, files={
            "indicators": (None, str(indicator)),
            "report": (None, "1"),
            "zones": (None, ""),
            "provinces": (None, ""),
            "year": (None, str(year)),
            "quarter": (None, "4"),
        })
        try:
            data = resp.json().get("Groupage", {}).get("data") or []
        except ValueError:
            return None
        return data

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None
        if wanted and self.country not in wanted:
            return

        for canonical, indicator, block, label in _MAP:
            spec = CANONICAL_INDICATORS.get(canonical)
            unit = spec.unit if spec else "count"
            grand_i = 2 + block * _BLOCK + _GRAND
            male_i = 2 + block * _BLOCK + _MALE_TOT
            female_i = 2 + block * _BLOCK + _FEMALE_TOT
            n = 0
            for year in _YEARS:
                if year < start_year or year > end_year:
                    continue
                rows = self._fetch_year(indicator, year)
                if not rows:
                    continue
                # integrity: block structure must be intact for this indicator's response
                ncol = len(rows[0]) - 2
                if ncol % _BLOCK != 0 or grand_i >= len(rows[0]):
                    log.warning("th_hivhub: unexpected column layout for indicator %s (%d cols) — skipping %s %d",
                                indicator, ncol, canonical, year)
                    continue
                nat = sum(_num(r[grand_i]) for r in rows)
                male = sum(_num(r[male_i]) for r in rows)
                female = sum(_num(r[female_i]) for r in rows)
                # anti-contamination: grand total must equal male+female (else layout changed)
                if abs(nat - (male + female)) > 1:
                    log.warning("th_hivhub: grand!=male+female for %s %d (%.0f vs %.0f) — skipping",
                                canonical, year, nat, male + female)
                    continue
                if nat <= 0:
                    continue
                yield self.make_row(
                    country_iso3="THA", country_name="Thailand",
                    indicator_id=canonical, year=year, value=nat, unit=unit,
                    source_url=_URL,
                    source_indicator_code=f"hivhub.ind{indicator}.blk{block}",
                    extra={"metric": label, "source": "NAP via HIV Info Hub Data Mart",
                           "reconcile_with": "unaids_aidsinfo, pepfar_panorama",
                           "note": "national programme figure (NAP), quarter=4 cumulative"},
                )
                n += 1
            log.info("th_hivhub: %-24s -> %d years (indicator %s / block %d)", canonical, n, indicator, block)
