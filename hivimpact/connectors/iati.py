"""
IATI via d-portal — HIV financing from every publisher that files to the IATI registry.

WHY THIS SOURCE EXISTS ALONGSIDE oecd_crs AND foreign_assistance
----------------------------------------------------------------
OECD CRS is an annual return filed by official donors, published about 14 months after
the year it describes, and the 2020 classification change moved money between purpose
codes in a way that breaks a series read straight across the break. ForeignAssistance.gov
is the United States only. IATI is neither: publishers file transaction by transaction,
within weeks, and the file names the day the money moved. For a study of a funding
collapse that began in January 2025, IATI is the only one of the three that can see the
collapse at all.

What IATI costs in exchange is that every publisher files to a different standard of
care. An activity may state its sectors as percentages or not at all, may name a country
or only a region, and may be a pass-through of money that already reached the panel from
the donor that supplied it. Every rule below exists because a publisher does one of those
things.

THE ROUTE
---------
d-portal (https://d-portal.org) mirrors the registry into Postgres and serves two things:

  the query service   /q?...&form=json    rows, fast, already split by country and sector
  the XML export      /q.xml?...          the publisher's own file, 2.03, nothing invented

The two are used for different jobs, and the split is deliberate.

The XML export is the source of every figure written for a publisher other than the
Global Fund, because only the publisher's own file carries the percentages the publisher
stated, the organisations it names as funders, and the title. The percentages the
publisher stated are the written value, which is how RESUME.md item 21 was settled on
28 September 2026.

No row carries a key named `extra.dportal_split_usd`. An earlier version of this
docstring said every row carries d-portal's own split of the same transaction under that
name, so that the first run would measure the disagreement between the two readings. The
key was never written and the claim was corrected on 30 September 2026 after counting the
`extra` keys on the 7,062 `iati` rows of the working panel, which carry 24 distinct keys
and no key of that name. Measuring the disagreement across the whole panel therefore
needs either a new key and a rerun or a separate read-only probe against the query
service, and item 21 turns on neither, because the publisher's file is the record and
d-portal's split is one reading of that record.

The Global Fund is read from the query service instead, and that is a departure from the
approved design of RESUME.md item 17(a). Three measurements justify the departure and
none of them is about convenience:

  1. The Global Fund's XML export runs to 573,710 bytes an activity over 1,246 activities,
     about 715 MB, because d-portal repeats every transaction of a grant inside every
     activity of that grant.
  2. Every Global Fund activity that names a country names exactly one country at 100 per
     cent, and no activity names both a country and a region. 42 of 48 activities sampled
     from the publisher's own XML name one country and no region, and the other six name
     a region and no country. So no allocation decision is being skipped by not reading
     the file.
  3. The Global Fund publishes in US dollars only and in sector vocabulary 1 only, so
     neither a currency conversion nor a vocabulary filter can change a figure.

The Global Fund's whole-grant value comes from summing d-portal's sector splits back
together, grouped on the activity identifier and the transaction ordinal. That grouping
was checked against the publisher's stated sector percentages and the two disagree, which
is the reason the sum is taken and the percentages are not used. On 47045-MWI-C-MOH-2 the
stored percentages are 1, 4 and 88 while the splits divide the money 7, 4 and 88, and on
47045-UGA-H-MoFPED-2 the stored percentages are 11 and 88 while the splits divide it 1 and
88. Reconstructing a published value by dividing a split by a stored percentage would
therefore have been wrong by up to 51 percentage points on the activities checked.

WHAT THIS CONNECTOR REFUSES TO DO
---------------------------------
It never reads d-portal's invented disbursements. d-portal marks a transaction it
generated itself with trans_flags=1, and two publishers carry them: Pact with 30 rows
worth 627,097,700 US dollars and Enabel with two rows worth 22,607.84. Every query here
pins trans_flags=0.

It never reads money through the activity-level join. An activity row carries `spend` and
`commitment` columns that are activity lifetime totals, so joining an activity to a
country and reading `spend` multiplies the grant by the number of countries.

It never resolves a country code by name. IATI recipient countries are ISO 3166-1 alpha-2
codes and are resolved here by an exact alpha-2 lookup, never through `to_iso3`, because
`to_iso3` falls through to pycountry's fuzzy search on a two-letter code it cannot place,
and fuzzy search matches subdivision names. The same trap once made the United Kingdom the
largest recipient of US HIV aid in this panel, at 59.9bn US dollars. Every code that fails
the strict lookup is named in the log with its money, not counted in silence.
"""
from __future__ import annotations

import csv
import gzip
import logging
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

try:
    import pycountry
    _HAS_PYCOUNTRY = True
except ImportError:  # pragma: no cover - the panel's other connectors make the same allowance
    _HAS_PYCOUNTRY = False

from ..connector_base import BaseConnector
from ..normalize import code_to_iso3, name_for
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_Q = "https://d-portal.org/q"
_QXML = "https://d-portal.org/q.xml"

#: OECD purpose code for STD control including HIV and AIDS. The panel's HIV money is this
#: code and nothing else, matching oecd_crs, so the two sources measure the same thing.
_HIV = "13040"
#: Reproductive health care. Carried in `extra` for the sensitivity check item 17(c) asks
#: for, never added to a written value.
_HIV_RELATED = "16064"

#: d-portal serves at most this many activities per XML page. Measured, not read from
#: documentation.
_ACT_PAGE = 300

#: The limit the query service is asked for, which is far above any query this connector
#: sends and is deliberately not a page size. `_qrows` takes a whole result in one request
#: and never pages, for the reason that function's docstring gives.
#:
#: A comment here used to record 20,000 as a measured per-page cap on the query service.
#: That figure was wrong. Measured on 30 September 2026, a limit of 200,000 was honoured in
#: 6.3 seconds and a limit of three million returns the largest query this connector sends,
#: 326,852 rows, complete in about 40 seconds. Nothing was capping the response at 20,000
#: except the connector asking for 20,000.
_ROW_LIMIT = 3_000_000

#: IATI dates arrive from the query service as days since 1 January 1970.
_EPOCH = date(1970, 1, 1)

# --------------------------------------------------------------------------------------
# the organisations whose money must not be counted twice
# --------------------------------------------------------------------------------------

#: The Global Fund publishes under the bare DAC number and is cited by others under both
#: shapes. The Global Fund's `reporting-org type` is 30, a public-private partnership, and
#: not 40. Identifying the Global Fund by organisation type would therefore both miss it
#: and, worse, leave the type-40 multilateral series believing the Global Fund was excluded.
_GLOBAL_FUND_REF = "47045"
_GLOBAL_FUND_ALIASES = {"47045", "XM-DAC-47045"}
_GLOBAL_FUND_NAME = "GLOBAL FUND TO FIGHT"

#: Eight US government publishers file HIV activities, not the five the survey first found:
#: US-GOV-1, 7, 9, 10, 11, 14, 17 and 18. The prefix catches all eight and any ninth.
#: US-EIN- and US-IRS- refs are American charities, not the American government, and are
#: deliberately absent.
_US_GOV_PREFIX = "US-GOV-"
#: The ref the files actually use for the United States as a funder is US-USAGOV, which
#: appeared 459 times in the sampled corpus against 170 for US-GOV-1. A matcher built from
#: the agency publisher ids alone would have missed most of the American money.
_US_GOV_REFS = {"US-USAGOV", "US-GOV", "XM-DAC-302"}
_US_GOV_NAMES = (
    "UNITED STATES OF AMERICA",
    "UNITED STATES AGENCY FOR INTERNATIONAL DEVELOPMENT",
    "U.S. AGENCY FOR INTERNATIONAL DEVELOPMENT",
    "USAID",
    "PEPFAR",
    "PRESIDENT'S EMERGENCY PLAN",
    "CENTERS FOR DISEASE CONTROL",
    "DEPARTMENT OF STATE",
    "MILLENNIUM CHALLENGE CORPORATION",
    "PEACE CORPS",
)

# --------------------------------------------------------------------------------------
# transaction types
# --------------------------------------------------------------------------------------

#: The XML states a numeric transaction type. 3 is a disbursement and 4 an expenditure,
#: and item 17(b) counts those two and nothing else. Commitments (2), incoming funds (1),
#: incoming commitments (11), pledges (12, 13), interest (5) and loan repayments (6) are
#: intent or income, not money spent on a country, and are never summed.
_MONEY_OUT_CODES = {"3", "4"}
#: A reimbursement is money flowing back, and item 17(b) subtracts none of it, because a
#: publisher that files a reimbursement has usually also revised the original disbursement
#: and subtracting both removes the money twice. On the Global Fund path the reimbursement
#: total is written onto the row in `reimbursements_usd`. On the publisher path the
#: reimbursement reaches no row at all and is logged once per currency the file states,
#: which is what item 38 settled on 1 October 2026.
_REIMBURSEMENT_CODE = "7"

#: The query service uses letters where IATI uses numbers. Measured across three
#: publishers: the Global Fund files D, C and R; WHO files D, E, C and the bare 11;
#: Sweden files D, E and C.
_MONEY_OUT_LETTERS = "D|E"
_REIMBURSEMENT_LETTER = "R"

# --------------------------------------------------------------------------------------
# the three series of item 17(f), keyed on the publisher's own organisation type
# --------------------------------------------------------------------------------------

_BILATERAL_TYPES = {"10", "11", "15"}      # government, local government, other public sector
_MULTILATERAL_TYPES = {"40"}
_FOUNDATION_TYPES = {"60"}

#: Everything else is logged and not written. NGOs (21 to 24) and academic bodies (80) are
#: usually spending money that reached the panel from the government that supplied it, and
#: companies (70 to 76) and public-private partnerships (30) are neither donors nor
#: recipients in the sense the three series mean.
_TYPE_LABELS = {
    "21": "international NGO", "22": "national NGO", "23": "regional NGO",
    "24": "partner country NGO", "30": "public-private partnership",
    "70": "private sector", "71": "private sector in provider country",
    "72": "private sector in aid recipient country", "73": "private sector in third country",
    "80": "academic, training and research", "90": "other",
}

_SERIES_BILATERAL = "external_hiv_bilateral_other"
_SERIES_MULTILATERAL = "external_hiv_multilateral_other"
_SERIES_FOUNDATION = "external_hiv_foundation"
_SERIES_GLOBAL_FUND = "global_fund_hiv_disbursements"

#: Item 17(f) holds the foundation series until the question of whether the CRS
#: all-official-donor total already contains Gates Foundation money is settled. The Gates
#: Foundation joined the DAC's reporting in 2020 and CRS carries its money from some year
#: onwards, so writing a foundation series now risks a series that double counts before
#: one year and not after. The type-60 money is still read, still logged and still counted,
#: so the run reports exactly what the series would hold on the day the hold is lifted.
_WRITE_FOUNDATION = False

#: Item 17(g), the pass-through exclusion, keeps money already measured by oecd_crs and by
#: foreign_assistance from entering the panel a second time through IATI.
#:
#: Mode "any" excludes an activity when ANY organisation it names as a funder, other than
#: the activity's own reporting organisation, is the Global Fund or a US government body.
#: Mode "sole" excludes an activity only when every funder it names is one of those two.
#:
#: The full run of 28 September 2026 measured what mode "any" costs. Mode "any" excluded
#: 2,140 activities across 10 publishers and only 109 of the 2,140 named an excluded funder
#: alone, so mode "any" was discarding 41 other donors' money in order to discard the
#: American share. UNAIDS was the extreme case and the reason the mode changed. UNAIDS
#: names 42 role-1 funders on every activity and the United States is always among the 42,
#: so mode "any" deleted all 1,228 UNAIDS activities and the panel held no UNAIDS row at
#: all, with nothing in the panel to say why. An absence a reader cannot see is worse than
#: an overlap a reader can filter.
#:
#: Jason settled item 20 as (g3) on 28 September 2026. The connector runs mode "sole", and
#: every row that survives while still naming an excluded funder carries
#: `extra.names_passthrough_funder` and `extra.passthrough_funder_usd`, so the strict
#: result remains reproducible by filtering and the overlap remains bounded by a number.
_PASSTHROUGH_MODE = "sole"


