"""
Phase 2 — country-level "to source" connectors.

Each connector here goes directly to a country's *national* programme data source
(not the global aggregators), for the feasibility test of whether "to source" is
realistic country by country. They are country-scoped: a connector emits only its own
country's rows, and yields nothing when that country isn't in the requested set.

Rows carry a `reconcile_with` note so the (coming) reconciliation layer cross-checks them
against the aggregator layer (UNAIDS, PEPFAR) instead of trusting them blindly. Most are
tagged `source_type=routine_programme`, with two exceptions. South Africa's national
source (Thembisa) is a model and not a facility reporting system, so South African rows
are `modelled_estimate` and should not be compared with programme counts as if a model
estimate and a programme count were the same kind of number. Cameroon's NASA assessments
are national expenditure accounts, so the `cm_nasa` rows are `expenditure_account` and
carry money in local currency rather than service volumes. Peru's ENDES rows are
`survey`, a weighted share of household respondents with a confidence interval.
"""
from .thailand_hivhub import ThailandHIVHubConnector
from .cambodia_nchads import CambodiaNCHADSConnector
from .philippines_doh import PhilippinesDOHConnector
from .south_africa_thembisa import SouthAfricaThembisaConnector
from .nigeria_ndr import NigeriaNDRConnector
from .cameroon_cnls import CameroonCNLSConnector
from .cameroon_nasa import CameroonNASAConnector
from .niger_annuaire import NigerAnnuaireConnector
from .guinea_annuaire import GuineaAnnuaireConnector
from .chad_annuaire import ChadAnnuaireConnector
from .peru_endes import PeruENDESConnector
from .haiti_mspp import HaitiMSPPConnector
from .bolivia_anuario import BoliviaAnuarioConnector
from .belize_moh import BelizeMOHConnector
from .argentina_snvs import ArgentinaSNVSConnector
from .paraguay_mercosur import ParaguayMercosurConnector
from .nicaragua_mapasalud import NicaraguaMapaSaludConnector
from .png_ndoh_dashboard import PNGNDoHDashboardConnector
from .china_ndcpa import ChinaNDCPAConnector
from .mongolia_hdc import MongoliaHDCConnector
from .sri_lanka_nsacp import SriLankaNSACPConnector
from .georgia_geostat import GeorgiaGeostatConnector
from .belarus_belstat import BelarusBelstatConnector
from .ukraine_npsi import UkraineNPSIConnector
from .kyrgyzstan_aidscenter import KyrgyzstanAidsCenterConnector
from .tajikistan_moh import TajikistanMoHConnector
from .north_korea_mics import NorthKoreaMICSConnector
from .tajikistan_stat import TajikistanStatConnector
from .montenegro_ijzcg import MontenegroIjzcgConnector
from .bangladesh_asp import BangladeshASPConnector
from .maldives_moh import MaldivesMoHConnector
from .india_naco import IndiaNACOConnector
from .armenia_ncid import ArmeniaNCIDConnector
from .kazakhstan_kncdiz import KazakhstanKNCDIZConnector
from .solomon_islands_sinso import SolomonIslandsSINSOConnector
from .bangladesh_sdg import BangladeshSDGConnector
from .fiji_mohms import FijiMOHMSConnector
from .nepal_ncasc import NepalNCASCConnector
from .vanuatu_mics import VanuatuMICSConnector
from .peru_cdc_sala import PeruCDCSalaConnector
from .lebanon_moph import LebanonMoPHBulletinConnector

