#!/usr/bin/env python3
"""
Build the static site from the assembled panel.

Reads only local files — the panel, the reconciliation tables and the agreement register —
and writes a complete site to site/dist/. Nothing here touches the network, so the same panel
always produces the same pages and the build can be re-run without re-collecting anything.

    python3 scripts/build_site.py [--panel data/panel/hiv_panel.csv] [--out site/dist]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import re
import shutil
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

try:                                            # only needed for the .xlsx of each figure
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
except ImportError:                             # the rest of the build does not depend on it
    Workbook = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hivimpact.config.indicators import CANONICAL_INDICATORS         # noqa: E402
from hivimpact.config.regions import REGIONS                         # noqa: E402
from hivimpact.normalize import name_for as panel_name_for           # noqa: E402

# site/charts.py is loaded by path: `site` is a standard-library module name, so importing
# the directory as a package would shadow it.
_spec = importlib.util.spec_from_file_location("hiv_site_charts", ROOT / "site" / "charts.py")
charts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(charts)

# The panel names a country by the country's ISO 3166 entry, which suits a data file and reads
# badly on a page. The ISO entries for the Democratic Republic of the Congo, Micronesia and
# Palestine are written as inverted index entries, and the ISO entry for São Tomé and Príncipe
# drops the accents the site prints everywhere else. The site shows the names below in place of
# the ISO entries. The panel and the downloads keep the panel's own names.
SITE_NAMES = {"COD": "DR Congo", "STP": "São Tomé and Príncipe", "FSM": "Micronesia",
              "PSE": "State of Palestine"}


def name_for(iso3: str) -> str:
    return SITE_NAMES.get(str(iso3).upper()) or panel_name_for(iso3)


def sort_name(name: str) -> str:
    """A country name with the accents removed, so that São Tomé files under Sa, before Senegal."""
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()


# --- fixed copy --------------------------------------------------------------------------
SITE = {
    "name": "HIV Funding Impacts",
    "tagline": ("Tracking the effect of global health funding cuts on HIV services in low- "
                "and middle-income countries"),
    "masthead_sub": "Global health funding · LMIC",
    "url": "https://hivfundingimpacts.aiinsocietyhub.com/",
    "citation": ("Smith, A. and Hung, J. (2026) HIV Funding Impacts: a source-tracked panel of "
                 "HIV financing and service indicators under the Trump administration. Panel "
                 "last "
                 "assembled on {built}."),
}


def phase_no(r: dict) -> int:
    """The number of a region's work phase, for ordering, or 0 for a region with no phase yet."""
    return int(r["phase"].split()[-1]) if r["phase"] else 0


def nav_regions(rel: str) -> list:
    """
    The regions as the masthead and the footer list them.

    Every region is named, in the order the configuration sets, but only a published
    one carries a link. The rest are shown so the scope of the project is visible from
    any page, and they become links as their pages are built.
    """
    return [{"name": r["name"], "slug": r["slug"], "phase": r["phase"],
             "phase_no": phase_no(r),
             "href": f'{rel}regions/{r["slug"]}/' if r["status"] == "live" else "",
             "live": r["status"] == "live"}
            for r in REGIONS]

# The server configuration that ships with the built site. It is written into the root of the
# output on every build, so it stays with the pages and is uploaded along with them.
HTACCESS = r"""DirectoryIndex index.html

# Every page is an index.html inside its own folder, so the server returns the page when the
# address stops at the folder, and that short form is what the links on the site use. Anyone
# who arrives at the longer form, from an old link or a saved bookmark, is sent on to the
# short one, so that each page is reached at one address and not at two.
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteCond %{THE_REQUEST} \s/+(.*/)?index\.html[\s?] [NC]
  RewriteRule ^(.*/)?index\.html$ /%1 [R=301,L]
</IfModule>

# The files under downloads/ are declared as what they are. Without these lines the server
# calls all of them plain text, and a browser then saves a .csv file under a .txt name.
AddType text/csv .csv
AddCharset UTF-8 .csv
AddType application/octet-stream .sqlite .parquet
AddType application/vnd.openxmlformats-officedocument.spreadsheetml.sheet .xlsx

# The links on the data page are meant to save a file, not to open one in the browser window.
#
# The host also keeps copies of these files on its edge servers. A copy taken while the lines
# above were missing goes on calling a .csv plain text, and a browser handed that copy saves the
# file as .txt. Asking for the copy to be checked against this server before it is handed out
# means a copy cannot outlive the type it was stored with. These files are downloaded once and
# read locally, so there is nothing lost in checking each time.
<IfModule mod_headers.c>
  <FilesMatch "\.(csv|sqlite|parquet|xlsx)$">
    Header set Content-Disposition "attachment"
    Header set Cache-Control "public, max-age=0, must-revalidate"
    Header unset Expires
  </FilesMatch>
</IfModule>
"""

SOURCE_META = {
    "unaids_aidsinfo": ("UNAIDS AIDSinfo",
                        "Epidemic estimates, treatment cascade, key-population indicators and "
                        "country-reported HIV expenditure."),
    "unaids_gam_expenditure": ("UNAIDS Global AIDS Monitoring expenditure database",
                               "HIV spending as reported by every country in the database, "
                               "split by payer and by programme. The database is the only "
                               "near-global source of a country's own account of PEPFAR and "
                               "Global Fund money."),
    "who_gho": ("WHO Global Health Observatory",
                "Epidemic and cascade indicators from the WHO indicator catalogue."),
    "world_bank": ("World Bank Open Data",
                   "Population denominators and UNAIDS-derived prevalence."),
    "oecd_crs": ("OECD Creditor Reporting System",
                 "Donor disbursements under purpose code 13040, by donor, including the "
                 "Global Fund."),
    "foreign_assistance": ("ForeignAssistance.gov",
                           "United States self-reported HIV disbursements, by fiscal year."),
    "pepfar_panorama": ("PEPFAR Panorama Spotlight",
                        "Results from PEPFAR-supported sites, which cover the PEPFAR programme "
                        "and not the national total."),
    "dhs": ("Demographic and Health Surveys",
            "Population-based survey estimates, national and by survey region."),
    "clm_asia": ("CLM Asia",
                 "Community-led monitoring of service access at a small number of selected "
                 "facilities in Indonesia and India."),
    "th_hivhub": ("Thailand HIV Info Hub",
                  "The National AIDS Programme cascade, summed across 77 provinces."),
    "kh_nchads_copct": ("Cambodia NCHADS",
                        "Key-population outreach, testing and ART enrolment from the quarterly "
                        "Boosted CoPCT report."),
    "ph_doh_cascade": ("Philippines DOH Epidemiology Bureau",
                       "The 95-95-95 cascade by region, from the quarterly surveillance "
                       "report."),
    "ng_ndr": ("Nigeria NASCP National Data Repository",
               "Treatment and viral load by state, from the repository every Nigerian "
               "ART facility reports into."),
    "who_tme": ("WHO Global Tuberculosis Programme",
                "The HIV columns national tuberculosis programmes report to WHO, including "
                "people on antiretroviral treatment and people who started treatment in the "
                "year."),
    "who_ghed": ("WHO Global Health Expenditure Database",
                 "Spending on HIV and other sexually transmitted infections in the national "
                 "health accounts of every country, split by payer."),
    "global_fund": ("Global Fund Data Service",
                    "Annual results reported by Global Fund grants, including people newly "
                    "diagnosed and started on treatment."),
    "global_fund_allocations": ("Global Fund allocations",
                                "The amount a country may apply for from the Global Fund in "
                                "every three-year funding cycle, up to the cycle for 2026 to "
                                "2028."),
    "iati": ("IATI, through d-portal",
             "HIV transactions filed by every publisher to the International Aid Transparency "
             "Initiative, dated to the day the money moved."),
    "pepfar_snu": ("PEPFAR results by province",
                   "Results from PEPFAR-supported sites by province and district, 2016 to "
                   "2025, which cover the PEPFAR programme and not the provincial total."),
    "pepfar_agency": ("PEPFAR results by funding agency",
                      "Treatment and testing at PEPFAR-supported sites, split between USAID, "
                      "HHS/CDC and other United States agencies."),
    "pepfar_agency_snu": ("PEPFAR results by funding agency and province",
                          "Treatment, treatment starts and positive tests at PEPFAR-supported "
                          "sites, split by funding agency within every province."),
    "pepfar_modality": ("PEPFAR testing by modality",
                        "HIV testing at PEPFAR-supported sites, split between testing in a "
                        "facility and testing through community outreach."),
    "pepfar_expenditure": ("PEPFAR budgets and expenditure",
                           "Planned funding against reported expenditure, by funding agency "
                           "and programme area, fiscal years 2021 to 2025."),
    "pepfar_ou_budgets": ("PEPFAR operating-unit budgets",
                          "Budget for every operating unit from 2005 to 2020 and expenditure "
                          "from 2018 to 2020, the years before PEPFAR's budgets and expenditure "
                          "by implementing partner begin in 2021."),
    "pepfar_commodities": ("PEPFAR commodity procurement plans",
                           "Planned spending on antiretrovirals, test kits and laboratory "
                           "supplies, from the country operational plans for 2019 to 2025."),
    "pepfar_hrh": ("PEPFAR human resources for health inventory",
                   "Staff paid through PEPFAR's implementing partners in fiscal year 2025, as "
                   "spend and as full-time equivalents."),
    "pepfar_vmmc": ("PEPFAR voluntary medical male circumcision",
                    "Circumcisions at PEPFAR-supported sites by country, 2010 to 2017. From "
                    "2018 the panel takes circumcisions from PEPFAR Panorama Spotlight."),
    "paho_core": ("PAHO Core Indicators",
                  "Notified HIV cases reported by the ministries of health of the Americas, "
                  "with the female and male split, from national case surveillance."),
    "paho_hiv": ("PAHO Interactive HIV Data Dashboard",
                 "Notified HIV cases the PAHO Core Indicators table lacks, Haiti from 2010 to "
                 "2024 among the gaps, and the share of people on ART taking a "
                 "dolutegravir-based regimen, 2020 to 2025."),
    "who_hts": ("WHO HIV testing services dashboard",
                "National HIV tests, test positivity, testing in community and facility "
                "settings and self-test kits distributed, as countries reported to Global AIDS "
                "Monitoring for 2018 to 2020 and 2022 to 2024."),
    "unaids_services": ("UNAIDS service continuation dashboard",
                        "Monthly HIV service counts 30 countries have reported to UNAIDS since "
                        "October 2024, kept as December counts of people on ART and as 2025 "
                        "totals only where a country reported all 12 months."),
    "unaids_naomi": ("UNAIDS HIV sub-national estimates viewer (Naomi)",
                     "December 2025 estimates from the Naomi small-area model for 31 countries, "
                     "nationally and for every province, region or county, with uncertainty "
                     "ranges, plus an earlier December for nine of the 31 countries. The panel "
                     "never keeps the projected years."),
    "unaids_databook": ("UNAIDS Data 2025 country databook",
                        "Domestic public, private and international HIV expenditure as countries "
                        "reported to UNAIDS for 2015 to 2023, and the 2024 estimates of people "
                        "living with HIV for Nigeria's 36 states and Federal Capital Territory "
                        "and Eritrea's six regions."),
    "unaids_phia": ("Population-based HIV Impact Assessment (PHIA) surveys, through the UNAIDS "
                    "Inequalities dashboard",
                    "National HIV prevalence, ART coverage, viral suppression and HIV incidence "
                    "for ages 15 to 49 from 17 household surveys in 13 countries of eastern and "
                    "southern Africa, west Africa and central Africa, 2016 to 2021, with the 95 "
                    "per cent confidence interval of the survey. The Ethiopian survey of 2018 "
                    "covered urban areas only and is not shown."),
    "who_europe_hfa": ("WHO Europe Health for All database",
                       "New HIV diagnoses for 48 countries and new AIDS cases for 45 countries "
                       "of the WHO European Region, 2000 to 2019, from the joint ECDC and WHO "
                       "Europe surveillance reports. Spanish, Italian and Dutch HIV diagnoses "
                       "start in the first year every region reported, Russian HIV diagnoses "
                       "start in 2016, the year the Russian case definitions changed, and "
                       "North Macedonian HIV diagnoses start in 2017, the year North Macedonia "
                       "began reporting HIV and AIDS in a single record. Spanish HIV diagnoses "
                       "stop in 2017 and Spanish AIDS cases stop in 2013, because some Spanish "
                       "regions sent no report for later years. The site holds no Turkish, "
                       "Luxembourgish or Austrian HIV count, no AIDS count for Turkey, North "
                       "Macedonia, Sweden, the Russian Federation, Austria or Luxembourg, and "
                       "no German AIDS count for 2019, because the WHO country notes describe "
                       "a narrower count or no report, the Luxembourg HIV counts are half the "
                       "national statistics, the Luxembourg AIDS counts run at 0.56 to 0.67 "
                       "times the joint report for 2024 data, the joint report for 2024 data "
                       "says the Austrian counts come from a cohort study, and the German AIDS "
                       "count for 2019 is a first report frozen when "
                       "Germany stopped reporting AIDS cases. The Serbian "
                       "counts of the database include Kosovo, so the site shows no Serbian "
                       "count from the database and takes the Serbian and Kosovar counts "
                       "from the joint report for 2024 data. The Armenian counts of the "
                       "database count citizens of Armenia alone, so the site shows no "
                       "Armenian count from the database and takes the Armenian HIV count, "
                       "citizens and foreign citizens together, from the National Centre for "
                       "Infectious Diseases of Armenia."),
    "ecdc_hiv_report": ("HIV/AIDS surveillance in Europe 2025, the joint report of ECDC (the "
                        "European Centre for Disease Prevention and Control) and the WHO "
                        "Regional Office for Europe, Tables 1 and 13",
                        "HIV diagnoses for 50 countries and AIDS diagnoses for 42 countries "
                        "of the WHO European Region, 2015 to 2024, the counts every country reported to The European Surveillance "
                        "System (TESSy), including people with an earlier positive diagnosis "
                        "made abroad or elsewhere in the country. The site holds no Austrian or "
                        "Turkish count, no North Macedonian count before 2017, and no Russian "
                        "count for 2015, Spanish count for 2018 or Ukrainian count for 2015, "
                        "because the report describes a cohort study, a narrower count, a change "
                        "of case definition, a missing region or a rounded figure. The site "
                        "holds no AIDS count for Austria, Turkey, North Macedonia, Ireland, "
                        "the United Kingdom, Cyprus, Kyrgyzstan or Spain, "
                        "no German AIDS count for 2019, no Maltese AIDS count "
                        "for 2020 or 2023, and no Ukrainian AIDS count from 2020, because the "
                        "report or the country notes describe a cohort study, AIDS counted "
                        "only at HIV diagnosis, missing regions, a corrected figure, a change "
                        "of definition, or counts the 2025 report moved far from the 2020 "
                        "report with no reason given. The Armenian counts of the report count "
                        "citizens of Armenia alone, so the site shows no Armenian count from "
                        "the report and takes the Armenian HIV count, citizens and foreign "
                        "citizens together, from the National Centre for Infectious Diseases "
                        "of Armenia."),
    "unicef_hiv": ("UNICEF HIV/AIDS dataset",
                   "PMTCT coverage and the vertical transmission rate from the UNAIDS 2026 "
                   "estimates round, 2010 to 2025, with whole series for Nigeria, Indonesia, "
                   "Bangladesh and six other countries the UNAIDS AIDSinfo exports show "
                   "without any value. People living with HIV, new HIV infections and "
                   "AIDS-related deaths for 10 age groups under age 25 from the same round, "
                   "2010 to 2025, for all sexes, females and males."),
    "pacific_data_hub": ("Pacific Data Hub of SPC (the Pacific Community)",
                         "Comprehensive HIV knowledge, condom use at last higher-risk sex and "
                         "sex before age 15 from the Pacific Demographic and Health Surveys of "
                         "eight Pacific countries, 2007 to 2015, for women and men separately, "
                         "under the standard survey definitions."),
    "unodc_pwid": ("World Drug Report 2026 of UNODC (the United Nations Office on Drugs and "
                   "Crime), statistical annex table 4.1",
                   "HIV prevalence among people who inject drugs for 11 countries, 2013 to 2024, "
                   "and the number of people who inject drugs for 30 countries, 2009 to 2025, "
                   "national estimates at the year the estimate describes. The site holds no "
                   "UNODC figure citing UNAIDS, and no figure from a treatment register, a case "
                   "notification or a count of lifetime injecting."),
    "za_thembisa":("Thembisa model, University of Cape Town",
                    "South Africa's official HIV model, nationally and for all nine "
                    "provinces, with 95 per cent uncertainty intervals. The panel keeps only the "
                    "years the model fits to data and never the projected years."),
    "cm_cnls": ("Cameroon National AIDS Control Committee",
                "People on antiretroviral treatment and the viral load cascade for all ten "
                "regions, from the annual reports for 2023 and 2024."),
    "cm_nasa": ("Cameroon National AIDS Spending Assessments",
                "HIV spending in CFA francs by source of revenue, from six assessments "
                "covering nine years between 2007 and 2021."),
    "ne_annuaire": ("Niger health statistics yearbook",
                    "People on antiretroviral treatment at 31 December, by region, from the "
                    "yearbooks for 2013 to 2024."),
    "gn_annuaire": ("Guinea statistical yearbook",
                    "Pregnant women living with HIV who received antiretrovirals, by region, "
                    "2022 to 2024."),
    "pe_endes": ("Peru Demographic and Family Health Survey (ENDES)",
                 "Share of people aged 15 to 49 who had an HIV test in the last 12 months, "
                 "nationally from 2013 and for 26 departments from 2014, with 95 per cent "
                 "confidence intervals."),
    "ht_mspp": ("Haiti Ministry of Public Health and Population statistical reports",
                "Notified HIV cases for all ten departments and nationally, 2020 to 2023. "
                "From 2022 the ministry removed duplicate records, so the fall between 2021 "
                "and 2022 is partly a change in counting."),
    "bo_anuario": ("Bolivia Ministry of Health and Sports epidemiology yearbook 2016",
                   "Notified HIV cases for all nine departments and nationally in 2016, "
                   "counting cases notified with HIV and cases notified in the AIDS phase "
                   "together."),
    "bz_moh": ("Belize Ministry of Health HIV Surveillance Report 2018",
               "Preliminary counts of newly diagnosed HIV infections for the six districts "
               "in 2018, from case-based surveillance in the Belize Health Information "
               "System."),
    "ar_snvs": ("Argentina Ministry of Health open data, HIV case notifications",
                "HIV cases notified to the national surveillance system SNVS 2.0 for "
                "the 24 provinces and nationally, by sex, 2015 to 2024, in the release "
                "of 20 January 2026. The ministry revises past years at every release, "
                "so the counts for 2015 to 2022 stand above the PAHO figures for the "
                "same years."),
    "py_mercosur": ("MERCOSUR HIV epidemiological bulletin 2012",
                    "New HIV diagnoses in Paraguay by sex, nationally, 2000 to 2009, as "
                    "the Paraguayan national programme reported the counts to the HIV/AIDS "
                    "commission of the MERCOSUR health ministers. The PAHO figures for "
                    "Paraguay start in 2014."),
    "ni_mapasalud": ("Nicaragua Ministry of Health health map (Mapa Nacional de la Salud)",
                     "New HIV cases recorded by epidemiological surveillance, for the 19 "
                     "local health areas (SILAIS) and nationally, 2017 to 2023, read from "
                     "archived copies of the ministry pages. Archived pages for 2022 cover "
                     "10 local health areas and for 2023 cover six."),
    "pe_cdc_sala": ("CDC Peru HIV situation room (Sala VIH)",
                    "HIV cases notified to CDC Peru, the national epidemiology centre of the "
                    "Peruvian Ministry of Health, AIDS cases included, for the 25 departments "
                    "and nationally by sex, 2019 to the last full year, from a web application "
                    "updated every month. CDC Peru revises past years at every update, and the "
                    "counts for 2019 and 2025 changed between the reads of 5 and 28 October "
                    "2026."),
    "lb_moph_bulletin": ("Lebanon Ministry of Public Health statistical bulletins",
                         "HIV cases notified to the National AIDS Program of the "
                         "Lebanese Ministry of Public Health, AIDS cases included, "
                         "nationally for 2007, 2009 and 2014 to 2018, by sex for "
                         "2007 and 2014 to 2018, and people newly started on "
                         "antiretroviral treatment for 2014 to 2017. No bulletin "
                         "states whether the counts cover residents of other "
                         "nationalities."),
    "td_annuaire": ("Chad health statistics yearbook",
                    "Antiretroviral treatment and viral load by province for 2023, with "
                    "national treatment starts and treatment of pregnant women for 2022."),
    "pg_ndoh_dashboard": ("Papua New Guinea National Department of Health provincial HIV dashboard",
                          "HIV tests, positive HIV test results, people on antiretroviral "
                          "treatment by age group, people who started treatment and mothers on "
                          "treatment to prevent transmission to the child, for the 22 provinces "
                          "and nationally, 2022 and 2023."),
    "cn_ndcpa": ("China National Disease Control and Prevention Administration yearly notifiable disease tables",
                 "Reported AIDS cases and the all-cause deaths of reported AIDS patients in "
                 "China, 2023 to 2025, from the yearly national tables, never from a sum of the "
                 "monthly tables. The AIDS row counts AIDS cases and not HIV diagnoses."),
    "mn_hdc": ("Mongolia Health Development Center Health Indicators books",
               "HIV cases newly registered in Mongolia in the year, nationally, 2015 to 2025, "
               "read from the 2024 English book and the 2025 Mongolian book and checked "
               "against the 2019, 2023 and 2024 books."),
    "lk_nsacp": ("Sri Lanka National STD/AIDS Control Programme annual report 2025",
                 "HIV cases reported in Sri Lanka in the year, nationally, 2010 to 2025, read "
                 "from Figure 2.6 of the 2025 annual report and checked against 16 quarterly "
                 "returns, which never enter the panel."),
    "ge_geostat": ("National Statistics Office of Georgia (Geostat) statistical database",
                   "HIV cases newly registered in Georgia in the year, nationally, 2002 to "
                   "2025, with women and men for 2012 to 2025, read from two tables of the "
                   "Geostat PxWeb service. The yearly count is kept only where the rise in "
                   "the cumulative register equals the new cases."),
    "by_belstat": ("National Statistical Committee of the Republic of Belarus (Belstat) data portal",
                   "HIV cases newly identified in Belarus in the year, 2000 to 2025, nationally "
                   "by sex and by five age groups, and for the six regions and Minsk city by "
                   "sex. A count is kept only where men plus women, the age groups and the "
                   "regions add to the published totals."),
    "ua_npsi": ("Public Health Centre of the Ministry of Health of Ukraine, HIV monitoring portal",
                "People newly registered with HIV in Ukraine in the year, 2016 to 2024, "
                "nationally by four age groups and by sex at ages 15 and over, and for 22 "
                "oblasts and Kyiv city for 2017 to 2021. A count is kept only where the age "
                "groups, the sexes and the regions add to the published totals. The counts "
                "cover the territory under the control of the Government of Ukraine."),
    "kg_aidscenter": ("Republican Centre for the Control of Blood-borne Viral Hepatitis and HIV "
                      "of the Kyrgyz Republic, situation report of 1 July 2026",
                      "HIV cases registered in Kyrgyzstan in the year among citizens and "
                      "foreign citizens, nationally, 2013 to 2025. The report enters only "
                      "where the nine regions add to the national total in every year, every "
                      "row adds to the printed total, and the citizen and foreign-citizen "
                      "totals match the page header."),
    "tj_moh": ("Ministry of Health and Social Protection of the Population of Tajikistan, "
               "health yearbooks for 2014, 2015, 2016, 2017 and 2021",
               "People newly registered with HIV in the year in the five regions of "
               "Tajikistan, 2014, 2015, 2016, 2017 and 2021. A yearbook enters only where "
               "the five regions add to the Republic total, the districts add to the "
               "Districts of Republican Subordination, and the next yearbook prints the same "
               "counts."),
    "prk_cbs_mics": ("Central Bureau of Statistics of the DPRK and UNICEF, Multiple Indicator "
                     "Cluster Survey 2009",
                     "Women with comprehensive knowledge about HIV in the Democratic "
                     "People's Republic of Korea, aged 15 to 49 and 15 to 24, nationally and "
                     "in the 10 provinces, 2009. The report enters only where the provinces "
                     "add to the national total and the sampling-error tables print the "
                     "same shares and numbers of women."),
    "tj_stat": ("Agency on Statistics under the President of the Republic of Tajikistan, "
                "health compendium of 2019",
                "People newly registered with HIV in the year in Tajikistan, nationally, by "
                "sex and by age, 2014 to 2018. The compendium enters only where the age "
                "groups add to the printed total of every sex and men plus women equal all "
                "people in every age group."),
    "fj_mohms": ("Ministry of Health and Medical Services of Fiji, public HIV surveillance "
                 "workbook and summary report for 2025",
                 "People newly registered with HIV in the year in Fiji, nationally since 1989, "
                 "and by division, sex and age from 2018, with the diagnosed people living with "
                 "HIV from 2020 and the people with a suppressed viral load from 2022. The "
                 "workbook enters only where the division, sex, age group and ethnicity sheets "
                 "add to the case sheet, and the cascade enters only where the summary report "
                 "prints the same counts and coverage."),
    "np_ncasc": ("National Centre for AIDS and STD Control of Nepal, World AIDS Day factsheets "
                 "of 2014 to 2019",
                 "Clients with an HIV positive result at the HIV testing and counselling sites "
                 "in the year in Nepal, which the centre reports as the reported HIV cases of "
                 "the year, nationally, 2008 to 2018, read from archived copies of six "
                 "factsheet editions. The factsheets enter only where every edition printing a "
                 "full year gives the same count, with the 2019 edition revising 2017 from "
                 "1,856 to 1,842."),
    "vu_mics": ("Vanuatu National Statistics Office and UNICEF, Multiple Indicator Cluster "
                "Survey 2007",
                "Women with comprehensive knowledge about HIV in Vanuatu, aged 15 to 49 and 15 "
                "to 24, nationally, 2007, read from an archived copy of the survey report. The "
                "report enters only where the regions, the urban and rural areas and the age "
                "groups add to the national total and the sampling-error table prints the same "
                "share for women aged 15 to 24."),
    "me_ijzcg": ("Institute of Public Health of Montenegro, annual HIV report for 2025",
                 "People registered with HIV in Montenegro in the year, including people "
                 "diagnosed abroad, nationally, 2001 to 2025, with men and women for 2025. "
                 "The report enters only where the columns of Table 5 add to the printed "
                 "totals, men plus women equal the 2025 total, and the municipalities add "
                 "to the new diagnoses of 2025."),
    "bd_asp": ("AIDS/STD Programme of Bangladesh, World AIDS Day files 2016 to 2025",
               "People newly reported HIV positive in Bangladesh, nationally, 2016 to 2025, "
               "in the programme's reporting year from 1 November of the year before to 31 "
               "October, Forcibly Displaced Myanmar Nationals included. The files enter only "
               "where every cumulative count equals the count of the year before plus the "
               "new cases."),
    "mv_moh": ("Ministry of Health of the Maldives, Maldives Health Statistics 2014 and 2015-16",
               "HIV positive cases detected in the Maldives, nationally, 2005 to 2016, in the "
               "calendar year, Maldivians and expatriates together. The tables enter only "
               "where the two editions agree on every year from 2007 to 2014."),
    "in_naco": ("National AIDS Control Organisation of India, Sankalak 2025, seventh edition",
                "Modelled HIV prevalence among adults aged 15 to 49, people living with HIV, "
                "new HIV infections and AIDS-related deaths in India, nationally and by State "
                "or Union Territory, 2024, with lower and upper bounds. The table enters only "
                "where the January and August versions of the booklet agree on every row, "
                "the State counts add to the India count, and the India figures match the "
                "overview table."),
    "am_ncid": ("National Centre for Infectious Diseases of Armenia, HIV situation analysis 2025",
                "HIV cases registered in Armenia in the year among citizens of Armenia and "
                "foreign citizens, nationally, 2015 to 2025. The report enters only where the "
                "yearly counts of citizens add to the 6,625 cases the text prints, the yearly "
                "counts of foreign citizens add to no more than the 490 cases the text prints, "
                "the citizen series of two charts agree in every year, and the 2025 counts "
                "match the text."),
    "kz_kncdiz": ("Kazakh Scientific Centre of Dermatology and Infectious Diseases, surveys "
                  "among people who inject drugs, 2022 and 2024",
                  "HIV prevalence among people aged 18 and over who inject drugs in Kazakhstan, "
                  "weighted for the respondent-driven sample, nationally, 2020, 2022 and 2024. "
                  "The reports enter only where Table 6, the text and the conclusions print the "
                  "same weighted figure, the HIV-positive respondents match the sample share, "
                  "and the two reports print the same 2022 round."),
    "sb_sinso_dhs": ("Solomon Islands National Statistics Office, Demographic and Health "
                     "Surveys 2006-2007 and 2015",
                     "HIV testing in the last 12 months with the result received for women and "
                     "men aged 15 to 49 in 2015, and comprehensive knowledge of HIV (2007 and "
                     "2015) and condom use at last higher-risk sex (2007) for men aged 15 to 49, "
                     "nationally. A table enters only where the testing shares add to 100, the "
                     "urban and rural rows give the total, and the men aged 15 to 49 and 50 "
                     "and over give the printed total for all men."),
    "bd_sdg": ("SDG Tracker of Bangladesh, National AIDS/STD Programme series of indicator "
               "3.3.1, 2022 and 2024",
               "People newly reported HIV positive in Bangladesh by gender, men and women, "
               "nationally, 2022 and 2024, in the programme's reporting year from 1 November "
               "of the year before to 31 October. A year enters only where the men, women "
               "and transgender people add to the World AIDS Day count of the programme and "
               "every count matches the share of the programme's gender chart."),
}

