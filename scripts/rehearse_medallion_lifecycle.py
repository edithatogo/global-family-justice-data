"""Recompute fictional lifecycle preparation without public operations."""

import argparse
import runpy
from pathlib import Path

from gfjd.medallion_lifecycle import assess_lifecycle_journal, verify_lifecycle_journal
from gfjd.medallion_qualification_inputs import canonical, sha


def build_report() -> dict:
    builder = Path(__file__).resolve().parents[1] / "tests/test_medallion_lifecycle.py"
    fixture = runpy.run_path(str(builder))
    args = fixture["all_operations"]()
    positive = assess_lifecycle_journal(*args)
    verify_lifecycle_journal(*args, positive)
    a, b = fixture["artifact"](), fixture["artifact"](revision="two")
    backlog = assess_lifecycle_journal(
        *fixture["journal"](
            [
                ("register", a, None, "active", ("available", "available")),
                ("correct", b, a, "active", ("available", "available")),
            ]
        )
    )
    report = {
        "contract_version": "gfjd-fictional-lifecycle-rehearsal-v1",
        "synthetic": True,
        "builder_sha256": sha(builder.read_bytes()),
        "rehearsal_sha256": sha(Path(__file__).read_bytes()),
        "all_operations": positive,
        "implicit_withdrawal_backlog": backlog,
        "authority": positive["authority"],
    }
    report["report_sha256"] = sha(canonical(report))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", type=Path, required=True)
    args = parser.parse_args(argv)
    expected = canonical(build_report()) + b"\n"
    try:
        with args.verify.open("rb") as stream:
            actual = stream.read(len(expected) + 1)
    except OSError:
        return 1
    if actual != expected:
        return 1
    print("fictional lifecycle replay verified; public execution remains unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
