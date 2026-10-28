"""
Peru, ENDES table 3.3: people aged 15 to 49 who had an HIV test in the last 12 months,
national, by sex, by age group and by department (to-source, survey, sub-national).

Source: INEI, Peru's national statistics institute, runs ENDES (Encuesta Demográfica y de
Salud Familiar), the country's continuous demographic and health survey. The 2025 health
report ships its tables as workbooks inside one zip at

    https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib2090/
        informacion_complementaria.zip

and table 3.3 ("CUADRO Nº 3.3") of `Cuadros_Estadisticos/Cap. 3_2025.xlsx` gives the share of
women and men aged 15 to 49 who had an HIV test in the 12 months before the interview. The
table runs from the second half of 2013 to 2025 nationally and from 2014 to 2025 for the 26
department rows. Every year carries the standard error, the 95% confidence interval, the
coefficient of variation and the weighted and unweighted case counts, and all of them travel
with the row.

Jason cleared the series on 7 October 2026 under a separate survey indicator carrying the
ENDES definition (research/phase5_lac/lac_round1_notes.md, "Survey indicator of recent HIV
testing"). The canonical id is hiv_tested_12m_survey_pct.

WHAT THE CELL FORMAT SAYS AND THE CELL VALUE DOES NOT
-----------------------------------------------------
INEI marks precision by number format while the stored value stays a plain number.

1. LOW PRECISION. The format `\\(0.0\\)` prints a value in brackets, and the table footnote
   reads "( ) Comprende a estimadores con coeficiente de variación mayor a 15% considerados
   como referenciales", so a bracketed value is an estimate with a coefficient of variation
   above 15 per cent, published for reference only. The 2025 edition brackets five
   department values (Apurímac 2014, Cajamarca 2014, Huancavelica 2014, Puno 2014 and Puno
   2020) and seven values of the foreign-nationality row. Bracketed values are emitted with
   extra.low_precision = True, and so is any value whose own coefficient of variation column
   exceeds 15 even without brackets. INEI stores some bracketed values already rounded to
   one decimal (Apurímac 2014 is 7.5), so the decimals of a low-precision value are the
   decimals INEI printed.

2. SUPPRESSION. The format `"a"` prints the letter a in place of the value. Table 3.4 uses
   the format for estimates from fewer than 20 unweighted cases. A cell formatted `"a"` is
   never emitted, whatever number sits underneath, because INEI chose not to publish the
   number. Table 3.3 of the 2025 edition has no such cell, and the rule is enforced anyway so
   a later edition cannot leak a hidden value.

Strings in value cells ("n.a." before 2014 for departments, "-" for ethnicity and language
before 2021) are absences and yield nothing.

WHAT THIS CONNECTOR DOES NOT READ
---------------------------------
Table 3.4 (people tested who learned the result) has people tested as denominator, not all
people aged 15 to 49, so table 3.4 is a different measure and the panel never carries a
product of table 3.3 and table 3.4. The sections of table 3.3 for area of residence,
residence domain, education, wealth quintile, ethnic self-identification and mother tongue
have no panel dimension and are skipped.

DEPARTMENTS
-----------
ENDES reports 26 rows for Peru's 25 regions. Callao ("Prov. Const. del Callao") is its own
row, and Lima is split into Lima Metropolitana (the 43 districts of the capital, footnote 4/)
and Departamento de Lima (the provinces Barranca, Cajatambo, Canta, Cañete, Huaral,
Huarochirí, Huaura, Oyón and Yauyos, footnote 5/), following Law 31140. The two Lima rows are
kept apart as two admin1 rows, and the footnote meaning travels in extra.admin1_note. A
department label outside `DEPARTMENTS` is logged and skipped, so a renamed row never becomes
a new admin1 by accident.

TIMING
------
ENDES interviews run through the calendar year, and the question asks about the 12 months
before the interview, so the 2025 value covers tests taken between early 2024 and late 2025.
The first column, "2013 - II Semestre", comes from the second half of 2013 alone and is
emitted as 2013 with extra.fieldwork saying so.

The department values are weighted survey shares. The national value is not the mean of
the departments, and nothing should rebuild a national share from the department rows.
"""
from __future__ import annotations

