"""
WHO Global Tuberculosis Programme (TME) connector — the HIV columns of a TB dataset.

Endpoint (confirmed open, no key, no login):
    https://extranet.who.int/tme/generateCSV.asp?ds={dataset}
with datasets `estimates`, `notifications`, `budget`, `expenditure_utilisation` and
`dictionary`. The dictionary is the authority on what every column means and is worth
reading before changing anything here.

Why a TB source is in an HIV panel. Every earlier round of source discovery keyed on
HIV — the word, its translations, DAC purpose code 13040 — so a dataset that carries HIV
as a handful of columns inside a general health collection was invisible to all of them.
TME turned out to hold 100 HIV-related variables across nine datasets, and the most
valuable of them are not TB measurements at all: national TB programmes report the total
number of people on ART and the number who started ART in the last 12 months, because
they need those denominators to work out TB preventive treatment coverage. That is a
reporting channel entirely separate from UNAIDS GAM and from WHO GHO, and it disagrees
with UNAIDS by more than a tenth in 28 per cent of the country-years they share.

The single most useful column is hiv_reg_new2, ART initiations. The panel is otherwise
almost all stocks, and a stock is the wrong instrument for a funding cut: people already
on treatment stay on it for a while after the money stops. Initiations fall in the same
period the testing and outreach stop.

Two things this connector deliberately does not do:

  * The connector does not repair the currency errors. Gabon's 2024 TB/HIV expenditure is
    325,375,873 in a column the dictionary declares to be US dollars, against an other-year
    median of 9,836, and the file has no currency field to check against. A connector
    records what the source said, so a money value in the wrong unit is refused with a
    logged reason and never converted, and writers._unit_outliers finds the money values
    in the wrong unit. Most of the other large jumps in the money columns are not unit errors
    at all but real variation on budgets of a few thousand dollars, which is why the check
    that matters tests for a break in an otherwise stable series and not for a big ratio.

  * It does not join the pre-2015 columns to the post-2015 ones. hivtest, hivtest_pos and
    hiv_reg were retired in 2014 and counted all TB patients; newrel_hivtest and its
    siblings count new and relapse cases only. Mapping both onto one canonical id would
    put a definition change in the middle of every series and read as a jump in 2015.

Refusals. `_REFUSED` lists the published values the connector refuses, with the reason for
every refusal, and the connector logs every refusal. The Lithuanian TB/HIV incidence of
2,800 for 2009 (e_inc_tbhiv_num, bounds 2,000 and 3,600) is refused, because the value
exceeds the UNAIDS estimate of 2,000 people living with HIV in Lithuania for 2009 and would
put 82 per cent of the 3,400 Lithuanian TB cases WHO estimates for 2009 among people with
HIV, against 88 of 3,900 for 2008 and 74 of 3,100 for 2010. Ruling R27 of
research/rulings_2026-10-15.md records the refusal, decided on 16 October 2026.

Ruling R28 of the same file, decided on 16 October 2026, refuses seven money values which
break an otherwise stable series by a factor of more than 20. The four Gabonese money values
for 2024 in the expenditure file look like CFA francs, because the Global Fund TB money
Gabon received in 2024 (731,795,829) is 573 times the 1,277,451 US dollars of Global Fund
TB money Gabon expected for 2024. The Timorese Global Fund TB money received in 2024
(309,530,584) and expected for 2025 (272,525,512) falls inside the range of every other
year of the same series when divided by 100. The Global Fund TB money Vanuatu received in
2019 (10,758,488) is 53 to 120 times every other year of the series above 1,000 US dollars.
"""
from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType
from ..config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_BASE = "https://extranet.who.int/tme/generateCSV.asp?ds="


@dataclass(frozen=True)
class TMEColumn:
    """One TME column and what it means in the panel's vocabulary."""
    canonical: str
    column: str
    dataset: str
    source_type: Optional[SourceType] = None   # None = the canonical's own default
    age_group: str = "all"
    lower: Optional[str] = None                # column holding WHO's low bound
    upper: Optional[str] = None
    fallback: Optional[str] = None             # used only where `column` is missing
    note: str = ""


