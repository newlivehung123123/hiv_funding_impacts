#!/usr/bin/env python3
"""
Discover, cache and characterise the Chad, Guinea and Niger health statistics yearbooks, so
the three remaining item 17 connectors can be written against real extracted text.

Why this script exists. Round four of the West and Central Africa survey read all three
yearbooks on 30 September 2026 and recorded the table numbers, the page counts and sample
figures in `docs/PHASE4_FEASIBILITY_WCA.md` and `docs/ACCESS_LADDER.md`. Round four saved no
file and recorded no download URL, only the three hostnames. `data/raw/` holds nothing for any
of the three countries, so none of the three parsers can be written, because a PDF table parser
depends on the header wording, the column order and the line layout the extraction library
produces, and none of the three can be guessed from a prose summary. The Cameroon build was held
to that standard and the Cameroon parsers were written against cached files, which is the
standard these three are held to as well.

Why discovery and not a URL list. The Cameroon survey could name its two index pages because
both were recorded. Here only `inseed.ssn-tchad.td` carries a recorded endpoint, being
`/api/publications/search?q=`, which answers without a token where `/api/menus` answers
`401 Token d'accès requis`. The empty search answered HTTP 400 on 2 October 2026, and the same
day `q=SANITAIRES` answered 200, so the script searches on the health word. For
`stat-guinee.org` and `stat-niger.org` nothing beyond the hostname was written down, so this
script enumerates each site's own links from the site root,
follows the matching pages one level deep on the same host only, and reports what it finds. A
guessed path that 404s teaches nothing, and a site's own navigation is the one description of
the site that cannot be out of date.

What this script does.

  1. Chad. Searches the INSEED catalogue for `SANITAIRES` and `SANITAIRE`, merges the records of
     the two searches, prints the field names of the first record in full
     because the field that carries the file is not recorded anywhere, lists every publication
     whose title names a health yearbook, and caches each one it can resolve to a PDF. A cached
     Chad file is named after its upload path, which carries no edition year, so the catalogue
     fields of every yearbook are saved beside the files as `catalogue_sanitaires.json`, and
     each file's size is checked against the size the catalogue gives.
  2. Guinea and Niger. Crawls the site root and one level below it, on the same host, collecting
     PDF links whose href or anchor text names a yearbook, and caches those.
  3. Characterises every cached PDF, printing page count, bytes, extracted characters, whether
     digits survive extraction, how many tables `pdfplumber` finds, which pages carry the
     captions each connector needs, and which pages name four or more of that country's own
     regions, which is the test round four applied by hand.

What this script does not do. It writes nothing outside `data/raw/`, touches no file under
`data/panel/`, computes no panel row and runs no part of the pipeline. A file already present is
left alone and characterised as it stands, so a vetted copy always wins and a second run costs
no download.

Table numbers are reported and never trusted. Round four read Chad's 2023 edition, Guinea's 2018
edition and Niger's 2019 edition, and the numbering of a yearbook table does not hold across
editions, so every caption is matched on a language-independent "tabl" stem plus the number, and
every number is reported per page and checked against the keyword block before any parser is
pinned to a number.

Usage, from the project root.

    python3 scripts/survey_wca_yearbooks.py
    python3 scripts/survey_wca_yearbooks.py --countries chad
    python3 scripts/survey_wca_yearbooks.py --no-download     # characterise what is cached
    python3 scripts/survey_wca_yearbooks.py --list-only       # discovery report, no download
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hivimpact.connector_base import BaseConnector  # noqa: E402

log = logging.getLogger("hivimpact")

RAW_ROOT = Path("data/raw")

# The one Chad endpoint round two recovered from the site's own JavaScript bundle. The site
# serves an identical 3,239-byte shell for every path, so no HTML page can be crawled here.
CHAD_API = "https://inseed.ssn-tchad.td/api"
CHAD_HOST = "https://inseed.ssn-tchad.td"
CHAD_SEARCH = f"{CHAD_API}/publications/search?q="
# On 2 October 2026 the empty search `q=` answered HTTP 400 on all four attempts, where on
# 17 August 2026 the empty search returned the whole catalogue. Jason's test the same day showed
# `q=SANITAIRES` answering 200 with eight records, against the ten health yearbooks recorded in
# August. The endpoint matches title text, so the singular `SANITAIRE` is searched as well, in
# case an edition's title is singular, and the records of both searches are merged on `_id`.
CHAD_QUERIES = ("SANITAIRES", "SANITAIRE")

GUINEA_ROOT = "https://www.stat-guinee.org/"
NIGER_ROOT = "https://www.stat-niger.org/"

# A link naming a statistics yearbook, on the href or on the anchor text. Round two established
# that Chad's own search returns nothing for `sante` and nothing for `VIH` while the titles read
# SANITAIRES, so the health word is matched on the `sanit` stem and never on `sante`.
_YEARBOOK_RE = re.compile(r"annuaire|yearbook|sanitaire|sanitaires|statistiques?[-_ ]sanit", re.I)
# A link worth following one level deep, when the link is not itself a PDF.
_FOLLOW_RE = re.compile(r"publication|annuaire|statistiq|rapport|document|biblioth|sanit|sant",
                        re.I)

_ANCHOR_RE = re.compile(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
_PDF_HREF_RE = re.compile(r'href=["\']([^"\']+?\.pdf[^"\']*)["\']', re.I)
_TAG_RE = re.compile(r"<[^>]+>")

# Captions each connector needs, from the round-four reads recorded in
# `docs/PHASE4_FEASIBILITY_WCA.md`. Tableau 4.2 is written so the pattern cannot also match
# Tableau 4.19, which is the other Guinea table and sits twelve pages away.
CHAD_CAPTIONS: List[Tuple[str, str]] = [
    ("Tableau 306, ART cohort by province with its flows", r"tabl\w*\s*306\b"),
    ("Tableau 322, PMTCT by province", r"tabl\w*\s*322\b"),
    ("any table numbered 300 to 330", r"tabl\w*\s*3[0-2]\d\b"),
]
GUINEA_CAPTIONS: List[Tuple[str, str]] = [
    ("Tableau 4.2, TB and HIV co-infection by health district", r"tabl\w*\s*4\.2(?!\d)"),
    ("Tableau 4.19, antenatal counselling and testing by district", r"tabl\w*\s*4\.19\b"),
    ("any table numbered 4.x", r"tabl\w*\s*4\.\d+"),
]
NIGER_CAPTIONS: List[Tuple[str, str]] = [
    ("Tableau 99, TB and HIV co-infection by district and region", r"tabl\w*\s*99\b"),
    ("Tableaux 58 and 59, HIV form completeness and promptitude", r"tabl\w*\s*5[89]\b"),
]

# Words that should appear on a page carrying the table each connector wants, as a second check
# that a numbered caption is the table round four described. Accented and unaccented forms are
# both written out, because whether accents survive extraction is one of the open questions.
_COMMON_KEYWORDS: List[Tuple[str, str]] = [
    ("an HIV word", r"vih|sida|hiv|aids"),
    ("antiretrovirals", r"\barv\b|antir[eé]trovir|\btarv\b|\bart\b"),
    ("tuberculosis co-infection", r"co[- ]?infection|tuberculose|\btb\b"),
    ("antenatal care", r"\bcpn\b|consultation pr[eé]natale|pr[eé]natal"),
    ("a reporting-completeness word", r"compl[eé]tude|promptitude"),
    ("a year label", r"\b20(0[5-9]|1\d|2[0-6])\b"),
]

# Each country's own first-level units, so a page can be tested for carrying four or more of
# them, which is the test round four applied by hand to decide a table was sub-national.
CHAD_UNITS = [r"n.?djamena", r"logone", r"\blac\b", r"ouadda", r"mayo[- ]kebbi", r"hadjer",
              r"batha", r"borkou", r"chari[- ]baguirmi", r"ennedi", r"gu[eé]ra", r"kanem",
              r"moyen[- ]chari", r"salamat", r"\bsila\b", r"tandjil", r"tibesti", r"wadi fira",
              r"barh[- ]el[- ]gazel"]
GUINEA_UNITS = [r"\bbok[eé]\b", r"conakry", r"faranah", r"kankan", r"kindia", r"\blab[eé]\b",
                r"mamou", r"nz[eé]r[eé]kor"]
NIGER_UNITS = [r"agadez", r"diffa", r"dosso", r"maradi", r"niamey", r"tahoua", r"tillab[eé]r",
               r"zinder"]


class YearbookFetcher(BaseConnector):
    """HTTP on the project's own session, headers, retries and timeout."""

    source_id = "wca_yearbook_survey"
    timeout = 120


