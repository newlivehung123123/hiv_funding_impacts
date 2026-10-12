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


def nav_regions(rel: str) -> list:
    """
    The regions as the masthead and the footer list them.

    Every region is named, in the order the configuration sets, but only a published
    one carries a link. The rest are shown so the scope of the project is visible from
    any page, and they become links as their pages are built.
    """
    return [{"name": r["name"], "slug": r["slug"], "phase": r["phase"],
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
            "Population-based survey estimates."),
    "clm_asia": ("CLM Asia",
                 "Community-led monitoring of service access at a small number of selected "
                 "facilities in Indonesia."),
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
    "za_thembisa": ("Thembisa model, University of Cape Town",
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
    "td_annuaire": ("Chad health statistics yearbook",
                    "Antiretroviral treatment and viral load by province for 2023, with "
                    "national treatment starts and treatment of pregnant women for 2022."),
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
}

# The words a country card and a country page carry when no national source has been read and
# COUNTRY_COPY has nothing written for the country. PEPFAR's provincial rows are named where
# they exist, because they are the only figures below the national level for such a country.
DEFAULT_BLURB = "International and donor reporting only."
DEFAULT_BLURB_SNU = "International and donor reporting, with PEPFAR's results by province."


# countries whose names take the article at the start of a sentence
WITH_ARTICLE = {"Central African Republic", "Gambia"}


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
                "phase": r["phase"], "note": r["note"], "countries": countries,
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
    n = int(r["n_cells"])
    matched = f"{count_word(n)} matched figure{'' if n == 1 else 's'}"
    rel, med = r["relationship"], r["median_rel_diff"]
    if rel == "insufficient" or pd.isna(med):
        return f"Only {matched}."
    if rel == "derived":
        return (f"The two sources agree within 2 per cent on "
                f"{r['agree_share_within_2pct'] * 100:.0f} per cent of {matched}, with a median "
                f"difference of {med * 100:.2f} per cent.")
    if rel == "subset":
        a, b = source_name(r["source_a"]), source_name(r["source_b"])
        ratio = r["median_ratio_a_over_b"]
        small = a if ratio < 1 else b
        return (f"{small} gives the smaller figure on "
                f"{r['direction_consistency'] * 100:.0f} per cent of {matched}, and the median "
                f"ratio of the {a} figure to the {b} figure is {ratio:.2f}.")
    return f"{matched[0].upper()}{matched[1:]}, with a median difference of {med * 100:.1f} per cent."


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
