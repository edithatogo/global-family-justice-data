"""Read-only verification of the tracked September 5 HF metadata merge receipt.

Only metadata files are retrieved. No source documents or mutation APIs are used.
Run with the Hugging Face CLI Python environment providing huggingface_hub/httpx.
"""

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import httpx
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "docs/engineering/hosted-metadata-merge-receipt-2026-09-05.json"
ALLOWED = {
    "edithatogo/dataset-estate-registry": {"catalog.json"},
    "edithatogo/gfjd-source-archive": {"archive_inventory.csv", "README.md"},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_receipt(payload):
    require(payload.get("merged") is True, "Receipt does not record completion")
    receipts = payload.get("receipts", [])
    require(len(receipts) == len(ALLOWED), "Unexpected receipt count")
    require({r.get("repo_id") for r in receipts} == set(ALLOWED), "Forbidden repository")
    for receipt in receipts:
        allowed = ALLOWED[receipt["repo_id"]]
        paths = receipt.get("changed_paths", [])
        require(len(paths) == len(allowed) and set(paths) == allowed, "Forbidden path")
        require(set(receipt.get("sha256", {})) == allowed, "Digest paths differ")
        for digest in receipt["sha256"].values():
            require(
                isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), "Invalid digest"
            )
        for key in ("parent", "proposed", "merged_revision"):
            value = receipt.get(key)
            require(
                isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value), "Invalid revision"
            )
    return receipts


def metadata(repo, revision, name):
    require(repo in ALLOWED and name in ALLOWED[repo], "Forbidden metadata request")
    response = httpx.get(
        f"https://huggingface.co/datasets/{repo}/resolve/{revision}/{name}",
        follow_redirects=True,
        timeout=60,
    )
    response.raise_for_status()
    return response.content


def tree(api, repo, revision):
    return {
        item.path: item.blob_id
        for item in api.list_repo_tree(repo, repo_type="dataset", revision=revision, recursive=True)
        if hasattr(item, "blob_id")
    }


def verify(payload, api):
    receipts = validate_receipt(payload)
    verified = []
    for receipt in receipts:
        repo = receipt["repo_id"]
        before = tree(api, repo, receipt["parent"])
        proposed = tree(api, repo, receipt["proposed"])
        merged = tree(api, repo, receipt["merged_revision"])
        changed = {
            key for key in before.keys() | proposed.keys() if before.get(key) != proposed.get(key)
        }
        require(changed == ALLOWED[repo], "Unexpected changed tree paths")
        require(proposed == merged, "Merged tree differs")
        for name, expected in receipt["sha256"].items():
            raw = metadata(repo, receipt["merged_revision"], name)
            require(hashlib.sha256(raw).hexdigest() == expected, "Anonymous digest differs")
        verified.append(
            {
                "repo_id": repo,
                "merged_revision": receipt["merged_revision"],
                "changed_paths": sorted(changed),
                "sha256": receipt["sha256"],
            }
        )
    return {
        "verified_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "source_requests": 0,
        "gate_acceptance": False,
        "verified": verified,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        require(not args.output.exists(), "Output already exists")
    raw = RECEIPT.read_bytes()
    result = verify(json.loads(raw), HfApi(token=False))
    result["execution_receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as handle:
            handle.write(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
