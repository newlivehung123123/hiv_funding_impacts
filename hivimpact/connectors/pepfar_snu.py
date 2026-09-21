"""
PEPFAR sub-national (SNU) connector — the admin1 layer no aggregator publishes.

UNAIDS, WHO and the World Bank all stop at the country. PEPFAR's Enhanced Geographical
Analysis file goes three levels below it, quarterly, from 2016 to 2025, which is the only
place in this pipeline where a funding cut can be watched land unevenly INSIDE a country.
That matters because a national total can hold steady while whole provinces lose their
implementing partner.

Access: download `Enhanced_Geographical_Analysis.zip` from https://data.pepfar.gov/datasets
and drop the ZIP into `data/raw/pepfar/` (no need to unzip — the `.txt` inside is read
directly). 157 MB unzipped, 624,800 rows, read in chunks. The ISO3 column names 59 countries
and two more, Bahamas and Belize, carry a blank ISO3 and are resolved from the Country column,
so the file covers 61.

FORMAT (verified 2026-08-04): tab-separated, WIDE. One row per
(Operating Unit, Country, ISO3, Indicator, Description, Numerator/Denominator, Modality,
SNU1, SNU2, SNU3), and 50 value columns — `{year} Targets` and `{year} Quarter {1-4}
Results` for 2016-2025. Targets are intent and are not read here.

WHAT IT DOES NOT HAVE: a funding agency. This file carries no agency column, and neither do
the two `Site_Performance_*` files. An entry of 2026-08-04 said that agency by province could
not be built from PEPFAR's public data at all, and that entry was wrong (corrected 2026-09-19,
docs/ACCESS_LADDER.md section 9w). `Partner_Performance.zip` names the funding agency of every
partner in every priority sub-national unit from FY2018 to FY2025. Among the 26 countries this
connector emits provinces for, Partner_Performance's units carry the same names as this
connector's provinces in 17 and sit lower, at district level, in nine, two levels lower in
Malawi and one level lower in the other eight. Partner_Performance
adds every partner's count without removing the people two partners both report, so
Partner_Performance's totals run above this file's and are never a substitute for this file.
The agency split in this panel stays national until a connector reads Partner_Performance.

This file itself is deduplicated, which is why `national_quarters` below is the check
pepfar_panorama runs its partner-summed national totals against.

TWO DOUBLE-COUNTING TRAPS, both checked before a single row was emitted:

1. **Modality.** HTS_TST and HTS_TST_POS carry 28 modality values including a blank one,
   and a blank category that turned out to be a TOTAL would double every count summed
   over it. The blank modality is not a total. The blank modality is how FY2016 and FY2017
   were reported, 78,545,152 and 87,552,680 tests and positives together with every named
   modality at zero, and the named modalities are how FY2018 onward is reported with the
   blank at zero. Counted at the level this connector emits, one country-unit-indicator-year,
   the two sides both carry a value in 26 unit-years out of 8,796, every one of the 26 in
   FY2025 and in the Dominican Republic or Mozambique, and the blank side in those 26 holds
   26,920 against 20,000,990 on the named side in the same year, 0.0038% of the two codes'
   total. A residual that size is not a total, so summing over modality is correct.

2. **Ragged depth.** Some units hold both an SNU3-named row and an SNU3-blank row, which
   would be a total-plus-parts pair if the blank row carried the unit's sum. The blank row
   does not carry the sum. Over the six codes and all ten years, 1,160 unit-indicator-quarter
   cells carry a value on both sides, 537 in the 26 countries read at SNU1 and 623 in the 35
   whose only SNU1 is the country name, and the two sides are equal in five of the 1,160.
   Each of those five cells holds one named SNU3 unit and values of 3, 5, 7, 62 and 71, which
   is two small numbers coinciding and not a total over its parts. In the other 1,155 the
   blank side runs from 0.002 to 221 times the named sum. The blank rows hold the part of a
   unit that the country attributed to no district, so summing every row up to the emitted
   unit is correct. Three countries put a large share of their programme on such rows, 26% of
   the Dominican Republic's six-code total, 4.2% of Laos's and 3.8% of Thailand's, which says
   how much district detail those three publish and is not a double count.

   Correction of 2026-09-20. An entry of 2026-08-04 recorded that zero groups carry a value
   on both sides. That count is wrong and the figures above are the recount. The conclusion
   the 2026-08-04 entry supported still stands, because the blank rows are residuals.

TWO LEVELS, BECAUSE 35 COUNTRIES PUBLISH A NATIONAL TOTAL AT SNU1: 35 of the 61 countries
publish a single "sub-national unit" that is the country itself, SNU1 "Thailand" for Thailand
and "Burma" for Burma. Those are national figures wearing a province's label, and emitting
them would duplicate `pepfar_panorama` under a fake admin1. In all 35, every row carrying a
value names a Sub-National Unit 2, and the SNU2 names are provinces, departments, states or
districts (Thailand 17 provinces, Myanmar 14 states and regions, Guatemala 19 departments,
Cambodia six provinces, Belize three districts). So a country whose only SNU1 is its own name
is read one level down instead of being dropped, and the other 26 countries are read at SNU1
(Kenya 47 counties, Nigeria 37 states, Vietnam 35 provinces, Cote d'Ivoire 34, Tanzania 32,
Ukraine 27 ...). Every row says which level it came from, in `extra.unit_level`.

Three SNU2 labels are not a place and are not read as one, a blank, "Data above SNU2" (the
part of the country's total the country attributed to no unit) and a name beginning with an
underscore (PEPFAR's own aggregate stand-in, `_Peru Aggregated PSNU`). Over the six codes read
here, "Data above SNU2" carries zero in all 35 countries and no row with a blank SNU2 carries
a value, so the only countries losing anything to those labels are Peru, whose entire
programme sits on `_Peru Aggregated PSNU`, and Colombia, where `_Colombia Aggregated PSNU`
holds 99.88% of the total and Antioquia the rest.

A country is read at SNU2 only where two or more of its SNU2 units carry a value, since a
country whose whole programme sits on one unit is publishing a national total again under a
smaller label. Over the six codes that test admits 29 of the 35 countries and 203 units, and
it excludes Bahamas (New Providence Island alone), Barbados (Saint Michael Parish alone),
Colombia, Peru, Guyana and Trinidad and Tobago. The same test is applied a second time per
indicator-year, which drops a further 100 country-indicator-years out of 5,446 where the
country named several units on other indicators and only one there (Papua New Guinea 43,
Indonesia 15, Suriname 11, China seven, Ghana six and ten countries with fewer than five).

Correction of 2026-09-20. A count of 2026-09-19 gave 31 countries and 239 units, and a count
before it gave 30 and 238. The 239 counts every one of the 35 indicators in the file, and 203
is the count over the six codes this connector reads. Guyana and Trinidad and Tobago reach two
units only on indicators the connector does not read, which is why 31 becomes 29. The count of
238 took SNU2 names from every row and so included Roraima in Brazil and Nickerie District in
Suriname, which carry no value.

Correction of 2026-09-20. The count of 35 national-only countries was 33 of 59 on 2026-08-04
because Bahamas and Belize carry no ISO3 code in this file, and a count grouped on the ISO3
column leaves both out. This connector resolves a country from the Country column when ISO3 is
blank.

UNIT NAMES: published names are kept as they are, with two exceptions at SNU1 that exist to
make the panel joinable, a leading province code ("ec Eastern Cape Province") and a trailing
" Province", both removed. That touches 19 names in two countries (ZAF, ZMB), collides
nothing, and makes PEPFAR's nine South African provinces match the nine Thembisa already
contributes, so the programme footprint and the modelled provincial total can be read against
each other for the first time. Neither exception is applied at SNU2, where no such join
exists and where removing a trailing " Province" would turn Sierra Leone's Eastern Province
into "Eastern" and would leave Laos with "Vientiane" beside "Vientiane Capital", which are two
different units. No SNU2 name collides with another in its country, and the one SNU2 unit
named after its own country, Guatemala, is a real department among the 19 Guatemala publishes.

TAGGING: PEPFAR MER measures the PEPFAR programme footprint, NOT provincial totals, and
provinces do not sum to the national total. source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import re
import unicodedata
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType
# Reporting cadence and the quarters behind a cumulative total are decided in one place for
# every connector reading this file, so a province and its country cannot disagree about
# which years are short.
from . import pepfar_panorama as _panorama

log = logging.getLogger("hivimpact")

FILE_HINT = "enhanced_geographical"

# MER code -> (canonical_id, is_snapshot). A snapshot's annual value is its latest
# reported quarter; a flow's is the sum of the quarters it reports.
MER = {
    "TX_CURR":     ("on_art_count", True),
    "HTS_TST_POS": ("new_diagnoses", False),
    "PrEP_NEW":    ("prep_recipients", False),
    "TX_PVLS":     ("viral_suppression_count", True),
    "TX_NEW":      ("art_initiations", False),
    "HTS_TST":     ("hiv_tests_performed", False),
}
# TX_PVLS publishes a denominator too (people on ART with a viral-load result in the last
# 12 months), so the third 95 can be computed at province level instead of inferred.
PCT_FROM = {"TX_PVLS": "viral_suppression_pct"}

YEARS = range(2016, 2026)
QUARTERS = (1, 2, 3, 4)

_COLS = ["Country", "ISO3", "Indicator", "Numerator/Denominator", "Modality",
         "Sub-National Unit 1", "Sub-National Unit 2"]
_VALUE_COLS = [f"{y} Quarter {q} Results" for y in YEARS for q in QUARTERS]

# SNU2 labels that are not a place. `Data above SNU2` is the part of a country's total that the
# country did not attribute to any unit, and a leading underscore marks PEPFAR's own aggregate
# stand-in (`_Peru Aggregated PSNU`). Neither is emitted, and both are logged as a share.
_ABOVE_SNU2 = "data above snu2"


def _admin1(name: str) -> str:
    """Published SNU1 name, minus the two decorations that block a join."""
    s = re.sub(r"^[a-z]{2} ", "", str(name).strip())
    return re.sub(r"\s+Province$", "", s).strip()


def _snu2_name(name: str) -> str:
    """Published SNU2 name, kept as published.

    The two decorations `_admin1` removes are removed to make SNU1 join Thembisa's South
    African provinces, and no such join exists at SNU2. Removing a trailing " Province" here
    would turn Sierra Leone's Eastern Province into "Eastern" and would leave Laos with
    "Vientiane" beside "Vientiane Capital", which are two different units.
    """
    return str(name).strip()


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


def national_quarters(raw_dir, codes: Iterable[str], wanted=None, start_year: int = 2000,
                      end_year: int = 2035) -> Optional[Dict[tuple, List[Optional[float]]]]:
    """Every row of this file added to the country, quarter by quarter, for the MER codes asked.

    Returns {(iso3, code, year): [q1, q2, q3, q4]}, with None for a quarter nothing reported, or
    None when the file is not on disk. Numerator rows only, every modality and every unit level
    included, since the two double-counting traps in the module docstring were both checked and
    neither applies to a sum over the whole country.

    pepfar_panorama calls this to test its own national totals. The partner file pepfar_panorama
    reads adds every partner without removing people two partners both report, and this file is
    deduplicated, so where the two disagree this file is the safer national figure.
    """
    raw_dir = Path(raw_dir)
    files = sorted(p for p in list(raw_dir.glob("*.zip")) + list(raw_dir.glob("*.txt"))
                   if FILE_HINT in p.name.lower()) if raw_dir.exists() else []
    if not files:
        return None
    codes = set(codes)
    years = [y for y in YEARS if start_year <= y <= end_year]
    qcols = [f"{y} Quarter {q} Results" for y in years for q in QUARTERS]
    iso_cache: Dict[tuple, Optional[str]] = {}
    total: Optional[pd.DataFrame] = None
    for path in files:
        for chunk in PEPFARSNUConnector._chunks(path):
            sub = chunk[chunk["Indicator"].isin(codes)
                        & chunk["Numerator/Denominator"].fillna("N").str.strip().str.upper().eq("N")]
            if sub.empty:
                continue
            keys = list(zip(sub["ISO3"].fillna(""), sub["Country"].fillna("")))
            for k in set(keys):
                if k not in iso_cache:
                    iso_cache[k] = to_iso3(k[0]) or to_iso3(k[1])
            sub = sub.assign(_iso3=[iso_cache[k] for k in keys]).dropna(subset=["_iso3"])
            if wanted:
                sub = sub[sub["_iso3"].isin(wanted)]
            vals = sub.reindex(columns=qcols).apply(
                lambda c: pd.to_numeric(c.astype(str).str.replace(",", "", regex=False),
                                        errors="coerce"))
            part = vals.groupby([sub["_iso3"], sub["Indicator"]]).sum(min_count=1)
            # adding two chunks keeps a quarter blank only where both chunks left it blank
            total = part if total is None else total.add(part, fill_value=0)
    out: Dict[tuple, List[Optional[float]]] = {}
    if total is None:
        return out
    for (iso3, code), row in total.iterrows():
        for y in years:
            q = [row[f"{y} Quarter {i} Results"] for i in QUARTERS]
            q = [None if pd.isna(v) else float(v) for v in q]
            if any(v is not None for v in q):
                out[(iso3, code, y)] = q
    return out


def _fold(name: str) -> str:
    """One spelling for comparing two files' names for the same place.

    Accents, case, punctuation and spacing all differ between PEPFAR's own files — the partner
    file writes Panama where the geographic file writes Panamá — and none of those differences
    mean two different places. Anything that survives folding is a real difference of name.
    """
    s = unicodedata.normalize("NFKD", str(name))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def emitted_units(raw_dir, wanted=None) -> Optional[Dict[str, dict]]:
    """The admin1 vocabulary this connector emits, so another connector can write into it.

    Returns {iso3: {"country", "level", "units", "lookup", "national_names"}}, or None when the
    geographic file is not on disk. `level` is "SNU1" or "SNU2", naming the level the country's
    units are read at, and is absent for a country this connector skips. `units` is the set of
    unit names emitted for that country. `lookup` is three dictionaries, one per level of the
    published hierarchy, each mapping a folded name to the unit this connector emits for it, so
    a file naming a district can find the province the district belongs to. `national_names`
    holds the folded spellings that mean the whole country, which must never resolve to a unit:
    Guatemala's priority sub-national unit named Guatemala is the national figure, and the
    department of Guatemala is a different thing with the same name.

    A name is looked up at one level, never at three in turn. Tanzania publishes a region called
    Kagera and, somewhere else in the country, a district called Kagera, so a search that falls
    through from one level to the next places a region in the wrong province.

    The unit set is a superset of what `fetch` emits, by the country-indicator-years `fetch`
    drops because a single unit carries the whole country in that cell. A caller wanting the
    exact set should compare against the rows themselves.
    """
    raw_dir = Path(raw_dir)
    files = sorted(p for p in list(raw_dir.glob("*.zip")) + list(raw_dir.glob("*.txt"))
                   if FILE_HINT in p.name.lower()) if raw_dir.exists() else []
    if not files:
        return None
    names: Dict[str, str] = {}
    units: Dict[str, set] = {}
    units2: Dict[str, set] = {}
    tree: Dict[str, set] = {}
    qcols = [f"{y} Quarter {q} Results" for y in YEARS for q in QUARTERS]
    iso_cache: Dict[tuple, Optional[str]] = {}
    for path in files:
        for chunk in PEPFARSNUConnector._chunks(path, hierarchy=True):
            sub = chunk[chunk["Indicator"].isin(MER)
                        & chunk["Numerator/Denominator"].fillna("N").str.strip().str.upper().eq("N")]
            if sub.empty:
                continue
            keys = list(zip(sub["ISO3"].fillna(""), sub["Country"].fillna("")))
            for k in set(keys):
                if k not in iso_cache:
                    iso_cache[k] = to_iso3(k[0]) or to_iso3(k[1])
            vals = sub.reindex(columns=qcols).apply(
                lambda c: pd.to_numeric(c.astype(str).str.replace(",", "", regex=False),
                                        errors="coerce"))
            carries = vals.notna().any(axis=1).tolist()
            s1s = sub["Sub-National Unit 1"].fillna("").str.strip().tolist()
            s2s = sub["Sub-National Unit 2"].fillna("").str.strip().tolist()
            s3s = (sub["Sub-National Unit 3"].fillna("").str.strip().tolist()
                   if "Sub-National Unit 3" in sub.columns else [""] * len(sub))
            countries = sub["Country"].fillna("").str.strip().tolist()
            for iso3, country, s1, s2, s3, has in zip(
                    (iso_cache[k] for k in keys), countries, s1s, s2s, s3s, carries):
                if not iso3 or not s1 or (wanted and iso3 not in wanted):
                    continue
                names[iso3] = country or iso3
                tree.setdefault(iso3, set()).add((s1, s2, s3))
                if not has:
                    continue
                units.setdefault(iso3, set()).add(s1)
                if (_admin1(s1).lower() == country.lower() and s2
                        and s2.lower() != _ABOVE_SNU2 and not s2.startswith("_")):
                    units2.setdefault(iso3, set()).add(_snu2_name(s2))

    national_only = {iso for iso, s in units.items()
                     if len(s) == 1 and _admin1(next(iter(s))).lower() == names.get(iso, "").lower()}
    read_at_snu2 = {iso for iso in national_only if len(units2.get(iso, ())) > 1}

    out: Dict[str, dict] = {}
    for iso3, triples in tree.items():
        level = ("SNU2" if iso3 in read_at_snu2
                 else None if iso3 in national_only else "SNU1")
        national = {_fold(names.get(iso3, iso3))}
        s1s = {s1 for s1, _, _ in triples}
        if len(s1s) == 1:
            national.add(_fold(next(iter(s1s))))
        entry = {"country": names.get(iso3, iso3), "units": set(), "national_names": national,
                 "lookup": [{}, {}, {}]}
        if level:
            entry["level"] = level
        out[iso3] = entry
        if not level:
            continue
        entry["units"] = ({_admin1(u) for u in units.get(iso3, ())} if level == "SNU1"
                          else set(units2.get(iso3, ())))
        clash = [set(), set(), set()]
        for s1, s2, s3 in triples:
            target = _admin1(s1) if level == "SNU1" else _snu2_name(s2)
            if not target or target not in entry["units"]:
                continue
            for i, name in ((0, s1), (0, _admin1(s1)), (1, s2), (2, s3)):
                if not name:
                    continue
                k = _fold(name)
                if k in entry["lookup"][i] and entry["lookup"][i][k] != target:
                    clash[i].add(k)
                entry["lookup"][i].setdefault(k, target)
        for i in range(3):
            for k in clash[i]:
                entry["lookup"][i].pop(k, None)
    return out


class PEPFARSNUConnector(BaseConnector):
    source_id = "pepfar_snu"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("PEPFAR MER at the province, county, state or department, read at sub-national "
                   "unit 1 in the 26 countries that publish real units there and at sub-national "
                   "unit 2 in the 29 whose only SNU1 is the country's own name. Six MER codes, "
                   "TX_CURR, TX_NEW, TX_PVLS, HTS_TST, HTS_TST_POS and PrEP_NEW. The admin1 layer "
                   "no aggregator publishes. Programme footprint, not provincial totals.")

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ---------------------------------------------------------------
    def _files(self) -> List[Path]:
        """The archives whose names carry FILE_HINT, and a count of everything else.

        A filter that returns quietly reports a clean run whether it matched everything or
        nothing, so the count of what FILE_HINT excluded is logged beside the count it kept.
        """
        if not self.raw_dir.exists():
            return []
        candidates = sorted(list(self.raw_dir.glob("*.zip")) + list(self.raw_dir.glob("*.txt")))
        kept = [p for p in candidates if FILE_HINT in p.name.lower()]
        if len(kept) < len(candidates):
            log.info("pepfar_snu: reading %d of %d archive(s) in %s, the ones named %r. "
                     "Not read: %s", len(kept), len(candidates), self.raw_dir, FILE_HINT,
                     [p.name for p in candidates if p not in kept])
        return kept

    @staticmethod
    def _chunks(path: Path, hierarchy: bool = False):
        # static so national_quarters can read the file without building a connector.
        # `hierarchy` adds the third level, which emitted_units needs to place a district and
        # fetch has no use for.
        cols = _COLS + ["Sub-National Unit 3"] if hierarchy else _COLS
        read = dict(sep="\t", dtype=str, chunksize=100_000, on_bad_lines="skip",
                    low_memory=False, usecols=lambda c: c in cols or c in _VALUE_COLS)
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as z:
                for member in [m for m in z.namelist() if m.lower().endswith((".txt", ".csv"))]:
                    with z.open(member) as fh:
                        yield from pd.read_csv(fh, **read)
        else:
            yield from pd.read_csv(path, **read)

    def _accumulate(self, chunk: pd.DataFrame, agg: Dict[tuple, List[Optional[float]]],
                    agg2: Dict[tuple, List[Optional[float]]], names: Dict[str, str],
                    units: Dict[str, set], units2: Dict[str, set],
                    carried: Dict[str, Dict[str, float]], wanted,
                    start_year: int, end_year: int) -> None:
        """Add a chunk to the SNU1 aggregate, and to the SNU2 aggregate where SNU1 is a country.

        `agg` holds every country at SNU1 and `agg2` holds one level down, built only from the
        rows whose SNU1 is the country's own name, since those are the only rows where SNU1
        carries no sub-national information. `carried` records, per country, how much of the
        six codes' numerator total sits on a named SNU2 unit and how much sits on a label that
        is not a place, so the log can report what reading SNU2 leaves behind.
        """
        sub = chunk[chunk["Indicator"].isin(MER)]
        if sub.empty:
            return
        for _, r in sub.iterrows():
            iso3 = to_iso3(r.get("ISO3") or "") or to_iso3(r.get("Country") or "")
            if not iso3 or (wanted and iso3 not in wanted):
                continue
            raw_snu = str(r.get("Sub-National Unit 1") or "").strip()
            if not raw_snu:
                continue
            country = str(r.get("Country") or "").strip()
            nd = str(r.get("Numerator/Denominator") or "N").strip().upper()
            if nd not in ("N", "D"):
                continue
            ind = r["Indicator"]
            if nd == "D" and ind not in PCT_FROM:
                continue
            names[iso3] = country or iso3
            units.setdefault(iso3, set()).add(raw_snu)
            admin1 = _admin1(raw_snu)

            # Where SNU1 is the country's own name, the sub-national unit the row belongs to is
            # named at SNU2. Three SNU2 labels are not a place and are not read as one: a blank,
            # `Data above SNU2` (the part of the country's total the country attributed to no
            # unit) and a name beginning with an underscore (PEPFAR's own aggregate stand-in,
            # `_Peru Aggregated PSNU`).
            raw2 = str(r.get("Sub-National Unit 2") or "").strip()
            if admin1.lower() != country.lower():
                level2 = None
            elif not raw2:
                level2 = "blank"
            elif raw2.lower() == _ABOVE_SNU2:
                level2 = "above"
            elif raw2.startswith("_"):
                level2 = "aggregate"
            else:
                level2 = "unit"

            for y in YEARS:
                if y < start_year or y > end_year:
                    continue
                vals = [_num(r.get(f"{y} Quarter {q} Results")) for q in QUARTERS]
                if all(v is None for v in vals):
                    continue
                key = (iso3, admin1, ind, nd, y)
                cur = agg.setdefault(key, [None, None, None, None])
                for i, v in enumerate(vals):
                    if v is not None:
                        cur[i] = (cur[i] or 0.0) + v
                if level2 is None:
                    continue
                if nd == "N":
                    book = carried.setdefault(iso3, {})
                    book[level2] = book.get(level2, 0.0) + sum(v for v in vals if v is not None)
                if level2 != "unit":
                    continue
                name2 = _snu2_name(raw2)
                key2 = (iso3, name2, ind, nd, y)
                cur2 = agg2.setdefault(key2, [None, None, None, None])
                for i, v in enumerate(vals):
                    if v is not None:
                        cur2[i] = (cur2[i] or 0.0) + v
                if nd == "N":
                    units2.setdefault(iso3, set()).add(name2)

    # -- emitting --------------------------------------------------------------
    @staticmethod
    def _snapshot(vals: List[Optional[float]]) -> Tuple[Optional[float], Optional[int]]:
        """Latest reported quarter, and which quarter it was."""
        reported = [i for i, v in enumerate(vals) if v is not None]
        if not reported:
            return None, None
        last = reported[-1]
        return vals[last], last + 1

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
            log.warning("pepfar_snu: no Enhanced Geographical Analysis file in %s — download it "
                        "from https://data.pepfar.gov/datasets", self.raw_dir)
            return

        agg: Dict[tuple, List[Optional[float]]] = {}
        agg2: Dict[tuple, List[Optional[float]]] = {}
        names: Dict[str, str] = {}
        units: Dict[str, set] = {}
        units2: Dict[str, set] = {}
        carried: Dict[str, Dict[str, float]] = {}
        for path in files:
            try:
                for chunk in self._chunks(path):
                    self._accumulate(chunk, agg, agg2, names, units, units2, carried,
                                     wanted, start_year, end_year)
            except Exception as exc:
                log.warning("pepfar_snu: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_snu: read %s", path.name)

        # How many quarters make a whole year, asked of the release rather than fixed at four.
        # PrEP_NEW is read here and published at Q2 and Q4 through FY2020, so counting to four
        # would put a partial-year warning on every province in a year that is complete. Same
        # helper as pepfar_panorama, so the national and provincial connectors cannot disagree
        # about which years are short.
        #
        # The vote is taken here, before any country moves from SNU1 to SNU2, so that regrouping
        # a country's rows under its SNU2 units cannot change which quarters an indicator-year is
        # held to publish at, and so cannot move a partial-year flag on a province of one of the
        # countries that already had provinces.
        cadence = _panorama.release_cadence(
            {k: v for k, v in agg.items() if k[3] == "N"}, lambda k: (k[2], k[4]))
        latest_year = max((y for _, y in cadence), default=0)

        # A country publishing exactly one "sub-national unit" that is its own name is
        # publishing a national total. Finding those here (and not by a hardcoded country
        # list) means a country that gains real SNU detail later starts appearing on its own.
        national_only = {iso for iso, s in units.items()
                         if len(s) == 1 and _admin1(next(iter(s))).lower() == names.get(iso, "").lower()}

        # THE SECOND LEVEL. In a country whose only SNU1 is its own name, the sub-national units
        # are named at SNU2, and reading them there is the difference between the country having
        # no admin1 rows at all and having its provinces. A country is read at SNU2 when two or
        # more of its SNU2 units carry a value, since a country whose whole programme sits on one
        # unit is publishing a national total again under a smaller label. The same test is
        # applied a second time per indicator-year, because a country can name several units on
        # one indicator and only one on another.
        agg2 = {k: v for k, v in agg2.items() if k[0] in national_only}
        by_cell: Dict[tuple, set] = {}
        for (iso3, unit, ind, nd, year) in agg2:
            if nd == "N":
                by_cell.setdefault((iso3, ind, year), set()).add(unit)
        read_at_snu2 = {iso for iso, s in units2.items()
                        if iso in national_only and len(s) > 1}
        solo_cells = {k for k, s in by_cell.items() if len(s) == 1 and k[0] in read_at_snu2}
        at_snu2: set = set()
        for key in [k for k in agg if k[0] in read_at_snu2]:
            del agg[key]
        for key, vals in agg2.items():
            iso3, unit, ind, nd, year = key
            if iso3 not in read_at_snu2 or (iso3, ind, year) in solo_cells:
                continue
            agg[key] = vals
            at_snu2.add((iso3, unit))
        skipped = national_only - read_at_snu2

        if read_at_snu2:
            log.info("pepfar_snu: %d countries publish only a country-wide 'SNU1' and are read one "
                     "level down at SNU2, where they name %d units carrying a value: %s",
                     len(read_at_snu2), len(at_snu2), ", ".join(sorted(read_at_snu2)))
            if solo_cells:
                log.info("pepfar_snu: %d country-indicator-years inside those countries name a "
                         "single SNU2 unit and are dropped, since one unit carrying the whole "
                         "country is a national total under a smaller label", len(solo_cells))
            for iso3 in sorted(read_at_snu2):
                book = carried.get(iso3, {})
                total = sum(book.values())
                loose = total - book.get("unit", 0.0)
                if total and loose / total > 0.01:
                    log.info("pepfar_snu: %s — %.1f%% of the programme total sits on a label that "
                             "is not a place (blank SNU2, 'Data above SNU2' or an aggregate name "
                             "beginning with an underscore) and is not emitted", iso3,
                             100.0 * loose / total)
        if skipped:
            log.info("pepfar_snu: %d countries publish only a country-wide 'SNU' and no usable "
                     "second level, and are skipped (they would duplicate pepfar_panorama under a "
                     "fake admin1): %s", len(skipped), ", ".join(sorted(skipped)))
            for iso3 in sorted(skipped):
                book = carried.get(iso3, {})
                total = sum(book.values())
                log.info("pepfar_snu: %s skipped, %d SNU2 unit(s) carry a value (%s) and %.1f%% of "
                         "its programme total sits on PEPFAR's own aggregate stand-in", iso3,
                         len(units2.get(iso3, ())), ", ".join(sorted(units2.get(iso3, ()))) or "none",
                         100.0 * book.get("aggregate", 0.0) / total if total else 0.0)

        # ONE QUARTER PER COUNTRY-YEAR, for the snapshot indicators.
        #
        # Reading each unit at its own latest reported quarter looks harmless and is not: the
        # provinces then sit at different dates and no longer add up to anything. Nigeria's
        # FY2024 TX_CURR is the case that showed it — 33 states reached Q4 and two stopped at
        # Q3, and summing each at its own last quarter gave 1,577,095 against a national
        # 1,537,786, a 39,309 surplus belonging to no point in time. So the quarter is chosen
        # per country-indicator-year (the latest any of its units reports) and every unit is
        # read at that quarter. A unit with nothing there is left out of that year and not
        # carried forward at a stale value, and the count of those is logged: a province that
        # stops reporting is a finding, and it should look like an absence, not like a
        # province still being served.
        common_q: Dict[tuple, int] = {}
        for (iso3, admin1, ind, nd, year), vals in agg.items():
            if nd != "N" or iso3 in skipped or not MER[ind][1]:
                continue
            _, q = self._snapshot(vals)
            if q:
                k = (iso3, ind, year)
                common_q[k] = max(common_q.get(k, 0), q)

        n = 0
        emitted_units: set = set()
        off_quarter: Dict[tuple, int] = {}
        for (iso3, admin1, ind, nd, year), vals in sorted(agg.items()):
            if nd != "N" or iso3 in skipped:
                continue
            canonical, is_snapshot = MER[ind]
            level = "SNU2" if (iso3, admin1) in at_snu2 else "SNU1"
            nq = len([v for v in vals if v is not None])
            extra = {"note": f"PEPFAR MER at {level} — PROGRAMME FOOTPRINT, not a provincial "
                             "total; provinces do not sum to the national figure",
                     "mer_indicator": ind,
                     "unit_level": level,
                     "quarters_reported": nq}

            if is_snapshot:
                q_now = common_q.get((iso3, ind, year))
                value = vals[q_now - 1] if q_now else None
                if value is None:
                    own = self._snapshot(vals)[1]
                    if own:
                        # reported this year, but not in the quarter its country was read at
                        off_quarter[(iso3, ind, year)] = off_quarter.get((iso3, ind, year), 0) + 1
                    continue
                extra["snapshot_quarter"] = q_now
                q_prev = common_q.get((iso3, ind, year - 1))
                if q_now and q_prev and q_now != q_prev:
                    extra["snapshot_quarter_mismatch"] = (
                        f"snapshot taken from Q{q_now} of FY{year} but Q{q_prev} of FY{year - 1} — "
                        f"these are not twelve months apart, and the change between them is not "
                        f"an annual change.")
            else:
                nn = [v for v in vals if v is not None]
                value = sum(nn) if nn else None
                # Same trap as the national connector, and it bites harder here: a province
                # whose partner stopped reporting looks like a province whose programme stopped.
                here = cadence.get((ind, year), [])
                prev_cad = cadence.get((ind, year - 1)) or here
                truncated, same_span = _panorama.span_status(
                    here, prev_cad, year, latest_year)
                extra["release_quarters"] = [f"Q{q}" for q in here]
                extra.update(_panorama.quarter_detail(
                    vals, agg.get((iso3, admin1, ind, nd, year - 1)), year, same_span))
                if value is not None and (truncated or 0 < nq < len(here)):
                    why = (f"FY{year} is part-published, carrying "
                           f"{', '.join('Q%d' % q for q in here)} where FY{year - 1} carries "
                           f"{', '.join('Q%d' % q for q in prev_cad)}" if truncated else
                           f"this province reported {nq} of the "
                           f"{', '.join('Q%d' % q for q in here)} that FY{year} publishes")
                    extra["partial_year"] = (
                        f"{why}. This annual total is a PARTIAL sum and must NOT be compared "
                        f"with full years or read as a decline.")
            if value is None:
                continue

            yield self.make_row(
                country_iso3=iso3, country_name=names.get(iso3, ""), admin1=admin1,
                indicator_id=canonical, year=year, value=value, unit="count",
                source_url="https://data.pepfar.gov/datasets",
                source_indicator_code=f"MER.{ind}", extra=extra,
            )
            n += 1
            emitted_units.add((iso3, admin1))

            # the third 95 at province level, from the same quarter on both sides
            pct_canonical = PCT_FROM.get(ind)
            if not pct_canonical:
                continue
            den = agg.get((iso3, admin1, ind, "D", year))
            if not den:
                continue
            # numerator and denominator read at the same quarter as the count above, so the
            # rate belongs to the same date as everything else in that country-year
            i = extra["snapshot_quarter"] - 1
            if vals[i] is None or not den[i]:
                continue
            pct = 100.0 * vals[i] / den[i]
            pct_extra = {"note": "PEPFAR TX_PVLS: virally suppressed / on ART with a VL result in "
                                 "the last 12 months, among the PEPFAR-supported cohort only",
                         "mer_indicator": ind, "unit_level": level, "snapshot_quarter": i + 1,
                         "numerator": vals[i], "denominator": den[i]}
            if pct > 100.0:
                # The numerator is not a strict subset of the denominator at this level. A
                # suppressed result can arrive for someone the quarter's denominator cohort does
                # not hold — a transfer in, or a late viral load credited to a facility that no
                # longer counts the patient as on ART. Published as it stands and flagged, since
                # clipping it to 100 would hide the reporting problem it is evidence of.
                pct_extra["data_quality_flag"] = (
                    f"ratio above 100% ({pct:.1f}%): {vals[i]:,.0f} suppressed against a "
                    f"denominator of {den[i]:,.0f} — numerator and denominator are not drawn "
                    f"from the same cohort in this unit-year")
                log.info("pepfar_snu: %s %s %s FY%d — viral suppression %.1f%% (%s/%s); kept and "
                         "flagged, not clipped", iso3, admin1, ind, year, pct,
                         f"{vals[i]:,.0f}", f"{den[i]:,.0f}")
            yield self.make_row(
                country_iso3=iso3, country_name=names.get(iso3, ""), admin1=admin1,
                indicator_id=pct_canonical, year=year, value=pct,
                unit="percent", source_url="https://data.pepfar.gov/datasets",
                source_indicator_code=f"MER.{ind}.N_over_D",
                extra=pct_extra,
            )
            n += 1
        for (iso3, ind, year), k in sorted(off_quarter.items()):
            log.info("pepfar_snu: %s %s FY%d — %d unit(s) reported this year but not in Q%d, the "
                     "quarter the country is read at; they are absent from that year and not "
                     "carried forward", iso3, ind, year, k, common_q.get((iso3, ind, year), 0))
        log.info("pepfar_snu: emitted %d rows over %d sub-national units in %d countries, of which "
                 "%d units in %d countries are read at SNU2",
                 n, len(emitted_units), len({i for i, _ in emitted_units}),
                 len(emitted_units & at_snu2), len({i for i, _ in emitted_units & at_snu2}))
