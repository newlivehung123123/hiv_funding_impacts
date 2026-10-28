"""
Peru, notified HIV cases by department, and nationally by sex, 2019 to the last full year, from
the CDC Peru HIV situation room (to-source, routine programme, sub-national).

Source. The "Sala VIH" of the Centro Nacional de Epidemiología, Prevención y Control de
Enfermedades (CDC Peru, the national epidemiology centre of the Ministry of Health, MINSA).
www.dge.gob.pe/vih leads to a Shiny application (an R web application) at
app7.dge.gob.pe/maps2/shiny_vih_web/, which prints the tables in the browser and offers no data
file. The tables travel over the Shiny websocket of the application (SockJS, no sign-in and no
key), and the connector opens one session of the application, as a browser does, and reads three
tables from the reply (research/phase5_lac/lac_round1_notes.md, the CDC Peru entry, and ruling
R72 of research/rulings_2026-10-15.md):

    ten-tab01-table   "Tendencia nacional", HIV and AIDS cases by year, national
    ten-tab02-table   HIV cases by year and sex (Hombre, Mujer), national
    ten-tab07-table   "Tabla: Casos y Tasa de incidencia", HIV and AIDS cases by department and year

The read of 28 October 2026 gave the cut-off date ("Fecha de corte") 30-09-2026, epidemiological
week 39, the update date ("Fecha de actualización") 06-10-2026 and a monthly update, with 9,888
HIV cases for 2019 and 9,112 for 2025. The connector stores the decoded reply once in `raw_dir`,
and every later run reads the cached copy. A reply whose table keys differ from the read of
28 October 2026 is logged as a WARNING and still read, because every gate below runs on the
reply itself.

WHAT THE COUNT IS
-----------------
HIV cases notified to CDC Peru, under `notified_hiv_cases` (Jason's ruling of 8 October 2026,
never merged with or compared to `new_diagnoses`). The page note ("Nota aclaratoria") says the
HIV count includes the AIDS cases, which makes the HIV column the whole count and the AIDS column a
part of the HIV column. The application does not say whether the year is the year of diagnosis
or of notification, or whether the department is the department of residence or of notification.

CDC PERU REVISES PAST YEARS EVERY MONTH
---------------------------------------
The read of 5 October 2026 gave 9,884 for 2019 and 9,038 for 2025, and the read of 28 October
2026 gave 9,888 and 9,112. Every row carries the cut-off date and the update date of the reply in
`extra`. A later read replaces the rows of an earlier read when the cached reply in `raw_dir` is
removed.

THE PARTIAL YEAR
----------------
The year of the cut-off date is partial (2026 to week 39 in the read of 28 October 2026) and is
never emitted, unless the cut-off date is 31 December.

INTEGRITY GATES
---------------
  * the page prints a cut-off date with an epidemiological week and an update date.
  * the three tables arrive in one session, with no output error.
  * tab07 holds the column Departamento with the footer "Total", then vih_1 to vih_n and sida_1
    to sida_n, with the column groups "Casos de VIH" and "Casos de sida", and the vih and sida
    columns carry the same run of consecutive four-digit years.
  * the departments are exactly the 25 below, every department once, and the department filter
    of the application offers the same 25 departments.
  * every count is a non-negative whole number.
  * every vih footer equals the sum of the 25 departments.
  * tab01 holds the columns ano, vih and sida, the same years as tab07, and in every year the
    national HIV count equals the sum of the 25 departments.
  * tab02 holds the columns ano, hombre, mujer and razon, the same years, and in every year the
    national HIV count lies between men plus women and 10 above men plus women.

The department gates held exactly in the reads of 5 and 28 October 2026. In the read of 28
October 2026 men plus women equal the national count in every year from 2019 to 2026 except
2024, where men (7,485) plus women (2,155) fall one short of the national count (9,641). The
difference is the count of cases with no recorded sex, which travels in `extra.sex_unknown` on
the national row for all sexes, as in paho_core and ar_snvs. Any failed gate refuses the whole
reply with a WARNING naming the reason.

NOT CARRIED
-----------
  * The AIDS columns ("Casos de sida"), because the AIDS-case indicator is held.
  * The rates ("Tasa"), which tab07 prints when "Mostrar por" is set to "Tasa", because the
    application does not name the population behind the rate.
  * tab03, cases by age group and sex summed over the five years 2021 to 2025, which fits no
    yearly row.
  * tab04, cases by sex and life course (0 to 11, 12 to 17, 18 to 29, 30 to 59, 60 and older),
    because the age groups form no age group of the panel.
  * tab05, cases aged 15 to 39 by the sex of sexual partners, which fits no indicator of the panel.
  * The tab "Estimaciones", "Estimaciones VIH 2024 - Perú", a Spectrum estimate which
    unaids_aidsinfo carries.

LABELS
------
`admin1` carries the department names with the Spanish accents, as in peru_endes. The
application prints one LIMA row next to a separate CALLAO row, and the LIMA row is never split
into Lima Metropolitana and Departamento de Lima as in peru_endes. The label of the application
goes into `extra.admin1_source_label`. The national rows are admin1 "".

RECONCILIATION
--------------
No other connector of the project emits Peruvian department rows of `notified_hiv_cases`
(checked in the connector code on 28 October 2026). `paho_core` holds national Peruvian
`notified_hiv_cases` rows from PAHO Core Indicator 93, reported by the same ministry. In the read
of 28 October 2026, PAHO sits above the CDC count for 2019 (10,546 against 9,888), 2020 (6,261
against 5,804) and 2021 (8,809 against 8,482), below for 2022 (9,960 against 10,106) and 2025
(9,037 against 9,112), and within 10 cases for 2023 and 2024. PAHO 2025 (9,037) is within one case
of the CDC read of 5 October 2026 (9,038), which ties PAHO Core Indicator 93 for Peru to the CDC
count. PAHO sits above every CDC read for 2019 to 2021, by 3.7 to 7.3 per cent, a revision of
the size the Argentine releases show (2017 fell from 5,591 to 5,218 between the releases of 2023
and 2024), with the cause for Peru NOT VERIFIED. The two sources stay separate rows and are
never merged, as for ar_snvs and bo_anuario.

NETWORK
-------
One GET of the application page (for the dates), then one websocket session. A refused or timed
out request fails at once, with no retry, and the connector yields no rows. The run depends on
the server of CDC Peru answering at the time of the run.

Source type. routine_programme_record, the national HIV case surveillance of CDC Peru.
"""
from __future__ import annotations

