"""
Armenia, notified HIV cases from the HIV situation analysis of the National Centre for Infectious
Diseases of the Ministry of Health of Armenia (Ինֆեկցիոն հիվանդությունների ազգային կենտրոն, NCID,
ncid.am), connector 65.

Source. NCID publishes "ՄԻԱՎ վարակի իրավիճակային վերլուծություն, Հայաստանի Հանրապետություն 2025"
(HIV situation analysis, Republic of Armenia, 2025, Yerevan 2026, posted on 1 June 2026) at
https://ncid.am/u/statistics/files/pbN9GNZTwNVrfE9fe5.docx, 245,389 bytes, read on 21 October
2026, from the statistics page of the centre (https://ncid.am/statistics). No sign-in and no key.
The connector downloads the report once into `raw_dir`, every later run reads the cached copy,
and the connector reads the Word file with zipfile and the standard XML parser. The counts come
from the data caches of the charts inside the Word file, with no optical character recognition.

Table read. Section 1.1 of the report covers citizens of Armenia, and section 1.2 covers foreign
citizens. Figure 1 (Գծապատկեր 1) counts HIV cases among foreign citizens by year of registration,
2015 to 2025. Figure 2 counts HIV cases among citizens by year of registration, with a first
entry for 1988 to 1996 and then every year from 1997 to 2025. Figure 3 repeats the citizen HIV
counts for 2005 to 2025 beside AIDS cases and deaths.

Gates. The report enters only when every check below passes, because two published figures
disagreeing leave the true figure unknown.
  The title paragraph "ՄԻԱՎ ՎԱՐԱԿԻ ԻՐԱՎԻՃԱԿԱՅԻՆ ՎԵՐԼՈՒԾՈՒԹՅՈՒՆ" is followed by the year of the
  report.
  Every figure is found by the caption printed before the chart, and every wanted caption names
  exactly one chart.
  The years of Figure 1 and Figure 2 run without a gap to the year of the report and end in the
  last year of the caption, and the years of Figure 1 start in the first year of the caption.
  Figure 2 adds to the count of citizen cases from 1988 to the end of the report year printed in
  section 1.1 (6,625 on the copy of 21 October 2026).
  Figure 1 adds to no more than the count of foreign-citizen cases from 1988 printed in section
  1.2 (490, against 405 for 2015 to 2025 in Figure 1).
  The citizen HIV series of Figure 3 equals Figure 2 in every year the two charts share.
  The section on HIV diagnosis prints the new citizen cases and the new foreign-citizen cases of
  the report year (467 and 47), equal to the report-year entries of Figure 2 and Figure 1.
  Section 1.3 prints the citizen cases of the report year (467) as men plus women (338 plus 129).

What the connector emits. National notified_hiv_cases, age group and sex "all", for 2015 to
2025, as citizens of Armenia plus foreign citizens registered with HIV in Armenia in the year,
the population of everyone diagnosed in the country (ruling R45, following R38 for Kyrgyzstan).
The citizen count and the foreign-citizen count travel in extra.

Check against other sources (read on 21 October 2026). The citizen counts of Figure 2 equal Table
1 of the joint ECDC and WHO Europe report HIV/AIDS surveillance in Europe 2025 (ecdc_hiv_report)
in every year from 2015 to 2024, and lie within nine cases of measure HFA_350 of the WHO Europe
Health for All database (who_europe_hfa) in every year from 2000 to 2019. The Armenian rows of
both aggregators therefore count citizens alone, and ruling R45 refuses them. The performance
report on the national strategic plan for 2024
(https://ncid.am/u/statistics/files/lMBmBAkTXl38UNxSse.pdf) prints 544 new HIV cases for 2024,
the citizen count of Figure 2.

Not carried.
  The years before 2015, for which the report prints no yearly count of foreign citizens.
  The citizen counts alone, a citizens-only definition ruling R37 refuses for Azerbaijan.
  The AIDS cases and deaths of Figure 3 and Figure 4, which count citizens only.
  The tests of Figure 14 and Figure 17, the people on treatment, the cascade and the viral load,
  the sex, age, transmission, place-of-infection and region charts, and the cumulative counts,
  for the reasons ruling R45 records.

Source type. routine_programme_record, the national HIV register of NCID.
"""
from __future__ import annotations

