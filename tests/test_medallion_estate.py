"""Offline fictional-namespace estate fixtures; no provider facts or source data."""

import hashlib
import json
from pathlib import Path

import pytest

from gfjd.medallion_estate import (
    POLICY_REFERENCE,
    SOURCEFILES,
    EstateError,
    prepare_estate,
    verify_estate,
)


@pytest.fixture
def configs() -> dict[str, bytes]:
    root = Path(__file__).resolve().parents[1]
    inputs = {
        name: (root / name).read_bytes().replace(b"edithatogo", b"fictional-estate")
        for name in SOURCEFILES
    }
    inputs[POLICY_REFERENCE] = (root / POLICY_REFERENCE).read_bytes()
    return inputs


def test_missing_policy_cannot_assert_approved_direction(configs: dict[str, bytes]) -> None:
    configs.pop(POLICY_REFERENCE)
    with pytest.raises(EstateError):
        prepare_estate(configs)


@pytest.mark.parametrize("policy", [b"altered policy", b"", b"x" * (1024 * 1024 + 1)])
def test_policy_binding_precedes_toml_parse(
    configs: dict[str, bytes], policy: bytes, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden_parse(raw: bytes) -> None:
        raise AssertionError("TOML parsed before policy binding")

    monkeypatch.setattr("gfjd.medallion_estate._parse", forbidden_parse)
    configs[POLICY_REFERENCE] = policy
    with pytest.raises(EstateError):
        prepare_estate(configs)


def test_existing_artifacts_cannot_bypass_changed_policy(configs: dict[str, bytes]) -> None:
    artifacts = prepare_estate(configs)
    configs[POLICY_REFERENCE] += b"\nChanged direction.\n"
    with pytest.raises(EstateError):
        verify_estate(configs, artifacts)


def test_exact_six_role_deterministic_drafts(configs: dict[str, bytes]) -> None:
    artifacts = prepare_estate(configs)
    assert artifacts == prepare_estate(dict(reversed(list(configs.items()))))
    assert len(artifacts) == 8
    verify_estate(configs, artifacts)
    manifest = json.loads(artifacts["estate-manifest.json"])
    assert manifest["contract_version"] == "gfjd-offline-estate-v2"
    assert len(manifest["roles"]) == 6
    assert manifest["namespace"] == "fictional-estate"
    assert manifest["github_minimum_publish_gate"] == "G6"
    assert len(manifest["artifact_sha256"]) == 7
    assert "estate-manifest.json" not in manifest["artifact_sha256"]
    for name, digest in manifest["artifact_sha256"].items():
        assert hashlib.sha256(artifacts[name]).hexdigest() == digest
    assert all(value is False for value in manifest["authority"].values())
    benchmark = next(item for item in manifest["roles"] if item["id"] == "extraction-benchmark")
    assert benchmark["classification"] == "experimental"
    assert benchmark["authority"] == "github"
    assert all(item["desired_link"]["requested"] is False for item in manifest["roles"])
    assert all(item["factual_states"]["availability"] == "unverified" for item in manifest["roles"])
    assert (
        "unresolved_rights_flag_does_not_override_exact_edition_policy" in manifest["diagnostics"]
    )


@pytest.mark.parametrize(
    "name,before,after",
    [
        ("config/bootstrap.toml", b"private_by_default = false", b"private_by_default = true"),
        ("config/bootstrap.toml", b'namespace = ""', b'namespace = "conflicting-namespace"'),
        ("config/bootstrap.toml", b'name = "gfjd-source-archive"', b'name = "../unsafe"'),
        ("config/bootstrap.toml", b'repo_type = "space"', b'repo_type = "dataset"'),
        ("config/bootstrap.toml", b'visibility = "public"', b'visibility = "private"'),
        (
            "config/archive_targets.toml",
            b'minimum_publish_gate = "G6"',
            b'minimum_publish_gate = "G3"',
        ),
        (
            "config/archive_targets.toml",
            b"require_edition_bound_rights = true",
            b"require_edition_bound_rights = false",
        ),
        ("portfolio/products.toml", b'class = "experimental"', b'class = "generated_distribution"'),
        (
            "portfolio/products.toml",
            b'publication_mode = "generated_only"',
            b'publication_mode = "manual"',
        ),
        (
            ".gfjd/product.toml",
            b'public_data_boundary = "aggregate_only"',
            b'public_data_boundary = "unrestricted"',
        ),
    ],
)
def test_conflicting_declarations(
    configs: dict[str, bytes], name: str, before: bytes, after: bytes
) -> None:
    assert before in configs[name]
    configs[name] = configs[name].replace(before, after)
    with pytest.raises(EstateError):
        prepare_estate(configs)


def test_omitted_and_extra_config_files(configs: dict[str, bytes]) -> None:
    extra = {**configs, "../other.toml": b""}
    with pytest.raises(EstateError):
        prepare_estate(extra)
    configs.pop(SOURCEFILES[0])
    with pytest.raises(EstateError):
        prepare_estate(configs)


@pytest.mark.parametrize("kind", ["missing", "extra", "modified", "unsafe"])
def test_exact_artifact_set_and_bytes(configs: dict[str, bytes], kind: str) -> None:
    artifacts = prepare_estate(configs)
    if kind == "missing":
        artifacts.pop("explorer/index.html")
    elif kind == "extra":
        artifacts["extra.txt"] = b"fictional"
    elif kind == "unsafe":
        artifacts["../escape"] = b"fictional"
    else:
        artifacts["explorer/index.html"] += b"<script>fetch('fictional')</script>"
    with pytest.raises(EstateError):
        verify_estate(configs, artifacts)


@pytest.mark.parametrize(
    "suffix", [b'\nlicence = "fabricated"\n', b'\navailability = "public_live"\n']
)
def test_unknown_factual_fields_rejected(configs: dict[str, bytes], suffix: bytes) -> None:
    configs[".gfjd/product.toml"] += suffix
    with pytest.raises(EstateError):
        prepare_estate(configs)


def test_role_addition_and_duplicate_rejected(configs: dict[str, bytes]) -> None:
    extra = (
        b'\n[[huggingface.repositories]]\nid="extra"\nname="extra"\nrepo_type="dataset"\n'
        b'visibility="public"\npublication_mode="public_catalogue"\n'
    )
    for fragment in (extra, extra.replace(b'id="extra"', b'id="source-archive"')):
        changed = {**configs, "config/bootstrap.toml": configs["config/bootstrap.toml"] + fragment}
        with pytest.raises(EstateError):
            prepare_estate(changed)


def test_bounded_toml(configs: dict[str, bytes]) -> None:
    for raw in (
        b"x" * (1024 * 1024 + 1),
        b"not valid toml",
        b"v=nan",
        b"v=" + b"[" * 40 + b"0" + b"]" * 40,
    ):
        with pytest.raises(EstateError):
            prepare_estate({**configs, ".gfjd/product.toml": raw})


def test_no_active_explorer_or_transport(
    configs: dict[str, bytes], monkeypatch: pytest.MonkeyPatch
) -> None:
    def prohibited(*args: object, **kwargs: object) -> None:
        raise AssertionError("offline compiler attempted external execution")

    monkeypatch.setattr("subprocess.run", prohibited)
    monkeypatch.setattr("socket.create_connection", prohibited)
    monkeypatch.setattr("urllib.request.urlopen", prohibited)
    artifacts = prepare_estate(configs)
    page = artifacts["explorer/index.html"].decode()
    assert "<script" not in page and "<iframe" not in page
    assert "fetch(" not in page and "data-src" not in page
    assert "Draft" in page


def test_policy_layers_and_exact_input_hashes(configs: dict[str, bytes]) -> None:
    manifest = json.loads(prepare_estate(configs)["estate-manifest.json"])
    layers = {item["id"]: item["layer_constraints"] for item in manifest["roles"]}
    assert layers["source-archive"] == ["b0"]
    assert layers["observations"] == ["b1", "silver", "gold"]
    assert layers["explorer"] == ["accepted_gold", "released_platinum"]
    assert layers["source-catalogue"] == ["cross_layer_metadata"]
    assert manifest["role_policy"]["sha256"] == (
        "5f44f2a64e49c3ac616f5dd456061d9c00bdbdfc09e218bab6fab36852109465"
    )
    assert manifest["input_sha256"] == {
        name: hashlib.sha256(raw).hexdigest() for name, raw in configs.items()
    }


@pytest.mark.parametrize(
    "before,after",
    [
        (b"max_command_output_bytes = 20000", b"max_command_output_bytes = true"),
        (b"fetch_prune = true", b'fetch_prune = "true"'),
        (b"include_hidden = false", b"include_hidden = 0"),
        (b'homepage = ""', b"homepage = []"),
    ],
)
def test_bound_types_even_for_non_emitted_config(
    configs: dict[str, bytes], before: bytes, after: bytes
) -> None:
    configs["config/bootstrap.toml"] = configs["config/bootstrap.toml"].replace(before, after)
    with pytest.raises(EstateError):
        prepare_estate(configs)


def test_missing_role_and_explicit_matching_namespace(configs: dict[str, bytes]) -> None:
    bootstrap = configs["config/bootstrap.toml"]
    configs["config/bootstrap.toml"] = bootstrap.replace(
        b'namespace = ""', b'namespace = "fictional-estate"'
    )
    assert len(prepare_estate(configs)) == 8
    start = bootstrap.index(b"[[huggingface.repositories]]")
    end = bootstrap.index(b"[[huggingface.repositories]]", start + 1)
    configs["config/bootstrap.toml"] = bootstrap[:start] + bootstrap[end:]
    with pytest.raises(EstateError):
        prepare_estate(configs)


def test_rehashing_manifest_does_not_bypass_exact_recomputation(configs: dict[str, bytes]) -> None:
    artifacts = prepare_estate(configs)
    manifest = json.loads(artifacts["estate-manifest.json"])
    manifest["roles"][0]["factual_states"]["availability"] = "verified"
    artifacts["estate-manifest.json"] = json.dumps(manifest).encode()
    with pytest.raises(EstateError):
        verify_estate(configs, artifacts)
