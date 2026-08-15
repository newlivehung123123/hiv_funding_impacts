"""
The canonical indicator registry — the living vocabulary of the panel.

Each connector maps its own source codes onto these canonical ids, so the panel is
comparable across sources (the basis for triangulation). This is deliberately a
*starter* set drawn from sections 1 and 3 of Adrian's indicator document; it is meant
to grow as we confirm exact source codes (that confirmation is Phase-1 discovery work,
not something to guess up front).

Only codes we are confident about are hard-wired (currently: World Bank). WHO and
UNAIDS codes are discovered/mapped inside their own connectors, because their exact
indicator identifiers must be read from the live catalogue / a real export, never
assumed.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..schema import SourceType


@dataclass(frozen=True)
class IndicatorSpec:
    canonical_id: str
    name: str
    unit: str                      # "count" | "percent" | "USD" | "per_1000"
    default_source_type: SourceType
    domain: str                    # "epi" | "cascade" | "prevention" | "financing" | "denominator"
    notes: str = ""


CANONICAL_INDICATORS = {s.canonical_id: s for s in [
    # -- denominators ----------------------------------------------------------
    IndicatorSpec("population_total", "Total population", "count",
                  SourceType.MODELLED_ESTIMATE, "denominator",
                  "Denominator for coverage/incidence rates. World Bank SP.POP.TOTL."),

    # -- epidemic (mostly UNAIDS/WHO modelled estimates, carry CIs) -------------
    IndicatorSpec("plhiv", "People living with HIV (all ages)", "count",
                  SourceType.MODELLED_ESTIMATE, "epi"),
    IndicatorSpec("new_infections", "New HIV infections (all ages)", "count",
                  SourceType.MODELLED_ESTIMATE, "epi"),
    IndicatorSpec("aids_deaths", "AIDS-related deaths (all ages)", "count",
                  SourceType.MODELLED_ESTIMATE, "epi"),
    IndicatorSpec("hiv_prevalence_15_49", "HIV prevalence, ages 15-49", "percent",
                  SourceType.MODELLED_ESTIMATE, "epi",
                  "World Bank SH.DYN.AIDS.ZS (UNAIDS-derived) — a triangulation duplicate of UNAIDS."),

    # -- treatment cascade (the 95-95-95) --------------------------------------
    IndicatorSpec("know_status_pct", "% of PLHIV who know their status (1st 95)", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade"),
    IndicatorSpec("art_coverage_pct", "% of PLHIV on ART (2nd 95, PLHIV base)", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade"),
    IndicatorSpec("on_art_count", "Number of people on ART (PEPFAR MER TX_CURR)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),
    IndicatorSpec("new_diagnoses", "Number newly diagnosed HIV-positive (PEPFAR MER HTS_TST_POS)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),

    # -- the same two counts, split by which US agency paid for them --------------------
    # The country total is the sum of several US funding agencies, and the agencies were not
    # cut alike: USAID was dismantled while HHS/CDC continued. Summing them hides the event
    # this project exists to measure. Kenya FY2024->FY2025 is the case in point — the USAID
    # treatment cohort falls 472,520 -> 413,032 while the CDC cohort rises 797,595 -> 844,340,
    # so the country total moves about one percent and shows almost nothing.
    #
    # These are a partition of `on_art_count` / `new_diagnoses`, not additions to them: the
    # three agency series for a country-year sum back to the country total. Anything that
    # totals the panel must therefore use one level or the other and never both.
    #
    # This follows the pattern already set by OECD CRS, where a donor is carried as its own
    # canonical series (`global_fund_hiv_disbursements`) instead of a column the schema
    # has not got.
    IndicatorSpec("on_art_count_usaid", "People on ART at USAID-funded partners (MER TX_CURR)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "USAID's share of the PEPFAR treatment cohort. The arm that was dismantled."),
    IndicatorSpec("on_art_count_cdc", "People on ART at HHS/CDC-funded partners (MER TX_CURR)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "CDC's share. The comparison arm — it continued while USAID was cut, so a "
                  "divergence between the two is the funding-cut signal with the country's own "
                  "epidemic, season and reporting calendar held constant."),
    IndicatorSpec("on_art_count_other_agency", "People on ART at other US-agency partners (MER TX_CURR)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "DOD, HRSA, Peace Corps, State. Small, and pooled so the three series still "
                  "sum to the country total."),
    IndicatorSpec("new_diagnoses_usaid", "Newly diagnosed at USAID-funded partners (MER HTS_TST_POS)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),
    IndicatorSpec("new_diagnoses_cdc", "Newly diagnosed at HHS/CDC-funded partners (MER HTS_TST_POS)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),
    IndicatorSpec("new_diagnoses_other_agency", "Newly diagnosed at other US-agency partners (MER HTS_TST_POS)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),
    IndicatorSpec("viral_suppression_pct", "% of people on ART who are virally suppressed (3rd 95)", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade",
                  "The strict third 95 (denominator = people on treatment)."),
    IndicatorSpec("community_viral_suppression_pct", "% of ALL PLHIV who are virally suppressed", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade",
                  "Community viral suppression (denominator = all PLHIV, ~product of the three 95s). "
                  "Distinct from the 3rd 95 — the amfAR report flags MOUs that conflate the two."),
    IndicatorSpec("pmtct_coverage_pct", "PMTCT ART coverage among pregnant women with HIV", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),
    IndicatorSpec("kp_hiv_prevalence", "HIV prevalence among a key population", "percent",
                  SourceType.SURVEY, "epi",
                  "Denominator = the key population (set via population_group). Adrian's section 2."),
    IndicatorSpec("know_status_count", "Number of PLHIV who know their HIV status", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Count (not %) — national programme figure. Reconcile vs know_status_pct × plhiv."),
    IndicatorSpec("viral_suppression_count", "Number of PLHIV virally suppressed (VL<1000)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Count (not %) — national programme figure."),
    IndicatorSpec("prep_recipients", "People receiving PrEP", "count",
                  SourceType.ROUTINE_PROGRAMME, "prevention"),

    # -- key-population programme flows (population_group carries WHICH key population) ---
    # NCHADS Cambodia "Boosted CoPCT" quarterly report. These are PERIOD FLOWS (activity
    # during a quarter), summed to an annual value; the sharpest funding-cut signal because
    # KP outreach/testing is the most PEPFAR/Global-Fund-dependent service.
    IndicatorSpec("kp_reached", "Key-population people reached by outreach (period flow)", "count",
                  SourceType.ROUTINE_PROGRAMME, "prevention",
                  "Community outreach reach among a key population (set via population_group). "
                  "Quarterly programme flow summed to annual; NCHADS Boosted CoPCT."),
    IndicatorSpec("kp_tested", "Key-population people tested for HIV (period flow)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "HIV tests delivered to a key population (population_group). Quarterly flow -> annual."),
    IndicatorSpec("kp_hiv_positive", "Key-population people newly testing HIV-positive (period flow)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Confirmed HIV-positive among a key population (population_group). Quarterly flow -> annual."),
    IndicatorSpec("kp_art_enrolled", "Key-population people newly enrolled on ART (period flow)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Newly enrolled on ART among a key population (population_group). Quarterly flow -> annual."),

    # -- community-led monitoring (CLM Asia sentinel; service-disruption signal) ---------
    # data.clm-asia.org, Indonesia slice. SENTINEL sample (a few Jakarta-area facilities),
    # NOT nationally representative — a ground-truth disruption signal, source_type=CLM.
    # Each is a pooled proportion of survey respondents; numerator+denominator retained.
    # `higher_is` in the row's `extra` says whether a rising value is good or bad.
    IndicatorSpec("clm_arv_stockout_pct", "CLM: left facility without ARV/OI due to stockout (last 3mo)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Supply-side disruption. Rising = worse. VS__arv_stockout / 'yes'."),
    IndicatorSpec("clm_treatment_interruption_pct", "CLM: ever stopped antiretroviral treatment", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Treatment interruption. Rising = worse. VS__stop_arv / 'yes'."),
    IndicatorSpec("clm_out_of_pocket_pct", "CLM: paid out of pocket for medicines/tests (last 6mo)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Cost barrier (rises as free/donor-funded services are cut). Rising = worse. PS__out_of_pocket_pay / 'yes'."),
    IndicatorSpec("clm_facility_open_ontime_pct", "CLM: facility opens and closes on time", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Service availability. Rising = better. PS__open_ontime / 'yes'."),
    IndicatorSpec("clm_enough_staff_pct", "CLM: enough staff to meet service-user needs", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Staffing adequacy (cut when funding drops). Rising = better. PS__enough_staff / 'yes'."),
    IndicatorSpec("clm_stigma_pct", "CLM: faced stigma/discrimination at facility (last 6mo)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Acceptability of services. Rising = worse. PS__stigma / 'yes'."),
    IndicatorSpec("clm_psychosocial_support_pct", "CLM: psychosocial support available for PLHIV", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Support-service availability. Rising = better. VS__psychosocial_support / 'yes'."),
    IndicatorSpec("clm_know_vl_pct", "CLM: service user knows own viral load", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "VL-testing access proxy. Rising = better. PS__know_vl / 'yes'."),

    # -- financing (section 3) -------------------------------------------------
    IndicatorSpec("domestic_hiv_spend", "Domestic public HIV expenditure", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing"),
    IndicatorSpec("hiv_expenditure_total", "Country-reported HIV expenditure, all sources", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "UNAIDS country-reported HIV spending across all funding sources."),
    IndicatorSpec("external_hiv_oda_total", "External HIV financing (all donors, ODA)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "OECD CRS purpose code 13040 (STD control incl. HIV/AIDS), all donors."),
    IndicatorSpec("external_hiv_oda_us", "External HIV financing from the United States (ODA)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "OECD CRS 13040, donor = United States, and ForeignAssistance.gov's own HIV "
                  "disbursements — two independent measures of the same money, so filter on "
                  "source_id before summing."),

    # -- the US series split by the agency that managed the money (FA.gov only) ---------
    # Same move as the PEPFAR split below, on Washington's own accounting. The column is
    # MANAGING agency, not funding agency: PEPFAR is appropriated to State's Global Health
    # Programs account, so a funding-agency split puts 102bn USD under State and separates
    # nothing, while managing agency gives USAID 72bn against HHS 43bn.
    #
    # State is its own series and is not pooled into other_agency, because STATE/GHSD is where
    # USAID's global health programmes went in 2025: 6m USD in FY2024, 271m in FY2025. Without
    # it, the USAID fall reads as a bigger cut than it was — Zimbabwe's USAID line drops 40.9m
    # while its State line rises 47.6m and its country total goes UP.
    #
    # The four series partition external_hiv_oda_us for source_id=foreign_assistance.
    IndicatorSpec("external_hiv_oda_us_usaid", "US HIV disbursements managed by USAID", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The arm that was dismantled. Read alongside _state before calling a fall a cut."),
    IndicatorSpec("external_hiv_oda_us_cdc", "US HIV disbursements managed by HHS/CDC", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "HHS restricted to sub-agency CDC, matching PEPFAR's own 'HHS/CDC' label. The "
                  "within-country comparison arm: it continued while USAID did not."),
    IndicatorSpec("external_hiv_oda_us_state", "US HIV disbursements managed by the State Department", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Near zero before FY2025 and then the destination of USAID's global health "
                  "programmes (STATE/GHSD). Reclassification, not new money."),
    IndicatorSpec("external_hiv_oda_us_other_agency", "US HIV disbursements managed by other US agencies", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "DOD, Peace Corps, MCC, DOL, and the non-CDC parts of HHS (NIH, HRSA) — pooled "
                  "so the four series still sum to the country total."),

    IndicatorSpec("global_fund_hiv_disbursements", "Global Fund HIV disbursements to the country", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "From OECD CRS (donor 9OTH012 = the Global Fund). A subset of "
                  "external_hiv_oda_total; key for the backfill/substitution question (does the "
                  "Global Fund rise as US/PEPFAR funding is cut?)."),

    # -- PEPFAR budget vs spend, and the same split by US funding agency ----------------
    # The money-side counterpart of on_art_count_usaid / _cdc. A budget is intent stated a year
    # ahead and an expenditure is what happened, so the gap between them opens as soon as an
    # agency stops spending — a reporting cycle before any treatment number moves.
    #
    # As with the MER split, the three agency series partition the country total: anything
    # summing the panel takes the agency level or the country level, never both.
    #
    # READ THE COMPLETENESS FIELDS BEFORE READING A FALL. Expenditure reports are filed by the
    # staff of the agency being reported on, and in FY2025 the share of budgeted USAID mechanisms
    # filing anything fell from ~0.85 to 0.42 while CDC's held near 0.85. The reported USAID
    # decline is therefore a spend decline and a reporting collapse superimposed, and the file
    # cannot separate them. Every row carries reporting_rate, planned_on_silent_mechanisms and
    # expenditure_ceiling so the interval is visible instead of a point estimate that flatters
    # whichever story the reader arrived with.
    IndicatorSpec("pepfar_planned_funding", "PEPFAR planned funding (budget), all US agencies", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Approved budget for the implementation year, summed over implementing "
                  "mechanisms. Intent, not spend."),
    IndicatorSpec("pepfar_planned_funding_usaid", "PEPFAR planned funding, USAID", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing"),
    IndicatorSpec("pepfar_planned_funding_cdc", "PEPFAR planned funding, HHS/CDC", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing"),
    IndicatorSpec("pepfar_planned_funding_other_agency", "PEPFAR planned funding, other US agencies", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "DOD, HRSA, State, Peace Corps — pooled so the series still sum to the country total."),
    IndicatorSpec("pepfar_expenditure", "PEPFAR expenditure, all US agencies", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Reported spend for the implementation year. A FLOOR where reporting is "
                  "incomplete — see extra.expenditure_ceiling."),
    IndicatorSpec("pepfar_expenditure_usaid", "PEPFAR expenditure, USAID", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The arm that was dismantled. FY2025 is not comparable with FY2024 without "
                  "extra.reporting_rate."),
    IndicatorSpec("pepfar_expenditure_cdc", "PEPFAR expenditure, HHS/CDC", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The comparison arm — it continued, and its reporting rate held, which is what "
                  "makes it a usable control for the USAID series."),
    IndicatorSpec("pepfar_expenditure_other_agency", "PEPFAR expenditure, other US agencies", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing"),
]}


def unit_for(canonical_id: str, default: str = "") -> str:
    spec = CANONICAL_INDICATORS.get(canonical_id)
    return spec.unit if spec else default
