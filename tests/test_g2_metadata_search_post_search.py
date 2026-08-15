from __future__ import annotations

import hashlib
import json
import shutil
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

import gfjd.g2_metadata_search_post_search as post_search

NOW = datetime(2026, 8, 18, tzinfo=UTC)
GENERATED = "2026-08-16T02:00:00+00:00"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _write(path: Path, value: dict[str, Any]) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    return {"path": path.as_posix(), "sha256": _sha(path)}


def _root(project_root: Path, tmp_path: Path) -> Path:
    schema_dir = tmp_path / post_search.SCHEMA_ROOT
    schema_dir.mkdir(parents=True)
    for name in (
        "g2_metadata_search_post_search_receipt.schema.json",
        "g2_metadata_search_post_search_panel_input.schema.json",
        "g2_metadata_search_post_search_stop.schema.json",
        "g2_metadata_search_post_search_registrar_boundary.schema.json",
        "g2_metadata_search_post_search_registrar_event_log.schema.json",
        "g2_metadata_search_post_search_commit_attestation.schema.json",
    ):
        shutil.copyfile(project_root / post_search.SCHEMA_ROOT / name, schema_dir / name)
    return tmp_path


def _bundle() -> dict[str, Any]:
    value: dict[str, Any] = {
        "bundle_id": "G2-SUCCESSOR-FUTURE-TEST",
        "generated_at": "2026-08-16T01:00:00+00:00",
        "execution_date": "2026-08-16",
        "tool_name": "web__run.search_query",
        "tool_version": "test",
        "provider_config": {"logical_queries_per_call": 1},
        "query_events": [],
        "query_manifest": {"path": "frozen/query.json", "sha256": "1" * 64},
        "design_manifest": {"path": "frozen/design.sha256", "sha256": "2" * 64},
        "authority_receipt": {"path": "authority/receipt.json", "sha256": "3" * 64},
        "successor_provider_calls": 208,
        "successor_logical_query_submissions": 208,
        "successor_retries": 0,
        "prior_lineage_submissions": 4,
        "cumulative_lineage_submissions": 212,
        "violations": [],
    }
    start = datetime(2026, 8, 16, tzinfo=UTC)
    for index in range(208):
        call_start = start + timedelta(seconds=index * 2)
        value["query_events"].append(
            {
                "query_id": f"G2S2Q-{index + 1:03d}",
                "provider_call_started_at": call_start.isoformat(),
                "provider_call_finished_at": (call_start + timedelta(seconds=1)).isoformat(),
            }
        )
    value.update({field: 0 for field in post_search.ZERO_BOUNDARIES})
    return value


def _bundle_file(root: Path, bundle: dict[str, Any]) -> dict[str, str]:
    authority_path = root / "authority/receipt.json"
    authority = {"owner_decision_commit": "a" * 40}
    authority_descriptor = _write(authority_path, authority)
    authority_descriptor["path"] = authority_path.relative_to(root).as_posix()
    bundle["authority_receipt"] = authority_descriptor
    path = root / "future/registrar-bundle.json"
    descriptor = _write(path, bundle)
    descriptor["path"] = path.relative_to(root).as_posix()
    return descriptor


