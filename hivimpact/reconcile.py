"""
Reconciliation layer — source-aware triangulation over the assembled panel.

The panel deliberately keeps every source's own figure instead of collapsing to one "best"
value. This module compares them, and its central design decision is that **a comparison is
worthless until you know what kind of comparison it is**.

Three relationships exist between two sources reporting the same country-indicator-year:

  derived      Both publish the same underlying estimate. UNAIDS, WHO GHO and the World Bank
               largely republish the same Spectrum output, so agreement between them is
               arithmetic, not corroboration. Counting these as triangulation would
               manufacture confidence the data does not support.
  subset       One measures a part of what the other measures (PEPFAR reports its own
               programme footprint, not the national total). A gap here is expected by
               construction and is not a contradiction.
  independent  Separate measurement systems, with nothing in common upstream (a national
               programme register against a modelled estimate; OECD donor reporting against
               US self-reporting). Only here does a divergence carry information.

A classification is inferred from the data wherever the provenance of the two figures is not
known, and declared in DECLARED_RELATIONSHIPS wherever the provenance is known, because the
numbers alone cannot say whether two figures come from one accounting record. Every
classification is written out with the evidence behind it (cell count, median relative
difference, agreement share, direction consistency) and with a `basis` column saying whether
the verdict was declared or inferred, so the call can be audited or overridden.

Outputs (data/panel/):
  reconciliation_pairs.csv  one row per indicator x source-pair: the relationship map
  reconciliation_cells.csv  cell-level comparisons for INDEPENDENT pairs, divergences flagged
  reconciliation_summary.txt  headline counts

Scope: national rows only (admin1 == ""), matched on country, indicator, population group,
sex, age group and year. Sub-national rows are excluded so regional detail is never compared
against national totals.
"""
from __future__ import annotations

import itertools
import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

log = logging.getLogger("hivimpact")

# --- classification thresholds (explicit, and reported alongside every verdict) ------------
DERIVED_MEDIAN_RELDIFF = 0.01   # near-identical on the typical cell
DERIVED_AGREE_SHARE = 0.90      # ...and near-identical almost everywhere
DERIVED_AGREE_BAND = 0.02
SUBSET_MEDIAN_RATIO = 0.90      # one side systematically smaller
SUBSET_DIRECTION_SHARE = 0.90   # ...consistently, not sporadically
MIN_CELLS = 3                   # below this, decline to classify
DIVERGENCE_FLAG = 0.10          # |relative difference| worth surfacing on an independent pair

# A relative difference is only meaningful when both figures are positive and materially
# sized. Funding series contain zeros, reversals (negative disbursements) and trivial sums;
# comparing $49,423 against $348, or +$14m against -$25m, produces a large ratio that carries
# no information. Such cells are separated out instead of counted as disagreements.
MATERIALITY = {"USD": 1_000_000.0, "count": 100.0, "percent": 1.0}
MATERIALITY_DEFAULT = 0.0

_KEY = ["country_iso3", "indicator_id", "population_group", "sex", "age_group", "year"]

