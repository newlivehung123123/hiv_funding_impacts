#!/usr/bin/env python3
"""
Publish the built site to the web host.

The pages are static, so publishing is a file copy: everything under site/dist is put into
public_html on the server, and anything left on the server that is no longer part of the build
is removed. The copy includes .htaccess, which the browser file manager leaves out without
saying so, and which carries the file types for the downloads and the redirect for the old
page addresses. That omission is what made the CSV files download as .txt.

The password is not written down anywhere in this repository. It is read from the macOS
keychain each time the script runs, so it is typed in once, by hand, and never again.

    python3 scripts/deploy.py --set-password   take the password and put it in the keychain
    python3 scripts/deploy.py                  publish, then check the live site
    python3 scripts/deploy.py --check          check the live site and change nothing
    python3 scripts/deploy.py --dry-run        list what would be sent and removed
"""

from __future__ import annotations

import argparse
import calendar
import ftplib
import getpass
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "site/dist"

HOST = "145.79.4.16"
USER = "u822293545.hivfundingimpacts.aiinsocietyhub.com"
SITE_DIR = "public_html"
KEYCHAIN_SERVICE = "hivfundingimpacts-ftp"
SITE = "https://hivfundingimpacts.aiinsocietyhub.com"

# What the server should be saying about the site once the files are in place. Each entry is a
# path, the header to read, and the value it has to carry. The first two are the reason the
# .htaccess has to survive publication, so they are checked on every run.
EXPECTED = [
    ("/downloads/hiv_panel.csv", "content-type", "text/csv"),
    ("/downloads/hiv_panel.sqlite", "content-type", "application/octet-stream"),
    ("/downloads/hiv_panel.parquet", "content-type", "application/octet-stream"),
    ("/downloads/hiv_panel.csv", "content-disposition", "attachment"),
]

# The region pages and the country pages are taken from the region configuration, so a region set
# live there is checked from the first publication that carries the region's pages.
sys.path.insert(0, str(ROOT))
from hivimpact.config.regions import REGIONS                         # noqa: E402

_LIVE = [r for r in REGIONS if r["status"] == "live"]
PAGES = (["/", "/about/", "/methods/", "/data/", "/reconciliation/"]
         + [f'/regions/{r["slug"]}/' for r in _LIVE]
         + [f"/countries/{iso3.lower()}/" for r in _LIVE for iso3 in r["iso3"]]
         + ["/static/css/site.css", "/static/js/rack.js"])

REDIRECTS = [("/index.html", "/"), ("/methods/index.html", "/methods/")]

# How many times each of the above is asked. The host answers from several edge servers, each
# with its own copy, so one wrong copy shows up only in a share of the requests.
SAMPLES = 8


# ---------------------------------------------------------------- the local build

def local_files() -> dict[str, Path]:
    """Every file in the build, keyed by its path relative to the root of the site."""
    if not LOCAL.is_dir():
        sys.exit(f"no build at {LOCAL}. Run: python3 scripts/build_site.py")
    files = {str(p.relative_to(LOCAL)): p for p in LOCAL.rglob("*")
             if p.is_file() and p.name != ".DS_Store"}
    if ".htaccess" not in files:
        sys.exit("the build has no .htaccess. Run: python3 scripts/build_site.py")
    return files


# ---------------------------------------------------------------- the connection

def password() -> str:
    r = subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", USER, "-w"],
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit("no FTP password in the keychain. Put it there once with:\n\n"
                 "    python3 scripts/deploy.py --set-password\n")
    return r.stdout.strip()