def _event_log_file(root: Path, bundle_descriptor: dict[str, str]) -> dict[str, str]:
    bundle = json.loads((root / bundle_descriptor["path"]).read_text())
    events = []
    for order, source in enumerate(bundle["query_events"], start=1):
        events.append(
            {
                "event_order": order,
                "occurred_at": source["provider_call_finished_at"],
                "event_type": "search_provider_call_completed",
                "query_id": source["query_id"],
                "non_search_network_requests": 0,
                "result_url_requests": 0,
                "landing_page_requests": 0,
                "source_file_requests": 0,
                "head_requests": 0,
                "redirects_followed": 0,
                "outbound_contacts": 0,
                "candidate_content_opened": False,
                "source_content_opened": False,
            }
        )
    generated_at = "2026-08-16T01:15:00+00:00"
    events.append(
        {
            "event_order": 209,
            "occurred_at": generated_at,
            "event_type": "boundary_closed",
            "query_id": None,
            "non_search_network_requests": 0,
            "result_url_requests": 0,
            "landing_page_requests": 0,
            "source_file_requests": 0,
            "head_requests": 0,
            "redirects_followed": 0,
            "outbound_contacts": 0,
            "candidate_content_opened": False,
            "source_content_opened": False,
        }
    )
    value = {
        "schema_version": "1.0",
        "event_log_id": "G2-METADATA-SEARCH-REGISTRAR-EVENT-LOG",
        "registrar_session_id": "REGISTRAR-SESSION-TEST",
        "run_id": bundle["bundle_id"],
        "generated_at": generated_at,
        "registrar_bundle": bundle_descriptor,
        "events": events,
    }
    path = root / "future/registrar-event-log.json"
    descriptor = _write(path, value)
    descriptor["path"] = path.relative_to(root).as_posix()
    return descriptor


def _boundary_file(
    root: Path,
    bundle_descriptor: dict[str, str],
    event_log_descriptor: dict[str, str],
) -> dict[str, str]:
    bundle = json.loads((root / bundle_descriptor["path"]).read_text())
    identity = {
        "bundle_id": bundle["bundle_id"],
        "execution_date": bundle["execution_date"],
        "tool_name": bundle["tool_name"],
        "tool_version": bundle["tool_version"],
        "query_manifest": bundle["query_manifest"],
        "design_manifest": bundle["design_manifest"],
        "authority_receipt": bundle["authority_receipt"],
    }
    value = {
        "schema_version": "1.0",
        "boundary_receipt_id": "G2-METADATA-SEARCH-REGISTRAR-BOUNDARY",
        "generated_at": "2026-08-16T01:30:00+00:00",
        "registrar_session_id": "REGISTRAR-SESSION-TEST",
        "run_id": bundle["bundle_id"],
        "registrar_bundle": bundle_descriptor,
        "registrar_event_log": event_log_descriptor,
        "execution_identity": identity,
        "execution_identity_sha256": hashlib.sha256(_canonical(identity)).hexdigest(),
        "provider_config_sha256": hashlib.sha256(_canonical(bundle["provider_config"])).hexdigest(),
        "query_event_transcript_sha256": hashlib.sha256(
            _canonical(bundle["query_events"])
        ).hexdigest(),
        "first_provider_call_started_at": bundle["query_events"][0]["provider_call_started_at"],
        "last_provider_call_finished_at": bundle["query_events"][-1]["provider_call_finished_at"],
        "search_provider_calls": 208,
        "logical_queries_submitted": 208,
        "successor_retries": 0,
        "prior_lineage_submissions": 4,
        "cumulative_lineage_submissions": 212,
        "non_search_network_requests": 0,
        "result_url_requests": 0,
        "landing_page_requests": 0,
        "source_file_requests": 0,
        "head_requests": 0,
        "redirects_followed": 0,
        "persisted_snippets": 0,
        "persisted_source_excerpts": 0,
        "persisted_target_facts": 0,
        "outbound_contacts": 0,
        "candidate_content_opened": False,
        "source_content_opened": False,
        "violations": [],
        "status": "captured_zero_boundary",
    }
    path = root / "future/registrar-boundary.json"
    descriptor = _write(path, value)
    descriptor["path"] = path.relative_to(root).as_posix()
    return descriptor


