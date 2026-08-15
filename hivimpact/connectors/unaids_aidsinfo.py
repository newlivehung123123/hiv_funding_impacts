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
]


def _clean_num(cell) -> Optional[float]:
    if cell is None:
        return None
    s = str(cell).strip()
    if s in ("", "...", "…", "-", "N/A", "NA", "nan"):
        return None
    s = (s.replace(" ", "").replace(" ", "").replace(" ", "")
         .replace(",", "").replace("<", "").replace(">", ""))
    try:
        return float(s)
    except ValueError:
        return None


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
                    val = _clean_num(row[y])
                    if val is None:
                        continue
                    year = int(y)
                    if year < start_year or year > end_year:
                        continue
                    yield self.make_row(
                        country_iso3=iso3, country_name=str(row["Country"]),
                        indicator_id=canonical, year=year, value=val,
                        value_lower=_clean_num(row.get(f"{y}_lower")),
                        value_upper=_clean_num(row.get(f"{y}_upper")),
                        population_group=pop, sex=sex, unit=unit, source_type=src_type,
                        source_url="https://aidsinfo.unaids.org/",
                        source_indicator_code=path.stem[:80],
                        extra={"export_file": path.name},
                    )
                    n += 1
                if recent_col and recent_year and start_year <= recent_year <= end_year:
                    val = _clean_num(row[recent_col])
                    if val is not None:
                        yield self.make_row(
                            country_iso3=iso3, country_name=str(row["Country"]),
                            indicator_id=canonical, year=recent_year, value=val,
                            population_group=pop, sex=sex, unit=unit, source_type=src_type,
                            source_url="https://aidsinfo.unaids.org/",
                            source_indicator_code=path.stem[:80],
                            extra={"export_file": path.name, "most_recent": True},
                        )
                        n += 1
            log.info("unaids_aidsinfo: %-60s -> %d rows (%s / %s)", path.name[:60], n, canonical, pop)

        log.info("unaids_aidsinfo: mapped %d files, skipped %d unmapped", mapped, skipped)
