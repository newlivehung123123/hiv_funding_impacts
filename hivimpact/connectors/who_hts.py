"""
WHO HIV testing services connector, connector 27, national test volume, test positivity,
testing by setting and HIV self-tests distributed, as countries report the counts to Global
AIDS Monitoring.

Source. The WHO HTS Dashboard (whohts.web.app, the World Health Organization page on HIV
testing services) is a public React page that reads an open JSON query service at
eic-database-290813.ew.r.appspot.com/query, with no key and no sign-in. The service answers
one indicator name and one source database per call, and returns every country's rows for the
single data year the database edition covers. The service address, the indicator names and
the validation filter below were read on 14 October 2026 from the dashboard script bundle
main.b557ae72.js.

Editions read, with the data year the edition holds.
  Global AIDS Monitoring 2019 holds 2018, Global AIDS Monitoring 2020 holds 2019,
  Global AIDS Monitoring 2021 holds 2020, Global AIDS Monitoring 2023 holds 2022,
  Global AIDS Monitoring 2024 holds 2023 and Global AIDS Monitoring 2025 holds 2024.
  The service answers "indicator not found" for a Global AIDS Monitoring 2022 edition, so the
  data year 2021 is missing from the source and not from the connector.
  National Programme Data 2019 holds three countries for 2018 (Angola, Chad and Mexico), and
  a National Programme Data 2019 row enters only where the Global AIDS Monitoring 2019 edition
  has no value for the same country, indicator, sex and age.

Why the panel needs the connector. On 14 October 2026 the panel held national test totals from
who_gho for 2022 to 2024 and from unaids_aidsinfo for 2019 and 2022 to 2024, and no national
total for 2018 or 2020. After the validation filter the service carries a national total for
101 countries in 2018 (98 from Global AIDS Monitoring 2019 and three from National Programme
Data 2019) and for 67 countries in 2020. The 2018 and 2020 rows already in the panel
come from pepfar_snu, pepfar_modality and global_fund, and a programme count covers the tests a
programme paid for, a share of the national total and never a rival estimate of the national
total. For 2022 to 2024 the service and who_gho agree exactly on the national total in all 325
country-years compared (93, 103 and 129), and on the female 15+ split in all 81 country-years
compared for 2024, so the 2022 to 2024 rows duplicate who_gho and reconcile keeps one copy.
For 2019 the service agrees with unaids_aidsinfo in all 92 country-years compared and adds 10
countries.

Testing by setting. hiv_tests_performed_community and hiv_tests_performed_facility already
carry the PEPFAR MER modality split from pepfar_modality, which counts PEPFAR-supported sites
only. The service carries the Global AIDS Monitoring split, which counts every test in the
country whoever paid. Community testing covers mobile testing, community voluntary counselling
and testing and other community testing. Facility testing covers provider-initiated testing,
antenatal clinics, facility voluntary counselling and testing, family planning clinics and
other facility testing. For 2024, community plus facility came within one per cent of the
national total in 40 of the 42 countries reporting all three counts, and Singapore reported
settings covering 19 per cent of the national total. The source_id separates the two
definitions, and no figure from pepfar_modality is ever compared with a figure from who_hts as
the same count.

HIV self-tests distributed. A new indicator, hiv_self_tests_distributed, registered on
14 October 2026. The service carries 12 countries for 2018 and 50 for 2024.

What the connector refuses, and why.
  - Editions from Global AIDS Monitoring 2020 onward keep only rows whose value_comment reads
    "validated", the same filter the dashboard applies. Rows marked "not published", "not
    validated", "No, active query", "no data reported", "not valid" or "partial valid" are
    counted in the log and never emitted. In the 2021 edition the filter drops 33 of the 100
    valued national totals.
  - The 2019 editions carry no validation field. A row marked "suppressed" is dropped and every
    unmarked row is kept.
  - Positivity in the 2022 to 2024 editions is rounded to one decimal place, while who_gho
    carries two decimal places for the same country-years, so reconcile prefers who_gho for
    positivity in those years.
  - Two rows for one country, indicator, sex, age and year inside one edition are summed by
    nobody. Equal values give one row. Different values give no row, and the log names the
    country-year.
  - PEPFAR COP and ROP editions duplicate the PEPFAR connectors, Shiny90 and Spectrum rows are
    modelled estimates already carried from UNAIDS, The Global Fund rows duplicate global_fund,
    and the HIV RDT demand forecast is a forecast, so none of the five enter the panel.

Fragile by construction. The service address belongs to the dashboard's App Engine project.
If WHO moves the dashboard to a new project, every call fails, and the connector raises so
run_all marks the source FAILED instead of writing an empty source.
"""
from __future__ import annotations

