"""
Nicaragua, MINSA Mapa Nacional de la Salud, notified HIV cases by SILAIS and nationally, 2017
to 2023 (to-source, routine programme, sub-national).

Nicaragua's Ministry of Health (MINSA, Ministerio del Poder Ciudadano para la Salud) publishes
the Mapa Nacional de la Salud en Nicaragua on mapasalud.minsa.gob.ni, a WordPress site with a
page for the whole country and a page for every SILAIS of the 19 SILAIS (Sistemas Locales de
Atención Integral en Salud, the local health areas through which the ministry runs health
services). Every page holds a section headed "Situación VIH" with a tab for every year, and every
year tab holds a table of 11 numbered rows headed "Año YYYY" over a footnote naming the source as
the "Sistema de información de Vigilancia Epidemiológica". Row 1 of every
table reads "Casos Nuevos", the new HIV cases of the year, and row 2 reads "Personas en TAR", the
people on antiretroviral treatment.

The live site fails the TLS handshake from outside Nicaragua (SSLEOFError on 13 and 14 October
2026), so the connector reads fixed captures from the Internet Archive's Wayback Machine. Every
capture is requested at the raw "id_" address, which returns the page as mapasalud served the
page, with no archive toolbar. A capture is downloaded once into `raw_dir` and read from the
cached copy after the first run. Captures are requested 30 seconds apart, and a capture not yet
cached is requested once, with no retry. The fifth to ninth runs (22 to 27 October 2026) made
12 retries after waits of 10 or 15 minutes, 11 retries were refused, mostly with HTTP 429 (too
many requests), and a single retry came through. The first capture lost to a refusal or a network error ends the downloads of
the run, the run then reads the cached captures only, and the captures already downloaded stay
cached, so the next run requests only the missing captures. With every capture cached, a cached
copy whose size or sha256 differs from the copy read on 14 October 2026 is logged as a WARNING
and still parsed, because every gate below runs on the tables themselves. With a SILAIS capture
not yet cached, the run emits the national rows only, under the gates of a partial run below.

    pages                                                    captured            years read
    the national page                                        8 September 2024    2017 to 2023
    Chinandega, Managua, Masaya, RACCS, Río San Juan, Rivas  June to Oct 2024    2017 to 2023
    Bilwi, León, Matagalpa, Zelaya Central                   Oct to Dec 2023     2017 to 2022
    Boaco, Carazo, Chontales, Estelí, Granada, Jinotega,     17 June 2022        2017 to 2021
      Las Minas, Madriz, Nueva Segovia

    national Casos Nuevos   2017 1,033  2018 1,102  2019 1,118  2020 953  2021 938
                            2022 1,129  2023 1,155

WHAT THE COUNT IS
-----------------
The emitted value is the Casos Nuevos entry of the year, the new HIV cases recorded by the
ministry's epidemiological surveillance system. The pages give no definition, so whether a case
is placed by the residence of the person or by the SILAIS making the diagnosis is not known.
Under Jason's ruling of 8 October 2026, a ministry's own count of HIV cases goes under
`notified_hiv_cases` and is never merged with or compared to `new_diagnoses`. The other 10 rows
of every table (people on treatment, pregnant women with HIV, HIV and syphilis tests, tests in
key populations, deaths from causes related to HIV) travel in `extra.other_rows_printed` as
printed and are not emitted. Treatment by SILAIS, surveillance deaths and test counts are held
for a decision (research/phase5_lac/lac_round1_notes.md, section "Nicaragua SILAIS check, 14
October 2026").

WHICH CAPTURES
--------------
Every page is read from the newest Wayback capture listed by the CDX index on 14 October 2026.
The nine SILAIS pages captured on 17 June 2022 have no later capture. For the 10 SILAIS pages
with a later capture, the captures of 10 June 2022 print the same values for 2017 to 2021 as the
later capture, so a capture never revised an earlier year, and only the newest capture is read.
In the captures from 2023 and 2024 the tabs show the last five years only, while the panes for
2017 and 2018 stay in the HTML, hidden, and are read.

THE SILAIS AND THE DEPARTMENTS
------------------------------
The district map files on mapasalud (wp-content/uploads/mapa/, one SVG for every SILAIS, with one
button for every municipality) list the municipalities of every SILAIS. Checked on 14 October
2026 against the 153 municipalities of the Spanish Wikipedia list "Anexo:Municipios de
Nicaragua", the 19 lists cover all 153 municipalities with no municipality twice.
  * 13 SILAIS cover exactly the municipalities of one department, and the rows of the 13 SILAIS
    carry the department name in admin1, spelt as pepfar_snu spells Nicaraguan departments
    (León, Río San Juan). The 13 SILAIS are Boaco, Carazo, Chinandega, Estelí, Granada,
    Jinotega, León, Madriz, Managua, Masaya, Nueva Segovia, Río San Juan and Rivas.
  * Six SILAIS cross department lines, and together the six SILAIS cover exactly the
    departments of Chontales and Matagalpa and the two autonomous regions of the Caribbean coast,
    RACCN (Región Autónoma de la Costa Caribe Norte) and RACCS (Región Autónoma de la Costa
    Caribe Sur), which pepfar_snu calls Atlántico Norte and Atlántico Sur. SILAIS Chontales holds
    the Chontales department without El Coral, plus El Ayote from RACCS. SILAIS Matagalpa holds
    the 13 municipalities of the Matagalpa department plus Waslala from RACCN. SILAIS Bilwi holds
    Puerto Cabezas, Waspam and Prinzapolka, all in RACCN. SILAIS Las Minas holds Siuna, Rosita,
    Bonanza and Mulukukú from RACCN plus Bocana de Paiwas from RACCS. SILAIS RACCS holds seven of
    the 12 municipalities of RACCS. SILAIS Zelaya Central holds Nueva Guinea, El Rama and Muelle
    de los Bueyes from RACCS plus El Coral from Chontales. The rows of the six SILAIS carry
    "SILAIS " and the SILAIS name in admin1 (SILAIS Chontales, SILAIS RACCS), so no row of the six
    SILAIS ever matches a department row of another source. The same practice holds in dhs,
    where admin1 holds a survey's own first regional level.
Every SILAIS row carries the municipalities in `extra.silais_municipalities` and the departments
covered in `extra.departments_covered`. The SILAIS rows cannot rebuild a department count for
Chontales, Matagalpa, RACCN or RACCS, so no department count is built for Chontales, Matagalpa,
RACCN or RACCS.

PARSING
-------
Every page is read with the standard library HTML parser, with character references converted
("&#8211;" becomes an en dash). A pane is a div element whose id reads "VIH" and a four-digit
year, and the pane id gives the year. A pane counts as an HIV pane when the pane holds a table
row of three entries reading "1", "Casos Nuevos" and a value. The Managua capture of 3 October
2024 carries a second div with the id "VIH2022" on an immunisation table in the section
"Inmunización", and every pane outside the HIV shape is logged at INFO and set aside. An HIV
pane holds 13 table rows, one header row whose last entry reads "Año YYYY" or "Años YYYY", one
footnote row, and the numbered rows 1 to 11. The header year must equal the pane year. The only
known exception is the Boaco pane "VIH2021" of 17 June 2022, which prints "Año 2020" over values
for 2021, as the sums below confirm, so the pane id wins and the printed label travels in
`extra.year_label_printed`. A value is digits, with or without commas between groups of three,
and surrounding spaces are ignored. Some tables print an en dash where a value belongs, and the
dash is kept as printed in `extra.other_rows_printed`. A dash in the Casos Nuevos row refuses the
source.

INTEGRITY GATES
---------------
  * every page answers with the h1 heading expected for the page.
  * every page holds exactly one HIV pane for every year expected on the page and no HIV pane
    for any other year.
  * every HIV pane holds the footnote row, the header row and the numbered rows 1 to 11 and
    nothing else, row 1 reads "Casos Nuevos" and row 2 reads "Personas en TAR".
  * every header year equals the pane year, with the Boaco exception above.
  * every Casos Nuevos entry is a whole number.
  * for 2017, 2019, 2020 and 2021 the 19 SILAIS sum exactly to the national page.
  * for 2018 the 19 SILAIS sum to 1,092, 10 cases short of the national 1,102. The shortfall
    stands in the source, since the captures of June 2022 print the same values as the later
    captures, so a shortfall of exactly 10 passes and any other difference refuses the source.
    The 2018 rows carry the shortfall in `extra.sum_check`.
  * for 2022 and 2023, when only some SILAIS pages carry the year, the SILAIS on the archived
    pages must not sum above the national page.
A failed gate refuses every page, because the sum gates join the pages. With every capture
cached, a value passing every gate but differing from the values read on 14 October 2026 is
logged as a WARNING and still emitted.

A partial run, with a SILAIS capture not yet cached, runs the page gates above on every cached
page and replaces the sum gates with stricter gates.
  * the national capture is cached.
  * every cached capture matches the size and sha256 of the copy read on 14 October 2026.
  * every cached page prints the Casos Nuevos values read on 14 October 2026.
  * in every year the cached SILAIS pages sum to no more than the national page.
  * the Casos Nuevos values read on 14 October 2026 from all 20 captures pass the sum gates
    above, 1,033 for 2017, 1,092 against 1,102 for 2018, 1,118 for 2019, 953 for 2020 and 938
    for 2021.
A partial run emits the 2017 to 2023 rows of the national page and no SILAIS row, because the
gates of a SILAIS row join all 19 SILAIS pages. The Wayback captures read at the "id_" address do
not change, so a cached capture matching the size and sha256 of the copy read on 14 October 2026
is the same page, and `extra.sum_check` of a national row cites the sums of the 14 October 2026
reading. `extra.silais_not_cached` names the SILAIS captures still missing.

LABELS
------
admin1 holds the department name for the 13 SILAIS equal to a department, "SILAIS" and the
SILAIS name for the six SILAIS crossing department lines, and "" for the national page. The h1
heading of the page travels in `extra.admin1_source_label`, and `extra.admin1_note` says what
area the row covers.

RECONCILIATION
--------------
For SILAIS rows, pepfar_snu holds Nicaraguan department rows of new_diagnoses and on_art_count, a
different count at donor-supported sites, and the two are never compared. For national rows,
paho_core holds Nicaragua from PAHO Core Indicator 93, reported by the same ministry, and the
`reconcile_with` note of every national row names the difference. The values agree in 2018, 2019
and 2021 and differ in 2017, 2020, 2022 and 2023. The rows stay apart and are not merged.

TAGGING
-------
source_type is routine_programme_record, indicator notified_hiv_cases, unit count, sex all and
age group all.
"""
from __future__ import annotations

