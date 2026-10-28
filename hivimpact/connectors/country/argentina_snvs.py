"""
Argentina, Ministry of Health open data: notified HIV cases by province and sex, 2015 to 2024
(to-source, routine programme, sub-national).

Source: the dataset "Notificación de casos de VIH" on datos.salud.gob.ar, the CKAN open-data
portal of Argentina's Ministerio de Salud de la Nación, published by the Dirección de Respuesta
al VIH, ITS, Hepatitis Virales y Tuberculosis. The dataset describes the count as "Casos de VIH
notificados al Sistema Nacional de Vigilancia de la Salud (SNVS 2.0) por sexo, grupos de edad y
jurisdicción de residencia", so the province is the province of residence. The metadata does not
say whether the year column is the year of diagnosis or the year of notification. This connector
reads one resource, the release of 20 January 2026 by sex and jurisdiction:

    resource   7c08861b-9578-4c2a-90f7-3fe78775d8ef, notificacion-de-casos-de-vih.csv
    released   20 January 2026 (CKAN last_modified, and the server's Last-Modified header)
    read       13 October 2026, 26,579 bytes, sha256 d661dda62780
    national   6,692 cases in 2024 (4,631 men, 2,047 women)

The resource description says 2014 to 2024, and the file holds 2015 to 2024. The file is
downloaded once into `raw_dir` and read from the cached copy after that. A cached copy whose size
or sha256 differs from the copy read on 13 October 2026 is logged as a WARNING and still read,
because every gate below runs on the file itself.

THE FILE
--------
Latin-1 text, semicolons between fields, CRLF line ends, the header
"id_sexo;sexo;id_jurisdiccion;jurisdiccion;anio;casos_vih", and a run of empty rows of
semicolons at the end. The two jurisdiction labels are swapped against the values, so the name
("Córdoba", or "ARG" for the country) sits under id_jurisdiccion and the INDEC province code
(14, or 200 for the country) under jurisdiccion. The connector tells the name from the code by
content and accepts both orders. Sex codes are 1 Varones (men), 2 Mujeres (women) and 3 Ambos
sexos (both sexes).

WHAT THE COUNT IS
-----------------
HIV cases notified to SNVS 2.0, under `notified_hiv_cases` (Jason's ruling of 8 October 2026,
never merged with or compared to `new_diagnoses`). The both-sexes row exceeds men plus women in
67 of the 250 jurisdiction-years of the release read on 13 October 2026, by up to 21 nationally
(2018), which is the count of cases with no recorded sex. The difference travels in
`extra.sex_unknown` on the both-sexes rows, as in paho_core. Chaco 2019 is the one exception,
with a both-sexes row three below men plus women. The national both-sexes row for 2019 sits
three above the sum of the provinces, so the Chaco both-sexes row is most probably three short.
The file is emitted as published.

THE MINISTRY REVISES PAST YEARS AT EVERY RELEASE
------------------------------------------------
The national count for 2019 reads 4,786 in the release of March 2022, 5,790 in October 2023,
6,311 in December 2024 and 6,834 here (research/phase5_lac/lac_round1_notes.md, the section on
the gap between the Argentine datastore and PAHO). The connector carries the release in the
cached file only, and writes the release date into `extra.release`. A later release replaces the
rows of an earlier one when the file in `raw_dir` is replaced.

INTEGRITY GATES
---------------
  * the header holds the six labels above, in that order;
  * every data row has six fields, a known sex code with the matching label, a four-digit year and
    a non-negative whole count;
  * the jurisdictions are exactly the country (code 200) and the 24 provinces, each name with
    the INDEC code of the same province;
  * every jurisdiction, sex and year appears exactly once, and every jurisdiction holds the same
    run of consecutive years for all three sexes;
  * in every sex and year the 24 provinces sum to the national row within 10 cases (largest
    gap in the release of 20 January 2026, four, men and both sexes, 2018);
  * in every jurisdiction and year the both-sexes row lies between five below and 50 above men
    plus women (measured range in the release of 20 January 2026, three below to 21 above).

Any failed gate refuses the whole file with a WARNING naming the reason.

LABELS
------
`admin1` carries the province names with the Spanish accents. "CABA" becomes "Ciudad Autónoma
de Buenos Aires". The file's own label goes into `extra.admin1_source_label` and the INDEC code
into `extra.indec_code`. The national row is admin1 "".

RECONCILIATION
--------------
No other source in the panel held Argentine province rows of any indicator when this connector
was built (checked 13 October 2026). `paho_core` holds national Argentine `notified_hiv_cases`
rows for 2003 to 2024 from PAHO Core Indicator 93, reported by the same ministry. PAHO equals
this release exactly for 2023 (7,141, 4,937 men, 2,194 women) and 2024 (6,692, 4,631 men, 2,047
women) and sits below the release for 2015 to 2022 (2019, 3,937 against 6,834), because PAHO
holds an earlier report of the ministry's count for each year and has not taken the later
revisions. The PAHO counts for 2021 (5,685) and 2022 (6,073) lie between the release of
October 2023 (5,300 and 5,629) and the release of December 2024 (5,772 and 6,168). The two
sources stay separate rows, and the national rows record the comparison in
`extra.reconcile_with`.

TLS
---
The server of datos.salud.gob.ar sends the site certificate without the Sectigo intermediate
that signed the certificate (checked 13 October 2026), so the certifi store behind `requests`
refuses the chain. The macOS trust store completes the chain itself, so the download goes
through `truststore` when the package is installed, with certificate checks on. Without
`truststore`, a failed download logs the address and the path for the cached copy.

TAGGING: source_type = routine_programme_record (national case surveillance, SNVS 2.0).
"""
from __future__ import annotations