import logging
from collections import Counter
from datetime import date
from typing import Dict, Iterable, Iterator, List, Optional, Tuple
from urllib.parse import urlencode

import requests

from ..connector_base import BaseConnector
from ..schema import PanelRow, SourceType, POP_ALL

log = logging.getLogger("hivimpact")

_API = "https://eic-database-290813.ew.r.appspot.com/query"
_DASHBOARD = "https://whohts.web.app/"

# (source indicator name, canonical id, sex, age group, unit). Global AIDS Monitoring 2020 to
# 2025 name the indicators after the reporting form's denominator and percentage fields.
_MAP_GAM = [
    ("Den Age-All", "hiv_tests_performed", "all", "all", "count"),
    ("Den Age-Male Gte 15", "hiv_tests_performed", "male", "15+", "count"),
    ("Den Age-Female Gte 15", "hiv_tests_performed", "female", "15+", "count"),
    ("Per Age-All", "hiv_test_positivity_pct", "all", "all", "percent"),
    ("Per Age-Male Gte 15", "hiv_test_positivity_pct", "male", "15+", "percent"),
    ("Per Age-Female Gte 15", "hiv_test_positivity_pct", "female", "15+", "percent"),
    ("Den Community-Community All", "hiv_tests_performed_community", "all", "all", "count"),
    ("Den Facility-Facility All", "hiv_tests_performed_facility", "all", "all", "count"),
    ("Self Test Distributed-Data Value", "hiv_self_tests_distributed", "all", "all", "count"),
]
# The 2019 editions name the same counts in words. The double space before "Positivity" is in
# the source names and the service matches the names exactly.
_MAP_2019 = [
    ("Total volume of tests conducted in past year", "hiv_tests_performed", "all", "all", "count"),
    ("Men (15+) - Number of tests", "hiv_tests_performed", "male", "15+", "count"),
    ("Women (15+) - Number of tests", "hiv_tests_performed", "female", "15+", "count"),
    ("Total aggregate positivity", "hiv_test_positivity_pct", "all", "all", "percent"),
    ("Men (15+) -  Positivity", "hiv_test_positivity_pct", "male", "15+", "percent"),
    ("Women (15+) -  Positivity", "hiv_test_positivity_pct", "female", "15+", "percent"),
    ("Total Volume - Tests conducted and positivity at community level",
     "hiv_tests_performed_community", "all", "all", "count"),
    ("Total Volume - Tests conducted and positivity at facility level",
     "hiv_tests_performed_facility", "all", "all", "count"),
    ("HIVSTs distributed", "hiv_self_tests_distributed", "all", "all", "count"),
]

# (source database, data year the edition holds, indicator map, validated rows only). The
# order matters, because the first edition to fill a country, indicator, sex, age and year
# keeps the row, which is how National Programme Data 2019 enters only as a fallback.
_EDITIONS = [
    ("Global AIDS Monitoring 2019", 2018, _MAP_2019, False),
    ("National Programme Data 2019", 2018, _MAP_2019, False),
    ("Global AIDS Monitoring 2020", 2019, _MAP_GAM, True),
    ("Global AIDS Monitoring 2021", 2020, _MAP_GAM, True),
    ("Global AIDS Monitoring 2023", 2022, _MAP_GAM, True),
    ("Global AIDS Monitoring 2024", 2023, _MAP_GAM, True),
    ("Global AIDS Monitoring 2025", 2024, _MAP_GAM, True),
]

_SETTING_NOTE = {
    "hiv_tests_performed_community": (
        "Global AIDS Monitoring testing in community settings, national and whoever paid, "
        "covering mobile testing, community voluntary counselling and testing and other "
        "community testing. Not the PEPFAR MER modality split of pepfar_modality."),
    "hiv_tests_performed_facility": (
        "Global AIDS Monitoring testing in health facilities, national and whoever paid, "
        "covering provider-initiated testing, antenatal clinics, facility voluntary counselling "
        "and testing, family planning clinics and other facility testing. Not the PEPFAR MER "
        "modality split of pepfar_modality."),
}


