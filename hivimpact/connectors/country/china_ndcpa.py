"""
China, reported AIDS cases and deaths among reported AIDS patients from the yearly notifiable
disease tables of the National Disease Control and Prevention Administration (connector 36).

Source. The National Disease Control and Prevention Administration (NDCPA, www.ndcpa.gov.cn)
publishes the channel 疫情信息 (epidemic information, channel code c100016) through the
Department of Surveillance and Early Warning (监测预警司). The listing page is drawn by
JavaScript from a POST to https://www.ndcpa.gov.cn/queryList, and the list answer holds the
full HTML of every article, so the connector reads the tables from the list answer with no
second request. On 15 October 2026 the list held 51 articles, 48 monthly reports from
September 2022 to August 2026 and yearly reports for 2023, 2024 and 2025, every table in HTML.
No sign-in and no key.

Yearly tables only (ruling R10 of research/rulings_2026-10-15.md). The connector reads the
articles titled "{year}年全国法定传染病疫情概况" (overview of the national notifiable disease
situation for the year) and never sums the monthly reports. The monthly tables count cases by
the date of final review (终审日期) and the yearly tables count the year's verified cases by the
date of onset (发病日期), and the 12 monthly AIDS counts sum to 59,533 cases for 2023, 55,344
for 2024 and 49,756 for 2025, above the yearly totals of 58,903, 54,931 and 49,326. The Chinese
years before 2023 stay empty, because the NDCPA list holds no yearly table for a year before
2023.

What the AIDS row counts. The 艾滋病 (AIDS) row of the yearly table holds 发病数 (reported
cases), 死亡数 (deaths) and the two rates per 100,000.
  aids_cases_reported. The first note of the yearly table says the table counts the year's reported
  clinical and laboratory-confirmed cases by the date of onset, without foreign nationals,
  Hong Kong, Macao and Taiwan. The Guangdong table of the same reporting system says the
  Guangdong counts exclude 病原携带者 (pathogen carriers, people with HIV who have not reached
  the AIDS stage), and the national count of 49,326 for 2025 sits 38,555 below the second-hand
  bulletin figure of 87,881 HIV/AIDS cases for 2025, so the AIDS row is read as a count of AIDS
  cases and never as a count of HIV diagnoses. The table names no AIDS diagnostic standard,
  so extra.case_definition carries the wording of the first note.
  aids_deaths_reported. The third note says the AIDS deaths are the all-cause deaths reported in
  the year among cumulative reported AIDS patients, the definition of aids_deaths_reported. A
  death row carries the AIDS case wording of the first note in extra.case_definition, as the
  case rows do, and the wording of the third note in extra.death_definition.
A table whose first note names no count by the date of onset gives no row for the year, and a
table whose third note gives another death definition gives no death row for the year.

Check against the China CDC annual page. The Chinese Center for Disease Control and
Prevention (China CDC) printed the 2023 yearly table at www.chinacdc.cn/jksj/jksj01/ with
58,903 AIDS cases and 22,137 deaths, the NDCPA figures. The China CDC listing pages carry no
yearly table for 2024 or 2025. The connector reads the China CDC page for 2023 at run time and
writes the outcome to extra.china_cdc_annual_page. A China CDC figure differing from the NDCPA
figure gives no row for the year and the indicator, because two official yearly figures
disagreeing leave the true figure unknown. A failed China CDC request leaves the NDCPA row in
place with extra.china_cdc_annual_page set to "not read in the run".

Rows from the saved answers of 15 October 2026, in an offline test with the network blocked.
Six rows, national, for 2023 to 2025.
  aids_cases_reported. 58,903 for 2023, 54,931 for 2024 and 49,326 for 2025.
  aids_deaths_reported. 22,137 for 2023, 19,970 for 2024 and 19,097 for 2025.
The rates per 100,000 travel in extra.rate_per_100000, with the population note of the table
in extra.population_note. The 2025 rates use the resident population at the end of 2024 from
the National Bureau of Statistics.

Not carried. The 48 monthly reports (counted by the date of final review). The second-hand
bulletin figure of 87,881 HIV/AIDS cases for 2025, which no page read so far prints. Monthly
provincial tables, including the Guangdong Word files (ruling R10).

Source type. routine_programme_record, for the counts of the national notifiable disease
reporting system.
"""
from __future__ import annotations

import json
import logging
import re
from html.parser import HTMLParser
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...config.indicators import CANONICAL_INDICATORS
from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL

log = logging.getLogger("hivimpact")

_SITE = "https://www.ndcpa.gov.cn"
_LIST_URL = _SITE + "/queryList"
_LIST_FORM = {"webSiteCode[]": "jbkzzx", "channelCode[]": "c100016"}
_PAGE_SIZE = 10
_YEARLY_TITLE = re.compile(r"^\s*(\d{4})年全国法定传染病疫情概况\s*$")

