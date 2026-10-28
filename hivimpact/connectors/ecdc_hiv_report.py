"""
European Centre for Disease Prevention and Control (ECDC) and WHO Regional Office for Europe, the
joint report HIV/AIDS surveillance in Europe 2025 (2024 data), Table 1, HIV diagnoses by country
and year of diagnosis, and Table 13, AIDS diagnoses by country and year of diagnosis, 2015 to 2024,
for the countries of the WHO European Region.

Every year ECDC and the WHO Regional Office for Europe publish a joint surveillance report from the
case reports every country sends to The European Surveillance System (TESSy). Table 1 of the 2025
report (pages 62 and 63, two identical printed copies) gives the count and the rate per 100,000 of
HIV diagnoses for 2015 to 2024 and the cumulative total since reporting began, for the 30 countries
of the European Union and European Economic Area (EU/EEA) and for 24 other countries of the WHO
European Region, with Serbia split into Serbia excluding Kosovo and Kosovo. The report is
born-digital, so the connector reads the pdfplumber text layer and uses no optical character
recognition, under ruling R25 of research/rulings_2026-10-15.md. The report carries the licence
CC BY-NC-SA 3.0 IGO (page 2). Rulings R35 and R36 of research/rulings_2026-10-15.md record why
the connector reads Table 1 and Table 13 and what the connector refuses.

WHY TABLE 1 OF THE 2025 REPORT
------------------------------
Measure HFA_350 of the WHO Europe Health for All database (who_europe_hfa) reproduces Table 1 of
the 2020 edition of the joint report (ruling R11) and stops at 2019. Countries keep sending late
case reports for earlier years, so every edition revises earlier years upward, and the 2025
edition holds the latest count for 2015 to 2019 and the only count in the panel for 2020 to 2024
for most European countries. A single table from a single edition keeps every year on one vintage
of the count. Measure HFA_348 reproduces the AIDS table of the 2020 edition in the same way, so
Table 13 of the 2025 edition plays the part for AIDS diagnoses which Table 1 plays for HIV
diagnoses (ruling R36).

THE FILE
--------
The connector downloads the report once into `raw_dir`, and every later run reads the cached copy.
A cached copy whose size or sha256 differs from the copy read on 20 October 2026 (20,246,576
bytes) is logged as a WARNING and still parsed, because every gate below runs on the text.

WHAT THE COUNT IS
-----------------
The emitted value is the count of HIV diagnoses a country reported to TESSy for the calendar year of
diagnosis, as Table 1 of the 2025 report prints the count, with no adjustment for reporting delay.
Footnotes 7 and 8 of section 1.1 (page 29) say the reported diagnoses hold the people diagnosed with
HIV for the first time together with the people with a previous positive diagnosis, made abroad or
in another setting of the reporting country before the year of reporting, and some countries report
a previous positive case on entry or return to care. A case diagnosed abroad enters the surveillance
of the reporting country for the first time in the year of report. A case diagnosed in another
setting of the reporting country, or reported on return to care, may also sit in the count of an
earlier year, and Table 1 cannot show how many cases repeat an earlier count. In the EU/EEA 14.7
per cent of the diagnoses of 2024 were previous positive diagnoses (page 29), and extra.definition
names the previous positive cases on every row.
Armenia and Ukraine report by the date of statistics (the date the case enters the national
statistics) in place of the date of diagnosis (Annex 5). The rows carry sex "all". The printed
rate, the area of the region (West, Centre or East) and the EU/EEA membership travel in extra, with
the country comments of Annex 5 which bear on the count. The cumulative totals are refused under
ruling R14. Serbia is emitted from the row for Serbia excluding Kosovo, and Kosovo (XKX) from the
row for Kosovo, so no case is counted under two codes, and the row for Serbia as a whole serves the
gates only. The panel holds Kosovo under XKX, and the World Bank population under SRB excludes
Kosovo. Measure HFA_350 reproduces the row for Serbia as a whole from the 2020 edition, Kosovo
included, so who_europe_hfa refuses the Serbian HFA_350 and HFA_348 counts (ruling R35).

COUNTRY-YEARS NOT EMITTED
-------------------------
A count covering part of a country, or counting a narrower group of people than the people
diagnosed with HIV, is not the panel measure. _REFUSED lists every refusal.
  Austria (AUT), every year. Footnote c of Table 1 says Austria uses study cohort data, and Annex 5
    says Austrian surveillance rests on the Austrian HIV cohort study (AHIVCOS), which in 2022
    held 64 per cent of the people who had ever received antiretroviral therapy in Austria.
    Annex 4a names a single Austrian HIV data source (AT-HIV) from 1980, so who_europe_hfa refuses
    the Austrian HFA_350 and HFA_348 counts for the same reason (ruling R35).
  Türkiye (TUR), every year. Annex 5 says the reported Turkish HIV cases exclude people diagnosed
    with AIDS at the time of HIV diagnosis, the reason who_europe_hfa refuses the Turkish count.
  North Macedonia (MKD), 2015 and 2016. Annex 5 says the North Macedonian AIDS cases include only
    people diagnosed with AIDS at the time of HIV diagnosis, and Annex 4a says North Macedonia
    reported the separate HIV record type for 1993 to 2016 and the joined HIV and AIDS record from
    2017. Under the separate HIV record the North Macedonian AIDS count exceeds the HIV count in 10
    years from 2000 to 2011 (who_europe_hfa), so an HIV count before 2017 can miss people diagnosed
    with AIDS at HIV diagnosis. A joined record holds the AIDS diagnosis inside the HIV case, and
    the AIDS count of Table 13 stays below the HIV count in every year from 2015, so 2017 to 2024
    are kept (ruling R35).
  The Russian Federation (RUS), 2015. Annex 5 says the Russian case definitions changed in 2016 and
    the Russian data for 2009 to 2015 cannot be compared directly with 2016 to 2024.
  Spain (ESP), 2018. Annex 5 says the 2018 data from Catalonia are not available.
  Ukraine (UKR), 2015. Table 1 prints 13 000, a round thousand, where every other Ukrainian year is
    an exact count, and the count for 2015 is not in the Ukrainian national connector.
  Armenia (ARM), every year. The Armenian counts of Table 1 equal the counts of citizens of Armenia
    in Figure 2 of the HIV situation analysis 2025 of the National Centre for Infectious Diseases of
    Armenia in every year from 2015 to 2024 (294, 303, 358, 429, 448, 369, 425, 535, 500 and 544),
    and the situation analysis counts foreign citizens apart (Figure 1). A citizens-only count
    under notified_hiv_cases would repeat the definition ruling R37 refuses for Azerbaijan, and
    am_ncid carries citizens plus foreign citizens for 2015 to 2025 (ruling R45).
A dash in Table 1 (Andorra and Monaco from 2019, Turkmenistan and Uzbekistan in every year) is an
absent value and emits nothing.

TABLE 13, AIDS DIAGNOSES
------------------------
Table 13 of the 2025 report (pages 82 and 83, two identical printed copies) gives the count and the
rate per 100,000 of AIDS diagnoses for 2015 to 2024 and the cumulative total, for the 56 rows of
Table 1, and the connector emits the counts as aids_cases_reported (ruling R36). Annex 1 says only
confirmed cases are reported at European level, under the WHO case definitions and the EU case
definitions of Commission Decision 2002/253/EC, and national definitions may differ, and
extra.case_definition carries the Annex 1 text on every AIDS row. An AIDS count which holds only
AIDS found at the time of HIV diagnosis, an AIDS count covering part of a country, and an AIDS count
which the 2025 edition moved far from the 2020 edition with no reason given are not the panel
measure. _REFUSED_AIDS lists every refusal.
  Austria (AUT), every year. Footnote c of Table 13 says Austria uses study cohort data (ruling
    R35).
  Türkiye (TUR) and North Macedonia (MKD), every year. The Turkish and North Macedonian AIDS counts
    hold only AIDS found at the time of HIV diagnosis.
  Ireland (IRL) and the United Kingdom (GBR), every year. Irish AIDS surveillance counts AIDS only
    at the time of HIV diagnosis from 2012, and British AIDS surveillance moved toward AIDS within
    three months of HIV diagnosis, the reasons who_europe_hfa refuses the Irish HFA_348 counts from
    2012 and the British HFA_348 counts from 2011.
  Spain (ESP), 2015 to 2023. Annex 5 says the AIDS data of two Spanish regions could not be
    included for 2015 to 2022 and of three regions for 2023, and Table 13 prints a dash for 2024,
    so ecdc_hiv_report carries no Spanish AIDS count.
  Cyprus (CYP), every year. The 2025 edition raises the Cypriot AIDS counts for 2015 to 2019 from
    13, 22, 15, 13 and 3 to 70, 75, 67, 73 and 85 with the Cypriot HIV counts unchanged, and Annex 5
    gives no reason.
  Kyrgyzstan (KGZ), every year. The 2025 edition lowers the Kyrgyz AIDS counts for 2015 to 2019
    from 125, 72, 59, 56 and 46 to 35, 33, 46, 47 and 20, and the Kyrgyz cumulative of 884 lies
    below the 999 AIDS deaths the Kyrgyz national HIV centre counts to 1 January 2026.
  Germany (DEU), 2019. The German count for 2019 (74) is a first report, frozen after Germany
    stopped reporting AIDS to TESSy, at 0.31 times the German count for 2018.
  Malta (MLT), 2020 and 2023. Annex 5 says the Maltese AIDS counts for 2020 and 2023 should read 1
    and 2, where Table 13 prints 0.
  Ukraine (UKR), 2020 to 2024. The Ukrainian AIDS definition changed in 2020 to AIDS at HIV
    registration (ruling R34).
  Armenia (ARM), every year. The joined HIV and AIDS record holds the Armenian AIDS diagnosis
    inside an Armenian HIV case, the Armenian HIV cases of Table 1 count citizens of Armenia alone,
    and the Armenian counts of Table 13 lie within 14 cases of the AIDS counts among citizens in
    Figure 3 of the HIV situation analysis 2025 of the National Centre for Infectious Diseases of
    Armenia in every year from 2015 to 2024 (ruling R45).
A dash in Table 13 is an absent value and emits nothing, and the dash printed in place of the
Russian cumulative is read as an absent cumulative. The Table 13 notes for Belgium, France,
Germany, Luxembourg, Liechtenstein, Switzerland, Azerbaijan and Ukraine (_AIDS_NOTES) travel in
extra.country_note. The Armenian notes of _COUNTRY_NOTES and _AIDS_NOTES stay in the code, and no
Armenian row carries the Armenian notes, because ruling R45 refuses every Armenian row.

INTEGRITY GATES
---------------
The gates run on Table 1 and on Table 13 apart (_TABLES).
  * The report prints at least one copy of the table (a page with the caption and table rows, so
    the list of tables on page 8 is passed over), every printed copy reads the same, the year
    line 2015 to 2024 heads the table, and every row holds 10 counts with a rate beside every count
    and a cumulative total, with every count grouped in thousands as printed.
  * The table holds exactly the 56 rows of _ISO3 (_ISO3_T13 for Table 13, whose footnote letters
    differ), 30 under EU/EEA and 26 under non-EU/EEA.
  * For every year, the EU/EEA rows add to the EU/EEA total, the non-EU/EEA rows (Serbia as a
    whole, Kosovo and Serbia excluding Kosovo counted once) add to the non-EU/EEA total, the rows of
    every area add to the area total, the three area totals add to the regional total, the EU/EEA
    and non-EU/EEA totals add to the regional total, and Serbia excluding Kosovo plus Kosovo
    equals Serbia.
  * The cumulative totals of the EU/EEA and non-EU/EEA rows add to the printed cumulative totals,
    with the Russian cumulative of Table 13, printed as a dash, counted as zero.

Any failed gate refuses every row of the table whose gate failed, with a WARNING naming the table
and the reason, and the rows of a table whose gates all passed are still emitted. A regional total
unlike the copy read on 20 October 2026 (_EXPECTED_REGION, _EXPECTED_REGION_T13) is logged as a
WARNING and still emitted, because every gate has passed.

RECONCILIATION
--------------
Measure HFA_350 behind who_europe_hfa holds the same TESSy reports at the vintage of the 2020
edition, so reconcile declares the pair derived (ruling R35), and a difference between
ecdc_hiv_report and who_europe_hfa is a later revision of one count. The Georgian (ge_geostat),
Belarusian (by_belstat) and Ukrainian (ua_npsi) connectors read the national registers behind
the Georgian, Belarusian and Ukrainian reports to TESSy. Never compare with new_diagnoses (Jason's ruling of 8 October 2026).
Measure HFA_348 behind who_europe_hfa holds the AIDS reports at the vintage of the 2020 edition,
so reconcile declares the aids_cases_reported pair derived (ruling R36). Over the 190
country-years for 2015 to 2019 in ecdc_hiv_report and who_europe_hfa, the counts are equal in 120, and the HFA_348
counts add to 98 per cent of the 2025 counts. Never compare aids_cases_reported with aids_deaths,
new_infections or notified_hiv_cases.

TAGGING. source_type is routine_programme_record (national case surveillance).
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ..config.indicators import CANONICAL_INDICATORS
from ..connector_base import BaseConnector
from ..normalize import name_for
from ..schema import PanelRow, SourceType, POP_ALL

log = logging.getLogger("hivimpact")

_URL = "https://www.ecdc.europa.eu/sites/default/files/documents/2025-Annual-HIV-Report.pdf"
_LOCAL = "ecdc_hiv_surveillance_europe_2025.pdf"
_KNOWN = (20_246_576, "dba8d8c5999d")      # size and sha256 prefix of the copy read on 20 October 2026
_EDITION = ("HIV/AIDS surveillance in Europe 2025 (2024 data), ECDC and WHO Regional Office for "
            "Europe")
_CAPTION = ("Table 1: HIV diagnoses and rates per 100 000 population, by country and year of "
            "diagnosis (2015–2024) and cumulative")
_NOTES = ("research/phase8_eeca/eeca_round1_notes.md, the ECDC report, and rulings R11 and R35 of "
          "research/rulings_2026-10-15.md")

_CAPTION_T13 = ("Table 13: AIDS diagnoses and rates per 100 000 population, by country and year of "
                "diagnosis (2015–2024) and cumulative")

_YEARS = tuple(range(2015, 2025))
#: the regional total of every year in the copy read on 20 October 2026
_EXPECTED_REGION = dict(zip(_YEARS, (160_009, 147_334, 147_403, 146_625, 140_970, 108_744,
                                     110_175, 113_542, 114_131, 105_922)))
_EXPECTED_REGION_T13 = dict(zip(_YEARS, (15_697, 15_813, 15_799, 15_157, 13_255, 8_502, 8_819,
                                         7_596, 8_174, 7_161)))

#: Table 1 row name (footnote letters included, as printed) -> ISO3, or None for a row the gates
#: read and the connector never emits
_ISO3: Dict[str, Optional[str]] = {
    "Austriac": "AUT", "Belgium": "BEL", "Bulgaria": "BGR", "Croatia": "HRV", "Cyprus": "CYP",
    "Czechia": "CZE", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN", "France": "FRA",
    "Germanyd": "DEU", "Greece": "GRC", "Hungary": "HUN", "Iceland": "ISL", "Ireland": "IRL",
    "Italy": "ITA", "Latvia": "LVA", "Liechtenstein": "LIE", "Lithuania": "LTU",
    "Luxembourge": "LUX", "Malta": "MLT", "Netherlands": "NLD", "Norway": "NOR", "Poland": "POL",
    "Portugal": "PRT", "Romania": "ROU", "Slovakia": "SVK", "Slovenia": "SVN", "Spain": "ESP",
    "Sweden": "SWE",
    "Albania": "ALB", "Andorra": "AND", "Armenia": "ARM", "Azerbaijan": "AZE", "Belarus": "BLR",
    "Bosnia and Herzegovina": "BIH", "Georgia": "GEO", "Israel": "ISR", "Kazakhstan": "KAZ",
    "Kyrgyzstan": "KGZ", "Moldova": "MDA", "Monaco": "MCO", "Montenegro": "MNE",
    "North Macedonia": "MKD", "Russian Federationf": "RUS", "San Marino": "SMR",
    "Serbia": None, "Serbia excluding Kosovog": "SRB", "Kosovog": "XKX", "Switzerland": "CHE",
    "Tajikistan": "TJK", "Türkiye": "TUR", "Turkmenistan": "TKM", "Ukraine": "UKR",
    "United Kingdom": "GBR", "Uzbekistan": "UZB",
}
_SERBIA_PARTS = ("Serbia excluding Kosovog", "Kosovog")

#: Table 13 prints the Russian row with no footnote letter and the Kosovo note as footnote f
_RENAMED_T13 = {"Russian Federationf": "Russian Federation",
                "Serbia excluding Kosovog": "Serbia excluding Kosovof", "Kosovog": "Kosovof"}
_ISO3_T13: Dict[str, Optional[str]] = {_RENAMED_T13.get(n, n): c for n, c in _ISO3.items()}
_SERBIA_PARTS_T13 = ("Serbia excluding Kosovof", "Kosovof")

#: (ISO3, first year, last year, reason). None as the last year means every later year.
_REFUSED = [
    ("AUT", 0, None, "footnote c of Table 1 says Austria uses study cohort data (AHIVCOS, 64 per "
                     "cent of the people ever on antiretroviral therapy in 2022, Annex 5)"),
    ("TUR", 0, None, "Annex 5 says the Turkish HIV cases exclude people diagnosed with AIDS at "
                     "the time of HIV diagnosis"),
    ("MKD", 0, 2016, "Annex 4a says North Macedonia reported the separate HIV record type to 2016, "
                     "under which an HIV count can miss people diagnosed with AIDS at HIV "
                     "diagnosis (Annex 5)"),
    ("RUS", 0, 2015, "Annex 5 says the Russian case definitions changed in 2016, and the data for "
                     "2009 to 2015 cannot be compared directly with 2016 to 2024"),
    ("ESP", 2018, 2018, "Annex 5 says the 2018 data from Catalonia are not available"),
    ("UKR", 2015, 2015, "Table 1 prints 13 000, a round thousand beside exact counts in every "
                        "other Ukrainian year"),
    ("ARM", 0, None, "Table 1 equals the counts of citizens of Armenia in Figure 2 of the HIV "
                     "situation analysis 2025 of the National Centre for Infectious Diseases of "
                     "Armenia in every year from 2015 to 2024, a citizens-only count, and am_ncid "
                     "carries citizens plus foreign citizens (ruling R45)"),
]

#: the refusals of Table 13 (AIDS diagnoses), (ISO3, first year, last year, reason)
_REFUSED_AIDS = [
    ("AUT", 0, None, "footnote c of Table 13 says Austria uses study cohort data, and Annex 4b gives "
                     "the Austrian AIDS source (AT-AIDS) the note on the Austrian HIV cohort study "
                     "(ruling R35)"),
    ("TUR", 0, None, "AIDS counted only at the time of HIV diagnosis (ruling R36)"),
    ("MKD", 0, None, "AIDS counted only at the time of HIV diagnosis (ruling R36)"),
    ("IRL", 0, None, "AIDS counted only at the time of HIV diagnosis from 2012, the reason "
                     "who_europe_hfa refuses HFA_348 from 2012 (ruling R36)"),
    ("GBR", 0, None, "British AIDS surveillance moved toward AIDS within three months of HIV "
                     "diagnosis, the reason who_europe_hfa refuses HFA_348 from 2011 (ruling R36)"),
    ("ESP", 2015, 2023, "Annex 5 says the AIDS data of two Spanish regions could not be included for "
                        "2015 to 2022 and of three regions for 2023 (ruling R36)"),
    ("CYP", 0, None, "the 2025 edition raises the Cypriot AIDS counts for 2015 to 2019 from 13, 22, "
                     "15, 13 and 3 to 70, 75, 67, 73 and 85 with the Cypriot HIV counts unchanged, "
                     "and Annex 5 gives no reason (ruling R36)"),
    ("KGZ", 0, None, "the 2025 edition lowers the Kyrgyz AIDS counts for 2015 to 2019 from 125, 72, "
                     "59, 56 and 46 to 35, 33, 46, 47 and 20, and the Kyrgyz cumulative of 884 lies "
                     "below the 999 AIDS deaths the Kyrgyz national HIV centre counts to 1 January "
                     "2026 (ruling R36)"),
    ("DEU", 2019, 2019, "the German count for 2019 (74) is a first report, frozen after Germany "
                        "stopped reporting AIDS to TESSy, at 0.31 times the count for 2018 (ruling "
                        "R36)"),
    ("MLT", 2020, 2020, "Annex 5 says the Maltese AIDS count for 2020 should read 1, where Table 13 "
                        "prints 0 (ruling R36)"),
    ("MLT", 2023, 2023, "Annex 5 says the Maltese AIDS count for 2023 should read 2, where Table 13 "
                        "prints 0 (ruling R36)"),
    ("UKR", 2020, None, "the Ukrainian AIDS definition changed in 2020 to AIDS at HIV registration "
                        "(ruling R34)"),
    ("ARM", 0, None, "the joined record holds the Armenian AIDS diagnosis inside an Armenian HIV "
                     "case, and the Armenian HIV cases of Table 1 count citizens of Armenia alone "
                     "(ruling R45)"),
]

#: Annex 5 comments which bear on the count, shortened, by ISO3
_COUNTRY_NOTES = {
    "ARM": "Annex 5 says the Armenian data are presented by date of statistics in place of date "
           "of diagnosis.",
    "UKR": "Annex 5 says the Ukrainian data are presented by date of statistics in place of date "
           "of diagnosis, and the population movement after 2022 has lowered the completeness "
           "and quality of the data.",
    "LUX": "Footnote e of Table 1 says the Luxembourg counts are by date of diagnosis, while the "
           "national statistics are by date of notification. Annex 5 says laboratories notify "
           "HIV cases electronically and no medical case notification exists.",
    "NLD": "Annex 5 says Dutch surveillance rests on the ATHENA cohort, which holds 98 per cent of "
           "the people who entered HIV care in the Netherlands, and the national report excludes "
           "migrants with a documented diagnosis before arrival.",
    "FRA": "Annex 5 says the French case reports are not exhaustive because of reporting delay "
           "and underreporting, estimated at 30 per cent for HIV in 2023, and gives an adjusted "
           "estimate of 5 473 new HIV diagnoses for 2023.",
    "IRL": "Annex 5 says the Irish HIV diagnoses include a growing share of people previously "
           "diagnosed elsewhere who transfer HIV care to Ireland on arrival.",
    "FIN": "Annex 5 says a case previously diagnosed abroad is classified by the year of "
           "diagnosis in Finland.",
    "GRC": "Annex 5 says a case previously diagnosed abroad is classified by the year of "
           "diagnosis abroad, or by the first positive test in Greece where the earlier date is "
           "unknown.",
    "CZE": "Annex 5 says foreigners with short stays are not counted, and the higher counts for "
           "2022 to 2024 come from the arrival of people from Ukraine.",
    "POL": "Annex 5 says refugees from Ukraine made up 22.3 per cent of the cases reported in "
           "2023.",
    "PRT": "Annex 5 says work on underreporting and reporting delay in 2013 and 2017 raised the "
           "reported cases of every earlier year.",
    "ITA": "Annex 5 says Italian surveillance has been national since 2012.",
    "RUS": "Annex 5 says the Russian Federation reports an aggregated data set, and the Russian "
           "case definitions changed in 2016.",
    "LIE": "Annex 5 says Liechtenstein reported to ECDC through Switzerland until 2021, and Table 1 "
           "prints a separate Liechtenstein count for every year.",
    "CHE": "Annex 5 says Liechtenstein reported to ECDC through Switzerland until 2021, and Table 1 "
           "prints a separate Liechtenstein count for every year.",
}

#: the notes of Table 13 (AIDS diagnoses) which bear on the count, by ISO3
_AIDS_NOTES = {
    "BEL": "Annex 4b says Belgian AIDS surveillance rests on reports of AIDS diagnoses at the time "
           "of HIV diagnosis or during medical follow-up, not exhaustively reported.",
    "FRA": "Annex 4b says French AIDS diagnoses are not exhaustively reported, with underreporting "
           "estimated at 41 per cent in 2007 to 2009, 46 per cent in 2016 to 2017 and 42 per cent "
           "in 2023, and the count stays the national reported count.",
    "DEU": "The German rows of the AIDS tables of the 2020 and 2025 editions are identical, "
           "because Germany stopped reporting AIDS cases to TESSy after the 2020 reporting round, "
           "and footnote d of Table 13 says the German cumulative differs from the national total "
           "because of the counting method.",
    "LUX": "Footnote e of Table 13 says the Luxembourg counts are by date of diagnosis, while the "
           "national statistics are by date of notification.",
    "LIE": "Annex 5 says Liechtenstein reported to ECDC through Switzerland until 2021, and Table 13 "
           "prints a separate Liechtenstein count to 2021.",
    "CHE": "Annex 5 says Liechtenstein reported to ECDC through Switzerland until 2021, and Table 13 "
           "prints a separate Liechtenstein count to 2021.",
    "ARM": "Annex 4b gives the Armenian AIDS source the code Se, while the joined HIV and AIDS record "
           "holds the AIDS diagnosis inside an HIV case reported nationally, and Annex 5 says the "
           "Armenian data are presented by date of statistics in place of date of diagnosis.",
    "AZE": "The AIDS counts of workbook 001_2_28.xls of the State Statistical Committee of "
           "Azerbaijan, for citizens of Azerbaijan alone, lie just below the Table 13 counts.",
    "UKR": "Annex 5 says the Ukrainian data are presented by date of statistics in place of date of "
           "diagnosis.",
}

_ROW = re.compile(r"^(West|Centre|East) (.+?) (\d{4}) (.+)$")
_TOTAL = re.compile(r"^(Total EU/EEA|Total non-EU/EEA|West|Centre|East|Total WHO European Region) "
                    r"([\d .\-]+?) (Total EU/EEA|Total non-EU/EEA|West|Centre|East|"
                    r"Total WHO European Region)$")
_SECTIONS = {"EU/EEA EU/EEA": "EU/EEA", "Non-EU/EEA Non-EU/EEA": "non-EU/EEA",
             "WHO European Region WHO European Region": "region"}


class _Refused(Exception):
    """A gate failed, and every row is refused."""


def _refusal(iso3: str, year: int, refused: List = _REFUSED) -> Optional[str]:
    for c, first, last, reason in refused:
        if c == iso3 and year >= first and (last is None or year <= last):
            return reason
    return None


def _group(digits: List[str]) -> int:
    """A count printed in groups of three digits, the first group holding one to three digits."""
    if (not digits or not re.fullmatch(r"\d{1,3}", digits[0])
            or any(not re.fullmatch(r"\d{3}", g) for g in digits[1:])):
        raise _Refused(f"a count is not grouped in thousands ({' '.join(digits)})")
    return int("".join(digits))


def _entries(tokens: List[str]) -> Tuple[List[Optional[Tuple[int, float]]], int]:
    """The 10 (count, rate) entries and the cumulative total of a printed row."""
    out: List[Optional[Tuple[int, float]]] = []
    digits: List[str] = []
    i = 0
    while len(out) < len(_YEARS):
        if i >= len(tokens):
            raise _Refused(f"a row ends before 10 entries ({' '.join(tokens)})")
        t = tokens[i]
        i += 1
        if t == "-":
            if digits or i >= len(tokens) or tokens[i] != "-":
                raise _Refused(f"a dash stands beside a number ({' '.join(tokens)})")
            i += 1
            out.append(None)
        elif re.fullmatch(r"\d+\.\d", t):
            out.append((_group(digits), float(t)))
            digits = []
        elif re.fullmatch(r"\d+", t):
            digits.append(t)
        else:
            raise _Refused(f"a row holds the token {t!r}")
    if digits:
        raise _Refused(f"a count has no rate ({' '.join(tokens)})")
    # Table 13 prints a single dash as the Russian cumulative total
    if tokens[i:] == ["-"]:
        return out, None
    return out, _group(tokens[i:])


def _parse_page(text: str) -> Dict:
    """Table 1 or Table 13 as printed on one page, the country rows and the total rows."""
    lines = [ln.strip() for ln in text.splitlines()]
    # Table 13 closes the EU/EEA total row with "Total EU-EEA"
    lines = [ln[: -len("Total EU-EEA")] + "Total EU/EEA"
             if ln.startswith("Total EU/EEA ") and ln.endswith(" Total EU-EEA") else ln
             for ln in lines]
    if not any(ln == "Year of " + " ".join(str(y) for y in _YEARS) for ln in lines):
        raise _Refused("the year line 2015 to 2024 is missing")
    rows: Dict[str, Dict] = {}
    totals: Dict[str, Tuple] = {}
    section = None
    for line in lines:
        if line in _SECTIONS:
            section = _SECTIONS[line]
            continue
        m = _TOTAL.match(line)
        if m and (m.group(1).startswith("Total") or section == "region"):
            if m.group(3) != m.group(1):
                raise _Refused(f"a total row is not closed by the row name ({line})")
            totals[m.group(1)] = _entries(m.group(2).split())
            continue
        m = _ROW.match(line)
        if m and section in ("EU/EEA", "non-EU/EEA"):
            area, name, _start, rest = m.groups()
            # the row name is printed at the start and at the end of the row
            if not rest.endswith(" " + name):
                raise _Refused(f"a row is not closed by the row name ({line})")
            body = rest[: -len(name) - 1]
            if name in rows:
                raise _Refused(f"the row {name} is printed twice")
            counts, cumulative = _entries(body.split())
            rows[name] = {"area": area, "section": section, "entries": counts,
                          "cumulative": cumulative}
    return {"rows": rows, "totals": totals}


#: the two tables the connector reads, with the constants every gate needs
_TABLES = {
    "table1": {"label": "Table 1", "caption": _CAPTION, "iso3": _ISO3, "serbia": _SERBIA_PARTS,
               "expected": _EXPECTED_REGION},
    "table13": {"label": "Table 13", "caption": _CAPTION_T13, "iso3": _ISO3_T13,
                "serbia": _SERBIA_PARTS_T13, "expected": _EXPECTED_REGION_T13},
}


def _check(table: Dict, spec: Dict) -> None:
    """The gates on the sums of Table 1 or Table 13. Raises _Refused on the first failure."""
    rows, totals, label_t = table["rows"], table["totals"], spec["label"]
    serbia = spec["serbia"]
    if set(rows) != set(spec["iso3"]):
        raise _Refused("the %s row names differ from the name map (missing %s, new %s)" % (
            label_t, sorted(set(spec["iso3"]) - set(rows)), sorted(set(rows) - set(spec["iso3"]))))
    for label in ("Total EU/EEA", "Total non-EU/EEA", "West", "Centre", "East",
                  "Total WHO European Region"):
        if label not in totals:
            raise _Refused(f"the {label_t} total row {label} is missing")
    eu = [n for n, r in rows.items() if r["section"] == "EU/EEA"]
    non_eu = [n for n, r in rows.items() if r["section"] == "non-EU/EEA" and n not in serbia]
    if len(eu) != 30 or len(non_eu) != 24:
        raise _Refused(f"{label_t} holds {len(eu)} EU/EEA and {len(non_eu)} other rows")

    def count(name: str, k: int) -> int:
        e = rows[name]["entries"][k]
        return 0 if e is None else e[0]

    for k, year in enumerate(_YEARS):
        region = totals["Total WHO European Region"][0][k][0]
        for label, names in (("Total EU/EEA", eu), ("Total non-EU/EEA", non_eu)):
            if sum(count(n, k) for n in names) != totals[label][0][k][0]:
                raise _Refused(f"the {label_t} {label} rows do not add to the total for {year}")
        for area in ("West", "Centre", "East"):
            names = [n for n in eu + non_eu if rows[n]["area"] == area]
            if sum(count(n, k) for n in names) != totals[area][0][k][0]:
                raise _Refused(f"the {label_t} {area} rows do not add to the area total for {year}")
        if sum(totals[a][0][k][0] for a in ("West", "Centre", "East")) != region:
            raise _Refused(f"the {label_t} area totals do not add to the regional total for {year}")
        if totals["Total EU/EEA"][0][k][0] + totals["Total non-EU/EEA"][0][k][0] != region:
            raise _Refused(f"the {label_t} EU/EEA and other totals do not add to the regional "
                           f"total for {year}")
        if sum(count(n, k) for n in serbia) != count("Serbia", k):
            raise _Refused(f"{label_t} Serbia excluding Kosovo plus Kosovo differs from Serbia for "
                           f"{year}")
        if region != spec["expected"][year]:
            log.warning("ecdc_hiv_report: the %s regional total for %d reads %d, where the copy "
                        "read on 20 October 2026 printed %d", label_t, year, region,
                        spec["expected"][year])
    for label, names in (("Total EU/EEA", eu), ("Total non-EU/EEA", non_eu)):
        # a dash as a cumulative total (the Russian row of Table 13) adds nothing
        if sum(rows[n]["cumulative"] or 0 for n in names) != totals[label][1]:
            raise _Refused(f"the {label_t} {label} cumulative totals do not add up")


class ECDCHIVReportConnector(BaseConnector):
    """ECDC and WHO Europe joint report 2025, Table 1, HIV diagnoses by country, 2015 to 2024."""

    source_id = "ecdc_hiv_report"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Joint ECDC and WHO Regional Office for Europe report HIV/AIDS surveillance in "
                   "Europe 2025 (2024 data), Table 1, HIV diagnoses by country and year of "
                   "diagnosis, 2015 to 2024.")
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/ecdc_hiv_report", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the report, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("ecdc_hiv_report: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("ecdc_hiv_report: downloaded the report (%.1f MB) -> %s", len(blob) / 1e6,
                     path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("ecdc_hiv_report: the report matches the copy read on 20 October 2026 "
                     "(sha256 %s)", digest[:12])
        else:
            log.warning("ecdc_hiv_report: the report differs from the copy read on 20 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s), and the text gates still "
                        "run", len(blob), digest[:12], *_KNOWN)
        return path

    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = {c.upper() for c in countries} if countries else None
        if wanted and not wanted & {c for c in _ISO3.values() if c}:
            return
        if end_year < _YEARS[0] or start_year > _YEARS[-1]:
            return
        try:
            import pdfplumber
        except ImportError:
            log.error("ecdc_hiv_report: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            path = self._pdf_path()
        except Exception as exc:
            log.warning("ecdc_hiv_report: the report could not be fetched (%s)", exc)
            return
        try:
            tables = self._parse(pdfplumber, path)
        except Exception as exc:
            log.warning("ecdc_hiv_report: the report failed to parse (%s)", exc)
            return
        emitted = 0
        for key in _TABLES:
            if key not in tables:
                continue
            for row in self._rows(tables[key], key, wanted, start_year, end_year):
                emitted += 1
                yield row
        log.info("ecdc_hiv_report: emitted %d rows", emitted)

    def _parse(self, pdfplumber, path: Path) -> Dict[str, Dict]:
        """Every table of _TABLES whose gates pass, by key. A table failing a gate is left
        unread with a WARNING, and the other table still emits."""
        found: Dict[str, List] = {key: [] for key in _TABLES}
        with pdfplumber.open(str(path)) as pdf:
            for number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                flat = " ".join(text.split())
                for key, spec in _TABLES.items():
                    # the list of tables names the caption on a page without table rows
                    if (spec["caption"] in flat
                            and any(_ROW.match(ln.strip()) for ln in text.splitlines())):
                        try:
                            found[key].append((number, _parse_page(text)))
                        except _Refused as exc:
                            found[key].append((number, exc))
        tables: Dict[str, Dict] = {}
        for key, spec in _TABLES.items():
            try:
                tables[key] = self._one(found[key], spec)
            except _Refused as exc:
                log.warning("ecdc_hiv_report: every %s row refused because %s", spec["label"], exc)
        return tables

    @staticmethod
    def _one(found: List, spec: Dict) -> Dict:
        """The single reading of one table, after the copy and sum gates."""
        label = spec["label"]
        if not found:
            raise _Refused(f"the report prints no {label}")
        for number, copy in found:
            if isinstance(copy, _Refused):
                raise _Refused(f"{copy} (page {number})")
        first = found[0][1]
        for number, copy in found[1:]:
            if copy != first:
                raise _Refused(f"the copy of {label} on page {number} differs from page "
                               f"{found[0][0]}")
        _check(first, spec)
        log.info("ecdc_hiv_report: %s on page%s %s (%d printed cop%s), 56 rows, every gate "
                 "passed", label, "s" if len(found) > 1 else "",
                 " and ".join(str(n) for n, _ in found), len(found),
                 "y" if len(found) == 1 else "ies")
        first["page"] = found[0][0]
        return first

    def _rows(self, table: Dict, key: str, wanted, start_year: int,
              end_year: int) -> Iterator[PanelRow]:
        aids = key == "table13"
        spec = _TABLES[key]
        indicator = "aids_cases_reported" if aids else "notified_hiv_cases"
        unit = CANONICAL_INDICATORS[indicator].unit
        refusals = _REFUSED_AIDS if aids else _REFUSED
        notes = _AIDS_NOTES if aids else _COUNTRY_NOTES
        refused: Dict[str, int] = {}
        absent = 0
        for name, iso3 in spec["iso3"].items():
            if iso3 is None or (wanted and iso3 not in wanted):
                continue
            row = table["rows"][name]
            for k, year in enumerate(_YEARS):
                if not start_year <= year <= end_year:
                    continue
                entry = row["entries"][k]
                if entry is None:
                    absent += 1
                    continue
                reason = _refusal(iso3, year, refusals)
                if reason:
                    rkey = f"{iso3}, {reason}"
                    refused[rkey] = refused.get(rkey, 0) + 1
                    continue
                count, rate = entry
                extra: Dict = {
                    "edition": _EDITION,
                    "page": table["page"],
                    "caption": spec["caption"] + " totals, in EU/EEA and other countries of the "
                                                 "WHO European Region",
                    "table_row": name,
                    "extraction": f"text layer, the N entry of {spec['label']}",
                    "rate_per_100000": rate,
                    "area": row["area"],
                    "eu_eea": row["section"] == "EU/EEA",
                    "reporting_delay_adjusted": False,
                    "integrity": (f"every printed copy of {spec['label']} reads the same, and the "
                                  "rows add to the EU/EEA, non-EU/EEA, area and regional totals in "
                                  "every year"),
                    "notes": _NOTES,
                }
                if aids:
                    extra["case_definition"] = (
                        "AIDS diagnoses the country reported to TESSy for the calendar year of "
                        "diagnosis, as Table 13 of the 2025 joint report prints the count. Annex 1 "
                        "of the 2025 joint report says only confirmed cases are reported at "
                        "European level, under the WHO case definitions and the EU case "
                        "definitions of Commission Decision 2002/253/EC, and says national case "
                        "definitions may differ across the WHO European Region")
                    extra["reconcile_with"] = (
                        "who_europe_hfa (HFA_348) holds the same TESSy reports at the vintage of "
                        "the 2020 edition, and reconcile declares the pair derived (ruling R36). "
                        "Never compare with the modelled aids_deaths or new_infections, or with "
                        "notified_hiv_cases")
                else:
                    extra["definition"] = (
                        "HIV diagnoses the country reported to TESSy for the calendar year of "
                        "diagnosis, people diagnosed for the first time and people with a "
                        "previous positive diagnosis abroad or elsewhere in the country together "
                        "(footnotes 7 and 8, page 29), as Table 1 of the 2025 joint report prints "
                        "the count")
                    extra["reconcile_with"] = (
                        "who_europe_hfa (HFA_350) holds the same TESSy reports at the vintage of "
                        "the 2020 edition, and reconcile declares the pair derived (ruling R35). "
                        "ge_geostat, by_belstat and ua_npsi read the national registers behind "
                        "the Georgian, Belarusian and Ukrainian counts. Never compare with "
                        "new_diagnoses (Jason's ruling of 8 October 2026)")
                if iso3 == "SRB":
                    extra["territory"] = (f"Serbia excluding Kosovo, the row {spec['label']} "
                                          "prints")
                if iso3 in notes:
                    extra["country_note"] = notes[iso3]
                yield self.make_row(
                    country_iso3=iso3, country_name=name_for(iso3),
                    indicator_id=indicator, year=year, value=float(count),
                    population_group=POP_ALL, unit=unit, source_url=_URL,
                    source_indicator_code=f"ecdc_hiv_2025.{key}.N",
                    extra=extra,
                )
        for reason, n in sorted(refused.items()):
            log.info("ecdc_hiv_report: %s, %d country-years refused, %s", spec["label"], n, reason)
        log.info("ecdc_hiv_report: %s, %d absent entries (a dash)", spec["label"], absent)
