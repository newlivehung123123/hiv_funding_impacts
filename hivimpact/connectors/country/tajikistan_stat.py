"""
Tajikistan, people newly registered with HIV by sex and age, from the health compendium of the
Agency on Statistics under the President of the Republic of Tajikistan, connector 71.

Source. The compendium "Здравоохранение в Республике Таджикистан / Тандурустӣ дар Ҷумҳурии
Тоҷикистон" (Health care in the Republic of Tajikistan), Agency on Statistics, 2019, 85 pages, is
linked from the medical statistics page of the Ministry of Health and Social Protection of the
Population (https://moh.tj/omori-tibbi/) and sits at
https://moh.tj/wp-content/uploads/2024/12/Statistika-2018-2019-Agenstvo.pdf, with a byte-identical
copy under https://moh.tj/wp-content/uploads/2024/10/. The file was read on 22 October 2026. No
sign-in and no key. The connector downloads the file once into `raw_dir`, every later run reads
the cached copy, and the connector reads the pdfplumber text layer of page 32 with no optical
character recognition.

Table read. Page 32, "Количество ВИЧ - инфицированных по полу и возрасту" (number of people
infected with HIV by sex and age), "Взято на учёт с диагнозом, установленным впервые" (registered
with a diagnosis made for the first time), for 2014 to 2018. The page prints three blocks, all
people (Њамагї, Всего), men (мардњо, мужчины) and women (занњо, женщины), and every block prints
a total row and seven age rows, 0-14, 15-19, 20-29, 30-39, 40-49, 50-59 and 60 and over.

Gates. The compendium enters only when every check below passes, because two printed figures
disagreeing leave the true figure unknown.
  The page prints the table caption, the registration line and the year header 2014 to 2018.
  The three block headings print exactly once and in the order all people, men, women.
  Every block prints the total row exactly once and every age row exactly once.
  The seven age rows add to the block total in every year.
  Men plus women equal the all-people count in every row and every year.

What the connector emits. notified_hiv_cases, national rows for 2014 to 2018, sex "male" and
"female" with age group "all" (10 rows), sex "all" by age group (35 rows), and sex "male" and
"female" by age group (70 rows), 115 rows in all. The age group of the oldest row is written
"60+". No row for all people of all ages is written, because ecdc_hiv_report and who_europe_hfa
carry the national count, and the printed total goes to extra.national_total_printed. The totals
for 2014 to 2017 (1,008, 1,146, 1,040 and 1,207) equal the Republic totals of the tj_moh
yearbooks. The 2015 total sits three cases below ecdc_hiv_report and who_europe_hfa (1,149),
the 2016 and 2017 totals sit two cases above (1,038 and 1,205), the 2018 total sits a single
case above (1,421), and the 2014 total sits 22 cases above who_europe_hfa (986). No other source carries a Tajik split by sex or age.

Not carried (ruling R59).
  Page 33, pregnant women with HIV infection by region (99, 89, 75, 60 and 77 for 2014 to 2018).
  The panel holds no routine indicator for registered pregnant women with HIV, the modelled
  pregnant_women_hiv follows a different definition, and the page does not say whether the count
  covers new diagnoses alone or every pregnant woman followed.
  Page 33, AIDS cases of 2018 by sex and region, under ruling R55, because the Republic count
  (162) differs from ecdc_hiv_report (212) and from who_europe_hfa (207).

Source type. routine_programme_record, the case register of the national HIV programme as the
Agency on Statistics publishes the register.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_URL = "https://moh.tj/wp-content/uploads/2024/12/Statistika-2018-2019-Agenstvo.pdf"
_SIZE, _PREFIX = 2_217_367, "c8700f2d8068"   # the copy read on 22 October 2026
_PAGE = 32
_YEARS = (2014, 2015, 2016, 2017, 2018)

# block -> heading pattern (the compendium prints the legacy Tajik glyphs њ, ї, љ)
_BLOCKS = {
    "all": r"Њамагї – Всего",
    "male": r"мардњо – мужчины",
    "female": r"занњо – женщины",
}
# age group -> pattern of the row label ahead of the five figures
_AGES = {
    "0-14": r"0-14",
    "15-19": r"15-19",
    "20-29": r"20-29",
    "30-39": r"30-39",
    "40-49": r"40- ?49",
    "50-59": r"50-59",
    "60+": r"60 сола 60 лет(?: и)?\s+ва калонтар",
}
_FIVE = r" (\d+) (\d+) (\d+) (\d+) (\d+) "

_DEFINITION = ("People newly registered with HIV in the year in Tajikistan, by sex and age, the "
               "table \"Количество ВИЧ - инфицированных по полу и возрасту\" (registered with a "
               "diagnosis made for the first time) of the Agency on Statistics health compendium "
               "of 2019, page 32")
_RECONCILE = ("No other source carries a Tajik split by sex or age. The printed totals for 2014 "
              "to 2017 equal the Republic totals of tj_moh. The 2015 total sits three cases "
              "below ecdc_hiv_report and who_europe_hfa, the 2016 and 2017 totals sit two "
              "cases above, the 2018 total sits a single case above, and the 2014 total sits "
              "22 cases above who_europe_hfa. Never "
              "compare with new_diagnoses (Jason's ruling of 8 October 2026)")
_NOT_CARRIED = ("page 33, pregnant women with HIV infection by region (no routine indicator, "
                "ruling R59), and page 33, AIDS cases of 2018 by sex and region (162 against 212 "
                "in ecdc_hiv_report, ruling R55)")


def _row(block: str, label: str, what: str) -> List[int]:
    """The five figures of the row `label` in `block`. Raises ValueError unless the row prints
    exactly once."""
    found = re.findall(r"(?m)^" + label + _FIVE, block + " ")
    if len(found) != 1:
        raise ValueError(f"{what}: the row {label!r} prints {len(found)} times, expected once")
    return [int(v) for v in found[0]]


def parse_page(page_text: str) -> Dict[str, Dict[str, List[int]]]:
    """{block: {"total": [five figures], age group: [five figures]}} from the text of page 32,
    after the gates of the module docstring. Raises ValueError when a gate fails."""
    what = "the 2019 compendium, page 32"
    text = re.sub(r"[ \t]+", " ", page_text)
    if "Количество ВИЧ - инфицированных по полу и возрасту" not in text:
        raise ValueError(f"{what}: the page does not print the caption on HIV by sex and age")
    if not re.search(r"Взято на уч.т с диагнозом, установленным впервые", text):
        raise ValueError(f"{what}: the page does not print the line on first diagnoses")
    if len(re.findall(r"(?m)^2014 2015 2016 2017 2018$", text)) != 1:
        raise ValueError(f"{what}: the page does not print the year header 2014 to 2018 once")
    starts = []
    for name, heading in _BLOCKS.items():
        found = [m.start() for m in re.finditer(heading, text)]
        if len(found) != 1:
            raise ValueError(f"{what}: the heading of the {name} block prints {len(found)} "
                             f"times, expected once")
        starts.append(found[0])
    if starts != sorted(starts):
        raise ValueError(f"{what}: the block headings print out of order")
    bounds = starts[1:] + [len(text)]
    out: Dict[str, Dict[str, List[int]]] = {}
    for (name, _), a, b in zip(_BLOCKS.items(), starts, bounds):
        block = text[a:b]
        rec = {"total": _row(block, r"Њамагї", what)}
        for age, label in _AGES.items():
            rec[age] = _row(block, label, what)
        for k, year in enumerate(_YEARS):
            added = sum(rec[age][k] for age in _AGES)
            if added != rec["total"][k]:
                raise ValueError(f"{what}: the age rows of the {name} block add to {added} for "
                                 f"{year}, against the printed total {rec['total'][k]}")
        out[name] = rec
    for key in ["total", *_AGES]:
        for k, year in enumerate(_YEARS):
            men, women, every = out["male"][key][k], out["female"][key][k], out["all"][key][k]
            if men + women != every:
                raise ValueError(f"{what}: men ({men}) plus women ({women}) do not equal all "
                                 f"people ({every}) in the {key} row for {year}")
    return out


class TajikistanStatConnector(BaseConnector):
    """Sex and age table of the Tajik Agency on Statistics health compendium of 2019."""

    source_id = "tj_stat"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Agency on Statistics under the President of the Republic of Tajikistan, "
                   "health compendium of 2019, people newly registered with HIV by sex and age "
                   "for 2014 to 2018 (to-source).")
    country = "TJK"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/tj_stat", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self) -> Path:
        """Local copy of the compendium, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / "tj_stat_health_compendium_2019.pdf"
        if path.exists():
            log.info("tj_stat: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_URL} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("tj_stat: downloaded the compendium (%d bytes) -> %s", len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (_SIZE, _PREFIX):
            log.info("tj_stat: the compendium matches the copy read on 22 October 2026 "
                     "(sha256 %s)", digest[:12])
        else:
            log.warning("tj_stat: the compendium differs from the copy read on 22 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes), and the gates still run",
                        len(blob), digest[:12], _SIZE)
        return path

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
            import pdfplumber
        except ImportError:
            log.error("tj_stat: pdfplumber not installed (pip install pdfplumber)")
            return
        try:
            with pdfplumber.open(str(self._pdf_path())) as pdf:
                text = pdf.pages[_PAGE - 1].extract_text() or ""
            table = parse_page(text)
        except Exception as exc:
            log.warning("tj_stat: the compendium failed (%s), no row emitted", exc)
            return
        emitted = 0
        for k, year in enumerate(_YEARS):
            if not start_year <= year <= end_year:
                continue
            for sex in ("all", "male", "female"):
                for age in ["total", *_AGES]:
                    if sex == "all" and age == "total":
                        continue
                    age_group = "all" if age == "total" else age
                    emitted += 1
                    yield self.make_row(
                        country_iso3="TJK", country_name="Tajikistan",
                        indicator_id="notified_hiv_cases", year=year,
                        value=float(table[sex][age][k]), unit="count",
                        population_group="all", sex=sex, age_group=age_group,
                        source_url=_URL,
                        source_indicator_code=f"tj_stat_2019:p{_PAGE}:{sex}:{age_group}",
                        extra={"definition": _DEFINITION,
                               "report": (f"Agency on Statistics, Здравоохранение в Республике "
                                          f"Таджикистан, 2019, page {_PAGE}"),
                               "national_total_printed": table["all"]["total"][k],
                               "reconcile_with": _RECONCILE,
                               "not_carried": _NOT_CARRIED},
                    )
        log.info("tj_stat: emitted %d rows", emitted)