def connect(pw: str | None = None) -> ftplib.FTP_TLS:
    """
    Open the connection with TLS. The password would cross the wire in the clear on a plain FTP
    login, so a host that refuses an encrypted session is treated as a failure here and not
    quietly accepted.

    The certificate is checked against the public certificate authorities, which is what shows
    it is not a forgery. Its name is not required to match the address. The host answers FTP on
    a numbered address, its certificate is issued for *.hstgr.io, and it publishes no name for
    that address, so insisting on the match would mean giving up encryption altogether.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ftp = ftplib.FTP_TLS(context=ctx)
    ftp.connect(HOST, 21, timeout=60)
    try:
        ftp.auth()
    except ftplib.all_errors as e:
        sys.exit(f"the server would not start an encrypted session: {e}")
    ftp.login(USER, pw or password())
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def store_password() -> int:
    """
    Take the password once, prove it works, and put it in the keychain.

    Set the password first in hPanel, under Files then FTP Accounts, with the Change FTP
    password link. That is a different password from the one used to sign in to Hostinger.

    It is asked for once here, it does not appear on the screen as it is typed, and it is not
    written into this repository. The login is tried before anything is saved, so a password
    that will not work is reported now and not on the day the site next needs publishing.
    """
    print(f"host   {HOST}")
    print(f"user   {USER}\n")
    print("Use the FTP password from hPanel: Files, then FTP Accounts, then the")
    print("Change FTP password link. It is not the Hostinger account password.\n", flush=True)

    try:
        pw = getpass.getpass("FTP password (nothing shows on screen as you type): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nnothing typed, nothing stored")
        return 1
    if not pw:
        print("nothing typed, nothing stored")
        return 1

    print("\ntrying it against the server ...")
    try:
        connect(pw).quit()
    except ftplib.all_errors as e:
        print(f"the server would not accept it: {e}\n")
        print("Nothing has been stored. Set a new password in hPanel with Change FTP")
        print("password, give it a minute, then run this again.")
        return 1
    print("the server accepted it")

    r = subprocess.run(["security", "add-generic-password", "-U",
                        "-s", KEYCHAIN_SERVICE, "-a", USER, "-w", pw],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"the keychain would not take it: {r.stderr.strip()}")
        return 1

    print(f"stored in the keychain under {KEYCHAIN_SERVICE}\n")
    print("Publishing from now on is one command:")
    print("    python3 scripts/build_site.py && python3 scripts/deploy.py")
    return 0


# ---------------------------------------------------------------- the remote side

def remote_entries(ftp: ftplib.FTP, path: str) -> list[tuple[str, bool, dict[str, str]]]:
    """
    The names in a remote folder, every name with whether the name is a folder and with the facts
    the host gives for the name, which include the size and the time of writing where the host
    gives them.
    """
    try:
        return [(name, facts.get("type") == "dir", facts)
                for name, facts in ftp.mlsd(path)
                if name not in (".", "..")]
    except ftplib.error_perm:
        out = []
        for name in ftp.nlst(path):
            name = name.rsplit("/", 1)[-1]
            if name in (".", ".."):
                continue
            here = ftp.pwd()
            try:
                ftp.cwd(f"{path}/{name}")
                out.append((name, True, {}))
                ftp.cwd(here)
            except ftplib.error_perm:
                out.append((name, False, {}))
        return out


def remote_tree(ftp: ftplib.FTP, base: str) -> tuple[dict[str, dict[str, str]], set[str]]:
    """Every file under base with the host's facts for the file, and every folder under base."""
    files, dirs, queue = {}, set(), [""]
    while queue:
        rel = queue.pop()
        here = f"{base}/{rel}".rstrip("/")
        for name, is_dir, facts in remote_entries(ftp, here):
            child = f"{rel}/{name}".lstrip("/")
            if is_dir:
                dirs.add(child)
                queue.append(child)
            else:
                files[child] = facts
    return files, dirs


