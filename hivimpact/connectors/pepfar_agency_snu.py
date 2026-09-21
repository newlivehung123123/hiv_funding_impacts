"""
PEPFAR MER split by funding agency AND by province — the funding cut where it lands.

`pepfar_agency` splits a country's treatment and testing between USAID, HHS/CDC and everything
else, which is the difference between a flat national total and a visible cut. `pepfar_snu`
puts the country total on provinces, which is the difference between a national decline and
knowing where it fell. Neither can answer the question the other half answers: a province whose
USAID-funded cohort collapsed while its CDC-funded cohort held is invisible in both, because
the agency split has no geography and the geography has no agency.

This connector reads `Partner_Performance`, the one Spotlight file carrying `Funding Agency`
and `Priority Sub-National Unit` on the same row, and emits the cross. Three indicators,
TX_CURR, HTS_TST_POS and TX_NEW, the same three `pepfar_agency` splits and for the same reason:
a cut stops testing and enrolment the week the money stops and moves the treatment cohort
months later, so `art_initiations_usaid` against `art_initiations_cdc` inside one province is
the sharpest comparison this panel can make.

WHAT A PRIORITY SUB-NATIONAL UNIT IS, AND WHY PLACING ONE IS NOT A JOIN

The partner file names one geographic column and gives it no level. A priority sub-national
unit is a province in Kenya, a district in Malawi, a municipality in Brazil and a country in
Thailand, and nothing in the row says which. It also spells names its own way: Panamá in the
geographic file is Panama here. So the units are placed rather than joined, against the
hierarchy `pepfar_snu` publishes through `emitted_units`, under three rules.

A name is resolved at ONE level of the hierarchy, chosen per country as the level most of that
country's units match, and never by falling through the levels in turn. Tanzania publishes a
region called Kagera and, elsewhere in the country, a district of the same name; Burma's
Rakhine is a state the geographic file names and a district somewhere else. Falling through
placed Rakhine in Sagaing.

A unit named after its own country is never placed. Guatemala's only priority sub-national unit
is called Guatemala, and Guatemala is also the department holding the capital. Placing it put
the whole national programme, 532,137 over eight years, into one department.

A unit that resolves to a province `pepfar_snu` does not emit is not emitted here either, so
the two connectors' admin1 vocabularies are the same set of names and a reader can put the
agency split beside the province total. Forty-six units are dropped that way and they carry no
value at all.

WHAT IS REFUSED, AND WHY IT IS NOT A LOSS

Fifteen countries publish no geography in this file: their only priority sub-national unit is
the country's own name. BRB, COL, GTM, GUY, HND, JAM, LAO, NIC, PAN, PER, PHL, SLV, SUR, THA
and TTO are therefore not emitted at all, because a national figure under a province's label is
the trap `pepfar_snu` was rewritten to avoid. `pepfar_agency` already holds those 15 countries
at national level, which is the grain the file actually supports. Three more countries, BHS,
BLZ and KHM, have rows here and no numbers in any of them.

Everything else places: 999 of the 1,015 units that carry a value, over 43 countries, and 99.02%
of the 527,123,747 this file records for the three indicators across every quarter. The 0.98%
left is the 15 countries above. The only value lost in a country this connector does emit is 43,
held by Congo on a unit called `Data reported above PSNU Level`, which is a heading and not a
place.

PARTNER SUMS, NOT DEDUPLICATED TOTALS

This file adds partners together. `pepfar_snu` reads the deduplicated geographic file. Where
two partners both report a patient the partner sum counts the patient twice and the geographic
file counts the patient once, so these province values sit at or above `pepfar_snu`'s for the
same province, and the gap is a property of the files and not an error in either. Of the 9,060
province-indicator-years both connectors cover, 8,282 agree to within 0.1 per cent and 777 sit
above. Of those 777, 54 sit at twice the deduplicated figure to within the same margin, and the
doubling is confined to five countries: Kazakhstan FY2021 to FY2025, Kyrgyzstan FY2021 to
FY2024, Tajikistan FY2021 to FY2023 and FY2025, Namibia FY2020 and FY2022, and Vietnam FY2018 to
FY2020. One province-indicator-year sits below, Lualaba in the Democratic Republic of the Congo
on HTS_TST_POS in FY2020 at 6,868 against 6,911.

So these rows are never subtracted from, or divided by, `pepfar_snu`'s rows. They are read
against each other: USAID against CDC, inside one province, in one year, where a patient counted
twice is counted twice on whichever side reports the patient.

WHAT THESE ROWS SHOW, AND THE ONE WAY TO MISREAD THEM

USAID and CDC report the same indicator in the same province and year at some point in 261 of
the 455 provinces, in 28 countries, and 35% of the province-indicator-years carry both. That is
the comparison this connector exists to serve. The
trap is that the set of agencies working a province changes: 36% of the province-indicator
series in this file change hands at least once, and FY2025 is where that happens on a scale
nothing before it approaches. USAID stops reporting in 151 province-indicator-years in FY2025
against nine in FY2024, and on TX_CURR alone it stops reporting in 47 provinces over ten
countries that held 1,953,646 patients in FY2024.

In three of those 47 provinces no agency reports TX_CURR in FY2025 at all, so PEPFAR's record of
the cohort ends there. Region 7 in the Dominican Republic held 1,144 patients in FY2024, and
Maharashtra and Telangana in India held 102,745 and 66,403, USAID's share being 62,009 and all
of Telangana. `pepfar_snu` ends in the same three provinces in the same year. No row exists in
FY2025 to carry a warning, so the only record of those three provinces is the count the run logs.

In the other 44 provinces, over nine countries, USAID held 1,824,090 patients in FY2024, and
almost none of those patients drop out of PEPFAR's count. In those 44 provinces the total across
all agencies falls by 3.0%, the median province still shows the whole departed cohort under
another agency, and 27 of the 44 provinces show more than nine tenths of the departed cohort.
Gauteng is the clearest case. USAID held 537,283 in Gauteng in FY2024 and reports nothing in
FY2025, while CDC goes from 681,535 to 1,166,174. Reading `on_art_count_usaid` on its own across
FY2024 and FY2025 therefore shows a collapse of nearly two million patients, where the count
across every agency in the 44 provinces USAID handed over falls by 3.0%.

Every row whose province did not carry the same agencies a year earlier says so, in
`agencies_here`, which names the agencies present in both years and what the departing agency
last held. A row carrying that field must be read against the other agencies in the same
province and year before the change is called a programme growing or shrinking.

THE CHECK THAT MATTERS, AND THE ONE THAT FAILS

Every run checks that the emitted provinces add back to this file's own national figure for the
same country, indicator, agency, year and quarter. Of 7,593 such cells, 5,860 reproduce the
national figure exactly and none exceeds it. The 1,733 that fall short are the 15 countries
above, which carry no province at all, and one Democratic Republic of the Congo cell holding 43
on `Data reported above PSNU Level`.

Every run also compares this file with the TopLine file `pepfar_agency` and `pepfar_panorama`
read, and that comparison does not come out clean. TopLine is a strict subset of this file. Of
7,593 country-indicator-agency-year-quarter cells, none exists in TopLine and not here, 188
exist here and not in TopLine, carrying 518,523, and 85 more disagree, with TopLine the lower
figure in all 85. The 273 cells fall in four years, 129 in FY2018, 114 in FY2019, 18 in FY2021
and 12 in FY2022, and most sit in the countries PEPFAR runs through a regional operating unit.
No cell from FY2023 on differs, so the years the funding cuts fall in are untouched. Before this
check existed the panel held Panama's FY2018 treatment cohort at 31 people where this file says
11,956 and the deduplicated geographic file says 11,932, Guatemala's at 281 where the two files
say 12,812 and 12,758, and Thailand's FY2019 at 2,450 where both files say 44,843. Two
independent files against one means TopLine is the short file.

The TopLine values are kept, because the ladder's rule is that a value is never replaced by
another file's figure. Every `pepfar_panorama` and `pepfar_agency` row whose annual value
differs from this file by more than 0.5 carries this file's figure beside its own in
`extra.partner_file_differs`, with the difference, the ratio and a note saying the TopLine value
is a floor (docs/ACCESS_LADDER.md section 9w). On the download of 2026-07-18 that flags 62
`pepfar_panorama` rows, 47 of which already carry `geographic_total_differs`, and 26
`pepfar_agency` rows. Where TopLine has no row for an agency at all, the other agencies' rows for
that country, indicator and year carry `agency_missing_from_topline`, which covers 43
country-indicator-years. Five country-indicator-years sit in this file with nothing in TopLine
for any agency, Barbados, Suriname and Trinidad and Tobago on TX_CURR in FY2018 and El Salvador
on TX_CURR and TX_NEW in FY2019. Those five have no row anywhere in the panel to carry a flag,
so every run logs them by name.

TARGETS

The file also carries the target PEPFAR set for every agency, place, indicator and year in the
country operational plan, which is agreed before the fiscal year begins. A target is never
emitted as a value. Every row whose agency held a target carries the target in
`extra.fy_target`, and where the result covers the whole year the row also carries
`result_to_target`. For TX_CURR a whole year means the Q4 snapshot and for a flow a year with
every quarter the release publishes. 11,979 of the 12,705 rows carry a target and 10,686 of
them carry the ratio. The FY2025 flows are the main exception, 921 rows, because the release
publishes part of FY2025 only. Targets come from this file and not from TopLine, because
TopLine's own target column is short of this file's in 124 cells.

The targets answer a question the results cannot, which is whether an agency's exit from a
province was planned. A row whose province lost an agency carries that agency's target for the
year in `agencies_here.left_target`. USAID left 47 provinces on TX_CURR in FY2025 and still held
an FY2025 target in 46 of them, 2,338,910 patients in total against the 1,953,646 USAID held in
those provinces in FY2024. The one exception is South West Ethiopia, where USAID held 48
patients. Earlier exits look different. In FY2020 USAID left 43 provinces and CDC left ten, and
neither agency held a target in any province it left. In FY2019 CDC held a target in one of the
17 provinces CDC left and USAID in two of the 20 provinces USAID left, and in FY2021 USAID held a
target in two of the 21 provinces USAID left. So the FY2025 exits were not in the plan when the
targets were set, and the exits of FY2019 to FY2021 almost all were. The run logs this count for
every agency and year in which an agency left five or more provinces on TX_CURR.

THE QUARTER TRAP

TX_CURR is a snapshot and its annual value is one quarter, not a sum. The quarter is chosen
once per country-indicator-year, the latest any agency's partners in any province report, and
every province and every agency is read at that same quarter — the rule `pepfar_agency` states
and for the same reason, that reading each province at its own last quarter puts the parts of
one partition at different dates and stops them adding to anything. The quarter chosen here
equals the quarter `pepfar_snu` reads the same country-indicator-year at in all 372 cases, so a
province's agency split and its total belong to the same date.

HTS_TST_POS and TX_NEW are cumulative and take the partial-year treatment `pepfar_panorama`
defines, through the same helpers, so a province and its country cannot disagree about which
years are short.

TAGGING: PEPFAR MER measures the PEPFAR programme footprint, not national totals, and a
province's value is the programme in that province and not the province's epidemic.
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
from . import pepfar_agency as _agency
from . import pepfar_panorama as _panorama
from . import pepfar_snu as _snu

log = logging.getLogger("hivimpact")

FILE_HINT = "partner_performance"
TOPLINE_HINT = "topline"

# The same three codes, the same canonical names and the same agency suffixes pepfar_agency
# uses, imported and not copied, so the national split and the provincial split cannot drift
# into two vocabularies for one thing.
MER_INDICATORS = dict(_agency.MER_INDICATORS)
SNAPSHOT_CANON = set(_agency.SNAPSHOT_CANON)
AGENCY_SUFFIX = dict(_agency.AGENCY_SUFFIX)
OTHER = _agency.OTHER

_KEY_COLS = ["Country", "ISO3", "Priority Sub-National Unit", "Funding Agency", "Indicator",
             "Numerator/Denominator"]
_VALUE_RE = re.compile(r"^(\d{4}) Quarter ([1-4]) Results$")
_TARGET_RE = re.compile(r"^(\d{4}) Targets$")

# Said on every row carrying a target. The target is evidence about intent, which is the one
# thing the results cannot show: an agency leaving a province it still held a target for had not
# planned to leave when the target was set.
TARGET_NOTE = (
    "the target PEPFAR set for this agency, indicator, place and year in the country operational "
    "plan agreed before the fiscal year began, as the Partner_Performance file records it. "
    "result_to_target is given only where the result covers the whole year, which for TX_CURR "
    "means a Q4 snapshot and for a flow means a year with every quarter the release publishes.")

# a priority sub-national unit that is a label and not a place
_NOT_A_PLACE = ("data reported above psnu level", "psnu placeholder")

# the published hierarchy, named the way pepfar_snu names it in `unit_level`
_LEVELS = ("SNU1", "SNU2", "SNU3")


def _num(cell) -> Optional[float]:
    if cell is None:
        return None
    s = str(cell).strip().replace(",", "")
    if s in ("", "nan", "NA", "N/A", "..."):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _suffix(agency) -> str:
    return AGENCY_SUFFIX.get(str(agency).strip().upper(), OTHER)


def result_to_target(value: float, target: Optional[float], full_year: bool) -> Optional[float]:
    """The result as a share of the target, or None where the share would mislead.

    A part-published year compared with a whole-year target reads as a shortfall that is only a
    shorter year, so the share is withheld there. The same helper serves pepfar_agency, so the
    national and the provincial rows cannot disagree about which years can be compared.
    """
    if not full_year or not target or target <= 0:
        return None
    return round(value / target, 4)


def partner_file_differs(value: float, pp_value: float, scope: str) -> Dict[str, object]:
    """The flag pepfar_panorama and pepfar_agency put on a TopLine value this file disagrees with.

    The value is never replaced. Replacing the value would give a row two source files, and
    Partner_Performance is a partner sum too, so the corrected figure would carry the same double
    count the TopLine figure does. The row keeps the TopLine value and carries this file's
    figure beside it, the rule pepfar_panorama already follows for the geographic file.
    """
    if pp_value > value:
        note = (f"PEPFAR's Partner_Performance file, which adds the same partners together as "
                f"the TopLine file this value comes from, gives {pp_value:,.0f} for this {scope}. "
                f"The TopLine file is missing reporting that the Partner_Performance file holds, "
                f"so this value is a floor, and a change against another year may be missing "
                f"reporting and not a change in services. The value is kept as TopLine publishes "
                f"it (docs/ACCESS_LADDER.md section 9w).")
    else:
        note = (f"PEPFAR's Partner_Performance file, which adds the same partners together as "
                f"the TopLine file this value comes from, gives {pp_value:,.0f} for this {scope}, "
                f"below this value. The two files should agree, and on the download of 2026-07-18 "
                f"no TopLine value sat above the Partner_Performance figure, so a row carrying "
                f"this note is a new disagreement and neither file can be taken as right.")
    return {"partner_performance_value": pp_value, "difference": pp_value - value,
            "ratio": round(value / pp_value, 4) if pp_value else None, "note": note}


# Partner_Performance read to the country, kept for the run, because pepfar_panorama and
# pepfar_agency both test their TopLine totals against this file and reading 26 MB twice buys
# nothing.
_NATIONAL_CACHE: Dict[tuple, tuple] = {}


def partner_performance_national(raw_dir, wanted=None, start_year: int = 2000,
                                 end_year: int = 2035):
    """This file added to the country by funding agency, quarter by quarter, with the targets.

    Returns (results, targets), where results is {(iso3, code, agency_suffix, year): [q1, q2,
    q3, q4]} with None for a quarter nothing reported, and targets is {(iso3, code,
    agency_suffix, year): target}. Returns None when the file is not on disk. Every priority
    sub-national unit is included, the ones named after the country as well, so the figure is
    the whole country and not only the part this connector can place.

    pepfar_agency and pepfar_panorama call this to test the TopLine file they read. Both files
    add partners together, so the two should agree cell for cell, and where they disagree on
    this download the TopLine file is the one missing reporting (docs/ACCESS_LADDER.md 9w).
    """
    raw_dir = Path(raw_dir)
    files = sorted(p for p in list(raw_dir.glob("*.zip")) + list(raw_dir.glob("*.txt"))
                   if FILE_HINT in p.name.lower()) if raw_dir.exists() else []
    if not files:
        return None
    key = (tuple((str(p.resolve()), p.stat().st_mtime, p.stat().st_size) for p in files),
           frozenset(wanted) if wanted else None, start_year, end_year)
    if key in _NATIONAL_CACHE:
        return _NATIONAL_CACHE[key]
    iso_cache: Dict[tuple, Optional[str]] = {}
    total: Optional[pd.DataFrame] = None
    for path in files:
        for chunk in PEPFARAgencySNUConnector._chunks(path):
            sub = chunk[chunk["Indicator"].isin(MER_INDICATORS)
                        & chunk["Numerator/Denominator"].fillna("N").str.strip().str.upper().eq("N")]
            if sub.empty:
                continue
            pairs = list(zip(sub["ISO3"].fillna(""), sub["Country"].fillna("")))
            for k in set(pairs):
                if k not in iso_cache:
                    iso_cache[k] = to_iso3(k[0]) or to_iso3(k[1])
            sub = sub.assign(_iso3=[iso_cache[k] for k in pairs],
                             _suf=sub["Funding Agency"].map(_suffix)).dropna(subset=["_iso3"])
            if wanted:
                sub = sub[sub["_iso3"].isin(wanted)]
            if sub.empty:
                continue
            cols = [c for c in sub.columns if _VALUE_RE.match(c) or _TARGET_RE.match(c)]
            vals = sub[cols].apply(lambda c: pd.to_numeric(
                c.astype(str).str.replace(",", "", regex=False), errors="coerce"))
            part = vals.groupby([sub["_iso3"], sub["Indicator"], sub["_suf"]]).sum(min_count=1)
            # adding two chunks keeps a cell blank only where both chunks left it blank
            total = part if total is None else total.add(part, fill_value=0)
    results: Dict[tuple, List[Optional[float]]] = {}
    targets: Dict[tuple, float] = {}
    if total is not None:
        for (iso3, code, suf), row in total.iterrows():
            for col, v in row.items():
                if pd.isna(v):
                    continue
                if m := _VALUE_RE.match(col):
                    y, q = int(m.group(1)), int(m.group(2))
                    if start_year <= y <= end_year:
                        results.setdefault((iso3, code, suf, y), [None] * 4)[q - 1] = float(v)
                elif m := _TARGET_RE.match(col):
                    y = int(m.group(1))
                    if start_year <= y <= end_year:
                        targets[(iso3, code, suf, y)] = float(v)
    _NATIONAL_CACHE[key] = (results, targets)
    return results, targets


def _topline_cells(raw_dir: Path, wanted=None) -> Optional[Dict[tuple, float]]:
    """The TopLine file's own cells, for the comparison in the docstring.

    Returns {(iso3, code, agency_suffix, year, quarter): value} or None when TopLine is not on
    disk. Read once per run and thrown away after the comparison is logged. The row filter is
    the one pepfar_agency applies, total numerator rows only, because TopLine also carries the
    same service broken down by age and by sex and adding those on top of the totals would
    manufacture a disagreement that is not there.
    """
    files = sorted(p for p in list(raw_dir.glob("*.zip")) + list(raw_dir.glob("*.txt"))
                   if TOPLINE_HINT in p.name.lower()) if raw_dir.exists() else []
    if not files:
        return None
    out: Dict[tuple, float] = {}
    iso_cache: Dict[tuple, Optional[str]] = {}
    qcols = ["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"]
    keep = set(_KEY_COLS + ["Fiscal Year", "Standardized Disaggregate"] + qcols)
    read = dict(sep="\t", dtype=str, chunksize=100_000, on_bad_lines="skip", low_memory=False,
                usecols=lambda c: c.strip() in keep)
    for path in files:
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as z:
                for member in [m for m in z.namelist() if m.lower().endswith((".txt", ".csv"))]:
                    with z.open(member) as fh:
                        for chunk in pd.read_csv(fh, **read):
                            _topline_add(chunk, out, iso_cache, qcols, wanted)
        else:
            for chunk in pd.read_csv(path, **read):
                _topline_add(chunk, out, iso_cache, qcols, wanted)
    return out


def _topline_add(chunk, out, iso_cache, qcols, wanted) -> None:
    chunk.columns = [c.strip() for c in chunk.columns]
    if "Standardized Disaggregate" not in chunk.columns or "Fiscal Year" not in chunk.columns:
        return
    sub = chunk[chunk["Indicator"].isin(MER_INDICATORS)
                & chunk["Numerator/Denominator"].fillna("N").str.strip().str.upper().eq("N")
                & chunk["Standardized Disaggregate"].astype(str).str.contains(
                    "Total Numerator", case=False, na=False)]
    if sub.empty:
        return
    for _, r in sub.iterrows():
        k = (str(r.get("ISO3") or ""), str(r.get("Country") or ""))
        if k not in iso_cache:
            iso_cache[k] = to_iso3(k[0]) or to_iso3(k[1])
        iso3 = iso_cache[k]
        if not iso3 or (wanted and iso3 not in wanted):
            continue
        try:
            year = int(str(r.get("Fiscal Year"))[:4])
        except (TypeError, ValueError):
            continue
        suf = _suffix(r.get("Funding Agency"))
        for i, c in enumerate(qcols, start=1):
            v = _num(r.get(c))
            if v is None:
                continue
            key = (iso3, r["Indicator"], suf, year, i)
            out[key] = out.get(key, 0.0) + v


class PEPFARAgencySNUConnector(BaseConnector):
    source_id = "pepfar_agency_snu"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("PEPFAR MER by funding agency at the province, county, state or department: "
                   "TX_CURR, HTS_TST_POS and TX_NEW split USAID / HHS-CDC / other agency inside "
                   "each sub-national unit, 455 units over 43 countries, FY2018 to FY2025. The "
                   "cross pepfar_agency and pepfar_snu each hold one half of. Programme "
                   "footprint, not provincial totals, and a partner sum, so a patient two "
                   "partners both report is counted twice. Each row carries the agency's "
                   "planned target for the year in extra, never as a value.")

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ---------------------------------------------------------------
    def _files(self) -> List[Path]:
        if not self.raw_dir.exists():
            return []
        candidates = sorted(list(self.raw_dir.glob("*.zip")) + list(self.raw_dir.glob("*.txt")))
        kept = [p for p in candidates if FILE_HINT in p.name.lower()]
        if len(kept) < len(candidates):
            log.info("pepfar_agency_snu: reading %d of %d archive(s) in %s, the ones named %r. "
                     "Not read: %s", len(kept), len(candidates), self.raw_dir, FILE_HINT,
                     [p.name for p in candidates if p not in kept])
        return kept

    @staticmethod
    def _chunks(path: Path):
        read = dict(sep="\t", dtype=str, chunksize=100_000, on_bad_lines="skip",
                    low_memory=False,
                    usecols=lambda c: (c.strip() in _KEY_COLS or _VALUE_RE.match(c.strip())
                                       or _TARGET_RE.match(c.strip())))
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as z:
                for member in [m for m in z.namelist() if m.lower().endswith((".txt", ".csv"))]:
                    with z.open(member) as fh:
                        for chunk in pd.read_csv(fh, **read):
                            chunk.columns = [c.strip() for c in chunk.columns]
                            yield chunk
        else:
            for chunk in pd.read_csv(path, **read):
                chunk.columns = [c.strip() for c in chunk.columns]
                yield chunk

    def _accumulate(self, chunk: pd.DataFrame, agg: Dict[tuple, List[Optional[float]]],
                    names: Dict[str, str], wanted, start_year: int, end_year: int,
                    targets: Optional[Dict[tuple, float]] = None) -> None:
        """Add a chunk, keyed on the priority sub-national unit as published.

        The unit is not placed here. Which level of the hierarchy a country's units are named at
        is a fact about the whole country and cannot be decided one row at a time. Targets are
        kept on the same key, apart from the results, because a target with no result beside it
        is how an agency that left a province still shows in this file.
        """
        sub = chunk[chunk["Indicator"].isin(MER_INDICATORS)
                    & chunk["Numerator/Denominator"].fillna("N").str.strip().str.upper().eq("N")]
        if sub.empty:
            return
        cells = [(c, int(m.group(1)), int(m.group(2)))
                 for c in sub.columns if (m := _VALUE_RE.match(c))
                 and start_year <= int(m.group(1)) <= end_year]
        tcells = [(c, int(m.group(1)))
                  for c in sub.columns if (m := _TARGET_RE.match(c))
                  and start_year <= int(m.group(1)) <= end_year] if targets is not None else []
        if not cells:
            return
        for _, r in sub.iterrows():
            iso3 = to_iso3(r.get("ISO3") or "") or to_iso3(r.get("Country") or "")
            if not iso3 or (wanted and iso3 not in wanted):
                continue
            psnu = str(r.get("Priority Sub-National Unit") or "").strip()
            if not psnu:
                continue
            names[iso3] = str(r.get("Country") or "").strip() or iso3
            base = MER_INDICATORS[r["Indicator"]]
            suf = _suffix(r.get("Funding Agency"))
            for col, year, q in cells:
                v = _num(r.get(col))
                if v is None:
                    continue
                key = (iso3, psnu, base, suf, year)
                cur = agg.setdefault(key, [None, None, None, None])
                cur[q - 1] = (cur[q - 1] or 0.0) + v
            for col, year in tcells:
                v = _num(r.get(col))
                if v is None:
                    continue
                key = (iso3, psnu, base, suf, year)
                targets[key] = targets.get(key, 0.0) + v

    # -- placing ---------------------------------------------------------------
    @staticmethod
    def _levels(agg, vocab) -> Dict[str, Optional[int]]:
        """Which level of the hierarchy each country names its priority sub-national units at.

        Counted over the country's units, ignoring the one named after the country itself, and
        settled once for the country. A country whose units match nothing gets None and is not
        emitted.
        """
        by_country: Dict[str, set] = {}
        for (iso3, psnu, _b, _s, _y) in agg:
            by_country.setdefault(iso3, set()).add(psnu)
        out: Dict[str, Optional[int]] = {}
        for iso3, psnus in by_country.items():
            entry = vocab.get(iso3)
            if not entry or "level" not in entry:
                out[iso3] = None
                continue
            real = [p for p in psnus if _snu._fold(p) not in entry["national_names"]]
            hits = [sum(_snu._fold(p) in entry["lookup"][i] for p in real) for i in range(3)]
            best = max(range(3), key=lambda i: (hits[i], -i))
            out[iso3] = best if hits[best] else None
        return out

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        files = self._files()
        if not files:
            log.warning("pepfar_agency_snu: no Partner Performance file in %s — download it from "
                        "https://data.pepfar.gov/datasets", self.raw_dir)
            return
        vocab = _snu.emitted_units(self.raw_dir, wanted)
        if vocab is None:
            log.warning("pepfar_agency_snu: the Enhanced Geographical Analysis file is not in %s. "
                        "Without it a priority sub-national unit cannot be placed in a province, "
                        "and placing one by name alone puts a national figure in a department. "
                        "Nothing emitted.", self.raw_dir)
            return

        agg: Dict[tuple, List[Optional[float]]] = {}
        names: Dict[str, str] = {}
        targets: Dict[tuple, float] = {}
        for path in files:
            try:
                for chunk in self._chunks(path):
                    self._accumulate(chunk, agg, names, wanted, start_year, end_year, targets)
            except Exception as exc:
                log.warning("pepfar_agency_snu: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_agency_snu: read %s", path.name)
        if not agg:
            log.warning("pepfar_agency_snu: the Partner Performance file carried no rows for "
                        "TX_CURR, HTS_TST_POS or TX_NEW")
            return

        # Cadence is voted on the country's own rows, before any unit is placed, so that
        # regrouping units into provinces cannot change which quarters an indicator-year is held
        # to publish at. Same helper and same grouping as pepfar_agency.
        national: Dict[tuple, List[Optional[float]]] = {}
        for (iso3, _psnu, base, suf, year), vals in agg.items():
            cur = national.setdefault((iso3, base, suf, year), [None, None, None, None])
            for i, v in enumerate(vals):
                if v is not None:
                    cur[i] = (cur[i] or 0.0) + v
        cadence = _panorama.release_cadence(national, lambda k: (k[1], k[2], k[3]))
        latest_year = max((y for _, _, y in cadence), default=0)

        level = self._levels(agg, vocab)

        def place(iso3: str, psnu: str) -> Optional[str]:
            entry, i = vocab.get(iso3), level.get(iso3)
            if entry and i is not None and _snu._fold(psnu) not in entry["national_names"]:
                return entry["lookup"][i].get(_snu._fold(psnu))
            return None

        placed: Dict[tuple, List[Optional[float]]] = {}
        unplaced: Dict[str, Dict[str, float]] = {}
        for (iso3, psnu, base, suf, year), vals in agg.items():
            unit = place(iso3, psnu)
            if unit is None:
                book = unplaced.setdefault(iso3, {})
                book[psnu] = book.get(psnu, 0.0) + sum(v for v in vals if v is not None)
                continue
            cur = placed.setdefault((iso3, unit, base, suf, year), [None, None, None, None])
            for j, v in enumerate(vals):
                if v is not None:
                    cur[j] = (cur[j] or 0.0) + v
        # Targets placed by the same rule, so a province's target and its result are the same
        # set of priority sub-national units.
        placed_t: Dict[tuple, float] = {}
        for (iso3, psnu, base, suf, year), t in targets.items():
            unit = place(iso3, psnu)
            if unit is not None:
                k = (iso3, unit, base, suf, year)
                placed_t[k] = placed_t.get(k, 0.0) + t

        self._log_refusals(vocab, level, unplaced, names)
        self._log_reconstruction(national, placed)
        self._log_against_topline(national, wanted)

        # ONE QUARTER PER COUNTRY-INDICATOR-YEAR, across every province and every agency, so the
        # parts of one partition belong to one date. See THE QUARTER TRAP above.
        common_q: Dict[tuple, int] = {}
        for (iso3, _unit, base, _suf, year), vals in placed.items():
            if base not in SNAPSHOT_CANON:
                continue
            reported = [j for j, v in enumerate(vals) if v is not None]
            if reported:
                k = (iso3, base, year)
                common_q[k] = max(common_q.get(k, 0), reported[-1] + 1)

        # The annual figure for every series, settled before any row is built, because a row has
        # to be able to say which OTHER agency was in the same province a year earlier. An agency
        # handing a province to another agency moves both series at once and imitates a collapse,
        # and the series that collapsed is the one that no longer exists, so it emits no row to
        # carry the warning.
        values: Dict[tuple, float] = {}
        off_quarter: Dict[tuple, int] = {}
        for key, vals in placed.items():
            iso3, _unit, base, _suf, year = key
            if base in SNAPSHOT_CANON:
                q_now = common_q.get((iso3, base, year))
                v = vals[q_now - 1] if q_now else None
                if v is None:
                    if any(x is not None for x in vals):
                        off_quarter[(iso3, base, year)] = \
                            off_quarter.get((iso3, base, year), 0) + 1
                    continue
                values[key] = v
            else:
                nn = [v for v in vals if v is not None]
                if nn:
                    values[key] = sum(nn)
        present: Dict[tuple, Dict[str, float]] = {}
        for (iso3, unit, base, suf, year), v in values.items():
            present.setdefault((iso3, unit, base, year), {})[suf] = v

        n = 0
        emitted: set = set()
        for key, value in sorted(values.items()):
            iso3, unit, base, suf, year = key
            vals = placed[key]
            canonical = f"{base}_{suf}"
            nq = len([v for v in vals if v is not None])
            extra: Dict[str, object] = {
                "note": "PEPFAR MER by funding agency at the province — PROGRAMME FOOTPRINT, not "
                        "a provincial total, and a partner sum, so two partners reporting one "
                        "patient count the patient twice",
                "mer_indicator": [c for c, b in MER_INDICATORS.items() if b == base][0],
                "funding_agency": suf,
                "unit_level": vocab[iso3].get("level"),
                "psnu_level": _LEVELS[level[iso3]],
                "quarters_reported": nq,
                "interpretation": _agency.INTERPRETATION,
            }
            if extra["psnu_level"] != extra["unit_level"]:
                extra["placement"] = (
                    f"this file names {extra['psnu_level']} units and pepfar_snu emits "
                    f"{extra['unit_level']}, so this value is the sum of every "
                    f"{extra['psnu_level']} unit belonging to {unit}")

            if base in SNAPSHOT_CANON:
                q_now = common_q.get((iso3, base, year))
                extra["snapshot_quarter"] = q_now
                full_year = q_now == 4
                q_prev = common_q.get((iso3, base, year - 1))
                if q_prev and q_now != q_prev:
                    extra["snapshot_quarter_mismatch"] = (
                        f"snapshot taken from Q{q_now} of FY{year} but Q{q_prev} of FY{year - 1} — "
                        f"these are not twelve months apart, and the change between them is not "
                        f"an annual change.")
            else:
                here = cadence.get((base, suf, year), [])
                prev_cad = cadence.get((base, suf, year - 1)) or here
                truncated, same_span = _panorama.span_status(here, prev_cad, year, latest_year)
                extra["release_quarters"] = [f"Q{q}" for q in here]
                extra.update(_panorama.quarter_detail(
                    vals, placed.get((iso3, unit, base, suf, year - 1)), year, same_span))
                full_year = not truncated and nq >= len(here)
                if truncated or 0 < nq < len(here):
                    why = (f"FY{year} is part-published, carrying "
                           f"{', '.join('Q%d' % q for q in here)} where FY{year - 1} carries "
                           f"{', '.join('Q%d' % q for q in prev_cad)}" if truncated else
                           f"this agency reported {nq} of the "
                           f"{', '.join('Q%d' % q for q in here)} that FY{year} publishes in "
                           f"this province")
                    extra["partial_year"] = (
                        f"{why}. This annual total is a PARTIAL sum and must NOT be compared "
                        f"with full years or read as a decline.")
            # THE PLAN FOR THE YEAR. A result far above its target in the year another agency
            # left the province is the arriving agency absorbing patients it had not planned for,
            # which is what Gauteng's CDC figure shows in FY2025.
            t = placed_t.get(key)
            if t is not None:
                extra["fy_target"] = {"value": t,
                                      "result_to_target": result_to_target(value, t, full_year),
                                      "note": TARGET_NOTE}
            # WHO ELSE WAS HERE LAST YEAR. In 36% of the province-indicator series in this file
            # the set of agencies working the province changes at least once, and a province
            # handed from USAID to CDC shows as a USAID series ending and a CDC series starting
            # at about the same size. Read on its own, either half is a collapse or a surge.
            was = present.get((iso3, unit, base, year - 1), {})
            now = present.get((iso3, unit, base, year), {})
            gone = {a: was[a] for a in was if a not in now}
            came = {a: now[a] for a in now if a not in was and a != suf}
            if gone or came:
                note = (f"the agencies working {unit} are not the same in FY{year} as in "
                        f"FY{year - 1}. A province changing hands moves two series at once, so "
                        f"compare this value with the sum of every agency in the province before "
                        f"reading the change as a programme growing or shrinking.")
                # Whether the departure was in the plan. An agency leaving a province it held no
                # target for had been planned out of it, and an agency leaving a province it
                # still held a target for had not been, when the targets were set.
                left_target = {a: placed_t.get((iso3, unit, base, a, year)) for a in sorted(gone)}
                for a, lt in left_target.items():
                    if lt and lt > 0:
                        note += (f" {a} still held an FY{year} target of {lt:,.0f} here and "
                                 f"reported nothing, so the {a} exit was not in the plan when "
                                 f"the targets were set.")
                    else:
                        note += (f" {a} held no FY{year} target here, which is what a planned "
                                 f"exit looks like.")
                extra["agencies_here"] = {
                    "this_year": sorted(now), "last_year": sorted(was),
                    "left": {a: v for a, v in sorted(gone.items())},
                    "left_target": left_target,
                    "arrived": {a: v for a, v in sorted(came.items())},
                    "note": note,
                }

            yield self.make_row(
                country_iso3=iso3, country_name=names.get(iso3, ""), admin1=unit,
                indicator_id=canonical, year=year, value=value, unit="count",
                source_url="https://data.pepfar.gov/datasets",
                source_indicator_code=f"MER.{extra['mer_indicator']}.{suf}",
                extra=extra,
            )
            n += 1
            emitted.add((iso3, unit))
        for (iso3, base, year), k in sorted(off_quarter.items()):
            log.info("pepfar_agency_snu: %s %s FY%d — %d province-agency series reported this year "
                     "but not in Q%d, the quarter the country is read at; they are absent from "
                     "that year and not carried forward", iso3, base, year, k,
                     common_q.get((iso3, base, year), 0))
        self._log_departures(present, placed_t, latest_year)
        log.info("pepfar_agency_snu: emitted %d rows over %d provinces in %d countries",
                 n, len(emitted), len({i for i, _ in emitted}))

    @staticmethod
    def _log_departures(present, placed_t, latest_year) -> None:
        """How many provinces each agency left in each year, and how many of them it had a target for.

        Counted once per province, not once per row, because agencies_here sits on every row of
        a province that changed hands. A province every agency left at once emits no row at all
        for that year, so the only record of that province is the count logged here.
        """
        book: Dict[tuple, List[float]] = {}
        vacated = 0
        for (iso3, unit, base, year), was in present.items():
            if year >= latest_year:
                continue
            now = present.get((iso3, unit, base, year + 1), {})
            if not now:
                vacated += 1
            for a, v in was.items():
                if a in now:
                    continue
                t = placed_t.get((iso3, unit, base, a, year + 1)) or 0.0
                b = book.setdefault((base, a, year + 1), [0, 0, 0.0, 0.0])
                b[0] += 1
                b[3] += v
                if t > 0:
                    b[1] += 1
                    b[2] += t
        for (base, a, year), (k, with_t, t, held) in sorted(book.items()):
            if base not in SNAPSHOT_CANON or k < 5:
                continue
            log.info("pepfar_agency_snu: %s left %d province(s) on %s in FY%d, holding %s the "
                     "year before, and still held an FY%d target in %d of them (%s in total)",
                     a, k, base, year, f"{held:,.0f}", year, with_t, f"{t:,.0f}")
        if vacated:
            log.info("pepfar_agency_snu: %d province-indicator-years have no agency at all the "
                     "year after one reported, so no row carries agencies_here for them", vacated)

    # -- the three checks ------------------------------------------------------
    @staticmethod
    def _log_refusals(vocab, level, unplaced, names) -> None:
        national_only = sorted(i for i, lv in level.items() if lv is None)
        if national_only:
            log.info("pepfar_agency_snu: %d countries name no province in this file — their only "
                     "priority sub-national unit is the country's own name, which is a national "
                     "figure under a province's label. Not emitted; pepfar_agency holds them at "
                     "country level: %s", len(national_only), ", ".join(national_only))
        labels: Dict[str, float] = {}   # a heading in the geography column, not a place
        places: Dict[str, float] = {}   # a place pepfar_snu does not emit a province for
        for iso3, book in unplaced.items():
            if level.get(iso3) is None:
                continue
            for psnu, v in book.items():
                low = psnu.lower()
                book_out = labels if any(t in low for t in _NOT_A_PLACE) else places
                book_out[f"{iso3} {psnu}"] = v
        if labels:
            log.info("pepfar_agency_snu: %d unit(s) are a heading and not a place, carrying %s. "
                     "The value belongs to the country and to no province, so it is left out: %s",
                     len(labels), f"{sum(labels.values()):,.0f}",
                     ", ".join(f"{k} ({v:,.0f})" for k, v in sorted(labels.items())))
        if places:
            carry = {k: v for k, v in places.items() if v}
            log.info("pepfar_agency_snu: %d priority sub-national unit(s) name a place that "
                     "pepfar_snu emits no province for, so the agency split has nothing to sit "
                     "beside and is not emitted. Carrying %s in total, and %d of them carry "
                     "nothing at all%s", len(places), f"{sum(places.values()):,.0f}",
                     len(places) - len(carry),
                     (". The ones carrying anything: "
                      + ", ".join(f"{k} ({v:,.0f})" for k, v in sorted(
                          carry.items(), key=lambda kv: -kv[1])[:10])) if carry else "")

    @staticmethod
    def _log_reconstruction(national, placed) -> None:
        """Do the emitted provinces add back to this file's own national figure?

        A province sum ABOVE the national figure means a unit has been placed twice and is a
        fault in the placement. A province sum below it is the part of the country this file
        attributes to no province, which is a fact about the file.
        """
        prov: Dict[tuple, List[Optional[float]]] = {}
        for (iso3, _unit, base, suf, year), vals in placed.items():
            cur = prov.setdefault((iso3, base, suf, year), [None, None, None, None])
            for i, v in enumerate(vals):
                if v is not None:
                    cur[i] = (cur[i] or 0.0) + v
        equal = above = below = 0
        worst: List[tuple] = []
        for key, vals in national.items():
            got = prov.get(key, [None, None, None, None])
            for i, v in enumerate(vals):
                if v is None:
                    continue
                g = got[i] or 0.0
                if abs(g - v) <= 0.5:
                    equal += 1
                elif g > v:
                    above += 1
                    worst.append((g - v, key, i + 1, v, g))
                else:
                    below += 1
        log.info("pepfar_agency_snu: the emitted provinces reproduce this file's own national "
                 "figure in %d of %d country-indicator-agency-year-quarter cells, exceed it in "
                 "%d and fall short in %d (the countries naming no province, plus whatever the "
                 "file attributes to no unit)", equal, equal + above + below, above, below)
        if worst:
            worst.sort(reverse=True)
            for gap, key, q, nat, got in worst[:5]:
                log.warning("pepfar_agency_snu: %s %s_%s FY%d Q%d — provinces sum to %s against a "
                            "national %s, a surplus of %s. A unit is being placed twice.",
                            key[0], key[1], key[2], key[3], q, f"{got:,.0f}", f"{nat:,.0f}",
                            f"{gap:,.0f}")

    def _log_against_topline(self, national, wanted) -> None:
        """Does this file agree with the TopLine file two other connectors read?

        It does not, and the disagreement is one-sided. See THE CHECK THAT MATTERS above. The
        comparison is made every run because a later download may fix it, and because a silent
        understatement of Panama's FY2018 treatment cohort by a factor of 386 is the kind of thing
        a panel carries for years.
        """
        top = _topline_cells(self.raw_dir, wanted)
        if top is None:
            log.info("pepfar_agency_snu: no TopLine file on disk, so this file's national totals "
                     "were not compared with the ones pepfar_agency emits")
            return
        here: Dict[tuple, float] = {}
        for (iso3, base, suf, year), vals in national.items():
            code = [c for c, b in MER_INDICATORS.items() if b == base][0]
            for i, v in enumerate(vals, start=1):
                if v is not None:
                    here[(iso3, code, suf, year, i)] = v
        only_here = {k: v for k, v in here.items() if k not in top}
        only_top = {k: v for k, v in top.items() if k not in here}
        differ = {k: (top[k], v) for k, v in here.items()
                  if k in top and abs(top[k] - v) > 0.5}
        log.info("pepfar_agency_snu: against the TopLine file pepfar_agency and pepfar_panorama "
                 "read — %d cells agree, %d are in TopLine only, %d are here only (carrying %s) "
                 "and %d disagree", len(here) - len(only_here) - len(differ), len(only_top),
                 len(only_here), f"{sum(only_here.values()):,.0f}", len(differ))
        if not only_here and not differ:
            return
        # The cells above are quarters, and a quarter is not what the panel holds. The shortfall
        # a reader meets is the annual figure: TX_CURR at the one quarter the country is read at,
        # which is the latest quarter any agency reports in the TopLine file, and a flow summed
        # over its quarters. Adding TX_CURR's four quarters together would count the same
        # patients four times, which is what the first version of this log did.
        snap_code = {c for c, b in MER_INDICATORS.items() if b in SNAPSHOT_CANON}
        tq: Dict[tuple, int] = {}
        hq: Dict[tuple, int] = {}
        for book, cells in ((tq, top), (hq, here)):
            for (iso3, code, _s, year, q) in cells:
                if code in snap_code:
                    book[(iso3, code, year)] = max(book.get((iso3, code, year), 0), q)
        short: Dict[tuple, float] = {}
        for (iso3, code, suf, year) in {k[:4] for k in here}:
            if code in snap_code:
                q = tq.get((iso3, code, year)) or hq.get((iso3, code, year))
                h, t = here.get((iso3, code, suf, year, q)), top.get((iso3, code, suf, year, q))
            else:
                h = sum(here.get((iso3, code, suf, year, q), 0.0) for q in (1, 2, 3, 4))
                t = sum(top.get((iso3, code, suf, year, q), 0.0) for q in (1, 2, 3, 4))
            gap = (h or 0.0) - (t or 0.0)
            if abs(gap) > 0.5:
                short[(iso3, code, suf, year)] = gap
        if not short:
            return
        years = sorted({k[3] for k in short})
        # Agencies are added within one country-year, where all of them are read at the same
        # quarter, and never across years, because a TX_CURR shortfall in FY2018 and another in
        # FY2019 are mostly the same patients missing twice.
        tx: Dict[tuple, float] = {}
        for (iso3, code, _s, year), gap in short.items():
            if code in snap_code:
                tx[(iso3, year)] = tx.get((iso3, year), 0.0) + gap
        worst = sorted(tx.items(), key=lambda kv: -kv[1])
        flows = {k: v for k, v in short.items() if k[1] not in snap_code}
        log.warning("pepfar_agency_snu: the TopLine file is SHORT, not this one — no cell exists "
                    "there and not here. At the annual grain the panel holds, %d agency-years "
                    "over %d countries fall short, all in FY%s. On TX_CURR, the people on "
                    "treatment at the quarter each country is read at, the shortfall by "
                    "country-year is %s. On new diagnoses and initiations %d agency-years fall "
                    "short, the largest %s. pepfar_panorama and pepfar_agency keep the TopLine "
                    "values and flag each affected row in extra.partner_file_differs.",
                    len(short), len({k[0] for k in short}), ", FY".join(str(y) for y in years),
                    ", ".join(f"{k[0]} FY{k[1]} {v:,.0f}" for k, v in worst if v > 0.5), len(flows),
                    ", ".join(f"{k[0]} {k[1]} {k[2]} FY{k[3]} {v:,.0f}" for k, v in
                              sorted(flows.items(), key=lambda kv: -kv[1])[:3]))