def _attestation_file(
    root: Path,
    bundle_descriptor: dict[str, str],
    boundary_descriptor: dict[str, str],
    event_log_descriptor: dict[str, str],
) -> dict[str, str]:
    bundle = json.loads((root / bundle_descriptor["path"]).read_text())
    authority = json.loads((root / bundle["authority_receipt"]["path"]).read_text())
    value = {
        "schema_version": "1.0",
        "attestation_id": "G2-METADATA-SEARCH-POST-EXECUTION-COMMIT-ATTESTATION",
        "generated_at": "2026-08-16T01:45:00+00:00",
        "registrar_session_id": "REGISTRAR-SESSION-TEST",
        "run_id": bundle["bundle_id"],
        "attested_commit": "b" * 40,
        "attested_commit_object_type": "commit",
        "signature": {
            "command": ["git", "verify-commit"],
            "status": "good",
            "verified_at": "2026-08-16T01:40:00+00:00",
        },
        "required_ancestor_commit": authority["owner_decision_commit"],
        "registrar_bundle": bundle_descriptor,
        "registrar_boundary_receipt": boundary_descriptor,
        "registrar_event_log": event_log_descriptor,
        "event_log_sha256": event_log_descriptor["sha256"],
        "tree_bindings": {
            "registrar_bundle": True,
            "registrar_boundary_receipt": True,
            "registrar_event_log": True,
        },
    }
    path = root / "future/post-execution-attestation.json"
    descriptor = _write(path, value)
    descriptor["path"] = path.relative_to(root).as_posix()
    return descriptor


def _inputs(
    root: Path, bundle: dict[str, Any]
) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    bundle_descriptor = _bundle_file(root, bundle)
    event_log_descriptor = _event_log_file(root, bundle_descriptor)
    boundary_descriptor = _boundary_file(root, bundle_descriptor, event_log_descriptor)
    attestation_descriptor = _attestation_file(
        root, bundle_descriptor, boundary_descriptor, event_log_descriptor
    )
    return (
        bundle_descriptor,
        boundary_descriptor,
        event_log_descriptor,
        attestation_descriptor,
    )