import hashlib
import io
import logging
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType, POP_ALL

log = logging.getLogger("hivimpact")

_ZIP_URL = ("https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib2090/"
            "informacion_complementaria.zip")
_ZIP_NAME = "informacion_complementaria.zip"
# Size and sha256 prefix of the copy read on 7 October 2026, logged against so a replaced
# file is visible in the run log.
_KNOWN_ZIP = (11_496_607, "5030f6c8ef9a")
_MEMBER_RE = re.compile(r"(?:^|/)Cap\.?\s*3_(\d{4})\.xlsx$", re.I)

INDICATOR = "hiv_tested_12m_survey_pct"
AGE_15_49 = "15-49"

# Matched after accents are folded and case is raised, see _fold.
_TITLE_KEY = "QUE SE REALIZARON LA PRUEBA DE VIH EN LOS ULTIMOS 12 MESES"
_TITLE_EXCLUDE = "CONOCIERON"  # table 3.4, a different denominator
_HEADER_LABEL = "CARACTERISTICA SELECCIONADA"
_LOW_PRECISION_FOOTNOTE_KEY = "COEFICIENTE DE VARIACION MAYOR A 15%"
_CV_LIMIT = 15.0

_HALF_YEAR_RE = re.compile(r"^(\d{4})\s*-\s*II\s+SEMESTRE$")
_FOOTNOTE_MARK_RE = re.compile(r"\s+\d+/$")
_AGE_RE = re.compile(r"^(\d{1,2})\s*-\s*(\d{1,2})$")

# source label (footnote marker stripped) -> admin1
DEPARTMENTS: Dict[str, str] = {
    "Amazonas": "Amazonas",
    "Áncash": "Áncash",
    "Apurímac": "Apurímac",
    "Arequipa": "Arequipa",
    "Ayacucho": "Ayacucho",
    "Cajamarca": "Cajamarca",
    "Prov. Const. del Callao": "Callao",
    "Cusco": "Cusco",
    "Huancavelica": "Huancavelica",
    "Huánuco": "Huánuco",
    "Ica": "Ica",
    "Junín": "Junín",
    "La Libertad": "La Libertad",
    "Lambayeque": "Lambayeque",
    "Lima Metropolitana": "Lima Metropolitana",
    "Departamento de Lima": "Departamento de Lima",
    "Loreto": "Loreto",
    "Madre de Dios": "Madre de Dios",
    "Moquegua": "Moquegua",
    "Pasco": "Pasco",
    "Piura": "Piura",
    "Puno": "Puno",
    "San Martín": "San Martín",
    "Tacna": "Tacna",
    "Tumbes": "Tumbes",
    "Ucayali": "Ucayali",
}
_ADMIN1_NOTE = {
    "Callao": "Constitutional Province of Callao, reported apart from Lima.",
    "Lima Metropolitana": "The 43 districts of Lima Metropolitana (ENDES footnote 4/, Law 31140). "
                          "Excludes Callao and Departamento de Lima.",
    "Departamento de Lima": "The provinces Barranca, Cajatambo, Canta, Cañete, Huaral, Huarochirí, "
                            "Huaura, Oyón and Yauyos (ENDES footnote 5/, Law 31140). Excludes "
                            "Lima Metropolitana and Callao.",
}
_SEX = {"HOMBRE": "male", "MUJER": "female"}

_DEFINITION = ("Share of women and men aged 15 to 49 who had an HIV test in the 12 months before "
               "the ENDES interview, with no condition on receiving the result (ENDES table 3.3).")
_LOW_PRECISION_NOTE = ("INEI brackets the value: coefficient of variation above 15 per cent, "
                       "published for reference only.")
_AGG_WARNING = ("Weighted survey shares. The national value is not the mean of the department "
                "values, so take national figures from the admin1='' rows.")
_REFERENCE = ("The question covers the 12 months before the interview, and interviews run "
              "through the survey year, so a survey year also covers tests from the year before.")


def _norm(v) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", v)).strip() if isinstance(v, str) else ""


def _fold(v) -> str:
    """Whitespace-normalised, accent-free, upper-case text for matching labels."""
    s = unicodedata.normalize("NFKD", _norm(v))
    return "".join(ch for ch in s if not unicodedata.combining(ch)).upper()


