"""Exact offline comparison of sealed descriptive SWE/AUS outputs."""

import argparse
import hashlib
import json
from pathlib import Path


def load(path: Path, digest: str) -> dict:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("seal mismatch")

    def unique(pairs: list) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    return json.loads(raw, object_pairs_hook=unique)


def validate(value: dict, contract: dict) -> None:
    assert set(value) == {"contract_id", "rows"}
    assert value["contract_id"] == contract["contract_id"]
    assert len(value["rows"]) == 14
    offset = 0
    for source in contract["cohort"]:
        rows = source.get("data_rows", source.get("table_rows_one_based"))
        for number in rows:
            row = value["rows"][offset]
            assert set(row) == set(contract["output_contract"]["common_fields"]) | set(
                source["row_fields"]
            )
            assert type(row["source_row"]) is int and row["source_row"] == number
            assert row["inventory_id"] == source["inventory_id"]
            assert row["source_sha256"] == source["sha256"]
            assert row["period_label_source"] == source["period_label"]
            assert row["period_start"] is None and row["period_end"] is None
            assert row["comparison_eligible"] is False and row["quarantined"] is True
            locator = (
                f"{source['sheet']}!B{number}:D{number}"
                if source["format"] == "xlsx"
                else f"PDF page 102; Table 3.3.1(a); data row {number}"
            )
            assert row["locator"] == locator
            for key in set(row) - {
                "source_row",
                "period_start",
                "period_end",
                "comparison_eligible",
                "quarantined",
            }:
                assert type(row[key]) is str and row[key] != ""
            offset += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("contract", "a", "b", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    for name in ("contract", "a", "b"):
        parser.add_argument(f"--{name}-sha256", required=True)
    args = parser.parse_args()
    contract = load(args.contract, args.contract_sha256)
    a, b = load(args.a, args.a_sha256), load(args.b, args.b_sha256)
    validate(a, contract)
    validate(b, contract)
    count = matches = populated = populated_matches = 0
    for left, right in zip(a["rows"], b["rows"], strict=True):
        for key in left:
            equal = type(left[key]) is type(right[key]) and left[key] == right[key]
            count += 1
            matches += equal
            if left[key] is not None or right[key] is not None:
                populated += 1
                populated_matches += equal
    passed = matches == count and populated_matches * 100 >= populated * 99
    report = dict(
        contract_sha256=args.contract_sha256,
        a_sha256=args.a_sha256,
        b_sha256=args.b_sha256,
        critical_matches=matches,
        critical_fields=count,
        populated_matches=populated_matches,
        populated_fields=populated,
        passed=passed,
        source_accuracy_review_required=True,
        gate_acceptance=False,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
