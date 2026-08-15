"""
OECD CRS (Creditor Reporting System) connector — external HIV financing (ODA).

VERIFIED against the live API (2026-07-18):
  endpoint:  https://sdmx.oecd.org/dcd-public/rest   (NB: dcd-public, not public —
             on the generic `public` endpoint CRS is only an external reference and 500s)
  dataflow:  OECD.DCD.FSD , DSD_CRS@DF_CRS , version 1.6
  key:       11 positional dimensions, ALL required (a short key -> HTTP 422):
             DONOR.RECIPIENT.SECTOR.MEASURE.CHANNEL.MODALITY.FLOW_TYPE.PRICE_BASE.MD_DIM.MD_ID.UNIT_MEASURE

We pin every dimension to a single unambiguous value so each query returns exactly one
row per recipient-year — no client-side summing, so no risk of double-counting
grants+loans+ODA-totals or aggregate+project-microdata rows:
  SECTOR       = 13040  (STD control incl. HIV/AIDS)
  MEASURE      = 100    (Official Development Assistance — the ODA total)
  FLOW_TYPE    = D      (Disbursements)
  PRICE_BASE   = V      (Current prices)
  CHANNEL/MODALITY/MD_DIM = _T ; MD_ID = 0   (aggregate, not per-project microdata)
  UNIT_MEASURE = USD
  DONOR        = ALLD   (all official donors) for the total series
               = USA    for the US bilateral series

Values arrive in millions (UNIT_MULT code 6); we rescale to absolute USD.
Cells are "CODE: Label"; we take the code.

RECIPIENTS ARE NOT ALL COUNTRIES
--------------------------------
An all-recipients query returns regional and unallocated aggregates alongside the
countries — "Africa, regional", "Bilateral, unspecified" and so on. Country recipients
are keyed by ISO3, aggregates by mnemonics, and the two are only distinguishable by
whether the code IS an ISO3.

Resolving those codes through the name-matching path (`to_iso3`) got this wrong for a
whole run: pycountry's fuzzy search also matches subdivision names, so aggregate codes
were answered with the country whose district or municipality they happened to spell.
The 2026-08-03 all-country panel therefore showed the United Kingdom as the world's
largest recipient of US HIV aid (59.9bn USD) and North Macedonia as the second
(12.0bn) — regional aggregates, wearing two countries' names. Both were flagged only
because a real GBR/MKD row already existed and the duplicate check caught the
collision; an aggregate that had landed on a country with no CRS row of its own would
have passed validation in silence.

So recipients now resolve through `code_to_iso3`, which accepts an ISO3 country and
nothing else, and every skipped code is counted and logged. If a genuine recipient is
ever coded outside ISO3, the log names it on the next run.
"""
from __future__ import annotations

import io
import logging
from typing import Iterable, Iterator, Optional

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import code_to_iso3, name_for
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_BASE = "https://sdmx.oecd.org/dcd-public/rest"
_FLOWREF = "OECD.DCD.FSD,DSD_CRS@DF_CRS,1.6"
_HIV = "13040"

# canonical_id -> DONOR code. The rest of the key is fixed (see _key).
_SERIES = {
    "external_hiv_oda_total": "ALLD",             # all official donors
    "external_hiv_oda_us": "USA",                 # United States only
    "global_fund_hiv_disbursements": "9OTH012",   # the Global Fund (multilateral donor)
}


def _key(donor: str, recipients: str) -> str:
    # DONOR.RECIPIENT.SECTOR.MEASURE.CHANNEL.MODALITY.FLOW_TYPE.PRICE_BASE.MD_DIM.MD_ID.UNIT_MEASURE
    return f"{donor}.{recipients}.{_HIV}.100._T._T.D.V._T.0.USD"


def _code(cell) -> str:
    """'THA: Thailand' -> 'THA'; '6: Millions' -> '6'."""
    return str(cell).split(":")[0].strip()


class OECDCRSConnector(BaseConnector):
    source_id = "oecd_crs"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = "OECD CRS/DAC — external HIV financing (purpose 13040): total (all donors) + US + Global Fund."
    request_pause = 0.5
    timeout = 120

    def _fetch(self, key: str, start_year: int, end_year: int) -> Optional[pd.DataFrame]:
        url = (f"{_BASE}/data/{_FLOWREF}/{key}"
               f"?startPeriod={start_year}&endPeriod={end_year}")
        try:
            text = self.get_text(url, headers={"Accept": "application/vnd.sdmx.data+csv; labels=both"})
        except Exception as exc:
            log.warning("oecd_crs: request failed for key %s: %s", key, exc)
            return None
        if not text.strip():
            return None
        try:
            return pd.read_csv(io.StringIO(text), dtype=str)
        except Exception as exc:
            log.warning("oecd_crs: could not parse CSV: %s", exc)
            return None

    @staticmethod
    def _col(df: pd.DataFrame, prefix: str) -> Optional[str]:
        return next((c for c in df.columns if c.startswith(prefix)), None)

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = sorted(c.upper() for c in countries) if countries else None
        recipients = "+".join(wanted) if wanted else ""  # empty = all recipients

        for indicator_id, donor in _SERIES.items():
            df = self._fetch(_key(donor, recipients), start_year, end_year)
            if df is None or df.empty:
                log.warning("oecd_crs: no data for %s (donor=%s)", indicator_id, donor)
                continue

            recip_c = self._col(df, "RECIPIENT")
            year_c = self._col(df, "TIME_PERIOD")
            val_c = "OBS_VALUE" if "OBS_VALUE" in df.columns else self._col(df, "OBS_VALUE")
            mult_c = self._col(df, "UNIT_MULT")
            if not (recip_c and year_c and val_c):
                log.warning("oecd_crs: unexpected columns for %s: %s", indicator_id, list(df.columns))
                continue

            n = 0
            skipped: dict[str, int] = {}
            for _, row in df.iterrows():
                code = _code(row[recip_c])
                iso3 = code_to_iso3(code)
                if iso3 is None:
                    skipped[code] = skipped.get(code, 0) + 1
                    continue
                try:
                    year = int(str(row[year_c])[:4])
                    value = float(row[val_c])
                except (TypeError, ValueError):
                    continue
                if year < start_year or year > end_year:
                    continue
                if mult_c and pd.notna(row[mult_c]):
                    try:
                        value *= 10 ** int(_code(row[mult_c]))
                    except (TypeError, ValueError):
                        pass
                yield self.make_row(
                    country_iso3=iso3,
                    country_name=name_for(iso3),   # SDMX keys are ISO3 only
                    indicator_id=indicator_id,
                    year=year,
                    value=value,
                    unit="USD",
                    source_url=f"{_BASE}/data/{_FLOWREF}/{_key(donor, iso3)}",
                    source_indicator_code=f"CRS.{_HIV}.{donor}",
                    extra={"note": "OECD CRS ODA gross disbursements, current USD",
                           "donor": donor},
                )
                n += 1
            log.info("oecd_crs: %s -> %d rows (donor=%s)", indicator_id, n, donor)
            if skipped:
                # Named, not just counted. These are the regional and unallocated
                # aggregates, and the list is also how we would find out that a real
                # recipient had been coded outside ISO3.
                log.info("oecd_crs: %s — %d non-country recipient code(s) skipped: %s",
                         indicator_id, sum(skipped.values()),
                         ", ".join(f"{c}({k})" for c, k in sorted(skipped.items())))