SOURCE_TYPE_LABEL = {
    "modelled_estimate": "Modelled estimate",
    "routine_programme_record": "Programme record",
    "expenditure_account": "Expenditure account",
    "survey": "Survey",
    "community_led_monitoring": "Community-led monitoring",
}

DOMAIN_LABEL = {
    "financing": "Financing",
    "cascade": "Treatment cascade",
    "epi": "Epidemic estimates",
    "prevention": "Prevention and outreach",
    "service_access": "Service access",
    "denominator": "Population denominators",
}
DOMAIN_BLURB = {
    "financing": ("What donors report disbursing, and what countries report spending. The OECD "
                  "record of United States disbursements and the record the United States "
                  "government publishes on ForeignAssistance.gov are kept separate, because the "
                  "two records are compiled independently."),
    "cascade": ("Diagnosis, treatment and viral suppression. Modelled coverage estimates sit "
                "beside programme counts from national registers, and the panel never merges a "
                "modelled estimate with a register count, because a model and a register "
                "measure different things."),
    "epi": ("People living with HIV, new infections, deaths and prevalence. Almost every "
            "epidemic estimate in the panel comes from the annual UNAIDS modelling round, "
            "whichever body publishes the estimate."),
    "prevention": ("Pre-exposure prophylaxis (PrEP) and key-population outreach. Outreach "
                   "figures are counts of people reached over a period, summed to a year, and "
                   "not counts of people at a single date."),
    "service_access": ("What service users report about stockouts, interruptions, staffing and "
                       "cost. The reports come from a small number of selected facilities and "
                       "are not a representative sample."),
    "denominator": "Total population, used as the denominator for coverage and rates.",
}
DOMAIN_ORDER = ["financing", "cascade", "epi", "prevention", "service_access", "denominator"]

# The downloads are named after the file they carry, so they need a slug of their own.
DL_PHOTO = {
    "hiv_panel.csv": "panel-csv",
    "hiv_panel.parquet": "panel-parquet",
    "hiv_panel.sqlite": "panel-sqlite",
    "reconciliation_pairs.csv": "panel-recon-pairs",
    "reconciliation_cells.csv": "panel-recon-cells",
    "mou_agreements.csv": "panel-mou",
}

# The files on the data page, in the order shown, with the line each one carries.
DOWNLOAD_FILES = [
    ("hiv_panel.csv", "The full panel. One row is one figure from one source."),
    ("hiv_panel.parquet", "The same panel, typed, for analysis."),
    ("hiv_panel.sqlite", "The same panel as a queryable database."),
    ("reconciliation_pairs.csv",
     "Every source pair, with the relationship inferred between the two sources and the "
     "statistics behind the classification."),
    ("reconciliation_cells.csv",
     "Every comparison of matched figures from independent source pairs, with material "
     "differences flagged."),
    ("mou_agreements.csv",
     "Bilateral agreements signed under the America First Global Health Strategy."),
]


def build_provenance(stats: dict) -> list:
    """The counts on the plate under the home page hero."""
    return [
        {"n": stats["n_obs_fmt"], "l": "observations, with the source and the retrieval date "
                                       "on every row"},
        {"n": stats["n_sources"], "l": "sources, from international estimates to national "
                                       "programme registers"},
        {"n": stats["n_indicators"], "l": "indicators, on one common vocabulary"},
        {"n": f'{stats["year_min"]}–{stats["year_max"]}', "l": "years covered"},
        # the HIV count is claimed only when the tracker states the programme areas of every
        # agreement, because an agreement with no stated areas is unknown and not a "no"
        {"n": stats["n_mou_hiv"], "l": f'of {stats["n_mou"]} bilateral agreements signed '
                                       f'so far cover HIV', "hl": True}
        if stats["n_mou_scoped"] == stats["n_mou"] else
        {"n": stats["n_mou"], "l": "bilateral agreements signed so far under the America "
                                   "First Global Health Strategy", "hl": True},
    ]


def mou_covers_hiv(r) -> bool | None:
    """True or False where the tracker states the programme areas of the agreement, None where
    the tracker states none. The file written on 3 October 2026 carries False on every row
    because the tracker dropped the column, so the empty areas decide, not the flag. A blank
    flag beside stated areas is also None, never False."""
    areas, flag = r.get("programme_areas"), str(r.get("covers_hiv")).strip().lower()
    if pd.isna(areas) or not str(areas).strip() or flag not in ("true", "false"):
        return None
    return flag == "true"

# Countries whose national programme is read at source, and what route was used.
AT_SOURCE = {
    "THA": "Read at source",
    "KHM": "Read at source",
    "PHL": "Read at source",
    "IDN": "Community monitoring",
    "ZAF": "Model at source",
    "NGA": "Read at source",
    "CMR": "Read at source",
    "NER": "Read at source",
    "GIN": "Read at source",
    "TCD": "Read at source",
    "IND": "Model at source",
    "BGD": "Read at source",
    "LKA": "Read at source",
    "MDV": "Read at source",
    "NPL": "Read at source",
    "CHN": "Read at source",
    "MNG": "Read at source",
    "PRK": "Read at source",
    "PNG": "Read at source",
    "SLB": "Read at source",
    "VUT": "Read at source",
    "ARM": "Read at source",
    "BLR": "Read at source",
    "GEO": "Read at source",
    "KAZ": "Read at source",
    "KGZ": "Read at source",
    "MNE": "Read at source",
    "TJK": "Read at source",
    "UKR": "Read at source",
    "ARG": "Read at source",
    "BLZ": "Read at source",
    "BOL": "Read at source",
    "HTI": "Read at source",
    "NIC": "Read at source",
    "PRY": "Read at source",
    "PER": "Read at source",
    "LBN": "Read at source",
}

# Countries whose national system is still to be reached, by an access request or by a probe
# that has not yet found the data portal. Shown as a lead and not as aggregator coverage, so
# the status grid says the position is open.
LEADS = {
    "LAO": "Access to be sought",
    "MMR": "Access to be sought",
    "TLS": "Access to be sought",
    "RWA": "Lead to follow",
    "SWZ": "Lead to follow",
    "BWA": "Lead to follow",
}