import hashlib
import io
import logging
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL, AGE_ALL, SEX_ALL

log = logging.getLogger("hivimpact")

_URL = "https://ncid.am/u/statistics/files/pbN9GNZTwNVrfE9fe5.docx"
_LOCAL = "am_ncid_hiv_situation_2025.docx"
_KNOWN = (245_389, "bf4717ed51d4")     # size and sha256 prefix of the copy read on 21 October 2026

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"

_TITLE = "ՄԻԱՎ ՎԱՐԱԿԻ ԻՐԱՎԻՃԱԿԱՅԻՆ ՎԵՐԼՈՒԾՈՒԹՅՈՒՆ"
_CAPTION = re.compile(r"^Գծապատկեր\s*(\d+)\.\s*(.+)$")
_RANGE = re.compile(r"(\d{4})\s*[-–]\s*(\d{4})")
_DOT = r"[.․]"
# section 1.1, the citizen cases from 1988 to 31 December of the report year
_P_CITIZENS = re.compile(r"մինչև\s*(\d{4})թ" + _DOT + r"\s*դեկտեմբերի\s*31-ը\s*գրանցվել\s*է\s*"
                         r"ՄԻԱՎ\s*վարակի\s*(\d+)\s*դեպք")
# section 1.2, the foreign-citizen cases from 1988 to 31 December of the report year
_P_FOREIGN = re.compile(r"մինչև\s*(\d{4})թ" + _DOT + r"\s*դեկտեմբերի\s*31-ը\s*ՀՀ-ում\s*"
                        r"օտարերկրացիների\s*շրջանում\s*գրանցվել\s*է\s*ՄԻԱՎ\s*վարակի\s*(\d+)\s*"
                        r"դեպք")
# the section on HIV diagnosis, the new cases of the report year by citizenship
_P_NEW = re.compile(r"(\d{4})\s*թվականի\s*ընթացքում\s*ախտորոշվել\s*է\s*ՄԻԱՎ\s*վարակի\s*(\d+)\s*"
                    r"նոր\s*դեպք\s*ՀՀ\s*քաղաքացիների\s*և\s*(\d+)\s*նոր\s*դեպք\s*օտարերկրյա\s*"
                    r"քաղաքացիների\s*շրջանում")
# section 1.3, the citizen cases of the report year by sex
_P_SEX = re.compile(r"(\d{4})թ" + _DOT + r"\s*ՀՀ\s*քաղաքացիների\s*շրջանում\s*գրանցվել\s*է\s*"
                    r"ՄԻԱՎ\s*վարակի\s*(\d+)\s*դեպք,\s*որից\s*(\d+)-ը՝\s*արական.*?(\d+)-ը՝\s*իգական")

# the wanted figures, as (key, words every caption must hold, words no caption may hold)
_FIGURES = (
    ("foreign", ("Օտարերկրացիների", "ըստ գրանցման տարիների"), ()),
    ("citizens", ("ՄԻԱՎ վարակի դեպքերն ըստ գրանցման տարիների",), ("Օտարերկրացիների",)),
    ("hiv_aids_deaths", ("ՄԻԱՎ-ի, ՁԻԱՀ-ի և մահվան",), ("ըստ սեռի",)),
)
_FIG3_HIV = "ՄԻԱՎ դեպքեր"

_DEFINITION = ("people registered with HIV in Armenia in the year, citizens of Armenia (Figure 2) "
               "plus foreign citizens (Figure 1), from the HIV situation analysis of the National "
               "Centre for Infectious Diseases of Armenia")
