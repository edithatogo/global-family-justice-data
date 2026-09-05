"""Offline checks for the fixed historical metadata preparation contract."""

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
    command = [sys.executable]
    if optimized:
        command.append("-O")
    result = subprocess.run(
        command + [str(SCRIPT), "--registry-snapshot", str(snapshot), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Registry predecessor changed" in result.stderr
    assert not output.exists()


def test_integrity_require_raises_explicit_exception() -> None:
    module = runpy.run_path(str(SCRIPT))
    with pytest.raises(ValueError, match="integrity mismatch"):
        module["require"](False, "integrity mismatch")
    module["require"](True, "must not fail")


def load_verifier(monkeypatch: pytest.MonkeyPatch):
    hub = ModuleType("huggingface_hub")
    hub.HfApi = object
    monkeypatch.setitem(sys.modules, "huggingface_hub", hub)
    monkeypatch.setitem(sys.modules, "httpx", ModuleType("httpx"))
    return runpy.run_path(str(SCRIPT.with_name("verify_hosted_metadata_prs.py")))


def test_changed_pr_head_stops_before_merge(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    module = load_verifier(monkeypatch)
    merges = []
    api = SimpleNamespace(
        repo_info=lambda *a, **kw: SimpleNamespace(
            sha="different" if "revision" in kw else "parent"
        ),
        merge_pull_request=lambda *a, **kw: merges.append(a),
    )
    path = tmp_path / "receipt.json"
    with pytest.raises(ValueError, match="PR head changed"):
        module["finish"](
            api,
            [{"repo_id": "owner/repo", "parent": "parent", "proposed": "proposed", "sha256": {}}],
            path,
            True,
        )
    assert not merges
    receipt = json.loads(path.read_text())
    assert receipt["complete"] is False
    assert receipt["merged"] is False


def test_partial_merge_checkpoint_survives_later_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    module = load_verifier(monkeypatch)
    merged = set()

    def info(repo, **kwargs):
        if "revision" in kwargs:
            return SimpleNamespace(sha="proposed")
        return SimpleNamespace(sha="merged" if repo in merged else "parent")

    def merge(repo, *args, **kwargs):
        if repo == "owner/two":
            raise RuntimeError("provider unavailable")
        merged.add(repo)

    api = SimpleNamespace(repo_info=info, merge_pull_request=merge)
    monkeypatch.setitem(module["finish"].__globals__, "tree", lambda *args: {"a": "blob"})
    receipts = [
        {"repo_id": repo, "parent": "parent", "proposed": "proposed", "sha256": {}}
        for repo in ("owner/one", "owner/two")
    ]
    path = tmp_path / "receipt.json"
    with pytest.raises(RuntimeError, match="provider unavailable"):
        module["finish"](api, receipts, path, True)
    observed = json.loads(path.read_text())
    assert observed["complete"] is False
    assert observed["receipts"][0]["merged_revision"] == "merged"
    assert observed["receipts"][0]["anonymous_exact_revision_readback"] is True
    assert observed["receipts"][1]["merge_attempted"] is True
    assert "merged_revision" not in observed["receipts"][1]