# China CDC annual pages, found on the listing pages www.chinacdc.cn/jksj/jksj01/index_2.html
# on 15 October 2026
_CHINA_CDC_ANNUAL = {
    2023: "https://www.chinacdc.cn/jksj/jksj01/202410/t20241010_301346.html",
}

_AIDS_ROW = "艾滋病"
# header cell -> field, matched on the text before the bracketed unit
_HEADER = {"发病数": "cases", "死亡数": "deaths", "发病率": "case_rate", "死亡率": "death_rate"}
_ONSET_BASIS = "按发病日期统计的临床诊断病例和实验室确诊病例"
_DEATH_DEFINITION = "艾滋病死亡数是累计报告艾滋病病人在当年报告的全死因死亡数"

_INDICATORS = (
    ("aids_cases_reported", "cases", "case_rate", "发病数"),
    ("aids_deaths_reported", "deaths", "death_rate", "死亡数"),
)
_CASE_DEFINITION = ("the year's reported clinical and laboratory-confirmed AIDS cases counted by "
                    "the date of onset, in the Chinese national notifiable disease reporting "
                    "system (the first note of the NDCPA yearly table, which names no diagnostic "
                    "standard)")
_DEATH_DEFINITION_EN = ("all-cause deaths reported in the year among cumulative reported AIDS "
                        "patients (the third note of the NDCPA yearly table)")


class _TableRows(HTMLParser):
    """Collects the text of every table row, a list of cell strings with whitespace removed."""

    def __init__(self):
        super().__init__()
        self.rows: List[List[str]] = []
        self._row: Optional[List[str]] = None
        self._cell: Optional[List[str]] = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", "", "".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def _plain(html_text: str) -> str:
    """The article text with tags and whitespace removed, for matching the table notes."""
    import html as _html
    return re.sub(r"\s+", "", _html.unescape(re.sub(r"<[^>]+>", "", html_text)))


def _number(cell: str) -> Optional[float]:
    cell = cell.replace(",", "").replace("，", "")
    if not re.fullmatch(r"\d+(\.\d+)?", cell):
        return None
    return float(cell)


def parse_aids_row(html_text: str) -> Optional[Dict[str, float]]:
    """The AIDS row of a notifiable disease table as {cases, deaths, case_rate, death_rate}, or
    None when the header is not the expected header or the AIDS row is missing or repeated."""
    parser = _TableRows()
    parser.feed(html_text)
    header = next((r for r in parser.rows if r and r[0] == "病名"), None)
    if header is None:
        return None
    columns: Dict[str, int] = {}
    for i, cell in enumerate(header):
        key = re.split(r"[（(]", cell)[0]
        if key in _HEADER:
            columns[_HEADER[key]] = i
    if set(columns) != set(_HEADER.values()):
        return None
    aids = [r for r in parser.rows if r and r[0] == _AIDS_ROW]
    if len(aids) != 1:
        return None
    row = aids[0]
    out: Dict[str, float] = {}
    for field, i in columns.items():
        value = _number(row[i]) if i < len(row) else None
        if value is None:
            return None
        out[field] = value
    return out


def _note(plain: str, number: int) -> str:
    """Note `number` of the table notes (注), up to the next numbered note."""
    m = re.search(rf"(?<!\d){number}\.(.*?)(?=(?<!\d)\d\.|$)", plain.split("注：", 1)[-1])
    return m.group(1) if m else ""


