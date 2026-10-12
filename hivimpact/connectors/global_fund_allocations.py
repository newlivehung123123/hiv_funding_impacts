"""
Global Fund communicated allocations — what each country was told it may apply for.

Endpoint (open, no key, no login):
    https://fetch.theglobalfund.org/v4.2/odata/AllFinancialIndicators
        ?$filter=financialDataSet eq 'CommunicatedAllocation_ReferenceRate'
    https://fetch.theglobalfund.org/v4.2/odata/Geographies
    https://fetch.theglobalfund.org/v4.2/odata/ActivityAreas

WHAT THIS IS, AND WHY THE PANEL WANTS IT. A communicated allocation is the sum the Global
Fund tells one country it may apply for over one three-year cycle. An allocation is a
forward commitment and a disbursement is money that has already moved, so an allocation
and a disbursement answer different questions, and before this connector the panel
answered only the disbursement question. The dataset already carries the 2026-2028 cycle,
and 2026-2028 is the first Global Fund allocation set after the PEPFAR and USAID
withdrawals, so a country whose allocation fell between 2023-2025 and 2026-2028 is visible
here years before any disbursement series could show the fall. No other source in this
panel states a forward commitment for that period at country level.

WHY THE OTHER 15 FINANCIAL DATASETS ARE NOT HERE. `AllFinancialIndicators` holds 1,269,005
rows over exactly 16 datasets, and two probes run on 30 September and 1 October 2026 asked
every one of the 16 what `recordId` resolves to. `recordId` is not one column across the
16. On 13 of the 16 it resolves to no table the service publishes, so no row of those 13
can be attributed to a country at all, and the 13 hold 1,262,046 of the 1,269,005 rows.
`Pledges_Contributions` resolves to `Donors`, which names who gave the money and never
names the country that received the money. `C19RM` resolves to `Geographies` and carries no
activity area, so the money reaches a country and cannot be split into an HIV share, and
the money is pandemic money. `DECLARED_DATASETS` below names all 15 with the reason each
is refused, and `scripts/audit_coverage.py` prints the list on every run.

THE HARD PART, AND WHAT THIS CONNECTOR DOES ABOUT IT. A three-year cycle is not a year.
Dividing an allocation by three would be this project inventing an annual profile the
Global Fund does not publish, and writing the whole cycle figure onto each of the cycle's
three years would triple the money for anyone who sums a country across years. So one
panel row carries one whole cycle, `year` holds the cycle's first year, the unit says the
figure covers a three-year cycle and is not annual, and `extra.allocation_period` names the
cycle. A reader who sums `global_fund_hiv_allocation_cycle` across years sums four cycles
and not twelve years. THIS SERIES MUST NEVER BE ADDED TO `global_fund_hiv_disbursements`.
An allocation is what the Global Fund promised and a disbursement is what the Global Fund
moved, and adding the two counts the same money twice.

FOUR REFUSALS INSIDE THE DATASET, each counted and logged rather than applied quietly.
A row whose geography is not a Country is dropped, because a regional or subnational
allocation has no one country to belong to, which is the same refusal the programmatic
connector beside this one makes. A row whose component is not HIV is dropped, because the
Tuberculosis and Malaria allocations are other diseases and a combined TB/HIV allocation
would need a split the Global Fund does not publish. A row marked superseded or cumulative
is dropped, because summing a superseded figure beside the figure that replaced it double
counts. A country, component and cycle that appears more than once is emitted for neither
row, because picking one of two unexplained figures is a silent wrong value, and the log
names the country, the cycle and every amount so a person can decide.

MEASURED ON PROBE ONE'S 200-ROW SAMPLE, 30 September 2026. Every row carries an amount,
every amount is in US dollars, every `activityAreaId` resolves to a named component,
`isLatestReported` is true on all 200 and `isCumulative` is false on all 200. `recordId`
reaches a geography on all 200, being 192 Country, 6 Multicountry and 2 Subnational, and
all 84 distinct country codes are three-letter codes. The components are 78 HIV, 71
Tuberculosis and 51 Malaria, so the HIV figure is a clean HIV figure and carries none of
the TB/HIV ambiguity the grant-level reading carries. The cycles are 2017-2019, 2020-2022,
2023-2025 and 2026-2028, no country, component and cycle appears twice, and the 78 HIV rows
of the sample alone carry 4,886,660,416 US dollars. The first full run is what confirms
those properties over all 1,034 rows, and every count above is re-measured and logged.

PASS `--end 2026` OR LATER. `scripts/run_all.py` defaults `--end` to 2025, and the
2026-2028 cycle sits at year 2026, so the default window drops the one cycle this connector
exists to carry. Rows dropped by the year window are counted and named in the log.
"""
from __future__ import annotations