def remote_root(ftp: ftplib.FTP) -> str:
    """
    Where on the server the pages belong.

    The account may sign in above the site's folder or already inside it, which is a choice the
    host makes and not one this script controls. Both are handled here, so the folder is found
    either way and the pages are never written a level out from where they are served.
    """
    here = ftp.pwd().rstrip("/") or "/"
    if here.rsplit("/", 1)[-1] == SITE_DIR:
        return here
    was = here
    try:
        ftp.cwd(SITE_DIR)
        root = ftp.pwd().rstrip("/")
        ftp.cwd(was)
        return root
    except ftplib.all_errors:
        sys.exit(f"the site's folder, {SITE_DIR}, is not where the login lands ({here}) "
                 f"and is not inside it either")


def ensure_dir(ftp: ftplib.FTP, root: str, path: str, made: set[str]) -> None:
    parts, walk = path.split("/"), root
    for part in parts:
        walk = f"{walk}/{part}"
        if walk in made:
            continue
        try:
            ftp.mkd(walk)
        except ftplib.error_perm:
            pass                       # already there, which is the common case
        made.add(walk)


# ---------------------------------------------------------------- publishing

# The host can close the connection part of the way through a publication. On 28 October 2026
# the host closed the connection between two files after 750 of 975 had gone. A closed
# connection is therefore opened again and the step which was due is tried again, up to
# RECONNECTS times in a row before the publication stops. A refusal by the host, a 5xx reply, is not a lost
# connection and is never retried, with the single exception of BUSY below.
RECONNECTS = 6
LOST = (EOFError, OSError, ftplib.error_temp)

# The host writes every upload under a hidden name and gives the upload the real name once the
# upload is complete. After a lost connection the host can keep the hidden copy of the unfinished
# upload, and while the hidden copy is there, the host refuses a new upload of the same file with
# "Temporary hidden file ... already exists". On 28 October 2026 the host refused
# hiv_panel.sqlite with the same message ten seconds after the second lost connection, and still
# held the hidden copy more than an hour later. The host also closes a connection left idle for
# a minute, and the connection is therefore closed before every wait and opened again after the
# wait. After BUSY_WAITS waits of BUSY_WAIT seconds the hidden copy counts as a leftover of a
# broken upload by deploy.py, and the hidden copy is removed before a last try.
BUSY = re.compile(r"Temporary hidden file (\S+) already exists")
BUSY_WAIT = 60
BUSY_WAITS = 2


def hidden_copy(path: str) -> str:
    """The name under which the host writes an upload of path until the upload is complete."""
    folder, name = path.rsplit("/", 1)
    return f"{folder}/.in.{name}."


class Session:
    """The FTP connection, opened again whenever the host drops the connection."""

    def __init__(self) -> None:
        self.ftp: ftplib.FTP_TLS | None = connect()
        self.reopened = 0

    def run(self, what: str, step):
        lost = busy = 0
        remove = None
        while True:
            try:
                if self.ftp is None:
                    self.ftp = connect()
                if remove is not None:
                    try:
                        self.ftp.delete(remove)
                    except ftplib.error_perm as refused:
                        print(f"  kept      {remove} ({refused})", flush=True)
                    remove = None
                return step(self.ftp)
            except ftplib.error_perm as e:
                hidden = BUSY.search(str(e))
                if hidden is None or busy > BUSY_WAITS:
                    raise
                lost = 0                   # a reply from the host shows the connection is alive
                busy += 1
                if busy <= BUSY_WAITS:
                    print(f"  waiting   the host still holds the unfinished copy of {what}, "
                          f"trying again in {BUSY_WAIT} s ({busy}/{BUSY_WAITS})", flush=True)
                    self.drop()
                    time.sleep(BUSY_WAIT)
                else:
                    remove = hidden.group(1)
                    print(f"  removing  {remove}, the unfinished copy the host kept "
                          f"after {BUSY_WAITS} waits", flush=True)
            except LOST as e:
                if lost == RECONNECTS:
                    raise
                lost += 1
                self.reopened += 1
                print(f"  lost      the connection at {what} ({type(e).__name__}: {e}), "
                      f"connecting again", flush=True)
                self.drop()
                time.sleep(15 * lost)

    def drop(self) -> None:
        if self.ftp is not None:
            try:
                self.ftp.close()
            except ftplib.all_errors:
                pass
        self.ftp = None

    def quit(self) -> None:
        if self.ftp is not None:
            try:
                self.ftp.quit()
            except ftplib.all_errors:
                pass
        self.ftp = None


