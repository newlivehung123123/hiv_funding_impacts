"""
WHO Global Health Observatory (GHO) OData API connector.

API (confirmed): base https://ghoapi.azureedge.net/api
  - /Indicator                      -> catalogue of {IndicatorCode, IndicatorName}
  - /{IndicatorCode}                -> observations with fields:
        SpatialDimType ('COUNTRY'), SpatialDim (ISO3), TimeDim (year),
        Dim1Type/Dim1 (e.g. SEX), NumericValue, Low, High, Value (display string)

Guessing indicator codes is the exact failure mode that broke GrantGlobe repeatedly,
so this connector does NOT hardcode WHO codes. Instead it resolves each canonical
indicator to a code by matching the *documented indicator name* against the live
catalogue, and logs every resolution so you can lock exact codes afterwards (run
scripts/list_who_hiv_indicators.py to dump the catalogue for review).

Once codes are locked, pass an explicit {canonical: who_code} map to the constructor
for the reliable, unambiguous path.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional

from ..connector_base import BaseConnector
from ..normalize import name_for
from ..schema import PanelRow, SourceType
from ..config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_BASE = "https://ghoapi.azureedge.net/api"

# GHO's own dimension tokens, in the panel's vocabulary. The tokens are not written the
# same way across indicators — the testing series return SEX_BTSX where the codes that
# carry a sex dimension elsewhere return a bare BTSX — so the type prefix is stripped
# before the lookup and both spellings resolve.
_AGE = {
    "YEARSALL": "all",
    "YEARS15PLUS": "15+",
    "YEARSLESS15": "0-14",
}
_SEX = {"MLE": "male", "FMLE": "female", "BTSX": "all"}


def _token(dim: Optional[str], dim_type: str) -> str:
    """Strip GHO's dimension-type prefix, where the value carries one."""
    d = (dim or "").strip()
    prefix = f"{dim_type}_"
    return d[len(prefix):] if d.upper().startswith(prefix) else d


@dataclass(frozen=True)
class GHOSeries:
    """One GHO indicator code and what it means in the panel's vocabulary.

    A canonical indicator can be served by more than one GHO code — reported ART is
    published as an all-ages series and a separate children's series, which are the same
    measurement at two age groups and not two different indicators — so this is a list
    and not a {canonical: code} mapping.
    """
    canonical: str
    code: str
    source_type: Optional[SourceType] = None  # None = take the canonical's default
    age_group: Optional[str] = None           # set where the code is age-restricted by construction
    note: str = ""


