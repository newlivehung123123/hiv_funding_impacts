"""Aggregator connectors (Phase 1)."""
from .world_bank import WorldBankConnector
from .who_gho import WHOGHOConnector
from .who_tme import WHOTMEConnector  # the HIV columns of WHO's TB dataset
from .unaids_aidsinfo import UNAIDSAidsinfoConnector
from .unaids_gam_expenditure import UNAIDSGAMExpenditureConnector  # who paid, and for what
from .who_ghed import WHOGHEDConnector  # the same money as the national health accounts see it
from .oecd_crs import OECDCRSConnector
from .dhs import DHSConnector
from .foreign_assistance import ForeignAssistanceConnector
from .pepfar_panorama import PEPFARPanoramaConnector
from .pepfar_agency import PEPFARAgencyConnector  # the same MER file, split by funding agency
from .pepfar_expenditure import PEPFARExpenditureConnector  # budget vs spend, split the same way
from .pepfar_snu import PEPFARSNUConnector  # the same programme, at admin1 (province/county/state)
from .pepfar_modality import PEPFARModalityConnector  # testing split community vs facility
from .pepfar_ou_budgets import PEPFAROUBudgetsConnector  # budget from 2004, before the partner file
from .pepfar_commodities import PEPFARCommoditiesConnector  # what PEPFAR planned to buy, COP18-COP24
from .pepfar_hrh import PEPFARHRHConnector  # the staff PEPFAR paid for, FY2025
from .clm_asia import CLMAsiaConnector  # community-led monitoring (Indonesia sentinel)
from .global_fund import GlobalFundConnector  # grant-reported annual results, by country and year
from .country import COUNTRY_CONNECTORS  # Phase 2 country-level "to source" connectors

# NB: the Global Fund enters the panel twice, and the two are different quantities.
# GlobalFundConnector reads the SERVICE results its grants report — people who started
# ART, tests done, people reached — by country and year, from OData v4.2. The MONEY still
# comes from OECDCRSConnector as a donor series (donor code 9OTH012) -> the canonical
# `global_fund_hiv_disbursements`, because the Data Service's financial entities are keyed
# on grants and implementation periods rather than on country-years.
#
# This note previously said the Global Fund had no country-level feed at all. That was
# written against API versions 2 and 3.3, which are now retired and answer every request
# with a 403 block page, including the bare root — a retired version and a closed door
# look identical from outside. Version 4.2 serves the results used here.

# registry: source_id -> connector class
CONNECTORS = {
    c.source_id: c
    for c in (
        WorldBankConnector,       # denominators + prevalence (API)
        WHOGHOConnector,          # HIV epi + cascade estimates (API)
        WHOTMEConnector,          # ART totals and initiations, TB/HIV cascade and money (CSV API)
        UNAIDSAidsinfoConnector,  # UNAIDS modules (CSV export ingest)
        UNAIDSGAMExpenditureConnector,  # country-reported HIV expenditure by source and programme
        WHOGHEDConnector,         # HIV and STD spending from the national health accounts (workbook)
        OECDCRSConnector,         # external HIV financing: total + US + Global Fund (SDMX API)
        DHSConnector,             # survey HIV prevalence (API)
        ForeignAssistanceConnector,  # US self-reported HIV disbursements (CSV ingest)
        PEPFARPanoramaConnector,     # PEPFAR MER programme data (MER dataset ingest)
        PEPFARAgencyConnector,       # the same MER rows split USAID / CDC / other (no new download)
        PEPFARExpenditureConnector,  # PEPFAR budget vs spend by agency (no new download)
        PEPFARSNUConnector,          # PEPFAR MER at SNU1 — the admin1 layer no aggregator has
        PEPFARModalityConnector,     # PEPFAR testing by modality — outreach vs the clinic door
        PEPFAROUBudgetsConnector,    # PEPFAR budget 2004-2020, the years the partner file lacks
        PEPFARCommoditiesConnector,  # PEPFAR commodity procurement plans 2019-2025, pre-freeze
        PEPFARHRHConnector,          # PEPFAR-funded staff, spend and FTE, FY2025 inventory
        CLMAsiaConnector,            # community-led monitoring — Indonesia sentinel (API)
        GlobalFundConnector,         # ART initiations and service results, grant-reported (OData v4.2)
    )
}
# add Phase-2 country connectors (country-scoped: emit only their country's rows)
CONNECTORS.update(COUNTRY_CONNECTORS)

__all__ = [
    "WorldBankConnector", "WHOGHOConnector", "WHOTMEConnector", "UNAIDSAidsinfoConnector",
    "UNAIDSGAMExpenditureConnector", "WHOGHEDConnector", "OECDCRSConnector",
    "DHSConnector", "ForeignAssistanceConnector", "PEPFARPanoramaConnector",
    "PEPFARAgencyConnector", "PEPFARExpenditureConnector", "PEPFARSNUConnector",
    "PEPFARModalityConnector", "PEPFAROUBudgetsConnector", "PEPFARCommoditiesConnector",
    "PEPFARHRHConnector", "CLMAsiaConnector", "GlobalFundConnector",
    "COUNTRY_CONNECTORS", "CONNECTORS",
]