def _accept_upstream(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(post_search, "verify_successor_bundle", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(post_search, "_signed_attestation_errors", lambda *_args, **_kwargs: [])


def test_verified_receipt_and_reverification_are_fail_closed(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    descriptor, boundary, event_log, attestation = _inputs(root, _bundle())
    _accept_upstream(monkeypatch)
    receipt = post_search.build_verified_receipt(
        root,
        descriptor,
        boundary,
        event_log,
        attestation,
        generated_at=GENERATED,
        now=NOW,
    )
    assert receipt["status"] == "verified_for_advisory_panel_only"
    assert receipt["g2_passage"] is False
    assert post_search.verify_receipt(root, receipt, now=NOW) == []
    tampered = deepcopy(receipt)
    tampered["design_manifest"]["sha256"] = "f" * 64
    assert post_search.verify_receipt(root, tampered, now=NOW)


def test_post_search_rejects_upstream_failure_boundary_and_future_time(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    bundle = _bundle()
    descriptor, boundary, event_log, attestation = _inputs(root, bundle)
    monkeypatch.setattr(
        post_search,
        "verify_successor_bundle",
        lambda *_args, **_kwargs: ["authority binding failed"],
    )
    with pytest.raises(post_search.PostSearchVerificationError, match="authority binding"):
        post_search.build_verified_receipt(
            root,
            descriptor,
            boundary,
            event_log,
            attestation,
            generated_at=GENERATED,
            now=NOW,
        )
    _accept_upstream(monkeypatch)
    bundle["source_file_requests"] = 1
    descriptor, boundary, event_log, attestation = _inputs(root, bundle)
    with pytest.raises(post_search.PostSearchVerificationError, match="source_file_requests"):
        post_search.build_verified_receipt(
            root,
            descriptor,
            boundary,
            event_log,
            attestation,
            generated_at=GENERATED,
            now=NOW,
        )
    bundle["source_file_requests"] = 0
    descriptor, boundary, event_log, attestation = _inputs(root, bundle)
    with pytest.raises(post_search.PostSearchVerificationError, match="timestamp"):
        post_search.build_verified_receipt(
            root,
            descriptor,
            boundary,
            event_log,
            attestation,
            generated_at="2026-08-19T00:00:00+00:00",
            now=NOW,
        )


@pytest.mark.parametrize("path", ["/tmp/bundle.json", "../../bundle.json"])
def test_post_search_rejects_absolute_and_traversal_bundle_paths(
    project_root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    root = _root(project_root, tmp_path)
    _accept_upstream(monkeypatch)
    descriptor = {"path": path, "sha256": "0" * 64}
    boundary = {"path": "future/missing-boundary.json", "sha256": "0" * 64}
    event_log = {"path": "future/missing-events.json", "sha256": "0" * 64}
    attestation = {"path": "future/missing-attestation.json", "sha256": "0" * 64}
    with pytest.raises(post_search.PostSearchVerificationError, match="binding"):
        post_search.build_verified_receipt(
            root,
            descriptor,
            boundary,
            event_log,
            attestation,
            generated_at=GENERATED,
            now=NOW,
        )


def test_post_search_rejects_symlink_and_digest_swap(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    descriptor, boundary, event_log, attestation = _inputs(root, _bundle())
    real = root / descriptor["path"]
    link = root / "future/link.json"
    link.symlink_to(real)
    _accept_upstream(monkeypatch)
    with pytest.raises(post_search.PostSearchVerificationError, match="binding"):
        post_search.build_verified_receipt(
            root,
            {"path": link.relative_to(root).as_posix(), "sha256": descriptor["sha256"]},
            boundary,
            event_log,
            attestation,
            generated_at=GENERATED,
            now=NOW,
        )
    descriptor["sha256"] = "f" * 64
    with pytest.raises(post_search.PostSearchVerificationError, match="binding"):
        post_search.build_verified_receipt(
            root,
            descriptor,
            boundary,
            event_log,
            attestation,
            generated_at=GENERATED,
            now=NOW,
        )


def test_panel_input_is_descriptor_only_and_reverified(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    _accept_upstream(monkeypatch)
    bundle_descriptor, boundary, event_log, attestation = _inputs(root, _bundle())
    receipt = post_search.build_verified_receipt(
        root,
        bundle_descriptor,
        boundary,
        event_log,
        attestation,
        generated_at=GENERATED,
        now=NOW,
    )
    receipt_path = root / "future/post-search-receipt.json"
    receipt_descriptor = _write(receipt_path, receipt)
    receipt_descriptor["path"] = receipt_path.relative_to(root).as_posix()
    panel = post_search.build_panel_input_index(
        root,
        receipt_descriptor,
        generated_at="2026-08-16T03:00:00+00:00",
        now=NOW,
    )
    assert panel["descriptor_only"] is True
    assert panel["network_access"] is False
    assert panel["owner_decision_required"] is True
    assert post_search.verify_panel_input_index(root, panel, now=NOW) == []
    tampered_panel = deepcopy(panel)
    tampered_panel["registrar_bundle"]["sha256"] = "f" * 64
    assert post_search.verify_panel_input_index(root, tampered_panel, now=NOW)
    receipt_descriptor["sha256"] = "0" * 64
    with pytest.raises(post_search.PostSearchVerificationError, match="binding"):
        post_search.build_panel_input_index(
            root,
            receipt_descriptor,
            generated_at="2026-08-16T03:00:00+00:00",
            now=NOW,
        )


def test_post_search_rejects_contact_or_non_search_network_boundary(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    _accept_upstream(monkeypatch)
    bundle_descriptor, boundary_descriptor, event_log, attestation = _inputs(root, _bundle())
    boundary_path = root / boundary_descriptor["path"]
    boundary = json.loads(boundary_path.read_text())
    boundary["outbound_contacts"] = 1
    boundary["non_search_network_requests"] = 1
    boundary_descriptor = _write(boundary_path, boundary)
    boundary_descriptor["path"] = boundary_path.relative_to(root).as_posix()
    with pytest.raises(post_search.PostSearchVerificationError):
        post_search.build_verified_receipt(
            root,
            bundle_descriptor,
            boundary_descriptor,
            event_log,
            attestation,
            generated_at=GENERATED,
            now=NOW,
        )


def test_post_search_rejects_swapped_or_fabricated_execution_boundary(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    _accept_upstream(monkeypatch)
    bundle_descriptor, boundary_descriptor, event_log, attestation = _inputs(root, _bundle())
    boundary_path = root / boundary_descriptor["path"]
    mutations = []
    swapped_identity = json.loads(boundary_path.read_text())
    swapped_identity["execution_identity"]["bundle_id"] = "G2-SWAPPED-RUN"
    swapped_identity["execution_identity_sha256"] = hashlib.sha256(
        _canonical(swapped_identity["execution_identity"])
    ).hexdigest()
    mutations.append(swapped_identity)
    fabricated_transcript = json.loads(boundary_path.read_text())
    fabricated_transcript["query_event_transcript_sha256"] = "f" * 64
    mutations.append(fabricated_transcript)
    swapped_tool = json.loads(boundary_path.read_text())
    swapped_tool["execution_identity"]["tool_version"] = "attacker"
    swapped_tool["execution_identity_sha256"] = hashlib.sha256(
        _canonical(swapped_tool["execution_identity"])
    ).hexdigest()
    mutations.append(swapped_tool)
    for mutation in mutations:
        mutated_descriptor = _write(boundary_path, mutation)
        mutated_descriptor["path"] = boundary_path.relative_to(root).as_posix()
        with pytest.raises(post_search.PostSearchVerificationError, match="cross-check"):
            post_search.build_verified_receipt(
                root,
                bundle_descriptor,
                mutated_descriptor,
                event_log,
                attestation,
                generated_at=GENERATED,
                now=NOW,
            )


def test_post_search_rejects_unsafe_or_symlinked_boundary_receipt(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    _accept_upstream(monkeypatch)
    bundle_descriptor, boundary_descriptor, event_log, attestation = _inputs(root, _bundle())
    boundary_path = root / boundary_descriptor["path"]
    link = root / "future/boundary-link.json"
    link.symlink_to(boundary_path)
    for descriptor in (
        {"path": "../../boundary.json", "sha256": boundary_descriptor["sha256"]},
        {"path": link.relative_to(root).as_posix(), "sha256": boundary_descriptor["sha256"]},
    ):
        with pytest.raises(post_search.PostSearchVerificationError, match="binding"):
            post_search.build_verified_receipt(
                root,
                bundle_descriptor,
                descriptor,
                event_log,
                attestation,
                generated_at=GENERATED,
                now=NOW,
            )


def test_post_search_rejects_wrong_attested_session_run_and_event_digest(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    _accept_upstream(monkeypatch)
    bundle, boundary, event_log, attestation = _inputs(root, _bundle())
    attestation_path = root / attestation["path"]
    mutations = []
    wrong_session = json.loads(attestation_path.read_text())
    wrong_session["registrar_session_id"] = "WRONG-SESSION"
    mutations.append((wrong_session, "session"))
    wrong_run = json.loads(attestation_path.read_text())
    wrong_run["run_id"] = "WRONG-RUN"
    mutations.append((wrong_run, "run"))
    wrong_digest = json.loads(attestation_path.read_text())
    wrong_digest["event_log_sha256"] = "f" * 64
    mutations.append((wrong_digest, "attestation"))
    for value, expected_error in mutations:
        changed = _write(attestation_path, value)
        changed["path"] = attestation_path.relative_to(root).as_posix()
        if expected_error == "attestation":
            monkeypatch.undo()
            monkeypatch.setattr(
                post_search, "verify_successor_bundle", lambda *_args, **_kwargs: []
            )
            monkeypatch.setattr(
                post_search,
                "_signed_attestation_errors",
                lambda _root, observed, **kwargs: (
                    []
                    if observed["event_log_sha256"] == kwargs["event_log_descriptor"]["sha256"]
                    else ["post-execution attestation mismatch: event_log_sha256"]
                ),
            )
        with pytest.raises(post_search.PostSearchVerificationError, match=expected_error):
            post_search.build_verified_receipt(
                root,
                bundle,
                boundary,
                event_log,
                changed,
                generated_at=GENERATED,
                now=NOW,
            )


def test_signed_attestation_rejects_wrong_commit_and_swapped_blobs(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    bundle, boundary, event_log, attestation_descriptor = _inputs(root, _bundle())
    attestation = json.loads((root / attestation_descriptor["path"]).read_text())
    authority = json.loads((root / "authority/receipt.json").read_text())
    errors = post_search._signed_attestation_errors(
        root,
        attestation,
        bundle_descriptor=bundle,
        boundary_descriptor=boundary,
        event_log_descriptor=event_log,
        owner_decision_commit=authority["owner_decision_commit"],
    )
    assert "post-execution attestation object is not a commit" in errors
    swapped = deepcopy(attestation)
    swapped["registrar_boundary_receipt"] = event_log
    errors = post_search._signed_attestation_errors(
        root,
        swapped,
        bundle_descriptor=bundle,
        boundary_descriptor=boundary,
        event_log_descriptor=event_log,
        owner_decision_commit=authority["owner_decision_commit"],
    )
    assert "post-execution attestation mismatch: registrar_boundary_receipt" in errors


def test_signed_attestation_rejects_unsigned_commit(
    project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _root(project_root, tmp_path)
    bundle, boundary, event_log, attestation_descriptor = _inputs(root, _bundle())
    attestation = json.loads((root / attestation_descriptor["path"]).read_text())
    authority = json.loads((root / "authority/receipt.json").read_text())

    class Result:
        def __init__(self, returncode: int, stdout: str | bytes = "") -> None:
            self.returncode = returncode
            self.stdout = stdout

    def fake_run(args: list[str], **_kwargs: Any) -> Result:
        if args[1] == "cat-file":
            return Result(0, "commit\n")
        if args[1] == "verify-commit":
            return Result(1, "")
        if args[1] == "show":
            relative = args[2].split(":", 1)[1]
            return Result(0, (root / relative).read_bytes())
        return Result(0, "")

    monkeypatch.setattr(post_search.subprocess, "run", fake_run)
    errors = post_search._signed_attestation_errors(
        root,
        attestation,
        bundle_descriptor=bundle,
        boundary_descriptor=boundary,
        event_log_descriptor=event_log,
        owner_decision_commit=authority["owner_decision_commit"],
    )
    assert "post-execution attestation commit signature is invalid" in errors


def test_stop_receipt_records_unknowns_and_cannot_enable_panel(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    bundle = _bundle()
    del bundle["persisted_target_facts"]
    descriptor = _bundle_file(root, bundle)
    stop = post_search.build_stop_receipt(
        root,
        descriptor,
        errors=["authority failure", "authority failure"],
        generated_at=GENERATED,
        now=NOW,
    )
    assert stop["errors"] == ["authority failure"]
    assert stop["boundary_violation_or_unknown"] is True
    assert stop["panel_inputs_allowed"] is False
    assert post_search.verify_stop_receipt(root, stop, now=NOW) == []
    tampered = deepcopy(stop)
    tampered["panel_inputs_allowed"] = True
    assert post_search.verify_stop_receipt(root, tampered, now=NOW)
    with pytest.raises(post_search.PostSearchVerificationError, match="explicit errors"):
        post_search.build_stop_receipt(
            root,
            descriptor,
            errors=[],
            generated_at=GENERATED,
            now=NOW,
        )


def test_stop_receipt_rejects_unsafe_future_backdated_and_digest_drift(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    descriptor = _bundle_file(root, _bundle())
    for generated_at in (
        "2026-08-15T23:59:59+00:00",
        "2026-08-19T00:00:00+00:00",
    ):
        with pytest.raises(post_search.PostSearchVerificationError, match="timestamp"):
            post_search.build_stop_receipt(
                root,
                descriptor,
                errors=["failure"],
                generated_at=generated_at,
                now=NOW,
            )
    drifted = deepcopy(descriptor)
    drifted["sha256"] = "f" * 64
    with pytest.raises(post_search.PostSearchVerificationError, match="binding"):
        post_search.build_stop_receipt(
            root, drifted, errors=["failure"], generated_at=GENERATED, now=NOW
        )
    unsafe = {"path": "../../bundle.json", "sha256": descriptor["sha256"]}
    with pytest.raises(post_search.PostSearchVerificationError, match="binding"):
        post_search.build_stop_receipt(
            root, unsafe, errors=["failure"], generated_at=GENERATED, now=NOW
        )
