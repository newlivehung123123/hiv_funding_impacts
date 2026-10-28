"""
Pacific Data Hub connector, three HIV survey measures from table DF_HEALTH of the Pacific
Data Hub, the statistics service of SPC (the Pacific Community, the regional technical and
scientific organisation of the Pacific), under ruling R22 of research/rulings_2026-10-15.md.

The Pacific Data Hub runs an SDMX (Statistical Data and Metadata eXchange) service at
stats-sdmx-disseminate.pacificdata.org. Table DF_HEALTH under the topic HIV holds 58 indicators
(HIV_01 to HIV_58) from the Pacific Demographic and Health Surveys (DHS) of Kiribati 2009, the
Marshall Islands 2007, Nauru 2007, Solomon Islands 2007 and 2015, Tonga 2012, Tuvalu 2007,
Vanuatu 2013 and Samoa 2009 and 2014, 580 HIV values in the answer of 16 October 2026, every
value a percentage.

What the connector reads, under the DHS standard definitions the SPC labels follow:
  hiv_comprehensive_knowledge_survey_pct   HIV_14 (women 15-49), HIV_16 (men 15+),
                                           HIV_47 (women 15-24), HIV_49 (men 15-24)
  condom_last_higher_risk_sex_survey_pct   HIV_34 (women 15-49), HIV_38 (men 15+)
  sex_before_15_survey_pct                 HIV_51 (women 15-24), HIV_53 (men 15-24)

The Pacific surveys interviewed men aged 15 and over, so the men's knowledge and condom values
carry age_group 15+ and the women's values carry 15-49. age_group keeps the two age ranges
apart, and reconcile never compares rows covering different ages (ruling R17).

What the connector leaves unread, and the reason:
  - The components of comprehensive knowledge (HIV_01 to HIV_13 and HIV_15), the knowledge of
    transmission by breastfeeding (HIV_17 and HIV_18) and the knowledge of a condom source
    (HIV_48 and HIV_50), parts of a composite measure or items with no panel indicator.
  - The attitudes towards people living with HIV (HIV_19 to HIV_26) and the gender attitudes
    on safer sex (HIV_27 to HIV_30), measures of attitude and not of HIV knowledge, risk or
    service use.
  - The partner counts and the condom use among respondents with several partners (HIV_31,
    HIV_33, HIV_35 and HIV_37). The SPC labels read "more than 2 partners", and the DHS
    standard counts two or more partners, so the labels and the standard give two different
    definitions and the connector cannot tell which definition the values follow.
  - The share of respondents with higher-risk intercourse (HIV_32 and HIV_36), the denominator
    of HIV_34 and HIV_38 and not a panel measure.
  - The symptoms of sexually transmitted infections (HIV_39 to HIV_46), sex before age 18
    (HIV_52 and HIV_54), condom use at first sex (HIV_55 and HIV_56) and sex when drunk
    (HIV_57 and HIV_58), measures outside the three of ruling R22.
  - A value with observation status O (missing) gives no row. A value with status U (low
    reliability) gives a row with extra.obs_status "U".
  - SH_HIV_INCD in table DF_SDG_03, new HIV infections per 1,000 uninfected people, a rate the
    panel can compute from new_infections, plhiv and population, the reason
    unaids_aidsinfo.DECLARED_UNMAPPED gives for the AIDSinfo export of the same rate.

The SPC country codes are ISO 3166-1 alpha-2 codes, and _GEO maps the codes to alpha-3 by a
closed list, so an unknown code gives no row and a log line. Nauru (NRU) is outside the
country list of hivimpact/config/regions.py and enters only under --countries all, as with
every other global connector.
"""
from __future__ import annotations

import csv
import io
import logging
from collections import Counter
from datetime import date
from typing import Dict, Iterable, Iterator, Optional, Tuple

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..schema import PanelRow, SourceType, POP_ALL

log = logging.getLogger("hivimpact")

_BASE = "https://stats-sdmx-disseminate.pacificdata.org/rest/data/SPC,DF_HEALTH,1.0/"
_ACCEPT = "application/vnd.sdmx.data+csv;version=1.0.0;labels=both"

# SPC indicator code -> (panel indicator, sex, SPC age code)
_MAP: Dict[str, Tuple[str, str, str]] = {
    "HIV_14": ("hiv_comprehensive_knowledge_survey_pct", "female", "Y15T49"),
    "HIV_16": ("hiv_comprehensive_knowledge_survey_pct", "male", "Y15T999"),
    "HIV_47": ("hiv_comprehensive_knowledge_survey_pct", "female", "Y15T24"),
    "HIV_49": ("hiv_comprehensive_knowledge_survey_pct", "male", "Y15T24"),
    "HIV_34": ("condom_last_higher_risk_sex_survey_pct", "female", "Y15T49"),
    "HIV_38": ("condom_last_higher_risk_sex_survey_pct", "male", "Y15T999"),
    "HIV_51": ("sex_before_15_survey_pct", "female", "Y15T24"),
    "HIV_53": ("sex_before_15_survey_pct", "male", "Y15T24"),
}
_SEX = {"F": "female", "M": "male"}
_AGE = {"Y15T49": "15-49", "Y15T999": "15+", "Y15T24": "15-24"}
# SPC alpha-2 code -> ISO3, the eight countries with HIV values in DF_HEALTH
_GEO = {"KI": "KIR", "MH": "MHL", "NR": "NRU", "SB": "SLB", "TO": "TON", "TV": "TUV",
        "VU": "VUT", "WS": "WSM"}


