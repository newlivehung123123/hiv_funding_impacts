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
_BASE = "https://datawrapper.dwcdn.net"
_TRACKER_URL = ("https://www.kff.org/global-health-policy/"
                "kff-tracker-america-first-mou-bilateral-global-health-agreements/")
_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

MOU_COLUMNS = [
    "country_iso3", "country_name", "country_name_as_published",
    "agreement_date", "agreement_date_raw",
    "total_funding_usd", "us_funding_usd", "country_coinvestment_usd",
    "coinvestment_share_pct", "programme_areas", "covers_hiv",
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


def _read_rows(text: str) -> List[dict]:
    """Parse the dataset, tolerating the delimiter changing between versions (v1 was CSV,
    current is TSV) and the decorative super-header above the real header row."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    header_i = next((i for i, ln in enumerate(lines[:5]) if "Country Name" in ln), 0)
    body = "\n".join(lines[header_i:])
    delim = "\t" if body.count("\t") > body.count(",") else ","
    return list(csv.DictReader(io.StringIO(body), delimiter=delim))


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
        text = session.get(url, timeout=timeout).text
    except requests.RequestException as exc:
        log.warning("mou_tracker: dataset fetch failed: %s", exc)
        return []

    today = date.today().isoformat()
    out: List[dict] = []
    unmapped: List[str] = []
    for r in _read_rows(text):
        raw_name = _clean_name(r.get("Country Name"))
        # the source carries a "Total = N countries" summary row; it is not a signatory
        if not raw_name or raw_name.lower().startswith("total"):
            continue
        iso3 = to_iso3(raw_name)
        if not iso3:
            unmapped.append(raw_name)
            continue
        areas = str(r.get("Program Areas") or "").strip()
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
            "programme_areas": areas,
            "covers_hiv": bool(re.search(r"HIV", areas, re.I)),
            "source_url": _primary_url(r.get("Country")),   # State Dept release (primary)
            "tracker_url": _TRACKER_URL,                    # KFF (secondary)
            "retrieved_at": today,
        })
    if unmapped:
        log.warning("mou_tracker: %d country name(s) could not be mapped to ISO3: %s",
                    len(unmapped), ", ".join(sorted(set(unmapped))))
    log.info("mou_tracker: %d signatories (%d covering HIV)",
             len(out), sum(1 for x in out if x["covers_hiv"]))
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
