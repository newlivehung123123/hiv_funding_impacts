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

from hivimpact.config.countries import SEA_ISO3                      # noqa: E402
from hivimpact.config.indicators import CANONICAL_INDICATORS         # noqa: E402
from hivimpact.config.regions import REGIONS                         # noqa: E402
from hivimpact.normalize import name_for                             # noqa: E402

# site/charts.py is loaded by path: `site` is a standard-library module name, so importing
# the directory as a package would shadow it.
_spec = importlib.util.spec_from_file_location("hiv_site_charts", ROOT / "site" / "charts.py")
charts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(charts)

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
    return [{"name": r["name"],
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
                               "What each country reports spending on HIV, split by who paid "
                               "for it and by programme. The only near-global source for a "
                               "country's own account of PEPFAR and Global Fund money."),
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
                        "Results from PEPFAR-supported sites. A programme footprint, not a "
                        "national total."),
    "dhs": ("Demographic and Health Surveys",
            "Population-based survey estimates."),
    "clm_asia": ("CLM Asia",
                 "Community-led monitoring of service access at sentinel facilities in "
                 "Indonesia."),
    "th_hivhub": ("Thailand HIV Info Hub",
                  "The National AIDS Programme cascade, summed across 77 provinces."),
    "kh_nchads_copct": ("Cambodia NCHADS",
                        "Key-population outreach, testing and ART enrolment from the quarterly "
                        "Boosted CoPCT report."),
    "ph_doh_cascade": ("Philippines DOH Epidemiology Bureau",
                       "The 95-95-95 cascade by region, from the quarterly surveillance "
                       "report."),
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
                  "record and the United States self-reported record are kept separately "
                  "because they are the panel's one independent pair."),
    "cascade": ("Diagnosis, treatment and viral suppression. Modelled coverage estimates sit "
                "beside programme counts from national registers; the two measure different "
                "things and are not merged."),
    "epi": ("People living with HIV, new infections, deaths and prevalence. Almost all of this "
            "originates in one modelling exercise, whichever body publishes it."),
    "prevention": ("PrEP provision and key-population outreach. Outreach figures are period "
                   "flows summed to a year, not stocks."),
    "service_access": ("What service users report about stockouts, interruptions, staffing and "
                       "cost. A sentinel signal from a small number of facilities, not a "
                       "representative sample."),
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

# Countries whose national programme is read at source, and what route was used.
AT_SOURCE = {
    "THA": "Read at source",
    "KHM": "Read at source",
    "PHL": "Read at source",
    "IDN": "Community monitoring",
}

