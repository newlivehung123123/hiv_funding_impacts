"""
ForeignAssistance.gov connector — US government's OWN reporting of HIV funding, by agency.

THE ROUTE, REBUILT ON 27 SEPTEMBER 2026

This connector used to parse a 3.7 gigabyte CSV that Jason downloaded by hand, because
foreignassistance.gov answers every non-browser client with HTTP 403 and the header
`cf-mitigated: challenge`. The challenge covers the Data API and the bulk CSV alike, so the
manual download was a consequence of Cloudflare and not of a missing API.

Every US government agency republishes the same transactions as IATI XML on Amazon S3,
outside the challenge, and the IATI Registry gives the address of every file. Those files
are ForeignAssistance.gov's own output and not a third party's copy: they carry elements in
the namespace `https://foreignassistance.gov`, among them `treasury-account` naming the
appropriation with a `fiscal-funding-year` child. So this connector now discovers the US
publishers in the registry, downloads their XML from S3, and parses it. Nothing is
downloaded by hand on a normal run.

WHAT THE ROUTE PROVES, AND WHERE IT STOPS

The Nigeria reconciliation of 26 and 27 September 2026 tested the S3 files against the
ForeignAssistance.gov Data API read from a browser. Three publishers reproduce the API:

    Department of State           exact in all 13 years FY2012-FY2026
    Health and Human Services     exact in all 14 years FY2012-FY2025
    USAID                         within 173 USD in FY2020-FY2024, short before FY2020

Those three carry 98.2 per cent of all US HIV disbursements. USAID's files fall short by up
to 2.9 per cent from FY2013 to FY2019 and hold nothing at all before FY2013, and the cause
is not a file that went unread. Every one of that publisher's 208 files that could hold
Nigeria money was read and the shortfall survives, so it is a limit of what USAID publishes.
The money that is missing is mostly operating cost booked to different lines in the two
sources, and neither award number nor activity title joins the two for the older years.

So the S3 route cannot supply the early years, and `HISTORY_FILE` does. That file is a small
extract of the Complete Data Set Jason downloaded on 18 July 2026, made once by
`scripts/extract_fa_history.py`, and it is the authority for every agency-year the S3 route
has not been proven on. `PROVEN_WINDOW` holds the first fiscal year each bucket is read from
S3. The manual download therefore becomes a one-off and not a step in the pipeline.

MANAGING AGENCY, NOT FUNDING AGENCY

The distinction is load-bearing and survives the rebuild. PEPFAR is appropriated to the State
Department's Global Health Programs account, so a split on funding agency puts 102bn USD under
State and tells you nothing. Managing agency records who spent it. In the XML the managing
agency is `reporting-org ref`, which is `US-GOV-1` for USAID, `US-GOV-11` for State and
`US-GOV-14` for Health and Human Services. The funding agency is `participating-org` role 1,
and this connector does not read it.

THE BUCKET THAT CHANGED, AND WHY

The CSV carried a managing SUB-AGENCY column, so the old connector could restrict Health and
Human Services to CDC and emit `external_hiv_oda_us_cdc`. The XML carries no sub-agency at
all. `participating-org` roles 2 and 3 both give `US-GOV-14`, the department, and the only
CDC signal in the file is the `treasury-account` code, which names the appropriation and is
therefore the funding basis this connector rejects. So the bucket is now the whole department
and the series is `external_hiv_oda_us_hhs`, replacing `external_hiv_oda_us_cdc`. CDC is
38.5bn USD of the department's 43.1bn, so the two are close, and they are not the same thing.
`_other_agency` loses NIH and HRSA to `_hhs` and the four series still partition the total.

THE SPLIT, AND THE TRAP IT SETS

HIV-labelled disbursements, FY2024 to FY2025, current USD m, countries only:

    USAID   2,037.0 -> 1,379.2   -32.3%
    HHS     1,510.2 -> 1,356.8   -10.2%
    State       6.4 ->   270.7
    other     105.8 ->    77.9
    total   3,659.4 -> 3,084.6   -15.7%

The trap is the State line. The Bureau of Global Health Security and Diplomacy absorbed
USAID's global health programmes in 2025, and disbursements managed by State go from about
6m USD in FY2024 to 271m in FY2025. Part of what left USAID did not leave the US government,
it was reclassified. Zimbabwe is the clearest case: USAID -40.9m, State +47.6m, country total
up 3.9%. A USAID series read on its own overstates the cut and a country total hides it.

THE AWARD REPORTED TWICE, AND THE SUBTRACTION THAT REMOVES IT

From FY2025 the Department of State and USAID both publish the same Nigeria bilateral awards
under different identifiers, `US-GOV-11-72062020CA00001-227505` against
`US-GOV-1-72062020CA00001`. The API does not choose between the two agencies. It takes the
State figure away from the USAID figure: FY2025 USAID 4,629,063 in the files against 3,651,931
in the API, and 4,629,063 less State's 977,134 is 3,651,929. So the connector subtracts the
whole State country total from the whole USAID country total in a fiscal year where the files
themselves show an overlap, and carries the unadjusted USAID figure in `extra`. That
reproduces the API to 142,135 USD at FY2025, which is 0.096 per cent, and to 59 USD at FY2026,
sign included.

The trigger has to be evidence inside the files, which is a State activity whose award number
USAID also publishes for the same country and fiscal year. Subtracting in every year instead
would delete State's FY2012-FY2018 money, all of which sits in one activity whose award number
is redacted and which USAID does not publish.

The sign of the State figure changes nothing, and a guard added on 27 September 2026 to skip a
negative State figure was wrong and was removed the same day. A State country-year below zero
is a year of recoveries and deobligations, and skipping the subtraction there looks prudent
because Papua New Guinea FY2025 turns a raw USAID figure of minus 7,782 USD into a positive
2,487,146 once State's minus 2,494,928 is taken away. ForeignAssistance.gov publishes
2,487,154 for that country-year. The Nepal files give 6,972,368 against the API's 6,972,374,
and the Indonesia files give 6,639,936 against 6,639,952. The USAID file reports State's
transactions as well as USAID's, so removing State recovers USAID's own money whatever the
sign, and leaving a negative State figure in place counts that money twice, once in the State
series and once inside the USAID series. The country total is where the damage shows. Papua
New Guinea's four agency series sum to minus 2,403,586 when the subtraction is skipped and to
91,342 when the subtraction runs, against the API's 91,350.

The result is not floored at zero either, for the same reason. A floor fired on none of the 48
adjusted country-years in the run of 27 September 2026, and the smallest result was Colombia
at 233,006 USD, so the floor was doing no work. A floor that did fire would move a country-year
away from what the API publishes, which is the fault the sign guard had already introduced.

DEDUPLICATION USES THE WHOLE TRANSACTION ROW

The key is the activity identifier, the transaction `ref`, the transaction date, the value and
the receiver organisation narrative together. USAID publishes five FY2026 Nigeria HIV
disbursements worth 15,851,027 USD together twice over, each repeat carrying the same `ref`,
date, value and receiver as the original while the API counts each payment once. Every repeat
sits in the same file as the original, four pairs worth 15,649,184 USD in
`iati-activities-Multiple_Countries-34.xml` and the fifth pair worth 201,843 USD in
`iati-activities-Nigeria.xml`. Deduplicating on the transaction `ref` alone destroys the State
reconciliation instead, because State attaches one `ref` to transactions differing in date, in
value and in receiver, and a `ref` key moves FY2012 from 623,717 to 551,282 USD and breaks
seven of 13 otherwise-exact State years.

A run reporting zero duplicates has to be read against its own year window before anyone
concludes the key is dormant. `scripts/check_fa_dedup.py` measured all three candidate keys
against USAID's 206 Nigeria files on 27 September 2026. Over FY2000 to FY2025, on 4,745 HIV
disbursements worth 1,644,535,037 USD gross, the whole-row key dropped nothing, because the
five duplicates are FY2026 and sat outside that window, which is also why a panel run ending at
FY2025 reports zero. Over FY2000 to FY2026, on 4,901 disbursements worth 1,775,318,599 USD, the
whole-row key drops the five and 15,851,027 USD. The same measurement settles the third
candidate, because the activity identifier alone drops 4,302 transactions worth 1,714,872,573
USD, which is 87.78 per cent of Nigeria's USAID HIV money and would leave 60,446,026 USD where
the truth is 1.78bn.

THE HIV TEST BELONGS ON THE TRANSACTION

Award `AID-OAA-TO-15-00009`, the Malaria task order of the Global Health Supply Chain
contract, holds 11 Nigeria disbursements worth 35.09m USD, of which two carry DAC purpose code
13040 and sum to 9,016,197 USD, exactly what the API attributes to HIV for that award. All 11
carry the USG sector narrative Malaria. An activity-level test takes all 35.09m or none of it.
Note also that the DAC code in the XML is the PURPOSE code 13040, not ForeignAssistance.gov's
sector code 134, and 13040 begins 130, so a prefix test on 134 matches nothing.

GRAIN AND DOUBLE COUNTING

The four agency series partition the country total and sum back to `external_hiv_oda_us`,
which this connector also emits. Anything totalling the panel takes one level or the other,
never both. `external_hiv_oda_us` is also emitted by the OECD CRS connector from a different
source, so filter on source_id before summing.

MEASURED ON THE FIRST FULL RUN, 27 SEPTEMBER 2026

The registry listed 2,116 publishers, 21 of them US government, and those 21 registered 2,041
files of which 20 are Worldwide and skipped. The corpus on disk is 2,723 megabytes over 2,014
files, 1,746 of those megabytes USAID's and 370 State's. Throughput on these buckets has varied
by more than two orders of magnitude between fetches of the same file, so the first run is slow.
Every file is cached by ETag under data/raw/foreign_assistance/iati/, so a rerun re-fetches only
what moved.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import logging
import statistics
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

import requests

from ..connector_base import BaseConnector
from ..normalize import code_to_iso3, name_for, to_iso3
from ..schema import PanelRow, SourceType

log = logging.getLogger("hivimpact")

TOTAL = "external_hiv_oda_us"

REGISTRY_ORGS = "https://iatiregistry.org/api/3/action/organization_list"
REGISTRY_PKGS = "https://iatiregistry.org/api/3/action/package_search"

# the registry listed 2,116 publishers on 27 September 2026, of which exactly 21 carry an
# identifier beginning US-GOV. The count is not a filter — every publisher the registry
# returns is read — it is a tripwire, because a publisher that quietly leaves the registry
# takes its money out of the panel without any other symptom.
US_PUBLISHER_PREFIX = "US-GOV"
US_PUBLISHERS_EXPECTED = 21

# managing agency -> bucket. Matched on the whole reference and never on a prefix, because
# US-GOV-11 starts with US-GOV-1 and a prefix test files every State dollar under USAID.
USAID, HHS, STATE, OTHER = "usaid", "hhs", "state", "other_agency"
BUCKETS = (USAID, HHS, STATE, OTHER)
REPORTING_ORG_BUCKET = {"US-GOV-1": USAID, "US-GOV-11": STATE, "US-GOV-14": HHS}

AGENCY_LABEL = {USAID: "USAID", HHS: "Health and Human Services",
                STATE: "State Department", OTHER: "other US agencies"}

# The first fiscal year each bucket is read from the S3 files. Before it the bucket comes from
# HISTORY_FILE. Measured for Nigeria against the ForeignAssistance.gov Data API on 26 and 27
# September 2026; `other_agency` has no entry because the four publishers behind it — Defense,
# the Peace Corps, Labor and the African Development Foundation, 1.8 per cent of US HIV money —
# were never tested on this route, so nothing about them is proven and the history serves them
# for every year it holds.
PROVEN_WINDOW = {USAID: 2020, HHS: 2012, STATE: 2012}

HISTORY_FILE = "history_fa_gov.csv"

# how often the download and the parse say where they are. The corpus is 2,723 megabytes over
# 2,015 files and both phases take a long time, so a run that reports only failures is
# indistinguishable from a run that has hung.
PROGRESS_EVERY = 100

# a year totalling less than this share of the median of the three before it is a part year
PARTIAL_YEAR_RATIO = 0.60

# how far an S3 figure may sit from the frozen history's figure for the same bucket-country-year
# before the run says so. 0.02 is wide enough for the rounding the two sources genuinely differ
# by and narrow enough to catch a parsing fault.
HISTORY_AGREEMENT_TOLERANCE = 0.02

HISTORY_DISAGREEMENT_NOTE = (
    "the IATI files on Amazon S3 and the frozen extract of ForeignAssistance.gov's Complete "
    "Data Set report different amounts for this agency, country and fiscal year, by more than "
    "2 per cent, in a fiscal year the Nigeria reconciliation of September 2026 proved for this "
    "agency. The figure in `value` is the one read from the IATI files, and the extract's "
    "figure is carried here beside it. Which of the two sources is right for this country and "
    "year is not yet settled, so treat this agency series as uncertain here and read the "
    "country total, which the disagreement also moves."
)

HISTORY_DISAGREEMENT_TOTAL_NOTE = (
    "at least one agency series behind this country total disagrees with the frozen extract of "
    "ForeignAssistance.gov's Complete Data Set by more than 2 per cent in a fiscal year the "
    "Nigeria reconciliation of September 2026 proved for that agency. The disagreeing agencies "
    "are named in `history_disagreement_buckets` and each carries both figures on its own row."
)


def resolve_country(code: str) -> Optional[str]:
    """The ISO3 code one IATI `recipient-country` code names, or None when the code names no
    country the panel can hold.

    The United States publishers write ForeignAssistance.gov's own numeric country list into
    `recipient-country`, and ForeignAssistance.gov's numbers are not the IATI codelist and not
    UN M49. `code_to_iso3` holds the codes that list explains and answers nothing for the rest.
    The fallback to `to_iso3` is here so that an alphabetic code or a country name that
    `code_to_iso3` does not hold still resolves, and sending a numeric code to `to_iso3` instead
    reinterprets the number under UN M49, where 798 is Tuvalu and 498 is Moldova. Before
    27 September 2026 the fallback ran on numeric codes too and put 65,997,099 USD into the
    panel that way, 65,951,587 of it into Tuvalu, a state of about 11,000 people that receives
    no United States HIV money at all and that ForeignAssistance.gov reports none for. The
    corpus carries 22 numeric codes and only 798 and 498 collide with an M49 number, so the
    other 20, among them 998 and the regional codes ending in 89, were already dropped here.
    A real country always arrives as an alphabetic code, so refusing the fallback on an
    all-digit code loses no money and ends the contamination.
    """
    raw = (code or "").strip()
    if not raw:
        return None
    direct = code_to_iso3(raw)
    if direct:
        return direct
    if raw.isdigit():
        return None
    return to_iso3(raw)


NON_POSITIVE_NOTE = (
    "a non-positive disbursement figure is not a gap: ForeignAssistance.gov books recoveries "
    "and deobligations as negative disbursements, so a year in which more was recovered than "
    "paid out nets below zero."
)

INTERPRETATION = (
    "US self-reported HIV disbursements, split by the agency that MANAGED the money and not "
    "the account it was appropriated to. PEPFAR is appropriated to State, so a split on "
    "funding agency puts nearly everything there and separates nothing. Read the USAID fall "
    "against the State series before calling it a cut: the Bureau of Global Health Security "
    "and Diplomacy took over USAID's global health programmes in 2025, and State-managed "
    "disbursements go from about 6m USD in FY2024 to 271m in FY2025. Part of what left USAID "
    "was reclassified, not withdrawn. Nominal USD, not deflated."
)


# -- registry and S3 ------------------------------------------------------------------------

def encode_url(url: str) -> str:
    """Encode a registry URL so Amazon S3 matches the key.

    Two encodings in the registry's own URLs break a naive fetcher, and they pull in opposite
    directions. Paths carry literal spaces, which Python's urllib refuses outright, so the path
    has to be quoted. Paths also carry literal plus signs, and quoting turns a plus into %2B,
    which S3 answers 403 on because S3 reads a plus in a key as a space. Quoting with the plus
    left safe fetches both classes. A connector that quoted every URL without this would have
    lost the 63 plus-carrying files silently.
    """
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, urllib.parse.quote(parts.path, safe="/+"),
         parts.query, parts.fragment))


def object_url(url: str) -> str:
    """Rewrite an Amazon S3 console link into the address of the object the console displays.

    The IATI Registry does not always hold the address of a file. The Department of Defence
    registers its `Africa North of Sahara` file as a link to the Amazon S3 web console,
    `https://us-east-1.console.aws.amazon.com/s3/object/iati-reporting?region=us-east-1&prefix=<key>`.
    A browser follows that link to a sign-in page and a script fetches 1,158 bytes of console
    HTML, which the XML parser then rejects as a malformed file. The registry record is the
    defect and the object itself is fine, because the bucket, the region and the key are all
    written in the console link and the object address built out of the bucket, the region and
    the key answers 200.

    The rewrite fires only on a console host with a path of the form `/s3/object/<bucket>`, so a
    console link to a folder listing, which uses `/s3/buckets/<bucket>`, is left alone rather
    than turned into an address for an object that does not exist. Every other URL is returned
    unchanged.

    A query string reads a plus sign as a space, so `parse_qs` returns the key with real spaces
    in it, and `encode_url` later quotes those spaces as %20. The cache filename that
    `_cache_path` builds is the same either way, because a space and a plus are both replaced by
    an underscore, so the rewrite does not strand the copy already on disk under a second name.
    """
    parts = urllib.parse.urlsplit(url)
    if not parts.netloc.endswith("console.aws.amazon.com"):
        return url
    segments = [s for s in parts.path.split("/") if s]
    if len(segments) < 3 or segments[0] != "s3" or segments[1] != "object":
        return url
    bucket = segments[2]
    query = urllib.parse.parse_qs(parts.query)
    key = (query.get("prefix") or [""])[0].lstrip("/")
    region = (query.get("region") or [""])[0]
    if not bucket or not key:
        return url
    host = f"{bucket}.s3.{region}.amazonaws.com" if region else f"{bucket}.s3.amazonaws.com"
    return urllib.parse.urlunsplit(("https", host, "/" + key, "", ""))


def distinct_name(filename: str, url: str) -> str:
    """A second local name for a file whose name a publisher has already used for another file.

    The cache stores one file per publisher and filename, so two different files sharing a
    filename inside one publisher would overwrite each other and the second download would
    destroy the first. Eight characters of the digest of the URL make the second name distinct
    and make the same URL produce the same name on every run, so a rerun serves the file from
    cache instead of fetching a new copy under a new name.
    """
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    stem, dot, extension = filename.rpartition(".")
    return f"{stem}-{digest}.{extension}" if dot else f"{filename}-{digest}"


def served_name(url: str) -> str:
    """The filename the host serves, which is the only reliable classifier.

    The registry package title and the served filename disagree, and a file whose name is
    truncated short of a word defeats a substring test on the title: USAID's
    `iati-activities-Eastern+and+Central+Africa+Regio.xml` is a region file whose name never
    contains the word region.
    """
    return urllib.parse.unquote(url.rsplit("/", 1)[-1].split("?", 1)[0])


def is_worldwide(filename: str) -> bool:
    """The files named Worldwide carry no country the panel can read and are skipped.

    State's Worldwide-2 holds 5,127 activities whose 13,723 country-coded transactions every
    one name code 998, countries unspecified, and neither Worldwide file holds a Nigeria HIV
    dollar. Skipping them saves 72.6 of USAID's 1,891.1 megabytes.
    """
    stem = filename.lower()
    for prefix in ("iati-activities-", "iati-organisations-"):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
    return stem.startswith("worldwide")


class ForeignAssistanceConnector(BaseConnector):
    source_id = "foreign_assistance"
    default_source_type = SourceType.EXPENDITURE_ACCOUNT
    description = ("ForeignAssistance.gov — US self-reported HIV disbursements by country and "
                   "managing agency, read as IATI XML from Amazon S3.")

    # the S3 buckets are slow by nature and a single file can run to 100 megabytes
    timeout = 900

    def __init__(self, raw_dir: str = "data/raw/foreign_assistance", workers: int = 6, **kw):
        super().__init__(**kw)
        self.raw_dir = Path(raw_dir)
        self.xml_dir = self.raw_dir / "iati"
        self.workers = workers
        self._local = threading.local()
        self._manifest: Dict[str, dict] = {}
        self._file_notes: List[dict] = []
        #: country-year -> the USAID total before the State subtraction, filled by
        #: _subtract_overlap and carried into extra by _emit
        self._unadjusted: Dict[Tuple[str, int], float] = {}
        # every bucket-country-year where the S3 files and the frozen history disagree inside a
        # proven window, kept so that `_emit` can put the disagreement on the row it affects
        self._disagreements: Dict[Tuple[str, int, str], Tuple[float, float]] = {}
        # every all-digit recipient-country code the run dropped, counted so that the log names
        # the codes and a publisher moving to a new numbering shows up instead of resolving to
        # whatever country shares the number under UN M49. See `resolve_country`.
        self._numeric_codes: Dict[str, int] = collections.Counter()

    # -- HTTP ---------------------------------------------------------------------------
    @property
    def _session(self) -> requests.Session:
        """One session per thread. requests.Session is not safe to share across threads and
        the download runs several at once."""
        session = getattr(self._local, "session", None)
        if session is None:
            session = requests.Session()
            session.headers.update(self.session.headers)
            self._local.session = session
        return session

    # -- discovery ----------------------------------------------------------------------
    def _publishers(self) -> List[dict]:
        """Every registry publisher whose IATI identifier begins US-GOV.

        Discovered and not hardcoded. A hardcoded list of 21 slugs would go stale silently the
        first time a department renamed itself, and the failure would look like a department
        that had stopped spending.
        """
        found: List[dict] = []
        offset = 0
        while True:
            page = self.get_json(REGISTRY_ORGS, params={
                "all_fields": "true", "include_extras": "true",
                "limit": 1000, "offset": offset})["result"]
            if not page:
                break
            found.extend(page)
            offset += len(page)
            if len(page) < 1000:
                break
        us = [o for o in found
              if str(o.get("publisher_iati_id") or "").upper().startswith(US_PUBLISHER_PREFIX)]
        log.info("foreign_assistance: registry lists %d publishers, %d of them US government",
                 len(found), len(us))
        if len(us) != US_PUBLISHERS_EXPECTED:
            log.warning("foreign_assistance: expected %d US government publishers and the "
                        "registry returned %d — a publisher has joined or left, and one that "
                        "left takes its money out of the panel with no other symptom: %s",
                        US_PUBLISHERS_EXPECTED, len(us),
                        ", ".join(sorted(o["name"] for o in us)))
        return sorted(us, key=lambda o: o["name"])

    def _resources(self, org: str) -> List[Tuple[str, str]]:
        """Every resource URL a publisher registers, as (package name, url).

        Paged until the returned count is reached and never until `package_count` is reached.
        Within one survey `package_search` returned more packages than `package_count`
        advertised, 126 against 125 for the Department of the Interior, so a run that trusts
        the advertised count stops one package short.
        """
        packages: List[dict] = []
        start = 0
        while True:
            result = self.get_json(REGISTRY_PKGS, params={
                "fq": f"organization:{org}", "rows": 1000, "start": start})["result"]
            packages.extend(result["results"])
            if not result["results"] or len(packages) >= result["count"]:
                break
            start += 1000
        out: List[Tuple[str, str]] = []
        for package in packages:
            for resource in package.get("resources", []):
                url = resource.get("url")
                if url:
                    out.append((package["name"], url))
        return out

    # -- download -----------------------------------------------------------------------
    def _cache_path(self, org: str, filename: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
        return self.xml_dir / org / safe

    def _download(self, job: Tuple[str, str, str]) -> dict:
        """Fetch one file unless its ETag says the copy on disk is current."""
        org, filename, url = job
        path = self._cache_path(org, filename)
        key = f"{org}/{path.name}"
        known = self._manifest.get(key, {})
        headers = {}
        if path.exists() and path.stat().st_size > 0 and known.get("etag"):
            headers["If-None-Match"] = known["etag"]
        try:
            response = self._session.get(encode_url(url), headers=headers,
                                         timeout=self.timeout, stream=True)
            if response.status_code == 304:
                response.close()
                return dict(known, org=org, file=filename, path=str(path), status="cached")
            response.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as handle:
                for block in response.iter_content(1 << 20):
                    handle.write(block)
            record = {
                "org": org, "file": filename, "path": str(path), "status": "fetched",
                "bytes": path.stat().st_size,
                "etag": response.headers.get("ETag", ""),
                "last_modified": response.headers.get("Last-Modified", ""),
                "url": url,
            }
            self._manifest[key] = record
            return record
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", "")
            return {"org": org, "file": filename, "path": str(path), "status": "failed",
                    "error": f"{type(exc).__name__} {status}".strip(), "url": url}

    def _load_manifest(self) -> None:
        path = self.xml_dir / "manifest.json"
        if path.exists():
            try:
                self._manifest = json.loads(path.read_text())
            except (OSError, ValueError):
                log.warning("foreign_assistance: manifest at %s is unreadable, refetching all",
                            path)
                self._manifest = {}

    def _save_manifest(self) -> None:
        """Write the manifest, replacing the old one in a single filesystem operation.

        Written through a temporary file and renamed over the target, because the download takes
        long enough that a run will sometimes be interrupted part way through a write, and a
        half-written manifest is unreadable, and an unreadable manifest re-fetches all 2,723
        megabytes. The rename is atomic on the same filesystem, so the file on disk is always
        either the previous manifest or the new one.
        """
        self.xml_dir.mkdir(parents=True, exist_ok=True)
        target = self.xml_dir / "manifest.json"
        temporary = target.with_name("manifest.json.tmp")
        temporary.write_text(json.dumps(self._manifest, indent=1))
        temporary.replace(target)

    def _corpus(self) -> List[dict]:
        """Discover, download and return one record per readable file."""
        self._load_manifest()
        jobs: List[Tuple[str, str, str]] = []
        skipped_worldwide = 0
        repeated_urls = 0
        collisions = 0
        # A publisher can register the same filename twice, and the two cases behind one
        # repeated filename need opposite treatment. The Department of Transportation registers
        # one URL, the Ecuador file, under both its Ecuador package and its Uruguay package, so
        # the corpus asked for that one file twice, wrote it twice to the same path and counted
        # two successes against one file on disk. That repeat is harmless and is dropped here.
        # Two different URLs landing on one filename is the case that costs something, because
        # the second download overwrites the first and the run reports nothing. No publisher
        # does that today, proven by the corpus arithmetic of 2,016 successful downloads against
        # 2,015 files, which the single Transportation repeat accounts for in full. A publisher
        # that starts doing it gets a warning and a distinct local name, so both files are read
        # and neither is lost.
        for publisher in self._publishers():
            org = publisher["name"]
            resources = self._resources(org)
            kept = 0
            claimed: Dict[str, str] = {}
            for _, registry_url in resources:
                url = object_url(registry_url)
                filename = served_name(url)
                if is_worldwide(filename):
                    skipped_worldwide += 1
                    continue
                holder = claimed.get(filename)
                if holder == url:
                    repeated_urls += 1
                    continue
                if holder is not None:
                    collisions += 1
                    renamed = distinct_name(filename, url)
                    log.warning("foreign_assistance: %s registers the filename %s for two "
                                "different files, so the second is stored as %s (%s and %s)",
                                org, filename, renamed, holder, url)
                    filename = renamed
                claimed[filename] = url
                jobs.append((org, filename, url))
                kept += 1
            log.info("foreign_assistance: %s (%s) registers %d resources, %d to read after "
                     "Worldwide files and repeated registrations are taken out",
                     org, publisher.get("publisher_iati_id"), len(resources), kept)
        log.info("foreign_assistance: %d files to read, %d Worldwide files skipped, "
                 "%d duplicate registrations of one URL dropped, %d filename collisions renamed",
                 len(jobs), skipped_worldwide, repeated_urls, collisions)

        # A successful download used to log nothing, so a run went silent for the whole 2,723
        # megabytes and looked hung. Progress is reported every PROGRESS_EVERY files with the
        # bytes and the rate, because the only honest way to tell a slow download from a stuck
        # one is to watch the count move.
        #
        # The manifest is saved after every file that was actually fetched, and not once at the
        # end. The manifest is what the ETag cache reads, so a run killed part way through used
        # to throw away every byte it had downloaded and start the whole corpus again. Saving as
        # the run goes means an interrupted run resumes from where it stopped. A file served from
        # cache changes nothing in the manifest and triggers no write, so a rerun over an
        # unchanged corpus writes the manifest once.
        #
        # Only a fetched file's bytes count towards the fetched total. A cached record is built
        # from the record the previous run stored and keeps that record's `bytes` field, so a
        # counter that added the bytes of every record printed the same 2,833 MB whether the run
        # had downloaded the corpus or served all of it from cache. The rerun of 27 September
        # 2026 re-fetched all 2,015 files and the progress line could not say so. The count of
        # cached files is printed alongside, because a rerun that reports no cache hits at all
        # is the symptom of a manifest that was not read.
        records: List[dict] = []
        started = time.time()
        fetched_bytes = 0
        fetched_files = 0
        cached_files = 0
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            for record in pool.map(self._download, jobs):
                records.append(record)
                if record["status"] == "fetched":
                    fetched_bytes += record.get("bytes", 0)
                    fetched_files += 1
                    self._save_manifest()
                elif record["status"] == "cached":
                    cached_files += 1
                if record["status"] == "failed":
                    log.warning("foreign_assistance: %s/%s did not download (%s)",
                                record["org"], record["file"], record.get("error"))
                if len(records) % PROGRESS_EVERY == 0 or len(records) == len(jobs):
                    elapsed = max(time.time() - started, 1e-6)
                    log.info("foreign_assistance: %d of %d files, %d fetched for %.0f MB at "
                             "%.1f MB/s, %d served from cache, %.0fs elapsed, now in %s",
                             len(records), len(jobs), fetched_files, fetched_bytes / 1e6,
                             fetched_bytes / 1e6 / elapsed, cached_files, elapsed, record["org"])
        self._save_manifest()

        ok = [r for r in records if r["status"] != "failed"]
        failed = [r for r in records if r["status"] == "failed"]
        if failed:
            log.warning("foreign_assistance: %d of %d files did not download — the agency "
                        "totals below are short by whatever those files hold",
                        len(failed), len(records))
        self._report_staleness(ok)
        self._file_notes = records
        return ok

    @staticmethod
    def _report_staleness(records: List[dict]) -> None:
        """Say when a publisher's files stopped moving.

        USAID's files answered Last-Modified 3 August 2026 while State's answered 5 September
        and Health and Human Services' 4 September. A publisher whose files have stopped being
        rewritten still serves them, so the symptom of a publisher that has stopped reporting
        is a date and nothing else.
        """
        latest: Dict[str, str] = {}
        for record in records:
            stamp = record.get("last_modified") or ""
            if stamp and stamp > latest.get(record["org"], ""):
                latest[record["org"]] = stamp
        for org in sorted(latest):
            log.info("foreign_assistance: %s files last modified %s", org, latest[org])

    # -- parsing ------------------------------------------------------------------------
    @staticmethod
    def _local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    @classmethod
    def _is_hiv(cls, element: ET.Element) -> Optional[bool]:
        """True when the element's own sectors name HIV, False when they name something else,
        None when the element carries no sector at all and the caller should look higher up.

        Two tests, because ForeignAssistance.gov's own HIV/AIDS sector name and the DAC purpose
        code disagree in both directions. For FY2024 disbursements 75 rows worth 62.3m USD are
        USG HIV without DAC 13040 and 131 rows worth 103.9m are DAC 13040 under a USG label of
        Malaria, Tuberculosis, Maternal and Child Health or Direct Administrative Costs.
        """
        sectors = [s for s in element if cls._local_name(s.tag) == "sector"]
        if not sectors:
            return None
        for sector in sectors:
            vocabulary = sector.get("vocabulary")
            code = (sector.get("code") or "").strip()
            narrative = ""
            for child in sector:
                if cls._local_name(child.tag) == "narrative":
                    narrative = (child.text or "").strip()
                    break
            if vocabulary == "99" and narrative.upper() == "HIV/AIDS":
                return True
            # the DAC code here is the PURPOSE code 13040, not FA.gov's sector code 134
            if vocabulary == "1" and code == "13040":
                return True
        return False

    @classmethod
    def _countries(cls, element: ET.Element) -> List[str]:
        return [c.get("code") or "" for c in element
                if cls._local_name(c.tag) == "recipient-country"]

    @classmethod
    def _receiver(cls, transaction: ET.Element) -> str:
        for child in transaction:
            if cls._local_name(child.tag) != "receiver-org":
                continue
            for narrative in child:
                if cls._local_name(narrative.tag) == "narrative":
                    return (narrative.text or "").strip()
        return ""

    @staticmethod
    def fiscal_year(iso_date: str) -> Optional[int]:
        """The US fiscal year, which begins on 1 October of the year before it is named."""
        try:
            year, month = int(iso_date[:4]), int(iso_date[5:7])
        except (TypeError, ValueError):
            return None
        return year + 1 if month >= 10 else year

    def _parse_file(self, org: str, path: Path, wanted: Optional[Set[str]], start_year: int,
                    end_year: int, seen: Set[tuple], raw: Dict[Tuple[str, int, str], float],
                    awards: Dict[Tuple[str, int, str], Set[str]],
                    counters: Dict[str, int]) -> None:
        """Read one publisher file and add its kept disbursements to `raw`.

        Parsed with iterparse and cleared activity by activity, because the corpus runs to
        2,723 megabytes and the largest single file is about 100 megabytes.

        The publisher is named in the warning and not only the filename. The run of 27 September
        2026 reported `iati-activities-Africa_North_of_Sahara.xml` as unreadable and no reader
        could tell which agency had lost money, because several publishers use the same file
        names.
        """
        try:
            stream = ET.iterparse(str(path), events=("end",))
            for _, element in stream:
                if self._local_name(element.tag) != "iati-activity":
                    continue
                self._parse_activity(element, wanted, start_year, end_year, seen, raw,
                                     awards, counters)
                element.clear()
        except ET.ParseError as exc:
            counters["unreadable_file"] += 1
            log.warning("foreign_assistance: %s/%s is not readable XML (%s) — whatever that "
                        "publisher reports in that file is missing from the totals below",
                        org, path.name, exc)

    def _parse_activity(self, activity: ET.Element, wanted: Optional[Set[str]],
                        start_year: int, end_year: int, seen: Set[tuple],
                        raw: Dict[Tuple[str, int, str], float],
                        awards: Dict[Tuple[str, int, str], Set[str]],
                        counters: Dict[str, int]) -> None:
        counters["activities"] += 1
        identifier = ""
        reporting_ref = ""
        default_currency = (activity.get("default-currency") or "").upper()
        for child in activity:
            name = self._local_name(child.tag)
            if name == "iati-identifier":
                identifier = (child.text or "").strip()
            elif name == "reporting-org":
                reporting_ref = (child.get("ref") or "").strip()
        bucket = REPORTING_ORG_BUCKET.get(reporting_ref, OTHER)
        activity_countries = self._countries(activity)
        activity_hiv = self._is_hiv(activity)

        for transaction in activity:
            if self._local_name(transaction.tag) != "transaction":
                continue
            fields = {self._local_name(c.tag): c for c in transaction}

            kind = fields.get("transaction-type")
            if kind is None or (kind.get("code") or "") != "3":
                continue  # disbursements only, never obligations or budget requests

            # the HIV test belongs on the transaction, and falls back to the activity only
            # when the transaction carries no sector element of its own
            hiv = self._is_hiv(transaction)
            if hiv is None:
                hiv = activity_hiv
            if not hiv:
                continue

            codes = self._countries(transaction) or activity_countries
            if not codes:
                counters["no_country"] += 1
                continue
            if len(codes) > 1:
                counters["multi_country"] += 1
                continue

            iso3 = resolve_country(codes[0])
            if not iso3:
                # regional money: USAID's Multiple Countries files hold 905 HIV disbursements
                # worth 101.245m USD under region codes 289, 998, 789, 380 and 619, and the API
                # carries none of it under a country either
                counters["not_a_country"] += 1
                if codes[0].strip().isdigit():
                    counters["numeric_code"] += 1
                    self._numeric_codes[codes[0].strip()] += 1
                continue
            if wanted and iso3 not in wanted:
                continue

            date_element = fields.get("transaction-date")
            iso_date = (date_element.get("iso-date") or "") if date_element is not None else ""
            year = self.fiscal_year(iso_date)
            if year is None or not (start_year <= year <= end_year):
                continue

            value_element = fields.get("value")
            if value_element is None:
                continue
            currency = (value_element.get("currency") or default_currency or "USD").upper()
            if currency != "USD":
                counters["not_usd"] += 1
                continue
            try:
                value = float((value_element.text or "").strip())
            except ValueError:
                counters["unreadable_value"] += 1
                continue

            # the whole row, because the transaction ref alone destroys the State
            # reconciliation and the identifier alone keeps USAID's duplicates
            key = (identifier, transaction.get("ref"), iso_date, value,
                   self._receiver(transaction))
            if key in seen:
                counters["duplicate"] += 1
                continue
            seen.add(key)

            raw[(iso3, year, bucket)] = raw.get((iso3, year, bucket), 0.0) + value
            counters["kept"] += 1
            award = self._award_number(identifier, bucket)
            if award:
                awards.setdefault((iso3, year, bucket), set()).add(award)

    @staticmethod
    def _award_number(identifier: str, bucket: str) -> str:
        """The award number inside an IATI identifier, or empty where it is not published.

        USAID writes `US-GOV-1-72062020CA00001`, the award alone. State writes
        `US-GOV-11-72062020CA00001-227505`, the award and then its own activity number, and
        where the award number is redacted it writes `US-GOV-11-227085`, the activity number
        alone. A trailing all-digit segment is therefore the activity number and what precedes
        it is the award, and an identifier that is all digits after the prefix carries no award
        at all. This is used only to decide whether the two agencies overlap in a year, never
        to match award to award, which the redaction makes impossible.
        """
        for prefix in ("US-GOV-1-", "US-GOV-11-", "US-GOV-14-"):
            if identifier.startswith(prefix):
                rest = identifier[len(prefix):]
                break
        else:
            return ""
        if bucket == STATE and "-" in rest:
            head, tail = rest.rsplit("-", 1)
            if tail.isdigit():
                rest = head
        return "" if rest.isdigit() else rest

    # -- the frozen history --------------------------------------------------------------
    def _history(self) -> Dict[Tuple[str, int, str], float]:
        """The pre-window years, extracted once from the Complete Data Set.

        `scripts/extract_fa_history.py` makes this file from the 3.7 gigabyte CSV Jason
        downloaded on 18 July 2026. It is the authority for every agency-year the S3 route has
        not been proven on, which is everything before `PROVEN_WINDOW` and everything in
        `other_agency`.
        """
        path = self.raw_dir / HISTORY_FILE
        if not path.exists():
            log.warning("foreign_assistance: no %s — the series will start at the first year "
                        "the S3 files cover and the early years of PEPFAR will be missing. "
                        "Run scripts/extract_fa_history.py once to build it.", path)
            return {}
        history: Dict[Tuple[str, int, str], float] = {}
        with open(path, newline="") as handle:
            for row in csv.DictReader(handle):
                try:
                    key = (row["country_iso3"], int(row["fiscal_year"]), row["bucket"])
                    history[key] = history.get(key, 0.0) + float(row["amount_usd"])
                except (KeyError, TypeError, ValueError):
                    continue
        log.info("foreign_assistance: frozen history holds %d country-year-agency figures",
                 len(history))
        return history

    # -- emitting ------------------------------------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        end_year = end_year or 2035
        wanted = set(c.upper() for c in countries) if countries else None

        files = self._corpus()
        if not files:
            log.warning("foreign_assistance: no IATI file downloaded — emitting nothing")
            return

        raw: Dict[Tuple[str, int, str], float] = {}
        awards: Dict[Tuple[str, int, str], Set[str]] = {}
        seen: Set[tuple] = set()
        counters: Dict[str, int] = {k: 0 for k in (
            "activities", "kept", "duplicate", "no_country", "multi_country",
            "not_a_country", "numeric_code", "not_usd", "unreadable_value", "unreadable_file")}
        self._numeric_codes = collections.Counter()
        log.info("foreign_assistance: parsing %d files", len(files))
        started = time.time()
        for n, record in enumerate(files, start=1):
            self._parse_file(record["org"], Path(record["path"]), wanted, start_year, end_year,
                             seen, raw, awards, counters)
            if n % PROGRESS_EVERY == 0 or n == len(files):
                log.info("foreign_assistance: parsed %d of %d files, %d activities, %d HIV "
                         "disbursements kept, %.0fs elapsed",
                         n, len(files), counters["activities"], counters["kept"],
                         time.time() - started)
        log.info("foreign_assistance: read %d activities, kept %d HIV disbursements, dropped "
                 "%d duplicates, %d without a recipient country, %d naming more than one "
                 "country, %d naming a region and not a country, %d not in US dollars, and "
                 "gave up on %d %s not readable as XML",
                 counters["activities"], counters["kept"], counters["duplicate"],
                 counters["no_country"], counters["multi_country"], counters["not_a_country"],
                 counters["not_usd"], counters["unreadable_file"],
                 "file" if counters["unreadable_file"] == 1 else "files")
        if self._numeric_codes:
            # naming the codes matters, because a code that is all digits is one of
            # ForeignAssistance.gov's own country numbers and carries no ISO meaning. Resolving
            # such a code through UN M49 is what put Tuvalu in the panel until 27 September
            # 2026, so a publisher adopting a new number should be visible and not silent.
            log.info("foreign_assistance: of those, %d carried an all-digit recipient-country "
                     "code, which names no country the panel can hold: %s",
                     counters["numeric_code"],
                     ", ".join(f"{code} ({n:,})" for code, n
                               in sorted(self._numeric_codes.items(),
                                         key=lambda kv: (-kv[1], kv[0]))))

        raw = self._subtract_overlap(raw, awards)
        merged, provenance = self._merge_history(raw, self._history(), start_year, end_year,
                                                 wanted)
        yield from self._emit(merged, provenance)

    def _subtract_overlap(self, raw: Dict[Tuple[str, int, str], float],
                          awards: Dict[Tuple[str, int, str], Set[str]],
                          ) -> Dict[Tuple[str, int, str], float]:
        """Remove the award State and USAID both report, where the files show they both do.

        The unadjusted USAID figure is kept in `self._unadjusted` and carried into `extra`, so
        no value is replaced without the replaced value staying visible.

        The subtraction runs whatever the sign of the State figure and the result is not
        floored, because ForeignAssistance.gov subtracts whatever the sign. Skipping a negative
        State country-year leaves State's money inside the USAID series as well as in the State
        series, and moves the country total by the whole State amount. See the module docstring
        for the Papua New Guinea, Nepal and Indonesia figures that establish this.
        """
        adjusted = dict(raw)
        for (iso3, year, bucket) in list(raw):
            if bucket != USAID:
                continue
            state_total = raw.get((iso3, year, STATE))
            if not state_total:
                continue
            shared = awards.get((iso3, year, USAID), set()) & awards.get((iso3, year, STATE), set())
            if not shared:
                continue
            before = raw[(iso3, year, USAID)]
            self._unadjusted[(iso3, year)] = before
            adjusted[(iso3, year, USAID)] = before - state_total
            log.info("foreign_assistance: %s FY%d USAID %.0f less State %.0f = %.0f, on %d "
                     "award numbers both agencies publish", iso3, year, before, state_total,
                     adjusted[(iso3, year, USAID)], len(shared))
        return adjusted

    def _merge_history(self, s3: Dict[Tuple[str, int, str], float],
                       history: Dict[Tuple[str, int, str], float],
                       start_year: int, end_year: int, wanted: Optional[Set[str]],
                       ) -> Tuple[Dict[Tuple[str, int, str], float],
                                  Dict[Tuple[str, int, str], str]]:
        """Take each bucket-year from the source proven for it, and check where both have it.

        Inside a proven window the two sources should agree, because inside the window the S3
        files reproduce the API and the history is the API's own output. A disagreement there
        is a parsing fault or a restatement and the run says which country-years it hit.

        A disagreement is also written onto the row it affects and not only into the run log. A
        log line is read once by whoever ran the connector and is gone, and the panel is read
        later by Adrian and by anyone who takes the CSV, so a figure the two sources disagree
        about has to carry that fact with it. `self._disagreements` holds both figures for every
        such bucket-country-year and `_emit` puts both on the row.
        """
        merged: Dict[Tuple[str, int, str], float] = {}
        provenance: Dict[Tuple[str, int, str], str] = {}
        disagreements: List[str] = []
        self._disagreements = {}

        for key in set(s3) | set(history):
            iso3, year, bucket = key
            if not (start_year <= year <= end_year):
                continue
            if wanted and iso3 not in wanted:
                continue
            opens = PROVEN_WINDOW.get(bucket)
            proven = opens is not None and year >= opens

            if proven and key in s3:
                merged[key] = s3[key]
                provenance[key] = "s3"
                if key in history:
                    a, b = s3[key], history[key]
                    scale = max(abs(a), abs(b))
                    if scale > 0 and abs(a - b) / scale > HISTORY_AGREEMENT_TOLERANCE:
                        disagreements.append(
                            f"{iso3} FY{year} {bucket} S3 {a:,.0f} against history {b:,.0f}")
                        self._disagreements[key] = (a, b)
            elif key in history:
                merged[key] = history[key]
                provenance[key] = "history"
            elif key in s3:
                merged[key] = s3[key]
                provenance[key] = "s3_unproven"

        if disagreements:
            log.warning("foreign_assistance: %d country-years differ by more than %.0f per cent "
                        "between the S3 files and the frozen history inside a proven window, "
                        "first 10: %s", len(disagreements), 100 * HISTORY_AGREEMENT_TOLERANCE,
                        "; ".join(sorted(disagreements)[:10]))
        unproven = sum(1 for v in provenance.values() if v == "s3_unproven")
        if unproven:
            log.info("foreign_assistance: %d country-years come from the S3 files in a bucket "
                     "or year the Nigeria reconciliation did not prove", unproven)
        return merged, provenance

    def _emit(self, merged: Dict[Tuple[str, int, str], float],
              provenance: Dict[Tuple[str, int, str], str]) -> Iterator[PanelRow]:
        totals: Dict[Tuple[str, int], float] = {}
        by_agency: Dict[Tuple[str, int], Dict[str, float]] = {}
        for (iso3, year, bucket), value in merged.items():
            totals[(iso3, year)] = totals.get((iso3, year), 0.0) + value
            by_agency.setdefault((iso3, year), {})[bucket] = value

        partial_year, partial_note = self._partial_year(totals)
        base_extra: Dict[str, object] = {
            "note": "US self-reported HIV disbursements; triangulates the OECD CRS US series",
            "interpretation": INTERPRETATION,
            "route": "IATI XML on Amazon S3, discovered through the IATI Registry",
        }

        n = 0
        for (iso3, year), value in sorted(totals.items()):
            country_name = name_for(iso3)
            agencies = by_agency.get((iso3, year), {})
            prev = by_agency.get((iso3, year - 1), {})
            sources = sorted({provenance.get((iso3, year, b), "") for b in agencies} - {""})

            extra = dict(base_extra, funding_agency="all_us_agencies")
            extra["agency_split"] = "external_hiv_oda_us_{usaid,hhs,state,other_agency}"
            extra["grain_warning"] = (
                "the agency series partition this total — sum one level or the other, never "
                "both. The split exists only for source_id=foreign_assistance.")
            extra["value_source"] = "+".join(sources)
            if self._unadjusted.get((iso3, year)) is not None:
                extra["usaid_before_state_subtraction"] = round(
                    self._unadjusted[(iso3, year)], 2)
                extra["overlap_note"] = (
                    "the State Department and USAID both publish this country's bilateral "
                    "awards in this fiscal year, and ForeignAssistance.gov reports the USAID "
                    "figure net of the State figure, so the State total has been subtracted "
                    "from the USAID total. The unadjusted USAID figure is carried here.")
            if year == partial_year:
                extra["partial_fiscal_year"] = True
                extra["partial_fiscal_year_note"] = partial_note
            if value <= 0:
                extra["value_note"] = NON_POSITIVE_NOTE
            # a disagreement inside one agency bucket moves the country total too, because the
            # total is the four buckets added up, so the total row has to say so as well. A
            # reader who takes only the total row would otherwise never see the warning.
            disagreeing = [b for b in BUCKETS if (iso3, year, b) in self._disagreements]
            if disagreeing:
                extra["history_disagreement"] = True
                extra["history_disagreement_buckets"] = ",".join(disagreeing)
                extra["history_disagreement_note"] = HISTORY_DISAGREEMENT_TOTAL_NOTE
            yield self.make_row(
                country_iso3=iso3, country_name=country_name,
                indicator_id=TOTAL, year=year, value=value, unit="USD",
                source_url="https://foreignassistance.gov/data",
                source_indicator_code="FA.gov HIV disbursements — all managing agencies",
                extra=extra,
            )
            n += 1

            for bucket in BUCKETS:
                amount = agencies.get(bucket)
                # a bucket that falls to nothing is emitted as a zero and not left missing: for
                # the question this panel asks, "USAID spent nothing here this year" and "we
                # have no figure" are opposite readings and must not look alike.
                if amount is None:
                    if not prev.get(bucket):
                        continue
                    amount = 0.0
                agency_extra = dict(
                    base_extra,
                    funding_agency=AGENCY_LABEL[bucket],
                    agency_basis="Managing Agency (who spent it), not Funding Agency (whose "
                                 "account it came from)",
                    grain_warning="one of four series partitioning external_hiv_oda_us for "
                                  "this source; do not sum with the total row",
                    value_source=provenance.get((iso3, year, bucket), "none"),
                )
                # a share only means something while the denominator is bigger than the parts.
                # Recoveries can leave a country-year whose total is a small residue of large
                # offsetting agency figures, and a ratio taken there is an artefact of the
                # denominator, so it is left out and the reason recorded.
                share = amount / value if value > 0 else None
                if share is not None and abs(share) <= 1:
                    agency_extra["share_of_country_total"] = round(share, 4)
                else:
                    agency_extra["share_of_country_total"] = None
                    agency_extra["share_note"] = (
                        "not computed: the country total for this year is zero, negative, or "
                        "smaller than this agency's own figure once recoveries are netted, so "
                        "the ratio would describe the denominator and not the split.")
                if bucket == HHS:
                    agency_extra["agency_basis"] += (
                        "; the whole department, because the IATI files carry no sub-agency. "
                        "This series replaces external_hiv_oda_us_cdc, which was CDC alone.")
                if bucket == USAID and self._unadjusted.get((iso3, year)) is not None:
                    agency_extra["usaid_before_state_subtraction"] = round(
                        self._unadjusted[(iso3, year)], 2)
                if provenance.get((iso3, year, bucket)) == "s3_unproven":
                    agency_extra["window_note"] = (
                        "read from the IATI files in a bucket or year the Nigeria "
                        "reconciliation of September 2026 did not test against "
                        "ForeignAssistance.gov's own API, so the figure is unverified.")
                disagreement = self._disagreements.get((iso3, year, bucket))
                if disagreement is not None:
                    from_s3, from_history = disagreement
                    scale = max(abs(from_s3), abs(from_history))
                    agency_extra["history_disagreement"] = True
                    agency_extra["history_disagreement_s3_usd"] = round(from_s3, 2)
                    agency_extra["history_disagreement_api_usd"] = round(from_history, 2)
                    agency_extra["history_disagreement_rel"] = (
                        round(abs(from_s3 - from_history) / scale, 4) if scale > 0 else None)
                    agency_extra["history_disagreement_note"] = HISTORY_DISAGREEMENT_NOTE
                if amount <= 0:
                    agency_extra["value_note"] = NON_POSITIVE_NOTE
                if bucket not in agencies:
                    agency_extra["zero_meaning"] = (
                        f"no HIV disbursement managed by this agency in FY{year}, against "
                        f"{prev.get(bucket, 0.0):,.0f} USD in FY{year - 1}. A reported zero, "
                        f"not a missing value.")
                if year == partial_year:
                    agency_extra["partial_fiscal_year"] = True
                    agency_extra["partial_fiscal_year_note"] = partial_note
                yield self.make_row(
                    country_iso3=iso3, country_name=country_name,
                    indicator_id=f"{TOTAL}_{bucket}", year=year, value=amount, unit="USD",
                    source_url="https://foreignassistance.gov/data",
                    source_indicator_code=f"FA.gov HIV disbursements — managing agency "
                                          f"{AGENCY_LABEL[bucket]}",
                    extra=agency_extra,
                )
                n += 1
        log.info("foreign_assistance: emitted %d rows over %d country-years", n, len(totals))

    @staticmethod
    def _partial_year(totals: Dict[Tuple[str, int], float]) -> Tuple[Optional[int], str]:
        """The S3 files are rewritten during a running fiscal year and nothing in them says
        which year is incomplete. Infer it: the latest year, if it holds far less than the
        years before it. Judged on the whole run and not per country, because a single
        country's year-on-year swing is noise and the file-level one is not."""
        by_year: Dict[int, float] = {}
        for (_, year), value in totals.items():
            by_year[year] = by_year.get(year, 0.0) + value
        if len(by_year) < 3:
            return None, ""
        latest = max(by_year)
        prior = [by_year[y] for y in (latest - 3, latest - 2, latest - 1) if y in by_year]
        if len(prior) < 2:
            return None, ""
        median = statistics.median(prior)
        if median <= 0 or by_year[latest] >= PARTIAL_YEAR_RATIO * median:
            return None, ""
        note = (
            f"FY{latest} disbursements total {by_year[latest]:,.0f} USD against a median of "
            f"{median:,.0f} for the years before it ({by_year[latest] / median:.0%}). The US "
            f"fiscal year ends 30 September and the publishers rewrite these files during it, "
            f"so FY{latest} is a part year and must not be compared with a full one."
        )
        log.warning("foreign_assistance: FY%d looks incomplete (%.0f%% of the prior median) — "
                    "rows flagged partial_fiscal_year", latest, 100 * by_year[latest] / median)
        return latest, note
