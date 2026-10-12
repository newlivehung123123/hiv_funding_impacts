#!/usr/bin/env python3
"""
Discover, cache and characterise Cameroon's two HIV document families, so the two
connectors can be written against real extracted text and not against a description of it.

Why this script exists. Round one of the West and Central Africa survey opened the 2024 CNLS
annual report on 15 August 2026 and recorded its table numbers and figures, and round four read
the UNAIDS spending-assessment index on 30 September 2026 and recorded eight Cameroon years.
Neither round saved a file. `data/raw/` holds no Cameroon document of either family, so the
table parsers cannot be written, because a PDF table parser depends on the header wording, the
column order and the line layout the extraction library produces, and none of the three can be
guessed from a prose summary. The Cambodia connector's parser was written against cached files
and its docstring records the editions it was verified on, which is the standard this build is
held to. Round one also established that a first automated read of the 2024 CNLS report called
the file scanned images and was wrong, which is the second reason the text layer is measured
here and not asserted. Round one read the tables with `pypdf`, and this survey reads them with
`pdfplumber`, because `pdfplumber` is what the Cambodia parser uses for table geometry, so
whether `pdfplumber` finds the same tables `pypdf` found is itself one of the open questions.

What this script does.

  1. Discovers the CNLS annual-report PDFs from `https://cnls.cm/catdocument/rapports-annuels/`
     and caches them under `data/raw/cameroon/cnls/`.
  2. Discovers Cameroon's spending-assessment reports from the UNAIDS index at
     `https://www.unaids.org/en/dataanalysis/knowyourresponse/nasacountryreports` and caches
     them under `data/raw/cameroon/nasa/`.
  3. Characterises every cached PDF, printing page count, bytes, extracted characters, whether
     digits survive extraction, how many tables `pdfplumber` finds, and which pages carry the
     captions the two connectors need.

What this script does not do. It writes nothing outside `data/raw/cameroon/`, touches no file
under `data/panel/`, computes no panel row and runs no part of the pipeline. A file already
present is left alone and characterised as it stands, so a vetted copy always wins and a second
run costs no download.

Both discovery pages are printed in full when a discovery finds nothing, because a page whose
markup has changed should produce a readable report and not an empty list. The anchor text of
every PDF link is printed beside the href either way, since round one established that the CNLS
page carries annual reports for 2024, 2023 and 2016 alongside an entry labelled 2021 that is the
2021 to 2023 strategic plan and not an annual report. That entry is downloaded like the rest and
then excluded by hand, because a filename cannot be trusted to say which of the two a file is.

Usage, from the project root.

    python3 scripts/survey_cameroon_reports.py
    python3 scripts/survey_cameroon_reports.py --no-download     # characterise what is cached
    python3 scripts/survey_cameroon_reports.py --list-only       # discovery report, no download
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hivimpact.connector_base import BaseConnector  # noqa: E402

log = logging.getLogger("hivimpact")

CNLS_INDEX = "https://cnls.cm/catdocument/rapports-annuels/"
NASA_INDEX = "https://www.unaids.org/en/dataanalysis/knowyourresponse/nasacountryreports"

RAW_ROOT = Path("data/raw/cameroon")

# An anchor carrying a PDF href, with the anchor's own inner text, so a document can be
# identified by its label and not by its filename alone.
_ANCHOR_RE = re.compile(
    r'<a\b[^>]*href=["\']([^"\']+?\.pdf[^"\']*)["\'][^>]*>(.*?)</a>',
    re.I | re.S,
)
# A bare PDF href, for a page that builds its links without an anchor body.
_HREF_RE = re.compile(r'href=["\']([^"\']+?\.pdf[^"\']*)["\']', re.I)
_TAG_RE = re.compile(r"<[^>]+>")

# Captions the CNLS connector needs, from the round-one read of the 2024 edition recorded in
# `docs/PHASE4_FEASIBILITY_WCA.md`. The French and the English editions of the same document are
# both published, so each caption is matched on the table number and a language-independent
# "tabl" stem, never on a full caption string. Table numbering is not assumed to hold across
# editions, which is why every number is reported per page and checked against the keywords
# below before a parser is pinned to a number.
CNLS_CAPTIONS: List[Tuple[str, str]] = [
    ("Table 38, active ART file by region, sex and children", r"tabl\w*\s*38\b"),
    ("Table 40, 12-month retention by region", r"tabl\w*\s*40\b"),
    ("Table 41, community dispensation by region and quarter", r"tabl\w*\s*41\b"),
    ("Table 42, viral-load coverage and suppression by region", r"tabl\w*\s*42\b"),
    ("Table 18, key populations screened, positive and linked", r"tabl\w*\s*18\b"),
    ("Table 46, funding by source in CFA francs", r"tabl\w*\s*46\b"),
    ("Tables 47 to 49, execution against budget", r"tabl\w*\s*4[789]\b"),
    ("Tables 14 and 16, condom distribution and testing",
     r"tabl\w*\s*1[46]\b"),
    ("Tables 19, 21 and 23, positivity and self-testing",
     r"tabl\w*\s*(19|21|23)\b"),
    ("Tables 27, 28 and 30, PMTCT and early infant diagnosis",
     r"tabl\w*\s*(27|28|30)\b"),
    ("Tables 32 and 33, infant prophylaxis", r"tabl\w*\s*3[23]\b"),
]

# Words that should appear on a page carrying the regional cascade, in either language, as a
# second check that a numbered caption is the table round one described.
CNLS_KEYWORDS: List[Tuple[str, str]] = [
    ("a region name", r"adamaoua|adamawa|littoral|extr[eê]me[- ]nord|far north|nord[- ]ouest|north[- ]west"),
    ("the active file", r"file active|active file|patients? actifs?"),
    ("viral load", r"charge virale|viral load"),
    ("a key population", r"travailleu|sex work|hsh|msm|transgenre|transgender"),
    ("money in CFA francs", r"fcfa|xaf|francs? cfa"),
]

NASA_KEYWORDS: List[Tuple[str, str]] = [
    ("a financing-source split", r"source de financement|financing source|sources? de financement"),
    ("a spending category", r"cat[eé]gorie de d[eé]pense|spending categor|aids spending categor"),
    ("a beneficiary population", r"population b[eé]n[eé]ficiaire|beneficiary population"),
    ("a financing agent", r"agent de financement|financing agent"),
    ("money in CFA francs", r"fcfa|xaf|francs? cfa"),
    ("a year label", r"\b20(0[5-9]|1\d|2\d)\b"),
]


class ReportFetcher(BaseConnector):
    """HTTP on the project's own session, headers, retries and timeout."""

    source_id = "cm_survey"
    timeout = 120


