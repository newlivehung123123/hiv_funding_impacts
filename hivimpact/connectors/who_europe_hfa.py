"""
WHO Europe Health for All connector, connector 34, national counts of new HIV diagnoses and of
new AIDS cases for the 53 countries of the WHO European Region reporting to the joint
European surveillance.

Source. The WHO/Europe Data Warehouse (dw.euro.who.int, the data store behind the European
Health Information Gateway of the WHO Regional Office for Europe) answers a documented public
JSON API, version 5, with no key and no sign-in. Measure HFA_350, "Number of new HIV
diagnoses", and measure HFA_348, "Number of new AIDS cases", in the European Health for All
database (HFA-DB) hold a count per country and calendar year for women and men together. A
request to /api/v5/measures/{measure} with output=data,attributes,notes returns every value of
the measure with the measure note and the country notes. HFA_350 was first read on 15 October
2026, and HFA_350 and HFA_348 were read again on the same day, when the values carried a data
update stamp of 15 September 2025. HFA_350 runs from 1979 to 2019 and HFA_348 from 1978 to 2019.

What the counts are. The measure note defines HFA_350 as the number of people newly diagnosed
with HIV during the calendar year and HFA_348 as the number of people newly diagnosed with AIDS
during the calendar year, with the counts taken from the annual HIV/AIDS surveillance in Europe reports of
the European Centre for Disease Prevention and Control (ECDC) and the WHO Regional Office for
Europe, with no adjustment for reporting delay. A count of people a national surveillance
system registers as newly diagnosed with HIV is the panel's notified_hiv_cases, never
new_diagnoses, which counts positive tests at donor-supported sites (Jason's ruling of 8
October 2026). HFA_348 enters aids_cases_reported (research/rulings_2026-10-15.md, ruling R7),
never the modelled aids_deaths or new_infections. The HFA_348 measure note names no AIDS case
definition. extra.case_definition records the missing name, together with the WHO and EU
case definitions named in Annex 1 of the joint ECDC and WHO report HIV/AIDS surveillance in
Europe 2020 (2019 data), read on 16 October 2026.

Why the panel needs the connector. On 15 October 2026 the panel held notified_hiv_cases only
from the Latin American and Caribbean connectors and no row for any of the 53 European
countries, and held no reported AIDS count at all.

Country-years not emitted. A count covering part of a country, or counting a narrower group of
people than the measure note names, is not the panel measure, and the connector refuses the
years the WHO country notes describe as departing from the measure note, and the years the
joint ECDC and WHO report HIV/AIDS surveillance in Europe 2020 (2019 data) describes as not
comparable with later years. _REFUSED lists every refusal.
  New HIV diagnoses (HFA_350).
    Spain (ESP) before 2013, and in 2018 and 2019. The Spanish note says HIV reporting covered
    nine of the 19 autonomous regions from 2003 and reached all 19 regions only in 2013. Annex 5
    of the joint report, page 121, says the 2018 data for Catalonia are not available because of
    extraction issues, and says Asturias, Aragón, Cantabria and Melilla reported no data for
    2019 while some other regions reported provisional data for 2019 (ruling R35).
    Italy (ITA) before 2012. The Italian note says 10 of the 21 regions reported from 2004 and
    all 21 regions only from 2012.
    The Netherlands (NLD) before 2002. The Dutch note says the counts before 2002 come from a
    national cohort of adults on antiretroviral therapy and the case reporting system started
    in 2002.
    Turkey (TUR), every year. The Turkish note says the reported HIV cases exclude persons
    diagnosed with AIDS at the time of HIV diagnosis, so the Turkish count misses the people
    diagnosed late.
    North Macedonia (MKD) before 2017. The North Macedonian AIDS note says the AIDS cases only
    include people diagnosed with AIDS at the time of HIV diagnosis, and in 10 years from 2000
    to 2011 the AIDS count exceeds the HIV count (five AIDS cases against no HIV diagnosis in
    2000, 10 AIDS cases against a single HIV diagnosis in 2005), so the North Macedonian HIV
    count for the 10 years misses the people diagnosed with AIDS at HIV diagnosis. Annex 4a of
    the 2025 edition of the joint report says North Macedonia reported the separate HIV record
    type for 1993 to 2016 and the joined HIV and AIDS record from 2017, which holds the AIDS
    diagnosis inside the HIV case, so 2017 and 2018 are kept (ruling R35).
    The Russian Federation (RUS) before 2016. Annex 1 of the joint report, page 113, says the
    Russian case definitions changed in 2016, says the updated federal statistical Form N61
    from medical facilities counts the individuals newly diagnosed with HIV, and says the
    Russian data for 2009 to 2015 cannot directly be compared with 2016 to 2019. The Russian
    counts from 2016 match the panel measure, a person newly registered as diagnosed, and the
    seven Russian years from 2009 to 2015 are refused. The Russian count falls from 100,220 in
    2015 to 86,855 in 2016.
    Luxembourg (LUX), every year. Footnote c of Table 1 of the joint report (page 68) gives 96
    new HIV diagnoses for 2019 in the Luxembourg national statistics, which count by date of
    notification, against the 48 of HFA_350 and of Table 1, which count by date of diagnosis.
    Table 1 of the 2025 edition prints 111 for 2019 and between 2.1 and 2.3 times the HFA_350
    count in every year from 2015 to 2019, and raises the cumulative Luxembourg count from 1,830
    to 3,777, so the 2025 edition revised every earlier Luxembourg year. Late case reports raise
    the latest years of an edition most, as in the Dutch ratio of the 2025 count to the HFA_350
    count (1.06 for 2015, 1.73 for 2019) and the Portuguese ratio (1.19 for 2015, 1.94 for 2019),
    while the Luxembourg ratio stays between 2.1 and 2.3 from 2015, four years before the latest
    year of the 2020 edition, so a late report does not explain the Luxembourg difference.
    HFA_350 therefore holds the Luxembourg series on an earlier basis which counts about half of
    the people the national register counts, and the 20 Luxembourg years are refused (ruling
    R35).
    Ukraine (UKR) in 2015. HFA_350 gives 13,000 for 2015, a round thousand where every other
    Ukrainian year from 2000 to 2019 is an exact count, and Table 1 of the 2025 edition of the
    joint report prints the same 13,000 (ruling R35).
    Austria (AUT), every year. Footnote c of Table 1 of the 2025 edition of the joint report
    says Austria uses study cohort data, and Annex 5 of the 2025 edition says Austrian HIV
    surveillance rests on the Austrian HIV cohort study (AHIVCOS), which in 2022 held 64 per
    cent of the people who had ever received antiretroviral therapy in Austria. Annex 4a of the
    2020 and 2025 editions names a single Austrian HIV data source (AT-HIV) from 1980, and the
    Austrian counts of the 2025 edition for 2015 to 2019 (346, 321, 337, 236 and 268) exceed the
    HFA_350 counts (324, 291, 302, 199 and 225), so the HFA_350 counts rest on the cohort as
    well and are refused, the rule ecdc_hiv_report applies to the Austrian rows of Table 1
    (ruling R35).
    Serbia (SRB), every year. The Serbian HFA_350 counts for 2010 to 2019 equal the row for
    Serbia as a whole in Table 1 of the 2020 edition of the joint report (152, 134, 137, 156,
    137, 183, 179, 186, 188 and 215), and Table 1 prints Serbia excluding Kosovo and Kosovo in
    separate rows beneath the row for Serbia as a whole, so the Serbian HFA_350 counts include
    the Kosovar cases. The panel holds Kosovo under the code XKX, and the World Bank population
    under the code SRB (6,586,476 for 2024) excludes Kosovo, so a Serbian count including
    Kosovo would put two territories under the code SRB, and the 20 Serbian years are refused.
    ecdc_hiv_report carries the row for Serbia excluding Kosovo under SRB and the Kosovar row
    under XKX (ruling R35).
    Armenia (ARM), every year. The Armenian HFA_350 counts for 2000 to 2019 lie within nine cases
    of the counts of citizens of Armenia in Figure 2 of the HIV situation analysis 2025 of the
    National Centre for Infectious Diseases of Armenia, equal in six years, and run 16 to 39
    cases below citizens plus foreign citizens for 2015 to 2019. A citizens-only count under
    notified_hiv_cases would repeat the definition ruling R37 refuses for Azerbaijan, and
    am_ncid carries citizens plus foreign citizens for 2015 to 2025 (ruling R45).
  New AIDS cases (HFA_348).
    Turkey (TUR), North Macedonia (MKD), every year, and Ireland (IRL) from 2012. The notes say
    AIDS cases are counted only where AIDS is diagnosed at the time of HIV diagnosis, a
    narrower count than the people newly diagnosed with AIDS.
    Spain (ESP) from 2014. Annex 5 of the joint report, page 121, says the AIDS reports of
    several Spanish regions could not be included for 2014 to 2019 (ruling R35).
    The United Kingdom (GBR) from 2011. The British note says the United Kingdom has moved
    toward surveillance of AIDS within three months of HIV diagnosis and the figures for 2015
    and 2016 are likely to be lower than earlier figures. The note names no year for the move.
    The British count falls from 665 in 2010 to 419 in 2011, by 37%, the largest fall in a
    single year from 2000 to 2019, so 2011 is taken as the first year under the narrower
    surveillance.
    Sweden (SWE) from 2000. The Swedish note says AIDS reporting has not been mandatory since
    2000 and the national AIDS surveillance system was discontinued from 2008 to 2016.
    Denmark (DNK) in 2004. HFA_348 gives a single Danish AIDS case for 2004, beside 40 for 2003
    and 44 for 2005, while the Danish HIV count for 2004 (306) lies within the range of the
    neighbouring years, so the Danish AIDS value for 2004 reads as a partial report and is
    refused.
    Belgium (BEL) in 2016. The Belgian note says the information on AIDS diagnoses for 2016 was
    not available because of a data merger issue, and the value for 2016 carries no note saying
    when the value arrived.
    The Russian Federation (RUS), every year. The Russian note says the Russian Federation
    reports no HIV/AIDS surveillance data to WHO, and the only Russian AIDS value from 2000 to
    2019 is a zero for 2010, a year with 62,581 new HIV diagnoses in HFA_350.
    Austria (AUT), every year. Footnote c of Table 13 of the 2025 edition of the joint report
    says Austria uses study cohort data, and Annex 4b of the 2025 edition gives the Austrian
    AIDS data source (AT-AIDS, from 1982) the note on the Austrian HIV cohort study, so the
    Austrian AIDS counts are refused with the Austrian HIV counts (ruling R35).
    Serbia (SRB), every year. The Serbian HFA_348 counts for 2010 to 2019 equal the row for
    Serbia as a whole in Table 14 of the 2020 edition of the joint report (52, 60, 57, 49, 49,
    50, 61, 64, 70 and 73), which includes the Kosovar AIDS cases, so the Serbian AIDS counts
    are refused with the Serbian HIV counts (ruling R35).
    Luxembourg (LUX), every year. The Luxembourg AIDS counts for 2015 to 2019 (10, 12, 6, 4
    and 3) run at 0.56 to 0.67 times the counts of Table 13 of the 2025 edition of the joint
    report (18, 19, 9, 7 and 5), and the 2025 edition raised the cumulative Luxembourg AIDS
    count from 334 to 599, the same revision ruling R35 found in the Luxembourg HIV counts
    (ruling R36).
    Germany (DEU) in 2019. The German AIDS count for 2019 (74) is a first report. The German
    rows of Table 13 are identical in the 2020 and 2025 editions, because Germany stopped
    reporting AIDS cases to TESSy (The European Surveillance System of ECDC) after the 2020
    reporting round, so the first report was never updated for late reports. The German count
    for 2019 is 0.31 times the count for 2018 (242), the lowest ratio of the latest year to the
    year before among the 32 country rows of the AIDS table of the 2020 edition, while German
    HIV diagnoses rose in 2019. The Danish value for 2004 sets the precedent (ruling R36).
    Armenia (ARM), every year. Figure 3 of the HIV situation analysis 2025 of the National
    Centre for Infectious Diseases of Armenia starts in 2005. The Armenian HFA_348 counts for
    2005 to 2019 equal the AIDS counts among citizens of Armenia in Figure 3 in six years from
    2006 to 2011 and lie within eight cases in every year, so the Armenian AIDS counts for 2000
    to 2019 are refused with the Armenian HIV counts (ruling R45).
Rows for country groups (COUNTRY_GRP filled, COUNTRY empty) are sums over WHO groupings and
are skipped.

Notes carried in extra. Every row of a country with a WHO country note carries the note of the
measure in extra.who_country_note, so the reader sees the caveat beside the count. Among other
caveats the notes record Russian HIV counts taken from the published data of the Russian
Federal Scientific and Methodological Centre for Prevention and Control of AIDS, Ukrainian
counts for 2014 to 2016 without Crimea, Sevastopol City and parts of the territories outside
government control, no report from Uzbekistan to WHO since 2010, an estimated 30% of French HIV
diagnoses missing in 2015 and 41% of French AIDS diagnoses missing in 2007 to 2009, and two HIV
cases officially reported by Turkmenistan since reporting began. Turkmenistan's zero counts
are the official reports and enter the panel with the Turkmen note, the same rule paho_core
applies to a reported zero. A zero notified count is
a measurement, unlike the zero placeholders of the Global AIDS Monitoring expenditure
workbooks.

Series read and not carried.
  EPW_11, estimated antiretroviral therapy coverage for 40 countries, 2000 to 2022, from the
  European Programme of Work indicators, is an older round of the UNAIDS modelled estimates.
  Only 38 of the 351 country-years EPW_11 shares with unaids_aidsinfo agree within half a
  percentage point, so the series would bring a superseded round into the panel.
  HFA_347 and HFA_349 are rates per 100,000 derived from HFA_348 and HFA_350. CAH_46 holds a
  single year (2013) with no values, and CAH_47, adolescent HIV rates for ages 15 to 24 by sex,
  ends in 2014.
  The European mortality database (MDB) and the HFAMDB measures were not read.

Rows from the saved answers of 20 October 2026 (data update stamp of 15 September 2025, the
stamp of the answers of 15 October 2026), in an offline test with the network blocked, for 2000
to 2019.
  notified_hiv_cases. 872 rows over 48 countries, after 147 country-years were refused (12 for
  Spain, eight for Italy, two for the Netherlands, 20 for Turkey, 17 for North Macedonia, seven
  for the Russian Federation, 20 for Luxembourg, a single year for Ukraine, 20 for Austria, 20
  for Serbia and 20 for Armenia).
  26 rows carry a reported zero, 13 for Turkmenistan, nine for Monaco, two for Malta and two
  for San Marino. 233 rows carry a WHO country note. The 2019 count for the Russian Federation is
  80,124 and the 2019 count for Ukraine is 16,357.
  aids_cases_reported. 847 rows over 45 countries, after 154 country-years were refused (20 for
  Turkey, 19 for North Macedonia, nine for the United Kingdom, eight for Ireland, eight for
  Sweden, six for Spain, a single year for Denmark, a single year for Belgium, a single year
  for the Russian Federation, 20 for Austria, 20 for Serbia, 20 for Luxembourg, a single year
  for Germany and 20 for Armenia). 57 rows carry a reported
  zero, 15 for Monaco, 13 for San Marino, 12 for Andorra, six for Iceland, four for Malta,
  four for Turkmenistan, and a single zero for Belarus (2000), for Kyrgyzstan (2000) and for
  Tajikistan (2002). 370 rows carry a WHO country note. The 2019 count for
  Ukraine is 7,511.

Certificate check. dw.euro.who.int sends the server certificate without the Sectigo
intermediate certificate (Sectigo Public Server Authentication CA DV R36), so Python's own
certificate store cannot complete the chain and the run of 15 October 2026 failed with
CERTIFICATE_VERIFY_FAILED. Requests to the host now go through the truststore package, which
asks the operating system to verify the certificate. macOS fetches the missing intermediate
certificate from the address the server certificate names, as curl does. Verification stays
on throughout, and a host with a wrong certificate is still refused.
"""
from __future__ import annotations