class WHOHTSConnector(BaseConnector):
    source_id = "who_hts"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("WHO HTS Dashboard (whohts.web.app), national HIV tests, positivity, testing "
                   "by setting and self-tests distributed, Global AIDS Monitoring 2019 to 2025 (API)")
    request_pause = 1.0
    timeout = 60

    def _query(self, indicator: str, database: str) -> Tuple[Optional[List[dict]], str]:
        params = {"indicator": indicator, "source_database": database}
        url = f"{_API}?{urlencode(params)}"
        try:
            data = self._request("GET", _API, params=params).json()
        except requests.HTTPError as exc:
            # The service answers HTTP 401 with {"error": "indicator not found"} for a name the
            # edition does not hold, which is a gap in the source and not a failed call.
            status = exc.response.status_code if exc.response is not None else None
            if status == 401:
                log.warning("who_hts: %s | %s -> not held by the service", database, indicator)
                return [], url
            log.warning("who_hts: %s | %s fetch failed: %s", database, indicator, exc)
            return None, url
        except Exception as exc:  # network error or a non-JSON error page
            log.warning("who_hts: %s | %s fetch failed: %s", database, indicator, exc)
            return None, url
        if isinstance(data, dict):
            log.warning("who_hts: %s | %s -> %s", database, indicator, data.get("error", data))
            return [], url
        return (data if isinstance(data, list) else []), url

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        end_year = end_year or date.today().year

        kept: Dict[tuple, PanelRow] = {}
        calls = failed = 0
        dropped: Counter = Counter()
        for database, data_year, imap, validated_only in _EDITIONS:
            if not (start_year <= data_year <= end_year):
                continue
            for name, canonical, sex, age, unit in imap:
                calls += 1
                rows, url = self._query(name, database)
                if rows is None:
                    failed += 1
                    continue
                # (country, year) -> values seen inside the edition, to catch a double row
                seen: Dict[tuple, set] = {}
                cand: Dict[tuple, dict] = {}
                for r in rows:
                    iso3 = str(r.get("country_iso_code") or "").strip().upper()
                    if len(iso3) != 3 or not iso3.isalpha():
                        continue
                    if r.get("area_name"):  # a sub-national row, never a national total
                        continue
                    if wanted and iso3 not in wanted:
                        continue
                    value = r.get("value")
                    if value is None:
                        continue
                    comment = r.get("value_comment")
                    if validated_only and comment != "validated":
                        dropped[(database, str(comment))] += 1
                        continue
                    if not validated_only and comment is not None:
                        dropped[(database, str(comment))] += 1
                        continue
                    try:
                        year = int(str(r.get("year"))[:4])
                    except ValueError:
                        continue
                    if not (start_year <= year <= end_year):
                        continue
                    seen.setdefault((iso3, year), set()).add(float(value))
                    cand[(iso3, year)] = r
                for (iso3, year), vals in seen.items():
                    if len(vals) > 1:
                        log.warning("who_hts: %s | %s | %s %d holds %d different values, no row",
                                    database, name, iso3, year, len(vals))
                        continue
                    key = (iso3, canonical, sex, age, year)
                    if key in kept:
                        continue
                    r = cand[(iso3, year)]
                    extra = {
                        "source_database": database,
                        "source_organization": r.get("source_organization"),
                        "value_comment": r.get("value_comment"),
                        "import_file": r.get("import_file"),
                        "indicator_description": r.get("indicator_description"),
                        "dashboard": _DASHBOARD,
                    }
                    if canonical in _SETTING_NOTE:
                        extra["definition"] = _SETTING_NOTE[canonical]
                    if year >= 2022 and canonical in ("hiv_tests_performed", "hiv_test_positivity_pct"):
                        extra["reconcile_with"] = ("who_gho, same national figure for 2022 to 2024, "
                                                   "with positivity at one decimal place here and two "
                                                   "in who_gho")
                    if year == 2019 and canonical == "hiv_tests_performed" and sex == "all":
                        extra["reconcile_with"] = "unaids_aidsinfo, same national figure for 2019"
                    kept[key] = self.make_row(
                        country_iso3=iso3, country_name=r.get("country_name") or "",
                        indicator_id=canonical, year=year, value=float(next(iter(vals))),
                        unit=unit, population_group=POP_ALL, sex=sex, age_group=age,
                        source_url=url, source_indicator_code=name, extra=extra,
                    )
        if calls and failed == calls:
            raise RuntimeError("who_hts: every call to the WHO HTS query service failed")
        for (database, comment), n in sorted(dropped.items()):
            log.info("who_hts: %s dropped %d rows marked %r", database, n, comment)
        by_ind = Counter(k[1] for k in kept)
        for canonical, n in sorted(by_ind.items()):
            log.info("who_hts: %-32s -> %d rows", canonical, n)
        log.info("who_hts: emitted %d rows from %d calls (%d failed)", len(kept), calls, failed)
        yield from kept.values()
