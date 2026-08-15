"""
Cambodia — NCHADS "Boosted CoPCT" key-population cascade connector (national programme, to-source).

Source: NCHADS (National Center for HIV/AIDS, Dermatology and STD) publishes a quarterly
"Boosted Continuum of Prevention to Care and Treatment (CoPCT)" report. NCHADS's ART and
VCCT quarterly reports are SCANNED images (no text layer — not machine-extractable without
OCR, which we don't do). The CoPCT report, by contrast, is BORN-DIGITAL with structured
tables, one page per key population (VERIFIED 2026-07-19 across 2023-Q1 … 2025-Q4):

    page 2 = Female entertainment workers (FEW)   -> sex_workers
    page 3 = Men who have sex with men (MSM)       -> gbmsm
    page 4 = Transgender (TG)                      -> transgender
    (page 1 = scanned cover; page 5 = "Key Populations" aggregate — both skipped)

Each page is a province table:
    Province | Reached | Tested | Reactive | Positive | ART enrolled | <age bands> | <syphilis>
with rows grouped [NORTHERN ZONE subtotal, its provinces, SOUTHERN ZONE subtotal, its
provinces, TOTAL]. We take the NATIONAL value from the printed **TOTAL** row (NCHADS's own
national figure) — never recomputed — guarded by an integrity check that
TOTAL == NORTHERN ZONE + SOUTHERN ZONE (analogous to the Thailand connector's
grand == male+female). Columns are located by HEADER NAME, not a fixed index, so the parse
survives minor layout drift; if a cascade column can't be found we bail instead of guessing.

The one born-digital artifact — stray spaces inside numbers ("8 23" -> "823",
"1 ,502" -> "1,502") — is stripped deterministically. No OCR, no prose parsing.

These are QUARTERLY FLOWS (reached/tested/positive/newly-enrolled during that quarter —
verified DISCRETE, not cumulative-YTD: 2025 ran 31,857 -> 57,228 -> 32,993 -> 27,091, i.e.
non-monotonic). Annual = sum of the available quarters, with n_quarters recorded so a
partial recent year (where the funding-cut signal lives) stays visible and interpretable.

Access: the connector auto-discovers the quarterly CoPCT PDFs from the NCHADS quarterly-
report category pages and caches them into `data/raw/nchads/`; any PDFs already there are
used as-is (a vetted/offline copy always wins). Pass discover=False for offline-only.

TAGGING: source_type = routine_programme_record. KEY-POPULATION programme data — the most
PEPFAR/Global-Fund-dependent services, hence the sharpest funding-cut signal.
"""
from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_SEX_WORKERS, POP_GBMSM, POP_TRANSGENDER

log = logging.getLogger("hivimpact")

# page-title keyword(s) -> population_group. First match wins.
_GROUP_PATTERNS = [
    (POP_SEX_WORKERS, ("female entertainment", "female entertain", "(few)")),
    (POP_GBMSM,       ("men who sex with men", "men who have sex", "(msm)")),
    (POP_TRANSGENDER, ("trangender", "transgender", "(tg)")),
]

# cascade column header keyword -> canonical indicator. "enrolled" uniquely tags "ART enrolled".
_COLS = [
    ("reached",  "kp_reached"),
    ("tested",   "kp_tested"),
    ("positive", "kp_hiv_positive"),
    ("enrolled", "kp_art_enrolled"),
]

_CATEGORY_TMPL = "https://www.nchads.gov.kh/category/quarterly-report-{year}-en/"
_PDF_RE = re.compile(r'https://www\.nchads\.gov\.kh/wp-content/uploads/[^"\'\s]+\.pdf', re.I)


# month-range -> quarter, for reports that print "(Oct-Dec)" without the "Q4" digit
_MONTH_Q = [(("jan", "mar"), 1), (("apr", "jun"), 2), (("jul", "sep"), 3), (("oct", "dec"), 4)]


def _detect_year_quarter(text: str, filename: str) -> Tuple[Optional[int], Optional[int]]:
    """Year+quarter from the page, robust to format drift: explicit 'Q<n>' first, then the
    month-range in the Quarter: line (e.g. '(Oct-Dec)' -> Q4), then the filename as a last
    resort. In-PDF 'Year:' is authoritative (filenames carry an unrelated upload-date prefix)."""
    low = text.lower()
    ym = re.search(r"year:\s*(\d{4})", low)
    year = int(ym.group(1)) if ym else None

    quarter = None
    qm = re.search(r"quarter:\s*q\s*([1-4])", low)
    if qm:
        quarter = int(qm.group(1))
    else:
        qline = re.search(r"quarter:\s*([^\n]*)", low)
        span = qline.group(1) if qline else ""
        quarter = next((q for (a, b), q in _MONTH_Q if a in span and b in span), None)

    fn = filename.lower()
    if quarter is None:
        fqm = re.search(r"q\s*-?\s*([1-4])", fn)   # e.g. "...Q4-2022.pdf"
        quarter = int(fqm.group(1)) if fqm else None
    if year is None:
        # strip the "YYYY_MM_" upload prefix so we don't read the upload date as the period
        stem = re.sub(r"^\d{4}_\d{2}_", "", fn)
        fym = re.search(r"(20\d{2})", stem)
        year = int(fym.group(1)) if fym else None
    return year, quarter