import html as _html
import json
import logging
import random
import re
import string
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from ...connector_base import BaseConnector
from ...schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

_HOST = "app7.dge.gob.pe"
_PATH = "/maps2/shiny_vih_web/"
_PAGE_URL = f"https://{_HOST}{_PATH}"
_SOCKET_BASE = f"wss://{_HOST}{_PATH}__sockjs__/"
_LOCAL = "sala_vih_reply.json"
_LOCAL_PAGE = "sala_vih_page.html"
_NOTES = ("research/phase5_lac/lac_round1_notes.md, the CDC Peru entry, and ruling R72 of "
          "research/rulings_2026-10-15.md")

_TAB_NATIONAL = "ten-tab01-table"
_TAB_SEX = "ten-tab02-table"
_TAB_DEPARTMENT = "ten-tab07-table"
_TABLES = (_TAB_NATIONAL, _TAB_SEX, _TAB_DEPARTMENT)

#: The table keys of the read of 28 October 2026, checked as fingerprints only.
_KNOWN_KEYS = {
    _TAB_NATIONAL: "520850a7056e7f72d9df322a562c95c7",
    _TAB_SEX: "0d061d8d7ffe97df7e904038d0c6c511",
    _TAB_DEPARTMENT: "94182b41755c81a4d159de80571eac4b",
}

