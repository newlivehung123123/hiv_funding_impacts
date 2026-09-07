"""
WHO Global Health Expenditure Database — HIV money as the national health accounts see it.

Source: WHO publishes one workbook holding every country's health accounts from 2000
onward, 4,120 variables over 4,612 country-years and 195 countries. One family of those
variables, `dis11`, carries spending on HIV/AIDS and other sexually transmitted diseases.

TAGGING: source_type = expenditure_account. System of Health Accounts 2011 returns,
compiled and reviewed by WHO with the country's own statistical office, then converted to
US dollars. This is a different accounting system from the National AIDS Spending
Assessment that feeds Global AIDS Monitoring, prepared by different people from different
ledgers, which is the reason to read it.

WHAT IS READ

Seven variables, four of money and three of share.

  * `dis11_usd`, `dis11_gghed_usd`, `dis11_ext_usd`, `dis11_pvtd_usd` — total HIV and STD
    spending and its split by who paid, government, external or domestic private.
  * `dis11_che` — HIV and STD spending as a share of all current health spending.
  * `dis11_ext_ext` — external HIV and STD spending as a share of all external health
    spending, which says how much of the donor health money in a country is HIV money and
    therefore how much a donor withdrawal takes with it.
  * `dis11_g_gghed` — government HIV and STD spending as a share of government health
    spending, which is the country's own commitment measured against its own budget.

The share of all health spending is not a small quantity in the countries this project is
about. Zambia in 2019 puts 65.2 percent of its entire current health expenditure through
the HIV and STD line, and 46 country-years exceed 20 percent, every one of them in
Eastern or Southern Africa. Zambia, Malawi, Mozambique, Zimbabwe, Uganda, Tanzania,
Eswatini, Botswana and Kenya are the countries above that mark. A funding cut to HIV in
these places is not a cut to one programme inside a health system, it is a cut to a large
fraction of the health system, and that is what this share is here to measure.

THE FIGURES ARE IN MILLIONS AND THE PANEL IS IN UNITS

Every `dis11` money variable is stated in millions, and the codebook says so for all eight
of them rather than for `dis11_usd` alone, which is what an earlier note in the access
ladder claimed. Three checks agree. The printed `dis11_che` equals `dis11 / che * 100` to
the sixth decimal on all 359 country-years, so `dis11` and `che` share one basis. Dividing
`dis11_usd` by `dis11_usd_pc` implies populations from 109,821 to 223,150,896 with a
median of 15,895,315, which are populations rather than nonsense. And the resulting country
totals sit alongside the Global AIDS Monitoring totals for the same country-years. The
connector multiplies by one million, and any future variable added to the read set must be
checked the same way before it is trusted.

HIV AND STD IS NOT HIV, SO THESE SERIES GET THEIR OWN CANONICALS

`dis11` is "HIV/AIDS and Other Sexually Transmitted Diseases", while every existing
expenditure series in the panel is HIV alone. The two are differently scoped rather than
two measurements of one quantity, so the connector does not put them under
`hiv_expenditure_total` and its neighbours. This follows the rule the GAM connector
already applies to `hiv_expenditure_international` against `external_hiv_oda_total`.

The arithmetic supports the decision rather than merely permitting it. Against the GAM
expenditure database over the country-years both cover:

  * total, 138 country-years over 44 countries, median ratio 1.14, GHED larger in 87,
    48 of the 138 differing by a factor of two or more;
  * external, 129 country-years over 39 countries, median ratio 1.002 with GHED larger in
    65 of 129, so the centres coincide while the direction of the disagreement is a coin
    flip;
  * government, 134 country-years over 43 countries, median ratio 1.22 and 68 of the 134
    differing by a factor of two or more.

Two accounts that agreed on the centre and disagreed country by country would be two
independent measurements of one quantity. A ratio of 1.14 that also swings by a factor of
two is something else, and reading a WHO total as though it answered the GAM question
would import the STD component and the accounting difference together, with no way
afterwards to tell which moved. The government comparison is the sharpest of the three
and is a finding in its own right: national health accounts and the AIDS spending
assessment disagree most about what counts as government HIV money.

Because the canonicals differ, the reconciliation layer will not pair these series with
anything. That is the intended outcome, and the comparison above is the evidence that
nothing has been lost by it, since no GHED series was a republication of a panel series.

A ZERO IS A MEASUREMENT HERE, UNLIKE IN GAM

The GAM connector drops zeroes because a GAM return leaves an unfilled line at zero and
nothing separates an unfilled line from a real one. The opposite holds in this file. Seven
component cells are zero across the whole HIV family, and in all seven the remaining
components still sum to the printed total within one percent, so each zero is an entry in
a closed account rather than a gap. Costa Rica 2020 and North Macedonia 2019 and 2020
record no external HIV money, Uzbekistan 2016 to 2018 and Haiti 2016 record no private
HIV money. Zeroes are emitted. Blanks are not, and blank is how this file says nothing is
known.

THE COMPONENTS ARE A TRUE PARTITION, SO NOTHING MAY SUM THEM WITH THE TOTAL

Government plus external plus private equals the total on all 328 country-years where the
four are printed together, at a median ratio of exactly 1.000000. That is stricter than
GAM, where the printed parts fail to close on a tenth of country-years. Anything totalling
the panel must take the total or the three components and never both, which is why every
row records which of the two levels it belongs to.

THE HIV LINE STOPS BEFORE THE EVENT THIS PROJECT MEASURES

The workbook runs to 2024 and its HIV line does not. 359 country-years carry an HIV
figure, over 60 countries, from 2013 to 2023, and the country count per year falls away
long before the end: 51 countries in 2018 and again in 2019, then 32, 26, 15 and 10. The
last year is not the last year of the file and must not be read as the current position.
This source cannot see the 2025 funding cuts at all. It is here as an independent account
of the years before them and as a check on GAM, and any use of it in the analysis has to
say so. The connector reports the span and the per-year country counts it actually found
rather than the ones written here, because a later release will move them.

WHETHER A FIGURE WAS DOCUMENTED OR ESTIMATED IS PUBLISHED, AND IS CARRIED

The Metadata sheet states, per country and per variable, which years were documented and
which WHO estimated, as text like "2013 - 2018: Documented; 2019: Estimated". Every one of
the 59 country records for `dis11` carries such a string and all of them parse, covering
340 of the 359 country-years on the total series, 303 documented, 35 estimated and 2
partially documented. The private component is filed for 57 countries rather than 59,
which is why 43 of the 1,381 money rows carry no label at all.

That label goes into `extra` on every row, because an expenditure figure a country
documented and one WHO estimated are not equally good evidence that spending changed, and
a reader who cannot tell them apart will read an estimation method as a funding cut.

THE CACHED FILENAME CARRIES NO VERSION

WHO serves the workbook from a single URL with `Content-Disposition: attachment;
filename=GHED_data.XLSX`, and that name is the same for every release. A cached copy
therefore cannot be told from a current one by its name, unlike the GAM workbook whose
filename carries its publication date. The connector reads the release date off the
Version sheet, logs it on every run and writes it into every row, so a stale cache shows
up in the panel instead of hiding in it. Deleting the cached file is how a new release is
taken.

Access: open, no key, no referer, 38.9 MB over one request. Cached in `data/raw/who_ghed/`.
"""
from __future__ import annotations