import logging
from collections import Counter, defaultdict
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..connector_base import BaseConnector
from ..schema import PanelRow, SourceType
from ..config.indicators import CANONICAL_INDICATORS
# The Global Fund country-code map lives in the programmatic Global Fund connector and is
# imported here instead of being copied, so that the two Global Fund connectors cannot read one
# service code two different ways. The comment above GF_CODE_ALIASES in that module says why the
# map must not move into hivimpact/normalize.py.
from .global_fund import gf_country_code

log = logging.getLogger("hivimpact")

_BASE = "https://fetch.theglobalfund.org/v4.2/odata"
_DATASET = "CommunicatedAllocation_ReferenceRate"
_INDICATOR = "global_fund_hiv_allocation_cycle"

#: The component this connector reads, as the Global Fund's own ActivityAreas table names it.
_COMPONENT = "HIV"

#: The unit, held constant across cycles on purpose. `hivimpact/writers.py` puts `unit` in
#: its series key, so a unit that named the cycle would split each country's allocation into
#: four series of one row and the level-break checks would see nothing. A country whose
#: allocation falls between 2023-2025 and 2026-2028 is the thing this connector was added to
#: show, so the four cycles have to stay one series. The cycle is named in
#: `extra.allocation_period` instead.
_UNIT = "USD per three-year allocation cycle"

#: Row counts the service itself reported for each of the 16 datasets on 30 September 2026,
#: through $apply=groupby. Kept so the audit can state the size of what is refused, and so a
#: later run that finds a different total says the service changed rather than saying nothing.
DATASET_ROWS: Dict[str, int] = {
    "C19RM": 387,
    "Commitment_ImplementationPeriodCurrency": 79_561,
    "Commitment_ReferenceRate": 79_561,
    "CommunicatedAllocation_ReferenceRate": 1_034,
    "Disbursement_ImplementationPeriodCurrency": 117_337,
    "Disbursement_ReferenceRate": 117_337,
    "Expenditure_Intervention_ImplementationPeriodCurrency": 174_983,
    "Expenditure_Intervention_ReferenceRate": 174_983,
    "Expenditure_InvestmentLandscape_ImplementationPeriodCurrency": 74_364,
    "Expenditure_InvestmentLandscape_ReferenceRate": 74_364,
    "GrantBudget_ImplementationPeriodCurrency": 172_065,
    "GrantBudget_ReferenceRate": 172_065,
    "ImplementationPeriodAggregate": 21_864,
    "ImplementationPeriodFinancialMetricAmount": 3_432,
    "OPEX_ReferenceRate": 130,
    "Pledges_Contributions": 5_538,
}

#: The reason each of the other 15 datasets is refused. An unread dataset is a decision
#: nobody has made and a declared dataset is a decision on the record, which is the
#: distinction `scripts/audit_coverage.py` is built around.
_NO_COUNTRY = (
    "recordId resolves to no table the service publishes, tested on 30 September and "
    "1 October 2026 against Grants.id, Geographies.id, FundingRequests.id and "
    "CoordinatingMechanisms.id, so no row can be attributed to a country"
)
DECLARED_DATASETS: Dict[str, str] = {
    "Disbursement_ReferenceRate": _NO_COUNTRY,
    "Disbursement_ImplementationPeriodCurrency": _NO_COUNTRY,
    "Commitment_ReferenceRate": _NO_COUNTRY,
    "Commitment_ImplementationPeriodCurrency": _NO_COUNTRY,
    "Expenditure_Intervention_ReferenceRate": _NO_COUNTRY,
    "Expenditure_Intervention_ImplementationPeriodCurrency": _NO_COUNTRY,
    "Expenditure_InvestmentLandscape_ReferenceRate": _NO_COUNTRY,
    "Expenditure_InvestmentLandscape_ImplementationPeriodCurrency": _NO_COUNTRY,
    "GrantBudget_ReferenceRate": _NO_COUNTRY,
    "GrantBudget_ImplementationPeriodCurrency": _NO_COUNTRY,
    "ImplementationPeriodAggregate": _NO_COUNTRY,
    "ImplementationPeriodFinancialMetricAmount": _NO_COUNTRY,
    "OPEX_ReferenceRate": _NO_COUNTRY,
    "Pledges_Contributions":
        "recordId resolves to Donors on all 200 sampled rows, so the rows name who gave the "
        "money and never name the country that received the money, which is the same "
        "donor-side refusal data/raw/global_fund/pledges-and-contributions.csv already carries",
    "C19RM":
        "recordId resolves to Geographies on all 200 sampled rows and no row carries an "
        "activity area, so the COVID-19 Response Mechanism's money reaches a country and "
        "cannot be split into an HIV share, and the money is pandemic money and not HIV money",
}