import html
import logging
import re
import ssl
from collections import Counter
from datetime import date
from typing import Dict, Iterable, Iterator, Optional

from requests.adapters import HTTPAdapter

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..normalize import code_to_iso3, name_for
from ..schema import PanelRow, SourceType, POP_ALL

log = logging.getLogger("hivimpact")

_BASE = "https://dw.euro.who.int/api/v5/measures/"
_MEASURES = {
    "HFA_350": "notified_hiv_cases",    # new HIV diagnoses
    "HFA_348": "aids_cases_reported",   # new AIDS cases
}
_CASE_DEFINITION = ("not named in the WHO/Europe measure note, which counts the people newly "
                    "diagnosed with AIDS during the calendar year in the joint ECDC and WHO "
                    "Regional Office for Europe surveillance. Annex 1 of the joint report "
                    "HIV/AIDS surveillance in Europe 2020 (2019 data) says only confirmed HIV "
                    "and AIDS cases are reported at European level, under the WHO case "
                    "definitions of 2007 and the EU case definitions of Commission Decision "
                    "2002/253/EC, and says national case definitions may differ across the "
                    "WHO European Region")

# Country-years refused, from the WHO country notes and values read on 15 October 2026 and the
# joint report read on 16 October 2026, as
# (measure, ISO3, first year, last year, reason). None as the last year means every later year.
_REFUSED = [
    ("HFA_350", "ESP", 0, 2012, "HIV reporting in part of the country (all 19 autonomous "
                                "regions report from 2013)"),
    ("HFA_350", "ESP", 2018, 2019, "HIV reporting in part of the country (the joint report for "
                                   "2019 data says the Catalan data for 2018 are not available, "
                                   "and Asturias, Aragón, Cantabria and Melilla reported no data "
                                   "for 2019)"),
    ("HFA_350", "ITA", 0, 2011, "HIV reporting in part of the country (all 21 regions report "
                                "from 2012)"),
    ("HFA_350", "NLD", 0, 2001, "a cohort on antiretroviral therapy before case reporting "
                                "began in 2002"),
    ("HFA_350", "TUR", 0, None, "the Turkish HIV counts exclude people diagnosed with AIDS at "
                                "the time of HIV diagnosis"),
    ("HFA_350", "MKD", 0, 2016, "the North Macedonian HIV counts are below the counts of AIDS "
                                "at HIV diagnosis in 10 years from 2000 to 2011, under the "
                                "separate HIV record type North Macedonia reported to 2016 "
                                "(ruling R35)"),
    ("HFA_350", "RUS", 0, 2015, "the joint ECDC and WHO report for 2019 data says the Russian "
                                "case definitions changed in 2016, and the Russian data for "
                                "2009 to 2015 cannot directly be compared with 2016 to 2019"),
    ("HFA_350", "LUX", 0, None, "the Luxembourg count for 2019 (48) is half the national "
                                "statistics (96) the joint report for 2019 data prints, and the "
                                "2025 edition raised the cumulative Luxembourg count from 1,830 "
                                "to 3,777 (ruling R35)"),
    ("HFA_350", "UKR", 2015, 2015, "13,000, a round thousand beside exact counts in every other "
                                   "Ukrainian year (ruling R35)"),
    ("HFA_350", "AUT", 0, None, "Austrian HIV surveillance rests on the Austrian HIV cohort "
                                "study (AHIVCOS), 64 per cent of the people ever on "
                                "antiretroviral therapy in Austria in 2022, says the joint "
                                "report for 2024 data (Annex 5, ruling R35)"),
    ("HFA_350", "SRB", 0, None, "the Serbian counts equal the row for Serbia as a whole, Kosovo "
                                "included, in Table 1 of the joint report for 2019 data, and "
                                "the panel holds Kosovo under XKX (ruling R35)"),
    ("HFA_350", "ARM", 0, None, "the Armenian counts lie within nine cases of the counts of "
                                "citizens of Armenia in Figure 2 of the HIV situation analysis "
                                "2025 of the National Centre for Infectious Diseases of Armenia, "
                                "a citizens-only count, and am_ncid carries citizens plus foreign "
                                "citizens (ruling R45)"),
    ("HFA_348", "TUR", 0, None, "AIDS counted only at the time of HIV diagnosis"),
    ("HFA_348", "MKD", 0, None, "AIDS counted only at the time of HIV diagnosis"),
    ("HFA_348", "ESP", 2014, None, "AIDS reporting in part of the country (the joint report for "
                                   "2019 data says the AIDS reports of several regions could not "
                                   "be included for 2014 to 2019)"),
    ("HFA_348", "IRL", 2012, None, "AIDS counted only at the time of HIV diagnosis from 2012"),
    ("HFA_348", "GBR", 2011, None, "AIDS surveillance moved toward AIDS within three months of "
                                   "HIV diagnosis"),
    ("HFA_348", "SWE", 2000, None, "AIDS reporting not mandatory from 2000 and discontinued "
                                   "from 2008 to 2016"),
    ("HFA_348", "DNK", 2004, 2004, "a single Danish AIDS case for 2004, beside 40 for 2003 and "
                                   "44 for 2005, read as a partial report"),
    ("HFA_348", "BEL", 2016, 2016, "the WHO note says the 2016 AIDS diagnoses were not "
                                   "available"),
    ("HFA_348", "RUS", 0, None, "no Russian report to WHO, and the single Russian AIDS value "
                                "is a zero for 2010"),
    ("HFA_348", "AUT", 0, None, "the joint report for 2024 data says the Austrian AIDS counts "
                                "are study cohort data (Table 13 and Annex 4b, ruling R35)"),
    ("HFA_348", "SRB", 0, None, "the Serbian AIDS counts equal the row for Serbia as a whole, "
                                "Kosovo included, in Table 14 of the joint report for 2019 "
                                "data, and the panel holds Kosovo under XKX (ruling R35)"),
    ("HFA_348", "LUX", 0, None, "the Luxembourg AIDS counts for 2015 to 2019 (10, 12, 6, 4 and "
                                "3) run at 0.56 to 0.67 times Table 13 of the joint report for "
                                "2024 data (18, 19, 9, 7 and 5), and the 2025 edition raised the "
                                "cumulative Luxembourg AIDS count from 334 to 599 (ruling R36)"),
    ("HFA_348", "DEU", 2019, 2019, "the German AIDS count for 2019 (74) is a first report, "
                                   "frozen after Germany stopped reporting AIDS to TESSy, and "
                                   "falls to 0.31 times the 2018 count while German HIV "
                                   "diagnoses rose in 2019 (ruling R36)"),
    ("HFA_348", "ARM", 0, None, "the Armenian AIDS counts lie within eight cases of the AIDS "
                                "counts among citizens of Armenia in Figure 3 of the HIV "
                                "situation analysis 2025 of the National Centre for Infectious "
                                "Diseases of Armenia, a citizens-only count (ruling R45)"),
]