COUNTRY_CONNECTORS = {
    c.source_id: c
    for c in (
        ThailandHIVHubConnector,
        CambodiaNCHADSConnector,
        PhilippinesDOHConnector,
        SouthAfricaThembisaConnector,  # modelled, not routine: see its module docstring
        NigeriaNDRConnector,           # refuses several published aggregates: see its docstring
        CameroonCNLSConnector,         # parse-only, reads PDFs already cached in data/raw
        CameroonNASAConnector,         # parse-only, and local currency: see its docstring
        NigerAnnuaireConnector,        # parse-only, reads PDFs already cached in data/raw
        GuineaAnnuaireConnector,       # parse-only, reads PDFs already cached in data/raw
        ChadAnnuaireConnector,         # parse-only, reads PDFs already cached in data/raw
        PeruENDESConnector,            # survey, not routine: see its module docstring
        HaitiMSPPConnector,            # downloads four PDFs once, then reads the cached copies
        BoliviaAnuarioConnector,       # downloads one PDF once, then reads the cached copy
        BelizeMOHConnector,            # downloads one PDF once, then reads the cached copy
        ArgentinaSNVSConnector,        # downloads one CSV once, then reads the cached copy
        ParaguayMercosurConnector,     # downloads one PDF once, then reads the cached copy
        NicaraguaMapaSaludConnector,   # 20 Wayback captures, cached after download, national rows only while a SILAIS capture is missing
        PNGNDoHDashboardConnector,     # reads the public Power BI dashboard of the PNG health ministry
        ChinaNDCPAConnector,           # yearly notifiable disease tables, never summed months
        MongoliaHDCConnector,          # downloads five PDFs once, then reads the cached copies
        SriLankaNSACPConnector,        # downloads 17 PDFs once, quarterly returns as a cross-check only
        GeorgiaGeostatConnector,       # reads two tables of the Geostat PxWeb API, no download
        BelarusBelstatConnector,       # reads one table of the Belstat data portal API, no download
        UkraineNPSIConnector,          # reads seven indicators of the PHC monitoring portal API, no download
        KyrgyzstanAidsCenterConnector, # downloads one PDF once, then reads the cached copy
        MontenegroIjzcgConnector,      # downloads one PDF once, then reads the cached copy
        BangladeshASPConnector,        # downloads 10 PDFs once, then reads the cached copies
        MaldivesMoHConnector,          # downloads two PDFs once, then reads the cached copies
        IndiaNACOConnector,            # downloads two PDFs once, then reads the cached copies
        ArmeniaNCIDConnector,          # downloads one Word file once, then reads the cached copy
        KazakhstanKNCDIZConnector,     # survey, not routine: downloads two PDFs once
        SolomonIslandsSINSOConnector,  # survey, not routine: downloads two PDFs once
        BangladeshSDGConnector,        # stores one JSON reply of the SDG Tracker once, then reads the cached copy
        TajikistanMoHConnector,        # downloads four PDFs and one Word file once, then reads the cached copies
        NorthKoreaMICSConnector,       # survey, not routine: downloads one PDF once
        TajikistanStatConnector,       # downloads one PDF once, then reads the cached copy
        FijiMOHMSConnector,            # downloads one workbook and one PDF once, then reads the cached copies
        NepalNCASCConnector,           # downloads six Wayback captures once, then reads the cached copies
        VanuatuMICSConnector,          # survey, not routine: downloads one Wayback capture once
        PeruCDCSalaConnector,          # reads three tables over the websocket of a Shiny application once, then the cached reply
        LebanonMoPHBulletinConnector,  # downloads seven PDFs once, then reads the cached copies
    )
}

__all__ = [
    "ThailandHIVHubConnector", "CambodiaNCHADSConnector", "PhilippinesDOHConnector",
    "SouthAfricaThembisaConnector", "NigeriaNDRConnector", "CameroonCNLSConnector",
    "CameroonNASAConnector", "NigerAnnuaireConnector", "GuineaAnnuaireConnector",
    "ChadAnnuaireConnector", "PeruENDESConnector", "HaitiMSPPConnector", "BoliviaAnuarioConnector",
    "BelizeMOHConnector", "ArgentinaSNVSConnector", "ParaguayMercosurConnector",
    "NicaraguaMapaSaludConnector", "PNGNDoHDashboardConnector", "ChinaNDCPAConnector",
    "MongoliaHDCConnector", "SriLankaNSACPConnector", "GeorgiaGeostatConnector",
    "BelarusBelstatConnector", "UkraineNPSIConnector", "KyrgyzstanAidsCenterConnector",
    "MontenegroIjzcgConnector", "BangladeshASPConnector", "MaldivesMoHConnector",
    "IndiaNACOConnector", "ArmeniaNCIDConnector", "KazakhstanKNCDIZConnector",
    "SolomonIslandsSINSOConnector", "BangladeshSDGConnector", "TajikistanMoHConnector",
    "NorthKoreaMICSConnector", "TajikistanStatConnector", "FijiMOHMSConnector", "NepalNCASCConnector",
    "VanuatuMICSConnector", "PeruCDCSalaConnector", "LebanonMoPHBulletinConnector",
    "COUNTRY_CONNECTORS",
]