def _strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", s)).strip()


def _absolute(href: str, page_url: str) -> str:
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("//"):
        return "https:" + href
    root = re.match(r"(https?://[^/]+)", page_url)
    base = root.group(1) if root else ""
    if href.startswith("/"):
        return base + href
    return page_url.rsplit("/", 1)[0] + "/" + href


def _bare_host(url: str) -> Optional[str]:
    """A URL's host, lowercased, with one leading `www.` removed and nothing else.

    `lstrip("www.")` cannot do this, because `lstrip` takes a set of characters and would turn
    a host beginning with a w, such as `waho.dhis2.org`, into `aho.dhis2.org`.
    """
    match = re.match(r"https?://([^/:]+)", url)
    if not match:
        return None
    host = match.group(1).lower()
    return host[4:] if host.startswith("www.") else host


def _same_host(url: str, other: str) -> bool:
    a, b = _bare_host(url), _bare_host(other)
    return a is not None and a == b


def _local_name(url: str) -> str:
    """Flatten a URL's path into one filename, following `cambodia_nchads.py`.

    A basename alone is not safe, because a content-management system stores one edition under
    `/uploads/2019/` and the next under `/uploads/2020/`, and two editions published under the
    same basename would overwrite each other.
    """
    path = url.split("?", 1)[0]
    path = re.sub(r"^https?://[^/]+", "", path)
    marker = "/uploads/"
    tail = path.split(marker, 1)[1] if marker in path else path.lstrip("/")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", tail.replace("/", "_"))
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name or "yearbook.pdf"