import csv
import hashlib
import io
import logging
import ssl
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_DATASET = "1f70534d-f5f0-41f7-bc9a-b9809c39a505"
_RESOURCE = "7c08861b-9578-4c2a-90f7-3fe78775d8ef"
_URL = (f"https://datos.salud.gob.ar/dataset/{_DATASET}/resource/{_RESOURCE}/download/"
        "notificacion-de-casos-de-vih.csv")
_LOCAL = "notificacion-de-casos-de-vih.csv"
_RELEASE = "2026-01-20"
_NOTES = ("research/phase5_lac/lac_round1_notes.md, the section on the gap between the "
          "Argentine datastore and PAHO and the section on download pass four")

#: The file read on 13 October 2026, (size, sha256 prefix), and the national 2024 row, checked
#: as fingerprints only.
_KNOWN = (26_579, "d661dda62780")
_NATIONAL_2024 = {"all": 6_692, "male": 4_631, "female": 2_047}

_HEADER = ["id_sexo", "sexo", "id_jurisdiccion", "jurisdiccion", "anio", "casos_vih"]
_SEX = {"1": ("varones", "male"), "2": ("mujeres", "female"), "3": ("ambos sexos", "all")}
_NATIONAL_CODE = 200

#: INDEC province code -> (the file's label, admin1).
_PROVINCES: Dict[int, Tuple[str, str]] = {
    2: ("CABA", "Ciudad Autónoma de Buenos Aires"),
    6: ("Buenos Aires", "Buenos Aires"),
    10: ("Catamarca", "Catamarca"),
    14: ("Córdoba", "Córdoba"),
    18: ("Corrientes", "Corrientes"),
    22: ("Chaco", "Chaco"),
    26: ("Chubut", "Chubut"),
    30: ("Entre Ríos", "Entre Ríos"),
    34: ("Formosa", "Formosa"),
    38: ("Jujuy", "Jujuy"),
    42: ("La Pampa", "La Pampa"),
    46: ("La Rioja", "La Rioja"),
    50: ("Mendoza", "Mendoza"),
    54: ("Misiones", "Misiones"),
    58: ("Neuquén", "Neuquén"),
    62: ("Río Negro", "Río Negro"),
    66: ("Salta", "Salta"),
    70: ("San Juan", "San Juan"),
    74: ("San Luis", "San Luis"),
    78: ("Santa Cruz", "Santa Cruz"),
    82: ("Santa Fe", "Santa Fe"),
    86: ("Santiago del Estero", "Santiago del Estero"),
    90: ("Tucumán", "Tucumán"),
    94: ("Tierra del Fuego", "Tierra del Fuego"),
}
_NATIONAL_LABEL = "ARG"

