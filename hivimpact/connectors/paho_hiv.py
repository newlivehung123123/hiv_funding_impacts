"""
PAHO Interactive HIV Data Dashboard connector, connector 28, notified HIV cases the Core
Indicators table lacks, and the share of people on ART on a dolutegravir-based regimen.

PAHO (the Pan American Health Organization) embeds one public Power BI report on the page
https://www.paho.org/en/interactive-hiv-data-dashboard-americas (report e1696511, model 3093636,
display name PAHO_HIV, refreshed 1 October 2026). The model holds four data tables, and the public
querydata endpoint of the report answers a semantic query without sign-in, the same route
paho_core reads for the Core Indicators model.

Coverage read on 14 October 2026 from the API answers (research/phase5_lac/lac_round1_notes.md).

Table "Nuevos diagnosticos", notified HIV cases. PAHO's own text box names the Core Indicators
in PLISA (the PAHO health information platform) as the source, completed with national
epidemiological bulletins or direct communication for countries PLISA lacks. 2,095 rows under
Core Indicator ids 93, 94 and 95. Against paho_core, 1,622 country-year-sex rows hold the same
value, 130 hold a different value, and 273 exist in the dashboard alone. The dashboard alone
holds Haiti for 2010 to 2024 with the female and male split, a country Core Indicator 93 lacks,
plus early years for Antigua and Barbuda, Chile, Colombia, Ecuador and Paraguay, the Nicaraguan
female and male split for 2010 to 2023, Honduras for 2022 to 2025, Venezuela for 2021 to 2025,
Peru for 2018, the Dominican Republic for 2020, Guatemala for 2024 and 2025, and 2025 for
Argentina, Jamaica, Panama, Suriname and Saint Vincent and the Grenadines.

Table "DTG", people on ART by treatment line, with the count on a dolutegravir (DTG) regimen
in each line. PAHO's heading reads transition to regimens based on DTG or other
second-generation integrase inhibitors, and the source line reads Global AIDS Monitoring (GAM)
reports plus direct communication with countries. 1,232 rows, 31 countries, 2020 to 2025, two
age groups ("Número en TAR ≥10", aged ten and over, and "Número en TAR <10", under ten). WHO's
Global Health Observatory and the UNAIDS export publish no regimen or DTG indicator, so the
DTG share is new to the panel. The table's TOTAL is the denominator of the regimen report and
not the national count on ART. Ages ten and over plus under ten match who_gho on_art_count
exactly in 31 of 108 country-years and within two per cent in 65, and Argentina's TOTAL is
about 65 per cent of the national count, probably the public sector alone.

What the connector emits.
  - notified_hiv_cases from "Nuevos diagnosticos", only for a country, year and sex that
    paho_core emits no row for. The connector runs PAHOCoreConnector itself to learn which keys
    paho_core fills, so a paho_hiv run reads the Core Indicators model too. Where Core
    Indicator 93 and the dashboard hold different values for one key (Brazil 2021 reads 36,857
    in the dashboard against 42,676 in Core Indicator 93), the paho_core row stands and the log
    names the country-year. Against the paho_core rows in the panel on 14 October 2026, the
    filters below leave 173 rows over 17 countries, 43 of the rows Haitian.
  - on_art_dtg_pct from "DTG", TOTAL en DTG divided by TOTAL, times 100, with the numerator and
    denominator, for age_group "10+" and "0-9" separately. The line counts travel in extra.
    The saved API answer of 14 October 2026 gives 137 rows for ages ten and over and 111 for
    children under ten, over 31 countries and 2020 to 2025.

What the connector refuses, and why.
  - The codes ALC and AL are PAHO regional totals, not countries.
  - A row whose Core Indicator id and "Sexo al nacer" label disagree (indicator 94 labelled Men,
    indicator 95 labelled Women, indicator 96 labelled Men, or no indicator id) is dropped,
    because the sex of the count cannot be known. Indicator 96, unknown sex, is not a sex the
    panel carries.
  - A row marked "Imputado" in the preliminary column (four Venezuelan female rows) is a PAHO
    imputation and not a reported count.
  - Two rows for one country, year and sex with different values give no row.
  - A DTG country-age-year without both TOTAL and TOTAL en DTG, or with a DTG count above
    TOTAL, gives no row. Ages ten and over and under ten are never summed into an all-age
    share, because no ruling covers summing the two age groups.
  - The table "Personas en PrEP" republishes the GAM PrEP counts that unaids_aidsinfo carries
    as prep_recipients, and "Personas en TAR" republishes the Spectrum and GAM counts on ART
    that who_gho carries. Neither table is read. The 2025 PrEP values are expected in the
    next UNAIDS export.

Known faults in the source, kept visible in extra.
  - Every Haitian total row of "Nuevos diagnosticos" for 2010 to 2025 names the National AIDS
    Programme Secretariat of Guyana as provider, and the Haitian female and male rows name no
    provider. extra.provider_mislabel marks the Haitian rows carrying the Guyanese provider.
  - Female plus male can differ from the total. Haiti 2023 reads 7,660 female and 4,959 male
    against a total of 13,739. A total row carries extra.female_plus_male whenever the
    dashboard holds both sex rows for the key, and extra.sex_parts_mismatch when the sum
    differs from the total. The dashboard holds no unknown-sex count for Haiti.
  - The DTG table writes GRE for Grenada, SLU for Saint Lucia and SVG for Saint Vincent and the
    Grenadines, and the connector maps the three codes to GRD, LCA and VCT.
  - TOTAL differs from the sum of the three lines in eight country-age-years (Haiti and Jamaica
    2021 and 2022, Peru 2022 ages ten and over), and TOTAL en DTG differs from the sum of the
    DTG lines in seven. extra.lines_sum_mismatch and extra.dtg_lines_sum_mismatch mark the rows.

Fragile by construction. The resource key, model id and wabi cluster below belong to the
published report. If PAHO republishes the report, the endpoint answers with an error object,
and the connector raises with the error text so run_all marks the source FAILED.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType
from .paho_core import PAHOCoreConnector, _QUERY_URL, _col, _float, _int, decode_dsr

log = logging.getLogger("hivimpact")

_PAGE_URL = "https://www.paho.org/en/interactive-hiv-data-dashboard-americas"

_REPORT = {
    "key": "972060bb-f744-4200-91ad-50e5d7b1432c",
    "model_id": 3093636,
    "dataset_id": "bdeb85ca-5cb3-471d-8293-a72904f89619",
    "report_id": "e1696511-a2d6-45e5-8028-b980c002550b",
}

# PAHO regional totals in "Nuevos diagnosticos", never a country
_AGGREGATES = {"ALC", "AL"}
# DTG table codes that are not ISO3
_ISO_FIX = {"GRE": "GRD", "SLU": "LCA", "SVG": "VCT"}

# Core Indicator id -> (panel sex, the "Sexo al nacer" label the id must carry)
_ND_SEX = {93: ("all", ".Total"), 94: ("female", "Women"), 95: ("male", "Men")}
_ND_COLUMNS = ["paho_indicator_id", "SpatialDim", "TimeDim", "Numeric_value", "indicator_status",
               "data_source_type", "data_provider_specific", "preliminary", "Sexo al nacer"]

_DTG_COLUMNS = ["INDICATOR", "Línea", "ISO3", "Año", "Identificador", "Nº Personas DTG"]
_DTG_AGE = {"Número en TAR ≥10": "10+", "Número en TAR <10": "0-9"}
_LINES = ["Primera línea", "Segunda línea", "Tercera línea"]
_DTG_LINES = ["Primera línea en DTG", "Segunda línea en DTG", "Tercera línea en DTG"]
_LINE_KEYS = {"Primera línea": "first_line", "Segunda línea": "second_line",
              "Tercera línea": "third_line", "Primera línea en DTG": "first_line_dtg",
              "Segunda línea en DTG": "second_line_dtg", "Tercera línea en DTG": "third_line_dtg"}


def _text(v) -> str:
    s = "" if v is None else str(v).strip()
    return "" if s.upper() == "NULL" else s


class PAHOHIVConnector(BaseConnector):
    source_id = "paho_hiv"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("PAHO Interactive HIV Data Dashboard, notified HIV cases Core Indicator 93 "
                   "lacks (Haiti 2010 to 2024 among them) and the share on ART on a "
                   "dolutegravir-based regimen.")
    request_pause = 1.0
    timeout = 90

    def _query(self, entity: str, columns: List[str]) -> List[dict]:
        select = [_col(c) for c in columns]
        body = {
            "version": "1.0.0",
            "queries": [{
                "Query": {"Commands": [{"SemanticQueryDataShapeCommand": {
                    "Query": {"Version": 2, "From": [{"Name": "t", "Entity": entity, "Type": 0}],
                              "Select": select},
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
        return [dict(zip(columns, r)) for r in decode_dsr(resp.json())]

    # -- notified HIV cases --------------------------------------------------------------
    def _core_keys(self, countries, start_year, end_year) -> Dict[Tuple[str, int, str], float]:
        """(iso3, year, sex) -> value for every row paho_core emits over the same filters."""
        core = PAHOCoreConnector()
        return {(r.country_iso3, r.year, r.sex): r.value
                for r in core.fetch(countries=countries, start_year=start_year, end_year=end_year)}

    def _notified(self, wanted, start_year, end_year, core) -> Iterator[PanelRow]:
        raw = self._query("Nuevos diagnosticos", _ND_COLUMNS)
        cells: Dict[Tuple[str, int, str], List[dict]] = {}
        skipped = {"aggregate": 0, "sex_label": 0, "unknown_sex": 0, "imputed": 0, "null": 0}
        for rec in raw:
            code = _text(rec["SpatialDim"]).upper()
            if code in _AGGREGATES:
                skipped["aggregate"] += 1
                continue
            iso3 = to_iso3(code) if len(code) == 3 else None
            if iso3 is None:
                skipped["aggregate"] += 1
                continue
            iid, year = _int(rec["paho_indicator_id"]), _int(rec["TimeDim"])
            if iid == 96:
                skipped["unknown_sex"] += 1
                continue
            if iid not in _ND_SEX or _text(rec["Sexo al nacer"]) != _ND_SEX[iid][1]:
                skipped["sex_label"] += 1
                log.info("paho_hiv: %s %s indicator %s labelled %r, sex unknown, no row",
                         iso3, year, iid, rec["Sexo al nacer"])
                continue
            if _text(rec["preliminary"]).lower() == "imputado":
                skipped["imputed"] += 1
                log.info("paho_hiv: %s %s indicator %s is a PAHO imputation, no row", iso3, year, iid)
                continue
            if year is None or _float(rec["Numeric_value"]) is None:
                skipped["null"] += 1
                continue
            if wanted is not None and iso3 not in wanted:
                continue
            if year < start_year or year > end_year:
                continue
            rec["val"] = _float(rec["Numeric_value"])
            cells.setdefault((iso3, year, _ND_SEX[iid][0]), []).append(rec)

        # one value per key, for the female plus male check on a total row
        single = {k: recs[0]["val"] for k, recs in cells.items() if len({r["val"] for r in recs}) == 1}
        refused, differ, same, emitted = [], [], 0, {"all": 0, "female": 0, "male": 0}
        this_year = date.today().year
        for key in sorted(cells):
            recs = cells[key]
            if len({r["val"] for r in recs}) > 1:
                refused.append(key)
                continue
            rec = recs[0]
            iso3, year, sex = key
            if key in core:
                if core[key] is not None and abs(core[key] - rec["val"]) > 0.5:
                    differ.append((key, core[key], rec["val"]))
                else:
                    same += 1
                continue
            provider = _text(rec["data_provider_specific"])
            extra = {
                "paho_indicator_id": _int(rec["paho_indicator_id"]),
                "paho_table": "Nuevos diagnosticos",
                "provider": provider,
                "source_data": _text(rec["data_source_type"]),
                "indicator_status": _text(rec["indicator_status"]),
                "preliminary": _text(rec["preliminary"]) or None,
                "fills": "a country, year and sex paho_core does not emit",
                "reconcile_with": "paho_core holds no row for the key. ht_mspp carries Haiti "
                                  "nationally and by department for 2020 to 2023, ar_snvs "
                                  "Argentina for 2015 to 2024 and py_mercosur Paraguay for "
                                  "2000 to 2009. Never compare with new_diagnoses",
            }
            if iso3 == "HTI" and "guyana" in provider.lower():
                extra["provider_mislabel"] = ("PAHO names the National AIDS Programme "
                                              "Secretariat of Guyana as provider of a Haitian row")
            if sex == "all":
                female, male = single.get((iso3, year, "female")), single.get((iso3, year, "male"))
                if female is not None and male is not None:
                    extra["female_plus_male"] = female + male
                    if abs(female + male - rec["val"]) > 0.5:
                        extra["sex_parts_mismatch"] = True
            if year >= this_year:
                extra["partial_year"] = True
            emitted[sex] += 1
            yield self.make_row(
                country_iso3=iso3,
                indicator_id="notified_hiv_cases",
                year=year,
                value=rec["val"],
                sex=sex,
                unit="count",
                source_url=_PAGE_URL,
                source_indicator_code=f"PAHO HIV dashboard, Nuevos diagnosticos, CI {extra['paho_indicator_id']}",
                extra=extra,
            )
        for key in refused:
            log.warning("paho_hiv: %s %s %s has %d rows with different values, none emitted",
                        key[0], key[1], key[2], len(cells[key]))
        for key, core_val, dash_val in differ:
            log.info("paho_hiv: %s %s %s paho_core %s, dashboard %s, the paho_core row stands",
                     key[0], key[1], key[2], core_val, dash_val)
        log.info("paho_hiv: notified_hiv_cases emitted %d total, %d female, %d male. %d keys equal "
                 "paho_core, %d differ from paho_core, %d refused. Skipped %s",
                 emitted["all"], emitted["female"], emitted["male"], same, len(differ),
                 len(refused), skipped)

    # -- share on a DTG regimen ------------------------------------------------------------
    def _dtg(self, wanted, start_year, end_year) -> Iterator[PanelRow]:
        raw = self._query("DTG", _DTG_COLUMNS)
        # (iso3, age, year) -> {line: [values]}, so a duplicate line is seen before any row
        cells: Dict[Tuple[str, str, int], Dict[str, List[float]]] = {}
        unknown_age = set()
        for rec in raw:
            code = _text(rec["ISO3"]).upper()
            iso3 = _ISO_FIX.get(code) or (to_iso3(code) if len(code) == 3 else None)
            age = _DTG_AGE.get(_text(rec["INDICATOR"]))
            year = _int(rec["Año"])
            val = _float(rec["Nº Personas DTG"])
            if age is None:
                unknown_age.add(_text(rec["INDICATOR"]))
                continue
            if iso3 is None or year is None or val is None:
                continue
            if wanted is not None and iso3 not in wanted:
                continue
            if year < start_year or year > end_year:
                continue
            cells.setdefault((iso3, age, year), {}).setdefault(_text(rec["Línea"]), []).append(val)
        if unknown_age:
            log.warning("paho_hiv: DTG rows under unknown INDICATOR labels skipped: %s",
                        sorted(unknown_age))

        emitted, refused = 0, []
        this_year = date.today().year
        for (iso3, age, year), lines in sorted(cells.items()):
            if any(len(set(v)) > 1 for v in lines.values()):
                refused.append((iso3, age, year, "conflicting values for one line"))
                continue
            one = {k: v[0] for k, v in lines.items()}
            total, dtg = one.get("TOTAL"), one.get("TOTAL en DTG")
            if total is None or dtg is None or total <= 0:
                continue
            if dtg > total:
                refused.append((iso3, age, year, f"DTG {dtg} above TOTAL {total}"))
                continue
            extra = {
                "paho_table": "DTG",
                "on_art_regimen_report": total,
                "on_dtg": dtg,
                "denominator_note": "TOTAL of the PAHO regimen report, not the national count "
                                    "on ART. Never compare with on_art_count",
                "regimen_scope": "dolutegravir or other second-generation integrase inhibitor, "
                                 "as PAHO heads the table",
            }
            for line in _LINES + _DTG_LINES:
                if line in one:
                    extra[_LINE_KEYS[line]] = one[line]
            if all(line in one for line in _LINES) and abs(sum(one[l] for l in _LINES) - total) > 0.5:
                extra["lines_sum_mismatch"] = True
            if all(line in one for line in _DTG_LINES) and abs(sum(one[l] for l in _DTG_LINES) - dtg) > 0.5:
                extra["dtg_lines_sum_mismatch"] = True
            if year >= this_year:
                extra["partial_year"] = True
            emitted += 1
            yield self.make_row(
                country_iso3=iso3,
                indicator_id="on_art_dtg_pct",
                year=year,
                value=round(100.0 * dtg / total, 2),
                age_group=age,
                unit="percent",
                numerator=dtg,
                denominator=total,
                source_url=_PAGE_URL,
                source_indicator_code="PAHO HIV dashboard, DTG, TOTAL en DTG / TOTAL",
                extra=extra,
            )
        for iso3, age, year, why in refused:
            log.warning("paho_hiv: DTG %s %s %s refused, %s", iso3, age, year, why)
        log.info("paho_hiv: on_art_dtg_pct emitted %d country-age-years, %d refused", emitted, len(refused))

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        # countries is None on a --countries all run, and None means every country.
        wanted = {c.strip().upper() for c in countries} if countries else None
        core = self._core_keys(sorted(wanted) if wanted else None, start_year, end_year)
        log.info("paho_hiv: paho_core fills %d country-year-sex keys", len(core))
        yield from self._notified(wanted, start_year, end_year, core)
        yield from self._dtg(wanted, start_year, end_year)
