"""
Access probe for national HIV / health data portals — the evidence behind the feasibility logs.

For each candidate endpoint this records what the host actually does when asked for data:
whether it resolves, what it returns, where it redirects, whether the page is a login wall, and
whether a DHIS2 API answers without a session. The output is the per-country evidence table in
docs/PHASE3_FEASIBILITY_AFRICA.md, and re-running it is how that log gets refreshed or extended.

TLS handling deserves a note, because it is where the first Africa pass went wrong. A host that
fails certificate verification is not a host that is down: nine of the twelve that failed on
2026-08-03 served ordinary content once verification was disabled. So when verification fails,
this probe retries twice — once with verification off and once over plain HTTP — PURELY to
classify the barrier. Those retries are diagnostics and nothing collected through them may enter
the panel: an unverified channel gives no way to attest that what arrived is what the ministry
published. The classification the probe writes down is "tls_unverified", never "unreachable".

Usage:
    python scripts/probe_country_portals.py [out.json]
"""
from __future__ import annotations

import json
import re
import socket
import sys
import urllib3
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
TIMEOUT = 25
WORKERS = 10

CANDIDATES = {
    # ---- Eastern and Southern Africa ----
    "ZAF": ["https://www.thembisa.org/", "https://www.health.gov.za/",
            "https://webdhis.health.gov.za/", "https://www.hst.org.za/",
            "https://sanac.org.za/", "https://www.nicd.ac.za/"],
    "TZA": ["https://nacp.go.tz/", "https://dhis.moh.go.tz/", "https://tacaids.go.tz/",
            "https://www.nbs.go.tz/"],
    "ZMB": ["https://www.moh.gov.zm/", "https://nac.org.zm/", "https://hmis.moh.gov.zm/"],
    "ZWE": ["https://www.mohcc.gov.zw/", "https://nac.org.zw/", "https://hmis.mohcc.gov.zw/"],
    "MOZ": ["https://www.misau.gov.mz/", "https://www.ins.gov.mz/"],
    "ETH": ["https://ephi.gov.et/", "https://dhis.moh.gov.et/", "https://www.moh.gov.et/"],
    "RWA": ["https://www.rbc.gov.rw/", "https://hmis.moh.gov.rw/", "https://www.moh.gov.rw/"],
    "LSO": ["https://www.health.gov.ls/", "https://dhis2.health.org.ls/"],
    "SWZ": ["https://www.gov.sz/", "https://www.nercha.org.sz/", "https://dhis2.gov.sz/"],
    "NAM": ["https://mhss.gov.na/", "https://dhis2.mhss.gov.na/"],
    "BWA": ["https://www.moh.gov.bw/", "https://www.nahpa.gov.bw/"],
    "KEN": ["https://hiskenya.org/", "https://nascop.or.ke/", "https://nsdcc.go.ke/",
            "https://www.health.go.ke/"],
    "UGA": ["https://hmis.health.go.ug/", "https://uac.go.ug/", "https://www.health.go.ug/"],
    "MWI": ["https://dhis2.health.gov.mw/", "https://www.health.gov.mw/", "https://www.nac.org.mw/"],
    # ---- Western and Central Africa (probed thinly — see the log) ----
    "NGA": ["https://naca.gov.ng/", "https://naiis.ng/", "https://ndr.phis3project.org.ng/",
            "https://ndr.shieldnrs.org/"],
    "COD": ["https://www.pnls.cd/", "https://minisantersd.cd/", "https://www.sante.gouv.cd/"],
    "CIV": ["https://www.sante.gouv.ci/", "https://pnls.ci/", "https://www.pnlsci.org/"],
    "CMR": ["https://cnls.cm/", "https://www.minsante.cm/"],
    "GHA": ["https://ghanaids.gov.gh/", "https://www.ghanahealthservice.org/",
            "https://dhims.ghsmis.org/"],
    # ---- regional / multi-country layers ----
    "REG": ["https://phia-data.icap.columbia.edu/", "https://phia.icap.columbia.edu/",
            "https://africacdc.org/", "https://dhis2.org/"],
}