def _strip_tags(s: str) -> str:
    return re.sub(r"\s+", " ", _TAG_RE.sub(" ", s)).strip()


def _absolute(href: str, page_url: str) -> str:
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("//"):
        return "https:" + href
    root = re.match(r"(https?://[^/]+)", page_url)
    base = root.group(1) if root else ""
    if href.startswith("/"):
        return base + href
    return page_url.rsplit("/", 1)[0] + "/" + href


def _report_other_links(html: str, page_url: str, require: Optional[str]) -> None:
    """Print the non-PDF links that mention the thing being looked for.

    An index page can list a landing page for each country and put the document one click
    further in, in which case no PDF href exists on the index and the useful output is the list
    of candidate landing pages. Printing those turns a failed discovery into a usable result
    from one run, instead of costing a second run to find out the page is built that way.
    """
    if require is None:
        return
    anchors = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.I | re.S)
    hits: List[Tuple[str, str]] = []
    seen = set()
    for href, body in anchors:
        text = _strip_tags(body)
        if not (re.search(require, href, re.I) or re.search(require, text, re.I)):
            continue
        url = _absolute(href, page_url)
        if url in seen:
            continue
        seen.add(url)
        hits.append((url, text))
    if not hits:
        print(f"no non-PDF link matches {require!r} either")
        return
    print(f"{len(hits)} non-PDF link(s) match {require!r}, which may be landing pages")
    for url, text in hits[:40]:
        print(f"  {url}")
        if text:
            print(f"        text  {text[:140]}")
    if len(hits) > 40:
        print(f"  and {len(hits) - 40} more")


def discover(fetcher: ReportFetcher, page_url: str, label: str,
             require: Optional[str] = None) -> List[Tuple[str, str]]:
    """Return a list of (url, anchor text) for every PDF link on one page.

    `require` is a regular expression a link must match, on the href or on the anchor text, for
    the link to be kept. The Cameroon filter is applied to the UNAIDS index, which lists every
    country, and no filter is applied to the CNLS page, which is Cameroon's own.
    """
    print(f"\n=== discovery, {label} ===")
    print(f"page  {page_url}")
    try:
        html = fetcher.get_text(page_url)
    except Exception as exc:
        print(f"FAILED to read the page: {exc}")
        return []
    print(f"read  {len(html):,} bytes of HTML")

    found: Dict[str, str] = {}
    for href, body in _ANCHOR_RE.findall(html):
        found.setdefault(_absolute(href, page_url), _strip_tags(body))
    for href in _HREF_RE.findall(html):
        found.setdefault(_absolute(href, page_url), "")

    if not found:
        print("no PDF link on the page at all.")
        _report_other_links(html, page_url, require)
        print("the whole page follows, so the markup can be read")
        print("-" * 70)
        print(html[:20000])
        print("-" * 70)
        return []

    print(f"{len(found)} PDF link(s) on the page")
    kept: List[Tuple[str, str]] = []
    for url in sorted(found):
        text = found[url]
        hit = True
        if require is not None:
            hit = bool(re.search(require, url, re.I) or re.search(require, text, re.I))
        mark = "KEEP" if hit else "    "
        print(f"  {mark}  {url}")
        if text:
            print(f"        text  {text[:140]}")
        if hit:
            kept.append((url, text))

    if require is not None and not kept:
        print(f"\nNo PDF link matched {require!r}. Every PDF link is printed above, so the right "
              "one can be named by hand if the index labels Cameroon differently.")
        _report_other_links(html, page_url, require)
    return kept


