import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from gfjd.g2_statcan_metadata import evaluate_metadata


def _payload(release: str = "2026-03-26T08:30") -> list[dict[str, object]]:
    return [
        {
            "status": "SUCCESS",
            "object": {
                "productId": "35100222",
                "cubeTitleEn": "Family law cases, by type of case",
                "cubeEndDate": "2024-01-01",
                "releaseTime": release,
                "issueDate": "2026-03-26",
            },
        }
    ]


def test_pre_cutoff_metadata_is_monitor_only() -> None:
    rows, summary = evaluate_metadata(
        _payload(),
        product_ids=[35100222],
        expected_titles={"35100222": "Family law cases, by type of case"},
        cutoff=datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC),
    )
    assert rows[0]["post_cutoff_update"] is False
    assert summary["outcome"] == "monitor_no_update"
    assert summary["eligibility_established"] is False


def test_post_cutoff_metadata_requires_review() -> None:
    _, summary = evaluate_metadata(
        _payload("2027-03-26T08:30"),
        product_ids=[35100222],
        expected_titles={"35100222": "Family law cases, by type of case"},
        cutoff=datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC),
    )
    assert summary["outcome"] == "review_required"


def test_title_drift_fails_closed() -> None:
    with pytest.raises(ValueError, match="title drift"):
        evaluate_metadata(
            _payload(),
            product_ids=[35100222],
            expected_titles={"35100222": "Wrong"},
            cutoff=datetime(2026, 8, 29, 5, 17, 40, tzinfo=UTC),
        )


def test_monitor_preserves_terminal_failure_receipt(tmp_path: Path) -> None:
    contract = {
        "campaign_id": "test",
        "endpoint": "https://prohibited.example/metadata",
        "allowed_endpoint_host": "www150.statcan.gc.ca",
        "allowed_endpoint_path": "/t1/wds/rest/getCubeMetadata",
        "product_ids": [35100222],
        "authority_boundary": {"table_data_access": False},
    }
    contract_path = tmp_path / "contract.json"
    output = tmp_path / "output"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/g2_statcan_family_law_metadata_monitor.py",
            "--contract",
            str(contract_path),
            "--output",
            str(output),
            "--checked-at",
            "2026-08-29T00:00:00Z",
            "--source-commit",
            "test",
            "--run-id",
            "test",
        ],
        check=False,
    )
    assert result.returncode == 2
    receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "terminal_failure"
    assert receipt["summary"]["eligibility_established"] is False