def _clean_int(s) -> Optional[int]:
    """Deterministic number cleaner: strip born-digital intra-number spaces/commas.

    "8 23" -> 823, "1 ,502" -> 1502, "-" -> 0. Returns None for a non-numeric
    cell (which flags the row, never silently coerces).
    """
    s = str(s or "").strip()
    if s in ("", "-", "‐", "–", "—", "N/A", "n/a", "."):
        return 0
    try:
        return int(re.sub(r"[\s,]", "", s))
    except ValueError:
        return None


class CambodiaNCHADSConnector(BaseConnector):
    source_id = "kh_nchads_copct"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "Cambodia NCHADS Boosted CoPCT — key-population cascade (to-source, quarterly->annual)."
    country = "KHM"
    request_pause = 0.3
    timeout = 90

    def __init__(self, raw_dir: str = "data/raw/nchads", discover: bool = True,
                 discover_years: Optional[Iterable[int]] = None, **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        self.discover = discover
        self.discover_years = (list(discover_years) if discover_years
                               else list(range(2022, date.today().year + 2)))

    # -- source discovery + caching --------------------------------------------
    def _discover_urls(self) -> List[str]:
        urls: List[str] = []
        seen = set()
        for year in self.discover_years:
            url = _CATEGORY_TMPL.format(year=year)
            try:
                html = self.get_text(url)
            except Exception as exc:                       # 404 for a non-existent year, etc.
                log.debug("kh_nchads_copct: category %s unavailable (%s)", year, exc)
                continue
            for m in _PDF_RE.findall(html):
                name = m.rsplit("/", 1)[-1].lower()
                if "copct" in name and m not in seen:      # matches English + Khmer-named files
                    seen.add(m)
                    urls.append(m)
        log.info("kh_nchads_copct: discovered %d CoPCT PDF(s) across category pages", len(urls))
        return urls

    @staticmethod
    def _local_name(url: str) -> str:
        # Flatten the post-/uploads/ path so files that share a basename but live under
        # different YYYY/MM upload folders don't collide (e.g. two 2023 KP-population PDFs).
        tail = url.split("/wp-content/uploads/", 1)[-1]
        return tail.replace("/", "_")

    def _ensure_local(self, urls: List[str]) -> List[Path]:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        paths: List[Path] = []
        for u in urls:
            dest = self.raw_dir / self._local_name(u)
            if not dest.exists() or dest.stat().st_size == 0:
                try:
                    resp = self._request("GET", u)
                    dest.write_bytes(resp.content)
                    log.info("kh_nchads_copct: cached %s (%d bytes)", dest.name, len(resp.content))
                except Exception as exc:
                    log.warning("kh_nchads_copct: failed to download %s: %s", dest.name, exc)
                    continue
            paths.append(dest)
        return paths

    # -- table parsing ----------------------------------------------------------
    def _parse_table(self, table: List[list]) -> Optional[Dict[str, int]]:
        """Return the national cascade dict from the printed TOTAL row, or None if the
        table fails structural integrity (so we emit nothing and not a wrong number)."""
        header_i = next((i for i, row in enumerate(table[:5])
                         if any("reached" in str(c or "").lower() for c in row)), None)
        if header_i is None:
            return None
        header = [str(c or "").lower() for c in table[header_i]]
        colmap: Dict[str, int] = {}
        for kw, canon in _COLS:
            ci = next((j for j, cell in enumerate(header) if kw in cell), None)
            if ci is not None:
                colmap[canon] = ci
        if len(colmap) != len(_COLS):                      # a cascade column missing -> bail
            return None

        total_row: Optional[Dict[str, int]] = None
        zone_sum = {canon: 0 for _, canon in _COLS}
        zones_found = False
        for row in table[header_i + 1:]:
            label = str(row[0] or "").strip().upper()
            if not label:
                continue
            vals: Optional[Dict[str, int]] = {}
            for canon, ci in colmap.items():
                v = _clean_int(row[ci]) if ci < len(row) else None
                if v is None:
                    vals = None
                    break
                vals[canon] = v
            if vals is None:
                continue                                   # non-numeric cell -> skip this row
            if label == "TOTAL":
                total_row = vals
            elif "ZONE" in label:
                zones_found = True
                for canon in zone_sum:
                    zone_sum[canon] += vals[canon]
        if total_row is None:
            return None
        # integrity: the printed TOTAL must equal the sum of the zone subtotals. Guards
        # against column misalignment / layout drift. (Skip only if zones were present.)
        if zones_found and any(total_row[c] != zone_sum[c] for _, c in _COLS):
            log.warning("kh_nchads_copct: TOTAL != zone-sum (%s vs %s) — layout drift, skipping page",
                        total_row, zone_sum)
            return None
        # soft cascade sanity (kept, but flagged): reached >= tested >= positive
        if not (total_row["kp_reached"] >= total_row["kp_tested"] >= total_row["kp_hiv_positive"]):
            log.warning("kh_nchads_copct: non-monotonic cascade %s — kept but flagged", total_row)
        return total_row

    def _parse_pdf(self, path: Path) -> Iterator[Tuple[str, int, int, Dict[str, int]]]:
        try:
            import pdfplumber
        except ImportError:
            log.error("kh_nchads_copct: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            pdf = pdfplumber.open(str(path))
        except Exception as exc:
            log.warning("kh_nchads_copct: cannot open %s: %s", path.name, exc)
            return
        with pdf:
            usable = 0
            for pg in pdf.pages:
                text = pg.extract_text() or ""
                if "copct for" not in text.lower():
                    continue
                low = text.lower()
                group = next((g for g, kws in _GROUP_PATTERNS if any(k in low for k in kws)), None)
                if group is None:                          # "Key Populations" aggregate page -> skip
                    continue
                year, quarter = _detect_year_quarter(text, path.name)
                if not (year and quarter):
                    log.warning("kh_nchads_copct: %s (%s) missing year/quarter — skipping", path.name, group)
                    continue
                tables = pg.extract_tables()
                if not tables:
                    continue
                national = self._parse_table(max(tables, key=len))
                if national is None:
                    log.warning("kh_nchads_copct: %s %s %d-Q%d failed integrity — skipping",
                                path.name, group, year, quarter)
                    continue
                usable += 1
                yield group, year, quarter, national
            if usable == 0:
                # e.g. a scanned CoPCT PDF (no text layer) — visible, not silently dropped
                log.warning("kh_nchads_copct: %s yielded no born-digital CoPCT tables "
                            "(scanned image?) — skipped", path.name)

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
                log.warning("kh_nchads_copct: discovery failed (%s) — using local files only", exc)
        # dedupe by resolved path
        seen, uniq = set(), []
        for p in paths:
            rp = p.resolve()
            if rp not in seen:
                seen.add(rp)
                uniq.append(p)
        paths = sorted(uniq)
        if not paths:
            log.warning("kh_nchads_copct: no CoPCT PDFs (none in %s, discovery empty)", self.raw_dir)
            return

        # aggregate discrete quarterly flows -> annual, per (population_group, indicator, year)
        agg: Dict[Tuple[str, str, int], Dict] = {}
        for path in paths:
            for group, year, quarter, national in self._parse_pdf(path):
                if year < start_year or year > end_year:
                    continue
                for canon, v in national.items():
                    b = agg.setdefault((group, canon, year), {"value": 0, "quarters": set()})
                    if quarter in b["quarters"]:
                        continue                           # same quarter seen twice (dup file)
                    b["value"] += v
                    b["quarters"].add(quarter)

        n = 0
        for (group, canon, year), b in sorted(agg.items()):
            quarters = sorted(b["quarters"])
            yield self.make_row(
                country_iso3="KHM", country_name="Cambodia",
                indicator_id=canon, year=year, value=b["value"], unit="count",
                population_group=group,
                source_url="https://www.nchads.gov.kh/",
                source_indicator_code=f"nchads.copct.{canon}",
                extra={
                    "source": "NCHADS Boosted CoPCT quarterly report (national TOTAL row)",
                    "population": group,
                    "quarters_included": quarters,
                    "n_quarters": len(quarters),
                    "aggregation": "sum of discrete quarterly flows",
                    "reconcile_with": "unaids_aidsinfo (key populations), pepfar_panorama",
                    "note": ("KEY-POPULATION programme flow; annual = sum of available quarters "
                             f"({len(quarters)}/4 present for {year})"),
                },
            )
            n += 1
        log.info("kh_nchads_copct: emitted %d rows from %d PDF(s)", n, len(paths))