LOGIN = re.compile(r"(login|signin|sign-in|auth|sso|account)", re.I)
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def _title(resp) -> str:
    ctype = resp.headers.get("content-type", "")
    if "html" not in ctype:
        return ""
    m = TITLE.search(resp.text[:20000])
    return re.sub(r"\s+", " ", m.group(1)).strip()[:90] if m else ""


def _classify(url: str, resp) -> str:
    if resp.status_code >= 400:
        return f"http_{resp.status_code}"
    if resp.url.rstrip("/") != url.rstrip("/") and LOGIN.search(resp.url):
        return "login_redirect"
    if LOGIN.search(_title(resp)):
        return "login_page"
    return "reachable"


def probe(iso: str, url: str) -> dict:
    out = {"iso3": iso, "url": url}
    host = urlparse(url).hostname
    try:
        socket.getaddrinfo(host, 443)
    except Exception as exc:
        out["outcome"] = "dns_fail"
        out["detail"] = str(exc)[:120]
        return out

    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT, allow_redirects=True)
    except requests.exceptions.SSLError as exc:
        # alive-but-untrusted is its own barrier class; classify it, do not collect from it
        out["outcome"] = "tls_unverified"
        out["detail"] = str(exc)[:140]
        out.update(_tls_diagnostic(url))
        return out
    except requests.RequestException as exc:
        out["outcome"] = "transport_error"
        out["detail"] = type(exc).__name__ + ": " + str(exc)[:120]
        return out

    out["status"] = r.status_code
    out["final_url"] = r.url
    out["content_type"] = r.headers.get("content-type", "")[:60]
    out["bytes"] = len(r.content)
    out["title"] = _title(r)
    out["outcome"] = _classify(url, r)

    # DHIS2 fingerprint: on an open instance this returns JSON without a session. On a gated
    # one it returns the login application, which is what says the API is authenticated too.
    if any(k in url for k in ("dhis", "hmis", "his")):
        try:
            a = requests.get(url.rstrip("/") + "/api/system/info.json",
                             headers={"User-Agent": UA}, timeout=TIMEOUT)
            out["dhis2_api"] = f"{a.status_code} {a.headers.get('content-type', '')[:30]}"
            if a.status_code == 200 and "json" in a.headers.get("content-type", ""):
                try:
                    out["dhis2_version"] = a.json().get("version")
                except ValueError:
                    pass
        except requests.RequestException as exc:
            out["dhis2_api"] = "error: " + type(exc).__name__
    return out


def _tls_diagnostic(url: str) -> dict:
    """Is this host alive behind the bad certificate? Diagnostic only — never a data channel."""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    d = {}
    for label, target, verify in (("no_verify", url, False),
                                  ("plain_http", url.replace("https://", "http://", 1), True)):
        try:
            r = requests.get(target, headers={"User-Agent": UA}, timeout=TIMEOUT, verify=verify)
            d[label] = f"{r.status_code} {_title(r)[:60]} -> {r.url}"
        except requests.RequestException as exc:
            d[label] = type(exc).__name__
    d["alive_behind_bad_cert"] = d["no_verify"].startswith("2") or d["plain_http"].startswith("2")
    return d


def main() -> None:
    jobs = [(iso, u) for iso, urls in CANDIDATES.items() for u in urls]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        results = list(ex.map(lambda j: probe(*j), jobs))

    out_path = sys.argv[1] if len(sys.argv) > 1 else "country_portal_probe.json"
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=1)

    for iso in CANDIDATES:
        print(f"\n== {iso}")
        for r in [x for x in results if x["iso3"] == iso]:
            extra = ""
            if r.get("dhis2_version"):
                extra = f"  DHIS2 v{r['dhis2_version']}"
            elif r.get("dhis2_api"):
                extra = f"  api={r['dhis2_api']}"
            if r["outcome"] == "tls_unverified":
                extra += f"  alive={r.get('alive_behind_bad_cert')}  [{r.get('no_verify','')[:60]}]"
            print(f"  {r['outcome']:<16} {r['url']:<45} {r.get('title', '')[:52]}{extra}")
    print(f"\n{len(results)} endpoints probed -> {out_path}")


if __name__ == "__main__":
    main()