COUNTRY_COPY = {
    "THA": {
        "lede": ("Thailand's National AIDS Programme publishes through the HIV Info Hub, which "
                 "the pipeline queries directly. The national cascade runs a year further than "
                 "the international estimates, and where the two overlap they differ by about "
                 "eight per cent. That gap is what separates a programme register from a "
                 "modelled estimate, not an error in either."),
        "blurb": "National cascade read from the HIV Info Hub, 2021 onward.",
    },
    "KHM": {
        "lede": ("Cambodia's National Center for HIV/AIDS publishes a quarterly Boosted CoPCT "
                 "report whose tables can be read without interpretation. It carries what the "
                 "aggregators do not: outreach, testing, positivity and ART enrolment for each "
                 "key population, quarter by quarter. Cambodia has also signed a bilateral "
                 "agreement with the United States."),
        "blurb": "Key-population outreach and testing, quarterly, from NCHADS.",
    },
    "PHL": {
        "lede": ("The Department of Health's quarterly surveillance report carries a full "
                 "95-95-95 cascade for each of the 18 regions from 2025 onward. This is "
                 "richer than the country's annual submission to UNAIDS, which is why it is "
                 "worth reading at source. The Philippines has also signed a bilateral "
                 "agreement with the United States."),
        "blurb": "Regional 95-95-95 cascade, 18 regions, from the DOH quarterly report.",
    },
    "IDN": {
        "lede": ("Indonesia's national reporting system is not publicly reachable, so the "
                 "country appears through the aggregators. Alongside them sits a community-led "
                 "monitoring feed from sentinel facilities, which records what service users "
                 "report about stockouts, interruptions, staffing and out-of-pocket cost. It "
                 "is a small sample and is not nationally representative."),
        "blurb": "Aggregators, plus community-led monitoring of service access.",
    },
    "VNM": {
        "lede": ("Vietnam's national HIV portal has been unreachable throughout the assessment, "
                 "from several networks, and the case-surveillance system is restricted to "
                 "programme staff. Vietnam is therefore covered by the aggregator layer alone. "
                 "The position will be revisited if the portal returns."),
        "blurb": "Aggregators only. The national portal is offline.",
    },
    "MYS": {
        "lede": ("Malaysia publishes a national HIV report, but that report is the country's "
                 "submission to UNAIDS. Reading it at source would return figures the panel "
                 "already holds, so Malaysia is covered by the aggregator layer. The limit here "
                 "is redundancy, not access."),
        "blurb": "Aggregators only. The national report is the UNAIDS submission.",
    },
    "MMR": {
        "lede": ("Myanmar's National AIDS Programme reporting is not publicly accessible, and "
                 "monitoring has been disrupted since 2021. The country is covered by the "
                 "aggregator layer, and the figures should be read with that disruption in "
                 "mind."),
        "blurb": "Aggregators only. National reporting is closed.",
    },
    "LAO": {
        "lede": ("Laos runs a national cascade database, HIVCAM, which is not open to the "
                 "public. What is published is aggregated. An institutional data-sharing "
                 "arrangement is the realistic route to the underlying figures."),
        "blurb": "Aggregators only. HIVCAM is closed to public access.",
    },
    "TLS": {
        "lede": ("Timor-Leste moved to case-based surveillance on DHIS2 in 2023. The system has "
                 "an interface but it is expected to require credentials. The epidemic is small "
                 "and the aggregator record is correspondingly thin."),
        "blurb": "Aggregators only. DHIS2 access to be tested.",
    },
}

FEASIBILITY = [
    ("Thailand", "HIV Info Hub data mart, run by the Department of Disease Control",
     "Open and structured. Answers queries directly.", "Read at source", True),
    ("Cambodia", "NCHADS quarterly Boosted CoPCT report",
     "Open. Published tables, readable without interpretation.", "Read at source", True),
    ("Philippines", "DOH Epidemiology Bureau quarterly surveillance report",
     "Open. Regional cascade annex from 2025 onward.", "Read at source", True),
    ("Indonesia", "SIHA national reporting system; CLM Asia sentinel monitoring",
     "SIHA does not respond. The community monitoring feed is open.",
     "Community monitoring", True),
    ("Vietnam", "VAAC portal; HIV INFO 4.0 case surveillance",
     "Portal unreachable. Surveillance restricted to programme staff.", "Aggregators only", False),
    ("Malaysia", "data.gov.my; Ministry of Health country progress report",
     "Open, but the report is the UNAIDS submission already in the panel.",
     "Aggregators only", False),
    ("Laos", "CHAS; HIVCAM national cascade database",
     "Closed. Published output is aggregated.", "Access to be sought", False),
    ("Myanmar", "National AIDS Programme monitoring and evaluation",
     "Closed, and disrupted since 2021.", "Access to be sought", False),
    ("Timor-Leste", "DHIS2 case-based surveillance, introduced 2023",
     "Has an interface; expected to require credentials.", "Access to be sought", False),
]

