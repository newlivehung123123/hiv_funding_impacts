"""
The panel schema — the one data model every connector emits into.

Long format: one row per (country, indicator, population_group, sex, age_group, year, source).
This mirrors section 4 of Adrian's indicator document ("one row per
indicator-population-year"), extended with the refinements agreed in design:
  - explicit uncertainty bounds (value_lower / value_upper) — the amfAR report's
    central critique is that HIV outcome metrics carry wide confidence intervals, so
    the panel must carry uncertainty as a first-class field, never a bare point value;
  - a source_type tag so triangulation/reconciliation can be source-type aware;
  - numerator + denominator retained where available, so coverage changes stay
    interpretable after funding cuts;
  - provenance (source_url + retrieved_at) on every row.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional


class SourceType(str, Enum):
    """The five source classes from section 4 of the indicator document.

    Interpreting a country-vs-aggregator discrepancy depends on which of these the
    two figures are — e.g. a routine_programme count diverging from a
    modelled_estimate means something very different from two modelled estimates
    disagreeing. Keep this faithful to the document's taxonomy.
    """

    MODELLED_ESTIMATE = "modelled_estimate"          # Spectrum/EPP, UNAIDS/WHO estimates, WB population
    ROUTINE_PROGRAMME = "routine_programme_record"    # facility/programme reported (e.g. GAM, PEPFAR MER)
    SURVEY = "survey"                                 # PHIA, DHS, biobehavioural surveys
    EXPENDITURE_ACCOUNT = "expenditure_account"       # NASA, OECD CRS, financing modules
    COMMUNITY_LED_MONITORING = "community_led_monitoring"


# Population-group dimension. "all" is the default; the key-population values map to
# Adrian's section 2 (GBMSM / transgender / PWID / sex workers). Extend as needed.
POP_ALL = "all"
POP_GBMSM = "gbmsm"
POP_TRANSGENDER = "transgender"
POP_PWID = "pwid"
POP_SEX_WORKERS = "sex_workers"
KEY_POPULATIONS = (POP_GBMSM, POP_TRANSGENDER, POP_PWID, POP_SEX_WORKERS)

SEX_ALL = "all"
AGE_ALL = "all"


@dataclass(slots=True)
class PanelRow:
    """One observation in the panel. Connectors build these via BaseConnector.make_row."""

    # --- identity / dimensions -------------------------------------------------
    country_iso3: str                       # ISO 3166-1 alpha-3, uppercase
    indicator_id: str                       # canonical id (see config/indicators.py)
    year: int
    value: Optional[float]                  # None == source reported no value (kept, not dropped)

    country_name: str = ""
    admin1: str = ""                        # sub-national unit (province/region); "" = national total
    population_group: str = POP_ALL
    sex: str = SEX_ALL
    age_group: str = AGE_ALL

    # --- value detail ----------------------------------------------------------
    value_lower: Optional[float] = None     # lower confidence bound, if the source gives one
    value_upper: Optional[float] = None     # upper confidence bound
    unit: str = ""                          # "count" | "percent" | "USD" | "per_1000" | ...
    numerator: Optional[float] = None
    denominator: Optional[float] = None

    # --- provenance (non-negotiable) ------------------------------------------
    source_id: str = ""                     # e.g. "unaids_aidsinfo", "who_gho", "world_bank", "oecd_crs"
    source_type: str = SourceType.MODELLED_ESTIMATE.value
    source_url: str = ""                    # the specific URL/endpoint the value came from
    source_indicator_code: str = ""         # the source's own code/label (e.g. WB "SP.POP.TOTL")
    retrieved_at: str = ""                  # ISO date the value was fetched

    # free-form provenance / notes (e.g. donor name for OECD, export file for UNAIDS)
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.country_iso3:
            self.country_iso3 = self.country_iso3.strip().upper()
        if not self.retrieved_at:
            self.retrieved_at = date.today().isoformat()

    def to_dict(self) -> dict:
        d = asdict(self)
        # flatten `extra` into a stable JSON string so the row stays tabular
        import json
        d["extra"] = json.dumps(self.extra, ensure_ascii=False, sort_keys=True) if self.extra else ""
        return d


# Column order for the exported panel (keeps CSV diffs stable across runs).
PANEL_COLUMNS = [
    "country_iso3", "country_name", "admin1", "indicator_id",
    "population_group", "sex", "age_group", "year",
    "value", "value_lower", "value_upper", "unit",
    "numerator", "denominator",
    "source_id", "source_type", "source_url",
    "source_indicator_code", "retrieved_at", "extra",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