COUNTRY_COPY = {
    "THA": {
        "lede": ("Thailand's National AIDS Programme publishes through the HIV Info Hub, which "
                 "our project queries directly. The national cascade runs a year further than "
                 "the international estimates. In the overlapping years, the national cascade "
                 "and the international estimates differ by about eight per cent, a difference "
                 "expected between a programme register and a modelled estimate and not a sign "
                 "of error in the register or in the model."),
        "blurb": "National cascade read from the HIV Info Hub, 2021 onward.",
    },
    "KHM": {
        "lede": ("Cambodia's National Center for HIV/AIDS publishes a quarterly Boosted CoPCT "
                 "report whose tables can be read without interpretation. The Boosted CoPCT "
                 "report gives figures that the international and donor bodies do not publish, "
                 "namely outreach, testing, the share of tests that are positive and enrolment "
                 "on antiretroviral treatment for every key population, quarter by quarter. "
                 "Cambodia has also signed a bilateral agreement with the United States."),
        "blurb": "Key-population outreach and testing, quarterly, from NCHADS.",
    },
    "PHL": {
        "lede": ("The Department of Health's quarterly surveillance report gives the full "
                 "95-95-95 cascade, covering diagnosis, treatment and viral suppression, for all "
                 "18 regions from 2025 onward. The surveillance report gives more detail than "
                 "the annual submission of the Philippines to UNAIDS, which is why our project "
                 "reads the surveillance report directly. The Philippines has also signed a "
                 "bilateral agreement with the United States."),
        "blurb": "Regional 95-95-95 cascade, 18 regions, from the DOH quarterly report.",
    },
    "IDN": {
        "lede": ("Indonesia's national HIV reporting system, SIHA, cannot be reached by the "
                 "public, so Indonesia appears through international and donor reporting. Our "
                 "project also reads reports from community-led monitoring at a small number of "
                 "selected facilities, where service users report stockouts, interruptions, "
                 "staffing and out-of-pocket cost. The facilities are a small sample and do not "
                 "represent Indonesia as a whole."),
        "blurb": "International and donor reporting, plus community-led monitoring of service "
                 "access.",
    },
    "VNM": {
        "lede": ("Vietnam's national HIV portal has been unreachable from several networks "
                 "throughout our assessment of national sources, and the case-surveillance system "
                 "is restricted to programme staff. Vietnam therefore appears only through "
                 "international and donor reporting. Our project will reassess Vietnam if the "
                 "national portal returns."),
        "blurb": "International and donor reporting only. The national portal is offline.",
    },
    "MYS": {
        "lede": ("Malaysia publishes a national HIV report, but the national report is "
                 "Malaysia's submission to UNAIDS. Reading the national report directly would "
                 "return figures the panel already holds, so Malaysia appears only through "
                 "international and donor reporting. The obstacle in Malaysia is duplication, "
                 "not access."),
        "blurb": "International and donor reporting only. The national report is the UNAIDS "
                 "submission.",
    },
    "MMR": {
        "lede": ("Myanmar's National AIDS Programme reporting is not publicly accessible, and HIV "
                 "monitoring in Myanmar has been disrupted since 2021. Myanmar appears only "
                 "through international and donor reporting, and the figures should be read "
                 "with the disruption to monitoring since 2021 in mind."),
        "blurb": "International and donor reporting only. National reporting is closed.",
    },
    "LAO": {
        "lede": ("Laos runs a national database of the treatment cascade, HIVCAM, which is not "
                 "open to the public, and the figures Laos publishes are national totals only. "
                 "A data-sharing agreement between institutions is the realistic route to the "
                 "figures held in HIVCAM."),
        "blurb": "International and donor reporting only. HIVCAM is closed to public access.",
    },
    "TLS": {
        "lede": ("Timor-Leste moved in 2023 to case-based surveillance on DHIS2, the health "
                 "information platform used by many national health ministries. The DHIS2 "
                 "system in Timor-Leste has a data interface, but the interface is expected to "
                 "require a login. The HIV epidemic in Timor-Leste is small, and the "
                 "international and donor record for the country is correspondingly thin."),
        "blurb": "International and donor reporting only. DHIS2 access to be tested.",
    },
    "ZAF": {
        "lede": ("South Africa's official HIV estimates come from the Thembisa model, which "
                 "Leigh Johnson and colleagues at the University of Cape Town publish as open "
                 "workbooks. The model gives every indicator nationally and for all nine "
                 "provinces, with a 95 per cent uncertainty interval. Our project keeps only the "
                 "years the model fits to data and never the projected years, so a Thembisa "
                 "series can end earlier than the matching international series. Thembisa is a "
                 "model, and the Thembisa figures are estimates and not register counts."),
        "blurb": "Thembisa model, national and nine provinces, with uncertainty intervals.",
    },
    "NGA": {
        "lede": ("Every antiretroviral treatment facility in Nigeria reports into the National "
                 "Data Repository run by the national HIV programme, NASCP. Our project reads "
                 "two of the repository's public data feeds directly, giving people on treatment "
                 "and the share virally suppressed for all 36 states and the Federal Capital "
                 "Territory. The repository publishes a current snapshot and not a history, so "
                 "the Nigerian programme series grows by one year with every annual reading."),
        "blurb": "Treatment and viral suppression by state, from the National Data Repository.",
    },
    "CMR": {
        "lede": ("Our project reads Cameroon's figures directly from two publications of the "
                 "National AIDS Control Committee, the CNLS. The annual reports for 2023 and 2024 "
                 "give people on antiretroviral treatment and the viral load cascade for all ten "
                 "regions. The National AIDS Spending Assessments give HIV spending in CFA francs "
                 "by source of revenue for nine years between 2007 and 2021. Cameroon has no year "
                 "in the UNAIDS expenditure database, so the National AIDS Spending Assessments "
                 "are the panel's only record of Cameroonian HIV spending split by named "
                 "donor."),
        "blurb": "Regional treatment cascade and national spending assessments, from the CNLS.",
    },
    "NER": {
        "lede": ("Niger's health statistics yearbooks, published through the national statistics "
                 "institute, count people on antiretroviral treatment at 31 December in all eight "
                 "regions, citing the national HIV programme. Our project reads the regional "
                 "treatment table from the yearbooks for 2013 to 2024. The 2015 yearbook is "
                 "excluded because the age columns of the 2015 yearbook do not add up to the "
                 "national row, so the Niger series has no point for 2015. PEPFAR does not report "
                 "below the national level in Niger, so the health statistics yearbooks are the "
                 "panel's only regional record of treatment in Niger."),
        "blurb": "People on treatment by region, from the health statistics yearbooks.",
    },
    "GIN": {
        "lede": ("Guinea's statistical yearbook, published by the national statistics institute, "
                 "counts pregnant women living with HIV who received antiretrovirals in all eight "
                 "regions, citing the health ministry's information system. Our project reads "
                 "2022 to 2024 only. The same table in the yearbook runs back to 2014, but the "
                 "earlier years came from a different programme source, and several of the "
                 "earlier figures are too large to be counts of women. A series joined across "
                 "2021 and 2022 would therefore show a fall that reflects a change of source and "
                 "not a change in care."),
        "blurb": "Pregnant women receiving antiretrovirals by region, 2022 to 2024.",
    },
    "TCD": {
        "lede": ("Chad's health statistics yearbooks, served by the national statistics "
                 "institute INSEED, give people on antiretroviral treatment, viral load tests and "
                 "suppressed results for all 23 provinces in 2023, and national treatment starts "
                 "and treatment of pregnant women in 2022. The number of people on treatment at "
                 "the end of 2022 is excluded, because the 2022 and 2023 yearbooks print two "
                 "figures for 31 December 2022 that differ by 24,280 people, without any "
                 "explanation of the difference."),
        "blurb": "Treatment and viral load by province, from the INSEED yearbooks.",
    },
    "IND": {
        "lede": ("India's National AIDS Control Organisation (NACO) publishes the national HIV "
                 "estimates in Sankalak, a yearly booklet. Our project reads the 2024 estimates "
                 "from the seventh edition of Sankalak, published in 2025, giving adult HIV "
                 "prevalence, people living with HIV, new HIV infections and AIDS-related deaths "
                 "for India and for every State and Union Territory, with lower and upper "
                 "bounds. The NACO table enters the panel only where the January and August "
                 "versions of the booklet agree on every row and the State counts add to the "
                 "India count. The NACO figures are model estimates and not register counts. Our "
                 "project also reads reports from community-led monitoring at a small number of "
                 "selected Indian facilities, and the selected facilities do not represent India "
                 "as a whole."),
        "blurb": "NACO model estimates for 2024, national and by State or Union Territory.",
    },
    "BGD": {
        "lede": ("The AIDS/STD Programme of Bangladesh, the national programme for HIV and other "
                 "sexually transmitted diseases (STD), counts the people newly reported HIV "
                 "positive in every year. Our project reads the national count for 2016 to 2025 "
                 "from the World AIDS Day files of the programme, and the counts of men and "
                 "women for 2022 and 2024 from the Sustainable Development Goals (SDG) Tracker "
                 "of Bangladesh. The reporting year of the programme runs from 1 November of the "
                 "year before to 31 October, and the counts include Forcibly Displaced Myanmar "
                 "Nationals. A World AIDS Day file enters the panel only where every cumulative "
                 "count equals the cumulative count of the year before plus the new cases."),
        "blurb": "People newly reported HIV positive, 2016 to 2025, from the national programme.",
    },
    "LKA": {
        "lede": ("Sri Lanka's National STD/AIDS Control Programme (NSACP), the national programme "
                 "for HIV and other sexually transmitted diseases (STD), publishes an annual "
                 "report with the HIV cases reported in every year. Our project reads the "
                 "national count for 2010 to 2025 from Figure 2.6 of the 2025 annual report, and "
                 "checks the count against 16 quarterly returns of the programme, which never "
                 "enter the panel."),
        "blurb": ("Reported HIV cases, 2010 to 2025, from the annual report of the national "
                  "programme."),
    },
    "MDV": {
        "lede": ("The Ministry of Health of the Maldives publishes the HIV positive cases "
                 "detected in every year in the Maldives Health Statistics. Our project reads "
                 "the national count for 2005 to 2016 from the 2014 and the 2015-16 editions, "
                 "and keeps the count only where the 2014 and 2015-16 editions agree on every "
                 "year from 2007 to 2014. The count covers Maldivians and expatriates together."),
        "blurb": ("HIV positive cases detected, 2005 to 2016, from the Maldives Health "
                  "Statistics."),
    },
    "NPL": {
        "lede": ("Nepal's National Centre for AIDS and STD Control (NCASC), where STD stands for "
                 "sexually transmitted disease, published World AIDS Day factsheets with the "
                 "clients given an HIV positive result at the HIV testing and counselling sites "
                 "in every year, which the centre reports as the HIV cases of the year. Our "
                 "project reads the national count for 2008 to 2018 from archived copies of six "
                 "factsheet editions, 2014 to 2019, and keeps a count only where every edition "
                 "printing a full year gives the same count."),
        "blurb": ("Positive results at testing sites, 2008 to 2018, from archived national "
                  "factsheets."),
    },
    "CHN": {
        "lede": ("China's National Disease Control and Prevention Administration (NDCPA) "
                 "publishes yearly tables of the notifiable infectious diseases. Our project "
                 "reads the reported AIDS cases and the deaths of reported AIDS patients for "
                 "2023 to 2025 from the yearly national tables, and never from a sum of the "
                 "monthly tables. The AIDS row counts people reported with AIDS and not people "
                 "newly diagnosed with HIV, and the deaths count deaths from all causes among "
                 "reported AIDS patients."),
        "blurb": "Reported AIDS cases and deaths, 2023 to 2025, from the national yearly tables.",
    },
    "MNG": {
        "lede": ("Mongolia's Health Development Center publishes the Health Indicators books. Our "
                 "project reads the HIV cases newly registered in every year, nationally, for "
                 "2015 to 2025, from the 2024 English book and the 2025 Mongolian book, and "
                 "checks the counts against the 2019, 2023 and 2024 books."),
        "blurb": "HIV cases newly registered, 2015 to 2025, from the Health Indicators books.",
    },
    "PRK": {
        "lede": ("North Korea's Central Bureau of Statistics (CBS) ran the 2009 Multiple "
                 "Indicator Cluster Survey (MICS) with the United Nations Children's Fund "
                 "(UNICEF). Our project reads the share of women with comprehensive knowledge "
                 "about HIV, at ages 15 to 49 and 15 to 24, nationally and for the 10 provinces. "
                 "The MICS report enters the panel only where the 10 provinces add to the "
                 "national total and the sampling-error tables print the same shares and numbers "
                 "of women."),
        "blurb": ("Women's knowledge about HIV, 2009, national and 10 provinces, from a household "
                  "survey."),
    },
    "PNG": {
        "lede": ("Papua New Guinea's National Department of Health (NDOH) publishes a provincial "
                 "HIV dashboard. Our project reads HIV tests, positive test results, people on "
                 "antiretroviral treatment by age group, people starting treatment and mothers "
                 "on treatment to prevent transmission to the child, for all 22 provinces and "
                 "nationally, for 2022 and 2023. The dashboard counts are programme reports and "
                 "not modelled estimates."),
        "blurb": "Testing and treatment by province, 2022 and 2023, from the national dashboard.",
    },
    "SLB": {
        "lede": ("The Solomon Islands National Statistics Office (SINSO) ran the Demographic and "
                 "Health Surveys (DHS) of 2006-2007 and 2015. Our project reads HIV testing in "
                 "the last 12 months with the result received, for women and men aged 15 to 49 "
                 "in 2015, and comprehensive knowledge of HIV in 2007 and 2015 and condom use at "
                 "last higher-risk sex in 2007, for men aged 15 to 49. A survey table enters the "
                 "panel only where the testing shares add to 100, the urban and rural rows give "
                 "the total, and the age groups of men give the printed total for all men. "
                 "Further survey figures for the Solomon Islands come through the Pacific Data "
                 "Hub of the Pacific Community (SPC)."),
        "blurb": ("HIV testing, knowledge and condom use, from the household surveys of 2007 and "
                  "2015."),
    },
    "VUT": {
        "lede": ("The Vanuatu National Statistics Office ran the 2007 Multiple Indicator Cluster "
                 "Survey (MICS) with the United Nations Children's Fund (UNICEF). Our project "
                 "reads the share of women with comprehensive knowledge about HIV, at ages 15 to "
                 "49 and 15 to 24, nationally, from an archived copy of the survey report. The "
                 "MICS report enters the panel only where the regions, the urban and rural areas "
                 "and the age groups add to the national total and the sampling-error table "
                 "prints the same share for women aged 15 to 24. Further survey figures for "
                 "Vanuatu come through the Pacific Data Hub of the Pacific Community (SPC)."),
        "blurb": "Women's knowledge about HIV, 2007, from an archived household survey report.",
    },
    "FJI": {
        "lede": ("Fiji's Ministry of Health and Medical Services publishes a public HIV "
                 "surveillance workbook and summary report, giving people newly registered with "
                 "HIV in every year since 1989, with breakdowns by division, sex and age from "
                 "2018. Our project has written the code to read the 2025 workbook and summary "
                 "report, but the gov.fj government domain gave no network address in any check "
                 "from 25 to 27 October 2026, and the workbook and summary report could not be "
                 "downloaded. Fiji therefore appears only through international and donor "
                 "reporting, and the Fijian figures enter the panel at the first reading after "
                 "the gov.fj domain returns."),
        "blurb": ("International and donor reporting only, while the national workbook host is "
                  "unreachable."),
    },
    "ARM": {
        "lede": ("Armenia's National Centre for Infectious Diseases (NCID) publishes an HIV "
                 "situation analysis. Our project reads the HIV cases registered in every year "
                 "from 2015 to 2025, among citizens of Armenia and among foreign citizens, from "
                 "the 2025 situation analysis. The 2025 report enters the panel only where the "
                 "yearly counts agree with the totals printed in the text of the report, and "
                 "where two charts of the citizen counts agree in every shared year."),
        "blurb": ("HIV cases registered, citizens and foreign citizens, 2015 to 2025, from the "
                  "national centre."),
    },
    "BLR": {
        "lede": ("The National Statistical Committee of the Republic of Belarus (Belstat) "
                 "publishes the HIV cases newly identified in every year on the Belstat data "
                 "portal. Our project reads the counts for 2000 to 2025, nationally by sex and "
                 "by five age groups, and for the six regions and Minsk city by sex. A count is "
                 "kept only where men plus women, the age groups and the regions add to the "
                 "published totals."),
        "blurb": ("New HIV cases by sex, age and region, 2000 to 2025, from the statistics "
                  "committee."),
    },
    "GEO": {
        "lede": ("The National Statistics Office of Georgia (Geostat) publishes the HIV cases "
                 "newly registered in every year in the Geostat statistical database. Our "
                 "project reads the national count for 2002 to 2025, with women and men for 2012 "
                 "to 2025, and keeps the count of a year only where the rise in the cumulative "
                 "register equals the new cases of the year."),
        "blurb": "New HIV cases, 2002 to 2025, with sex from 2012, from the statistics office.",
    },
    "KAZ": {
        "lede": ("The Kazakh Scientific Centre of Dermatology and Infectious Diseases (KNCDIZ) "
                 "runs surveys of people who inject drugs. Our project reads HIV prevalence "
                 "among people aged 18 and over who inject drugs, weighted for a "
                 "respondent-driven sample, in which respondents recruit further respondents, "
                 "for the survey rounds of 2020, 2022 and 2024, from the reports of 2022 and "
                 "2024. The 2022 and 2024 reports enter the panel only where the table, the text "
                 "and the conclusions of a report print the same weighted figure, and where the "
                 "2022 and 2024 reports print the same figure for the 2022 round. The figures "
                 "describe people who inject drugs and not the whole population of Kazakhstan."),
        "blurb": "HIV prevalence among people who inject drugs, 2020, 2022 and 2024.",
    },
    "KGZ": {
        "lede": ("The Republican Centre for the Control of Blood-borne Viral Hepatitis and HIV of "
                 "the Kyrgyz Republic publishes a situation report on HIV. Our project reads the "
                 "HIV cases registered in every year from 2013 to 2025, among citizens and among "
                 "foreign citizens, from the report of 1 July 2026. The situation report enters "
                 "the panel only where the nine regions add to the national total in every year "
                 "and every row adds to the printed total."),
        "blurb": "HIV cases registered, 2013 to 2025, from the national HIV centre.",
    },
    "MNE": {
        "lede": ("The Institute of Public Health of Montenegro (IJZCG) publishes an annual HIV "
                 "report. Our project reads the people registered with HIV in every year from "
                 "2001 to 2025 from the 2025 report, including people diagnosed abroad, with men "
                 "and women for 2025. The 2025 report enters the panel only where the columns of "
                 "the main table add to the printed totals, men plus women equal the 2025 total, "
                 "and the municipalities add to the new diagnoses of 2025."),
        "blurb": "People registered with HIV, 2001 to 2025, from the public health institute.",
    },
    "TJK": {
        "lede": ("Our project reads two Tajik publishers. The health yearbooks of the Ministry of "
                 "Health and Social Protection of the Population give the people newly "
                 "registered with HIV in the five regions of Tajikistan for 2014 to 2017 and "
                 "2021, and the 2019 health compendium of the Agency on Statistics under the "
                 "President gives the national count by sex and by age for 2014 to 2018. A "
                 "yearbook enters the panel only where the five regions add to the Republic "
                 "total and the next yearbook prints the same counts, and the compendium enters "
                 "the panel only where the age groups and the sexes add to the printed totals."),
        "blurb": "New HIV registrations by region, sex and age, from two national publishers.",
    },
    "UKR": {
        "lede": ("The Public Health Centre of the Ministry of Health of Ukraine publishes an HIV "
                 "monitoring portal. Our project reads the people newly registered with HIV in "
                 "every year from 2016 to 2024, nationally by four age groups and by sex at ages "
                 "15 and over, and for 22 oblasts (regions) and Kyiv city for 2017 to 2021. A "
                 "count is kept only where the age groups, the sexes and the regions add to the "
                 "published totals. The counts cover the territory under the control of the "
                 "Government of Ukraine."),
        "blurb": "New HIV registrations by age, sex and oblast, from the Public Health Centre.",
    },
    "ARG": {
        "lede": ("Argentina's Ministry of Health publishes the HIV cases notified to the national "
                 "health surveillance system (SNVS 2.0, Sistema Nacional de Vigilancia de la "
                 "Salud) on the open-data portal of the ministry. Our project reads the notified "
                 "cases for 2015 to 2024, for the 24 provinces and nationally, for men, for "
                 "women and for all sexes, from the release of 20 January 2026. The release "
                 "enters the panel only where the 24 provinces sum to the national row within 10 "
                 "cases in every sex and year, and where the row for all sexes lies between five "
                 "below and 50 above men plus women. The ministry revises past years at every "
                 "release, and the counts for 2015 to 2022 stand above the counts the Pan "
                 "American Health Organization (PAHO) holds for the same years."),
        "blurb": ("Notified HIV cases by province and sex, 2015 to 2024, from the surveillance "
                  "system."),
    },
    "BLZ": {
        "lede": ("The Epidemiology Unit of Belize's Ministry of Health published the HIV "
                 "Surveillance Report 2018 in July 2019, with preliminary counts of newly "
                 "diagnosed HIV infections from case-based surveillance in the Belize Health "
                 "Information System. Our project reads the counts for the six districts of "
                 "Belize in 2018, for women, for men and in total. The 2018 report enters the "
                 "panel only where women plus men equal the total in every row, and where the "
                 "six districts and the cases with no known district sum exactly to the Grand "
                 "Total of the table."),
        "blurb": "Newly diagnosed HIV infections by district, 2018, from the Ministry of Health.",
    },
    "BOL": {
        "lede": ("Bolivia's Ministry of Health and Sports (MSyD, Ministerio de Salud y Deportes) "
                 "publishes an epidemiology yearbook. Our project reads the notified HIV cases "
                 "for the nine departments and nationally in 2016 from the 2016 yearbook, "
                 "counting the cases notified with HIV and the cases notified in the AIDS phase "
                 "together. The 2016 yearbook enters the panel only where the nine departments "
                 "sum exactly to the national total in every column, and where the cases with "
                 "HIV and the cases in the AIDS phase add to the printed total in every row."),
        "blurb": "Notified HIV cases by department, 2016, from the ministry yearbook.",
    },
    "HTI": {
        "lede": ("Haiti's Ministry of Public Health and Population (MSPP, Ministère de la Santé "
                 "Publique et de la Population) publishes an annual statistical report. Our "
                 "project reads the notified HIV cases for the ten departments and nationally "
                 "for 2020 to 2023 from the reports. A report enters the panel only where the "
                 "ten departments sum exactly to the national total in people tested and in "
                 "cases, and where the printed share of positive tests matches the counts in "
                 "every row. From 2022 the ministry removed duplicate records, and the fall "
                 "between 2021 and 2022 is partly a change in counting. The Core Indicators "
                 "table of the Pan American Health Organization (PAHO) holds no Haitian row."),
        "blurb": "Notified HIV cases by department, 2020 to 2023, from the ministry reports.",
    },
    "NIC": {
        "lede": ("Nicaragua's Ministry of Health (MINSA) publishes a national health map, the "
                 "Mapa Nacional de la Salud, with the new HIV cases recorded by epidemiological "
                 "surveillance. Our project reads the national count for 2017 to 2023 from "
                 "archived copies of the ministry pages. The counts for the 19 local health "
                 "areas (SILAIS) enter the panel once archived copies of every area page are "
                 "stored. The archived pages for 2022 cover 10 local health areas, and the "
                 "archived pages for 2023 cover six."),
        "blurb": ("New HIV cases nationally, 2017 to 2023, from the Ministry of Health health "
                  "map."),
    },
    "PRY": {
        "lede": ("The health ministries of Argentina, Brazil, Paraguay and Uruguay published a "
                 "joint HIV bulletin in 2012 through the HIV/AIDS commission of the health "
                 "ministers of the Southern Common Market (MERCOSUR). Our project reads the new "
                 "HIV diagnoses in Paraguay for 2000 to 2009, for men and for women, as the "
                 "Paraguayan national programme reported the counts to the commission. The 2012 "
                 "bulletin enters the panel only where the table and the charts of the bulletin "
                 "print the same rates, and where every count and rate imply a consistent "
                 "population. The figures of the Pan American Health Organization (PAHO) for "
                 "Paraguay start in 2014."),
        "blurb": "New HIV diagnoses by sex, 2000 to 2009, from the MERCOSUR bulletin.",
    },
    "PER": {
        "lede": ("Our project reads two Peruvian publishers. The Demographic and Family Health "
                 "Survey (ENDES) of the national statistics institute (INEI) gives the share of "
                 "people aged 15 to 49 who had an HIV test in the last 12 months, nationally "
                 "from the second half of 2013 and for 26 departments from 2014, with 95 per "
                 "cent confidence intervals. The HIV situation room of CDC Peru, the national "
                 "epidemiology centre of the Ministry of Health, gives the HIV cases notified "
                 "for 2019 to 2025, AIDS cases included, for the 25 departments and nationally "
                 "by sex. The situation room enters the panel only where the 25 departments sum "
                 "to the national count in every year, and CDC Peru revises past years at every "
                 "monthly update."),
        "blurb": ("HIV testing from the ENDES survey, and notified HIV cases by department from "
                  "CDC Peru."),
    },
    "LBN": {
        "lede": ("Our project reads the statistical bulletins of the Lebanese Ministry of "
                 "Public Health for 2007, 2009 and 2014 to 2018. The bulletins give the HIV "
                 "cases notified to the National AIDS Program of the ministry in every year, "
                 "AIDS cases included, by sex for 2007 and 2014 to 2018, and the people newly "
                 "started on antiretroviral therapy (ART) for 2014 to 2017. A bulletin enters "
                 "the panel only where the stages of disease and the sexes sum to the printed "
                 "total, and where every printed percentage matches the count over the total. "
                 "The bulletins for 2010, 2011 and 2013 count cases up to November and are "
                 "not read, and no bulletin states whether the counts cover residents of "
                 "other nationalities."),
        "blurb": ("Notified HIV cases by sex, and people newly started on antiretroviral "
                  "therapy, from the bulletins of the Ministry of Public Health."),
    },
}