# --- declared provenance -------------------------------------------------------------------
# Item 27. `classify_pairs` reads the relationship off the numbers, and the numbers cannot say
# where a figure came from. Two publications of one accounting record that differ in scope or
# in dating disagree widely enough to fall through the derived and subset tests and land on
# `independent`, which is the verdict that tells a reader the divergence carries information.
# On the panel of 30 September 2026 the Global Fund's own two returns did exactly that, and
# 2,002 cells were counted as independent evidence of a disagreement between one reporter and
# itself.
#
# So a pair whose provenance is known is declared here and read instead of inferred. The key
# is the indicator and the two source identifiers in the order `build_comparisons` sorts them
# into, and the entry carries the reason in prose beside the verdict. Every classified pair
# also reports whether the verdict was declared or inferred, so that a reader can tell one
# from the other without reading this file.
#
# Only what is known goes in. The two `unaids_gam_expenditure` pairs look independent and have
# not been established as independent, so no entry claims either way and both keep an inferred
# verdict until Adrian Smith and the UNAIDS documentation settle the question.
DECLARED_RELATIONSHIPS: Dict[tuple, tuple] = {
    ("global_fund_hiv_disbursements", "iati", "oecd_crs"): (
        "derived",
        "The Global Fund publishes the same disbursements to the IATI registry and to the "
        "OECD Creditor Reporting System, where the Global Fund is reporter 9OTH012, so the "
        "iati and oecd_crs figures for this indicator are two publications of one accounting "
        "record and agreement between them is arithmetic. The two figures differ because the "
        "IATI reading dates money by transaction date while the OECD CRS reading dates money "
        "by reporting year, and because the IATI connector counts the whole value of an H or "
        "C grant where the OECD CRS return carries purpose code 13040 alone. A difference "
        "produced by two treatments of one record is not two measurements disagreeing.",
    ),
    # RESUME.md item 46. Read from data/panel/hiv_panel.csv on 2 October 2026.
    ("on_art_count", "ne_annuaire", "who_gho"): (
        "derived",
        "The Niger health yearbook's national count of people on ART equals the WHO GHO figure "
        "exactly in seven of 12 years from 2013 to 2024, and an exact match on a five-digit "
        "count cannot come from two separate counts. Both figures are the one count of the "
        "national HIV and hepatitis programme (PNLSH), printed in the health ministry's "
        "yearbook and reported to WHO, so agreement is duplication and not corroboration. "
        "RESUME.md item 46 records as findings the years the two publications differ, with "
        "WHO GHO lower in 2016, 2017, 2021 and 2022 and higher by 14 in 2024.",
    ),
    ("on_art_count", "global_fund", "ne_annuaire"): (
        "derived",
        "The Global Fund's reported result for Niger equals the Niger health yearbook's national "
        "count of people on ART exactly in five of the eight years both report from 2017 to "
        "2024, so both figures are the one count of the national HIV and hepatitis programme "
        "(PNLSH), printed in the health ministry's yearbook and reported to the Global Fund as "
        "a grant result. The "
        "Global Fund figure is lower by 4,426 in 2018, higher by 842 in 2022 and lower by 12 in "
        "2024, and RESUME.md item 46 records those three years as findings.",
    ),
    ("on_art_count", "ne_annuaire", "unaids_aidsinfo"): (
        "derived",
        "The UNAIDS AIDSinfo count of people on ART in Niger is the WHO GHO count rounded to the "
        "nearest thousand in every year from 2013 to 2024, and the WHO GHO count is the Niger "
        "health yearbook's national count in seven of those 12 years. The UNAIDS figure is "
        "therefore the national programme's one count, rounded, and agreement with the yearbook "
        "is duplication and not corroboration.",
    ),
    # RESUME.md item 47. Read from data/panel/hiv_panel.csv on 2 October 2026.
    ("pmtct_arv_count", "gn_annuaire", "unaids_aidsinfo"): (
        "derived",
        "The Guinea statistics yearbook's 2023 national count of pregnant women on ARVs, 3,802, "
        "equals the UNAIDS AIDSinfo figure exactly, and an exact four-digit match cannot come "
        "from two separate counts, so both figures are the national health information "
        "system's one count. The evidence is thinner than for Niger, with three shared years, "
        "and the yearbook sits 6 per cent above UNAIDS in 2022 and 16 per cent above UNAIDS in "
        "2024. RESUME.md item 47 records both gaps as findings, because declaring the pair "
        "derived keeps the gaps out of the divergence report.",
    ),
    ("pmtct_arv_count", "gn_annuaire", "who_gho"): (
        "derived",
        "WHO GHO prints the same Guinea count of pregnant women on ARVs as UNAIDS AIDSinfo in "
        "every Guinea year, and the Guinea statistics yearbook's 2023 national count, 3,802, "
        "equals the WHO GHO figure exactly. The WHO GHO pair therefore carries the same single "
        "count as the UNAIDS pair, with the same 2022 and 2024 gaps recorded in RESUME.md item "
        "47. The Global Fund pair is left inferred, because the Global Fund's Guinea results "
        "match the yearbook in no year.",
    ),
    # Connector 29. Read from the UNICEF SDMX answer of 14 October 2026.
    ("pmtct_coverage_pct", "unaids_aidsinfo", "unicef_hiv"): (
        "derived",
        "UNICEF republishes the UNAIDS estimates, and the DATA_SOURCE label of every UNICEF "
        "PMTCT coverage value names the UNAIDS 2026 estimates round, while the AIDSinfo exports "
        "behind unaids_aidsinfo hold the 2025 round and stop at 2024. The UNICEF figure and "
        "the AIDSinfo figure come out of the same UNAIDS model, and a difference between the "
        "UNICEF figure and the AIDSinfo figure is a revision between rounds and not two "
        "measurements disagreeing. Read on 14 October 2026 against the AIDSinfo exports saved "
        "on 18 July 2026 (hivimpact/connectors/unicef_hiv.py).",
    ),
    ("vertical_transmission_pct", "unaids_aidsinfo", "unicef_hiv"): (
        "derived",
        "UNICEF republishes the UNAIDS estimates, and the DATA_SOURCE label of every UNICEF "
        "vertical transmission value names the UNAIDS 2026 estimates round, while the "
        "AIDSinfo exports behind unaids_aidsinfo hold the 2025 round and stop at 2024. The "
        "UNICEF figure and the AIDSinfo figure come out of the same UNAIDS model, and a "
        "difference between the UNICEF figure and the AIDSinfo figure is a revision between "
        "rounds and not two measurements disagreeing. Read on 14 October 2026 against the "
        "AIDSinfo exports saved on 18 July 2026 (hivimpact/connectors/unicef_hiv.py).",
    ),
}
# Ruling R17 of research/rulings_2026-10-15.md. The UNICEF age-group counts read on 15 October
# 2026 against the AIDSinfo age-group exports saved on 18 July 2026.
DECLARED_RELATIONSHIPS.update({
    (ind, "unaids_aidsinfo", "unicef_hiv"): (
        "derived",
        "UNICEF republishes the UNAIDS estimates by age group, and the DATA_SOURCE label of every "
        "UNICEF value names the UNAIDS 2026 estimates round, while the AIDSinfo age-group exports "
        "behind unaids_aidsinfo hold the 2025 round and stop at 2024. The UNICEF figure and the "
        "AIDSinfo figure come out of the same UNAIDS model, and a difference between the UNICEF "
        "figure and the AIDSinfo figure is a revision between rounds and not two measurements "
        "disagreeing. Over the ages 0 to 14, 10 to 19 and 15 to 24, the 5,785 shared values with "
        "no censoring in UNICEF or AIDSinfo differ by a median of 8.3 per cent, and Colombia's "
        "new infections at ages 10 to 19 read 2,400 for 2012 in the 2026 round against 620 in "
        "the 2025 round, with the all-ages count at 11,000 in the 2025 round and the 2026 round "
        "(hivimpact/connectors/unicef_hiv.py).",
    )
    for ind in ("plhiv", "new_infections", "aids_deaths")
})
# Ruling R19 of research/rulings_2026-10-15.md. Read from data/panel/hiv_panel.csv on 15 October
# 2026.
DECLARED_RELATIONSHIPS.update({
    (ind, "unaids_aidsinfo", "who_gho"): (
        "derived",
        "WHO GHO publishes the UNAIDS/WHO modelled estimates under HIV_0000000001, "
        "HIV_0000000026, HIV_0000000006, HIV_ARTCOVERAGE, HIV_STATUSKNOWNHIV, "
        "HIV_VIRALLOADSUPPRESSEDART and HIV_VIRALLOADSUPPRESSED, the same estimates AIDSinfo "
        "publishes (hivimpact/connectors/who_gho.py). In the panel of 15 October 2026 WHO GHO "
        "carries a 2025 value in all seven estimate series and every AIDSinfo export stops at "
        "2024, so WHO GHO holds a later annual round of the UNAIDS/WHO estimates, and a new round "
        "re-estimates every earlier year. Over the 3,146 uncensored plhiv values AIDSinfo and WHO "
        "GHO share, the median ratio of the AIDSinfo value to the WHO GHO value is 1.0. A "
        "difference between the WHO GHO figure and the AIDSinfo figure is a difference between "
        "two rounds of the UNAIDS estimates and not two measurements disagreeing.",
    )
    for ind in ("plhiv", "new_infections", "aids_deaths", "art_coverage_pct", "know_status_pct",
                "viral_suppression_pct", "community_viral_suppression_pct")
})
_THEMBISA_REASON = (
    "South Africa submits HIV estimates from the Thembisa model to UNAIDS in place of Spectrum. "
    "Leigh Johnson of the University of Cape Town, the lead developer of Thembisa, and Yogan "
    "Pillay, previously a deputy director-general of the South African Department of Health, "
    "are quoted on the Thembisa submission by Bhekisisa and Daily Maverick in reports of 23 "
    "July 2024. The UNAIDS figures for South Africa, and the UNICEF, WHO GHO and World Bank "
    "figures republishing the UNAIDS figures, therefore come out of the Thembisa model behind "
    "za_thembisa. In the panel of 15 October "
    "2026 the know_status_pct values of AIDSinfo and za_thembisa differ by a median of 0.5 per "
    "cent over 16 years. A difference between za_thembisa and a UNAIDS figure for South Africa "
    "is a difference between two publications of the Thembisa estimates and not two "
    "measurements disagreeing. The UNAIDS feature story of 28 June 2019 on the South African "
    "model sits on unaids.org, which answers 403 to the project, and was not read."
)
DECLARED_RELATIONSHIPS.update({
    (ind, src, "za_thembisa"): ("derived", _THEMBISA_REASON)
    for ind, sources in {
        "plhiv": ("unaids_aidsinfo", "unicef_hiv", "who_gho"),
        "new_infections": ("unaids_aidsinfo", "unicef_hiv", "who_gho"),
        "aids_deaths": ("unaids_aidsinfo", "unicef_hiv", "who_gho"),
        "hiv_prevalence_15_49": ("unaids_aidsinfo", "world_bank"),
        "art_coverage_pct": ("unaids_aidsinfo", "who_gho"),
        "know_status_pct": ("unaids_aidsinfo", "who_gho"),
        "viral_suppression_pct": ("unaids_aidsinfo", "who_gho"),
        "community_viral_suppression_pct": ("unaids_aidsinfo", "who_gho"),
    }.items()
    for src in sources
})
# Ruling R20 of research/rulings_2026-10-15.md. Read from data/panel/hiv_panel.csv on 15 October
# 2026.
_GAM_POSITIVITY_REASON = (
    "AIDSinfo, WHO GHO and the WHO HTS Dashboard (who_hts) publish the HIV test positivity every "
    "country reports to Global AIDS Monitoring, and who_hts reads the Global AIDS Monitoring "
    "editions (hivimpact/connectors/who_hts.py). AIDSinfo, WHO GHO and who_hts round the "
    "percentage to different precision. In the panel of 15 October 2026 the AIDSinfo value is "
    "the WHO GHO value rounded to two significant figures in 221 of 321 shared country-years, "
    "the AIDSinfo value equals the who_hts value in 240 of 399 shared country-years, and who_hts "
    "and WHO GHO agree exactly on the national test total in all 325 country-years compared."
)
DECLARED_RELATIONSHIPS.update({
    ("on_art_count", "unaids_aidsinfo", "who_gho"): (
        "derived",
        "AIDSinfo and WHO GHO publish the number on antiretroviral treatment every country reports "
        "to Global AIDS Monitoring. AIDSinfo rounds the count to two significant figures and "
        "prints a small count as a bound (for example <500), and WHO GHO publishes the count "
        "unrounded under HIV_0000000009. In the panel of 15 October 2026 the AIDSinfo value is the "
        "WHO GHO value rounded to two significant figures in 1,602 of 2,030 shared country-years, "
        "and in 238 more the AIDSinfo value is a bound holding the WHO GHO value.",
    ),
    ("pmtct_arv_count", "unaids_aidsinfo", "who_gho"): (
        "derived",
        "AIDSinfo and WHO GHO publish the number of pregnant women living with HIV receiving "
        "antiretroviral medicines to prevent vertical transmission, as every country reports the "
        "number to Global AIDS Monitoring. In the panel of 15 October 2026 the AIDSinfo value "
        "equals the WHO GHO value in 1,162 of 1,515 shared country-years and in 111 of the 204 "
        "shared country-years at 10,000 or more, where the AIDSinfo and WHO GHO counts are "
        "unrounded.",
    ),
    ("pregnant_women_hiv", "unaids_aidsinfo", "who_gho"): (
        "derived",
        "WHO GHO publishes the UNAIDS/WHO modelled estimate of pregnant women living with HIV under "
        "HIV_0000000021, the estimate AIDSinfo publishes as pregnant women needing antiretroviral "
        "medicines. In the panel of 15 October 2026 WHO GHO carries a 2025 value for 90 countries "
        "and the AIDSinfo export stops at 2024, so WHO GHO holds a later annual round of the "
        "estimate, and over the 759 uncensored values AIDSinfo and WHO GHO share, the median "
        "ratio of the AIDSinfo value to the WHO GHO value is 0.98.",
    ),
    ("hiv_test_positivity_pct", "unaids_aidsinfo", "who_gho"): ("derived", _GAM_POSITIVITY_REASON),
    ("hiv_test_positivity_pct", "unaids_aidsinfo", "who_hts"): ("derived", _GAM_POSITIVITY_REASON),
    ("hiv_test_positivity_pct", "who_gho", "who_hts"): ("derived", _GAM_POSITIVITY_REASON),
})
# Ruling R31 of research/rulings_2026-10-15.md. Read from data/panel/hiv_panel.csv and from the
# Geostat PxWeb API on 20 October 2026.
DECLARED_RELATIONSHIPS.update({
    ("notified_hiv_cases", "ge_geostat", "who_europe_hfa"): (
        "derived",
        "Geostat republishes the Georgian HIV case register, and the SOURCE field of the Geostat "
        "morbidity table names the Ministry of Internally Displaced Persons From The Occupied "
        "Territories, Labour, Health and Social Affairs of Georgia. The NOTEX field of the Geostat table says Georgia joined the ECDC HIV/AIDS surveillance "
        "system (TESSy) in 2008 and 2009 and revised the earlier Georgian data, and measure "
        "HFA_350 behind who_europe_hfa holds the new HIV diagnoses of the joint ECDC and WHO "
        "Europe surveillance, which Georgia reports through TESSy. The Geostat count equals the "
        "HFA_350 count in every year from 2009 to 2019 and differs by one to seven cases for "
        "2002 to 2008, the years Geostat revised. A difference between ge_geostat and "
        "who_europe_hfa is a revision of one register and not two measurements disagreeing "
        "(hivimpact/connectors/country/georgia_geostat.py).",
    ),
})
# Ruling R35 of research/rulings_2026-10-15.md. Read from Table 1 of the 2025 joint ECDC and WHO
# Europe report and from the WHO/Europe Data Warehouse answers of 20 October 2026.
DECLARED_RELATIONSHIPS.update({
    ("notified_hiv_cases", "ecdc_hiv_report", "who_europe_hfa"): (
        "derived",
        "ecdc_hiv_report reads Table 1 of the joint ECDC and WHO Europe report HIV/AIDS "
        "surveillance in Europe 2025 (2024 data), and measure HFA_350 behind who_europe_hfa "
        "reproduces Table 1 of the 2020 edition of the same report, so ecdc_hiv_report and "
        "who_europe_hfa read the case reports every country sends to The European Surveillance "
        "System (TESSy), five editions apart. Over the 225 country-years for 2015 to 2019 in "
        "ecdc_hiv_report and who_europe_hfa, the counts are equal in 123, the HFA_350 count is "
        "lower in 76 and higher in 26, and the HFA_350 counts add to 99 per cent of the 2025 "
        "counts. The largest gaps are Portugal for 2017 to 2019, Spain for 2017 and the "
        "Netherlands for 2019, and grow toward the latest year of the 2020 edition, the pattern "
        "of late case reports, and the 2020 edition adjusts the 2019 counts of the Netherlands "
        "and Portugal for reporting delay by factors of 1.18 and 1.73. A difference between "
        "ecdc_hiv_report and who_europe_hfa is a later revision of one count and not two "
        "measurements disagreeing (hivimpact/connectors/ecdc_hiv_report.py).",
    ),
})
# Ruling R36 of research/rulings_2026-10-15.md. Read from Table 13 of the 2025 joint report and
# from measure HFA_348 of the WHO/Europe Data Warehouse answers of 20 October 2026.
DECLARED_RELATIONSHIPS.update({
    ("aids_cases_reported", "ecdc_hiv_report", "who_europe_hfa"): (
        "derived",
        "ecdc_hiv_report reads Table 13 (AIDS diagnoses) of the joint ECDC and WHO Europe report "
        "HIV/AIDS surveillance in Europe 2025 (2024 data), and measure HFA_348 behind "
        "who_europe_hfa reproduces the AIDS table of the 2020 edition of the same report, so "
        "ecdc_hiv_report and who_europe_hfa read the AIDS case reports every country sends to "
        "TESSy, five editions apart. Over the 190 country-years for 2015 to 2019 that "
        "ecdc_hiv_report and who_europe_hfa both carry after ruling R36, the counts are equal in "
        "120, the HFA_348 count is lower in 65 and higher in five, and the HFA_348 counts add "
        "to 98 per cent of the 2025 counts, from 99 per cent for 2015 to 96 per cent for 2019. "
        "The largest gaps are the Netherlands, Portugal, Israel and France for 2019, the pattern "
        "of late case reports, and the five higher HFA_348 counts exceed the 2025 counts by one "
        "to three cases. A difference between ecdc_hiv_report and who_europe_hfa is a later "
        "revision of one count and not two measurements disagreeing "
        "(hivimpact/connectors/ecdc_hiv_report.py). Never compare aids_cases_reported with "
        "aids_deaths, new_infections or notified_hiv_cases.",
    ),
})
# Ruling R38 of research/rulings_2026-10-15.md. Read from the aidscenter.kg situation report of
# 1 July 2026 and from the panel copy of measure HFA_350 on 20 October 2026.
DECLARED_RELATIONSHIPS.update({
    ("notified_hiv_cases", "kg_aidscenter", "who_europe_hfa"): (
        "derived",
        "kg_aidscenter reads the Kyrgyz HIV case register as the Republican Centre for the "
        "Control of Blood-borne Viral Hepatitis and HIV prints the register in the situation "
        "report of 1 July 2026, citizens plus foreign citizens, and measure HFA_350 behind "
        "who_europe_hfa holds the new HIV diagnoses Kyrgyzstan reports from the same register "
        "to the joint ECDC and WHO Europe surveillance. For 2013 to 2019 the counts read 500 and "
        "503, 647 and 649, 619 and 653, 748 and 764, 836 and 840, 867 and 876, and 842 and 850, "
        "within two per cent in five of the seven years, and Table 1 of the 2025 joint report "
        "(ecdc_hiv_report) prints 619 for 2015 and 748 for 2016, the kg_aidscenter counts, so "
        "the larger gaps are revisions of the register after the 2020 edition. A difference "
        "between kg_aidscenter and who_europe_hfa is a revision of one register and not two "
        "measurements disagreeing (hivimpact/connectors/country/kyrgyzstan_aidscenter.py).",
    ),
})
# Ruling R39 of research/rulings_2026-10-15.md. Read from Table 5 of the 2025 annual HIV report of
# the Institute of Public Health of Montenegro, from the panel copy of measure HFA_350 and from
# Table 1 of the 2025 joint ECDC and WHO Europe report on 20 October 2026.
DECLARED_RELATIONSHIPS.update({
    ("notified_hiv_cases", "me_ijzcg", "who_europe_hfa"): (
        "derived",
        "me_ijzcg reads the Montenegrin HIV register as the Institute of Public Health of "
        "Montenegro prints the register in Table 5 of the 2025 annual HIV report, people "
        "registered with HIV in the year including people diagnosed abroad, and measure HFA_350 "
        "behind who_europe_hfa holds the new HIV diagnoses Montenegro reports from the same "
        "register to the joint ECDC and WHO Europe surveillance. The two sources print the same "
        "count in every year from 2001 to 2019. A difference between me_ijzcg and who_europe_hfa "
        "is a revision of one register and not two measurements disagreeing "
        "(hivimpact/connectors/country/montenegro_ijzcg.py).",
    ),
    ("notified_hiv_cases", "ecdc_hiv_report", "me_ijzcg"): (
        "derived",
        "Table 1 of the 2025 joint ECDC and WHO Europe report (ecdc_hiv_report) prints the new "
        "HIV diagnoses Montenegro reports from the national HIV register, and me_ijzcg reads the "
        "same register in Table 5 of the 2025 annual HIV report of the Institute of Public "
        "Health of Montenegro. The two sources print the same count in every year from 2015 to "
        "2024. A difference between ecdc_hiv_report and me_ijzcg is a revision of one register "
        "and not two measurements disagreeing (hivimpact/connectors/country/montenegro_ijzcg.py).",
    ),
})
# Ruling R44 of research/rulings_2026-10-15.md. Read from Tables 2.1 and 2.2 of Sankalak 2025 and
# from data/panel/hiv_panel.csv on 21 October 2026.
_NACO_REASON = (
    "The National AIDS Control Organisation (NACO) estimates the HIV burden of India with the "
    "Spectrum model UNAIDS recommends, and UNAIDS publishes the India estimates NACO submits. "
    "Table 2.1 of Sankalak 2025, the seventh edition of the yearly NACO status report, cites the "
    "UNAIDS 2025 estimates and the India HIV Estimates 2025. In the panel of 21 October 2026 the "
    "AIDSinfo figures for India of 2024 equal the in_naco figures of Table 2.2 rounded to two "
    "significant figures in all nine values and bounds of people living with HIV, new infections "
    "and AIDS-related deaths (2,600,000 against 2,561,161, 64,000 against 64,465 and 32,000 "
    "against 32,162), and the adult prevalence of 0.2 per cent of AIDSinfo and of the World Bank "
    "is the in_naco figure of 0.20 per cent rounded. The UNICEF, WHO GHO and World Bank figures "
    "republish the UNAIDS figures. A difference between in_naco and a UNAIDS figure for India is "
    "a difference between two publications or two rounds of the NACO estimates and not two "
    "measurements disagreeing (hivimpact/connectors/country/india_naco.py)."
)
DECLARED_RELATIONSHIPS.update({
    (ind, "in_naco", src): ("derived", _NACO_REASON)
    for ind, sources in {
        "plhiv": ("unaids_aidsinfo", "unicef_hiv", "who_gho"),
        "new_infections": ("unaids_aidsinfo", "unicef_hiv", "who_gho"),
        "aids_deaths": ("unaids_aidsinfo", "unicef_hiv", "who_gho"),
        "hiv_prevalence_15_49": ("unaids_aidsinfo", "world_bank"),
    }.items()
    for src in sources
})


