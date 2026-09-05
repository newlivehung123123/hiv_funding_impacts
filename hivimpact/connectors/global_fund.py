"""
Global Fund Data Service connector — grant-reported annual results, by country and year.

Endpoint (open, no key, no login):
    https://fetch.theglobalfund.org/v4.2/odata/AllProgrammaticIndicators
    https://fetch.theglobalfund.org/v4.2/odata/Geographies

The service moved twice and the old paths do not say so. data-service.theglobalfund.org
301s to fetch.theglobalfund.org, and every retired version under that host answers with an
Azure Front Door page reading "The request is blocked." on an HTTP 403 — including the
bare root. Version 2 and version 3.3 are both retired, so a connector written against the
paths the earlier documentation gives returns a block page, and reads as a source that has
closed its door to us rather than a version that no longer exists. The live versions are
listed at data-service.theglobalfund.org/api, and 4.2 is the current one.

What is here that is not elsewhere. The Global Fund reports "People newly diagnosed with
HIV initiated on ART" for 40 countries over 2017 to 2024, from its own grant reporting.
That is a count of people who started treatment in a year, which is what falls when the
money stops, and it arrives through a channel that has nothing to do with the UNAIDS
estimate that WHO and the World Bank republish. The panel's other initiation series comes
from WHO's tuberculosis programme, so this is a second independent reading of the same
quantity for the countries the two share.

Three traps, all of which would enter the panel silently.

  * `$expand` empties the result. Asking for `$expand=geography` on
    AllProgrammaticIndicators returns HTTP 200 with an empty value array rather than an
    error, so a connector that joins through the navigation property looks like a source
    with no data in it. The join is done here on `recordId` instead, which for the
    Annual_Results dataset is a Geography id.

  * A national-looking row that is one grant's slice. 21 of the 114 ART-initiation rows
    are marked Subnational, and they carry a country-level geography exactly like the
    national ones. South Africa's 2022 subnational row is 1,531 people, against a national
    figure in the hundreds of thousands. Nothing in the country code, the year or the value
    marks it as partial, and no range check would catch it because 1,531 is a perfectly
    ordinary number for a small country. `geographicCoverage` is the only field that
    separates the two, so only National rows are emitted and the rest are counted and named
    in the log.

  * Sixty-three of the 300 geographies are Multicountry, and a regional grant's results
    would land on whichever country the code resolved to. Only geographies the service
    itself grades as Country are accepted.

Annual_Results is not an HIV dataset. It is 15,313 rows covering every indicator the
institution's grants report, so malaria, drug-resistant TB and the cross-cutting
health-systems lines arrive in the same response and are named in _UNMAPPED_OTHER_DISEASE
rather than skipped silently. The whole dataset arrives at once with no nextLink, so there
is no paging to get wrong.

Measured on the run of 2026-09-05: 4,797 rows emitted over nine canonical indicators, 2,034
subnational rows left out and 80 rows whose geography is not a country. The count of
reporting countries in `new_diagnoses` falls from 22 in 2023 to eight in 2024, which is
grant reporting arriving late rather than diagnoses collapsing, so every Global Fund series
has to be read on the countries reporting both years. `writers._reporter_drops` says so in
the validation log.

One row in that run is a different quantity from its own series. Ethiopia's 2017 testing
figure is 7,919,182 against roughly 300,000 in every other year from 2018 to 2024, a 27-fold
break of the kind §8c of ACCESS_LADDER describes. It is emitted as published, because a
connector records what the source said and validation says what it means, and
`writers._unit_outliers` names it.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, Optional, Tuple

from ..connector_base import BaseConnector
from ..schema import (
    PanelRow, SourceType, POP_ALL, POP_GBMSM, POP_PWID, POP_SEX_WORKERS, POP_TRANSGENDER,
)
from ..config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_BASE = "https://fetch.theglobalfund.org/v4.2/odata"
_DATASET = "Annual_Results"


@dataclass(frozen=True)
class GFSeries:
    """One Global Fund indicator name and what it means in the panel's vocabulary."""

    canonical: str
    population_group: str = POP_ALL
    source_type: Optional[SourceType] = None


