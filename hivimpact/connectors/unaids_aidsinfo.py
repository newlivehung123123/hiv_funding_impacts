"""
UNAIDS AIDSinfo connector — ingests the platform's official CSV exports.

AIDSinfo (https://aidsinfo.unaids.org/) has no clean public API; its supported
structured export is CSV. You export indicators from the platform into
`data/raw/unaids/`, keeping AIDSinfo's own descriptive filenames — e.g.
  `People living with HIV_People living with HIV - All ages_Population_ All.csv`
  `Men who have sex with men_HIV prevalence among men who have sex with men_Population_ Total.csv`
This connector maps those descriptive names to canonical indicators (and, for the key
populations, to a population_group), so you don't have to rename anything.

CSV shape (wide): `Country, 1990, 1990_lower, 1990_upper, 1990_Footnote, 1991, ...`.
Values use spaces as thousands separators ("920 000"); `...` = missing. We capture the
point estimate plus its lower/upper uncertainty bounds.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType
from ..config.indicators import CANONICAL_INDICATORS

log = logging.getLogger("hivimpact")

_YEAR = re.compile(r"^(19|20)\d{2}$")

# --- key-population files: category prefix -> population_group -----------------
POP_FROM_CATEGORY = {
    "men who have sex with men": "gbmsm",
    "people who inject drugs": "pwid",
    "sex workers": "sex_workers",
    "transgender people": "transgender",
    "prisoners": "prisoners",
}
# within a key-population file, indicator-name substring -> canonical id
KP_INDICATOR_MAP = {
    "hiv prevalence among": "kp_hiv_prevalence",
    "antiretroviral therapy coverage among": "art_coverage_pct",
    "hiv testing and status awareness among": "know_status_pct",
}

# --- general (all-population) files: name substring -> canonical --------------
# order matters: first match wins, so keep specific strings.
CORE_MAP: List[Tuple[str, str]] = [
    ("people living with hiv - all ages", "plhiv"),
    ("new hiv infections - all ages", "new_infections"),
    ("aids-related deaths - all ages", "aids_deaths"),
    ("people living with hiv receiving art (#)", "on_art_count"),
    ("people living with hiv receiving art (%)", "art_coverage_pct"),
    ("people living with hiv who know their status (%)", "know_status_pct"),
    ("people living with hiv who have suppressed viral loads (%)", "community_viral_suppression_pct"),
    ("hiv prevalence - adults (15-49)", "hiv_prevalence_15_49"),
    ("coverage of pregnant women who receive arv for pmtct", "pmtct_coverage_pct"),
    ("people receiving pre-exposure prophylaxis (prep)", "prep_recipients"),
    ("country-reported hiv expenditure", "hiv_expenditure_total"),

    # The seven "TB and HIV" exports. These sat unread in data/raw/unaids until 2026-09-05,
    # because the connector only reads a file it can name and nothing here had a canonical
    # id. Three of them are the counterpart to the TB preventive services the Global Fund
    # publishes as counts, which is what turns those from a single-source series into a
    # measured one. The two modelled files land on canonicals WHO TME already fills.
    #
    # Keep these below the core entries and keep each string long enough to be unambiguous.
    # First match wins, and "newly enrolled ... started on TB preventive therapy" and
    # "currently enrolled ... started on TB preventive therapy" differ by one word.
    ("newly enrolled in hiv treatment started on tb preventive therapy", "tpt_initiation_new_pct"),
    ("currently enrolled in hiv treatment started on tb preventive therapy", "tpt_initiation_current_pct"),
    ("on art who completed a course of tpt", "tpt_completion_pct"),
    ("newly enrolled in hiv treatment diagnosed with tb disease", "plhiv_new_tb_diagnosed_pct"),
    ("co-management of tb and hiv treatment", "tbhiv_comanagement_pct"),
    ("incident tb cases in people living with hiv", "tbhiv_incidence"),
    ("tb-related deaths among people living with hiv", "tbhiv_deaths"),
]


def _parse_cell(cell) -> Tuple[Optional[float], Optional[str]]:
    """Parse one AIDSinfo cell into (number, censoring notation).

    AIDSinfo censors small figures for display: `<100`, `<500`, `<200`, `<0.1`, `<0.01`
    and, in the cascade files, `>95`. There are 66,291 such cells across the exports in
    data/raw/unaids. They are bounds, and stripping the `<` puts a point estimate in the
    panel that the source never asserted — which is how Ukraine came to be recorded as
    spending 100 US dollars on HIV in 2018, between 108 million in 2017 and 100 million
    in 2019. The notation is returned alongside the number so the caller can decide what
    the bound means for its own indicator.
    """
    if cell is None:
        return None, None
    s = str(cell).strip()
    if s in ("", "...", "…", "-", "N/A", "NA", "nan"):
        return None, None
    censored = s if s[:1] in ("<", ">") else None
    s = (s.replace(" ", "").replace(" ", "").replace(" ", "")
         .replace(",", "").replace("<", "").replace(">", ""))
    try:
        return float(s), censored
    except ValueError:
        return None, None


def _clean_num(cell) -> Optional[float]:
    """The bare number, where the censoring carries no meaning worth keeping."""
    return _parse_cell(cell)[0]


def _bound(cell, is_lower: bool) -> Optional[float]:
    """One end of the source's own uncertainty interval.

    The bound columns are censored on the same rule as the point column, so they need
    reading the same way. A `<100` in a lower column does not mean the interval stops at
    100 — it means it reaches down to nothing. A `>98` in an upper column states no
    ceiling at all rather than a ceiling of 98. Read literally, both narrow the interval
    the source published, which is the wrong direction for an uncertainty bound to move.
    """
    v, censored = _parse_cell(cell)
    if v is None or not censored:
        return v
    if censored.startswith("<") and is_lower:
        return 0.0
    if censored.startswith(">") and not is_lower:
        return None
    return v


def _censored_row(value: Optional[float], notation: str, unit: str,
                  lower: Optional[float], upper: Optional[float]):
    """Turn a censored cell into (value, lower, upper) for the panel.

    The notation means different things in the two instruments AIDSinfo publishes, and
    the difference is not a matter of degree. In the epidemiological files a `<100` sits
    inside a series whose other years run to about 800, so it is an honest small estimate
    of a small epidemic — 37 countries have their entire new-infections series censored,
    and blanking it would delete them from the panel. In the country-reported expenditure
    file the same `<100` sits inside a series whose other years have a median of 22.4
    million US dollars: South Africa is `<100` for 2015 and 2016 against an other-year
    median of 2.42 billion. No country spent under 100 dollars on HIV. There the notation
    is the display floor standing in for a GAM return with no usable total, which makes
    it a non-report — the same finding as the GAM zero, arrived at from the other side.

    So a censored count keeps its number, bounded, and a censored currency amount keeps
    no number at all. Either way the notation itself is recorded, so the choice can be
    revisited without re-reading the raw exports.
    """
    if notation.startswith(">"):
        # The cascade files report `>95` for a country at or above the target: a floor,
        # not a ceiling, so the bound goes on the other side.
        lower = value if lower is None else lower
    else:
        lower = 0.0 if lower is None else lower
        upper = value if upper is None else upper
        if unit == "USD":
            value = None
    return value, lower, upper


def _classify(stem: str) -> Optional[Tuple[str, str, str]]:
    """Return (canonical_id, population_group, sex) for a filename stem, or None to skip."""
    low = stem.lower()
    category = low.split("_", 1)[0].strip()
    sex = "female" if low.rstrip().endswith("females") else "male" if low.rstrip().endswith("males") else "all"

    if category in POP_FROM_CATEGORY:
        for sub, canon in KP_INDICATOR_MAP.items():
            if sub in low:
                return canon, POP_FROM_CATEGORY[category], sex
        return None
    for sub, canon in CORE_MAP:
        if sub in low:
            return canon, "all", sex
    return None


class UNAIDSAidsinfoConnector(BaseConnector):
    source_id = "unaids_aidsinfo"
    default_source_type = SourceType.MODELLED_ESTIMATE
    description = "UNAIDS AIDSinfo — CSV exports (epi, cascade, key populations, finance)."

    def __init__(self, raw_dir: str = "data/raw/unaids", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        if not self.raw_dir.exists():
            log.warning("unaids_aidsinfo: %s does not exist — export CSVs from AIDSinfo first", self.raw_dir)
            return
        files = sorted(self.raw_dir.glob("*.csv"))
        if not files:
            log.warning("unaids_aidsinfo: no CSV in %s", self.raw_dir)
            return

        mapped = skipped = 0
        for path in files:
            cls = _classify(path.stem)
            if cls is None:
                skipped += 1
                continue
            canonical, pop, sex = cls
            spec = CANONICAL_INDICATORS.get(canonical)
            unit = spec.unit if spec else ""
            src_type = (spec.default_source_type if spec else self.default_source_type).value
            mapped += 1

            try:
                df = pd.read_csv(path, dtype=str)
            except Exception as exc:
                log.warning("unaids_aidsinfo: could not read %s: %s", path.name, exc)
                continue
            df.columns = [str(c).strip() for c in df.columns]
            if "Country" not in df.columns:
                log.warning("unaids_aidsinfo: no Country column in %s — skipping", path.name)
                continue
            year_cols = [c for c in df.columns if _YEAR.match(c)]
            # key-population / survey exports use a single "Most recent data as of YYYY" column
            recent_col = next((c for c in df.columns if "most recent data as of" in c.lower()), None)
            recent_year = None
            if recent_col:
                m = re.search(r"(19|20)\d{2}", recent_col)
                recent_year = int(m.group()) if m else None

            n = 0
            for _, row in df.iterrows():
                iso3 = to_iso3(row["Country"])
                if not iso3 or (wanted and iso3 not in wanted):
                    continue
                for y in year_cols:
                    val, censored = _parse_cell(row[y])
                    if val is None:
                        continue
                    year = int(y)
                    if year < start_year or year > end_year:
                        continue
                    lo = _bound(row.get(f"{y}_lower"), True)
                    hi = _bound(row.get(f"{y}_upper"), False)
                    extra = {"export_file": path.name}
                    if censored:
                        val, lo, hi = _censored_row(val, censored, unit, lo, hi)
                        extra["censored"] = censored
                    yield self.make_row(
                        country_iso3=iso3, country_name=str(row["Country"]),
                        indicator_id=canonical, year=year, value=val,
                        value_lower=lo, value_upper=hi,
                        population_group=pop, sex=sex, unit=unit, source_type=src_type,
                        source_url="https://aidsinfo.unaids.org/",
                        source_indicator_code=path.stem[:80],
                        extra=extra,
                    )
                    n += 1
                if recent_col and recent_year and start_year <= recent_year <= end_year:
                    val, censored = _parse_cell(row[recent_col])
                    if val is not None:
                        lo = hi = None
                        extra = {"export_file": path.name, "most_recent": True}
                        if censored:
                            val, lo, hi = _censored_row(val, censored, unit, None, None)
                            extra["censored"] = censored
                        yield self.make_row(
                            country_iso3=iso3, country_name=str(row["Country"]),
                            indicator_id=canonical, year=recent_year, value=val,
                            value_lower=lo, value_upper=hi,
                            population_group=pop, sex=sex, unit=unit, source_type=src_type,
                            source_url="https://aidsinfo.unaids.org/",
                            source_indicator_code=path.stem[:80],
                            extra=extra,
                        )
                        n += 1
            log.info("unaids_aidsinfo: %-60s -> %d rows (%s / %s)", path.name[:60], n, canonical, pop)

        log.info("unaids_aidsinfo: mapped %d files, skipped %d unmapped", mapped, skipped)
