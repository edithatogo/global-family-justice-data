"""Recompute the bounded Swedish replay; preserve source outputs outside Git."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from gfjd import medallion_pipeline, medallion_xlsx


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "build/real-swe-replay-20260905-02"
    output.mkdir(mode=0o700, exist_ok=False)
    canonical = medallion_pipeline._canonical

    def sha(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    frozen_path = root / "data/methods/g2-swe-aus-successor-20260905.json"
    frozen = json.loads(frozen_path.read_bytes())["cohort"][0]
    source = (
        root
        / "data/raw/files/direct-enquiries/SWE"
        / "Cases filed and determined, family cases in district courts 2025.xlsx"
    ).read_bytes()
    safety = (root / "data/preservation/public_b0_safety_20260827.json").read_bytes()
    custody = (root / "data/preservation/public_b0_custody_20260827.json").read_bytes()
    extraction = {
        "extraction_version": medallion_xlsx.VERSION,
        "source_sha256": frozen["sha256"],
        "sheet_name": frozen["sheet"],
        "header_row": frozen["header_row"],
        "columns": frozen["columns"],
        "data_rows": frozen["data_rows"],
    }
    b1 = medallion_xlsx.extract_xlsx(source, extraction)
    contract = {
        "pipeline_version": medallion_pipeline.VERSION,
        "inventory_id": frozen["inventory_id"],
        "safety_receipt_sha256": sha(safety),
        "custody_receipt_sha256": sha(custody),
        "extraction_contract": extraction,
        "projection_contract": {
            "contract_version": "gfjd-json-projection-v1",
            "source_sha256": sha(canonical(b1["rows"])),
            "projection": {
                "case_type_source": "Case type",
                "cases_filed_source": "Cases filed",
                "cases_determined_source": "Cases determined",
            },
            "valid_from": None,
            "recorded_at": "2026-09-05T00:00:00Z",
        },
    }
    first = medallion_pipeline.replay_pipeline(source, safety, custody, contract)
    second = medallion_pipeline.replay_pipeline(source, safety, custody, contract)
    medallion_pipeline.verify_pipeline(source, safety, custody, contract, first)
    if canonical(first) != canonical(second):
        raise ValueError("nondeterministic replay")
    checks = {}
    tampered = copy.deepcopy(first)
    tampered["b1"]["rows"][0]["Cases filed"] = "tampered"
    for label, raw, receipt in (
        ("changed_source_rejected", source + b"tampered", first),
        ("changed_output_rejected", source, tampered),
    ):
        try:
            medallion_pipeline.verify_pipeline(raw, safety, custody, contract, receipt)
        except medallion_pipeline.PipelineError:
            checks[label] = True
        else:
            raise ValueError(label)
    sealed_path = root / "build/g2-swe-aus-successor/role-a/output.json"
    sealed_bytes = sealed_path.read_bytes()
    expected_seal = "da6a1b140487714cba8df727deae1b64b022e7cc1e73e7d5d9085ca768b41474"
    if sha(sealed_bytes) != expected_seal:
        raise ValueError("G2 supporting output seal mismatch")
    reviewed = [
        r for r in json.loads(sealed_bytes)["rows"] if r["inventory_id"] == frozen["inventory_id"]
    ]
    fields = contract["projection_contract"]["projection"]
    expected = [{key: row[key] for key in fields} for row in reviewed]
    if first["silver"]["rows"] != expected:
        raise ValueError("reviewed source-field mapping mismatch")
    for name, value in (
        ("contract.json", contract),
        ("replay-a.json", first),
        ("replay-b.json", second),
    ):
        path = output / name
        path.write_bytes(canonical(value))
        path.chmod(0o600)
    receipt = {
        "schema_version": "1.0",
        "evidence_id": "E-REAL-SWE-B0-REPLAY-20260905-02",
        "source_sha256": sha(source),
        "contract_sha256": sha(canonical(contract)),
        "artifact_sha256": sha(canonical(first)),
        "b1_rows_sha256": first["b1_rows_sha256"],
        "b1_row_count": len(first["b1"]["rows"]),
        "silver_row_count": len(first["silver"]["rows"]),
        "deterministic_double_execution": True,
        "source_recomputation_verifier": True,
        "verifier_implementation": (
            "verify_pipeline invokes the same replay_pipeline implementation; "
            "this is recomputation, not implementation-independent verification."
        ),
        "negative_checks": checks,
        "source_field_mapping": contract["projection_contract"]["projection"],
        "supporting_g2_contract_sha256": sha(frozen_path.read_bytes()),
        "supporting_sealed_extraction_output_sha256": expected_seal,
        "sealed_extraction_lexical_field_matches": 30,
        "lexical_match_scope": (
            "Ten original SWE B:D triples; exact lexical values, same row order. "
            "Matches extractor A's sealed output. No new source-accuracy review, "
            "independent G2 run or extension of owner acceptance."
        ),
        "status": "empirical_replay_verified_pending_layer_adjudication",
        "network_requests": 0,
        "current_remote_custody_verified": False,
        "rights_clearance": False,
        "layer_acceptance": False,
        "g2_acceptance": False,
        "publication_authorized": False,
        "release_authorized": False,
        "artifact_directory": "build/real-swe-replay-20260905-02",
        "historical_artifact_reconstructed": False,
        "recorded_at_semantics": (
            "Fixed replay metadata instant on observation date; "
            "not source publication or measured run time."
        ),
    }
    receipt_path = root / "data/federation/real-swe-b0-replay-receipt-20260905-02.json"
    with receipt_path.open("x") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