# The Global Fund's own indicator names, verbatim, as the key. A name that is not here is
# counted and logged rather than guessed at, so a renamed indicator shows up as a source
# the panel stopped reading and not as a series that quietly ended.
_SERIES: Dict[str, GFSeries] = {
    # -- the treatment cascade -------------------------------------------------
    "People newly diagnosed with HIV initiated on ART": GFSeries("art_initiations"),
    "People on antiretroviral therapy for HIV": GFSeries("on_art_count"),
    "Total number of HIV tests": GFSeries("hiv_tests_performed"),
    "Number of HIV positive tests": GFSeries("new_diagnoses"),
    "HIV-positive pregnant women who received ART during pregnancy": GFSeries("pmtct_arv_count"),
    "People using pre-exposure prophylaxis": GFSeries("prep_recipients"),

    # -- key populations, where the panel has a population dimension for them ---
    "Men who have sex with men reached with HIV prevention programs": GFSeries("kp_reached", POP_GBMSM),
    "Sex workers reached with HIV prevention programs": GFSeries("kp_reached", POP_SEX_WORKERS),
    "People who use drugs reached with HIV prevention programs": GFSeries("kp_reached", POP_PWID),
    "Transgender people reached with HIV prevention programs": GFSeries("kp_reached", POP_TRANSGENDER),
    "Number of HIV tests among men who have sex with men": GFSeries("kp_tested", POP_GBMSM),
    "Number of HIV tests among sex workers": GFSeries("kp_tested", POP_SEX_WORKERS),
    "Number of HIV tests among drug users": GFSeries("kp_tested", POP_PWID),
    "Number of HIV tests among transgender population": GFSeries("kp_tested", POP_TRANSGENDER),
    "Men who have sex with men who received antiretroviral pre-exposure prophylaxis":
        GFSeries("prep_recipients", POP_GBMSM),
    "Sex workers who received antiretroviral pre-exposure prophylaxis":
        GFSeries("prep_recipients", POP_SEX_WORKERS),
    "People who use drugs received antiretroviral pre-exposure prophylaxis":
        GFSeries("prep_recipients", POP_PWID),
    "Transgender people who received antiretroviral pre-exposure prophylaxis":
        GFSeries("prep_recipients", POP_TRANSGENDER),

    # -- the TB/HIV component --------------------------------------------------
    "TB Patients with documented HIV status": GFSeries("tb_patients_hiv_tested"),
    "HIV-positive TB patients on ART during TB treatment": GFSeries("tbhiv_on_art"),
    "HIV-positive TB patients on CPT prophylaxis during treatment": GFSeries("tbhiv_on_cpt"),

    # -- TB preventive services for people already in HIV care -------------------
    # Held out of the first version of this connector on the grounds that nothing else in
    # the panel measured them. That was wrong about the panel. UNAIDS AIDSinfo publishes
    # the proportion counterpart of all three, and those exports were already sitting in
    # data/raw/unaids unread, so these are two-instrument series and always were.
    "People living with HIV in care screened for TB": GFSeries("plhiv_tb_screened"),
    "People living with HIV on ART who initiated TB preventive therapy": GFSeries("tpt_initiations"),
    "People who completed TPT": GFSeries("tpt_completions"),
}

# Named so the log can say these were seen and left out on purpose, which is the whole
# point of the mechanism: a warning that fires on 31 names every run hides the one new
# name that matters. Three different reasons appear below and they are kept apart.

# 1. HIV indicators with no canonical id, or no population dimension in the panel. Adding
#    either is a decision about the panel's vocabulary and not about this source.
_UNMAPPED_HIV = {
    "Adolescent girls and young women (AGYW) reached with HIV prevention programs",
    "Adolescent girls and young women who received antiretroviral pre-exposure prophylaxis",
    "Antenatal care attendees tested for syphilis",
    "Care & support services to people Living with HIV",
    "Early infant diagnosis",
    "Individual HIV self-test kits distributed",
    "Medical male circumcisions performed",
    "Number of HIV tests among adolescents and youth",
    "Number of HIV tests among other vulnerable population",
    "Number of HIV tests taken among prisoners",
    "Other vulnerable populations reached with HIV prevention programs",
    "People on ART who are received multi month supply of antiretroviral medicine",
    "People on ART with viral load test result",
    "People reached with HIV prevention programs",
    "People receiving Opioid Substitution Therapy",
    "Pregnant women who know their HIV status",
    "Prisoners reached with HIV prevention programs",
    "Young people aged 10-24 years reached by comprehensive sexuality education and/or "
    "life skills-based HIV education",
    "Young people aged 10-24 years reached with HIV prevention programs",
}

# 2. The rest of the Global Fund's portfolio. Annual_Results is not an HIV dataset, it is
#    every indicator the institution's grants report, so malaria, drug-resistant TB and
#    the cross-cutting health-systems lines all arrive in the same response and are all
#    outside this panel.
_UNMAPPED_OTHER_DISEASE = {
    "Care & support services to TB patients",
    "Cases of Malaria treated",
    "Cases reported within 24 hours of treatment (elimination settings)",
    "Children who received seasonal malaria chemoprophylaxis",
    "Confirmed malaria cases fully investigated and classified",
    "Contacts of people with bacteriologically confirmed TB evaluated for TB",
    "Districts achieving national target for the proportion of confirmed malaria patients "
    "who received first-line antimalarial treatment",
    "Districts achieving national target for the proportion of suspected malaria patients "
    "who received a parasitological test",
    "Infants who received the full number of courses of perennial malaria chemoprevention (PMC)",
    "Insecticide-treated mosquito nets distributed",
    "Malaria foci fully investigated and classified",
    "Number of cases of XDR TB enrolled on treatment",
    "Number of community based organizations that received a pre-defined package of training",
    "Number of iCCM conditions treated among children under five in target areas",
    "People in contact with TB patients received preventive therapy",
    "People with TB treated",
    "Percentage of TB patients with DST result for at least Rifampicin",
    "Population covered by Indoor Residual Spraying",
    "Pregnant women attending antenatal clinics who received intermittent preventive "
    "treatment for malaria",
    "Prevention: People covered by LLINs distributed",
    "RR-TB and/or MDR-TB cases notified",
    "RR-TB and/or MDR-TB that began second-line treatment",
    "RR/MDR-TB patients with DST results for Fluoroquinolone",
    "Structures covered by Indoor Residual Spraying",
    "Suspected malaria cases that receive a parasitological test",
    "TB patients tested using WHO recommended rapid tests",
}

