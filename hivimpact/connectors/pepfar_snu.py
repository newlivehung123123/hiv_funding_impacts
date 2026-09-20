"""
PEPFAR sub-national (SNU) connector — the admin1 layer no aggregator publishes.

UNAIDS, WHO and the World Bank all stop at the country. PEPFAR's Enhanced Geographical
Analysis file goes three levels below it, quarterly, from 2016 to 2025, which is the only
place in this pipeline where a funding cut can be watched land unevenly INSIDE a country.
That matters because a national total can hold steady while whole provinces lose their
implementing partner.

Access: download `Enhanced_Geographical_Analysis.zip` from https://data.pepfar.gov/datasets
and drop the ZIP into `data/raw/pepfar/` (no need to unzip — the `.txt` inside is read
directly). 157 MB unzipped, 624,800 rows, 59 countries, read in chunks.

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
   over it. It is not a total: the blank modality is how 2016 and 2017 were reported
   (75.3m and 84.2m tests, with the named modalities at zero), and named modalities are
   how 2018 onward is reported (with the blank at zero). Across ten years the two never
   both carry a value in the same unit-year, except 49 units in FY2025 totalling 24,782
   against 19.6m — 0.13%, an unspecified residual and not a total. Summing over modality
   is therefore correct.

2. **Ragged depth.** Some SNU2 groups hold both an SNU3-named row and an SNU3-blank row,
   which would be a total-plus-parts pair if the blank one carried the group's sum. It
   does not: over all ten years, zero SNU2 groups have a value on both sides. Countries
   simply publish two levels or three. Summing every row up to SNU1 is therefore correct.

NATIONAL TOTALS IN DISGUISE: 35 of the 61 countries publish a single "sub-national unit"
that is the country itself — SNU1 "Thailand" for Thailand, "Burma" for Burma. Those are
national figures wearing a province's label, and emitting them would duplicate
`pepfar_panorama` under a fake admin1. A country whose only SNU1 is its own name is
dropped, which leaves 26 countries with real sub-national detail (Kenya 47 counties,
Nigeria 37 states, Vietnam 35 provinces, Cote d'Ivoire 34, Tanzania 32, Ukraine 27 ...).

Correction of 2026-09-20. The count of 2026-08-04 was 33 of 59 because Bahamas and Belize
carry no ISO3 code in this file, and a count grouped on the ISO3 column leaves both out. This
connector resolves a country from the Country column when ISO3 is blank, and the connector's
own log names 35 countries skipped.

Correction of 2026-09-19, recounted 2026-09-20. Most of the 35 skipped countries publish real
provinces one level down. In all 35, every row carrying a value names a Sub-National Unit 2.
Leaving aside the "Data above SNU2" rows and the units whose names begin with an underscore, 31
of the 35 countries name two or more SNU2 units carrying a value on some indicator, 239 units
in all, and the SNU2 names are provinces, departments, states or districts (Thailand 17
provinces, Cambodia six provinces, Myanmar 15 states and regions, Guatemala 19 departments,
Belize three districts). Peru's only SNU2 unit is `_Peru Aggregated PSNU`, Colombia's are
`_Colombia Aggregated PSNU` and Antioquia, Barbados's is Saint Michael Parish and Bahamas's is
New Providence Island, so Peru, Colombia, Barbados and Bahamas have no provincial split to
read. The first count of 2026-09-19 gave 238 units over 30 countries, because the first count
took SNU2 names from every row and so included Roraima in Brazil and Nickerie District in
Suriname, which carry no value. This connector reads SNU1 only and so emits nothing for the 31
countries yet, six of the nine Southeast Asian countries among them. Reading SNU2 where SNU1
is the country is a change awaiting Jason's decision, recorded in docs/ACCESS_LADDER.md
section 9w.

ADMIN1 NAMES: published names are kept as they are, with two exceptions that exist to
make the panel joinable — a leading province code ("ec Eastern Cape Province") and a
trailing " Province" are removed. That touches 19 names in two countries (ZAF, ZMB),
collides nothing, and makes PEPFAR's nine South African provinces match the nine
Thembisa already contributes, so the programme footprint and the modelled provincial
total can be read against each other for the first time.

TAGGING: PEPFAR MER measures the PEPFAR programme footprint, NOT provincial totals, and
provinces do not sum to the national total. source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import re
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
}
# TX_PVLS publishes a denominator too (people on ART with a viral-load result in the last
# 12 months), so the third 95 can be computed at province level instead of inferred.
PCT_FROM = {"TX_PVLS": "viral_suppression_pct"}

YEARS = range(2016, 2026)
QUARTERS = (1, 2, 3, 4)

_COLS = ["Country", "ISO3", "Indicator", "Numerator/Denominator", "Modality",
         "Sub-National Unit 1"]
_VALUE_COLS = [f"{y} Quarter {q} Results" for y in YEARS for q in QUARTERS]


def _admin1(name: str) -> str:
    """Published SNU1 name, minus the two decorations that block a join."""
    s = re.sub(r"^[a-z]{2} ", "", str(name).strip())
    return re.sub(r"\s+Province$", "", s).strip()


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


class PEPFARSNUConnector(BaseConnector):
    source_id = "pepfar_snu"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("PEPFAR MER at sub-national unit 1 (province/county/state) — the admin1 layer "
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
    def _chunks(path: Path):
        # static so national_quarters can read the file without building a connector
        read = dict(sep="\t", dtype=str, chunksize=100_000, on_bad_lines="skip",
                    low_memory=False, usecols=lambda c: c in _COLS or c in _VALUE_COLS)
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as z:
                for member in [m for m in z.namelist() if m.lower().endswith((".txt", ".csv"))]:
                    with z.open(member) as fh:
                        yield from pd.read_csv(fh, **read)
        else:
            yield from pd.read_csv(path, **read)

    def _accumulate(self, chunk: pd.DataFrame, agg: Dict[tuple, List[Optional[float]]],
                    names: Dict[str, str], units: Dict[str, set], wanted,
                    start_year: int, end_year: int) -> None:
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
        names: Dict[str, str] = {}
        units: Dict[str, set] = {}
        for path in files:
            try:
                for chunk in self._chunks(path):
                    self._accumulate(chunk, agg, names, units, wanted, start_year, end_year)
            except Exception as exc:
                log.warning("pepfar_snu: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_snu: read %s", path.name)

        # A country publishing exactly one "sub-national unit" that is its own name is
        # publishing a national total. Dropping it here (and not by a hardcoded country
        # list) means a country that gains real SNU detail later starts appearing on its own.
        national_only = {iso for iso, s in units.items()
                         if len(s) == 1 and _admin1(next(iter(s))).lower() == names.get(iso, "").lower()}
        if national_only:
            log.info("pepfar_snu: %d countries publish only a country-wide 'SNU' and are skipped "
                     "(they would duplicate pepfar_panorama under a fake admin1): %s",
                     len(national_only), ", ".join(sorted(national_only)))

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
            if nd != "N" or iso3 in national_only or not MER[ind][1]:
                continue
            _, q = self._snapshot(vals)
            if q:
                k = (iso3, ind, year)
                common_q[k] = max(common_q.get(k, 0), q)

        # How many quarters make a whole year, asked of the release rather than fixed at four.
        # PrEP_NEW is read here and published at Q2 and Q4 through FY2020, so counting to four
        # would put a partial-year warning on every province in a year that is complete. Same
        # helper as pepfar_panorama, so the national and provincial connectors cannot disagree
        # about which years are short.
        cadence = _panorama.release_cadence(
            {k: v for k, v in agg.items() if k[3] == "N"}, lambda k: (k[2], k[4]))
        latest_year = max((y for _, y in cadence), default=0)

        n = 0
        emitted_units: set = set()
        off_quarter: Dict[tuple, int] = {}
        for (iso3, admin1, ind, nd, year), vals in sorted(agg.items()):
            if nd != "N" or iso3 in national_only:
                continue
            canonical, is_snapshot = MER[ind]
            nq = len([v for v in vals if v is not None])
            extra = {"note": "PEPFAR MER at SNU1 — PROGRAMME FOOTPRINT, not a provincial total; "
                             "provinces do not sum to the national figure",
                     "mer_indicator": ind,
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
                         "mer_indicator": ind, "snapshot_quarter": i + 1,
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
        log.info("pepfar_snu: emitted %d rows over %d sub-national units in %d countries",
                 n, len(emitted_units), len({i for i, _ in emitted_units}))