# --------------------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------------------

def _local_name(tag: str) -> str:
    """'{ns}activity' -> 'activity'. d-portal's export is usually unprefixed and
    occasionally is not, and a namespace appearing on one publisher's file is not a reason
    for that publisher to vanish from the panel."""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _children(elem, name: str) -> List[ET.Element]:
    return [c for c in elem if _local_name(c.tag) == name]


def _narrative(elem) -> str:
    """The text of an element, taking its <narrative> children when it has them."""
    if elem is None:
        return ""
    parts = [t.strip() for t in elem.itertext() if t and t.strip()]
    return " ".join(parts)


def _day_to_date(day) -> Optional[date]:
    try:
        return _EPOCH + timedelta(days=int(day))
    except (TypeError, ValueError):
        return None


def _iso_date(text: str) -> Optional[date]:
    if not text:
        return None
    try:
        return date.fromisoformat(str(text).strip()[:10])
    except ValueError:
        return None


def _amount(value_elem) -> Optional[float]:
    """The number out of an IATI <value> element.

    IATI puts the amount in the element's text and the currency and value date in its
    attributes, so <value currency="SEK" value-date="2004-01-01">16251</value> is sixteen
    thousand Swedish crowns. Reading an attribute called value returns nothing at all, and
    a connector that did so would report a publisher with 3,241 disbursements as a
    publisher with no HIV money.
    """
    if value_elem is None:
        return None
    out = _float((value_elem.text or "").strip())
    return out if out is not None else _float(value_elem.get("value"))


def _float(text) -> Optional[float]:
    if text is None or text == "":
        return None
    try:
        return float(str(text).replace(",", ""))
    except (TypeError, ValueError):
        return None


#: Kosovo has no ISO 3166-1 entry. The panel's convention, set in normalize.py and used by
#: the World Bank, is the user-assigned XKX, and IATI publishers write XK.
_ALPHA2_USER_ASSIGNED = {"XK": "XKX"}

#: Item 22. IATI's `recipient-country` element expects an ISO 3166-1 alpha-2 code, and two
#: publishers in the corpus file an OECD DAC recipient number there instead. The Swiss
#: Agency for Development and Cooperation, CH-4, publishes in French and files the DAC
#: number with the DAC French label beside it. The Department of Foreign Affairs and Trade
#: with Irish Aid, XM-DAC-21-1, files the unspecified bucket 998 with the DAC English label.
#:
#: Every entry below was checked one by one against the published OECD DAC recipient code
#: list at https://datahub.io/core/dac-and-crs-code-lists, file data/recipients.csv, whose
#: French column matches the narrative CH-4 filed character for character. The table holds
#: only codes the corpus actually contains, so no entry is transcribed without evidence on
#: both sides. A numeric code absent from the table stays refused and is named with its
#: money in the run log, so the next publisher to file an unmapped DAC number is visible
#: rather than silent, and the published list above is where the entry then comes from.
#:
#: A numeric code cannot collide with an ISO code, because code_to_iso3 requires three
#: letters and _alpha2_to_iso3 requires two, so consulting this table first is safe. This
#: is a code lookup against a published standard and never a name lookup, which is what
#: keeps it clear of the fuzzy trap described on _alpha2_to_iso3.
_DAC_RECIPIENT_TO_ISO3 = {
    "229": "CMR",   # Cameroon, filed by CH-4 as "Cameroun"
    "259": "MOZ",   # Mozambique, filed by CH-4 as "Mozambique"
    "265": "ZWE",   # Zimbabwe, filed by CH-4 as "Zimbabwe"
    "282": "TZA",   # Tanzania, filed by CH-4 as "Tanzanie"
    "753": "MNG",   # Mongolia, filed by CH-4 as "Mongolie"
}

#: DAC codes naming a region or naming no destination at all, filed into the country
#: element by the same publishers. IATI's own Region codelist contains all three, so money
#: filed against one of them is region money and is treated exactly as a `recipient-region`
#: carrying the same code would be treated. Under item 17 region money stays with the
#: region and is written nowhere, so recognising these three moves their money out of the
#: refused-code bucket, where the destination is unknown, into the region bucket, where the
#: destination is known and the decision not to write it is deliberate.
_DAC_REGIONAL = {
    "289": "South of Sahara, regional",
    "298": "Africa, regional",
    "998": "Developing countries, unspecified",
}


def _alpha2_to_iso3(code: str) -> Optional[str]:
    """Strict alpha-2 to ISO3, or None so the caller can log the code it refused.

    This deliberately does not call `to_iso3`. On a two-letter code pycountry cannot place,
    `to_iso3` falls through to `search_fuzzy`, and `search_fuzzy` matches subdivision names
    as readily as country names. That path is how a regional aggregate once entered this
    panel wearing the United Kingdom's name. A code this function cannot resolve is a code
    the log must name, not a code to guess at.
    """
    if not code:
        return None
    raw = str(code).strip().upper()
    if raw in _ALPHA2_USER_ASSIGNED:
        return _ALPHA2_USER_ASSIGNED[raw]
    if len(raw) != 2 or not raw.isalpha():
        return None
    if not _HAS_PYCOUNTRY:
        return None
    rec = pycountry.countries.get(alpha_2=raw)
    return rec.alpha_3 if rec is not None else None


def _any_code_to_iso3(code: str) -> Optional[str]:
    """Resolve a d-portal country code, which may arrive as alpha-2 or alpha-3, or None.

    The query service returns whatever the publisher filed, and IATI's own standard says
    alpha-2 while a few publishers file alpha-3 anyway. Both shapes are resolved strictly,
    the three-letter shape through the panel's own code_to_iso3, which already knows that
    Kosovo is XKX and that XKV is a synonym for it. Neither branch can reach a fuzzy match.

    A third shape is an OECD DAC recipient number, which CH-4 files in place of the alpha-2
    code IATI asks for. Item 22 settled that shape, and _DAC_RECIPIENT_TO_ISO3 carries the
    codes the corpus contains. A DAC region code is deliberately absent from that table and
    resolves to None here, because region money is handled in _geography and must never
    become a country.
    """
    if not code:
        return None
    raw = str(code).strip().upper()
    if raw in _DAC_RECIPIENT_TO_ISO3:
        return _DAC_RECIPIENT_TO_ISO3[raw]
    if len(raw) == 3:
        return code_to_iso3(raw)
    return _alpha2_to_iso3(raw)


def _is_hc_grant(aid: str) -> bool:
    """True when a Global Fund identifier names an HIV or a combined HIV and TB grant.

    The Global Fund writes two identifier shapes and the component letter sits in a
    different place in each: 47045-GIN-H-MOH-1 has five parts with the letter at index 2,
    and 47045-NMB-202-G01-H-00-1 has seven with the letter at index 4. Measured over the
    1,246 activities carrying purpose 13040, 729 use the five-part shape, 401 use six parts
    and 116 use seven. Scanning every part after the country code is immune to the
    difference, and the grant-number parts are always a G followed by digits, so no grant
    number can be mistaken for a component letter.

    The letters are the Global Fund's own: H is HIV, C is HIV and TB together, T is TB, M is
    malaria, S is health systems and Z is multi-component. 970 of the 1,246 activities are H,
    241 are C and 34 are Z, and the 34 Z grants are the ones item 17(e) reads through the
    13040 share instead of whole.
    """
    return any(part in ("H", "C") for part in str(aid).split("-")[2:])


