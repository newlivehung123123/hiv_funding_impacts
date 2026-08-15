"""Aggregator connectors (Phase 1)."""
from .world_bank import WorldBankConnector
from .who_gho import WHOGHOConnector
from .unaids_aidsinfo import UNAIDSAidsinfoConnector
from .oecd_crs import OECDCRSConnector
from .dhs import DHSConnector
from .foreign_assistance import ForeignAssistanceConnector
from .pepfar_panorama import PEPFARPanoramaConnector
from .pepfar_agency import PEPFARAgencyConnector  # the same MER file, split by funding agency
from .pepfar_expenditure import PEPFARExpenditureConnector  # budget vs spend, split the same way
from .pepfar_snu import PEPFARSNUConnector  # the same programme, at admin1 (province/county/state)
from .clm_asia import CLMAsiaConnector  # community-led monitoring (Indonesia sentinel)
from .country import COUNTRY_CONNECTORS  # Phase 2 country-level "to source" connectors

# NB: the Global Fund is NOT a standalone connector — it has no programmatic
# disbursements-by-country feed (its site offers only per-country manual profiles, and
# its OData FinancialIndicators entity 500s on filtered queries). Instead the Global Fund
# is pulled as a DONOR series inside OECDCRSConnector (donor code 9OTH012) -> the
# canonical `global_fund_hiv_disbursements`. Same reliable SDMX API, same units.

# registry: source_id -> connector class
CONNECTORS = {
    c.source_id: c
    for c in (
        WorldBankConnector,       # denominators + prevalence (API)
        WHOGHOConnector,          # HIV epi + cascade estimates (API)
        UNAIDSAidsinfoConnector,  # UNAIDS modules (CSV export ingest)
        OECDCRSConnector,         # external HIV financing: total + US + Global Fund (SDMX API)
        DHSConnector,             # survey HIV prevalence (API)
        ForeignAssistanceConnector,  # US self-reported HIV disbursements (CSV ingest)
        PEPFARPanoramaConnector,     # PEPFAR MER programme data (MER dataset ingest)
        PEPFARAgencyConnector,       # the same MER rows split USAID / CDC / other (no new download)
        PEPFARExpenditureConnector,  # PEPFAR budget vs spend by agency (no new download)
        PEPFARSNUConnector,          # PEPFAR MER at SNU1 — the admin1 layer no aggregator has
        CLMAsiaConnector,            # community-led monitoring — Indonesia sentinel (API)
    )
}
# add Phase-2 country connectors (country-scoped: emit only their country's rows)
CONNECTORS.update(COUNTRY_CONNECTORS)

__all__ = [
    "WorldBankConnector", "WHOGHOConnector", "UNAIDSAidsinfoConnector", "OECDCRSConnector",
    "DHSConnector", "ForeignAssistanceConnector", "PEPFARPanoramaConnector",
    "PEPFARAgencyConnector", "PEPFARExpenditureConnector", "PEPFARSNUConnector",
    "CLMAsiaConnector",
    "COUNTRY_CONNECTORS", "CONNECTORS",
]
