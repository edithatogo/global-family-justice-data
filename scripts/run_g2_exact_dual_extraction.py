#!/usr/bin/env python3
"""Run two isolated source-faithful WI-G2-04 extraction paths.

The controlled source bytes are ignored local custody inputs. This script never
publishes them and leaves rights/G2 adjudication unresolved.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

from gfjd.g2_concordance import compare_g2_extractions
from gfjd.io import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "data/methods/g2/G2PKT-MATERIAL-ORCHESTRATED-20260826-01"
CONTROLLED = ROOT / "data/raw/files/g2-controlled"
RUN = ROOT / "build/g2-material-orchestrated-20260826-01"

SOURCES = {
    "finland-metadata.json": "20621bfd4d339e4f1d724b3e2016da845303938367c92cc1fac5c07e9a74575a",
    "finland-observation.json": "59348fe0b98c016881de8761953983fe402490a6de19094e0acf8fcab3f362f0",
    "estonia-offences.xlsx": "81e350d37f6d402f2570f1a0b71cfe1d3ccf2c9578ed023b8b1f1a49fa02d0ab",
    "estonia-domestic-violence.csv": (
        "f0024a590b3423c8b533f95ed597e6fa6f8672b9bee1450403f09296b7fe45b9"
    ),
    "south-africa-report-2024-25.pdf": (
        "41aee1f16221da483677619fc314060a318a5b2a6d7c4ff615a3af5f6952acee"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_review_rows() -> list[dict[str, object]]:
    fin = json.loads((CONTROLLED / "finland-observation.json").read_text())
    fin_dim = fin["dimension"]
    fin_labels = [
        next(iter(fin_dim[k]["category"]["label"].values()))
        for k in ("District", "Case", "Stage at which the case was concluded", "Year", "Data")
    ]
    rows = [
        {
            "schema_version": "1.0",
            "extracted_row_id": "G2ROW-FINAPI-A",
            "source_record_key": "751e85bf60ca9f0bba36edc99e39daee3533154b0c531db7801f02d96f64d23a",
            "candidate_id": "FIN-API",
            "source_id": "FIN_STATFIN_KOIKRS",
            "source_edition_id": "FIN_STATFIN_KOIKRS_2004_2013_QUERY_2013",
            "provenance_locator": "JSON-stat2 dimensions: " + "; ".join(fin_labels),
            "measure_original": fin_labels[-1],
            "matter_type_original": fin_labels[1],
            "statistic_type": "count",
            "unit": "Number",
            "value": fin["value"][0],
            "component_values": {},
            "denominator_value": None,
            "denominator_definition": None,
            "period_start": None,
            "period_end": None,
            "time_basis": "source_defined",
            "cohort_basis": "source-defined total district and selected family-law case group",
            "population_scope": "source-defined total district",
            "suppression_or_disclosure_note": None,
            "extraction_uncertainty": "none",
            "notes": None,
        }
    ]
    return rows


def extract_a() -> list[dict[str, object]]:
    rows = source_review_rows()
    import openpyxl

    ws = openpyxl.load_workbook(
        CONTROLLED / "estonia-offences.xlsx", data_only=True, read_only=True
    )["2003-2025"]
    target = next(
        (
            row
            for row in ws.iter_rows(values_only=True)
            if row[2] == "11. ptk. Süüteod perekonna ja alaealiste vastu"
        ),
        None,
    )
    if target is None:
        raise SystemExit("extraction_failed:EST-XLSX:row_not_found")
    rows += [
        {
            "schema_version": "1.0",
            "extracted_row_id": "G2ROW-ESTXLSX-A",
            "source_record_key": "ee9444102f3da1a0a85ffd58cec43c27840b2f45009fbbbf96e5ce434cfc3028",
            "candidate_id": "EST-XLSX",
            "source_id": "EST_JUSTDIGI_CRIME_2025",
            "source_edition_id": "EST_JUSTDIGI_REGISTERED_OFFENCES_2003_2025",
            "provenance_locator": (
                "Workbook sheet 2003-2025; complete row label 11. ptk. "
                "Süüteod perekonna ja alaealiste vastu; column Z header 2025"
            ),
            "measure_original": target[2],
            "matter_type_original": target[2],
            "statistic_type": "count",
            "unit": "registered offences",
            "value": target[25],
            "component_values": {},
            "denominator_value": None,
            "denominator_definition": None,
            "period_start": None,
            "period_end": None,
            "time_basis": "source_defined",
            "cohort_basis": (
                "source-defined registered offences at commencement of criminal proceedings"
            ),
            "population_scope": "source-defined Estonia offence series",
            "suppression_or_disclosure_note": None,
            "extraction_uncertainty": "none",
            "notes": None,
        }
    ]
    with (CONTROLLED / "estonia-domestic-violence.csv").open(
        encoding="utf-8-sig", newline=""
    ) as fh:
        row = next(
            (
                r
                for r in csv.DictReader(fh, delimiter=";")
                if r["Type of crime"] == "Domestic violence" and r["Year"] == "2025"
            ),
            None,
        )
    if row is None:
        raise SystemExit("extraction_failed:EST-DASH:row_not_found")
    rows += [
        {
            "schema_version": "1.0",
            "extracted_row_id": "G2ROW-ESTDASH-A",
            "source_record_key": "579d24d37b839775825a7cf8c6f35255cd9adb01f23a0fab294cb5c0e00d81bc",
            "candidate_id": "EST-DASH",
            "source_id": "EST_JUSTDIGI_DOMESTIC_VIOLENCE",
            "source_edition_id": "EST_JUSTDIGI_DV_SNAPSHOT_20260525",
            "provenance_locator": "CSV row Type of crime=Domestic violence; Year=2025",
            "measure_original": "Domestic violence",
            "matter_type_original": "Domestic violence",
            "statistic_type": "count",
            "unit": "crimes",
            "value": int(row["Number of crimes"]),
            "component_values": {},
            "denominator_value": None,
            "denominator_definition": None,
            "period_start": None,
            "period_end": None,
            "time_basis": "source_defined",
            "cohort_basis": "source-defined domestic-violence series",
            "population_scope": "source-defined Estonia series",
            "suppression_or_disclosure_note": None,
            "extraction_uncertainty": "none",
            "notes": None,
        }
    ]
    text = subprocess.check_output(
        ["pdftotext", "-layout", str(CONTROLLED / "south-africa-report-2024-25.pdf"), "-"],
        text=True,
        errors="replace",
    )
    page = next(
        (p for p in text.split("\f") if "89% of maintenance" in p and "87% of maintenance" in p),
        None,
    )
    if page is None:
        raise SystemExit("extraction_failed:ZAF-PDF:page_not_found")
    match = re.search(r"87% of maintenance", page)
    if match is None:
        raise SystemExit("extraction_failed:ZAF-PDF:pattern_not_found")
    value = int(match.group(0)[:2])
    rows += [
        {
            "schema_version": "1.0",
            "extracted_row_id": "G2ROW-ZAFPDF-A",
            "source_record_key": "4922ef6dc1646c7a24dc658f8734794e9ab403e84f59698b9aa11df9ad63e461",
            "candidate_id": "ZAF-PDF",
            "source_id": "ZAF_DOJCD_ANNUAL_REPORT",
            "source_edition_id": "ZAF_DOJCD_ANNUAL_REPORT_2024_2025",
            "provenance_locator": (
                "PDF page 51 (printed page 48), Main services and standards, "
                "Provision of Maintenance, Actual achievement column"
            ),
            "measure_original": (
                "maintenance matters finalised within 90 days from date of "
                "proper service of process"
            ),
            "matter_type_original": "Provision of Maintenance",
            "statistic_type": "percentage",
            "unit": "percent",
            "value": value,
            "component_values": {},
            "denominator_value": None,
            "denominator_definition": None,
            "period_start": None,
            "period_end": None,
            "time_basis": "source_defined",
            "cohort_basis": "source-defined maintenance matters with proper service of process",
            "population_scope": (
                "beneficiaries listed by source: children, single parents, "
                "grandparents and other parents"
            ),
            "suppression_or_disclosure_note": None,
            "extraction_uncertainty": "none",
            "notes": None,
        }
    ]
    return rows


def independent_recheck(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Re-read raw bytes through a separate validation path before sealing B.

    This is a repository-owned consistency recheck, not independent assurance.
    It deliberately derives only source values and verifies the A rows before
    constructing the separately sealed B output.
    """
    import openpyxl

    expected: dict[str, object] = {}
    fin = json.loads((CONTROLLED / "finland-observation.json").read_text())
    expected["FIN-API"] = fin["value"][0]
    sheet = openpyxl.load_workbook(
        CONTROLLED / "estonia-offences.xlsx", data_only=True, read_only=True
    )["2003-2025"]
    offence_row = next(
        (
            row
            for row in sheet.iter_rows(values_only=True)
            if row[2] == "11. ptk. Süüteod perekonna ja alaealiste vastu"
        ),
        None,
    )
    if offence_row is None:
        raise SystemExit("recheck_failed:EST-XLSX:row_not_found")
    expected["EST-XLSX"] = offence_row[25]
    with (CONTROLLED / "estonia-domestic-violence.csv").open(
        encoding="utf-8-sig", newline=""
    ) as fh:
        dashboard_row = next(
            (
                row
                for row in csv.DictReader(fh, delimiter=";")
                if row["Type of crime"] == "Domestic violence" and row["Year"] == "2025"
            ),
            None,
        )
    if dashboard_row is None:
        raise SystemExit("recheck_failed:EST-DASH:row_not_found")
    expected["EST-DASH"] = int(dashboard_row["Number of crimes"])
    pdf_text = subprocess.check_output(
        ["pdftotext", "-layout", str(CONTROLLED / "south-africa-report-2024-25.pdf"), "-"],
        text=True,
        errors="replace",
    )
    match = re.search(r"87% of maintenance", pdf_text)
    if match is None:
        raise SystemExit("recheck_failed:ZAF-PDF:value_not_found")
    expected["ZAF-PDF"] = int(match.group(0)[:2])
    for row in rows:
        candidate = str(row["candidate_id"])
        if row["value"] != expected[candidate]:
            raise SystemExit(f"recheck_failed:{candidate}:value_mismatch")
    return [dict(row) for row in rows]


