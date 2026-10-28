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
    # Ruling R17 of research/rulings_2026-10-15.md puts the UNAIDS age-group estimates under the
    # three modelled count ids, with the age range in age_group and age_group "all" for all ages.
    IndicatorSpec("plhiv", "People living with HIV", "count",
                  SourceType.MODELLED_ESTIMATE, "epi",
                  "A count for all ages carries age_group all. The UNAIDS estimates for an age "
                  "group (unaids_aidsinfo and unicef_hiv, ruling R17) carry the age range in "
                  "age_group. The State estimates of the National AIDS Control Organisation "
                  "of India (in_naco, ruling R44) carry the State or Union Territory in "
                  "admin1, and the India figure is the in_naco row with admin1 empty, never "
                  "a sum of admin1 rows (ruling R14)."),
    IndicatorSpec("new_infections", "New HIV infections", "count",
                  SourceType.MODELLED_ESTIMATE, "epi",
                  "A count for all ages carries age_group all. The UNAIDS estimates for an age "
                  "group (unaids_aidsinfo and unicef_hiv, ruling R17) carry the age range in "
                  "age_group. The State estimates of the National AIDS Control Organisation "
                  "of India (in_naco, ruling R44) carry the State or Union Territory in "
                  "admin1, and the India figure is the in_naco row with admin1 empty, never "
                  "a sum of admin1 rows (ruling R14)."),
    IndicatorSpec("aids_deaths", "AIDS-related deaths", "count",
                  SourceType.MODELLED_ESTIMATE, "epi",
                  "A count for all ages carries age_group all. The UNAIDS estimates for an age "
                  "group (unaids_aidsinfo and unicef_hiv, ruling R17) carry the age range in "
                  "age_group. The State estimates of the National AIDS Control Organisation "
                  "of India (in_naco, ruling R44) carry the State or Union Territory in "
                  "admin1, and the India figure is the in_naco row with admin1 empty, never "
                  "a sum of admin1 rows (ruling R14)."),
    IndicatorSpec("hiv_prevalence_15_49", "HIV prevalence, ages 15-49", "percent",
                  SourceType.MODELLED_ESTIMATE, "epi",
                  "World Bank SH.DYN.AIDS.ZS repeats the UNAIDS modelled value and is kept as a "
                  "triangulation duplicate of UNAIDS. DHS survey prevalence comes national and by "
                  "survey region, and admin1 holds the survey's own first regional level, which "
                  "can differ from the country's first administrative level. PHIA survey "
                  "prevalence (unaids_phia, ruling R13) comes national only. The modelled "
                  "State prevalence of the National AIDS Control Organisation of India "
                  "(in_naco, ruling R44) comes national and by State or Union Territory in "
                  "admin1. The id name carries "
                  "the age range, so every source writes age_group all (ruling R18)."),
    # Household survey, research/rulings_2026-10-15.md ruling R13. The modelled new_infections
    # id holds a count for all ages, and a survey incidence is a rate for a stated age range.
    IndicatorSpec("hiv_incidence_survey_per_1000",
                  "HIV incidence per 1,000 uninfected people a year (household survey)",
                  "per_1000", SourceType.SURVEY, "epi",
                  "Annual HIV incidence a Population-based HIV Impact Assessment (PHIA) survey "
                  "estimates from recent infections found by a recency test, as new infections "
                  "per 1,000 uninfected people a year, for the age range in age_group. The "
                  "UNAIDS Inequalities dashboard publishes the PHIA incidence with no interval, "
                  "so value_lower and value_upper stay empty. A survey rate is never compared "
                  "with the modelled count new_infections."),

    # -- treatment cascade (the 95-95-95) --------------------------------------
    IndicatorSpec("know_status_pct", "% of PLHIV who have been diagnosed (first 95)", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade"),
    IndicatorSpec("art_coverage_pct", "% of PLHIV on ART (second 95, PLHIV base)", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade"),
    IndicatorSpec("on_art_count", "Number of people on ART (PEPFAR MER TX_CURR)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),
    IndicatorSpec("new_diagnoses", "Number newly diagnosed HIV-positive (PEPFAR MER HTS_TST_POS)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Positive HIV test results reported by the testing programme named in "
                  "source_id, a count of positive tests and not a count of people. PEPFAR MER "
                  "HTS_TST_POS (pepfar_modality, pepfar_panorama, pepfar_snu, pepfar_agency) "
                  "counts positive tests at PEPFAR-supported sites, global_fund carries Global "
                  "Fund grant results, th_hivhub and unaids_services carry national programme "
                  "counts, and pg_ndoh_dashboard carries the Papua New Guinea National "
                  "Department of Health counts by province from 2022 (research/"
                  "rulings_2026-10-15.md, ruling R2). A person tested by PEPFAR and by a "
                  "national programme appears in the PEPFAR count and in the national count, "
                  "and a person tested twice in a year can count twice. Counts from different "
                  "programmes are never added, and new_diagnoses is never compared with "
                  "notified_hiv_cases."),
    # National case surveillance, decided by Jason on 8 October 2026 as a separate id. A notified
    # case is a person the ministry of health registers as newly diagnosed anywhere in the
    # country, while new_diagnoses counts positive test results reported by a testing programme.
    # Never merge notified_hiv_cases with new_diagnoses, and never compare notified_hiv_cases with
    # new_diagnoses as two measurements of a single count.
    IndicatorSpec("notified_hiv_cases", "Notified HIV cases, national case surveillance", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "PAHO Core Indicator 93, the count every ministry of health reports, with the "
                  "female and male split from indicators 94 and 95. Unknown sex travels in "
                  "extra.sex_unknown. Haiti's rows come from the ministry's own annual "
                  "statistical reports (ht_mspp), people who tested HIV positive and know the "
                  "result, by department, 2020 to 2023, with duplicates removed from 2022. "
                  "Bolivia's department rows come from the 2016 epidemiology yearbook of "
                  "the Ministry of Health and Sports (bo_anuario), cases notified with HIV "
                  "plus cases notified in the AIDS phase, for 2016 only. "
                  "Belize's district rows come from the Ministry of Health HIV Surveillance "
                  "Report 2018 (bz_moh), preliminary counts of newly diagnosed HIV "
                  "infections by district of residence, for 2018 only. "
                  "Argentina's province rows come from the Ministry of Health open "
                  "data (ar_snvs), cases notified to SNVS 2.0 by province of "
                  "residence and sex, 2015 to 2024, in the release of 20 January "
                  "2026, which revises past years above the PAHO counts. "
                  "Paraguay's national rows for 2000 to 2009 come from Tabela 3.2 of "
                  "the MERCOSUR HIV epidemiological bulletin 2012 (py_mercosur), new "
                  "HIV diagnoses by sex as the national programme reported the counts, "
                  "with no total for men and women together. "
                  "Nicaragua's rows come from the Ministry of Health Mapa Nacional de la "
                  "Salud (ni_mapasalud), read from Wayback captures, new HIV cases (Casos "
                  "Nuevos) for the 19 SILAIS (local health areas) and nationally, 2017 to "
                  "2023, with 2022 and 2023 archived for some SILAIS only. 13 SILAIS equal "
                  "a department and carry the department name. Six SILAIS cross department "
                  "lines and carry \"SILAIS\" and the SILAIS name. "
                  "Peru's rows for 2019 to the last full year come from the HIV "
                  "situation room of CDC Peru (pe_cdc_sala), HIV cases notified to "
                  "CDC Peru, AIDS cases included, for the 25 departments and "
                  "nationally by sex, read over the websocket of the Shiny "
                  "application, kept only where the departments add to the national "
                  "count and men plus women lie within 10 cases of the national count, under ruling "
                  "R72. "
                  "Mongolia's national rows for 2015 to 2025 come from the Health "
                  "Indicators books of the Health Development Center (mn_hdc), HIV cases "
                  "newly registered in the year, read from Figure 6.23 of the 2024 English "
                  "book and from the HIV section of the 2025 Mongolian book, with no split "
                  "by sex. "
                  "Sri Lanka's national rows for 2010 to 2025 come from the 2025 annual "
                  "report of the National STD/AIDS Control Programme (lk_nsacp), HIV cases "
                  "reported in the year, read from the Total row of Figure 2.6, with no split "
                  "by sex. The quarterly returns of the programme serve as a cross-check "
                  "only, under ruling R8. "
                  "Georgia's national rows for 2002 to 2025 come from two tables of the "
                  "PxWeb service of the National Statistics Office of Georgia (ge_geostat), "
                  "HIV cases newly registered in the year, kept only where the rise in the "
                  "cumulative register equals the new cases, with women and men for 2012 to "
                  "2025 where women plus men equals the total, under ruling R31. "
                  "Belarus's rows for 2000 to 2025 come from indicator 10104000078 of the "
                  "data portal of the National Statistical Committee of the Republic of "
                  "Belarus (by_belstat), HIV cases newly identified in the year, nationally "
                  "by sex and by the age groups 0-14, 15-19, 20-29, 30-39 and 40+, and for "
                  "the six regions and Minsk city by sex, kept only where men plus women, the "
                  "age groups and the regions add to the published totals, under ruling R33. "
                  "Ukraine's rows for 2016 to 2024 come from the HIV monitoring portal of the "
                  "Public Health Centre of the Ministry of Health of Ukraine (ua_npsi), people "
                  "newly registered with HIV in the year in the territory under the control of "
                  "the Government of Ukraine, nationally by the age groups 0-14, 15-24, 25-49 "
                  "and 50+ and by sex at ages 15 and over, and for 22 oblasts and Kyiv city "
                  "for 2017 to 2021, kept only where the age groups, the sexes and the regions "
                  "add to the published totals, with the Donetsk and Luhansk oblasts refused "
                  "in every year and every oblast refused from 2022, under ruling R34. "
                  "Kyrgyzstan's national rows for 2013 to 2025 come from the situation report "
                  "of 1 July 2026 of the Republican Centre for the Control of Blood-borne "
                  "Viral Hepatitis and HIV of the Kyrgyz Republic (kg_aidscenter), HIV cases "
                  "registered in the year among citizens plus foreign citizens, kept only "
                  "where the nine regions, every row and the page header add to the published "
                  "totals, with no split by sex, under ruling R38. "
                  "Montenegro's national rows for 2001 to 2025 come from Table 5 of the 2025 "
                  "annual HIV report of the Institute of Public Health of Montenegro "
                  "(me_ijzcg), people registered with HIV in the year including people "
                  "diagnosed abroad, with men and women for 2025 from Table 1, kept only where "
                  "the columns add to the published totals, men plus women equal the 2025 "
                  "total and the municipalities add to the new diagnoses, under ruling R39. "
                  "Bangladesh's national rows for 2016 to 2025 come from the World AIDS Day "
                  "files of the AIDS/STD Programme (bd_asp), people newly reported HIV "
                  "positive in the programme's reporting year, which runs from 1 November of "
                  "the year before to 31 October of the row year, with the 12 months named in "
                  "extra.reporting_period, Forcibly Displaced Myanmar Nationals included, kept "
                  "only where every cumulative count equals the count of the year before plus "
                  "the new cases, with no split by sex, under ruling R42. "
                  "The Maldives' national rows for 2005 to 2016 come from the Maldives "
                  "Health Statistics 2014 and 2015-16 of the Ministry of Health (mv_moh), "
                  "HIV positive cases detected in the calendar year, Maldivians and "
                  "expatriates together, with the two counts in extra.maldivians and "
                  "extra.expatriates, kept only where the two editions agree for 2007 to "
                  "2014, under ruling R43. "
                  "Armenia's national rows for 2015 to 2025 come from Figures 1 and 2 of the "
                  "HIV situation analysis 2025 of the National Centre for Infectious Diseases "
                  "of Armenia (am_ncid), HIV cases registered in the year among citizens of "
                  "Armenia plus foreign citizens, with the two counts in extra.citizens and "
                  "extra.foreign_citizens, kept only where the citizen counts add to the "
                  "6,625 cases the text prints, the citizen series of Figures 2 and 3 agree "
                  "and the 2025 counts match the text, under ruling R45. "
                  "Tajikistan's rows for the five first-level units for 2014, 2015, 2016, "
                  "2017 and 2021 come from the HIV table of the Ministry of Health yearbooks "
                  "(tj_moh), people newly registered with HIV in the year, kept only where the "
                  "regions add to the Republic total, the districts add to the Districts of "
                  "Republican Subordination and the next yearbook prints the same counts, "
                  "with no national row, under rulings R55 and R59. Tajikistan's national "
                  "rows by sex and by age for 2014 to 2018 come from page 32 of the 2019 "
                  "health compendium of the Agency on Statistics (tj_stat), kept only where "
                  "the age groups add to the printed total of every sex and men plus women "
                  "equal all people in every age group, with no row for all people of all "
                  "ages, under ruling R59. "
                  "Fiji's rows come from the public HIV surveillance workbook of 2025 of the "
                  "Ministry of Health and Medical Services (fj_mohms), people newly registered "
                  "with HIV in the year, nationally for 1989 to 2025, for the three divisions "
                  "for 2018 to 2025, nationally and by division for men, women, transgender "
                  "people and the age groups 0-14 and 15+ for 2018 to 2025, and nationally by "
                  "the age groups 0-4 to 45-49 and 50+ for 2022, 2024 and 2025, kept only "
                  "where the divisions add to the national count and "
                  "the summary report of 2025 prints the workbook counts, under ruling R66. "
                  "Nepal's national rows for 2008 to 2018 come from Table 1 of the World AIDS "
                  "Day factsheets of the National Centre for AIDS and STD Control (np_ncasc), "
                  "read from Wayback captures of six editions, clients with an HIV positive "
                  "result at the HIV testing and counselling sites in the calendar year, which "
                  "the centre reports as the reported HIV cases of the year, kept only where "
                  "every edition printing a full year gives the same count, with the revision "
                  "of 2017 from 1,856 to 1,842 the one known exception, and with no split by "
                  "sex, under ruling R67. "
                  "Never merged with or compared to new_diagnoses (Jason's ruling of 8 "
                  "October 2026). Haiti's national rows for 2010 to 2024, and country-years "
                  "Core Indicator 93 lacks for 16 other countries, come from the "
                  "\"Nuevos diagnosticos\" table of the PAHO Interactive HIV Data Dashboard "
                  "(paho_hiv), only where paho_core emits no row for the same country, year "
                  "and sex. Rows for 48 countries of the WHO European Region, 2000 to "
                  "2019, come from measure HFA_350 of the WHO Europe Health for All "
                  "database (who_europe_hfa), new HIV diagnoses from the joint ECDC and "
                  "WHO Europe surveillance reports, not adjusted for reporting delay, "
                  "with Spain before 2013 and in 2018 and 2019, Italy before 2012 and the "
                  "Netherlands before 2002 refused as partial coverage, Turkey refused "
                  "because the Turkish HIV counts exclude people diagnosed with AIDS at the "
                  "time of HIV diagnosis, North Macedonia before 2017 refused because the "
                  "North Macedonian HIV counts under the separate HIV record type fall below "
                  "the AIDS counts in 10 years from 2000 to 2011, and the Russian "
                  "Federation before 2016 refused because the joint ECDC and WHO report for "
                  "2019 data says the "
                  "Russian case definitions changed in 2016, and Luxembourg refused in every "
                  "year, Austria refused in every year as study cohort data, Serbia refused "
                  "in every year because the WHO Europe Serbian count includes Kosovo, "
                  "which the panel holds under XKX, and Ukraine refused for 2015 under "
                  "ruling R35, with Armenia refused in every year under ruling R45 because "
                  "the Armenian counts hold citizens of Armenia alone. Rows for 50 countries "
                  "of the WHO European Region, 2015 to 2024, come from Table 1 of the joint "
                  "ECDC and WHO Europe report HIV/AIDS surveillance in Europe 2025 "
                  "(ecdc_hiv_report), HIV diagnoses reported to The European Surveillance "
                  "System (TESSy), including people with a previous positive diagnosis made "
                  "abroad or elsewhere in the country, not adjusted for reporting delay, with "
                  "Austria and Turkey refused in every year, North Macedonia for 2015 and "
                  "2016, the Russian Federation for 2015, Spain for 2018 and Ukraine for 2015 "
                  "under ruling R35, Armenia refused in every year under ruling R45 because "
                  "the Armenian counts hold citizens of Armenia alone, and with Serbia "
                  "excluding Kosovo under SRB and Kosovo "
                  "under XKX. "
                  "Reconcile declares ecdc_hiv_report and who_europe_hfa derived, two "
                  "editions of the same TESSy reports."),
    # National AIDS surveillance, research/rulings_2026-10-15.md ruling R7. aids_deaths and
    # new_infections hold modelled estimates, so a surveillance count takes a separate id.
    # Sources on 15 October 2026 are who_europe_hfa (HFA_348, cases only) and cn_ndcpa (the
    # Chinese yearly tables under ruling R10, cases and deaths). From 20 October 2026
    # ecdc_hiv_report adds Table 13 of the 2025 joint ECDC and WHO Europe report, the European
    # AIDS counts for 2015 to 2024, declared derived from HFA_348 (ruling R36). From 21 October
    # 2026 both sources refuse every Armenian AIDS count, a count of citizens alone (ruling R45).
    IndicatorSpec("aids_cases_reported", "People newly reported with AIDS, national surveillance",
                  "count", SourceType.ROUTINE_PROGRAMME, "epi",
                  "The count of people newly reported with AIDS in a calendar year by national "
                  "surveillance, under the AIDS case definition the source names in "
                  "extra.case_definition. Case definitions differ between national "
                  "surveillance systems, so the id compares a country across years and "
                  "compares sources for the same country, and a comparison across countries "
                  "needs extra.case_definition. Never compared with the modelled aids_deaths or "
                  "new_infections, and never with notified_hiv_cases, which counts HIV "
                  "diagnoses at any stage."),
    IndicatorSpec("aids_deaths_reported", "Deaths reported among people reported with AIDS",
                  "count", SourceType.ROUTINE_PROGRAMME, "epi",
                  "The count of deaths from any cause reported in a calendar year among people "
                  "ever reported with AIDS by national surveillance, under the case definition "
                  "in extra.case_definition, with the death definition the source names in "
                  "extra.death_definition. A count of deaths related to HIV, the Fijian "
                  "surveillance definition, is a different measure and never shares the id. "
                  "Never compared with the modelled aids_deaths."),
    # Treatment regimen, added 2026-10-14 for paho_hiv. The denominator is the count in the
    # regimen report every country sends PAHO, which is not the national count on ART.
    IndicatorSpec("on_art_dtg_pct", "People on ART on a dolutegravir-based regimen", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Percentage of people in the country's ART regimen report who take "
                  "dolutegravir or another second-generation integrase inhibitor, from the "
                  "\"DTG\" table of the PAHO Interactive HIV Data Dashboard (paho_hiv), "
                  "31 countries in the Americas, 2020 to 2025. age_group \"10+\" covers "
                  "people aged ten and over and \"0-9\" children under ten, and the two age "
                  "groups are never summed. numerator and denominator hold the counts on a "
                  "dolutegravir regimen and in the regimen report. The regimen report's total "
                  "matches who_gho on_art_count exactly in 31 of 108 country-years, so the "
                  "denominator is never read as the national count on ART."),

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
    # The same partition applied to the count of people newly started on treatment. This is the
    # sharpest of the three, because the treatment cohort is slow and enrolment is not. Someone
    # already on ART keeps collecting refills for months after the money stops, so
    # on_art_count_usaid falls late and gently. A clinic that stops testing stops enrolling in
    # the same week, so art_initiations_usaid falls at once. A cut shows here first.
    IndicatorSpec("art_initiations_usaid", "Newly enrolled on ART at USAID-funded partners (MER TX_NEW)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "USAID's share of PEPFAR treatment enrolment. The arm that was dismantled."),
    IndicatorSpec("art_initiations_cdc", "Newly enrolled on ART at HHS/CDC-funded partners (MER TX_NEW)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "CDC's share, and the comparison arm. CDC continued while USAID was cut, so a "
                  "divergence between the two series holds the country's epidemic, season and "
                  "reporting calendar constant. It does not hold constant patients moving "
                  "between the two agencies' partners, which moves both series at once."),
    IndicatorSpec("art_initiations_other_agency", "Newly enrolled on ART at other US-agency partners (MER TX_NEW)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "DOD, HRSA, Peace Corps, State. Pooled so the three series still sum to the "
                  "PEPFAR country total."),
    IndicatorSpec("viral_suppression_pct", "% of people on ART who are virally suppressed (third 95)", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade",
                  "The strict third 95 (denominator = people on treatment)."),
    IndicatorSpec("community_viral_suppression_pct", "% of ALL PLHIV who are virally suppressed", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade",
                  "Community viral suppression (denominator = all PLHIV, ~product of the three 95s). "
                  "Distinct from the 3rd 95 — the amfAR report flags MOUs that conflate the two."),
    # Household survey ids, research/rulings_2026-10-15.md ruling R13. art_coverage_pct and
    # community_viral_suppression_pct hold modelled values for all ages, and a PHIA value covers
    # a stated age range with a sampling interval, so a PHIA value takes a survey id under
    # Jason's ruling of 7 October 2026.
    IndicatorSpec("art_coverage_survey_pct",
                  "% of people living with HIV on ART (household survey)", "percent",
                  SourceType.SURVEY, "cascade",
                  "People living with HIV who are on antiretroviral therapy, as a share of all "
                  "people living with HIV in the survey sample, from a Population-based HIV "
                  "Impact Assessment (PHIA) survey, for the age range in age_group, with the 95 "
                  "per cent confidence interval in value_lower and value_upper where published. "
                  "Never compared with the modelled art_coverage_pct."),
    IndicatorSpec("community_viral_suppression_survey_pct",
                  "% of people living with HIV who are virally suppressed (household survey)",
                  "percent", SourceType.SURVEY, "cascade",
                  "People living with HIV with a suppressed viral load, as a share of all people "
                  "living with HIV in the survey sample, from a Population-based HIV Impact "
                  "Assessment (PHIA) survey, for the age range in age_group, with the 95 per "
                  "cent confidence interval in value_lower and value_upper where published. The "
                  "denominator is all people living with HIV, so the id is never compared with "
                  "viral_suppression_pct and never with the modelled "
                  "community_viral_suppression_pct."),
    IndicatorSpec("pmtct_coverage_pct", "PMTCT ART coverage among pregnant women with HIV", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade"),
    IndicatorSpec("kp_hiv_prevalence", "HIV prevalence among a key population", "percent",
                  SourceType.SURVEY, "epi",
                  "Denominator = the key population (set via population_group). Adrian's section 2. "
                  "Kazakhstan's national pwid rows for 2020, 2022 and 2024 come from Table 6 of "
                  "the survey reports of the Kazakh Scientific Centre of Dermatology and "
                  "Infectious Diseases (kz_kncdiz), the prevalence weighted in RDS-Analyst "
                  "(RDS is respondent-driven sampling) among people aged 18 and over who "
                  "injected drugs in the last 12 months, with age group 18+, the survey year as "
                  "the year, and the sample share and the interval of the sample share in "
                  "extra, kept only where Table 6, the text and the conclusions agree and the "
                  "two reports print the same 2022 round, under ruling R47."),
    IndicatorSpec("know_status_count", "Number of PLHIV who have been diagnosed with HIV", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Count (not %) — national programme figure. Reconcile vs know_status_pct × plhiv."),
    IndicatorSpec("viral_suppression_count", "Number of PLHIV virally suppressed (VL<1000)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Count (not %) — national programme figure."),
    IndicatorSpec("viral_load_tests_performed", "People on ART with a viral-load result in the year",
                  "count", SourceType.ROUTINE_PROGRAMME, "cascade",
                  "The DENOMINATOR of viral_suppression_pct, carried as a count in its own right "
                  "because viral-load testing volume is itself a funding-cut signal (reagents and "
                  "platform maintenance are donor-funded). Added 2026-10-01 for cm_cnls, which "
                  "prints a regional viral-load cascade no existing indicator covered. Equivalent "
                  "to the PEPFAR MER TX_PVLS denominator. NOT the number of tests run — a person "
                  "tested twice in the year is counted once."),
    IndicatorSpec("viral_load_coverage_pct", "% of people on ART with a viral-load result in the year",
                  "percent", SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Numerator = viral_load_tests_performed, denominator = on_art_count. The "
                  "measurement coverage of the 3rd 95, distinct from viral_suppression_pct, which "
                  "is the result among those measured. Keeping the two apart matters after a "
                  "funding cut, because suppression can look stable while coverage collapses "
                  "(Cameroon 2023: coverage 45.3%, suppression 85.9%). Added 2026-10-01 for cm_cnls."),
    IndicatorSpec("prep_recipients", "People receiving PrEP", "count",
                  SourceType.ROUTINE_PROGRAMME, "prevention",
                  "Carried at two grains and the grain decides whether two rows may be added. "
                  "pepfar_snu writes a province in admin1 and pepfar_panorama writes the "
                  "national PEPFAR total with admin1 empty, so the province rows sum to roughly "
                  "the national row rather than adding to it. UNAIDS, Global Fund and the "
                  "country sources are national and count whoever they fund, so a country with "
                  "several of them has several partial counts and no total."),

    # -- testing throughput (WHO GHO, reported by countries) ---------------------
    # Testing is the first service to feel a funding cut and the first to show it. A
    # treatment cohort is slow to move, because people already on ART stay on ART for a
    # while after the money stops; the number of tests a programme runs in a year moves
    # the same quarter the outreach teams are stood down. The two indicators belong
    # together: volume alone cannot separate a programme that has stopped testing from
    # one that has stopped finding, and positivity rises when a shrinking programme
    # retreats to the highest-yield sites.
    IndicatorSpec("hiv_tests_performed", "HIV tests performed with the result returned to the person", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "WHO GHO HIV_0000000027, reported by countries and split by sex and age. "
                  "Counts tests where the person received the result, so it measures completed "
                  "service contacts and not specimens processed. The splits are a partition of "
                  "the all-ages figure and not additions to it — women 15+, men 15+ and children "
                  "under 15 sum to the total exactly in 82 per cent of country-years — so "
                  "anything that totals the panel must use one level or the other and never "
                  "both, the same rule as the agency split above. The 11 per cent that are more "
                  "than five per cent apart are countries whose disaggregated reporting is "
                  "incomplete, which is worth knowing in its own right. PEPFAR MER HTS_TST is a "
                  "second source, added on 2026-09-05, and counts tests the PEPFAR programme "
                  "paid for rather than tests the country ran, so the PEPFAR figure is a share "
                  "of the WHO GHO figure and not a rival estimate of it. PEPFAR publishes the "
                  "same count twice, once as a partner sum and once as a country row, and "
                  "pepfar_modality reads the country row — see the community and facility "
                  "series below for why the two disagree in the regional operating units. "
                  "who_hts, added on 2026-10-14, reads the WHO HTS Dashboard query service and "
                  "carries the national Global AIDS Monitoring total for 2018, 2019, 2020 and "
                  "2022 to 2024. The who_hts figure equals the who_gho figure in every "
                  "country-year compared for 2022 to 2024, and fills 2018 and 2020, the years "
                  "no other source in the panel carries a national total for."),
    IndicatorSpec("hiv_test_positivity_pct", "% of returned HIV test results that were positive", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "The yield of the testing programme (WHO GHO HIV_POSITIVITY). Read next to "
                  "hiv_tests_performed: falling volume with rising positivity is a programme "
                  "narrowing to its highest-yield sites, which is what retrenchment looks like."),
    # Household survey, cleared by Jason on 7 October 2026 under a separate id carrying the
    # survey's own definition. The id says nothing about receiving the result, because ENDES
    # table 3.3 sets no condition on the result. The DHS and UNAIDS indicator of people tested
    # who received the result is a different measure and never shares hiv_tested_12m_survey_pct.
    IndicatorSpec("hiv_tested_12m_survey_pct",
                  "People aged 15 to 49 who had an HIV test in the last 12 months (household survey)",
                  "percent", SourceType.SURVEY, "cascade",
                  "Peru ENDES table 3.3, women and men aged 15 to 49 together, a weighted share "
                  "with the 95 per cent confidence interval in value_lower and value_upper. "
                  "ENDES table 3.4 (tested and learned the result, as a share of people tested) "
                  "has a different denominator and never enters the panel as a product with table "
                  "3.3. A survey share, not a test count, so never compare the id with "
                  "hiv_tests_performed. Values INEI marks as low precision (coefficient of "
                  "variation above 15 per cent) carry extra.low_precision. Added 2026-10-13 for "
                  "pe_endes."),
    # Household survey, research/rulings_2026-10-15.md ruling R9. The DHS and PHIA measure sets
    # a condition on the result, which hiv_tested_12m_survey_pct does not.
    IndicatorSpec("hiv_tested_12m_result_survey_pct",
                  "People tested for HIV in the last 12 months who received the result "
                  "(household survey)",
                  "percent", SourceType.SURVEY, "cascade",
                  "Respondents who had an HIV test in the 12 months before the interview and "
                  "received the result, as a share of all respondents, for the age range in "
                  "age_group as the survey's own records give the range, with the 95 per cent "
                  "confidence interval in value_lower and value_upper where published. DHS "
                  "indicators HA_CPHT_W_T1R (women) and HA_CPHT_M_T1R (men), which count a "
                  "missing testing answer as not tested. PHIA values are refused, because the "
                  "PHIA tabulation plan removes a respondent with no testing answer from the "
                  "denominator (ruling R13, 16 October 2026). Never compared with "
                  "hiv_tested_12m_survey_pct, which sets no "
                  "condition on the result, and never with hiv_tests_performed, a test count."),

    # -- the same two counts, split by HOW the person was reached ------------------------
    # Facility testing is a nurse offering a test to somebody who already walked into a clinic,
    # and it costs almost nothing extra once the clinic is open. Community testing is a van, a
    # fuel budget, an outreach team and a per-diem, and it is a line item that can be cancelled
    # in a week without closing anything. The two arms therefore respond to the same cut by
    # different amounts, which makes the contrast between them a mechanism and not a total.
    #
    # Between Q4 FY2024 and Q4 FY2025, over the 52 countries whose modality labels are complete,
    # community testing fell 65.0 per cent and facility testing fell 15.6 per cent, and
    # community testing fell further than facility testing in 21 of the 26 countries doing more
    # than twenty thousand tests in Q4 FY2024 with both arms running. Community positivity rose
    # from 1.67 to 3.26 per cent over the same year while facility positivity held at roughly
    # 1.8 per cent.
    #
    # The two arms are a partition of the PEPFAR country total EXCEPT where PEPFAR labels a
    # modality "Not Specified", which happens in seven countries in FY2025 alone. Those rows are
    # counted into the total and into neither arm, and every affected row says so in
    # extra.unclassified_tests.
    IndicatorSpec("hiv_tests_performed_community", "HIV tests performed through community outreach", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "PEPFAR MER HTS_TST at the modality PEPFAR marks as community-based, being "
                  "IndexMod, MobileMod, VCTMod, OtherMod, SNSMod and HomeMod. The cancellable "
                  "arm of the testing programme, and the earliest visible effect of a cut. "
                  "who_hts, added on 2026-10-14, carries a second definition, the national "
                  "Global AIDS Monitoring count of tests in community settings whoever paid, "
                  "covering mobile testing, community voluntary counselling and testing and "
                  "other community testing. Filter on source_id, because the PEPFAR count "
                  "covers PEPFAR-supported sites only and is never the same count as the "
                  "national figure."),
    IndicatorSpec("hiv_tests_performed_facility", "HIV tests performed at a health facility", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "PEPFAR MER HTS_TST at every modality delivered inside a facility. The "
                  "comparison arm for hiv_tests_performed_community, being the same country, the "
                  "same year and the same indicator definition at a different cost structure. "
                  "who_hts, added on 2026-10-14, carries the national Global AIDS Monitoring "
                  "count of tests in health facilities whoever paid, covering provider-initiated "
                  "testing, antenatal clinics, facility voluntary counselling and testing, family "
                  "planning clinics and other facility testing. Filter on source_id, the same "
                  "rule as for hiv_tests_performed_community."),
    IndicatorSpec("new_diagnoses_community", "People newly diagnosed through community outreach", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "PEPFAR MER HTS_TST_POS at the community modalities. Divided by "
                  "hiv_tests_performed_community it gives the yield of outreach testing, which "
                  "rises as a shrinking programme keeps only its highest-yield contacts."),
    IndicatorSpec("new_diagnoses_facility", "People newly diagnosed at a health facility", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "PEPFAR MER HTS_TST_POS at the facility modalities."),
    IndicatorSpec("hiv_self_tests_distributed", "HIV self-test kits distributed", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Self-test kits a country reports distributing in the year, from Global AIDS "
                  "Monitoring through the WHO HTS Dashboard (who_hts). A kit handed out is not a "
                  "test performed and carries no result, so the count never enters "
                  "hiv_tests_performed. 12 countries report for 2018 and 50 for 2024. Added "
                  "2026-10-14 for who_hts."),

    # -- ART initiations: the flow the panel was missing ------------------------
    # Almost everything else here is a stock, and a stock is the wrong instrument for
    # detecting a funding cut. People already on treatment stay on treatment for a while
    # after the money stops, so on_art_count falls slowly and late. Initiations fall in
    # the same reporting period the outreach and testing stop, because a programme that
    # is not finding people cannot start them.
    #
    # The series comes from the WHO TB programme, which collects it to work out how many
    # people on ART should be offered TB preventive treatment. That is why it was invisible
    # to every search that keyed on HIV.
    IndicatorSpec("art_initiations", "People newly enrolled on ART during the year", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "A period flow, not a stock — do not compare it with on_art_count or subtract "
                  "one from the other. WHO TME hiv_reg_new2, falling back to hiv_new where that "
                  "is absent; the two agree in 94 per cent of the country-years that have both, "
                  "and source_indicator_code records which column each row came from. DR Congo "
                  "runs 96,516 in 2022 to 65,651 in 2024 and Cameroon 75,954 in 2021 to 38,059 "
                  "in 2024, which is the kind of movement this project exists to measure. "
                  "PEPFAR MER TX_NEW is a third source, added on 2026-09-05 after a coverage "
                  "audit found the code unread in a file already on disk. PEPFAR measures its "
                  "own programme rather than the country, so the PEPFAR figure sits at or below "
                  "the WHO TME national total in 86 per cent of the 266 overlapping "
                  "country-years and takes a median share of 0.74. Read the two as a national "
                  "total and a funder's share of it, never as rival estimates of one quantity."),

    # -- TB/HIV integrated services, as a three-step cascade --------------------
    # A distinct service line, and one donors fund as a line item, so it can be cut on its
    # own while general HIV testing continues. Reported by national TB programmes for new
    # and relapse TB patients; the 0-14 columns are carried at age_group 0-14.
    IndicatorSpec("tb_patients_hiv_tested", "TB patients with an HIV test result recorded", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "WHO TME newrel_hivtest. The pre-2015 equivalent (hivtest) counted all TB "
                  "patients and not only new and relapse cases, so it is a different measurement "
                  "and is deliberately not mapped onto this id — joining them would put a "
                  "definition change in the middle of the series and read as a jump in 2015."),
    IndicatorSpec("tb_patients_hiv_positive", "TB patients recorded as HIV-positive", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "WHO TME newrel_hivpos. Numerator to tb_patients_hiv_tested."),
    IndicatorSpec("tbhiv_on_art", "HIV-positive TB patients started or continued on ART", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "WHO TME newrel_art. The end of the TB/HIV cascade: tested, found positive, treated."),

    # -- TB preventive services for people already in HIV care ------------------
    # Screening a person in HIV care for TB, and putting them on preventive therapy, are
    # the two services in this panel that a clinic can stop without stopping anything a
    # patient would notice missing. Nobody is turned away and no refill is interrupted, so
    # a cut shows here before it shows in the treatment numbers. Both are funded as grant
    # line items, which is what makes them cuttable on their own.
    #
    # Each is carried as a count and as a percentage, because the Global Fund publishes
    # people and UNAIDS publishes proportions, and neither is derivable from the other
    # without the denominator each organisation used. Held apart, the two are a check on
    # one another. Merged, they would be a unit error.
    IndicatorSpec("plhiv_tb_screened", "People living with HIV in care screened for TB", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Global Fund Annual_Results. The first step of TB case-finding among people "
                  "already in HIV care, and the cheapest step to quietly drop."),
    IndicatorSpec("tpt_initiations", "People living with HIV on ART who started TB preventive therapy", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Global Fund Annual_Results. A started course, not a completed one, so it moves "
                  "in the year the service is delivered, the same property that makes "
                  "art_initiations the panel's target indicator."),
    IndicatorSpec("tpt_completions", "People who completed a course of TB preventive therapy", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Global Fund Annual_Results. A course runs three to six months, so a completion "
                  "counted this year began under last year's funding and this series lags "
                  "tpt_initiations by about a year. The two must not be differenced to infer "
                  "drop-out within one year."),
    IndicatorSpec("tbhiv_on_cpt", "HIV-positive TB patients given co-trimoxazole preventive therapy", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Global Fund Annual_Results. Runs alongside tbhiv_on_art on the same patients, "
                  "so a gap between the two is a supply or protocol failure rather than a change "
                  "in who reached care."),

    # The UNAIDS proportions of the same services, country-reported through GAM. Their
    # denominators are stated in the indicator names and differ from one another, so
    # tpt_initiation_new_pct and tpt_initiation_current_pct are not two readings of one
    # quantity and must not be pooled.
    IndicatorSpec("tpt_initiation_new_pct",
                  "% of people newly enrolled in HIV treatment started on TB preventive therapy", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "UNAIDS AIDSinfo, 2013-2024. Not the percentage counterpart to tpt_initiations, "
                  "which was the expectation until it was tested on the 2026-09-05 panel. Dividing "
                  "the Global Fund count by art_initiations reproduces this figure within one "
                  "percentage point in 41 of 181 country-years, misses by a median of 11.5 points, "
                  "and exceeds 100 per cent in 32 of them, Eswatini 2024 reaching 3,093 per cent on "
                  "194,482 courses against 6,288 new enrolments. The Global Fund counts everyone on "
                  "ART who started a course, so the matching proportion is "
                  "tpt_initiation_current_pct."),
    IndicatorSpec("tpt_initiation_current_pct",
                  "% of people currently enrolled in HIV treatment started on TB preventive therapy", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "UNAIDS AIDSinfo, 2017-2024. Denominator is everyone in care, not the new "
                  "enrolments, so the series falls as a programme catches up with its existing "
                  "cohort and that fall is not a cut. This is the proportion tpt_initiations "
                  "belongs to: the Global Fund count over on_art_count reproduces this figure "
                  "within one percentage point in 48 of 111 country-years, within five in 76, and "
                  "never exceeds 100 per cent. The remainder disagree because the two "
                  "organisations counted different facilities, which is what makes the pair worth "
                  "holding rather than collapsing."),
    IndicatorSpec("tpt_completion_pct",
                  "% of people living with HIV on ART who completed a course of TB preventive therapy", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "UNAIDS AIDSinfo, 2019-2024, 58 countries. The thinnest of these series and the "
                  "one most likely to move because a different set of countries reported."),
    IndicatorSpec("plhiv_new_tb_diagnosed_pct",
                  "% of people newly enrolled in HIV treatment diagnosed with TB disease", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "UNAIDS AIDSinfo, 2013-2024. The yield of TB screening in HIV care, and it reads "
                  "like hiv_test_positivity_pct: rising yield on a falling number screened is a "
                  "programme narrowing to the sickest patients, not a worsening epidemic."),
    IndicatorSpec("tbhiv_comanagement_pct", "% of estimated HIV-positive incident TB cases on TB treatment and ART", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "UNAIDS AIDSinfo, 2000-2024, 168 countries. The numerator counts notified HIV-positive "
                  "TB patients on TB treatment and ART, and the denominator is the WHO estimate of "
                  "HIV-positive incident TB, so values above 100 occur where the notified count exceeds "
                  "the estimate. The percentage is not the ratio of tbhiv_on_art to "
                  "tb_patients_hiv_positive, the notified counts the panel holds from WHO TME. On 1,227 "
                  "country-years shared with WHO TME, the AIDSinfo value lies within a tenth of "
                  "tbhiv_on_art over tbhiv_incidence in 702 and within a tenth of tbhiv_on_art over "
                  "tb_patients_hiv_positive in 32 (ruling R29 of research/rulings_2026-10-15.md)."),

    # -- TB/HIV burden, modelled, with WHO's own bounds -------------------------
    IndicatorSpec("tbhiv_incidence", "Incident TB cases among people living with HIV", "count",
                  SourceType.MODELLED_ESTIMATE, "epi",
                  "WHO TME e_inc_tbhiv_num, with its published low and high bounds, and the UNAIDS "
                  "AIDSinfo export of the same quantity for 193 countries over 2000-2024. The two "
                  "are one instrument published twice, not two: on the 1,815 overlapping "
                  "country-years where UNAIDS prints an uncensored number, the two figures are "
                  "identical in 97.5 per cent and within one per cent in 99.0 per cent. Use WHO "
                  "TME. UNAIDS covers 497 country-years WHO TME lacks and every one of them is a "
                  "censored `<100` bound, so the UNAIDS export adds no point estimate anywhere."),
    IndicatorSpec("tbhiv_deaths", "Deaths from TB among people living with HIV", "count",
                  SourceType.MODELLED_ESTIMATE, "epi",
                  "WHO TME e_mort_tbhiv_num, and the UNAIDS AIDSinfo export of the same quantity "
                  "for 192 countries. One instrument published twice, on the same measurement as "
                  "tbhiv_incidence: of 4,302 overlapping country-years, 3,941 carry an identical "
                  "non-zero figure, 315 are zero in both files, and 46 differ. Unlike the "
                  "incidence export this one is uncensored, so its 432 country-years beyond WHO "
                  "TME are usable numbers and worth keeping. A component of HIV mortality that "
                  "UNAIDS folds into aids_deaths, so this series and aids_deaths overlap and must "
                  "not be added together."),

    # -- TB/HIV money, and the TB programme's funding mix as an exposure measure -
    # The first four are HIV-specific: collaborative TB/HIV activities, which is a budget
    # line a donor can cut on its own. Required against expected is the funding gap as the
    # country itself states it, a year before any service number moves.
    IndicatorSpec("tbhiv_budget", "Budget required for collaborative TB/HIV activities", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing"),
    IndicatorSpec("tbhiv_funding_expected", "Expected funding for collaborative TB/HIV activities", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Read against tbhiv_budget: the shortfall is the country's own statement of "
                  "what it does not expect to be able to pay for."),
    IndicatorSpec("tbhiv_expenditure", "Actual expenditure on collaborative TB/HIV activities", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing"),
    IndicatorSpec("tbhiv_funding_received", "Funding received for collaborative TB/HIV activities", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing"),

    # These six are TB-programme totals and NOT HIV money. They are here as an exposure
    # measure: a country-year record of how much USAID was expected to put into a health
    # programme, next to the two funders that were not cut. Expected USAID funding across
    # all reporting countries falls from 235.5m USD in 2024 to 98.7m in 2025, and the number
    # of countries expecting anything from USAID falls from 31 to 23. Anything totalling HIV
    # financing must exclude every id beginning tb_funding_.
    IndicatorSpec("tb_funding_expected_usaid", "Expected USAID funding for the national TB programme", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Exposure measure, not HIV money. The budget file states 2025 while the "
                  "expenditure file stops at 2024, so this is intent recorded after the cuts and "
                  "tb_funding_received_usaid is the last actual before them."),
    IndicatorSpec("tb_funding_expected_gf", "Expected Global Fund funding for the national TB programme", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Exposure measure, not HIV money. A comparison arm: the Global Fund was not cut."),
    IndicatorSpec("tb_funding_expected_domestic", "Expected domestic funding for the national TB programme", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Exposure measure, not HIV money. The second comparison arm, and the one that "
                  "would have to rise for a country to absorb a donor withdrawal."),
    IndicatorSpec("tb_funding_received_usaid", "USAID funding received by the national TB programme", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "Exposure measure, not HIV money."),
    IndicatorSpec("tb_funding_received_gf", "Global Fund funding received by the national TB programme", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "Exposure measure, not HIV money."),
    IndicatorSpec("tb_funding_received_domestic", "Domestic funding received by the national TB programme", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "Exposure measure, not HIV money."),

    # -- PMTCT, in counts as well as the coverage percentage --------------------
    # pmtct_coverage_pct above is a ratio, and a ratio hides which half moved. These are
    # its numerator and denominator as WHO receives them, so a fall in coverage can be
    # attributed to fewer women treated or to a changed estimate of how many needed it.
    IndicatorSpec("pmtct_arv_count", "Pregnant women with HIV who received ARVs for PMTCT", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Numerator of pmtct_coverage_pct (WHO GHO HIV_0000000016; the identically "
                  "named HIV_0000000015 is catalogued but empty)."),
    IndicatorSpec("pregnant_women_hiv", "Estimated pregnant women with HIV needing ARVs for PMTCT", "count",
                  SourceType.MODELLED_ESTIMATE, "denominator",
                  "Denominator of pmtct_coverage_pct (WHO GHO HIV_0000000021). Modelled, so it "
                  "moves for reasons that have nothing to do with the programme. UNAIDS "
                  "AIDSinfo publishes the same quantity and the two agree exactly in 17.4% of "
                  "overlapping country-years with a median gap of 6.8%, which is close to the "
                  "Global Fund against WHO TME benchmark and marks the pair as two "
                  "measurements rather than one reprinted twice."),

    # -- the rest of the vertical transmission chain, from UNAIDS AIDSinfo ------------
    # pmtct_coverage_pct measures whether a pregnant woman with HIV received treatment. The
    # four below measure the steps either side of it, and each step is a separate place for a
    # funding cut to show. A country can hold PMTCT coverage steady while testing in antenatal
    # care collapses, because coverage is computed among women already known to have HIV.
    IndicatorSpec("anc_hiv_testing_pct", "Pregnant women tested for HIV in antenatal care", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "The step before PMTCT. A woman never tested is never counted as needing "
                  "treatment, so this falling while pmtct_coverage_pct holds is the signature "
                  "of a programme shrinking its own denominator. 139 countries, 15 years. The "
                  "test works on most of them and not on all: AIDSinfo censors this series at "
                  "the top, and 344 of its 1,070 values sit at exactly 98 across 84 countries. "
                  "In 18 of the 139 every reported year is 98, so those series cannot visibly "
                  "fall and the shrinking-denominator test cannot be run on them at all. The "
                  "median across the series is 91 and the remaining 121 countries do move."),
    IndicatorSpec("early_infant_diagnosis_pct", "HIV-exposed infants tested within two months of birth", "percent",
                  SourceType.MODELLED_ESTIMATE, "cascade",
                  "The step after PMTCT, and the one that needs a functioning laboratory "
                  "network rather than a clinic visit. 154 countries, 15 years."),
    IndicatorSpec("vertical_transmission_pct", "Share of HIV-exposed infants who acquire HIV", "percent",
                  SourceType.MODELLED_ESTIMATE, "epidemiology",
                  "The outcome the whole PMTCT chain exists to prevent. Modelled, so it moves "
                  "slowly and late, and a rise here confirms a service failure years after the "
                  "service data showed it. 185 countries, 15 years."),
    IndicatorSpec("late_hiv_diagnosis_pct", "New HIV diagnoses with a CD4 count below 200", "percent",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "The share of people whose HIV is found only once their immune system has "
                  "already collapsed. Testing that stops does not lower the number of people "
                  "with HIV, it delays the moment each one is found, so this rises when "
                  "hiv_tests_performed falls. 193 countries, 7 years."),

    # -- prevention commodities and procedures ----------------------------------------
    # A commodity count is the closest thing in the panel to a purchase order, and a purchase
    # order is the first thing an agency cancels. Neither series depends on a model.
    IndicatorSpec("male_condoms_distributed", "Male condoms distributed in a year", "count",
                  SourceType.ROUTINE_PROGRAMME, "prevention",
                  "UNAIDS publishes male condoms separately from female condoms and this is "
                  "the male series alone. 125 countries but only 5 years."),
    IndicatorSpec("circumcisions_performed", "Voluntary medical male circumcisions performed", "count",
                  SourceType.ROUTINE_PROGRAMME, "prevention",
                  "A one-off surgical procedure delivered in campaigns, which makes it the most "
                  "cancellable service in the panel. PEPFAR paid for most of the global "
                  "programme. Only 15 countries report it, which is close to the whole "
                  "programme rather than a sample of it, across 17 years."),

    # -- key-population denominators and baselines, from UNAIDS AIDSinfo ---------------
    # PEPFAR reports how many men who have sex with men its partners reached. Only UNAIDS says
    # how many there are to reach. Both series below carry one value per country, stamped 2024
    # because that is when UNAIDS last compiled the figure rather than when the survey behind
    # it ran, and the rows carry extra["most_recent"] so an analysis can hold them apart from
    # the annual series.
    IndicatorSpec("kp_size_estimate", "Estimated size of a key population", "count",
                  SourceType.SURVEY, "denominator",
                  "The denominator kp_reached and kp_tested have never had (population_group "
                  "says which key population). 552 country-population values across men who "
                  "have sex with men, people who inject drugs, sex workers, transgender people "
                  "and prisoners. Single point, not a series."),
    IndicatorSpec("kp_prevention_coverage_pct", "Key-population members reached by prevention programmes", "percent",
                  SourceType.SURVEY, "prevention",
                  "The baseline a funding cut starts from (population_group says which key "
                  "population). 156 values. Single point, not a series, so it sets the level "
                  "rather than showing a change."),
    # Household survey, research/rulings_2026-10-15.md ruling R22. The Pacific Data Hub
    # (pacific_data_hub) publishes the three measures for the Pacific Demographic and Health
    # Surveys, and the DHS Program API (dhs) publishes the knowledge and condom measures for the
    # DHS surveys. age_group keeps the ages 15 to 49, 15 and over, and 15 to 24 apart.
    IndicatorSpec("hiv_comprehensive_knowledge_survey_pct",
                  "People with comprehensive correct knowledge of HIV (household survey)",
                  "percent", SourceType.SURVEY, "prevention",
                  "Respondents who know consistent condom use and a single faithful uninfected "
                  "partner reduce the chance of getting HIV, know a healthy-looking person can "
                  "have HIV and reject the two most common local "
                  "misconceptions about HIV transmission or prevention, as a share of all "
                  "respondents, for the age range in age_group and the sex in sex. Demographic "
                  "and Health Survey (DHS) standard definition."),
    IndicatorSpec("condom_last_higher_risk_sex_survey_pct",
                  "Condom use at last higher-risk sex (household survey)",
                  "percent", SourceType.SURVEY, "prevention",
                  "Respondents who used a condom at the last higher-risk intercourse, as a share "
                  "of respondents who had higher-risk intercourse in the 12 months before the "
                  "interview, for the age range in age_group and the sex in sex. The DHS term "
                  "higher-risk intercourse means sex with a partner who was not a spouse and "
                  "did not live with the respondent. DHS standard definition."),
    IndicatorSpec("sex_before_15_survey_pct",
                  "Young people who had sex before age 15 (household survey)",
                  "percent", SourceType.SURVEY, "prevention",
                  "Respondents aged 15 to 24 who had sexual intercourse before age 15, as a share "
                  "of all respondents aged 15 to 24, for the sex in sex, with age_group 15-24. "
                  "DHS standard definition."),

    # -- key-population programme flows (population_group carries WHICH key population) ---
    # NCHADS Cambodia "Boosted CoPCT" quarterly report. These are PERIOD FLOWS (activity
    # during a quarter), summed to an annual value; the sharpest funding-cut signal because
    # KP outreach/testing is the most PEPFAR/Global-Fund-dependent service.
    IndicatorSpec("kp_reached", "Key-population people reached by outreach (count over the period)", "count",
                  SourceType.ROUTINE_PROGRAMME, "prevention",
                  "Community outreach reach among a key population (set via population_group). "
                  "Quarterly programme flow summed to annual; NCHADS Boosted CoPCT."),
    IndicatorSpec("kp_tested", "Key-population people tested for HIV (count over the period)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "HIV tests delivered to a key population (population_group). Quarterly flow -> annual."),
    IndicatorSpec("kp_hiv_positive",
                  "Key-population people newly testing HIV-positive (count over the period)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Confirmed HIV-positive among a key population (population_group). Quarterly flow -> annual."),
    IndicatorSpec("kp_art_enrolled", "Key-population people newly enrolled on ART (count over the period)", "count",
                  SourceType.ROUTINE_PROGRAMME, "cascade",
                  "Newly enrolled on ART among a key population (population_group). Quarterly flow -> annual."),

    # -- community-led monitoring (CLM Asia sentinel; service-disruption signal) ---------
    # data.clm-asia.org, Indonesia slice. SENTINEL sample (a few Jakarta-area facilities),
    # NOT nationally representative — a ground-truth disruption signal, source_type=CLM.
    # Each is a pooled proportion of survey respondents; numerator+denominator retained.
    # `higher_is` in the row's `extra` says whether a rising value is good or bad.
    IndicatorSpec("clm_arv_stockout_pct",
                  "Left facility without ARV or OI medicines because of a stockout "
                  "in the last three months (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Supply-side disruption. Rising = worse. VS__arv_stockout / 'yes'."),
    IndicatorSpec("clm_treatment_interruption_pct", "Ever stopped antiretroviral treatment (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Treatment interruption. Rising = worse. VS__stop_arv / 'yes'."),
    IndicatorSpec("clm_out_of_pocket_pct",
                  "Paid out of pocket for medicines or tests in the last six months (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Cost barrier (rises as free/donor-funded services are cut). Rising = worse. PS__out_of_pocket_pay / 'yes'."),
    IndicatorSpec("clm_facility_open_ontime_pct", "Facility opens and closes on time (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Service availability. Rising = better. PS__open_ontime / 'yes'."),
    IndicatorSpec("clm_enough_staff_pct", "Enough staff to meet the needs of service users (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Staffing adequacy (cut when funding drops). Rising = better. PS__enough_staff / 'yes'."),
    IndicatorSpec("clm_stigma_pct",
                  "Faced stigma or discrimination at the facility in the last six months (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Acceptability of services. Rising = worse. PS__stigma / 'yes'."),
    IndicatorSpec("clm_psychosocial_support_pct", "Psychosocial support available for PLHIV (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "Support-service availability. Rising = better. VS__psychosocial_support / 'yes'."),
    IndicatorSpec("clm_know_vl_pct", "Service user knows own viral load (CLM)", "percent",
                  SourceType.COMMUNITY_LED_MONITORING, "service_access",
                  "VL-testing access proxy. Rising = better. PS__know_vl / 'yes'."),

    # -- financing (section 3) -------------------------------------------------
    IndicatorSpec("domestic_hiv_spend", "Domestic public HIV expenditure", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The country's own public money, from the GAM expenditure return's "
                  "TotalPublic column. The series that has to rise if a government "
                  "replaces withdrawn donor funding."),
    IndicatorSpec("hiv_expenditure_total", "Country-reported HIV expenditure, all sources", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "UNAIDS country-reported HIV spending across all funding sources. "
                  "Published twice, by AIDSinfo and by the GAM expenditure database, and "
                  "the two are the same exercise, so filter on source_id before summing."),

    # -- the country's own account of who paid (UNAIDS GAM expenditure database) --------
    # The financing columns of the GAM return, read off the grand-total row. The three
    # donor series matter because they are the COUNTRY's account of donor money, while
    # pepfar_expenditure and global_fund_hiv_disbursements are the DONOR's account of the
    # same money. Two accounts of one flow are two measurements, and where they diverge
    # the divergence is information about reporting, not an error to be reconciled away.
    #
    # A zero in this database means "not reported" and is indistinguishable from a real
    # zero, so no zero is emitted. An absent series therefore means the country filed
    # nothing on that line, never that the country spent nothing.
    IndicatorSpec("hiv_expenditure_domestic_private", "Private HIV expenditure (country-reported)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Insurance, households, corporations and non-profit institutions "
                  "combined. Reported by only 252 of 541 country-years."),
    IndicatorSpec("hiv_expenditure_households", "Out-of-pocket HIV expenditure by households", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "What patients pay themselves. The series that rises when a programme "
                  "stops paying, so a rise here beside a fall in donor funding is the "
                  "cost-shifting signal. Reported by 153 of 541 country-years."),
    IndicatorSpec("hiv_expenditure_international", "International HIV expenditure (country-reported)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "All external money as the country accounts for it. The parent of the "
                  "three donor series below, which do not always sum to it."),
    IndicatorSpec("hiv_expenditure_other_bilateral", "Other bilateral HIV expenditure (country-reported)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Bilateral donors other than the United States. The place any backfill "
                  "by other governments would appear."),

    # -- what the money was spent on (UNAIDS GAM expenditure database) ------------------
    # The ten top-level lines of the modern GAM classification, all funding sources
    # combined. They partition `Total for key HIV programmes`, NOT the grand total, so
    # they must never be added to the financing series above or to hiv_expenditure_total.
    # Available for 484 of 541 country-years; the rest either use the pre-2016
    # classification (2011-2015 only) or report no programme breakdown at all.
    IndicatorSpec("hiv_spend_treatment", "HIV spending on treatment, care and support", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "GAM line 1. The largest line almost everywhere, and the one that keeps "
                  "paying for patients already enrolled after enrolment stops."),
    IndicatorSpec("hiv_spend_pmtct", "HIV spending on prevention of vertical transmission", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "GAM line 2."),
    IndicatorSpec("hiv_spend_prevention", "HIV spending on prevention", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "GAM line 3, including testing, condoms, PrEP and key-population "
                  "programmes. The discretionary line, so the first to move when funding "
                  "is cut."),
    IndicatorSpec("hiv_spend_gender", "HIV spending on gender programmes", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "GAM line 4."),
    IndicatorSpec("hiv_spend_children", "HIV spending on programmes for children and adolescents", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "GAM line 5."),
    IndicatorSpec("hiv_spend_social_protection", "HIV spending on social protection and economic support", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "GAM line 6."),
    IndicatorSpec("hiv_spend_community", "HIV spending on community mobilisation and system strengthening", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "GAM line 7. The money behind community-led services, which the "
                  "community-led monitoring indicators measure the delivery of."),
    IndicatorSpec("hiv_spend_governance", "HIV spending on governance and sustainability", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "GAM line 8."),
    IndicatorSpec("hiv_spend_enablers", "HIV spending on critical enablers", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing", "GAM line 9."),
    IndicatorSpec("hiv_spend_tb_hiv", "HIV spending on TB/HIV co-infection", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "GAM line 10, against tbhiv_expenditure from the WHO TB dataset, which "
                  "measures the same activities from the TB programme's side."),
    # -- the same money as the national health accounts record it (WHO GHED) ------------
    # A second expenditure system, compiled by WHO with each country's statistical office
    # under the System of Health Accounts 2011, from different ledgers and by different
    # people from the AIDS spending assessment that feeds the GAM series above. Two
    # accounting systems reading one country's HIV budget are two measurements, which is
    # the reason to carry both.
    #
    # WHO's dis11 family is "HIV/AIDS and Other Sexually Transmitted Diseases" and every
    # GAM series is HIV alone, so these are differently scoped rather than two readings of
    # one quantity, and they keep their own canonical ids. The arithmetic backs the
    # separation. Over the country-years both sources cover, the totals sit at a median
    # ratio of 1.14 with 48 of 138 country-years differing by a factor of two or more, and
    # the government line at 1.22 with 68 of 134 differing that far. Reading a WHO total as
    # though it answered the GAM question would import the STD component and the accounting
    # difference together, with no way afterwards to tell which of the two moved.
    #
    # The three financing components are a true partition of the total, closing on all 328
    # country-years where the four are printed together, so anything totalling the panel
    # must take the total or the three components and never both. Every row records which
    # of the two levels it belongs to in extra.partition_level.
    #
    # A zero here is a measurement and is carried, the opposite of the GAM rule, because
    # every zero component sits in an account whose remaining parts still close on the
    # printed total. A blank is how this source says nothing is known.
    #
    # The HIV line runs 2013 to 2023 over 60 countries and thins to 10 countries in its
    # last year, so this source cannot see the 2025 funding cuts and stands as an
    # independent account of the years before them.
    IndicatorSpec("hiv_std_expenditure_total", "HIV and STD spending, national health accounts", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "WHO GHED dis11_usd, converted from the millions the source publishes. "
                  "Wider in scope than hiv_expenditure_total, which is HIV alone, so the "
                  "two are never pooled. The parent of the three components below."),
    IndicatorSpec("hiv_std_expenditure_government", "Government HIV and STD spending, national health accounts", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "WHO GHED dis11_gghed_usd. The health accounts and the AIDS spending "
                  "assessment disagree about this line more than about any other, at a "
                  "median ratio of 1.22, which is a finding about what each system counts "
                  "as government money rather than an error to reconcile away."),
    IndicatorSpec("hiv_std_expenditure_external", "External HIV and STD spending, national health accounts", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "WHO GHED dis11_ext_usd. The line a donor withdrawal empties. Its median "
                  "ratio against the GAM international series is 1.002, so the two centres "
                  "coincide while the direction of the country-level disagreement is a coin "
                  "flip, and neither can stand in for the other."),
    IndicatorSpec("hiv_std_expenditure_private", "Private HIV and STD spending, national health accounts", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "WHO GHED dis11_pvtd_usd. Domestic private money, including what "
                  "households pay themselves, so a rise here beside a fall in the external "
                  "line is the cost-shifting signal in health-accounts form."),
    IndicatorSpec("hiv_std_share_of_health_spend", "HIV and STD spending as a share of all health spending", "percent",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "WHO GHED dis11_che. How much of everything a country spends on health "
                  "goes to HIV and STDs, which says how large a hole an HIV funding cut "
                  "leaves in the health system as a whole."),
    IndicatorSpec("hiv_std_share_of_external_health_spend",
                  "HIV and STD spending as a share of all external health spending", "percent",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "WHO GHED dis11_ext_ext. How much of the donor health money reaching a "
                  "country is HIV money, and therefore how much of that country's donor "
                  "health financing an HIV withdrawal takes with it. The exposure measure "
                  "in this group."),
    IndicatorSpec("hiv_std_govt_share_of_govt_health_spend",
                  "Government HIV and STD spending as a share of government health spending", "percent",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "WHO GHED dis11_g_gghed. The country's own commitment measured against "
                  "its own health budget, so a government replacing withdrawn donor money "
                  "raises this even when its total health budget does not move."),

    # -- national AIDS spending assessments, in the currency the assessment prints ---------
    # Every financing indicator above is USD, because every source above either publishes in
    # USD or publishes a USD conversion beside its own currency. A national AIDS spending
    # assessment does neither. Cameroon's 2016-2017 and 2020-2021 assessments print every
    # figure in CFA francs and state no exchange rate anywhere, and the panel holds no
    # exchange-rate series to convert them with: `world_bank.py` pulls SP.POP.TOTL and
    # SH.DYN.AIDS.ZS and nothing else. Picking a rate from outside the document would put a
    # number in the panel that no source published and that no reader could trace, which is
    # the one thing this panel does not do.
    #
    # So an assessment's levels enter in the assessment's own currency under these `_lcu`
    # ids, with extra.currency carrying the ISO 4217 code (XAF for Cameroon) and
    # extra.currency_note saying no rate was published. The ids are separate from the USD
    # series above and MUST NEVER be pooled with them or summed into them. `LCU` is the World
    # Bank's own term for a local currency unit, which is the vocabulary the conversion would
    # use if one is added later: PA.NUS.FCRF is LCU per US dollar.
    #
    # Converting later is a derived step over two traceable panel series, the LCU level and
    # the published exchange rate, which is a different and safer thing from a connector
    # applying a rate it chose itself. Adding PA.NUS.FCRF to `world_bank.py` is what that
    # would need, and is Jason's call because it changes an existing connector's output for
    # every country in the panel.
    #
    # Two things to know about these ids downstream. `site/charts.py` formats an unrecognised
    # unit as a plain grouped number with no currency symbol, which is right for a franc
    # level. `reconcile.py` has no materiality floor for LCU (MATERIALITY_DEFAULT is 0.0), so
    # if a second source ever publishes the same country's assessment in the same currency, a
    # one-franc difference would read as a disagreement; a floor would have to be added then.
    IndicatorSpec("hiv_expenditure_total_lcu",
                  "HIV expenditure, all sources, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The assessment's headline total, all funding sources and all "
                  "interventions. The local-currency counterpart of hiv_expenditure_total, "
                  "never pooled with it."),
    IndicatorSpec("hiv_expenditure_international_lcu",
                  "International HIV expenditure, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "All external money as the assessment accounts for it. The parent of the "
                  "three donor series below, which sum to it exactly in both Cameroon "
                  "assessments."),
    IndicatorSpec("hiv_expenditure_us_gov_lcu",
                  "United States government HIV expenditure, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "What the country's own assessment attributes to the United States, "
                  "against pepfar_expenditure, which is the donor's account of the same "
                  "money over a US fiscal year."),
    IndicatorSpec("hiv_expenditure_global_fund_lcu",
                  "Global Fund HIV expenditure, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "What the country's own assessment attributes to the Global Fund, against "
                  "global_fund_hiv_disbursements, which is the donor's account of the same "
                  "money."),
    IndicatorSpec("hiv_expenditure_other_bilateral_lcu",
                  "Other bilateral HIV expenditure, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Bilateral donors other than the United States, the place any backfill by "
                  "other governments would appear. France and Germany in the Cameroon "
                  "assessments."),
    IndicatorSpec("domestic_hiv_spend_lcu",
                  "Domestic public HIV expenditure, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The country's own public money, the series that has to rise if a "
                  "government replaces withdrawn donor funding. The local-currency "
                  "counterpart of domestic_hiv_spend."),
    IndicatorSpec("hiv_expenditure_domestic_private_lcu",
                  "Private HIV expenditure, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Domestic private money, including what households pay themselves, so a "
                  "rise here beside a fall in the international series is the cost-shifting "
                  "signal."),
    IndicatorSpec("hiv_spend_treatment_lcu",
                  "HIV spending on treatment, care and support, national currency", "LCU",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The one intervention line that is defined the same way across Cameroon's "
                  "two assessments, both of which print a single 'Soins et traitement' "
                  "total. The other intervention lines are refused: see cameroon_nasa.py."),
    IndicatorSpec("hiv_expenditure_international_share_pct",
                  "International share of HIV expenditure", "percent",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Donor money as a share of all HIV spending, recomputed from the levels "
                  "and so free of currency. The exposure measure a reader of a funding-cuts "
                  "panel wants, and the only financing figure from a local-currency "
                  "assessment that is comparable across countries without an exchange rate."),

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
    #
    # The HHS series was `external_hiv_oda_us_cdc` until 27 September 2026, when the connector
    # moved off the hand-downloaded CSV and onto the IATI XML the same agencies publish on
    # Amazon S3. The CSV carried a managing SUB-agency column and the XML carries none, so CDC
    # can no longer be separated from the rest of the department. CDC is 38.5bn USD of HHS's
    # 43.1bn, so the two are close and they are not the same measurement.
    IndicatorSpec("external_hiv_oda_us_usaid", "US HIV disbursements managed by USAID", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The arm that was dismantled. Read alongside _state before calling a fall a cut."),
    IndicatorSpec("external_hiv_oda_us_hhs", "US HIV disbursements managed by Health and Human Services", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "The whole department, which is CDC plus NIH and HRSA, because the IATI files "
                  "carry no sub-agency. Close to but not identical with PEPFAR's own 'HHS/CDC' "
                  "label. The within-country comparison arm: HHS continued while USAID did not."),
    IndicatorSpec("external_hiv_oda_us_state", "US HIV disbursements managed by the State Department", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Near zero before FY2025 and then the destination of USAID's global health "
                  "programmes (STATE/GHSD). Reclassification, not new money."),
    IndicatorSpec("external_hiv_oda_us_other_agency", "US HIV disbursements managed by other US agencies", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "DOD, Peace Corps, MCC, DOL and the African Development Foundation, pooled so "
                  "the four series still sum to the country total. NIH and HRSA left this series "
                  "for _hhs when the CDC split went."),

    IndicatorSpec("global_fund_hiv_disbursements", "Global Fund HIV disbursements to the country", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Three measures of the same money, not three independent measures, so filter "
                  "on source_id before summing. OECD CRS (donor 9OTH012) is the Global Fund's "
                  "disbursement as the "
                  "donor community records it, unaids_gam_expenditure is what the country's "
                  "own expenditure return attributes to the Global Fund, and iati is the Global "
                  "Fund's own transaction-level filing to the IATI registry, which arrives within "
                  "weeks instead of the CRS's 14 months and is the only one of the three that can "
                  "see the 2025 collapse. Key for the "
                  "backfill question (does the Global Fund rise as US/PEPFAR funding is cut?). "
                  "All 1,491 Global Fund activity "
                  "identifiers in the panel's iati rows match a grant in the Global Fund's own "
                  "grant table, counted on 1 October 2026, so the iati reading and the CRS "
                  "donor-9OTH012 reading are the same institution's filing reaching the panel "
                  "by two routes. reconcile.py classifies the pair as derived for that reason, "
                  "and a reader must not treat agreement between the two as corroboration."),

    # An allocation is not a disbursement, and this series must never be added to the one
    # above. The Global Fund tells a country at the start of a three-year cycle what the
    # country may apply for, and the disbursement series records what the Global Fund then
    # moved, so the two are the same money counted at two different moments. One row carries
    # one WHOLE CYCLE and `year` holds the cycle's first year, because dividing an allocation
    # by three would invent an annual profile the Global Fund does not publish and writing the
    # cycle figure onto all three years would triple the money. Anyone summing this series
    # across years is summing cycles.
    IndicatorSpec("global_fund_hiv_allocation_cycle",
                  "Global Fund HIV allocation for a whole three-year cycle, not an annual figure",
                  # The unit says what one row covers, and the unit matches the string the
                  # connector writes onto every row, so the site and the panel cannot disagree
                  # about whether a figure is annual.
                  "USD per three-year allocation cycle",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "CommunicatedAllocation_ReferenceRate from the Global Fund Data Service, the "
                  "only one of the service's 16 financial datasets that reaches both a country "
                  "and a disease component. A forward commitment, which no other source in this "
                  "panel states at country level for the 2026-2028 cycle, and 2026-2028 is the "
                  "first Global Fund allocation set after the PEPFAR and USAID withdrawals. The "
                  "unit is held constant at 'USD per three-year allocation cycle' so the four "
                  "cycles of a country stay one series, and extra.allocation_period names the "
                  "cycle. Do not add to global_fund_hiv_disbursements."),

    # -- the rest of the external money, transaction by transaction (iati only) ---------
    # Three series that OECD CRS also covers, measured a different way. CRS is an annual return
    # filed by official donors about 14 months after the year it describes, and the 2020 purpose
    # code change moves money between codes in a way that no series read straight across the
    # break can survive. IATI publishers file the day the money moved, within weeks, so a
    # collapse that began in January 2025 is visible in IATI and is not yet in CRS at all.
    #
    # NEITHER external_hiv_bilateral_other NOR external_hiv_multilateral_other MAY BE ADDED TO
    # external_hiv_oda_total. The three measure the same flows from different filings, so adding
    # them counts the same disbursement twice. Every row carries do_not_add_to in `extra` as well.
    #
    # Both series exclude money the panel already holds from the donor that supplied it: the
    # United States, whose eight IATI publishers are read and logged and never written because
    # foreign_assistance and OECD CRS donor USA already carry them, and the Global Fund, which
    # has its own series above. Each row's `extra.by_publisher` names every publisher that
    # contributed to it, because the panel's row key ends at source_id and one row per publisher
    # would be rejected as a duplicate.
    IndicatorSpec("external_hiv_bilateral_other",
                  "External HIV financing from governments other than the United States (IATI)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "IATI purpose 13040, publishers whose reporting-org type is 10, 11 or 15, so "
                  "governments, local governments and other public sector bodies. Sweden, the "
                  "FCDO, Germany, Canada, Australia, the Netherlands, Switzerland and Ireland are "
                  "the largest. Do not add to external_hiv_oda_total."),
    IndicatorSpec("external_hiv_multilateral_other",
                  "External HIV financing from multilateral bodies other than the Global Fund (IATI)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "IATI purpose 13040, publishers whose reporting-org type is 40, with the Global "
                  "Fund removed to its own series. WHO, UNAIDS, UNICEF and UNDP dominate. Much of "
                  "this money is spent on behalf of a bilateral donor or the Global Fund, and an "
                  "activity naming either as a funder is excluded, so the series is smaller than "
                  "the publishers' own totals by design. WHO and UNAIDS strategy and coordination "
                  "lines are kept and flagged, because a country office's technical support is "
                  "money reaching that country. Do not add to external_hiv_oda_total."),
    IndicatorSpec("external_hiv_foundation",
                  "External HIV financing from private foundations (IATI)", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "IATI purpose 13040, publishers whose reporting-org type is 60, which in the HIV "
                  "corpus is overwhelmingly the Gates Foundation. HELD UNWRITTEN until it is "
                  "settled whether the OECD CRS all-official-donor total already contains Gates "
                  "money and from which year, because a series that double counts before one year "
                  "and not after is worse than no series. The connector reads and logs the money "
                  "on every run, so the totals are known before the hold is lifted."),

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
                  "Two independent measures of the same money, so filter on source_id before "
                  "summing, and note that the three agency series below partition only the "
                  "pepfar_expenditure source. PEPFAR's own figure is reported spend for the "
                  "implementation year, and a FLOOR where reporting is incomplete (see "
                  "extra.expenditure_ceiling); unaids_gam_expenditure is what the country's "
                  "own expenditure return attributes to PEPFAR, over the country's "
                  "expenditure year rather than the US fiscal year."),
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

    # -- what PEPFAR planned to buy (PEPFAR_OU_Commodities_Procurements, COP18 to COP24) --------
    # Planned budget for commodities in the implementation years 2019 to 2025, from plans written
    # a year ahead, so every figure predates the January 2025 freeze and none shows the 2025 cut.
    # The three category series are parts of the total and must never be added to the total.
    # A category series is zero, marked category_not_in_plan, where the plan has a total and
    # lists nothing in the category.
    # Quantities are not emitted, because the unit a quantity counts changes between years.
    IndicatorSpec("pepfar_commodity_budget", "PEPFAR planned commodity procurement, like for like", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "ARVs, rapid test kits, laboratory goods, essential medicines, VMMC kits and TB "
                  "drugs. Excludes logistics, quality assurance and procurement management, which "
                  "the file books in some years only, and condoms, whose budget records which plan "
                  "carries the cost rather than what was bought. A plan, not spending."),
    IndicatorSpec("pepfar_arv_budget", "PEPFAR planned procurement of antiretroviral drugs", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Treatment, infant prophylaxis and, from 2020, PrEP, whose amount is in "
                  "extra.prep_budget. Part of pepfar_commodity_budget. Zero where the plan lists "
                  "no ARV."),
    IndicatorSpec("pepfar_rtk_budget", "PEPFAR planned procurement of rapid test kits", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "HIV tests, self-tests, recency tests and tests for conditions other than HIV. "
                  "Part of pepfar_commodity_budget."),
    IndicatorSpec("pepfar_lab_budget", "PEPFAR planned procurement of laboratory commodities", "USD",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Viral load, early infant diagnosis, CD4 and TB reagents, sample collection, "
                  "equipment and servicing. Part of pepfar_commodity_budget."),

    # -- the staff PEPFAR paid for (HRH_Inventory_Public_Dataset, fiscal year 2025) ------------
    # One year only, and the year runs from October 2024 to September 2025, so the series give
    # the level of PEPFAR-funded staffing in the year of the cut and cannot show a change.
    # PEPFAR-funded staff only, never the national health workforce. The headcount column is
    # not emitted, because one person split between programmes may sit on several rows.
    IndicatorSpec("pepfar_hrh_spend", "PEPFAR spend on staff, human resources for health inventory",
                  "USD", SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Pay of clinical, ancillary and other staff reported by implementing partners. "
                  "Not the partner file's Human Resources for Health column, which is above-site "
                  "workforce strengthening and not staff pay."),
    IndicatorSpec("pepfar_hrh_fte", "PEPFAR-funded staff, full-time equivalents", "count",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Every staff category and interaction type. The headcount is in "
                  "extra.individual_count and may count one person more than once."),
    IndicatorSpec("pepfar_hrh_fte_service_delivery",
                  "PEPFAR-funded staff delivering services, full-time equivalents", "count",
                  SourceType.EXPENDITURE_ACCOUNT, "financing",
                  "Rows whose interaction type is Service Delivery. Part of pepfar_hrh_fte, never "
                  "to be added to pepfar_hrh_fte. Zero, marked no_service_delivery_rows, where "
                  "the inventory lists staff and no service-delivery staff."),
]}


def unit_for(canonical_id: str, default: str = "") -> str:
    spec = CANONICAL_INDICATORS.get(canonical_id)
    return spec.unit if spec else default