COLUMNS: List[TMEColumn] = [
    # -- national HIV programme counts, reported to the TB programme -----------
    TMEColumn("on_art_count", "hiv_all", "notifications", SourceType.ROUTINE_PROGRAMME,
              note="Total on ART. 2020-2024, 88 countries, 17 of the 24 in West and Central "
                   "Africa. Against UNAIDS it is within one per cent in 32 per cent of shared "
                   "country-years and more than a tenth out in 28 per cent."),
    TMEColumn("art_initiations", "hiv_reg_new2", "notifications", SourceType.ROUTINE_PROGRAMME,
              fallback="hiv_new",
              note="hiv_new is the same measurement under a second name — the two are identical "
                   "in 94 per cent of the country-years carrying both — and it reaches 39 "
                   "country-years hiv_reg_new2 does not, so it fills gaps and never overrides."),

    # -- the TB/HIV service cascade, all ages and then children ----------------
    TMEColumn("tb_patients_hiv_tested", "newrel_hivtest", "notifications", SourceType.ROUTINE_PROGRAMME),
    TMEColumn("tb_patients_hiv_positive", "newrel_hivpos", "notifications", SourceType.ROUTINE_PROGRAMME),
    TMEColumn("tbhiv_on_art", "newrel_art", "notifications", SourceType.ROUTINE_PROGRAMME),
    TMEColumn("tb_patients_hiv_tested", "newrel_hivtest_014", "notifications",
              SourceType.ROUTINE_PROGRAMME, age_group="0-14"),
    TMEColumn("tb_patients_hiv_positive", "newrel_hivpos_014", "notifications",
              SourceType.ROUTINE_PROGRAMME, age_group="0-14"),
    TMEColumn("tbhiv_on_art", "newrel_art_014", "notifications",
              SourceType.ROUTINE_PROGRAMME, age_group="0-14"),

    # -- modelled TB/HIV burden, with WHO's own bounds -------------------------
    TMEColumn("tbhiv_incidence", "e_inc_tbhiv_num", "estimates", SourceType.MODELLED_ESTIMATE,
              lower="e_inc_tbhiv_num_lo", upper="e_inc_tbhiv_num_hi"),
    TMEColumn("tbhiv_deaths", "e_mort_tbhiv_num", "estimates", SourceType.MODELLED_ESTIMATE,
              lower="e_mort_tbhiv_num_lo", upper="e_mort_tbhiv_num_hi"),

    # -- money. The first two are stated a year ahead, the second two are actuals
    TMEColumn("tbhiv_budget", "budget_tbhiv", "budget", SourceType.EXPENDITURE_ACCOUNT),
    TMEColumn("tbhiv_funding_expected", "cf_tbhiv", "budget", SourceType.EXPENDITURE_ACCOUNT),
    TMEColumn("tbhiv_expenditure", "exp_tbhiv", "expenditure_utilisation", SourceType.EXPENDITURE_ACCOUNT),
    TMEColumn("tbhiv_funding_received", "rcvd_tbhiv", "expenditure_utilisation", SourceType.EXPENDITURE_ACCOUNT),

    # -- the TB programme's funding mix: exposure, not HIV money ---------------
    TMEColumn("tb_funding_expected_usaid", "cf_tot_usaid", "budget", SourceType.EXPENDITURE_ACCOUNT,
              note="Runs to 2025, where the expenditure file stops at 2024. Expected USAID "
                   "funding across all reporting countries falls from 235.5m USD in 2024 to "
                   "98.7m in 2025, and the count of countries expecting anything falls from 31 "
                   "to 23."),
    TMEColumn("tb_funding_expected_gf", "cf_tot_gf", "budget", SourceType.EXPENDITURE_ACCOUNT),
    TMEColumn("tb_funding_expected_domestic", "cf_tot_domestic", "budget", SourceType.EXPENDITURE_ACCOUNT),
    TMEColumn("tb_funding_received_usaid", "rcvd_tot_usaid", "expenditure_utilisation",
              SourceType.EXPENDITURE_ACCOUNT),
    TMEColumn("tb_funding_received_gf", "rcvd_tot_gf", "expenditure_utilisation",
              SourceType.EXPENDITURE_ACCOUNT),
    TMEColumn("tb_funding_received_domestic", "rcvd_tot_domestic", "expenditure_utilisation",
              SourceType.EXPENDITURE_ACCOUNT),
]

DATASET_URL = "https://www.who.int/teams/global-tuberculosis-programme/data"

