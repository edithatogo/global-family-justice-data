"""Offline checks for historical metadata preparation and read-only verification."""

import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "prepare_hosted_metadata_corrections.py"


@pytest.mark.parametrize("optimized", [False, True])
def test_changed_predecessor_rejected_without_output(tmp_path: Path, optimized: bool) -> None:
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "catalog.json").write_text('{"datasets": []}')
    output = tmp_path / "output"
    command = [sys.executable] + (["-O"] if optimized else [])
    result = subprocess.run(
        command + [str(SCRIPT), "--registry-snapshot", str(snapshot), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Registry predecessor changed" in result.stderr
    assert not output.exists()


@pytest.fixture
def verifier(monkeypatch):
    hub = ModuleType("huggingface_hub")
    hub.HfApi = object
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)
    monkeypatch.setitem(sys.modules, "httpx", ModuleType("httpx"))
    module = runpy.run_path(str(SCRIPT.with_name("verify_hosted_metadata_prs.py")))
    payload = json.loads(module["RECEIPT"].read_text())
    for receipt in payload["receipts"]:
        receipt["sha256"] = {
            name: hashlib.sha256(b"metadata").hexdigest() for name in receipt["sha256"]
        }
    return module, payload


@pytest.mark.parametrize("bad", ["repo", "path", "digest", "revision"])
def test_invalid_binding_fails_before_api(verifier, bad):
    module, payload = verifier
    receipt = payload["receipts"][0]
    if bad == "repo":
        receipt["repo_id"] = "someone/else"
    elif bad == "path":
        receipt["changed_paths"] = ["sources/document.pdf"]
    elif bad == "digest":
        receipt["sha256"]["catalog.json"] = "not-a-hash"
    else:
        receipt["merged_revision"] = "main"
    with pytest.raises(ValueError):
        module["verify"](payload, object())


def fake_api(payload, *, tree_drift=False):
    def listing(repo, *, revision, **kwargs):
        receipt = next(x for x in payload["receipts"] if x["repo_id"] == repo)
        tree = {
            name: "old" if revision == receipt["parent"] else "new"
            for name in receipt["changed_paths"]
        }
        tree["sources/preserved.pdf"] = "unchanged"
        if tree_drift and revision == receipt["merged_revision"]:
            tree["sources/preserved.pdf"] = "changed"
        return [SimpleNamespace(path=path, blob_id=blob) for path, blob in tree.items()]

    return SimpleNamespace(list_repo_tree=listing)


def test_read_only_verification_needs_no_mutation_api(verifier, monkeypatch):
    module, payload = verifier
    calls = []

    def metadata(repo, revision, name):
        calls.append(name)
        return b"metadata"

    monkeypatch.setitem(module["verify"].__globals__, "metadata", metadata)
    result = module["verify"](payload, fake_api(payload))
    assert result["read_only"] is True
    assert len(result["verified"]) == 2
    assert set(calls) == {"catalog.json", "README.md", "archive_inventory.csv"}


@pytest.mark.parametrize("tree_drift", [True, False])
def test_tree_or_readback_mismatch_fails(verifier, monkeypatch, tree_drift):
    module, payload = verifier
    monkeypatch.setitem(module["verify"].__globals__, "metadata", lambda *args: b"wrong")
    with pytest.raises(ValueError, match="Merged tree differs|Anonymous digest differs"):
        module["verify"](payload, fake_api(payload, tree_drift=tree_drift))


def test_metadata_disallows_source_request(verifier):
    module, _ = verifier
    with pytest.raises(ValueError, match="Forbidden metadata request"):
        module["metadata"]("edithatogo/gfjd-source-archive", "a" * 40, "sources/file.pdf")
