"""
Lebanon, Ministry of Public Health statistical bulletins, with HIV cases notified to the National
AIDS Program by sex and people newly started on ART, 2007 to 2018 (to-source, routine programme,
national).

The Lebanese Ministry of Public Health (MoPH) publishes a Statistical Bulletin for every year from
2006 to 2018 on www.moph.gov.lb, under Statistics, Statistical Bulletins, and serves every
bulletin as a PDF at /en/DynamicPages/page_download_file/<id>. Every bulletin from 2007 prints one
table of the cases reported to the National AIDS Program (NAP) of the ministry during the year,
with the stage of disease (HIV, AIDS, not specified), sex, age group, mode of transmission and,
from 2013, the people newly started on antiretroviral therapy (ART). The connector reads seven
bulletins, downloads every bulletin once into `raw_dir`, and every later run reads the cached
copy. A cached copy whose size or sha256 differs from the copy read on 28 October 2026 is logged as
a WARNING and still parsed, because every gate below runs on the table itself.

    year                      2007  2009  2014  2015  2016  2017  2018
    cases notified to NAP       92    97   109   113   108   205   160
    men                         57     .   100    97   100   193   151
    women                       34     .     9    16     8    12     9
    newly started on ART         .     .   114   140   150   186     .

WHAT THE COUNT IS
-----------------
The emitted `notified_hiv_cases` value is the count of HIV cases, AIDS cases included, reported to
the NAP during the year, as the bulletin prints the count. The bulletins of 2014 to 2018 call the
count "estimated incidence" and "incident cases" and print a rate per 100,000 beside the count,
and the count is still a count of reported cases (the 2014 bulletin reads "newly Reported Cases in
2014"). The rate is not carried. The 2017 bulletin says the rate covers the Lebanese population
only. No bulletin says whether the count covers residents of other nationalities, and every row
carries the note in `extra`. The emitted `art_initiations` value is the "New in <year>" figure
under ART.

BULLETINS NOT READ
------------------
  * 2006 has no text layer (a scanned copy), and no OCR figure enters the panel.
  * 2008 prints no NAP table in the text layer.
  * 2010, 2011 and 2013 count cases "up to November" of the year, which is part of a year.
  * 2012 prints the total in glyph codes of an embedded font, which the text layer cannot read.
  * The 2018 ART figure is "New until November in 2018", part of a year, and 2018 gives no
    `art_initiations` row.
  * The 2009 bulletin prints the sexes in per cent only, and 2009 gives the total only.
Every bulletin also prints figures which are not carried, namely the AIDS-only row of Table
A.1 (the panel holds no AIDS-case indicator), the incidence rate, the cumulative counts, age
groups, mode of transmission and sexual behaviour.

PARSING
-------
The table page is found by CAPTION TEXT, "AIDS statistics-2007" in 2007, "Table 10: HIV/AIDS
Incidence in Lebanon, 2009" in 2009 and "Table D.1: HIV/AIDS estimated incidence in Lebanon,
<year>" from 2014, on a page which prints the sexes (Male or Males) and is not the contents
page (the 2009 contents page lists the caption with no heading in the text layer). The caption
year must equal the bulletin year. The text lines of the page are joined with " | ", and every
figure is read by a pattern anchored on the printed label (Males, Females, HIV, AIDS, Not
specified, New in <year>).

INTEGRITY GATES
---------------
  * Exactly one table page in the bulletin, and the year printed beside the total equals the
    bulletin year.
  * HIV, AIDS and not specified sum to the total (2007 and 2014 to 2018), and the 2009 narrative
    count of AIDS cases and HIV cases sums to the total.
  * Men and women (and, in 2007, sex unspecified) sum to the total.
  * Every printed percentage lies within 0.6 points of the count over the total.
Any failed gate refuses the bulletin with a WARNING naming the reason, and the other bulletins
still run. Counts which differ from the table above are logged as a WARNING and still emitted,
because every gate has passed.

LABELS
------
National rows only, admin1 "", sex "all", "male" and "female".

RECONCILIATION
--------------
No other source in the panel held Lebanese `notified_hiv_cases` or `new_diagnoses` rows when the
connector was built (checked 28 October 2026). The `art_initiations` rows meet the aggregator
`art_initiations` rows for Lebanon in reconcile.py.

TAGGING. source_type is routine_programme_record (the NAP case register, per the source line of
every table).
"""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_BASE = "https://www.moph.gov.lb/en/DynamicPages/page_download_file/"
_PAGE_URL = "https://www.moph.gov.lb/en/Pages/8/327/statistical-bulletins"
_NOTES = "research/rulings_2026-10-15.md, Lebanon Ministry of Public Health statistical bulletins"

