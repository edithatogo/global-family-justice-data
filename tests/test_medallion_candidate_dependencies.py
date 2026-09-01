"""Fictional dependency declarations; no package installation or registry access."""

import hashlib
import json
import socket
import traceback
from datetime import UTC, datetime
from pathlib import Path

import pytest

from gfjd import medallion_candidate_dependencies as module
from gfjd.medallion_candidate_dependencies import (
    assess_dependency_evidence,
    verify_dependency_evidence,
)
from gfjd.supply_chain import LockedPackage, LockInventory, build_spdx_document

TIME = "2026-09-01T00:00:00Z"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def lock_text(extra="", dep="demo", source='registry = "https://pypi.org/simple"', version="1.0"):
    payload = b"FICTIONAL_WHEEL"
    wheel = (
        '{ url = "https://files.pythonhosted.org/fictional.whl", '
        f'hash = "sha256:{sha(payload)}", size = {len(payload)} }}'
    )
    return f'''version = 1
[[package]]
name = "fictional"
version = "0.1"
source = {{ editable = "." }}
dependencies = [{{ name = "{dep}" }}]
[[package]]
name = "demo"
version = "{version}"
source = {{ {source} }}
wheels = [{wheel}]
{extra}
'''.encode()


@pytest.fixture
def case():
    lock = lock_text()
    inventory = LockInventory(
        Path("NEVER_OPEN"),
        sha(lock),
        1,
        "fictional",
        "0.1",
        ("demo",),
        (),
        (LockedPackage("demo", "1.0", (), "https://pypi.org/simple"),),
    )
    sbom = encoded(
        build_spdx_document(
            inventory,
            release_version="0.1",
            created_at=datetime(2026, 9, 1, tzinfo=UTC),
            scope="build",
            namespace_base="https://global-family-justice-data.example/spdx",
            project_uri="https://github.com/edithatogo/global-family-justice-data",
        )
    )
    package = b"FICTIONAL_WHEEL"
    bindings = encoded(
        {
            "contract_version": "gfjd-candidate-package-bindings-v1",
            "candidate_id": "FICTIONAL",
            "lock_sha256": sha(lock),
            "sbom_sha256": sha(sbom),
            "packages": [
                {
                    "object_id": "wheel",
                    "name": "demo",
                    "version": "1.0",
                    "distribution_sha256": sha(package),
                }
            ],
        }
    )
    bank = {sha(raw): raw for raw in (lock, sbom, bindings, package)}
    objects = [
        {"object_id": name, "role": role, "sha256": sha(raw)}
        for name, role, raw in (
            ("lock", "dependency", lock),
            ("sbom", "manifest", sbom),
            ("bindings", "metadata", bindings),
            ("wheel", "package", package),
        )
    ]
    return [lock, sbom, bindings], dict(
        project_name="fictional",
        candidate_id="FICTIONAL",
        as_of=TIME,
        candidate_bank=bank,
        scope_objects=objects,
    )


def test_missing_candidate_metadata_red():
    with pytest.raises(ValueError):
        assess_dependency_evidence(
            b"version=1",
            b"{}",
            b"{}",
            project_name="fictional",
            candidate_id="FICTIONAL",
            as_of="2026-09-01T00:00:00Z",
            candidate_bank={},
            scope_objects=[],
        )


def test_full_graph_and_exact_package(case):
    args, kwargs = case
    report = assess_dependency_evidence(*args, **kwargs)
    assert report["status"] == "internal_consistency_verified"
    assert report["package_count"] == 2 and report["relationship_count"] == 2
    assert report["missing_distribution_sha256"] == []
    assert report["unbound_package_object_ids"] == []
    assert report["validated_package_bindings"] == [
        {
            "object_id": "wheel",
            "name": "demo",
            "version": "1.0",
            "distribution_sha256": sha(b"FICTIONAL_WHEEL"),
            "size_bytes": len(b"FICTIONAL_WHEEL"),
        }
    ]
    assert not any(report["authority"].values())
    assert set(report["factual_requirements"].values()) == {"unverified"}
    verify_dependency_evidence(*args, report, **kwargs)