SCHEMA = [
    ("country_iso3", "ISO 3166-1 alpha-3 country code."),
    ("country_name", "Country name as used throughout the panel."),
    ("admin1", "Sub-national unit, where the source publishes one. Empty for national figures."),
    ("indicator_id", "Canonical indicator identifier, common across sources."),
    ("population_group", "Key population the figure refers to, or 'all'."),
    ("sex", "Sex the figure refers to, or 'all'."),
    ("age_group", "Age group the figure refers to, or 'all'."),
    ("year", "Reporting year. For United States disbursements this is a fiscal year."),
    ("value", "The figure as published. Never rescaled, rounded or imputed."),
    ("value_lower", "Lower bound, where the source publishes an interval."),
    ("value_upper", "Upper bound, where the source publishes an interval."),
    ("unit", "count, percent or USD."),
    ("numerator", "Numerator behind a proportion, where the source gives one."),
    ("denominator", "Denominator behind a proportion, where the source gives one."),
    ("source_id", "Which connector produced the row."),
    ("source_type", "What kind of measurement it is."),
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
            f"year apart, this measure is {move} ({fmt_int(lq['last_year'])} to "
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
                    f"{int(row['year'])}; this is a partial sum and is not comparable with a "
                    f"complete year")
    except (TypeError, ValueError):
        pass
    if row.get("source_id") == "foreign_assistance" and int(row["year"]) >= OPEN_FY:
        return (f"United States fiscal year {int(row['year'])} is still open; disbursements "
                f"continue to be reported")
    return None


def quality_note(row) -> str | None:
    return parse_extra(row.get("extra")).get("data_quality_flag")


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
    keep = g[g["n"] >= max(1, math.ceil(g["n"].max() * coverage))]
    if len(keep) < 3:
        return None
    flags = []
    for yr in keep.index:
        rows = d[d["year"] == yr]
        flags.append(any(period_note(r) for _, r in rows.iterrows()))
    return {"label": indicator_name(indicator),
            "points": [(int(y), float(v)) for y, v in keep["value"].items()],
            "flags": flags, "source": source, "unit": indicator_unit(indicator),
            "n_countries": int(keep["n"].max())}


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
    plural = "Points" if len(ys) > 1 else "The point"
    return (f' <span class="flagmark">{plural} at {", ".join(ys)} '
            f'{"are" if len(ys) > 1 else "is"} drawn from a reporting period that is still '
            f'open or that the source marks as incomplete, and {"are" if len(ys) > 1 else "is"} '
            f'shown as an open ring. Do not read {"them" if len(ys) > 1 else "it"} as a '
            f'fall.</span>')


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
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:64].rstrip("-")


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
        "n_mou": len(mou), "n_mou_hiv": int(mou["covers_hiv"].sum()) if len(mou) else 0,
        "mou_retrieved": (pd.to_datetime(mou["retrieved_at"]).max().strftime("%d %B %Y")
                          if len(mou) else ""),
        "built_on": date.today().strftime("%d %B %Y"),
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
        countries = [{"name": name_for(c), "built": c in AT_SOURCE} for c in r["iso3"]]
        countries.sort(key=lambda c: c["name"])
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
             "subset": "different scope by construction",
             "independent": "separate measurement systems",
             "insufficient": "too few overlapping cells to classify"}
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
        "n_divergent": n_div, "n_set_aside": aside,
        "stack": stack,
        "thr": {"derived_band": "2%", "derived_share": "90%", "derived_med": "1%",
                "subset_dir": "90%", "subset_ratio": "0.90", "min_cells": "three",
                "divergence": "10%"},
    }


def build_country_status(df, rel) -> list:
    out = []
    for iso3 in SEA_ISO3:
        built = iso3 in AT_SOURCE
        label = AT_SOURCE.get(iso3, "Aggregators only")
        if iso3 in ("LAO", "MMR", "TLS"):
            label, cls = "Access to be sought", "lead"
        elif built:
            cls = "ok"
        else:
            cls = "no"
        out.append({"name": name_for(iso3), "label": label, "cls": cls,
                    "tone": "" if built else "metal--dormant",
                    "photo": photo(f"country-{iso3.lower()}"),
                    "href": f"{rel}countries/{iso3.lower()}/"})
    return out