import logging
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import openpyxl

from ..connector_base import BaseConnector
from ..normalize import code_to_iso3, name_for, to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_URL = "https://apps.who.int/nha/database/Home/IndicatorsDownload/en"
_CACHE_NAME = "GHED_data.xlsx"

_SHEET_DATA = "Data"
_SHEET_META = "Metadata"
_SHEET_VERSION = "Version"

_COL_LOCATION = "location"
_COL_CODE = "code"
_COL_REGION = "region"
_COL_INCOME = "income"
_COL_YEAR = "year"
_IDENTIFIERS = (_COL_LOCATION, _COL_CODE, _COL_REGION, _COL_INCOME, _COL_YEAR)

#: one million, because every dis11 money variable is stated in millions
_MILLION = 1_000_000.0

#: the money variables. Source code -> (canonical id, level within the partition).
#: The level is recorded on the row so that a reader adding the panel up can see, without
#: consulting this file, that the total and the three components are the same money twice.
_MONEY: List[Tuple[str, str, str]] = [
    ("dis11_usd", "hiv_std_expenditure_total", "total"),
    ("dis11_gghed_usd", "hiv_std_expenditure_government", "component"),
    ("dis11_ext_usd", "hiv_std_expenditure_external", "component"),
    ("dis11_pvtd_usd", "hiv_std_expenditure_private", "component"),
]

