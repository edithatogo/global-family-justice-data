"""Fictional offline fixtures for the prospective acquisition boundary."""

import copy
import json
import runpy

import pytest


@pytest.fixture
def capture(project_root):
    return runpy.run_path(str(project_root / "scripts/capture_g2_dynamic_successor.py"))


@pytest.fixture
def bra():
    return {
        "took": 1,
        "timed_out": False,
        "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
        "hits": {"hits": [], "max_score": None},
        "aggregations": {
            "case_classes": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [{"key": 1389, "doc_count": 7}],
            }
        },
    }


@pytest.fixture
def models():
    return {
        "models": [{"id": 3141088}],
        "exploration": {
            "sections": [{"visualContainers": [{"config": json.dumps({"name": "7945851748"})}]}]
        },
    }


def test_valid_fictional_responses(capture, bra, models):
    capture["validate_bra"](bra)
    capture["validate_models"](models)


@pytest.mark.parametrize(
    "mutation", ["hits", "extra_total", "bool_shard", "class", "partial", "extra_bucket"]
)
def test_bra_boundary(capture, bra, mutation):
    if mutation == "hits":
        bra["hits"]["hits"] = [{"fictional_case": True}]
    elif mutation == "extra_total":
        bra["hits"]["total"] = {"name": "fictional person"}
    elif mutation == "bool_shard":
        bra["_shards"]["failed"] = False
    elif mutation == "class":
        bra["aggregations"]["case_classes"]["buckets"][0]["key"] = 1
    elif mutation == "partial":
        bra["aggregations"]["case_classes"]["sum_other_doc_count"] = 1
    else:
        bra["aggregations"]["case_classes"]["buckets"][0]["name"] = "fictional"
    with pytest.raises(ValueError):
        capture["validate_bra"](bra)


@pytest.mark.parametrize(
    "mutation", ["nested_data", "serialized_data", "fake_identity", "root", "contact"]
)
def test_dashboard_boundary(capture, models, mutation):
    if mutation == "nested_data":
        models["exploration"]["rows"] = [{"name": "fictional"}]
    elif mutation == "serialized_data":
        models["exploration"]["extra"] = json.dumps({"data": [{"name": "fictional"}]})
    elif mutation == "fake_identity":
        models["exploration"] = {"note": "7945851748", "sections": []}
    elif mutation == "root":
        models["unreviewed"] = True
    else:
        models["exploration"]["text"] = "fictional@example.invalid"
    with pytest.raises(ValueError):
        capture["validate_models"](models)


@pytest.mark.parametrize("raw", ['{"a":1,"a":2}', '{"a":NaN}'])
def test_strict_json(capture, raw):
    with pytest.raises(ValueError):
        capture["strict_json"](raw)


def test_key_discovery_does_not_guess(capture):
    key = "A" * 32
    assert capture["public_key"](f"<code>APIKey {key}</code>".encode()) == key
    with pytest.raises(ValueError):
        capture["public_key"](b"no key")
    with pytest.raises(ValueError):
        capture["public_key"](f"APIKey {key} APIKey {'B' * 32}".encode())


@pytest.mark.parametrize("mutation", ["host", "body", "budget", "retry"])
def test_plan_scope_is_fixed(capture, project_root, mutation):
    plan = json.loads((project_root / capture["PLAN"]).read_text())
    if mutation == "host":
        plan["requests"][0]["url"] = "http://localhost/"
    elif mutation == "body":
        plan["requests"][1]["body"]["size"] = 1
    elif mutation == "budget":
        plan["requests"][1]["maximum_bytes"] += 1
    else:
        plan["retries"] = 1
    with pytest.raises(ValueError):
        capture["validate_plan"](plan)


@pytest.mark.parametrize("fail_bra", [False, True])
def test_one_shot_sealing_and_terminal_stop(
    capture, project_root, tmp_path, monkeypatch, bra, models, fail_bra
):
    plan = json.loads((project_root / capture["PLAN"]).read_text())
    namespace = capture["execute"].__globals__
    monkeypatch.setitem(namespace, "ROOT", tmp_path)
    plan_path = tmp_path / capture["PLAN"]
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(json.dumps(plan))
    vault = tmp_path / "vault"
    receipt_path = tmp_path / "receipt.json"
    key = "A" * 32
    if fail_bra:
        bra = copy.deepcopy(bra)
        bra["hits"]["hits"] = [{"fictional_case": True}]
    responses = [f"APIKey {key}".encode(), json.dumps(bra).encode(), json.dumps(models).encode()]
    calls = []

    def fake_fetch(item, supplied_key):
        calls.append(item["id"])
        recorded = json.loads(receipt_path.read_text())
        assert recorded["requests"][-1]["state"] == "attempted"
        return responses[len(calls) - 1], None

    monkeypatch.setitem(namespace, "fetch", fake_fetch)
    receipt = capture["execute"](plan, vault, receipt_path, "fictional-freeze")
    assert key not in receipt_path.read_text()
    assert receipt["extraction_performed"] is False
    assert len(calls) == (2 if fail_bra else 3)
    assert (vault / "bra_aggregate.json").exists() is not fail_bra
    assert not (vault / "public_key_document.json").exists()
    assert (receipt["state"] == "terminal_stop") is fail_bra
    with pytest.raises(ValueError, match="already attempted"):
        capture["execute"](plan, vault, receipt_path, "fictional-freeze")