#: The label of the application -> admin1, with the accents of peru_endes.
_DEPARTMENTS: Dict[str, str] = {
    "AMAZONAS": "Amazonas", "ANCASH": "Áncash", "APURIMAC": "Apurímac",
    "AREQUIPA": "Arequipa", "AYACUCHO": "Ayacucho", "CAJAMARCA": "Cajamarca",
    "CALLAO": "Callao", "CUSCO": "Cusco", "HUANCAVELICA": "Huancavelica",
    "HUANUCO": "Huánuco", "ICA": "Ica", "JUNIN": "Junín", "LA LIBERTAD": "La Libertad",
    "LAMBAYEQUE": "Lambayeque", "LIMA": "Lima", "LORETO": "Loreto",
    "MADRE DE DIOS": "Madre de Dios", "MOQUEGUA": "Moquegua", "PASCO": "Pasco",
    "PIURA": "Piura", "PUNO": "Puno", "SAN MARTIN": "San Martín", "TACNA": "Tacna",
    "TUMBES": "Tumbes", "UCAYALI": "Ucayali",
}
_ADMIN1_NOTE = {
    "Lima": ("The application prints one LIMA row next to a separate CALLAO row, and does not "
             "split Lima into Lima Metropolitana and Departamento de Lima as peru_endes does."),
    "Callao": "Constitutional Province of Callao, printed apart from Lima.",
}

#: The inputs of the application at first load, as the page sets the inputs, with the three
#: tables marked visible. Every other output stays hidden, and the server renders the three
#: tables only.
_INPUTS = {
    "ten-tog01": "vih", "ten-tog02": "vih", "ten-tog03a": "vih", "ten-tog03b": "1",
    "ten-tog04a": "vih", "ten-tog04t": "1", "ten-tog05a": "vih", "ten-tog05b": "hombre",
    "ten-tog05t": "1", "ten-tog06": "vih", "ten-tog07a": "vih", "ten-tog07b": "1",
    "ten-tog07t": "1", "ten-fdepa-filter": "1", "ten-fprov-filter": "0",
    "ten-fdist-filter": "0", "ten-run:shiny.action": 0,
    ".clientdata_url_protocol": "https:", ".clientdata_url_hostname": _HOST,
    ".clientdata_url_port": "", ".clientdata_url_pathname": _PATH, ".clientdata_url_search": "",
    ".clientdata_url_hash_initial": "", ".clientdata_url_hash": "", ".clientdata_pixelratio": 1,
    ".clientdata_singletons": "", ".clientdata_allowDataUriScheme": True,
}
_INPUTS.update({f".clientdata_output_{t}_hidden": False for t in _TABLES})

#: Largest count of cases with no recorded sex allowed in a year (national count minus men plus
#: women, measured 0 to 1 in the read of 28 October 2026).
_SEX_GAP_MAX = 10

#: Seconds allowed for the whole websocket session, and for every single read on the socket.
_SESSION_LIMIT = 90
_SOCKET_TIMEOUT = 30

_CORTE_RE = re.compile(r"Fecha de corte:\s*\*?\s*(\d{2})-(\d{2})-(\d{4})\s*\(SE\s*(\d{1,2})\)")
_UPDATE_RE = re.compile(r"Fecha de actualizaci[oó]n:\s*(\d{2})-(\d{2})-(\d{4})")
_FREQ_RE = re.compile(r"Frecuencia:\s*([A-Za-zÁÉÍÓÚáéíóú]+)")
_NOTE_RE = re.compile(r"Nota aclaratoria:\s*(.+?Los datos no deben sumarse de forma independiente\.)")
_OPTION_RE = re.compile(r'<option value="([^"]*)">')


class _Refused(Exception):
    """A gate failed. The whole reply is refused, never part of the reply."""


def _page_facts(page: str) -> Dict:
    """The cut-off date, the epidemiological week, the update date, the frequency and the page
    note, read from the text of the application page."""
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    text = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", text)))
    corte, update = _CORTE_RE.search(text), _UPDATE_RE.search(text)
    if not corte or not update:
        raise _Refused("the application page prints no cut-off date or no update date")
    freq, note = _FREQ_RE.search(text), _NOTE_RE.search(text)
    d, m, y, week = corte.groups()
    ud, um, uy = update.groups()
    return {
        "fecha_corte": date(int(y), int(m), int(d)).isoformat(),
        "semana_epidemiologica": int(week),
        "fecha_actualizacion": date(int(uy), int(um), int(ud)).isoformat(),
        "frecuencia": freq.group(1) if freq else "",
        "nota_aclaratoria": note.group(1) if note else "",
    }