#: the share variables, already percentages, so no conversion and no partition
_SHARES: List[Tuple[str, str]] = [
    ("dis11_che", "hiv_std_share_of_health_spend"),
    ("dis11_ext_ext", "hiv_std_share_of_external_health_spend"),
    ("dis11_g_gghed", "hiv_std_govt_share_of_govt_health_spend"),
]

_READ: Dict[str, Tuple[str, str, float]] = {
    **{code: (canonical, level, _MILLION) for code, canonical, level in _MONEY},
    **{code: (canonical, "share", 1.0) for code, canonical in _SHARES},
}

#: the three components whose sum is checked against the printed total
_COMPONENT_CODES = ("dis11_gghed_usd", "dis11_ext_usd", "dis11_pvtd_usd")

#: "2013 - 2018: Documented; 2019: Estimated" -> one label per year
_SPAN_RE = re.compile(r"^\s*(\d{4})\s*(?:-\s*(\d{4}))?\s*$")
_VERSION_RE = re.compile(r"Last updated:\s*(.+?)\s*$", re.I)


def declared_reason(code: str) -> Optional[str]:
    """The written reason a GHED variable is left alone, or None if nobody has decided.

    Every one of the 4,120 columns must answer here, so the run log can report what was
    discarded beside what was used. A `dis11` variable that matches none of the rules
    returns None on purpose: a new member of the HIV family in a future release must
    surface as an undecided column rather than be filed away with the health-system
    aggregates nobody looks at.
    """
    if code in _READ:
        return None  # read, not discarded
    if code in _IDENTIFIERS:
        return "identifier column"

    if code.startswith("dis11"):
        rest = code[len("dis11"):]
        # ordered so that the first sufficient reason wins; several are true at once for
        # a name like dis11_gghed_ncu2023_pc, and one written reason is enough
        if "2023" in rest:
            return "constant 2023 prices, and the panel holds current prices"
        if "ppp" in rest:
            return "purchasing-power parity, and the panel holds current US dollars"
        if rest.endswith("_pc"):
            return "per capita, and the panel holds the country total"
        if "ncu" in rest or rest in ("", "_gghed", "_ext", "_pvtd"):
            return "national currency units, and the current US dollar series is read instead"
        if rest.endswith("_gdp") or rest.endswith("_gge"):
            return ("expressed against gross domestic product or total government spending, "
                    "denominators the panel does not carry")
        if rest.endswith("_che"):
            return ("a component's share of current health expenditure, recoverable from the "
                    "money series already read")
        return None  # a member of the HIV family this connector has never seen

    if code.startswith("dis12"):
        return ("all tuberculosis spending, which is not the TB/HIV collaborative spending "
                "the panel names")
    if code.startswith("dis"):
        return "a disease category the panel does not name"
    return "a health-system aggregate rather than an HIV series"


