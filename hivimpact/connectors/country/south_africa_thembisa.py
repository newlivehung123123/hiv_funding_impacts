"""
South Africa — Thembisa model outputs (national + provincial HIV estimates).

Thembisa is the model that produces South Africa's official national and provincial HIV
estimates. It is run academically (Leigh Johnson and colleagues, UCT) and published as
open, versioned Excel workbooks at https://www.thembisa.org/downloads — no registration,
no login, no bot blocking. In the access-ladder terms of docs/ACCESS_LADDER.md this is a
**grade 1** country-side source, and as of the 2026-08-03 probe it is the only one found
in Africa: every other national portal probed was either a DHIS2 login wall or a host
serving an invalid TLS certificate.

What it carries that the aggregator layer does not:
  - PROVINCES. Nine provinces plus the national series, with the same indicator set.
    UNAIDS/WHO carry South Africa only as a single national number, so this is the
    sub-national layer for the largest epidemic in the panel (~7.9m PLHIV).
  - 95% CONFIDENCE INTERVALS on every indicator, published as their own rows. These go
    straight into value_lower / value_upper, which is what the panel schema was built for.
  - KEY POPULATIONS as modelled series (sex workers, cis-gender MSM, transgender women,
    PWID) with prevalence, ART coverage, viral suppression and diagnosis rates.

Three rules from the workbook's own Notes sheet are enforced here, not left to the reader:

1. ESTIMATE vs PROJECTION IS ENCODED IN THE FONT COLOUR. "Estimates that are based on
   fitting the model to historic data are formatted in black. Projections, which are
   based on model extrapolations of past trends (and for which we have no data), are
   formatted in grey." There is no year cutoff to hard-code: the boundary is per
   indicator, because it tracks the last year of data feeding that particular series
   (AIDS deaths are fitted to 2018, the last vital-registration year; population to 2011,
   the last census; the HIV cascade to 2022-2025). This connector reads the colour and
   emits ONLY the black years. Projections never enter the panel as observations, which
   matters more than usual here: a study of what a funding cut did in 2025 must not read
   a model's pre-cut extrapolation of 2025 as evidence about 2025.

2. PROVINCES DO NOT SUM TO NATIONAL. The national model is calibrated independently of
   the provincial models, so the national series is not the sum of the nine. Anything
   aggregating this connector's output takes the admin1="" rows or the province rows,
   never both, and never re-derives the national total by addition. Every row carries
   this warning in `extra`.

3. THE CIs EXCLUDE DEMOGRAPHIC-PARAMETER UNCERTAINTY. They cover HIV transmission, disease
   progression, HIV mortality and testing rates only. So the bounds on `population_total`
   are narrower than the real uncertainty; that caveat rides on every row too.

Timing follows the workbook: stocks are mid-year, flows run from mid-year of the stated
year to mid-year of the next. Percentages are published as fractions and are multiplied
by 100 here, driven off the canonical indicator's declared unit.

Citation (requested by the modellers): Johnson LF, et al. (2022) The effect of HIV
programs in South Africa on national HIV incidence trends, 2000-2019. JAIDS 90: 115-123.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import (
    PanelRow, SourceType, POP_ALL, POP_GBMSM, POP_PWID, POP_SEX_WORKERS, POP_TRANSGENDER,
)
from ...config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_BASE = "https://www.thembisa.org"
_DOWNLOADS = f"{_BASE}/downloads"
# the download page keys are named ProvOutputs5_0 / ProvOutput4_82 / ProvOutput4_7 ...
_KEY_RE = re.compile(r"/content/downloadPage/(ProvOutputs?(\d+)_(\d+))", re.I)
# ...and that page is an interstitial that redirects to the file with a JS location set
_FILEDL_RE = re.compile(r'window\.location\s*=\s*["\'](/content/filedl/[^"\']+)["\']', re.I)

# sheet code -> admin1 name ("" = national). From the workbook's Abbreviations sheet.
SHEETS: Dict[str, str] = {
    "SA": "",
    "EC": "Eastern Cape",
    "FS": "Free State",
    "GT": "Gauteng",
    "KZ": "KwaZulu-Natal",
    "LM": "Limpopo",
    "MP": "Mpumalanga",
    "NC": "Northern Cape",
    "NW": "North West",
    "WC": "Western Cape",
}

# (workbook label, canonical_id, population_group, sex, age_group)
# Labels are matched on whitespace-normalised text, because the workbook has at least one
# label with a double space in it ("...living with HIV  who are on ART with VL <1000").
_MAP: Tuple[Tuple[str, str, str, str, str], ...] = (
    # --- mortality -------------------------------------------------------------
    ("Total AIDS deaths",                                    "aids_deaths",   POP_ALL, "all",    "all"),
    ("AIDS deaths in adult males (15+)",                     "aids_deaths",   POP_ALL, "male",   "15+"),
    ("AIDS deaths in adult females (15+)",                   "aids_deaths",   POP_ALL, "female", "15+"),
    ("AIDS deaths in children",                              "aids_deaths",   POP_ALL, "all",    "0-14"),
    # --- incidence -------------------------------------------------------------
    ("Total new HIV infections",                             "new_infections", POP_ALL, "all",    "all"),
    ("New infections in males aged 15+",                     "new_infections", POP_ALL, "male",   "15+"),
    ("New infections in females aged 15+",                   "new_infections", POP_ALL, "female", "15+"),
    ("New HIV infections in children <15",                   "new_infections", POP_ALL, "all",    "0-14"),
    ("New HIV infections in 15-24 year olds",                "new_infections", POP_ALL, "all",    "15-24"),
    ("New HIV infections in 15-49 year olds",                "new_infections", POP_ALL, "all",    "15-49"),
    ("New HIV infections in sex workers",                    "new_infections", POP_SEX_WORKERS, "all", "all"),
    ("New HIV infections in cis-gender MSM",                 "new_infections", POP_GBMSM, "all", "all"),
    ("New HIV infections in transgender women",              "new_infections", POP_TRANSGENDER, "all", "all"),
    ("New HIV infections in PWID",                           "new_infections", POP_PWID, "all", "all"),
    # --- prevalence / PLHIV ----------------------------------------------------
    ("Total people living with HIV",                         "plhiv",         POP_ALL, "all",    "all"),
    ("Total males aged 15+ who are living with HIV",         "plhiv",         POP_ALL, "male",   "15+"),
    ("Total females aged 15+ who are living with HIV",       "plhiv",         POP_ALL, "female", "15+"),
    ("Total children (<15) who are living with HIV",         "plhiv",         POP_ALL, "all",    "0-14"),
    ("Total people living with HIV, aged 15-24",             "plhiv",         POP_ALL, "all",    "15-24"),
    ("Total people living with HIV, aged 15-49",             "plhiv",         POP_ALL, "all",    "15-49"),
    ("HIV prevalence in age group 15-49",                    "hiv_prevalence_15_49", POP_ALL, "all",    "15-49"),
    ("HIV prevalence in males aged 15-49",                   "hiv_prevalence_15_49", POP_ALL, "male",   "15-49"),
    ("HIV prevalence in females aged 15-49",                 "hiv_prevalence_15_49", POP_ALL, "female", "15-49"),
    ("HIV prevalence in female sex workers",                 "kp_hiv_prevalence", POP_SEX_WORKERS, "female", "all"),
    ("HIV prevalence in men who have sex with men (ages 18+)", "kp_hiv_prevalence", POP_GBMSM, "male", "18+"),
    ("HIV prevalence in transgender women (ages 18+)",       "kp_hiv_prevalence", POP_TRANSGENDER, "all", "18+"),
    ("HIV prevalence in PWID",                               "kp_hiv_prevalence", POP_PWID, "all", "all"),
    # --- treatment -------------------------------------------------------------
    ("Total on ART",                                         "on_art_count",  POP_ALL, "all",    "all"),
    ("Males age 15+ on ART",                                 "on_art_count",  POP_ALL, "male",   "15+"),
    ("Females age 15+ on ART",                               "on_art_count",  POP_ALL, "female", "15+"),
    ("Children aged <15 on ART",                             "on_art_count",  POP_ALL, "all",    "0-14"),
    ("Total on ART, ages 15-24",                             "on_art_count",  POP_ALL, "all",    "15-24"),
    ("ART coverage",                                         "art_coverage_pct", POP_ALL, "all",    "all"),
    ("ART coverage in males age 15+",                        "art_coverage_pct", POP_ALL, "male",   "15+"),
    ("ART coverage in females age 15+",                      "art_coverage_pct", POP_ALL, "female", "15+"),
    ("ART coverage in children <15",                         "art_coverage_pct", POP_ALL, "all",    "0-14"),
    ("ART coverage at ages 15-24",                           "art_coverage_pct", POP_ALL, "all",    "15-24"),
    ("ART coverage in female sex workers",                   "art_coverage_pct", POP_SEX_WORKERS, "female", "all"),
    ("ART coverage in MSM",                                  "art_coverage_pct", POP_GBMSM, "male", "all"),
    ("ART coverage in PWID",                                 "art_coverage_pct", POP_PWID, "all",  "all"),
    # --- diagnosis (first 90) --------------------------------------------------
    ("% of people living with HIV who are diagnosed",        "know_status_pct", POP_ALL, "all",    "all"),
    ("% of males (15+) living with HIV who are diagnosed",   "know_status_pct", POP_ALL, "male",   "15+"),
    ("% of females (15+) living with HIV who are diagnosed", "know_status_pct", POP_ALL, "female", "15+"),
    ("% of children (<15) living with HIV who are diagnosed", "know_status_pct", POP_ALL, "all",   "0-14"),
    ("% of FSWs living with HIV who are diagnosed",          "know_status_pct", POP_SEX_WORKERS, "female", "all"),
    ("% of MSM living with HIV who are diagnosed",           "know_status_pct", POP_GBMSM, "male", "all"),
    ("% of PWID living with HIV who are diagnosed",          "know_status_pct", POP_PWID, "all",  "all"),
    # --- viral suppression (third 90; <1000 copies/ml, the UNAIDS threshold) ----
    ("% of ART patients who are virologically suppressed (RNA count <1000 copies/ml)",
     "viral_suppression_pct", POP_ALL, "all", "all"),
    ("% of males 15+ on ART who are virologically suppressed (RNA count <1000 copies/ml)",
     "viral_suppression_pct", POP_ALL, "male", "15+"),
    ("% of females 15+ on ART who are virologically suppressed (RNA count <1000 copies/ml)",
     "viral_suppression_pct", POP_ALL, "female", "15+"),
    ("% of children on ART who are virologically suppressed (RNA count <1000 copies/ml)",
     "viral_suppression_pct", POP_ALL, "all", "0-14"),
    ("% of FSWs on ART who are virologically suppressed (RNA count <1000 copies/ml)",
     "viral_suppression_pct", POP_SEX_WORKERS, "female", "all"),
    ("% of MSM on ART who are virologically suppressed (RNA count <1000 copies/ml)",
     "viral_suppression_pct", POP_GBMSM, "male", "all"),
    ("% of PWID on ART who are virologically suppressed (RNA count <1000 copies/ml)",
     "viral_suppression_pct", POP_PWID, "all", "all"),
    # community viral suppression = suppressed as a share of ALL PLHIV, not of ART patients
    ("% of people living with HIV who are on ART with VL <1000",
     "community_viral_suppression_pct", POP_ALL, "all", "all"),
    ("% of males (15+) living with HIV who are on ART with VL <1000",
     "community_viral_suppression_pct", POP_ALL, "male", "15+"),
    ("% of females (15+) living with HIV who are on ART with VL <1000",
     "community_viral_suppression_pct", POP_ALL, "female", "15+"),
    # --- prevention ------------------------------------------------------------
    ("Number of males using oral PrEP",                      "prep_recipients", POP_ALL, "male",   "all"),
    ("Number of females using oral PrEP",                    "prep_recipients", POP_ALL, "female", "all"),
    ("Number of sex workers using oral PrEP",                "prep_recipients", POP_SEX_WORKERS, "all", "all"),
    ("Number of men who have sex with men using oral PrEP",  "prep_recipients", POP_GBMSM, "male", "all"),
    ("Number of PWID using oral PrEP",                       "prep_recipients", POP_PWID, "all",  "all"),
    # --- denominator -----------------------------------------------------------
    ("Total population",                                     "population_total", POP_ALL, "all",  "all"),
)

# the injectable-PrEP rows exist in v5.0 but are empty (SA had no CAB-LA rollout in the
# fitted period), so oral PrEP IS total PrEP. If a later workbook fills them in, the
# `prep_recipients` rows below silently become an undercount — so watch for it and say so.
_INJECTABLE = ("Number of males using injectable PrEP", "Number of females using injectable PrEP")

_AGG_WARNING = (
    "Provincial estimates do NOT sum to the national estimate: the national model is "
    "calibrated independently of the provincial models. Take national totals from the "
    "admin1='' rows, never by adding the nine provinces."
)
_CI_WARNING = (
    "95% CIs cover HIV transmission, disease progression, HIV mortality and testing rates "
    "only. They exclude demographic-parameter uncertainty (non-HIV mortality, fertility, "
    "migration), so bounds on population_total understate the real uncertainty."
)
_CITATION = ("Johnson LF, et al. (2022) The effect of HIV programs in South Africa on "
             "national HIV incidence trends, 2000-2019. JAIDS 90: 115-123")


def _norm(s) -> str:
    return re.sub(r"\s+", " ", s).strip() if isinstance(s, str) else ""


def _is_projection(cell) -> bool:
    """True when the cell is formatted grey, i.e. an extrapolation rather than a fit.

    Estimates carry the default font colour (no explicit colour, or theme 1 "text 1" with
    no tint). Projections carry theme 0 ("background 1", white) tinted -0.5, which renders
    as 50% grey. Anything else explicitly coloured is treated as a projection: a workbook
    that starts marking uncertainty a new way should cost us rows, not silently pass
    extrapolations off as observations.
    """
    col = cell.font.color if cell.font else None
    if col is None:
        return False
    if col.type == "theme":
        return not (col.theme == 1 and not (col.tint or 0))
    if col.type == "rgb" and isinstance(col.rgb, str):
        return col.rgb.upper() not in ("FF000000", "00000000")
    return False


def _num(v) -> Optional[float]:
    # blank cells in this workbook are runs of spaces, not empty strings
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


class SouthAfricaThembisaConnector(BaseConnector):
    source_id = "za_thembisa"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = "South Africa — Thembisa model (national + 9 provinces, with 95% CIs)."
    country = "ZAF"
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/thembisa", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- locating the workbook --------------------------------------------------
    def _latest_key(self) -> Tuple[str, str]:
        """Return (key, version) for the newest ProvOutputs workbook on /downloads."""
        html = self.get_text(_DOWNLOADS)
        found = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in _KEY_RE.finditer(html)]
        if not found:
            raise RuntimeError("za_thembisa: no ProvOutputs link found on /downloads")
        key, major, minor = max(found, key=lambda t: (t[1], t[2]))
        return key, f"{major}.{minor}"

    def _workbook_path(self) -> Tuple[Path, str, str]:
        """Local .xlsx path, download URL and version — downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        cached = sorted(self.raw_dir.glob("ProvOutput*.xlsx"))
        if cached:
            path = cached[-1]
            m = re.search(r"(\d+)_(\d+)", path.stem)
            version = f"{m.group(1)}.{m.group(2)}" if m else "unknown"
            log.info("za_thembisa: using cached workbook %s (v%s)", path.name, version)
            return path, f"{_BASE}/content/filedl/{path.stem}", version

        key, version = self._latest_key()
        # the download page is an interstitial; the file itself sits behind /content/filedl/
        page = self.get_text(f"{_BASE}/content/downloadPage/{key}")
        m = _FILEDL_RE.search(page)
        url = _BASE + (m.group(1) if m else f"/content/filedl/{key}")
        # served with content-type text/html despite being xlsx — trust the key, not the header
        blob = self._request("GET", url).content
        if not blob.startswith(b"PK"):
            raise RuntimeError(f"za_thembisa: {url} did not return an xlsx (got {blob[:16]!r})")
        path = self.raw_dir / f"{key}.xlsx"
        path.write_bytes(blob)
        log.info("za_thembisa: downloaded %s (v%s, %.1f MB) -> %s",
                 key, version, len(blob) / 1e6, path)
        return path, url, version

    # -- reading ----------------------------------------------------------------
    @staticmethod
    def _index(rows: List[list]) -> Dict[str, int]:
        """Map normalised indicator label -> row index of its 'Mean' row."""
        idx: Dict[str, int] = {}
        for i, row in enumerate(rows):
            if _norm(row[2].value) != "Mean":
                continue
            label = _norm(row[0].value)
            if label and label not in idx:
                idx[label] = i
        return idx

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        if wanted and self.country not in wanted:
            return

        import openpyxl  # local import: only this connector needs it

        path, url, version = self._workbook_path()
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        model = f"Thembisa {version}"
        end_year = end_year or 9999

        for sheet, admin1 in SHEETS.items():
            if sheet not in wb.sheetnames:
                log.warning("za_thembisa: sheet %s missing from %s — skipping", sheet, path.name)
                continue
            ws = wb[sheet]
            rows = list(ws.iter_rows(min_row=1, max_row=ws.max_row))
            header = [c.value for c in rows[0]]
            years = [(j, header[j]) for j in range(3, len(header)) if isinstance(header[j], int)]
            index = self._index(rows)

            # anti-drift: if injectable PrEP ever gets FITTED values, oral-only stops being
            # the total. v5.0 fills these rows only from 2026, i.e. entirely in the grey
            # projection range, so the test has to ignore projections exactly as the row
            # emission does — otherwise it fires on numbers that never enter the panel.
            for lbl in _INJECTABLE:
                i = index.get(lbl)
                if i is None:
                    continue
                fitted_inj = [y for j, y in years
                              if _num(rows[i][j].value) and not _is_projection(rows[i][j])]
                if fitted_inj:
                    log.warning("za_thembisa: %s has fitted values from %s in %s — "
                                "prep_recipients rows are ORAL ONLY and now understate total "
                                "PrEP use", lbl, min(fitted_inj), model)

            n_rows = 0
            oral_total: Dict[int, List[float]] = {}
            for label, canonical, pop, sex, age in _MAP:
                i = index.get(label)
                if i is None:
                    log.warning("za_thembisa: label not found in %s/%s: %r", path.name, sheet, label)
                    continue
                mean_row = rows[i]
                # the two rows under a Mean row must be its bounds; if not, take no bounds
                lo_row = rows[i + 1] if i + 1 < len(rows) else None
                hi_row = rows[i + 2] if i + 2 < len(rows) else None
                if not (lo_row is not None and hi_row is not None
                        and _norm(lo_row[2].value) == "95% LL" and _norm(hi_row[2].value) == "95% UL"):
                    log.warning("za_thembisa: %s/%s: %r is not followed by 95%% LL/UL — "
                                "emitting without bounds", path.name, sheet, label)
                    lo_row = hi_row = None

                spec = CANONICAL_INDICATORS.get(canonical)
                unit = spec.unit if spec else "count"
                scale = 100.0 if unit == "percent" else 1.0
                var_type = _norm(mean_row[1].value) or "Stock"

                fitted = [y for j, y in years
                          if _num(mean_row[j].value) is not None and not _is_projection(mean_row[j])]
                last_estimate = max(fitted) if fitted else None

                for j, year in years:
                    if year < start_year or year > end_year:
                        continue
                    value = _num(mean_row[j].value)
                    if value is None:
                        continue
                    # RULE 1: projections are extrapolations, not observations — drop them
                    if _is_projection(mean_row[j]):
                        continue
                    lower = _num(lo_row[j].value) * scale if lo_row and _num(lo_row[j].value) is not None else None
                    upper = _num(hi_row[j].value) * scale if hi_row and _num(hi_row[j].value) is not None else None

                    extra = {
                        "model": model,
                        "source_label": label,
                        "variable_type": var_type.lower(),
                        "timing": ("mid-year stock" if var_type.lower() == "stock"
                                   else f"flow from mid-{year} to mid-{year + 1}"),
                        "last_estimate_year": last_estimate,
                        "estimate_basis": "fitted to data (black in the workbook); "
                                          "grey projection years are not emitted",
                        "aggregation_warning": _AGG_WARNING,
                        "ci_note": _CI_WARNING,
                        "citation": _CITATION,
                        "reconcile_with": "unaids_aidsinfo, who_gho, pepfar_panorama",
                    }
                    yield self.make_row(
                        country_iso3="ZAF", country_name="South Africa",
                        admin1=admin1,
                        indicator_id=canonical, year=year,
                        value=value * scale, value_lower=lower, value_upper=upper,
                        unit=unit,
                        population_group=pop, sex=sex, age_group=age,
                        source_url=url,
                        source_indicator_code=f"{sheet}!{label}",
                        extra=extra,
                    )
                    n_rows += 1

                    if canonical == "prep_recipients" and pop == POP_ALL and sex in ("male", "female"):
                        oral_total.setdefault(year, []).append(value)

            # Thembisa publishes oral PrEP by sex but no combined total. Males and females
            # partition the population, so the sum is the total — but the two published CIs
            # cannot be added, so this row carries a point estimate and no bounds.
            for year, parts in sorted(oral_total.items()):
                if len(parts) != 2:
                    continue
                yield self.make_row(
                    country_iso3="ZAF", country_name="South Africa",
                    admin1=admin1,
                    indicator_id="prep_recipients", year=year,
                    value=sum(parts), unit="count",
                    source_url=url,
                    source_indicator_code=f"{sheet}!oral PrEP, male + female",
                    extra={
                        "model": model,
                        "derived": True,
                        "derivation": "sum of the published male and female oral-PrEP series; "
                                      "the model publishes no combined total, and the two "
                                      "published 95% CIs cannot be added, so this row has no bounds",
                        "variable_type": "stock",
                        "timing": "mid-year stock",
                        "aggregation_warning": _AGG_WARNING,
                        "citation": _CITATION,
                    },
                )
                n_rows += 1

            log.info("za_thembisa: %-14s -> %d rows", admin1 or "SA (national)", n_rows)
        wb.close()