FEASIBILITY = [
    ("Thailand", "HIV Info Hub data mart, run by the Department of Disease Control",
     "Open and structured. Answers queries directly.", "Read at source", True),
    ("Cambodia", "NCHADS quarterly Boosted CoPCT report",
     "Open. Published tables, readable without interpretation.", "Read at source", True),
    ("Philippines", "DOH Epidemiology Bureau quarterly surveillance report",
     "Open. Regional cascade annex from 2025 onward.", "Read at source", True),
    ("Indonesia", "SIHA national reporting system and CLM Asia community-led monitoring",
     "SIHA does not respond. The community monitoring reports are open.",
     "Community monitoring", True),
    ("Vietnam", "VAAC portal and HIV INFO 4.0 case surveillance",
     "Portal unreachable. Surveillance restricted to programme staff.", "Aggregators only", False),
    ("Malaysia", "data.gov.my and the Ministry of Health country progress report",
     "Open, but the report is the UNAIDS submission already in the panel.",
     "Aggregators only", False),
    ("Laos", "CHAS and the HIVCAM national cascade database",
     "Closed. Published figures are national totals only.", "Access to be sought", False),
    ("Myanmar", "National AIDS Programme monitoring and evaluation",
     "Closed, and disrupted since 2021.", "Access to be sought", False),
    ("Timor-Leste", "DHIS2 case-based surveillance, introduced 2023",
     "Has a data interface, which is expected to require a login.", "Access to be sought",
     False),
]

# The same assessment for the regions published after the pilot, in the order the methods page
# lists them. Each region's rows come from that region's feasibility log in docs/, and the
# summary above each table says how the region was assessed.
FEASIBILITY_LATER = [
    ("eastern-and-southern-africa", "Eastern and Southern Africa",
     ("The Eastern and Southern African countries were assessed on 3 August 2026 by an "
      "automated check of national data hosts. The automated check recorded whether every host "
      "answered, what every host returned and whether a DHIS2 data interface responded, DHIS2 "
      "being the health information platform used by many national health ministries. An "
      "automated check can show that a host blocks access, but a check of a guessed host name "
      "that does not exist shows nothing about whether national figures are available. South "
      "Africa's Thembisa model is the only national source in the region that is open, "
      "structured and gives figures that international reporting does not. Angola, Burundi, "
      "Comoros, Eritrea, Madagascar, Mauritius, Somalia and South Sudan were not checked and are "
      "not yet assessed."),
     [
         ("South Africa", "Thembisa model, University of Cape Town",
          "Open versioned workbooks, national and nine provinces, no login.",
          "Model at source", True),
         ("Rwanda", "Rwanda HMIS, Rwanda Biomedical Centre",
          "Reachable and not behind a login, but the DHIS2 data interface does not answer.",
          "Lead to follow", False),
         ("Eswatini", "NERCHA and the government portal",
          "Reachable. No data portal found.", "Lead to follow", False),
         ("Botswana", "Ministry of Health and Wellness",
          "Reachable. No data portal found.", "Lead to follow", False),
         ("Tanzania", "Tanzania HMIS, NACP and TACAIDS",
          "The HMIS redirects to a DHIS2 login page.", "Aggregators only", False),
         ("Ethiopia", "Ethiopian DHIS2 and EPHI",
          "DHIS2 login page. The data interface returns the login page as well.",
          "Aggregators only", False),
         ("Uganda", "Uganda HMIS and the Uganda AIDS Commission",
          "DHIS2 login page.", "Aggregators only", False),
         ("Malawi", "Malawi HMIS and the Ministry of Health",
          "DHIS2 login page. The ministry site refuses the request.", "Aggregators only", False),
         ("Kenya", "KHIS, NASCOP and NSDCC",
          "Untrusted certificate, then a DHIS2 login page.", "Aggregators only", False),
         ("Zambia", "Zambia HMIS, Ministry of Health and the National AIDS Council",
          "Untrusted certificate. The host serves a software tool and no public data.",
          "Aggregators only", False),
         ("Zimbabwe", "Zimbabwe HMIS, MoHCC and the National AIDS Council",
          "Untrusted certificate. The host serves a patient record system and no public data.",
          "Aggregators only", False),
         ("Mozambique", "MISAU and INS",
          "The MISAU and INS certificates were untrusted, and the INS site was down for "
          "maintenance.", "Inconclusive", False),
         ("Lesotho", "Ministry of Health",
          "Untrusted certificate. No DHIS2 host found.", "Inconclusive", False),
         ("Namibia", "Ministry of Health and Social Services",
          "The connection timed out.", "Inconclusive", False),
         ("Angola, Burundi, Comoros, Eritrea, Madagascar, Mauritius, Somalia and South Sudan",
          "Not yet identified", "Not checked in the August 2026 survey.",
          "Not yet assessed", False),
     ]),
    ("western-and-central-africa", "Western and Central Africa",
     ("Western and Central Africa was assessed in four survey rounds, and the fourth round "
      "ended on 1 October 2026. The fourth round graded every candidate national source against "
      "the panel, so a national report whose years the panel already holds counts as no gain. "
      "Nigeria, Cameroon, Niger, Guinea and Chad are read at source, through six national "
      "sources. The spending assessments of DR Congo and Togo would add four country-years from "
      "2019 onward and are under review."),
     [
         ("Nigeria", "National Data Repository, run by NASCP",
          "Two public data feeds, by state, no login.", "Read at source", True),
         ("Cameroon", "CNLS annual reports and National AIDS Spending Assessments",
          "Open report PDFs in English and French.", "Read at source", True),
         ("Niger", "Health statistics yearbooks, national statistics institute",
          "Open yearbooks, 2013 to 2024. The 2015 edition is excluded.",
          "Read at source", True),
         ("Guinea", "Statistical yearbook, national statistics institute",
          "Open yearbooks, read for 2022 to 2024.", "Read at source", True),
         ("Chad", "Health statistics yearbooks, INSEED",
          "Open through the institute's publications interface.", "Read at source", True),
         ("DR Congo", "PNMLS GAM report and National AIDS Spending Assessments",
          "The national database needs registration. The spending assessments add 2019 and "
          "2020.", "Under review", False),
         ("Togo", "National AIDS Spending Assessment 2023",
          "Open report, adding 2022 and 2023. The 2023 yearbook cannot be reached.",
          "Under review", False),
         ("Senegal", "National AIDS programme",
          "No spending assessment exists, and the UNAIDS expenditure workbook already holds "
          "Senegal's spending years.", "Aggregators only", False),
         ("Burkina Faso", "National AIDS Spending Assessments",
          "Open, but adds no year from 2019 onward that the panel lacks.",
          "Aggregators only", False),
         ("Mali", "National AIDS Spending Assessments",
          "Open, but adds no year from 2019 onward that the panel lacks.",
          "Aggregators only", False),
         ("Benin", "National AIDS Spending Assessment 2024",
          "Open, but the panel already holds Benin's spending for 2018 to 2024.",
          "Aggregators only", False),
         ("Liberia", "National AIDS Spending Assessments",
          "Open, but adds no year from 2019 onward that the panel lacks.",
          "Aggregators only", False),
         ("Sierra Leone", "National AIDS Spending Assessments",
          "Open, but adds no year from 2019 onward that the panel lacks.",
          "Aggregators only", False),
         ("Ghana", "Ghana AIDS Commission, Ghana Health Service and DHIMS2",
          "No national database found. The 2022 spending assessment repeats years the panel "
          "holds.", "Aggregators only", False),
         ("Côte d'Ivoire", "PNLS Spectrum profiles and DIIS RASS yearbooks",
          "Open, but the profiles are model output and the yearbooks stop at 2020.",
          "Aggregators only", False),
         ("Gambia", "Gambia Bureau of Statistics",
          "No health statistics yearbook. District figures appear only in the five-year "
          "strategic plan.", "Aggregators only", False),
         ("Gabon", "Statistics institute yearbook",
          "The yearbook link is gone, and the HIV figures the institute shows are republished "
          "UNAIDS estimates.", "Aggregators only", False),
         ("Central African Republic", "ICASEES statistical yearbook, 2018 to 2021",
          "Open. A lead at low priority, since HIV prevalence in the yearbook comes from a "
          "survey the panel already holds.", "Aggregators only", False),
         ("Mauritania", "Statistical yearbook 2015",
          "No current series behind the 2015 yearbook. A lead at low priority.",
          "Aggregators only", False),
         ("Cabo Verde, Congo, Equatorial Guinea, Guinea-Bissau and São Tomé and Príncipe",
          "None found",
          "No spending assessment, no year in the UNAIDS expenditure workbook and no "
          "sub-national figures from any source.", "Aggregators only", False),
     ]),
    ("south-asia", "South Asia",
     ("South Asia was assessed from 14 to 25 October 2026, by the method of the Western and "
      "Central African assessment. Every candidate national source was graded against the panel, "
      "and a national report whose years the panel already holds counts as no gain. Bangladesh, "
      "India, the Maldives, Nepal and Sri Lanka are read at source, through six national "
      "sources."),
     [
         ("India", "Sankalak estimates of the National AIDS Control Organisation (NACO)",
          "Open booklet, national and every State or Union Territory, 2024.",
          "Model at source", True),
         ("Bangladesh", ("World AIDS Day files of the AIDS/STD Programme, and the Sustainable "
          "Development Goals (SDG) Tracker"),
          "Open files, 2016 to 2025, with men and women for 2022 and 2024.",
          "Read at source", True),
         ("Sri Lanka", ("Annual report of the National STD/AIDS Control Programme (NSACP), "
          "where STD stands for sexually transmitted disease"),
          "Open report, 2010 to 2025, checked against the quarterly returns.",
          "Read at source", True),
         ("Maldives", "Maldives Health Statistics, Ministry of Health",
          "Open editions of 2014 and 2015-16, giving 2005 to 2016.",
          "Read at source", True),
         ("Nepal", ("World AIDS Day factsheets of the National Centre for AIDS and STD Control "
          "(NCASC)"),
          "Archived copies of six editions, giving 2008 to 2018.",
          "Read at source", True),
         ("Pakistan", "National AIDS Control Programme and National Institute of Health",
          ("The programme counts are cumulative and the trend charts are images. The weekly "
           "bulletins count suspected cases."),
          "Aggregators only", False),
         ("Bhutan", "Ministry of Health and National Statistics Bureau",
          "The ministry and bureau hosts refuse automated requests.",
          "Aggregators only", False),
         ("Afghanistan", "Ministry of Public Health and the national statistics office",
          ("The weekly surveillance reports carry no HIV line, and the statistics host failed a "
           "secure connection."),
          "Aggregators only", False),
     ]),
    ("east-asia-and-the-pacific", "East Asia and the Pacific",
     ("East Asia and the Pacific was assessed from 14 to 27 October 2026, by the method of the "
      "Western and Central African assessment. China, Mongolia, North Korea, Papua New Guinea, "
      "the Solomon Islands and Vanuatu are read at source. The Fijian connector is built, and "
      "the Fijian figures enter the panel once the gov.fj government domain gives a network "
      "address again."),
     [
         ("China", ("Yearly tables of the National Disease Control and Prevention "
          "Administration (NDCPA)"),
          "Open tables of reported AIDS cases and deaths, 2023 to 2025.",
          "Read at source", True),
         ("Mongolia", "Health Indicators books, Health Development Center",
          "Open books, 2015 to 2025.",
          "Read at source", True),
         ("North Korea", ("Multiple Indicator Cluster Survey (MICS) 2009, Central Bureau of "
          "Statistics and the United Nations Children's Fund (UNICEF)"),
          "Open report, national and 10 provinces.",
          "Read at source", True),
         ("Papua New Guinea", "Provincial HIV dashboard, National Department of Health",
          "Open dashboard, 22 provinces, 2022 and 2023.",
          "Read at source", True),
         ("Solomon Islands", ("Demographic and Health Surveys (DHS) of 2006-2007 and 2015, "
          "Solomon Islands National Statistics Office"),
          "Open survey reports.",
          "Read at source", True),
         ("Vanuatu", "MICS 2007, Vanuatu National Statistics Office",
          "Archived copy of the survey report.",
          "Read at source", True),
         ("Fiji", "Public HIV surveillance workbook, Ministry of Health and Medical Services",
          ("Connector built. The gov.fj domain gave no network address from 25 to 27 October "
           "2026."),
          "Aggregators only", False),
         ("Samoa", "Ministry of Health bulletins",
          "Open, but the bulletins count laboratory specimens tested and not people.",
          "Aggregators only", False),
         ("Tonga", "Ministry of Health and Tonga Statistics Department",
          ("The health site was under maintenance, and the statistics department has no HIV "
           "table."),
          "Aggregators only", False),
         ("Kiribati", "DHS 2009 and MICS 2018-19",
          ("The 2009 survey failed the consistency checks, and the 2018-19 survey report refused "
           "access."),
          "Aggregators only", False),
         ("Tuvalu", "MICS 2019-20",
          "The survey report refused access.",
          "Aggregators only", False),
         ("Micronesia", "Health and statistics offices",
          ("The health and statistics hosts failed, and the statistics office publishes no HIV "
           "table."),
          "Aggregators only", False),
         ("Marshall Islands", "Ministry of Health and Human Services",
          "The HIV page is empty, and the health dashboard is an image.",
          "Aggregators only", False),
     ]),
    ("eastern-europe-and-central-asia", "Eastern Europe and Central Asia",
     ("Eastern Europe and Central Asia was assessed from 20 to 22 October 2026, by the method of "
      "the Western and Central African assessment. Armenia, Belarus, Georgia, Kazakhstan, "
      "Kyrgyzstan, Montenegro, Tajikistan and Ukraine are read at source, through nine national "
      "sources."),
     [
         ("Armenia", "Situation analysis of the National Centre for Infectious Diseases",
          "Open report, 2015 to 2025.",
          "Read at source", True),
         ("Belarus", "Data portal of the National Statistical Committee (Belstat)",
          "Open portal, 2000 to 2025, by sex, age and region.",
          "Read at source", True),
         ("Georgia", ("Statistical database of the National Statistics Office of Georgia "
          "(Geostat)"),
          "Open database tables, 2002 to 2025.",
          "Read at source", True),
         ("Kazakhstan", ("Surveys among people who inject drugs, Kazakh Scientific Centre of "
          "Dermatology and Infectious Diseases"),
          "Open reports, rounds of 2020, 2022 and 2024.",
          "Read at source", True),
         ("Kyrgyzstan", "Situation report of the national HIV centre",
          "Open report, 2013 to 2025.",
          "Read at source", True),
         ("Montenegro", "Annual report of the Institute of Public Health of Montenegro",
          "Open report, 2001 to 2025.",
          "Read at source", True),
         ("Tajikistan", ("Ministry of Health yearbooks and the compendium of the statistics "
          "agency"),
          "Open yearbooks for the five regions, and an open compendium by sex and age.",
          "Read at source", True),
         ("Ukraine", "HIV monitoring portal of the Public Health Centre",
          "Open portal, 2016 to 2024, territory under government control.",
          "Read at source", True),
         ("Azerbaijan", "State Statistical Committee",
          "Open, but the workbook counts citizens only.",
          "Aggregators only", False),
         ("Moldova", "National Bureau of Statistics",
          "Open, but the tables exclude the left bank of the Nistru and Bender.",
          "Aggregators only", False),
         ("Bosnia and Herzegovina", ("Public health institutes of the Federation of Bosnia and "
          "Herzegovina and of Republika Srpska"),
          "Open, but the reports count to 1 December and not the full year.",
          "Aggregators only", False),
         ("Serbia", "Statistics portal and the Batut Institute of Public Health",
          "The portal republishes the UNAIDS estimate, and the institute host timed out.",
          "Aggregators only", False),
         ("North Macedonia", ("MakStat, the database of the State Statistical Office, and the "
          "Institute of Public Health"),
          "MakStat holds no HIV indicator, and the monthly bulletins give no yearly figure.",
          "Aggregators only", False),
         ("Albania", "Institute of Public Health and INSTAT, the statistics institute",
          ("The 2025 count covers part of the year, a firewall blocked further requests, and "
           "INSTAT timed out."),
          "Aggregators only", False),
         ("Türkiye", ("TÜİK, the Turkish Statistical Institute, and the Ministry of Health "
          "yearbook"),
          ("The data service refused access, and the published AIDS counts do not state the case "
           "definition."),
          "Aggregators only", False),
         ("Turkmenistan", "State Committee on Statistics",
          "No health table.",
          "Aggregators only", False),
         ("Uzbekistan", "National Statistics Committee and Republican AIDS Centre",
          ("The statistics portal gives a rate with no stated method, and the AIDS centre timed "
           "out."),
          "Aggregators only", False),
     ]),
    ("latin-america-and-the-caribbean", "Latin America and the Caribbean",
     ("Latin America and the Caribbean was assessed from 5 to 28 October 2026, by the method of "
      "the Western and Central African assessment. Argentina, Belize, Bolivia, Haiti, Nicaragua, "
      "Paraguay and Peru are read at source, through eight country sources."),
     [
         ("Argentina", ("Open data of the Ministry of Health, from the national health "
          "surveillance system (SNVS 2.0)"),
          "Open files, 2015 to 2024, by province and sex.",
          "Read at source", True),
         ("Belize", "HIV Surveillance Report 2018 of the Ministry of Health",
          "Open report, 2018, by district.",
          "Read at source", True),
         ("Bolivia", "Epidemiology yearbook 2016 of the Ministry of Health and Sports",
          "Open yearbook, 2016, by department.",
          "Read at source", True),
         ("Haiti", ("Annual statistical reports of the Ministry of Public Health and "
          "Population"),
          "Open reports, 2020 to 2023, by department.",
          "Read at source", True),
         ("Nicaragua", "National health map of the Ministry of Health",
          "Archived copies of the ministry pages, 2017 to 2023, national.",
          "Read at source", True),
         ("Paraguay", ("HIV bulletin of the health ministers of the Southern Common Market "
          "(MERCOSUR), 2012"),
          "Open bulletin, 2000 to 2009, by sex.",
          "Read at source", True),
         ("Peru", ("Demographic and Family Health Survey (ENDES) of the statistics institute, "
          "and the HIV situation room of CDC Peru, the national epidemiology centre"),
          ("Open survey tables from 2013, and an open web application, 2019 to 2025, by "
           "department."),
          "Read at source", True),
         ("Brazil", "Ministry of Health portals on gov.br",
          "Not queried, under a project decision of 12 October 2026.",
          "Aggregators only", False),
         ("Colombia", "SIVIGILA, the national public health surveillance system",
          "Open, but event 850 counts HIV cases, AIDS cases and AIDS deaths together.",
          "Aggregators only", False),
         ("Costa Rica", "Ministry of Health",
          ("A firewall blocked the reports, and the HIV workbook stands above the PAHO count for "
           "2011 to 2017 for a reason not verified."),
          "Aggregators only", False),
         ("Cuba", "Ministry of Public Health yearbook and ONEI, the statistics office",
          ("The yearbook gives AIDS cases and registered deaths with no province HIV table, and "
           "the ONEI hosts timed out."),
          "Aggregators only", False),
         ("Dominican Republic", ("National HIV council (CONAVIHSIDA) and SeNaSa, the public "
          "health insurer"),
          ("The council host refused access, and the insurer files count the users of one insurer "
           "only."),
          "Aggregators only", False),
         ("Ecuador", "Ministry of Public Health",
          "The ministry host timed out.",
          "Aggregators only", False),
         ("El Salvador", "Ministry of Health",
          "The hosts refused or did not answer automated requests.",
          "Aggregators only", False),
         ("Guatemala", "Ministry of Public Health and INE, the statistics institute",
          ("The HIV category of the ministry situation room refused access, and the statistics "
           "institute and the open-data catalogue sit behind bot challenges."),
          "Aggregators only", False),
         ("Guyana", "Ministry of Health statistical bulletins",
          "The bulletins of 2004 to 2009 survive only in web archives.",
          "Aggregators only", False),
         ("Honduras", ("Health ministry reports, copied by a national association of people "
          "living with HIV"),
          "The report link asks for a sign-in, and the department counts appear only as images.",
          "Aggregators only", False),
         ("Jamaica", "National health and statistics hosts",
          "The hosts refused or did not answer automated requests.",
          "Aggregators only", False),
         ("Mexico", ("CENSIDA, the national HIV centre, and the morbidity yearbook of the "
          "epidemiology directorate"),
          ("CENSIDA counts patients per medicine, the CENSIDA document list sits behind a bot "
           "challenge, and the yearbook host timed out."),
          "Aggregators only", False),
         ("Panama", "National statistics yearbooks",
          ("The yearbooks give registered HIV deaths only, a source class the panel does not yet "
           "carry."),
          "Aggregators only", False),
         ("Suriname", "General Bureau of Statistics (ABS)",
          ("The tables give registered HIV and AIDS deaths only, a source class the panel does "
           "not yet carry."),
          "Aggregators only", False),
         ("Trinidad and Tobago", "Ministry of Health budget guides and development estimates",
          ("The HIV project items appear only in scanned files, and the project enters no figure "
           "read from a scan."),
          "Aggregators only", False),
         ("Venezuela", "Morbidity yearbooks of the Ministry of Health (MPPS)",
          ("Open, but the yearbooks count consultations, with the 2013 count at 55 per cent of "
           "the PAHO count for 2014."),
          "Aggregators only", False),
     ]),
    ("middle-east-and-north-africa", "Middle East and North Africa",
     ("The Middle East and North Africa was assessed on 28 October 2026, by the method of "
      "the Western and Central African assessment. Lebanon is read at source, through the "
      "statistical bulletins of the Ministry of Public Health."),
     [
         ("Lebanon", "Statistical bulletins of the Ministry of Public Health",
          "Open bulletins, 2007, 2009 and 2014 to 2018, national and by sex.",
          "Read at source", True),
         ("Algeria", ("Ministry of Health, the National Public Health Institute (INSP) and "
          "the National Office of Statistics (ONS)"),
          "Every host timed out.",
          "Aggregators only", False),
         ("Djibouti", "INSTAD, the statistics institute, and the Ministry of Health",
          ("The statistics institute serves a JavaScript application with no published "
           "table, and the ministry host gave no reply to the second request."),
          "Aggregators only", False),
         ("Egypt", "CAPMAS, the statistics agency, and the Ministry of Health and Population",
          ("The statistics agency serves a JavaScript application with no published table, "
           "and the ministry host timed out."),
          "Aggregators only", False),
         ("Iran", "Statistical Centre of Iran and the Ministry of Health",
          "No host answered.",
          "Aggregators only", False),
         ("Iraq", "Ministry of Health and COSIT, the statistics organisation",
          ("The ministry host blocked automated requests, and the statistics organisation "
           "publishes no health section."),
          "Aggregators only", False),
         ("Jordan", "Ministry of Health and the Department of Statistics",
          "Every host timed out.",
          "Aggregators only", False),
         ("Libya", ("National Centre for Disease Control and the Bureau of Statistics and "
          "Census"),
          ("The AIDS department page of the disease control centre lists branch offices "
           "only, and the statistics bureau gave no reply to the second request."),
          "Aggregators only", False),
         ("Morocco", "Ministry of Health and the High Commission for Planning (HCP)",
          ("The ministry host did not answer, and the HCP gives only a cumulative count to "
           "2014, quoted from the ministry."),
          "Aggregators only", False),
         ("Palestine", "Ministry of Health and the Palestinian Central Bureau of Statistics",
          "No host answered.",
          "Aggregators only", False),
         ("Sudan", "Federal Ministry of Health and the Central Bureau of Statistics",
          ("The ministry host redirects to itself, and the statistics host gave no network "
           "address."),
          "Aggregators only", False),
         ("Syria", "Central Bureau of Statistics and the Ministry of Health",
          ("The statistics domain now carries a parked page, and the ministry host timed "
           "out."),
          "Aggregators only", False),
         ("Tunisia", "INS, the statistics institute, and the Ministry of Health",
          ("The statistical yearbook for 2019 to 2023 holds no HIV table, and the ministry "
           "host has no network address."),
          "Aggregators only", False),
         ("Yemen", "Ministry of Public Health and Population and the Central Statistical "
          "Organisation",
          ("The ministry host returned a server error, and the statistics site carries no "
           "health table."),
          "Aggregators only", False),
     ]),
]