def _local_name(url: str) -> str:
    """Flatten a URL's path into one filename, following `cambodia_nchads.py`.

    A basename alone is not safe, because a WordPress media library stores one year of reports
    under `/wp-content/uploads/2025/06/` and the next under `/wp-content/uploads/2024/06/`, and
    two editions published under the same basename would overwrite each other. The path after
    `/uploads/` is kept and flattened, so the year directories survive in the filename.
    """
    path = url.split("?", 1)[0]
    path = re.sub(r"^https?://[^/]+", "", path)
    marker = "/uploads/"
    tail = path.split(marker, 1)[1] if marker in path else path.lstrip("/")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", tail.replace("/", "_"))
    return name or "report.pdf"


def cache(fetcher: ReportFetcher, urls: List[Tuple[str, str]], dest_dir: Path) -> List[Path]:
    """Download each URL into `dest_dir`, skipping a file already on disk."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    for url, _text in urls:
        dest = dest_dir / _local_name(url)
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


def characterise(path: Path, captions: List[Tuple[str, str]],
                 keywords: List[Tuple[str, str]]) -> None:
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

        joined = "\n".join(page_text).lower()
        if captions:
            print("captions, by page number as pdfplumber indexes them from 1")
            for label, pattern in captions:
                hits = [i + 1 for i, t in enumerate(page_text)
                        if re.search(pattern, t.lower())]
                shown = ", ".join(str(h) for h in hits[:12]) if hits else "NOT FOUND"
                more = f" and {len(hits) - 12} more" if len(hits) > 12 else ""
                print(f"  {label:<58} {shown}{more}")
        if keywords:
            print("keywords, present or absent in the whole document")
            for label, pattern in keywords:
                found = "yes" if re.search(pattern, joined) else "NO"
                print(f"  {label:<58} {found}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-download", action="store_true",
                    help="characterise the files already cached and fetch nothing")
    ap.add_argument("--list-only", action="store_true",
                    help="print the discovery report and stop, downloading nothing")
    ap.add_argument("--raw-dir", default=str(RAW_ROOT),
                    help=f"cache root (default {RAW_ROOT})")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    root = Path(args.raw_dir)
    cnls_dir = root / "cnls"
    nasa_dir = root / "nasa"
    fetcher = ReportFetcher()

    print("Cameroon document survey")
    print(f"cache root  {root.resolve()}")
    print("This script writes only inside the cache root and reads nothing from data/panel/.")

    if args.no_download:
        cnls_urls: List[Tuple[str, str]] = []
        nasa_urls: List[Tuple[str, str]] = []
        print("\n--no-download given, so discovery is skipped entirely.")
    else:
        cnls_urls = discover(fetcher, CNLS_INDEX, "CNLS annual reports")
        nasa_urls = discover(fetcher, NASA_INDEX, "UNAIDS spending-assessment index",
                             require=r"cameroon|cameroun|\bcmr\b")

    if args.list_only:
        print("\n--list-only given, so nothing was downloaded.")
        return 0

    if not args.no_download:
        print("\n=== caching, CNLS ===")
        cache(fetcher, cnls_urls, cnls_dir)
        print("\n=== caching, spending assessment ===")
        cache(fetcher, nasa_urls, nasa_dir)

    print("\n=== text layer, CNLS annual reports ===")
    cnls_files = sorted(cnls_dir.glob("*.pdf")) if cnls_dir.exists() else []
    if not cnls_files:
        print(f"nothing cached in {cnls_dir}")
    for p in cnls_files:
        characterise(p, CNLS_CAPTIONS, CNLS_KEYWORDS)

    print("\n=== text layer, spending-assessment reports ===")
    nasa_files = sorted(nasa_dir.glob("*.pdf")) if nasa_dir.exists() else []
    if not nasa_files:
        print(f"nothing cached in {nasa_dir}")
    for p in nasa_files:
        characterise(p, [], NASA_KEYWORDS)

    print("\n=== summary ===")
    print(f"CNLS annual reports cached            {len(cnls_files)}")
    print(f"spending-assessment reports cached    {len(nasa_files)}")
    print("Hand this whole output back, and the two parsers get written against the pages and "
          "captions it names.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