# -- Chad, a JSON catalogue and no crawlable HTML -----------------------------------------

def _walk_json(node, prefix: str = "") -> List[Tuple[str, object]]:
    """Flatten a JSON record to (dotted key, scalar) pairs, so no field is missed.

    The INSEED record's field names were never written down, and the field that carries the
    file could be `file`, `fichier`, `url`, `path`, `document` or something else again, so the
    whole record is flattened and printed instead of a guessed subset.
    """
    out: List[Tuple[str, object]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            out += _walk_json(value, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(node, list):
        for i, value in enumerate(node[:4]):
            out += _walk_json(value, f"{prefix}[{i}]")
    else:
        out.append((prefix, node))
    return out


def _records(payload) -> List[dict]:
    """Pull the list of publication records out of whatever shape the endpoint returns."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        for key in ("data", "results", "publications", "items", "rows", "content"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return [r for r in inner if isinstance(r, dict)]
            if isinstance(inner, dict):
                deeper = _records(inner)
                if deeper:
                    return deeper
    return []


def _candidate_urls(record: dict) -> List[str]:
    """Every value in a record that could address a file, most file-like first."""
    scored: List[Tuple[int, str]] = []
    for key, value in _walk_json(record):
        if not isinstance(value, str) or not value.strip():
            continue
        low_key, low_val = key.lower(), value.lower()
        if low_val.endswith(".pdf"):
            score = 0
        elif "/" in value and re.search(r"file|fichier|path|url|document|lien|media|download",
                                        low_key):
            score = 1
        elif re.search(r"file|fichier|path|document|slug", low_key) and " " not in value:
            score = 2
        else:
            continue
        scored.append((score, value.strip()))
    seen, out = set(), []
    for _score, value in sorted(scored, key=lambda p: p[0]):
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _chad_file_urls(path: str) -> List[str]:
    """The addresses a catalogue file path could be served from, most likely first.

    The catalogue gives a file as a root-relative path such as `/uploads/publications/x.pdf`,
    and whether the site serves `/uploads/` from the host root or behind the `/api` prefix was
    never tested. Both forms are offered, and `cache` keeps only a body that starts `%PDF`, so
    a shell page answering the wrong form is refused and the next form is tried. Both forms
    flatten to one local filename, so the second form is skipped once the first is cached.
    """
    if not path.startswith("/") or path.startswith("//"):
        return [_absolute(path, CHAD_API + "/")]
    urls = [CHAD_HOST + path]
    if not path.startswith("/api/"):
        urls.append(CHAD_API + path)
    return urls


def discover_chad(fetcher: YearbookFetcher,
                  manifest: Optional[List[dict]] = None) -> List[Tuple[str, str]]:
    """Search the INSEED catalogue and return (address, title) pairs for every health yearbook.

    A cached Chad file is named after the catalogue's upload path, which carries no edition
    year, so when `manifest` is given each yearbook's own catalogue fields are appended to it,
    for `write_chad_manifest` to save beside the files.
    """
    print("\n=== discovery, Chad INSEED catalogue ===")
    records: List[dict] = []
    seen_ids: set = set()
    for query in CHAD_QUERIES:
        endpoint = CHAD_SEARCH + query
        print(f"endpoint  {endpoint}")
        try:
            payload = fetcher.get_json(endpoint)
        except Exception as exc:
            print(f"  FAILED to read the catalogue: {exc}")
            continue
        found = _records(payload)
        if isinstance(payload, dict):
            print(f"  answered count {payload.get('count')}, total {payload.get('total')}, "
                  f"page {payload.get('page')} of {payload.get('pages')}")
            if isinstance(payload.get("pages"), int) and payload["pages"] > 1:
                print("  WARNING the answer runs to more than one page and only the first page "
                      "was read, so the catalogue may hold editions this survey does not see.")
        if not found:
            print("  no record list found in the payload. The payload's own shape follows, so "
                  "the right key can be named by hand.")
            print(json.dumps(payload, ensure_ascii=False, indent=2)[:4000])
            continue
        added = 0
        for record in found:
            key = record.get("_id") or json.dumps(record, sort_keys=True, ensure_ascii=False)
            if key in seen_ids:
                continue
            seen_ids.add(key)
            records.append(record)
            added += 1
        print(f"  {len(found)} record(s), {added} not already seen")

    print(f"catalogue returned {len(records)} distinct record(s) over {len(CHAD_QUERIES)} "
          "searches, against the ten health yearbooks recorded on 17 August 2026")
    if not records:
        print("Round two reached this endpoint without a token on 17 August 2026, and Jason's "
              "test of 2 October 2026 reached `q=SANITAIRES`. If every search now fails, the "
              "Chad build is blocked and the refusal belongs in the access ladder.")
        return []

    print("\nthe first record in full, so the field that carries the file can be named")
    for key, value in _walk_json(records[0]):
        shown = str(value)
        print(f"  {key:<40} {shown[:120]}")

    kept: List[Tuple[str, str]] = []
    print(f"\nevery record whose title names a health yearbook, of {len(records)}")
    for record in records:
        title = ""
        for key in ("titre", "title", "nom", "name", "libelle", "intitule"):
            if isinstance(record.get(key), str) and record[key].strip():
                title = record[key].strip()
                break
        if not title:
            title = " ".join(str(v) for _k, v in _walk_json(record)
                             if isinstance(v, str) and len(v) > 8)[:200]
        if not _YEARBOOK_RE.search(title):
            continue
        urls = _candidate_urls(record)
        print(f"  {title[:110]}  (annee {record.get('annee')}, "
              f"published {str(record.get('datePublication', ''))[:10]})")
        if not urls:
            print("        no field in this record looks like a file address")
            continue
        for url in urls[:4]:
            print(f"        candidate  {url}")
        print(f"        local name {_local_name(urls[0])}")
        for address in _chad_file_urls(urls[0]):
            print(f"        will try   {address}")
            kept.append((address, title))
        if manifest is not None:
            fichier = record.get("fichier") if isinstance(record.get("fichier"), dict) else {}
            manifest.append({
                "local_name": _local_name(urls[0]),
                "catalogue_path": urls[0],
                "addresses_tried": _chad_file_urls(urls[0]),
                "titre": title,
                "annee": record.get("annee"),
                "datePublication": record.get("datePublication"),
                "taille": fichier.get("taille"),
                "slug": record.get("slug"),
                "_id": record.get("_id"),
            })

    if not kept:
        print("  none. Every title in the catalogue follows, so the yearbook can be named by "
              "hand if INSEED has relabelled the series.")
        for record in records[:140]:
            for key in ("titre", "title", "nom", "name", "libelle"):
                if isinstance(record.get(key), str):
                    print(f"        {record[key][:140]}")
                    break
    return kept


# -- Guinea and Niger, a site root and one level below it ---------------------------------

def discover_site(fetcher: YearbookFetcher, root_url: str, label: str,
                  max_pages: int = 14) -> List[Tuple[str, str]]:
    """Collect yearbook PDF links from a site root and one level below it, same host only.

    Nothing about either site's path layout was recorded, so the site's own navigation is
    followed instead of a guessed path. The crawl stops at depth one and at `max_pages` fetches,
    because the object here is to find a document family that round four already read and not to
    mirror a statistics institute.
    """
    print(f"\n=== discovery, {label} ===")
    print(f"root  {root_url}")
    pdfs: Dict[str, str] = {}
    follow: List[Tuple[str, str]] = []
    visited: set = set()

    def read(url: str) -> Optional[str]:
        if url in visited:
            return None
        visited.add(url)
        try:
            return fetcher.get_text(url)
        except Exception as exc:
            print(f"  FAILED  {url}: {exc}")
            return None

    html = read(root_url)
    if html is None:
        print("the site root could not be read at all, so the country is blocked until the host "
              "answers. A certificate failure and a refusal are different findings and the "
              "error above says which this is.")
        return []
    print(f"read  {len(html):,} bytes of HTML from the root")

    def harvest(page_html: str, page_url: str) -> None:
        for href, body in _ANCHOR_RE.findall(page_html):
            text = _strip_tags(body)
            url = _absolute(href, page_url)
            if not url.lower().startswith(("http://", "https://")):
                continue
            if ".pdf" in url.lower().split("?", 1)[0]:
                pdfs.setdefault(url, text)
            elif _same_host(url, root_url) and _FOLLOW_RE.search(href + " " + text):
                if url not in visited and (url, text) not in follow:
                    follow.append((url, text))
        for href in _PDF_HREF_RE.findall(page_html):
            pdfs.setdefault(_absolute(href, page_url), "")

    harvest(html, root_url)
    print(f"root carries {len(pdfs)} PDF link(s) and {len(follow)} page(s) worth following")
    for url, text in follow[:max_pages]:
        print(f"  following  {url}")
        if text:
            print(f"        text  {text[:120]}")
        page = read(url)
        if page is not None:
            harvest(page, url)

    if not pdfs:
        print("no PDF link anywhere on the root or the pages followed. The root's markup follows "
              "so the layout can be read by hand.")
        print("-" * 70)
        print(html[:20000])
        print("-" * 70)
        return []

    print(f"\n{len(pdfs)} PDF link(s) in all")
    kept: List[Tuple[str, str]] = []
    for url in sorted(pdfs):
        text = pdfs[url]
        hit = bool(_YEARBOOK_RE.search(url) or _YEARBOOK_RE.search(text))
        print(f"  {'KEEP' if hit else '    '}  {url}")
        if text:
            print(f"        text  {text[:120]}")
        if hit:
            kept.append((url, text))
    if not kept:
        print(f"\nNo PDF link names a yearbook. Every PDF link is printed above, so the right "
              f"one can be named by hand if {label} labels the series differently.")
    return kept


# -- caching and characterising -----------------------------------------------------------

def cache(fetcher: YearbookFetcher, urls: Sequence[Tuple[str, str]],
          dest_dir: Path) -> List[Path]:
    """Download each URL into `dest_dir`, skipping a file already on disk.

    Chad offers two addresses per file, and both flatten to one local name, so an address whose
    file this call has already cached or found on disk is passed over without a second request.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    for url, _text in urls:
        dest = dest_dir / _local_name(url)
        if dest in paths:
            continue
        if dest.exists() and dest.stat().st_size > 0:
            print(f"  already cached  {dest} ({dest.stat().st_size:,} bytes)")
            paths.append(dest)
            continue
        try:
            resp = fetcher._request("GET", url)
        except Exception as exc:
            print(f"  FAILED  {url}: {exc}")
            continue
        body = resp.content
        ctype = resp.headers.get("Content-Type", "")
        if not body.startswith(b"%PDF"):
            print(f"  NOT A PDF  {url} returned {len(body):,} bytes of {ctype!r}, first bytes "
                  f"{body[:16]!r}. Not cached.")
            continue
        dest.write_bytes(body)
        print(f"  cached  {dest} ({len(body):,} bytes)")
        paths.append(dest)
    return paths


CHAD_MANIFEST_NAME = "catalogue_sanitaires.json"


def write_chad_manifest(manifest: Sequence[dict], dest_dir: Path) -> None:
    """Save the catalogue fields of each Chad yearbook beside the files, and check each size.

    The catalogue's `taille` field gives the file's size in bytes, so a cached file whose size
    differs is reported, because a truncated download would otherwise pass the `%PDF` test.
    """
    print(f"\n=== catalogue record, chad, {len(manifest)} yearbook(s) ===")
    out = []
    for entry in manifest:
        path = dest_dir / entry["local_name"]
        on_disk = path.stat().st_size if path.exists() else None
        expected = entry.get("taille")
        if isinstance(expected, str) and expected.strip().isdigit():
            expected = int(expected.strip())
        if on_disk is None:
            verdict = "NOT CACHED"
        elif isinstance(expected, int) and expected == on_disk:
            verdict = "size matches the catalogue"
        elif isinstance(expected, int):
            verdict = f"SIZE DIFFERS, catalogue {expected:,} bytes"
        else:
            verdict = "the catalogue gives no size"
        shown = f"{on_disk:,} bytes" if on_disk is not None else "no file"
        print(f"  {str(entry.get('annee')):<6} {entry['titre'][:60]:<60} {shown:>18}  {verdict}")
        out.append({**entry, "bytes_on_disk": on_disk})
    if not dest_dir.exists():
        print("  no cache directory, so no catalogue record was written")
        return
    target = dest_dir / CHAD_MANIFEST_NAME
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  catalogue record written to {target}")


def characterise(path: Path, captions: Sequence[Tuple[str, str]],
                 units: Sequence[str]) -> None:
    """Print what a cached PDF's text layer holds, which is what decides the parser."""
    print(f"\n--- {path} ---")
    print(f"bytes  {path.stat().st_size:,}")
    try:
        import pdfplumber
    except ImportError:
        print("pdfplumber is not installed, so no text can be read. pip install pdfplumber")
        return
    try:
        pdf = pdfplumber.open(str(path))
    except Exception as exc:
        print(f"pdfplumber cannot open the file: {exc}")
        return

    with pdf:
        pages = pdf.pages
        print(f"pages  {len(pages)}")
        per_page_chars: List[int] = []
        digit_pages = 0
        table_total = 0
        page_text: List[str] = []
        for pg in pages:
            try:
                text = pg.extract_text() or ""
            except Exception:
                text = ""
            page_text.append(text)
            per_page_chars.append(len(text))
            if re.search(r"\d", text):
                digit_pages += 1
            try:
                table_total += len(pg.extract_tables())
            except Exception:
                pass

        total = sum(per_page_chars)
        ordered = sorted(per_page_chars)
        median = ordered[len(ordered) // 2] if ordered else 0
        empty = sum(1 for n in per_page_chars if n == 0)
        print(f"characters  {total:,} in all, median {median:,} a page, "
              f"{empty} page(s) with no text at all")
        print(f"pages carrying a digit  {digit_pages} of {len(pages)}")
        print(f"tables pdfplumber finds  {table_total}")

        if total == 0:
            print("VERDICT  no text layer, so this edition is scanned images and is refused, "
                  "because this project does not use OCR.")
            return
        if digit_pages == 0:
            print("VERDICT  text but no digits, so the figures are images over a text layer "
                  "and the edition is refused.")
            return
        print("VERDICT  born-digital with digits in the text layer, so a deterministic parser "
              "is possible on this edition.")

        lowered = [t.lower() for t in page_text]
        joined = "\n".join(lowered)

        print("captions, by page number as pdfplumber indexes them from 1")
        for label, pattern in captions:
            hits = [i + 1 for i, t in enumerate(lowered) if re.search(pattern, t)]
            shown = ", ".join(str(h) for h in hits[:14]) if hits else "NOT FOUND"
            more = f" and {len(hits) - 14} more" if len(hits) > 14 else ""
            print(f"  {label:<60} {shown}{more}")

        print("keywords, present or absent in the whole document")
        for label, pattern in _COMMON_KEYWORDS:
            print(f"  {label:<60} {'yes' if re.search(pattern, joined) else 'NO'}")

        hiv_pages = [i + 1 for i, t in enumerate(lowered) if re.search(r"vih|sida|hiv", t)]
        print(f"pages mentioning HIV  {len(hiv_pages)} of {len(pages)}")
        if hiv_pages:
            print("      " + ", ".join(str(p) for p in hiv_pages[:40])
                  + (f" and {len(hiv_pages) - 40} more" if len(hiv_pages) > 40 else ""))

        # Round four's own test for a sub-national table, applied page by page instead of by
        # hand, and reported together with the HIV test so the pages that pass both are visible.
        both: List[Tuple[int, int]] = []
        for i, text in enumerate(lowered):
            named = sum(1 for u in units if re.search(u, text))
            if named >= 4:
                both.append((i + 1, named))
        print(f"pages naming four or more of this country's own regions  {len(both)}")
        for page_no, named in both[:40]:
            hiv = "HIV too" if re.search(r"vih|sida|hiv", lowered[page_no - 1]) else ""
            print(f"      page {page_no:>4}  {named} regions  {hiv}")
        if len(both) > 40:
            print(f"      and {len(both) - 40} more")


COUNTRIES = ("chad", "guinea", "niger")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--countries", default=",".join(COUNTRIES),
                    help=f"comma-separated subset of {', '.join(COUNTRIES)}")
    ap.add_argument("--no-download", action="store_true",
                    help="characterise the files already cached and fetch nothing")
    ap.add_argument("--list-only", action="store_true",
                    help="print the discovery report and stop, downloading nothing")
    ap.add_argument("--raw-dir", default=str(RAW_ROOT),
                    help=f"cache root (default {RAW_ROOT})")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    wanted = [c.strip().lower() for c in args.countries.split(",") if c.strip()]
    unknown = [c for c in wanted if c not in COUNTRIES]
    if unknown:
        print(f"unknown country name(s) {unknown}, pick from {', '.join(COUNTRIES)}")
        return 2

    root = Path(args.raw_dir)
    fetcher = YearbookFetcher()
    print("Chad, Guinea and Niger health statistics yearbook survey")
    print(f"cache root  {root.resolve()}")
    print(f"countries   {', '.join(wanted)}")
    print("This script writes only inside the cache root and reads nothing from data/panel/.")

    plan = {
        "chad": (root / "chad" / "inseed", CHAD_CAPTIONS, CHAD_UNITS),
        "guinea": (root / "guinea" / "ins", GUINEA_CAPTIONS, GUINEA_UNITS),
        "niger": (root / "niger" / "ins", NIGER_CAPTIONS, NIGER_UNITS),
    }

    found: Dict[str, List[Tuple[str, str]]] = {c: [] for c in wanted}
    chad_manifest: List[dict] = []
    if args.no_download:
        print("\n--no-download given, so discovery is skipped entirely.")
    else:
        if "chad" in wanted:
            found["chad"] = discover_chad(fetcher, chad_manifest)
        if "guinea" in wanted:
            found["guinea"] = discover_site(fetcher, GUINEA_ROOT, "Guinea, stat-guinee.org")
        if "niger" in wanted:
            found["niger"] = discover_site(fetcher, NIGER_ROOT, "Niger, stat-niger.org")

    if args.list_only:
        print("\n--list-only given, so nothing was downloaded.")
        return 0

    if not args.no_download:
        for country in wanted:
            dest, _captions, _units = plan[country]
            print(f"\n=== caching, {country} ===")
            if not found[country]:
                print("  nothing to cache, discovery found no yearbook link")
                continue
            cache(fetcher, found[country], dest)
            if country == "chad" and chad_manifest:
                write_chad_manifest(chad_manifest, dest)

    cached: Dict[str, List[Path]] = {}
    for country in wanted:
        dest, captions, units = plan[country]
        print(f"\n=== text layer, {country} ===")
        files = sorted(dest.glob("*.pdf")) if dest.exists() else []
        cached[country] = files
        if not files:
            print(f"nothing cached in {dest}")
            continue
        for path in files:
            characterise(path, captions, units)

    print("\n=== summary ===")
    for country in wanted:
        print(f"{country:<8} yearbooks cached  {len(cached.get(country, []))}")
    print("Hand this whole output back, and the three parsers get written against the pages, "
          "captions and region counts it names.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
