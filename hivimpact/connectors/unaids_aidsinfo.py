"""
UNAIDS AIDSinfo connector — ingests the platform's official CSV exports.

AIDSinfo (https://aidsinfo.unaids.org/) has no clean public API; its supported
structured export is CSV. You export indicators from the platform into
`data/raw/unaids/`, keeping AIDSinfo's own descriptive filenames — e.g.
  `People living with HIV_People living with HIV - All ages_Population_ All.csv`
  `Men who have sex with men_HIV prevalence among men who have sex with men_Population_ Total.csv`
This connector maps those descriptive names to canonical indicators (and, for the key
populations, to a population_group), so you don't have to rename anything.

CSV shape (wide): `Country, 1990, 1990_lower, 1990_upper, 1990_Footnote, 1991, ...`.
Values use spaces as thousands separators ("920 000"); `...` = missing. We capture the
point estimate plus its lower/upper uncertainty bounds.

Eight early infant diagnosis values in the export carry bounds which exclude the value, for
Brunei (2013, 2018, 2019, 2022 and 2023) and Timor-Leste (2013, 2014 and 2022). Brunei 2013
reads ">98" with bounds of 38 and 79, and Timor-Leste 2013 reads 9 with a lower and an upper
bound of ">98". Under ruling R30 of research/rulings_2026-10-15.md the values enter without
bounds, and the bounds as published stay in extra under bounds_refused.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import AGE_ALL, PanelRow, SourceType
from ..config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_YEAR = re.compile(r"^(19|20)\d{2}$")

# Published values refused, keyed by canonical id, ISO3 and year, with the reason logged
# for every refusal. AIDSinfo republishes the WHO TB/HIV estimates, and the refusal of the
# Lithuanian TB/HIV incidence for 2009 matches the refusal in who_tme (ruling R27 of
# research/rulings_2026-10-15.md, 16 October 2026).
_REFUSED: Dict[Tuple[str, str, int], str] = {
    ("tbhiv_incidence", "LTU", 2009): "the Lithuanian TB/HIV incidence of 2,800 for 2009 exceeds "
                                      "the UNAIDS estimate of 2,000 people living with HIV in "
                                      "Lithuania for 2009 and would make 82 per cent of Lithuanian "
                                      "TB cases HIV-positive, against about two per cent in 2008 "
                                      "and 2010",
}

# --- key-population files: category prefix -> population_group -----------------
POP_FROM_CATEGORY = {
    "men who have sex with men": "gbmsm",
    "people who inject drugs": "pwid",
    "sex workers": "sex_workers",
    "transgender people": "transgender",
    "prisoners": "prisoners",
}
# within a key-population file, indicator-name substring -> canonical id
KP_INDICATOR_MAP = {
    "hiv prevalence among": "kp_hiv_prevalence",
    "antiretroviral therapy coverage among": "art_coverage_pct",
    "hiv testing and status awareness among": "know_status_pct",

    # Added 2026-09-05. Every key-population export carries one column, "Most recent data as
    # of 2024", so none of these files is a time series and none can show a change after a
    # funding cut. The two below earn a place anyway because a service count means nothing
    # without a denominator. PEPFAR reports how many men who have sex with men its partners
    # reached; only UNAIDS says how many there are to reach. The size estimate supplies the
    # denominator for 552 country-population pairs and the coverage figure supplies the
    # baseline the cut starts from, for 156.
    #
    # The year on these rows is 2024 because that is when UNAIDS last compiled the figure,
    # not when the survey behind it ran, and the survey year differs by country. The rows
    # carry extra["most_recent"] = True so a later analysis can hold them apart from the
    # annual series rather than reading a 2024 stamp as a 2024 measurement.
    "size estimate": "kp_size_estimate",
    "coverage of hiv prevention programmes": "kp_prevention_coverage_pct",
}

# --- general (all-population) files: name substring -> canonical --------------
# order matters: first match wins, so keep specific strings.
CORE_MAP: List[Tuple[str, str]] = [
    ("people living with hiv - all ages", "plhiv"),
    ("new hiv infections - all ages", "new_infections"),
    ("aids-related deaths - all ages", "aids_deaths"),
    ("people living with hiv receiving art (#)", "on_art_count"),
    ("people living with hiv receiving art (%)", "art_coverage_pct"),
    ("people living with hiv who know their status (%)", "know_status_pct"),
    ("people living with hiv who have suppressed viral loads (%)", "community_viral_suppression_pct"),
    ("hiv prevalence - adults (15-49)", "hiv_prevalence_15_49"),
    ("coverage of pregnant women who receive arv for pmtct", "pmtct_coverage_pct"),
    ("people receiving pre-exposure prophylaxis (prep)", "prep_recipients"),
    ("country-reported hiv expenditure", "hiv_expenditure_total"),

    # The seven "TB and HIV" exports. These sat unread in data/raw/unaids until 2026-09-05,
    # because the connector only reads a file it can name and nothing here had a canonical
    # id. Three of them are the counterpart to the TB preventive services the Global Fund
    # publishes as counts, which is what turns those from a single-source series into a
    # measured one. The two modelled files land on canonicals WHO TME already fills.
    #
    # Keep these below the core entries and keep each string long enough to be unambiguous.
    # First match wins, and "newly enrolled ... started on TB preventive therapy" and
    # "currently enrolled ... started on TB preventive therapy" differ by one word.
    ("newly enrolled in hiv treatment started on tb preventive therapy", "tpt_initiation_new_pct"),
    ("currently enrolled in hiv treatment started on tb preventive therapy", "tpt_initiation_current_pct"),
    ("on art who completed a course of tpt", "tpt_completion_pct"),
    ("newly enrolled in hiv treatment diagnosed with tb disease", "plhiv_new_tb_diagnosed_pct"),
    ("co-management of tb and hiv treatment", "tbhiv_comanagement_pct"),
    ("incident tb cases in people living with hiv", "tbhiv_incidence"),
    ("tb-related deaths among people living with hiv", "tbhiv_deaths"),

    # The prevention and vertical-transmission exports, added 2026-09-05 after the coverage
    # audit in scripts/audit_coverage.py reported this connector reading 32 of 146 files.
    #
    # Four of the ten land on canonicals another source already fills, so each was measured
    # against the series already in the panel before being written here. Exact agreement
    # between two sources means one instrument published twice, and a republication must not
    # be counted as corroboration.
    #
    #   hiv_tests_performed        323 overlapping cells, 100.0% exact. This is WHO GHO's own
    #                              series reprinted by UNAIDS, not a second measurement of the
    #                              same quantity. Ingested for the 92 country-years GHO does
    #                              not carry, and never to be read as agreement.
    #   hiv_test_positivity_pct    289 overlaps, 22.5% exact, 65.1% within one percentage
    #                              point, median gap 0.5%. The same instrument at finer
    #                              precision, because UNAIDS prints two decimals where GHO
    #                              rounds. Adds 83 country-years.
    #   pmtct_arv_count            1,515 overlaps, 76.7% exact, median gap 0.0%. Largely a
    #                              republication. Adds 339 cells across 34 countries.
    #   pregnant_women_hiv         759 overlaps, 17.4% exact, median gap 6.8%. The one
    #                              genuinely independent pairing of the four, close to the
    #                              Global Fund against WHO TME benchmark of 8% exact and a
    #                              3.5% median gap. 38% of the cells are censored.
    #
    # The male circumcision file covers 15 countries, which is the whole voluntary medical
    # male circumcision programme, and PEPFAR paid for most of it.
    ("late hiv diagnosis", "late_hiv_diagnosis_pct"),
    ("hiv testing among pregnant women", "anc_hiv_testing_pct"),
    ("early infant diagnosis", "early_infant_diagnosis_pct"),
    ("vertical transmission rate", "vertical_transmission_pct"),
    ("annual number of condoms distributed", "male_condoms_distributed"),
    ("number of male circumcisions performed", "circumcisions_performed"),
    ("hiv tests (volume)", "hiv_tests_performed"),
    ("hiv positivity rate (%)", "hiv_test_positivity_pct"),
    ("pregnant women who received arv for pmtct", "pmtct_arv_count"),
    ("pregnant women needing arv for pmtct", "pregnant_women_hiv"),
]

# The age-group exports of plhiv, new_infections and aids_deaths, filename substring ->
# (canonical id, age_group), under ruling R17 of research/rulings_2026-10-15.md. AGE_MAP is
# read before CORE_MAP. The 18 exports were saved on 18 July 2026 with the all-ages exports and
# hold the years 1990 to 2024, the 2025 round behind the all-ages rows of unaids_aidsinfo. The
# children's rows (0 to 14) and the adults' rows (15 and over) add to the all-ages row, and the
# rows for ages 15 to 49 and 50 and over add to the row for ages 15 and over, within 8.5% in
# every country-year with no censored value, where AIDSinfo prints the totals with two
# significant figures (Pakistan 2012 people living with HIV, 110,000 for all ages against a
# sum of 101,700). No age-group value exceeds the value of the wider age group holding the
# narrower age group. The age_group column keeps every age-group row apart from the all-ages
# row, so reconcile compares an age-group row only with a row of the same age group.
AGE_MAP: List[Tuple[str, str, str]] = [
    (f"{stem} - {label}", canonical, age)
    for stem, canonical in (("people living with hiv", "plhiv"),
                            ("new hiv infections", "new_infections"),
                            ("aids-related deaths", "aids_deaths"))
    for label, age in (("children (0-14)", "0-14"),
                       ("adolescents (10-19)", "10-19"),
                       ("young people (15-24)", "15-24"),
                       ("adults (15-49)", "15-49"),
                       ("adults (15+)", "15+"),
                       ("people aged 50 and over", "50+"))
]

# The exports hivimpact/connectors/unaids_aidsinfo.py is handed and does not read on purpose,
# with the reason for every unread export.
#
# scripts/audit_coverage.py counts an unread file as a gap, the right default, because a filter
# returning quietly reports a clean run whether the filter matched every file or no file. A gap
# somebody has looked at and decided about differs from a gap nobody has seen, and a report
# should not show a decided gap and an unseen gap as the same number. Naming the decision in
# DECLARED_UNMAPPED turns an unseen gap into a decided gap.
#
# An entry is a filename substring and the reason the file stays unread. To revisit an entry,
# move the substring into CORE_MAP or KP_INDICATOR_MAP and add the canonical.
DECLARED_UNMAPPED: List[Tuple[str, str]] = [
    # HIV prevalence for ages 15 and over and for ages 15 to 24. hiv_prevalence_15_49 names
    # the age range in the id, and every source writes hiv_prevalence_15_49 with age_group
    # "all" under ruling R18, so a prevalence for another age range needs a separate id,
    # and no ruling has set up an id for prevalence at ages 15 and over or 15 to 24.
    ("hiv prevalence - adults (15+)", "prevalence for ages 15 and over, no panel id for the age range"),
    ("hiv prevalence - young people (15-24)", "prevalence for ages 15 to 24, no panel id for the age range"),

    # Eight files, four titled "Progress towards 95-95-95 targets" and four titled "Testing and
    # treatment cascade", for all ages, children, female adults and male adults. The eight
    # files use a two-row header, with the year in the first row and the indicator in the
    # second row, and the AIDSinfo parser reads a one-row header only. The all-ages files hold
    # 3,532 values over 176 countries and 3,660 values over 185 countries from 2015 onwards.
    #
    # Reading the files needs a separate parser, and deciding what to do with the values needs
    # a researcher. The first step of every cascade repeats know_status_pct, which the panel
    # already holds. The second and third steps are conditional percentages, the share on
    # treatment among people diagnosed with HIV and the share virally suppressed among people
    # on treatment, and a conditional percentage measures something other than the
    # unconditional art_coverage_pct and community_viral_suppression_pct already in the panel.
    # Whether the conditional percentages earn new canonicals is a question about the analysis
    # and not about the parser.
    ("progress towards 95-95-95", "two-row header the AIDSinfo parser cannot read, and the conditional percentages wait on a ruling"),
    ("testing and treatment cascade", "two-row header the AIDSinfo parser cannot read, and the conditional percentages wait on a ruling"),

    # Treatment-cascade files with ordinary headers and almost no data, the cryptococcal
    # infection file and the two files on differentiated service delivery (DSD) models of
    # antiretroviral treatment. DSD is how a clinic keeps a patient on treatment with fewer
    # visits, and the DSD files would matter if a DSD file covered more than one year.
    ("cryptococcal infection", "24 values over 17 countries and two years, too sparse"),
    ("dsd art models", "one year (2023) across 23 and 14 countries, cannot show a change"),

    # Figures the panel can already compute from series in the panel. An incidence rate per
    # 1,000 for all ages is new_infections over the uninfected population (population less
    # plhiv), an incidence to mortality ratio divides two indicators already present, and
    # storing the quotient invites a later analysis to treat a derived number as a
    # measurement. The incidence rates for an age group divide by the uninfected population of
    # the age group, and the panel holds no population by age group, so no panel id carries
    # the rates for an age group.
    ("per 1000 uninfected population - all ages", "derivable from new_infections, plhiv and population"),
    ("per 1000 uninfected population", "modelled rate for an age group, no population by age group in the panel"),
    ("aids mortality per 1000 population", "derivable from aids_deaths and population"),
    ("incidence_mortality ratio", "derivable from two indicators already in the panel"),
    ("incidence_prevalence ratio", "derivable from two indicators already in the panel"),
    ("trend of aids-related deaths", "derivable from aids_deaths"),
    ("trend of new hiv infections", "derivable from new_infections"),

    # Service counts with no usable time dimension. Every file in the group was inspected on
    # 2026-09-05 and holds a single year or a sparse scatter of values, so no file in the group
    # can show a level before a funding cut and a level after. Procured self-test kits covers
    # 48 countries for 2019 alone. The four cervical cancer files cover 43, 20, 10 and eight
    # countries, with three of the four files for 2024 alone. Male circumcision prevalence
    # holds 47 values spread over 35 countries and 11 years.
    ("procured self-test kits", "one year only (2019), cannot show a change"),
    ("cervical cancer and hiv_", "single-year or near-empty, cannot show a change"),
    ("prevalence of male circumcision", "47 values over 35 countries and 11 years, too sparse"),

    # Modelled counterfactuals and downstream consequences, and not services delivered.
    # Infections averted is a model output and not a figure a clinic records.
    ("infections averted due to pmtct", "modelled counterfactual, not a service count"),
    ("hiv-exposed children who are uninfected", "modelled consequence, not a service count"),
    ("aids orphans", "modelled consequence, not a service count"),

    # Different diseases and different research questions. Congenital syphilis and hepatitis
    # C sit beside HIV in the same antenatal and harm-reduction services, which makes syphilis
    # and hepatitis C of interest, but a panel measuring HIV service delivery would need a
    # decision to widen the research question before carrying syphilis or hepatitis C.
    ("syphilis", "different disease, would widen the research question"),
    ("hcv treatment", "different disease, would widen the research question"),
    ("gender_", "attitudes and partner violence, a different research question"),
    # Ruling R22 of research/rulings_2026-10-15.md carries comprehensive HIV knowledge and condom
    # use at last higher-risk sex by sex, under the Demographic and Health Survey (DHS) standard
    # definitions. The AIDSinfo exports of the two measures give no split by sex, and the
    # footnotes name DHS, Multiple Indicator Cluster Surveys (MICS), Behavioural Surveillance
    # Surveys, surveys of knowledge, attitudes, behaviour and practices, and in the condom
    # export an online survey, so a single export mixes several survey definitions.
    ("knowledge about hiv prevention", "no split by sex and several survey types, unlike the DHS definition of ruling R22"),
    ("combination prevention_condom use at last high-risk sex", "no split by sex and several survey types, unlike the DHS definition of ruling R22"),

    # The key-population exports still unread are single-point 2024 snapshots like the
    # key-population indicators already mapped in KP_INDICATOR_MAP, but every snapshot would need a
    # separate canonical, and no unread snapshot supplies a denominator or a baseline for a
    # service PEPFAR funds. Stigma, violence, syphilis and viral hepatitis are outcomes of a
    # different research question. Condom use among a key population is a 2024 value for a
    # single population, apart from the survey measure of ruling R22.
    ("stigma and discrimination", "single-point 2024 snapshot, outcome of a different question"),
    ("physical violence", "single-point 2024 snapshot, outcome of a different question"),
    ("condom use ", "single-point 2024 snapshot for a key population, no series"),
    ("syphilis prevalence", "single-point 2024 snapshot, outcome of a different question"),
    ("viral hepatitis", "single-point 2024 snapshot, outcome of a different question"),
    ("opioid agonist maintenance therapy", "single-point 2024 snapshot, one population only"),
    ("needles per person who injects drugs", "single-point 2024 snapshot, one population only"),
    ("safe injecting practices", "single-point 2024 snapshot, one population only"),
    ("hiv prevention programmes in prisons", "single-point 2024 snapshot, one population only"),
]


def _declared_reason(stem: str) -> Optional[str]:
    """The reason the AIDSinfo connector leaves a file unread, or None if nobody has decided yet."""
    low = stem.lower()
    for sub, reason in DECLARED_UNMAPPED:
        if sub in low:
            return reason
    return None


def _parse_cell(cell) -> Tuple[Optional[float], Optional[str]]:
    """Parse one AIDSinfo cell into (number, censoring notation).

    AIDSinfo censors small figures for display: `<100`, `<500`, `<200`, `<0.1`, `<0.01`
    and, in the cascade files, `>95`. There are 66,291 such cells across the exports in
    data/raw/unaids. They are bounds, and stripping the `<` puts a point estimate in the
    panel that the source never asserted — which is how Ukraine came to be recorded as
    spending 100 US dollars on HIV in 2018, between 108 million in 2017 and 100 million
    in 2019. The notation is returned alongside the number so the caller can decide what
    the bound means for its own indicator.
    """
    if cell is None:
        return None, None
    s = str(cell).strip()
    if s in ("", "...", "…", "-", "N/A", "NA", "nan"):
        return None, None
    censored = s if s[:1] in ("<", ">") else None
    s = (s.replace(" ", "").replace(" ", "").replace(" ", "")
         .replace(",", "").replace("<", "").replace(">", ""))
    try:
        return float(s), censored
    except ValueError:
        return None, None


def _clean_num(cell) -> Optional[float]:
    """The bare number, where the censoring carries no meaning worth keeping."""
    return _parse_cell(cell)[0]


def _bound(cell, is_lower: bool) -> Optional[float]:
    """One end of the source's own uncertainty interval.

    The bound columns are censored on the same rule as the point column, so they need
    reading the same way. A `<100` in a lower column does not mean the interval stops at
    100 — it means it reaches down to nothing. A `>98` in an upper column states no
    ceiling at all rather than a ceiling of 98. Read literally, both narrow the interval
    the source published, which is the wrong direction for an uncertainty bound to move.
    """
    v, censored = _parse_cell(cell)
    if v is None or not censored:
        return v
    if censored.startswith("<") and is_lower:
        return 0.0
    if censored.startswith(">") and not is_lower:
        return None
    return v


def _censored_row(value: Optional[float], notation: str, unit: str,
                  lower: Optional[float], upper: Optional[float]):
    """Turn a censored cell into (value, lower, upper) for the panel.

    The notation means different things in the two instruments AIDSinfo publishes, and
    the difference is not a matter of degree. In the epidemiological files a `<100` sits
    inside a series whose other years run to about 800, so it is an honest small estimate
    of a small epidemic — 37 countries have their entire new-infections series censored,
    and blanking it would delete them from the panel. In the country-reported expenditure
    file the same `<100` sits inside a series whose other years have a median of 22.4
    million US dollars: South Africa is `<100` for 2015 and 2016 against an other-year
    median of 2.42 billion. No country spent under 100 dollars on HIV. There the notation
    is the display floor standing in for a GAM return with no usable total, which makes
    it a non-report — the same finding as the GAM zero, arrived at from the other side.

    So a censored count keeps its number, bounded, and a censored currency amount keeps
    no number at all. Either way the notation itself is recorded, so the choice can be
    revisited without re-reading the raw exports.
    """
    if notation.startswith(">"):
        # The cascade files report `>95` for a country at or above the target: a floor,
        # not a ceiling, so the bound goes on the other side.
        lower = value if lower is None else lower
    else:
        lower = 0.0 if lower is None else lower
        upper = value if upper is None else upper
        if unit == "USD":
            value = None
    return value, lower, upper


def _classify(stem: str) -> Optional[Tuple[str, str, str, str]]:
    """Return (canonical_id, population_group, sex, age_group) for a filename stem, or None to skip."""
    low = stem.lower()
    category = low.split("_", 1)[0].strip()
    sex = "female" if low.rstrip().endswith("females") else "male" if low.rstrip().endswith("males") else "all"

    if category in POP_FROM_CATEGORY:
        for sub, canon in KP_INDICATOR_MAP.items():
            if sub in low:
                return canon, POP_FROM_CATEGORY[category], sex, AGE_ALL
        return None
    for sub, canon, age in AGE_MAP:
        if sub in low:
            return canon, "all", sex, age
    for sub, canon in CORE_MAP:
        if sub in low:
            return canon, "all", sex, AGE_ALL
    return None


class UNAIDSAidsinfoConnector(BaseConnector):
    source_id = "unaids_aidsinfo"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = "UNAIDS AIDSinfo — CSV exports (epi, cascade, key populations, finance)."

    def __init__(self, raw_dir: str = "data/raw/unaids", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        if not self.raw_dir.exists():
            log.warning("unaids_aidsinfo: %s does not exist — export CSVs from AIDSinfo first", self.raw_dir)
            return
        files = sorted(self.raw_dir.glob("*.csv"))
        if not files:
            log.warning("unaids_aidsinfo: no CSV in %s", self.raw_dir)
            return

        mapped = declared = 0
        undecided: List[str] = []
        bounds_refused: Dict[str, int] = {}
        for path in files:
            cls = _classify(path.stem)
            if cls is None:
                if _declared_reason(path.stem):
                    declared += 1
                else:
                    undecided.append(path.name)
                continue
            canonical, pop, sex, age = cls
            spec = CANONICAL_INDICATORS.get(canonical)
            unit = spec.unit if spec else ""
            src_type = (spec.default_source_type if spec else self.default_source_type).value
            mapped += 1

            try:
                df = pd.read_csv(path, dtype=str)
            except Exception as exc:
                log.warning("unaids_aidsinfo: could not read %s: %s", path.name, exc)
                continue
            df.columns = [str(c).strip() for c in df.columns]
            if "Country" not in df.columns:
                log.warning("unaids_aidsinfo: no Country column in %s — skipping", path.name)
                continue
            year_cols = [c for c in df.columns if _YEAR.match(c)]
            # key-population / survey exports use a single "Most recent data as of YYYY" column
            recent_col = next((c for c in df.columns if "most recent data as of" in c.lower()), None)
            recent_year = None
            if recent_col:
                m = re.search(r"(19|20)\d{2}", recent_col)
                recent_year = int(m.group()) if m else None

            n = 0
            for _, row in df.iterrows():
                iso3 = to_iso3(row["Country"])
                if not iso3 or (wanted and iso3 not in wanted):
                    continue
                for y in year_cols:
                    val, censored = _parse_cell(row[y])
                    if val is None:
                        continue
                    year = int(y)
                    if year < start_year or year > end_year:
                        continue
                    reason = _REFUSED.get((canonical, iso3, year))
                    if reason:
                        log.info("unaids_aidsinfo: %s %s %d refused, %s", canonical, iso3, year, reason)
                        continue
                    lo = _bound(row.get(f"{y}_lower"), True)
                    hi = _bound(row.get(f"{y}_upper"), False)
                    extra = {"export_file": path.name}
                    if censored:
                        val, lo, hi = _censored_row(val, censored, unit, lo, hi)
                        extra["censored"] = censored
                    if val is not None and ((lo is not None and lo > val)
                                            or (hi is not None and hi < val)):
                        # Ruling R30. Bounds which exclude the value of the same row are
                        # not an interval around the value, and the connector does not
                        # repair a bound. The bounds as published stay in extra.
                        printed = (row.get(f"{y}_lower"), row.get(f"{y}_upper"))
                        extra["bounds_refused"] = " to ".join(
                            "missing" if pd.isna(c) or not str(c).strip() else str(c).strip()
                            for c in printed)
                        lo = hi = None
                        bounds_refused[canonical] = bounds_refused.get(canonical, 0) + 1
                    yield self.make_row(
                        country_iso3=iso3, country_name=str(row["Country"]),
                        indicator_id=canonical, year=year, value=val,
                        value_lower=lo, value_upper=hi,
                        population_group=pop, sex=sex, age_group=age, unit=unit, source_type=src_type,
                        source_url="https://aidsinfo.unaids.org/",
                        source_indicator_code=path.stem[:80],
                        extra=extra,
                    )
                    n += 1
                if recent_col and recent_year and start_year <= recent_year <= end_year:
                    val, censored = _parse_cell(row[recent_col])
                    if val is not None:
                        lo = hi = None
                        extra = {"export_file": path.name, "most_recent": True}
                        if censored:
                            val, lo, hi = _censored_row(val, censored, unit, None, None)
                            extra["censored"] = censored
                        yield self.make_row(
                            country_iso3=iso3, country_name=str(row["Country"]),
                            indicator_id=canonical, year=recent_year, value=val,
                            value_lower=lo, value_upper=hi,
                            population_group=pop, sex=sex, age_group=age, unit=unit, source_type=src_type,
                            source_url="https://aidsinfo.unaids.org/",
                            source_indicator_code=path.stem[:80],
                            extra=extra,
                        )
                        n += 1
            log.info("unaids_aidsinfo: %-60s -> %d rows (%s / %s / %s)", path.name[:60], n, canonical, pop, age)

        # A count of files read says nothing on its own, because a connector reporting a
        # clean run reports the same clean run whether the connector matched everything or
        # almost nothing. Reporting the three numbers together is what makes the difference
        # visible, and an export in the third number is the only one that needs anyone's
        # attention, because an export in the third number is a decision nobody has made.
        log.info("unaids_aidsinfo: read %d of %d exports, %d deliberately left alone, "
                 "%d awaiting a decision", mapped, len(files), declared, len(undecided))
        for canonical, n in sorted(bounds_refused.items()):
            log.info("unaids_aidsinfo: %s, %d values have published bounds which exclude the "
                     "value, and the values enter without bounds under ruling R30", canonical, n)
        for name in undecided:
            log.warning("unaids_aidsinfo: no rule covers %s. Add the file to CORE_MAP, to "
                        "KP_INDICATOR_MAP, or to DECLARED_UNMAPPED with a reason.", name)