import hashlib
import logging
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
from ._pdf_text import norm as _norm

log = logging.getLogger("hivimpact")

_WAYBACK = "https://web.archive.org/web/{ts}id_/{url}"
_SITE = "mapasalud.minsa.gob.ni/"
_NOTES = ("research/phase5_lac/lac_round1_notes.md, section \"Nicaragua SILAIS check, 14 October "
          "2026\"")
_NATIONAL = "nicaragua"

# key, admin1, h1 heading as printed, capture timestamp, page address, (size, sha256[:12]) of the
# copy read on 14 October 2026, last year carried
_PAGES: Tuple[Tuple[str, str, str, str, str, Tuple[int, str], int], ...] = (
    (_NATIONAL, "", "Mapa Nacional de la Salud en Nicaragua", "20240908121951",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-de-nicaragua/",
     (369_461, "2baad731277e"), 2023),
    ("bilwi-raccn", "SILAIS Bilwi",
     "Región Autónoma de la Costa Caribe Norte (RACCN) – SILAIS Bilwi", "20231010173726",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-bilwi-raccn/",
     (282_440, "cc64849646d1"), 2022),
    ("boaco", "Boaco", "SILAIS Boaco", "20220617102235",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-boaco/",
     (251_125, "a6aba6214bea"), 2021),
    ("carazo", "Carazo", "SILAIS Carazo", "20220617102215",
     "http://mapasalud.minsa.gob.ni/ministerio-del-poder-ciudadano-para-la-salud-mapa-de-"
     "padecimientos-de-salud-silais-carazo/",
     (243_862, "81788c3aa3ce"), 2021),
    ("chinandega", "Chinandega", "SILAIS Chinandega", "20240908124755",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-chinandega/",
     (335_651, "1d0090ecabb7"), 2023),
    ("chontales", "SILAIS Chontales", "SILAIS Chontales", "20220617102230",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-chontales/",
     (234_579, "51cefa42058b"), 2021),
    ("esteli", "Estelí", "SILAIS Estelí", "20220617102243",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-esteli/",
     (228_570, "e368a4d3fef0"), 2021),
    ("granada", "Granada", "SILAIS Granada", "20220617102219",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-granada/",
     (241_162, "8ee2e2904438"), 2021),
    ("jinotega", "Jinotega", "SILAIS Jinotega", "20220617102256",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-jinotega/",
     (231_409, "933b25d01393"), 2021),
    ("las-minas", "SILAIS Las Minas", "SILAIS Las Minas", "20220617102305",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-las-minas/",
     (230_613, "ca20f083c872"), 2021),
    ("leon", "León", "SILAIS León", "20231219034031",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-leon/",
     (272_352, "d80ca7cc06c5"), 2022),
    ("madriz", "Madriz", "SILAIS Madriz", "20220617102247",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-madriz/",
     (218_909, "02e6257f79c3"), 2021),
    ("managua", "Managua", "SILAIS Managua", "20241003203938",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-managua/",
     (320_089, "e455121a7bb4"), 2023),
    ("masaya", "Masaya", "SILAIS Masaya", "20240619201831",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-masaya/",
     (323_225, "5209212248ce"), 2023),
    ("matagalpa", "SILAIS Matagalpa", "SILAIS Matagalpa", "20231204125406",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-departamento-de-matagalpa/",
     (275_378, "6842ce32ac6f"), 2022),
    ("nueva-segovia", "Nueva Segovia", "SILAIS Nueva Segovia", "20220617102252",
     "http://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-nueva-segovia/",
     (231_135, "941bab1028cb"), 2021),
    ("raccs", "SILAIS RACCS", "SILAIS Región Autónoma Costa Caribe Sur (RACCS)", "20240908134243",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-raccs/",
     (328_314, "19fb29d662ff"), 2023),
    ("rio-san-juan", "Río San Juan", "SILAIS Río San Juan", "20241003205411",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-rio-san-juan/",
     (323_353, "5edd0c9a8840"), 2023),
    ("rivas", "Rivas", "SILAIS Rivas", "20241003190521",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-rivas/",
     (313_734, "1f1f97918221"), 2023),
    ("zelaya-central", "SILAIS Zelaya Central", "SILAIS Zelaya Central", "20231228203552",
     "https://mapasalud.minsa.gob.ni/mapa-de-padecimientos-de-salud-silais-zelaya-central/",
     (294_534, "e870e41732cd"), 2022),
)
_FIRST_YEAR = 2017