# The pages go up before the large downloads, and a publication cut off during a download of
# several hundred megabytes therefore still leaves every page of the new build live.
BIG = 20 * 1024 * 1024

# A file the host already holds from the current build is not sent again, and a second run after
# a publication was cut off therefore sends only the files which had not arrived. The host's copy
# counts as the current build's copy when the sizes match and the host wrote the copy at or after
# the time the build wrote the file. The host gives the time in UTC, and a copy dated more than
# CLOCK_SLACK seconds ahead of the local clock is sent again, and a host clock running hours
# ahead therefore cannot pass an older copy off as a new copy.
CLOCK_SLACK = 300


def already_sent(facts: dict[str, str], path: Path) -> bool:
    try:
        size = int(facts["size"])
        stamp = calendar.timegm(time.strptime(facts["modify"][:14], "%Y%m%d%H%M%S"))
    except (KeyError, ValueError):
        return False                   # a host which gives no size or time gets every file again
    st = path.stat()
    return size == st.st_size and int(st.st_mtime) <= stamp <= time.time() + CLOCK_SLACK


# A file above BIG goes up under a new name on every try and takes the real name only once the
# whole file is on the host. A reader therefore never meets half a download, and a hidden copy
# kept from a broken upload under the real name cannot block the new upload. A host which refuses
# the rename gets the file again under the real name. On 28 October 2026 the host kept the hidden
# copy of hiv_panel.sqlite for more than an hour and refused every new upload of hiv_panel.sqlite.
def send_big(session: Session, root: str, rel: str, path: Path, made: set[str]) -> None:
    final = f"{root}/{rel}"
    folder, name = final.rsplit("/", 1)
    size = path.stat().st_size
    parts: list[str] = []

    def held(ftp) -> dict[str, dict[str, str]]:
        return {n: facts for n, _, facts in remote_entries(ftp, folder)}

    with path.open("rb") as fh:
        def put(ftp):
            if "/" in rel:
                ensure_dir(ftp, root, rel.rsplit("/", 1)[0], made)
            part = f"{final}.{time.strftime('%Y%m%d%H%M%S')}-{len(parts)}.part"
            parts.append(part)
            fh.seek(0)
            ftp.storbinary(f"STOR {part}", fh)
            return part
        part = session.run(rel, put)

    def swap(ftp):
        there = held(ftp)
        if part.rsplit("/", 1)[1] not in there and already_sent(there.get(name, {}), path):
            return                     # the rename went through before the connection was lost
        try:
            ftp.rename(part, final)
        except ftplib.error_perm:
            aside = f"{part}.old"      # a host which will not rename onto a name in use
            ftp.rename(final, aside)
            try:
                ftp.rename(part, final)
            except ftplib.error_perm:
                ftp.rename(aside, final)
                raise
            try:
                ftp.delete(aside)
            except ftplib.error_perm:
                pass                   # the strip after the uploads tries again

    try:
        session.run(rel, swap)
    except ftplib.error_perm as refused:
        print(f"  renaming  refused by the host ({refused}), sending {rel} again under the "
              f"real name", flush=True)
        with path.open("rb") as fh:
            def put_final(ftp):
                fh.seek(0)
                ftp.storbinary(f"STOR {final}", fh)
            session.run(rel, put_final)

    def verify(ftp):
        got = held(ftp).get(name, {}).get("size")
        if got is not None and int(got) != size:
            sys.exit(f"the host holds {rel} at {got} bytes, and the build holds {size} bytes")
    session.run(rel, verify)

    def clear(ftp) -> int:
        gone = 0
        for p in [final] + parts:
            try:
                ftp.delete(hidden_copy(p))
                gone += 1
            except ftplib.error_perm:
                pass                   # no hidden copy under the name, the usual case
        return gone
    gone = session.run(rel, clear)
    if gone:
        print(f"  cleared   {gone} unfinished copies of {rel} which the host had kept", flush=True)


