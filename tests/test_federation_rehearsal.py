"""Fictional federation integration; generated reports never confer authority."""

import json
import runpy
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/rehearse_federation_bundle.py"


def test_forged_report_cannot_pass(tmp_path: Path) -> None:
    script = runpy.run_path(str(SCRIPT))
    report = tmp_path / "forged.json"
    report.write_bytes(b'{"synthetic":false,"publication_authorized":true}')
    assert script["main"](["--verify", str(report)]) == 1


def test_deterministic_complete_machinery_with_pending_facts() -> None:
    script = runpy.run_path(str(SCRIPT))
    report = script["build_report"]()
    assert report == script["build_report"]()
    assert report["synthetic"] is True
    assert report["factual_evidence"] == "unverified"
    assert report["metadata_route_count"] == 4
    assert report["estate_role_count"] == 6
    assert report["provenance_pending_object_ids"] == ["fictional-1", "fictional-2", "fictional-3"]
    assert not any(report["authority"].values())
    assert report["incomplete_metadata_preserved"] is True
    assert len(report["negative_cases_rejected"]) == 4
    assert "FICTIONAL_INPUT_ONLY_MARKER" not in json.dumps(report)


def test_roundtrip_refuses_changed_report_without_overwrite(tmp_path: Path) -> None:
    script = runpy.run_path(str(SCRIPT))
    output = tmp_path / "nested/report.json"
    assert script["main"](["--output", str(output)]) == 0
    assert script["main"](["--output", str(output)]) == 0
    assert script["main"](["--verify", str(output)]) == 0
    changed = json.loads(output.read_bytes())
    changed["authority"]["publication"] = True
    tampered = json.dumps(changed).encode()
    output.write_bytes(tampered)
    assert script["main"](["--verify", str(output)]) == 1
    assert script["main"](["--output", str(output)]) == 1
    assert output.read_bytes() == tampered


def test_missing_report_not_created(tmp_path: Path) -> None:
    script = runpy.run_path(str(SCRIPT))
    output = tmp_path / "missing.json"
    assert script["main"](["--verify", str(output)]) == 1
    assert not output.exists()


def test_no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    import socket
    import urllib.request

    def forbidden(*args, **kwargs):
        raise AssertionError("network requested")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    script = runpy.run_path(str(SCRIPT))
    assert script["build_report"]()["synthetic"] is True


def test_symlink_target_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = runpy.run_path(str(SCRIPT))
    output = tmp_path / "link.json"
    original = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda path: path == output or original(path))
    assert script["main"](["--output", str(output)]) == 1
    assert not output.exists()


def test_symlink_ancestor_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = runpy.run_path(str(SCRIPT))
    output = tmp_path / "linked/report.json"
    original = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda path: path == output.parent or original(path))
    assert script["main"](["--output", str(output)]) == 1
    assert not output.exists()


def test_input_counterexample_does_not_rely_on_changed_output_hash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from gfjd.federation_metadata import MetadataError

    script = runpy.run_path(str(SCRIPT))
    original = script["prepare_replayed_bundle"]
    good = script["fictional_inputs"]()

    def defective_prepare(*inputs):
        scoped = json.loads(inputs[0])
        if scoped["objects"][0]["content_sha256"] == "0" * 64:
            result = original(*good)
            manifest = json.loads(result["bundle-manifest.json"])
            manifest["scope_sha256"] = inputs[1]
            result["bundle-manifest.json"] = script["canonical"](manifest)
            return result
        return original(*inputs)

    def defective_verify(*args):
        if defective_prepare(*args[:-1]) != args[-1]:
            raise MetadataError("output mismatch")

    scope = script["build_report"].__globals__
    monkeypatch.setitem(scope, "prepare_replayed_bundle", defective_prepare)
    monkeypatch.setitem(scope, "verify_replayed_bundle", defective_verify)
    with pytest.raises(ValueError, match="negative case was accepted"):
        script["build_report"]()


def test_special_file_not_opened(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = runpy.run_path(str(SCRIPT))
    target = tmp_path / "special"
    target.write_bytes(b"placeholder")
    original = Path.lstat
    monkeypatch.setattr(
        Path,
        "lstat",
        lambda path: SimpleNamespace(st_mode=stat.S_IFIFO) if path == target else original(path),
    )

    def forbidden(*args):
        raise AssertionError("special file was opened")

    monkeypatch.setitem(script["main"].__globals__, "read_report", forbidden)
    assert script["main"](["--verify", str(target)]) == 1


def test_descriptor_type_checked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import os

    script = runpy.run_path(str(SCRIPT))
    target = tmp_path / "raced"
    target.write_bytes(b"regular before open")
    monkeypatch.setattr(os, "fstat", lambda fd: SimpleNamespace(st_mode=stat.S_IFIFO))
    with pytest.raises(ValueError, match="nonregular"):
        script["read_report"](target, 10)


def test_content_addressed_report_directory(tmp_path: Path) -> None:
    script = runpy.run_path(str(SCRIPT))
    output = tmp_path / "reports"
    assert script["main"](["--verify-directory", str(output)]) == 1
    assert script["main"](["--output-directory", str(output)]) == 0
    assert script["main"](["--verify-directory", str(output)]) == 0
    files = list(output.iterdir())
    assert len(files) == 1
    assert files[0].name == "report-" + script["sha"](files[0].read_bytes()) + ".json"
    files[0].write_bytes(b"forged")
    assert script["main"](["--output-directory", str(output)]) == 1
    assert files[0].read_bytes() == b"forged"
