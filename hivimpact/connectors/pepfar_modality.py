"""
PEPFAR testing split by HOW the person was reached — outreach against the clinic door.

Every other PEPFAR series in this panel counts services. This one counts the way the service
found the person, which is the part of the programme a funding cut removes first. Facility
testing is a nurse in a clinic offering a test to somebody who already walked in, and it costs
almost nothing extra once the clinic is open. Community testing is a van, a fuel budget, a
team of outreach workers and a per-diem, and it is a line item that can be cancelled in a week
without closing anything. So the two arms respond to the same cut at different speeds and by
different amounts, and the contrast between them is a mechanism rather than a total.

The file is `Country_Level_Results_by_Modality_Coarse_Age_and_Sex`, published at country level
rather than partner level, one row per country, indicator, coarse age, sex and MODALITY, with a
column per fiscal year and quarter.

WHAT THE SPLIT SHOWS, Q4 FY2024 AGAINST Q4 FY2025

Both quarters are the fourth quarter of their fiscal year, so the comparison is twelve months
apart and like for like, and FY2025 publishes Q4 alone. The base is the 52 of the file's 59
countries whose modality labels are complete, meaning the seven that carry an unclassified
modality in FY2025 are held out (see UNCLASSIFIED below):

    community testing   3,056,545 -> 1,068,854   (-65.0%)
    facility testing   16,021,304 -> 13,517,748  (-15.6%)
    community share          16.0% ->      7.3%

    positives found in the community  51,185 -> 34,825  (-32.0%)
    positives found in facilities    294,968 -> 241,411 (-18.2%)

Community testing fell roughly four times as far as facility testing, and it fell further than
facility testing in 21 of the 26 countries doing more than twenty thousand tests in Q4 FY2024
with both arms running, including Uganda (-93.5% community against -10.3% facility) and Nigeria
(-83.4% against -15.8%). Positivity in the community arm rose from 1.67 per cent to 3.26 per
cent while facility positivity barely moved, 1.84 per cent to 1.79 per cent, which is what a
programme looks like when it stops going out to find people and keeps only its highest-yield
contacts.

THE PARTNER-COVERAGE DEFECT THIS FILE EXPOSES (found 2026-09-07)

`pepfar_panorama` and `pepfar_agency` build their country totals by adding up the partners named
in `Public_Partner_MER_TopLine`. This file reports the country directly. Summing this file's
HTS_TST across modality, age and sex gives a country total that can be compared with the partner
sum, and over 415 country-years in 58 countries the median ratio is exactly 1.000000, with 349
of them inside half a per cent. The two are the same quantity.

They part company in one identifiable place. Where PEPFAR runs a country through a REGIONAL
operating unit it names very few partners, and the partner sum is then a fraction of the country
figure. Thailand FY2018 publishes exactly one partner, Bangkok Metropolitan Administration, with
1,308 tests, against 75,944 in this file. Thailand FY2019 is 1,752 against 136,227. Every
country-year where the partner sum falls more than five per cent short belongs to South and
Southeast Asia Region, Central Asia Region or Central and South America Region, with the single
exception of Kenya FY2018 at 5.8 per cent.

So this connector also emits the country totals, under the same canonical ids `pepfar_panorama`
uses. That is deliberate. The two sources then form a pair in the reconciliation table, and the
regional operating units show up there as a named divergence instead of sitting in the panel as
a silent undercount. Anything summing the panel must filter on source_id, the same rule the
agency split already carries.

Eleven country-years run the other way, with this file three to fifty-four per cent BELOW the
partner sum, worst at Malawi FY2018 (0.462) and Namibia FY2020 to FY2022 (0.68 to 0.74). The
shortfall is spread evenly across all four quarters and no modality is missing, so it is not a
missing quarter and not a missing modality. Ordinary explanations were tested and failed: the
obvious one, that results reported without an age breakdown are dropped rather than filed under
Unknown Age, is contradicted by Namibia, whose Unknown Age share is 28 per cent in exactly the
years it falls short. It is recorded here as unexplained rather than described as understood.

UNCLASSIFIED: THE MODALITY THAT APPEARS IN THE YEAR THE ANSWER CHANGES

`Not Specified` carries no HTS_TST at all before FY2025 and 784,344 tests in Q4 FY2025, which is
the one year the community share collapses. A category that arrives with the finding has to be
kept out of the finding. Rows carrying `Not Specified` are counted into the country total, put
in NEITHER arm, and recorded in `extra.unclassified_tests`, and a country carrying any of them
is held out of the headline comparison above.

The unclassified rows are confined to seven countries, Thailand, Mozambique, Haiti, the
Dominican Republic, Botswana, Jamaica and Zambia, and 727,005 of the 784,344 belongs to
Thailand alone. To see why holding those seven out matters, Thailand's own classified testing
in Q4 FY2024 was 45,211 tests across both arms, so putting the 727,005 into either arm would
have moved the arm by more than sixteen times the whole of Thailand's previous quarter. None of
the countries driving the community collapse, Uganda, Nigeria, South Africa, Tanzania and
Ethiopia, carries a single unclassified test.

WHAT ELSE IS IN THE FILE, AND WHY ALMOST NONE OF IT IS READ

The file holds 46 MER codes, and only four of them carry a modality at all: HTS_TST, HTS_TST_POS,
HTS_INDEX and HTS_RECENT. The other 42 have an empty modality column, so for those codes this
file is the same country total already in the panel at a different age and sex grain, and reading
it would duplicate rows without adding a measurement. HTS_INDEX and HTS_RECENT do carry a
modality and are left alone only because neither has a canonical definition yet, which is an open
decision and not an oversight.

Age and sex are collapsed. Coarse Age here is 15+, <15 and Unknown Age for the two codes read,
which is a partition, so collapsing is exact. The 18+ and <18 scheme in this file belongs to the
OVC indicators alone and never mixes with the 15+ scheme inside a code. Keeping the age and sex
detail needs the `age_group` column decision that is still open, so it is declared and dropped
rather than half-kept.

TWO DEFINITION CHANGES THAT BREAK A MODALITY TIME SERIES, THOUGH NOT THE ARM SPLIT

`Post ANC1` runs from FY2019 to FY2023 and is replaced in FY2024 by `PMTCT Post ANC1
Pregnant/L&D` and `PMTCT Post ANC1 Breastfeeding`. `SNS` and `SNSMod` begin in FY2022. Both
changes are inside the facility and community arms respectively, so the two-arm split is
continuous across them, but no single modality label should be tracked through FY2024 without
checking this first.

TAGGING: PEPFAR MER measures the PEPFAR programme footprint, not national totals.
source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from . import pepfar_panorama as _panorama
from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

# the two codes whose modality axis this connector exists to read, and the canonical each one
# already occupies at country level. Both are cumulative: an annual figure is the sum of the
# quarters published, never the latest quarter. TX_CURR is in this file too and IS a snapshot,
# which is one of the reasons it is not read here — see DECLARED_UNMAPPED.
MER_INDICATORS = {"HTS_TST": "hiv_tests_performed", "HTS_TST_POS": "new_diagnoses"}

COMMUNITY, FACILITY, UNCLASSIFIED = "community", "facility", "unclassified"

# PEPFAR's own modality vocabulary, listed rather than pattern-matched.
#
# The tempting rule is that a label ending in "Mod" is community-based, which is true of every
# label in this download. It is not written that way because a future MER version adding
# "Drop-in Centre" or "Peer Navigator" would be filed as facility in silence, and the whole
# value of this connector is the boundary between the two arms. An unknown label is counted
# into the country total, put in neither arm, and logged as a warning.
COMMUNITY_MODALITIES = {
    "IndexMod",     # index (partner) testing done at the contact's home or in the community
    "MobileMod",    # mobile vans and outreach events
    "VCTMod",       # voluntary counselling and testing delivered outside a facility
    "OtherMod",     # other community modality
    "SNSMod",       # social network strategy, community arm
    "HomeMod",      # home-based testing (present as a label, carries no volume in this download)
}
FACILITY_MODALITIES = {
    "Index", "Active Index", "Active Other", "Active SNS", "SNS",
    "Emergency Ward", "Inpat", "Malnutrition", "Other Facility", "Other PITC", "Pediatric",
    "PMTCT ANC", "Post ANC1", "PMTCT Post ANC1 Pregnant/L&D", "PMTCT Post ANC1 Breastfeeding",
    "PrEP CT", "STI Clinic", "TBClinic", "VCT", "VMMC",
}
# Present in the file, and genuinely not an answer to "how was this person reached". Counted
# into the total, kept out of both arms. See UNCLASSIFIED in the docstring for why this
# category matters more than its size suggests.
UNCLASSIFIED_MODALITIES = {"Not Specified", ""}

# every code in this download, with the reason it is not read. Written out rather than
# defaulted, so a code appearing in a future refresh is unaccounted for loudly.
_NO_MODALITY = ("carries an empty modality column throughout, so this file holds the same "
                "country total already in the panel at a different age and sex grain and "
                "reading it would duplicate rows without adding a measurement")
DECLARED_UNMAPPED: Dict[str, str] = {
    "HTS_INDEX": "does carry a modality, and has no canonical definition yet — the same open "
                 "decision pepfar_panorama records for this code",
    "HTS_RECENT": "recency testing, which separates recent infection from long-standing "
                  "infection. Carries a modality and would be worth splitting, but has no "
                  "canonical definition yet",
    "HTS_INDEX_KNOWNPOS": "modality is Not Specified on every row, so there is no split to read",
    "HTS_INDEX_NEWNEG": "modality is Not Specified on every row, so there is no split to read",
    "HTS_INDEX_NEWPOS": "modality is Not Specified on every row, so there is no split to read",
    "TX_CURR": f"{_NO_MODALITY}, and it is a snapshot rather than a sum, which this connector "
               f"has no need to handle",
    "TX_PVLS": f"{_NO_MODALITY}, and it is a snapshot",
}
DECLARED_UNMAPPED.update({code: _NO_MODALITY for code in (
    "AGYW_PREV", "CXCA_SCRN", "CXCA_SCRN_POS", "CXCA_TX", "HTS_SELF",
    "OVC_HIVSTAT", "OVC_HIVSTAT_NEG", "OVC_HIVSTAT_POS", "OVC_SERV",
    "PMTCT_ART", "PMTCT_EID", "PMTCT_HEI_POS", "PMTCT_STAT", "PMTCT_STAT_POS",
    "POST_RESP", "PP_PREV", "PrEP_CT", "PrEP_CURR", "PrEP_NEW",
    "TB_ART", "TB_PREV", "TB_STAT", "TX_TB", "TX_NEW", "TX_NET_NEW", "TX_RTT",
    "TX_CURR_ARVDisp_less_three_mo", "TX_CURR_ARVDisp_three_five_mo",
    "TX_CURR_ARVDisp_six_more_mo",
    "TX_ML_died", "TX_ML_refused_stopped", "TX_ML_transferred_out",
    "TX_ML_IIT_less_three_mo", "TX_ML_IIT_three_five_mo",
    "TX_ML_IIT_more_three_mo", "TX_ML_IIT_six_more_mo",
    "VMMC_CIRC",
)})

INTERPRETATION = (
    "PEPFAR programme footprint, not a national total. Community and facility are the two ways "
    "a testing programme reaches a person, and they cost different things, so a cut moves them "
    "by different amounts. Read the two arms against each other rather than either on its own: "
    "the community arm falling while the facility arm holds is outreach being cancelled, and "
    "both falling together is the clinic itself closing. Where extra.unclassified_tests is "
    "present the two arms do not add to the country total."
)

_YEAR_Q = re.compile(r"^(\d{4})\s+Quarter\s+([1-4])\s+Results$", re.I)
_YEAR_TARGET = re.compile(r"^(\d{4})\s+Targets$", re.I)


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


def _ci(cols: List[str], *names: str) -> Optional[str]:
    low = {c.lower().strip(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    return None


def year_columns(cols: List[str]) -> Dict[int, List[Optional[str]]]:
    """Which column holds which fiscal year and quarter, read off the header.

    The years this file covers are a property of the download and not of the format. FY2018 to
    FY2025 is what the September 2025 release happens to carry; a later refresh carries FY2026
    and an earlier archive carries less. Discovering the years from the header rather than
    hard-coding a range is the same rule the period note follows elsewhere in this project.
    """
    found: Dict[int, List[Optional[str]]] = {}
    for c in cols:
        m = _YEAR_Q.match(str(c).strip())
        if m:
            year, q = int(m.group(1)), int(m.group(2))
            found.setdefault(year, [None, None, None, None])[q - 1] = c
    return found


def classify(modality) -> Tuple[str, str]:
    """(arm, label) for one modality cell. Unknown labels land in UNCLASSIFIED, never in an arm."""
    label = "" if modality is None else str(modality).strip()
    if label.lower() in ("nan", "none"):
        label = ""
    if label in COMMUNITY_MODALITIES:
        return COMMUNITY, label
    if label in FACILITY_MODALITIES:
        return FACILITY, label
    return UNCLASSIFIED, label


class PEPFARModalityConnector(BaseConnector):
    source_id = "pepfar_modality"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = "PEPFAR HIV testing split community vs facility — the mechanism a cut removes first."

    def __init__(self, raw_dir: str = "data/raw/pepfar", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _process(
        self,
        chunk: pd.DataFrame,
        agg: Dict[tuple, List[Optional[float]]],
        names: Dict[str, str],
        ous: Dict[str, str],
        labels: Dict[tuple, Counter],
        wanted,
        start_year: int,
        end_year: int,
        seen: Counter,
        unknown: Counter,
        ages: Counter,
        dropped_cols: set,
    ) -> bool:
        cols = list(chunk.columns)
        ind_c = _ci(cols, "indicator")
        iso_c = _ci(cols, "iso3")
        mod_c = _ci(cols, "modality")
        age_c = _ci(cols, "coarse age")
        ou_c = _ci(cols, "operating unit")
        years = year_columns(cols)
        # a MER file without a modality column, or without the wide year columns, is one of the
        # other Spotlight datasets and is not this connector's
        if not (ind_c and iso_c and mod_c and years):
            return False

        seen.update(chunk[ind_c].dropna().astype(str))
        # a target is what PEPFAR planned to do, not what it did, so the Targets columns are
        # named here and dropped rather than left unmentioned
        dropped_cols.update(c for c in cols if _YEAR_TARGET.match(str(c).strip()))

        sub = chunk[chunk[ind_c].isin(MER_INDICATORS)]
        for _, r in sub.iterrows():
            iso3 = to_iso3(r[iso_c])
            if not iso3 or (wanted and iso3 not in wanted):
                continue
            arm, label = classify(r[mod_c])
            if arm == UNCLASSIFIED and label not in UNCLASSIFIED_MODALITIES:
                unknown[label] += 1
            if age_c:
                ages[str(r[age_c]).strip()] += 1
            base = MER_INDICATORS[r[ind_c]]
            for year, qcols in years.items():
                if year < start_year or year > end_year:
                    continue
                qs = [_num(r[c]) if c else None for c in qcols]
                if all(q is None for q in qs):
                    continue
                key = (iso3, base, arm, year)
                cur = agg.setdefault(key, [None, None, None, None])
                for i, q in enumerate(qs):
                    if q is not None:
                        cur[i] = (cur[i] or 0.0) + q
                if label:
                    labels.setdefault(key, Counter())[label] += 1
            if "Country" in cols:
                names[iso3] = str(r["Country"]).strip()
            if ou_c:
                ous[iso3] = str(r[ou_c]).strip()
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
            log.warning("pepfar_modality: %s does not exist — download the Spotlight ZIPs from "
                        "data.pepfar.gov", self.raw_dir)
            return
        files = sorted(list(self.raw_dir.glob("*.zip")) + list(self.raw_dir.glob("*.txt"))
                       + list(self.raw_dir.glob("*.csv")))
        mine = [f for f in files if "modality" in f.name.lower()]
        if not mine:
            log.warning("pepfar_modality: no modality file in %s — nothing to split", self.raw_dir)
            return
        # A zip and its own extracted .txt sitting side by side would be read as two datasets and
        # every number would silently double, because this connector accumulates rather than
        # replaces. The archive wins and the loose copy is named and skipped.
        zipped = {f.stem for f in mine if f.suffix == ".zip"}
        dupes = [f for f in mine if f.suffix != ".zip" and f.stem in zipped]
        if dupes:
            log.info("pepfar_modality: skipping %s — already read from the matching .zip, and "
                     "reading both would double every count.", [f.name for f in dupes])
            mine = [f for f in mine if f not in dupes]
        log.info("pepfar_modality: reading %d of %d file(s) in %s. Not read: %s",
                 len(mine), len(files), self.raw_dir,
                 [f.name for f in files if f not in mine])

        agg: Dict[tuple, List[Optional[float]]] = {}
        names: Dict[str, str] = {}
        ous: Dict[str, str] = {}
        labels: Dict[tuple, Counter] = {}
        seen: Counter = Counter()
        unknown: Counter = Counter()
        ages: Counter = Counter()
        dropped_cols: set = set()

        for path in mine:
            used = False
            try:
                if path.suffix == ".zip":
                    with zipfile.ZipFile(path) as z:
                        for member in [m for m in z.namelist() if m.lower().endswith(".txt")]:
                            with z.open(member) as fh:
                                for chunk in pd.read_csv(fh, sep="\t", dtype=str, chunksize=50_000,
                                                         on_bad_lines="skip", low_memory=False):
                                    if self._process(chunk, agg, names, ous, labels, wanted,
                                                     start_year, end_year, seen, unknown, ages,
                                                     dropped_cols):
                                        used = True
                                    else:
                                        break
                else:
                    sep = "\t" if path.suffix == ".txt" else ","
                    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=50_000,
                                             on_bad_lines="skip", low_memory=False):
                        if self._process(chunk, agg, names, ous, labels, wanted,
                                         start_year, end_year, seen, unknown, ages,
                                         dropped_cols):
                            used = True
                        else:
                            break
            except Exception as exc:
                log.warning("pepfar_modality: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_modality: %s %s", path.name,
                     "(used)" if used else "(skipped — no modality column)")

        # what was read, what was declared out of scope, what nobody has decided about
        read = [c for c in seen if c in MER_INDICATORS]
        declared = [c for c in seen if c in DECLARED_UNMAPPED and c not in MER_INDICATORS]
        undecided = sorted(c for c in seen
                           if c not in MER_INDICATORS and c not in DECLARED_UNMAPPED)
        log.info("pepfar_modality: split %d of %d MER codes, %d deliberately left alone, "
                 "%d awaiting a decision", len(read), len(seen), len(declared), len(undecided))
        for code in undecided:
            log.warning("pepfar_modality: no rule covers MER code %s (%s rows). Add it to "
                        "MER_INDICATORS or to DECLARED_UNMAPPED with a reason.",
                        code, f"{seen[code]:,}")
        for label, n in unknown.most_common():
            log.warning("pepfar_modality: modality %r is in neither COMMUNITY_MODALITIES nor "
                        "FACILITY_MODALITIES (%s rows). Counted into the country total and into "
                        "neither arm. Classify it before reading the arm split for these rows.",
                        label, f"{n:,}")
        if dropped_cols:
            log.info("pepfar_modality: %d target column(s) read and dropped (%s). A target is "
                     "what PEPFAR planned to do, not what it did, and this panel holds results.",
                     len(dropped_cols), ", ".join(sorted(dropped_cols)))
        if ages:
            log.info("pepfar_modality: age and sex collapsed away. Coarse Age values read: %s. "
                     "Keeping them needs the age_group column decision, which is still open.",
                     dict(ages))

        yield from self._emit(agg, names, ous, labels)

    def _emit(self, agg, names, ous, labels) -> Iterator[PanelRow]:
        # the arms of one country-indicator-year, gathered so the total and the two arms are
        # emitted together and the unclassified remainder is visible on all three
        groups: Dict[tuple, Dict[str, List[Optional[float]]]] = {}
        for (iso3, base, arm, year), vals in agg.items():
            groups.setdefault((iso3, base, year), {})[arm] = vals

        def add(a: Optional[List[Optional[float]]], b: Optional[List[Optional[float]]]):
            if a is None:
                return list(b) if b else None
            if b is None:
                return list(a)
            return [None if (x is None and y is None) else (x or 0.0) + (y or 0.0)
                    for x, y in zip(a, b)]

        # totals first, because cadence is a property of the indicator-year and is read off the
        # series that carries the most countries
        totals: Dict[tuple, List[Optional[float]]] = {}
        for key, arms in groups.items():
            t = None
            for vals in arms.values():
                t = add(t, vals)
            if t is not None:
                totals[key] = t

        # Which quarters an indicator-year publishes, asked of the release rather than assumed.
        # FY2025 carries Q4 alone in this download, exactly as it does in the TopLine file, so a
        # rule counting to four would call every FY2025 row a part-published year. Same helper as
        # pepfar_panorama so the two connectors cannot drift apart on what a whole year means.
        cadence = _panorama.release_cadence(totals, lambda k: (k[1], k[2]))
        latest_year = max((y for _, y in cadence), default=0)

        n = 0
        like: Dict[tuple, List[float]] = {}
        for (iso3, base, year), arms in sorted(groups.items()):
            total = totals.get((iso3, base, year))
            if total is None:
                continue
            unclass = arms.get(UNCLASSIFIED)
            unclass_sum = sum(v for v in unclass if v is not None) if unclass else 0.0

            here = cadence.get((base, year), [])
            prev_cad = cadence.get((base, year - 1)) or here
            truncated, same_span = _panorama.span_status(here, prev_cad, year, latest_year)

            for canonical, vals in (
                (base, total),
                (f"{base}_{COMMUNITY}", arms.get(COMMUNITY)),
                (f"{base}_{FACILITY}", arms.get(FACILITY)),
            ):
                if vals is None:
                    continue
                nn = [v for v in vals if v is not None]
                if not nn:
                    continue
                value = sum(nn)
                nq = len(nn)
                arm = canonical[len(base) + 1:] or "total"

                prev_vals = (totals.get((iso3, base, year - 1)) if arm == "total"
                             else agg.get((iso3, base, arm, year - 1)))
                extra: Dict[str, object] = {
                    "note": "PEPFAR MER — PROGRAM FOOTPRINT, not national totals",
                    "testing_arm": arm,
                    "grain": "country level, published by PEPFAR as a country row",
                    "quarters_reported": nq,
                    "age_sex_collapsed": "Coarse Age and Sex summed away; the 15+, <15 and "
                                         "Unknown Age bands are a partition, so the sum is exact",
                    "interpretation": INTERPRETATION,
                }
                if ous.get(iso3):
                    extra["operating_unit"] = ous[iso3]
                if arm == "total":
                    # the reason this connector emits a series pepfar_panorama already emits
                    extra["why_a_second_total"] = (
                        "PEPFAR publishes this country row directly, while pepfar_panorama adds "
                        "up the partners it names. The two agree to a median ratio of exactly "
                        "1.000000 over 415 country-years, and part company where PEPFAR runs a "
                        "country through a regional operating unit and names few partners. "
                        "Filter on source_id before summing.")
                else:
                    mods = labels.get((iso3, base, arm, year)) or Counter()
                    if mods:
                        extra["modalities"] = sorted(mods)
                if unclass_sum:
                    extra["unclassified_tests"] = unclass_sum
                    extra["unclassified_note"] = (
                        f"{unclass_sum:,.0f} of this country-year carries the modality label "
                        f"'Not Specified', which is counted into the country total and into "
                        f"neither arm. The community and facility series therefore do NOT add "
                        f"to the total here, and the arm split for this country-year should not "
                        f"be read as a share.")

                extra.update(_panorama.quarter_detail(vals, prev_vals, year, same_span))
                lq = (extra.get("like_quarter_comparison") or {}).get("ratio")
                if lq:
                    like.setdefault((canonical, year), []).append(lq)
                extra["release_quarters"] = [f"Q{q}" for q in here]
                extra["comparison_year_quarters"] = [f"Q{q}" for q in prev_cad]
                if truncated or 0 < nq < len(here):
                    why = (f"FY{year} is part-published, carrying "
                           f"{', '.join('Q%d' % q for q in here)} where FY{year - 1} carries "
                           f"{', '.join('Q%d' % q for q in prev_cad)}" if truncated else
                           f"this series reported {nq} of the "
                           f"{', '.join('Q%d' % q for q in here)} that FY{year} publishes")
                    extra["partial_year"] = (
                        f"{why}. This annual total covers less of the year than the total it "
                        f"would be compared with, so it is a PARTIAL sum and must not be read "
                        f"as a decline. Use like_quarter_comparison instead.")

                yield self.make_row(
                    country_iso3=iso3, country_name=names.get(iso3, ""),
                    indicator_id=canonical, year=year, value=value, unit="count",
                    source_url="https://data.pepfar.gov/datasets",
                    source_indicator_code="MER (country level, by modality)",
                    extra=extra,
                )
                n += 1

        # the comparison that survives a part-published year, one line per series whose quarters
        # moved. The two arms are meant to be read against each other here: the same cut shows as
        # the community ratio falling while the facility ratio holds.
        for (canonical, year), ratios in sorted(like.items()):
            ratios.sort()
            med = ratios[len(ratios) // 2]
            log.info("pepfar_modality: %s FY%d — quarters differ from FY%d, so the annual totals "
                     "are not comparable. Like-quarter median %.2f over %d countries, below 1.0 "
                     "in %d of them.", canonical, year, year - 1, med, len(ratios),
                     len([r for r in ratios if r < 1.0]))
        log.info("pepfar_modality: emitted %d rows", n)
