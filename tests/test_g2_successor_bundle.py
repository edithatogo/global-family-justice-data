from pathlib import Path

from gfjd.g2_successor_bundle import _query_manifest, _role_bundles


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
