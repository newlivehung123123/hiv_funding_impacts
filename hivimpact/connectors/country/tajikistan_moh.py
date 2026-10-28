"""
Tajikistan, people newly registered with HIV by region, from the HIV table of the annual
health yearbook of the Ministry of Health and Social Protection of the Population of the Republic
of Tajikistan, connector 70.

Source. The yearbooks "Солимии аҳолӣ ва фаъолияти муассисаҳои тандурустӣ дар соли <year>"
(Health of the population and activity of health institutions in <year>) are linked from the
medical statistics page of the ministry (https://moh.tj/omori-tibbi/) and sit under
https://moh.tj/wp-content/uploads/2024/10/. The files were read on 21 October 2026. The same page
links the HIV chapter of the yearbook for 2017 as a Word 97 file (11.-VNMO.doc, "11. ВНМО"), read
on 22 October 2026. No sign-in and no key. The connector downloads every file once into `raw_dir`,
every later run reads the cached copies, and the connector reads the pdfplumber text layer of the
PDF files and the text of the Word file (module _msdoc, which keeps the cell boundaries of a Word
table) with no optical character recognition.

Table read. The table "Сироятёбӣ ба ВНМО ва беморшавӣ ба БПНМ" (HIV infection and AIDS
morbidity), column "Шумораи сироятёфтагон бо ВНМО, ҳамагӣ" (people infected with HIV, all), for
the yearbook's own year. The 2021 yearbook prints the table as Table 63 on page 317. The 2014,
2015 and 2016 yearbooks print the table as Table 129 on page 349, Table 129 on page 338 and
Table 64 on page 318, where the page is turned and the text layer runs backwards, and the
connector therefore reverses the text of the turned pages before reading. The 2017 chapter prints
the table as Table 63, followed by the district tables 63.1 to 63.3, and the connector reads Table
63 alone. The rows are the five first-level units, Dushanbe city, the Districts of Republican
Subordination (ШНТҶ), Sughd region, Khatlon region and the Gorno-Badakhshan Autonomous Region
(ВМКБ), with the Republic total (Ҷумҳурӣ).

Gates. A yearbook enters only when every check below passes, because two printed figures
disagreeing leave the true figure unknown.
  The page prints the table caption and the two year headers of the table.
  Every region label and the Republic label print exactly once on the page.
  The five regions add to the Republic total in the earlier year column and in the own column.
  The district rows of the Districts of Republican Subordination add to the ШНТҶ row in the
  earlier year column and in the own column, where a printed double dash counts as zero, and a
  printed single hyphen (the 2017 Lakhsh row) counts as zero too, the sign the yearbooks use for
  no case.
  When the yearbook of the next year is read too, the earlier column of the next yearbook equals
  the yearbook's own column in every region, and a year whose two printings disagree enters with
  no row.

What the connector emits. notified_hiv_cases, admin1 rows for the five units, sex "all", for the
yearbook's own year only (2014, 2015, 2016, 2017 and 2021). The admin1 names follow the
pepfar_snu names (Dushanbe, Districts of Republican Subordination, Sughd Oblast, Khatlon Oblast,
GBAO). The
Republic total goes to extra.national_total_printed, and no national row is written, because
ecdc_hiv_report and who_europe_hfa carry the national count. The Republic total equals
ecdc_hiv_report for 2021 (922), sits two cases above ecdc_hiv_report and who_europe_hfa for 2017
(1,207 against 1,205) and for 2016 (1,040 against 1,038), sits three cases below for 2015 (1,146
against 1,149), and sits 22 cases above who_europe_hfa for 2014 (1,008 against 986). The earlier
column of the 2015, 2016 and 2017 yearbooks equals the own column of the 2014, 2015 and 2016
yearbooks in every region.

Not carried (ruling R55).
  The earlier year column of every yearbook. The 2021 yearbook prints 1,397 people for 2020,
  against 1,083 in ecdc_hiv_report, and the gap of 314 matches the excess of the Dushanbe row
  (460 for 2020 against 141 for 2021). The 2020 column therefore fails the accuracy test, and no 2020
  yearbook is published on the ministry page.
  The district rows, a second administrative level.
  The rates per 100,000 people, the AIDS columns (200 in 2016, 180 in 2017, 86 in 2020 and 76 in
  2021, against 237, 264, 110 and 130 in ecdc_hiv_report), the treatment columns and the deaths,
  which fall under the Fiji deaths ruling.

Source type. routine_programme_record, the case register of the national HIV programme.
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType
from ._msdoc import doc_text

log = logging.getLogger("hivimpact")

_BASE = "https://moh.tj/wp-content/uploads/2024/10/"

# yearbook year -> (file name on moh.tj, size, sha256 prefix of the copy read on 21 or 22 October
# 2026, page of the HIV table (None for the Word file), table number, True when the page is turned
# and the text runs backwards)
_FILES = {
    2014: ("SOLIMII-ANOL-VA-FAOLIYATI-MUASSISANOI-TANDURUST-DAR-SOLI-2014.pdf", 30_189_532,
           "b2e5284bc7e3", 349, 129, True),
    2015: ("SOLIMII-ANOL-VA-FAOLIYATI-MUASSISANOI-TANDURUST-DAR-SOLI-2015.pdf", 6_527_393,
           "c7b61772cdf4", 338, 129, True),
    2016: ("SOLIMII-ANOL-VA-FAOLIYATI-MUASSISANOI-TANDURUST-DAR-SOLI-2016.pdf", 9_598_396,
           "df7b11c6ff8d", 318, 64, True),
    2017: ("11.-VNMO.doc", 255_488, "f649a6d50fcb", None, 63, False),
    2021: ("SOLIMII-ANOL-VA-FAOLIYATI-MUASSISANOI-TANDURUST-DAR-SOLI-2021.pdf", 8_102_859,
           "1aac2c17283f", 317, 63, False),
}
_MAGIC = {".pdf": b"%PDF", ".doc": bytes.fromhex("D0CF11E0A1B11AE1")}

# admin1 name -> label pattern of the row (the yearbooks print the legacy Tajik glyphs ѓ, љ, њ, ї)
_REGIONS = {
    "Dushanbe": r"ш\. ?Душанбе",
    "Districts of Republican Subordination": r"Ш?НТЉ",
    "Sughd Oblast": r"(?:Вил\. ?|Вилояти )?Суѓд",
    "Khatlon Oblast": r"(?:Вил\. ?)?Хатлон",
    "GBAO": r"ВМКБ",
}
_REPUBLIC = r"Љумњурї"
_FIG = r"(\d+|––|-)"

_DEFINITION = ("People newly registered with HIV in the year by the national HIV programme of "
               "Tajikistan, by region, the column \"Шумораи сироятёфтагон бо ВНМО, ҳамагӣ\" of "
               "the HIV table of the Ministry of Health yearbook for the same year")
_RECONCILE = ("No other source carries notified_hiv_cases for Tajik regions. The five regions add "
              "to the Republic total, which equals ecdc_hiv_report for 2021, sits two cases "
              "above ecdc_hiv_report for 2016 and three below for 2015, and sits 22 cases above "
              "who_europe_hfa for 2014. The 2017 total sits two cases above ecdc_hiv_report "
              "and who_europe_hfa. Never compare with new_diagnoses (Jason's ruling of "
              "8 October 2026), which pepfar_snu carries for PEPFAR-supported sites only")
_NOT_CARRIED = ("the earlier year column of every yearbook (the 2020 column of the 2021 yearbook "
                "prints 1,397 against 1,083 in ecdc_hiv_report, ruling R55), the district rows, "
                "the rates per 100,000 people, the AIDS, treatment and death columns")


def _num(tok: str) -> int:
    return 0 if tok in ("––", "-") else int(tok)


def doc_table(doc: str, table: int) -> str:
    """The text of Table `table` of the Word chapter, from the table caption to the caption of the
    next table, with every cell mark turned into a space. Raises ValueError unless the caption
    prints exactly once."""
    text = doc.replace("\x07", " ")
    found = list(re.finditer(rf"Љадвали\s+{table}(?![\d.])", text))
    if len(found) != 1:
        raise ValueError(f"the Word chapter prints the caption of Table {table} {len(found)} "
                         f"times, expected once")
    start = found[0].start()
    nxt = re.search(r"Љадвали", text[found[0].end():])
    return text[start:found[0].end() + nxt.start()] if nxt else text[start:]


def _once(text: str, label: str, what: str) -> Tuple[int, int, Tuple[int, int]]:
    """(earlier column, own column, span) of the row `label`. Raises ValueError unless the label
    prints exactly once."""
    found = list(re.finditer(r"(?<!\w)" + label + " " + _FIG + " " + _FIG + " ", text))
    if len(found) != 1:
        raise ValueError(f"{what}: the row {label!r} prints {len(found)} times, expected once")
    m = found[0]
    return _num(m.group(1)), _num(m.group(2)), m.span()


def parse_page(page_text: str, year: int, table: int, turned: bool) -> Dict[str, object]:
    """{"regions": {admin1: (earlier, own)}, "republic": (earlier, own)} from the text of the
    HIV table page, after the gates of the module docstring. Raises ValueError when a gate fails."""
    text = page_text[::-1] if turned else page_text
    text = re.sub(r"\s+", " ", text).strip()
    what = f"the {year} yearbook"
    if not re.search(rf"Љадвали {table}(?!\d)", text) or "ВНМО" not in text or "БПНМ" not in text:
        raise ValueError(f"{what}: the page does not print Table {table} on HIV and AIDS")
    if not re.search(rf"(?<!\d){year - 1}[сc]?\.? {year}[сc]?\.?(?!\d)", text):
        raise ValueError(f"{what}: the page does not print the year headers {year - 1} and {year}")
    regions: Dict[str, Tuple[int, int]] = {}
    spans: Dict[str, Tuple[int, int]] = {}
    for name, label in _REGIONS.items():
        earlier, own, span = _once(text, label, what)
        regions[name], spans[name] = (earlier, own), span
    rep_earlier, rep_own, _ = _once(text, _REPUBLIC, what)
    for col, total in ((0, rep_earlier), (1, rep_own)):
        added = sum(v[col] for v in regions.values())
        if added != total:
            raise ValueError(f"{what}: the regions add to {added} in column {col + 1}, against "
                             f"the Republic total {total}")
    # district rows between the ШНТҶ row and the Sughd row (the turned page runs backwards, so
    # the Sughd row comes first there)
    drs = "Districts of Republican Subordination"
    a, b = spans[drs], spans["Sughd Oblast"]
    between = text[a[1]:b[0]] if a[1] <= b[0] else text[b[1]:a[0]]
    districts = re.findall(r"(?:ш|н)\. ?[^\d–]+? " + _FIG + " " + _FIG + " ", between)
    if not districts:
        raise ValueError(f"{what}: no district row under the Districts of Republican "
                         f"Subordination")
    for col in (0, 1):
        added = sum(_num(d[col]) for d in districts)
        if added != regions[drs][col]:
            raise ValueError(f"{what}: the {len(districts)} districts add to {added} in column "
                             f"{col + 1}, against {regions[drs][col]}")
    return {"regions": regions, "republic": (rep_earlier, rep_own),
            "districts": len(districts)}


def own_years(parsed: Dict[int, Dict[str, object]]) -> Dict[int, Dict[str, object]]:
    """The yearbooks whose own column agrees with the earlier column of the next yearbook, when
    the next yearbook is read too."""
    out = {}
    for year, rec in parsed.items():
        nxt = parsed.get(year + 1)
        if nxt is not None:
            clash = [n for n, v in rec["regions"].items() if nxt["regions"][n][0] != v[1]]
            if clash:
                log.warning("tj_moh: the %d and %d yearbooks print different %d counts for %s, "
                            "no row emitted for %d", year, year + 1, year, ", ".join(clash), year)
                continue
        out[year] = rec
    return out


class TajikistanMoHConnector(BaseConnector):
    """HIV table of the Tajik Ministry of Health yearbooks for 2014 to 2017 and 2021, by region."""

    source_id = "tj_moh"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Ministry of Health and Social Protection of the Population of the Republic "
                   "of Tajikistan, health yearbooks for 2014, 2015, 2016, 2017 and 2021, people "
                   "newly registered with HIV by region (to-source).")
    country = "TJK"
    timeout = 300

    def __init__(self, raw_dir: str = "data/raw/tj_moh", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _file_path(self, year: int) -> Path:
        """Local copy of the `year` yearbook, downloading only if not cached."""
        name, size, prefix = _FILES[year][:3]
        url = _BASE + name
        suffix = Path(name).suffix
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / f"tj_moh_yearbook_{year}{suffix}"
        if path.exists():
            log.info("tj_moh: using cached %s", path)
        else:
            blob = self._request("GET", url).content
            if not blob.startswith(_MAGIC[suffix]):
                raise RuntimeError(f"{url} did not return a {suffix} file (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("tj_moh: downloaded the %d yearbook (%d bytes) -> %s", year, len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == (size, prefix):
            log.info("tj_moh: the %d yearbook matches the copy read in October 2026 "
                     "(sha256 %s)", year, digest[:12])
        else:
            log.warning("tj_moh: the %d yearbook differs from the copy read in October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes), and the gates still run",
                        year, len(blob), digest[:12], size)
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
            log.error("tj_moh: pdfplumber not installed (pip install pdfplumber)")
            return
        parsed: Dict[int, Dict[str, object]] = {}
        for year in sorted(_FILES):
            if not start_year <= year <= end_year + 1:
                continue
            _, _, _, page, table, turned = _FILES[year]
            try:
                path = self._file_path(year)
                if page is None:
                    text = doc_table(doc_text(path.read_bytes()), table)
                else:
                    with pdfplumber.open(str(path)) as pdf:
                        text = pdf.pages[page - 1].extract_text() or ""
                parsed[year] = parse_page(text, year, table, turned)
            except Exception as exc:
                log.warning("tj_moh: the %d yearbook failed (%s), no row emitted for %d",
                            year, exc, year)
        emitted = 0
        for year, rec in sorted(own_years(parsed).items()):
            if not start_year <= year <= end_year:
                continue
            name, _, _, page, table, _ = _FILES[year]
            for admin1, (_, own) in rec["regions"].items():
                emitted += 1
                yield self.make_row(
                    country_iso3="TJK", country_name="Tajikistan", admin1=admin1,
                    indicator_id="notified_hiv_cases", year=year, value=float(own),
                    unit="count", population_group="all", sex="all", age_group="all",
                    source_url=_BASE + name,
                    source_indicator_code=f"tj_moh_{year}:Table {table}:{admin1}",
                    extra={"definition": _DEFINITION,
                           "report": (f"Ministry of Health yearbook for {year}, Table {table}, "
                                      f"page {page}" if page is not None else
                                      f"Ministry of Health yearbook for {year}, chapter XI "
                                      f"(Word file {name}), Table {table}"),
                           "national_total_printed": rec["republic"][1],
                           "reconcile_with": _RECONCILE,
                           "not_carried": _NOT_CARRIED},
                )
        log.info("tj_moh: emitted %d rows", emitted)
