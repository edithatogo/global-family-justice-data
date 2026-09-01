"""Fictional full-denominator candidate assurance; no public release."""

import copy
import io
import zipfile

import pytest
from blake3 import blake3

from gfjd import medallion_candidate_assurance as assurance
from gfjd.medallion_candidate_inputs import bundle_fingerprint
from tests.test_medallion_candidate_dependencies import case as dependency_case
from tests.test_medallion_candidate_inputs import encoded, fixture, sha

# Imported fixture is used by the combined all-role rehearsal.
assert dependency_case


def assess(data):
    plan, scope, bank, bundles = data
    plan["scope_sha256"] = sha(encoded(scope))
    raw = encoded(plan)
    return assurance.assess_candidate_assurance(raw, sha(raw), encoded(scope), bank, bundles)


def test_missing_evidence_never_becomes_release_clearance():
    report = assess(fixture())
    assert report["release_status"] == "blocked"
    assert report["mechanical_coverage_complete"] is False
    assert not any(report["authority"].values())
    assert report["objects"][0]["dimensions"]["provenance"] == "missing_evidence"


def test_rehashed_forgery_rejected():
    data = fixture()
    report = copy.deepcopy(assess(data))
    report["release_status"] = "authorized"
    report["report_sha256"] = sha(
        encoded({k: v for k, v in report.items() if k != "report_sha256"})
    )
    plan, scope, bank, bundles = data
    with pytest.raises(ValueError):
        assurance.verify_candidate_assurance(
            encoded(plan), sha(encoded(plan)), encoded(scope), bank, bundles, report
        )


def add(data, identity, raw, role="metadata", media="application/json"):
    _, scope, bank, _ = data
    obj = copy.deepcopy(scope["objects"][0])
    obj.update(
        object_id=identity,
        sha256=sha(raw),
        blake3=blake3(raw).hexdigest(),
        size_bytes=len(raw),
        role=role,
        media_type=media,
        edges=[],
    )
    scope["objects"].append(obj)
    bank[sha(raw)] = raw
    return obj


def archive(members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as zipped:
        for name, raw in members:
            zipped.writestr(name, raw)
    return stream.getvalue()


def test_every_role_and_inactive_object_retained():
    data = fixture()
    for role in ("data", "transformation", "package", "manifest", "dependency", "locator_record"):
        obj = add(data, role, encoded({"fictional": role}), role)
        obj["lifecycle"] = "quarantined"
    report = assess(data)
    assert len(report["objects"]) == 7
    assert set(report["inventory"]["category_counts"]) == {
        "data",
        "metadata",
        "transformation",
        "package",
        "manifest",
        "dependency",
        "locator_record",
    }
    for dimension in assurance.DIMENSIONS:
        assert sum(report["coverage"][dimension].values()) == 7
    assert not report["mechanical_coverage_complete"]


def test_auxiliary_secret_cannot_hide_behind_role():
    data = fixture()
    token = "ghp_" + "a" * 36
    add(data, "aux", encoded({"fictional": token}), "locator_record")
    report = assess(data)
    row = next(row for row in report["objects"] if row["object_id"] == "aux")
    assert row["dimensions"]["secrets"] == "failed"
    assert any(f["severity"] == "critical" for f in row["findings"])
    assert token not in encoded(report).decode()


@pytest.mark.parametrize("copies", [1, 2, 3])
def test_package_composition_requires_exact_multiset(copies):
    data = fixture()
    member = b'{"fictional":true}'
    package = archive([("a.json", member), ("b.json", member)])
    obj = add(data, "package", package, "package", "application/zip")
    for index in range(copies):
        target = add(data, f"member{index}", member)
        obj["edges"].append({"relation": "package_member", "target_object_id": target["object_id"]})
    row = next(r for r in assess(data)["objects"] if r["object_id"] == "package")
    assert row["package_composition"]["status"] == (
        "checked_no_findings" if copies == 2 else "failed"
    )


def test_shared_content_scanned_once_but_every_object_reported(monkeypatch):
    data = fixture()
    add(data, "duplicate", next(iter(data[2].values())), media="text/plain")
    calls = []
    original = assurance.medallion_candidate_scan.scan_candidate_bytes

    def scan(*args):
        calls.append(args)
        return original(*args)

    monkeypatch.setattr(assurance.medallion_candidate_scan, "scan_candidate_bytes", scan)
    report = assess(data)
    assert len(calls) == 1 and len(report["objects"]) == 2


def test_budget_binding_failure_precedes_any_scan(monkeypatch):
    data = fixture()
    data[2]["0" * 64] = b"unbound"

    def forbidden(*args):
        pytest.fail("scanner called before complete input validation")

    monkeypatch.setattr(assurance.medallion_candidate_scan, "scan_candidate_bytes", forbidden)
    with pytest.raises(ValueError):
        assess(data)


def test_dependency_graph_is_not_package_authenticity(dependency_case):
    args, kwargs = dependency_case
    data = fixture()
    for obj in kwargs["scope_objects"]:
        add(
            data,
            obj["object_id"],
            kwargs["candidate_bank"][obj["sha256"]],
            obj["role"],
            "text/plain" if obj["object_id"] in {"lock", "wheel"} else "application/json",
        )
    bundle = dict(zip(("lock_raw", "sbom_raw", "package_bindings_raw"), args, strict=True))
    bundle["project_name"] = kwargs["project_name"]
    data[3]["dependencies"] = bundle
    data[0]["evidence_bindings"]["dependencies"] = bundle_fingerprint(bundle)
    report = assess(data)
    rows = {row["object_id"]: row for row in report["objects"]}
    assert rows["wheel"]["dimensions"]["dependencies"] == "checked_no_findings"
    assert rows["wheel"]["dimensions"]["supply_chain"] == "unsupported"
    assert rows["FICTIONAL"]["dimensions"]["dependencies"] == "unsupported"
    assert set(report["factual_requirements"].values()) == {"unverified"}
    assert report["release_status"] == "blocked"


def test_locator_declarations_remain_unrequested(monkeypatch):
    import socket

    def forbidden(*args, **kwargs):
        pytest.fail("network access is forbidden")

    monkeypatch.setattr(socket, "socket", forbidden)
    data = fixture()
    data[1]["objects"][0]["locators"] = {
        "github": "https://github.com/fictional/candidate",
        "huggingface": "https://huggingface.co/fictional/candidate",
    }
    report = assess(data)
    assert report["objects"][0]["dimensions"]["locators"] == "checked_no_findings"
    assert report["factual_requirements"]["actual_remote_restore"] == "unverified"
