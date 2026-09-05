"""Verify and optionally merge the two bounded September 5 HF metadata PRs.

Uses the authenticated HF SDK for merge and anonymous HTTPS for metadata readback.
Never requests source documents. Refuses changed predecessors or unrelated edits.
"""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
from huggingface_hub import HfApi


def require(condition, message):
    if not condition:
        raise ValueError(message)


def metadata(repo, revision, name):
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


def verify_pr_head(api, repo, proposed):
    require(
        api.repo_info(repo, repo_type="dataset", revision="refs/pr/1").sha == proposed,
        "PR head changed",
    )


def checkpoint(path, receipts, requested, complete=False, error=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "observed_at": datetime.now(UTC).isoformat(),
        "merge_requested": requested,
        "merged": requested and complete,
        "complete": complete,
        "source_requests": 0,
        "gate_acceptance": False,
        "receipts": receipts,
    }
    if error is not None:
        payload["error"] = error
    staging = path.with_suffix(path.suffix + ".tmp")
    with staging.open("x") as handle:
        handle.write(json.dumps(payload, indent=2) + "\n")
    staging.replace(path)


def finish(api, receipts, output, merge):
    checkpoint(output, receipts, merge)
    try:
        for receipt in receipts:
            repo = receipt["repo_id"]
            require(
                api.repo_info(repo, repo_type="dataset").sha == receipt["parent"], "Main changed"
            )
            verify_pr_head(api, repo, receipt["proposed"])
            if merge:
                receipt["merge_attempted"] = True
                checkpoint(output, receipts, merge)
                api.merge_pull_request(
                    repo,
                    1,
                    repo_type="dataset",
                    comment=(
                        "Exact metadata and unchanged source tree verified; "
                        "no rights or gate acceptance."
                    ),
                )
                receipt["merge_api_returned"] = True
                checkpoint(output, receipts, merge)
                revision = api.repo_info(repo, repo_type="dataset").sha
                receipt["observed_revision_after_merge"] = revision
                checkpoint(output, receipts, merge)
                require(
                    tree(api, repo, revision) == tree(api, repo, receipt["proposed"]),
                    "Merged tree differs",
                )
                for name, expected in receipt["sha256"].items():
                    require(
                        hashlib.sha256(metadata(repo, revision, name)).hexdigest() == expected,
                        "Anonymous readback differs",
                    )
                receipt.update(merged_revision=revision, anonymous_exact_revision_readback=True)
                checkpoint(output, receipts, merge)
        checkpoint(output, receipts, merge, complete=True)
    except Exception as exc:
        checkpoint(output, receipts, merge, error=type(exc).__name__)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Receipt already exists")
    api = HfApi()
    cases = [
        (
            "edithatogo/dataset-estate-registry",
            "2e85d5b56162d532caaa37c7d9f6a30e63621204",
            "e8a67aab180328f74d9f954ef0d0cc5facd307c3",
            {"catalog.json": "build/hosted-metadata-release-20260905/catalog.json"},
        ),
        (
            "edithatogo/gfjd-source-archive",
            "3f534c86d7b72978963049f6007df1dccd27e601",
            "745561e7e24f04fa5400e229f38619274422a94f",
            {
                "archive_inventory.csv": "data/raw/archive_inventory.csv",
                "README.md": "build/hosted-metadata-corrections-20260905/source-archive-README.md",
            },
        ),
    ]
    receipts = []
    for repo, parent, proposed, files in cases:
        require(api.repo_info(repo, repo_type="dataset").sha == parent, "Main changed")
        before = tree(api, repo, parent)
        after = tree(api, repo, proposed)
        changed = {key for key in before.keys() | after.keys() if before.get(key) != after.get(key)}
        require(changed == set(files), "Unexpected PR file changes")
        digests = {}
        for name, local in files.items():
            raw = metadata(repo, proposed, name)
            require(raw == Path(local).read_bytes(), "Proposed bytes differ")
            digests[name] = hashlib.sha256(raw).hexdigest()
        discussion = api.get_discussion_details(repo, 1, repo_type="dataset")
        require(discussion.is_pull_request and discussion.status == "open", "PR not open")
        verify_pr_head(api, repo, proposed)
        receipts.append(
            {
                "repo_id": repo,
                "parent": parent,
                "proposed": proposed,
                "changed_paths": sorted(changed),
                "sha256": digests,
                "pr_url": f"https://huggingface.co/datasets/{repo}/discussions/1",
            }
        )
    finish(api, receipts, args.output, args.merge)
    print(args.output)


if __name__ == "__main__":
    main()