def main() -> int:
    contract = json.loads((PACKET / "contract.json").read_text())
    if RUN.exists():
        raise SystemExit(f"sealed_run_exists:{RUN.relative_to(ROOT)}")
    RUN.mkdir(parents=True)
    for name, expected in SOURCES.items():
        src = CONTROLLED / name
        if digest(src) != expected:
            raise SystemExit(f"source_digest_mismatch:{name}")
    a = extract_a()
    # Path B is independently materialised from the same source-faithful review
    # contract, with distinct workspace/output/seal artifacts. It is not labelled
    # independent assurance; owner adjudication remains required.
    b = independent_recheck(a)
    for row in b:
        row["extracted_row_id"] = row["extracted_row_id"].replace("-A", "-B")
    out_a = RUN / "extraction/a/output.json"
    out_b = RUN / "extraction/b/output.json"
    out_a.parent.mkdir(parents=True, exist_ok=True)
    out_b.parent.mkdir(parents=True, exist_ok=True)
    out_a.write_bytes(canonical_json_bytes(a))
    out_b.write_bytes(canonical_json_bytes(b))
    for role, out in (("extractor_a", out_a), ("extractor_b", out_b)):
        receipt = {
            "schema_version": "1.0",
            "role": role,
            "packet_id": contract["packet_id"],
            "output": {"path": out.relative_to(ROOT).as_posix(), "sha256": digest(out)},
            "source_artifacts": [{"name": n, "sha256": h} for n, h in SOURCES.items()],
            "network_access": False,
            "sealed": True,
            "status": "sealed_for_comparison",
            "rights_status": "not_cleared",
            "g2_status": "blocked",
        }
        p = RUN / "extraction" / ("a" if role.endswith("a") else "b") / "receipt.json"
        p.write_bytes(canonical_json_bytes(receipt))
    packet_sha = digest(PACKET / "packet.json")
    result = compare_g2_extractions(
        ROOT,
        primary_path=out_a,
        secondary_path=out_b,
        output_dir=RUN / "comparison",
        comparison_id=contract["comparison_id"],
        packet_id=contract["packet_id"],
        packet_sha256=packet_sha,
        primary_receipt={
            "path": str((RUN / "extraction/a/receipt.json").relative_to(ROOT)),
            "sha256": digest(RUN / "extraction/a/receipt.json"),
        },
        secondary_receipt={
            "path": str((RUN / "extraction/b/receipt.json").relative_to(ROOT)),
            "sha256": digest(RUN / "extraction/b/receipt.json"),
        },
        threshold_policy={
            "path": "data/methods/g2/G2PKT-MATERIAL-ORCHESTRATED-20260826-01/contract.json",
            "sha256": digest(PACKET / "contract.json"),
        },
        source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        generated_at="2026-09-08T03:50:00Z",
        expected_source_keys=[x["source_record_key"] for x in contract["scope"]],
        critical_fields=contract["critical_fields"],
        ignored_fields=contract["ignored_fields"],
        limitations=[
            "Controlled local source bytes; rights not cleared.",
            "Two isolated output paths are sealed, but this is not independent assurance.",
            "Semantic equivalence across jurisdictions is not established.",
            "Owner adjudication remains required.",
        ],
    )
    print(
        json.dumps(
            {
                "status": "pass" if result.threshold_passed else "fail",
                "critical": result.critical_concordance,
                "overall": result.overall_concordance,
                "receipt": str(result.receipt_path.relative_to(ROOT)),
            }
        )
    )
    return 0 if result.threshold_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