def _first_section(fmt: Optional[str]) -> str:
    # A number format may carry positive;negative;zero;text sections. Only the positive
    # section decides how a share prints, and a bracketed negative section is no flag.
    return (fmt or "").split(";")[0]


def _number(v) -> Optional[float]:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


@dataclass
class _Block:
    """The columns one survey year occupies in table 3.3."""
    year: int
    header: str
    half_year: bool
    value: int
    sd: Optional[int] = None
    lower: Optional[int] = None
    upper: Optional[int] = None
    cv: Optional[int] = None
    weighted: Optional[int] = None
    unweighted: Optional[int] = None


class PeruENDESConnector(BaseConnector):
    source_id = "pe_endes"
    default_source_type = SourceType.SURVEY
    description = ("Peru — ENDES household survey, HIV test in the last 12 months, ages 15 to 49 "
                   "(national, sex, age, 26 departments, with 95% CIs).")
    country = "PER"
    timeout = 180

    def __init__(self, raw_dir: str = "data/raw/peru_endes", **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    # -- locating the workbook --------------------------------------------------
    def _zip_path(self) -> Path:
        """Local copy of the INEI zip, downloading only if not cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _ZIP_NAME
        if path.exists():
            log.info("pe_endes: using cached %s", path)
        else:
            blob = self._request("GET", _ZIP_URL).content
            if not blob.startswith(b"PK"):
                raise RuntimeError(f"pe_endes: {_ZIP_URL} did not return a zip (got {blob[:16]!r})")
            path.write_bytes(blob)
            log.info("pe_endes: downloaded %s (%.1f MB) -> %s", _ZIP_NAME, len(blob) / 1e6, path)
        blob = path.read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if (len(blob), digest[:12]) == _KNOWN_ZIP:
            log.info("pe_endes: zip matches the copy read on 7 October 2026 (sha256 %s)", digest[:12])
        else:
            log.warning("pe_endes: zip differs from the copy read on 7 October 2026 "
                        "(%d bytes, sha256 %s, expected %d bytes, %s); check the table layout",
                        len(blob), digest[:12], *_KNOWN_ZIP)
        return path

    @staticmethod
    def _member(zf: zipfile.ZipFile) -> Tuple[str, int]:
        found = [(n, int(m.group(1))) for n in zf.namelist() if (m := _MEMBER_RE.search(n))]
        if not found:
            raise RuntimeError("pe_endes: no 'Cap. 3_<year>.xlsx' workbook in the zip")
        return max(found, key=lambda t: t[1])

    # -- reading the table ------------------------------------------------------
    @staticmethod
    def _find_sheet(wb):
        """The sheet whose title asks about an HIV test in the last 12 months, not table 3.4."""
        for ws in wb.worksheets:
            for r in range(1, 6):
                for c in range(1, 6):
                    t = _fold(ws.cell(r, c).value)
                    if _TITLE_KEY in t and _TITLE_EXCLUDE not in t:
                        return ws
        raise RuntimeError("pe_endes: no sheet titled for an HIV test in the last 12 months")

    @staticmethod
    def _header(ws) -> Tuple[int, int]:
        """(row, column) of the 'Característica seleccionada' cell."""
        for r in range(1, 21):
            for c in range(1, 6):
                if _fold(ws.cell(r, c).value) == _HEADER_LABEL:
                    return r, c
        raise RuntimeError(f"pe_endes: header '{_HEADER_LABEL}' not found in sheet {ws.title}")

    @staticmethod
    def _blocks(ws, hr: int, label_col: int) -> List[_Block]:
        """One _Block per survey year, from the year header row and the two rows under it.

        A year header is merged across the year's columns, so the block runs from the year
        cell to the next filled header cell, which is another year or a 'Diferencias' or
        'Test de diferencia de medias' column.
        """
        filled = [c for c in range(label_col + 1, ws.max_column + 1)
                  if ws.cell(hr, c).value not in (None, "")]
        blocks: List[_Block] = []
        for i, c in enumerate(filled):
            raw = ws.cell(hr, c).value
            end = filled[i + 1] if i + 1 < len(filled) else ws.max_column + 1
            if isinstance(raw, (int, float)) and float(raw).is_integer() and 1990 <= raw <= 2100:
                year, half = int(raw), False
            elif re.fullmatch(r"\d{4}", _fold(raw)):
                year, half = int(_fold(raw)), False
            else:
                m = _HALF_YEAR_RE.match(_fold(raw))
                if not m:
                    continue  # a 'Diferencias' or significance-test column
                year, half = int(m.group(1)), True
            cols: Dict[str, int] = {}
            for k in range(c, end):
                sub = _fold(ws.cell(hr + 1, k).value)
                if sub == "VALOR ESTIMADO":
                    cols["value"] = k
                elif sub == "DESVIACION ESTANDAR":
                    cols["sd"] = k
                elif sub.startswith("INTERVALO DE CONFIANZA"):
                    if (_fold(ws.cell(hr + 2, k).value) == "INFERIOR"
                            and _fold(ws.cell(hr + 2, k + 1).value) == "SUPERIOR"):
                        cols["lower"], cols["upper"] = k, k + 1
                elif sub == "COEFICIENTE DE VARIACION":
                    cols["cv"] = k
                elif sub == "TOTAL DE CASOS PONDERADOS":
                    cols["weighted"] = k
                elif sub == "TOTAL DE CASOS SIN PONDERAR":
                    cols["unweighted"] = k
            if "value" not in cols:
                log.warning("pe_endes: no 'Valor estimado' column under %r, year skipped", raw)
                continue
            if "lower" not in cols:
                log.warning("pe_endes: no 95%% interval under %r, rows carry no bounds", raw)
            blocks.append(_Block(year=year, header=_norm(str(raw)), half_year=half, **cols))
        return blocks

    @staticmethod
    def _cell(ws, r: int, c: Optional[int]) -> Tuple[Optional[float], str]:
        """(value, status), status being ok, low_precision, suppressed or absent."""
        if c is None:
            return None, "absent"
        cell = ws.cell(r, c)
        v = _number(cell.value)
        if v is None:
            return None, "absent"
        fmt = _first_section(cell.number_format)
        if '"a"' in fmt:
            return None, "suppressed"
        if "(" in fmt:
            return v, "low_precision"
        return v, "ok"

    # -- the rows -----------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        wanted = set(c.upper() for c in countries) if countries else None
        if wanted and self.country not in wanted:
            return

        import openpyxl  # local import: only the xlsx connectors need it

        path = self._zip_path()
        with zipfile.ZipFile(path) as zf:
            member, edition = self._member(zf)
            data = zf.read(member)
        # Full mode, not read_only, because merged headers and number formats are both read.
        wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
        ws = self._find_sheet(wb)
        table = _norm(ws.cell(1, 1).value) or ws.title
        hr, label_col = self._header(ws)
        all_blocks = self._blocks(ws, hr, label_col)
        blocks = [b for b in all_blocks if start_year <= b.year <= (end_year or 9999)]
        log.info("pe_endes: %s, sheet %s, %s, years %s", member, ws.title, table,
                 [b.header for b in blocks])

        footnotes = " ".join(_fold(ws.cell(r, label_col).value) for r in range(hr, ws.max_row + 1))
        if _LOW_PRECISION_FOOTNOTE_KEY not in footnotes:
            log.warning("pe_endes: the bracket footnote is missing from %s, so the meaning of a "
                        "bracketed value is unconfirmed for this edition", member)

        survey = f"ENDES {edition}"
        counts = {"rows": 0, "low_precision": 0, "suppressed": 0, "cv_without_brackets": 0,
                  "skipped_labels": 0}
        seen_departments: List[str] = []
        section = ""
        national_seen = False

        for r in range(hr + 3, ws.max_row + 1):
            label = _norm(ws.cell(r, label_col).value)
            if not label:
                continue
            folded = _fold(label)
            if folded.startswith(("NOTA", "FUENTE")):
                break
            # every year, not only the requested years, so a narrow year range cannot turn
            # a data row into a section heading
            has_data = any(ws.cell(r, b.value).value not in (None, "") for b in all_blocks)
            if not has_data:
                section = folded
                continue

            plain = _FOOTNOTE_MARK_RE.sub("", label)
            admin1, sex, age = "", "all", AGE_15_49
            if folded == "TOTAL" and not section:
                national_seen = True
            elif section == "SEXO" and folded in _SEX:
                sex = _SEX[folded]
            elif section.startswith("GRUPO") and _AGE_RE.match(folded):
                a, b = _AGE_RE.match(folded).groups()
                age = f"{int(a)}-{int(b)}"
            elif section == "DEPARTAMENTO":
                admin1 = DEPARTMENTS.get(plain, "")
                if not admin1:
                    log.warning("pe_endes: department label %r is not in DEPARTMENTS, skipped", label)
                    counts["skipped_labels"] += 1
                    continue
                seen_departments.append(admin1)
            else:
                counts["skipped_labels"] += 1  # area, domain, education, wealth, ethnicity, language
                continue

            for b in blocks:
                value, status = self._cell(ws, r, b.value)
                if status == "suppressed":
                    counts["suppressed"] += 1
                    continue
                if value is None:
                    continue
                sd, _ = self._cell(ws, r, b.sd)
                lower, _ = self._cell(ws, r, b.lower)
                upper, _ = self._cell(ws, r, b.upper)
                cv, _ = self._cell(ws, r, b.cv)
                weighted, _ = self._cell(ws, r, b.weighted)
                unweighted, _ = self._cell(ws, r, b.unweighted)
                if lower is not None and upper is not None and not (lower <= value <= upper):
                    log.warning("pe_endes: %s %s: interval %s to %s excludes %s, bounds dropped",
                                label, b.header, lower, upper, value)
                    lower = upper = None

                by_format = status == "low_precision"
                by_cv = cv is not None and cv > _CV_LIMIT
                low = by_format or by_cv
                counts["low_precision"] += low
                counts["cv_without_brackets"] += by_cv and not by_format

                extra = {
                    "survey": survey,
                    "table": table,
                    "source_label": label,
                    "year_header": b.header,
                    "definition": _DEFINITION,
                    "reference_period": _REFERENCE,
                    "fieldwork": ("second half of 2013 only (July to December)" if b.half_year
                                  else f"interviews across {b.year}"),
                    "standard_error": sd,
                    "cv_pct": cv,
                    "weighted_cases": weighted,
                    "unweighted_cases": int(unweighted) if unweighted is not None else None,
                    "low_precision": low,
                    "low_precision_by_format": by_format,
                    "aggregation_warning": _AGG_WARNING,
                    "reconcile_with": "no other panel source carries "
                                      f"{INDICATOR} on 13 October 2026",
                }
                if low:
                    extra["low_precision_note"] = _LOW_PRECISION_NOTE
                if admin1 in _ADMIN1_NOTE:
                    extra["admin1_note"] = _ADMIN1_NOTE[admin1]

                yield self.make_row(
                    country_iso3="PER", country_name="Peru",
                    admin1=admin1,
                    indicator_id=INDICATOR, year=b.year,
                    value=value, value_lower=lower, value_upper=upper,
                    unit="percent",
                    population_group=POP_ALL, sex=sex, age_group=age,
                    source_url=_ZIP_URL,
                    source_indicator_code=f"{survey} {table} | {label}",
                    extra=extra,
                )
                counts["rows"] += 1

        if not national_seen:
            raise RuntimeError(f"pe_endes: no national 'Total' row in {member} sheet {ws.title}")
        if len(set(seen_departments)) != len(DEPARTMENTS):
            missing = sorted(set(DEPARTMENTS.values()) - set(seen_departments))
            log.warning("pe_endes: %d of %d departments found, missing %s",
                        len(set(seen_departments)), len(DEPARTMENTS), missing)
        if counts["cv_without_brackets"]:
            log.warning("pe_endes: %d values have a coefficient of variation above %.0f without "
                        "brackets, flagged low precision anyway", counts["cv_without_brackets"],
                        _CV_LIMIT)
        log.info("pe_endes: %d rows, %d low precision, %d suppressed cells dropped, "
                 "%d labels outside the panel dimensions", counts["rows"], counts["low_precision"],
                 counts["suppressed"], counts["skipped_labels"])
