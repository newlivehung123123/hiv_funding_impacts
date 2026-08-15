"""
ForeignAssistance.gov connector — US government's OWN reporting of HIV funding, by agency.

ForeignAssistance.gov is a JS app; its programmatic access is the "Complete Data Set"
bulk CSV download (obligations + disbursements by country/sector/agency/year, 2001-).
So this is a download-then-ingest connector (like UNAIDS): you download the complete
CSV into data/raw/foreign_assistance/ and this parses it.

Why it's in scope: it is the US's self-reported HIV disbursements by country, so it
TRIANGULATES the OECD-CRS US series (external_hiv_oda_us) against Washington's own
numbers — two independent measures of the same US money, which is exactly the funding
we're tracking cuts to.

MANAGING AGENCY, NOT FUNDING AGENCY

The file carries both, and they answer different questions. PEPFAR is appropriated to the
State Department's Global Health Programs account, so a split on **Funding Agency** puts
102bn USD under STATE and tells you nothing: it records which committee's account the money
came out of. **Managing Agency** records who spent it — USAID 72bn, HHS 43bn — and that is
the column that mirrors the USAID/CDC split already recovered on the PEPFAR service side
(`pepfar_agency`) and money side (`pepfar_expenditure`). Within HHS the sub-agency column
separates CDC (38.5bn) from NIH (3.3bn) and HRSA (1.3bn), so `_cdc` here means CDC and not
all of HHS, which is what PEPFAR's own "HHS/CDC" label means too.

WHAT THE SPLIT SHOWS, AND THE TRAP IT SETS

HIV-labelled disbursements, FY2024 to FY2025, current USD m, countries only:

    USAID   2,037.0 -> 1,379.2   -32.3%
    CDC     1,510.2 -> 1,356.8   -10.2%
    State       6.4 ->   270.7
    other     105.8 ->    77.9
    total   3,659.4 -> 3,084.6   -15.7%

The trap is the State line. The Bureau of Global Health Security and Diplomacy (STATE/GHSD)
absorbed USAID's global health programmes in 2025, and disbursements managed by State go from
about 6m USD in FY2024 to 271m in FY2025 — essentially all of it GHSD, which disbursed nothing
at all before FY2025. So part of what left USAID did not leave the US government; it was
reclassified. Zimbabwe is the clearest case: USAID -40.9m, State +47.6m, country total up 3.9%.
Kenya USAID -55.2m against State +16.5m, Mozambique -110.4m against +41.4m, Zambia -83.5m
against +37.2m. A USAID series read on its own overstates the cut in every one of them, and a
country total hides it entirely.

This is why State gets its own series here and is not pooled into `other_agency` the way
`pepfar_expenditure` pools it. The two files disagree on purpose: PEPFAR's own expenditure
reporting still labels its agencies USAID / HHS-CDC / State bureaux with no GHSD line at all
through FY2025, so the reclassification is invisible there and visible here. Where they
disagree, this file is the one recording where the money actually went.

THE PARTIAL YEAR

The download is a snapshot taken during a running US fiscal year, so its last year is a
part-year figure. In the current file FY2026 holds 613m USD against a ~3,500m typical year,
and its composition is the reclassification in mid-flight (USAID 7m, CDC 0, State 595m).
Nothing in the file says "incomplete", so this connector works it out — if the latest year
totals less than 60% of the median of the three before it, every row in that year carries
`partial_fiscal_year` and the note saying not to compare it with a full year. The pipeline's
default `--end 2025` hides FY2026 but does not protect a run that asks for it.

GRAIN AND DOUBLE COUNTING

The four agency series partition the country total and sum back to `external_hiv_oda_us`,
which this connector also emits. Anything totalling the panel takes one level or the other,
never both. Note that `external_hiv_oda_us` is also emitted by the OECD CRS connector from a
different source; the agency split exists only for the `foreign_assistance` rows, so filter on
source_id before summing.

>>> CONFIRM ON FIRST FILE: FA.gov column names have changed across releases. The parser
    auto-detects the country / category / transaction-type / amount / year / agency columns
    and logs what it picked; adjust the candidate lists below if a release differs. If the
    managing-agency columns are absent the connector emits the country total alone and says
    so. It does not guess a split.
"""
from __future__ import annotations

import logging
import statistics
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

TOTAL = "external_hiv_oda_us"

# the sector/purpose columns that carry the HIV label. Order and membership are load-bearing:
# they define which rows are "HIV" and any change here changes the country totals.
SECTOR_COLS = ("US Sector Name", "International Sector Name",
               "International Purpose Name", "US Category Name")