_RECONCILE = ("no other Armenian notified_hiv_cases source after ruling R45 refuses the Armenian "
              "rows of ecdc_hiv_report and who_europe_hfa, which count citizens alone. Never "
              "compare with new_diagnoses (Jason's ruling of 8 October 2026)")
_NOT_CARRIED = ("the years before 2015 (no yearly count of foreign citizens), the citizen counts "
                "alone (citizens-only, ruling R37), the AIDS cases and deaths (citizens only), the "
                "tests, the people on treatment, the cascade and the viral load, the sex, age, "
                "transmission, place-of-infection and region charts, and the cumulative counts "
                "(ruling R45)")

Block = Tuple[str, object]


def _text(el) -> str:
    return re.sub(r"\s+", " ", "".join(t.text or "" for t in el.iter(_W + "t"))).strip()


def _points(el) -> List[str]:
    """The cached points of a chart category or value element, in index order, refusing a
    missing point."""
    count = el.find(".//" + _C + "ptCount")
    pts = {int(p.get("idx")): p.find(_C + "v").text for p in el.iter(_C + "pt")}
    n = int(count.get("val")) if count is not None else len(pts)
    if sorted(pts) != list(range(n)):
        raise ValueError(f"a chart cache holds the points {sorted(pts)} of {n}")
    return [pts[i] for i in range(n)]


def _chart(xml: bytes) -> List[Tuple[Optional[str], List[str], List[str]]]:
    """Every series of a chart part as (name, categories, values)."""
    series = []
    for ser in ET.fromstring(xml).iter(_C + "ser"):
        tx = ser.find(_C + "tx")
        name = "".join(v.text or "" for v in tx.iter(_C + "v")) if tx is not None else None
        cat, val = ser.find(_C + "cat"), ser.find(_C + "val")
        if cat is None or val is None:
            raise ValueError(f"the chart series {name!r} holds no categories or no values")
        series.append((name, _points(cat), _points(val)))
    return series


def read_docx(blob: bytes) -> List[Block]:
    """The paragraphs and charts of the Word file in document order, as ("p", text) and
    ("chart", series)."""
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        body = ET.fromstring(z.read("word/document.xml")).find(_W + "body")
        blocks: List[Block] = []
        for p in body.iter(_W + "p"):
            for ref in p.iter(_C + "chart"):
                target = targets.get(ref.get(_R + "id"), "")
                blocks.append(("chart", _chart(z.read("word/" + target.lstrip("/")))))
            text = _text(p)
            if text:
                blocks.append(("p", text))
    return blocks


def _one(paragraphs: List[str], pattern: re.Pattern, what: str) -> re.Match:
    found = [m for m in (pattern.search(t) for t in paragraphs) if m]
    if len(found) != 1:
        raise ValueError(f"{len(found)} paragraphs print {what}, expected one")
    return found[0]


def _count(token: str) -> int:
    value = float(token)
    if value != int(value) or value < 0:
        raise ValueError(f"the chart value {token!r} is not a count")
    return int(value)


