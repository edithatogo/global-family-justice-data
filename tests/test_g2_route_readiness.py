"""Regressions for confusing acquisition metadata with extraction inputs."""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "data/methods/g2/G2-ROUTE-MATCHED-READINESS-20260905.json"
PROPOSAL = ROOT / "data/methods/g2/G2NEXT-UNBLOCK-20260824-01/blind-execution-proposal.json"


@pytest.mark.parametrize("route", ["api", "spreadsheet", "html_dashboard"])
def test_readiness_source_matches_approved_scope_and_packet(route: str) -> None:
    readiness = json.loads(READINESS.read_text())
    proposal = json.loads(PROPOSAL.read_text())
    row = next(item for item in readiness["missing_cells"] if item["route"] == route)
    approved = next(
        item for item in proposal["source_scope"] if item["candidate_id"] == row["candidate_id"]
    )
    assert row["source_sha256"] == approved["content_sha256"]
    packet_bytes = (ROOT / row["source_packet_path"]).read_bytes()
    assert hashlib.sha256(packet_bytes).hexdigest() == row["source_packet_sha256"]
    packet = json.loads(packet_bytes)
    if route == "api":
        bound = packet["response"]["sha256"]
        assert packet["source"]["class_code"] == 1389
    elif route == "html_dashboard":
        bound = packet["bound_artifacts"]["query_response_sha256"]
        assert packet["filters"]["period"] == "Quarterly"
        assert bound != packet["source"]["entry_html_sha256"]
    else:
        source = next(
            item for item in packet["sources"] if item["candidate_id"] == row["candidate_id"]
        )
        bound = source["source_sha256"]
    assert row["source_sha256"] == bound