# managing agency -> the suffix the canonical id carries. HHS covers CDC, NIH, HRSA, FDA and
# SAMHSA, and only CDC runs the PEPFAR treatment programmes, so the sub-agency decides. State
# is its own bucket here (see the docstring); everything else — DOD, Peace Corps, MCC, DOL,
# and the non-CDC parts of HHS — is pooled so the series still partition the country total.
USAID, CDC, STATE, OTHER = "usaid", "cdc", "state", "other_agency"
BUCKETS = (USAID, CDC, STATE, OTHER)

AGENCY_LABEL = {USAID: "USAID", CDC: "HHS/CDC", STATE: "State Department",
                OTHER: "other US agencies"}

# a year totalling less than this share of the median of the three before it is a part year
PARTIAL_YEAR_RATIO = 0.60

# FA.gov books recoveries and deobligations as negative disbursements, so a country-year with
# more recovered than paid out comes through negative and one that offsets exactly comes
# through as zero. Both are real accounting outcomes and neither is a parse failure, which is
# what a reader hitting a zero in a funding series will otherwise assume.
NON_POSITIVE_NOTE = (
    "a non-positive disbursement figure is not a gap: FA.gov books recoveries and "
    "deobligations as negative disbursements, so a year in which more was recovered than paid "
    "out nets below zero."
)

INTERPRETATION = (
    "US self-reported HIV disbursements, split by the agency that MANAGED the money and not "
    "the account it was appropriated to — PEPFAR is appropriated to State, so a split on "
    "funding agency puts nearly everything there and separates nothing. Read the USAID fall "
    "against the State series before calling it a cut: the Bureau of Global Health Security "
    "and Diplomacy took over USAID's global health programmes in 2025, and State-managed "
    "disbursements go from about 6m USD in FY2024 to 271m in FY2025. Part of what left USAID "
    "was reclassified, not withdrawn. Nominal USD, not deflated."
)


def _find(cols: List[str], *cands: str) -> Optional[str]:
    low = {c.lower(): c for c in cols}
    for c in cands:
        if c.lower() in low:
            return low[c.lower()]
    for col in cols:
        if any(c.lower() in col.lower() for c in cands):
            return col
    return None


def _bucket(managing: str, sub: str) -> str:
    m = str(managing).strip().upper()
    s = str(sub).strip().upper()
    if m == "USAID":
        return USAID
    if m == "HHS" and s == "CDC":
        return CDC
    if m == "STATE":
        return STATE
    return OTHER