def parse_data_type(text: object) -> Dict[int, str]:
    """Year -> "Documented" / "Estimated" / "Partially Documented" from one metadata cell.

    The published form is semicolon-separated clauses, each a year or a year range, a
    colon, then the label. A clause whose span does not parse is dropped rather than
    guessed at, and the caller sees the shortfall as rows without a label.
    """
    out: Dict[int, str] = {}
    if not isinstance(text, str):
        return out
    for part in text.split(";"):
        if ":" not in part:
            continue
        span, label = part.split(":", 1)
        m = _SPAN_RE.match(span)
        if not m:
            continue
        first = int(m.group(1))
        last = int(m.group(2) or m.group(1))
        if last < first:
            continue
        for year in range(first, last + 1):
            out[year] = label.strip()
    return out


def resolve_country(name: str, code: str) -> Tuple[Optional[str], Optional[str]]:
    """ISO3 for one country, code first and name second, plus a disagreement note.

    All 195 GHED codes resolved and none disagreed with its country name when this
    connector was written, so the fallback and the note are here to report a change in the
    file rather than to paper over a known defect.
    """
    by_code = code_to_iso3(str(code)) if code else None
    by_name = to_iso3(str(name)) if name else None
    if by_code and by_name and by_code != by_name:
        return by_code, f"code {code} resolves to {by_code}, name '{name}' to {by_name}"
    return (by_code or by_name), None


def usable(value: object) -> bool:
    """True when a cell is a measurement.

    A blank means the account records nothing known. A zero does not: the three component
    cells that are zero all sit in accounts whose parts still sum to the printed total, so
    a zero here is an entry rather than a gap. This is the opposite of the GAM database
    and the difference is a property of the two sources, not a matter of taste.
    """
    if value is None or value == "":
        return False
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return number == number and number >= 0  # number == number rejects NaN