#: Bulletin year to download id, file name served, and the size and sha256 prefix of the copy
#: read on 28 October 2026.
_EDITIONS: Dict[int, Tuple[int, str, int, str]] = {
    2007: (425, "Statistical_Bulletin_2007.pdf", 5_425_747, "a1f0c75f995d"),
    2009: (427, "Statistical_Bulletin_2009.pdf", 5_183_649, "de7449fd893b"),
    2014: (1611, "STATISTICALBULLETIN2014.pdf", 4_489_248, "c447bb00bf18"),
    2015: (1871, "STATISTICALBULLETIN2015.pdf", 4_307_091, "194a831771c9"),
    2016: (2000, "STATISTICALBULLETIN.2016.pdf", 3_751_074, "8e6a5f32c3f2"),
    2017: (2537, "STATISTICALBULLETIN_2017.pdf", 3_024_802, "14e64ca6b248"),
    2018: (2896, "STATISTICALBULLETIN2018.pdf", 3_020_952, "ccbc0f67a187"),
}

#: The figures of the copies read on 28 October 2026 (total, men, women, newly on ART), checked
#: as a fingerprint only.
_EXPECTED = {
    2007: (92, 57, 34, None), 2009: (97, None, None, None), 2014: (109, 100, 9, 114),
    2015: (113, 97, 16, 140), 2016: (108, 100, 8, 150), 2017: (205, 193, 12, 186),
    2018: (160, 151, 9, None),
}

_CAPTION = re.compile(r"(?:Table D\.1: HIV/AIDS estimated incidence in Lebanon, "
                      r"|Table 10: HIV/AIDS Incidence in Lebanon, |AIDS statistics-)(\d{4})")
_CONTENTS = re.compile(r"(?i)table of contents")
_BODY = re.compile(r"\bMales?\b")
_N_PCT = r"(\d+) ?\((\d+(?:\.\d+)?) ?%?\)"
_TOTAL_D1 = re.compile(r"(?:newly Reported Cases|incident cases) in (\d{4}) is (\d+)")
_STAGES_D1 = re.compile(r"\| HIV " + _N_PCT + r" \| AIDS " + _N_PCT + r" \| Not specified "
                        + _N_PCT + r" \|")
_SEXES_D1 = re.compile(r"\| Males " + _N_PCT + r" \| Females " + _N_PCT + r" \|")
_ART_D1 = re.compile(r"ART \| New in (\d{4}) Cumulative \| (\d+) (\d+) \|")
_TOTAL_2007 = re.compile(r"\| Number of cases (\d+) (\d{4}) \| HIV (\d+) \| AIDS (\d+) \| "
                         r"Unspecified (\d+) \|")
_SEXES_2007 = re.compile(r"\| Gender \(incident cases\) \( \) \| Male (\d+) \| Female (\d+) \| "
                         r"Unspecified (\d+) \|")
_NARRATIVE_2009 = re.compile(r"There are (\d+) new cases of AIDS and (\d+) (\d+) cases HIV "
                             r"reported to the")
_YEAR_2009 = re.compile(r"Number of Reported Cases in (\d{4})")
_STAGES_2009 = re.compile(r"\| HIV (\d+\.\d+)% \| AIDS (\d+\.\d+)%")
_PCT_TOL = 0.6


class _Refused(Exception):
    """A gate failed. The whole bulletin is refused, never part of the bulletin."""


def _check_pct(label: str, n: int, total: int, printed: float) -> None:
    got = 100.0 * n / total
    if abs(got - printed) > _PCT_TOL:
        raise _Refused(f"{label} prints {n} ({printed} per cent), where {n} of {total} is "
                       f"{got:.1f} per cent")