def parse_report(blocks: List[Block]) -> Dict:
    """Figure 1, Figure 2 and Figure 3 as {report_year, citizens, foreign, ...}, after the gates of
    the module docstring. Raises ValueError when any gate fails."""
    paragraphs = [b[1] for b in blocks if b[0] == "p"]
    if _TITLE not in paragraphs:
        raise ValueError("the title paragraph of the situation analysis was not found")
    after = paragraphs[paragraphs.index(_TITLE) + 1:paragraphs.index(_TITLE) + 4]
    years = [t for t in after if re.fullmatch(r"\d{4}", t)]
    if len(years) != 1:
        raise ValueError(f"the title is followed by {len(years)} year paragraphs, expected one")
    report_year = int(years[0])

    captioned: Dict[str, List[Tuple[re.Match, list]]] = {key: [] for key, _, _ in _FIGURES}
    caption: Optional[re.Match] = None
    for kind, content in blocks:
        if kind == "p":
            m = _CAPTION.match(content)
            if m:
                caption = m
            continue
        if caption is not None:
            for key, need, refuse in _FIGURES:
                if all(w in caption.group(2) for w in need) and \
                        not any(w in caption.group(2) for w in refuse):
                    captioned[key].append((caption, content))
        caption = None          # a caption names the first chart after the caption only
    for key, found in captioned.items():
        if len(found) != 1:
            raise ValueError(f"{len(found)} charts carry the caption of the {key} figure, "
                             f"expected one")

    def series_of(key: str, name: Optional[str] = None) -> Tuple[re.Match, List[str], List[int]]:
        cap, series = captioned[key][0]
        picked = [s for s in series if name is None or s[0] == name]
        if len(picked) != 1 or (name is None and len(series) != 1):
            raise ValueError(f"Figure {cap.group(1)} holds {len(series)} series, and "
                             f"{len(picked)} match {name!r}")
        _, cats, vals = picked[0]
        if len(cats) != len(vals):
            raise ValueError(f"Figure {cap.group(1)} holds {len(cats)} categories and "
                             f"{len(vals)} values")
        return cap, cats, [_count(v) for v in vals]

    cap1, cats1, vals1 = series_of("foreign")
    cap2, cats2, vals2 = series_of("citizens")
    cap3, cats3, vals3 = series_of("hiv_aids_deaths", _FIG3_HIV)
    range1, range2 = _RANGE.search(cap1.group(2)), _RANGE.search(cap2.group(2))
    if not range1 or not range2:
        raise ValueError("the caption of Figure 1 or Figure 2 prints no year range")

    if not all(re.fullmatch(r"\d{4}", c) for c in cats1):
        raise ValueError(f"the categories of Figure 1 are not years: {cats1}")
    years1 = [int(c) for c in cats1]
    if years1 != list(range(int(range1.group(1)), report_year + 1)) or \
            int(range1.group(2)) != report_year:
        raise ValueError(f"the years of Figure 1 ({years1}) do not run without a gap over the "
                         f"caption range {range1.group(0)} to {report_year}")
    foreign = dict(zip(years1, vals1))

    if not re.fullmatch(r"<\s*\d{4}", cats2[0]) or \
            not all(re.fullmatch(r"\d{4}", c) for c in cats2[1:]):
        raise ValueError(f"the categories of Figure 2 are not a first entry and years: {cats2}")
    years2 = [int(c) for c in cats2[1:]]
    if years2 != list(range(int(cats2[0].lstrip("< ")) + 1, report_year + 1)) or \
            int(range2.group(2)) != report_year:
        raise ValueError(f"the years of Figure 2 ({years2}) do not run without a gap to "
                         f"{report_year}")
    citizens = dict(zip(years2, vals2[1:]))

    total = _one(paragraphs, _P_CITIZENS, "the citizen cases from 1988")
    if int(total.group(1)) != report_year or int(total.group(2)) != sum(vals2):
        raise ValueError(f"Figure 2 adds to {sum(vals2)} against {total.group(2)} citizen cases "
                         f"printed to {total.group(1)}")
    total_foreign = _one(paragraphs, _P_FOREIGN, "the foreign-citizen cases from 1988")
    if int(total_foreign.group(1)) != report_year or \
            sum(vals1) > int(total_foreign.group(2)):
        raise ValueError(f"Figure 1 adds to {sum(vals1)}, above the {total_foreign.group(2)} "
                         f"foreign-citizen cases printed to {total_foreign.group(1)}")

    if not all(re.fullmatch(r"\d{4}", c) for c in cats3):
        raise ValueError(f"the categories of Figure 3 are not years: {cats3}")
    shared = [(int(c), v) for c, v in zip(cats3, vals3) if int(c) in citizens]
    if not shared or any(citizens[y] != v for y, v in shared):
        raise ValueError("the citizen HIV series of Figure 3 differs from Figure 2")

    new = _one(paragraphs, _P_NEW, "the new cases of the year by citizenship")
    if int(new.group(1)) != report_year or int(new.group(2)) != citizens[report_year] or \
            int(new.group(3)) != foreign[report_year]:
        raise ValueError(f"the section on HIV diagnosis prints {new.group(2)} citizens and "
                         f"{new.group(3)} foreign citizens for {new.group(1)}, against "
                         f"{citizens[report_year]} and {foreign[report_year]} in the charts")
    sex = _one(paragraphs, _P_SEX, "the citizen cases of the year by sex")
    if int(sex.group(1)) != report_year or int(sex.group(2)) != citizens[report_year] or \
            int(sex.group(3)) + int(sex.group(4)) != citizens[report_year]:
        raise ValueError(f"section 1.3 prints {sex.group(2)} citizen cases for {sex.group(1)} as "
                         f"{sex.group(3)} men and {sex.group(4)} women, against "
                         f"{citizens[report_year]} in Figure 2")
    return {
        "report_title": f"{_TITLE} {report_year}",
        "report_year": report_year,
        "citizens": citizens,
        "foreign": foreign,
        "citizens_total": int(total.group(2)),
        "foreign_total": int(total_foreign.group(2)),
    }


