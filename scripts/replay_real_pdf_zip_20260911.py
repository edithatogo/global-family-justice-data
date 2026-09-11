#!/usr/bin/env python3
"""Run a fresh two-path replay for the real PDF/ZIP B0 routes.

The source bytes are already present in the controlled local cohort.  This
script performs no network access and writes only aggregate rows, hashes and
receipts.  It is supporting reproducibility evidence, not rights, semantic,
layer, maturity, gate, publication or release acceptance.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from gfjd import g2_concordance, medallion_pdf, medallion_zip
from gfjd.io import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "data/federation/real-pdf-zip-replay-contract-20260911.json"
RUN = ROOT / "data/federation/real-pdf-zip-replay-20260911"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: Any) -> bytes:
    return canonical_json_bytes(value)


def source_bytes(contract: dict[str, Any]) -> bytes:
    path = ROOT / contract["payload_path"]
    raw = path.read_bytes()
    if sha(raw) != contract["source_sha256"]:
        raise SystemExit(f"source_digest_mismatch:{contract['inventory_id']}")
    return raw


def row(contract: dict[str, Any], value: int | float, locator: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "extracted_row_id": contract["row_id"],
        "source_record_key": contract["source_record_key"],
        "candidate_id": contract["candidate_id"],
        "source_id": contract["source_id"],
        "source_edition_id": contract["source_edition_id"],
        "provenance_locator": locator,
        "measure_original": contract["measure_original"],
        "matter_type_original": contract["matter_type_original"],
        "statistic_type": contract["statistic_type"],
        "unit": contract["unit"],
        "value": value,
        "component_values": {},
        "denominator_value": None,
        "denominator_definition": None,
        "period_start": None,
        "period_end": None,
        "time_basis": "source_defined",
        "cohort_basis": contract["cohort_basis"],
        "population_scope": contract["population_scope"],
        "suppression_or_disclosure_note": None,
        "extraction_uncertainty": "none",
        "notes": None,
    }


def path_a(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Primary path: versioned bounded adapters."""
    result = []
    for contract in contracts:
        source = source_bytes(contract)
        if contract["format"] == "pdf":
            receipt = medallion_pdf.extract_pdf(source, contract["adapter_contract"])
        else:
            receipt = medallion_zip.extract_zip_csv(source, contract["adapter_contract"])
        result.append(row(contract, receipt["value"], contract["locator"]))
    return result