# What each region page says in words. `lede_tail` follows the region's own counts in the
# opening paragraph, and `callout` sits in the box that says what the page does not yet show,
# ahead of the link to the region's table in Methods.
REGION_COPY = {
    "southeast-asia": {
        "lede_tail": ("Thailand, Cambodia and the Philippines are read at source, and Indonesia "
                      "has reports from community-led monitoring beside the international "
                      "reporting. Vietnam, Malaysia, Myanmar, Laos and Timor-Leste appear only "
                      "through international and donor reporting, and PEPFAR's results by "
                      "province reach seven of the nine countries in the region."),
        "callout": ("PEPFAR's results by province count only the sites PEPFAR supports, and the "
                    "Philippines is the only Southeast Asian country whose national programme "
                    "reports by region. A national programme record is read at source only in "
                    "Cambodia, the Philippines and Thailand. Vietnam's national programme portal "
                    "is offline, and Malaysia, Myanmar, Laos and Timor-Leste appear through "
                    "international and donor reporting only."),
    },
    "eastern-and-southern-africa": {
        "lede_tail": ("South Africa is read at source through the Thembisa model, nationally and "
                      "for all nine provinces. Every country in the region except South Africa "
                      "appears only through international and donor reporting, and PEPFAR's "
                      "results by province reach 17 of the 22 countries in the region."),
        "callout": ("Sub-national figures for Eastern and Southern Africa come only from the "
                    "Thembisa model, for South Africa's nine provinces, and from PEPFAR's results "
                    "by province, which count only the sites PEPFAR supports. The national health "
                    "information systems of Tanzania, Ethiopia, Uganda, Malawi and Kenya sit "
                    "behind a login page, and the health information hosts of Zambia and Zimbabwe "
                    "serve no public data. Rwanda, Eswatini and Botswana remain leads to follow, "
                    "and the automated checks of Mozambique, Lesotho and Namibia were "
                    "inconclusive. Angola, "
                    "Burundi, Comoros, Eritrea, Madagascar, Mauritius, Somalia and South Sudan are "
                    "not yet assessed."),
    },
    "western-and-central-africa": {
        "lede_tail": ("Nigeria, Cameroon, Niger, Guinea and Chad are read at source through six "
                      "national sources, namely Nigeria's National Data Repository, the annual "
                      "reports and the spending assessments of Cameroon's national AIDS committee, "
                      "and the statistics yearbooks of Niger, Guinea and Chad. Every country in "
                      "the region except Nigeria, Cameroon, Niger, Guinea and Chad appears only "
                      "through international and donor reporting, and PEPFAR's results by "
                      "province reach 12 of the 24 countries in the region."),
        "callout": ("Sub-national figures for Western and Central Africa come from PEPFAR's "
                    "results by province, which count only the sites PEPFAR supports, and from the "
                    "national sources of Nigeria, Cameroon, Niger, Guinea and Chad. The spending "
                    "assessments of Burkina Faso, Mali, Benin, Liberia and Sierra Leone add no year "
                    "from 2019 onward that the panel lacks, and Senegal has no spending assessment. "
                    "Cabo Verde, Congo, Equatorial Guinea, Guinea-Bissau and São Tomé and Príncipe "
                    "have no spending assessment and no sub-national figures from any source. The "
                    "spending assessments of DR Congo for 2019 and 2020 and of Togo for 2022 and "
                    "2023 are under review. Niger's treatment series has no point for 2015, because "
                    "the age columns of the 2015 yearbook do not add up to the national row. Chad's "
                    "count of people on treatment at 31 December 2022 is excluded, because the "
                    "2022 and 2023 yearbooks print two different figures for 31 December 2022."),
    },
    "south-asia": {
        "lede_tail": ("Bangladesh, the Maldives, Nepal and Sri Lanka are read at source through "
                      "national case counts, and India through the model estimates of the "
                      "National AIDS Control Organisation (NACO) for 2024, with reports from "
                      "community-led monitoring at selected Indian facilities. Afghanistan, "
                      "Bhutan and Pakistan appear only through international and donor "
                      "reporting, and PEPFAR's results by province reach India and Nepal."),
        "callout": ("Sub-national figures for South Asia come from the NACO estimates for the "
                    "States and Union Territories of India, from the Demographic and Health "
                    "Surveys of India, and from PEPFAR's results by province for India and "
                    "Nepal, which count only the sites PEPFAR supports. The NACO figures are "
                    "model estimates for 2024 and not register counts. The Nepal counts run from "
                    "2008 to 2018 and the Maldives counts from 2005 to 2016. Pakistan's national "
                    "programme publishes cumulative counts and trend charts as images, and the "
                    "weekly disease surveillance bulletins of Pakistan count suspected cases. "
                    "The Ministry of Health and the National Statistics Bureau of Bhutan refused "
                    "automated requests, and the weekly surveillance reports of the Ministry of "
                    "Public Health of Afghanistan carry no HIV line."),
    },
    "east-asia-and-the-pacific": {
        "lede_tail": ("China, Mongolia, North Korea, Papua New Guinea, the Solomon Islands and "
                      "Vanuatu are read at source, through national disease tables, health "
                      "indicator books, a provincial dashboard and national household surveys. "
                      "Fiji, Samoa, Tonga, Kiribati, Tuvalu, Micronesia and the Marshall Islands "
                      "appear only through international and donor reporting. The Pacific Data "
                      "Hub of the Pacific Community (SPC) gives survey figures for Kiribati, the "
                      "Marshall Islands, Samoa, the Solomon Islands, Tonga, Tuvalu and Vanuatu, "
                      "and PEPFAR's results by province reach China and Papua New Guinea."),
        "callout": ("Fiji's national connector is built, but the gov.fj government domain gave no "
                    "network address from 25 to 27 October 2026, and no Fijian figure is yet "
                    "read at source. The national sources give sub-national figures for the 22 "
                    "provinces of Papua New Guinea and the 10 provinces of North Korea, and "
                    "PEPFAR's results by province for China and Papua New Guinea count only the "
                    "sites PEPFAR supports. The North Korean, Solomon Islands and Vanuatu "
                    "figures are survey shares from 2007 to 2015, and the national tables of "
                    "China count AIDS cases and not HIV diagnoses. Samoa's health bulletins "
                    "count laboratory specimens tested and not people tested, Tonga's health "
                    "site was under maintenance, and the statistics offices of Tonga and "
                    "Micronesia publish no HIV table. The Kiribati survey of 2009 failed the "
                    "consistency checks of our project, the hosts of the later Kiribati and "
                    "Tuvalu survey reports refused access, and the HIV page of the health "
                    "ministry of the Marshall Islands is empty."),
    },
    "eastern-europe-and-central-asia": {
        "lede_tail": ("Armenia, Belarus, Georgia, Kazakhstan, Kyrgyzstan, Montenegro, Tajikistan "
                      "and Ukraine are read at source, through national statistics offices, "
                      "public health bodies and national HIV centres. Albania, Azerbaijan, "
                      "Bosnia and Herzegovina, Moldova, North Macedonia, Serbia, Türkiye, "
                      "Turkmenistan and Uzbekistan appear only through international and donor "
                      "reporting, including the joint HIV surveillance report of the European "
                      "Centre for Disease Prevention and Control (ECDC) and the WHO Regional "
                      "Office for Europe, and the WHO Europe Health for All database. PEPFAR's "
                      "results by province reach Kazakhstan, Kyrgyzstan, Tajikistan and Ukraine."),
        "callout": ("Kazakhstan is read at source only for HIV prevalence among people who inject "
                    "drugs. The national sources give sub-national figures for the six regions "
                    "and Minsk city of Belarus, for 22 oblasts and Kyiv city of Ukraine for 2017 "
                    "to 2021, and for the five regions of Tajikistan, and the Ukrainian counts "
                    "cover the territory under the control of the Government of Ukraine. "
                    "PEPFAR's results by province for Kazakhstan, Kyrgyzstan, Tajikistan and "
                    "Ukraine count only the sites PEPFAR supports. Azerbaijan's statistics "
                    "committee counts citizens only, Moldova's statistics bureau excludes the "
                    "left bank of the Nistru and Bender, the reports of the public health "
                    "institutes of Bosnia and Herzegovina count to 1 December and not the full "
                    "year, and Serbia's statistics portal republishes the UNAIDS estimate. North "
                    "Macedonia's statistics office holds no HIV indicator, Albania's 2025 count "
                    "covers part of the year, Türkiye's statistics institute refused access to "
                    "the data service, Turkmenistan's statistics committee has no health table, "
                    "and Uzbekistan's statistics portal gives an HIV rate with no stated method."),
    },
    "latin-america-and-the-caribbean": {
        "lede_tail": ("Argentina, Belize, Bolivia, Haiti, Nicaragua, Paraguay and Peru are read "
                      "at source, through ministries of health, the Peruvian statistics "
                      "institute and a joint bulletin of the health ministers of the Southern "
                      "Common Market (MERCOSUR). Brazil, Colombia, Costa Rica, Cuba, the "
                      "Dominican Republic, Ecuador, El Salvador, Guatemala, Guyana, Honduras, "
                      "Jamaica, Mexico, Panama, Suriname, Trinidad and Tobago and Venezuela "
                      "appear only through international and donor reporting, including Core "
                      "Indicator 93 of the Pan American Health Organization (PAHO), the count of "
                      "notified HIV cases reported by the ministries of health of the Americas."),
        "callout": ("Nicaragua enters the panel nationally, and the counts for the 19 local "
                    "health areas enter once archived copies of every area page are stored. "
                    "Belize is read for 2018, Bolivia for 2016, and Paraguay for 2000 to 2009, "
                    "the years before the PAHO series for Paraguay starts. The Argentine and "
                    "Peruvian sources revise past years at every release. Brazil's Ministry of "
                    "Health publishes on gov.br hosts, which the project does not query, "
                    "Colombia's national surveillance system (SIVIGILA) counts HIV cases, AIDS "
                    "cases and AIDS deaths together under event 850, and Mexico's national HIV "
                    "centre (CENSIDA) counts people on antiretroviral therapy (ART) per medicine "
                    "and excludes the social-security institutions. The Salvadoran and Jamaican "
                    "hosts refused or did not answer automated requests, the HIV items of "
                    "Trinidad and Tobago appear only in scanned files, and the national hosts of "
                    "Costa Rica, the Dominican Republic and Guatemala blocked automated requests "
                    "or refused access. The health ministry hosts of Ecuador and Paraguay did "
                    "not answer, the statistical bulletins of Guyana survive only in web "
                    "archives, the Honduran ministry report asks for a sign-in, and the "
                    "Venezuelan morbidity yearbooks count consultations, with the 2013 count at "
                    "55 per cent of the PAHO count for 2014. Cuba, Panama and Suriname publish "
                    "registered HIV or AIDS deaths from civil registration, a source class the "
                    "panel does not yet carry."),
    },
    "middle-east-and-north-africa": {
        "lede_tail": ("Lebanon is read at source, through the statistical bulletins of the "
                      "Ministry of Public Health. Algeria, Djibouti, Egypt, Iran, Iraq, "
                      "Jordan, Libya, Morocco, Palestine, Sudan, Syria, Tunisia and Yemen "
                      "appear only through international and donor reporting."),
        "callout": ("Lebanon enters the panel nationally, for 2007, 2009 and 2014 to 2018, "
                    "and the Lebanese bulletins for 2010, 2011 and 2013 count cases up to "
                    "November and are not read. The national hosts of Algeria, Iran, Jordan "
                    "and Palestine did not answer, the Iraqi health ministry host blocked "
                    "automated requests, and the statistics agencies of Djibouti and Egypt "
                    "serve JavaScript applications with no published table. The statistics "
                    "yearbook of Tunisia holds no HIV table, the Moroccan planning commission "
                    "gives only a cumulative count to 2014, and the Libyan disease control "
                    "centre lists branch offices only. The health ministry hosts of Sudan, "
                    "Syria and Yemen did not serve a page, and the regional health observatory "
                    "of the WHO Regional Office for the Eastern Mediterranean returned a "
                    "missing-page error."),
    },
}

# The words a country card and a country page carry when no national source has been read and
# COUNTRY_COPY has nothing written for the country. PEPFAR's provincial rows are named where
# they exist, because they are the only figures below the national level for such a country.
DEFAULT_BLURB = "International and donor reporting only."
DEFAULT_BLURB_SNU = "International and donor reporting, with PEPFAR's results by province."


# countries whose names take the article at the start of a sentence
WITH_ARTICLE = {"Central African Republic", "Dominican Republic", "Gambia", "Maldives",
                "Marshall Islands"}


def default_lede(name: str, has_snu: bool) -> str:
    lead = f"The {name}" if name in WITH_ARTICLE else name
    s = (f"{lead} appears only through international and donor bodies that compile figures "
         f"across many countries, and no figures for the country are read directly from a "
         f"national publisher.")
    if has_snu:
        s += (" PEPFAR's results for the country are broken down by province and count only the "
              "sites PEPFAR supports.")
    return s + (" The assessment of national sources, country by country, is set out on the "
                "Methods page.")

SCHEMA = [
    ("country_iso3", "ISO 3166-1 alpha-3 country code."),
    ("country_name", "Country name as used throughout the panel."),
    ("admin1", "Sub-national unit, where the source publishes a sub-national figure. Empty for national "
               "figures."),
    ("indicator_id", "Canonical indicator identifier, common across sources."),
    ("population_group", "Key population the figure refers to, or 'all'."),
    ("sex", "Sex the figure refers to, or 'all'."),
    ("age_group", "Age group the figure refers to, or 'all'."),
    ("year", "Reporting year. For United States disbursements the year is a fiscal year."),
    ("value", "The figure as published. Never rescaled, rounded or imputed."),
    ("value_lower", "Lower bound, where the source publishes an interval."),
    ("value_upper", "Upper bound, where the source publishes an interval."),
    ("unit", "count, percent, USD, or LCU (local currency units) for a figure published only "
             "in the national currency of the country, in which case extra.currency names the "
             "currency."),
    ("numerator", "Numerator behind a proportion, where the source gives the numerator."),
    ("denominator", "Denominator behind a proportion, where the source gives the denominator."),
    ("source_id", "Identifier of the source the row was read from."),
    ("source_type", "The kind of measurement the row records."),
    ("source_url", "Where the figure was read from."),
    ("source_indicator_code", "The source's own code for the indicator."),
    ("retrieved_at", "Date the figure was read."),
    ("extra", "Source-specific notes, including reporting-period and data-quality flags."),
]


# --- helpers -----------------------------------------------------------------------------
_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


def count_word(n, cap: bool = False) -> str:
    """A count as it should be written in a sentence: nought to nine in words, ten and above
    in figures. Tables, charts and the statistics rails are not sentences and keep their
    figures throughout, so this is only for prose."""
    try:
        i = int(n)
    except (TypeError, ValueError):
        return str(n)
    s = _WORDS[i] if 0 <= i <= 9 else f"{i:,}"
    return s[0].upper() + s[1:] if cap else s


def parse_extra(v) -> dict:
    if not isinstance(v, str) or not v.strip():
        return {}
    try:
        d = json.loads(v)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def us_fiscal_year(d: date) -> int:
    return d.year + 1 if d.month >= 10 else d.year


OPEN_FY = us_fiscal_year(date.today())


def instead_note(x, year) -> str:
    """The comparison that does hold, for a row whose annual total does not.

    Telling a reader that a number cannot be compared and stopping there leaves them holding
    the uncomparable number, which is the one they will use. The connector keeps the four
    quarterly values on every cumulative row precisely so the honest comparison can be stated
    here rather than pointed at.
    """
    lq = x.get("like_quarter_comparison") or {}
    ratio = lq.get("ratio")
    if not ratio or not lq.get("quarters"):
        return ""
    qs = ", ".join(lq["quarters"])
    move = ("unchanged" if 0.98 <= ratio <= 1.02 else
            f"down {round((1 - ratio) * 100)}%" if ratio < 1 else
            f"up {round((ratio - 1) * 100)}%")
    return (f" Comparing {qs} in {int(year)} with {qs} in {int(year) - 1}, the same months a "
            f"year apart, the reported figure is {move} ({fmt_int(lq['last_year'])} to "
            f"{fmt_int(lq['this_year'])}).")


def period_note(row) -> str | None:
    """Why this observation covers an incomplete reporting period, or None."""
    x = parse_extra(row.get("extra"))
    if x.get("partial_year"):
        base = str(x["partial_year"]).replace(
            " Use like_quarter_comparison instead.", "")
        return base + instead_note(x, row["year"])
    # A change of reporting frequency deliberately produces NO note here. The site charts
    # annual values, a semi-annual year is a whole year, and the annual totals either side of
    # such a change are comparable. Flagging those rows would mark correct data as suspect.
    # The `cadence_change` field stays in the panel's extra column for anyone reading quarters.
    # A connector that reports how many quarters the year is SUPPOSED to have has already
    # decided whether this row is short, and its answer stands. Counting to four here would
    # put the warning back on the semi-annual years the connector cleared, because PEPFAR
    # publishes some indicators twice a year and a two-quarter year is then a whole year.
    if x.get("quarters_expected") or x.get("release_quarters"):
        return None
    q = x.get("quarters_reported", x.get("n_quarters"))
    try:
        if q is not None and float(q) < 4:
            return (f"{count_word(float(q), cap=True)} of four quarters reported for "
                    f"{int(row['year'])}. The figure for {int(row['year'])} is a partial sum and "
                    f"is not comparable with a complete year")
    except (TypeError, ValueError):
        pass
    if row.get("source_id") == "foreign_assistance" and int(row["year"]) >= OPEN_FY:
        return (f"United States fiscal year {int(row['year'])} is still open, and disbursements "
                f"for fiscal year {int(row['year'])} are still being reported")
    return None


# The connectors write a data-quality flag as a terse note for an analyst, and the note stays
# in the panel exactly as written. The site shows the same facts as plain sentences, with
# every number carried over unchanged. A flag in any other wording is shown as written.
_JUMP = re.compile(r"^discontinuity vs (\d{4}): (-?[\d,]+) -> (-?[\d,]+)\. Likely a "
                   r"reporting-scope/partner-attribution change")