def publish(dry_run: bool) -> None:
    files = local_files()
    total_kb = sum(p.stat().st_size for p in files.values()) / 1024
    print(f"build       {len(files)} files, {total_kb/1024:.1f} MB, from {LOCAL}")

    session = Session()
    root = session.run("the site folder", remote_root)
    if not dry_run:
        print(f"connected   {HOST} as {USER}, encrypted")
    print(f"site folder {root}")

    remote_before, _ = session.run("the listing", lambda ftp: remote_tree(ftp, root))
    order = sorted(files.items(), key=lambda kv: (kv[1].stat().st_size > BIG, kv[0]))
    todo = [(rel, path) for rel, path in order
            if not already_sent(remote_before.get(rel, {}), path)]
    held = len(files) - len(todo)
    stale = sorted(set(remote_before) - set(files))

    if dry_run:
        session.quit()
        htaccess = ", .htaccess among them" if any(rel == ".htaccess" for rel, _ in todo) else ""
        print(f"would skip  {held} files the host already holds from the current build")
        print(f"would send  {len(todo)} files{htaccess}")
        print(f"would strip {len(stale)} files no longer in the build")
        for s in stale[:20]:
            print(f"              {s}")
        return

    if held:
        print(f"skipped     {held} files the host already holds from the current build")
    made: set[str] = set()
    sent = 0
    for rel, path in todo:
        size = path.stat().st_size
        if size > BIG:
            print(f"  sending   {rel}, {size/1024/1024:.1f} MB", flush=True)
            send_big(session, root, rel, path, made)
        else:
            with path.open("rb") as fh:
                def put(ftp, rel=rel, fh=fh):
                    if "/" in rel:
                        ensure_dir(ftp, root, rel.rsplit("/", 1)[0], made)
                    fh.seek(0)             # a file cut off by a lost connection goes again whole
                    ftp.storbinary(f"STOR {root}/{rel}", fh)
                session.run(rel, put)
        sent += 1
        if sent % 10 == 0 or sent == len(todo):
            print(f"  sent      {sent}/{len(todo)}", flush=True)

    # The listing after the uploads also finds the copies of a broken upload under a temporary
    # name, and the strip removes every file outside the build.
    remote_after, dirs_after = session.run("the listing", lambda ftp: remote_tree(ftp, root))
    stale = sorted(set(remote_after) - set(files))
    for rel in stale:
        def strip(ftp, rel=rel):
            try:
                ftp.delete(f"{root}/{rel}")
            except ftplib.error_perm as e:
                print(f"  kept      {rel} ({e})")
        session.run(rel, strip)
    if stale:
        print(f"  stripped  {len(stale)} files no longer in the build")

    # the folders are pruned deepest first, so a folder emptied by the strip above goes too
    wanted: set[str] = set()
    for rel in files:
        parts = rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            wanted.add("/".join(parts[:i]))
    for d in sorted(dirs_after - wanted, key=lambda s: s.count("/"), reverse=True):
        def prune(ftp, d=d):
            try:
                ftp.rmd(f"{root}/{d}")
                print(f"  removed   {d}/")
            except ftplib.error_perm:
                pass
        session.run(d, prune)

    session.quit()
    if session.reopened:
        print(f"  reconnected {session.reopened} times after the host closed the connection")
    print("published")


# ---------------------------------------------------------------- checking

