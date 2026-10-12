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
from .pepfar_agency_snu import PEPFARAgencySNUConnector  # the agency split inside each province
from .pepfar_modality import PEPFARModalityConnector  # testing split community vs facility
from .pepfar_ou_budgets import PEPFAROUBudgetsConnector  # budget from 2004, before the partner file
from .pepfar_commodities import PEPFARCommoditiesConnector  # what PEPFAR planned to buy, COP18-COP24
from .pepfar_hrh import PEPFARHRHConnector  # the staff PEPFAR paid for, FY2025
from .pepfar_vmmc import PEPFARVMMCConnector  # circumcisions 2010-2017, before the partner file
from .clm_asia import CLMAsiaConnector  # community-led monitoring (Indonesia sentinel)
from .global_fund import GlobalFundConnector  # grant-reported annual results, by country and year
from .global_fund_allocations import GlobalFundAllocationsConnector  # what each country may apply for
from .iati import IATIConnector  # transaction-level HIV financing from every IATI publisher
from .country import COUNTRY_CONNECTORS  # Phase 2 country-level "to source" connectors

# NB: the Global Fund enters the panel four times, and the four are different quantities.
# GlobalFundConnector reads the SERVICE results its grants report — people who started
# ART, tests done, people reached — by country and year, from OData v4.2. The MONEY ALREADY
# MOVED reaches the canonical `global_fund_hiv_disbursements` from two places. OECDCRSConnector
# supplies it as a donor series (donor code 9OTH012), annual and about 14 months late, and
# IATIConnector supplies the Global Fund's own transaction-level filing, which names the day
# each disbursement moved and arrives within weeks. Those two are not independent of each
# other: all 1,491 Global Fund activity identifiers in the panel's iati rows match a grant in
# the Global Fund's own grant table, counted on 1 October 2026. The MONEY PROMISED reaches
# `global_fund_hiv_allocation_cycle` from GlobalFundAllocationsConnector, which is a forward
# commitment per three-year cycle and not an annual figure, and which must never be added to
# the disbursement series. Anything summing any of these filters on source_id first.
#
# 15 of the 16 datasets inside AllFinancialIndicators stay unused, and the reason each one is
# refused is written out in global_fund_allocations.DECLARED_DATASETS. On 13 of the 15,
# `recordId` resolves to no table the service publishes, so no row can be attributed to a
# country at all. This note previously said the financial entities were "keyed on grants and
# implementation periods rather than on country-years", which was a guess made before the two
# probes of 30 September and 1 October 2026 asked the service directly.
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
        PEPFARAgencySNUConnector,    # USAID vs CDC inside one province (Partner Performance file)
        PEPFARModalityConnector,     # PEPFAR testing by modality — outreach vs the clinic door
        PEPFAROUBudgetsConnector,    # PEPFAR budget 2004-2020, the years the partner file lacks
        PEPFARCommoditiesConnector,  # PEPFAR commodity procurement plans 2019-2025, pre-freeze
        PEPFARHRHConnector,          # PEPFAR-funded staff, spend and FTE, FY2025 inventory
        PEPFARVMMCConnector,         # PEPFAR circumcisions 2010-2017, the years the partner file lacks
        CLMAsiaConnector,            # community-led monitoring — Indonesia sentinel (API)
        GlobalFundConnector,         # ART initiations and service results, grant-reported (OData v4.2)
        GlobalFundAllocationsConnector,  # what each country may apply for, per three-year cycle
        IATIConnector,               # HIV financing transaction by transaction, 95 publishers (d-portal)
    )
}
# add Phase-2 country connectors (country-scoped: emit only their country's rows)
CONNECTORS.update(COUNTRY_CONNECTORS)

__all__ = [
    "WorldBankConnector", "WHOGHOConnector", "WHOTMEConnector", "UNAIDSAidsinfoConnector",
    "UNAIDSGAMExpenditureConnector", "WHOGHEDConnector", "OECDCRSConnector",
    "DHSConnector", "ForeignAssistanceConnector", "PEPFARPanoramaConnector",
    "PEPFARAgencyConnector", "PEPFARExpenditureConnector", "PEPFARSNUConnector",
    "PEPFARAgencySNUConnector", "PEPFARModalityConnector", "PEPFAROUBudgetsConnector", "PEPFARCommoditiesConnector",
    "PEPFARHRHConnector", "PEPFARVMMCConnector", "CLMAsiaConnector", "GlobalFundConnector",
    "GlobalFundAllocationsConnector", "IATIConnector",
    "COUNTRY_CONNECTORS", "CONNECTORS",
]