_OVER = re.compile(r"^ratio above 100% \(([\d.]+)%\): ([\d,]+) suppressed against a "
                   r"denominator of ([\d,]+) — numerator and denominator are not drawn "
                   r"from the same cohort in this unit-year$")


def quality_note(row) -> str | None:
    raw = parse_extra(row.get("extra")).get("data_quality_flag")
    if not raw:
        return raw
    year = int(row["year"])
    m = _JUMP.match(raw)
    if m:
        prev_year, prev, value = m.groups()
        return (f"The value moved from {prev} in {prev_year} to {value} in {year}, a change of "
                f"more than threefold in a single year. The move from {prev} to {value} is "
                f"likely to reflect a change in which organisations funded by PEPFAR report the "
                f"figures, or in the scope of the PEPFAR reporting, so the values for {prev_year} "
                f"and {year} are not comparable. Check the figures by reporting organisation "
                f"before reading a trend across {prev_year} and {year}.")
    m = _OVER.match(raw)
    if m:
        pct, num, den = m.groups()
        admin1 = row.get("admin1")
        place = f"{admin1} in {year}" if isinstance(admin1, str) and admin1 else str(year)
        return (f"The ratio of {num} people reported as virally suppressed to a denominator of "
                f"{den} is {pct} per cent, above 100 per cent, so the numerator and the "
                f"denominator do not come from the same group of patients for {place}.")
    return raw


def fmt_int(n) -> str:
    return f"{int(n):,}"


def stamp_of(path: Path) -> str:
    """A short mark taken from a file's own contents. See the note on the download links."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:10]


def size_of(path: Path) -> str:
    kb = path.stat().st_size / 1024
    return f"{kb/1024:.1f} MB" if kb >= 1024 else f"{max(1, round(kb)):.0f} KB"


def year_range(s) -> str:
    a, b = int(s.min()), int(s.max())
    return f"{a}" if a == b else f"{a}–{b}"


def host_of(url) -> str:
    if not isinstance(url, str) or not url:
        return ""
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def indicator_name(iid: str) -> str:
    spec = CANONICAL_INDICATORS.get(iid)
    return spec.name if spec else iid


def indicator_domain(iid: str) -> str:
    spec = CANONICAL_INDICATORS.get(iid)
    return spec.domain if spec else "other"


def indicator_unit(iid: str) -> str:
    spec = CANONICAL_INDICATORS.get(iid)
    return spec.unit if spec else ""


def source_name(sid: str) -> str:
    return SOURCE_META.get(sid, (sid, ""))[0]


def national(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["admin1"].fillna("") == ""]
    return d[(d["population_group"].fillna("all") == "all")
             & (d["sex"].fillna("all") == "all")
             & (d["age_group"].fillna("all") == "all")]


def series_for(df: pd.DataFrame, iso3: str | None, indicator: str, source: str | None = None,
               with_band: bool = False, min_points: int = 3) -> dict | None:
    """One country's series for one indicator from one source, as the chart wants it."""
    d = national(df)
    d = d[d["indicator_id"] == indicator]
    if iso3:
        d = d[d["country_iso3"] == iso3]
    if source:
        d = d[d["source_id"] == source]
    if d.empty:
        return None
    if not source:
        source = d["source_id"].value_counts().idxmax()
        d = d[d["source_id"] == source]
    d = d.sort_values("year").drop_duplicates("year", keep="last")
    if len(d) < min_points:
        return None
    pts, flags, band = [], [], []
    for _, r in d.iterrows():
        pts.append((int(r["year"]), float(r["value"])))
        flags.append(bool(period_note(r) or quality_note(r)))
        if with_band and pd.notna(r.get("value_lower")) and pd.notna(r.get("value_upper")):
            band.append((int(r["year"]), float(r["value_lower"]), float(r["value_upper"])))
    out = {"label": indicator_name(indicator), "points": pts, "flags": flags,
           "source": source, "unit": indicator_unit(indicator)}
    if len(band) == len(pts):
        out["band"] = band
    return out


def regional_series(df: pd.DataFrame, iso3s, indicator: str, source: str,
                    coverage: float = 0.7) -> dict | None:
    """
    Sum an indicator across a set of countries, keeping only the years in which enough of
    them report. Without that guard the early years of a donor series look like growth when
    they are only widening coverage.
    """
    d = national(df)
    d = d[(d["indicator_id"] == indicator) & (d["source_id"] == source)
          & (d["country_iso3"].isin(iso3s))]
    if d.empty:
        return None
    g = d.groupby("year").agg(value=("value", "sum"), n=("country_iso3", "nunique"))
    if g.empty:
        return None
    n_max = int(g["n"].max())
    bar = max(1, math.ceil(n_max * coverage))
    keep = g[g["n"] >= bar]
    if len(keep) < 3:
        return None
    flags = []
    for yr in keep.index:
        rows = d[d["year"] == yr]
        flags.append(any(period_note(r) for _, r in rows.iterrows()))
    kept = [int(y) for y in keep.index]
    dropped = sorted(int(y) for y in g.index if int(y) not in kept)
    # The note under a regional figure says which years were left out and why, so it is built
    # from the same numbers that decided the drawing and cannot drift from what is drawn.
    return {"label": indicator_name(indicator),
            "points": [(int(y), float(v)) for y, v in keep["value"].items()],
            "flags": flags, "source": source, "unit": indicator_unit(indicator),
            "n_countries": n_max, "n_scope": len(set(iso3s)), "bar": bar,
            "dropped": dropped,
            "gaps": [y for y in dropped if kept[0] < y < kept[-1]],
            "never": sorted(set(iso3s) - set(d["country_iso3"]))}


def join_years(years) -> str:
    """Years as a sentence lists them, with a run of three or more written as a span."""
    ys = sorted(set(int(y) for y in years))
    parts, i = [], 0
    while i < len(ys):
        j = i
        while j + 1 < len(ys) and ys[j + 1] == ys[j] + 1:
            j += 1
        if j - i >= 2:
            parts.append(f"{ys[i]} to {ys[j]}")
        else:
            parts.extend(str(y) for y in ys[i:j + 1])
        i = j + 1
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def join_names(names) -> str:
    names = list(names)
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


COVERAGE_RULE = ("A year is drawn only when the number of countries reporting reaches 70 per "
                 "cent of the highest number of countries reporting in any single year, because "
                 "a total built from a few countries is low for reasons unrelated to the level "
                 "of funding.")


def coverage_sentence(s: dict, who: str) -> str:
    """
    What the 70 per cent rule did to one regional series, in a sentence. `who` names the
    series inside the sentence, for example "the United States".
    """
    n, bar, scope = s["n_countries"], s["bar"], s["n_scope"]
    most = (f"all {count_word(scope)} countries report in at least one year" if n == scope
            else f"at most {count_word(n)} of the {count_word(scope)} countries report in any "
                 f"single year")
    first, last = s["points"][0][0], s["points"][-1][0]
    if not s["dropped"]:
        return (f"For {who}, {most}, and every year from {first} to {last} meets the minimum of "
                f"{count_word(bar)} countries.")
    k = len(s["dropped"])
    out = (f"For {who}, {most}, so the minimum is {count_word(bar)} countries, and "
           f"{join_years(s['dropped'])} {'falls' if k == 1 else 'fall'} below the minimum and "
           f"{'is' if k == 1 else 'are'} excluded.")
    if s["gaps"]:
        out += (f" The line for {who} therefore has a gap at {join_years(s['gaps'])}.")
    return out


def missing_sentence(named_series, what: str) -> str:
    """
    Names the countries a regional total excludes because the source has no figure for the
    countries. `named_series` pairs every series with the words that name the series total.
    """
    named_series = [(s, noun) for s, noun in named_series if s]
    sets = [tuple(s["never"]) for s, _ in named_series]
    if not any(sets):
        return ""
    if len(set(sets)) == 1:
        names = join_names(name_for(c) for c in sets[0])
        return (f" Every total in the figure excludes {names}, for which {what} publishes no "
                f"national figure.")
    out = ""
    for (s, noun), never in zip(named_series, sets):
        if never:
            names = join_names(name_for(c) for c in never)
            out += f" The total of {noun} excludes {names}, for which {what} publishes no figure."
    return out


def flag_sentence(series_list) -> str:
    """The note under a figure, naming any point drawn from an open reporting period."""
    marked = []
    for s in series_list:
        for (yr, _), f in zip(s["points"], s.get("flags") or []):
            if f:
                marked.append(str(yr))
    if not marked:
        return ""
    ys = sorted(set(marked))
    many = len(ys) > 1
    return (f' <span class="flagmark">{"The points" if many else "The point"} at '
            f'{join_names(ys)} {"are" if many else "is"} drawn from a reporting period that is '
            f'still open or that the source marks as incomplete, and {"are" if many else "is"} '
            f'shown as {"open rings" if many else "an open ring"}. A lower value at an open ring '
            f'may reflect incomplete reporting and should not be read as a fall.</span>')


# --- the numbers behind a drawing ---------------------------------------------------------
#
# A chart is an argument about a shape, and it is the right way to see whether external
# financing turned over in 2024. It is the wrong way to answer what the 2024 figure actually
# was, or to take three of these series into R. Both questions get asked of the same figure,
# so each one now carries its numbers as well as its drawing: a table the reader can switch
# to in place of the chart, and a file of the same numbers to take away.
#
# The two are built from one source. The series handed to the chart are the series written to
# the table and to the file, so the three cannot drift apart — a table maintained separately
# from the drawing above it is a table that is wrong by the second release.

def slug_of(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", sort_name(text).lower()).strip("-")[:64].rstrip("-")


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def figure_table(fig: dict) -> dict:
    """
    A figure's numbers in the two shapes its two uses want.

    On screen the reader wants the shape of the drawing: a row per year, a column per line,
    which is how the eye moved across the chart it replaced. A file taken away wants the
    shape an analysis wants: a row per observation, carrying its own series name and unit,
    so several of these files stack into one frame without reshaping. Neither shape is a
    substitute for the other, so both are produced here from the same series.

    A point the source marks as provisional is drawn as an open ring on the chart. It keeps
    that status in both shapes: marked in the table, and a column of its own in the file,
    because a value silently equal to a settled one is the way an open period ends up read
    as a fall.
    """
    unit = fig["unit"]
    long_cols = ["place", "figure", "year", "series", "value", "unit", "provisional"]

    if "cats" in fig:
        # one year, a row per question — the only figure on the site read across categories
        # instead of across time
        year = fig.get("year", "")
        head = [fig.get("x_name", "Category"), "Value"]
        body = [{"x": label, "cells": [{"t": charts.fmt_value(v, unit), "flag": False}]}
                for label, v in fig["cats"]]
        long = [{"year": year, "series": label, "value": v, "unit": unit, "provisional": ""}
                for label, v in fig["cats"]]
        # the row heading here is a question put to service users, not a year, and on a narrow
        # screen a question held to one line pushes its own answer off the edge
        return {"head": head, "body": body, "long": long, "long_cols": long_cols,
                "x_name": head[0], "x_wraps": True, "row_shape": "One row per category.",
                "n_rows": len(body), "flagged": False}

    series = fig["series"]
    years = sorted({y for s in series for y, _ in s["points"]})
    cols = []
    for s in series:
        flags = s.get("flags") or [False] * len(s["points"])
        cols.append({
            "label": s["label"],
            "vals": {y: v for y, v in s["points"]},
            "flags": {y: bool(f) for (y, _), f in zip(s["points"], flags)},
            "band": {y: (lo, hi) for y, lo, hi in s.get("band", [])},
        })

    head = ["Year"]
    for c in cols:
        head.append(c["label"])
        if c["band"]:
            head += [f'{c["label"]} (lower)', f'{c["label"]} (upper)']

    body, any_flag = [], False
    for y in years:
        cells = []
        for c in cols:
            v = c["vals"].get(y)
            flag = c["flags"].get(y, False)
            any_flag = any_flag or flag
            cells.append({"t": charts.fmt_value(v, unit) if v is not None else "—",
                          "flag": flag})
            if c["band"]:
                lo, hi = c["band"].get(y, (None, None))
                cells.append({"t": charts.fmt_value(lo, unit) if lo is not None else "—",
                              "flag": False})
                cells.append({"t": charts.fmt_value(hi, unit) if hi is not None else "—",
                              "flag": False})
        body.append({"x": str(y), "cells": cells})

    banded = any(c["band"] for c in cols)
    if banded:
        long_cols = long_cols + ["value_lower", "value_upper"]
    long = []
    for c in cols:
        for y in sorted(c["vals"]):
            row = {"year": y, "series": c["label"], "value": c["vals"][y], "unit": unit,
                   "provisional": "yes" if c["flags"].get(y) else ""}
            if banded:
                lo, hi = c["band"].get(y, (None, None))
                row["value_lower"], row["value_upper"] = lo, hi
            long.append(row)

    shape = "One row per year and series." if len(series) > 1 else "One row per year."
    return {"head": head, "body": body, "long": long, "long_cols": long_cols,
            "x_name": "Year", "x_wraps": False, "row_shape": shape,
            "n_rows": len(body), "flagged": any_flag}


def write_figure_files(fig: dict, table: dict, out: Path, place: str, slug: str,
                       built_on: str) -> dict:
    """
    The same numbers as a file, in the two formats a reader will already have a use for.

    The CSV is the one to build on and the .xlsx is the one to open. Both are here because
    neither can stand in for the other: a CSV opened in Excel on a machine set to a comma
    decimal separator arrives in a single column, and an .xlsx read into pandas needs a
    dependency the reader may not have. Neither is the awkward one for everybody, and which
    is awkward is not something the site can know.

    The reader's browser assembles nothing. Both files are written at build time, so what
    arrives came out of the same run that drew the chart, and a reader with scripting turned
    off is not left with a button that does nothing.
    """
    fdir = out / "downloads" / "figures"
    fdir.mkdir(parents=True, exist_ok=True)
    cols = table["long_cols"]
    rows = [{"place": place, "figure": fig["title"], **r} for r in table["long"]]

    csv_path = fdir / f"{slug}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    hrefs = {"csv": f"downloads/figures/{csv_path.name}?v={stamp_of(csv_path)}",
             "csv_size": size_of(csv_path)}

    if Workbook is None:
        return hrefs

    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(cols)
    for r in rows:
        ws.append([r.get(c) for c in cols])
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="left")
    ws.freeze_panes = "A2"
    for i, c in enumerate(cols, start=1):
        width = max(len(c), *(len(str(r.get(c, ""))) for r in rows)) if rows else len(c)
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(46, width + 3)

    # A file that leaves the site loses everything the page around the chart was saying, and
    # a column of numbers with no note on it is the raw material for a misreading. What the
    # figure said about itself travels with it.
    about = wb.create_sheet("About")
    for k, v in (("Figure", fig["title"]), ("Place", place), ("Source", fig["source"]),
                 ("Note", strip_tags(fig.get("note", ""))), ("Panel built", built_on),
                 ("From", SITE["url"]), ("Cite as", SITE["citation"])):
        about.append([k, v])
    for row in about.iter_rows(min_col=1, max_col=1):
        row[0].font = Font(bold=True)
    about.column_dimensions["A"].width = 14
    about.column_dimensions["B"].width = 100
    for row in about.iter_rows(min_col=2, max_col=2):
        row[0].alignment = Alignment(wrap_text=True, vertical="top")

    xlsx_path = fdir / f"{slug}.xlsx"
    wb.save(xlsx_path)
    hrefs["xlsx"] = f"downloads/figures/{xlsx_path.name}?v={stamp_of(xlsx_path)}"
    hrefs["xlsx_size"] = size_of(xlsx_path)
    return hrefs


def attach_figure_data(figs: list, place: str, place_slug: str, out: Path,
                       built_on: str) -> list:
    """Give every figure on a page its table, its two files and an id to be addressed by."""
    for i, fig in enumerate(figs, start=1):
        table = figure_table(fig)
        slug = f"{place_slug}-{slug_of(fig['title'])}"
        fig["id"] = f"fig-{i}"
        fig["slug"] = slug
        fig["table"] = table
        fig["dl"] = write_figure_files(fig, table, out, place, slug, built_on)
        fig.pop("series", None)
        fig.pop("cats", None)
    return figs


# --- page data ---------------------------------------------------------------------------
def build_stats(df, mou, pairs, cells) -> dict:
    flagged = sum(1 for _, r in df.iterrows() if period_note(r) or quality_note(r))
    explicit = sum(1 for _, r in df.iterrows()
                   if parse_extra(r.get("extra")).get("partial_year")
                   or parse_extra(r.get("extra")).get("data_quality_flag"))
    return {
        "n_obs": len(df), "n_obs_fmt": fmt_int(len(df)),
        "n_countries": df["country_iso3"].nunique(),
        "n_indicators": df["indicator_id"].nunique(),
        "n_sources": df["source_id"].nunique(),
        "n_types": df["source_type"].nunique(),
        "year_min": int(df["year"].min()), "year_max": int(df["year"].max()),
        "n_flagged": flagged, "n_flagged_explicit": explicit,
        "n_mou": len(mou),
        "n_mou_hiv": sum(1 for _, r in mou.iterrows() if mou_covers_hiv(r)),
        "n_mou_scoped": sum(1 for _, r in mou.iterrows() if mou_covers_hiv(r) is not None),
        # "3 October 2026", not "03 October 2026"
        "mou_retrieved": (f'{(d := pd.to_datetime(mou["retrieved_at"]).max()).day} {d:%B %Y}'
                          if len(mou) else ""),
        "built_on": f"{date.today().day} {date.today():%B %Y}",
        "built_year": date.today().year,
    }


PHOTO_DIR = ROOT / "site" / "static" / "img" / "photos"
PHOTO_EXT = (".webp", ".avif", ".jpg", ".jpeg", ".png")


def photo(slug: str) -> str:
    """
    Path to the photograph shown behind a segment, or "" if none has been placed yet.

    Every backdrop on the site works the same way and is optional by design: name a
    file after the segment's slug, put it in site/static/img/photos, and the build
    picks it up on its next run. A segment without one is drawn on plain metal, so the
    photographs can be added or replaced one at a time.

    The slug says what the segment is: region-southeast-asia, domain-financing,
    country-tha, rel-derived, panel-csv.
    """
    for ext in PHOTO_EXT:
        if (PHOTO_DIR / f"{slug}{ext}").exists():
            return f"static/img/photos/{slug}{ext}"
    return ""


def build_regions(df) -> list:
    out = []
    for r in REGIONS:
        # Indonesia is marked apart: community-led monitoring is read there, and no national
        # publisher is, so the rack must not call Indonesia read at source
        countries = [{"name": name_for(c), "built": c in AT_SOURCE,
                      "tag": ("" if c not in AT_SOURCE
                              else "AT SOURCE" if AT_SOURCE[c].endswith("at source")
                              else "COMMUNITY")} for c in r["iso3"]]
        countries.sort(key=lambda c: sort_name(c["name"]))
        item = {"slug": r["slug"], "name": r["name"], "status": r["status"],
                "phase": r["phase"], "phase_no": phase_no(r), "note": r["note"],
                "countries": countries,
                "n_countries": len(r["iso3"]), "photo": photo(f'region-{r["slug"]}')}
        d = df[df["country_iso3"].isin(r["iso3"])]
        if r["status"] == "live" and len(d):
            item.update(n_obs=fmt_int(len(d)), n_indicators=d["indicator_id"].nunique(),
                        years=year_range(d["year"]))
        out.append(item)
    return out


def build_categories(df) -> list:
    out = []
    for k, dom in enumerate(DOMAIN_ORDER):
        d = df[df["indicator_id"].map(indicator_domain) == dom]
        if d.empty:
            continue
        rep = d.groupby(["indicator_id", "source_id"]).size().idxmax()
        s = national(d)
        s = s[(s["indicator_id"] == rep[0]) & (s["source_id"] == rep[1])]
        vals = s.groupby("year")["value"].sum().sort_index().tolist()
        line, fill = charts.sparkline(vals)
        srcs = [source_name(x) for x in d["source_id"].value_counts().index[:3]]
        out.append({
            "slug": dom, "name": DOMAIN_LABEL[dom], "blurb": DOMAIN_BLURB[dom],
            "n": len(d), "n_fmt": fmt_int(len(d)),
            "n_indicators": d["indicator_id"].nunique(),
            "sources": srcs, "spark": line, "spark_fill": fill,
            "tone": "metal--plate" if k % 2 else "", "photo": photo(f"domain-{dom}"),
        })
    return out


