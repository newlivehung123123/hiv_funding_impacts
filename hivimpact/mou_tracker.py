"""
America First bilateral global-health MOUs — the policy EXPOSURE table.

Everything else in this repository measures consequences: funding flows, treatment counts,
stockouts, service disruption. This module captures the *instrument* presumed to cause them,
which is the second half of Adrian's question (bilateral-arrangement opacity: America First
replaced multilateral USAID flows with country-to-country MOUs, making funding hard to trace).

Source: the KFF tracker "America First MOU Bilateral Global Health Agreements", which renders
through Datawrapper. Datawrapper exposes the chart's underlying data at
    https://datawrapper.dwcdn.net/<chart>/<version>/dataset.csv
KFF is a SECONDARY source, so every row also carries the primary State Department release URL
that the tracker itself links (extracted from the anchor in the "Country" column).

Why this is a separate table, not panel rows: an MOU is an EVENT with a precise signing date,
a text scope, and *committed* (not disbursed) amounts. The panel's grain is one row per
country-indicator-year measurement; forcing an MOU into it would degrade the signing date to a
year and mix a policy instrument into a measurement table. Standard practice is an outcome
panel plus a treatment table joined on country_iso3, which is what this writes:
    data/panel/mou_agreements.csv   (join to hiv_panel.csv on country_iso3)

Analytical value: signing dates are STAGGERED across signatories, giving a dated treatment,
a treatment intensity (US committed funding, co-investment share), a scope flag (whether HIV
is in the MOU) and an untreated comparison group. Of direct relevance here, Cambodia
(2 Apr 2026) and the Philippines (7 Apr 2026) both signed, and both have country-level
to-source connectors in this pipeline with quarterly pre-signature baselines.

VERSION DISCOVERY: the current Datawrapper version must be discovered, never hardcoded. The
unversioned chart URL returns a redirect stub naming the live version. Note the chart id
contains a digit, so the version must be taken from a capture group, not a bare digit match.

PROGRAMME AREAS: versions 1 to 50 of the agreements chart (Kj5gQ) carry a "Program Areas"
column, and versions 51 and 52 do not. KFF now publishes the programme areas in a chart of
their own (IsvxV, "USG Global Health MOU Program Areas by Country"), with one Y or N column
per area. KFF codes the areas by keyword searches of press releases and agreement texts, so
the areas are KFF's coding and every row records the dataset version the areas came from.
"""
from __future__ import annotations

import csv
import io
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

from .normalize import name_for, to_iso3

log = logging.getLogger("hivimpact")

_CHART_ID = "Kj5gQ"
# the programme areas, one Y or N column per area ("HIV/AIDS", "TB", "Malaria", "Polio",
# "MCH", "GHS") and one row per signatory, keyed by a "Country" column
_AREAS_CHART_ID = "IsvxV"
_BASE = "https://datawrapper.dwcdn.net"
_TRACKER_URL = ("https://www.kff.org/global-health-policy/"
                "kff-tracker-america-first-mou-bilateral-global-health-agreements/")
_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

MOU_COLUMNS = [
    "country_iso3", "country_name", "country_name_as_published",
    "agreement_date", "agreement_date_raw",
    "total_funding_usd", "us_funding_usd", "country_coinvestment_usd",
    "coinvestment_share_pct", "programme_areas", "covers_hiv", "programme_areas_url",
    "source_url", "tracker_url", "retrieved_at",
]

_MONTHS = ("january february march april may june july august september october november december")


def _money(cell) -> Optional[float]:
    """Parse a funding cell; '-' and blanks mean not disclosed (None, never 0)."""
    s = re.sub(r"[^0-9.]", "", str(cell or ""))
    try:
        return float(s) if s else None
    except ValueError:
        return None


