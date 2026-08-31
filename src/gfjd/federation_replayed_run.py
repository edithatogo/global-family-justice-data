"""Declared RunEvent association with exact replay evidence, not observed execution.

Existing replay helpers and this compiler fingerprint implementation files.
No source loader, network access, event executor or publisher is invoked.
"""

import hashlib
import re
from pathlib import Path
from typing import Any

from gfjd import federation_replayed_bundle, federation_run_sequence
from gfjd.federation_metadata import MetadataError, parse_json, require
from gfjd.federation_prov import _canonical


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def assess_replayed_run(
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
    replay_raw: bytes,
    expected_replay_sha256: str,
    replay_bank: dict[str, bytes],
    sequence_raw: bytes,
    expected_sequence_sha256: str,
    binding_raw: bytes,
    expected_binding_sha256: str,
) -> dict[str, Any]:
    """Check a declared metadata association, without inferring actual production."""
    try:
        artifacts = federation_replayed_bundle.prepare_replayed_bundle(
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
            standards,
            replay_raw,
            expected_replay_sha256,
            replay_bank,
        )
        lifecycle = federation_run_sequence.assess_run_sequence(
            sequence_raw, expected_sequence_sha256, standards["openlineage-2-0-2.json"]
        )
        require(type(binding_raw) is bytes and 0 < len(binding_raw) <= 1024 * 1024)
        require(type(expected_binding_sha256) is str)
        require(re.fullmatch(r"[a-f0-9]{64}", expected_binding_sha256) is not None)
        require(_sha(binding_raw) == expected_binding_sha256)
        binding = parse_json(binding_raw)
        require(
            type(binding) is dict
            and set(binding)
            == {
                "contract_version",
                "run_id",
                "job_namespace",
                "job_name",
                "producer",
                "terminal_type",
                "direction",
                "dataset_namespace",
                "dataset_name",
                "object_id",
                "canonical_id",
                "entity_sha256",
            }
        )
        require(binding["contract_version"] == "gfjd-openlineage-replay-association-v1")
        for key in ("run_id", "job_namespace", "job_name", "producer"):
            require(binding[key] == lifecycle[key])
        require(binding["terminal_type"] == lifecycle["declared_terminal_type"])
        require(binding["direction"] in ("input", "output"))
        manifest = parse_json(artifacts["bundle-manifest.json"])
        selected = manifest["replay_binding"]
        for key in ("object_id", "canonical_id", "entity_sha256"):
            require(binding[key] == selected[key])
        matches = [
            item
            for item in lifecycle["datasets"]
            if item["direction"] == binding["direction"]
            and item["namespace"] == binding["dataset_namespace"]
            and item["name"] == binding["dataset_name"]
        ]
        require(len(matches) == 1)
        authority = dict(manifest["authority"])
        require(not any(authority.values()) and not any(lifecycle["authority"].values()))
        return {
            "contract_version": "gfjd-openlineage-replay-association-report-v1",
            "association_kind": "declared_metadata_only",
            "sequence_profile_validated": True,
            "declared_terminal_type": lifecycle["declared_terminal_type"],
            "sequence_sha256": expected_sequence_sha256,
            "binding_sha256": expected_binding_sha256,
            "scope_sha256": expected_scope_sha256,
            "replay_sha256": expected_replay_sha256,
            "replay_bank_sha256": sorted(replay_bank),
            "replayed_bundle_sha256": _sha(artifacts["bundle-manifest.json"]),
            "replayed_artifact_sha256": {k: _sha(v) for k, v in sorted(artifacts.items())},
            "lifecycle_report": lifecycle,
            "selected_replay_binding": selected,
            "dataset_association": matches[0],
            "unbound_datasets": [item for item in lifecycle["datasets"] if item != matches[0]],
            "unbound_object_ids": manifest["provenance_pending_object_ids"],
            "implementation_sha256": _sha(Path(__file__).read_bytes()),
            "component_implementation_sha256": {
                module.__name__: _sha(Path(str(module.__file__)).read_bytes())
                for module in (federation_replayed_bundle, federation_run_sequence)
            },
            "execution_observed": False,
            "production_verified": False,
            "factual_evidence": "unverified",
            "semantic_equivalence": "unverified",
            "ownership": "unverified",
            "full_conformance": "unverified",
            "filesystem_access": "component-helper-and-compiler-fingerprints-only",
            "authority": authority,
        }
    except Exception:
        raise MetadataError("Run replay association contract violation") from None


def verify_replayed_run(
    scope_raw: bytes,
    expected_scope_sha256: str,
    metadata_bank: dict[str, bytes],
    estate_inputs: dict[str, bytes],
    standards: dict[str, bytes],
    replay_raw: bytes,
    expected_replay_sha256: str,
    replay_bank: dict[str, bytes],
    sequence_raw: bytes,
    expected_sequence_sha256: str,
    binding_raw: bytes,
    expected_binding_sha256: str,
    report: dict[str, Any],
) -> None:
    """Regenerate full lifecycle and replay associations, rejecting rehashed assertions."""
    try:
        expected = assess_replayed_run(
            scope_raw,
            expected_scope_sha256,
            metadata_bank,
            estate_inputs,
            standards,
            replay_raw,
            expected_replay_sha256,
            replay_bank,
            sequence_raw,
            expected_sequence_sha256,
            binding_raw,
            expected_binding_sha256,
        )
        require(type(report) is dict and report == expected)
        require(_canonical(report) == _canonical(expected))
    except Exception:
        raise MetadataError("Run replay association contract violation") from None
