"""Execute the fixed prospective acquisition stage once, with no retry or redirect."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from gfjd.g2_successor_transport import (
    PeerBoundHTTPSConnection,
    bounded_read,
    resolve_public_addresses,
)

ROOT = Path(__file__).resolve().parents[1]
PLAN = Path("data/methods/g2/G2-DYNAMIC-SUCCESSOR-20260907-01/plan.json")
VAULT = Path("data/raw/files/G2-DYNAMIC-SUCCESSOR-20260907-01")
RECEIPT = Path("docs/governance/g2-dynamic-successor-capture-2026-09-07.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("non-finite JSON number")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def validate_bra(payload):
    require(isinstance(payload, dict), "BRA root is not object")
    require(set(payload) <= {"took", "timed_out", "_shards", "hits", "aggregations"}, "BRA fields")
    require(payload.get("timed_out") is False, "BRA timeout")
    require(type(payload.get("took")) is int and payload["took"] >= 0, "BRA duration")
    shards = payload.get("_shards", {})
    require(set(shards) <= {"total", "successful", "skipped", "failed"}, "BRA shard fields")
    require(all(type(value) is int and value >= 0 for value in shards.values()), "BRA shard types")
    require(shards.get("failed") == 0 and shards.get("total", 0) > 0, "BRA failed shards")
    require(shards.get("successful") == shards.get("total"), "BRA partial shards")
    hits = payload.get("hits", {})
    require(set(hits) <= {"total", "max_score", "hits"}, "BRA hit fields")
    require(hits.get("hits") == [], "BRA case hits")
    require(hits.get("max_score") is None, "BRA score")
    if "total" in hits:
        total = hits["total"]
        if isinstance(total, dict):
            require(set(total) == {"value", "relation"}, "BRA total fields")
            require(total["relation"] == "eq", "BRA approximate total")
            total = total["value"]
        require(type(total) is int and total >= 0, "BRA total type")
    require(set(payload.get("aggregations", {})) == {"case_classes"}, "BRA aggregation fields")
    aggregate = payload["aggregations"]["case_classes"]
    require(
        set(aggregate) == {"doc_count_error_upper_bound", "sum_other_doc_count", "buckets"},
        "BRA terms fields",
    )
    require(aggregate["doc_count_error_upper_bound"] == 0, "BRA approximate counts")
    require(aggregate["sum_other_doc_count"] == 0, "BRA truncated buckets")
    require(type(aggregate["doc_count_error_upper_bound"]) is int, "BRA error type")
    require(type(aggregate["sum_other_doc_count"]) is int, "BRA other type")
    buckets = aggregate["buckets"]
    require(isinstance(buckets, list) and 0 < len(buckets) <= 20, "BRA missing or excess buckets")
    for bucket in buckets:
        require(set(bucket) <= {"key", "key_as_string", "doc_count"}, "BRA bucket fields")
        require(str(bucket.get("key")) == "1389", "BRA unexpected class")
        if "key_as_string" in bucket:
            require(bucket["key_as_string"] == "1389", "BRA unexpected class label")
        require(type(bucket.get("doc_count")) is int and bucket["doc_count"] >= 0, "BRA count")


class DocumentText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def public_key(raw):
    parser = DocumentText()
    parser.feed(raw.decode("utf-8"))
    matches = set(re.findall(r"\bAPIKey\s+([A-Za-z0-9+/=]{20,512})", " ".join(parser.parts)))
    require(len(matches) == 1, "public key discovery ambiguous or absent")
    return matches.pop()


def metadata_boundary(value):
    forbidden = {
        "rows",
        "results",
        "hits",
        "data",
        "records",
        "cases",
        "contacts",
        "email",
        "firstname",
        "lastname",
        "address",
        "casenumber",
        "cpf",
        "partyname",
    }
    if isinstance(value, dict):
        require(not forbidden.intersection(key.lower() for key in value), "dashboard data boundary")
        for child in value.values():
            metadata_boundary(child)
    elif isinstance(value, list):
        for child in value:
            metadata_boundary(child)
    elif isinstance(value, str):
        require(
            not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", value), "dashboard contact boundary"
        )
        if value.lstrip().startswith(("{", "[")):
            metadata_boundary(strict_json(value))


def validate_models(payload):
    require(isinstance(payload, dict), "dashboard root is not object")
    require(set(payload) == {"models", "exploration"}, "dashboard root fields")
    metadata_boundary(payload)
    models = payload.get("models")
    require(isinstance(models, list), "dashboard models missing")
    require(
        sum(str(model.get("id")) == "3141088" for model in models) == 1, "dashboard model drift"
    )
    exploration = payload.get("exploration")
    require(isinstance(exploration, dict), "dashboard exploration missing")
    # No target values or data queries are derived by this structural stage.
    sections = exploration.get("sections")
    require(isinstance(sections, list), "dashboard sections missing")
    matches = 0
    for section in sections:
        for visual in section.get("visualContainers", []):
            configuration = visual.get("config")
            require(isinstance(configuration, str), "dashboard visual configuration")
            configuration = strict_json(configuration)
            matches += configuration.get("name") == "7945851748"
    require(matches == 1, "dashboard visual identity drift")


def validate_plan(plan):
    require(plan["lineage_id"] == "G2-DYNAMIC-SUCCESSOR-20260907-01", "lineage identity")
    require(plan["retries"] == 0 and plan["redirects"] is False, "retry or redirect policy")
    require(len(plan["requests"]) == plan["max_requests"] == 3, "request budget")
    expected = [
        (
            "public_key_document",
            "GET",
            "https://datajud-wiki.cnj.jus.br/api-publica/acesso",
            1000000,
            False,
        ),
        (
            "bra_aggregate",
            "POST",
            "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search",
            1000000,
            True,
        ),
        (
            "dashboard_models",
            "GET",
            "https://wabi-north-europe-e-primary-api.analysis.windows.net/public/reports/c809ac7e-68c0-41ae-8552-3e483d0d20b8/modelsAndExploration?preferReadOnlySession=true",
            10000000,
            True,
        ),
    ]
    for item, contract in zip(plan["requests"], expected, strict=True):
        require(
            tuple(item[key] for key in ("id", "method", "url", "maximum_bytes", "retain_body"))
            == contract,
            "request scope drift",
        )
        if item["id"] != "bra_aggregate":
            require("body" not in item, "unexpected request body")
    require(
        plan["requests"][1]["body"]
        == {
            "size": 0,
            "track_total_hits": False,
            "query": {"bool": {"must": [{"match": {"classe.codigo": 1389}}]}},
            "aggs": {"case_classes": {"terms": {"field": "classe.codigo", "size": 20}}},
        },
        "BRA request scope drift",
    )


def fetch(item, key):
    parsed = urlsplit(item["url"])
    require(parsed.scheme == "https" and parsed.hostname and not parsed.username, "HTTPS required")
    addresses = resolve_public_addresses(parsed.hostname)
    connection = PeerBoundHTTPSConnection(
        parsed.hostname, validated_addresses=addresses, timeout=30
    )
    body = json.dumps(item["body"], separators=(",", ":")).encode() if "body" in item else None
    headers = {"User-Agent": "GFJD-prospective-capture/1.0", "Accept-Encoding": "identity"}
    if item["id"] == "bra_aggregate":
        require(key, "public key unavailable")
        headers.update(Authorization=f"APIKey {key}", **{"Content-Type": "application/json"})
    try:
        connection.request(
            item["method"],
            parsed.path + ("?" + parsed.query if parsed.query else ""),
            body,
            headers,
        )
        response = connection.getresponse()
        require(response.status == 200, f"HTTP status {response.status}")
        require(
            response.getheader("Content-Encoding", "identity") == "identity", "content encoding"
        )
        content_type = response.getheader("Content-Type", "").split(";")[0].lower()
        expected_type = "text/html" if item["id"] == "public_key_document" else "application/json"
        require(content_type == expected_type, "content type")
        raw = bounded_read(response, maximum_bytes=item["maximum_bytes"])
        return raw, hashlib.sha256(body).hexdigest() if body else None
    finally:
        connection.close()


def checkpoint(path, receipt):
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(receipt, indent=2) + "\n")
    temporary.replace(path)


def execute(plan, vault, receipt_path, freeze_commit):
    validate_plan(plan)
    for target in (vault, receipt_path):
        require(target.is_relative_to(ROOT), "output outside repository")
        require(not any(part.is_symlink() for part in (target, *target.parents)), "output symlink")
    require(not vault.exists() and not receipt_path.exists(), "lineage already attempted")
    vault.mkdir(mode=0o700)
    receipt = {
        "lineage_id": plan["lineage_id"],
        "freeze_commit": freeze_commit,
        "plan_sha256": hashlib.sha256((ROOT / PLAN).read_bytes()).hexdigest(),
        "started_at": datetime.now(UTC).isoformat(),
        "state": "running",
        "requests": [],
        "quarantine": True,
        "extraction_performed": False,
        "g2_acceptance": False,
        "raw_source_publication": False,
        "retention_review_by": plan["retention_review_by"],
    }
    checkpoint(receipt_path, receipt)
    key = None
    try:
        for item in plan["requests"]:
            record = {
                "id": item["id"],
                "url": item["url"],
                "method": item["method"],
                "state": "attempted",
            }
            receipt["requests"].append(record)
            checkpoint(receipt_path, receipt)
            raw, request_sha = fetch(item, key)
            record.update(
                response_sha256=hashlib.sha256(raw).hexdigest(),
                bytes=len(raw),
                request_sha256=request_sha,
            )
            if item["id"] == "public_key_document":
                key = public_key(raw)
            elif item["id"] == "bra_aggregate":
                validate_bra(strict_json(raw))
            else:
                validate_models(strict_json(raw))
            if item["retain_body"]:
                destination = vault / (item["id"] + ".json")
                with destination.open("xb") as handle:
                    os.chmod(destination, 0o600)
                    handle.write(raw)
                require(
                    hashlib.sha256(destination.read_bytes()).hexdigest()
                    == record["response_sha256"],
                    "custody digest",
                )
                record["retained_path"] = destination.relative_to(ROOT).as_posix()
            record["state"] = "validated"
            checkpoint(receipt_path, receipt)
        receipt["state"] = "acquisition_stage_complete_pending_query_contract"
    except Exception as error:
        receipt["state"] = "terminal_stop"
        # Do not serialize response bodies, headers, credentials or arbitrary exception text.
        receipt["failure_type"] = type(error).__name__
        receipt["failure_reason"] = (
            str(error) if type(error) is ValueError else "transport_or_processing_failure"
        )
    finally:
        key = None
        receipt["finished_at"] = datetime.now(UTC).isoformat()
        checkpoint(receipt_path, receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-commit", required=True)
    args = parser.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require(head == args.freeze_commit, "freeze is not HEAD")
    subprocess.run(["git", "verify-commit", head], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(["git", "diff", "--quiet", head, "--"], cwd=ROOT, check=True)
    tracked = subprocess.check_output(["git", "show", f"{head}:{PLAN.as_posix()}"], cwd=ROOT)
    require(tracked == (ROOT / PLAN).read_bytes(), "plan binding differs")
    plan = strict_json(tracked)
    validate_plan(plan)
    receipt = execute(plan, ROOT / VAULT, ROOT / RECEIPT, head)
    print(json.dumps({"state": receipt["state"], "receipt": RECEIPT.as_posix()}))
    return 0 if receipt["state"] != "terminal_stop" else 2


if __name__ == "__main__":
    raise SystemExit(main())
