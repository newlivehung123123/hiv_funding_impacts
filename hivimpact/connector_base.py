"""
BaseConnector — the contract every source connector implements.

A connector's single job: turn one structured/authoritative source into a stream of
PanelRow objects. It must NOT interpret prose, guess numbers, or fabricate values for
gaps. If a source doesn't publish something, the connector simply yields nothing for
it (the absence is then visible in the panel).

HTTP hygiene (lessons carried over from GrantGlobe): a real browser User-Agent,
explicit timeouts, and retry-with-backoff on 429/5xx. Never a self-identifying bot UA.
"""
from __future__ import annotations

import logging
import time
from typing import Iterable, Iterator, Optional

import requests

from .schema import PanelRow, SourceType, date

log = logging.getLogger("hivimpact")

_REAL_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)


class BaseConnector:
    #: stable id used in the panel's source_id column
    source_id: str = "base"
    #: default source_type for rows this connector emits (can be overridden per-row)
    default_source_type: SourceType = SourceType.MODELLED_ESTIMATE
    #: human description, shown in run summaries
    description: str = ""

    # polite pacing between HTTP calls (seconds); tune per source
    request_pause: float = 0.0

    #: per-request timeout in seconds. A subclass raises this for a source that is
    #: slow by nature (OECD's SDMX service, World Bank's all-country pages). It was
    #: previously an __init__ default only, so the class-level values subclasses had
    #: already declared did nothing and every source ran on 60s.
    timeout: int = 60

    def __init__(self, timeout: Optional[int] = None, max_retries: int = 4):
        self.timeout = type(self).timeout if timeout is None else timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": _REAL_UA, "Accept-Encoding": "gzip, deflate"})

    # -- subclasses implement this ---------------------------------------------
    def fetch(
        self,
        countries: Optional[Iterable[str]] = None,
        start_year: int = 2000,
        end_year: Optional[int] = None,
    ) -> Iterator[PanelRow]:
        """Yield PanelRow objects. `countries` is an iterable of ISO3 codes, or None = all."""
        raise NotImplementedError

    # -- shared helpers ---------------------------------------------------------
    # transient statuses worth retrying (400 included: World Bank 400s intermittently on
    # valid multi-country queries). 401/403/404/410 are NOT here -> they fail fast.
    RETRYABLE_STATUS = (400, 429, 500, 502, 503, 504)

    def _request(self, method: str, url: str, **kw) -> requests.Response:
        kw.setdefault("timeout", self.timeout)
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.request(method, url, **kw)
            except requests.RequestException as exc:  # transport error -> retry
                last_exc = exc
                wait = min(2 ** attempt, 30)
                log.warning("%s %s -> %s (attempt %d/%d), retrying in %ss",
                            self.source_id, url, exc, attempt, self.max_retries, wait)
                time.sleep(wait)
                continue
            if resp.status_code in self.RETRYABLE_STATUS:
                wait = min(2 ** attempt, 30)
                log.warning("%s %s -> HTTP %s (attempt %d/%d), backing off %ss",
                            self.source_id, url, resp.status_code, attempt, self.max_retries, wait)
                time.sleep(wait)
                continue
            # any other non-2xx (404/403/…) raises immediately, outside the retry loop
            resp.raise_for_status()
            if self.request_pause:
                time.sleep(self.request_pause)
            return resp
        raise RuntimeError(f"{self.source_id}: request failed after {self.max_retries} attempts: {url}") from last_exc

    def get_json(self, url: str, **kw):
        return self._request("GET", url, **kw).json()

    def get_text(self, url: str, **kw) -> str:
        return self._request("GET", url, **kw).text

    def make_row(self, **kw) -> PanelRow:
        """Build a PanelRow with source provenance pre-filled."""
        kw.setdefault("source_id", self.source_id)
        kw.setdefault("source_type", self.default_source_type.value)
        kw.setdefault("retrieved_at", date.today().isoformat())
        return PanelRow(**kw)
