"""Recompute a fictional five-layer qualification and fail-closed counterexample.

Developer rehearsal only: uses the checked-in fictional test builder, not any
source edition. Provider-shaped fixture assertions are never live retrievals.
"""

from __future__ import annotations

import argparse
import copy
import json
import runpy
from pathlib import Path
from typing import Any

from gfjd.medallion_history import build_event
from gfjd.medallion_qualification import verify_qualification
from gfjd.medallion_qualification_inputs import canonical, sha


def build_report() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    builder = root / "tests/test_medallion_qualification.py"
    fixture = runpy.run_path(str(builder))
    inputs = fixture["fixture"](root)
    _, records, bank, _ = inputs
    silver = records[2]
    projection = json.loads(bank[silver["artifacts"]["contract"]])
    current_rows = bank[silver["artifacts"]["source"]]
    old_rows = json.loads(current_rows)
    old_rows[0]["value"] = "9"
    old_raw = canonical(old_rows)
    old_projection = {
        **projection,
        "source_sha256": sha(old_raw),
        "recorded_at": "2026-08-30T00:00:00Z",
    }
    old_event = build_event(
        old_raw, old_projection, partition="FICTIONAL", valid_until=None, supersedes=None
    )
    current_event = build_event(
        current_rows,
        projection,
        partition="FICTIONAL",
        valid_until=None,
        supersedes=old_event["event_id"],
    )
    history = {
        "version": "gfjd-qualification-history-v1",
        "object_id": "FICTIONAL",
        "edition_id": "FICTIONAL-EDITION",
        "events": [old_event, current_event],
        "sources": [
            {"sha256": sha(old_raw), "rows": old_rows},
            {"sha256": sha(current_rows), "rows": json.loads(current_rows)},
        ],
    }
    checkpoint = {
        "version": "gfjd-qualification-history-v1",
        "object_id": "FICTIONAL",
        "edition_id": "FICTIONAL-EDITION",
        "previous_events": [old_event],
        "previous_events_sha256": sha(canonical([old_event])),
    }
    for role, value in (("history", history), ("checkpoint", checkpoint)):
        raw = canonical(value)
        bank[sha(raw)] = raw
        silver["artifacts"][role] = sha(raw)
    positive = fixture["evaluate"](inputs)
    verify_qualification(*fixture["arguments"](*inputs), positive, as_of=fixture["AS_OF"])
    changed = copy.deepcopy(inputs)
    scope, records, bank, contract = changed
    false_rows = canonical([{"fictional": "intentionally substituted Gold rows"}])
    bank[sha(false_rows)] = false_rows
    records[3]["artifacts"]["rows"] = sha(false_rows)
    negative_inputs = (scope, records, fixture["prune"](records, bank), contract)
    negative = fixture["evaluate"](negative_inputs)
    verify_qualification(*fixture["arguments"](*negative_inputs), negative, as_of=fixture["AS_OF"])
    if not (
        len(positive["coverage"]) == 5
        and positive["coverage"][2]["mechanical_checks"]["history"]["full_replay"]["event_count"]
        == 2
        and positive["coverage"][4]["mechanical_checks"]["composition"]["object_count"] == 1
        and negative["coverage"][0]["dimensions"]["fixity"] == "verified"
        and negative["coverage"][3]["dimensions"]["reproducibility"] == "failed"
        and negative["coverage"][4]["blockers"]
    ):
        raise ValueError("fictional qualification rehearsal contract failed")
    report = {
        "rehearsal_id": "FICTIONAL-MEDALLION-QUALIFICATION-20260831-02",
        "predecessor_rehearsal_sha256": (
            "58c47f7f18e5a19f51ddee00531967318aa24632a96dcd254b3dfdf60cc65fd2"
        ),
        "synthetic": True,
        "fixture_implementation_sha256": sha(builder.read_bytes()),
        "rehearsal_implementation_sha256": sha(Path(__file__).read_bytes()),
        "fixture_scope": "one fictional object; all five layers; no empirical coverage claim",
        "provider_assertions": "fictional only; no provider contacted or retrieved",
        "positive_mechanics_with_pending_authority": positive,
        "substitution_rejected_with_upstream_fixity_preserved": negative,
        "authority": dict.fromkeys(
            [
                "network",
                "source_access",
                "rights_clearance",
                "promotion",
                "publication",
                "release",
                "gate_acceptance",
            ],
            False,
        ),
    }
    report["report_sha256"] = sha(canonical(report))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--verify", type=Path)
    args = parser.parse_args(argv)
    expected = canonical(build_report()) + b"\n"
    if args.verify is not None:
        try:
            with args.verify.open("rb") as stream:
                actual = stream.read(len(expected) + 1)
        except OSError:
            print("fictional qualification rehearsal unavailable")
            return 1
        if actual != expected:
            print("fictional qualification rehearsal differs from recomputation")
            return 1
        print("fictional qualification recomputed; no maturity or authority granted")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(expected)
    print("fictional qualification report written; no source or provider access")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