def load_panel(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "admin1" in df.columns:                      # national totals only
        df = df[df["admin1"].fillna("") == ""]
    df = df[df["value"].notna()].copy()
    for c in ("population_group", "sex", "age_group"):
        if c in df.columns:
            df[c] = df[c].fillna("all")
    # Ruling R21 of research/rulings_2026-10-15.md. AIDSinfo and UNICEF print a small figure as
    # a bound (<100, <500, >95), and the connectors record the notation in extra.censored. The
    # column holds "<", ">" or an empty string.
    extra = df["extra"].fillna("").astype(str) if "extra" in df.columns else pd.Series("", index=df.index)
    df["censored"] = extra.str.extract(r'"censored":\s*"([<>])', expand=False).fillna("")
    return df


def build_comparisons(df: pd.DataFrame) -> pd.DataFrame:
    """Every pairwise comparison of two sources reporting the same cell."""
    rows: List[dict] = []
    for key, g in df.groupby(_KEY, dropna=False):
        g = g.drop_duplicates(subset=["source_id"], keep="first")
        if len(g) < 2:
            continue
        recs = g.set_index("source_id")["value"].to_dict()
        units = g.set_index("source_id")["unit"].to_dict()
        cens = g.set_index("source_id")["censored"].to_dict() if "censored" in g.columns else {}
        for a, b in itertools.combinations(sorted(recs), 2):
            va, vb = float(recs[a]), float(recs[b])
            denom = (abs(va) + abs(vb)) / 2.0
            rows.append({
                **dict(zip(_KEY, key)),
                "source_a": a, "source_b": b,
                "value_a": va, "value_b": vb,
                "unit": units.get(a) or units.get(b) or "",
                "abs_diff": va - vb,
                "rel_diff": (va - vb) / denom if denom > 0 else None,
                "ratio": (va / vb) if vb not in (0,) else None,
                "censored_a": cens.get(a, ""), "censored_b": cens.get(b, ""),
            })
    return pd.DataFrame(rows)


def classify_pairs(cmp_df: pd.DataFrame) -> pd.DataFrame:
    """Infer the relationship for each (indicator, source_a, source_b), with its evidence."""
    out: List[dict] = []
    if cmp_df.empty:
        return pd.DataFrame(out)
    for (ind, a, b), g in cmp_df.groupby(["indicator_id", "source_a", "source_b"]):
        n_all = len(g)
        # Ruling R21 of research/rulings_2026-10-15.md. A printed bound is not a point estimate,
        # so a comparison with a censored side stays out of the statistics the relationship is
        # read from, and n counts the comparisons with a point value from source a and from source b.
        if "censored_a" in g.columns:
            g = g[(g["censored_a"].fillna("") == "") & (g["censored_b"].fillna("") == "")]
        rel = g["rel_diff"].dropna().abs()
        n = len(g)
        med_rel = float(rel.median()) if len(rel) else None
        agree_share = float((rel <= DERIVED_AGREE_BAND).mean()) if len(rel) else None
        ratio = g["ratio"].dropna()
        med_ratio = float(ratio.median()) if len(ratio) else None
        # is one side consistently the smaller one?
        a_smaller = float((g["value_a"] < g["value_b"]).mean())
        direction = max(a_smaller, 1 - a_smaller)

        declared = DECLARED_RELATIONSHIPS.get((ind, a, b))
        if declared is not None:
            verdict = declared[0]
            why = f"declared, not inferred. {declared[1]}"
        elif n < MIN_CELLS:
            verdict, why = "insufficient", f"only {n} overlapping cell(s)"
        elif med_rel is not None and agree_share is not None \
                and med_rel <= DERIVED_MEDIAN_RELDIFF and agree_share >= DERIVED_AGREE_SHARE:
            verdict = "derived"
            why = (f"agree within {DERIVED_AGREE_BAND:.0%} on {agree_share:.0%} of {n} cells "
                   f"(median rel. diff {med_rel:.2%}); same underlying estimate, not corroboration")
        elif med_ratio is not None and direction >= SUBSET_DIRECTION_SHARE and (
                med_ratio <= SUBSET_MEDIAN_RATIO or (med_ratio and 1 / med_ratio <= SUBSET_MEDIAN_RATIO)):
            smaller = a if a_smaller >= 0.5 else b
            verdict = "subset"
            why = (f"{smaller} is smaller in {direction:.0%} of {n} cells "
                   f"(median ratio a/b {med_ratio:.2f}); different scope, gap expected")
        else:
            verdict = "independent"
            why = (f"{n} cells, median rel. diff {med_rel:.1%}; separate measurement systems, "
                   f"divergence is informative")
        out.append({
            "indicator_id": ind, "source_a": a, "source_b": b, "n_cells": n_all,
            "n_point_cells": n,
            "median_rel_diff": med_rel, "agree_share_within_2pct": agree_share,
            "median_ratio_a_over_b": med_ratio, "direction_consistency": direction,
            "relationship": verdict, "basis": "declared" if declared else "inferred",
            "evidence": why,
        })
    return pd.DataFrame(out).sort_values(["relationship", "indicator_id", "source_a", "source_b"])


def flag_divergences(cmp_df: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Cell-level comparisons for independent pairs only, with material divergences flagged."""
    if cmp_df.empty or pairs.empty:
        return pd.DataFrame()
    indep = pairs[pairs["relationship"] == "independent"][["indicator_id", "source_a", "source_b"]]
    cells = cmp_df.merge(indep, on=["indicator_id", "source_a", "source_b"], how="inner").copy()
    if cells.empty:
        return cells

    floor = cells["unit"].map(lambda u: MATERIALITY.get(u, MATERIALITY_DEFAULT))
    magnitude = cells[["value_a", "value_b"]].abs().max(axis=1)
    opposed = (cells["value_a"] <= 0) | (cells["value_b"] <= 0)

    cells["comparison_status"] = "comparable"
    cells.loc[magnitude < floor, "comparison_status"] = "immaterial"
    cells.loc[opposed, "comparison_status"] = "zero_or_negative"
    # Ruling R21 of research/rulings_2026-10-15.md. Where source a or source b prints the value
    # as a bound and the value from the other source lies inside the bound, the comparison takes
    # the status within_censored_bound and is set aside.
    if "censored_a" in cells.columns:
        ca, cb = cells["censored_a"].fillna(""), cells["censored_b"].fillna("")
        va, vb = cells["value_a"], cells["value_b"]
        held = (((ca == "<") & (vb <= va)) | ((ca == ">") & (vb >= va))
                | ((cb == "<") & (va <= vb)) | ((cb == ">") & (va >= vb)))
        cells.loc[held & (cells["comparison_status"] == "comparable"),
                  "comparison_status"] = "within_censored_bound"

    # only a comparable cell can be a genuine disagreement
    cells["divergent"] = (cells["comparison_status"] == "comparable") & \
                         (cells["rel_diff"].abs() > DIVERGENCE_FLAG)
    cells = cells.sort_values(["divergent", "rel_diff"],
                              key=lambda s: s.abs() if s.name == "rel_diff" else s,
                              ascending=[False, False])
    return cells


def run(panel: str | Path = "data/panel/hiv_panel.csv",
        outdir: str | Path = "data/panel") -> Dict[str, object]:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df = load_panel(panel)
    cmp_df = build_comparisons(df)
    pairs = classify_pairs(cmp_df)
    cells = flag_divergences(cmp_df, pairs)

    pairs.to_csv(outdir / "reconciliation_pairs.csv", index=False)
    if len(cells):
        cells.to_csv(outdir / "reconciliation_cells.csv", index=False)

    # headline counts: how much of the panel's apparent multi-source depth is real
    by_rel = (cmp_df.merge(pairs[["indicator_id", "source_a", "source_b", "relationship"]],
                           on=["indicator_id", "source_a", "source_b"], how="left")
              .groupby("relationship").size().to_dict()) if len(cmp_df) else {}
    n_div = int(cells["divergent"].sum()) if len(cells) else 0
    by_status = cells["comparison_status"].value_counts().to_dict() if len(cells) else {}

    lines = [
        "Reconciliation summary",
        f"panel: {panel}",
        f"national cells compared (pairwise): {len(cmp_df)}",
        "",
        "comparisons by relationship:",
        *[f"  {k:14s} {v}" for k, v in sorted(by_rel.items(), key=lambda x: -x[1])],
        "",
        f"independent pairs: {int((pairs['relationship'] == 'independent').sum())}",
        f"pairs whose relationship was declared and not inferred: "
        f"{int((pairs['basis'] == 'declared').sum())}",
        "",
        "independent-pair cells by comparability:",
        *[f"  {k:22s} {v}" for k, v in sorted(by_status.items(), key=lambda x: -x[1])],
        f"material divergences flagged (comparable cells, |rel diff| > {DIVERGENCE_FLAG:.0%}): {n_div}",
        "",
        "Note: 'derived' comparisons are the same underlying estimate republished and must not",
        "be counted as corroboration. 'subset' comparisons measure different scopes.",
    ]
    (outdir / "reconciliation_summary.txt").write_text("\n".join(lines) + "\n")
    for ln in lines:
        log.info("reconcile: %s", ln)
    return {"comparisons": cmp_df, "pairs": pairs, "cells": cells, "by_relationship": by_rel}


if __name__ == "__main__":   # python -m hivimpact.reconcile
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