def _code(cell: Optional[str]) -> str:
    """The code part of a labels=both cell, for example "SB" from "SB: Solomon Islands"."""
    return (cell or "").split(":", 1)[0].strip()


def _label(cell: Optional[str]) -> str:
    """The label part of a labels=both cell, for example "Solomon Islands"."""
    parts = (cell or "").split(":", 1)
    return parts[1].strip() if len(parts) == 2 else ""


def _column(header: Iterable[str], code: str) -> str:
    """The header of a labels=both CSV names a column "CODE: Label", and the code finds the column."""
    for name in header:
        if _code(name) == code:
            return name
    raise KeyError(f"pacific_data_hub: no column {code} in the CSV answer")


class PacificDataHubConnector(BaseConnector):
    source_id = "pacific_data_hub"
    default_source_type = SourceType.SURVEY
    description = ("Pacific Data Hub of SPC (SDMX API), comprehensive HIV knowledge, condom use "
                   "at last higher-risk sex and sex before 15 from the Pacific Demographic and "
                   "Health Surveys, by sex and age group.")
    request_pause = 0.5
    timeout = 90

    def _query(self) -> Tuple[str, str]:
        """One SDMX CSV request for every indicator in _MAP, returning the URL and the CSV text."""
        key = "A..HIV." + "+".join(_MAP) + ".."   # FREQ, GEO_PICT, TOPIC, INDICATOR, SEX, AGE
        url = _BASE + key
        resp = self._request("GET", url, params={"dimensionAtObservation": "AllDimensions"},
                             headers={"Accept": _ACCEPT})
        return resp.url or url, resp.text

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or date.today().year
        url, text = self._query()
        yield from self.parse(text, url, countries, start_year, end_year)

    def parse(
        self,
        text: str,
        url: str,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        """Rows from the labels=both CSV answer of DF_HEALTH, with every refusal counted in the log."""
        end_year = end_year or date.today().year
        wanted = set(c.upper() for c in countries) if countries else None
        reader = csv.DictReader(io.StringIO(text))
        header = reader.fieldnames or []
        col = {c: _column(header, c) for c in ("TIME_PERIOD", "GEO_PICT", "INDICATOR", "SEX", "AGE",
                                               "UNIT_MEASURE", "OBS_STATUS")}
        col_comment = next((h for h in header if _code(h) == "OBS_COMMENT"), None)
        col_source = next((h for h in header if _code(h) == "DATA_SOURCE"), None)
        skipped: Counter = Counter()
        seen = set()
        written: Counter = Counter()
        for r in reader:
            spc_id = _code(r.get(col["INDICATOR"]))
            spec = _MAP.get(spc_id)
            if spec is None:
                skipped["indicator outside ruling R22"] += 1
                continue
            canonical, sex_want, age_want = spec
            status = _code(r.get(col["OBS_STATUS"]))
            if status == "O":
                skipped["observation status O (missing)"] += 1
                continue
            geo = _code(r.get(col["GEO_PICT"]))
            iso3 = _GEO.get(geo)
            if iso3 is None:
                skipped["country code outside _GEO"] += 1
                log.info("pacific_data_hub: %s %s refused, unknown country code %r", spc_id,
                         r.get(col["TIME_PERIOD"]), geo)
                continue
            if wanted is not None and iso3 not in wanted:
                continue
            sex = _SEX.get(_code(r.get(col["SEX"])))
            age_code = _code(r.get(col["AGE"]))
            if sex != sex_want or age_code != age_want:
                skipped["sex or age code unlike the SPC label"] += 1
                log.info("pacific_data_hub: %s %s %s refused, sex %r and age %r", spc_id, iso3,
                         r.get(col["TIME_PERIOD"]), sex, age_code)
                continue
            if _code(r.get(col["UNIT_MEASURE"])) != "PERCENT":
                skipped["unit other than PERCENT"] += 1
                continue
            try:
                year = int(_code(r.get(col["TIME_PERIOD"])))
                value = float(r.get("OBS_VALUE") or "")
            except ValueError:
                skipped["year or value not a number"] += 1
                continue
            if year < start_year or year > end_year:
                continue
            key = (iso3, canonical, sex, age_code, year)
            if key in seen:
                skipped["repeated key"] += 1
                continue
            seen.add(key)
            extra = {"survey": "Pacific DHS", "spc_indicator": _label(r.get(col["INDICATOR"]))}
            if status:
                extra["obs_status"] = status
            if col_comment and r.get(col_comment):
                extra["obs_comment"] = r[col_comment]
            if col_source and r.get(col_source):
                extra["data_source"] = r[col_source]
            written[canonical] += 1
            yield self.make_row(
                country_iso3=iso3, country_name=_label(r.get(col["GEO_PICT"])),
                indicator_id=canonical, year=year, value=value,
                population_group=POP_ALL, sex=sex, age_group=_AGE[age_code],
                unit=CANONICAL_INDICATORS[canonical].unit,
                source_url=url, source_indicator_code=spc_id, extra=extra,
            )
        for canonical, n in sorted(written.items()):
            log.info("pacific_data_hub: %s %d rows", canonical, n)
        for reason, n in sorted(skipped.items()):
            log.info("pacific_data_hub: %d values refused, %s", n, reason)