def _messages(frame: str) -> Iterator[Dict]:
    """The Shiny messages of one SockJS frame. A frame of messages reads a["0|m|{json}", ...],
    with the quotes of every message escaped inside the frame, and every frame is decoded
    before any test."""
    if not frame.startswith("a["):
        return
    for part in json.loads(frame[1:]):
        if "|m|" in part:
            yield json.loads(part.split("|m|", 1)[1])


def _is_count(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _attribs(reply: Dict, table: str) -> Dict:
    try:
        return reply["values"][table]["x"]["tag"]["attribs"]
    except (KeyError, TypeError):
        raise _Refused(f"the reply holds no table {table}")


def _year_column(attribs: Dict, table: str, names: List[str]) -> Tuple[List[int], Dict]:
    """Gate a national table with the columns `names`, the first being the year. Returns the
    years and the data."""
    ids = [c.get("id") for c in attribs.get("columns", [])]
    if ids != names:
        raise _Refused(f"{table} holds the columns {ids}, expected {names}")
    data = attribs["data"]
    years = data[names[0]]
    if not years or any(not isinstance(y, int) or isinstance(y, bool) for y in years):
        raise _Refused(f"{table} holds a year that is not a whole number")
    return years, data


def _parse(reply: Dict) -> Dict:
    """Gate the whole reply. Returns the years, the department counts, the national counts by
    sex and the page facts."""
    errors = reply.get("errors") or {}
    for table in _TABLES:
        if table in errors:
            raise _Refused(f"the application reported an error for {table}: {errors[table]}")

    t7 = _attribs(reply, _TAB_DEPARTMENT)
    cols = t7.get("columns", [])
    if not cols or cols[0].get("id") != "Departamento" or cols[0].get("footer") != "Total":
        raise _Refused("tab07 does not open with the column Departamento and the footer Total")
    vih = [c for c in cols[1:] if str(c.get("id", "")).startswith("vih_")]
    sida = [c for c in cols[1:] if str(c.get("id", "")).startswith("sida_")]
    n = len(vih)
    if n == 0 or len(cols) != 1 + 2 * n:
        raise _Refused(f"tab07 holds {len(cols)} columns, expected Departamento and two equal runs")
    if [c["id"] for c in vih] != [f"vih_{i}" for i in range(1, n + 1)] or \
            [c["id"] for c in sida] != [f"sida_{i}" for i in range(1, n + 1)]:
        raise _Refused("tab07 does not number the vih and sida columns from 1 in order")
    try:
        years = [int(c["name"]) for c in vih]
    except (KeyError, ValueError):
        raise _Refused("tab07 names a vih column with no four-digit year")
    if any(not 1980 <= y <= 2100 for y in years) or years != list(range(years[0], years[0] + n)):
        raise _Refused(f"tab07 holds the years {years}, not one run of consecutive years")
    if [c.get("name") for c in sida] != [c.get("name") for c in vih]:
        raise _Refused("tab07 names the sida columns with years apart from the vih columns")
    groups = [(g.get("name"), g.get("columns")) for g in t7.get("columnGroups") or []]
    if groups != [("Casos de VIH", [c["id"] for c in vih]),
                  ("Casos de sida", [c["id"] for c in sida])]:
        raise _Refused(f"tab07 holds the column groups {[g[0] for g in groups]}")

    data = t7["data"]
    labels = data.get("Departamento") or []
    if sorted(labels) != sorted(_DEPARTMENTS) or len(labels) != len(set(labels)):
        raise _Refused(f"tab07 holds {len(labels)} department rows, not the 25 departments once each")
    offered = reply.get("departments_offered") or []
    if sorted(offered) != sorted(_DEPARTMENTS):
        raise _Refused("the department filter of the application offers departments apart "
                       "from the 25 of tab07")
    counts: Dict[Tuple[str, int], int] = {}
    totals: Dict[int, int] = {}
    for col, year in zip(vih, years):
        values = data.get(col["id"]) or []
        if len(values) != len(labels) or not all(_is_count(v) for v in values):
            raise _Refused(f"tab07 holds a count for {year} that is not a non-negative whole number")
        totals[year] = sum(values)
        try:
            footer = int(str(col.get("footer", "")).replace(",", ""))
        except ValueError:
            raise _Refused(f"tab07 prints no whole-number footer for {year}")
        if footer != totals[year]:
            raise _Refused(f"the tab07 footer for {year} ({footer}) differs from the sum of the "
                           f"25 departments ({totals[year]})")
        for label, v in zip(labels, values):
            counts[(label, year)] = v

    t1_years, t1 = _year_column(_attribs(reply, _TAB_NATIONAL), "tab01", ["ano", "vih", "sida"])
    if t1_years != years:
        raise _Refused(f"tab01 holds the years {t1_years}, tab07 the years {years}")
    national = dict(zip(t1_years, t1["vih"]))
    for year in years:
        if not _is_count(national[year]) or national[year] != totals[year]:
            raise _Refused(f"the tab01 national count for {year} ({national[year]}) differs from "
                           f"the sum of the 25 departments ({totals[year]})")

    t2_years, t2 = _year_column(_attribs(reply, _TAB_SEX), "tab02",
                                ["ano", "hombre", "mujer", "razon"])
    if t2_years != years:
        raise _Refused(f"tab02 holds the years {t2_years}, tab07 the years {years}")
    by_sex: Dict[Tuple[str, int], int] = {}
    sex_unknown: Dict[int, int] = {}
    for year, men, women in zip(t2_years, t2["hombre"], t2["mujer"]):
        if not _is_count(men) or not _is_count(women) or \
                not 0 <= national[year] - men - women <= _SEX_GAP_MAX:
            raise _Refused(f"tab02 men plus women for {year} ({men} and {women}) lie outside 0 to "
                           f"{_SEX_GAP_MAX} below the national count ({national[year]})")
        by_sex[("all", year)], by_sex[("male", year)], by_sex[("female", year)] = (
            national[year], men, women)
        sex_unknown[year] = national[year] - men - women

    page = reply.get("page") or {}
    if not page.get("fecha_corte") or not page.get("fecha_actualizacion"):
        raise _Refused("the reply holds no cut-off date or no update date")
    corte = date.fromisoformat(page["fecha_corte"])
    full_years = [y for y in years if y < corte.year or (y == corte.year and
                                                         (corte.month, corte.day) == (12, 31))]
    return {"years": full_years, "all_years": years, "departments": counts,
            "national": by_sex, "sex_unknown": sex_unknown, "page": page, "read_at": reply.get("read_at", "")}


class PeruCDCSalaConnector(BaseConnector):
    """Notified HIV cases by department, and nationally by sex, from the CDC Peru HIV situation room."""

    source_id = "pe_cdc_sala"
    default_source_type = SourceType.ROUTINE_PROGRAMME
    description = ("CDC Peru HIV situation room (Sala VIH, app7.dge.gob.pe): HIV cases notified "
                   "to CDC Peru by department, and nationally by sex, 2019 to the last full "
                   "year, read over the websocket of the Shiny application (to-source).")
    country = "PER"
    timeout = _SOCKET_TIMEOUT

    def __init__(self, raw_dir: str = "data/raw/peru_cdc_sala", **kw):
        kw.setdefault("max_retries", 1)   # a refused or timed out request fails at once
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)

    def _capture(self) -> Tuple[Dict, bytes]:
        """One GET of the application page, then one websocket session. Returns the decoded
        reply and the page."""
        page_blob = self._request("GET", _PAGE_URL).content
        page = page_blob.decode("utf-8", errors="replace")
        if "shiny" not in page.lower() or _TAB_DEPARTMENT not in page:
            raise RuntimeError(f"{_PAGE_URL} did not return the Shiny application page")
        try:
            facts = _page_facts(page)
        except _Refused as exc:
            raise RuntimeError(str(exc))
        try:
            import websocket   # websocket-client, listed in requirements.txt
        except ImportError:
            raise RuntimeError("the package websocket-client is not installed")
        session = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        url = f"{_SOCKET_BASE}{random.randint(100, 999)}/{session}/websocket"
        ws = websocket.create_connection(url, timeout=_SOCKET_TIMEOUT, origin=f"https://{_HOST}",
                                         header=[f"User-Agent: {self.session.headers['User-Agent']}"])
        values: Dict = {}
        errors: Dict = {}
        offered: List[str] = []
        started = time.time()
        try:
            # the server sends the three tables, the output errors and the department filter
            # together in one message once the session is idle (reads of 28 October 2026)
            while not (all(t in values for t in _TABLES) and offered):
                if time.time() - started > _SESSION_LIMIT:
                    raise RuntimeError(f"the session did not send the three tables and the "
                                       f"department filter within {_SESSION_LIMIT} seconds "
                                       f"(received {sorted(values)})")
                frame = ws.recv()
                if frame == "o":
                    ws.send(json.dumps(["0|o|"]))
                    ws.send(json.dumps(["0|m|" + json.dumps({"method": "init", "data": _INPUTS})]))
                    continue
                if frame.startswith("c["):
                    raise RuntimeError(f"the server closed the session ({frame[:120]})")
                for msg in _messages(frame):
                    for table in _TABLES:
                        if table in (msg.get("values") or {}):
                            values[table] = msg["values"][table]
                    errors.update(msg.get("errors") or {})
                    for im in msg.get("inputMessages") or []:
                        if im.get("id") == "ten-fdepa-filter":
                            opts = _OPTION_RE.findall((im.get("message") or {}).get("options", ""))
                            offered = [o for o in opts if o != "1"]
                if any(t in errors for t in _TABLES):
                    break
        finally:
            ws.close()
        failed = {t: errors[t] for t in _TABLES if t in errors}
        if failed:
            # never cached, and the next run reads the application again
            raise RuntimeError(f"the application reported an output error {failed}")
        reply = {
            "read_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "page_url": _PAGE_URL,
            "page": facts,
            "departments_offered": offered,
            "errors": {t: errors[t] for t in _TABLES if t in errors},
            "values": values,
        }
        return reply, page_blob

    def _reply(self) -> Dict:
        """The cached reply, reading the application only if no reply is cached."""
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_dir / _LOCAL
        if path.exists():
            log.info("pe_cdc_sala: using cached %s", path)
        else:
            reply, page_blob = self._capture()
            (self.raw_dir / _LOCAL_PAGE).write_bytes(page_blob)
            path.write_text(json.dumps(reply, ensure_ascii=False, indent=1), encoding="utf-8")
            log.info("pe_cdc_sala: read the application (cut-off date %s) -> %s",
                     reply["page"]["fecha_corte"], path)
        reply = json.loads(path.read_text(encoding="utf-8"))
        for table, key in _KNOWN_KEYS.items():
            got = ((reply.get("values") or {}).get(table) or {}).get("x", {}).get("tag", {}) \
                .get("attribs", {}).get("dataKey")
            if got != key:
                log.warning("pe_cdc_sala: %s differs from the read of 28 October 2026 (key %s, "
                            "expected %s); the gates still run", table, got, key)
        return reply

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
            reply = self._reply()
        except Exception as exc:
            log.warning("pe_cdc_sala: the application could not be read (%s: %s). The run "
                        "depends on the server of CDC Peru at %s", type(exc).__name__, exc,
                        _PAGE_URL)
            return
        try:
            table = _parse(reply)
        except _Refused as exc:
            log.warning("pe_cdc_sala: the reply refused because %s", exc)
            return
        dropped = sorted(set(table["all_years"]) - set(table["years"]))
        if dropped:
            log.info("pe_cdc_sala: %s not emitted, partial to the cut-off date %s", dropped,
                     table["page"]["fecha_corte"])
        emitted = 0
        for row in self._rows(table, start_year, end_year):
            emitted += 1
            yield row
        log.info("pe_cdc_sala: emitted %d rows", emitted)

    def _rows(self, table: Dict, start_year: int, end_year: int) -> Iterator[PanelRow]:
        page = table["page"]
        years = [y for y in table["years"] if start_year <= y <= end_year]
        base = {
            "application": "Sala VIH, CDC Peru (Centro Nacional de Epidemiología, Prevención y "
                           "Control de Enfermedades, MINSA)",
            "fecha_corte": page["fecha_corte"],
            "semana_epidemiologica": page.get("semana_epidemiologica"),
            "fecha_actualizacion": page["fecha_actualizacion"],
            "frecuencia": page.get("frecuencia", ""),
            "read_at": table["read_at"],
            "definition": ("HIV cases notified to CDC Peru. The HIV count includes the AIDS cases "
                           "(Nota aclaratoria of the application). The application does not say "
                           "whether the year is the year of diagnosis or of notification, or "
                           "whether the department is the department of residence or of "
                           "notification"),
            "revision_note": ("CDC Peru revises past years every month, and the row carries the "
                              f"read with the cut-off date {page['fecha_corte']} ({_NOTES})"),
        }
        for label in sorted(_DEPARTMENTS, key=lambda k: _DEPARTMENTS[k]):
            admin1 = _DEPARTMENTS[label]
            for year in years:
                extra = dict(base, admin1_source_label=label, table=_TAB_DEPARTMENT)
                if admin1 in _ADMIN1_NOTE:
                    extra["admin1_note"] = _ADMIN1_NOTE[admin1]
                extra["reconcile_with"] = (
                    "none. No other connector of the project emits Peruvian department rows of "
                    "notified_hiv_cases (checked 28 October 2026)")
                yield self.make_row(
                    country_iso3="PER", country_name="Peru",
                    indicator_id="notified_hiv_cases", year=year,
                    value=table["departments"][(label, year)], unit="count", admin1=admin1,
                    sex="all", source_url=_PAGE_URL,
                    source_indicator_code="cdc_sala_vih.tab07.vih",
                    extra=extra,
                )
        for sex in ("all", "male", "female"):
            for year in years:
                extra = dict(base, table=_TAB_NATIONAL if sex == "all" else _TAB_SEX)
                if sex == "all":
                    extra["department_sum_note"] = (
                        "equal to the sum of the 25 departments of tab07 and to the tab07 footer")
                    extra["sex_unknown"] = table["sex_unknown"][year]
                else:
                    extra["sex_sum_note"] = (
                        "men plus women equal the national count of tab01 less the cases with no "
                        "recorded sex (extra.sex_unknown on the national row for all sexes)")
                extra["reconcile_with"] = (
                    "paho_core holds the national row from PAHO Core Indicator 93, reported by "
                    "the same ministry. In the read of 28 October 2026 PAHO sits above the CDC "
                    "count for 2019 to 2021 (2019, 10,546 against 9,888), below for 2022 and "
                    "2025, and within 10 cases for 2023 and 2024, and PAHO 2025 (9,037) is within "
                    "one case of the CDC read of 5 October 2026 (9,038), which ties PAHO to the CDC "
                    "count. The cause of the gap for 2019 to 2021 is NOT VERIFIED. The two "
                    "sources stay separate rows and are not "
                    "merged. Never compare with new_diagnoses (Jason's ruling of 8 October 2026)")
                yield self.make_row(
                    country_iso3="PER", country_name="Peru",
                    indicator_id="notified_hiv_cases", year=year,
                    value=table["national"][(sex, year)], unit="count", admin1="", sex=sex,
                    source_url=_PAGE_URL,
                    source_indicator_code=("cdc_sala_vih.tab01.vih" if sex == "all"
                                           else "cdc_sala_vih.tab02.sexo"),
                    extra=extra,
                )