def build_hero(df) -> list:
    """Real series for the animated hero, each named in the caption as it is drawn."""
    out = []
    specs = [
        ("external_hiv_oda_us", "oecd_crs",
         "United States HIV disbursements to Southeast Asia", "OECD Creditor Reporting System"),
        ("external_hiv_oda_us", "foreign_assistance",
         "The same flow, as the United States reports it", "ForeignAssistance.gov"),
        ("global_fund_hiv_disbursements", "oecd_crs",
         "Global Fund HIV disbursements to Southeast Asia", "OECD Creditor Reporting System"),
        ("plhiv", "unaids_aidsinfo",
         "People living with HIV in Southeast Asia", "UNAIDS AIDSinfo"),
        ("on_art_count", "unaids_aidsinfo",
         "People on antiretroviral treatment in Southeast Asia", "UNAIDS AIDSinfo"),
    ]
    for ind, src, label, meta in specs:
        s = regional_series(df, SEA_ISO3, ind, src)
        if not s:
            continue
        unit = s["unit"]
        first, last = s["points"][0], s["points"][-1]
        out.append({
            "label": label,
            "meta": (f"{meta} · {first[0]}–{last[0]} · "
                     f"{charts.fmt_value(last[1], unit)} in {last[0]}"),
            "points": [[y, v] for y, v in s["points"]],
            "flags": s["flags"],
        })
    return out