# Verified against the live GHO catalogue and, for everything added after the first seven,
# against the returned observations themselves. The catalogue name is not sufficient
# evidence of what a code contains: HIV_0000000020 is named "Estimated number of pregnant
# women living with HIV" and returns 69, 67, 64, 63, 56, 61 for Nigeria, which is PMTCT
# coverage as a percentage — 36,701 of 53,000 women is 69.2 per cent. Loaded on the
# strength of its name it would have entered the panel as a headcount of pregnant women,
# in units of "count", at about a thousandth of the true figure, and no range or outlier
# check would have caught it because 56 to 69 is an unremarkable number. Every code below
# was checked against its own values before being mapped.
GHO_SERIES: List[GHOSeries] = [
    # -- the original seven: UNAIDS/WHO modelled estimates ---------------------
    GHOSeries("plhiv", "HIV_0000000001"),                    # PLHIV, all ages
    GHOSeries("new_infections", "HIV_0000000026"),
    GHOSeries("aids_deaths", "HIV_0000000006"),
    GHOSeries("art_coverage_pct", "HIV_ARTCOVERAGE"),
    GHOSeries("know_status_pct", "HIV_STATUSKNOWNHIV"),      # 1st 95
    GHOSeries("viral_suppression_pct", "HIV_VIRALLOADSUPPRESSEDART"),   # 3rd 95
    GHOSeries("community_viral_suppression_pct", "HIV_VIRALLOADSUPPRESSED"),

    # -- what countries reported, as distinct from what Spectrum modelled -------
    # This is the reason to come back to GHO at all. The seven above are the same
    # Spectrum output UNAIDS publishes, so they agree with AIDSinfo by construction and
    # buy nothing but a checksum. The reported series are a different instrument: a
    # programme counting its own patients. Against the panel's existing on_art_count
    # they are identical in 1 per cent of overlapping country-years, within one per cent
    # in half, and more than a tenth apart in 13 per cent — and they carry 1,636
    # country-years the panel has no ART figure for at all, 155 of them 2023 or later.
    # They also un-censor AIDSinfo: Maldives is "<100" in the UNAIDS export and 2, 3, 5,
    # 6, 8 people here, which confirms from the outside that those censored cells are
    # small true numbers and not missing data.
    GHOSeries("on_art_count", "HIV_0000000009", SourceType.ROUTINE_PROGRAMME, "all",
              "Reported number on ART. 2000-2025, 152 countries."),
    GHOSeries("on_art_count", "HIV_0000000011", SourceType.ROUTINE_PROGRAMME, "0-14",
              "Reported number of children on ART. Paediatric treatment is the thinnest "
              "part of most programmes and the first to be dropped."),
    GHOSeries("art_coverage_pct", "HIV_0000000024", SourceType.MODELLED_ESTIMATE, "0-14",
              "Estimated ART coverage among children."),

    # -- testing throughput, reported, split by sex and age ---------------------
    # 2022-2024 only, but all 24 West and Central African countries in every year.
    GHOSeries("hiv_tests_performed", "HIV_0000000027", SourceType.ROUTINE_PROGRAMME),
    GHOSeries("hiv_test_positivity_pct", "HIV_POSITIVITY", SourceType.ROUTINE_PROGRAMME),

    # -- PMTCT, as its two parts rather than the ratio --------------------------
    # HIV_0000000015 carries the same catalogue name as HIV_0000000016 and returns an
    # empty array; 16 is the live code. The published coverage percentage (HIV_0000000020)
    # is these two divided, so it is derived by construction and is not mapped.
    GHOSeries("pmtct_arv_count", "HIV_0000000016", SourceType.ROUTINE_PROGRAMME, "all"),
    GHOSeries("pregnant_women_hiv", "HIV_0000000021", SourceType.MODELLED_ESTIMATE, "all"),
]

# Kept for callers that want the old shape. Where a canonical is served by several codes
# this holds the first, so it is a convenience and not the connector's source of truth.
DEFAULT_WHO_CODES: Dict[str, str] = {}
for _s in GHO_SERIES:
    DEFAULT_WHO_CODES.setdefault(_s.canonical, _s.code)

# canonical_id -> name substrings to look for in the GHO catalogue (any-match, lowercased).
# Fallback auto-resolution only, for canonicals not in DEFAULT_WHO_CODES.
NAME_HINTS: Dict[str, List[str]] = {
    "plhiv": ["number of people living with hiv"],
    "new_infections": ["number of new hiv infections"],
    "aids_deaths": ["number of aids-related deaths", "number of deaths due to hiv"],
    "art_coverage_pct": ["antiretroviral therapy coverage among people living with hiv",
                          "art coverage"],
    "know_status_pct": ["people living with hiv who know their status",
                        "knowledge of hiv status"],
    "viral_suppression_pct": ["viral suppression", "virally suppressed"],
}