#: Largest gap allowed between the national row and the sum of the 24 provinces.
_SUM_TOL = 10
#: Allowed range of the both-sexes row minus men plus women.
_SEX_GAP = (-5, 50)


class _Refused(Exception):
    """A gate failed. The whole file is refused, never part of the file."""


def _decode(blob: bytes) -> Tuple[str, str]:
    """The file as text and the encoding read. UTF-8 first, then Latin-1, the encoding of the
    release of 20 January 2026."""
    try:
        return blob.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return blob.decode("latin-1"), "latin-1"


def _parse(blob: bytes) -> Dict:
    """Read and gate the whole file. Returns {(code, sex, year): count} and the file facts."""
    text, encoding = _decode(blob)
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    if not rows:
        raise _Refused("the file is empty")
    header = [h.strip().lstrip("﻿").lower() for h in rows[0]]
    if header != _HEADER:
        raise _Refused(f"the header reads {rows[0]}, where {_HEADER} was read on 13 October 2026")

    by_label = {lab: code for code, (lab, _) in _PROVINCES.items()}
    by_label[_NATIONAL_LABEL] = _NATIONAL_CODE
    counts: Dict[Tuple[int, str, int], int] = {}
    empty = 0
    for i, r in enumerate(rows[1:], 2):
        if not any(x.strip() for x in r):
            empty += 1
            continue
        if len(r) != 6:
            raise _Refused(f"line {i} has {len(r)} fields where six belong")
        sid, slab, a, b, yr, n = (x.strip() for x in r)
        if sid not in _SEX or slab.lower() != _SEX[sid][0]:
            raise _Refused(f"line {i} carries the sex {sid!r} {slab!r}, not one of {_SEX}")
        # The labels id_jurisdiccion and jurisdiccion are swapped against the values in the
        # release of 20 January 2026, so the name and the code are told apart by content.
        if b.isdigit() and not a.isdigit():
            name, code = a, int(b)
        elif a.isdigit() and not b.isdigit():
            name, code = b, int(a)
        else:
            raise _Refused(f"line {i} carries the jurisdiction fields {a!r} and {b!r}, where one "
                           f"name and one code belong")
        if by_label.get(name) != code:
            raise _Refused(f"line {i} pairs the jurisdiction {name!r} with the code {code}, "
                           f"which is not the INDEC pairing read on 13 October 2026")
        if not (len(yr) == 4 and yr.isdigit()):
            raise _Refused(f"line {i} carries the year {yr!r}")
        if not n.isdigit():
            raise _Refused(f"line {i} carries the count {n!r}, not a non-negative whole number")
        key = (code, _SEX[sid][1], int(yr))
        if key in counts:
            raise _Refused(f"line {i} repeats the jurisdiction {name!r}, sex {slab!r} and year "
                           f"{yr}")
        counts[key] = int(n)

    years_of: Dict[Tuple[int, str], List[int]] = defaultdict(list)
    for code, sex, year in counts:
        years_of[(code, sex)].append(year)
    codes = {code for code, _ in years_of}
    want = set(_PROVINCES) | {_NATIONAL_CODE}
    if codes != want:
        raise _Refused(f"jurisdictions missing {sorted(want - codes)} and unexpected "
                       f"{sorted(codes - want)}")
    runs = {tuple(sorted(ys)) for ys in years_of.values()}
    if len(years_of) != len(want) * 3 or len(runs) != 1:
        raise _Refused("the jurisdictions and sexes do not all hold the same run of years")
    years = list(next(iter(runs)))
    if years != list(range(years[0], years[-1] + 1)):
        raise _Refused(f"the years {years} are not consecutive")

    sum_gaps, sex_gaps = [], []
    for sex in ("all", "male", "female"):
        for year in years:
            provinces = sum(counts[(c, sex, year)] for c in _PROVINCES)
            gap = counts[(_NATIONAL_CODE, sex, year)] - provinces
            if abs(gap) > _SUM_TOL:
                raise _Refused(f"the 24 provinces sum to {provinces:,} for sex {sex} in {year}, "
                               f"where the national row reads "
                               f"{counts[(_NATIONAL_CODE, sex, year)]:,}")
            if gap:
                sum_gaps.append((sex, year, gap))
    for code in want:
        for year in years:
            gap = (counts[(code, "all", year)] - counts[(code, "male", year)]
                   - counts[(code, "female", year)])
            if not _SEX_GAP[0] <= gap <= _SEX_GAP[1]:
                raise _Refused(f"the both-sexes row for code {code} in {year} differs from men "
                               f"plus women by {gap}, outside {_SEX_GAP}")
            if gap < 0:
                sex_gaps.append((code, year, gap))

    if sum_gaps:
        log.info("ar_snvs: national row minus the sum of the provinces, where not zero, %s",
                 ", ".join(f"{s} {y} {g:+d}" for s, y, g in sum_gaps))
    if sex_gaps:
        log.info("ar_snvs: both-sexes rows below men plus women, %s",
                 ", ".join(f"{_PROVINCES[c][0]} {y} {g:+d}" for c, y, g in sex_gaps))
    if years[-1] == 2024:
        got = {s: counts[(_NATIONAL_CODE, s, 2024)] for s in _NATIONAL_2024}
        if got != _NATIONAL_2024:
            log.warning("ar_snvs: the national 2024 row reads %s, where the file read on 13 "
                        "October 2026 printed %s", got, _NATIONAL_2024)
    log.info("ar_snvs: %d rows read, %d empty rows set aside, years %d to %d, encoding %s",
             len(counts), empty, years[0], years[-1], encoding)
    return {"counts": counts, "years": years, "encoding": encoding,
            "sum_gaps": {(s, y): g for s, y, g in sum_gaps}}


