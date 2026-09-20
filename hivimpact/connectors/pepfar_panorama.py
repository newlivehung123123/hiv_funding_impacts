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

   How many quarters make a whole year is asked of the release (`release_cadence`) and not
   assumed, because reporting frequency turned out to be a property of the indicator AND the
   year rather than of the indicator alone. TB_STAT and TB_STAT_POS published at Q2 and Q4 in
   FY2018 and quarterly from FY2019, PrEP_NEW at Q2 and Q4 through FY2020 and quarterly from
   FY2021, and TB_PREV and KP_PREV at Q2 and Q4 throughout. Counting to a fixed four put a
   false partial-year warning on 93 operating-unit-years whose totals are complete, being
   PrEP_NEW in FY2019 and FY2020 and TB_STAT and TB_STAT_POS in FY2018.

   A semi-annual report covers six months rather than three, so a two-quarter year is a WHOLE
   year. Across the FY2018 to FY2019 change the full-year ratios are 0.99 for TB_STAT and 0.96
   for TB_STAT_POS, while comparing FY2019's Q2 and Q4 alone against FY2018 gives 0.53 and
   0.49. So a year publishing fewer quarters than the year before it is only short when the
   release itself stopped early, which `span_status` decides and which can only be true of the
   newest fiscal year in the download.

2. **Reporting-scope discontinuities** (`extra.data_quality_flag`) — a >3x year-on-year jump.
   E.g. Thailand FY2025 `on_art_count` 53,330 -> 260,981: the SAME three partners, but the
   government ones (MOPH 25k->185k, BMA 11k->76k) began reporting their full national
   caseload while the USAID partner collapsed (FHI 17,363 -> 207, a genuine funding-cut
   signal). The country total is not comparable across that boundary; the partner-level
   detail is where the real signal lives.

Neither flag alters the source value — we surface the problem and let the analyst decide.

THE THREE INDICATORS THIS CONNECTOR WAS NOT READING (found 2026-09-05)

The TopLine file holds 71 MER indicators and this connector read two of them for eight
months. Every log line stayed clean and the row count never fell, because a connector that
never asks for an indicator has nothing to report about the indicator. The coverage audit in
`scripts/audit_coverage.py` is what surfaced the gap, and the audit exists to be run again.

One of the 69 unread codes was TX_NEW, the count of people newly started on antiretroviral
therapy, which is the indicator this whole project was built to measure. TX_NEW carries the
same coverage as TX_CURR in the same file, 57 countries and fiscal years 2018 to 2025, so the
series cost one dictionary entry. Before the entry was written the pairing was tested against
the WHO TME national totals already in the panel, because PEPFAR measures a programme
footprint and a programme footprint that exceeded the national total would mean the pairing
was wrong. Across the 266 overlapping country-years PEPFAR sits at or below the national
total in 86 per cent of them and takes a median share of 0.74, which is the shape a
programme footprint should have. The 15 country-years above 1.25 are led by Mali 2020 at 5.19
and Uganda 2019 at 1.98, and PEPFAR's October to September fiscal year against WHO's calendar
year explains part of the excess. TX_NEW also covers 88 country-years across 38 countries
where WHO TME publishes no initiation figure at all.

TX_NEW, HTS_TST and PrEP_NEW are all period flows, so each annual value is the sum of the
quarters and each inherits the partial-year flag above. The quarters were checked and they
are independent periods rather than a running total, because FY2024 TX_NEW reads 390,160 in
Q1 and 464,878 in Q4 rather than roughly four times the first quarter.

SIX MORE, MAPPED ONTO CANONICALS THAT WERE ALREADY WAITING (2026-09-05)

Running the audit a second time showed that the 66 codes left over were not 66 codes needing new
canonical indicators. Ten of the largest already had a canonical sitting in the registry, put
there by other sources, so the panel had a name for the quantity and no PEPFAR measurement under
it. Six of the ten could be paired on the arithmetic alone and are now read:

    TX_PVLS     -> viral_suppression_count    393 of 399 country-years are ones no other source
                                              in the panel covers at all
    TB_PREV     -> tpt_completions            250 of 252 country-years are new
    TB_STAT     -> tb_patients_hiv_tested     median 0.58 of the WHO TME national figure over
                                              201 overlaps, at or below it in 96 per cent
    TB_STAT_POS -> tb_patients_hiv_positive   median 0.77 over 197 overlaps, below in 93 per cent
    PMTCT_ART   -> pmtct_arv_count            median 0.75 to 0.81 against three separate national
                                              sources, below each in 91 to 93 per cent
    VMMC_CIRC   -> circumcisions_performed    median 0.91 over 98 overlaps