_KNOWN_UNMAPPED = frozenset(_UNMAPPED_HIV | _UNMAPPED_OTHER_DISEASE)


class GlobalFundConnector(BaseConnector):
    source_id = "global_fund"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "Global Fund Data Service, grant-reported annual results by country and year"
    timeout = 120

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._geographies: Optional[Dict[str, Tuple[str, str]]] = None

    # -- the country map -------------------------------------------------------
    def geographies(self) -> Dict[str, Tuple[str, str]]:
        """Geography id -> (ISO3, country name), for the countries only.

        Multicountry, Sub-continent, Continent and World geographies are left out. A
        regional grant's results have no country to belong to, and a code that resolved to
        one anyway would put a region's figures under a country's name.
        """
        if self._geographies is None:
            url = f"{_BASE}/Geographies?$select=id,code,level,name"
            rows = self.get_json(url).get("value", [])
            kept = {}
            levels: Dict[str, int] = {}
            for r in rows:
                level = str(r.get("level") or "")
                levels[level] = levels.get(level, 0) + 1
                if level != "Country":
                    continue
                code = str(r.get("code") or "").strip().upper()
                if len(code) == 3:
                    kept[str(r.get("id"))] = (code, str(r.get("name") or ""))
            self._geographies = kept
            log.info("global_fund: %d geographies, %d of them countries (%s)",
                     len(rows), len(kept),
                     ", ".join(f"{k or 'unlabelled'} {v}" for k, v in sorted(levels.items())))
        return self._geographies

    # -- the results -----------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None
        geo = self.geographies()

        url = (f"{_BASE}/AllProgrammaticIndicators"
               f"?$filter=programmaticDataSet eq '{_DATASET}'")
        payload = self.get_json(url)
        rows = payload.get("value", [])
        if payload.get("@odata.nextLink"):
            log.warning("global_fund: the response is paged now, and this connector reads "
                        "only the first page — %d rows so far", len(rows))
        log.info("global_fund: %d %s rows", len(rows), _DATASET)

        emitted = 0
        subnational = 0
        unresolved = 0
        unmapped: Dict[str, int] = {}
        per_indicator: Dict[str, int] = {}

        for r in rows:
            name = str(r.get("indicatorName") or "").strip()
            spec = _SERIES.get(name)
            if spec is None:
                unmapped[name] = unmapped.get(name, 0) + 1
                continue

            # One grant's catchment, wearing a country's code. See the docstring.
            if str(r.get("geographicCoverage") or "").strip() != "National":
                subnational += 1
                continue

            resolved = geo.get(str(r.get("recordId")))
            if resolved is None:
                unresolved += 1
                continue
            iso3, country_name = resolved
            if wanted and iso3 not in wanted:
                continue

            year = r.get("resultValueYear")
            try:
                year = int(year)
            except (TypeError, ValueError):
                continue
            if year < start_year or year > end_year:
                continue

            value = r.get("resultValueNumerator")
            if value is None:
                continue
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue

            canonical = CANONICAL_INDICATORS.get(spec.canonical)
            src_type = spec.source_type or (
                canonical.default_source_type if canonical else self.default_source_type)

            yield self.make_row(
                country_iso3=iso3,
                country_name=country_name,
                indicator_id=spec.canonical,
                year=year,
                value=value,
                population_group=spec.population_group,
                denominator=_num(r.get("resultValueDenominator")),
                unit=canonical.unit if canonical else "count",
                source_type=src_type.value,
                source_url=url,
                source_indicator_code=name,
                extra={"dataset": _DATASET,
                       "value_type": r.get("valueType") or "",
                       "geographic_coverage": r.get("geographicCoverage") or ""},
            )
            emitted += 1
            per_indicator[spec.canonical] = per_indicator.get(spec.canonical, 0) + 1

        for canonical, n in sorted(per_indicator.items(), key=lambda kv: -kv[1]):
            log.info("global_fund: %-24s %5d rows", canonical, n)
        log.info("global_fund: %d rows emitted, %d subnational rows left out, "
                 "%d rows whose geography is not a country", emitted, subnational, unresolved)

        new_names = {n: c for n, c in unmapped.items() if n not in _KNOWN_UNMAPPED and n}
        if new_names:
            log.warning("global_fund: %d indicator names this connector does not map, and "
                        "which were not there when it was written: %s",
                        len(new_names),
                        ", ".join(f"{n} ({c})" for n, c in sorted(new_names.items())))


def _num(x) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