def build_recon(pairs, cells, stats) -> dict:
    counts = pairs.groupby("relationship")["n_cells"].sum().to_dict() if len(pairs) else {}
    total = sum(counts.values()) or 1
    palette = {"derived": "#3A4F6B", "subset": "#4E6688",
               "independent": "#C9A464", "insufficient": "#262E37"}
    notes = {"derived": "the same estimate, republished",
             "subset": "sources that differ in scope",
             "independent": "separate measurement systems",
             "insufficient": "too few matched figures to classify"}
    stack = []
    for rel in ("derived", "subset", "independent", "insufficient"):
        n = counts.get(rel, 0)
        if not n:
            continue
        stack.append({"label": rel.capitalize(), "n": n, "n_fmt": fmt_int(n),
                      "pct": round(n / total * 100, 2), "colour": palette[rel],
                      "note": notes[rel]})
    n_div = int(cells["divergent"].sum()) if len(cells) else 0
    aside = int((cells["comparison_status"] != "comparable").sum()) if len(cells) else 0
    return {
        "n_total": total, "n_total_fmt": fmt_int(total),
        "derived_fmt": fmt_int(counts.get("derived", 0)),
        "subset_fmt": fmt_int(counts.get("subset", 0)),
        "independent_fmt": fmt_int(counts.get("independent", 0)),
        "insufficient": counts.get("insufficient", 0),
        "derived_pct": round(counts.get("derived", 0) / total * 100),
        "n_independent_pairs": int((pairs["relationship"] == "independent").sum()) if len(pairs) else 0,
        "n_pairs_total": len(pairs),
        "n_declared": int((pairs["basis"] == "declared").sum()) if len(pairs) else 0,
        "n_divergent": n_div, "n_set_aside": aside,
        "stack": stack,
        "thr": {"derived_band": "2%", "derived_share": "90%", "derived_med": "1%",
                "subset_dir": "90%", "subset_ratio": "0.90", "min_cells": "three",
                "divergence": "10%"},
    }


# The Basis column for the six pairs classified by our project from documents. Every other pair
# is classified by the statistical rule in reconcile.py, and pair_basis() writes the sentence for
# every other pair from the statistics in reconciliation_pairs.csv. The evidence column of the csv
# is research data and stays as reconcile.py writes the column.
DECLARED_BASIS = {
    ("global_fund_hiv_disbursements", "iati", "oecd_crs"): (
        "Classified by our project from documents. The Global Fund publishes the same "
        "disbursements to the IATI registry and to the OECD Creditor Reporting System, so "
        "agreement between the IATI and OECD figures is arithmetic and not corroboration. The "
        "IATI figures date a disbursement by transaction date and the OECD figures by reporting "
        "year, and the IATI figures count the whole value of an HIV grant or a combined HIV and "
        "tuberculosis grant, while the OECD figures count only the spending coded as HIV control."),
    ("on_art_count", "global_fund", "ne_annuaire"): (
        "Classified by our project from documents. The Global Fund result for Niger equals the "
        "national count of people on antiretroviral treatment in the Niger health yearbook "
        "exactly in five of the eight years from 2017 to 2024, so the Global Fund and the "
        "yearbook print the same count from the national HIV and hepatitis programme (PNLSH). "
        "The Global Fund figure is lower by 4,426 in 2018, higher by 842 in 2022 and lower by 12 "
        "in 2024, and the differences for 2018, 2022 and 2024 are recorded as findings."),
    ("on_art_count", "ne_annuaire", "unaids_aidsinfo"): (
        "Classified by our project from documents. The UNAIDS count of people on antiretroviral "
        "treatment in Niger is the WHO GHO count rounded to the nearest thousand in every year "
        "from 2013 to 2024, and the WHO GHO count equals the Niger health yearbook count in "
        "seven of the 12 years. The UNAIDS figure is therefore the national programme count, "
        "rounded, and agreement with the yearbook is duplication and not corroboration."),
    ("on_art_count", "ne_annuaire", "who_gho"): (
        "Classified by our project from documents. The national count of people on "
        "antiretroviral treatment in the Niger health yearbook equals the WHO GHO figure exactly "
        "in seven of the 12 years from 2013 to 2024, and two separate counts would not match "
        "exactly on a five-digit number. The yearbook and WHO GHO therefore print the same count "
        "from the national HIV and hepatitis programme (PNLSH). The WHO GHO figure is lower in "
        "2016, 2017, 2021 and 2022 and higher by 14 in 2024, and the differences in 2016, 2017, "
        "2021, 2022 and 2024 are recorded as findings."),
    ("pmtct_arv_count", "gn_annuaire", "unaids_aidsinfo"): (
        "Classified by our project from documents. The 2023 national count of pregnant women on "
        "antiretroviral drugs in the Guinea statistics yearbook, 3,802, equals the UNAIDS figure "
        "exactly, and two separate counts would not match exactly on a four-digit number. The "
        "yearbook and UNAIDS share only three years, and the yearbook figure is six per cent "
        "above the UNAIDS figure in 2022 and 16 per cent above in 2024. The differences for 2022 "
        "and 2024 are recorded as findings."),
    ("pmtct_arv_count", "gn_annuaire", "who_gho"): (
        "Classified by our project from documents. WHO GHO prints the same Guinea count of "
        "pregnant women on antiretroviral drugs as UNAIDS in every year, and the 2023 count in "
        "the Guinea statistics yearbook, 3,802, equals the WHO GHO figure exactly. The WHO GHO "
        "figures therefore carry the same national count as the UNAIDS figures, with the same "
        "differences from the yearbook in 2022 and 2024."),
}


def pair_basis(r) -> str:
    """The sentence in the Basis column of the reconciliation table for one source pair."""
    key = (r["indicator_id"], r["source_a"], r["source_b"])
    if key in DECLARED_BASIS:
        return DECLARED_BASIS[key]
    n_all = int(r["n_cells"])
    # Ruling R21 of research/rulings_2026-10-15.md. reconcile reads the statistics from the
    # matched figures with a point value from source a and from source b, and sets aside a figure
    # printed as a bound.
    n_pt = r.get("n_point_cells")
    n = int(n_pt) if n_pt is not None and pd.notna(n_pt) else n_all
    matched = f"{count_word(n)} matched figure{'' if n == 1 else 's'}"
    rel, med = r["relationship"], r["median_rel_diff"]
    # A pair in reconcile.DECLARED_RELATIONSHIPS and not in DECLARED_BASIS carries the statistics
    # sentence, and lead opens the sentence by saying our project classified the pair from
    # documents and not from the statistics.
    lead = "Classified by our project from documents. " if r.get("basis") == "declared" else ""
    k = n_all - n
    bound = (f" A further {count_word(k)} matched figure{'' if k == 1 else 's'} "
             f"{'is' if k == 1 else 'are'} printed by a source as a bound, for example <100, "
             f"and {'is' if k == 1 else 'are'} set aside.") if k > 0 else ""
    if rel == "insufficient" or pd.isna(med):
        return f"{lead}Only {matched}.{bound}"
    if rel == "derived":
        return (f"{lead}The two sources agree within 2 per cent on "
                f"{r['agree_share_within_2pct'] * 100:.0f} per cent of {matched}, with a median "
                f"difference of {med * 100:.2f} per cent.{bound}")
    if rel == "subset":
        a, b = source_name(r["source_a"]), source_name(r["source_b"])
        ratio = r["median_ratio_a_over_b"]
        small = a if ratio < 1 else b
        return (f"{lead}{small} gives the smaller figure on "
                f"{r['direction_consistency'] * 100:.0f} per cent of {matched}, and the median "
                f"ratio of the {a} figure to the {b} figure is {ratio:.2f}.{bound}")
    return (f"{lead}{matched[0].upper()}{matched[1:]}, with a median difference of "
            f"{med * 100:.1f} per cent.{bound}")


def live_regions() -> list:
    return [r for r in REGIONS if r["status"] == "live"]


def status_of(iso3: str) -> tuple:
    """The label and class a country carries on the status grid and the region page."""
    if iso3 in LEADS:
        return LEADS[iso3], "lead"
    if iso3 in AT_SOURCE:
        return AT_SOURCE[iso3], "ok"
    return "Aggregators only", "no"


def build_country_status(df, rel) -> list:
    """The status grid on the home page, one group for each published region."""
    groups = []
    for r in live_regions():
        rows = []
        for iso3 in r["iso3"]:
            label, cls = status_of(iso3)
            built = iso3 in AT_SOURCE
            rows.append({"name": name_for(iso3), "label": label, "cls": cls,
                         "tone": "" if built else "metal--dormant",
                         "photo": photo(f"country-{iso3.lower()}"),
                         "href": f"{rel}countries/{iso3.lower()}/"})
        # countries read at source first, then by name, so each group opens on what was built
        rows.sort(key=lambda c: (c["cls"] != "ok", sort_name(c["name"])))
        groups.append({"name": r["name"], "slug": r["slug"], "countries": rows})
    return groups


def last_run(points: list, flags: list, min_len: int = 3) -> tuple:
    """
    The last unbroken run of years in a series, of at least `min_len` years. The hero draws
    one continuous curve and would join across a year the regional rule left out, which draws
    a line through a year nobody measured.
    """
    runs, start = [], 0
    for i in range(1, len(points) + 1):
        if i == len(points) or points[i][0] != points[i - 1][0] + 1:
            runs.append((start, i))
            start = i
    for a, b in reversed(runs):
        if b - a >= min_len:
            return points[a:b], flags[a:b]
    return [], []


def build_hero(df) -> list:
    """Real series for the animated hero, each named in the caption as it is drawn."""
    out = []
    specs = [
        ("external_hiv_oda_us", "oecd_crs",
         "United States HIV disbursements to {}", "OECD Creditor Reporting System"),
        ("external_hiv_oda_us", "foreign_assistance",
         "United States HIV disbursements to {}, as the United States reports them",
         "ForeignAssistance.gov"),
        ("global_fund_hiv_disbursements", "oecd_crs",
         "Global Fund HIV disbursements to {}", "OECD Creditor Reporting System"),
        ("plhiv", "unaids_aidsinfo",
         "People living with HIV in {}", "UNAIDS AIDSinfo"),
        ("on_art_count", "unaids_aidsinfo",
         "People on antiretroviral treatment in {}", "UNAIDS AIDSinfo"),
    ]
    # one indicator across every region before the next indicator, so the hero moves between
    # regions as it plays and not through one region's five series in turn
    for ind, src, label, meta in specs:
        for r in live_regions():
            s = regional_series(df, r["iso3"], ind, src)
            if not s:
                continue
            pts, flags = last_run(s["points"], s["flags"])
            if not pts:
                continue
            unit = s["unit"]
            first, last = pts[0], pts[-1]
            out.append({
                "label": label.format(r["name"]),
                "meta": (f"{meta} · {first[0]}–{last[0]} · "
                         f"{charts.fmt_value(last[1], unit)} in {last[0]}"),
                "points": [[y, v] for y, v in pts],
                "flags": flags,
            })
    return out


def region_figures(df, iso3s, name: str) -> list:
    figs = []
    n_words = count_word(len(set(iso3s)))

    total = regional_series(df, iso3s, "external_hiv_oda_total", "oecd_crs")
    us = regional_series(df, iso3s, "external_hiv_oda_us", "oecd_crs")
    gf = regional_series(df, iso3s, "global_fund_hiv_disbursements", "oecd_crs")
    named = [(total, "All donors", "all donors combined"),
             (us, "United States", "the United States"),
             (gf, "The Global Fund", "the Global Fund")]
    band = [s for s, _, _ in named if s]
    if band:
        for s, label, _ in named:
            if s:
                s["label"] = label
        figs.append({
            "title": f"External HIV financing to {name}, by source of funds",
            "source": "OECD CRS · purpose code 13040",
            "svg": charts.line_chart(band, unit="USD"),
            "series": band, "unit": "USD",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(band)],
            "note": (f"Disbursements reported to the OECD by all donors, by the United States "
                     f"alone, and by the Global Fund, summed across the {n_words} countries of "
                     f"{name}. " + COVERAGE_RULE + " "
                     + " ".join(coverage_sentence(s, who) for s, _, who in named if s)
                     + missing_sentence(((total, "disbursements from all donors"),
                                         (us, "United States disbursements"),
                                         (gf, "Global Fund disbursements")), "the OECD")
                     + flag_sentence(band)),
        })

    a = regional_series(df, iso3s, "external_hiv_oda_us", "oecd_crs")
    b = regional_series(df, iso3s, "external_hiv_oda_us", "foreign_assistance")
    pair = [s for s in (a, b) if s]
    if len(pair) == 2:
        a["label"], b["label"] = "OECD reporting", "United States self-reporting"
        a_last, b_last = a["points"][-1][0], b["points"][-1][0]
        ends = (f"The OECD record ends in {a_last} and the self-reported record ends in "
                f"{b_last}. " if a_last != b_last else "")
        figs.append({
            "title": f"The same United States disbursements to {name}, recorded twice",
            "source": "OECD CRS · ForeignAssistance.gov",
            "svg": charts.line_chart(pair, unit="USD"),
            "series": pair, "unit": "USD",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(pair)],
            "note": (f"The two lines record the same United States HIV disbursements to {name}, "
                     "once as the United States reports the disbursements to the OECD and once "
                     "as the United States government publishes the disbursements on "
                     "ForeignAssistance.gov. The two records are compiled independently, so a "
                     "difference between the two lines is informative and does not come from "
                     "republication of the same figures. The self-reported record is filed by "
                     "United States fiscal year, which runs from October to September, and the "
                     "OECD record is filed by calendar year. " + ends
                     + "A year is kept in the OECD record or in the self-reported record only "
                     "when the number of countries reporting reaches 70 per cent of the highest "
                     "number of countries reporting in any single year. "
                     + coverage_sentence(a, "the OECD record") + " "
                     + coverage_sentence(b, "the self-reported record")
                     + flag_sentence(pair)),
        })

    plhiv = regional_series(df, iso3s, "plhiv", "unaids_aidsinfo")
    art = regional_series(df, iso3s, "on_art_count", "unaids_aidsinfo")
    epi = [s for s in (plhiv, art) if s]
    if epi:
        if plhiv:
            plhiv["label"] = "People living with HIV"
        if art:
            art["label"] = "People on antiretroviral treatment"
        cover = " ".join(coverage_sentence(s, who) for s, who in
                         ((plhiv, "people living with HIV"),
                          (art, "people on antiretroviral treatment"))
                         if s and s["dropped"])
        figs.append({
            "title": f"The epidemic and the treatment response in {name}",
            "source": "UNAIDS AIDSinfo",
            "svg": charts.line_chart(epi, unit="count"),
            "series": epi, "unit": "count",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(epi)],
            "note": ("Modelled estimates, summed across the countries of " + name + ". The gap "
                     "between the two lines is the number of people living with HIV who are not "
                     "on antiretroviral treatment, which is the figure most exposed to a change "
                     "in external financing."
                     + missing_sentence(((plhiv, "people living with HIV"),
                                         (art, "people on antiretroviral treatment")), "UNAIDS")
                     + (" " + cover if cover else "")
                     + flag_sentence(epi)),
        })
    return figs


def country_figures(df, iso3) -> list:
    figs = []
    d = df[df["country_iso3"] == iso3]

    fin = []
    fin_srcs = []
    for ind, src, lab in (("external_hiv_oda_total", "oecd_crs", "All donors"),
                          ("external_hiv_oda_us", "oecd_crs", "United States, OECD record"),
                          ("global_fund_hiv_disbursements", "oecd_crs", "The Global Fund"),
                          ("external_hiv_oda_us", "foreign_assistance",
                           "United States, self-reported")):
        s = series_for(d, iso3, ind, src)
        if s:
            s["label"] = lab
            fin.append(s)
            if src not in fin_srcs:
                fin_srcs.append(src)
    if fin:
        # Credit only the sources actually drawn. A country can be missing one side entirely —
        # OECD publishes nothing for it, or its SDMX service is down on the day of collection —
        # and a figure that names a source it did not draw from misattributes the data.
        src_label = {"oecd_crs": "OECD CRS", "foreign_assistance": "ForeignAssistance.gov"}
        both = len(fin_srcs) == 2
        figs.append({
            "title": "External HIV financing",
            "source": " · ".join(src_label[s] for s in fin_srcs),
            "svg": charts.line_chart(fin, unit="USD"),
            "series": fin, "unit": "USD",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(fin)],
            "note": ("Disbursements reported for the country. "
                     + ("The OECD record and the United States self-reported record are drawn "
                        "separately. The two records cover the same United States disbursements, "
                        "but the OECD record is filed by calendar year and the self-reported "
                        "record by United States fiscal year." if both else
                        "Only the {} record is available for the country, so the two independent "
                        "records of United States disbursements cannot be compared in the "
                        "figure.".format(src_label[fin_srcs[0]]))
                     + flag_sentence(fin)),
        })

    plhiv = series_for(d, iso3, "plhiv", "unaids_aidsinfo", with_band=True)
    art = series_for(d, iso3, "on_art_count", "unaids_aidsinfo")
    epi = [s for s in (plhiv, art) if s]
    if epi:
        if plhiv:
            plhiv["label"] = "People living with HIV"
        if art:
            art["label"] = "People on treatment"
        figs.append({
            "title": "People living with HIV and people on treatment",
            "source": "UNAIDS AIDSinfo",
            "svg": charts.line_chart(epi, unit="count"),
            "series": epi, "unit": "count",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(epi)],
            "note": ("Modelled estimates. The shaded area is the published uncertainty interval "
                     "around the number of people living with HIV, because a single estimate "
                     "without the interval would overstate the precision of the model."
                     + flag_sentence(epi)),
        })

    casc = []
    for ind, lab in (("know_status_pct", "Diagnosed"),
                     ("art_coverage_pct", "On treatment"),
                     ("community_viral_suppression_pct", "Virally suppressed")):
        s = series_for(d, iso3, ind, "unaids_aidsinfo")
        if s:
            s["label"] = lab
            casc.append(s)
    if casc:
        figs.append({
            "title": "The treatment cascade",
            "source": "UNAIDS AIDSinfo",
            "svg": charts.line_chart(casc, unit="percent", zero_base=False),
            "series": casc, "unit": "percent",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(casc)],
            "note": ("Every line is a percentage of all people living with HIV, so the three lines "
                     "share a denominator and can be compared directly. Viral suppression in the "
                     "figure is the share of all people living with HIV who are virally "
                     "suppressed, and not the narrower third 95 target, which counts only people "
                     "on treatment."
                     + flag_sentence(casc)),
        })

    # national programme record, where one is read at source. Nigeria is listed although
    # `ng_ndr` reads live snapshots and so holds one year per run, which is below
    # series_for's three-point minimum until three annual runs have accumulated. The
    # figure then appears without a further change here.
    # Niger's yearbooks give one count a year from 2013, and the 2015 edition is held back, so
    # the Niger line breaks at 2015. Cameroon, Guinea and Chad are read at source for two or
    # three years each, below the three-point minimum or on an indicator outside this figure,
    # and their figures stay in the indicator table until the series lengthen.
    src = {"THA": "th_hivhub", "PHL": "ph_doh_cascade", "NGA": "ng_ndr",
           "NER": "ne_annuaire"}.get(iso3)
    if src:
        prog = []
        for ind in ("on_art_count", "know_status_count", "viral_suppression_count",
                    "new_diagnoses", "prep_recipients"):
            s = series_for(d, iso3, ind, src)
            if s:
                prog.append(s)
        if prog:
            figs.append({
                "title": "The national programme record",
                "source": SOURCE_META[src][0],
                "svg": charts.line_chart(prog, unit="count"),
                "series": prog, "unit": "count",
                "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                           for i, s in enumerate(prog)],
                "note": ("Counts read directly from the national programme's own publication. The "
                         "counts come from a programme register and are not modelled estimates, "
                         "so the counts will not match the international series exactly."
                         + (" The 2015 yearbook is excluded because the age columns of the 2015 "
                            "yearbook do not add up to the national row, so the line has a gap at "
                            "2015." if iso3 == "NER" else "")
                         + flag_sentence(prog)),
            })

    if iso3 == "ZAF":
        th = []
        for ind, lab, band in (("plhiv", "People living with HIV", True),
                               ("on_art_count", "People on treatment", True)):
            s = series_for(d, iso3, ind, "za_thembisa", with_band=band)
            if s:
                s["label"] = lab
                th.append(s)
        if th:
            figs.append({
                "title": "The Thembisa model, national estimates",
                "source": SOURCE_META["za_thembisa"][0],
                "svg": charts.line_chart(th, unit="count"),
                "series": th, "unit": "count",
                "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                           for i, s in enumerate(th)],
                "note": ("South Africa's official HIV model, read directly from the workbooks the "
                         "University of Cape Town publishes. The shaded areas are the 95 per cent "
                         "uncertainty intervals of the Thembisa model. Only the years the model "
                         "fits to data are kept, so every Thembisa line ends at the last fitted "
                         "year and not at the last projected year." + flag_sentence(th)),
            })

    if iso3 == "KHM":
        d2 = df[(df["country_iso3"] == "KHM") & (df["source_id"] == "kh_nchads_copct")]
        for ind, title in (("kp_reached", "Key populations reached by outreach"),
                           ("kp_tested", "Key populations tested for HIV")):
            sub = d2[d2["indicator_id"] == ind]
            if sub.empty:
                continue
            series = []
            for grp, g in sub.groupby("population_group"):
                g = g.sort_values("year")
                if len(g) < 3:
                    continue
                series.append({
                    "label": grp.replace("_", " "),
                    "points": [(int(r["year"]), float(r["value"])) for _, r in g.iterrows()],
                    "flags": [bool(period_note(r)) for _, r in g.iterrows()],
                })
            if series:
                figs.append({
                    "title": title,
                    "source": "NCHADS Boosted CoPCT, quarterly",
                    "svg": charts.line_chart(series, unit="count"),
                    "series": series, "unit": "count",
                    "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                               for i, s in enumerate(series)],
                    "note": ("Quarterly programme counts summed to a year. Outreach and testing "
                             "depend more on donor funding than any other part of the HIV "
                             "response, so a change in funding is likely to appear first in "
                             "outreach and testing." + flag_sentence(series)),
                })

    if iso3 == "IDN":
        d2 = df[(df["country_iso3"] == "IDN") & (df["source_id"] == "clm_asia")]
        if not d2.empty:
            latest = int(d2["year"].max())
            rows = d2[d2["year"] == latest].sort_values("value", ascending=False)
            pts = [(indicator_name(r["indicator_id"]).removesuffix(" (CLM)"), float(r["value"]))
                   for _, r in rows.iterrows()]
            # the drawing cuts a long question short because the label has to fit beside the
            # bar. The table and the file are not short of room, so they take the whole
            # question — a truncated label is a drawing decision and not a fact about the data
            drawn = [(p[0][:34], p[1]) for p in pts]
            figs.append({
                "title": f"What service users reported, {latest}",
                "source": "CLM Asia · selected facilities",
                "svg": charts.bar_chart(drawn, unit="percent"),
                "cats": pts, "unit": "percent", "year": latest,
                "x_name": "Question put to service users",
                "legend": None,
                "note": ("Pooled responses from service users at a small number of facilities in "
                         "the Jakarta area. The responses come from selected facilities and are "
                         "not a national estimate, and whether a higher or a lower percentage "
                         "signals a problem differs from question to question."),
            })
    return figs