class WHOGHOConnector(BaseConnector):
    source_id = "who_gho"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = "WHO Global Health Observatory (OData) — HIV epidemic & cascade estimates."
    request_pause = 0.2

    def __init__(self, indicator_map: Optional[Dict[str, str]] = None, **kw):
        super().__init__(**kw)
        # Defaults to the verified series list. A {canonical: who_code} dict still works
        # and overrides it; pass {} to force catalogue auto-resolution instead.
        if indicator_map is None:
            self.series = list(GHO_SERIES)
            self.indicator_map = DEFAULT_WHO_CODES
        else:
            self.series = [GHOSeries(c, k) for c, k in indicator_map.items()]
            self.indicator_map = indicator_map

    # -- catalogue --------------------------------------------------------------
    def list_hiv_indicators(self) -> List[dict]:
        url = f"{_BASE}/Indicator?$filter=contains(IndicatorName,'HIV')"
        return self.get_json(url).get("value", [])

    def _resolve_series(self) -> List[GHOSeries]:
        if self.series:
            return self.series
        # Catalogue auto-resolution matches on the indicator's published name, and the
        # name is not reliable evidence of what the code returns (see GHO_SERIES above).
        # Anything resolved this way needs its values read before it is trusted.
        log.warning("who_gho: resolving codes by catalogue name — verify the values before use")
        return [GHOSeries(c, k) for c, k in self._resolve_codes().items()]

    def _resolve_codes(self) -> Dict[str, str]:
        if self.indicator_map:
            return self.indicator_map
        catalogue = self.list_hiv_indicators()
        resolved: Dict[str, str] = {}
        for canonical, hints in NAME_HINTS.items():
            best = None
            for entry in catalogue:
                name = (entry.get("IndicatorName") or "").lower()
                if any(h in name for h in hints):
                    # prefer the shortest name (usually the headline series)
                    if best is None or len(name) < len(best[1]):
                        best = (entry["IndicatorCode"], name)
            if best:
                resolved[canonical] = best[0]
                log.info("who_gho resolved %-22s -> %s (%s)", canonical, best[0], best[1][:60])
            else:
                log.warning("who_gho could NOT resolve %s from catalogue", canonical)
        return resolved

    # -- data -------------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None
        series = self._resolve_series()
        unknown_dims: set = set()

        for s in series:
            spec = CANONICAL_INDICATORS.get(s.canonical)
            unit = spec.unit if spec else ""
            src_type = s.source_type or (spec.default_source_type if spec else self.default_source_type)
            url = f"{_BASE}/{s.code}?$filter=SpatialDimType eq 'COUNTRY'"
            observations = self.get_json(url).get("value", [])
            if not observations:
                # GHO catalogues codes it no longer serves (HIV_0000000015 is one).
                log.warning("who_gho: %s (%s) returned no observations", s.code, s.canonical)
                continue
            n = 0
            for o in observations:
                iso3 = (o.get("SpatialDim") or "").strip().upper()
                if len(iso3) != 3:
                    continue
                if wanted and iso3 not in wanted:
                    continue
                try:
                    year = int(o.get("TimeDim"))
                except (TypeError, ValueError):
                    continue
                if year < start_year or year > end_year:
                    continue
                value = o.get("NumericValue")

                sex, age = "all", s.age_group or "all"
                for dim, dim_type in ((o.get("Dim1"), o.get("Dim1Type")),
                                      (o.get("Dim2"), o.get("Dim2Type"))):
                    dim_type = (dim_type or "").upper()
                    if dim_type == "SEX":
                        tok = _token(dim, "SEX")
                        sex = _SEX.get(tok.upper(), tok or "all")
                        if tok and tok.upper() not in _SEX:
                            unknown_dims.add(f"SEX:{dim}")
                    elif dim_type == "AGEGROUP" and s.age_group is None:
                        # An unrecognised age band keeps its own token. Folding it into
                        # "all" would put two different age groups on one panel key and
                        # let one silently overwrite the other.
                        tok = _token(dim, "AGEGROUP")
                        age = _AGE.get(tok.upper(), tok or "all")
                        if tok and tok.upper() not in _AGE:
                            unknown_dims.add(f"AGEGROUP:{dim}")

                yield self.make_row(
                    country_iso3=iso3,
                    country_name=name_for(iso3),   # GHO returns ISO3 only (SpatialDim)
                    indicator_id=s.canonical,
                    year=year,
                    value=float(value) if value is not None else None,
                    value_lower=_num(o.get("Low")),
                    value_upper=_num(o.get("High")),
                    sex=sex,
                    age_group=age,
                    unit=unit,
                    source_type=src_type.value,
                    source_url=f"{_BASE}/{s.code}",
                    source_indicator_code=s.code,
                )
                n += 1
            log.info("who_gho: %-22s <- %-26s %6d rows (%s)", s.canonical, s.code, n, src_type.value)

        if unknown_dims:
            log.warning("who_gho: unmapped AGEGROUP tokens carried through as-is: %s",
                        ", ".join(sorted(unknown_dims)))


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
