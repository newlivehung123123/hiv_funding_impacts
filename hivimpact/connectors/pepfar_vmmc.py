"""
PEPFAR-supported voluntary medical male circumcisions by country for 2010 to 2017, the eight
years before the partner file that pepfar_panorama reads begins.

WHAT THE FILE IS

`Voluntary_Male_Medical_Circumcisions_Results_by_Operating_Unit.zip` is one of PEPFAR's
Spotlight downloads. The zip holds a single tab-separated table of 17 rows, one per country, with
a column for every year from 2010 to 2024, a column pooling 2007 to 2009 into one figure, and a
total. On the download of 2026-07-18, dated 29 May 2025 inside the zip, the total equals the sum
of the year columns and the pooled column in all 17 rows. The connector repeats that check on
every run and logs any row that fails the check.

WHY ONLY 2010 TO 2017

From 2018 onwards pepfar_panorama already emits `circumcisions_performed` from the partner file.
This file and pepfar_panorama agree within half of one per cent in 92 of the 101 country-years
both carry, and the other nine sit between 0.952 of pepfar_panorama's value (Zambia 2018) and
1.030 (Kenya 2018). Emitting both files would put two PEPFAR figures on one country-year, so this
connector leaves 2018 onwards to pepfar_panorama and says so in the log. The same agreement shows
that the years in this file are PEPFAR fiscal years, which run from October to September, and not
calendar years.

The geographic file (`Enhanced_Geographical_Analysis`, read by pepfar_snu) also carries
circumcisions for 2016 and 2017. The geographic file removes people whom two partners both
report, and this file equals the geographic file exactly in 27 of the 28 country-years of 2016
and 2017. The one exception is Uganda 2017, at 732,527 here against 734,492 in the geographic
file. So this file is the deduplicated series and carries none of the partner overcount that
section 9w of docs/ACCESS_LADDER.md records for pepfar_panorama.

THE 2007-2009 COLUMN IS NOT A YEAR

The `2007-2009` column holds one figure for three years. Six countries carry a value there, Kenya
45,657, South Africa 18,100, Botswana 5,180, Eswatini 3,802, Tanzania 262 and Namibia 117, and
73,118 in all. Dividing each figure by three would invent a year-by-year path that the file does
not contain. The column is read and counted in the log and is never emitted, in the same way that
pepfar_ou_budgets reads and never emits the years it does not own.

ZEROS ARE NOT EMITTED

The file writes 0 in two different situations. Where PEPFAR ran no circumcision programme the
file writes 0, as in Nigeria, Burundi and Sierra Leone in every year from 2010 to 2017 (the three
countries report 22 procedures between them after 2019). The file also writes 0 in the middle of
a running programme, in Namibia 2013 between 6,121 in 2012 and 785 in 2014, and in Botswana 2011
between 534 in 2010 and 8,590 in 2012. The file cannot tell a year without services from a year
without reporting, and a 0 in the panel would read as a measured stop to the programme. The
connector therefore emits cells above 0 only and names in the log every 0 it leaves out, split
into zeros before a country's first reported year and zeros inside a running programme.

WHAT THE COUNT IS AND IS NOT

The count covers the circumcisions that PEPFAR supported, not every circumcision in the country.
unaids_aidsinfo carries the national count under the same indicator for 107 of the 108
country-years emitted here, and the one exception is Lesotho 2011, where UNAIDS reports 0 and this
file 199. In 85 of those 107 country-years PEPFAR's figure is at or below the national figure,
with a median of 0.831 of the national figure, which fits a PEPFAR share of a national total. In
four country-years PEPFAR's figure sits more than 25 per cent above the national figure, Malawi
2013 at 1.65 times, Eswatini 2012 at 1.45 times, Tanzania 2015 at 1.39 times and Namibia 2012 at
1.26 times. A PEPFAR fiscal year begins three months before the calendar year of the same number,
which could move a campaign from one year to the next, but neither file can confirm that
explanation, so the four country-years are recorded here and not explained. The PEPFAR series
and the UNAIDS series must never be added together. The PEPFAR series divided by the UNAIDS series
is the share of the national programme that PEPFAR supported, which is the share a cut to PEPFAR
puts at risk.

source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import re
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

INDICATOR = "circumcisions_performed"
FILE_HINT = "voluntary_male_medical_circumcisions"

# pepfar_panorama emits this indicator from 2018 onwards, from the partner file
LAST_YEAR = 2017

SOURCE_URL = "https://data.pepfar.gov/datasets"

INTERPRETATION = (
    "Voluntary medical male circumcisions that PEPFAR supported in the country in the PEPFAR "
    "fiscal year, which runs from October of the previous year to September. Not the national "
    "count, which unaids_aidsinfo carries under the same indicator, and the two series must never "
    "be added together. A year missing from this series between two years present in this series "
    "is a year the file gives as 0, which can mean a year without services or a year without "
    "reporting, and the file cannot tell the two apart."
)


def _num(cell) -> Optional[float]:
    """Blank means the file says nothing. The current file has no blank cell."""
    if cell is None:
        return None
    s = str(cell).strip().replace(",", "")
    if s in ("", "nan", "NaN", "NA", "N/A"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _ci(cols: List[str], *names: str) -> Optional[str]:
    low = {c.lower().strip(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    return None


def _cells(d: Dict[str, List[int]]) -> str:
    return ", ".join(f"{k} {', '.join(str(y) for y in v)}" for k, v in sorted(d.items())) or "none"


class PEPFARVMMCConnector(BaseConnector):
    source_id = "pepfar_vmmc"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("PEPFAR-supported voluntary medical male circumcisions by country for fiscal "
                   "years 2010 to 2017, the years before the partner file begins.")

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _read_frame(self) -> Optional[pd.DataFrame]:
        if not self.raw_dir.exists():
            log.warning("pepfar_vmmc: %s does not exist. Download Voluntary_Male_Medical_"
                        "Circumcisions_Results_by_Operating_Unit from data.pepfar.gov", self.raw_dir)
            return None

        candidates = [p for p in sorted(self.raw_dir.glob("*.zip")) if FILE_HINT in p.name.lower()]
        if not candidates:
            log.warning("pepfar_vmmc: no Voluntary_Male_Medical_Circumcisions zip in %s",
                        self.raw_dir)
            return None

        for path in candidates:
            try:
                with zipfile.ZipFile(path) as z:
                    members = [m for m in z.namelist() if m.lower().endswith(".txt")]
                    skipped = [m for m in z.namelist() if m not in members]
                    if not members:
                        continue
                    with z.open(members[0]) as fh:
                        df = pd.read_csv(fh, sep="\t", dtype=str, on_bad_lines="skip")
                    log.info("pepfar_vmmc: read %s from %s. Not read: %s",
                             members[0], path.name, skipped or "nothing")
                    return df
            except Exception as exc:
                log.warning("pepfar_vmmc: error reading %s: %s", path.name, exc)
        return None

    # -- emitting ---------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        df = self._read_frame()
        if df is None or df.empty:
            return

        cols = list(df.columns)
        iso_c = _ci(cols, "iso3")
        cn_c = _ci(cols, "country")
        ou_c = _ci(cols, "operating unit")
        total_c = next((c for c in cols if c.strip().lower().startswith("total")), None)
        years = {int(c): c for c in cols if re.fullmatch(r"\d{4}", c.strip())}
        pooled = [c for c in cols if re.fullmatch(r"\d{4}-\d{4}", c.strip())]
        if not (iso_c or cn_c) or not years:
            log.warning("pepfar_vmmc: file lacks a country column or year columns, not this "
                        "dataset, nothing emitted")
            return

        # Everything down to the country filter is a property of the file and is measured over
        # every row, not only over the countries a run asks for.
        pooled_by: Dict[str, float] = {}
        later: Dict[str, int] = {}
        before_first: Dict[str, List[int]] = {}
        inside: Dict[str, List[int]] = {}
        blank: Dict[str, List[int]] = {}
        total_off: List[str] = []
        no_iso = 0
        n = 0
        emitted = set()

        for _, r in df.iterrows():
            iso3 = to_iso3(r[iso_c]) if iso_c and pd.notna(r[iso_c]) else None
            if not iso3 and cn_c and pd.notna(r[cn_c]):
                iso3 = to_iso3(r[cn_c])
            if not iso3:
                no_iso += 1
                continue
            name = str(r[cn_c]).strip() if cn_c and pd.notna(r[cn_c]) else iso3
            vals = {y: _num(r[c]) for y, c in years.items()}

            for c in pooled:
                v = _num(r[c]) or 0.0
                if v:
                    pooled_by[iso3] = pooled_by.get(iso3, 0.0) + v
            if total_c:
                whole = sum(v or 0.0 for v in vals.values()) + sum(_num(r[c]) or 0.0 for c in pooled)
                stated = _num(r[total_c])
                if stated is not None and abs(stated - whole) > 0.5:
                    total_off.append(f"{iso3} total {stated:,.0f} against {whole:,.0f}")

            reported = [y for y, v in vals.items() if v]
            for y, v in sorted(vals.items()):
                if y > LAST_YEAR:
                    if v:
                        later[iso3] = later.get(iso3, 0) + 1
                    continue
                if v is None:
                    blank.setdefault(iso3, []).append(y)
                elif v == 0:
                    if reported and min(reported) < y < max(reported):
                        inside.setdefault(iso3, []).append(y)
                    else:
                        before_first.setdefault(iso3, []).append(y)

            if wanted and iso3 not in wanted:
                continue
            ou = str(r[ou_c]).strip() if ou_c and pd.notna(r[ou_c]) else None
            for y, v in sorted(vals.items()):
                if y > LAST_YEAR or not v or y < start_year or y > end_year:
                    continue
                extra = {
                    "note": ("PEPFAR-supported circumcisions only, not the national count. "
                             "unaids_aidsinfo carries the national count under the same "
                             "indicator, and the two must never be added together."),
                    "fiscal_year": f"PEPFAR fiscal year {y}, October {y - 1} to September {y}",
                    "operating_unit": ou,
                    "interpretation": INTERPRETATION,
                }
                if iso3 in inside:
                    extra["zero_years_not_emitted"] = inside[iso3]
                n += 1
                emitted.add(iso3)
                yield self.make_row(
                    country_iso3=iso3, country_name=name, indicator_id=INDICATOR, year=y,
                    value=v, unit="count", source_url=SOURCE_URL,
                    source_indicator_code="PEPFAR VMMC Results by Operating Unit",
                    extra=extra,
                )

        if total_off:
            log.warning("pepfar_vmmc: the total column differs from the sum of the year columns "
                        "in %d rows, so the file has changed shape since the download of "
                        "2026-07-18 and needs reading again. %s", len(total_off),
                        "; ".join(total_off))
        if no_iso:
            log.warning("pepfar_vmmc: %d rows carry no country this connector recognises and are "
                        "dropped", no_iso)
        if pooled:
            log.info("pepfar_vmmc: column %s pools several years into one figure and is not "
                     "emitted. %s circumcisions in %d countries (%s)", ", ".join(pooled),
                     f"{sum(pooled_by.values()):,.0f}", len(pooled_by),
                     ", ".join(f"{k} {v:,.0f}" for k, v in sorted(pooled_by.items(),
                                                                   key=lambda kv: -kv[1])))
        log.info("pepfar_vmmc: %d cells above 0 over %d countries fall after %d and are left to "
                 "pepfar_panorama, which reads the same series from the partner file",
                 sum(later.values()), len(later), LAST_YEAR)
        log.info("pepfar_vmmc: zeros not emitted, the file writing 0 both where PEPFAR ran no "
                 "programme and where a running programme reported nothing. Before a country's "
                 "first reported year or in a country with no programme: %s. Inside a running "
                 "programme: %s", _cells(before_first), _cells(inside))
        if blank:
            log.warning("pepfar_vmmc: blank cells, which the download of 2026-07-18 did not "
                        "have: %s", _cells(blank))
        log.info("pepfar_vmmc: emitted %d rows over %d countries", n, len(emitted))
