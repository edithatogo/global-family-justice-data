"""Fictional composition fixtures; no accepted Gold or public release evidence."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from gfjd import medallion_release_checks
from gfjd.medallion_release_checks import assess_release, verify_release_composition


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fixture() -> tuple[dict, dict, dict[str, bytes], dict]:
    artifacts = {sha(b"fictional one"): b"fictional one", sha(b"fictional two"): b"fictional two"}
    scope = {
        "contract_version": "gfjd-platinum-scope-v1",
        "release_id": "FICTIONAL-RELEASE",
        "object_ids": ["FICTIONAL-1", "FICTIONAL-2"],
    }
    objects = [
        {
            "object_id": identity,
            "layer": "gold",
            "sha256": digest,
            "size_bytes": len(raw),
            "media_type": "text/plain",
        }
        for identity, (digest, raw) in zip(scope["object_ids"], artifacts.items(), strict=True)
    ]
    federation = {
        "contract_version": "gfjd-federation-composition-v1",
        "release_id": scope["release_id"],
        "objects": [
            {
                "object_id": item["object_id"],
                "content_sha256": item["sha256"],
                "canonical_object_id": item["object_id"],
            }
            for item in objects
        ],
    }
    manifest = {
        "contract_version": "gfjd-platinum-composition-v1",
        "release_id": scope["release_id"],
        "scope_sha256": sha(encoded(scope)),
        "federation_sha256": sha(encoded(federation)),
        "objects": objects,
    }
    return manifest, federation, artifacts, scope


def assess(manifest: dict, federation: dict, artifacts: dict[str, bytes], scope: dict) -> dict:
    return assess_release(encoded(manifest), encoded(federation), artifacts, encoded(scope))


def test_exact_composition_and_pending_authority() -> None:
    args = fixture()
    result = assess(*args)
    assert result["status"] == "composition_verified"
    assert result["object_count"] == 2
    assert all(value == "pending" for value in result["factual_requirements"].values())
    assert all(value is False for value in result["authority"].values())
    assert result == assess(args[0], args[1], dict(reversed(list(args[2].items()))), args[3])
    verify_release_composition(
        encoded(args[0]), encoded(args[1]), args[2], encoded(args[3]), result
    )


def test_reordered_declarations_preserve_sorted_checks_not_raw_digests() -> None:
    manifest, federation, bank, scope = fixture()
    first = assess(manifest, federation, bank, scope)
    manifest["objects"].reverse()
    federation["objects"].reverse()
    manifest["federation_sha256"] = sha(encoded(federation))
    second = assess(manifest, federation, bank, scope)
    assert first["members"] == second["members"]
    assert first["manifest_sha256"] != second["manifest_sha256"]


@pytest.mark.parametrize(
    "change",
    [
        "duplicate_manifest",
        "duplicate_federation",
        "duplicate_scope",
        "duplicate_canonical",
        "missing",
        "extra",
        "layer",
        "size_bool",
        "size_wrong",
        "digest",
        "release",
        "scope",
        "unknown",
    ],
)
def test_invalid_composition(change: str) -> None:
    manifest, federation, bank, scope = fixture()
    if change == "duplicate_manifest":
        manifest["objects"].append(manifest["objects"][0])
    elif change == "duplicate_federation":
        federation["objects"].append(federation["objects"][0])
    elif change == "duplicate_scope":
        scope["object_ids"].append(scope["object_ids"][0])
    elif change == "duplicate_canonical":
        federation["objects"][1]["canonical_object_id"] = federation["objects"][0][
            "canonical_object_id"
        ]
    elif change == "missing":
        bank.pop(next(iter(bank)))
    elif change == "extra":
        bank[sha(b"extra fictional")] = b"extra fictional"
    elif change == "layer":
        manifest["objects"][0]["layer"] = "silver"
    elif change == "size_bool":
        manifest["objects"][0]["size_bytes"] = True
    elif change == "size_wrong":
        manifest["objects"][0]["size_bytes"] = 0
    elif change == "digest":
        bank[next(iter(bank))] = b"changed"
    elif change == "release":
        federation["release_id"] = "OTHER"
    elif change == "scope":
        scope["object_ids"].pop()
    else:
        manifest["objects"][0]["untrusted_field"] = "untrusted_value"
    manifest["federation_sha256"] = sha(encoded(federation))
    manifest["scope_sha256"] = sha(encoded(scope))
    with pytest.raises(ValueError, match="^release composition validation failed$"):
        assess(manifest, federation, bank, scope)


@pytest.mark.parametrize(
    "raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e999}', b"\xff", b"x" * (1024 * 1024 + 1)]
)
def test_strict_json_and_byte_bound(raw: bytes) -> None:
    manifest, federation, bank, scope = fixture()
    with pytest.raises(ValueError):
        assess_release(raw, encoded(federation), bank, encoded(scope))


def test_rehashed_forged_report_fails() -> None:
    manifest, federation, bank, scope = fixture()
    result = copy.deepcopy(assess(manifest, federation, bank, scope))
    result["authority"]["publication"] = True
    result.pop("report_sha256")
    result["report_sha256"] = sha(encoded(result))
    with pytest.raises(ValueError):
        verify_release_composition(
            encoded(manifest), encoded(federation), bank, encoded(scope), result
        )


def test_bank_budget_and_object_limit() -> None:
    manifest, federation, bank, scope = fixture()
    bank = {sha(b"x" * (8 * 1024 * 1024 + 1)): b"x" * (8 * 1024 * 1024 + 1)}
    with pytest.raises(ValueError):
        assess(manifest, federation, bank, scope)
    manifest["objects"] *= 51
    with pytest.raises(ValueError):
        assess(manifest, federation, {}, scope)


@pytest.mark.parametrize("field", ["scope_sha256", "federation_sha256"])
def test_exact_input_bindings_not_just_semantic_equivalence(field: str) -> None:
    manifest, federation, bank, scope = fixture()
    manifest[field] = "0" * 64
    with pytest.raises(ValueError):
        assess(manifest, federation, bank, scope)


def test_federation_content_substitution_rejected_after_rebinding() -> None:
    manifest, federation, bank, scope = fixture()
    federation["objects"][0]["content_sha256"] = federation["objects"][1]["content_sha256"]
    manifest["federation_sha256"] = sha(encoded(federation))
    with pytest.raises(ValueError):
        assess(manifest, federation, bank, scope)


@pytest.mark.parametrize("which", ["federation", "scope"])
def test_other_json_inputs_reject_duplicate_keys(which: str) -> None:
    manifest, federation, bank, scope = fixture()
    raw = b'{"release_id":"fictional","release_id":"other"}'
    with pytest.raises(ValueError):
        assess_release(
            encoded(manifest),
            raw if which == "federation" else encoded(federation),
            bank,
            raw if which == "scope" else encoded(scope),
        )


def test_same_content_can_have_distinct_declared_objects_without_fake_byte_counts() -> None:
    manifest, federation, bank, scope = fixture()
    first = manifest["objects"][0]
    manifest["objects"][1].update(sha256=first["sha256"], size_bytes=first["size_bytes"])
    federation["objects"][1]["content_sha256"] = first["sha256"]
    manifest["federation_sha256"] = sha(encoded(federation))
    bank = {first["sha256"]: bank[first["sha256"]]}
    result = assess(manifest, federation, bank, scope)
    assert result["object_count"] == 2
    assert result["artifact_count"] == 1
    assert result["artifact_bytes"] == first["size_bytes"]


def test_empty_cohort_cannot_claim_verified_composition() -> None:
    manifest, federation, _, scope = fixture()
    scope["object_ids"] = []
    federation["objects"] = []
    manifest["objects"] = []
    manifest["scope_sha256"] = sha(encoded(scope))
    manifest["federation_sha256"] = sha(encoded(federation))
    with pytest.raises(ValueError, match="^release composition validation failed$"):
        assess(manifest, federation, {}, scope)


def test_implementation_digest_is_recomputed() -> None:
    manifest, federation, bank, scope = fixture()
    report = assess(manifest, federation, bank, scope)
    assert report["implementation_sha256"] == sha(
        Path(medallion_release_checks.__file__).read_bytes()
    )
    report["implementation_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        verify_release_composition(
            encoded(manifest), encoded(federation), bank, encoded(scope), report
        )