class WHOGHEDConnector(BaseConnector):
    source_id = "who_ghed"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = (
        "WHO Global Health Expenditure Database: HIV and STD spending and its financing "
        "split, as the national health accounts record it"
    )
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/who_ghed", **kw) -> None:
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        self.source_url = _URL
        self.release: str = ""

    # -- acquisition -----------------------------------------------------------
    def local_copy(self) -> Path:
        """Path to the cached workbook, downloading it once if it is not already there.

        The served filename is the same for every release, so a cached copy is used
        without any way to tell which release it is until the Version sheet is read. The
        log says plainly which of the two happened.
        """
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        dest = self.raw_dir / _CACHE_NAME
        if dest.exists():
            log.info("who_ghed: using the cached workbook at %s (%d bytes). WHO serves "
                     "every release under one filename, so delete this file to take a "
                     "newer one", dest, dest.stat().st_size)
            return dest
        log.info("who_ghed: downloading %s", _URL)
        resp = self._request("GET", _URL)
        dest.write_bytes(resp.content)
        log.info("who_ghed: cached %s (%d bytes)", dest, dest.stat().st_size)
        return dest

    # -- reading (each takes a workbook, returns plain data) --------------------
    @staticmethod
    def read_release(wb) -> str:
        """The release date printed on the Version sheet, or "" if it is not there."""
        if _SHEET_VERSION not in wb.sheetnames:
            return ""
        for row in wb[_SHEET_VERSION].iter_rows(values_only=True):
            for cell in row:
                if isinstance(cell, str):
                    m = _VERSION_RE.search(cell)
                    if m:
                        return m.group(1)
        return ""

    @staticmethod
    def read_data_types(wb) -> Dict[Tuple[str, str], Dict[int, str]]:
        """(ISO3 code as filed, variable code) -> {year: label} from the Metadata sheet.

        Only the variables this connector reads are kept, so the 32,664-row sheet does not
        become 32,664 dictionaries. The money variables are labelled under their national
        currency names (`dis11`, `dis11_gghed`), not their US dollar ones, because the
        label describes the underlying figure rather than the conversion, so the caller
        looks the label up under the base name.
        """
        wanted = {"dis11", "dis11_gghed", "dis11_ext", "dis11_pvtd"}
        out: Dict[Tuple[str, str], Dict[int, str]] = {}
        rows = wb[_SHEET_META].iter_rows(values_only=True)
        header = [str(c).strip() if c is not None else "" for c in next(rows)]
        try:
            i_code = header.index("code")
            i_var = header.index("variable code")
            i_type = header.index("Data type")
        except ValueError:
            log.warning("who_ghed: the Metadata sheet does not carry the columns this "
                        "connector reads, so no documented/estimated labels are attached")
            return out
        for row in rows:
            var = str(row[i_var] or "").strip()
            if var not in wanted:
                continue
            parsed = parse_data_type(row[i_type])
            if parsed:
                out[(str(row[i_code] or "").strip(), var)] = parsed
        return out

    # -- the contract ----------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        path = self.local_copy()
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        self.release = self.read_release(wb)
        log.info("who_ghed: workbook release %s", self.release or "not stated on the Version sheet")
        data_types = self.read_data_types(wb)
        log.info("who_ghed: %d country and variable records carry a documented or "
                 "estimated label", len(data_types))
        yield from self.rows_from_sheet(
            wb, data_types, countries=countries, start_year=start_year, end_year=end_year
        )

    def rows_from_sheet(
        self,
        wb,
        data_types: Dict[Tuple[str, str], Dict[int, str]],
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        """Stream the Data sheet and yield one row per readable cell.

        The sheet is 4,120 columns wide and holds about 19 million cells, so it is streamed
        rather than loaded into a frame, and only the columns in the read set are ever
        looked at.
        """
        end_year = end_year or 2035
        wanted = {c.upper() for c in countries} if countries else None

        rows = wb[_SHEET_DATA].iter_rows(values_only=True)
        header = [str(c).strip() if c is not None else "" for c in next(rows)]

        # the §9g accounting, done on the columns before a single value is read
        read_cols: Dict[str, int] = {}
        declared: Counter = Counter()
        undecided: List[str] = []
        for position, code in enumerate(header):
            if not code:
                continue
            if code in _READ:
                read_cols[code] = position
                continue
            reason = declared_reason(code)
            if reason is None:
                undecided.append(code)
            else:
                declared[reason] += 1
        missing = [c for c in _READ if c not in read_cols]
        if missing:
            log.warning("who_ghed: %d variables this connector reads are not in the "
                        "workbook and contribute nothing: %s", len(missing), ", ".join(missing))
        log.info("who_ghed: read %d of %d columns, %d deliberately left alone, %d awaiting "
                 "a decision", len(read_cols), len(header), sum(declared.values()), len(undecided))
        if undecided:
            log.warning("who_ghed: %d HIV-family columns have no written decision: %s",
                        len(undecided), ", ".join(sorted(undecided)[:10]))

        try:
            i_location = header.index(_COL_LOCATION)
            i_code = header.index(_COL_CODE)
            i_region = header.index(_COL_REGION)
            i_income = header.index(_COL_INCOME)
            i_year = header.index(_COL_YEAR)
        except ValueError as exc:
            raise RuntimeError(f"who_ghed: the Data sheet is missing an identifier column: {exc}")

        #: money variable -> the metadata name the documented/estimated label is filed under
        label_base = {
            "dis11_usd": "dis11",
            "dis11_gghed_usd": "dis11_gghed",
            "dis11_ext_usd": "dis11_ext",
            "dis11_pvtd_usd": "dis11_pvtd",
        }

        n_emitted = Counter()
        n_blank = 0
        n_zero = 0
        no_label = 0
        years_seen: Counter = Counter()
        countries_by_year: Dict[int, set] = {}
        unresolved: Counter = Counter()
        disagreements: Dict[str, str] = {}
        iso_cache: Dict[Tuple[str, str], Optional[str]] = {}
        partition_closes = 0
        partition_checked = 0

        for row in rows:
            year_raw = row[i_year]
            if year_raw is None:
                continue
            try:
                year = int(year_raw)
            except (TypeError, ValueError):
                continue
            if year < start_year or year > end_year:
                continue

            name = str(row[i_location] or "").strip()
            filed_code = str(row[i_code] or "").strip()
            cache_key = (name, filed_code)
            if cache_key not in iso_cache:
                iso3, note = resolve_country(name, filed_code)
                iso_cache[cache_key] = iso3
                if note:
                    disagreements[name] = note
            iso3 = iso_cache[cache_key]

            values = {code: row[pos] for code, pos in read_cols.items()}
            if not any(usable(v) for v in values.values()):
                continue  # a country-year with no HIV line at all, which is most of them

            if iso3 is None:
                unresolved[f"{name} ({filed_code})"] += 1
                continue
            if wanted and iso3 not in wanted:
                continue

            # whether the country's own three components close on the printed total, so a
            # reader can see the account balanced before trusting any one component
            parts = [values.get(c) for c in _COMPONENT_CODES]
            total = values.get("dis11_usd")
            closes: Optional[bool] = None
            if all(usable(p) for p in parts) and usable(total) and float(total) > 0:
                closes = abs(sum(float(p) for p in parts) / float(total) - 1.0) <= 0.01
                partition_checked += 1
                partition_closes += int(closes)

            region = str(row[i_region] or "").strip()
            income = str(row[i_income] or "").strip()
            years_seen[year] += 1
            countries_by_year.setdefault(year, set()).add(iso3)

            for code, (canonical, level, factor) in _READ.items():
                if code not in read_cols:
                    continue
                raw = values.get(code)
                if not usable(raw):
                    n_blank += 1
                    continue
                number = float(raw)
                if number == 0.0:
                    n_zero += 1

                extra = {
                    "ghed_variable": code,
                    "ghed_release": self.release,
                    "who_region": region,
                    "income_group": income,
                    "partition_level": level,
                }
                base = label_base.get(code)
                if base:
                    label = data_types.get((filed_code, base), {}).get(year)
                    if label:
                        extra["data_type"] = label
                    else:
                        no_label += 1
                if code == "dis11_usd" and closes is not None:
                    extra["components_sum_to_total"] = closes

                yield self.make_row(
                    country_iso3=iso3,
                    country_name=name_for(iso3),
                    indicator_id=canonical,
                    year=year,
                    value=number * factor,
                    unit="percent" if level == "share" else "USD",
                    source_url=_URL,
                    source_indicator_code=code,
                    extra=extra,
                )
                n_emitted[canonical] += 1

        total_rows = sum(n_emitted.values())
        log.info("who_ghed: %d rows emitted over %d indicators, %d cells blank and "
                 "therefore not reported, %d cells zero and reported as measurements",
                 total_rows, len(n_emitted), n_blank, n_zero)
        if years_seen:
            span = f"{min(years_seen)} to {max(years_seen)}"
            worst = max(countries_by_year, key=lambda y: len(countries_by_year[y]))
            latest = max(countries_by_year)
            log.info("who_ghed: the HIV line covers %d country-years over %s. Coverage "
                     "peaks at %d countries in %d and falls to %d in %d, so the last year "
                     "present is not the current position and this source cannot speak to "
                     "anything after it",
                     sum(years_seen.values()), span,
                     len(countries_by_year[worst]), worst,
                     len(countries_by_year[latest]), latest)
        if partition_checked:
            log.info("who_ghed: government plus external plus private equals the printed "
                     "total on %d of %d country-years, so the total and the three "
                     "components are the same money at two levels and must never be summed "
                     "together", partition_closes, partition_checked)
        if no_label:
            log.info("who_ghed: %d money rows carry no documented-or-estimated label, "
                     "because WHO published none for that country and year", no_label)
        for note in disagreements.values():
            log.warning("who_ghed: %s", note)
        if unresolved:
            log.warning("who_ghed: %d places with an HIV figure did not resolve to an ISO3 "
                        "country and were dropped: %s",
                        len(unresolved), ", ".join(sorted(unresolved)))
