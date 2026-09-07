"""Offline fictional fixtures; no empirical dashboard data or network."""

import json
import runpy

import pytest


@pytest.fixture
def stage(project_root):
    return runpy.run_path(str(project_root / "scripts/capture_g2_dashboard_structural.py"))


@pytest.mark.parametrize(
    "key,value",
    [
        ("max_requests", 2),
        ("max_requests", True),
        ("retries", 1),
        ("redirects", True),
        ("timeout_seconds", 31),
        ("maximum_body_read_bytes", 10000002),
        ("retention_review_by", "2099-01-01"),
        ("quarantine", False),
        ("g2_acceptance", True),
        ("publication_authorized", True),
    ],
)
def test_plan_rejects_changed_controls(stage, project_root, key, value):
    plan = json.loads((project_root / stage["PLAN"]).read_text())
    plan[key] = value
    with pytest.raises(ValueError, match="plan binding"):
        stage["validate_plan"](plan)


@pytest.mark.parametrize(
    "field,value", [("body", {}), ("url", "https://example.invalid/"), ("method", "POST")]
)
def test_plan_rejects_request_drift(stage, project_root, field, value):
    plan = json.loads((project_root / stage["PLAN"]).read_text())
    plan["requests"][0][field] = value
    with pytest.raises(ValueError):
        stage["validate_plan"](plan)


@pytest.mark.parametrize("failure", [None, "timeout", "schema"])
def test_one_request_only_and_immutable_stop(stage, project_root, tmp_path, monkeypatch, failure):
    engine = stage["load_engine"]()
    plan = json.loads((project_root / stage["PLAN"]).read_text())
    monkeypatch.setattr(engine, "ROOT", tmp_path)
    plan_path = tmp_path / engine.PLAN
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(json.dumps(plan))
    receipt_path = tmp_path / "receipt.json"
    vault = tmp_path / "vault"
    calls = []

    def fake_fetch(item, key):
        assert key is None
        assert json.loads(receipt_path.read_text())["requests"][0]["state"] == "attempted"
        calls.append(item)
        if failure == "timeout":
            raise TimeoutError("must not be persisted")
        payload = {
            "models": [{"id": 3141088}],
            "exploration": {
                "sections": [{"visualContainers": [{"config": json.dumps({"name": "7945851748"})}]}]
            },
        }
        if failure == "schema":
            payload["unreviewed"] = True
        return json.dumps(payload).encode(), None

    monkeypatch.setattr(engine, "fetch", fake_fetch)
    receipt = engine.execute(plan, vault, receipt_path, "fictional-freeze")
    assert calls == [stage["REQUEST"]]
    assert receipt["lineage_id"] == stage["LINEAGE"]
    assert receipt["extraction_performed"] is False
    assert receipt["g2_acceptance"] is False
    assert (receipt["state"] == "terminal_stop") == (failure is not None)
    assert (vault / "dashboard_models.json").exists() == (failure is None)
    assert "must not be persisted" not in receipt_path.read_text()
    with pytest.raises(ValueError, match="already attempted"):
        engine.execute(plan, vault, receipt_path, "fictional-freeze")


def test_checkpoint_refuses_symlink(stage, tmp_path):
    victim = tmp_path / "victim"
    victim.write_text("unchanged")
    receipt = tmp_path / "receipt.json"
    try:
        receipt.with_suffix(".pending").symlink_to(victim)
    except OSError:
        pytest.skip("symlink privilege unavailable")
    with pytest.raises(FileExistsError):
        stage["checkpoint"](receipt, {"state": "running"})
    assert victim.read_text() == "unchanged"
    assert not receipt.exists()


def test_engine_instances_do_not_reconfigure_historical_module(stage):
    first = stage["load_engine"]()
    second = stage["load_engine"]()
    assert first is not second
    assert first.PLAN == second.PLAN == stage["PLAN"]
    assert "DYNAMIC-SUCCESSOR" not in first.VAULT.as_posix()