def _table_page(pdf, year: int) -> Tuple[int, str]:
    found: List[Tuple[int, str]] = []
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        if _CONTENTS.search(text) or not _BODY.search(text):
            continue
        years = {int(y) for y in _CAPTION.findall(text)}
        if years:
            if years != {year}:
                raise _Refused(f"page {i + 1} prints a caption for {sorted(years)}, where the "
                               f"bulletin is the bulletin of {year}")
            found.append((i + 1, " | ".join(ln.strip() for ln in text.split("\n") if ln.strip())))
    if len(found) != 1:
        raise _Refused(f"{len(found)} pages carry the NAP table caption, where one belongs")
    return found[0]


def _one(pattern: re.Pattern, text: str, what: str):
    hits = pattern.findall(text)
    if len(hits) != 1:
        raise _Refused(f"{len(hits)} matches for {what}, where one belongs")
    return hits[0]


def _parse(pdf, year: int) -> Dict:
    pno, text = _table_page(pdf, year)
    out: Dict = {"page": pno, "male": None, "female": None, "art": None, "sex_unspecified": None}
    if year == 2007:
        total, yr, hiv, aids, unspec = map(int, _one(_TOTAL_2007, text, "the 2007 total"))
        if yr != year:
            raise _Refused(f"the total is printed for {yr}")
        if hiv + aids + unspec != total:
            raise _Refused(f"HIV {hiv}, AIDS {aids} and unspecified {unspec} do not sum to "
                           f"{total}")
        male, female, sex_unspec = map(int, _one(_SEXES_2007, text, "the 2007 sexes"))
        if male + female + sex_unspec != total:
            raise _Refused(f"men {male}, women {female} and sex unspecified {sex_unspec} do not "
                           f"sum to {total}")
        out.update(total=total, male=male, female=female, sex_unspecified=sex_unspec,
                   stages=(hiv, aids, unspec))
    elif year == 2009:
        flat = text.replace(" | ", " ")
        aids, hiv, total = map(int, _one(_NARRATIVE_2009, flat, "the 2009 narrative"))
        if int(_one(_YEAR_2009, text, "the 2009 count year")) != year:
            raise _Refused("the count is printed for another year")
        if aids + hiv != total:
            raise _Refused(f"AIDS {aids} and HIV {hiv} do not sum to {total}")
        p_hiv, p_aids = map(float, _one(_STAGES_2009, text, "the 2009 stage shares"))
        _check_pct("HIV", hiv, total, p_hiv)
        _check_pct("AIDS", aids, total, p_aids)
        out.update(total=total, stages=(hiv, aids, 0))
    else:
        yr, total = map(int, _one(_TOTAL_D1, text, "the total"))
        if yr != year:
            raise _Refused(f"the total is printed for {yr}")
        hiv, p1, aids, p2, unspec, p3 = _one(_STAGES_D1, text, "the stages")
        for label, n, p in (("HIV", hiv, p1), ("AIDS", aids, p2), ("Not specified", unspec, p3)):
            _check_pct(label, int(n), total, float(p))
        if int(hiv) + int(aids) + int(unspec) != total:
            raise _Refused(f"HIV {hiv}, AIDS {aids} and not specified {unspec} do not sum to "
                           f"{total}")
        male, pm, female, pf = _one(_SEXES_D1, text, "the sexes")
        _check_pct("Males", int(male), total, float(pm))
        _check_pct("Females", int(female), total, float(pf))
        if int(male) + int(female) != total:
            raise _Refused(f"men {male} and women {female} do not sum to {total}")
        out.update(total=total, male=int(male), female=int(female),
                   stages=(int(hiv), int(aids), int(unspec)))
        art = _ART_D1.findall(text)
        if len(art) > 1:
            raise _Refused(f"{len(art)} ART rows, where at most one belongs")
        if art:
            ayr, new, cum = map(int, art[0])
            if ayr != year:
                raise _Refused(f"the ART row is printed for {ayr}")
            out["art"] = new
        else:
            log.info("lb_moph_bulletin: %d prints no full-year ART row, and gives no "
                     "art_initiations row", year)
    want = _EXPECTED[year]
    got = (out["total"], out["male"], out["female"], out["art"])
    if got != want:
        log.warning("lb_moph_bulletin: %d reads %s, where the copy read on 28 October 2026 "
                    "printed %s", year, got, want)
    return out