class IATIConnector(BaseConnector):
    source_id = "iati"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = (
        "IATI via d-portal — HIV financing (purpose 13040) transaction by transaction: the "
        "Global Fund's disbursements, and bilateral, multilateral and foundation money from "
        "every other publisher. Complements oecd_crs, which is annual and lagged."
    )
    request_pause = 0.5
    #: d-portal answers a 20,000-row page in tens of seconds and a 300-activity XML page in
    #: minutes for a publisher with long transaction lists.
    timeout = 900

    def __init__(self, raw_dir: str = "data/raw/iati", refresh: bool = False, **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        self.refresh = refresh
        #: exchange rates recovered from d-portal's own conversions, keyed (currency, YYYY-MM)
        self._rates: Dict[Tuple[str, str], float] = {}
        self._rates_by_year: Dict[Tuple[str, int], float] = {}
        self._rates_mean: Dict[str, float] = {}

    # ----------------------------------------------------------------------------------
    # the query service
    # ----------------------------------------------------------------------------------

    def _qrows(self, params: dict, limit: int = _ROW_LIMIT) -> Iterator[dict]:
        """Take a whole query-service result in one request. Never page on offset.

        This function used to page with `limit` and `offset`, and that was a defect which
        silently changed the panel from one run to the next. The query service applies no
        ORDER BY unless asked, and a relational engine given no ORDER BY may return rows in
        any order and in a different order on two executions of the same statement, so
        `LIMIT n OFFSET n` is not guaranteed to continue where `LIMIT n OFFSET 0` stopped.
        Rows repeat across pages, other rows are never returned at all, and which rows are
        lost changes run to run.

        Measured on 30 September 2026, two identical 20,000-row requests for the Global
        Fund's transactions returned 20,000 rows each of which 14,680 differed. The Global
        Fund series moved by 1,387,699,426 USD between two runs of identical code, 101
        country-years gained money naming grants the previous run never saw, 224 lost money,
        and Rwanda lost every row.

        One request cannot shuffle, because one execution of one statement returns the whole
        result set whatever order the rows arrive in. Ordering is therefore unnecessary, and
        asking for it would cost a sort the service takes about 24 seconds over. `orderby`
        is honoured on that one spelling, so ordering remains available if a future query
        outgrows a single request, but no query here does.

        The single failure mode is a result larger than the limit, which the service would
        answer by returning the limit and losing the remainder without saying so. That is a
        truncation bug traded for a shuffling bug, and it is refused rather than accepted. A
        count strictly below the limit is a complete result. A count equal to the limit
        raises, because a count equal to the limit is the one case where a single request
        loses rows silently. `_ROW_LIMIT` is three million against a largest measured query
        of 326,852 rows, so the raise is a guard and not an expected path.

        Transport failures need no handling here. `connector_base._request` retries every
        `requests.RequestException`, read timeouts included, with exponential backoff, and
        raises rather than returning partial data once the attempts run out. The query
        service is intermittently very slow, and one measured request failed after 933
        seconds and then answered in 19.5, which is exactly the case that retry covers.

        Server-side aggregation is never requested. Asking for sum() drops the aggregate
        from the SELECT without an error, visible only in the `dquery` the service echoes
        back, and `groupby` is ignored the same way, so a caller that trusted either would
        receive ungrouped rows and sum them twice. Every total here is summed in Python,
        which also avoids d-portal storing its sums in single precision. The service
        silently drops `groupby`, `order_by`, `order`, `sort`, `sortby`, `trans_day_min`,
        `trans_day_max`, `year` and `trans_year` in the same way, so no query here relies on
        any of them.
        """
        body = self.get_json(_Q, params={**params, "form": "json",
                                         "limit": limit, "offset": 0})
        rows = body.get("rows") or []
        if body.get("error"):
            log.warning("iati: query service reported an error for %s: %s",
                        params.get("reporting_ref", params), body["error"])
        if len(rows) >= limit:
            raise RuntimeError(
                f"iati: the query service returned {len(rows)} rows against a limit of "
                f"{limit}, so the result was truncated and an unknown remainder is missing. "
                f"Raise _ROW_LIMIT above the true size of this query before running again. "
                f"The query was {params!r}")
        for row in rows:
            yield row

    def _publishers(self) -> List[Tuple[str, int]]:
        """Every publisher filing an activity under purpose 13040, largest first."""
        counts: Dict[str, int] = defaultdict(int)
        missing = 0
        for row in self._qrows({"from": "act,sector", "sector_code": _HIV,
                                "select": "aid,reporting_ref"}):
            ref = (row.get("reporting_ref") or "").strip()
            if not ref:
                missing += 1
                continue
            counts[ref] += 1
        if missing:
            # One publisher, Progressio, reaches d-portal with no reporting reference at
            # all. An activity with no publisher cannot be attributed, cannot be tested
            # against the pass-through rule and cannot be excluded as a US publisher, so it
            # is refused here rather than guessed at.
            log.info("iati: %d activity row(s) carry no reporting reference and are skipped",
                     missing)
        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        log.info("iati: %d publishers file under purpose %s, %d activity-sector rows in all",
                 len(ordered), _HIV, sum(counts.values()))
        return ordered

    def _load_rates(self, refs: Iterable[str]) -> None:
        """Recover d-portal's monthly exchange rates from its own conversions.

        The XML export states a transaction in the currency the publisher used and nothing
        else, so a figure taken from the XML needs a rate to become US dollars. d-portal
        already applies one, and the rate it applied is recoverable exactly as trans_usd
        divided by trans_value on any row of that currency and month. Recovering the rate
        this way keeps every figure in the panel on the same conversion d-portal used, so
        a figure read from the XML export and a figure read from the query service stay
        comparable, which matters because the Global Fund rows come from the query service
        and every other publisher's rows come from the export. An earlier version of this
        docstring named `extra.dportal_split_usd` as the figure kept comparable, and no row
        carries a key of that name.

        A rate belongs to a currency and a month, not to a publisher, so one publisher's
        rows serve every publisher using that currency. Measured publishing currencies are
        one per publisher: Sweden files SEK, the FCDO and CAFOD GBP, Germany, the
        Netherlands and Irish Aid EUR, Australia AUD, Canada CAD, Switzerland CHF, and the
        Global Fund, WHO, UNAIDS, UNICEF, UNDP and the Gates Foundation all file USD.
        """
        samples: Dict[Tuple[str, str], List[float]] = defaultdict(list)
        for ref in refs:
            for row in self._qrows({"from": "trans,act", "reporting_ref": ref,
                                    "trans_sector": _HIV, "trans_flags": 0,
                                    "trans_code": _MONEY_OUT_LETTERS,
                                    "select": "trans_day,trans_currency,trans_value,trans_usd"}):
                cur = (row.get("trans_currency") or "").strip().upper()
                val = _float(row.get("trans_value"))
                usd = _float(row.get("trans_usd"))
                when = _day_to_date(row.get("trans_day"))
                if not cur or not val or usd is None or when is None:
                    continue
                samples[(cur, f"{when.year:04d}-{when.month:02d}")].append(usd / val)
        for key, values in samples.items():
            self._rates[key] = sum(values) / len(values)
        by_year: Dict[Tuple[str, int], List[float]] = defaultdict(list)
        by_cur: Dict[str, List[float]] = defaultdict(list)
        for (cur, month), rate in self._rates.items():
            by_year[(cur, int(month[:4]))].append(rate)
            by_cur[cur].append(rate)
        self._rates_by_year = {k: sum(v) / len(v) for k, v in by_year.items()}
        self._rates_mean = {k: sum(v) / len(v) for k, v in by_cur.items()}
        log.info("iati: recovered %d monthly rates covering %d currencies: %s",
                 len(self._rates), len(self._rates_mean), ", ".join(sorted(self._rates_mean)))

    def _to_usd(self, value: float, currency: str, when: date) -> Optional[float]:
        """Convert a stated amount into US dollars, or return None where no rate is held.

        Item 30, approved on 1 October 2026. A blank currency used to take the same path as
        a stated US dollar, so a transaction naming no currency entered the panel as dollars
        with no key on the row recording the assumption and no counter in the log reporting
        how many such transactions a publisher filed. 119 of the 374,789 transaction value
        elements in the cache of 30 September 2026 state no currency, 83 pass the sector,
        transaction-type and year filters, and 48 panel rows carried 13,629,785.48 USD
        written that way, being 63.1 per cent of the money the Ministry for Foreign Affairs
        of Finland holds in the panel and 28.8 per cent of Irish Aid's. Neither publisher
        states a US dollar anywhere in the HIV sector. A blank currency now returns None, so
        the caller has to resolve the currency before asking for a conversion and no later
        caller can write dollars by accident.
        """
        cur = (currency or "").strip().upper()
        if not cur:
            return None
        if cur == "USD":
            return value
        key = (cur, f"{when.year:04d}-{when.month:02d}")
        if key in self._rates:
            return value * self._rates[key]
        if (cur, when.year) in self._rates_by_year:
            return value * self._rates_by_year[(cur, when.year)]
        if cur in self._rates_mean:
            return value * self._rates_mean[cur]
        return None

    # ----------------------------------------------------------------------------------
    # the XML cache, item 17(l)
    # ----------------------------------------------------------------------------------

    def _cache_path(self, ref: str, offset: int) -> Path:
        slug = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in ref)
        return self.raw_dir / slug / f"page_{offset:06d}.xml.gz"

    def _xml_pages(self, ref: str, first_page_only: bool = False) -> Iterator[Tuple[Path, bytes]]:
        """Yield every cached XML page for one publisher, fetching what is missing.

        Pages are gzipped on disk. Uncompressed the cache for the publishers other than the
        Global Fund runs to roughly 800 MB, dominated by Sweden at about 364 MB and WHO at
        about 300 MB, against 15 GB free beside a data/raw that already holds 2.8 GB.
        Gzipped the same cache is roughly 80 MB. The extension is free to choose because
        scripts/audit_coverage.py walks the top level of a raw directory only, and every
        page here sits one level down in a per-publisher directory, which is the same
        arrangement foreign_assistance uses for the IATI files it fetches for itself.
        """
        offset = 0
        while True:
            path = self._cache_path(ref, offset)
            if path.exists() and path.stat().st_size > 0 and not self.refresh:
                body = gzip.decompress(path.read_bytes())
            else:
                try:
                    body = self._request("GET", _QXML, params={
                        "from": "act,sector", "sector_code": _HIV, "reporting_ref": ref,
                        "limit": _ACT_PAGE, "offset": offset}).content
                except Exception as exc:
                    log.warning("iati: %s page at offset %d failed: %s", ref, offset, exc)
                    return
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(gzip.compress(body, compresslevel=6))
            try:
                root = ET.fromstring(body)
            except ET.ParseError as exc:
                log.warning("iati: %s page at offset %d does not parse: %s", ref, offset, exc)
                return
            activities = [a for a in root if _local_name(a.tag) == "iati-activity"]
            if not activities:
                activities = list(root)
            yield path, body
            if first_page_only or len(activities) < _ACT_PAGE:
                return
            offset += _ACT_PAGE

    def _org_type(self, ref: str) -> str:
        """The publisher's own reporting-org type, read from the first page and no further.

        The type is a property of the publisher and not of the activity, so the first
        activity that states one settles it. Activities filed by a secondary reporter are
        skipped, because a secondary reporter states its own type and not the type of the
        publisher whose money is being described.
        """
        for _path, body in self._xml_pages(ref, first_page_only=True):
            try:
                root = ET.fromstring(body)
            except ET.ParseError:
                return ""
            for act in root:
                reporting = next(iter(_children(act, "reporting-org")), None)
                if reporting is None:
                    continue
                if (reporting.get("secondary-reporter") or "0").strip() == "1":
                    continue
                stated = (reporting.get("type") or "").strip()
                if stated:
                    return stated
        return ""

    # ----------------------------------------------------------------------------------
    # the Global Fund, item 17(e)
    # ----------------------------------------------------------------------------------

    def _check_apportionment(self, rows_per_tx: Dict[Tuple[str, int], int]) -> None:
        """Test the assumption the Global Fund series rests on, and log what the test found.

        Adding a transaction's sector shares reaches the transaction only while two things
        hold of d-portal. Every Global Fund activity's declared sector percentages must sum
        to 100, or a whole-grant total is a fraction or a multiple of the money the Global
        Fund moved. And the `trans` table must hold one row per transaction per declared
        sector row, because a surplus row is d-portal duplicating a share and adding a
        duplicated share invents money.

        Both held completely when measured on 30 September 2026. All 2,726 Global Fund
        activities declared percentages summing to exactly 100 across 4,721 sector rows, and
        all 113,777 transactions returned exactly as many rows as their activity declared,
        with none surplus and none short. Neither is a property d-portal documents or
        promises, so the run tests both rather than trusting the measurement to hold. The
        sector table costs one query of about 4,700 rows and a few seconds.

        Nothing here changes a figure. A failure is logged as a warning and the run continues,
        because a run that reaches the panel with a warning against it is worth more than a
        run that raises and leaves nothing to inspect.
        """
        declared: Dict[str, List[float]] = defaultdict(list)
        for row in self._qrows({"from": "act,sector", "reporting_ref": _GLOBAL_FUND_REF,
                                "select": "aid,sector_code,sector_percent"}):
            percent = _float(row.get("sector_percent"))
            declared[row.get("aid") or ""].append(0.0 if percent is None else percent)

        off_hundred = {aid: round(sum(pcts), 2) for aid, pcts in declared.items()
                       if abs(sum(pcts) - 100.0) > 0.5}
        equal = short = surplus = undeclared = 0
        surplus_examples: List[str] = []
        for (aid, tid), got in rows_per_tx.items():
            want = len(declared.get(aid, []))
            if want == 0:
                undeclared += 1
            elif got == want:
                equal += 1
            elif got < want:
                short += 1
            else:
                surplus += 1
                if len(surplus_examples) < 5:
                    surplus_examples.append(f"{aid} transaction {tid} returned {got} "
                                            f"against {want} declared")

        log.info("iati: global fund apportionment — %d activity(ies) declaring %d sector "
                 "row(s); of %d transaction(s), %d match the declared sector count, %d are "
                 "short and %d are surplus, and %d belong to an activity declaring no sector",
                 len(declared), sum(len(p) for p in declared.values()), len(rows_per_tx),
                 equal, short, surplus, undeclared)
        if off_hundred:
            log.warning("iati: global fund apportionment — %d activity(ies) declare sector "
                        "percentages that do not sum to 100, so a whole-grant total for those "
                        "activities is not the money the Global Fund moved: %s",
                        len(off_hundred),
                        ", ".join(f"{aid} sums to {total}"
                                  for aid, total in sorted(off_hundred.items())[:10]))
        if surplus:
            log.warning("iati: global fund apportionment — %d transaction(s) returned more "
                        "rows than their activity declares sector rows, so d-portal has "
                        "duplicated a share and those transactions are overstated: %s",
                        surplus, "; ".join(surplus_examples))
        if short:
            log.info("iati: global fund apportionment — %d transaction(s) returned fewer rows "
                     "than declared, which costs nothing, because a share d-portal omits is a "
                     "share that rounded to nothing", short)

    def _global_fund(self, wanted: Optional[Set[str]], start_year: int, end_year: int,
                     crs: Dict[Tuple[str, int], float]) -> Iterator[PanelRow]:
        """The Global Fund's disbursements, whole for HIV grants and by share for the rest.

        Item 17(e) defines the series as the whole value of every H and C grant plus the
        13040 share of every other grant, and that definition rather than a pure 13040 read
        is what holds across the 2020 CRS classification break. The Global Fund changed how
        it codes grant sectors in 2018 and the CRS changed how it classified them in 2020,
        so a series built on the sector code alone has two steps in it that are accounting
        changes and not money.
        """
        titles: Dict[str, str] = {}
        for row in self._qrows({"from": "act,sector", "sector_code": _HIV,
                                "reporting_ref": _GLOBAL_FUND_REF, "select": "aid,title"}):
            titles[row.get("aid") or ""] = row.get("title") or ""

        # Rule 17(h), the COVID exclusion, is applied to the Global Fund from the title
        # column. Exactly one of the 1,246 activities names COVID, 47045-BWA-C-BMoH-3, and
        # that title also names HIV, so on today's corpus the rule excludes nothing here.
        # Rule 17(g), the pass-through exclusion, is not applied to the Global Fund at all.
        # The rule exists to stop Global Fund and American money entering the panel a second
        # time through a body spending it on their behalf, and the Global Fund spending its
        # own money is the first time, not the second.
        covid_excluded = {aid for aid, title in titles.items()
                          if ("COVID" in title.upper() or "C19" in title.upper())
                          and "HIV" not in title.upper() and "AIDS" not in title.upper()}
        if covid_excluded:
            log.info("iati: global fund — %d activity(ies) excluded by the COVID rule: %s",
                     len(covid_excluded), ", ".join(sorted(covid_excluded)))

        # d-portal's `trans` table is pre-apportioned. The table holds one row per transaction
        # per sector row the activity declares, and each row carries the transaction's value
        # times that sector's percentage. So `trans_usd` is a sector's share of a transaction
        # and never a transaction, and a transaction's shares sum to the transaction.
        #
        # An activity may declare the same sector code twice at two different percentages.
        # 47045-MWI-C-MOH-2 declares 12263 at 4 per cent, 12110 at 7, 12110 again at 1, and
        # 13040 at 88, which sum to 100, and every repeated key on that grant carries two rows
        # in a ratio of exactly seven. Ten Global Fund activities go further and declare one
        # code twice at the same percentage, all ten on sector 12110.
        #
        # This line therefore accumulates and must never assign. An assignment kept whichever
        # row happened to arrive last, so one share of a doubly declared code was discarded
        # without a trace, and which share survived depended on arrival order. Measured on 30
        # September 2026 over the whole corpus, assigning gives 35,013,714,747 USD against
        # 38,152,946,330 accumulating, so the assignment understated the Global Fund HIV series
        # by 3,139,231,583 USD. The understatement is exactly zero for every year from 2002 to
        # 2016 and grows from 0.3 per cent in 2017 to 26.1 per cent in 2023, because the Global
        # Fund changed how it codes grant sectors in 2018, so the defect manufactured part of
        # the fall this panel exists to measure.
        #
        # Adding the shares is correct and does not double count. Across 2,726 Global Fund
        # activities declaring 4,721 sector rows, every activity's declared percentages sum to
        # exactly 100, all 113,777 transactions return exactly as many rows as their activity
        # declares sector rows with none surplus and none short, and on 113,774 of 113,774
        # transactions the percentages recovered from the shares match the declared percentages.
        groups: Dict[Tuple[str, int], Dict[str, float]] = defaultdict(dict)
        meta: Dict[Tuple[str, int], dict] = {}
        rows_per_tx: Dict[Tuple[str, int], int] = defaultdict(int)
        for row in self._qrows({"from": "trans,act", "reporting_ref": _GLOBAL_FUND_REF,
                                "trans_flags": 0,
                                "trans_code": f"{_MONEY_OUT_LETTERS}|{_REIMBURSEMENT_LETTER}",
                                "select": "aid,trans_id,trans_day,trans_code,trans_sector,"
                                          "trans_country,trans_usd"}):
            aid = row.get("aid") or ""
            key = (aid, row.get("trans_id"))
            # Counted before the value test, because `_check_apportionment` compares what
            # d-portal returned against what the activity declared, and a row carrying no
            # value is still a row d-portal returned.
            rows_per_tx[key] += 1
            usd = _float(row.get("trans_usd"))
            if usd is None:
                continue
            sector = str(row.get("trans_sector") or "")
            groups[key][sector] = groups[key].get(sector, 0.0) + usd
            meta.setdefault(key, {"day": row.get("trans_day"),
                                  "code": row.get("trans_code"),
                                  "country": row.get("trans_country")})

        self._check_apportionment(rows_per_tx)

        totals: Dict[Tuple[str, int], float] = defaultdict(float)
        share_13040: Dict[Tuple[str, int], float] = defaultdict(float)
        share_12110: Dict[Tuple[str, int], float] = defaultdict(float)
        share_12263: Dict[Tuple[str, int], float] = defaultdict(float)
        share_other: Dict[Tuple[str, int], float] = defaultdict(float)
        not_counted: Dict[Tuple[str, int], float] = defaultdict(float)
        reimbursed: Dict[Tuple[str, int], float] = defaultdict(float)
        grants: Dict[Tuple[str, int], Set[str]] = defaultdict(set)
        whole_grant_years: Set[Tuple[str, int]] = set()
        no_country = defaultdict(float)
        unresolved = defaultdict(float)
        excluded_money = 0.0

        for (aid, _tid), members in groups.items():
            if aid in covid_excluded:
                excluded_money += sum(members.values())
                continue
            info = meta[(aid, _tid)]
            when = _day_to_date(info["day"])
            if when is None:
                continue
            if when.year < start_year or when.year > end_year:
                continue
            code = (info.get("country") or "").strip()
            if not code:
                # The 142 Global Fund activities with no country row are the regional and
                # multi-country grants. Item 17(j) logs the money and writes none of it,
                # because splitting a regional grant across the region's countries would be
                # this connector inventing a geography the publisher did not state.
                no_country[aid.split("-")[1] if len(aid.split("-")) > 1 else "?"] += sum(members.values())
                continue
            iso3 = _any_code_to_iso3(code)
            if iso3 is None:
                unresolved[code] += sum(members.values())
                continue
            if wanted and iso3 not in wanted:
                continue
            key = (iso3, when.year)
            grants[key].add(aid)
            if info.get("code") == _REIMBURSEMENT_LETTER:
                reimbursed[key] += sum(members.values())
                continue
            # Adding the shares reaches the whole transaction, and reaches it exactly, because
            # every Global Fund activity's declared sector percentages sum to 100 and d-portal
            # returns one row per declared sector row. `members` holds the accumulated share
            # per sector code, so `sum(members.values())` is the transaction and
            # `members.get(_HIV)` is the transaction's whole HIV share even where the activity
            # declares 13040 more than once.
            #
            # Item 26. The four sector keys describe the money the row carries and nothing
            # else, so that a reader who adds the four keys reaches the row's value. An H or
            # C grant enters the value whole, so every sector's share of that transaction
            # belongs in the keys, and `share_other` carries the part of it declared under a
            # purpose code that none of the three named keys holds. Any other grant enters
            # the value at its purpose-13040 share alone, so only `share_13040` takes money
            # from it, and the remainder of that transaction is money this connector saw and
            # did not count, recorded in `not_counted` and standing outside the value.
            #
            # Before this repair all three named keys took money from every grant while the
            # value took the whole of H and C grants and the purpose-13040 share of the rest,
            # so on the panel of 30 September 2026 the keys exceeded the value by
            # 15,801,029,329 USD on 1,745 of the 1,905 rows and a reader adding the keys
            # reached a figure the panel does not assert.
            #
            # `share_13040` takes `members.get(_HIV, 0.0)` on both branches, exactly as it did
            # before this repair, so the `measured` test below reads the same figure and no
            # country-year moves between carrying a value and carrying None.
            whole = sum(members.values())
            hiv_part = members.get(_HIV, 0.0)
            share_13040[key] += hiv_part
            if _is_hc_grant(aid):
                totals[key] += whole
                whole_grant_years.add(key)
                policy_part = members.get("12110", 0.0)
                tb_part = members.get("12263", 0.0)
                share_12110[key] += policy_part
                share_12263[key] += tb_part
                share_other[key] += whole - hiv_part - policy_part - tb_part
            else:
                totals[key] += hiv_part
                not_counted[key] += whole - hiv_part

        # Item 37, approved on 1 October 2026 as option three with option one's counter. The
        # writing loop used to run over `totals`, and the reimbursement branch above adds to
        # `reimbursed` and continues before `totals[key]` is ever touched, so a country-year
        # whose every Global Fund transaction was a reimbursement created no key in `totals`,
        # was written nowhere and appeared in no log line. `grants[key].add(aid)` runs above
        # that branch, so `grants` holds every country-year the connector saw after every
        # filter, and `set(grants)` is `set(totals) | set(reimbursed)` by construction. The
        # loop now runs over `grants`, which keeps item 24's convention, namely that a
        # country-year the connector saw without measuring HIV money is kept with no value
        # and a stated reason instead of vanishing from the series.
        #
        # Every row the repair adds carries no value, because a country-year reached by
        # reimbursement alone entered neither `whole_grant_years` nor `share_13040`, so the
        # `measured` test below reads False on every one of those country-years and no figure
        # already in the panel moves.
        #
        # `latest` is taken over `grants` for the same reason, because the latest year the
        # connector saw is the year `partial_year` describes. The year taken over `grants`
        # differs from the year taken over `totals` only where a country-year reached by
        # reimbursement alone sits later than every country-year carrying a value, and in
        # that case the year taken over `totals` was not the latest year the connector saw.
        only_reimbursement_keys = set(grants) - set(totals)
        latest = max((y for _, y in grants), default=end_year)
        written = 0
        unmeasured = 0
        unmeasured_crs = 0.0
        # Item 26. The repair above is meant to hold an invariant, namely that the four
        # sector keys add to the value on every row that carries a value, and an invariant
        # nobody measures is a hope. The run counts the rows that break the invariant and
        # logs the count and the largest disagreement, so a reviewer reads the answer off
        # the log instead of recomputing it from the panel.
        #
        # Item 29. Two counts are kept, because the accumulators and the written keys can
        # disagree with the value for two different reasons and only one of the two is a
        # defect. `key_mismatch` counts the country-years whose unrounded accumulators
        # stand more than a cent from the value, which is an accounting defect and is what
        # the item 26 check was built to catch. `file_mismatch` counts the rows whose four
        # written keys do not add to the written value to the cent, which is what a reader
        # of the panel can test. The first version of the check reported only the first
        # count, read 0.00 USD on the run of 30 September 2026, and said nothing about the
        # file that run wrote, where the four keys stood a cent from the value on 212 of
        # the 2,385 rows carrying a value.
        key_mismatch = 0
        file_mismatch = 0
        worst_gap = 0.0
        # Item 31. The country-years written with no value whose only HIV transactions were
        # reimbursements, counted apart from the rest, because the two carry different stated
        # reasons and the log line below used to assert the wrong one of the two for both.
        reimbursement_only = 0
        # Item 37. The rows the repair adds, counted so that the run log states how many
        # country-years the Global Fund reached by reimbursement alone. The count cannot be
        # read off any earlier panel, because those country-years were written nowhere.
        only_reimbursement_written = 0
        for (iso3, year) in sorted(grants):
            # Item 24. `totals` is a defaultdict and the else branch above runs
            # `totals[key] += 0.0` for every non-HC transaction carrying no purpose-13040
            # money, so a country-year in which the Global Fund moved only malaria or TB
            # money created a key here and used to be written as a row of value zero. A zero
            # in this series reads as "the Global Fund disbursed nothing for HIV to this
            # country in this year", which for Zimbabwe in 2019 is false. OECD CRS records
            # 122,147,155 USD for Zimbabwe in 2019, and the connector had simply seen no
            # HIV-coded Global Fund transaction for Zimbabwe that year.
            #
            # The full run of 28 September 2026 wrote 424 such rows out of 2,148, and OECD
            # CRS reports 5,097,904,760 USD against 265 of the 424.
            #
            # schema.py line 60 states the panel's own convention for this case, namely that
            # a value of None means the source reported no value and that the row is kept
            # and not dropped. A country-year whose value the connector measured carries the
            # figure. A country-year the connector saw without measuring any HIV money
            # carries None and a stated reason. Dropping the rows instead would have removed
            # 424 country-years and emptied the Global Fund series for nine countries,
            # Angola, Bulgaria, Brazil, Egypt, Iraq, Panama, North Korea, Solomon Islands and
            # Turkmenistan, which hides the Global Fund's presence in a country rather than
            # reporting an unmeasured year.
            #
            # A country-year counts as measured when the connector took an H or C grant whole
            # or found purpose-13040 money in some other grant. A genuine zero inside an H or
            # C grant still carries the figure zero, because whole_grant_years records the
            # presence of the grant and not the amount.
            measured = ((iso3, year) in whole_grant_years
                        or bool(share_13040[(iso3, year)]))
            value = totals[(iso3, year)] if measured else None

            # Item 29. Each key is rounded to a cent and the value is written unrounded, so
            # four keys rounded on their own can add to a cent away from the value the four
            # are said to decompose. The three named keys are rounded as before and
            # `sector_other_usd` carries the remainder of the rounded value, so the four
            # keys add to the value to the cent on every row that carries a value.
            # `sector_other_usd` is the key that absorbs the rounding because
            # `sector_other_usd` is the only one of the four that names no purpose code and
            # that no limitation in docs/DOWNLOADS.md quotes on its own.
            #
            # The remainder is taken only where the accumulators already agree with the
            # value to a cent, which is the rounding case. A residual written unconditionally
            # would define the invariant to be true and would bury a real accounting defect
            # inside `sector_other_usd`, which is the opposite of what the check exists for.
            # Where the accumulators disagree with the value by more than a cent, the keys
            # stay as the accumulators state them, the row is counted, and the disagreement
            # reaches both the log and the file. A row carrying no value has no value to
            # take a remainder from, so the key there stays the rounded accumulator.
            k13040 = round(share_13040[(iso3, year)], 2)
            k12110 = round(share_12110[(iso3, year)], 2)
            k12263 = round(share_12263[(iso3, year)], 2)
            kother = round(share_other[(iso3, year)], 2)
            if value is not None:
                gap = (share_13040[(iso3, year)] + share_12110[(iso3, year)]
                       + share_12263[(iso3, year)] + share_other[(iso3, year)]) - value
                if abs(gap) > 0.01:
                    key_mismatch += 1
                    worst_gap = max(worst_gap, abs(gap))
                else:
                    kother = round(round(value, 2) - k13040 - k12110 - k12263, 2)
                if round(k13040 + k12110 + k12263 + kother - round(value, 2), 2):
                    file_mismatch += 1
            crs_value = crs.get((iso3, year))
            extra = {
                "note": "IATI disbursements and expenditures, whole value of H and C grants "
                        "plus the purpose-13040 share of the rest. The four sector keys add "
                        "to the value, sector_other_usd carrying the rounding remainder. "
                        "seen_not_counted_usd stands outside the value and "
                        "records the non-HIV part of the grants counted at their "
                        "purpose-13040 share alone.",
                "sector_13040_usd": k13040,
                "sector_12110_usd": k12110,
                "sector_12263_usd": k12263,
                "sector_other_usd": kother,
                "seen_not_counted_usd": round(not_counted[(iso3, year)], 2),
                "grant_identifiers": sorted(grants[(iso3, year)]),
                "whole_grant_basis": (iso3, year) in whole_grant_years,
                # Item 37. True where every Global Fund transaction this connector read for
                # the country-year was a reimbursement, which is the population the repair
                # made visible. The boolean carries the case so that the reconciliation layer
                # and the validation report select or exclude the case by reading one key,
                # instead of matching words inside value_missing_reason. The boolean stands
                # on every row of the series, False included, so a reader filtering on the
                # key does not mistake a row written before this repair for a row the case
                # does not cover.
                "only_reimbursements_seen": (iso3, year) in only_reimbursement_keys,
                "reimbursements_usd": round(reimbursed[(iso3, year)], 2),
                "same_reporter_as": "oecd_crs CRS.13040.9OTH012",
                "read_from": "d-portal query service, not the XML export",
            }
            if not measured:
                unmeasured += 1
                if crs_value:
                    unmeasured_crs += crs_value
                # Item 31, approved on 1 October 2026 as option two. The one reason this row
                # used to carry was false on 10 of the 192 unmeasured rows, because the
                # reason denied the row's own grant list. `grants[key].add(aid)` above runs
                # before the reimbursement branch, so a country-year whose only HIV
                # transactions were reimbursements lists an H or C grant on the row while
                # never entering `whole_grant_years`. A reimbursement is money returning to
                # the Global Fund, so writing no value there is the right answer and the
                # defect was in what the row said about the absence. Where an H or C grant
                # is named and the row is unmeasured, every transaction the connector read
                # for that grant was a reimbursement, because any other transaction of an H
                # or C grant reaches the branch that sets `whole_grant_years`.
                #
                # The 10 rows on the panel of 30 September 2026 are Botswana 2012, China
                # 2014, Côte d'Ivoire 2009, Colombia 2010, Guinea 2006, Indonesia 2007, Peru
                # 2015, Romania 2011, Romania 2013 and Suriname 2016, holding
                # -10,503,815.34 USD of reimbursements between them. No value on any of the
                # 10 moves, and what moves is what the panel tells a reader about why a
                # value is missing.
                #
                # Item 37. A country-year the repair added is tested first, because every
                # transaction the connector read for that country-year was a reimbursement
                # and both reasons below would describe the absence wrongly. The second
                # reason speaks of transactions belonging to an H or C grant, which these
                # country-years may have none of, and the third reason speaks of the Global
                # Fund moving money the connector did not count, which a reimbursement is
                # not, a reimbursement being money returning to the Global Fund.
                if (iso3, year) in only_reimbursement_keys:
                    only_reimbursement_written += 1
                    extra["value_missing_reason"] = (
                        "The Global Fund reported transactions for this country and year and "
                        "every one of them was a reimbursement, which is money returning to "
                        "the Global Fund and not a disbursement, so this connector measured "
                        "no HIV money. The reimbursement total stands in reimbursements_usd "
                        "and the grants are named in grant_identifiers. The value is absent "
                        "and not zero, because zero would assert a disbursement of nothing "
                        "that the Global Fund's own OECD CRS return often contradicts, and "
                        "the row is kept and not dropped, because dropping it would hide the "
                        "Global Fund's presence in the country in this year.")
                elif any(_is_hc_grant(aid) for aid in grants[(iso3, year)]):
                    reimbursement_only += 1
                    extra["value_missing_reason"] = (
                        "The Global Fund reported transactions for this country and year, "
                        "and every transaction belonging to an H or C grant was a "
                        "reimbursement, which is money returning to the Global Fund and not "
                        "a disbursement, while no other grant carried purpose code 13040, so "
                        "this connector measured no HIV money. The reimbursement total "
                        "stands in reimbursements_usd and the grants are named in "
                        "grant_identifiers. The value is absent and not zero, because zero "
                        "would assert a disbursement of nothing that the Global Fund's own "
                        "OECD CRS return often contradicts.")
                else:
                    extra["value_missing_reason"] = (
                        "The Global Fund reported transactions for this country and year, "
                        "and none of them was an H or C grant or carried purpose code 13040, "
                        "so this connector measured no HIV money. The value is absent and "
                        "not zero, because zero would assert a disbursement of nothing that "
                        "the Global Fund's own OECD CRS return often contradicts.")
                # Item 31. `grants_seen_but_not_hiv_coded` is gone. The key was written as
                # `sorted(grants[(iso3, year)])`, which is the identical list the same row
                # already carries under `grant_identifiers`, and the key's name asserted
                # something about the list that the list does not satisfy, because the list
                # includes H and C grants on the rows above. Checked against the panel of 30
                # September 2026, the two lists are identical on all 192 rows carrying the
                # key and all 169 distinct identifiers inside the dropped key also appear in
                # `grant_identifiers`, so dropping the key loses nothing.
            if crs_value is not None:
                extra["oecd_crs_usd"] = round(crs_value, 2)
                extra["ratio_to_oecd_crs"] = (
                    round(value / crs_value, 4)
                    if value is not None and crs_value else None)
            if year == latest:
                extra["partial_year"] = True
            if value is not None and value < 0:
                extra["net_negative"] = True
            yield self.make_row(
                country_iso3=iso3,
                country_name=name_for(iso3),
                indicator_id=_SERIES_GLOBAL_FUND,
                year=year,
                value=value,
                unit="USD",
                source_url=f"{_Q}?from=trans,act&reporting_ref={_GLOBAL_FUND_REF}&form=json",
                source_indicator_code=f"IATI.{_GLOBAL_FUND_REF}.{_HIV}",
                extra=extra,
            )
            written += 1

        log.info("iati: global fund -> %d country-year rows", written)
        valued = written - unmeasured
        log.info("iati: global fund — the four sector accumulators agree with the value on "
                 "%d of the %d row(s) carrying a value, largest disagreement %.2f USD. As "
                 "written to the panel, the four rounded keys add to the rounded value on "
                 "%d of those %d row(s). A further %.2f USD across the series is money seen "
                 "and not counted, the non-HIV part of the grants counted at their "
                 "purpose-13040 share alone.",
                 valued - key_mismatch, valued, worst_gap,
                 valued - file_mismatch, valued, sum(not_counted.values()))
        if unmeasured:
            # Item 31. The reasons are counted and logged apart, because a country-year whose
            # only HIV transactions were reimbursements saw an H or C grant and is not a
            # country-year where the Global Fund moved only non-HIV money, and the single
            # sentence this line used to print asserted the second of the two for both.
            #
            # Item 37. A third count joins them, being the country-years the Global Fund
            # reached by reimbursement alone, which no earlier run could report because the
            # rows were written nowhere. The three counts add to the unmeasured total.
            log.info("iati: global fund — %d of those %d country-year(s) carry no value and "
                     "a zero would have asserted a disbursement of nothing. OECD CRS reports "
                     "%.2f USD against the %d. On %d of the %d the Global Fund moved only "
                     "non-HIV money, on %d every transaction belonging to an H or C grant was "
                     "a reimbursement, and on %d every transaction of any kind was a "
                     "reimbursement.",
                     unmeasured, written, unmeasured_crs, unmeasured,
                     unmeasured - reimbursement_only - only_reimbursement_written,
                     unmeasured, reimbursement_only, only_reimbursement_written)
        if excluded_money:
            log.info("iati: global fund — %.2f USD excluded by the COVID rule", excluded_money)
        if no_country:
            log.info("iati: global fund — %.2f USD in %d regional or multi-country grant "
                     "group(s) written nowhere: %s", sum(no_country.values()), len(no_country),
                     ", ".join(f"{k}({v:,.0f})" for k, v in sorted(no_country.items())))
        if unresolved:
            log.info("iati: global fund — %d country code(s) refused by the strict lookup: %s",
                     len(unresolved),
                     ", ".join(f"{c}({v:,.0f} USD)" for c, v in sorted(unresolved.items())))

    def _crs_lookup(self) -> Dict[Tuple[str, int], float]:
        """The Global Fund's CRS disbursements, for the comparison item 17(e) asks for.

        Read through OECDCRSConnector so the two figures come from the same call the panel
        already trusts, and guarded so that a CRS outage costs the run a log line and not
        the IATI series.
        """
        out: Dict[Tuple[str, int], float] = {}
        try:
            from .oecd_crs import OECDCRSConnector
            crs = OECDCRSConnector()
            for row in crs.fetch(start_year=2000):
                if row.indicator_id == _SERIES_GLOBAL_FUND and row.value is not None:
                    out[(row.country_iso3, row.year)] = row.value
        except Exception as exc:
            log.warning("iati: the OECD CRS comparison is unavailable this run: %s", exc)
        return out

    # ----------------------------------------------------------------------------------
    # every other publisher, items 17(a) to (d) and (f) to (n)
    # ----------------------------------------------------------------------------------

    @staticmethod
    def _funders(act: ET.Element, reporter_ref: str) -> List[Tuple[str, str]]:
        """Every organisation an activity names as a funder, other than the publisher.

        The exemption for the publisher's own reference is the difference between a working
        rule and a rule that deletes its own subject. The Global Fund names itself as a
        role-1 funder on its own grants, so a pass-through rule that tested every named
        funder would have excluded all 1,246 Global Fund activities from the Global Fund's
        own series.
        """
        out = []
        for org in _children(act, "participating-org"):
            if (org.get("role") or "").strip() != "1":
                continue
            ref = (org.get("ref") or "").strip().upper()
            if ref and ref == reporter_ref:
                continue
            out.append((ref, _narrative(org).upper()))
        return out

    @staticmethod
    def _is_global_fund(ref: str, name: str) -> bool:
        return ref in _GLOBAL_FUND_ALIASES or _GLOBAL_FUND_NAME in name

    @staticmethod
    def _is_us_gov(ref: str, name: str) -> bool:
        if ref.startswith(_US_GOV_PREFIX) or ref in _US_GOV_REFS:
            return True
        return any(n in name for n in _US_GOV_NAMES)

    def _sector_share(self, sectors: List[ET.Element], code: str) -> Optional[float]:
        """The share of a transaction belonging to one purpose code.

        Only vocabulary 1, the OECD DAC five-digit purpose list, or no stated vocabulary
        counts, because a publisher using its own vocabulary can code anything as 13040 and
        mean something else by it. Shares are taken over the pool of the sectors that
        survive that filter, so a file whose percentages sum to 93 or to 99 still allocates
        the whole transaction and does not quietly lose 7 per cent of the money.
        """
        usable = [s for s in sectors if (s.get("vocabulary") or "1") in ("", "1")]
        if not usable:
            return None
        percentages = [_float(s.get("percentage")) for s in usable]
        if all(p is None for p in percentages):
            # Several sectors and not one percentage between them. An equal split is the only
            # reading the file supports, and across 3,962 sampled activities from 23
            # publishers this case arose zero times, so no figure in the panel depends on it.
            matches = sum(1 for s in usable if (s.get("code") or "").strip() == code)
            return matches / len(usable)
        pool = sum(p for p in percentages if p is not None)
        if not pool:
            return None
        hit = sum(p for s, p in zip(usable, percentages)
                  if p is not None and (s.get("code") or "").strip() == code)
        return hit / pool

    def _geography(self, countries: List[ET.Element], regions: List[ET.Element],
                   ) -> Tuple[List[Tuple[str, float]], float, float, Optional[str]]:
        """Split a transaction across the countries an activity names.

        Returns the country shares, the share belonging to a named region, the share whose
        destination the publisher did not name at all, and a reason string when the
        transaction cannot be allocated. A country's share is its own percentage over the sum
        of every country and region percentage, so money a publisher assigned to a region
        stays with the region and is reported rather than being spread over whichever
        countries happened to be named beside it.

        A recipient element carrying a percentage and no code keeps its place in the pool and
        is reported as unnamed. Two publishers file such elements, UNICEF on 67 activities of
        906 and the Swiss Agency for Development and Cooperation (`CH-4`) on seven of 200,
        counted over the whole cached export on 30 September 2026. Each of UNICEF's 67 files
        both `<recipient-country percentage="100"/>` and `<recipient-region percentage="100"/>`
        with no code on either, and no country share comes back for any of the 67, so nothing
        in a UNICEF activity of that shape names a country. Six of the seven Swiss activities
        also name a coded country, so a Swiss unnamed share is part of a transaction and not
        the whole of it. An earlier version of this docstring said 34 activities and named
        UNICEF alone, which was the count over the one page a publisher the survey sampled.
        Dropping those elements from the pool instead would hand their share to whichever
        country was named beside them, which is the one outcome worse than writing nothing,
        because a country would gain money no publisher ever assigned to it.

        The two branches that refuse to allocate, several countries with no percentages and
        several countries with only some, fired zero times across 3,962 activities from 23
        publishers. They are guards against a publisher that has not done it yet.
        """
        # Item 22. A DAC region code filed into the country element is region money, not a
        # country code the resolver failed on. CH-4 files 289, 298 and 998 this way, and
        # XM-DAC-21-1 files 998. Moving those elements to the region pool here is what makes
        # the run log's refused-code line mean what it says, namely a destination nobody can
        # determine, instead of mixing in destinations the publisher stated perfectly well.
        coded = [c for c in countries
                 if (c.get("code") or "").strip()
                 and (c.get("code") or "").strip().upper() not in _DAC_REGIONAL]
        misfiled_regions = [c for c in countries
                            if (c.get("code") or "").strip().upper() in _DAC_REGIONAL]
        uncoded = [c for c in countries if not (c.get("code") or "").strip()]
        coded_regions = [r for r in regions if (r.get("code") or "").strip()] + misfiled_regions
        uncoded += [r for r in regions if not (r.get("code") or "").strip()]

        if not coded and not coded_regions and not uncoded:
            return [], 0.0, 0.0, "no geography stated"
        if not coded:
            named = sum(_float(r.get("percentage")) or 0.0 for r in coded_regions)
            unnamed = sum(_float(u.get("percentage")) or 0.0 for u in uncoded)
            if not named and not unnamed:
                return [], 1.0, 0.0, None
            pool = named + unnamed
            return [], named / pool, unnamed / pool, None

        cpct = [_float(c.get("percentage")) for c in coded]
        rpct = [_float(r.get("percentage")) for r in coded_regions]
        upct = [_float(u.get("percentage")) for u in uncoded]
        if len(coded) == 1 and cpct[0] is None:
            if coded_regions or uncoded:
                return [], 0.0, 0.0, "one country with no percentage beside another recipient"
            return [((coded[0].get("code") or "").strip(), 1.0)], 0.0, 0.0, None
        if any(p is None for p in cpct):
            if all(p is None for p in cpct):
                return [], 0.0, 0.0, "several countries, none with a percentage"
            return [], 0.0, 0.0, "several countries, only some with a percentage"
        pool = (sum(cpct) + sum(p for p in rpct if p is not None)
                + sum(p for p in upct if p is not None))
        if not pool:
            return [], 0.0, 0.0, "recipient percentages sum to zero"
        shares = [((c.get("code") or "").strip(), p / pool) for c, p in zip(coded, cpct)]
        region_share = sum(p for p in rpct if p is not None) / pool
        unnamed_share = sum(p for p in upct if p is not None) / pool
        return shares, region_share, unnamed_share, None

    def _publisher_rows(self, ref: str, wanted: Optional[Set[str]],
                        start_year: int, end_year: int,
                        buckets: Dict[Tuple[str, str, int], Dict[str, float]],
                        detail: Dict[Tuple[str, str, int], Dict[str, float]],
                        tally: Dict[str, float],
                        assumed: Optional[Dict[Tuple[str, str, int], dict]] = None) -> None:
        """Read one publisher's XML into the shared country-year buckets.

        `assumed` collects item 30's record of every country-year holding money converted at
        a currency the publisher did not state on the transaction, keyed by the row and then
        by the publisher. The parameter defaults to None so a read-only replay of one
        publisher can call this method with the six arguments the method took before item 30.
        """
        # The organisation type decides which of the three series a publisher belongs to, and
        # a publisher belonging to none of the three is never written. Reading the type from
        # the first page alone, before any other page is fetched, is what keeps the NGOs,
        # companies and academic bodies among the 95 publishers from costing a download each.
        org_type = self._org_type(ref)
        series = None
        if org_type in _BILATERAL_TYPES:
            series = _SERIES_BILATERAL
        elif org_type in _MULTILATERAL_TYPES and ref not in _GLOBAL_FUND_ALIASES:
            series = _SERIES_MULTILATERAL
        elif org_type in _FOUNDATION_TYPES:
            series = _SERIES_FOUNDATION
        if series is None:
            tally[f"type {org_type or 'unstated'} ({_TYPE_LABELS.get(org_type, 'unclassified')})"] += 1
            log.info("iati: %s — organisation type %s (%s), read and not written",
                     ref, org_type or "unstated", _TYPE_LABELS.get(org_type, "unclassified"))
            return

        # Pass one. Fingerprint every transaction so item 17(k) can tell a parent restating
        # a child's transactions from a parent spending money of its own. A fingerprint is
        # the day, the value, the currency and the type, which is everything the two files
        # would have to agree on for the money to be the same money.
        #
        # The two passes each walk the publisher's pages from the generator instead of from a
        # list, and the second pass reads the pages the first pass left in the cache, so no
        # page is fetched twice and no publisher's whole file is ever held in memory. Sweden
        # alone is about 364 MB of XML, which a list would have loaded in full.
        fingerprints: Dict[str, Set[tuple]] = {}
        declared_children: Dict[str, Set[str]] = {}
        secondary = 0
        # Item 30. Every currency this publisher states on a transaction of its own, counted,
        # so pass two can tell a publisher that states one currency everywhere from a
        # publisher that states several or none. A secondary reporter's activities are
        # skipped below before anything is counted, which is right here too, because a
        # secondary reporter files on another body's behalf and the currency those
        # activities state is not evidence about this publisher.
        currencies_stated: Dict[str, int] = defaultdict(int)
        for _path, body in self._xml_pages(ref):
            try:
                root = ET.fromstring(body)
            except ET.ParseError:
                continue
            for act in root:
                ident = _narrative(next(iter(_children(act, "iati-identifier")), None))
                if not ident:
                    continue
                reporting = next(iter(_children(act, "reporting-org")), None)
                if reporting is not None and (reporting.get("secondary-reporter") or "0").strip() == "1":
                    secondary += 1
                    continue
                prints = set()
                for tx in _children(act, "transaction"):
                    tcode = next(iter(_children(tx, "transaction-type")), None)
                    tval = next(iter(_children(tx, "value")), None)
                    tdate = next(iter(_children(tx, "transaction-date")), None)
                    if tval is None:
                        continue
                    prints.add(((tcode.get("code") if tcode is not None else ""),
                                (tdate.get("iso-date") if tdate is not None else ""),
                                _amount(tval), tval.get("currency")))
                    stated = (tval.get("currency") or "").strip().upper()
                    if stated:
                        currencies_stated[stated] += 1
                fingerprints[ident] = prints
                kids = {(r.get("ref") or "").strip()
                        for r in _children(act, "related-activity")
                        if (r.get("type") or "").strip() == "2"}
                if kids:
                    declared_children[ident] = kids

        if secondary:
            # Item 17(n). A secondary reporter is a body filing on someone else's behalf, so
            # its activity is a second copy of an activity the original publisher also files.
            log.info("iati: %s — %d secondary-reporter activity(ies) skipped", ref, secondary)
        if not fingerprints:
            return

        # Item 30, the inference Jason approved on 1 October 2026, option two with option one
        # as the fallback. A publisher that states one currency and no other on every
        # transaction the publisher files has the transactions that state no currency
        # converted at that currency, and the row records the currency, the money resting on
        # the inference and the number of the publisher's own transactions the inference
        # rests on, so a reader can reverse the inference. A publisher that states no
        # currency anywhere, or states more than one, has the transaction refused, which is
        # option one, because no currency can be inferred from a file that does not agree
        # with itself.
        #
        # The population is every transaction in this publisher's cached file that states a
        # currency, measured over the cache of 30 September 2026. The evidence is unanimous
        # for both affected publishers, the Ministry for Foreign Affairs of Finland stating
        # EUR on 68 transactions and nothing else beside 75 stating no currency, and Irish
        # Aid stating EUR on 217 beside 38 stating no currency. Neither publisher states a US
        # dollar anywhere in the file, which is the currency both publishers' blank
        # transactions used to enter the panel as.
        #
        # Two publishers file the same shape and are never written. The Indigo Trust
        # (`GB-CHC-1075920`) states no currency on either of its two transactions, so the
        # inference refuses and option one takes 5,774.91 USD out of the foundation series,
        # which `_WRITE_FOUNDATION` holds back in any case. Plan International USA
        # (`US-IRS-13-5661832`) states USD once beside four transactions stating nothing, so
        # the inference would fire on an evidence count of one and would write the dollars
        # the old code wrote, and organisation type 21 means no series takes the publisher at
        # all. The evidence count is written onto every affected row, so a reader meeting a
        # count of one can judge the inference as weak without reading this comment.
        sole_currency: Optional[str] = None
        sole_currency_count = 0
        if len(currencies_stated) == 1:
            sole_currency, sole_currency_count = next(iter(currencies_stated.items()))

        # Pass two. Allocate and sum.
        counters = defaultdict(int)
        money = defaultdict(float)
        # Item 30. Held apart from `money`, because every label in `money` is a dollar figure
        # and this one is a bare number in a currency nobody stated, so the dollar suffix the
        # money log prints would assert the very thing the refusal refused to assume.
        refused_undetermined = 0.0
        # Item 38, approved on 1 October 2026 as option two with option three's label
        # correction. Held apart from `money` and keyed on the currency the file states,
        # because the reimbursement branch stands above item 30's currency ladder and
        # converts nothing, so a single total printed through the money log carried a USD
        # suffix on a figure this connector never converted.
        reimbursements: Dict[str, float] = defaultdict(float)
        summed: Set[str] = set()
        repeats = 0
        passthrough_any = passthrough_sole = passthrough_kept = 0
        for _path, body in self._xml_pages(ref):
            try:
                root = ET.fromstring(body)
            except ET.ParseError:
                continue
            # Item 30. The IATI standard lets a publisher state the currency once on the
            # file root or once on the activity instead of on every transaction, so the
            # currency is read from the file before anything about the file is inferred.
            # Neither attribute carries a currency on any of the activities affected in the
            # cache of 30 September 2026, so reading both rungs changes no figure in that
            # cache and stops a stated currency being overridden by an inference the day a
            # publisher starts stating one.
            root_default = (root.get("default-currency") or "").strip().upper()
            for act in root:
                ident = _narrative(next(iter(_children(act, "iati-identifier")), None))
                if not ident or ident not in fingerprints:
                    continue
                act_default = (act.get("default-currency") or "").strip().upper()
                # Item 28. `_xml_pages` asks d-portal for `from=act,sector` with
                # `sector_code=13040`, which joins the activity table to the sector table, so
                # d-portal serves one complete copy of the activity per joined row and an
                # activity declaring purpose code 13040 twice under vocabulary 1 arrives
                # twice. The membership test above asks whether the identifier is known, not
                # whether the identifier has already been summed, and the money below adds,
                # so before this guard every copy's transactions were counted again. Pass one
                # was never affected, because pass one assigns into `fingerprints` and a
                # repeat overwrites.
                #
                # The cache of 30 September 2026 holds 71 surplus copies across 11,698
                # activity elements, in three publishers, and the effect on a single country
                # is nothing like the effect on the aggregate. Australia's whole contribution
                # to Cambodia was doubled in nine years between 2009 and 2020, Kenya's
                # multilateral row moved in four years, and one of those four was understated
                # and not overstated, so the direction is not uniform either.
                #
                # The identifier is the whole of the test. Every repeated copy in the cache is
                # byte-identical to the copy already served, so skipping a repeat cannot lose
                # money. The set lives outside the page loop because nothing in the query
                # holds the copies of one activity inside a single page, and a set rebuilt per
                # page would let a repeat through wherever the copies fell either side of an
                # offset. No repeat in the cache of 30 September 2026 straddles two pages, so
                # the placement changed no figure in the run of that date and guards a case
                # the query permits and the cache does not happen to contain. What a page
                # boundary was observed to do is the opposite of a repeat, namely serve an
                # activity once whose second join row fell past the limit, which is what
                # GB-CHC-285776's single page of exactly 300 join rows holds.
                if ident in summed:
                    repeats += 1
                    continue
                summed.add(ident)
                reporting = next(iter(_children(act, "reporting-org")), None)
                reporter_ref = (reporting.get("ref") or "").strip().upper() if reporting is not None else ""

                title = _narrative(next(iter(_children(act, "title")), None)).upper()
                if ("COVID" in title or "CORONAVIRUS" in title) and "HIV" not in title and "AIDS" not in title:
                    counters["excluded, COVID title naming neither HIV nor AIDS"] += 1
                    continue

                funders = self._funders(act, reporter_ref)
                hits = [(r, n) for r, n in funders
                        if self._is_global_fund(r, n) or self._is_us_gov(r, n)]
                receivers_gf = any(
                    self._is_global_fund((o.get("ref") or "").strip().upper(), _narrative(o).upper())
                    for o in _children(act, "participating-org")
                    if (o.get("role") or "").strip() == "4"
                    and (o.get("ref") or "").strip().upper() != reporter_ref)
                names_passthrough = False
                if hits or receivers_gf:
                    passthrough_any += 1
                    if len(hits) == len(funders) and funders:
                        passthrough_sole += 1
                    if _PASSTHROUGH_MODE == "any" or (len(hits) == len(funders) and funders) or receivers_gf:
                        counters["excluded, pass-through of Global Fund or US money"] += 1
                        continue
                    # Item 20 as settled at (g3). The activity survives because it names
                    # funders the panel does not already measure, and every row it feeds is
                    # stamped so the overlap with oecd_crs and foreign_assistance stays
                    # visible and countable instead of being silently dropped or silently
                    # kept.
                    names_passthrough = True
                    passthrough_kept += 1
                    counters["kept, names a pass-through funder alongside others"] += 1

                act_sectors = _children(act, "sector")
                act_countries = _children(act, "recipient-country")
                act_regions = _children(act, "recipient-region")
                child_prints = set()
                for kid in declared_children.get(ident, ()):
                    child_prints |= fingerprints.get(kid, set())

                for tx in _children(act, "transaction"):
                    tcode = next(iter(_children(tx, "transaction-type")), None)
                    code = (tcode.get("code") or "").strip() if tcode is not None else ""
                    tval = next(iter(_children(tx, "value")), None)
                    tdate = next(iter(_children(tx, "transaction-date")), None)
                    counters["transactions seen"] += 1
                    if tval is None:
                        counters["skipped, transaction with no value element"] += 1
                        continue
                    raw = _amount(tval)
                    if raw is None:
                        counters["skipped, value element with no readable amount"] += 1
                        continue
                    when = _iso_date(tval.get("value-date") or (tdate.get("iso-date") if tdate is not None else ""))
                    if when is None:
                        counters["skipped, transaction with no usable date"] += 1
                        continue
                    if code == _REIMBURSEMENT_CODE:
                        # Item 38. The branch stays here, above item 30's currency ladder and
                        # above the sector and geography tests, because a reimbursement on
                        # this path is logged and reaches no row, so nothing below the branch
                        # has any work to do on it. Nothing here is converted, so the amount
                        # is accumulated under the currency the file states for the
                        # transaction, taken from the transaction itself, then the activity's
                        # default currency, then the file's default currency, which are the
                        # three rungs of that ladder that read the file and never infer. An
                        # amount no part of the file states a currency for accumulates under
                        # the empty string and is logged as what it is.
                        #
                        # The two labels this branch used to write were both false on this
                        # path. The money label said "carried in extra, never subtracted",
                        # and the words were borrowed from the Global Fund branch, which does
                        # write reimbursements_usd onto a row, while a publisher reimbursement
                        # reaches no row and no `extra`. The counter repeated the same words.
                        # The counter now says only that the reimbursement was read and
                        # written nowhere, and counts every reimbursement the publisher filed
                        # whatever currency the file stated.
                        reimb_currency = (tval.get("currency") or "").strip().upper()
                        if not reimb_currency:
                            reimb_currency = act_default or root_default
                        reimbursements[reimb_currency] += raw
                        counters["reimbursement, read and written nowhere"] += 1
                        continue
                    if code not in _MONEY_OUT_CODES:
                        counters[f"skipped, transaction type {code or 'unstated'} is not money out"] += 1
                        continue
                    if ((code, tdate.get("iso-date") if tdate is not None else "",
                         raw, tval.get("currency")) in child_prints):
                        counters["skipped, a parent restating a child's transaction"] += 1
                        continue
                    if when.year < start_year or when.year > end_year:
                        counters["skipped, outside the requested years"] += 1
                        continue

                    sectors = _children(tx, "sector") or act_sectors
                    hiv_share = self._sector_share(sectors, _HIV)
                    if hiv_share is None:
                        counters["skipped, no sector in vocabulary 1"] += 1
                        continue
                    related_share = self._sector_share(sectors, _HIV_RELATED) or 0.0

                    tx_countries = _children(tx, "recipient-country") or act_countries
                    tx_regions = _children(tx, "recipient-region") or act_regions
                    shares, region_share, unnamed_share, refusal = self._geography(
                        tx_countries, tx_regions)
                    if refusal:
                        counters[f"skipped, {refusal}"] += 1
                        continue

                    # Item 30. Four rungs, taken in order, and a refusal at the bottom. The
                    # currency the transaction states, then the currency the activity states
                    # as its default, then the currency the file states as its default, then
                    # the only currency the publisher states anywhere, and a refusal where
                    # the publisher states no currency anywhere or states more than one. The
                    # first three rungs read the file and the fourth infers, so only the
                    # fourth is written onto the row.
                    currency = (tval.get("currency") or "").strip().upper()
                    basis = "stated on the transaction"
                    if not currency and act_default:
                        currency, basis = act_default, "the activity's default currency"
                    if not currency and root_default:
                        currency, basis = root_default, "the file's default currency"
                    inferred = False
                    if not currency and sole_currency:
                        currency, basis = sole_currency, "the publisher's only stated currency"
                        inferred = True
                    if not currency:
                        counters["refused, no currency stated on the transaction, the activity "
                                 "or the file, and the publisher states no single currency "
                                 "to infer"] += 1
                        refused_undetermined += raw
                        continue

                    usd = self._to_usd(raw, currency, when)
                    if usd is None:
                        counters[f"skipped, no exchange rate for {currency}"] += 1
                        continue
                    if basis != "stated on the transaction":
                        counters[f"converted at {basis}, the transaction stating none"] += 1
                        # The whole converted transaction, before the sector share and the
                        # country split, so the figure is what the conversion touched and not
                        # what the panel carries. The part each row carries is written onto
                        # the row itself under `currency_assumed`.
                        money[f"converted at {basis}, the transaction stating none, whole "
                              f"transactions before the sector share and the country "
                              f"split"] += usd
                    if region_share:
                        money["assigned to a named region, written nowhere"] += usd * region_share * hiv_share
                    if unnamed_share:
                        money["recipient stated with no country or region code, written nowhere"] += (
                            usd * unnamed_share * hiv_share)

                    for code2, share in shares:
                        iso3 = _any_code_to_iso3(code2)
                        if iso3 is None:
                            counters[f"skipped, country code {code2!r} refused"] += 1
                            money[f"refused country code {code2!r}"] += usd * share * hiv_share
                            continue
                        if wanted and iso3 not in wanted:
                            counters["skipped, outside the requested countries"] += 1
                            continue
                        key = (iso3, series, when.year)
                        buckets[key][ref] = buckets[key].get(ref, 0.0) + usd * share * hiv_share
                        detail[key]["value"] = detail[key].get("value", 0.0) + usd * share * hiv_share
                        detail[key]["related_16064_usd"] = (
                            detail[key].get("related_16064_usd", 0.0) + usd * share * related_share)
                        if names_passthrough:
                            # Set even when the amount is zero, because the row builder tests
                            # for the key's presence and a zero-value contribution still means
                            # the row draws on an activity naming an excluded funder.
                            detail[key]["passthrough_funder_usd"] = (
                                detail[key].get("passthrough_funder_usd", 0.0)
                                + usd * share * hiv_share)
                        if inferred and assumed is not None:
                            # Item 30. One entry per publisher, because a country-year takes
                            # money from several publishers and a reader reversing the
                            # inference needs to know which publisher's money rests on it and
                            # how much. The evidence count belongs to the publisher and not to
                            # the row, so the count is written once per publisher and not
                            # accumulated.
                            book = assumed.setdefault(key, {})
                            entry = book.setdefault(ref, {
                                "currency": sole_currency,
                                "usd": 0.0,
                                "publisher_transactions_stating_that_currency":
                                    sole_currency_count,
                            })
                            entry["usd"] += usd * share * hiv_share
                        counters["written"] += 1

        summary = ", ".join(f"{k} {v}" for k, v in sorted(counters.items()))
        log.info("iati: %s (type %s -> %s): %s", ref, org_type, series, summary or "nothing")
        if repeats:
            # Item 28. The number belongs on every run, because what d-portal serves for a
            # joined query can change between runs and a reviewer should not have to scan the
            # page cache to find out how many copies the reader refused.
            log.info("iati: %s — %d repeated activity element(s) skipped, d-portal having "
                     "served one copy per declared purpose-13040 sector row", ref, repeats)
        for label, amount in sorted(money.items()):
            log.info("iati: %s — %s: %.2f USD", ref, label, amount)
        if refused_undetermined:
            # Item 30. No currency on the number, because the number's currency is what the
            # publisher failed to state. The figure is the sum of the refused amounts as the
            # file wrote them, so a reader can see the size of what was refused without being
            # told a currency the file never named.
            log.info("iati: %s — refused, amounts in an undetermined currency, written "
                     "nowhere, stated in no currency and so summed as the file wrote them: "
                     "%.2f", ref, refused_undetermined)
        for reimb_currency, amount in sorted(reimbursements.items()):
            # Item 38. One line per currency, with the currency named and no suffix added,
            # because this branch converts nothing and a single total carrying a USD suffix
            # asserted a currency the connector never resolved. The money reaches no row, so
            # the figure tells a reader the size of what the publisher filed and nothing about
            # what the panel holds.
            log.info("iati: %s — reimbursements the publisher filed, read and written "
                     "nowhere, stated in %s: %.2f", ref,
                     reimb_currency or "a currency no part of the file states", amount)
        if passthrough_any:
            # Item 20 is settled at (g3) and mode "sole" excludes the second number only.
            # Both numbers stay in the log, because the gap between them is the size of the
            # judgement that was made and a reviewer is entitled to see it on every run.
            log.info("iati: %s — pass-through rule, mode %r: %d activity(ies) name a Global "
                     "Fund or US funder, of which %d name no other funder and are excluded, "
                     "leaving %d kept and stamped", ref, _PASSTHROUGH_MODE, passthrough_any,
                     passthrough_sole, passthrough_kept)

    # ----------------------------------------------------------------------------------
    # item 17(d), the American comparison
    # ----------------------------------------------------------------------------------

    def _log_us_comparison(self, publishers: List[Tuple[str, int]],
                           start_year: int, end_year: int) -> None:
        """Log the American publishers' totals without writing a row of them.

        The United States already enters the panel twice, as OECD CRS donor USA and as
        ForeignAssistance.gov's own return, and a third measurement of the same money would
        be summed with the other two by anyone who forgot to filter on source_id. So the
        American publishers are read, compared and logged, and never written.

        The comparison is stated in fiscal years, October to September, because that is the
        unit Washington reports in and a calendar-year comparison against a fiscal-year
        series disagrees for reasons that have nothing to do with the data.
        """
        us_refs = [ref for ref, _ in publishers if ref.upper().startswith(_US_GOV_PREFIX)]
        if not us_refs:
            return
        by_fy: Dict[int, float] = defaultdict(float)
        by_cy: Dict[int, float] = defaultdict(float)
        for ref in us_refs:
            for row in self._qrows({"from": "trans,act", "reporting_ref": ref,
                                    "trans_sector": _HIV, "trans_flags": 0,
                                    "trans_code": _MONEY_OUT_LETTERS,
                                    "select": "trans_day,trans_usd"}):
                usd = _float(row.get("trans_usd"))
                when = _day_to_date(row.get("trans_day"))
                if usd is None or when is None or not (start_year <= when.year <= end_year):
                    continue
                by_cy[when.year] += usd
                by_fy[when.year + 1 if when.month >= 10 else when.year] += usd
        log.info("iati: US publishers read and not written (%s). Fiscal-year totals: %s",
                 ", ".join(us_refs),
                 ", ".join(f"FY{y} {v:,.0f}" for y, v in sorted(by_fy.items())))

        panel = Path("data/panel/hiv_panel.csv")
        if not panel.exists():
            log.info("iati: no panel on disk yet, so the foreign_assistance comparison is "
                     "deferred to the next run")
            return
        fa: Dict[int, float] = defaultdict(float)
        try:
            with panel.open(newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    if row.get("source_id") != "foreign_assistance":
                        continue
                    if row.get("indicator_id") != "external_hiv_oda_us":
                        continue
                    try:
                        fa[int(row["year"])] += float(row["value"])
                    except (KeyError, TypeError, ValueError):
                        continue
        except OSError as exc:
            log.warning("iati: could not read the panel for the US comparison: %s", exc)
            return
        lines = []
        for year in sorted(set(by_fy) & set(fa)):
            ratio = by_fy[year] / fa[year] if fa[year] else None
            lines.append(f"FY{year} iati {by_fy[year]:,.0f} vs foreign_assistance {fa[year]:,.0f}"
                         + (f" ({ratio:.2f}x)" if ratio else ""))
        log.info("iati: American money, the two measurements side by side: %s",
                 "; ".join(lines) if lines else "no overlapping years")

    # ----------------------------------------------------------------------------------
    # the entry point
    # ----------------------------------------------------------------------------------

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or date.today().year
        wanted = {c.strip().upper() for c in countries} if countries else None

        publishers = self._publishers()
        yield from self._global_fund(wanted, start_year, end_year, self._crs_lookup())
        self._log_us_comparison(publishers, start_year, end_year)

        others = [ref for ref, _ in publishers
                  if ref not in _GLOBAL_FUND_ALIASES
                  and not ref.upper().startswith(_US_GOV_PREFIX)]
        self._load_rates(others)

        buckets: Dict[Tuple[str, str, int], Dict[str, float]] = defaultdict(dict)
        detail: Dict[Tuple[str, str, int], Dict[str, float]] = defaultdict(dict)
        tally: Dict[str, float] = defaultdict(float)
        # Item 30. One entry per country-year that holds money converted at a currency the
        # publisher did not state on the transaction, filled by `_publisher_rows` and read by
        # the row builder below.
        assumed: Dict[Tuple[str, str, int], dict] = {}
        for ref in others:
            self._publisher_rows(ref, wanted, start_year, end_year, buckets, detail, tally,
                                 assumed)

        if tally:
            log.info("iati: publishers read and not written, by organisation type: %s",
                     ", ".join(f"{k} x{int(v)}" for k, v in sorted(tally.items())))

        # One row per country, series and year, with the publisher split inside `extra`.
        # One row per publisher would be a truer record and the duplicate validator would
        # reject every one of them, because the panel's row key ends at source_id and every
        # publisher here shares the source_id `iati`.
        latest = max((y for _, _, y in buckets), default=end_year)
        counts: Dict[str, int] = defaultdict(int)
        for (iso3, series, year) in sorted(buckets):
            if series == _SERIES_FOUNDATION and not _WRITE_FOUNDATION:
                counts["foundation, held unwritten"] += 1
                continue
            value = detail[(iso3, series, year)].get("value", 0.0)
            # Item 29. `by_publisher` accumulates the same money as the value, one publisher
            # at a time, and each publisher's figure is then rounded to a cent on its own,
            # so adding the publishers reaches a figure that can stand a cent or two from
            # the value. Measured on the panel of 30 September 2026, 439 of the 4,485
            # bilateral and multilateral rows are affected, 291 bilateral and 148
            # multilateral, the largest difference is 0.02 USD and the differences sum to
            # 4.41 USD across the series.
            #
            # The sector keys on the Global Fund rows absorb their rounding into
            # `sector_other_usd`, which names no purpose code, so absorbing there attributes
            # nothing to anybody. Every key here names a publisher, so the same treatment
            # would state that a named publisher disbursed a cent the publisher did not
            # publish. The note says what the figures are instead, and the value stays the
            # figure to quote.
            extra = {
                "note": "IATI disbursements and expenditures, purpose 13040, split by the "
                        "percentages each publisher stated. Each publisher figure is "
                        "rounded to a cent on its own, so adding the publishers can reach "
                        "a cent or two either side of the value. The value is the figure "
                        "to quote and the split is a reading of where the value came from.",
                "by_publisher": {k: round(v, 2) for k, v in
                                 sorted(buckets[(iso3, series, year)].items())},
                "related_16064_usd": round(detail[(iso3, series, year)].get("related_16064_usd", 0.0), 2),
            }
            if series in (_SERIES_BILATERAL, _SERIES_MULTILATERAL):
                extra["do_not_add_to"] = "external_hiv_oda_total"
                extra["overlap_note"] = (
                    "OECD CRS all official donors already counts this money on its own "
                    "annual basis, so this series is a faster and finer measurement of the "
                    "same flows and not an addition to them.")
            # Item 20 as settled at (g3). Both keys appear only on rows fed by an activity
            # naming the Global Fund or a US government body alongside funders the panel does
            # not otherwise measure. Filtering these rows out reproduces the strict rule
            # exactly, and the dollar figure bounds the overlap for anyone keeping them.
            if "passthrough_funder_usd" in detail[(iso3, series, year)]:
                extra["names_passthrough_funder"] = True
                extra["passthrough_funder_usd"] = round(
                    detail[(iso3, series, year)]["passthrough_funder_usd"], 2)
                extra["passthrough_note"] = (
                    "Part of this row comes from activities that also name the Global Fund "
                    "or a US government body as a funder, both of which the panel measures "
                    "separately through oecd_crs and foreign_assistance. The named amount "
                    "is the part at risk of overlapping those two sources.")
            # Item 30 as approved on 1 October 2026. The keys appear only on a row holding
            # money whose currency the publisher stated nowhere the file could be read, and
            # the named amount is the part of the row's value resting on the inference, so a
            # reader who rejects the inference can subtract the amount or drop the row.
            if (iso3, series, year) in assumed:
                extra["currency_assumed"] = {
                    publisher: {
                        "currency": entry["currency"],
                        "usd": round(entry["usd"], 2),
                        "publisher_transactions_stating_that_currency":
                            entry["publisher_transactions_stating_that_currency"],
                    }
                    for publisher, entry in sorted(assumed[(iso3, series, year)].items())
                }
                extra["currency_assumed_note"] = (
                    "Part of this row comes from transactions stating no currency, where "
                    "neither the activity nor the file states a default currency either. "
                    "The named amount was converted at the only currency the publisher "
                    "states anywhere in this export, and the count of the publisher's own "
                    "transactions stating that currency stands beside the amount, so a "
                    "reader can reverse the inference. A publisher stating no currency "
                    "anywhere, or stating more than one, has the transaction refused "
                    "instead and the refusal counted in the run log.")
            if year == latest:
                extra["partial_year"] = True
            if value < 0:
                extra["net_negative"] = True
            yield self.make_row(
                country_iso3=iso3,
                country_name=name_for(iso3),
                indicator_id=series,
                year=year,
                value=value,
                unit="USD",
                source_url=f"{_QXML}?from=act,sector&sector_code={_HIV}",
                source_indicator_code=f"IATI.{_HIV}.{series}",
                extra=extra,
            )
            counts[series] += 1
        log.info("iati: wrote %s", ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
                 or "no rows")
        if not _WRITE_FOUNDATION:
            log.info("iati: the foundation series is held unwritten pending the question of "
                     "whether OECD CRS's all-official-donor total already contains Gates "
                     "Foundation money. See RESUME.md item 17(f).")
