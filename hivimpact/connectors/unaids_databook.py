"""
UNAIDS country databook connector, connector 33, the financing split of every country's HIV
expenditure and the 2024 state and regional estimates of people living with HIV for Nigeria and
Eritrea, read from the Power BI model behind the UNAIDS Data 2025 country databook.

UNAIDS (the Joint United Nations Programme on HIV/AIDS) embeds one public Power BI report in the
AIDSinfo pages /kpatlas and /ncpi under the resource key of the public link. The report's model
470871, "UNAIDS_DATABOOK_web", was refreshed on 21 October 2025 and runs in DirectQuery mode. The
model's conceptualschema route answers HTTP 401 (Unauthorized), and the connector never calls
that route. The table and column names below come from the report's own visual definitions in
the modelsAndExploration answer, and the anonymous querydata route paho_core, paho_hiv and
unaids_services call answered every query on 15 October 2026 (research/aggregator_sweep_notes.md).

What the connector reads.
  - "Reported expenditures from all sources of funding 2015-2023", one row per country and
    expenditure year with domestic public, domestic private and total international HIV
    expenditure in US dollars. 434 country-years over 112 countries for 2015 to 2023 on
    15 October 2026, plus one row whose country key matches no country and gives no row.
  - 2024_plhiv_all_ages, the 2024 number of people living with HIV for 2,312 districts in 33
    countries of sub-Saharan Africa and in Haiti, with the upper bound in a column of the table
    and both bounds in an uncertainty string of the form "[lower - upper]". The year comes from
    the table name, because the table carries no year column.

Panel indicators and databook columns.
  domestic_hiv_spend                 domestic public expenditures
  hiv_expenditure_domestic_private   domestic private expenditures
  hiv_expenditure_international      Total international Expenditures
  plhiv                              estimate, with value_lower and value_upper from the
                                     uncertainty string

The financing split against the panel of 14 October 2026. The databook values repeat the
country returns unaids_gam_expenditure reads from the GAM (Global AIDS Monitoring) expenditure
workbook. Domestic public spending matches the unaids_gam_expenditure value within half a per
cent for 354 country-years and differs for eight, private spending matches for 171 and differs
for five, and international spending matches for 323 and differs for eight. The differing
country-years are Bangladesh 2021 and 2022, Colombia 2022, Kazakhstan 2021 and 2023, Singapore
2020, South Africa 2017 and Tajikistan 2021 to 2023. The databook holds a nonzero split for 17
country-years with no matching unaids_gam_expenditure row, namely Benin 2015 to 2017, Chile 2016,
Guinea 2019, Indonesia 2016, Kiribati 2018, Madagascar 2019, Malawi 2015, Mauritius 2018, Nepal
2020, Senegal 2015, South Sudan 2018 and 2020, Zambia 2017, Kazakhstan 2021 for domestic public
spending and Sierra Leone 2021 for international spending. The connector emits every
country-year, so reconcile.py can infer the relationship of the unaids_databook and
unaids_gam_expenditure pair, and no relationship is declared.

A zero is not emitted. unaids_gam_expenditure gives the reason for the GAM workbook, where a zero
and a blank both mean "not reported", and the databook shows the same pattern. Tajikistan 2021
reads zero for private and international spending in the databook against 393,243 and 6,145,663
US dollars in the GAM workbook. A country-year that the databook lists twice with different
values gives no row, and the connector logs the country-year.

Why only Nigeria and Eritrea from the district table. The panel holds one subnational column,
admin1, for the first administrative level below the country, and unaids_naomi reads Naomi at
that level. The databook table sits at the first administrative level for some countries and at
health districts or health zones for others (Benin 34 health zones, Côte d'Ivoire 113 health
districts, the Democratic Republic of the Congo 471 rows). Nigeria and Eritrea are the two
countries where the databook unit is the first administrative level, Nigeria's 36 states and
the Federal Capital Territory and Eritrea's six regions, and where the panel holds no
unaids_naomi row. The connector checks the unit count of each country against _ADMIN1_UNITS and
refuses the country's rows when the count differs, because a changed count means the databook
has changed the level. The other 32 countries of the table wait on a decision about rows below
the first administrative level, recorded in the sweep notes.

What the connector refuses, and why.
  - The programme spending tables (key populations, prevention pillars, treatment, human rights
    programmes). Each table gives one latest year per country, and the categories are narrower
    parts of the GAM programme lines (the treatment total matches hiv_spend_treatment for five
    of 80 country-years). The GAM workbook gives the same programme lines as a time series.
  - HIV_Expenditure_Source_Funding, rounded display strings such as "2.0M" with no year column.
  - KEY_POPULATIONS, the medicine cost tables and the differentiated service delivery table.
    The key-population and medicine cost tables carry no year column, and the panel holds no
    id for differentiated service delivery or for medicine costs.
  - HIV_EPIDEMIC_ESTIMATES and EID, the UNAIDS 2025 modelled estimates unaids_aidsinfo already
    reads from the AIDSinfo 2025 export.
  - The regional and global rows ("UNAIDS Region - Caribbean", "Global"), because to_iso3
    refuses the names.

Rows from the saved answers of 15 October 2026, in an offline test with the network blocked.
1,012 rows over 108 countries. domestic_hiv_spend gives 404 rows with 30 zeros not emitted,
hiv_expenditure_domestic_private 192 rows with 242 zeros not emitted, hiv_expenditure_international
373 rows with 61 zeros not emitted, and plhiv 43 rows, 37 Nigerian and six Eritrean. The 37
Nigerian values add up to 2,041,242 against the unaids_aidsinfo national value of 2,000,000
(1,800,000 to 2,100,000) for 2024, and the six Eritrean values add up to 13,132 against 12,000
(10,000 to 15,000).
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from collections import defaultdict
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType, POP_ALL
from .paho_core import decode_dsr

log = logging.getLogger("hivimpact")

_QUERY_URL = ("https://wabi-north-europe-p-primary-api.analysis.windows.net"
              "/public/reports/querydata?synchronous=true")
# the AIDSinfo page the report is embedded in, written into source_url for a human reader
_PAGE_URL = "https://aidsinfo.unaids.org/kpatlas"

# "UNAIDS_DATABOOK_web", read from modelsAndExploration on 15 October 2026
_REPORT = {
    "key": "a68209be-f40e-4851-8258-559cb4f050e7",
    "model_id": 470871,
    "dataset_id": "e39c9cd9-c170-4236-83ea-fa72dc30b95d",
    "report_id": "1fb6c61d-105d-41de-a62e-5f812016bc32",
}

_FINANCING_TABLE = "Reported expenditures from all sources of funding 2015-2023"
# databook column -> panel indicator, in the order of the query's Select after country and year
_FINANCING = [
    ("domestic public expenditures", "domestic_hiv_spend"),
    ("domestic private expenditures", "hiv_expenditure_domestic_private"),
    ("Total international Expenditures", "hiv_expenditure_international"),
]

_DISTRICT_TABLE = "2024_plhiv_all_ages"
_DISTRICT_YEAR = 2024
# country -> number of first-level units the databook gave on 15 October 2026
_ADMIN1_UNITS = {"NGA": 37, "ERI": 6}

_BOUNDS = re.compile(r"^\[\s*(-?[\d.]+)\s*-\s*(-?[\d.]+)\s*\]$")


def _col(alias: str, prop: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop},
            "Name": f"{alias}.{prop}"}


def _number(v) -> Optional[float]:
    """A number from the databook, which sends some decimals as strings."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else f