# Casos Nuevos as read on 14 October 2026, from 2017
_EXPECTED: Dict[str, Tuple[int, ...]] = {
    _NATIONAL: (1033, 1102, 1118, 953, 938, 1129, 1155),
    "bilwi-raccn": (95, 119, 110, 82, 83, 87),
    "boaco": (12, 8, 12, 19, 13),
    "carazo": (26, 26, 24, 18, 25),
    "chinandega": (90, 127, 127, 117, 86, 78, 78),
    "chontales": (30, 25, 32, 27, 25),
    "esteli": (13, 10, 11, 13, 19),
    "granada": (37, 43, 27, 41, 26),
    "jinotega": (16, 16, 22, 19, 21),
    "las-minas": (9, 12, 22, 20, 14),
    "leon": (61, 68, 65, 49, 60, 65),
    "madriz": (6, 5, 4, 9, 5),
    "managua": (503, 445, 461, 374, 395, 493, 458),
    "masaya": (44, 59, 71, 70, 58, 85, 98),
    "matagalpa": (42, 39, 34, 23, 35, 43),
    "nueva-segovia": (13, 7, 14, 7, 8),
    "raccs": (17, 25, 29, 20, 15, 18, 29),
    "rio-san-juan": (3, 12, 15, 8, 11, 7, 11),
    "rivas": (13, 35, 28, 28, 34, 29, 32),
    "zelaya-central": (3, 11, 10, 9, 5, 9),
}