class ChinaNDCPAConnector(BaseConnector):
    """China NDCPA yearly notifiable disease tables, reported AIDS cases and AIDS deaths."""

    source_id = "cn_ndcpa"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("China National Disease Control and Prevention Administration yearly "
                   "notifiable disease tables, with reported AIDS cases and deaths among "
                   "reported AIDS patients, national, from 2023 (to-source).")
    country = "CHN"
    request_pause = 1.0
    # the list answer for 10 articles is about 700,000 bytes from a slow host
    timeout = 300

    def _articles(self) -> List[dict]:
        articles: List[dict] = []
        page, total = 1, None
        while total is None or len(articles) < total:
            form = dict(_LIST_FORM, current=str(page), pageSize=str(_PAGE_SIZE))
            data = self._request("POST", _LIST_URL, data=form).json()["data"]
            total = int(data["total"])
            results = data.get("results") or []
            if not results:
                break
            articles += [r["source"] for r in results]
            page += 1
        if total is not None and len(articles) != total:
            log.warning("cn_ndcpa: the list route gave %d of %d articles", len(articles), total)
        return articles

    def _china_cdc(self, year: int) -> Tuple[str, Optional[Dict[str, float]]]:
        url = _CHINA_CDC_ANNUAL.get(year)
        if not url:
            return "", None
        try:
            return url, parse_aids_row(self._request("GET", url).text)
        except Exception as exc:
            log.warning("cn_ndcpa: the China CDC annual page for %d was not read (%s)", year, exc)
            return url, None

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = {c.upper() for c in countries} if countries else None
        if wanted and self.country not in wanted:
            return
        try:
            articles = self._articles()
        except Exception as exc:
            log.warning("cn_ndcpa: the NDCPA list route failed (%s)", exc)
            return
        yearly: Dict[int, List[dict]] = {}
        for art in articles:
            m = _YEARLY_TITLE.match(art.get("title") or "")
            if m and start_year <= int(m.group(1)) <= end_year:
                yearly.setdefault(int(m.group(1)), []).append(art)
        emitted = 0
        for year in sorted(yearly):
            for row in self._year_rows(year, yearly[year]):
                emitted += 1
                yield row
        log.info("cn_ndcpa: %d yearly tables (%s), emitted %d rows", len(yearly),
                 ", ".join(str(y) for y in sorted(yearly)), emitted)

    def _year_rows(self, year: int, arts: List[dict]) -> Iterator[PanelRow]:
        parsed = []
        for art in arts:
            content = (art.get("content") or {}).get("content") or ""
            values = parse_aids_row(content)
            plain = _plain(content)
            if values is None:
                log.warning("cn_ndcpa: %d, article %s holds no readable AIDS row, no row "
                            "emitted", year, art.get("id"))
                continue
            if _ONSET_BASIS not in plain:
                log.warning("cn_ndcpa: %d, article %s names no count by the date of onset, "
                            "no row emitted", year, art.get("id"))
                continue
            parsed.append((art, values, plain))
        if not parsed:
            return
        if len({json.dumps(v, sort_keys=True) for _, v, _ in parsed}) > 1:
            log.warning("cn_ndcpa: %d, %d yearly articles disagree on the AIDS row, no value "
                        "emitted", year, len(parsed))
            return
        art, values, plain = parsed[0]
        cdc_url, cdc = self._china_cdc(year)
        try:
            urls = json.loads(art.get("urls") or "{}")
        except ValueError:
            urls = {}
        page = _SITE + urls["common"] if urls.get("common") else _SITE + "/jbkzzx/c100016/"
        for indicator, field, rate_field, column in _INDICATORS:
            if indicator == "aids_deaths_reported" and _DEATH_DEFINITION not in plain:
                log.warning("cn_ndcpa: %d, the third table note gives no all-cause death count among "
                            "reported AIDS patients, no death row emitted", year)
                continue
            if cdc_url and cdc is None:
                cdc_check = "not read in the run"
            elif cdc_url and cdc[field] != values[field]:
                log.warning("cn_ndcpa: %d, %s, the China CDC annual page reads %s against the "
                            "NDCPA %s, no value emitted", year, indicator, cdc[field],
                            values[field])
                continue
            elif cdc_url:
                cdc_check = f"agrees ({cdc_url})"
            else:
                cdc_check = "no China CDC annual page for the year"
            yield self._row(indicator, year, values[field], values[rate_field], column, art,
                            page, plain, cdc_check)

    def _row(self, indicator: str, year: int, value: float, rate: float, column: str,
             art: dict, page: str, plain: str, cdc_check: str) -> PanelRow:
        spec = CANONICAL_INDICATORS[indicator]
        extra: Dict = {
            "ndcpa_article_id": str(art.get("id") or ""),
            "ndcpa_title": (art.get("title") or "").strip(),
            "ndcpa_published": art.get("pubDate") or art.get("publishTime") or "",
            "publisher": art.get("contentSource") or "",
            "count_basis": "yearly table by the date of onset, never a sum of monthly tables",
            "rate_per_100000": rate,
            "table_note_1": _note(plain, 1),
            "population_note": next((_note(plain, n) for n in range(1, 12)
                                     if "人口资料" in _note(plain, n)), ""),
            "china_cdc_annual_page": cdc_check,
        }
        extra["case_definition"] = _CASE_DEFINITION
        if indicator == "aids_deaths_reported":
            extra["death_definition"] = _DEATH_DEFINITION_EN
            extra["table_note_3"] = _note(plain, 3)
        return self.make_row(
            country_iso3="CHN", country_name="China",
            indicator_id=indicator, year=year, value=value,
            population_group=POP_ALL, unit=spec.unit,
            source_url=page,
            source_indicator_code=f"c100016:{_AIDS_ROW}:{column}",
            extra=extra,
        )