Exact agreement with the national series is 0.0 per cent for five of the six and 1.0 per cent for
VMMC_CIRC, so none of them is a national series reprinted under a PEPFAR label. Every one sits at
or below the national total in the large majority of country-years, which is the shape a
programme footprint has to have, and the departures above 1.0 are concentrated where PEPFAR's
October to September fiscal year straddles two calendar years.

TX_PVLS is the one that would have been silently wrong. Summed across quarters it reaches a
median of 2.32 times TX_CURR and exceeds the treatment cohort in 70 per cent of country-years,
which cannot happen. TX_PVLS restates a rolling twelve months every quarter, so it is a snapshot,
and read at the latest quarter the median is 0.71.

The remaining codes are all named in DECLARED_UNMAPPED with the reason each is left alone. Most
are parts of a code already read, and adding a part alongside its whole double counts. The rest
need a canonical definition rather than a dictionary entry, TX_ML and TX_RTT among them, or sit
outside HIV testing and treatment altogether, as cervical cancer screening and post-violence care
do. KP_PREV is the interesting refusal: summing its two half-years and taking the later one
differ by a factor of two against the Global Fund national figure, and no arithmetic decides
which reading PEPFAR intends.

TAGGING: PEPFAR MER measures the PEPFAR program footprint, NOT national totals.
source_type = routine_programme_record.
"""
from __future__ import annotations

import logging
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

MER_INDICATORS = {
    "TX_CURR": "on_art_count",
    "HTS_TST_POS": "new_diagnoses",
    "TX_NEW": "art_initiations",
    "HTS_TST": "hiv_tests_performed",
    "PrEP_NEW": "prep_recipients",
    "TX_PVLS": "viral_suppression_count",
    "TB_PREV": "tpt_completions",
    "TB_STAT": "tb_patients_hiv_tested",
    "TB_STAT_POS": "tb_patients_hiv_positive",
    "PMTCT_ART": "pmtct_arv_count",
    "VMMC_CIRC": "circumcisions_performed",
}
# annual = the latest quarter reported, never a sum. TX_PVLS belongs here and the arithmetic is
# what says so. TX_PVLS counts people on ART with a suppressed viral load result documented in
# the preceding twelve months, so each quarter restates a rolling year rather than adding a new
# period to it. Summed across quarters TX_PVLS reaches a median of 2.32 times TX_CURR and exceeds
# the treatment cohort in 70 per cent of country-years, which cannot happen, because a person
# with a suppressed result is by definition a person on treatment. Read at the latest quarter the
# median is 0.71 and the excess appears in 1 per cent.
SNAPSHOT = {"TX_CURR", "TX_PVLS"}
# canonicals whose annual value is a SUM of quarters — for these a part-reported year yields a
# PARTIAL total that must never be read as a real decline (e.g. FY2025 has only 1 of 4 quarters).
CUMULATIVE_CANON = {MER_INDICATORS[k] for k in MER_INDICATORS if k not in SNAPSHOT}

# Codes PEPFAR publishes twice a year rather than four times. TB_PREV reports Q2 and Q4 in 204 of
# its 258 country-years and KP_PREV in 304 of 362, so two quarters is a COMPLETE year for these
# and not a partial one. Kept as a record of the finding and as a check on the derived cadence,
# but NOT used to decide whether a year is complete. Frequency turned out to be a property of the
# code AND the year rather than of the code alone: TB_STAT and TB_STAT_POS published at Q2 and Q4
# in FY2018 and quarterly from FY2019, PrEP_NEW at Q2 and Q4 through FY2020 and quarterly from
# FY2021, and no fixed list can hold that. release_cadence() asks the release instead.
SEMI_ANNUAL = {"TB_PREV", "KP_PREV"}
SEMI_ANNUAL_CANON = {MER_INDICATORS[k] for k in SEMI_ANNUAL if k in MER_INDICATORS}

# How far a national total may sit from the geographic file's figure before the row carries the
# geographic figure beside it. Five per cent is the tolerance every section 9f comparison in this
# project uses. On the download of 2026-07-18 the count of rows above the geographic file falls
# from 335 past 0.5 per cent to 222 past 2 per cent and 157 past 5 per cent, so the choice moves
# the count and a reader wanting a tighter test can recompute from geographic_value.
GEO_TOLERANCE = 0.05

# Every other code in the TopLine file, with the reason this connector leaves the code alone.
# The audit in scripts/audit_coverage.py subtracts this list before reporting a gap, so a code
# named here is a decision on the record and a code named nowhere is a decision nobody has made.
# The reason matters more than the entry: "not mapped" invites the same code to be looked at
# again every few months, while "the parts sum to a whole this connector already reads" ends it.
DECLARED_UNMAPPED: Dict[str, str] = {
    # A part of something this connector already reads. Adding the part alongside the whole
    # counts the same people twice. Each share below was measured on this download.
    "HTS_TST_NEG": "part of HTS_TST, which this connector reads (POS + NEG sum to HTS_TST in "
                   "99% of 415 country-years)",
    "TB_STAT_POS_NewlyIdentified_Positive": "part of TB_STAT_POS, which this connector reads "
                                            "(the two positive legs sum to it in 100% of 189)",
    "TB_STAT_POS_KnownAtEntry_Positive": "part of TB_STAT_POS, which this connector reads",
    "TB_STAT_NEG_NewlyIdentified_Negative": "part of TB_STAT, which this connector reads (the "
                                            "positive and negative legs sum to it in 100% of 43)",
    "TB_STAT_NEG_Recent_Negative": "part of TB_STAT, which this connector reads",
    "TX_CURR_ARVDisp_less_three_mo": "multi-month dispensing split of TX_CURR, which this "
                                     "connector reads (the three legs sum to TX_CURR in 71% of "
                                     "304 country-years and never exceed it)",
    "TX_CURR_ARVDisp_three_five_mo": "multi-month dispensing split of TX_CURR",
    "TX_CURR_ARVDisp_six_more_mo": "multi-month dispensing split of TX_CURR",

    # A part of something this connector does NOT read. A fragment carrying a whole-sounding
    # name is worse than a gap, because a gap is visible and a fragment is not.
    "TX_ML_died": "part of TX_ML, which is itself left for a decision below",
    "TX_ML_transferred_out": "part of TX_ML, which is itself left for a decision below",
    "TX_ML_refused_stopped": "part of TX_ML, which is itself left for a decision below",
    "TX_ML_IIT_less_three_mo": "part of TX_ML, which is itself left for a decision below",
    "TX_ML_IIT_three_five_mo": "part of TX_ML, which is itself left for a decision below",
    "TX_ML_IIT_six_more_mo": "part of TX_ML, which is itself left for a decision below",
    "TX_ML_IIT_more_three_mo": "part of TX_ML, which is itself left for a decision below",
    "PMTCT_EID_Less_Equal_Two_Months": "age split of PMTCT_EID, which is left for a decision",
    "PMTCT_EID_Two_Twelve_Months": "age split of PMTCT_EID, which is left for a decision",
    "HTS_INDEX_NEWPOS": "outcome split of HTS_INDEX, which is left for a decision",
    "HTS_INDEX_NEWNEG": "outcome split of HTS_INDEX, which is left for a decision",
    "HTS_INDEX_KNOWNPOS": "outcome split of HTS_INDEX, which is left for a decision",
    "PMTCT_STAT_POS": "positive leg of PMTCT_STAT, which is left for a decision",
    "PMTCT_HEI_POS": "outcome split of PMTCT_HEI, which is left for a decision",
    "PMTCT_HEI_NEG": "outcome split of PMTCT_HEI, which is left for a decision",
    "PMTCT_HEI_POS_ART": "outcome split of PMTCT_HEI, which is left for a decision",
    "PMTCT_HEI_POS_2MO": "outcome split of PMTCT_HEI, which is left for a decision",
    "TX_TB_D_POS": "denominator leg of TX_TB, which is left for a decision",
    "TX_TB_D_NEG": "denominator leg of TX_TB, which is left for a decision",

    # The canonical exists but is a PERCENTAGE, and this connector reads Total Numerator rows
    # only. Pairing these needs the Denominator leg of the same code, which is a change to how
    # the file is read rather than a dictionary entry, so the change is not made in passing.
    "PMTCT_STAT": "pairs with anc_hiv_testing_pct, a percentage; needs the Denominator rows this "
                  "connector filters out",
    "PMTCT_EID": "pairs with early_infant_diagnosis_pct, a percentage; needs the Denominator rows",
    "TX_TB": "pairs with plhiv_new_tb_diagnosed_pct, a percentage; needs the Denominator rows",

    # No canonical exists, and writing one is a definition rather than a dictionary entry. Each
    # of these measures something the panel has no name for yet.
    "TX_ML": "people who left treatment. Equals the sum of its seven sub-codes to within 1% "
             "across 177 country-years, so mapping TX_ML alone would be correct. Needs a "
             "canonical definition first",
    "TX_RTT": "people who returned to treatment after an interruption. Needs a canonical",
    "TX_NET_NEW": "change in the treatment cohort between quarters, a derived difference rather "
                  "than a count of people. Needs a canonical and a decision about signs",
    "TX_RET": "retention on treatment at a fixed interval. Needs a canonical",
    "TB_ART": "TB patients already on antiretroviral therapy. Distinct from "
              "tb_patients_hiv_positive, which counts status not treatment. Needs a canonical",
    "PMTCT_FO": "final outcome of exposed infants. Needs a canonical",
    "PMTCT_HEI": "HIV-exposed infants. Needs a canonical",
    "HTS_INDEX": "contacts of a diagnosed person offered testing. Needs a canonical, and the "
                 "three outcome legs sum to it in only 33% of 332 country-years, so the parent "
                 "and the parts are not the same population",
    "HTS_SELF": "self-test kits distributed. Needs a canonical",
    "HTS_RECENT": "tests classified as recent infection. Needs a canonical",
    "PrEP_CURR": "people currently on pre-exposure prophylaxis. Distinct from PrEP_NEW, which "
                 "this connector reads as prep_recipients. Needs its own canonical",
    "PrEP_CT": "PrEP continuation. Needs a canonical",
    "KP_MAT": "medication-assisted therapy for opioid dependence. Needs a canonical",
    "AGYW_PREV": "adolescent girls and young women reached by DREAMS. Needs a canonical",
    "PP_PREV": "priority populations reached with prevention. Needs a canonical",
    # KP_PREV is the one candidate that failed on arithmetic rather than on vocabulary, and the
    # failure is worth recording because the code otherwise looks ready to map. KP_PREV reports
    # Q2 and Q4 and counts individuals reached within each half-year, deduplicated inside the
    # half and not across it. Summing the halves gives a median of 0.58 of the Global Fund
    # national figure over 142 overlapping country-years; taking the later half alone gives 0.29.
    # A factor of two between two defensible readings is not something arithmetic can settle, and
    # PEPFAR's own guidance has to. TB_PREV is mapped despite the same reporting pattern because
    # completing a course of preventive therapy is an event and events add, while being reached
    # is a status and the same person is reached in both halves of a year as a matter of course.
    "KP_PREV": "key populations reached with prevention. Summing the two half-years and taking "
               "the later one differ by a factor of two and both are defensible; the choice "
               "needs PEPFAR's definition, not this connector's arithmetic",

    # Services PEPFAR funds that sit outside the HIV testing and treatment cascade this panel
    # measures. A funding cut reaches them too, and a panel that measured them would be a
    # different panel with a different denominator for every comparison in it.
    "CXCA_SCRN": "cervical cancer screening, outside the HIV cascade this panel measures",
    "CXCA_SCRN_POS": "cervical cancer screening, outside the HIV cascade",
    "CXCA_TX": "cervical cancer treatment, outside the HIV cascade",
    "POST_RESP": "post-violence care, outside the HIV cascade",
    "POST_RESP_SexualViolence": "post-violence care, outside the HIV cascade",
    "POST_RESP_PhysicalEmotionalViolence": "post-violence care, outside the HIV cascade",
    "OVC_SERV": "orphans and vulnerable children services, outside the HIV cascade",
    "OVC_SERV_UNDER_18": "orphans and vulnerable children services, outside the HIV cascade",
    "OVC_SERV_OVER_18": "orphans and vulnerable children services, outside the HIV cascade",
    "OVC_SERV_ACTIVE": "orphans and vulnerable children services, outside the HIV cascade",
    "OVC_SERV_GRADUATED": "orphans and vulnerable children services, outside the HIV cascade",
    "OVC_HIVSTAT": "HIV status of children in OVC programmes, outside the HIV cascade",
    "OVC_HIVSTAT_POS": "HIV status of children in OVC programmes, outside the HIV cascade",
    "OVC_HIVSTAT_NEG": "HIV status of children in OVC programmes, outside the HIV cascade",
}


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


def _reported_quarters(vals: List[Optional[float]]) -> List[int]:
    """The quarters (1-4) that carry a number."""
    return [i + 1 for i, v in enumerate(vals) if v is not None]


def release_cadence(agg: Dict[tuple, List[Optional[float]]], group) -> Dict[tuple, List[int]]:
    """The quarters an indicator-year is published at, taken from the release rather than assumed.

    PEPFAR changes how often an indicator reports. TB_STAT and TB_STAT_POS published at Q2 and
    Q4 in FY2018 and quarterly from FY2019, PrEP_NEW published at Q2 and Q4 through FY2020 and
    quarterly from FY2021, and the whole FY2025 download carries Q4 alone. A rule that expects
    four quarters calls every one of those a part-reported year, which put a warning on 101
    country-years whose totals are in fact complete, and a rule that expects two for a named
    list of codes only moves the same mistake elsewhere.

    So the release is asked. The quarter set most countries report for an indicator-year is what
    that indicator-year publishes at. Ties go to the fuller pattern, because expecting more
    quarters than a year publishes only ever adds a caution and never removes one.
    """
    counts: Dict[tuple, Counter] = {}
    for key, vals in agg.items():
        qs = tuple(_reported_quarters(vals))
        if qs:
            counts.setdefault(group(key), Counter())[qs] += 1
    return {g: list(max(c.items(), key=lambda kv: (kv[1], len(kv[0])))[0]) for g, c in counts.items()}


def span_status(here: List[int], prev_cad: List[int], year: int,
                latest_year: int) -> tuple:
    """Whether an indicator-year is a part-published release, and whether each of its
    quarterly reports covers the same months as the comparison year's.

    A year publishing fewer quarters than the year before it has two possible causes, and
    telling them apart decides which comparison is honest.

    The year is TRUNCATED when the rest of it has not been released yet, which can only be
    true of the newest fiscal year in the download. Each report still covers three months,
    so the year is genuinely short and only the shared quarters can be compared.

    Otherwise PEPFAR changed how often the indicator reports. A semi-annual report covers
    six months rather than three, so a two-quarter year is a WHOLE year and the annual
    totals stay comparable while a quarter-by-quarter comparison does not.

    A cadence change in the newest year cannot be separated from truncation by arithmetic,
    since both look like fewer quarters with no later year to check against. Truncation is
    the reading taken, because a download collected part-way through a fiscal year meets it
    far more often.
    """
    truncated = year == latest_year and 0 < len(here) < len(prev_cad)
    return truncated, truncated or set(here) == set(prev_cad)


def quarter_detail(vals: List[Optional[float]], prev_vals: Optional[List[Optional[float]]],
                   year: int, same_span: bool) -> Dict[str, object]:
    """The quarters behind one cumulative annual total, and the honest comparison with the
    year before.

    Summing quarters into a year throws the quarters away, and a reader holding only the annual
    total cannot tell a year that published four quarters from a year that published one. So the
    quarters are kept on the row, and the comparison that holds is named.

    WHICH comparison holds depends on whether a report in this year covers the same months as
    a report in the year before, which span_status decides and passes in as same_span.

    When the two years report at the same frequency, one quarter means three months in both,
    so the shared quarters are twelve months apart and comparing them is right. FY2025 in this
    download carries Q4 alone, and that Q4 is the same three months FY2024's Q4 covered.

    When PEPFAR changed the frequency, a semi-annual report covers six months rather than
    three, the two-quarter year is a WHOLE year, and the annual totals are what compare. Two
    independent measurements in this download say so.

    TB_STAT and TB_STAT_POS moved from Q2 and Q4 to quarterly at FY2019. Their full-year
    ratios across that change are 0.99 and 0.96, which is a flat service holding flat, while
    comparing FY2019's Q2 and Q4 alone against FY2018 gives 0.53 and 0.49, which is the same
    service apparently halving.

    PrEP_NEW moved the other way at FY2019, from quarterly to Q2 and Q4, and grew steeply
    throughout, so a raw ratio says nothing on its own. The two ratios share that growth and
    the comparison between them still does: the full-year ratio is 3.10 and the Q2+Q4 ratio is
    6.05, a factor of 1.95. Six months against three. Had a semi-annual report covered three
    months, the two ratios would have agreed.

    That reading is inferred from the arithmetic in this download rather than read off PEPFAR
    documentation, so it is stated on the row.
    """
    qs = _reported_quarters(vals)
    detail: Dict[str, object] = {"quarters": {f"Q{q}": vals[q - 1] for q in qs}}
    if prev_vals is None:
        return detail
    prev_qs = _reported_quarters(prev_vals)
    if not prev_qs or set(qs) == set(prev_qs):
        return detail
    if not same_span:
        detail["cadence_change"] = (
            f"FY{year} reports {', '.join('Q%d' % q for q in qs)} where FY{year - 1} reports "
            f"{', '.join('Q%d' % q for q in prev_qs)}. This is a change of reporting frequency "
            f"and not a short year: a semi-annual report covers six months rather than three, so "
            f"both annual totals cover a whole year and can be compared. Do NOT compare the two "
            f"years quarter by quarter, which would put 12 months against six."
        )
        return detail
    shared = [q for q in qs if q in prev_qs]
    if not shared:
        detail["like_quarter_comparison"] = {
            "note": (f"FY{year} reports {', '.join('Q%d' % q for q in qs)} and FY{year - 1} "
                     f"reports {', '.join('Q%d' % q for q in prev_qs)}. The two years share no "
                     f"quarter, so no like-for-like comparison can be made between them."),
        }
        return detail
    now = sum(vals[q - 1] for q in shared)
    then = sum(prev_vals[q - 1] for q in shared)
    detail["like_quarter_comparison"] = {
        "quarters": [f"Q{q}" for q in shared],
        "this_year": now,
        "last_year": then,
        "ratio": round(now / then, 4) if then else None,
        "note": (f"FY{year} and FY{year - 1} do not report the same quarters at the same "
                 f"frequency, so their annual totals cover different spans and are not "
                 f"comparable. These figures cover {', '.join('Q%d' % q for q in shared)} in "
                 f"both years, which is the comparison to use instead."),
    }
    return detail


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
                 wanted, start_year: int, end_year: int,
                 seen: Optional[Counter] = None) -> bool:
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

        # Every code the file contains, counted before the dictionary narrows the rows. A
        # connector that only ever looks at the codes it already knows cannot report the codes
        # it does not, which is the whole of how 69 of these sat unread for eight months.
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
        # Name the discarded files rather than only the kept one. A log line that reports what a
        # connector used tells a reader nothing about what the connector threw away, which is
        # how 12 PEPFAR archives sat unopened for eight months without a single warning.
        topline = [f for f in files if "topline" in f.name.lower()]
        if topline:
            dropped = [f.name for f in files if f not in topline]
            log.info("pepfar_panorama: using TopLine totals file(s) only: %s", [f.name for f in topline])
            if dropped:
                log.info("pepfar_panorama: %d other file(s) in %s not read by this connector: %s",
                         len(dropped), self.raw_dir, dropped)
            files = topline

        agg: Dict[tuple, List[Optional[float]]] = {}
        names: Dict[str, str] = {}
        partner_q: Dict[tuple, Dict[str, List[Optional[float]]]] = {}
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
                                    if self._process(chunk, agg, names, partner_q, wanted,
                                                     start_year, end_year, seen):
                                        used = True
                                    else:
                                        break
                else:
                    sep = "\t" if path.suffix == ".txt" else ","
                    for chunk in pd.read_csv(path, sep=sep, dtype=str, chunksize=200_000,
                                             on_bad_lines="skip", low_memory=False):
                        if self._process(chunk, agg, names, partner_q, wanted,
                                         start_year, end_year, seen):
                            used = True
                        else:
                            break
            except Exception as exc:
                log.warning("pepfar_panorama: error reading %s: %s", path.name, exc)
                continue
            log.info("pepfar_panorama: %s %s", path.name, "(used)" if used else "(skipped — not long MER format)")

        # What was read, what was left alone on purpose, and what nobody has decided about. The
        # third number is the only one that needs anyone's attention, and a code reaching it is
        # new in the download rather than overlooked, because the other 71 are all accounted for.
        if seen:
            read = sorted(c for c in seen if c in MER_INDICATORS)
            declared = sorted(c for c in seen if c in DECLARED_UNMAPPED and c not in MER_INDICATORS)
            undecided = sorted(c for c in seen
                               if c not in MER_INDICATORS and c not in DECLARED_UNMAPPED)
            log.info("pepfar_panorama: read %d of %d MER codes, %d deliberately left alone, "
                     "%d awaiting a decision", len(read), len(seen), len(declared), len(undecided))
            for code in undecided:
                log.warning("pepfar_panorama: no rule covers MER code %s (%s rows). Add it to "
                            "MER_INDICATORS or to DECLARED_UNMAPPED with a reason.",
                            code, f"{seen[code]:,}")

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

        # How often each indicator reported in each year, read off the release. A change of
        # cadence is announced, because a year that publishes twice sitting next to a year that
        # publishes four times is the single easiest way to read a cut that did not happen.
        cadence = release_cadence(agg, lambda k: (k[1], k[2]))
        # The newest fiscal year in the download, which is the only year whose missing
        # quarters can be a release that has not finished rather than a change of frequency.
        latest_year = max((y for _, y in cadence), default=0)
        for (canonical, year), qs in sorted(cadence.items()):
            was = cadence.get((canonical, year - 1))
            if not was or was == qs:
                continue
            if year == latest_year and len(qs) < len(was):
                log.warning("pepfar_panorama: %s FY%d is PART-PUBLISHED, carrying %s where "
                            "FY%d carries %s. Every cumulative total for FY%d is a partial "
                            "sum and a fall against FY%d is an artefact of the release.",
                            canonical, year, ", ".join(f"Q{q}" for q in qs), year - 1,
                            ", ".join(f"Q{q}" for q in was), year, year - 1)
            else:
                log.info("pepfar_panorama: %s changed reporting frequency at FY%d, from %s in "
                         "FY%d to %s. A semi-annual report covers six months rather than "
                         "three, so the annual totals stay comparable across that year while "
                         "a quarter-by-quarter comparison does not.", canonical, year,
                         ", ".join(f"Q{q}" for q in was), year - 1,
                         ", ".join(f"Q{q}" for q in qs))

        # The same national figure from PEPFAR's geographic file, which removes people two
        # partners both report. The TopLine file read above adds every mechanism without that
        # removal, so a TopLine total can sit above the geographic one, and Kazakhstan's TX_CURR
        # sits at exactly twice the geographic figure in every year from FY2021 to FY2025. A
        # TopLine total can also sit below it where TopLine is missing reporting that the
        # geographic file holds, as Thailand FY2018 HTS_TST does at 1,308 against 75,944. Values
        # are never replaced. A row more than GEO_TOLERANCE away carries the geographic figure
        # beside its own, in either direction (docs/ACCESS_LADDER.md section 9w).
        # Imported here and not at the top, because pepfar_snu imports this module at load.
        from .pepfar_agency import MER_INDICATORS as _AGENCY_CODES
        from .pepfar_snu import national_quarters
        geo = national_quarters(self.raw_dir, MER_INDICATORS, wanted, start_year, end_year)
        if geo is None:
            log.warning("pepfar_panorama: no Enhanced Geographical Analysis file in %s, so the "
                        "national totals are not checked against the geographic file this run",
                        self.raw_dir)
        code_of = {v: k for k, v in MER_INDICATORS.items()}
        agency_canon = set(_AGENCY_CODES.values())
        geo_off: Dict[str, List[str]] = {"above": [], "below": []}
        geo_checked = 0

        n = 0
        like: Dict[tuple, List[float]] = {}
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
            # What this indicator-year publishes at, and what the year before it published at.
            # Both come from the release rather than from a fixed count of four, which is what
            # stops the warning firing on TB_STAT in FY2018 and PrEP_NEW in FY2019 and FY2020,
            # where two quarters was the whole year those indicators then published.
            here = cadence.get((canonical, year), [])
            prev_cad = cadence.get((canonical, year - 1)) or here
            truncated, same_span = span_status(here, prev_cad, year, latest_year)
            extra["release_quarters"] = [f"Q{q}" for q in here]
            extra["quarters_expected"] = len(here)
            extra["comparison_year_quarters"] = [f"Q{q}" for q in prev_cad]
            if canonical in CUMULATIVE_CANON:
                extra.update(quarter_detail(
                    agg[key], agg.get((iso3, canonical, year - 1)), year, same_span))
                lq = (extra.get("like_quarter_comparison") or {}).get("ratio")
                if lq:
                    like.setdefault((canonical, year), []).append(lq)
            # A cumulative total is PARTIAL, and must never be read as a decline, in two
            # situations. Either the release itself stops early, which is FY2025 carrying Q4
            # alone and making new_diagnoses look like a 70-90% collapse in every country, or
            # this one country reported fewer quarters than its indicator-year publishes while
            # the countries around it reported all of them.
            if canonical in CUMULATIVE_CANON and (truncated or 0 < nq < len(here)):
                against = len(prev_cad) if truncated else len(here)
                why = (f"FY{year} is part-published, carrying "
                       f"{', '.join('Q%d' % q for q in here)} where FY{year - 1} carries "
                       f"{', '.join('Q%d' % q for q in prev_cad)}" if truncated else
                       f"this country reported {nq} of the "
                       f"{', '.join('Q%d' % q for q in here)} that FY{year} publishes")
                extra["partial_year"] = (
                    f"{why}. This annual total covers less of the year than the total it "
                    f"would be compared with, so it is a PARTIAL sum and must not be read as "
                    f"a decline. Use like_quarter_comparison instead."
                )
                log.warning("pepfar_panorama: %s %s %d — PARTIAL YEAR (%d quarter(s) against "
                            "%d); annual total is a partial sum, not a decline",
                            iso3, canonical, year, nq, against)
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
            # A snapshot is compared at the quarter this row was read at, which is not always the
            # geographic file's own latest quarter (five country-years differ), and a flow is
            # compared as the sum of whatever quarters the geographic file reports.
            gq = geo.get((iso3, code_of[canonical], year)) if geo else None
            if gq:
                if canonical in CUMULATIVE_CANON:
                    g_nn = [v for v in gq if v is not None]
                    g_value = sum(g_nn) if g_nn else None
                else:
                    g_value = gq[snap_q[key] - 1]
                if g_value:
                    geo_checked += 1
                    ratio = value / g_value
                    if abs(ratio - 1) > GEO_TOLERANCE:
                        above = ratio > 1
                        if above:
                            note = (f"PEPFAR's geographic file gives {g_value:,.0f} for this "
                                    f"country and year and this value is {ratio:.2f} times that "
                                    f"figure. The partner file this value comes from adds every "
                                    f"partner's count without removing the people two partners "
                                    f"both report, and the geographic file removes them, so "
                                    f"the geographic figure is the safer national total.")
                            if canonical in agency_canon:
                                note += (" The pepfar_agency rows split this same partner total "
                                         "by funding agency and carry the same excess.")
                        else:
                            note = (f"PEPFAR's geographic file gives {g_value:,.0f} for this "
                                    f"country and year and this value is {ratio:.2f} of that "
                                    f"figure. The partner file this value comes from is missing "
                                    f"reporting that the geographic file holds, so this value is "
                                    f"a floor for the PEPFAR programme, and a fall against "
                                    f"another year may be missing reporting and not missing "
                                    f"services.")
                        extra["geographic_total_differs"] = {
                            "geographic_value": g_value, "ratio": round(ratio, 4),
                            "direction": "above" if above else "below", "note": note}
                        geo_off["above" if above else "below"].append(f"{iso3} {canonical} {year}")
            yield self.make_row(
                country_iso3=iso3, country_name=names.get(iso3, ""),
                indicator_id=canonical, year=year, value=value, unit="count",
                source_url="https://data.pepfar.gov/datasets", source_indicator_code="MER",
                extra=extra,
            )
            n += 1
        # One line per indicator-year where the quarters do not match the year before, carrying
        # the comparison that holds. A part-reported year produces a warning on every country,
        # which tells a reader what not to do and leaves them without the number they wanted.
        for (canonical, year), ratios in sorted(like.items()):
            ratios.sort()
            med = ratios[len(ratios) // 2]
            log.info("pepfar_panorama: %s FY%d — quarters differ from FY%d, so the annual totals "
                     "are not comparable. Like-quarter median %.2f over %d countries, below 1.0 "
                     "in %d of them.", canonical, year, year - 1, med, len(ratios),
                     len([r for r in ratios if r < 1.0]))
        if geo is not None:
            for direction, rows in geo_off.items():
                countries = Counter(r.split()[0] for r in rows)
                log.warning("pepfar_panorama: %d of %d rows checked sit more than %d%% %s the "
                            "geographic file, flagged in extra.geographic_total_differs. By "
                            "country: %s", len(rows), geo_checked, round(GEO_TOLERANCE * 100),
                            direction, ", ".join(f"{c} {k}" for c, k in countries.most_common()))
        log.info("pepfar_panorama: emitted %d rows", n)
