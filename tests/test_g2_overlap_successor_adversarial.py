from __future__ import annotations

import json
from pathlib import Path

import pytest

import gfjd.g2_overlap_successor as subject

ROOT = Path(__file__).resolve().parents[1]


def test_safe_path_rejects_escape_and_symlink(tmp_path: Path) -> None:
    assert subject._safe(tmp_path, "/tmp/out") is None
    assert subject._safe(tmp_path, "../out") is None
    target = tmp_path / "target"
    target.write_text("x")
    link = tmp_path / "link"
    link.symlink_to(target)
    assert subject._safe(tmp_path, "link") is None


@pytest.mark.parametrize(
    "exception",
    [OSError(), UnicodeDecodeError("utf-8", b"x", 0, 1, "bad"), json.JSONDecodeError("x", "x", 0)],
)
def test_invalid_design_json_fails_closed(
    monkeypatch: pytest.MonkeyPatch, exception: Exception
) -> None:
    monkeypatch.setattr(subject, "_load_object", lambda _path: (_ for _ in ()).throw(exception))
    assert subject.verify_overlap_successor_design(ROOT) == [
        "overlap successor design JSON is invalid"
    ]


def test_semantic_mutations_are_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = json.loads((ROOT / subject.DESIGN / "plan.json").read_text())
    ledger = json.loads((ROOT / subject.DESIGN / "ledger.json").read_text())
    queries = json.loads((ROOT / subject.DESIGN / "query-manifest.json").read_text())
    ledger["denied_urls"] = ["http://["] * 609
    ledger["predecessor"] = None
    queries["queries"][0]["query_order"] = 2
    queries["queries"][1]["query_sha256"] = "0" * 64
    plan["authorization_flags"]["network_access_authorized"] = True
    plan["authorization_flags"]["design_preparation_authorized"] = False
    values = iter((plan, ledger, queries))
    monkeypatch.setattr(subject, "_load_object", lambda _path: next(values))
    monkeypatch.setattr(subject, "_builder_output", lambda _root: None)
    errors = subject.verify_overlap_successor_design(ROOT)
    assert {
        "overlap successor builder cannot be loaded",
        "successor denied URL is invalid",
        "successor predecessor descriptor is missing",
        "successor exact query scope is invalid",
        "successor query digest mismatch",
        "successor plan authorizes prohibited activity",
        "successor preparation authority is missing",
    }.issubset(errors)


def test_projection_and_manifest_failures_are_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    plan = json.loads((ROOT / subject.DESIGN / "plan.json").read_text())
    ledger = json.loads((ROOT / subject.DESIGN / "ledger.json").read_text())
    queries = json.loads((ROOT / subject.DESIGN / "query-manifest.json").read_text())
    ledger["predecessor_chain"] = []
    ledger["cumulative_denied_url_count"] = 0
    values = iter((plan, ledger, queries))
    monkeypatch.setattr(subject, "_load_object", lambda _path: next(values))
    monkeypatch.setattr(
        subject,
        "_builder_output",
        lambda _root: {"plan": {}, "ledger": {}, "query_manifest": {}},
    )
    monkeypatch.setattr(subject, "MANIFEST", Path("missing-manifest"))
    errors = subject.verify_overlap_successor_design(ROOT)
    assert {
        "overlap successor builder equivalence mismatch",
        "successor predecessor chain projection mismatch",
        "successor cumulative denied URL count mismatch",
        "successor detached manifest is missing",
    }.issubset(errors)

    manifest = tmp_path / "manifest"
    manifest.write_text("bad\n" + "0" * 64 + "  missing\n" + "0" * 64 + "  missing\n")
    monkeypatch.setattr(subject, "MANIFEST", manifest.relative_to(tmp_path))
    monkeypatch.setattr(subject, "DESIGN", Path("design"))
    (tmp_path / "design").mkdir()
    for name, value in (
        ("plan.json", plan),
        ("ledger.json", ledger),
        ("query-manifest.json", queries),
    ):
        (tmp_path / "design" / name).write_text(json.dumps(value))
    values = iter((plan, ledger, queries))
    monkeypatch.setattr(subject, "_load_object", lambda _path: next(values))
    errors = subject.verify_overlap_successor_design(tmp_path)
    assert "successor detached manifest entry is malformed" in errors
    assert "successor detached manifest mismatch: missing" in errors
    assert "successor detached manifest omits a design artifact" in errors