class ForeignAssistanceConnector(BaseConnector):
    source_id = "foreign_assistance"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("ForeignAssistance.gov — US self-reported HIV disbursements by country and "
                   "managing agency (triangulates OECD US).")

    def __init__(self, raw_dir: str = "data/raw/foreign_assistance", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- reading ----------------------------------------------------------------
    def _columns(self, path: Path) -> Optional[dict]:
        """Resolve the columns from the header alone, so the body can be read with `usecols`.
        The complete data set is 56 columns and 3.7 GB; this connector needs nine of them."""
        head = pd.read_csv(path, dtype=str, nrows=0)
        cols = list(head.columns)
        found = {
            "country": _find(cols, "Country Name", "Country"),
            "txn": _find(cols, "Transaction Type Name", "Transaction Type"),
            "amount": _find(cols, "Current Dollar Amount", "Current Amount",
                            "constant Dollar Amount", "Amount"),
            "year": _find(cols, "Fiscal Year", "Year"),
            "agency": _find(cols, "Managing Agency Acronym", "Managing Agency Name"),
            "subagency": _find(cols, "Managing Sub-agency or Bureau Acronym",
                               "Managing Sub-agency or Bureau Name"),
        }
        # HIV is labelled in the SECTOR columns ("HIV/AIDS"), NOT "US Category Name" alone.
        found["sectors"] = [c for c in SECTOR_COLS if c in cols]
        if not (found["country"] and found["sectors"] and found["amount"] and found["year"]):
            log.warning("foreign_assistance: missing expected columns in %s: %s", path.name, cols)
            return None
        if not found["agency"]:
            log.warning("foreign_assistance: %s has no managing-agency column — emitting the "
                        "country total only, with no agency split", path.name)
        return found

    def _scan(self, path: Path, cols: dict, wanted, start_year: int, end_year: int,
              raw: Dict[Tuple[str, int, str], float], names: Dict[str, str]) -> None:
        iso_cache: Dict[str, Optional[str]] = {}
        usecols = [c for c in (cols["country"], cols["txn"], cols["amount"], cols["year"],
                               cols["agency"], cols["subagency"]) if c] + list(cols["sectors"])
        usecols = list(dict.fromkeys(usecols))

        for chunk in pd.read_csv(path, dtype=str, usecols=usecols, chunksize=500_000,
                                 low_memory=False):
            mask = pd.Series(False, index=chunk.index)
            for c in cols["sectors"]:
                mask |= chunk[c].astype(str).str.contains("HIV", case=False, na=False)
            hiv = chunk[mask]
            if cols["txn"]:  # disbursements only, never obligations
                hiv = hiv[hiv[cols["txn"]].astype(str)
                          .str.contains("disburs", case=False, na=False)]
            if hiv.empty:
                continue

            amt = pd.to_numeric(hiv[cols["amount"]].astype(str)
                                .str.replace(r"[,$]", "", regex=True), errors="coerce")
            year = pd.to_numeric(hiv[cols["year"]].astype(str).str.slice(0, 4), errors="coerce")
            keep = amt.notna() & year.notna() & year.between(start_year, end_year)
            if not keep.any():
                continue

            country = hiv[cols["country"]].astype(str)[keep]
            for name in country.unique():
                if name not in iso_cache:
                    iso_cache[name] = to_iso3(name)
                    if iso_cache[name]:
                        names[iso_cache[name]] = name
            iso = country.map(iso_cache)

            if cols["agency"]:
                sub = (hiv[cols["subagency"]].astype(str)[keep] if cols["subagency"]
                       else pd.Series("", index=iso.index))
                bucket = [_bucket(a, s) for a, s in
                          zip(hiv[cols["agency"]].astype(str)[keep], sub)]
            else:
                bucket = [""] * len(iso)

            frame = pd.DataFrame({"iso3": iso, "year": year[keep].astype(int),
                                  "bucket": bucket, "amount": amt[keep]})
            frame = frame[frame["iso3"].notna()]
            if wanted:
                frame = frame[frame["iso3"].isin(wanted)]
            if frame.empty:
                continue
            for key, value in frame.groupby(["iso3", "year", "bucket"], sort=False)["amount"].sum().items():
                raw[key] = raw.get(key, 0.0) + float(value)

    # -- emitting ---------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        files = sorted(self.raw_dir.glob("*.csv")) if self.raw_dir.exists() else []
        if not files:
            log.warning("foreign_assistance: no CSV in %s — download the 'Complete Data Set' "
                        "from foreignassistance.gov/data", self.raw_dir)
            return

        raw: Dict[Tuple[str, int, str], float] = {}
        names: Dict[str, str] = {}
        split = False
        for path in files:
            cols = self._columns(path)
            if not cols:
                continue
            log.info("foreign_assistance: %s country=%s sectors=%s txn=%s amount=%s year=%s "
                     "agency=%s subagency=%s", path.name, cols["country"], cols["sectors"],
                     cols["txn"], cols["amount"], cols["year"], cols["agency"], cols["subagency"])
            split = split or bool(cols["agency"])
            self._scan(path, cols, wanted, start_year, end_year, raw, names)

        yield from self._emit(raw, names, split)

    def _emit(self, raw: Dict[Tuple[str, int, str], float], names: Dict[str, str],
              split: bool) -> Iterator[PanelRow]:
        totals: Dict[Tuple[str, int], float] = {}
        by_agency: Dict[Tuple[str, int], Dict[str, float]] = {}
        for (iso3, year, bucket), value in raw.items():
            totals[(iso3, year)] = totals.get((iso3, year), 0.0) + value
            if bucket:
                by_agency.setdefault((iso3, year), {})[bucket] = value

        partial_year, partial_note = self._partial_year(totals)
        base_extra: Dict[str, object] = {
            "note": "US self-reported HIV disbursements; triangulates OECD CRS US series",
            "interpretation": INTERPRETATION,
        }

        n = 0
        for (iso3, year), value in sorted(totals.items()):
            country_name = names.get(iso3, "")
            agencies = by_agency.get((iso3, year), {})
            prev = by_agency.get((iso3, year - 1), {})

            extra = dict(base_extra, funding_agency="all_us_agencies")
            if split:
                extra["agency_split"] = "external_hiv_oda_us_{usaid,cdc,state,other_agency}"
                extra["grain_warning"] = (
                    "the agency series partition this total — sum one level or the other, "
                    "never both. The split exists only for source_id=foreign_assistance."
                )
            if year == partial_year:
                extra["partial_fiscal_year"] = True
                extra["partial_fiscal_year_note"] = partial_note
            if value <= 0:
                extra["value_note"] = NON_POSITIVE_NOTE
            yield self.make_row(
                country_iso3=iso3, country_name=country_name,
                indicator_id=TOTAL, year=year, value=value, unit="USD",
                source_url="https://foreignassistance.gov/data",
                source_indicator_code="FA.gov HIV disbursements — all managing agencies",
                extra=extra,
            )
            n += 1

            for bucket in BUCKETS:
                amount = agencies.get(bucket)
                # a bucket that falls to nothing is emitted as a zero, not left missing: for
                # the question this panel asks, "USAID spent nothing here this year" and "we
                # have no figure" are opposite readings and must not look alike.
                if amount is None:
                    if not prev.get(bucket):
                        continue
                    amount = 0.0
                agency_extra = dict(
                    base_extra,
                    funding_agency=AGENCY_LABEL[bucket],
                    agency_basis="Managing Agency (who spent it), not Funding Agency (whose "
                                 "account it came from)",
                    grain_warning="one of four series partitioning external_hiv_oda_us for this "
                                  "source; do not sum with the total row",
                )
                # a share only means something while the denominator is bigger than the parts.
                # Recoveries can leave a country-year whose total is a small residue of large
                # offsetting agency figures, and a ratio taken there is an artefact of the
                # denominator, so it is left out and the reason recorded.
                share = amount / value if value > 0 else None
                if share is not None and abs(share) <= 1:
                    agency_extra["share_of_country_total"] = round(share, 4)
                else:
                    agency_extra["share_of_country_total"] = None
                    agency_extra["share_note"] = (
                        "not computed: the country total for this year is zero, negative, or "
                        "smaller than this agency's own figure once recoveries are netted, so "
                        "the ratio would describe the denominator and not the split."
                    )
                if bucket == CDC:
                    agency_extra["agency_basis"] += "; HHS restricted to sub-agency CDC"
                if amount <= 0:
                    agency_extra["value_note"] = NON_POSITIVE_NOTE
                if bucket not in agencies:
                    agency_extra["zero_meaning"] = (
                        f"no HIV disbursement managed by this agency in FY{year}, against "
                        f"{prev.get(bucket, 0.0):,.0f} USD in FY{year - 1}. A reported zero, "
                        f"not a missing value."
                    )
                if year == partial_year:
                    agency_extra["partial_fiscal_year"] = True
                    agency_extra["partial_fiscal_year_note"] = partial_note
                yield self.make_row(
                    country_iso3=iso3, country_name=country_name,
                    indicator_id=f"{TOTAL}_{bucket}", year=year, value=amount, unit="USD",
                    source_url="https://foreignassistance.gov/data",
                    source_indicator_code=f"FA.gov HIV disbursements — managing agency "
                                          f"{AGENCY_LABEL[bucket]}",
                    extra=agency_extra,
                )
                n += 1
        log.info("foreign_assistance: emitted %d rows over %d country-years%s",
                 n, len(totals), " (with agency split)" if split else "")

    @staticmethod
    def _partial_year(totals: Dict[Tuple[str, int], float]) -> Tuple[Optional[int], str]:
        """The download is a snapshot of a running fiscal year, and nothing in the file says
        which year is incomplete. Infer it: the latest year, if it holds far less than the
        years before it. Judged on the whole run and not per country, because a single
        country's year-on-year swing is noise and the file-level one is not."""
        by_year: Dict[int, float] = {}
        for (_, year), value in totals.items():
            by_year[year] = by_year.get(year, 0.0) + value
        if len(by_year) < 3:
            return None, ""
        latest = max(by_year)
        prior = [by_year[y] for y in (latest - 3, latest - 2, latest - 1) if y in by_year]
        if len(prior) < 2:
            return None, ""
        median = statistics.median(prior)
        if median <= 0 or by_year[latest] >= PARTIAL_YEAR_RATIO * median:
            return None, ""
        note = (
            f"FY{latest} disbursements in this download total {by_year[latest]:,.0f} USD against "
            f"a median of {median:,.0f} for the years before it ({by_year[latest] / median:.0%}). "
            f"The US fiscal year ends 30 September and this file is a snapshot taken during it, "
            f"so FY{latest} is a part year and must not be compared with a full one."
        )
        log.warning("foreign_assistance: FY%d looks incomplete (%.0f%% of the prior median) — "
                    "rows flagged partial_fiscal_year", latest, 100 * by_year[latest] / median)
        return latest, note
