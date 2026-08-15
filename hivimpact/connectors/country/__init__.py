"""
Phase 2 — country-level "to source" connectors.

Each connector here goes directly to a country's *national* programme data source
(not the global aggregators), for the feasibility test of whether "to source" is
realistic country by country. They are country-scoped: a connector emits only its own
country's rows, and yields nothing when that country isn't in the requested set.

Rows carry a `reconcile_with` note so the (coming) reconciliation layer cross-checks them
against the aggregator layer (UNAIDS, PEPFAR) instead of trusting them blindly. Most are
tagged `source_type=routine_programme`; South Africa is the exception, because its
national source (Thembisa) is a model rather than a facility reporting system, so its
rows are `modelled_estimate` and should not be compared with programme counts as if they
were the same kind of number.
"""
from .thailand_hivhub import ThailandHIVHubConnector
from .cambodia_nchads import CambodiaNCHADSConnector
from .philippines_doh import PhilippinesDOHConnector
from .south_africa_thembisa import SouthAfricaThembisaConnector

COUNTRY_CONNECTORS = {
    c.source_id: c
    for c in (
        ThailandHIVHubConnector,
        CambodiaNCHADSConnector,
        PhilippinesDOHConnector,
        SouthAfricaThembisaConnector,  # modelled, not routine: see its module docstring
    )
}

__all__ = [
    "ThailandHIVHubConnector", "CambodiaNCHADSConnector", "PhilippinesDOHConnector",
    "SouthAfricaThembisaConnector", "COUNTRY_CONNECTORS",
]