class LebanonMoPHBulletinConnector(BaseConnector):
    """Lebanon, MoPH statistical bulletins, with NAP-notified HIV cases by sex and ART starts."""

    source_id = "lb_moph_bulletin"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Lebanese Ministry of Public Health statistical bulletins 2007 to 2018, with "
                   "HIV cases reported to the National AIDS Program by sex, and people newly "
                   "started on ART, national (to-source).")
    country = "LBN"
    timeout = 180

    def __init__(self, raw_dir: str = "data/raw/lebanon_moph", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _pdf_path(self, year: int) -> Path:
        """Local copy of one bulletin, downloading only if not cached."""
        did, name, size, sha = _EDITIONS[year]
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / name
        if path.exists():
            log.info("lb_moph_bulletin: using cached %s", path)
        else:
            blob = self._request("GET", _BASE + str(did)).content
            if not blob.startswith(b"%PDF"):
                raise RuntimeError(f"{_BASE}{did} did not return a PDF (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("lb_moph_bulletin: downloaded the %d bulletin (%.1f MB) -> %s", year,
                     len(blob) / 1e6, path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()[:12]
        if (len(blob), digest) != (size, sha):
            log.warning("lb_moph_bulletin: the %d bulletin differs from the copy read on 28 "
                        "October 2026 (%d bytes, sha256 %s, expected %d bytes, %s), and the "
                        "table gates still run", year, len(blob), digest, size, sha)
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
            log.error("lb_moph_bulletin: pdfplumber not installed (pip install pdfplumber)")
            return
        emitted = 0
        for year in sorted(_EDITIONS):
            if not start_year <= year <= end_year:
                continue
            try:
                path = self._pdf_path(year)
            except Exception as exc:
                log.warning("lb_moph_bulletin: the %d bulletin could not be fetched (%s)", year,
                            exc)
                continue
            try:
                with pdfplumber.open(str(path)) as pdf:
                    table = _parse(pdf, year)
            except _Refused as exc:
                log.warning("lb_moph_bulletin: the %d bulletin refused because %s", year, exc)
                continue
            except Exception as exc:
                log.warning("lb_moph_bulletin: the %d bulletin failed to parse (%s)", year, exc)
                continue
            for row in self._rows(year, table):
                emitted += 1
                yield row
        log.info("lb_moph_bulletin: emitted %d rows", emitted)

    def _rows(self, year: int, table: Dict) -> Iterator[PanelRow]:
        did, name, _, _ = _EDITIONS[year]
        hiv, aids, unspec = table["stages"]
        base: Dict = {
            "edition": f"MoPH Statistical Bulletin {year}",
            "edition_file": name,
            "page": table["page"],
            "listing": _PAGE_URL,
            "extraction": ("text layer, caption-anchored, every figure read beside the printed "
                           "label"),
            "stages_printed": {"hiv": hiv, "aids": aids, "not_specified": unspec},
            "population_note": ("no bulletin says whether the count covers residents of other "
                                "nationalities. The 2017 bulletin computes the rate for the "
                                "Lebanese population only"),
            "notes": _NOTES,
        }
        if table["sex_unspecified"] is not None:
            base["sex_unspecified"] = table["sex_unspecified"]
        cases = dict(base, definition=(
            "HIV cases, AIDS cases included, reported to the National AIDS Program of the "
            "Ministry of Public Health during the year"),
            reconcile_with=("No other source in the panel held Lebanese notified_hiv_cases "
                            "or new_diagnoses rows (checked 28 October 2026). Never compare with "
                            "new_diagnoses (Jason's ruling of 8 October 2026)"))
        for sex in ("all", "male", "female"):
            value = table["total"] if sex == "all" else table[sex]
            if value is None:
                continue
            yield self.make_row(
                country_iso3="LBN", country_name="Lebanon",
                indicator_id="notified_hiv_cases", year=year, value=value, unit="count",
                admin1="", sex=sex, source_url=_BASE + str(did),
                source_indicator_code=f"moph_statistical_bulletin.{year}.nap.{sex}",
                extra=cases,
            )
        if table["art"] is not None:
            art = dict(base, definition=("people newly started on ART during the year, the "
                                         "\"New in <year>\" figure of the NAP table"))
            yield self.make_row(
                country_iso3="LBN", country_name="Lebanon",
                indicator_id="art_initiations", year=year, value=table["art"], unit="count",
                admin1="", sex="all", source_url=_BASE + str(did),
                source_indicator_code=f"moph_statistical_bulletin.{year}.nap.art_new",
                extra=art,
            )
