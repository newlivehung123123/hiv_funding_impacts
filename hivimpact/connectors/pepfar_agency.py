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

TAGGING: PEPFAR MER measures the PEPFAR programme footprint, not national totals.
source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

# the MER indicators worth splitting: the treatment cohort and the testing yield
MER_INDICATORS = {"TX_CURR": "on_art_count", "HTS_TST_POS": "new_diagnoses"}
SNAPSHOT = {"TX_CURR"}  # annual = latest reported quarter, never a sum
SNAPSHOT_CANON = {MER_INDICATORS[k] for k in SNAPSHOT}

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
        files = topline

        agg: Dict[tuple, List[Optional[float]]] = {}
        names: Dict[str, str] = {}
        partners: Dict[tuple, Dict[str, List[Optional[float]]]] = {}

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
                                                     wanted, start_year, end_year):
                                        used = True
                                    else:
                                        break
                else:
                    sep = "\t" if path.suffix == ".txt" else ","
                    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=200_000,
                                             on_bad_lines="skip", low_memory=False):
                        if self._process(chunk, agg, names, partners,
                                         wanted, start_year, end_year):
                            used = True
                        else:
                            break
            except Exception as exc:
                log.warning("pepfar_agency: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_agency: %s %s", path.name,
                     "(used)" if used else "(skipped — no Funding Agency column)")

        yield from self._emit(agg, names, partners)

    def _emit(self, agg, names, partners) -> Iterator[PanelRow]:
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

        n = 0
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
                if q_now and q_prev and q_now != q_prev:
                    warn = (f"snapshot taken from Q{q_now} of FY{year} but Q{q_prev} of "
                            f"FY{year - 1} — these are not twelve months apart and the change "
                            f"between them is not an annual change.")
                    extra["snapshot_quarter_mismatch"] = warn
                    log.warning("pepfar_agency: %s %s %d — %s", iso3, canonical, year, warn)
            elif 0 < nq < 4:
                extra["partial_year"] = (
                    f"only {nq}/4 quarters reported for FY{year} — this annual total is a "
                    f"PARTIAL sum and must NOT be compared with full years or read as a decline.")

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

            yield self.make_row(
                country_iso3=iso3, country_name=names.get(iso3, ""),
                indicator_id=canonical, year=year, value=value, unit="count",
                source_url="https://data.pepfar.gov/datasets",
                source_indicator_code="MER (by funding agency)",
                extra=extra,
            )
            n += 1
        log.info("pepfar_agency: emitted %d rows", n)