def head(url: str) -> tuple[int, dict[str, str], str]:
    """The status, the headers and the redirect target, without pulling the file down."""
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("Cache-Control", "no-cache")

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=40) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.headers.get("location", "")
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, e.headers.get("location", "")
    except Exception as e:                                    # noqa: BLE001
        return 0, {}, str(e)


def sample(path: str, judge) -> tuple[int, list[str]]:
    """
    Ask the same question several times and count how often the answer is right.

    The host answers from whichever of its edge servers is nearest, and each of them keeps its
    own copy of a file. One wrong copy among them shows itself only now and then. A site handing
    readers the wrong file one time in five will answer a single question correctly four times
    out of five, so asking once is no test at all. Each is asked SAMPLES times and every answer
    has to be right.
    """
    good, seen = 0, []
    for _ in range(SAMPLES):
        ok, note = judge(head(SITE + path))
        good += ok
        seen.append(note)
    return good, seen


def spread(seen: list[str]) -> str:
    """The distinct answers, worst first, so a wrong one is never hidden behind a right one."""
    counts: dict[str, int] = {}
    for s in seen:
        counts[s] = counts.get(s, 0) + 1
    return ", ".join(f"{s or '(none)'} ×{n}" for s, n in sorted(counts.items(), key=lambda kv: kv[1]))


def header_ok(path: str, header: str, want: str) -> tuple[bool, str]:
    """Whether the server declares what it should, every time it is asked."""
    def judge(r):
        code, headers, _ = r
        got = headers.get(header, "") if code == 200 else f"HTTP {code}"
        return want in got and code == 200, got
    good, seen = sample(path, judge)
    note = spread(seen)
    if good < SAMPLES:
        note += f"   —  right {good} of {SAMPLES} times"
    return good == SAMPLES, note


def redirect_ok(path: str, want: str) -> tuple[bool, str]:
    """Whether the old address sends the reader on to the short one, every time it is asked."""
    def judge(r):
        code, _, where = r
        ok = code == 301 and where.split("?")[0].endswith(want)
        return ok, f"{code} -> {where.split('?')[0] or '(nowhere)'}"
    good, seen = sample(path, judge)
    note = spread(seen)
    if good < SAMPLES:
        note += f"   —  right {good} of {SAMPLES} times"
    return good == SAMPLES, note


def check() -> int:
    """Read the live site, asking each question enough times to catch an answer that varies."""
    print(f"\nchecking    {SITE}   ({SAMPLES} requests per line)")
    bad = 0

    for path, header, want in EXPECTED:
        ok, note = header_ok(path, header, want)
        bad += not ok
        print(f"  {'ok  ' if ok else 'BAD '} {path}  {header}: {note}")

    for path, want in REDIRECTS:
        ok, note = redirect_ok(path, want)
        bad += not ok
        print(f"  {'ok  ' if ok else 'BAD '} {path}  {note}")

    broken = [(p, c) for p in PAGES for c in [head(SITE + p)[0]] if c != 200]
    bad += len(broken)
    if broken:
        for path, code in broken:
            print(f"  BAD  {path}  {code}")
    else:
        print(f"  ok   all {len(PAGES)} pages and assets return 200")

    if bad:
        print(f"\n{bad} checks failed.")
        print("A line that is right some of the time and not others is the host's edge servers")
        print("holding a copy taken before the .htaccess arrived. Clear the cache in hPanel,")
        print("under the site's Performance section, and run this again.")
    else:
        print("\neverything the site should be serving, it is serving, on every request")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish the built site to the web host.")
    ap.add_argument("--set-password", action="store_true",
                    help="take the FTP password and put it in the keychain")
    ap.add_argument("--check", action="store_true", help="check the live site and change nothing")
    ap.add_argument("--dry-run", action="store_true", help="list what would be sent and removed")
    args = ap.parse_args()

    if args.set_password:
        return store_password()
    if args.check:
        return check()
    publish(args.dry_run)
    return 0 if args.dry_run else check()


if __name__ == "__main__":
    raise SystemExit(main())
