"""
UNAIDS GAM programme-expenditure database — what countries say they spent, and on what.

Source: UNAIDS publishes one workbook holding every HIV expenditure return countries
filed under Global AIDS Monitoring, from the GARPR 2016 cycle to GAM 2025. Each row is
one programme line for one country and one expenditure year, with the money split by who
paid for it. 59,947 rows, 121 countries, 541 country-years, expenditure years 2011-2024.
Forty-one country-years carry expenditure year 2024, which is the pre-cut baseline.

This is the only near-global source that says what a country's OWN accounting attributes
to PEPFAR and to the Global Fund. Every other financing series in the panel is the donor's
account of its own money. Two accounts of the same money are two measurements, so the
reconciliation layer has something to compare rather than an identity to rediscover.

TAGGING: source_type = expenditure_account. National AIDS Spending Assessment returns,
converted to US dollars by UNAIDS at the country's own exchange rate where the country
reported in local currency, and at the United Nations official rate where it did not.

WHAT IS READ

Two partitions of the same money, kept apart because they do not nest:

  * the financing split, taken from the one `TOTAL GRAND (including other essential
    programmes)` row each country-year has (541 of 541, no duplicates) — public, private,
    households, international, and the three donor lines PEPFAR, Global Fund and other
    bilateral;
  * the ten top-level programme lines of the modern classification, all-sources value
    only, for the 484 country-years that use that classification.

The ten programme lines partition `Total for key HIV programmes`, NOT the grand total:
they sum to the key-programmes total for 461 of 467 country-years (median ratio 1.00000)
but to the grand total for only 389 of 477, because the grand total also contains "other
essential programmes". Nothing in the panel may add a programme series to a financing
series.

WHAT IS NOT READ, AND WHY

  * 252 dotted sub-lines (`1.2 Antiretroviral treatment`, `3.9 ... prisoners`), 52,782
    rows. Parts of lines already read. Reading both levels would put the same money in
    the panel twice.
  * the three aggregate rows, 1,409 rows, except `TOTAL GRAND` which is read for the
    financing split.
  * the eight top-level lines of the pre-2016 classification, 248 rows over 31
    country-years. See THE TWO CLASSIFICATIONS below.
  * four `0N ... (reported by country separately under other essential programmes)`
    lines, 24 rows. These sit inside "other essential programmes", not inside the key
    programme total, so adding them to their numbered twin would break the partition,
    and the same label repeats twice in one country-year (Tanzania 2017 and 2018,
    Kazakhstan 2023) so there is no single value to take.
  * 16 residual and country-written lines, 644 rows, including `Other essential
    programmes for selected year` and free text a country typed in Russian, Spanish or
    French. Prose is not parsed for numbers.

THE MAP IS KEYED ON THE LABEL, NEVER ON THE NUMBER

Programme numbers are not stable across cycles and the labels are. Line `3.11` is "Cash
transfers to girls (high-prevalence countries)" from GAM 2017 to GAM 2023 and "Prevention
programmes for vulnerable and accessible populations (excluding HIV testing)" from GAM
2024, and `3.12` shifts the same way, from vulnerable populations to post-exposure
prophylaxis. A number-keyed map would splice cash transfers to girls onto a
vulnerable-populations series at exactly the 2024 boundary the project is measuring.

THE TWO CLASSIFICATIONS

The pre-2016 scheme writes a full stop after the digit (`4. Universal access to
treatment`); the modern scheme does not (`4 Gender programmes`). 31 country-years use the
old scheme, 484 the modern one, 26 report a grand total with no programme breakdown at
all, and no country-year mixes the two. The reporting cycle is not the discriminator:
GARPR 2016 and GAM 2017 both contain old-scheme returns.

The old scheme is declared out of scope for programme series. Its top level does not map
onto the modern one — "8. Synergies with development sectors" spans four modern lines,
and the modern gender, children, social-protection and community lines have no old
counterpart, so a mapped series would begin in 2016 with a definitional break wearing the
appearance of a change in spending. The cost is nil for this project's question: every
old-scheme country-year lies in expenditure years 2011 to 2015. Those 31 country-years
still contribute their financing split, which is classification-independent.

A ZERO IS NOT A MEASUREMENT

In this database a zero and a blank both mean "not reported", and nothing distinguishes
them. On the grand-total row the Households column is blank 13 times and zero 375 times
against 153 positive values, and PEPFAR is blank 14 times and zero 313 times against 214.
Neither is emitted. The consequence is that a programme genuinely defunded to nothing
cannot be told apart from a programme nobody filed a return for, and this source cannot
recover the difference.

THE PRINTED PARTS DO NOT ALWAYS ADD UP

Public plus private plus international equals the total for 532 of 540 country-years, the
six international sub-columns sum to International for 423 of 469, the four public columns
sum to TotalPublic for 425 of 495, and the four private columns sum to TotalPrivate for
226 of 250. No series here may be derived by subtracting others.

THE GRAND TOTAL IS A REPUBLICATION, THE DONOR COLUMNS ARE NOT

`TOTAL GRAND` x `Total expenditures from all sources` is the same series as UNAIDS
AIDSinfo's "Country-reported HIV expenditure, all sources", already in the panel through
unaids_aidsinfo: n=469, median ratio 1.0000, 420 within 1%, and the residual is AIDSinfo
rounding to two significant figures. It is emitted anyway so the reconciliation layer can
reach that verdict from the data instead of being told it. The donor columns behave
differently — GAM's PEPFAR against PEPFAR's own expenditure gives n=72 and a median of
0.995 with only 35 of 72 country-years within 10%, and GAM's GlobalFund against the OECD
CRS Global Fund series gives n=326 and a median of 0.806 with 47 within 10%. The centres
agree while the country-years scatter, which is what two independent accounts of one flow
of money look like.

Because those two are measurements of the same quantity, they are emitted under the
canonicals the donors' own accounts use, `pepfar_expenditure` and
`global_fund_hiv_disbursements`, so that the reconciliation layer compares them. Anything
that sums either series must filter on source_id first, exactly as `external_hiv_oda_us`
already requires. The two accounts also cover different windows, PEPFAR's fiscal year
against the country's own expenditure year, which is one reason among several for the
scatter and cannot be removed from this file.

THE COUNTRY CODE IS NOT ALWAYS ISO3

Kazakhstan is filed as `KZK`, not `KAZ`, in all 102 of its rows for expenditure year 2018.
A connector trusting CountryID drops Kazakhstan without saying so. In the other direction
"Gambia (Republic of The)" defeats name resolution while its `GMB` code is fine. So the
code is tried first, the name second, and any disagreement between the two is logged.

DE-DUPLICATION IS ALREADY DONE UPSTREAM. UNAIDS states that where a country reported the
same year in more than one cycle the database keeps the latest, and the file bears that
out: every (country, expenditure year) appears in exactly one reporting cycle.

Access: the workbook filename carries its publication date and will change when UNAIDS
publishes the next cycle, so the connector reads the current link off the index page at
hivfinancial.unaids.org and falls back to the last known-good URL. The file is cached in
`data/raw/unaids_gam/`; a copy already there is used as-is.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import pandas as pd

from ..connector_base import BaseConnector
from ..normalize import code_to_iso3, name_for, to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_INDEX_URL = "https://hivfinancial.unaids.org/"
_FALLBACK_URL = (
    "https://hivfinancial.unaids.org/GARPR16-GAM2025ProgrammeExpenditures-20250903.xlsx"
)
_LINK_RE = re.compile(
    r'href="(https://hivfinancial\.unaids\.org/[^"]*ProgrammeExpenditures[^"]*\.xlsx)"',
    re.I,
)

_SHEET = "data"
#: the workbook carries a two-row header, so the real column names are on row index 1
_HEADER_ROW = 1

_COL_CYCLE = "Reporting cycle"
_COL_COUNTRY = "Country"
_COL_CODE = "CountryID"
_COL_YEAR = "Expenditure year"
_COL_LABEL = "HIV Programmes"
_COL_ALL_SOURCES = "Total expenditures from all sources"

_GRAND = "TOTAL GRAND (including other essential programmes)"
_KEY_TOTAL = "Total for key HIV programmes"
_OTHER_TOTAL = "Total for other essential programmes"

#: the financing split, read off the grand-total row only. Column name -> canonical id.
#: TotalPublic, TotalPrivate and International are the three that partition the total;
#: Households is read because household out-of-pocket spending is what rises when a
#: programme stops paying, and the three donor columns are read because the country's
#: own account of donor money is the measurement no donor source can supply.
_FINANCING: List[Tuple[str, str]] = [
    ("TotalPublic", "domestic_hiv_spend"),
    ("TotalPrivate", "hiv_expenditure_domestic_private"),
    ("Households", "hiv_expenditure_households"),
    ("International", "hiv_expenditure_international"),
    # The two donor columns take the canonical the donor's own account already uses, so
    # the reconciliation layer compares the country's account with the donor's instead of
    # holding two series that never meet. Which canonical each takes was decided by the
    # arithmetic, not by the column name: GAM's PEPFAR column against pepfar_expenditure
    # gives n=72 with a median ratio of 0.995 and 35 country-years within 10%, against
    # external_hiv_oda_us n=205, median 1.031 and 54 within 10%. The wider overlap is
    # coverage, not agreement, and PEPFAR's own account is the closer measurement.
    ("PEPFAR", "pepfar_expenditure"),
    ("GlobalFund", "global_fund_hiv_disbursements"),
    # International and OtherBilateral keep their own canonicals. GAM's International is
    # every external pound and dollar the country received, while external_hiv_oda_total
    # is what OECD members reported as aid under purpose code 13040, so the two are
    # differently scoped rather than two measurements of one quantity.
    ("OtherBilateral", "hiv_expenditure_other_bilateral"),
    (_COL_ALL_SOURCES, "hiv_expenditure_total"),
]

#: the columns whose sum is checked against the total, recorded on the total row so a
#: reader can see whether the country's own arithmetic closed before trusting a component
_FINANCING_PARTS = ("TotalPublic", "TotalPrivate", "International")

#: the ten top-level lines of the modern classification. Sixteen labels for ten lines,
#: because six of them are written two ways across cycles ("6 Social protection" and
#: "6 Social protection and economic support" are the same line). Keyed on the label,
#: for the reason set out in the module docstring.
_PROGRAMME: Dict[str, str] = {
    "1 Treatment, care and support": "hiv_spend_treatment",
    "1 Treatment, care and support (sub-total)": "hiv_spend_treatment",
    "2 Prevention of vertical transmission of HIV (sub-total)": "hiv_spend_pmtct",
    "3 Prevention": "hiv_spend_prevention",
    "3 Prevention (sub-total)": "hiv_spend_prevention",
    "4 Gender programmes": "hiv_spend_gender",
    "5 Programmes for children and adolescents": "hiv_spend_children",
    "6 Social protection": "hiv_spend_social_protection",
    "6 Social protection and economic support": "hiv_spend_social_protection",
    "7 Community mobilization": "hiv_spend_community",
    "7 Community mobilization and system strengthening": "hiv_spend_community",
    "8 Governance and sustainability": "hiv_spend_governance",
    "8 Governance and sustainability (sub-total)": "hiv_spend_governance",
    "9 Critical enablers": "hiv_spend_enablers",
    "9 Critical enablers (sub-total)": "hiv_spend_enablers",
    "10 TB / HIV co-infection, diagnosis and treatment (sub-total)": "hiv_spend_tb_hiv",
}

_MODERN_TOP_RE = re.compile(r"^\d+ [A-Za-z]")
_MODERN_SUB_RE = re.compile(r"^\d+\.\d")
_OLD_TOP_RE = re.compile(r"^\d+\.\s")
_PADDED_RE = re.compile(r"^0\d ")

#: the residual buckets, named so a change in one of them shows up rather than being
#: absorbed into the free-text class along with everything a country typed by hand
_RESIDUAL = (
    "Other essential programmes for selected year",
    "HIV programmes n.e.c. (reported by country separately under other essential programmes)",
)


def declared_reason(label: str) -> Optional[str]:
    """The written reason a label is left alone, or None if nobody has decided about it.

    Every label the connector does not read must answer here, so the run log can report
    what was discarded beside what was used rather than reporting only the successes. A
    top-level line that is not in the map returns None on purpose: an eleventh programme
    line in a future cycle must surface as an undecided label, not be filed away as free
    text nobody looks at.
    """
    if label in _PROGRAMME or label == _GRAND:
        return None  # read, not discarded
    if label in (_KEY_TOTAL, _OTHER_TOTAL):
        return "aggregate of lines read separately"
    if _PADDED_RE.match(label):
        return "filed under other essential programmes, and repeats within a country-year"
    if _MODERN_SUB_RE.match(label):
        return "part of a top-level line already read"
    if _OLD_TOP_RE.match(label):
        return "pre-2016 classification, does not map onto the modern lines"
    if _MODERN_TOP_RE.match(label):
        return None  # a top-level line this connector has never seen
    if label in _RESIDUAL:
        return "residual bucket, whose parts are not separable"
    if label.startswith("("):
        return "other-essential line of the pre-2016 return form"
    return "country-written free text, and prose is not parsed for numbers"


def read_workbook(path: Path) -> pd.DataFrame:
    """Read the workbook into a frame with the label column stripped and named `label`."""
    df = pd.read_excel(path, sheet_name=_SHEET, header=_HEADER_ROW)
    df["label"] = df[_COL_LABEL].astype(str).str.strip()
    return df


def resolve_country(name: str, code: str) -> Tuple[Optional[str], Optional[str]]:
    """ISO3 for one country, code first and name second, plus a disagreement note.

    The code is tried first because it survives the punctuation a country name picks up
    ("Gambia (Republic of The)"), and the name is the fallback because the code is
    occasionally not ISO3 at all (Kazakhstan is filed as KZK).
    """
    by_code = code_to_iso3(str(code)) if code else None
    by_name = to_iso3(str(name)) if name else None
    if by_code and by_name and by_code != by_name:
        return by_code, f"code {code} resolves to {by_code}, name '{name}' to {by_name}"
    return (by_code or by_name), None


def usable(value) -> bool:
    """True when a cell is a measurement.

    A blank means the country did not report. A zero means the same thing, because the
    return form leaves an unfilled programme line at zero, and nothing in the file
    separates a real zero from an unfilled one.
    """
    if value is None or pd.isna(value):
        return False
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


class UNAIDSGAMExpenditureConnector(BaseConnector):
    source_id = "unaids_gam_expenditure"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = (
        "UNAIDS Global AIDS Monitoring programme expenditure: the financing split and the "
        "ten top-level programme lines, as the country itself reported them"
    )
    timeout = 180

    def __init__(
        self,
        raw_dir: str = "data/raw/unaids_gam",
        discover: bool = True,
        **kw,
    ) -> None:
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        self.discover = discover
        self.source_url = _FALLBACK_URL

    # -- acquisition -----------------------------------------------------------
    def workbook_url(self) -> str:
        """The current workbook link from the index page, or the last known-good URL.

        The filename carries its publication date (-20250903), so hardcoding it means the
        connector reads a stale cycle for a year after UNAIDS publishes the next one.
        """
        if not self.discover:
            return _FALLBACK_URL
        try:
            html = self.get_text(_INDEX_URL)
        except Exception as exc:  # the index is a convenience, never the dependency
            log.warning("unaids_gam_expenditure: index page unreadable (%s), using the "
                        "last known-good URL", exc)
            return _FALLBACK_URL
        found = _LINK_RE.findall(html)
        if not found:
            log.warning("unaids_gam_expenditure: no ProgrammeExpenditures link on %s, "
                        "using the last known-good URL", _INDEX_URL)
            return _FALLBACK_URL
        url = sorted(set(found))[-1]  # the publication date sorts last
        if url != _FALLBACK_URL:
            log.info("unaids_gam_expenditure: the index page offers %s, which is not the "
                     "URL this connector was written against", url)
        return url

    def local_copy(self) -> Path:
        """Path to the cached workbook, downloading it once if it is not already there."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        existing = sorted(self.raw_dir.glob("*ProgrammeExpenditures*.xlsx"))
        if existing:
            # the workbook sits at the site root, so the cached filename is the URL
            self.source_url = _INDEX_URL.rstrip("/") + "/" + existing[-1].name
            return existing[-1]
        url = self.workbook_url()
        self.source_url = url
        dest = self.raw_dir / url.rsplit("/", 1)[-1]
        log.info("unaids_gam_expenditure: downloading %s", url)
        resp = self._request("GET", url)
        dest.write_bytes(resp.content)
        log.info("unaids_gam_expenditure: cached %s (%d bytes)", dest, dest.stat().st_size)
        return dest

    # -- parsing (pure: takes a frame, does no I/O) -----------------------------
    def rows_from_frame(
        self,
        df: pd.DataFrame,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = {c.upper() for c in countries} if countries else None

        read_labels: set = set()
        declared_labels: Dict[str, int] = {}
        undecided_labels: Dict[str, int] = {}
        seen_labels: set = set()

        unresolved: Dict[str, int] = {}
        disagreements: Dict[str, str] = {}
        iso_cache: Dict[Tuple[str, str], Optional[str]] = {}

        n_financing = 0
        n_programme = 0
        n_blank_or_zero = 0
        old_scheme_years: set = set()

        # to_dict keeps the workbook's own column names, which itertuples would rename
        # (every name with a space becomes a positional _4, _22 and so on)
        for rec in df.to_dict(orient="records"):
            label = str(rec.get("label") or "").strip()
            seen_labels.add(label)

            reason = declared_reason(label)
            is_financing = label == _GRAND
            is_programme = label in _PROGRAMME
            if not is_financing and not is_programme:
                if reason is None:
                    undecided_labels[label] = undecided_labels.get(label, 0) + 1
                else:
                    declared_labels[label] = declared_labels.get(label, 0) + 1
                    if _OLD_TOP_RE.match(label):
                        old_scheme_years.add(int(rec.get(_COL_YEAR)))
                continue
            read_labels.add(label)

            year_raw = rec.get(_COL_YEAR)
            if year_raw is None or pd.isna(year_raw):
                continue
            year = int(year_raw)
            if year < start_year or year > end_year:
                continue

            name = str(rec.get(_COL_COUNTRY) or "").strip()
            code = str(rec.get(_COL_CODE) or "").strip()
            cache_key = (name, code)
            if cache_key not in iso_cache:
                iso3, note = resolve_country(name, code)
                iso_cache[cache_key] = iso3
                if note:
                    disagreements[name] = note
            iso3 = iso_cache[cache_key]
            if iso3 is None:
                unresolved[f"{name} ({code})"] = unresolved.get(f"{name} ({code})", 0) + 1
                continue
            if wanted and iso3 not in wanted:
                continue

            cycle = str(rec.get(_COL_CYCLE) or "").strip()
            extra_base = {"reporting_cycle": cycle, "gam_line": label}

            if is_financing:
                parts = [rec.get(c) for c in _FINANCING_PARTS]
                total = rec.get(_COL_ALL_SOURCES)
                parts_ok = None
                if all(p is not None and not pd.isna(p) for p in parts) and usable(total):
                    parts_ok = abs(sum(float(p) for p in parts) / float(total) - 1.0) <= 0.01
                for column, canonical in _FINANCING:
                    value = rec.get(column)
                    if not usable(value):
                        n_blank_or_zero += 1
                        continue
                    extra = dict(extra_base)
                    if canonical == "hiv_expenditure_total" and parts_ok is not None:
                        extra["financing_parts_sum_to_total"] = parts_ok
                    yield self.make_row(
                        country_iso3=iso3,
                        country_name=name_for(iso3),
                        indicator_id=canonical,
                        year=year,
                        value=float(value),
                        unit="USD",
                        source_url=self.source_url,
                        source_indicator_code=f"{_GRAND} | {column}",
                        extra=extra,
                    )
                    n_financing += 1
                continue

            value = rec.get(_COL_ALL_SOURCES)
            if not usable(value):
                n_blank_or_zero += 1
                continue
            yield self.make_row(
                country_iso3=iso3,
                country_name=name_for(iso3),
                indicator_id=_PROGRAMME[label],
                year=year,
                value=float(value),
                unit="USD",
                source_url=self.source_url,
                source_indicator_code=f"{label} | {_COL_ALL_SOURCES}",
                extra=extra_base,
            )
            n_programme += 1

        log.info(
            "unaids_gam_expenditure: read %d of %d programme labels, %d deliberately left "
            "alone, %d awaiting a decision",
            len(read_labels), len(seen_labels), len(declared_labels), len(undecided_labels),
        )
        log.info(
            "unaids_gam_expenditure: %d financing rows and %d programme rows emitted, "
            "%d cells blank or zero and therefore not reported",
            n_financing, n_programme, n_blank_or_zero,
        )
        if old_scheme_years:
            log.info(
                "unaids_gam_expenditure: the pre-2016 classification appears in expenditure "
                "years %s and contributes financing rows only",
                ", ".join(str(y) for y in sorted(old_scheme_years)),
            )
        if undecided_labels:
            worst = sorted(undecided_labels.items(), key=lambda kv: -kv[1])[:10]
            log.warning(
                "unaids_gam_expenditure: %d labels have no written decision: %s",
                len(undecided_labels), "; ".join(f"{k} ({n})" for k, n in worst),
            )
        for note in disagreements.values():
            log.warning("unaids_gam_expenditure: %s", note)
        if unresolved:
            log.warning(
                "unaids_gam_expenditure: %d places did not resolve to an ISO3 country: %s",
                len(unresolved), ", ".join(sorted(unresolved)),
            )

    # -- the contract ----------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        path = self.local_copy()
        df = read_workbook(path)
        log.info("unaids_gam_expenditure: %d rows from %s", len(df), path.name)
        yield from self.rows_from_frame(
            df, countries=countries, start_year=start_year, end_year=end_year
        )