def _bounds(text) -> Tuple[Optional[float], Optional[float]]:
    """"[39748 - 55810]" -> (39748, 55810), anything else (None, None)."""
    m = _BOUNDS.match(str(text or "").strip())
    if not m:
        return None, None
    return _number(m.group(1)), _number(m.group(2))


class UNAIDSDatabookConnector(BaseConnector):
    source_id = "unaids_databook"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("UNAIDS Data 2025 country databook, domestic public, private and international "
                   "HIV expenditure 2015-2023 and 2024 state estimates for Nigeria and Eritrea.")
    request_pause = 1.0
    timeout = 120

    def _query(self, from_: List[Tuple[str, str]], select: list) -> List[list]:
        query = {"Version": 2,
                 "From": [{"Name": alias, "Entity": entity, "Type": 0} for alias, entity in from_],
                 "Select": select}
        body = {
            "version": "1.0.0",
            "queries": [{
                "Query": {"Commands": [{"SemanticQueryDataShapeCommand": {
                    "Query": query,
                    "Binding": {"Primary": {"Groupings": [{"Projections": list(range(len(select)))}]},
                                "DataReduction": {"DataVolume": 4,
                                                  "Primary": {"Window": {"Count": 30000}}},
                                "Version": 1}}}]},
                "QueryId": "",
                "ApplicationContext": {"DatasetId": _REPORT["dataset_id"],
                                       "Sources": [{"ReportId": _REPORT["report_id"]}]},
            }],
            "cancelQueries": [],
            "modelId": _REPORT["model_id"],
        }
        headers = {"X-PowerBI-ResourceKey": _REPORT["key"],
                   "Content-Type": "application/json;charset=UTF-8",
                   "ActivityId": str(uuid.uuid4()), "RequestId": str(uuid.uuid4())}
        resp = self._request("POST", _QUERY_URL, data=json.dumps(body), headers=headers)
        return decode_dsr(resp.json())

    def _financing_rows(self) -> List[list]:
        """Country name, year, indicator name and the three columns of _FINANCING."""
        select = [_col("c", "area_name"), _col("t", "Year"), _col("t", "indicator_name")]
        select += [_col("t", column) for column, _ in _FINANCING]
        return self._query([("c", "Country"), ("t", _FINANCING_TABLE)], select)

    def _district_rows(self) -> List[list]:
        """Country name, indicator, district, estimate, upper bound and uncertainty string."""
        select = [_col("t", p) for p in ("area_name", "indicator", "subarea_name", "estimate",
                                         "upper", "Uncertainty")]
        return self._query([("t", _DISTRICT_TABLE)], select)

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2015,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        end_year = min(end_year or date.today().year, date.today().year)

        def keep(iso3: Optional[str], year: int) -> bool:
            return (iso3 is not None and (wanted is None or iso3 in wanted)
                    and start_year <= year <= end_year)

        # -- the financing split -------------------------------------------------------------
        unnamed: set = set()
        values: Dict[Tuple[str, int, str], set] = defaultdict(set)
        names: Dict[str, str] = {}
        for rec in self._financing_rows():
            name, year = rec[0], _number(rec[1])
            if not name or year is None:
                continue
            iso3 = to_iso3(name)
            if iso3 is None:
                unnamed.add(str(name))
                continue
            if not keep(iso3, int(year)):
                continue
            names[iso3] = str(name)
            for (column, canonical), v in zip(_FINANCING, rec[3:]):
                values[(iso3, int(year), canonical)].add(_number(v))

        emitted: Dict[str, int] = defaultdict(int)
        zeros: Dict[str, int] = defaultdict(int)
        conflicts: List[str] = []
        column_of = {canonical: column for column, canonical in _FINANCING}
        for (iso3, year, canonical), seen in sorted(values.items()):
            seen.discard(None)
            if len(seen) > 1:
                conflicts.append(f"{iso3} {year} {canonical}")
                continue
            if not seen:
                continue
            value = next(iter(seen))
            if value == 0:
                zeros[canonical] += 1
                continue
            spec = CANONICAL_INDICATORS[canonical]
            yield self.make_row(
                country_iso3=iso3, country_name=names[iso3], indicator_id=canonical, year=year,
                value=value, population_group=POP_ALL, unit=spec.unit, source_url=_PAGE_URL,
                source_indicator_code=f"{_FINANCING_TABLE} | {column_of[canonical]}",
                extra={"databook_table": _FINANCING_TABLE,
                       "databook_model": f"{_REPORT['model_id']} UNAIDS_DATABOOK_web"},
            )
            emitted[canonical] += 1

        # -- the 2024 state and regional estimates -------------------------------------------
        districts: Dict[str, List[list]] = defaultdict(list)
        if keep("NGA", _DISTRICT_YEAR) or keep("ERI", _DISTRICT_YEAR):
            for rec in self._district_rows():
                iso3 = to_iso3(rec[0]) if rec[0] else None
                if iso3 in _ADMIN1_UNITS and keep(iso3, _DISTRICT_YEAR):
                    districts[iso3].append(rec)
        spec = CANONICAL_INDICATORS["plhiv"]
        for iso3, recs in sorted(districts.items()):
            units = {r[2] for r in recs if r[2]}
            if len(units) != _ADMIN1_UNITS[iso3] or len(recs) != len(units):
                log.warning("unaids_databook: %s gives %d rows over %d named units against %d "
                            "first-level units, and the country gives no row", iso3, len(recs),
                            len(units), _ADMIN1_UNITS[iso3])
                continue
            for name, indicator, unit, estimate, upper, uncertainty in recs:
                value = _number(estimate)
                if value is None or str(indicator).strip() != "Number of people living with HIV":
                    continue
                lower, high = _bounds(uncertainty)
                yield self.make_row(
                    country_iso3=iso3, country_name=str(name), indicator_id="plhiv",
                    year=_DISTRICT_YEAR, value=value, value_lower=lower,
                    value_upper=high if high is not None else _number(upper),
                    admin1=str(unit).strip(), population_group=POP_ALL, unit=spec.unit,
                    source_type=SourceType.MODELLED_ESTIMATE.value, source_url=_PAGE_URL,
                    source_indicator_code=f"{_DISTRICT_TABLE} | estimate",
                    extra={"databook_table": _DISTRICT_TABLE,
                           "databook_model": f"{_REPORT['model_id']} UNAIDS_DATABOOK_web",
                           "uncertainty_published": str(uncertainty),
                           "year_basis": "the year in the table name, the table has no year column"},
                )
                emitted["plhiv"] += 1

        for canonical in [c for _, c in _FINANCING] + ["plhiv"]:
            log.info("unaids_databook: %-34s -> %d rows, %d zeros not emitted", canonical,
                     emitted.get(canonical, 0), zeros.get(canonical, 0))
        if conflicts:
            log.warning("unaids_databook: %d country-years listed twice with different values "
                        "give no row (%s)", len(conflicts), ", ".join(conflicts))
        log.info("unaids_databook: %d area names outside ISO 3166 were skipped (%s)",
                 len(unnamed), ", ".join(sorted(unnamed)))