#: Components this connector sees and deliberately leaves alone. Named so the log can say
#: these were seen and left out on purpose, the way global_fund._UNMAPPED_OTHER_DISEASE does,
#: because a warning that fires on three names every run hides the one new name that matters.
DECLARED_COMPONENTS: Dict[str, str] = {
    "Tuberculosis": "another disease, outside this panel",
    "Malaria": "another disease, outside this panel",
    "TB/HIV": "a combined allocation, and the Global Fund publishes no HIV share of it, so "
              "writing a share would be this project inventing the split",
    "RSSH": "resilient and sustainable systems for health, which is cross-cutting money that "
            "no published rule attributes to HIV",
    "Multicomponent": "an allocation covering several diseases at once, with no published "
                      "split into components",
}


class GlobalFundAllocationsConnector(BaseConnector):
    source_id = "global_fund_allocations"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("Global Fund communicated allocations, one row per country and three-year "
                   "cycle (OData v4.2)")
    timeout = 120

    #: Paging guard. The dataset is 1,034 rows and the service answers in pages, so a run
    #: that needs more pages than this is reporting a service that changed, not a big dataset.
    page_cap = 40

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._geographies: Optional[Dict[str, Tuple[str, str, str]]] = None
        self._components: Optional[Dict[str, str]] = None
        #: Geography id -> the reason the country code on that geography is refused. Filled by
        #: geographies() and read by fetch(), so that one refused code is written once and
        #: reported in the same words wherever the refused code is met.
        self._geo_refusals: Dict[str, str] = {}

    # -- paging ----------------------------------------------------------------
    def _get_all(self, path: str) -> List[dict]:
        """GET one OData path and follow @odata.nextLink to the end of the result."""
        url = f"{_BASE}/{path}"
        rows: List[dict] = []
        pages = 0
        while url and pages < self.page_cap:
            payload = self.get_json(url)
            rows.extend(payload.get("value") or [])
            url = payload.get("@odata.nextLink")
            if url and not str(url).lower().startswith("http"):
                url = f"{_BASE}/{str(url).lstrip('/')}"
            pages += 1
        if url:
            log.warning("global_fund_allocations: %s hit the %d-page cap, so the %d rows read "
                        "are a floor and not the whole table", path, self.page_cap, len(rows))
        return rows

    # -- the two lookup tables -------------------------------------------------
    def geographies(self) -> Dict[str, Tuple[str, str, str]]:
        """Geography id -> (ISO3, country name, level), every level, countries marked.

        Every level is kept here, unlike the programmatic connector beside this one, because
        this connector has to report how much money the Multicountry and Subnational rows
        carry and cannot report money it never looked at.

        A Country-level code passes through gf_country_code() from the programmatic connector,
        so that a Global Fund code which is not an ISO 3166-1 alpha-3 code reaches the panel as
        the code the rest of the panel uses, or reaches the panel as nothing at all. A code on
        any other level is left exactly as the service published the code, because fetch()
        refuses every other level by level and never reads the code.
        """
        if self._geographies is None:
            rows = self._get_all("Geographies?$select=id,code,level,name")
            kept: Dict[str, Tuple[str, str, str]] = {}
            refusals: Dict[str, str] = {}
            aliased: Dict[str, str] = {}
            for r in rows:
                if not r.get("id"):
                    continue
                geo_id = str(r.get("id"))
                code = str(r.get("code") or "").strip().upper()
                level = str(r.get("level") or "")
                if level == "Country":
                    iso3, reason = gf_country_code(code)
                    if iso3 is None:
                        refusals[geo_id] = str(reason)
                    else:
                        if iso3 != code:
                            aliased[code] = iso3
                        code = iso3
                kept[geo_id] = (code, str(r.get("name") or ""), level)
            self._geographies = kept
            self._geo_refusals = refusals
            levels = Counter(v[2] for v in kept.values())
            log.info("global_fund_allocations: %d geographies (%s)", len(kept),
                     ", ".join(f"{k or 'unlabelled'} {n}" for k, n in sorted(levels.items())))
            for code, iso3 in sorted(aliased.items()):
                log.info("global_fund_allocations: country code %s read as %s, the code this "
                         "panel uses", code, iso3)
            for geo_id, reason in sorted(refusals.items(), key=lambda kv: kv[1]):
                log.info("global_fund_allocations: country code %s refused, %s",
                         kept[geo_id][0], reason)
        return self._geographies

    def components(self) -> Dict[str, str]:
        """Activity area id -> component name, for the areas the service types as Component."""
        if self._components is None:
            rows = self._get_all("ActivityAreas?$select=id,type,name,code")
            self._components = {str(r.get("id")): str(r.get("name") or "")
                                for r in rows if r.get("id")}
            n_component = sum(1 for r in rows if str(r.get("type") or "") == "Component")
            log.info("global_fund_allocations: %d activity areas, %d of them components",
                     len(self._components), n_component)
        return self._components

    # -- the allocations -------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None
        geo = self.geographies()
        comp = self.components()

        url = (f"{_BASE}/AllFinancialIndicators"
               f"?$filter=financialDataSet eq '{_DATASET}'")
        rows = self._get_all(f"AllFinancialIndicators?$filter=financialDataSet eq '{_DATASET}'")
        log.info("global_fund_allocations: %d %s rows, against %d the service reported on "
                 "30 September 2026", len(rows), _DATASET, DATASET_ROWS[_DATASET])

        # Every refusal below is counted, and the money inside each refusal is counted with it,
        # because a count of dropped rows says nothing about how much was dropped.
        dropped: Counter = Counter()
        dropped_money: Dict[str, float] = defaultdict(float)
        other_component: Counter = Counter()
        other_component_money: Dict[str, float] = defaultdict(float)
        geo_levels: Counter = Counter()
        currencies: Counter = Counter()
        cycles_out_of_window: Counter = Counter()

        def refuse(reason: str, amount: Optional[float]) -> None:
            dropped[reason] += 1
            dropped_money[reason] += float(amount or 0.0)

        # Collected by key first, so a country, component and cycle that appears twice is
        # caught before anything is emitted rather than overwriting itself in the panel.
        by_key: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
        meta: Dict[Tuple[str, str], Tuple[str, str]] = {}

        for r in rows:
            amount = _num(r.get("actualAmount"))

            if not r.get("isLatestReported"):
                refuse("superseded by a later report (isLatestReported false)", amount)
                continue
            if r.get("isCumulative"):
                refuse("cumulative, so summing it beside the rows it contains double counts",
                       amount)
                continue

            geo_id = str(r.get("recordId"))
            resolved = geo.get(geo_id)
            if resolved is None:
                refuse("recordId reaches no geography the service publishes", amount)
                continue
            iso3, country_name, level = resolved
            geo_levels[level] += 1
            if level != "Country":
                refuse(f"geography level {level or 'unlabelled'}, which belongs to no one "
                       f"country", amount)
                continue
            # geographies() has already aliased the Country-level codes that the panel knows
            # under another spelling, so a code refused here is one the panel cannot place.
            if geo_id in self._geo_refusals:
                refuse(f"country code {iso3!r} refused, {self._geo_refusals[geo_id]}", amount)
                continue

            component = comp.get(str(r.get("activityAreaId")))
            if component is None:
                refuse("activityAreaId reaches no activity area the service publishes", amount)
                continue
            if component != _COMPONENT:
                other_component[component] += 1
                other_component_money[component] += float(amount or 0.0)
                continue

            period = str(r.get("periodCovered") or "").strip()
            first_year = _year(r.get("periodFrom")) or _year(period[:4])
            if first_year is None:
                refuse(f"no readable first year in periodCovered {period!r}", amount)
                continue
            if first_year < start_year or first_year > end_year:
                cycles_out_of_window[period or str(first_year)] += 1
                continue
            if wanted and iso3 not in wanted:
                continue

            currency = str(r.get("actualAmountCurrency") or "").strip().upper()
            currencies[currency or "unstated"] += 1
            if currency != "USD":
                refuse(f"amount stated in {currency or 'no currency'} and not US dollars, and "
                       f"this connector converts nothing", amount)
                continue
            if amount is None:
                refuse("no amount on the row", None)
                continue

            by_key[(iso3, period or str(first_year))].append(r)
            meta[(iso3, period or str(first_year))] = (country_name, str(first_year))

        # A repeated key is unexplained, because isLatestReported has already removed the
        # revisions. Emitting one of two unexplained figures would be a silent wrong value, so
        # neither is emitted and the log names the country, the cycle and every amount.
        emitted = 0
        total = 0.0
        per_cycle: Counter = Counter()
        per_cycle_money: Dict[str, float] = defaultdict(float)
        spec = CANONICAL_INDICATORS.get(_INDICATOR)

        for (iso3, period), group in sorted(by_key.items()):
            country_name, first_year = meta[(iso3, period)]
            if len(group) > 1:
                amounts = ", ".join(f"{_num(g.get('actualAmount')):,.0f}" for g in group)
                log.warning("global_fund_allocations: %s %s appears %d times with amounts %s, "
                            "and isLatestReported has already removed the revisions, so neither "
                            "figure is emitted and the country is absent for that cycle",
                            iso3, period, len(group), amounts)
                refuse("country, component and cycle appearing more than once",
                       sum(_num(g.get("actualAmount")) or 0.0 for g in group))
                continue

            r = group[0]
            amount = float(_num(r.get("actualAmount")))
            period_from = str(r.get("periodFrom") or "").strip()
            period_to = str(r.get("periodTo") or "").strip()

            yield self.make_row(
                country_iso3=iso3,
                country_name=country_name,
                indicator_id=_INDICATOR,
                year=int(first_year),
                value=amount,
                unit=_UNIT,
                source_url=url,
                source_indicator_code=str(r.get("indicatorName") or _DATASET),
                extra={
                    "dataset": _DATASET,
                    "component": _COMPONENT,
                    "allocation_period": period,
                    "allocation_period_from": period_from,
                    "allocation_period_to": period_to,
                    # Said on the row as well as in the registry, because a reader meets the
                    # row before the registry and the two series are the same institution's
                    # money counted at two different moments.
                    "covers_whole_cycle_not_one_year": True,
                    "do_not_add_to": "global_fund_hiv_disbursements",
                },
            )
            emitted += 1
            total += amount
            per_cycle[period] += 1
            per_cycle_money[period] += amount

        # -- what the run saw, said in full ------------------------------------
        log.info("global_fund_allocations: %d rows emitted over %d countries, %s USD in all",
                 emitted, len({k[0] for k in by_key}), f"{total:,.0f}")
        for period in sorted(per_cycle):
            log.info("global_fund_allocations:   cycle %-10s %4d countries  %18s USD",
                     period, per_cycle[period], f"{per_cycle_money[period]:,.0f}")
        log.info("global_fund_allocations: geography levels seen %s, currencies seen %s",
                 dict(geo_levels.most_common()), dict(currencies.most_common()))
        for component, n in other_component.most_common():
            reason = DECLARED_COMPONENTS.get(component)
            log.info("global_fund_allocations: component %-16s %4d rows %18s USD left out, %s",
                     component, n, f"{other_component_money[component]:,.0f}",
                     reason or "NOT DECLARED, and this connector did not expect it")
        for reason, n in dropped.most_common():
            log.info("global_fund_allocations: %4d rows %18s USD dropped, %s",
                     n, f"{dropped_money[reason]:,.0f}", reason)
        if cycles_out_of_window:
            log.warning("global_fund_allocations: %d rows fall outside the year window "
                        "%d to %d and were not read, by cycle %s. The 2026-2028 cycle sits at "
                        "year 2026, so a run that wants it passes --end 2026 or later.",
                        sum(cycles_out_of_window.values()), start_year, end_year,
                        dict(cycles_out_of_window.most_common()))

        new_components = [c for c in other_component if c not in DECLARED_COMPONENTS]
        if new_components:
            log.warning("global_fund_allocations: %d component names this connector does not "
                        "declare, and which were not there when this connector was written: %s",
                        len(new_components),
                        ", ".join(f"{c} ({other_component[c]})" for c in sorted(new_components)))
        if spec is None:
            log.warning("global_fund_allocations: %s is not in CANONICAL_INDICATORS, so the "
                        "rows carry an indicator id the registry does not describe", _INDICATOR)


def _num(x) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _year(x) -> Optional[int]:
    """The four-digit year in a value like 2023, "2023" or "2023-2025"."""
    if x is None:
        return None
    text = str(x).strip()[:4]
    return int(text) if text.isdigit() and len(text) == 4 else None
