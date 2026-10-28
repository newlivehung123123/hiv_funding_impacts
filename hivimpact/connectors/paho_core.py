"""
PAHO Core Indicators connector, connector 26, notified HIV cases reported by ministries of health.

PAHO (the Pan American Health Organization) publishes Core Indicator 93, the count of new HIV
diagnoses each ministry of health reports through national case surveillance, with indicators
94, 95 and 96 splitting the same count into female, male and unknown sex. The values sit in one
Power BI model (model 3091957, table Indicators_Data_2022) behind the four public Core
Indicators reports, and the public querydata endpoint of the first report answers a semantic
query without sign-in. The same table ships as a dated zip on the download page
(paho-core-indicators-2026-20261001.zip in October 2026, 157 MB of CSV), which is the fallback
route if the public report is ever withdrawn.

Coverage read on 6 October 2026 (docs/PHASE5_FEASIBILITY_LAC.md, notes line 773). Indicator 93
covers 22 of the 23 LAC countries of config/regions.py, from 1995 for Belize, Bolivia, Cuba,
Mexico and Brazil, and holds no row for Haiti. 833 rows over all of the Americas.

Why a separate indicator id. The panel's `new_diagnoses` counts people testing positive at
PEPFAR-supported or Global Fund-supported sites, a programme count, while Core Indicator 93 is
the national surveillance count of notified cases. For Brazil in 2024 the PEPFAR count is 1,156
against 39,216 notified. Jason ruled on 8 October 2026 that national notified cases go under
`notified_hiv_cases` and never into `new_diagnoses` (notes lines 2063 and 2065).

What the connector refuses, and why.
  - Indicator 96, unknown sex, is not a sex the panel carries. The count travels in the total
    row's extra.sex_unknown, and extra.sex_parts_mismatch marks any year where female, male and
    unknown do not add to the total.
  - The sex split is emitted only when the PAHO metadata labels indicator 94 female and 95 male.
    A renumbered model would otherwise put one sex's count under the other's name, so a label
    that fails the check drops the sex rows and keeps the totals.
  - A country code that is not an ISO3 country (a PAHO subregion or aggregate) is skipped.
  - Two rows for one country, indicator and year are summed by nobody. Equal values give one
    row. Different values give no row, and the log names the country-year.

Fragile by construction. The resource key, model id and wabi cluster below belong to the
published report. If PAHO republishes the report, the endpoint answers with an error object,
and the connector raises with the error text so run_all marks the source FAILED instead of
writing an empty source.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..connector_base import BaseConnector
from ..normalize import to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_QUERY_URL = ("https://wabi-south-central-us-c-primary-api.analysis.windows.net"
              "/public/reports/querydata?synchronous=true")
# the public page the report is embedded in, written into source_url for a human reader
_PAGE_URL = "https://opendata.paho.org/en/core-indicators/core-indicators-dashboard"

# "CI Dashboard-Latest data EN", the first of the four public Core Indicators reports
_REPORT = {
    "key": "8d6e4cfa-8ecc-4081-9edd-3906d860f515",
    "model_id": 3091957,
    "dataset_id": "85b19a22-3017-4eae-88c1-2c16f0ba6b35",
    "report_id": "8003301f-0c6d-4cad-ac9f-d9a6adc09dee",
}

TOTAL_ID = 93
SEX_IDS = {94: "female", 95: "male"}
UNKNOWN_SEX_ID = 96
ALL_IDS = [TOTAL_ID, *SEX_IDS, UNKNOWN_SEX_ID]

_DATA_COLUMNS = ["country_code_iso3", "indicator_id", "period_id", "key", "source_data",
                 "source_data_specific", "collection_method", "preliminary", "modified_at"]
_META_COLUMNS = ["id", "indicator_code", "label_en", "sex_code", "nondisaggregated_id",
                 "database_status", "data_collection_process"]


def _col(prop: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": prop},
            "Name": f"t.{prop}"}


def _sum(prop: str) -> dict:
    return {"Aggregation": {"Expression": {"Column": {"Expression": {"SourceRef": {"Source": "t"}},
                                                      "Property": prop}},
                            "Function": 0},
            "Name": f"Sum(t.{prop})"}


def _in(prop: str, values: List[int]) -> list:
    return [{"Condition": {"In": {
        "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": prop}}],
        "Values": [[{"Literal": {"Value": f"{v}L"}}] for v in values]}}}]


def decode_dsr(result: dict) -> List[list]:
    """Turn one Power BI querydata result into plain rows, in the order of the Select.

    The DSR format sends each row's values once. Bit i of R says column i repeats the previous
    row's value, bit i of the null mask says column i is empty, and the remaining values arrive
    in order in C. A column carrying DN is dictionary-encoded, and an integer in C is an index
    into that dictionary.
    """
    res = result["results"][0]["result"]
    if "data" not in res:
        raise RuntimeError(f"paho_core: querydata returned no data: {json.dumps(res)[:600]}")
    ds = res["data"]["dsr"]["DS"][0]
    if ds.get("IC") is False:
        # the window of 30,000 rows was too small, and a partial table must not reach the panel
        raise RuntimeError("paho_core: querydata reports an incomplete result window")
    dicts = ds.get("ValueDicts", {})
    ph = ds["PH"][0]
    dm = ph[next(iter(ph))]
    if not dm:
        return []
    schema = dm[0]["S"]
    n = len(schema)
    rows: List[list] = []
    prev: list = [None] * n
    for row in dm:
        out: list = [None] * n
        repeat = row.get("R", 0)
        nulls = row.get("Ø", 0)
        vals = row.get("C", [])
        ci = 0
        for i in range(n):
            if repeat & (1 << i):
                out[i] = prev[i]
            elif nulls & (1 << i):
                out[i] = None
            else:
                v = vals[ci]
                ci += 1
                dn = schema[i].get("DN")
                if dn and isinstance(v, int):
                    v = dicts[dn][v]
                out[i] = v
        rows.append(out)
        prev = out
    return rows


def _sex_from_label(label: str) -> str:
    text = (label or "").lower()
    if "female" in text or "women" in text:
        return "female"
    if re.search(r"\bmale\b", text) or re.search(r"\bmen\b", text):
        return "male"
    if "unknown" in text or "not specified" in text:
        return "unknown"
    return "all"


def _sex_of(rec: dict) -> str:
    """Sex of one PAHO indicator, from the English label, else from sex_code when the code is a letter."""
    sex = _sex_from_label(rec.get("label_en", ""))
    if sex != "all":
        return sex
    code = str(rec.get("sex_code") or "").strip().upper()
    return {"F": "female", "FEMALE": "female", "M": "male", "MALE": "male"}.get(code, "all")


def _int(v) -> Optional[int]:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _float(v) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


class PAHOCoreConnector(BaseConnector):
    source_id = "paho_core"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("PAHO Core Indicator 93, notified HIV cases from national case surveillance, "
                   "with the female and male split.")
    request_pause = 1.0
    timeout = 90

    def _query(self, entity: str, select: list, where: list) -> List[list]:
        query = {"Version": 2, "From": [{"Name": "t", "Entity": entity, "Type": 0}],
                 "Select": select}
        if where:
            query["Where"] = where
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

    def _indicator_meta(self) -> Dict[int, dict]:
        # The whole table (763 rows on 5 October 2026) is read and filtered here, because the
        # type of Indicators.id was never seen, and a Long literal against a text column fails.
        rows = self._query("Indicators", [_col(c) for c in _META_COLUMNS], [])
        meta: Dict[int, dict] = {}
        for r in rows:
            rec = dict(zip(_META_COLUMNS, r))
            iid = _int(rec["id"])
            if iid in ALL_IDS:
                meta[iid] = rec
        return meta

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        # countries is None on a --countries all run, and None means every country.
        wanted = {c.strip().upper() for c in countries} if countries else None

        meta = self._indicator_meta()
        if TOTAL_ID not in meta:
            raise RuntimeError("paho_core: indicator 93 is missing from the PAHO Indicators table")
        labels = {i: (meta.get(i) or {}).get("label_en", "") for i in ALL_IDS}
        sex_ok = all(_sex_of(meta.get(i) or {}) == sex for i, sex in SEX_IDS.items())
        sex_ok = sex_ok and _sex_of(meta[TOTAL_ID]) == "all"
        if not sex_ok:
            log.warning("paho_core: indicator metadata %s fails the sex check, sex rows dropped",
                        {i: (labels.get(i), (meta.get(i) or {}).get("sex_code")) for i in ALL_IDS})

        select = [_col(c) for c in _DATA_COLUMNS] + [_sum("val")]
        raw = self._query("Indicators_Data_2022", select, _in("indicator_id", ALL_IDS))

        # (iso3, indicator, year) -> list of records, so a duplicate is seen before any row is emitted
        cells: Dict[Tuple[str, int, int], List[dict]] = {}
        unmapped: Dict[str, int] = {}
        for r in raw:
            rec = dict(zip(_DATA_COLUMNS + ["val"], r))
            code = str(rec["country_code_iso3"] or "").strip()
            iso3 = to_iso3(code) if len(code) == 3 else None
            iid, year, val = _int(rec["indicator_id"]), _int(rec["period_id"]), _float(rec["val"])
            if iso3 is None:
                unmapped[code] = unmapped.get(code, 0) + 1
                continue
            if iid not in ALL_IDS or year is None:
                continue
            if wanted is not None and iso3 not in wanted:
                continue
            if year < start_year or year > end_year:
                continue
            rec["val"] = val
            cells.setdefault((iso3, iid, year), []).append(rec)

        chosen: Dict[Tuple[str, int, int], dict] = {}
        refused = []
        for k, recs in cells.items():
            values = {rec["val"] for rec in recs}
            if len(values) == 1:
                chosen[k] = recs[0]
            else:
                refused.append(k)
        for k in sorted(refused):
            log.warning("paho_core: %s indicator %s %s has %d rows with different values, none emitted",
                        k[0], k[1], k[2], len(cells[k]))
        if unmapped:
            log.info("paho_core: skipped %d rows under codes that are not ISO3 countries: %s",
                     sum(unmapped.values()), ", ".join(sorted(unmapped)))

        this_year = date.today().year
        emitted = {"all": 0, "female": 0, "male": 0}
        for (iso3, iid, year), rec in sorted(chosen.items()):
            if iid == UNKNOWN_SEX_ID:
                continue
            sex = "all" if iid == TOTAL_ID else SEX_IDS[iid]
            if sex != "all" and not sex_ok:
                continue
            if rec["val"] is None:
                continue
            extra = {
                "paho_indicator_id": iid,
                "paho_label": labels.get(iid, ""),
                "provider": rec.get("source_data_specific") or "",
                "source_data": rec.get("source_data") or "",
                "collection_method": rec.get("collection_method") or "",
                "preliminary": rec.get("preliminary"),
                "paho_modified_at": rec.get("modified_at"),
                "paho_key": rec.get("key"),
                "reconcile_with": "no other source carries notified_hiv_cases. Never compare "
                                  "with new_diagnoses, which counts programme positives",
            }
            if year >= this_year:
                extra["partial_year"] = True
            if iid == TOTAL_ID:
                parts = {s: chosen.get((iso3, i, year)) for i, s in
                         [*SEX_IDS.items(), (UNKNOWN_SEX_ID, "unknown")]}
                unknown = parts["unknown"]["val"] if parts["unknown"] else None
                if unknown is not None:
                    extra["sex_unknown"] = unknown
                if all(p is not None and p["val"] is not None for p in parts.values()):
                    if abs(sum(p["val"] for p in parts.values()) - rec["val"]) > 0.5:
                        extra["sex_parts_mismatch"] = True
            emitted[sex] += 1
            yield self.make_row(
                country_iso3=iso3,
                indicator_id="notified_hiv_cases",
                year=year,
                value=rec["val"],
                sex=sex,
                unit="count",
                source_url=_PAGE_URL,
                source_indicator_code=f"PAHO CI {iid}",
                extra=extra,
            )
        log.info("paho_core: emitted %d total rows, %d female, %d male, %d country-years refused",
                 emitted["all"], emitted["female"], emitted["male"], len(refused))