def replace_input(case, index, raw):
    args, kwargs = case
    old = args[index]
    kwargs["candidate_bank"].pop(sha(old))
    kwargs["candidate_bank"][sha(raw)] = raw
    for obj in kwargs["scope_objects"]:
        if obj["sha256"] == sha(old):
            obj["sha256"] = sha(raw)
    args[index] = raw


def test_missing_distribution_unbound_package(case):
    args, kwargs = case
    bindings = json.loads(args[2])
    bindings["packages"] = []
    replace_input(case, 2, encoded(bindings))
    kwargs["candidate_bank"].pop(sha(b"FICTIONAL_WHEEL"))
    arbitrary = b"NON_PYTHON_PACKAGE"
    kwargs["candidate_bank"][sha(arbitrary)] = arbitrary
    kwargs["scope_objects"][-1]["sha256"] = sha(arbitrary)
    report = assess_dependency_evidence(*args, **kwargs)
    assert report["unbound_package_object_ids"] == ["wheel"]
    assert report["missing_distribution_sha256"] == [sha(b"FICTIONAL_WHEEL")]


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "unrelated"),
        ("version", "2.0"),
        ("distribution_sha256", "a" * 64),
        ("object_id", "lock"),
        ("extra", "x"),
    ],
)
def test_wrong_package_binding(case, field, value):
    args, kwargs = case
    binding = json.loads(args[2])
    binding["packages"][0][field] = value
    replace_input(case, 2, encoded(binding))
    with pytest.raises(ValueError):
        assess_dependency_evidence(*args, **kwargs)


def test_whole_spdx_not_field_presence(case):
    args, kwargs = case
    sbom = json.loads(args[1])
    sbom["relationships"] = []
    replace_input(case, 1, encoded(sbom))
    binding = json.loads(args[2])
    binding["sbom_sha256"] = sha(args[1])
    replace_input(case, 2, encoded(binding))
    with pytest.raises(ValueError):
        assess_dependency_evidence(*args, **kwargs)


@pytest.mark.parametrize(
    "raw",
    [
        lock_text(dep="unresolved"),
        lock_text(extra='dependencies = [{name="fictional"}]'),
        lock_text(source='git = "https://example.invalid/repo"'),
        lock_text(extra="timestamp = 2026-09-01T00:00:00Z"),
        lock_text(extra="x = nan"),
        lock_text(extra='x = "\\u0000"'),
        lock_text(extra="wheels = []"),
        lock_text(extra='dependencies = ["demo"]'),
        lock_text(extra="optional-dependencies = []"),
        lock_text(extra='dev-dependencies = {test=[{name="missing"}]}'),
        lock_text().replace(b"version = 1\n", b"version = true\n", 1),
        lock_text().replace(b"size = 15", b"size = true"),
    ],
)
def test_lock_contract_rejects(raw):
    with pytest.raises(ValueError):
        module._lock(raw, "fictional")


def test_all_nonroot_groups_resolved_and_preserved():
    raw = lock_text(
        extra='optional-dependencies = {test=[{name="demo"}]}\n'
        'dev-dependencies = {dev=[{name="demo"}]}'
    )
    inventory, _, _, edges = module._lock(raw, "fictional")
    assert inventory.packages[0].dependencies == ("demo",)
    assert edges == 3


def test_colliding_spdx_ids():
    raw = (
        lock_text(version="1+0")
        + b"""\n[[package]]
name="demo"
version="1-0"
source={registry="https://pypi.org/simple"}
"""
    )
    with pytest.raises(ValueError):
        module._lock(raw, "fictional")


def test_duplicate_normalized_identity():
    raw = (
        lock_text()
        + b"""\n[[package]]
name="Demo"
version="1.0"
source={registry="https://pypi.org/simple"}
"""
    )
    with pytest.raises(ValueError):
        module._lock(raw, "fictional")


