"""
HIV Policy Lab adoption statuses, the policy table of ruling R6 (research/rulings_2026-10-15.md).

Source: the HIV Policy Lab of the O'Neill Institute for National and Global Health Law at
Georgetown University, which tracks whether 194 countries have adopted 33 HIV laws and policies
(83 policy items with the sub-items) for 2017 to 2024, from legal documents, government reporting
and independent research. The data access page (https://www.hivpolicylab.org/data-access/) offers
    /data/hiv-policy-lab.csv   one row per policy item, country and year (MIT licence)
    /data/codebook.csv         the question and the status definitions of every policy item

Why a separate table, not panel rows: an adoption status is a category (Adopted, Partially
adopted, Not adopted, and Yes or No for the PrEP sub-items by population and by product). Coding
the categories as numbers would invent a scale the HIV Policy Lab never published, and the panel
value column would hold a number with no unit. The module writes
    data/policy/hiv_policy_lab.csv            join to hiv_panel.csv on country_iso3 and year
    data/policy/hiv_policy_lab_codebook.csv   join to the status table on policy_id

Encoding: on 16 October 2026 the data file decoded as Windows-1252 (cp1252) and not as UTF-8, for
example "Guía práctica" in a citation, while the codebook decoded as UTF-8. Every file is read as
strict UTF-8 first and as cp1252 only when strict UTF-8 fails, and the log names the encoding read.

Blank statuses: 71,547 of the 128,623 rows of the copy read on 16 October 2026 hold no adoption
status. A blank is no published status, so a blank row is not written. A top-level policy with
sub-items (for example S1, same-sex sex non-criminalization) holds the status in the sub-items
(S1i, criminalization, and S1ii, prosecution), and the table keeps every policy item as published.

Gates. Any failed gate refuses the whole table and writes nothing:
  * the data file and the codebook hold exactly the expected columns;
  * every policy item of the data file is in the codebook, and every codebook item is in the data;
  * no policy item, country and year repeats;
  * every status is Adopted, Partially adopted, Not adopted, Yes, No or blank, and Yes or No
    appears only on a sub-item by population or by product (an id with an underscore);
  * every ISO3 code maps to the same code through normalize.to_iso3;
  * every year is a four-digit year from 2017 to the current year.

Run: python3 -m hivimpact.policy_lab
"""
from __future__ import annotations

import csv
import hashlib
import io
import logging
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

from .connector_base import _REAL_UA
from .normalize import name_for, to_iso3

log = logging.getLogger("hivimpact")

SOURCE_ID = "hiv_policy_lab"
_BASE = "https://www.hivpolicylab.org"
_DATA_URL = _BASE + "/data/hiv-policy-lab.csv"
_CODEBOOK_URL = _BASE + "/data/codebook.csv"

#: (size, sha256) of the copies read on 16 October 2026. A different copy is read and gated
#: the same way, and the log records the change.
_SEEN = {
    "hiv-policy-lab.csv": (6798668, "fe8c56834bc7c9b6dec378cb87c85a2d51ff4717c7a886f7e7e8fb876a905d98"),
    "codebook.csv": (38482, "fa32e1627b15431437d8a0f246be13e2b8f5f72ff0f998c7f3f8f612e87013b8"),
}

_DATA_COLUMNS = ["category", "number", "letter", "year", "iso3", "country", "adoptionStatus",
                 "citation", "cautions", "documentUrls"]
_CODEBOOK_COLUMNS = ["categoryName", "category", "number", "letter", "name", "question",
                     "adoptedDefinition", "partiallyAdoptedDefinition", "notAdoptedDefinition"]
_STATUSES = {"Adopted", "Partially adopted", "Not adopted"}
_SUBGROUP_STATUSES = {"Yes", "No"}
_FIRST_YEAR = 2017

POLICY_COLUMNS = [
    "country_iso3", "country_name", "year", "policy_id", "category", "category_name",
    "policy_name", "adoption_status", "cautions", "citation",
    "source_id", "source_url", "retrieved_at", "file_sha256",
]
CODEBOOK_COLUMNS = [
    "policy_id", "category", "category_name", "policy_name", "question",
    "adopted_definition", "partially_adopted_definition", "not_adopted_definition",
    "source_id", "source_url", "retrieved_at", "file_sha256",
]


def _decode(name: str, blob: bytes) -> str:
    try:
        text = blob.decode("utf-8")
        enc = "utf-8"
    except UnicodeDecodeError:
        text = blob.decode("cp1252")
        enc = "cp1252"
    log.info("%s: %s read as %s", SOURCE_ID, name, enc)
    return text[1:] if text.startswith("﻿") else text


def _read(text: str, columns: List[str], name: str) -> Optional[List[dict]]:
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != columns:
        log.warning("%s: refused, the columns of %s are %s and not %s", SOURCE_ID, name,
                    reader.fieldnames, columns)
        return None
    return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def _pid(row: dict) -> str:
    return row["category"] + row["number"] + row["letter"]


def _fetch(session: requests.Session, url: str, raw_dir: Path, timeout: int) -> Tuple[bytes, str]:
    name = url.rsplit("/", 1)[1]
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    blob = resp.content
    digest = hashlib.sha256(blob).hexdigest()
    if _SEEN.get(name) == (len(blob), digest):
        log.info("%s: %s matches the copy read on 16 October 2026 (sha256 %s)", SOURCE_ID, name,
                 digest[:12])
    else:
        log.warning("%s: %s differs from the copy read on 16 October 2026 (%d bytes, sha256 %s), "
                    "and the gates check the new copy", SOURCE_ID, name, len(blob), digest[:12])
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{date.today().isoformat()}_{name}").write_bytes(blob)
    return blob, digest


