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
carry money in local currency rather than service volumes.
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
    )
}

__all__ = [
    "ThailandHIVHubConnector", "CambodiaNCHADSConnector", "PhilippinesDOHConnector",
    "SouthAfricaThembisaConnector", "NigeriaNDRConnector", "CameroonCNLSConnector",
    "CameroonNASAConnector", "NigerAnnuaireConnector", "GuineaAnnuaireConnector",
    "ChadAnnuaireConnector",
    "COUNTRY_CONNECTORS",
]