def test_graph_bound_before_builder():
    # 80 locked versions each depend on all80 versions through the same name.
    raw = b'version=1\n[[package]]\nname="fictional"\nversion="1"\nsource={editable="."}\n'
    for i in range(80):
        raw += f'[[package]]\nname="demo"\nversion="{i}"\nsource={{registry="https://pypi.org/simple"}}\ndependencies=[{{name="demo"}}]\n'.encode()
    with pytest.raises(ValueError):
        module._lock(raw, "fictional")


def test_missing_root_and_distribution_size_conflict():
    raw = lock_text().replace(b'name = "fictional"', b'name = "other"')
    with pytest.raises(ValueError):
        module._lock(raw, "fictional")
    raw = lock_text(
        extra='sdist = { url="https://files.pythonhosted.org/other", '
        f'hash="sha256:{sha(b"FICTIONAL_WHEEL")}",size=999 }}'
    )
    with pytest.raises(ValueError):
        module._lock(raw, "fictional")


@pytest.mark.parametrize(
    "url",
    [
        "http://files.pythonhosted.org/a",
        "https://files.pythonhosted.org:443/a",
        "https://files.pythonhosted.org/a?q=1",
        "https://other.invalid/a",
    ],
)
def test_distribution_url(url):
    raw = lock_text().replace(b"https://files.pythonhosted.org/fictional.whl", url.encode())
    with pytest.raises(ValueError):
        module._lock(raw, "fictional")


@pytest.mark.parametrize(
    "field,value",
    [("candidate_id", "OTHER"), ("as_of", "2026-09-02T00:00:00Z"), ("project_name", "other")],
)
def test_wrong_scope(case, field, value):
    args, kwargs = case
    kwargs[field] = value
    with pytest.raises(ValueError):
        assess_dependency_evidence(*args, **kwargs)


def test_missing_candidate_input(case):
    args, kwargs = case
    digest = sha(args[0])
    kwargs["candidate_bank"].pop(digest)
    kwargs["scope_objects"] = [obj for obj in kwargs["scope_objects"] if obj["sha256"] != digest]
    with pytest.raises(ValueError):
        assess_dependency_evidence(*args, **kwargs)


def test_secrets_never_returned(case):
    args, kwargs = case
    token = "ghp_" + "a" * 35
    raw = lock_text(extra='extra="' + "".join(f"\\u{ord(c):04x}" for c in token) + '"')
    replace_input(case, 0, raw)
    try:
        assess_dependency_evidence(*args, **kwargs)
    except ValueError:
        assert token not in traceback.format_exc()
    else:
        pytest.fail("escaped secret accepted")


def test_budgets_before_hash(case, monkeypatch):
    args, kwargs = case
    kwargs["candidate_bank"] = {f"{i:064x}": b"x" * (8 * module.MIB) for i in range(4)}

    def forbidden(*args, **kwargs):
        pytest.fail("hash before budget")

    monkeypatch.setattr(module, "_sha", forbidden)
    with pytest.raises(ValueError):
        assess_dependency_evidence(*args, **kwargs)


@pytest.mark.parametrize(
    "field,value",
    [
        ("package_count", True),
        ("status", "accepted"),
        ("implementation_sha256", "a" * 64),
        ("missing_distribution_sha256", ["a" * 64]),
    ],
)
def test_forged_report(case, field, value):
    args, kwargs = case
    report = assess_dependency_evidence(*args, **kwargs)
    report[field] = value
    with pytest.raises(ValueError):
        verify_dependency_evidence(*args, report, **kwargs)


def test_no_loader_or_network(case, monkeypatch):
    args, kwargs = case

    def forbidden(*args, **kwargs):
        pytest.fail("forbidden dependency capability")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(module.supply_chain, "load_lock_inventory", forbidden)
    assert assess_dependency_evidence(*args, **kwargs) == assess_dependency_evidence(
        *args, **kwargs
    )
