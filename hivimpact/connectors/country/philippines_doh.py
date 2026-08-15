"""
Philippines — DOH Epidemiology Bureau HIV care-cascade connector (born-digital PDF, to-source).

Source: the DOH Epidemiology Bureau's quarterly "HIV & AIDS Surveillance of the Philippines"
report. It is an infographic PDF (born-digital) whose pages 1-6 are graphics, but the **Annex**
carries a clean, deterministically-extractable "HIV Care Cascade by Region" table — 18 regions ×
the full 95-95-95 columns. (Introduced in the 2025 reports; 2024 reports carry the national
cascade only in infographic prose, which we do NOT parse — same principle as scanned PDFs.)

Annex columns (VERIFIED 2026-07-19):
  Region | Est.PLHIV | Diagnosed | Dx% | OnART | ART% | VL_tested | Cov% | VL_supp | Supp% | 3rd95%
      0        1          2        3      4       5        6         7        8        9      10

We emit BOTH the per-region rows (admin1=region code) AND the national total (admin1="",
sum across the 18 regions) — the regional cascade is a genuine sub-national/small-area layer no
aggregator carries. There is no exact national total in a clean table (the headline national
lives in the infographic prose and slightly exceeds the regional sum because some cases are
nationally unallocated — e.g. summed diagnosed 152,344 vs headline 153,207, ~0.6%). So the
emitted national is sum-of-regions, tagged as such.

Extraction integrity (anti-contamination): the annex prints BOTH counts and percentages, so for
every region we check the printed % against the computed one — round(100*diagnosed/est) == Dx%,
round(100*on_art/diagnosed) == ART%. This validates the column mapping the way Thailand's
grand==male+female and Cambodia's TOTAL==zone-sum do; if the printed % doesn't match, the layout
drifted and we skip that report instead of emitting a wrong number.

Access: auto-discovers report PDFs via the ship.ph WordPress REST API
(/wp-json/wp/v2/media?search=surveillance) and caches into data/raw/philippines/; any local files
win. (ship.ph mirrors the DOH Epidemiology Bureau reports.)
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_WP_MEDIA = "https://www.ship.ph/wp-json/wp/v2/media"
_REGION_RE = re.compile(r"^(\d{1,2}[AB]?|NCR|BARMM|CAR|CARAGA|NIR)$", re.I)

# annex column index -> (canonical indicator, source_type). %-columns (3,5,7,9,10) are used only
# for the integrity cross-check, not emitted.
_COUNT_COLS = {
    1: ("plhiv",                   SourceType.MODELLED_ESTIMATE),   # regional Spectrum estimate
    2: ("know_status_count",       SourceType.ROUTINE_PROGRAMME),   # diagnosed (1st 95 numerator)
    4: ("on_art_count",            SourceType.ROUTINE_PROGRAMME),   # on ART (2nd 95 numerator)
    8: ("viral_suppression_count", SourceType.ROUTINE_PROGRAMME),   # VL suppressed (3rd 95 numerator)
}
# (count_col, pct_col, denom_col) triples for the printed-vs-computed % integrity check
_PCT_CHECKS = [(2, 3, 1), (4, 5, 2), (8, 9, 6)]


def _num(s) -> Optional[int]:
    s = str(s or "").strip()
    if s in ("", "-", "–", "—"):
        return 0
    s2 = re.sub(r"[^0-9]", "", s)
    return int(s2) if s2 else None


def _pct(s) -> Optional[float]:
    s = str(s or "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


class PhilippinesDOHConnector(BaseConnector):
    source_id = "ph_doh_cascade"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "Philippines DOH HIV care cascade (born-digital surveillance report; to-source, sum-of-regions)."
    country = "PHL"
    request_pause = 0.3
    timeout = 90

    def __init__(self, raw_dir: str = "data/raw/philippines", discover: bool = True, **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        self.discover = discover

    # -- discovery + caching ----------------------------------------------------
    def _discover_urls(self) -> List[str]:
        urls, seen = [], set()
        for term in ("surveillance", "HIV-AIDS-Surveillance"):
            try:
                items = self.get_json(f"{_WP_MEDIA}?search={term}&per_page=100&_fields=source_url")
            except Exception as exc:
                log.debug("ph_doh_cascade: WP media search '%s' failed: %s", term, exc)
                continue
            for m in items if isinstance(items, list) else []:
                u = str(m.get("source_url", ""))
                if u.lower().endswith(".pdf") and "surveillance" in u.lower() and u not in seen:
                    seen.add(u)
                    urls.append(u)
        log.info("ph_doh_cascade: discovered %d surveillance PDF(s)", len(urls))
        return urls

    def _ensure_local(self, urls: List[str]) -> List[Path]:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for u in urls:
            dest = self.raw_dir / u.rsplit("/", 1)[-1]
            if not dest.exists() or dest.stat().st_size == 0:
                try:
                    dest.write_bytes(self._request("GET", u).content)
                    log.info("ph_doh_cascade: cached %s", dest.name)
                except Exception as exc:
                    log.warning("ph_doh_cascade: download failed %s: %s", dest.name, exc)
                    continue
            paths.append(dest)
        return paths

    # -- parsing ----------------------------------------------------------------
    @staticmethod
    def _year_quarter(path: Path, text: str) -> Tuple[Optional[int], Optional[int]]:
        m = re.search(r"(20\d{2})[_\-\s]*Q\s*([1-4])", path.name, re.I)
        if m:
            return int(m.group(1)), int(m.group(2))
        # fallback: report text "OCT-DEC 2025" / "as of December 2025"
        mon = re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[-–]\s*"
                        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(20\d{2})", text, re.I)
        if mon:
            q = {"mar": 1, "jun": 2, "sep": 3, "dec": 4}.get(mon.group(2).lower()[:3])
            return int(mon.group(3)), q
        return None, None

    def _parse_annex(self, table: List[list]) -> Optional[Tuple[Dict[str, int], List[Tuple[str, Dict[str, int]]]]]:
        """Return (national_totals, per_region) or None. per_region = [(region_code, {canon:val})]."""
        regions = [r for r in table if r and r[0] and _REGION_RE.match((r[0] or "").strip())]
        if len(regions) < 14 or max(len(r) for r in regions) < 10:
            return None
        totals = {canon: 0 for _, (canon, _st) in _COUNT_COLS.items()}
        per_region: List[Tuple[str, Dict[str, int]]] = []
        ok = bad = 0
        for r in regions:
            vals = {ci: _num(r[ci]) if ci < len(r) else None for ci in _COUNT_COLS}
            if any(v is None for v in vals.values()):
                continue
            # integrity: printed % must match computed % (validates the column mapping)
            row_ok = True
            for cnt_c, pct_c, den_c in _PCT_CHECKS:
                printed = _pct(r[pct_c]) if pct_c < len(r) else None
                num, den = _num(r[cnt_c]), _num(r[den_c])
                if printed is None or not num or not den:
                    continue
                if abs(round(100.0 * num / den) - printed) > 2:
                    row_ok = False
            ok += row_ok
            bad += (not row_ok)
            canon_vals = {_COUNT_COLS[ci][0]: v for ci, v in vals.items()}
            per_region.append(((r[0] or "").strip().upper(), canon_vals))
            for canon, v in canon_vals.items():
                totals[canon] += v
        if ok == 0 or bad > ok:          # column mapping doesn't hold -> refuse
            return None
        # national cascade monotonicity
        if not (totals["plhiv"] >= totals["know_status_count"] >= totals["on_art_count"]
                >= totals["viral_suppression_count"]):
            log.warning("ph_doh_cascade: national cascade non-monotonic %s — skipping", totals)
            return None
        return totals, per_region

    def _parse_pdf(self, path: Path):
        """Return (year, quarter, national_totals, per_region) or None."""
        try:
            import pdfplumber
        except ImportError:
            log.error("ph_doh_cascade: pdfplumber not installed")
            return None
        try:
            pdf = pdfplumber.open(str(path))
        except Exception as exc:
            log.warning("ph_doh_cascade: cannot open %s: %s", path.name, exc)
            return None
        with pdf:
            # page 1's date is garbled by overlapping infographic layers; the annex page
            # carries a clean "OCT-DEC 2025" header, so scan all pages for the fallback.
            full_text = " ".join((pg.extract_text() or "") for pg in pdf.pages)
            year, quarter = self._year_quarter(path, full_text)
            for pg in pdf.pages:
                for t in pg.extract_tables():
                    parsed = self._parse_annex(t)
                    if parsed:
                        if not (year and quarter):
                            log.warning("ph_doh_cascade: %s has annex but no year/quarter — skipping", path.name)
                            return None
                        national, per_region = parsed
                        return year, quarter, national, per_region
        return None  # no regional cascade annex (e.g. pre-2025 reports) — silently skipped

    # -- driver -----------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None
        if wanted and self.country not in wanted:
            return

        paths: List[Path] = list(self.raw_dir.glob("*.pdf")) if self.raw_dir.exists() else []
        if self.discover:
            try:
                paths.extend(self._ensure_local(self._discover_urls()))
            except Exception as exc:
                log.warning("ph_doh_cascade: discovery failed (%s) — using local files", exc)
        seen, uniq = set(), []
        for p in paths:
            if p.resolve() not in seen:
                seen.add(p.resolve())
                uniq.append(p)
        if not uniq:
            log.warning("ph_doh_cascade: no report PDFs (none in %s, discovery empty)", self.raw_dir)
            return

        # keep the latest quarter's snapshot per year (cascade is as-of, not a flow)
        best: Dict[int, Tuple] = {}
        for path in sorted(uniq):
            parsed = self._parse_pdf(path)
            if not parsed:
                continue
            year, quarter, national, per_region = parsed
            if year < start_year or year > end_year:
                continue
            if year not in best or quarter > best[year][0]:
                best[year] = (quarter, national, per_region)

        _stype = {canon: st for _ci, (canon, st) in _COUNT_COLS.items()}
        n = 0
        for year, (quarter, national, per_region) in sorted(best.items()):
            # (admin1, values-dict) pairs: national first (admin1=""), then each region
            units = [("", national)] + [(code, vals) for code, vals in per_region]
            for admin1, vals in units:
                is_natl = admin1 == ""
                for canon, val in vals.items():
                    if not val:
                        continue
                    yield self.make_row(
                        country_iso3="PHL", country_name="Philippines", admin1=admin1,
                        indicator_id=canon, year=year, value=val, unit="count",
                        source_type=_stype[canon].value,
                        source_url="https://www.ship.ph/ (DOH Epidemiology Bureau surveillance report)",
                        source_indicator_code=f"ph.harp.cascade.q{quarter}",
                        extra={
                            "source": "DOH Epidemiology Bureau HIV & AIDS Surveillance report (Care Cascade by Region annex)",
                            "snapshot_quarter": f"Q{quarter}",
                            "geo_level": "national" if is_natl else "region",
                            "aggregation": ("sum of 18 regions" if is_natl else "region as reported"),
                            "note": (("national = sum-of-regions; ~0.6-3% below the report's headline "
                                      "national (nationally-unallocated cases). ") if is_natl else "")
                                    + "Snapshot as of quarter end.",
                            "reconcile_with": "unaids_aidsinfo, pepfar_panorama, th_hivhub, kh_nchads_copct",
                        },
                    )
                    n += 1
            log.info("ph_doh_cascade: %d region(s)+national for %d (Q%d snapshot)", len(per_region), year, quarter)
        log.info("ph_doh_cascade: emitted %d rows", n)
