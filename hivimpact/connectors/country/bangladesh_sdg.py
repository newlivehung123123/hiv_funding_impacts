"""
Bangladesh, notified HIV cases by sex from the SDG Tracker of the Bangladesh Bureau of Statistics
(https://sdg.gov.bd/), connector 68.

Source. The SDG Tracker (the national platform for the Sustainable Development Goals, run by the
SDG Cell of the Bangladesh Bureau of Statistics with the a2i Programme) prints indicator 3.3.1
for two sources, UNAIDS (source id 28) and the National AIDS/STD Programme of the Directorate
General of Health Services (NASP, source id 27). The goal 3 page
(/indicator-information/7AYriX9) carries a form token, and the page script posts the token, the
source id and the indicator id (32) to /get-source-wise-data-value, which answers with a JSON
reply holding the table as HTML. The reply was read on 21 October 2026. No sign-in and no key.
The connector stores the reply once in `raw_dir`, and every later run reads the cached copy.

Table read. The NASP table prints, for 2019, 2022 and 2024, the new HIV cases by age (0-14,
15-24, 15-49 and 50 years and older), by gender (Male, Female and Transgender) and a "Total"
column holding a rate per 1,000 population (0.006, 0.006 and 0.008). The Male, Female and
Transgender counts of every year sum to the World AIDS Day count of the ASP for the same year
(919, 947 and 1,438), so the tracker years follow the ASP reporting year from 1 November of the
year before to 31 October (ruling R42 of research/rulings_2026-10-15.md).

Gates (ruling R52). A year enters only when every check below passes, because two published
figures disagreeing leave the true figure unknown.
  The table header names the 11 columns read on 21 October 2026, in the same order.
  Male, Female and Transgender sum to the ASP World AIDS Day count of the year.
  Every gender count over the ASP count rounds to the share the ASP World AIDS Day file of the
  year prints in the gender chart of the new cases (2022 to the nearest tenth of a per cent,
  70.5, 28.6 and 0.8, and 2024 to the nearest whole per cent, 77, 22 and 1).

What the connector emits. National notified_hiv_cases for Bangladesh, sex "male" and "female",
age group "all", for 2022 and 2024. The Transgender count travels in extra, because the panel
holds no sex value for hijra and transgender people.

Not carried (ruling R52).
  The 2019 gender counts. The 2019 ASP gender chart covers the 813 cases of the host population
  alone, while the tracker counts sum to 919, the count with the FDMN cases (Forcibly Displaced
  Myanmar Nationals), so no ASP figure checks the 2019 counts.
  The age counts. The 2019 and 2022 ASP files print the age groups 0-5, 6-9, 10-18, 19-24 and
  25-49, from which the tracker age groups 0-14 and 15-24 cannot be formed, the tracker count for 0-14 in
  2019 (53) equals the ASP host count for 0 to 18 years (26, 10 and 17), and the text layer of
  the 2024 ASP age chart prints the shares apart from the age labels.
  The "Total" rate, a rate per 1,000 population derived from national case reports, which fits
  no indicator id of the panel (ruling R51).
  The UNAIDS source, 0.01 per 1,000 for 2016, a rounded copy of the UNAIDS estimate which
  unaids_aidsinfo carries.
  The national metadata file "HIV SDG 2019 2022 2024.pdf" (105,529 bytes), a scanned page with
  no text layer, which would need optical character recognition (ruling R25).

Source type. routine_programme_record, the national HIV case reports of the NASP.
"""
from __future__ import annotations

import html as _html
import json
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL

log = logging.getLogger("hivimpact")

_SITE = "https://sdg.gov.bd"
_GOAL_PAGE = _SITE + "/indicator-information/7AYriX9"
_DATA_URL = _SITE + "/get-source-wise-data-value"
_SOURCE_NASP = "27"
_INDICATOR_331 = "32"

_HEADER = ["Years", "0-14 years", "15-24 years", "15-49 years", "50 years and older", "Male",
           "Female", "Transgender", "Total", "Target", "Status"]

# Reporting year: (ASP World AIDS Day count of new cases, ASP gender shares in per cent as
# printed for Male, Female and Hijra/Transgender, decimals the ASP prints). Read with pdfplumber
# from the World AIDS Day files of 2022 (f1ae11518ac947828bfffdecd1d3b0a4.pdf, page 10) and 2024
# (a30b7bb8bb6844c69bf7319d88084183.pdf, page 8) on 21 October 2026.
_ASP_CHECK = {
    2022: (947, (70.5, 28.6, 0.8), 1),
    2024: (1438, (77.0, 22.0, 1.0), 0),
}

_DEFINITION = ("people newly reported HIV positive in Bangladesh in the reporting year of the "
               "AIDS/STD Programme, 1 November of the year before to 31 October, FDMN cases "
               "included, by gender, the NASP series of indicator 3.3.1 of the SDG Tracker")
_RECONCILE = ("Male, Female and Transgender sum to the bd_asp count of the same year. Never "
              "compare with new_diagnoses (Jason's ruling of 8 October 2026)")
