#!/usr/bin/env python3
"""Deterministic fictional XLSX-to-correction rehearsal; never retrieved evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import stat
import zipfile
from pathlib import Path
from types import ModuleType
from typing import Any

from blake3 import blake3

from gfjd import (
    medallion_history,
    medallion_pipeline,
    medallion_replay,
    medallion_xlsx,
    public_archive,
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def implementation_digest(module: ModuleType) -> str:
    if module.__file__ is None:
        raise ValueError("rehearsal implementation file unavailable")
    return sha(Path(module.__file__).read_bytes())


def fictional_workbook(value: str) -> bytes:
    """Build a stored, fixed-metadata OOXML fixture, never read a source workbook."""
    if value not in {"0007", "0009"}:
        raise ValueError("unsupported fictional revision")
    s, r, p, t = medallion_xlsx.S, medallion_xlsx.R, medallion_xlsx.P, medallion_xlsx.T
    parts = {
        "[Content_Types].xml": (
            f'<Types xmlns="{t}"><Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": f'<Relationships xmlns="{p}"><Relationship Id="rId1" '
        f'Type="{r}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<workbook xmlns="{s}" xmlns:r="{r}"><sheets>'
        '<sheet name="Fictional" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": f'<Relationships xmlns="{p}"><Relationship Id="rId1" '
        f'Type="{r}/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": (
            f'<worksheet xmlns="{s}"><sheetData><row r="1">'
            '<c r="A1" t="inlineStr"><is><t>Measure</t></is></c>'
            '<c r="B1" t="inlineStr"><is><t>Count</t></is></c></row><row r="2">'
            '<c r="A2" t="inlineStr"><is><t>Fictional applications</t></is></c>'
            f'<c r="B2" t="n"><v>{value}</v></c></row></sheetData></worksheet>'
        ),
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, xml in sorted(parts.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, xml.encode("utf-8"))
    return output.getvalue()


def fictional_inputs(value: str, recorded_at: str) -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    source = fictional_workbook(value)
    safe = {
        "inventory_id": "FICTIONAL-NOT-RETRIEVED",
        "payload_path": "fictional.xlsx",
        "sha256": sha(source),
        "blake3": blake3(source).hexdigest(),
        "size_bytes": len(source),
        "disposition": "public_safe",
        "findings": [],
    }
    safety = canonical(
        {
            "contract_version": public_archive.CONTRACT_VERSION,
            "status": "pass",
            "synthetic": True,
            "not_retrieved": True,
            "objects": [safe],
        }
    )
    item = {key: safe[key] for key in ("inventory_id", "sha256", "blake3", "size_bytes")}
    item["replicas"] = [
        {
            "provider": provider,
            "url": f"https://{host}/fictional/not-retrieved",
            "anonymous_get_verified": True,
            "retrieved_sha256": sha(source),
            "retrieved_blake3": blake3(source).hexdigest(),
            "synthetic_assertion_not_retrieved": True,
        }
        for provider, host in (("github", "github.com"), ("huggingface", "huggingface.co"))
    ]
    custody = canonical(
        {
            "contract_version": public_archive.CUSTODY_CONTRACT_VERSION,
            "safety_receipt_sha256": sha(safety),
            "synthetic": True,
            "not_retrieved": True,
            "objects": [item],
        }
    )
    b1_rows = [{"Measure": "Fictional applications", "Count": value}]
    contract = {
        "pipeline_version": medallion_pipeline.VERSION,
        "inventory_id": safe["inventory_id"],
        "safety_receipt_sha256": sha(safety),
        "custody_receipt_sha256": sha(custody),
        "extraction_contract": {
            "extraction_version": medallion_xlsx.VERSION,
            "source_sha256": sha(source),
            "sheet_name": "Fictional",
            "header_row": 1,
            "columns": ["A", "B"],
            "data_rows": [2],
        },
        "projection_contract": {
            "contract_version": medallion_replay.VERSION,
            "source_sha256": sha(canonical(b1_rows)),
            "projection": {"measure": "Measure", "value": "Count"},
            "valid_from": None,
            "recorded_at": recorded_at,
        },
    }
    return source, safety, custody, contract


def build_report() -> dict[str, Any]:
    """Independently regenerate inputs and replay all layers and the checkpoint."""
    fixtures = [
        fictional_inputs("0007", "2026-08-30T00:00:00Z"),
        fictional_inputs("0009", "2026-08-31T00:00:00Z"),
    ]
    sources, safety_bank, custody_bank, contracts = {}, {}, {}, {}
    entries = []
    parent = None
    for source, safety, custody, contract in fixtures:
        sources[sha(source)] = source
        safety_bank[sha(safety)] = safety
        custody_bank[sha(custody)] = custody
        contracts[sha(canonical(contract))] = contract
        entry = medallion_pipeline.build_pipeline_event(
            source,
            safety,
            custody,
            contract,
            partition="FICTIONAL-REHEARSAL",
            valid_until=None,
            supersedes=parent,
        )
        parent = entry["history_event"]["event_id"]
        entries.append(entry)
    banks = sources, safety_bank, custody_bank, contracts
    previous = medallion_pipeline.replay_pipeline_history(entries[:1], *banks)
    current = medallion_pipeline.verify_pipeline_append_only(
        entries[:1], entries, *banks, previous_entries_sha256=previous["entries_sha256"]
    )
    events = [entry["history_event"] for entry in entries]
    b1_sources = {
        entry["pipeline"]["b1_rows_sha256"]: canonical(entry["pipeline"]["b1"]["rows"])
        for entry in entries
    }
    queries = {
        name: medallion_history.replay_partition(
            events, b1_sources, partition="FICTIONAL-REHEARSAL", recorded_as_of=instant
        )
        for name, instant in (
            ("before_correction", "2026-08-30T12:00:00Z"),
            ("after_correction", "2026-08-31T00:00:00Z"),
        )
    }
    modules = (
        medallion_pipeline,
        medallion_history,
        medallion_replay,
        medallion_xlsx,
        public_archive,
    )
    report = {
        "schema_version": "1.0",
        "rehearsal_id": "FICTIONAL-MEDALLION-LINEAGE-20260831-01",
        "synthetic": True,
        "current_remote_custody_verified": False,
        "custody_assertions": (
            "fictional test assertions; neither provider was contacted or retrieved"
        ),
        "valid_time": "unknown; recorded-only queries do not establish source validity",
        "implementation_sha256": {
            module.__name__: implementation_digest(module) for module in modules
        },
        "rehearsal_implementation_sha256": sha(Path(__file__).read_bytes()),
        "inputs": [
            {
                "source_sha256": sha(source),
                "source_bytes": len(source),
                "safety_receipt_sha256": sha(safety),
                "custody_receipt_sha256": sha(custody),
                "contract_sha256": sha(canonical(contract)),
            }
            for source, safety, custody, contract in fixtures
        ],
        "entries": entries,
        "history": current,
        "queries": queries,
        "append_checkpoint": {
            "previous_entries_sha256": previous["entries_sha256"],
            "new_entries_sha256": current["entries_sha256"],
            "full_linked_prefix_recomputed": True,
        },
        "authority": dict.fromkeys(
            (
                "network",
                "source_access",
                "rights_clearance",
                "publication",
                "release",
                "promotion",
                "gate_acceptance",
            ),
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
            print("fictional rehearsal report unavailable")
            return 1
        if actual != expected:
            print("fictional rehearsal report differs from recomputed evidence")
            return 1
        print("fictional rehearsal exact recomputation passed; no promotion authority")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(expected)
    print("fictional rehearsal report written; no provider retrieval or promotion authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
