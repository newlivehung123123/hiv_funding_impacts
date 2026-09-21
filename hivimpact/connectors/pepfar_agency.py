"""
PEPFAR MER split by the US agency that funded the service — the funding-cut signal itself.

This reads the same file `pepfar_panorama` reads, `Public_Partner_MER_TopLine`, and keeps the
column that one sums away. Every MER row already names its `Funding Agency` and its
`Partner Name`; the country total is those partners added together. That total is the wrong
place to look for the event this project is about, because the agencies were not cut alike.
USAID was dismantled over 2025 and HHS/CDC was not, so a country whose CDC-funded cohort grows
while its USAID-funded cohort shrinks shows a flat total and no visible harm.

Kenya is the case. On ART, FY2024 -> FY2025:

    USAID       472,520 ->   413,032   (-12.6%)
    HHS/CDC     797,595 ->   844,340   (+5.9%)
    other        66,185 ->    67,080   (+1.4%)
    total     1,336,300 -> 1,324,452   (-0.9%)

The same shape appears in Zambia (USAID -14.7%, CDC +4.8%, total -3.9%). A reader of the country
total sees a programme holding steady. A reader of the split sees roughly sixty thousand people
in Kenya alone leaving the arm that lost its funder.

WHY THIS IS A USABLE COMPARISON, AND WHERE IT STOPS BEING ONE

The two agencies work in the same country, in the same year, under the same epidemic, the same
reporting calendar and the same definition of TX_CURR. CDC is therefore a control for almost
everything except the cut. What it is not a control for is transfer: a patient moved from a
USAID-funded clinic to a CDC-funded one leaves the first series and joins the second, which
looks exactly like the harm we are trying to measure and is not harm at all. When both series
move in opposite directions by similar magnitudes, transfer has to be excluded before loss is
claimed. Kenya's numbers do not net out — USAID falls 59,488 while CDC rises 46,745 — but that
is an argument for looking, not a finding on its own. Every row carries
`extra.interpretation` saying so.

THE QUARTER TRAP, AND WHY FY2025 SURVIVES IT

TX_CURR is a snapshot: its annual value is the latest quarter reported, not a sum. FY2025
publishes one quarter of four, so the obvious worry is that a partial year puts the FY2025
snapshot at a different point in the year from FY2024's and manufactures the decline. It does
not: the quarter FY2025 reports is **Q4**, the same quarter FY2024's snapshot comes from, so the
comparison is twelve months apart and like for like. That is a fact about this particular
download and not a property of the format, so this connector records the quarter each snapshot
was taken from in `extra.snapshot_quarter` and warns when consecutive years are read off
different quarters. A future refresh that publishes FY2026 Q1 must not be compared with FY2025
Q4 in silence.

HTS_TST_POS is cumulative and takes the existing partial-year treatment: a part-reported year
is a partial sum and is flagged, never presented as a decline.

ONE QUARTER FOR THE WHOLE COUNTRY (fixed 2026-08-04)

"Latest reported quarter" has to mean one quarter per country-year. Reading every partner at
its own last quarter and adding those together counts a transferred cohort twice: Zimbabwe
FY2024 came out 44% above its Q4 figure because a mechanism moved from UNIVERSITY OF
WASHINGTON (Q1 only, 539,106 on ART) to Zim - TTECH (Q2-Q4) and both were counted. So the
quarter is chosen once per country-indicator-year — the latest quarter ANY agency's partners
report — and all three agency series are read at that same quarter. Choosing it per agency
would have been the natural-looking thing to do and would have quietly broken the partition
below, by putting USAID at Q3 and CDC at Q4 of the same year.

An agency with nothing at that quarter is left out of that year and not carried forward at a
stale value, and the omission is logged. A funder that stops reporting is the event this
connector exists to see; it should look like an absence, not like a programme still running.

GRAIN AND DOUBLE COUNTING

The three agency series for a country-year are a partition of the country total, so they add
back to `on_art_count` / `new_diagnoses` as emitted by `pepfar_panorama` — the two connectors
read the same rows of the same file and now pick the same quarter, so the partition is exact.
They are a second view of the same numbers, not more numbers. Anything summing the panel must
take one level or the other.

TOPLINE IS SHORT IN FOUR YEARS

Every run compares the TopLine values with PEPFAR's Partner_Performance file, which adds the
same partners together and should therefore agree with TopLine cell for cell. The two files
differ only in FY2018, FY2019, FY2021 and FY2022, and TopLine is the lower figure in every cell
where the two files differ (docs/ACCESS_LADDER.md section 9w). Kenya's USAID-funded treatment
cohort in FY2018 is 355,447 here and 405,420 in Partner_Performance, a shortfall of 49,973. No
value from FY2023 on is affected, so the Kenya comparison above stands as printed.

The values are kept as TopLine publishes them, because the ladder's rule is that a value is never
replaced by another file's figure. A row that differs from Partner_Performance by more than 0.5
carries the Partner_Performance figure beside its own in `extra.partner_file_differs`, and on the
download of 2026-07-18 that flags 26 rows. Where TopLine has no row for an agency that
Partner_Performance reports, the other agencies' rows for the same country, indicator and year
carry `agency_missing_from_topline`, which covers 43 country-indicator-years and 47 rows.
Guatemala in FY2018 is one of the 43. TopLine holds no USAID treatment row there, so a sum of the
agency rows for Guatemala in FY2018 is short by the whole USAID cohort. Five
country-indicator-years have no TopLine row for any agency, Barbados, Suriname and Trinidad and
Tobago on TX_CURR in FY2018 and El Salvador on TX_CURR and TX_NEW in FY2019. No row exists to
carry a flag for those five, so every run logs them by name.

TARGETS

Partner_Performance also carries the target PEPFAR set for each agency, country, indicator and
year in the country operational plan, which is agreed before the fiscal year begins. A target is
never emitted as a value. A row whose agency held a target carries the target in
`extra.fy_target`, 2,030 of the 2,077 rows, and where the result covers the whole year the row
also carries `result_to_target`, 1,813 rows. For TX_CURR a whole year means the Q4 snapshot and
for a flow a year with every quarter the release publishes.

Kenya's FY2025 cohort shows what the targets add. USAID reached 413,032 against a target of
471,741, a ratio of 0.876, while CDC reached 844,340 against 825,326, a ratio of 1.023. Summed
over the TX_CURR rows that carry both, USAID's ratio runs between 0.81 and 0.94 in FY2021 to
FY2024 and falls to 0.65 in FY2025, while CDC's ratio runs between 0.99 and 1.03 and rises to
1.17. USAID's FY2025 target on those rows, 8,179,443, is 7% below USAID's FY2024 target, while
USAID's FY2025 result, 5,328,202, is 28% below USAID's FY2024 result. So the FY2025 fall was not
in the plan, and CDC's result above CDC's own target in the same year is what patients moving
from USAID-funded to CDC-funded care would produce. The targets do not prove a transfer, and the
test the section above sets for transfer still applies.

Where an agency held a target for a country, indicator and year and reported nothing in either
partner file, the other agencies' rows carry `agency_held_target_without_result`. In FY2025 that
covers USAID in India, with a treatment target of 195,559, in Namibia with 6,274 and in Colombia
with 2,465, so USAID's national FY2025 treatment target across every country is 8,383,741 and
not the 8,179,443 the rows carry.

TAGGING: PEPFAR MER measures the PEPFAR programme footprint, not national totals.
source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

import pandas as pd

from . import pepfar_panorama as _panorama
from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

# the MER indicators worth splitting: the treatment cohort, the testing yield and the count of
# people newly started on treatment. TX_NEW was added on 2026-09-05 after the coverage audit
# found the code sitting unread in the file this connector already opens. Splitting TX_NEW by
# agency is the reason the split exists at all. The treatment cohort is slow, because people
# already on ART keep collecting refills for months after the money stops, so on_art_count
# moves late. Enrolment stops the week the clinic stops testing, so art_initiations_usaid
# against art_initiations_cdc is the sharpest form of the within-country comparison.
MER_INDICATORS = {"TX_CURR": "on_art_count", "HTS_TST_POS": "new_diagnoses",
                  "TX_NEW": "art_initiations"}
SNAPSHOT = {"TX_CURR"}  # annual = latest reported quarter, never a sum
SNAPSHOT_CANON = {MER_INDICATORS[k] for k in SNAPSHOT}

# Why this connector splits three indicators and not seventy-one.
#
# Every indicator added here becomes three series, one per agency, and each of the three needs
# its own entry in the canonical registry, so the split is not a dictionary entry the way a
# country-level mapping is. The three chosen are the ones where the USAID and CDC contrast
# answers the question the project asks. A cut stops enrolment first, which is art_initiations,
# and stops testing with it, which is new_diagnoses, while on_art_count moves late because people
# already on treatment keep collecting refills for months. Splitting an indicator that a cut does
# not move would add rows and no evidence.
#
# The strongest candidate for a fourth is TX_PVLS, viral suppression, which pepfar_panorama now
# reads at country level. Suppression is the outcome the cascade exists to produce, so a USAID
# arm losing suppression while the CDC arm holds would be the clearest harm this panel could
# show. Adding it needs three canonical definitions written first, so it is left as a decision
# rather than taken here.
#
# Everything else the TopLine file contains is declared where pepfar_panorama declares it. The
# list is imported rather than copied, so a code appearing in a future download is unaccounted
# for in one place instead of two.
DECLARED_UNMAPPED: Dict[str, str] = dict(_panorama.DECLARED_UNMAPPED)
DECLARED_UNMAPPED.update({
    code: f"read at country level by pepfar_panorama as {canon}; the agency split is confined to "
          f"the three indicators a funding cut moves first"
    for code, canon in _panorama.MER_INDICATORS.items() if code not in MER_INDICATORS
})

# PEPFAR's agency labels -> the suffix the canonical id carries. Everything not named here
# (DOD, HHS/HRSA, State/PRM, State/AF, Peace Corps, Default) is pooled into "other_agency",
# so the three series still add back to the country total.
AGENCY_SUFFIX = {"USAID": "usaid", "HHS/CDC": "cdc"}
OTHER = "other_agency"

# said on every row, because the divergence is evidence and not yet a conclusion
INTERPRETATION = (
    "Agency share of the PEPFAR programme, not a national total. CDC acts as a within-country "
    "control for USAID: same year, same epidemic, same indicator definition. It does not "
    "control for patients transferring between an agency's partners, which moves both series "
    "at once and imitates loss. Check whether the two series net out before reading a fall as "
    "people leaving care."
)


def _ci(cols: List[str], *names: str) -> Optional[str]:
    low = {c.lower().strip(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    return None


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


def _suffix(agency: str) -> str:
    return AGENCY_SUFFIX.get(str(agency).strip().upper(), OTHER)


def _last_q(vals: List[Optional[float]]) -> Optional[int]:
    """The latest quarter (1-4) that carries a number, or None if the year is empty."""
    reported = [i for i, v in enumerate(vals) if v is not None]
    return reported[-1] + 1 if reported else None


def _unit_id(row, pn_c: Optional[str], mc_c: Optional[str]):
    """(id, partner name) of the thing that reported this row — the MECHANISM.

    One row is one mechanism, and 530 partner names in this download run more than one of them
    inside a single country-indicator-year. Keying the detail by partner name would merge
    units that report different quarters, which is how a handover hides.
    """
    pname = str(row[pn_c]).strip() if pn_c else ""
    if pname.lower() in ("nan", "none"):
        pname = ""
    code = str(row[mc_c]).strip() if mc_c else ""
    if code.lower() in ("nan", "none"):
        code = ""
    if not code and not pname:
        return None, None
    return (code or pname), (pname or code)


class PEPFARAgencyConnector(BaseConnector):
    source_id = "pepfar_agency"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "PEPFAR MER split by funding agency (USAID vs CDC) — the funding-cut contrast."

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _process(
        self,
        chunk: pd.DataFrame,
        agg: Dict[tuple, List[Optional[float]]],
        names: Dict[str, str],
        partners: Dict[tuple, Dict[str, List[Optional[float]]]],
        wanted,
        start_year: int,
        end_year: int,
        seen: Optional[Counter] = None,
    ) -> bool:
        cols = list(chunk.columns)
        ind_c = _ci(cols, "indicator")
        fy_c = _ci(cols, "fiscal year")
        nd_c = _ci(cols, "numerator/denominator")
        dis_c = _ci(cols, "standardized disaggregate")
        iso_c = _ci(cols, "iso3") or _ci(cols, "country")
        ag_c = _ci(cols, "funding agency")
        pn_c = _ci(cols, "partner name")
        mc_c = _ci(cols, "mechanism code")
        q_cs = [_ci(cols, f"quarter {i}") for i in (1, 2, 3, 4)]
        # the agency column is the whole point — a MER file without it is not this connector's
        if not (ind_c and fy_c and dis_c and iso_c and ag_c and all(q_cs)):
            return False

        # counted before the dictionary narrows anything, so this connector can report the codes
        # it does not read as well as the codes it does
        if seen is not None:
            seen.update(chunk[ind_c].dropna().astype(str))

        sub = chunk[chunk[ind_c].isin(MER_INDICATORS.keys())]
        sub = sub[sub[dis_c].astype(str).str.contains("Total Numerator", case=False, na=False)]
        if nd_c:
            sub = sub[sub[nd_c].astype(str).str.upper().eq("N")]

        for _, r in sub.iterrows():
            iso3 = to_iso3(r[iso_c])
            if not iso3 or (wanted and iso3 not in wanted):
                continue
            try:
                year = int(str(r[fy_c])[:4])
            except (TypeError, ValueError):
                continue
            if year < start_year or year > end_year:
                continue

            ind = r[ind_c]
            qs = [_num(r[c]) for c in q_cs]
            reported = [i for i, q in enumerate(qs) if q is not None]
            if not reported:
                continue

            # Quarter by quarter, and collapsed to an annual figure only once the file has been
            # read — see ONE QUARTER FOR THE WHOLE COUNTRY above. Collapsing each partner first
            # and adding the results is what inflated Zimbabwe FY2024 by 44%.
            key = (iso3, MER_INDICATORS[ind], _suffix(r[ag_c]), year)
            cur = agg.setdefault(key, [None, None, None, None])
            for i in reported:
                cur[i] = (cur[i] or 0.0) + qs[i]
            names[iso3] = str(r.get("Country", iso3)) if "Country" in cols else iso3
            # partner detail, kept so a country-level move can be traced to the partners that
            # made it. A collapse concentrated in one partner and a collapse spread across all
            # of them are different events and the country number cannot tell them apart.
            uid, pname = _unit_id(r, pn_c, mc_c)
            if uid is not None:
                u = partners.setdefault(key, {}).setdefault(
                    uid, {"partner": pname, "mechanism": uid, "q": [None, None, None, None]})
                for i in reported:
                    u["q"][i] = (u["q"][i] or 0.0) + qs[i]
        return True

    # -- emitting ---------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        if not self.raw_dir.exists():
            log.warning("pepfar_agency: %s does not exist — download the MER Spotlight ZIPs "
                        "from data.pepfar.gov", self.raw_dir)
            return
        files = sorted(list(self.raw_dir.glob("*.zip")) + list(self.raw_dir.glob("*.txt"))
                       + list(self.raw_dir.glob("*.csv")))
        # the same TopLine file the country-total connector uses. Reading any other MER file
        # alongside it would count the same service twice at a different grain.
        topline = [f for f in files if "topline" in f.name.lower()]
        if not topline:
            log.warning("pepfar_agency: no TopLine MER file in %s — nothing to split", self.raw_dir)
            return
        if len(topline) < len(files):
            log.info("pepfar_agency: reading %d of %d file(s) in %s. Not read: %s",
                     len(topline), len(files), self.raw_dir,
                     [f.name for f in files if f not in topline])
        files = topline

        agg: Dict[tuple, List[Optional[float]]] = {}
        names: Dict[str, str] = {}
        partners: Dict[tuple, Dict[str, List[Optional[float]]]] = {}
        seen: Counter = Counter()

        for path in files:
            used = False
            try:
                if path.suffix == ".zip":
                    with zipfile.ZipFile(path) as z:
                        for member in [m for m in z.namelist() if m.lower().endswith(".txt")]:
                            with z.open(member) as fh:
                                for chunk in pd.read_csv(fh, sep="\t", dtype=str, chunksize=200_000,
                                                         on_bad_lines="skip", low_memory=False):
                                    if self._process(chunk, agg, names, partners,
                                                     wanted, start_year, end_year, seen):
                                        used = True
                                    else:
                                        break
                else:
                    sep = "\t" if path.suffix == ".txt" else ","
                    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=200_000,
                                             on_bad_lines="skip", low_memory=False):
                        if self._process(chunk, agg, names, partners,
                                         wanted, start_year, end_year, seen):
                            used = True
                        else:
                            break
            except Exception as exc:
                log.warning("pepfar_agency: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_agency: %s %s", path.name,
                     "(used)" if used else "(skipped — no Funding Agency column)")

        if seen:
            read = [c for c in seen if c in MER_INDICATORS]
            declared = [c for c in seen if c in DECLARED_UNMAPPED and c not in MER_INDICATORS]
            undecided = sorted(c for c in seen
                               if c not in MER_INDICATORS and c not in DECLARED_UNMAPPED)
            log.info("pepfar_agency: split %d of %d MER codes, %d deliberately left alone, "
                     "%d awaiting a decision", len(read), len(seen), len(declared), len(undecided))
            for code in undecided:
                log.warning("pepfar_agency: no rule covers MER code %s (%s rows). Add it to "
                            "MER_INDICATORS or to DECLARED_UNMAPPED with a reason.",
                            code, f"{seen[code]:,}")

        # The Partner_Performance file, read to the country, to test the TopLine values and to
        # carry each year's target. See TOPLINE IS SHORT IN FOUR YEARS above. Imported here and
        # not at the top, because pepfar_agency_snu imports this module at load.
        from .pepfar_agency_snu import partner_performance_national
        pp = partner_performance_national(self.raw_dir, wanted, start_year, end_year)
        if pp is None:
            log.warning("pepfar_agency: no Partner_Performance file in %s, so the TopLine values "
                        "are not checked and no row carries a target this run", self.raw_dir)
        yield from self._emit(agg, names, partners, pp)

    def _emit(self, agg, names, partners, pp=None) -> Iterator[PanelRow]:
        # The snapshot quarter belongs to the COUNTRY-year, not to one agency's slice of it:
        # the latest quarter any agency's partners reached. Reading USAID at Q3 because that is
        # where its own reporting stopped, while CDC is read at Q4, would put two halves of the
        # same partition months apart and stop them adding back to the country total.
        common_q: Dict[tuple, int] = {}
        for (iso3, base, _suf, year), vals in agg.items():
            if base not in SNAPSHOT_CANON:
                continue
            q = _last_q(vals)
            if q:
                k = (iso3, base, year)
                common_q[k] = max(common_q.get(k, 0), q)

        values: Dict[tuple, float] = {}
        for key, vals in agg.items():
            iso3, base, _suf, year = key
            if base in SNAPSHOT_CANON:
                q = common_q.get((iso3, base, year))
                if q and vals[q - 1] is not None:
                    values[key] = vals[q - 1]
                elif q:
                    own = _last_q(vals)
                    log.info("pepfar_agency: %s %s_%s FY%d — nothing reported in Q%d, the quarter "
                             "this country is read at (last figure Q%s). Left out of that year "
                             "and not carried forward.",
                             iso3, base, _suf, year, q, own)
            else:
                nn = [v for v in vals if v is not None]
                if nn:
                    values[key] = sum(nn)

        # Cadence is a property of the indicator-year, not of one agency's slice, but the two
        # agencies inside a country do not always report the same quarters, so each agency series
        # is asked separately. Same helper as pepfar_panorama, so a change of reporting frequency
        # cannot be caught in one connector and missed in the other.
        cadence = _panorama.release_cadence(agg, lambda k: (k[1], k[2], k[3]))
        latest_year = max((y for _, _, y in cadence), default=0)

        # The Partner_Performance figure for every series, by the rule this connector uses: a
        # snapshot at the quarter the country is read at, a flow summed. Then the two kinds of
        # series the TopLine file cannot show. An agency Partner_Performance reports and TopLine
        # does not has no row here at all, and neither has an agency that held a target and
        # reported nothing in either file, so both are written on the rows that do exist.
        from .pepfar_agency_snu import partner_file_differs, result_to_target, TARGET_NOTE
        pp_res, pp_tgt = pp if pp else ({}, {})
        code_of = {b: c for c, b in MER_INDICATORS.items()}
        pp_val: Dict[tuple, float] = {}
        pp_only: Dict[tuple, float] = {}
        in_topline = {(k[0], k[1], k[3]) for k in values}
        for (iso3, code, suf, year), qv in pp_res.items():
            base = MER_INDICATORS.get(code)
            if base is None:
                continue
            if base in SNAPSHOT_CANON:
                q = common_q.get((iso3, base, year))
                own = _last_q(qv)
                v = qv[q - 1] if q else None
                shown = qv[own - 1] if own else None
            else:
                nn = [x for x in qv if x is not None]
                v = shown = sum(nn) if nn else None
            if (iso3, base, year) not in in_topline:
                pp_only[(iso3, base, suf, year)] = shown or 0.0
            if v is not None:
                pp_val[(iso3, base, suf, year)] = v
        missing: Dict[tuple, Dict[str, float]] = {}
        for (iso3, base, suf, year), v in pp_val.items():
            if (iso3, base, year) in in_topline and (iso3, base, suf, year) not in values \
                    and v > 0.5:
                missing.setdefault((iso3, base, year), {})[suf] = v
        held: Dict[tuple, Dict[str, float]] = {}
        for (iso3, code, suf, year), t in pp_tgt.items():
            base = MER_INDICATORS.get(code)
            k = (iso3, base, suf, year)
            if base and t > 0 and (iso3, base, year) in in_topline and k not in values \
                    and (iso3, code, suf, year) not in pp_res:
                held.setdefault((iso3, base, year), {})[suf] = t
        if pp_only:
            log.warning("pepfar_agency: %d agency series are reported in Partner_Performance for "
                        "a country and year the TopLine file carries nothing for at all, so no "
                        "row exists to flag: %s", len(pp_only),
                        ", ".join(f"{k[0]} {k[1]}_{k[2]} FY{k[3]} ({v:,.0f})"
                                  for k, v in sorted(pp_only.items())))

        n = 0
        flagged = 0
        like: Dict[tuple, List[float]] = {}
        for key, value in sorted(values.items()):
            iso3, base, suffix, year = key
            canonical = f"{base}_{suffix}"
            vals = agg[key]
            snapshot = base in SNAPSHOT_CANON
            nq = len([v for v in vals if v is not None])
            extra: Dict[str, object] = {
                "note": "PEPFAR MER — PROGRAM FOOTPRINT, not national totals",
                "funding_agency": suffix,
                "quarters_reported": nq,
                "interpretation": INTERPRETATION,
            }

            if snapshot:
                # WHICH quarter the snapshot came from, because two snapshots taken from
                # different quarters are months apart and are not a year-on-year comparison.
                q_now = common_q.get((iso3, base, year))
                q_prev = common_q.get((iso3, base, year - 1))
                extra["snapshot_quarter"] = q_now
                full_year = q_now == 4
                if q_now and q_prev and q_now != q_prev:
                    warn = (f"snapshot taken from Q{q_now} of FY{year} but Q{q_prev} of "
                            f"FY{year - 1} — these are not twelve months apart and the change "
                            f"between them is not an annual change.")
                    extra["snapshot_quarter_mismatch"] = warn
                    log.warning("pepfar_agency: %s %s %d — %s", iso3, canonical, year, warn)
            else:
                # The quarters behind the sum, and the same quarters a year earlier. The agency
                # split is the reason to keep them: FY2025 publishes Q4 alone, so a USAID series
                # falling and a CDC series holding are both invisible under an annual total that
                # compares one quarter with four. Same helpers as pepfar_panorama, so the two
                # connectors cannot drift apart on what a year means.
                here = cadence.get((base, suffix, year), [])
                prev_cad = cadence.get((base, suffix, year - 1)) or here
                truncated, same_span = _panorama.span_status(
                    here, prev_cad, year, latest_year)
                extra.update(_panorama.quarter_detail(
                    vals, agg.get((iso3, base, suffix, year - 1)), year, same_span))
                lq = (extra.get("like_quarter_comparison") or {}).get("ratio")
                if lq:
                    like.setdefault((canonical, year), []).append(lq)
                extra["release_quarters"] = [f"Q{q}" for q in here]
                extra["comparison_year_quarters"] = [f"Q{q}" for q in prev_cad]
                full_year = not truncated and nq >= len(here)
                if truncated or 0 < nq < len(here):
                    why = (f"FY{year} is part-published, carrying "
                           f"{', '.join('Q%d' % q for q in here)} where FY{year - 1} carries "
                           f"{', '.join('Q%d' % q for q in prev_cad)}" if truncated else
                           f"this agency series reported {nq} of the "
                           f"{', '.join('Q%d' % q for q in here)} that FY{year} publishes")
                    extra["partial_year"] = (
                        f"{why}. This annual total covers less of the year than the total it "
                        f"would be compared with, so it is a PARTIAL sum and must not be read "
                        f"as a decline. Use like_quarter_comparison instead.")

            # the partners behind the number, largest first, so a move can be traced — read at
            # the same quarter the series itself is read at, so they add up to it
            det = partners.get(key) or {}
            collapsed: Dict[str, float] = {}
            absent = []
            for u in det.values():
                pv, pname = u["q"], u["partner"]
                if snapshot:
                    v = pv[extra["snapshot_quarter"] - 1] if extra["snapshot_quarter"] else None
                    if v is None:
                        q_own = _last_q(pv)
                        if q_own:
                            absent.append({"partner": pname, "mechanism": u["mechanism"],
                                           "last_quarter": q_own, "last_value": pv[q_own - 1]})
                        continue
                else:
                    nn = [x for x in pv if x is not None]
                    v = sum(nn) if nn else None
                    if v is None:
                        continue
                # displayed by partner, accumulated by mechanism: a partner running two
                # mechanisms is one line in `top_partners` and two units underneath it.
                collapsed[pname] = collapsed.get(pname, 0.0) + v
            if collapsed:
                top = sorted(collapsed.items(), key=lambda kv: kv[1], reverse=True)[:5]
                extra["top_partners"] = [{"partner": p, "value": v} for p, v in top]
                extra["n_partners"] = len(collapsed)
            if absent:
                # A partner that reported earlier in the year and not at the quarter the country
                # is read at has usually handed its mechanism to another partner. Its last figure
                # is not carried forward — that is what counted Zimbabwe's cohort twice — so it
                # is recorded here, where a reader can see how much moved.
                absent.sort(key=lambda d: d["last_value"], reverse=True)
                extra["partners_absent"] = {
                    "n": len(absent),
                    "last_reported_total": sum(d["last_value"] for d in absent),
                    "partners": absent[:5],
                    "note": (f"reported earlier in FY{year} but not in "
                             f"Q{extra['snapshot_quarter']}, the quarter this country is read "
                             f"at; not carried forward."),
                }

            # The TopLine value tested against Partner_Performance, and kept either way.
            pv = pp_val.get(key)
            if pv is not None and abs(pv - value) > 0.5:
                extra["partner_file_differs"] = partner_file_differs(
                    value, pv, f"{suffix} series, country and year")
                flagged += 1
            t = pp_tgt.get((iso3, code_of[base], suffix, year))
            if t is not None:
                extra["fy_target"] = {"value": t,
                                      "result_to_target": result_to_target(value, t, full_year),
                                      "note": TARGET_NOTE}
            gone = {a: v for a, v in missing.get((iso3, base, year), {}).items() if a != suffix}
            if gone:
                extra["agency_missing_from_topline"] = {
                    "partner_performance_value": gone,
                    "note": (f"Partner_Performance reports {', '.join(sorted(gone))} in this "
                             f"country in FY{year} and the TopLine file this connector reads "
                             f"does not, so no row exists for "
                             f"{' or '.join(sorted(gone))} this year. The missing row is missing "
                             f"reporting and not an agency that stopped working here."),
                }
            quit_ = {a: v for a, v in held.get((iso3, base, year), {}).items() if a != suffix}
            if quit_:
                extra["agency_held_target_without_result"] = {
                    "target": quit_,
                    "note": (f"{', '.join(sorted(quit_))} held an FY{year} target in this "
                             f"country and reported nothing in either PEPFAR partner file, so "
                             f"the absence of a row is a stop and not a gap in one file, and the "
                             f"stop was not in the plan when the targets were set."),
                }

            yield self.make_row(
                country_iso3=iso3, country_name=names.get(iso3, ""),
                indicator_id=canonical, year=year, value=value, unit="count",
                source_url="https://data.pepfar.gov/datasets",
                source_indicator_code="MER (by funding agency)",
                extra=extra,
            )
            n += 1
        # The comparison that holds, one line per agency series whose quarters moved. Read these
        # against each other rather than on their own: the same funding cut shows as one agency's
        # ratio falling while another agency's holds, and neither ratio says that by itself.
        for (canonical, year), ratios in sorted(like.items()):
            ratios.sort()
            med = ratios[len(ratios) // 2]
            log.info("pepfar_agency: %s FY%d — quarters differ from FY%d, so the annual totals "
                     "are not comparable. Like-quarter median %.2f over %d countries, below 1.0 "
                     "in %d of them.", canonical, year, year - 1, med, len(ratios),
                     len([r for r in ratios if r < 1.0]))
        if pp:
            log.warning("pepfar_agency: %d rows differ from Partner_Performance and carry "
                        "extra.partner_file_differs; %d country-indicator-years have an agency "
                        "Partner_Performance reports and TopLine does not (%s)", flagged,
                        len(missing), ", ".join(
                            f"{k[0]} {k[1]} FY{k[2]} {'/'.join(sorted(v))}"
                            for k, v in sorted(missing.items())))
            if held:
                log.info("pepfar_agency: %d country-indicator-years have an agency that held a "
                         "target and reported nothing in either file: %s", len(held), ", ".join(
                             f"{k[0]} {k[1]} FY{k[2]} {'/'.join(sorted(v))}"
                             for k, v in sorted(held.items())))
        log.info("pepfar_agency: emitted %d rows", n)