def build_country(df, iso3, stats, rel) -> dict:
    d = df[df["country_iso3"] == iso3]
    copy = COUNTRY_COPY.get(iso3, {})
    srcs = []
    for sid, g in d.groupby("source_id"):
        url = g["source_url"].dropna()
        u = url.iloc[0] if len(url) else ""
        srcs.append({"name": source_name(sid),
                     "type": SOURCE_TYPE_LABEL.get(g["source_type"].iloc[0],
                                                   g["source_type"].iloc[0]),
                     "n": fmt_int(len(g)), "n_ind": g["indicator_id"].nunique(),
                     "years": year_range(g["year"]), "url": u, "host": host_of(u),
                     "retrieved": str(pd.to_datetime(g["retrieved_at"]).max().date()),
                     "_n": len(g)})
    srcs.sort(key=lambda s: -s["_n"])

    inds = []
    for iid, g in d.groupby("indicator_id"):
        # The latest figure is a national one wherever a national figure exists. Taking the
        # last row of the whole group printed one province's value, or one funding agency's
        # share, as if it were the country's, once PEPFAR's provincial rows came into the panel.
        nat = national(g)
        if len(nat):
            last = nat.sort_values("year").iloc[-1]
            latest = f'{charts.fmt_value(last["value"], last["unit"])} ({int(last["year"])})'
        elif (g["admin1"].fillna("") == "").any():
            latest = f'By population group, sex or age only, to {int(g["year"].max())}'
        else:
            latest = f'Sub-national only, to {int(g["year"].max())}'
        inds.append({"name": indicator_name(iid),
                     "domain": DOMAIN_LABEL.get(indicator_domain(iid), "—"),
                     "unit": indicator_unit(iid), "n": len(g),
                     "years": year_range(g["year"]),
                     "sources": ", ".join(sorted(source_name(s) for s in g["source_id"].unique())),
                     "latest": latest,
                     "_d": DOMAIN_ORDER.index(indicator_domain(iid))
                     if indicator_domain(iid) in DOMAIN_ORDER else 99})
    inds.sort(key=lambda i: (i["_d"], i["name"]))

    keynums = []
    for ind, lab in (("plhiv", "People living with HIV"),
                     ("art_coverage_pct", "On antiretroviral treatment"),
                     ("external_hiv_oda_us", "United States HIV disbursements"),
                     ("external_hiv_oda_total", "External HIV financing, all donors")):
        n = national(d)
        n = n[n["indicator_id"] == ind]
        if n.empty:
            continue
        r = n.sort_values("year").iloc[-1]
        keynums.append({"value": charts.fmt_value(r["value"], r["unit"]),
                        "label": f'{lab}, {int(r["year"])}',
                        "source": source_name(r["source_id"]),
                        "tone": "metal--plate" if len(keynums) % 2 else ""})

    flags = []
    for _, r in d.iterrows():
        q = quality_note(r)
        if q:
            # a sub-national row names the province, or two flags on one indicator and year
            # read as the same flag twice
            a1 = r.get("admin1")
            where = f"{a1}, " if isinstance(a1, str) and a1 else ""
            flags.append({"what": f'{indicator_name(r["indicator_id"])}, {where}{int(r["year"])} '
                                  f'({source_name(r["source_id"])})',
                          "why": q})
    return {
        "iso3": iso3, "name": name_for(iso3),
        "lede": copy.get("lede") or default_lede(name_for(iso3),
                                                 (d["source_id"] == "pepfar_snu").any()),
        "n_obs": fmt_int(len(d)), "sources": srcs, "indicators": inds,
        "keynums": keynums, "flags": flags,
    }


# --- render ------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default=str(ROOT / "data/panel/hiv_panel.csv"))
    ap.add_argument("--out", default=str(ROOT / "site/dist"))
    args = ap.parse_args()

    panel_dir = Path(args.panel).parent
    out = Path(args.out)

    df = pd.read_csv(args.panel)
    df = df[df["value"].notna()].copy()
    mou = pd.read_csv(panel_dir / "mou_agreements.csv")
    pairs_p = panel_dir / "reconciliation_pairs.csv"
    pairs = pd.read_csv(pairs_p)
    cells_p = panel_dir / "reconciliation_cells.csv"
    cells = pd.read_csv(cells_p) if cells_p.exists() else pd.DataFrame()

    # The reconciliation page states which sources agree, and those verdicts are a reading of one
    # particular panel. A panel rewritten since the tables were built leaves the page publishing
    # verdicts about rows that are no longer there, which is worse than publishing nothing, because
    # a stale verdict looks exactly like a current one. This went unnoticed from 20 July 2026 until
    # the GAM expenditure connector added three pairs that never appeared on the page.
    stale_recon = pairs_p.stat().st_mtime < (panel_dir / "hiv_panel.csv").stat().st_mtime
    if stale_recon:
        print(f"  WARNING    {pairs_p.name} is older than the panel. The reconciliation page is "
              f"about to publish\n             verdicts from "
              f"{datetime.fromtimestamp(pairs_p.stat().st_mtime).date()} beside a panel from "
              f"{datetime.fromtimestamp((panel_dir / 'hiv_panel.csv').stat().st_mtime).date()}. "
              f"Rerun scripts/run_all.py,\n             or python3 -m hivimpact.reconcile, before "
              f"deploying.")

    stats = build_stats(df, mou, pairs, cells)
    SITE["citation"] = SITE["citation"].format(built=stats["built_on"])

    env = Environment(loader=FileSystemLoader(str(ROOT / "site/templates")),
                      autoescape=select_autoescape(["html"]), trim_blocks=True,
                      lstrip_blocks=True)
    # segments written out by hand in a template, and not looped over a list, look
    # their own backdrop up
    env.globals["photo"] = photo

    # The host tells a browser to keep the stylesheet and the scripts for a week. That is the
    # right instruction for a file whose address never changes, and the wrong one for ours,
    # because the address did not change when the file did: a reader who had been to the site
    # before kept the old stylesheet and saw the site as it looked at their last visit, for up
    # to seven days, with no sign that anything was being held back. The only way out was a
    # forced reload, which is not something a reader knows to do.
    #
    # The address now carries a stamp taken from the contents of the file, the same device the
    # downloads use below. Change the file and the stamp changes with it, so the address is one
    # the browser has never held a copy of and it fetches afresh; leave the file alone and the
    # address is unchanged and the week-long copy is used, which is what it is for.
    def asset(rel_path: str) -> str:
        src = ROOT / "site/static" / rel_path
        return f"static/{rel_path}?v={hashlib.sha256(src.read_bytes()).hexdigest()[:10]}"

    env.globals["asset"] = asset
    env.filters["count"] = count_word

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copytree(ROOT / "site/static", out / "static")

    (out / ".htaccess").write_text(HTACCESS)

    # downloads
    dl_dir = out / "downloads"
    dl_dir.mkdir()
    downloads = []
    n_rows = {"reconciliation_pairs.csv": len(pairs), "reconciliation_cells.csv": len(cells),
              "mou_agreements.csv": len(mou)}
    files = [(fn, desc, f"{n_rows.get(fn, len(df)):,} rows") for fn, desc in DOWNLOAD_FILES]
    for i, (fn, desc, rows) in enumerate(files):
        src = panel_dir / fn
        if not src.exists():
            continue
        shutil.copy2(src, dl_dir / fn)
        size = size_of(src)

        # The host keeps copies of these files on its edge servers, and a copy taken before the
        # server was told what a .csv is keeps calling it plain text, which is what makes a
        # browser save hiv_panel.csv under the name hiv_panel.txt. Such a copy can outlive the
        # correction by hours, and which edge server answers a given reader is chance, so the
        # fault comes and goes and looks like it has been fixed when it has not. The link
        # therefore carries a stamp taken from the contents of the file. When the file changes
        # the stamp changes with it, the address is one no edge server has seen, and the reader
        # is answered from the origin. The stamp is not part of the name the file is saved
        # under, which comes from the last part of the path.
        stamp = stamp_of(src)
        downloads.append({"file": fn, "desc": desc, "size": size, "rows": rows,
                          "href": f"downloads/{fn}?v={stamp}", "photo": photo(DL_PHOTO.get(fn, "")),
                          "tone": "metal--plate" if i % 2 else ""})

    def write(path: Path, tmpl: str, **ctx):
        # every link on a page is written against that page's own position in the folder tree,
        # which is what rel carries. A page one or more folders down reaches the home page
        # through its rel prefix; the home page itself has no prefix and points at its folder
        home = ctx.get("rel", "") or "./"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(env.get_template(tmpl).render(
            site=SITE, stats=stats, home=home,
            nav_regions=nav_regions(ctx.get("rel", "")), **ctx))

    # ---- home
    write(out / "index.html", "home.html", rel="", nav="home", paper=False,
          regions=build_regions(df),
          categories=build_categories(df),
          recon=build_recon(pairs, cells, stats),
          country_status=build_country_status(df, ""),
          hero_json=json.dumps(build_hero(df), separators=(",", ":")),
          provenance=build_provenance(stats))

    # ---- regions, and the countries of each
    for reg in live_regions():
        iso3s = reg["iso3"]
        d_r = df[df["country_iso3"].isin(iso3s)]
        countries = []
        for iso3 in iso3s:
            d = d_r[d_r["country_iso3"] == iso3]
            built = iso3 in AT_SOURCE
            has_snu = (d["source_id"] == "pepfar_snu").any()
            countries.append({
                "iso3": iso3, "name": name_for(iso3), "built": built,
                # the same label the status grid on the home page gives the country
                "status_label": status_of(iso3)[0],
                "blurb": (COUNTRY_COPY.get(iso3, {}).get("blurb")
                          or (DEFAULT_BLURB_SNU if has_snu else DEFAULT_BLURB)),
                "n_obs": fmt_int(len(d)), "n_indicators": d["indicator_id"].nunique(),
                "n_sources": d["source_id"].nunique(),
                "tone": "" if built else "metal--dormant",
                "photo": photo(f"country-{iso3.lower()}"),
            })
        # countries read at source first, then by name, as on the home page
        countries.sort(key=lambda c: (not c["built"], sort_name(c["name"])))

        reg_mou = mou[mou["country_iso3"].isin(iso3s)]
        mous = [{
            "country": name_for(r["country_iso3"]),
            "date": str(r["agreement_date"]),
            "total": charts.fmt_value(r["total_funding_usd"], "USD")
                     if pd.notna(r["total_funding_usd"]) else "not stated",
            "us": charts.fmt_value(r["us_funding_usd"], "USD")
                  if pd.notna(r["us_funding_usd"]) else "not stated",
            "co": charts.fmt_value(r["country_coinvestment_usd"], "USD")
                  if pd.notna(r["country_coinvestment_usd"]) else "not stated",
            "areas": r["programme_areas"] if mou_covers_hiv(r) is not None else "not stated",
            "hiv": {True: "Yes", False: "No", None: "not stated"}[mou_covers_hiv(r)],
            "scoped": mou_covers_hiv(r) is not None,
        } for _, r in reg_mou.sort_values("agreement_date").iterrows()]

        copy = REGION_COPY.get(reg["slug"], {})
        region = {"name": reg["name"], "slug": reg["slug"], "n_countries": len(iso3s),
                  "n_obs_fmt": fmt_int(len(d_r)), "n_sources": d_r["source_id"].nunique(),
                  "year_min": int(d_r["year"].min()), "year_max": int(d_r["year"].max()),
                  "lede_tail": copy.get("lede_tail", ""), "callout": copy.get("callout", "")}
        write(out / f'regions/{reg["slug"]}/index.html', "region.html", rel="../../",
              nav="region", paper=False, region=region,
              figures=attach_figure_data(region_figures(df, iso3s, reg["name"]), reg["name"],
                                         reg["slug"], out, stats["built_on"]),
              countries=countries, mous=mous)

        for iso3 in iso3s:
            c = build_country(df, iso3, stats, "../../")
            write(out / f"countries/{iso3.lower()}/index.html", "country.html",
                  rel="../../", nav="region", paper=False, region=region,
                  country=c, flags=c["flags"],
                  figures=attach_figure_data(country_figures(df, iso3), c["name"],
                                             slug_of(c["name"]), out, stats["built_on"]))

    # ---- reconciliation
    p = pairs.copy()
    order = {"independent": 0, "subset": 1, "derived": 2, "insufficient": 3}
    p["_o"] = p["relationship"].map(order).fillna(9)
    p = p.sort_values(["_o", "n_cells"], ascending=[True, False]).head(40)
    pair_rows = [{"indicator": indicator_name(r["indicator_id"]),
                  "a": source_name(r["source_a"]), "b": source_name(r["source_b"]),
                  "n": int(r["n_cells"]),
                  "med": (f'{r["median_rel_diff"]*100:.1f}%'
                          if pd.notna(r["median_rel_diff"]) else "—"),
                  "rel": r["relationship"], "basis": pair_basis(r)}
                 for _, r in p.iterrows()]

    cell_rows = []
    if len(cells):
        c = cells[cells["divergent"]].copy()
        c["_a"] = c["rel_diff"].abs()
        for _, r in c.sort_values("_a", ascending=False).head(40).iterrows():
            cell_rows.append({
                "country": name_for(r["country_iso3"]), "year": int(r["year"]),
                "indicator": indicator_name(r["indicator_id"]),
                "a": source_name(r["source_a"]), "b": source_name(r["source_b"]),
                "va": charts.fmt_value(r["value_a"], r["unit"]),
                "vb": charts.fmt_value(r["value_b"], r["unit"]),
                "rel": f'{r["rel_diff"]*100:+.0f}%',
                "colour": "#C4623F" if abs(r["rel_diff"]) > 0.5 else "#C9A464",
            })
    write(out / "reconciliation/index.html", "reconciliation.html", rel="../", nav="recon",
          paper=False, recon=build_recon(pairs, cells, stats), pairs=pair_rows, cells=cell_rows)

    # ---- data
    src_rows = []
    for sid, g in df.groupby("source_id"):
        url = g["source_url"].dropna()
        u = url.iloc[0] if len(url) else ""
        src_rows.append({"name": source_name(sid),
                         "type": SOURCE_TYPE_LABEL.get(g["source_type"].iloc[0],
                                                       g["source_type"].iloc[0]),
                         "n": fmt_int(len(g)), "n_countries": g["country_iso3"].nunique(),
                         "years": year_range(g["year"]), "url": u, "host": host_of(u),
                         "retrieved": str(pd.to_datetime(g["retrieved_at"]).max().date()),
                         "what": SOURCE_META.get(sid, ("", ""))[1], "_n": len(g)})
    src_rows.sort(key=lambda s: -s["_n"])

    # Two sources measuring one country-year are alternative readings, never two amounts to add
    # together. The lede says sources are not merged, which a reader can take as an invitation to
    # merge them, and on a money indicator the merge doubles the number. `global_fund_hiv_disbursements`
    # carries OECD CRS beside the country's own GAM return over 652 colliding rows, and a groupby on
    # country and year silently reports twice the money. So each indicator says how many of its rows
    # sit on a country-year another source also measured.
    overlap_key = [c for c in ("country_iso3", "population_group", "sex", "age_group", "year")
                   if c in df.columns]

    def overlapping_rows(g: pd.DataFrame) -> int:
        if g["source_id"].nunique() < 2:
            return 0
        per_cell = g.groupby(overlap_key, dropna=False)["source_id"].transform("nunique")
        return int((per_cell > 1).sum())

    groups = []
    for dom in DOMAIN_ORDER:
        rows = []
        for iid, g in df[df["indicator_id"].map(indicator_domain) == dom].groupby("indicator_id"):
            n_over = overlapping_rows(g)
            rows.append({"name": indicator_name(iid), "id": iid, "unit": indicator_unit(iid),
                         "n": len(g), "n_countries": g["country_iso3"].nunique(),
                         "years": year_range(g["year"]),
                         "n_overlap": n_over,
                         "overlap": (f"{fmt_int(n_over)} rows share a country and year with another "
                                     "source, so the rows are alternative measurements of the same "
                                     "figure and must not be added together") if n_over else "",
                         "sources": ", ".join(sorted(source_name(s)
                                                     for s in g["source_id"].unique()))})
        if rows:
            groups.append({"slug": dom, "name": DOMAIN_LABEL[dom], "blurb": DOMAIN_BLURB[dom],
                           "rows": sorted(rows, key=lambda r: -r["n"])})
    write(out / "data/index.html", "data.html", rel="../", nav="data", paper=False,
          downloads=downloads, schema=[{"f": f, "d": d} for f, d in SCHEMA],
          indicator_groups=groups, sources=src_rows)

    # ---- methods, about
    pep = df[(df["source_id"] == "pepfar_panorama")]
    pep_year = int(pep["year"].max()) if len(pep) else OPEN_FY - 1
    # How much of the latest PEPFAR year the release covers, and how much a full year is.
    # Both are taken from the release rather than fixed at four, because PEPFAR publishes
    # some indicators twice a year and four would be the wrong denominator for those.
    pep_q, pep_of = 1, 4
    if len(pep):
        latest = pep[pep["year"] == pep_year]
        here, prev = [], []
        for _, r in latest.iterrows():
            x = parse_extra(r.get("extra"))
            if x.get("release_quarters"):
                here.append(len(x["release_quarters"]))
            if x.get("comparison_year_quarters"):
                prev.append(len(x["comparison_year_quarters"]))
        if not here:
            qs = [q for q in (parse_extra(r.get("extra")).get("quarters_reported")
                              for _, r in latest.iterrows()) if q is not None]
            here = [int(min(float(q) for q in qs))] if qs else []
        pep_q = min(here) if here else 1
        pep_of = max(prev) if prev else 4
    write(out / "methods/index.html", "methods.html", rel="../", nav="methods", paper=True,
          sources=src_rows,
          feasibility=[{"country": c, "source": s, "access": a, "status": st, "built": b}
                       for c, s, a, st, b in FEASIBILITY],
          feasibility_regions=[{"slug": slug, "name": name, "summary": summary,
                                "rows": [{"country": c, "source": s, "access": a, "status": st,
                                          "built": b} for c, s, a, st, b in rows]}
                               for slug, name, summary, rows in FEASIBILITY_LATER
                               if slug in {r["slug"] for r in live_regions()}],
          flagpolicy={"open_fy": OPEN_FY, "pepfar_year": pep_year,
                      "pepfar_quarters": {1: "one", 2: "two", 3: "three"}.get(pep_q, str(pep_q)),
                      "pepfar_of": {2: "two", 3: "three", 4: "four"}.get(pep_of, str(pep_of))})
    write(out / "about/index.html", "about.html", rel="../", nav="about", paper=True)

    n = sum(1 for _ in out.rglob("*.html"))
    print(f"built {n} pages -> {out}")
    print(f"  panel        {stats['n_obs_fmt']} observations, {stats['n_sources']} sources, "
          f"{stats['year_min']}–{stats['year_max']}")
    print(f"  flagged      {stats['n_flagged']} rows from open or incomplete periods "
          f"({stats['n_flagged_explicit']} carry an explicit flag)")
    print(f"  open US FY   {OPEN_FY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
