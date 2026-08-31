"""Fictional two-bank complete-inventory rehearsal; no actual provider access."""

import argparse
import runpy
from pathlib import Path
from typing import Any

from gfjd.medallion_qualification_inputs import canonical, sha
from gfjd.medallion_restore import assess_restore_rehearsal, verify_restore_rehearsal


def build_report() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    builder = root / "tests/test_medallion_restore.py"
    fixture = runpy.run_path(str(builder))
    arguments = fixture["restore_arguments"]()
    positive = assess_restore_rehearsal(*arguments)
    verify_restore_rehearsal(*arguments, positive)
    blocked = assess_restore_rehearsal(*fixture["restore_arguments"](blocked=True))
    missing = fixture["restore_arguments"]()
    missing[-1]["huggingface"].pop(next(iter(missing[-1]["huggingface"])))
    try:
        assess_restore_rehearsal(*missing)
    except ValueError:
        missing_rejected = True
    else:
        raise ValueError("fictional missing peer unexpectedly accepted")
    report = {
        "contract_version": "gfjd-fictional-two-replica-rehearsal-v1",
        "synthetic": True,
        "builder_sha256": sha(builder.read_bytes()),
        "qualification_builder_sha256": sha(
            (root / "tests/test_medallion_qualification.py").read_bytes()
        ),
        "rehearsal_sha256": sha(Path(__file__).read_bytes()),
        "complete_supplied_banks": positive,
        "reproduced_blocked_qualification": blocked,
        "missing_peer_rejected": missing_rejected,
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
    print("fictional restore recomputed; public restore and authority remain unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
