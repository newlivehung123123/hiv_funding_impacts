"""
PEPFAR Panorama Spotlight connector — the programmatic "to source" baseline.

PEPFAR's own MER (Monitoring, Evaluation & Reporting) service-delivery data — the
process metrics amfAR and Adrian centre on. Historically public, quarterly, at
sub-national + demographic granularity; being dismantled under the MOUs, so ingesting
it now is ARCHIVAL insurance.

Access: download the Spotlight datasets from https://data.pepfar.gov/datasets — they
arrive as ZIPs. Drop the ZIPs straight into `data/raw/pepfar/` (no need to unzip; we
read the `.txt` inside). The connector targets the **long MER format** (e.g.
`Public_Partner_MER_TopLine`): columns include ISO3, Indicator, Numerator/Denominator,
Standardized Disaggregate, Fiscal Year, Quarter 1-4. Wide Spotlight files, PDFs, budget
and site-level files are auto-skipped.

Correctness detail: `TX_CURR` (people currently on treatment) is a SNAPSHOT — its annual
value is the latest reported quarter, NOT the sum of quarters. `HTS_TST_POS` (tested
positive) is cumulative — annual = sum of the quarters. We handle each accordingly, then
sum across partners to the country total (Total Numerator rows only).

THE MIXED-QUARTER TRAP (found 2026-08-04, and it was live in the published panel)

"Latest reported quarter" has to mean one quarter for the whole country, not each partner
at its own. Reading every partner at whichever quarter it last reported and adding those
together produces a total that belongs to no date, and when a mechanism changes hands
mid-year it counts the same cohort twice. Zimbabwe FY2024 is the case: UNIVERSITY OF
WASHINGTON reported Q1 only (539,106 on ART) and then handed the mechanism to Zim - TTECH,
which reported Q2-Q4. Summing each at its own last quarter gave 1,753,641 against a Q4
figure of 1,214,535 — an inflation of 44%, of exactly the size of the transferred cohort.

So the quarter is now chosen per country-indicator-year — the latest quarter any partner
reports — and every partner is read at that quarter. A partner with nothing there is left
out of that year and not carried forward at a stale value, and what it last reported is
recorded in `extra.partners_absent` and logged. A partner that stops reporting is a finding
in a funding-cut study; it should look like an absence, not like a programme still running.

TWO DATA-QUALITY TRAPS this connector flags instead of hiding (both found 2026-07-19):

1. **Partial years** (`extra.partial_year`, `extra.quarters_reported`). A cumulative
   indicator in a part-reported year is a PARTIAL total, not a decline. FY2025 currently
   publishes only **1 of 4 quarters**, which makes every SEA country's `new_diagnoses` look
   like a 70-90% collapse (MMR -93%, VNM -83%, IDN -76%, PHL -74%, LAO -70%). Read naively
   in a funding-cut study this is a catastrophic false positive.

2. **Reporting-scope discontinuities** (`extra.data_quality_flag`) — a >3x year-on-year jump.
   E.g. Thailand FY2025 `on_art_count` 53,330 -> 260,981: the SAME three partners, but the
   government ones (MOPH 25k->185k, BMA 11k->76k) began reporting their full national
   caseload while the USAID partner collapsed (FHI 17,363 -> 207, a genuine funding-cut
   signal). The country total is not comparable across that boundary; the partner-level
   detail is where the real signal lives.

Neither flag alters the source value — we surface the problem and let the analyst decide.

TAGGING: PEPFAR MER measures the PEPFAR program footprint, NOT national totals.
source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

MER_INDICATORS = {"TX_CURR": "on_art_count", "HTS_TST_POS": "new_diagnoses"}
SNAPSHOT = {"TX_CURR"}  # annual = latest quarter, not a sum
# canonicals whose annual value is a SUM of quarters — for these a part-reported year yields a
# PARTIAL total that must never be read as a real decline (e.g. FY2025 has only 1 of 4 quarters).
CUMULATIVE_CANON = {MER_INDICATORS[k] for k in MER_INDICATORS if k not in SNAPSHOT}


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


def _last_q(vals: List[Optional[float]]) -> Optional[int]:
    """The latest quarter (1-4) that carries a number, or None if the year is empty."""
    reported = [i for i, v in enumerate(vals) if v is not None]
    return reported[-1] + 1 if reported else None


def _unit_id(row, pn_c: Optional[str], mc_c: Optional[str]):
    """(id, label) of the thing that reported this row — the MECHANISM, not the partner.

    One row of the TopLine file is one mechanism. 530 partner names in this download run two
    or more mechanisms inside the same country-indicator-year, so keying the detail by partner
    name merges units that report different quarters and hides exactly the handovers this
    connector needs to see.
    """
    pname = str(row[pn_c]).strip() if pn_c else ""
    if pname.lower() in ("nan", "none"):
        pname = ""
    code = str(row[mc_c]).strip() if mc_c else ""
    if code.lower() in ("nan", "none"):
        code = ""
    if not code and not pname:
        return None, None
    return (code or pname), (f"{pname} (mechanism {code})" if pname and code else pname or code)


class PEPFARPanoramaConnector(BaseConnector):
    source_id = "pepfar_panorama"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "PEPFAR Panorama MER (TX_CURR, HTS_TST_POS). PEPFAR footprint, not national."

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _process(self, chunk: pd.DataFrame, agg: Dict[tuple, List[Optional[float]]],
                 names: Dict[str, str], partner_q: Dict[tuple, Dict[str, List[Optional[float]]]],
                 wanted, start_year: int, end_year: int) -> bool:
        cols = list(chunk.columns)
        ind_c = _ci(cols, "indicator")
        fy_c = _ci(cols, "fiscal year")
        nd_c = _ci(cols, "numerator/denominator")
        dis_c = _ci(cols, "standardized disaggregate")
        iso_c = _ci(cols, "iso3") or _ci(cols, "country")
        pn_c = _ci(cols, "partner name")
        mc_c = _ci(cols, "mechanism code")
        q_cs = [_ci(cols, f"quarter {i}") for i in (1, 2, 3, 4)]
        if not (ind_c and fy_c and dis_c and iso_c and all(q_cs)):
            return False  # not the long MER format -> signal skip

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
            # Partners are added QUARTER BY QUARTER and collapsed to an annual figure only once
            # the whole file has been read. Collapsing each partner first and adding the results
            # is what inflated Zimbabwe by 44% (see THE MIXED-QUARTER TRAP above); a cumulative
            # indicator is unaffected either way, since summing quarters and summing partners
            # commute.
            key = (iso3, MER_INDICATORS[ind], year)
            cur = agg.setdefault(key, [None, None, None, None])
            for i in reported:
                cur[i] = (cur[i] or 0.0) + qs[i]
            names[iso3] = str(r.get("Country", iso3)) if "Country" in cols else iso3
            # For snapshots, keep each reporting unit's own quarters, so the ones missing from
            # the quarter the country ends up being read at can be named, not just dropped.
            if ind in SNAPSHOT:
                uid, label = _unit_id(r, pn_c, mc_c)
                if uid is not None:
                    u = partner_q.setdefault(key, {}).setdefault(
                        uid, {"label": label, "q": [None, None, None, None]})
                    for i in reported:
                        u["q"][i] = (u["q"][i] or 0.0) + qs[i]
        return True

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        files = (sorted(list(self.raw_dir.glob("*.zip")) + list(self.raw_dir.glob("*.txt"))
                        + list(self.raw_dir.glob("*.csv"))) if self.raw_dir.exists() else [])
        if not files:
            log.warning("pepfar_panorama: no files in %s — download MER Spotlight ZIPs from data.pepfar.gov", self.raw_dir)
            return
        # avoid double-counting: TopLine already holds the country totals, so if it is
        # present use it exclusively (skip AgeSex / other granular MER files).
        topline = [f for f in files if "topline" in f.name.lower()]
        if topline:
            log.info("pepfar_panorama: using TopLine totals file(s) only: %s", [f.name for f in topline])
            files = topline

        agg: Dict[tuple, List[Optional[float]]] = {}
        names: Dict[str, str] = {}
        partner_q: Dict[tuple, Dict[str, List[Optional[float]]]] = {}
        for path in files:
            used = False
            try:
                if path.suffix == ".zip":
                    with zipfile.ZipFile(path) as z:
                        for member in [m for m in z.namelist() if m.lower().endswith(".txt")]:
                            with z.open(member) as fh:
                                for chunk in pd.read_csv(fh, sep="\t", dtype=str, chunksize=200_000,
                                                         on_bad_lines="skip", low_memory=False):
                                    if self._process(chunk, agg, names, partner_q, wanted,
                                                     start_year, end_year):
                                        used = True
                                    else:
                                        break
                else:
                    sep = "\t" if path.suffix == ".txt" else ","
                    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=200_000,
                                             on_bad_lines="skip", low_memory=False):
                        if self._process(chunk, agg, names, partner_q, wanted,
                                         start_year, end_year):
                            used = True
                        else:
                            break
            except Exception as exc:
                log.warning("pepfar_panorama: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_panorama: %s %s", path.name, "(used)" if used else "(skipped — not long MER format)")

        # One collapse from quarters to a year, done for every country-year before any row is
        # emitted, so a year can be compared with the one before it on the same rule.
        values: Dict[tuple, float] = {}
        snap_q: Dict[tuple, int] = {}
        for key, vals in agg.items():
            if key[1] in CUMULATIVE_CANON:
                nn = [v for v in vals if v is not None]
                if nn:
                    values[key] = sum(nn)
            else:
                q = _last_q(vals)
                if q:
                    values[key] = vals[q - 1]
                    snap_q[key] = q

        n = 0
        for (iso3, canonical, year), value in sorted(values.items()):
            key = (iso3, canonical, year)
            extra = {"note": "PEPFAR MER — PROGRAM FOOTPRINT, not national totals"}
            nq = len([v for v in agg[key] if v is not None])
            extra["quarters_reported"] = nq
            # A snapshot indicator is immune to a part-reported year — one quarter is a whole
            # answer — but only if it is the SAME quarter as the year before. FY2025 currently
            # publishes Q4, which is the quarter FY2024's snapshot also comes from, so the two
            # are twelve months apart and comparable. That is true of this download and not of
            # the format, so the quarter is recorded and a change of quarter is called out.
            if canonical not in CUMULATIVE_CANON:
                q_now = snap_q.get(key)
                q_prev = snap_q.get((iso3, canonical, year - 1))
                extra["snapshot_quarter"] = q_now
                if q_now and q_prev and q_now != q_prev:
                    warn = (f"snapshot taken from Q{q_now} of FY{year} but Q{q_prev} of "
                            f"FY{year - 1} — these are not twelve months apart, and the change "
                            f"between them is not an annual change.")
                    extra["snapshot_quarter_mismatch"] = warn
                    log.warning("pepfar_panorama: %s %s %d — %s", iso3, canonical, year, warn)
                # Partners that reported earlier in the year and not in the quarter the country
                # is read at. Their last figure is deliberately NOT carried forward — a
                # mechanism handed to another partner would otherwise be counted twice — so it
                # is reported here instead, where a reader can see how much of the cohort moved.
                absent = []
                for u in (partner_q.get(key) or {}).values():
                    pv = u["q"]
                    if pv[q_now - 1] is not None:
                        continue
                    q_own = _last_q(pv)
                    if q_own:
                        absent.append({"partner": u["label"], "last_quarter": q_own,
                                       "last_value": pv[q_own - 1]})
                if absent:
                    absent.sort(key=lambda d: d["last_value"], reverse=True)
                    total = sum(d["last_value"] for d in absent)
                    extra["partners_absent"] = {
                        "n": len(absent), "last_reported_total": total,
                        "partners": absent[:5],
                        "note": (f"reported earlier in FY{year} but not in Q{q_now}, the quarter "
                                 f"this country is read at. Not carried forward: a partner that "
                                 f"stops reporting is usually a mechanism transfer, and adding "
                                 f"its stale figure to the new partner's counts the same cohort "
                                 f"twice."),
                    }
                    log.info("pepfar_panorama: %s %s %d — %d partner(s) absent from Q%d "
                             "(%s between them at their own last quarter); not carried forward",
                             iso3, canonical, year, len(absent), q_now, f"{total:,.0f}")
            # A cumulative indicator in a part-reported year is a PARTIAL total, NOT a decline.
            # FY2025 currently publishes only 1 of 4 quarters, which makes every country's
            # new_diagnoses look like a 70-90% collapse. Flag it so nobody reads it as a cut.
            if canonical in CUMULATIVE_CANON and 0 < nq < 4:
                extra["partial_year"] = (
                    f"only {nq}/4 quarters reported for FY{year} — this annual total is a PARTIAL "
                    f"sum and must NOT be compared with full years or read as a decline."
                )
                log.warning("pepfar_panorama: %s %s %d — PARTIAL YEAR (%d/4 quarters reported); "
                            "annual total is a partial sum, not a decline", iso3, canonical, year, nq)
            # Surface (never silently "fix") year-on-year discontinuities. PEPFAR partner
            # reporting scope can change: e.g. Thailand FY2025, where the government partners
            # (MOPH/BMA) began reporting their full national caseload (25k -> 185k) while the
            # USAID partner collapsed (17,363 -> 207). The country total is then NOT comparable
            # across that boundary, and a naive read shows "growth" where the opposite happened.
            prev = values.get((iso3, canonical, year - 1))
            # (skip when already explained by partial reporting — that's incompleteness, not scope)
            if "partial_year" not in extra and prev and value and (value / prev > 3 or prev / value > 3):
                flag = (f"discontinuity vs {year - 1}: {prev:,.0f} -> {value:,.0f}. Likely a "
                        f"reporting-scope/partner-attribution change — NOT comparable year-on-year; "
                        f"inspect partner-level detail before using in trend analysis.")
                extra["data_quality_flag"] = flag
                log.warning("pepfar_panorama: %s %s %d — %s", iso3, canonical, year, flag)
            yield self.make_row(
                country_iso3=iso3, country_name=names.get(iso3, ""),
                indicator_id=canonical, year=year, value=value, unit="count",
                source_url="https://data.pepfar.gov/datasets", source_indicator_code="MER",
                extra=extra,
            )
            n += 1
        log.info("pepfar_panorama: emitted %d rows", n)