def build_tables(data_blob: bytes, data_sha: str, codebook_blob: bytes, codebook_sha: str,
                 today: Optional[str] = None) -> Optional[Tuple[List[dict], List[dict]]]:
    """Gate the two files and return (status rows, codebook rows), or None when a gate fails."""
    today = today or date.today().isoformat()
    data = _read(_decode("hiv-policy-lab.csv", data_blob), _DATA_COLUMNS, "hiv-policy-lab.csv")
    book = _read(_decode("codebook.csv", codebook_blob), _CODEBOOK_COLUMNS, "codebook.csv")
    if data is None or book is None:
        return None

    entries: Dict[str, dict] = {}
    for b in book:
        pid = _pid(b)
        if pid in entries:
            log.warning("%s: refused, the codebook repeats the policy item %s", SOURCE_ID, pid)
            return None
        entries[pid] = b
    data_ids = {_pid(r) for r in data}
    if data_ids != set(entries):
        log.warning("%s: refused, policy items in the data file and not in the codebook %s, and in "
                    "the codebook and not in the data file %s", SOURCE_ID,
                    sorted(data_ids - set(entries)), sorted(set(entries) - data_ids))
        return None

    last_year = int(today[:4])
    seen = set()
    rows: List[dict] = []
    blank = 0
    for r in data:
        pid, iso3, year, status = _pid(r), r["iso3"], r["year"], r["adoptionStatus"]
        key = (pid, iso3, year)
        if key in seen:
            log.warning("%s: refused, the data file repeats %s", SOURCE_ID, key)
            return None
        seen.add(key)
        if not (len(year) == 4 and year.isdigit() and _FIRST_YEAR <= int(year) <= last_year):
            log.warning("%s: refused, the year %r of %s is outside %d to %d", SOURCE_ID, year, key,
                        _FIRST_YEAR, last_year)
            return None
        if to_iso3(iso3) != iso3:
            log.warning("%s: refused, the ISO3 code %r maps to %r", SOURCE_ID, iso3, to_iso3(iso3))
            return None
        if status in _SUBGROUP_STATUSES and "_" not in pid:
            log.warning("%s: refused, the status %r sits on the policy item %s", SOURCE_ID, status, pid)
            return None
        if status and status not in _STATUSES | _SUBGROUP_STATUSES:
            log.warning("%s: refused, the status %r of %s is not a published category", SOURCE_ID,
                        status, key)
            return None
        if not status:
            blank += 1
            continue
        b = entries[pid]
        rows.append({
            "country_iso3": iso3, "country_name": name_for(iso3), "year": int(year),
            "policy_id": pid, "category": b["category"], "category_name": b["categoryName"],
            "policy_name": b["name"], "adoption_status": status,
            "cautions": r["cautions"], "citation": r["citation"],
            "source_id": SOURCE_ID, "source_url": _DATA_URL, "retrieved_at": today,
            "file_sha256": data_sha,
        })

    codebook = [{
        "policy_id": pid, "category": b["category"], "category_name": b["categoryName"],
        "policy_name": b["name"], "question": b["question"],
        "adopted_definition": b["adoptedDefinition"],
        "partially_adopted_definition": b["partiallyAdoptedDefinition"],
        "not_adopted_definition": b["notAdoptedDefinition"],
        "source_id": SOURCE_ID, "source_url": _CODEBOOK_URL, "retrieved_at": today,
        "file_sha256": codebook_sha,
    } for pid, b in entries.items()]

    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["adoption_status"]] = counts.get(row["adoption_status"], 0) + 1
    log.info("%s: %d status rows over %d countries, %d policy items and the years %d to %d, %s, "
             "with %d blank statuses not written", SOURCE_ID, len(rows),
             len({x["country_iso3"] for x in rows}), len({x["policy_id"] for x in rows}),
             min(x["year"] for x in rows), max(x["year"] for x in rows), counts, blank)
    return rows, codebook


def _write(rows: List[dict], columns: List[str], path: Path, key) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        w.writerows(sorted(rows, key=key))
    log.info("%s: wrote %d rows to %s", SOURCE_ID, len(rows), path)


def run(outdir: str | Path = "data/policy", raw_dir: str | Path = "data/raw/hiv_policy_lab",
        timeout: int = 60) -> Optional[Path]:
    session = requests.Session()
    session.headers.update({"User-Agent": _REAL_UA})
    data_blob, data_sha = _fetch(session, _DATA_URL, Path(raw_dir), timeout)
    book_blob, book_sha = _fetch(session, _CODEBOOK_URL, Path(raw_dir), timeout)
    tables = build_tables(data_blob, data_sha, book_blob, book_sha)
    if tables is None:
        return None
    rows, codebook = tables
    outdir = Path(outdir)
    path = outdir / "hiv_policy_lab.csv"
    _write(rows, POLICY_COLUMNS, path,
           lambda r: (r["country_iso3"], r["year"], r["category"], r["policy_id"]))
    _write(codebook, CODEBOOK_COLUMNS, outdir / "hiv_policy_lab_codebook.csv",
           lambda r: (r["category"], r["policy_id"]))
    return path


if __name__ == "__main__":   # python -m hivimpact.policy_lab
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run()