def _parse_date(raw: str) -> Optional[str]:
    """Return ISO date. Handles 4/2/2026, 12/23/25 and 'December 22, 2025 or December 23, 2025**'.
    Where the source gives two candidate dates, the earliest is taken and the raw text retained."""
    s = str(raw or "").strip()
    if not s or s in ("-", "–"):
        return None
    best: Optional[datetime] = None
    for m, d, y in re.findall(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", s):
        yr = int(y) + 2000 if len(y) == 2 else int(y)
        try:
            dt = datetime(yr, int(m), int(d))
        except ValueError:
            continue
        best = dt if best is None or dt < best else best
    if best is None:
        for mon, dd, yy in re.findall(r"([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})", s):
            if mon.lower() not in _MONTHS:
                continue
            try:
                dt = datetime.strptime(f"{mon[:3]} {dd} {yy}", "%b %d %Y")
            except ValueError:
                continue
            best = dt if best is None or dt < best else best
    return best.date().isoformat() if best else None


def _clean_name(cell) -> str:
    """Strip footnote markers ('Philippines***', 'Bolivia*') and whitespace."""
    return re.sub(r"[*†‡]+$", "", str(cell or "").strip()).strip()


def _primary_url(cell) -> str:
    """Extract the State Department release URL from the tracker's anchor markup."""
    m = re.search(r'href=["\']?(https?://[^"\'>\s]+)', str(cell or ""))
    return m.group(1) if m else ""


def discover_version(session: requests.Session, chart_id: str = _CHART_ID, timeout: int = 30) -> Optional[int]:
    """Resolve the live Datawrapper version. The unversioned URL returns a redirect stub naming
    it. The capture group is essential: the chart id itself contains a digit."""
    try:
        html = session.get(f"{_BASE}/{chart_id}/", timeout=timeout).text
    except requests.RequestException as exc:
        log.warning("mou_tracker: version discovery failed: %s", exc)
        return None
    m = re.search(rf"/{re.escape(chart_id)}/(\d+)/", html)
    return int(m.group(1)) if m else None


def _get_text(session: requests.Session, url: str, timeout: int) -> str:
    """Fetch a Datawrapper dataset as UTF-8. Datawrapper serves the datasets as
    application/octet-stream with no charset, so requests guesses the encoding, and on
    5 October 2026 the guess for the short programme-areas file turned "Côte d'Ivoire" into
    "CÃ´te d'Ivoire", which then failed to map to ISO3."""
    content = session.get(url, timeout=timeout).content
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        log.warning("mou_tracker: %s is not valid UTF-8, so the encoding is guessed", url)
        return content.decode("cp1252", errors="replace")


def _read_rows(text: str, key: str = "Country Name") -> List[dict]:
    """Parse the dataset, tolerating the delimiter changing between versions (v1 was CSV,
    current is TSV) and the decorative super-header above the real header row. `key` names a
    column of the real header row."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    header_i = next((i for i, ln in enumerate(lines[:5]) if key in ln), 0)
    body = "\n".join(lines[header_i:])
    delim = "\t" if body.count("\t") > body.count(",") else ","
    return list(csv.DictReader(io.StringIO(body), delimiter=delim))


def _areas_from_rows(rows: List[dict], url: str) -> Dict[str, dict]:
    """Programme areas per signatory from the rows of the programme-areas chart. A Y cell puts
    the area in `programme_areas`, in the published column order. `covers_hiv` is True for Y
    and False for N in the HIV column, and empty for any other cell, so an agreement is marked
    as excluding HIV only where KFF publishes N. A row with no Y at all is left empty, because
    an agreement with no area stated is unknown."""
    if not rows:
        return {}
    areas = [c for c in rows[0] if c and c.strip() != "Country"]
    hiv = [c for c in areas if re.search(r"HIV", c, re.I)]
    if len(hiv) != 1:
        log.warning("mou_tracker: the programme-areas dataset has %d HIV columns (%s), so the "
                    "programme areas are left empty", len(hiv), ", ".join(hiv) or "none")
        return {}
    out: Dict[str, dict] = {}
    unmapped: List[str] = []
    for r in rows:
        name = _clean_name(r.get("Country"))
        # the source closes on a "Total" row counting the Y cells; it is not a signatory
        if not name or name.lower().startswith("total"):
            continue
        iso3 = to_iso3(name)
        if not iso3:
            unmapped.append(name)
            continue
        cell = {c: str(r.get(c) or "").strip().upper() for c in areas}
        odd = sorted(c for c in areas if cell[c] not in ("Y", "N"))
        if odd:
            log.warning("mou_tracker: %s has a cell other than Y or N under %s",
                        name, ", ".join(odd))
        stated = "; ".join(c.strip() for c in areas if cell[c] == "Y")
        out[iso3] = {"programme_areas": stated,
                     "covers_hiv": {"Y": True, "N": False}.get(cell[hiv[0]]) if stated else None,
                     "programme_areas_url": url if stated else ""}
    if unmapped:
        log.warning("mou_tracker: %d programme-areas country name(s) could not be mapped to "
                    "ISO3: %s", len(unmapped), ", ".join(sorted(set(unmapped))))
    return out


def fetch_programme_areas(session: requests.Session, timeout: int = 45) -> Dict[str, dict]:
    """Read the KFF programme-areas chart at its live version. Returns {iso3: {programme_areas,
    covers_hiv, programme_areas_url}}, and an empty dict when the chart cannot be read."""
    version = discover_version(session, _AREAS_CHART_ID, timeout=timeout)
    if version is None:
        log.warning("mou_tracker: could not discover the programme-areas chart version")
        return {}
    url = f"{_BASE}/{_AREAS_CHART_ID}/{version}/dataset.csv"
    try:
        text = _get_text(session, url, timeout)
    except requests.RequestException as exc:
        log.warning("mou_tracker: programme-areas fetch failed: %s", exc)
        return {}
    out = _areas_from_rows(_read_rows(text, key="Country"), url)
    log.info("mou_tracker: programme-areas chart %s version %d lists %d signatories "
             "(%d covering HIV)", _AREAS_CHART_ID, version, len(out),
             sum(1 for x in out.values() if x["covers_hiv"]))
    return out


def fetch_agreements(timeout: int = 45) -> List[dict]:
    """Fetch and normalise the MOU table. Returns a list of dicts keyed by MOU_COLUMNS."""
    session = requests.Session()
    session.headers.update({"User-Agent": _UA})

    version = discover_version(session, timeout=timeout)
    if version is None:
        log.warning("mou_tracker: could not discover chart version — skipping")
        return []
    url = f"{_BASE}/{_CHART_ID}/{version}/dataset.csv"
    log.info("mou_tracker: using Datawrapper version %d", version)
    try:
        text = _get_text(session, url, timeout)
    except requests.RequestException as exc:
        log.warning("mou_tracker: dataset fetch failed: %s", exc)
        return []

    today = date.today().isoformat()
    out: List[dict] = []
    unmapped: List[str] = []
    rows = _read_rows(text)
    areas_by_iso3 = fetch_programme_areas(session, timeout=timeout)
    matched: set = set()
    # versions 51 and 52 carry no such column, and reading the absent column as "no HIV"
    # published 0 of 35 agreements covering HIV on 3 October 2026
    if rows and "Program Areas" not in rows[0] and not areas_by_iso3:
        log.warning("mou_tracker: version %d publishes no 'Program Areas' column and the "
                    "programme-areas chart returned nothing, so programme_areas and covers_hiv "
                    "are left empty", version)
    for r in rows:
        raw_name = _clean_name(r.get("Country Name"))
        # the source carries a "Total = N countries" summary row; it is not a signatory
        if not raw_name or raw_name.lower().startswith("total"):
            continue
        iso3 = to_iso3(raw_name)
        if not iso3:
            unmapped.append(raw_name)
            continue
        areas = str(r.get("Program Areas") or "").strip()
        # empty when the tracker states no programme areas: unknown, never False
        scope = {"programme_areas": areas,
                 "covers_hiv": bool(re.search(r"HIV", areas, re.I)) if areas else None,
                 "programme_areas_url": url if areas else ""}
        # the programme-areas chart is the current KFF table and wins over the old column
        found = areas_by_iso3.get(iso3)
        if found:
            matched.add(iso3)
            if areas and scope["covers_hiv"] != found["covers_hiv"]:
                log.warning("mou_tracker: %s covers HIV in one KFF chart and not in the other "
                            "(%r against %r), so the programme-areas chart is used",
                            iso3, areas, found["programme_areas"])
            scope = found
        raw_date = str(r.get("Agreement Date") or "").strip()
        out.append({
            "country_iso3": iso3,
            "country_name": name_for(iso3),
            "country_name_as_published": str(r.get("Country Name") or "").strip(),
            "agreement_date": _parse_date(raw_date),
            "agreement_date_raw": raw_date,
            "total_funding_usd": _money(r.get("Total Funding")),
            "us_funding_usd": _money(r.get("U.S. Funding")),
            "country_coinvestment_usd": _money(r.get("Country Co-Investment")),
            "coinvestment_share_pct": _money(r.get("Country Co-Investment Share")),
            **scope,
            "source_url": _primary_url(r.get("Country")),   # State Dept release (primary)
            "tracker_url": _TRACKER_URL,                    # KFF (secondary)
            "retrieved_at": today,
        })
    if unmapped:
        log.warning("mou_tracker: %d country name(s) could not be mapped to ISO3: %s",
                    len(unmapped), ", ".join(sorted(set(unmapped))))
    stray = sorted(set(areas_by_iso3) - matched)
    if stray:
        log.warning("mou_tracker: the programme-areas chart lists %d country(ies) the agreements "
                    "chart does not: %s", len(stray), ", ".join(stray))
    log.info("mou_tracker: %d signatories (%d covering HIV, %d with no programme areas stated)",
             len(out), sum(1 for x in out if x["covers_hiv"]),
             sum(1 for x in out if x["covers_hiv"] is None))
    return out


def write_mou_table(rows: List[dict], outdir: str | Path, basename: str = "mou_agreements") -> Optional[Path]:
    """Write the instrument table. Join to hiv_panel.csv on country_iso3."""
    if not rows:
        log.warning("mou_tracker: nothing to write")
        return None
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{basename}.csv"
    rows = sorted(rows, key=lambda r: (r["agreement_date"] or "9999", r["country_iso3"]))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MOU_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    log.info("mou_tracker: wrote %d agreements to %s", len(rows), path)
    return path


def run(outdir: str | Path = "data/panel") -> Optional[Path]:
    return write_mou_table(fetch_agreements(), outdir)


if __name__ == "__main__":   # python -m hivimpact.mou_tracker
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
