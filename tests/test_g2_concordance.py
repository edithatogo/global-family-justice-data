from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gfjd.g2_concordance import G2ConcordanceError, compare_g2_extractions
from gfjd.io import sha256_file

SHA = "a" * 64
COMMIT = "b" * 40


def _root(project_root: Path, tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    schemas = root / "schemas"
    schemas.mkdir(parents=True)
    for name in ("g2_extraction_row.schema.json", "g2_concordance.schema.json"):
        shutil.copyfile(project_root / "schemas" / name, schemas / name)
    return root


def _row(index: int, **changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "extracted_row_id": f"G2ROW-TEST{index:03d}",
        "source_record_key": hashlib.sha256(f"record-{index}".encode()).hexdigest(),
        "candidate_id": "AUS",
        "source_id": "AUS-FCFCOA-AR",
        "source_edition_id": "ED-AUS-TEST",
        "provenance_locator": f"page 1 row {index}",
        "measure_original": "Applications",
        "matter_type_original": "Family",
        "statistic_type": "count",
        "unit": "applications",
        "value": index,
        "component_values": {},
        "denominator_value": None,
        "denominator_definition": None,
        "period_start": "2025-01-01",
        "period_end": "2025-12-31",
        "time_basis": "not_applicable",
        "cohort_basis": "filed",
        "population_scope": "national",
        "suppression_or_disclosure_note": None,
        "extraction_uncertainty": "none",
        "notes": None,
    }
    payload.update(changes)
    return payload


def _write(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _artifact(path: str) -> dict[str, str]:
    return {"path": path, "sha256": SHA}


def _compare(
    root: Path,
    primary: list[dict[str, object]],
    secondary: list[dict[str, object]],
    *,
    output: str = "build/compare",
    **kwargs: object,
):
    primary_path = _write(root / "inputs/primary.json", primary)
    secondary_path = _write(root / "inputs/secondary.json", secondary)
    return compare_g2_extractions(
        root,
        primary_path=primary_path,
        secondary_path=secondary_path,
        output_dir=Path(output),
        comparison_id="G2CMP-TEST01",
        packet_id="G2PKT-TEST01",
        packet_sha256=SHA,
        primary_receipt=_artifact("primary-receipt.json"),
        secondary_receipt=_artifact("secondary-receipt.json"),
        threshold_policy=_artifact("threshold-policy.json"),
        source_commit=COMMIT,
        generated_at="2026-08-15T00:00:00Z",
        **kwargs,
    )


def test_comparator_passes_identical_rows_and_emits_schema_valid_receipt(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    primary = [_row(1), _row(2)]
    secondary = [
        _row(2, extracted_row_id="G2ROW-SECONDARY002"),
        _row(1, extracted_row_id="G2ROW-SECONDARY001"),
    ]

    result = _compare(root, primary, secondary)

    assert result.threshold_passed is True
    assert result.critical_concordance == 1.0
    assert result.overall_concordance == 1.0
    receipt = json.loads(result.receipt_path.read_text(encoding="utf-8"))
    differences = json.loads(result.difference_path.read_text(encoding="utf-8"))
    schema = json.loads((root / "schemas/g2_concordance.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    assert list(validator.iter_errors(receipt)) == []
    assert receipt["status"] == "pass"
    assert receipt["difference_artifact"]["sha256"] == sha256_file(result.difference_path)
    assert differences["difference_count"] == 0


def test_comparator_never_waives_critical_difference_above_overall_threshold(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    primary = [_row(index) for index in range(100)]
    secondary = [_row(index) for index in range(100)]
    secondary[0]["value"] = 999

    result = _compare(root, primary, secondary)

    receipt = json.loads(result.receipt_path.read_text(encoding="utf-8"))
    differences = json.loads(result.difference_path.read_text(encoding="utf-8"))
    assert receipt["overall_concordance"] >= 0.99
    assert receipt["critical_concordance"] < 1.0
    assert result.threshold_passed is False
    assert receipt["status"] == "fail"
    assert differences["differences"][0]["field"] == "value"
    assert differences["differences"][0]["critical"] is True


def test_comparator_expands_component_values_as_critical_fields(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    primary = [_row(index, component_values={"filed": index}) for index in range(100)]
    secondary = [_row(index, component_values={"filed": index}) for index in range(100)]
    secondary[0]["component_values"] = {"filed": 999}

    result = _compare(root, primary, secondary)

    receipt = json.loads(result.receipt_path.read_text(encoding="utf-8"))
    differences = json.loads(result.difference_path.read_text(encoding="utf-8"))
    assert receipt["overall_concordance"] >= 0.99
    assert receipt["field_metrics"]["component_values.filed"]["critical"] is True
    assert receipt["field_metrics"]["component_values.filed"]["concordance"] == 0.99
    assert result.threshold_passed is False
    assert differences["differences"][0]["field"] == "component_values.filed"
    assert differences["differences"][0]["critical"] is True


@pytest.mark.parametrize("missing_from", ["primary", "secondary"])
def test_comparator_fails_on_unmatched_rows(
    project_root: Path, tmp_path: Path, missing_from: str
) -> None:
    root = _root(project_root, tmp_path)
    primary = [_row(1), _row(2)]
    secondary = [_row(1), _row(2)]
    if missing_from == "primary":
        primary.pop()
    else:
        secondary.pop()

    result = _compare(root, primary, secondary)

    receipt = json.loads(result.receipt_path.read_text(encoding="utf-8"))
    differences = json.loads(result.difference_path.read_text(encoding="utf-8"))
    assert result.threshold_passed is False
    assert receipt[f"{missing_from}_only_rows"] == 0
    opposite = "secondary" if missing_from == "primary" else "primary"
    assert receipt[f"{opposite}_only_rows"] == 1
    assert differences["differences"][0]["difference_type"] == f"{opposite}_only_row"


def test_comparator_enforces_overall_populated_field_threshold(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    primary = [_row(1, notes="primary")]
    secondary = [_row(1, extracted_row_id="G2ROW-SECONDARY001", notes="secondary")]

    result = _compare(root, primary, secondary)

    assert result.critical_concordance == 1.0
    assert result.overall_concordance < 0.99
    assert result.threshold_passed is False


def test_comparator_rejects_weakened_threshold_and_empty_evidence(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    with pytest.raises(G2ConcordanceError, match="between 0.99 and 1"):
        _compare(root, [_row(1)], [_row(1)], overall_threshold=0.98)
    with pytest.raises(G2ConcordanceError, match="at least one critical field"):
        _compare(root, [_row(1)], [_row(1)], critical_fields=[])

    result = _compare(root, [], [])
    assert result.threshold_passed is False


def test_comparator_rejects_invalid_rows_and_duplicate_keys(
    project_root: Path, tmp_path: Path
) -> None:
    root = _root(project_root, tmp_path)
    invalid = _row(1)
    invalid["value"] = "not-a-number"
    with pytest.raises(G2ConcordanceError, match="primary"):
        _compare(root, [invalid], [_row(1)])

    duplicate = [_row(1), _row(1, extracted_row_id="G2ROW-DUPLICATE001")]
    with pytest.raises(G2ConcordanceError, match="duplicate source_record_key"):
        _compare(root, duplicate, [_row(1)])


def test_difference_artifact_is_deterministic(project_root: Path, tmp_path: Path) -> None:
    root = _root(project_root, tmp_path)
    primary = [_row(1, notes="first")]
    secondary = [_row(1, extracted_row_id="G2ROW-SECONDARY001", notes="second")]

    first = _compare(root, primary, secondary, output="build/first")
    first_bytes = first.difference_path.read_bytes()
    second = _compare(root, primary, secondary, output="build/second")

    assert second.difference_path.read_bytes() == first_bytes