# Published values refused, keyed by canonical id, ISO3 and year, with the reason logged
# for every refusal (rulings R27 and R28 of research/rulings_2026-10-15.md, 16 October 2026).
_REFUSED: Dict[Tuple[str, str, int], str] = {
    ("tbhiv_incidence", "LTU", 2009): "the Lithuanian TB/HIV incidence of 2,800 for 2009 exceeds "
                                      "the UNAIDS estimate of 2,000 people living with HIV in "
                                      "Lithuania for 2009 and would make 82 per cent of Lithuanian "
                                      "TB cases HIV-positive, against about two per cent in 2008 "
                                      "and 2010",
    ("tbhiv_expenditure", "GAB", 2024): "the Gabonese money values for 2024 in the expenditure file look like CFA francs, because the Global Fund TB money received in 2024 is 573 times the Global Fund TB money expected for 2024 in US dollars",
    ("tbhiv_funding_received", "GAB", 2024): "the Gabonese money values for 2024 in the expenditure file look like CFA francs, because the Global Fund TB money received in 2024 is 573 times the Global Fund TB money expected for 2024 in US dollars",
    ("tb_funding_received_gf", "GAB", 2024): "the Gabonese money values for 2024 in the expenditure file look like CFA francs, because the Global Fund TB money received in 2024 is 573 times the Global Fund TB money expected for 2024 in US dollars",
    ("tb_funding_received_domestic", "GAB", 2024): "the Gabonese money values for 2024 in the expenditure file look like CFA francs, because the Global Fund TB money received in 2024 is 573 times the Global Fund TB money expected for 2024 in US dollars",
    ("tb_funding_received_gf", "TLS", 2024): "the Timorese Global Fund TB money of 2024 falls inside the range of every other year of the series when divided by 100, and Timor-Leste uses the US dollar",
    ("tb_funding_expected_gf", "TLS", 2025): "the Timorese Global Fund TB money of 2025 falls inside the range of every other year of the series when divided by 100, and Timor-Leste uses the US dollar",
    ("tb_funding_received_gf", "VUT", 2019): "the Global Fund TB money Vanuatu received in 2019 is 53 to 120 times every other year of the series above 1,000 US dollars",
}


class WHOTMEConnector(BaseConnector):
    source_id = "who_tme"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "WHO Global TB Programme (TME) — the HIV columns: ART totals and initiations, the TB/HIV cascade, TB/HIV money."
    request_pause = 0.5
    timeout = 240

    def __init__(self, columns: Optional[List[TMEColumn]] = None, **kw):
        super().__init__(**kw)
        self.columns = list(COLUMNS if columns is None else columns)
        self._cache: Dict[str, pd.DataFrame] = {}

    # -- data ------------------------------------------------------------------
    def load(self, dataset: str) -> pd.DataFrame:
        """One TME dataset as a frame, fetched once per run."""
        if dataset not in self._cache:
            text = self.get_text(f"{_BASE}{dataset}")
            df = pd.read_csv(io.StringIO(text), low_memory=False)
            df.columns = [str(c).strip() for c in df.columns]
            self._cache[dataset] = df
            log.info("who_tme: %s -> %d rows x %d cols", dataset, len(df), df.shape[1])
        return self._cache[dataset]

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        for spec in self.columns:
            try:
                df = self.load(spec.dataset)
            except Exception as exc:
                log.warning("who_tme: could not load %s: %s", spec.dataset, exc)
                continue
            if spec.column not in df.columns:
                log.warning("who_tme: %s absent from %s — the source's columns have moved",
                            spec.column, spec.dataset)
                continue

            canonical = CANONICAL_INDICATORS.get(spec.canonical)
            unit = canonical.unit if canonical else ""
            src_type = spec.source_type or (
                canonical.default_source_type if canonical else self.default_source_type)
            url = f"{_BASE}{spec.dataset}"

            n = filled = 0
            for _, row in df.iterrows():
                iso3 = str(row.get("iso3") or "").strip().upper()
                if len(iso3) != 3:
                    iso3 = to_iso3(row.get("country")) or ""
                if len(iso3) != 3 or (wanted and iso3 not in wanted):
                    continue
                try:
                    year = int(row["year"])
                except (TypeError, ValueError, KeyError):
                    continue
                if year < start_year or year > end_year:
                    continue

                value, came_from = _num(row.get(spec.column)), spec.column
                if value is None and spec.fallback and spec.fallback in df.columns:
                    value, came_from = _num(row.get(spec.fallback)), spec.fallback
                    if value is not None:
                        filled += 1
                if value is None:
                    continue
                reason = _REFUSED.get((spec.canonical, iso3, year))
                if reason:
                    log.info("who_tme: %s %s %d refused, %s", spec.canonical, iso3, year, reason)
                    continue

                yield self.make_row(
                    country_iso3=iso3,
                    country_name=str(row.get("country") or ""),
                    indicator_id=spec.canonical,
                    year=year,
                    value=value,
                    value_lower=_num(row.get(spec.lower)) if spec.lower else None,
                    value_upper=_num(row.get(spec.upper)) if spec.upper else None,
                    age_group=spec.age_group,
                    unit=unit,
                    source_type=src_type.value,
                    source_url=url,
                    source_indicator_code=came_from,
                    extra={"dataset": spec.dataset},
                )
                n += 1
            log.info("who_tme: %-28s <- %-20s [%s] %5d rows%s",
                     spec.canonical, spec.column, spec.dataset, n,
                     f" ({filled} from {spec.fallback})" if filled else "")


def _num(x) -> Optional[float]:
    """A number, or None. Blanks and WHO's own missing markers both mean absent."""
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
        pass
    s = str(x).strip().replace(",", "")
    if s in ("", "-", "NA", "N/A", "nan", "NaN", "..."):
        return None
    try:
        return float(s)
    except ValueError:
        return None