def _truststore_session():
    """A requests adapter that checks certificates against the operating system's trust store,
    or None when truststore is not installed."""
    try:
        import truststore
        from requests.adapters import HTTPAdapter
    except ImportError:
        return None

    class _SystemTrust(HTTPAdapter):
        def init_poolmanager(self, *a, **kw):
            kw["ssl_context"] = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            return super().init_poolmanager(*a, **kw)

    return _SystemTrust()


class ArgentinaSNVSConnector(BaseConnector):
    """Argentina Ministry of Health open data: notified HIV cases by province and sex."""

    source_id = "ar_snvs"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("Argentina Ministry of Health open data (datos.salud.gob.ar): HIV cases "
                   "notified to SNVS 2.0 by province of residence and sex, 2015 to 2024, "
                   "release of 20 January 2026 (to-source).")
    country = "ARG"
    timeout = 120

    def __init__(self, raw_dir: str = "data/raw/argentina_snvs", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        adapter = _truststore_session()
        if adapter is not None:
            self.session.mount("https://datos.salud.gob.ar/", adapter)

    def _csv_bytes(self) -> bytes:
        """The cached file, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("ar_snvs: using cached %s", path)
        else:
            blob = self._request("GET", _URL).content
            if not blob.lstrip(b"\xef\xbb\xbf").lower().startswith(b"id_sexo;"):
                raise RuntimeError(f"{_URL} did not return the expected CSV (got {blob[:24]!r})")
            path.write_bytes(blob)
            log.info("ar_snvs: downloaded the release (%d bytes) -> %s", len(blob), path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN:
            log.info("ar_snvs: the file matches the copy read on 13 October 2026 (sha256 %s)",
                     digest[:12])
        else:
            log.warning("ar_snvs: the file differs from the copy read on 13 October 2026 (%d "
                        "bytes, sha256 %s, expected %d bytes, %s); the gates still run, and "
                        "extra.release keeps the date %s until the connector is updated",
                        len(blob), digest[:12], *_KNOWN, _RELEASE)
        return blob

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
            blob = self._csv_bytes()
        except Exception as exc:
            log.warning("ar_snvs: the release could not be fetched (%s). The file can be placed "
                        "by hand at %s from %s", exc, self.raw_dir / _LOCAL, _URL)
            return
        try:
            table = _parse(blob)
        except _Refused as exc:
            log.warning("ar_snvs: the release refused because %s", exc)
            return
        emitted = 0
        for row in self._rows(table, start_year, end_year):
            emitted += 1
            yield row
        log.info("ar_snvs: emitted %d rows", emitted)

    def _rows(self, table: Dict, start_year: int, end_year: int) -> Iterator[PanelRow]:
        counts = table["counts"]
        first, last = table["years"][0], table["years"][-1]
        order = sorted(_PROVINCES, key=lambda c: _PROVINCES[c][1]) + [_NATIONAL_CODE]
        for code in order:
            label, admin1 = _PROVINCES.get(code, (_NATIONAL_LABEL, ""))
            for sex in ("all", "male", "female"):
                for year in table["years"]:
                    if not start_year <= year <= end_year:
                        continue
                    extra: Dict = {
                        "dataset": "Notificación de casos de VIH, datos.salud.gob.ar",
                        "resource": _RESOURCE,
                        "release": _RELEASE,
                        "release_years": f"{first} to {last}",
                        "file_encoding": table["encoding"],
                        "admin1_source_label": label,
                        "indec_code": code,
                        "definition": ("HIV cases notified to the national health surveillance "
                                       "system SNVS 2.0, by province of residence. The dataset "
                                       "does not say whether the year is the year of diagnosis "
                                       "or of notification"),
                        "revision_note": ("the ministry revises past years at every release, "
                                          f"and this row carries the release of {_RELEASE} "
                                          f"({_NOTES})"),
                    }
                    if sex == "all":
                        gap = (counts[(code, "all", year)] - counts[(code, "male", year)]
                               - counts[(code, "female", year)])
                        if gap >= 0:
                            extra["sex_unknown"] = gap
                        else:
                            extra["sex_note"] = (
                                f"the both-sexes row is {-gap} below men plus women in the file "
                                "as published")
                    if admin1:
                        extra["reconcile_with"] = (
                            "none. No other source in the panel held Argentine province rows "
                            "of any indicator when this connector was built (checked 13 "
                            "October 2026)")
                    else:
                        gap = table["sum_gaps"].get((sex, year))
                        if gap:
                            extra["province_sum_note"] = (
                                f"the national row is {gap:+d} against the sum of the 24 "
                                "provinces in the file as published")
                        extra["reconcile_with"] = (
                            "paho_core holds the national row from PAHO Core Indicator 93, "
                            "reported by the same ministry. PAHO equals the release of 20 "
                            "January 2026 for 2023 and 2024 and sits below the release for 2015 to "
                            "2022 (2019, 3,937 against 6,834), because PAHO holds an earlier "
                            "report of the ministry's count for each year and has not taken "
                            "the later revisions. The two sources stay separate rows and are "
                            "not merged. "
                            "Never compare with new_diagnoses (Jason's ruling of 8 October "
                            "2026)")
                    yield self.make_row(
                        country_iso3="ARG", country_name="Argentina",
                        indicator_id="notified_hiv_cases", year=year,
                        value=counts[(code, sex, year)], unit="count", admin1=admin1, sex=sex,
                        source_url=_URL,
                        source_indicator_code=f"snvs.notificacion_vih.{_RESOURCE[:8]}",
                        extra=extra,
                    )