# national minus the sum of the 19 SILAIS, for the years every SILAIS page carries
_SHORTFALL = {2018: 10}
_FULL_YEARS = range(2017, 2022)

# (page, pane year): the year the header prints instead of the pane year
_YEAR_LABEL_KNOWN = {("boaco", 2021): 2020}

# municipalities from the MINSA district map files, with the department of every municipality
# from the Spanish Wikipedia list "Anexo:Municipios de Nicaragua", the lists checked 14 October 2026
_MUNICIPALITIES: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "boaco": {"Boaco": ("Boaco", "Camoapa", "San José de los Remates", "San Lorenzo",
                        "Santa Lucía", "Teustepe")},
    "carazo": {"Carazo": ("Diriamba", "Dolores", "El Rosario", "Jinotepe", "La Conquista",
                          "La Paz de Carazo", "San Marcos", "Santa Teresa")},
    "chinandega": {"Chinandega": ("Chichigalpa", "Chinandega", "Corinto", "El Realejo",
                                  "El Viejo", "Posoltega", "Puerto Morazán",
                                  "San Francisco del Norte", "San Juan de Cinco Pinos",
                                  "San Pedro del Norte", "Santo Tomás del Norte", "Somotillo",
                                  "Villanueva")},
    "esteli": {"Estelí": ("Condega", "Estelí", "La Trinidad", "Pueblo Nuevo",
                          "San Juan de Limay", "San Nicolás")},
    "granada": {"Granada": ("Diriá", "Diriomo", "Granada", "Nandaime")},
    "jinotega": {"Jinotega": ("El Cuá", "Jinotega", "La Concordia", "San José de Bocay",
                              "San Rafael del Norte", "San Sebastián de Yalí",
                              "Santa María de Pantasma", "Wiwilí de Jinotega")},
    "leon": {"León": ("Achuapa", "El Jicaral", "El Sauce", "La Paz Centro", "Larreynaga", "León",
                      "Nagarote", "Quezalguaque", "Santa Rosa del Peñón", "Telica")},
    "madriz": {"Madriz": ("Las Sabanas", "Palacagüina", "San José de Cusmapa",
                          "San Juan de Río Coco", "San Lucas", "Somoto", "Telpaneca",
                          "Totogalpa", "Yalagüina")},
    "managua": {"Managua": ("Ciudad Sandino", "El Crucero", "Managua", "Mateare",
                            "San Francisco Libre", "San Rafael del Sur", "Ticuantepe",
                            "Tipitapa", "Villa El Carmen")},
    "masaya": {"Masaya": ("Catarina", "La Concepción", "Masatepe", "Masaya", "Nandasmo",
                          "Nindirí", "Niquinohomo", "San Juan de Oriente", "Tisma")},
    "nueva-segovia": {"Nueva Segovia": ("Ciudad Antigua", "Dipilto", "El Jícaro", "Jalapa",
                                        "Macuelizo", "Mozonte", "Murra", "Ocotal", "Quilalí",
                                        "San Fernando", "Santa María",
                                        "Wiwilí de Nueva Segovia")},
    "rio-san-juan": {"Río San Juan": ("El Almendro", "El Castillo", "Morrito", "San Carlos",
                                      "San Juan de Nicaragua", "San Miguelito")},
    "rivas": {"Rivas": ("Altagracia", "Belén", "Buenos Aires", "Cárdenas", "Moyogalpa",
                        "Potosí", "Rivas", "San Jorge", "San Juan del Sur", "Tola")},
    "bilwi-raccn": {"RACCN": ("Prinzapolka", "Puerto Cabezas", "Waspam")},
    "chontales": {"Chontales": ("Acoyapa", "Comalapa", "Cuapa", "Juigalpa", "La Libertad",
                                "San Pedro de Lovago", "Santo Domingo", "Santo Tomás",
                                "Villa Sandino"),
                  "RACCS": ("El Ayote",)},
    "las-minas": {"RACCN": ("Bonanza", "Mulukukú", "Rosita", "Siuna"),
                  "RACCS": ("Bocana de Paiwas",)},
    "matagalpa": {"Matagalpa": ("Ciudad Darío", "El Tuma-La Dalia", "Esquipulas", "Matagalpa",
                                "Matiguás", "Muy Muy", "Rancho Grande", "Río Blanco",
                                "San Dionisio", "San Isidro", "San Ramón", "Sébaco",
                                "Terrabona"),
                  "RACCN": ("Waslala",)},
    "raccs": {"RACCS": ("Bluefields", "Corn Island", "Desembocadura de Río Grande",
                        "El Tortuguero", "Kukra Hill", "La Cruz de Río Grande",
                        "Laguna de Perlas")},
    "zelaya-central": {"RACCS": ("El Rama", "Muelle de los Bueyes", "Nueva Guinea"),
                       "Chontales": ("El Coral",)},
}
_DEPARTMENT_SIZE = {"RACCN": 8, "RACCS": 12, "Chontales": 10, "Matagalpa": 13}
_WORDS = ("", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")

_PANE_ID = re.compile(r"VIH(\d{4})")
_YEAR_LABEL = re.compile(r"A[ñn]os? (\d{4})")
_VALUE = re.compile(r"\d{1,3}(?:,\d{3})+|\d+")
_FOOTNOTE = "fuente sistema de informacion de vigilancia epidemiologica"
_ROW1 = "casos nuevos"
_ROW2 = "personas en tar"
_ROWS = 11


class _Refused(Exception):
    """A gate failed. Every page is refused, never part of the pages."""


class _Page(HTMLParser):
    """The h1 headings of a page and every div whose id reads VIH and a year, with the table
    rows inside the div."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1: List[str] = []
        self.panes: List[Dict] = []
        self._divs: List[Optional[Dict]] = []
        self._pane: Optional[Dict] = None
        self._row: Optional[List[str]] = None
        self._entry: Optional[List[str]] = None
        self._h1: Optional[List[str]] = None

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            m = _PANE_ID.fullmatch(dict(attrs).get("id") or "")
            if m and self._pane is not None:
                raise _Refused(f"the pane {m.group(0)} opens inside the pane "
                               f"{self._pane['id']}")
            if m:
                self._pane = {"id": m.group(0), "year": int(m.group(1)), "rows": []}
                self.panes.append(self._pane)
                self._divs.append(self._pane)
            else:
                self._divs.append(None)
        elif tag == "tr" and self._pane is not None:
            self._row = []
            self._pane["rows"].append(self._row)
        elif tag in ("td", "th") and self._row is not None:
            self._entry = []
        elif tag == "h1":
            self._h1 = []

    def handle_endtag(self, tag):
        if tag == "div" and self._divs:
            if self._divs.pop() is not None:
                self._pane, self._row, self._entry = None, None, None
        elif tag in ("td", "th") and self._entry is not None and self._row is not None:
            self._row.append(" ".join("".join(self._entry).split()))
            self._entry = None
        elif tag == "tr":
            self._row = None
        elif tag == "h1" and self._h1 is not None:
            self.h1.append(" ".join("".join(self._h1).split()))
            self._h1 = None

    def handle_data(self, data):
        if self._entry is not None:
            self._entry.append(data)
        if self._h1 is not None:
            self._h1.append(data)


def _value(text: str, where: str) -> int:
    if not _VALUE.fullmatch(text):
        raise _Refused(f"{where} reads {text!r} where a whole number belongs")
    return int(text.replace(",", ""))


def _hiv_pane(pane: Dict) -> bool:
    return any(len(r) == 3 and r[0] == "1" and _norm(r[1]) == _ROW1 for r in pane["rows"])


def _read_pane(key: str, pane: Dict) -> Dict:
    where = f"the {key} pane {pane['id']}"
    numbered, header, footnote = [], [], []
    for r in pane["rows"]:
        if len(r) == 3 and r[0].isdigit():
            numbered.append(r)
        elif r and r[-1] and _YEAR_LABEL.fullmatch(r[-1]) and not any(r[:-1]):
            header.append(r[-1])
        elif [e for e in r if e] and all(_norm(e) == _FOOTNOTE for e in r if e) and \
                len([e for e in r if e]) == 1:
            footnote.append(next(e for e in r if e))
        else:
            raise _Refused(f"{where} holds the row {r!r}, and the row is not the header, the "
                           "footnote or a numbered row")
    if [r[0] for r in numbered] != [str(n) for n in range(1, _ROWS + 1)]:
        raise _Refused(f"{where} numbers the rows {[r[0] for r in numbered]}, where 1 to "
                       f"{_ROWS} belong")
    if len(header) != 1 or len(footnote) != 1:
        raise _Refused(f"{where} holds {len(header)} header row(s) and {len(footnote)} footnote "
                       "row(s), where a single header row and a single footnote row belong")
    if _norm(numbered[1][1]) != _ROW2:
        raise _Refused(f"{where} labels row 2 {numbered[1][1]!r}, where 'Personas en TAR' "
                       "belongs")
    printed_year = int(_YEAR_LABEL.fullmatch(header[0]).group(1))
    if printed_year != pane["year"] and _YEAR_LABEL_KNOWN.get((key, pane["year"])) != printed_year:
        raise _Refused(f"{where} prints the header {header[0]!r}")
    return {
        "id": pane["id"],
        "year": pane["year"],
        "cases": _value(numbered[0][2], f"{where}, row 1 ({numbered[0][1]})"),
        "row_printed": " ".join(numbered[0]),
        "year_label": header[0],
        "footnote": footnote[0],
        "others": {r[1]: r[2] for r in numbered[1:]},
    }


def _expected_sum(year: int) -> Tuple[int, int]:
    """(SILAIS carrying the year, sum of the SILAIS) in the values read on 14 October 2026."""
    i = year - _FIRST_YEAR
    vals = [v[i] for k, v in _EXPECTED.items() if k != _NATIONAL and len(v) > i]
    return len(vals), sum(vals)


def _parse(pages: Dict[str, str], differs: Iterable[str] = ()) -> Dict[str, Dict]:
    """Parse the HTML of every page and run every gate. `pages` maps a page key to the page, and
    `differs` names the cached captures whose size or sha256 differs from the copy read on 14
    October 2026. With every page present, every page is returned. With a SILAIS page missing,
    the national page alone is returned, under the gates of a partial run."""
    missing = [p[0] for p in _PAGES if p[0] not in pages]
    if _NATIONAL in missing:
        raise _Refused(f"the {_NATIONAL} page is missing")
    changed = [k for k in differs if k in pages]
    if missing and changed:
        raise _Refused(f"{_num(len(missing))} SILAIS captures are not cached, and the cached "
                       f"captures of {', '.join(changed)} differ from the copies read on 14 "
                       "October 2026")
    if missing:
        for year in _FULL_YEARS:
            n, total = _expected_sum(year)
            nat = _EXPECTED[_NATIONAL][year - _FIRST_YEAR]
            if n != len(_PAGES) - 1 or nat - total != _SHORTFALL.get(year, 0):
                raise _Refused(f"the values read on 14 October 2026 give {_num(n)} SILAIS "
                               f"summing to {total:,} in {year}, against {nat:,} nationally")
    out: Dict[str, Dict] = {}
    for key, admin1, h1, ts, url, known, last in _PAGES:
        if key not in pages:
            continue
        page = _Page()
        page.feed(pages[key])
        page.close()
        if h1 not in page.h1:
            raise _Refused(f"the {key} page carries the h1 heading(s) {page.h1!r}, where "
                           f"{h1!r} belongs")
        panes: Dict[int, Dict] = {}
        for pane in page.panes:
            if not _hiv_pane(pane):
                first = next((r for r in pane["rows"] if len(r) >= 2 and r[0] == "1"), None)
                log.info("ni_mapasalud: the %s page holds a pane %s outside the HIV shape "
                         "(row 1 %r), set aside", key, pane["id"], first)
                continue
            if pane["year"] in panes:
                raise _Refused(f"the {key} page holds two HIV panes for {pane['year']}")
            panes[pane["year"]] = _read_pane(key, pane)
        want = list(range(_FIRST_YEAR, last + 1))
        if sorted(panes) != want:
            raise _Refused(f"the {key} page holds HIV panes for {sorted(panes)}, where "
                           f"{want[0]} to {want[-1]} belong")
        for year in want:
            if (key, year) in _YEAR_LABEL_KNOWN and \
                    panes[year]["year_label"].endswith(str(year)):
                log.info("ni_mapasalud: the %s pane for %d now prints the pane year", key, year)
        got = tuple(panes[y]["cases"] for y in want)
        if got != _EXPECTED[key] and missing:
            raise _Refused(f"{_num(len(missing))} SILAIS captures are not cached, and the {key} "
                           f"Casos Nuevos read {got}, where the values read on 14 October 2026 "
                           f"are {_EXPECTED[key]}")
        if got != _EXPECTED[key]:
            log.warning("ni_mapasalud: the %s Casos Nuevos read %s, where the values read on 14 "
                        "October 2026 are %s. The gates passed, so the rows are emitted", key,
                        got, _EXPECTED[key])
        out[key] = {"admin1": admin1, "h1": h1, "ts": ts, "url": url, "panes": panes}
    silais = [k for k in out if k != _NATIONAL]
    for year in range(_FIRST_YEAR, max(p[6] for p in _PAGES) + 1):
        carried = [k for k in silais if year in out[k]["panes"]]
        total = sum(out[k]["panes"][year]["cases"] for k in carried)
        nat = out[_NATIONAL]["panes"][year]["cases"]
        if year in _FULL_YEARS and not missing:
            if len(carried) != len(silais):
                raise _Refused(f"only {_num(len(carried))} SILAIS pages carry {year}")
            gap = _SHORTFALL.get(year, 0)
            if nat - total != gap:
                want_gap = f"a difference of {_num(gap)}" if gap else "no difference"
                raise _Refused(f"the 19 SILAIS sum to {total:,} in {year}, against {nat:,} on "
                               f"the national page, where {want_gap} belongs")
        elif total > nat:
            raise _Refused(f"the {_num(len(carried))} SILAIS pages carrying {year} sum to "
                           f"{total:,}, "
                           f"above the {nat:,} on the national page")
        out[_NATIONAL]["panes"][year]["silais_sum"] = (len(carried), total)
    if missing:
        out[_NATIONAL]["missing"] = missing
        return {_NATIONAL: out[_NATIONAL]}
    return out


class NicaraguaMapaSaludConnector(BaseConnector):
    """Nicaragua MINSA Mapa Nacional de la Salud, notified HIV cases by SILAIS, 2017 to 2023."""

    source_id = "ni_mapasalud"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Nicaragua MINSA Mapa Nacional de la Salud, read from Wayback captures, new HIV "
                   "cases (Casos Nuevos) by SILAIS and nationally, 2017 to 2023 (to-source).")
    country = "NIC"
    # The Wayback Machine answered HTTP 429 (too many requests) to Jason's first run of
    # 14 October 2026 at a pause of 1.5 seconds and gave up on the fifth capture after waits of 2,
    # 4, 8 and 16 seconds. Jason's second run paused six seconds after every capture and waited 30,
    # 60, 120 and 120 seconds after a 429, downloaded four more captures and gave up on the ninth
    # capture, Jinotega. The connector now pauses 20 seconds after every capture, three requests a
    # minute, tries a capture eight times, and waits 60, 120, 240 and then 300 seconds after a 429.
    # Jason's third run downloaded Jinotega and Las Minas, and the León capture then drew two 429
    # answers, a 60-second read timeout and five DNS failures ("Failed to resolve
    # 'web.archive.org'"), after which the base waits of 8, 16 and 30 seconds ran out. A network
    # error now takes the same waits as a 429. Jason's fourth run downloaded León after two 429
    # answers, and the Madriz capture then drew seven 429 answers and one dropped connection over
    # eight attempts and 27 minutes of waits. The yield fell from four captures a run
    # to one, so the refusal outlasts the gaps between runs, and retries every five minutes did not
    # end the refusal. The connector now pauses 30 seconds after every capture, tries a capture four
    # times, and waits 10, 15 and 15 minutes after a 429 or a network error, so a refused capture
    # costs four requests in 40 minutes. The fifth, sixth and seventh runs (22 and 25 October 2026)
    # made nine retries after waits of 10 and 15 minutes, and no retry came through, while the
    # vu_mics download of 25 October 2026 came through after one wait of 10 minutes. The
    # connector now tries a capture twice with one wait of 10 minutes, so a refused capture costs
    # two requests in 10 minutes. No wait follows the last attempt, because the run stops there.
    # The sixth, eighth and ninth runs (25, 26 and 27 October 2026) downloaded the captures of
    # Madriz, Managua and Masaya, a single capture in every run. Madriz and Managua came with the
    # first request of the run, and Masaya came on the retry after a wait of 10 minutes. The next
    # capture then drew HTTP 429 on every attempt. The fifth to ninth runs made 12 retries, and 11
    # retries were refused. Jason ended the reruns on 27 October 2026. The connector now requests a
    # missing capture once with no retry, ends the downloads of the run at the first failure, and
    # emits the national rows from the cached captures under the gates of a partial run, so a
    # refused capture costs one request and no wait.
    request_pause = 30.0

    def __init__(self, raw_dir: str = "data/raw/nicaragua_mapasalud", **kw):
        kw.setdefault("max_retries", 1)
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        self._differs: List[str] = []

    def _retry_wait(self, attempt: int, status: Optional[int]) -> float:
        if attempt >= self.max_retries:
            return 0
        if status in (429, None):
            return 600
        return super()._retry_wait(attempt, status)

    def _page(self, key: str, ts: str, url: str, known: Tuple[int, str],
              download: bool = True) -> Optional[str]:
        """Local copy of one capture, downloading only if not cached. None when the capture is
        not cached and `download` is off."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / f"{key}_{ts}.html"
        if path.exists():
            log.info("ni_mapasalud: using cached %s", path)
        elif not download:
            log.info("ni_mapasalud: the %s capture of %s is not cached and is not requested in "
                     "this run", key, ts)
            return None
        else:
            capture = _WAYBACK.format(ts=ts, url=url)
            blob = self._request("GET", capture).content
            if not blob.lstrip()[:15].lower().startswith(b"<!doctype html"):
                raise RuntimeError(f"{capture} did not return an HTML page (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("ni_mapasalud: downloaded the %s capture of %s (%d bytes) -> %s", key, ts,
                     len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) != known:
            self._differs.append(key)
            log.warning("ni_mapasalud: the %s capture differs from the copy read on 14 October "
                        "2026 (%d bytes, sha256 %s, expected %d bytes, %s). The table gates "
                        "still run", key, len(blob), digest[:12], *known)
        return blob.decode("utf-8")

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
        last = max(p[6] for p in _PAGES)
        if end_year < _FIRST_YEAR or start_year > last:
            return
        self._differs = []
        pages: Dict[str, str] = {}
        download = True
        for key, _a, _h, ts, url, known, _l in _PAGES:
            try:
                text = self._page(key, ts, url, known, download)
            except Exception as exc:
                log.warning("ni_mapasalud: the %s capture could not be fetched or read (%s), so "
                            "no other capture is requested in this run", key, exc)
                download = False
                continue
            if text is not None:
                pages[key] = text
        missing = [p[0] for p in _PAGES if p[0] not in pages]
        if missing:
            log.warning("ni_mapasalud: %d of the %d captures are not cached (%s), so only the "
                        "national rows can pass, under the gates of a partial run",
                        len(missing), len(_PAGES), ", ".join(missing))
        try:
            table = _parse(pages, self._differs)
        except _Refused as exc:
            log.warning("ni_mapasalud: the mapasalud pages refused because %s", exc)
            return
        except Exception as exc:
            log.warning("ni_mapasalud: the mapasalud pages failed to parse (%s)", exc)
            return
        emitted = 0
        for row in self._rows(table):
            if start_year <= row.year <= end_year:
                emitted += 1
                yield row
        log.info("ni_mapasalud: emitted %d rows", emitted)

    def _rows(self, table: Dict[str, Dict]) -> Iterator[PanelRow]:
        nat = table[_NATIONAL]["panes"]
        missing = table[_NATIONAL].get("missing", [])
        names = [a[len("SILAIS "):] if a.startswith("SILAIS ") else a
                 for k, a, *_ in _PAGES if k in missing]
        reading = "in the reading of all 20 captures on 14 October 2026, " if missing else ""
        partial = (f". In this run {_num(len(missing))} SILAIS captures are not cached "
                   f"({', '.join(names)}), and every cached capture matches the size and sha256 "
                   "of the copy read on 14 October 2026" if missing else "")
        for key in sorted(k for k in table if k != _NATIONAL) + [_NATIONAL]:
            page = table[key]
            for year, pane in sorted(page["panes"].items()):
                extra: Dict = {
                    "page_url": page["url"],
                    "capture_url": _WAYBACK.format(ts=page["ts"], url=page["url"]),
                    "captured": f"{page['ts'][:4]}-{page['ts'][4:6]}-{page['ts'][6:8]}",
                    "pane_id": pane["id"],
                    "year_label_printed": pane["year_label"],
                    "footnote": pane["footnote"],
                    "source_row": pane["row_printed"],
                    "other_rows_printed": pane["others"],
                    "admin1_source_label": page["h1"],
                    "definition": ("new HIV cases of the year (Casos Nuevos) recorded by the "
                                   "MINSA epidemiological surveillance system, as printed on "
                                   "the mapasalud page. The page gives no definition and does "
                                   "not say whether a case is placed by residence or by the "
                                   "SILAIS making the diagnosis"),
                    "other_rows_note": ("the other 10 rows of the table travel as printed and "
                                        f"are not emitted, held for a decision ({_NOTES})"),
                }
                if pane["year_label"] != f"Año {year}" and pane["year_label"] != f"Años {year}":
                    extra["year_label_note"] = (
                        f"the header prints {pane['year_label']!r} over the pane {pane['id']}. "
                        "The pane id gives the year, and the 19 SILAIS sum exactly to the "
                        f"national page for {year} with the pane read as {year}")
                if year in _FULL_YEARS:
                    gap = _SHORTFALL.get(year, 0)
                    total = _expected_sum(year)[1] if missing else nat[year]["silais_sum"][1]
                    extra["sum_check"] = reading + (
                        f"the 19 SILAIS sum exactly to the national {nat[year]['cases']:,} in "
                        f"{year}" if not gap else
                        f"the 19 SILAIS sum to {total:,} in {year}, {gap} cases short of the "
                        f"national {nat[year]['cases']:,}. The captures of June 2022 print the "
                        "same values as the later captures, so the shortfall stands in the "
                        f"source ({_NOTES})") + partial
                if key == _NATIONAL:
                    n, total = _expected_sum(year) if missing else pane["silais_sum"]
                    if year not in _FULL_YEARS:
                        extra["silais_coverage"] = reading + (
                            f"the archived SILAIS pages carry {year} for {_num(n)} of the 19 "
                            "SILAIS, "
                            f"{total:,} of the {pane['cases']:,} national cases") + partial
                    if missing:
                        extra["silais_not_cached"] = names
                        extra["silais_rows_note"] = (
                            "no SILAIS row is emitted in this run, because the gates of a SILAIS "
                            "row join all 19 SILAIS pages")
                    extra["reconcile_with"] = _PAHO_NOTE[year]
                else:
                    municipalities = _MUNICIPALITIES[key]
                    extra["silais_municipalities"] = sorted(
                        m for ms in municipalities.values() for m in ms)
                    extra["departments_covered"] = {d: list(ms) for d, ms in
                                                    municipalities.items()}
                    extra["admin1_note"] = _admin1_note(page["admin1"], municipalities)
                    extra["reconcile_with"] = (
                        "none. pepfar_snu holds Nicaraguan department rows of new_diagnoses and "
                        "on_art_count, counts at donor-supported sites, which are never "
                        "compared with notified cases (Jason's ruling of 8 October 2026)")
                yield self.make_row(
                    country_iso3="NIC", country_name="Nicaragua",
                    indicator_id="notified_hiv_cases", year=year, value=pane["cases"],
                    unit="count", admin1=page["admin1"],
                    source_url=page["url"],
                    source_indicator_code=f"mapasalud.{key}.{pane['id'].lower()}.casos_nuevos",
                    extra=extra,
                )


def _num(n: int) -> str:
    return _WORDS[n] if 0 < n < 10 else f"{n:,}"


def _admin1_note(admin1: str, municipalities: Dict[str, Tuple[str, ...]]) -> str:
    n = sum(len(ms) for ms in municipalities.values())
    if not admin1.startswith("SILAIS "):
        (dept,) = municipalities
        return (f"the SILAIS covers all {_num(n)} municipalities of the {dept} department and "
                "nothing else, so the SILAIS and the department cover the same area")
    parts = []
    for dept, ms in municipalities.items():
        size = _DEPARTMENT_SIZE[dept]
        parts.append(f"{_num(len(ms))} of the {_num(size)} municipalities of {dept}"
                     + (" (all)" if len(ms) == size else f" ({', '.join(ms)})"))
    return (f"{admin1} crosses department lines and covers {_num(n)} municipalities, "
            + " and ".join(parts) + ". No department count can be rebuilt from the SILAIS rows")


_PAHO_NOTE = {
    year: (f"paho_core holds the national {year} row from PAHO Core Indicator 93, reported by "
           f"the same ministry, at {paho:,} cases"
           + (", the same value" if paho == ours else
              f", {abs(paho - ours)} {'more' if paho > ours else 'fewer'} than the {ours:,} on the "
              "mapasalud page. The paho_core row and the mapasalud row stay separate and are not "
              "merged")
           + ". Never compare with new_diagnoses (Jason's ruling of 8 October 2026)")
    for year, paho, ours in ((2017, 959, 1033), (2018, 1102, 1102), (2019, 1118, 1118),
                             (2020, 970, 953), (2021, 938, 938), (2022, 1141, 1129),
                             (2023, 1164, 1155))
}
