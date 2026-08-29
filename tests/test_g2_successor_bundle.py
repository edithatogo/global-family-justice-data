import json
import shutil
from pathlib import Path

from gfjd.g2_successor_bundle import _query_manifest, _role_bundles, build, verify


def test_successor_queries_are_distinct_and_bounded() -> None:
    manifest = _query_manifest()
    queries = manifest["queries"]
    assert len(queries) == 16
    assert [item["ordinal"] for item in queries] == list(range(1, 17))
    assert len({item["query_text"] for item in queries}) == 16
    assert manifest["provider_result_policy"] == {
        "requested_maximum": 10,
        "absolute_safety_cap": 50,
    }


def test_role_bundles_begin_fail_closed() -> None:
    bundles = _role_bundles()["bundles"]
    assert len(bundles) == 6
    assert all(bundle["activation"] == "pending_stage_interlock" for bundle in bundles)
    assert all(bundle["network_url_allowlist"] == [] for bundle in bundles)
    prefixes = [Path(str(bundle["output_prefix"])) for bundle in bundles]
    assert len(set(prefixes)) == len(prefixes)


def _root(tmp_path: Path, project_root: Path) -> Path:
    root = tmp_path / "repository"
    controls = root / "src/gfjd/g2_successor_controls.py"
    controls.parent.mkdir(parents=True)
    shutil.copyfile(project_root / "src/gfjd/g2_successor_controls.py", controls)
    evidence = root / "data/methods/g2/example/evidence.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text(
        json.dumps(
            {
                "source_url": "https://example.test/report.pdf",
                "source_sha256": "a" * 64,
            }
        ),
        encoding="utf-8",
    )
    schema = evidence.with_name("ignored.schema.json")
    schema.write_text(json.dumps({"source_url": {"type": "string"}}), encoding="utf-8")
    return root


def test_build_and_verify_complete_preparation_bundle(tmp_path: Path, project_root: Path) -> None:
    root = _root(tmp_path, project_root)
    output = Path("data/methods/g2/successor/execution-control")

    packet = build(root, output)

    assert packet["authority_boundary"] == {
        "network_access": False,
        "source_access": False,
        "publication": False,
        "release": False,
        "g2_passage": False,
    }
    snapshot = json.loads((root / output / "exposure-snapshot.json").read_text())
    assert snapshot["counts"] == {"content_sha256": 1, "urls": 1}
    assert len(snapshot["inputs"]) == 1
    assert verify(root, output) == []


def test_verify_rejects_semantic_tampering(tmp_path: Path, project_root: Path) -> None:
    root = _root(tmp_path, project_root)
    output = Path("data/methods/g2/successor/execution-control")
    build(root, output)
    transport_path = root / output / "transport-contract.json"
    transport = json.loads(transport_path.read_text())
    transport["execution_enabled"] = True
    transport_path.write_text(json.dumps(transport), encoding="utf-8")

    assert verify(root, output) == ["transport contract differs"]


def test_verify_rejects_packet_binding_tampering(tmp_path: Path, project_root: Path) -> None:
    root = _root(tmp_path, project_root)
    output = Path("data/methods/g2/successor/execution-control")
    build(root, output)
    packet_path = root / output / "preparation-packet.json"
    packet = json.loads(packet_path.read_text())
    packet["stages"]["metadata_registration"] = "authorized"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    assert verify(root, output) == ["preparation packet differs"]
