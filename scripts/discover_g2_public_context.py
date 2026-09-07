"""Bounded HTML-only public access-context inspection; no dashboard queries."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

from gfjd.g2_successor_transport import (
    PeerBoundHTTPSConnection,
    bounded_read,
    resolve_public_addresses,
)

ROOT = Path(__file__).resolve().parents[1]
LINEAGE = "G2-PUBLIC-CONTEXT-20260907-01"
PLAN = Path(f"data/methods/g2/{LINEAGE}/plan.json")
ENTRY = "https://www.gov.uk/government/collections/family-court-statistics-quarterly"
RECEIPT = Path("docs/governance/g2-public-context-receipt-2026-09-07.json")
CONTRACT = {
    "lineage_id": LINEAGE,
    "entry": ENTRY,
    "maximum_requests": 4,
    "maximum_release_pages": 2,
    "maximum_view_pages": 1,
    "maximum_accepted_body_bytes": 2000000,
    "maximum_body_read_bytes": 2000001,
    "socket_timeout_seconds": 30,
    "retries": 0,
    "redirects": False,
    "cookies": False,
    "credentials": False,
    "scripts": False,
    "raw_body_retention": False,
    "query_execution": False,
    "g2_acceptance": False,
    "selector": "newest_explicit_calendar_quarter_then_unique_dashboard_link",
}
QUARTERS = {
    "january-to-march": 1,
    "april-to-june": 2,
    "july-to-september": 3,
    "october-to-december": 4,
}
RELEASE = re.compile(
    r"/government/statistics/family-court-statistics-quarterly-(january-to-march|april-to-june|july-to-september|october-to-december)-(20[0-9]{2})$"
)


class ContextStop(ValueError):
    """Only fixed, non-source-derived messages may be recorded."""


def require(condition, reason):
    if not condition:
        raise ContextStop(reason)


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def validate_url(url, kind):
    require(len(url) <= 8192 and not any(c.isspace() or ord(c) < 32 for c in url), "URL syntax")
    parsed = urlsplit(url)
    require(
        parsed.scheme == "https" and not parsed.username and not parsed.password, "HTTPS identity"
    )
    require(
        parsed.port is None and not parsed.fragment and "\\" not in url, "URL authority or fragment"
    )
    if kind == "view":
        require(parsed.netloc == "app.powerbi.com" and parsed.path == "/view", "view host or path")
        query = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
        require(
            set(query) == {"r"} and len(query["r"]) == 1 and query["r"][0],
            "view parameter ambiguity",
        )
    else:
        require(
            parsed.netloc == "www.gov.uk" and not parsed.query and "%" not in parsed.path,
            "GOV.UK URL",
        )
        require(
            url == ENTRY
            or bool(RELEASE.fullmatch(parsed.path))
            or bool(RELEASE.fullmatch(parsed.path.rsplit("/", 1)[0])),
            "release path",
        )
    return parsed


def safe_locator(url, kind):
    parsed = validate_url(url, kind)
    result = {"base_url": f"https://{parsed.netloc}{parsed.path}", "url_sha256": digest(url)}
    if kind == "view":
        result["resource_parameter_sha256"] = digest(parse_qs(parsed.query)["r"][0])
    return result


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.anchor = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        require(tag != "base", "base element changes URL interpretation")
        names = [key for key, _ in attrs]
        require(names.count("href") <= 1 and names.count("src") <= 1, "duplicate URL attribute")
        attrs = dict(attrs)
        if tag == "a":
            require(self.anchor is None, "nested anchor")
            self.anchor = attrs.get("href")
            self.text = []
        if tag == "iframe" and attrs.get("src"):
            self.links.append((attrs["src"], ""))
        require(len(self.links) <= 5000, "link count limit")

    def handle_data(self, data):
        if self.anchor is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor is not None:
            self.links.append((self.anchor, " ".join(self.text)))
            self.anchor = None
            self.text = []


def parse_links(raw, page):
    parser = Links()
    parser.feed(raw.decode("utf-8"))
    parser.close()
    require(parser.anchor is None and len(parser.links) <= 5000, "incomplete or excess links")
    return [(urljoin(page, href), text) for href, text in parser.links]


def choose_release(links):
    candidates = {}
    for url, _ in links:
        parsed = urlsplit(url)
        match = RELEASE.fullmatch(parsed.path)
        if parsed.hostname == "www.gov.uk" and match:
            validate_url(url, "release")
            candidates[url] = (int(match[2]), QUARTERS[match[1]])
    require(candidates, "no explicit quarterly release")
    newest = max(candidates.values())
    selected = [url for url, period in candidates.items() if period == newest]
    require(len(selected) == 1, "ambiguous newest release")
    return selected[0]


def choose_next(links, page, allow_detail):
    views = set()
    details = set()
    for url, label in links:
        parsed = urlsplit(url)
        if parsed.hostname == "app.powerbi.com":
            validate_url(url, "view")
            views.add(url)
        elif allow_detail and "dashboard" in label.lower() and url.startswith(page + "/"):
            validate_url(url, "release")
            details.add(url)
    require(len(views) <= 1, "ambiguous public view")
    if views:
        return next(iter(views)), "view"
    require(allow_detail and len(details) == 1, "missing or ambiguous dashboard detail")
    return next(iter(details)), "release"


def fetch_html(url, kind):
    parsed = validate_url(url, kind)
    connection = PeerBoundHTTPSConnection(
        parsed.hostname, validated_addresses=resolve_public_addresses(parsed.hostname), timeout=30
    )
    try:
        connection.request(
            "GET",
            parsed.path + ("?" + parsed.query if parsed.query else ""),
            headers={"User-Agent": "GFJD-public-context/1.0", "Accept-Encoding": "identity"},
        )
        response = connection.getresponse()
        require(response.status == 200, f"HTTP status {response.status}")
        require(
            response.getheader("Content-Type", "").split(";")[0].lower() == "text/html",
            "HTML media type required",
        )
        require(
            response.getheader("Content-Encoding", "identity") == "identity", "content encoding"
        )
        return bounded_read(response, maximum_bytes=2000000)
    finally:
        connection.close()


def checkpoint(path, value):
    pending = path.with_suffix(".pending")
    fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(value, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    pending.replace(path)


def execute(root, freeze, fetcher=fetch_html):
    plan_bytes = (root / PLAN).read_bytes()
    require(
        json.dumps(json.loads(plan_bytes), sort_keys=True) == json.dumps(CONTRACT, sort_keys=True),
        "plan binding",
    )
    receipt_path = root / RECEIPT
    lock = root / "data/raw/files" / LINEAGE
    for path in (receipt_path, lock):
        require(not any(part.is_symlink() for part in (path, *path.parents)), "output symlink")
        require(not path.exists(), "lineage already attempted")
    lock.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock.mkdir(mode=0o700)
    receipt = {
        "lineage_id": LINEAGE,
        "freeze_commit": freeze,
        "plan_sha256": digest(plan_bytes),
        "started_at": datetime.now(UTC).isoformat(),
        "state": "running",
        "requests": [],
        "request_contract_qualified": False,
        "extraction_performed": False,
        "g2_acceptance": False,
        "raw_body_retention": False,
    }
    checkpoint(receipt_path, receipt)
    url, kind = ENTRY, "entry"
    release_count = 0
    try:
        for _ in range(4):
            record = {
                **safe_locator(url, kind),
                "kind": kind,
                "method": "GET",
                "requested": True,
                "state": "attempted",
                "attempted_at": datetime.now(UTC).isoformat(),
            }
            receipt["requests"].append(record)
            checkpoint(receipt_path, receipt)
            raw = fetcher(url, kind)
            require(len(raw) <= 2000000, "body budget")
            links = parse_links(raw, url)
            record.update(
                state="observed",
                body_sha256=digest(raw),
                body_bytes=len(raw),
                link_count=len(links),
            )
            raw = None
            checkpoint(receipt_path, receipt)
            if kind == "view":
                receipt["state"] = "public_entry_observed_contract_pending"
                receipt["missing_evidence"] = [
                    "source-derived anonymous request-header contract",
                    "current report and model binding",
                ]
                break
            if kind == "entry":
                url, kind = choose_release(links), "release"
            else:
                release_count += 1
                url, kind = choose_next(links, url, release_count < 2)
        else:
            raise ContextStop("request budget exhausted")
    except Exception as error:
        receipt["state"] = "terminal_stop"
        receipt["failure_type"] = type(error).__name__
        receipt["failure_reason"] = (
            str(error) if type(error) is ContextStop else "transport_or_parse_failure"
        )
    finally:
        receipt["finished_at"] = datetime.now(UTC).isoformat()
        checkpoint(receipt_path, receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require(head == args.freeze_commit, "freeze is not HEAD")
    subprocess.run(
        [
            "git",
            "-c",
            f"gpg.ssh.allowedSignersFile={ROOT / 'config/ssh_allowed_signers'}",
            "verify-commit",
            head,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "diff", "--quiet", head, "--"], cwd=ROOT, check=True)
    tracked = subprocess.check_output(["git", "show", f"{head}:{PLAN.as_posix()}"], cwd=ROOT)
    require(tracked == (ROOT / PLAN).read_bytes(), "plan differs from freeze")
    result = execute(ROOT, head)
    print(json.dumps({"state": result["state"], "receipt": RECEIPT.as_posix()}))
    return 2 if result["state"] == "terminal_stop" else 0


if __name__ == "__main__":
    raise SystemExit(main())