def region_figures(df) -> list:
    figs = []

    total = regional_series(df, SEA_ISO3, "external_hiv_oda_total", "oecd_crs")
    us = regional_series(df, SEA_ISO3, "external_hiv_oda_us", "oecd_crs")
    gf = regional_series(df, SEA_ISO3, "global_fund_hiv_disbursements", "oecd_crs")
    band = [s for s in (total, us, gf) if s]
    if band:
        labels = ["All donors", "United States", "The Global Fund"]
        for s, l in zip([total, us, gf], labels):
            if s:
                s["label"] = l
        figs.append({
            "title": "External HIV financing to Southeast Asia, by source of funds",
            "source": "OECD CRS · purpose code 13040",
            "svg": charts.line_chart(band, unit="USD"),
            "series": band, "unit": "USD",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(band)],
            "note": ("Disbursements reported to the OECD by all donors, by the United States "
                     "alone, and by the Global Fund, summed across the nine countries. A year "
                     "is drawn only when at least seven of the nine countries reported for "
                     "that year, because a total built from four or five countries is low for "
                     "a reason that has nothing to do with how much money was disbursed. For "
                     "all donors combined, all nine countries reported in every year. For the "
                     "United States, fewer than seven countries reported in 2002. For the "
                     "Global Fund, fewer than seven countries reported in 2003, 2004, 2006 and "
                     "2007, so its line is broken between 2005 and 2008 and 2005 is drawn as a "
                     "single point."
                     + flag_sentence(band)),
        })

    a = regional_series(df, SEA_ISO3, "external_hiv_oda_us", "oecd_crs")
    b = regional_series(df, SEA_ISO3, "external_hiv_oda_us", "foreign_assistance")
    pair = [s for s in (a, b) if s]
    if len(pair) == 2:
        a["label"], b["label"] = "OECD reporting", "United States self-reporting"
        figs.append({
            "title": "The same United States flow, recorded twice",
            "source": "OECD CRS · ForeignAssistance.gov",
            "svg": charts.line_chart(pair, unit="USD"),
            "series": pair, "unit": "USD",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(pair)],
            "note": ("These two records are the panel's one independent pair on funding: (1) "
                     "what the United States reports to the OECD, and (2) what it publishes "
                     "itself. Where they diverge, the divergence carries meaningful information "
                     "instead of being an artefact of republication. The self-reported series "
                     "runs later because it is filed on a fiscal year."
                     + flag_sentence(pair)),
        })

    plhiv = regional_series(df, SEA_ISO3, "plhiv", "unaids_aidsinfo")
    art = regional_series(df, SEA_ISO3, "on_art_count", "unaids_aidsinfo")
    epi = [s for s in (plhiv, art) if s]
    if epi:
        if plhiv:
            plhiv["label"] = "People living with HIV"
        if art:
            art["label"] = "People on antiretroviral treatment"
        figs.append({
            "title": "The epidemic and the treatment response",
            "source": "UNAIDS AIDSinfo",
            "svg": charts.line_chart(epi, unit="count"),
            "series": epi, "unit": "count",
            "legend": [{"label": s["label"], "colour": charts.STROKE_HEX[i % len(charts.STROKE_HEX)]}
                       for i, s in enumerate(epi)],
            "note": ("Modelled estimates for the nine countries combined. The gap between the "
                     "two lines is the treatment gap, and it is the quantity most exposed to a "
                     "change in external financing." + flag_sentence(epi)),
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
            "note": ("Disbursements reported for this country. "
                     + ("The OECD record and the United States self-reported record are drawn "
                        "separately; they cover the same flow but are filed on different "
                        "calendars." if both else
                        "Only the {} record is available for this country, so the two independent "
                        "records of the same flow cannot be compared here.".format(
                            src_label[fin_srcs[0]]))
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
            "note": ("Modelled estimates. The shaded band is the published uncertainty interval "
                     "around the number of people living with HIV; a point estimate on its own "
                     "would overstate what is known." + flag_sentence(epi)),
        })

    casc = []
    for ind, lab in (("know_status_pct", "Know their status"),
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
            "note": ("Each figure is a share of all people living with HIV, so the three lines "
                     "are on one denominator and can be read against each other. Suppression "
                     "here is community viral suppression, not the narrower third target."
                     + flag_sentence(casc)),
        })

    # national programme record, where one is read at source
    src = {"THA": "th_hivhub", "PHL": "ph_doh_cascade"}.get(iso3)
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
                "note": ("Counts from the national programme, read at source. These are register "
                         "figures, not modelled estimates, and they will not match the "
                         "international series exactly." + flag_sentence(prog)),
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
                    "note": ("Quarterly programme flows summed to a year. Outreach and testing "
                             "are the most donor-dependent parts of the response and so the "
                             "first place a funding change shows up." + flag_sentence(series)),
                })

    if iso3 == "IDN":
        d2 = df[(df["country_iso3"] == "IDN") & (df["source_id"] == "clm_asia")]
        if not d2.empty:
            latest = int(d2["year"].max())
            rows = d2[d2["year"] == latest].sort_values("value", ascending=False)
            pts = [(indicator_name(r["indicator_id"]).replace("CLM: ", ""), float(r["value"]))
                   for _, r in rows.iterrows()]
            # the drawing cuts a long question short because the label has to fit beside the
            # bar. The table and the file are not short of room, so they take the whole
            # question — a truncated label is a drawing decision and not a fact about the data
            drawn = [(p[0][:34], p[1]) for p in pts]
            figs.append({
                "title": f"What service users reported, {latest}",
                "source": "CLM Asia · sentinel facilities",
                "svg": charts.bar_chart(drawn, unit="percent"),
                "cats": pts, "unit": "percent", "year": latest,
                "x_name": "Question put to service users",
                "legend": None,
                "note": ("Pooled responses from service users at a small number of facilities in "
                         "the Jakarta area. This is a sentinel signal, not a national estimate, "
                         "and the direction that counts as bad differs by question."),
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
        last = g.sort_values("year").iloc[-1]
        inds.append({"name": indicator_name(iid),
                     "domain": DOMAIN_LABEL.get(indicator_domain(iid), "—"),
                     "unit": indicator_unit(iid), "n": len(g),
                     "years": year_range(g["year"]),
                     "sources": ", ".join(sorted(source_name(s) for s in g["source_id"].unique())),
                     "latest": f'{charts.fmt_value(last["value"], last["unit"])} ({int(last["year"])})',
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
            flags.append({"what": f'{indicator_name(r["indicator_id"])}, {int(r["year"])} '
                                  f'({source_name(r["source_id"])})',
                          "why": q})
    return {
        "iso3": iso3, "name": name_for(iso3),
        "lede": copy.get("lede", ""),
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
    files = [("hiv_panel.csv", "The full panel. One row is one figure from one source.",
              f"{len(df):,} rows"),
             ("hiv_panel.parquet", "The same panel, typed, for analysis.", f"{len(df):,} rows"),
             ("hiv_panel.sqlite", "The same panel as a queryable database.", f"{len(df):,} rows"),
             ("reconciliation_pairs.csv",
              "Every source pair, its inferred relationship and the evidence behind it.",
              f"{len(pairs):,} rows"),
             ("reconciliation_cells.csv",
              "Cell-level comparisons for independent pairs, with divergences flagged.",
              f"{len(cells):,} rows"),
             ("mou_agreements.csv",
              "Bilateral agreements signed under the America First Global Health Strategy.",
              f"{len(mou):,} rows")]
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
          provenance=[
              {"n": stats["n_obs_fmt"], "l": "observations, each with its source and the date "
                                             "it was read"},
              {"n": stats["n_sources"], "l": "sources, from international estimates to national "
                                             "programme registers"},
              {"n": stats["n_indicators"], "l": "indicators, on one common vocabulary"},
              {"n": f'{stats["year_min"]}–{stats["year_max"]}', "l": "years covered"},
              {"n": stats["n_mou_hiv"], "l": f'of {stats["n_mou"]} bilateral agreements signed '
                                             f'so far cover HIV', "hl": True},
          ])

    # ---- region
    sea_countries = []
    for iso3 in SEA_ISO3:
        d = df[df["country_iso3"] == iso3]
        built = iso3 in AT_SOURCE
        sea_countries.append({
            "iso3": iso3, "name": name_for(iso3), "built": built,
            "status_label": AT_SOURCE.get(iso3, "Aggregators only"),
            "blurb": COUNTRY_COPY.get(iso3, {}).get("blurb", ""),
            "n_obs": fmt_int(len(d)), "n_indicators": d["indicator_id"].nunique(),
            "n_sources": d["source_id"].nunique(),
            "tone": "" if built else "metal--dormant",
            "photo": photo(f"country-{iso3.lower()}"),
        })
    sea_mou = mou[mou["country_iso3"].isin(SEA_ISO3)]
    mous = [{
        "country": r["country_name"],
        "date": str(r["agreement_date"]),
        "total": charts.fmt_value(r["total_funding_usd"], "USD")
                 if pd.notna(r["total_funding_usd"]) else "not stated",
        "us": charts.fmt_value(r["us_funding_usd"], "USD")
              if pd.notna(r["us_funding_usd"]) else "not stated",
        "co": charts.fmt_value(r["country_coinvestment_usd"], "USD")
              if pd.notna(r["country_coinvestment_usd"]) else "not stated",
        "areas": r["programme_areas"] if pd.notna(r["programme_areas"]) else "—",
        "hiv": "Yes" if r["covers_hiv"] else "No",
    } for _, r in sea_mou.iterrows()]

    write(out / "regions/southeast-asia/index.html", "region.html", rel="../../", nav="sea",
          paper=False,
          region={"name": "Southeast Asia", "n_countries": len(SEA_ISO3)},
          figures=attach_figure_data(region_figures(df), "Southeast Asia", "southeast-asia",
                                     out, stats["built_on"]),
          countries=sea_countries, mous=mous)

    # ---- countries
    for iso3 in SEA_ISO3:
        c = build_country(df, iso3, stats, "../../")
        write(out / f"countries/{iso3.lower()}/index.html", "country.html",
              rel="../../", nav="sea", paper=False,
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
                  "rel": r["relationship"], "evidence": r["evidence"]}
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
                                     "source, so these are alternative measurements and must not be "
                                     "added together") if n_over else "",
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