def _refusal(measure: str, iso3: str, year: int) -> Optional[str]:
    for m, c, first, last, reason in _REFUSED:
        if m == measure and c == iso3 and year >= first and (last is None or year <= last):
            return reason
    return None


class _OSTrustAdapter(HTTPAdapter):
    """Transport adapter verifying certificates through the operating system trust store."""

    def __init__(self, ctx: ssl.SSLContext, **kw):
        self._ctx = ctx
        super().__init__(**kw)

    def init_poolmanager(self, *args, **kw):
        kw["ssl_context"] = self._ctx
        return super().init_poolmanager(*args, **kw)


def _note_text(raw: str) -> str:
    """The note with HTML tags removed and runs of white space joined."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw or ""))
    return re.sub(r"\s+", " ", text).strip()


class WHOEuropeHFAConnector(BaseConnector):
    source_id = "who_europe_hfa"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("WHO/Europe Data Warehouse API, European Health for All measures HFA_350 "
                   "(new HIV diagnoses) and HFA_348 (new AIDS cases) from the joint ECDC and "
                   "WHO Europe surveillance.")
    request_pause = 1.0
    timeout = 90

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        try:
            import truststore
        except ImportError:
            log.warning("who_europe_hfa: the truststore package is missing, and dw.euro.who.int "
                        "sends an incomplete certificate chain, so the request may fail the "
                        "certificate check")
        else:
            self.session.mount("https://dw.euro.who.int/",
                               _OSTrustAdapter(truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)))

    def _measure(self, measure: str) -> dict:
        """A single request for the values, the measure note and the country notes of a measure."""
        return self._request("GET", _BASE + measure,
                             params={"output": "data,attributes,notes"}).json()

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        end_year = min(end_year or date.today().year, date.today().year)
        start_year = max(start_year, 2000)
        for measure, indicator in _MEASURES.items():
            yield from self._fetch_measure(measure, indicator, wanted, start_year, end_year)

    def _fetch_measure(self, measure, indicator, wanted, start_year, end_year) -> Iterator[PanelRow]:
        d = self._measure(measure)
        notes: Dict[str, str] = {}
        for block in d.get("notes") or []:
            if block.get("note_type") == "COUNTRY":
                for v in block.get("values") or []:
                    if v.get("code"):
                        notes[str(v["code"]).upper()] = _note_text(v.get("value"))
        data_updated = d.get("data_updated_on")
        spec = CANONICAL_INDICATORS[indicator]
        url = _BASE + measure

        seen: Dict[tuple, float] = {}
        groups = 0
        missing = 0
        conflicts = 0
        refused = Counter()
        skipped_codes = set()
        rows = []
        for r in d.get("data") or []:
            dims = r.get("dimensions") or {}
            if dims.get("COUNTRY_GRP") or not dims.get("COUNTRY"):
                groups += 1
                continue
            if (dims.get("SEX") or "ALL") != "ALL":
                continue
            iso3 = code_to_iso3(dims.get("COUNTRY"))
            if iso3 is None:
                skipped_codes.add(dims.get("COUNTRY"))
                continue
            if wanted and iso3 not in wanted:
                continue
            try:
                year = int(str(dims.get("YEAR"))[:4])
            except ValueError:
                continue
            if not start_year <= year <= end_year:
                continue
            value = (r.get("value") or {}).get("numeric")
            if value is None:
                missing += 1
                continue
            reason = _refusal(measure, iso3, year)
            if reason:
                refused[f"{iso3}, {reason}"] += 1
                continue
            key = (iso3, year)
            if key in seen:
                if seen[key] != value:
                    conflicts += 1
                    log.warning("who_europe_hfa: %s %s %d has two values (%s and %s), no value "
                                "emitted", measure, iso3, year, seen[key], value)
                    seen[key] = None
                continue
            seen[key] = value
            rows.append((iso3, year, r))

        emitted = 0
        countries_out = set()
        for iso3, year, r in rows:
            value = seen[(iso3, year)]
            if value is None:
                continue
            extra = {
                "who_measure": measure,
                "measure_type": (r.get("attributes") or {}).get("MEASURE_TYPE"),
                "reporting_delay_adjusted": False,
                "data_updated_on": data_updated,
                "source_report": "ECDC and WHO Regional Office for Europe, HIV/AIDS surveillance "
                                 "in Europe annual reports",
            }
            if indicator == "aids_cases_reported":
                extra["case_definition"] = _CASE_DEFINITION
            if iso3 in notes:
                extra["who_country_note"] = notes[iso3]
            yield self.make_row(
                country_iso3=iso3, country_name=name_for(iso3),   # the API returns ISO3 codes only
                indicator_id=indicator, year=year, value=float(value),
                population_group=POP_ALL, unit=spec.unit,
                source_type=spec.default_source_type.value,
                source_url=url, source_indicator_code=measure,
                extra=extra,
            )
            emitted += 1
            countries_out.add(iso3)

        log.info("who_europe_hfa: %s %-22s -> %d country-years over %d countries",
                 measure, indicator, emitted, len(countries_out))
        for reason, n in sorted(refused.items()):
            log.info("who_europe_hfa: %s, %d country-years refused, %s", measure, n, reason)
        log.info("who_europe_hfa: %s, %d empty values, %d conflicting duplicates, %d country-group "
                 "rows skipped, codes not mapped (%s)", measure, missing, conflicts, groups,
                 ", ".join(sorted(str(c) for c in skipped_codes)) or "no code")
