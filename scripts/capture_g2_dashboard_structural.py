"""One new dashboard structural GET; never resume the failed dynamic lineage."""

import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINEAGE = "G2-DASHBOARD-STRUCTURAL-20260907-01"
PLAN = Path(f"data/methods/g2/{LINEAGE}/plan.json")
URL = (
    "https://wabi-north-europe-e-primary-api.analysis.windows.net/public/reports/"
    "c809ac7e-68c0-41ae-8552-3e483d0d20b8/modelsAndExploration?preferReadOnlySession=true"
)
REQUEST = {
    "id": "dashboard_models",
    "method": "GET",
    "url": URL,
    "maximum_bytes": 10000000,
    "retain_body": True,
}


def validate_plan(plan):
    required = {
        "lineage_id": LINEAGE,
        "max_requests": 1,
        "retries": 0,
        "redirects": False,
        "timeout_seconds": 30,
        "maximum_body_read_bytes": 10000001,
        "retention_review_by": "2027-08-24",
        "quarantine": True,
        "g2_acceptance": False,
        "publication_authorized": False,
        "requests": [REQUEST],
    }
    for key, expected in required.items():
        # Reject bool-as-int and extra request fields, including GET bodies.
        if json.dumps(plan.get(key), sort_keys=True) != json.dumps(expected, sort_keys=True):
            raise ValueError(f"dashboard plan binding: {key}")


def checkpoint(path, receipt):
    pending = path.with_suffix(".pending")
    # O_EXCL refuses both a preexisting file and a dangling/live symlink.
    fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(receipt, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    pending.replace(path)


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "dashboard_structural_engine", ROOT / "scripts/capture_g2_dynamic_successor.py"
    )
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    # A fresh module instance, not changes to historical files or global state.
    engine.PLAN = PLAN
    engine.VAULT = Path(f"data/raw/files/{LINEAGE}")
    engine.RECEIPT = Path("docs/governance/g2-dashboard-structural-capture-2026-09-07.json")
    engine.validate_plan = validate_plan
    engine.checkpoint = checkpoint
    return engine


if __name__ == "__main__":
    raise SystemExit(load_engine().main())