class ArmeniaNCIDConnector(BaseConnector):
    """HIV situation analysis of the National Centre for Infectious Diseases of Armenia, notified
    HIV cases."""

    source_id = "am_ncid"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("National Centre for Infectious Diseases of Armenia, HIV situation analysis "
                   "2025, citizens plus foreign citizens registered with HIV in the year, "
                   "national, 2015 to 2025 (to-source).")
    country = "ARM"
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/am_ncid", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _docx_path(self) -> Path:
        """Local copy of the report, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("am_ncid: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.startswith(b"PK\x03\x04"):
                raise RuntimeError(f"{_URL} did not return a Word file (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("am_ncid: downloaded the report (%d bytes) -> %s", len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("am_ncid: the report matches the copy read on 21 October 2026 "
                     "(sha256 %s)", digest[:12])
        else:
            log.warning("am_ncid: the report differs from the copy read on 21 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s), and the gates still run",
                        len(blob), digest[:12], *_KNOWN)
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
            path = self._docx_path()
        except Exception as exc:
            log.warning("am_ncid: the report could not be fetched (%s)", exc)
            return
        try:
            report = parse_report(read_docx(path.read_bytes()))
        except Exception as exc:
            log.warning("am_ncid: the report failed a gate (%s), no row emitted", exc)
            return
        base = {
            "report_title": report["report_title"],
            "definition": _DEFINITION,
            "table_check": ("Figure 2 adds to the citizen cases printed in section 1.1, Figure 1 "
                            "adds to no more than the foreign-citizen cases printed in section "
                            "1.2, and the report-year entries equal the text"),
            "reconcile_with": _RECONCILE,
            "not_carried": _NOT_CARRIED,
        }
        emitted = 0
        for year in sorted(set(report["citizens"]) & set(report["foreign"])):
            if not start_year <= year <= end_year:
                continue
            citizens, foreign = report["citizens"][year], report["foreign"][year]
            emitted += 1
            yield self.make_row(
                country_iso3="ARM", country_name="Armenia", admin1="",
                indicator_id="notified_hiv_cases", year=year, value=float(citizens + foreign),
                unit="count", population_group=POP_ALL, sex=SEX_ALL, age_group=AGE_ALL,
                source_url=_URL,
                source_indicator_code="ncid_am:figure2+figure1:citizens+foreign",
                extra=dict(base, citizens=citizens, foreign_citizens=foreign),
            )
        log.info("am_ncid: report for %d, emitted %d rows", report["report_year"], emitted)
