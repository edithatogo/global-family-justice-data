from __future__ import annotations

import json
from pathlib import Path

import pytest

from gfjd.g2_role_isolation import (
    G2RoleIsolationError,
    build_role_workspace,
    verify_role_workspace,
)
from gfjd.io import sha256_file


def _input(path: Path, root: Path, target_name: str) -> dict[str, str]:
    return {
        "source_path": path.relative_to(root).as_posix(),
        "target_name": target_name,
        "sha256": sha256_file(path),
    }


def test_builds_minimal_digest_bound_workspace(project_root: Path, tmp_path: Path) -> None:
    source = project_root / "build" / f"{tmp_path.name}-isolation-source.bin"
    source.parent.mkdir(exist_ok=True)
    source.write_bytes(b"aggregate evidence")
    destination = project_root / "build" / f"{tmp_path.name}-isolated-role"

    receipt_path = build_role_workspace(
        project_root,
        destination=destination,
        packet_id="G2PKT-TEST-ISOLATION",
        role="extractor_a",
        source_commit="a" * 40,
        generated_at="2026-08-26T00:00:00Z",
        inputs=[_input(source, project_root, "source-01.bin")],
    )

    assert sorted(path.name for path in destination.iterdir()) == [
        "inputs",
        "isolation-receipt.json",
    ]
    assert (destination / "inputs" / "source-01.bin").read_bytes() == b"aggregate evidence"
    assert verify_role_workspace(project_root, destination) == []
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["workspace_policy"] == "explicit_allowlist_only"
    assert receipt["source_contents_embedded_in_receipt"] is False


def test_rejects_existing_workspace(project_root: Path, tmp_path: Path) -> None:
    destination = project_root / "build" / f"{tmp_path.name}-existing-role"
    destination.mkdir(parents=True, exist_ok=True)
    with pytest.raises(G2RoleIsolationError, match="already exists"):
        build_role_workspace(
            project_root,
            destination=destination,
            packet_id="G2PKT-TEST-ISOLATION",
            role="extractor_a",
            source_commit="a" * 40,
            generated_at="2026-08-26T00:00:00Z",
            inputs=[{"source_path": "missing", "target_name": "x", "sha256": "0" * 64}],
        )


def test_rejects_digest_mismatch_and_target_traversal(project_root: Path, tmp_path: Path) -> None:
    source = project_root / "build" / f"{tmp_path.name}-isolation-mismatch.bin"
    source.parent.mkdir(exist_ok=True)
    source.write_bytes(b"evidence")
    common = {
        "root": project_root,
        "destination": project_root / "build" / f"{tmp_path.name}-mismatch-role",
        "packet_id": "G2PKT-TEST-ISOLATION",
        "role": "extractor_a",
        "source_commit": "a" * 40,
        "generated_at": "2026-08-26T00:00:00Z",
    }
    with pytest.raises(G2RoleIsolationError, match="digest differs"):
        build_role_workspace(
            **common,
            inputs=[
                {
                    "source_path": source.relative_to(project_root).as_posix(),
                    "target_name": "source.bin",
                    "sha256": "0" * 64,
                }
            ],
        )
    with pytest.raises(G2RoleIsolationError, match="invalid target_name"):
        build_role_workspace(
            **common,
            inputs=[_input(source, project_root, "../source.bin")],
        )


def test_verifier_detects_extra_file_and_tampering(project_root: Path, tmp_path: Path) -> None:
    source = project_root / "build" / f"{tmp_path.name}-isolation-tamper.bin"
    source.parent.mkdir(exist_ok=True)
    source.write_bytes(b"original")
    destination = project_root / "build" / f"{tmp_path.name}-tamper-role"
    build_role_workspace(
        project_root,
        destination=destination,
        packet_id="G2PKT-TEST-ISOLATION",
        role="extractor_b",
        source_commit="a" * 40,
        generated_at="2026-08-26T00:00:00Z",
        inputs=[_input(source, project_root, "source.bin")],
    )
    (destination / "inputs" / "source.bin").write_bytes(b"tampered-longer")
    (destination / "unexpected").write_text("x", encoding="utf-8")

    errors = verify_role_workspace(project_root, destination)
    assert any("unexpected workspace entries" in error for error in errors)
    assert any("byte count differs" in error for error in errors)
    assert any("digest differs" in error for error in errors)