def path_b_pdf(source: bytes, contract: dict[str, Any]) -> int | float:
    """Separate PDF path using a subprocess text rendering and the same frozen markers."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
        handle.write(source)
        handle.flush()
        text = subprocess.check_output(
            ["pdftotext", "-f", str(contract["page_number"]), "-l", str(contract["page_number"]), "-layout", handle.name, "-"],
            text=True,
            errors="strict",
        )
    if not all(marker in text for marker in contract["markers"]):
        raise SystemExit("path_b_pdf_marker_mismatch")
    import re

    pattern = contract["pattern"]
    # pdftotext preserves layout indentation; compare the same source lines
    # after removing only layout whitespace, never lexical content.
    matches = []
    for line in text.splitlines():
        candidate = line.strip()
        if re.fullmatch(pattern.replace("(?m)^", "").replace("$", ""), candidate):
            matches.extend(re.finditer(pattern.replace("(?m)^", "").replace("$", ""), candidate))
    if len(matches) != 1:
        raise SystemExit("path_b_pdf_match_count_mismatch")
    raw = matches[0].group("value").replace(",", "").strip()
    return float(raw) if "." in raw else int(raw)


def path_b_zip(source: bytes, contract: dict[str, Any]) -> int | float:
    """Separate ZIP path using direct CSV parsing, not the adapter implementation."""
    with zipfile.ZipFile(io.BytesIO(source), "r") as archive:
        raw = archive.read(contract["member_name"])
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    matches = [
        item
        for item in rows
        if all(item.get(key) == value for key, value in contract["selector"].items())
    ]
    if len(matches) != 1:
        raise SystemExit("path_b_zip_match_count_mismatch")
    raw_value = matches[0][contract["value_field"]].strip()
    return float(raw_value) if "." in raw_value else int(raw_value)


def path_b(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for contract in contracts:
        source = source_bytes(contract)
        adapter = contract["adapter_contract"]
        value = path_b_pdf(source, adapter) if contract["format"] == "pdf" else path_b_zip(source, adapter)
        result.append(row(contract, value, contract["locator"]))
    return result


def main() -> None:
    packet = json.loads(PACKET.read_bytes())
    contracts = packet["contracts"]
    RUN.mkdir(parents=True, exist_ok=False)
    a_rows = path_a(contracts)
    b_rows = path_b(contracts)
    a_path = RUN / "extraction-a.json"
    b_path = RUN / "extraction-b.json"
    a_path.write_bytes(canonical(a_rows) + b"\n")
    b_path.write_bytes(canonical(b_rows) + b"\n")
    threshold_path = RUN / "threshold-policy.json"
    threshold_path.write_bytes(canonical(packet["thresholds"]) + b"\n")
    comparison = g2_concordance.compare_g2_extractions(
        ROOT,
        primary_path=a_path,
        secondary_path=b_path,
        output_dir=RUN / "comparison",
        comparison_id="G2CMP-REAL-PDF-ZIP-20260911-01",
        packet_id=packet["packet_id"],
        packet_sha256=sha(PACKET.read_bytes()),
        primary_receipt={"path": a_path.relative_to(ROOT).as_posix(), "sha256": sha(a_path.read_bytes())},
        secondary_receipt={"path": b_path.relative_to(ROOT).as_posix(), "sha256": sha(b_path.read_bytes())},
        threshold_policy={
            "path": threshold_path.relative_to(ROOT).as_posix(),
            "sha256": sha(threshold_path.read_bytes()),
        },
        source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        generated_at="2026-09-11T00:00:00Z",
        expected_source_keys=[item["source_record_key"] for item in contracts],
        limitations=(
            "Two repository-owned extraction paths over the frozen local B0 bytes.",
            "This is supporting reproducibility evidence, not independent assurance.",
            "Rows remain quarantined; rights, semantic equivalence, layer maturity, G2, publication and release are unresolved.",
        ),
    )
    receipt = {
        "schema_version": "1.0",
        "evidence_id": "E-REAL-PDF-ZIP-REPLAY-20260911",
        "packet_id": packet["packet_id"],
        "packet_sha256": sha(PACKET.read_bytes()),
        "source_scope": [item["inventory_id"] for item in contracts],
        "source_bytes_local_only": True,
        "network_requests": 0,
        "path_a": {"path": a_path.relative_to(ROOT).as_posix(), "sha256": sha(a_path.read_bytes())},
        "path_b": {"path": b_path.relative_to(ROOT).as_posix(), "sha256": sha(b_path.read_bytes())},
        "comparison": {
            "path": comparison.receipt_path.relative_to(ROOT).as_posix(),
            "sha256": sha(comparison.receipt_path.read_bytes()),
            "difference_path": comparison.difference_path.relative_to(ROOT).as_posix(),
            "difference_sha256": sha(comparison.difference_path.read_bytes()),
            "threshold_passed": comparison.threshold_passed,
            "critical_concordance": comparison.critical_concordance,
            "overall_concordance": comparison.overall_concordance,
        },
        "status": "supporting_reproducibility_pass" if comparison.threshold_passed else "failed",
        "rights_clearance": False,
        "semantic_equivalence": False,
        "layer_acceptance": False,
        "maturity_acceptance": False,
        "g2_acceptance": False,
        "publication_authorized": False,
        "release_authorized": False,
    }
    receipt_path = ROOT / "data/federation/real-pdf-zip-replay-receipt-20260911.json"
    receipt_path.write_bytes(canonical(receipt) + b"\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