_NOT_CARRIED = ("the 2019 gender counts (no ASP figure checks the 2019 counts), the age counts "
                "(the ASP age groups of 2019 and 2022 differ, and the 2024 chart prints the "
                "shares apart from the labels), the Total rate per 1,000 population (ruling R51) "
                "and the UNAIDS source (a rounded copy of the UNAIDS estimate)")


def _cells(row_html: str) -> List[str]:
    cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, re.S)
    return [re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in cells]


def parse_reply(reply: Dict) -> Dict[int, Dict[str, int]]:
    """Gender counts by year from the NASP reply, after the header gate."""
    table = reply.get("disagg_html") or ""
    rows = [_cells(r) for r in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S)]
    header = next((r for r in rows if r and r[0] == "Years"), None)
    if header is None or header[:len(_HEADER)] != _HEADER:
        raise ValueError(f"the table header changed ({header!r})")
    out: Dict[int, Dict[str, int]] = {}
    for r in rows:
        if not r or not re.fullmatch(r"\d{4}", r[0]) or r[5] == "-":
            continue
        out[int(r[0])] = {"male": int(r[5]), "female": int(r[6]), "transgender": int(r[7])}
    return out


def check_year(year: int, counts: Dict[str, int]) -> None:
    """Raise unless the gender counts of `year` agree with the ASP World AIDS Day file."""
    total, shares, decimals = _ASP_CHECK[year]
    got = counts["male"] + counts["female"] + counts["transgender"]
    if got != total:
        raise ValueError(f"{year}: the gender counts sum to {got}, the ASP count is {total}")
    for key, share in zip(("male", "female", "transgender"), shares):
        printed = round(100.0 * counts[key] / total, decimals)
        if printed != share:
            raise ValueError(f"{year}: {key} gives {printed} per cent, the ASP prints {share}")


class BangladeshSDGConnector(BaseConnector):
    source_id = "bd_sdg"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("SDG Tracker of Bangladesh, NASP series of indicator 3.3.1, people newly "
                   "reported HIV positive by gender in the reporting year from November to "
                   "October, national, 2022 and 2024 (to-source).")
    country = "BGD"
    timeout = 60

    def __init__(self, raw_dir: str = "data/raw/bd_sdg", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _reply(self) -> Dict:
        """The NASP reply for indicator 3.3.1, posting once and then reading the cached copy."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / "bd_sdg_331_nasp.json"
        if path.exists():
            log.info("bd_sdg: using cached %s", path)
        else:
            page = self._request("GET", _GOAL_PAGE).text
            token = re.search(r'name="_token" value="([^"]+)"', page)
            if token is None:
                raise RuntimeError(f"{_GOAL_PAGE} holds no form token")
            resp = self._request(
                "POST", _DATA_URL,
                data={"_token": token.group(1), "srcId": _SOURCE_NASP, "indicatorId": _INDICATOR_331},
                headers={"X-Requested-With": "XMLHttpRequest", "Referer": _GOAL_PAGE},
            )
            path.write_bytes(resp.content)
            log.info("bd_sdg: stored the NASP reply (%d bytes) -> %s", len(resp.content), path)
        reply = json.loads(path.read_text(encoding="utf-8"))
        if reply.get("responseCode") != 1:
            raise RuntimeError(f"the reply in {path} carries responseCode {reply.get('responseCode')!r}")
        return reply

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
            series = parse_reply(self._reply())
            for year in _ASP_CHECK:
                if year not in series:
                    raise ValueError(f"the table holds no {year} row")
                check_year(year, series[year])
        except Exception as exc:
            log.warning("bd_sdg: the NASP reply failed a gate (%s), no row emitted", exc)
            return
        emitted = 0
        for year in sorted(_ASP_CHECK):
            if not start_year <= year <= end_year:
                continue
            counts = series[year]
            for sex in ("male", "female"):
                extra = {
                    "definition": _DEFINITION,
                    "reporting_period": f"1 November {year - 1} to 31 October {year}",
                    "transgender_cases": counts["transgender"],
                    "asp_check": (f"Male, Female and Transgender sum to {_ASP_CHECK[year][0]}, the "
                                  f"ASP World AIDS Day count of {year}, and every gender count "
                                  "rounds to the share of the ASP gender chart"),
                    "reconcile_with": _RECONCILE,
                    "not_carried": _NOT_CARRIED,
                }
                emitted += 1
                yield self.make_row(
                    country_iso3="BGD", country_name="Bangladesh", admin1="",
                    indicator_id="notified_hiv_cases", year=year, value=float(counts[sex]),
                    unit="count", population_group=POP_ALL, sex=sex, age_group=AGE_ALL,
                    source_url=_GOAL_PAGE,
                    source_indicator_code=f"sdg_bd:3.3.1:nasp:{year}:{sex}",
                    extra=extra,
                )
        log.info("bd_sdg: NASP series of indicator 3.3.1, emitted %d rows", emitted)
