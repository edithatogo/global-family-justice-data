#!/usr/bin/env python3
"""Independent path-B extractor for the bounded G2 exact-edition cohort.

This module intentionally shares no extraction functions with path A. It is
repository-owned reproducibility preparation, not independent assurance.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
CONTROLLED = ROOT / "data/raw/files/g2-controlled"


def row(**values: object) -> dict[str, object]:
    defaults = {
        "schema_version": "1.0",
        "component_values": {},
        "denominator_value": None,
        "denominator_definition": None,
        "period_start": None,
        "period_end": None,
        "time_basis": "source_defined",
        "suppression_or_disclosure_note": None,
        "extraction_uncertainty": "none",
        "notes": None,
    }
    defaults.update(values)
    return defaults


def extract() -> list[dict[str, object]]:
    fin = json.loads((CONTROLLED / "finland-observation.json").read_text())
    dims = fin["dimension"]
    labels = [
        next(iter(dims[name]["category"]["label"].values()))
        for name in ("District", "Case", "Stage at which the case was concluded", "Year", "Data")
    ]
    rows = [
        row(
            extracted_row_id="G2ROW-FINAPI-B",
            source_record_key="751e85bf60ca9f0bba36edc99e39daee3533154b0c531db7801f02d96f64d23a",
            candidate_id="FIN-API",
            source_id="FIN_STATFIN_KOIKRS",
            source_edition_id="FIN_STATFIN_KOIKRS_2004_2013_QUERY_2013",
            provenance_locator="JSON-stat2 dimensions: " + "; ".join(labels),
            measure_original=labels[-1],
            matter_type_original=labels[1],
            statistic_type="count",
            unit="Number",
            value=fin["value"][0],
            cohort_basis="source-defined total district and selected family-law case group",
            population_scope="source-defined total district",
        )
    ]
    sheet = openpyxl.load_workbook(
        CONTROLLED / "estonia-offences.xlsx", data_only=True, read_only=True
    )["2003-2025"]
    offence = next(
        (
            cells
            for cells in sheet.iter_rows(values_only=True)
            if cells[2] == "11. ptk. Süüteod perekonna ja alaealiste vastu"
        ),
        None,
    )
    if offence is None:
        raise SystemExit("path_b_failed:EST-XLSX:row_not_found")
    rows.append(
        row(
            extracted_row_id="G2ROW-ESTXLSX-B",
            source_record_key="ee9444102f3da1a0a85ffd58cec43c27840b2f45009fbbbf96e5ce434cfc3028",
            candidate_id="EST-XLSX",
            source_id="EST_JUSTDIGI_CRIME_2025",
            source_edition_id="EST_JUSTDIGI_REGISTERED_OFFENCES_2003_2025",
            provenance_locator=(
                "Workbook sheet 2003-2025; complete row label 11. ptk. "
                "Süüteod perekonna ja alaealiste vastu; column Z header 2025"
            ),
            measure_original=offence[2],
            matter_type_original=offence[2],
            statistic_type="count",
            unit="registered offences",
            value=offence[25],
            cohort_basis=(
                "source-defined registered offences at commencement of criminal proceedings"
            ),
            population_scope="source-defined Estonia offence series",
        )
    )
    with (CONTROLLED / "estonia-domestic-violence.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        dashboard = next(
            (
                item
                for item in csv.DictReader(handle, delimiter=";")
                if item["Type of crime"] == "Domestic violence" and item["Year"] == "2025"
            ),
            None,
        )
    if dashboard is None:
        raise SystemExit("path_b_failed:EST-DASH:row_not_found")
    rows.append(
        row(
            extracted_row_id="G2ROW-ESTDASH-B",
            source_record_key="579d24d37b839775825a7cf8c6f35255cd9adb01f23a0fab294cb5c0e00d81bc",
            candidate_id="EST-DASH",
            source_id="EST_JUSTDIGI_DOMESTIC_VIOLENCE",
            source_edition_id="EST_JUSTDIGI_DV_SNAPSHOT_20260525",
            provenance_locator="CSV row Type of crime=Domestic violence; Year=2025",
            measure_original="Domestic violence",
            matter_type_original="Domestic violence",
            statistic_type="count",
            unit="crimes",
            value=int(dashboard["Number of crimes"]),
            cohort_basis="source-defined domestic-violence series",
            population_scope="source-defined Estonia series",
        )
    )
    text = subprocess.check_output(
        ["pdftotext", "-layout", str(CONTROLLED / "south-africa-report-2024-25.pdf"), "-"],
        text=True,
        errors="replace",
    )
    page = next(
        (
            block
            for block in text.split("\f")
            if "89% of maintenance" in block and "87% of maintenance" in block
        ),
        None,
    )
    match = re.search(r"87% of maintenance", page or "")
    if match is None:
        raise SystemExit("path_b_failed:ZAF-PDF:value_not_found")
    rows.append(
        row(
            extracted_row_id="G2ROW-ZAFPDF-B",
            source_record_key="4922ef6dc1646c7a24dc658f8734794e9ab403e84f59698b9aa11df9ad63e461",
            candidate_id="ZAF-PDF",
            source_id="ZAF_DOJCD_ANNUAL_REPORT",
            source_edition_id="ZAF_DOJCD_ANNUAL_REPORT_2024_2025",
            provenance_locator=(
                "PDF page 51 (printed page 48), Main services and standards, "
                "Provision of Maintenance, Actual achievement column"
            ),
            measure_original=(
                "maintenance matters finalised within 90 days from date of "
                "proper service of process"
            ),
            matter_type_original="Provision of Maintenance",
            statistic_type="percentage",
            unit="percent",
            value=int(match.group(0)[:2]),
            cohort_basis="source-defined maintenance matters with proper service of process",
            population_scope=(
                "beneficiaries listed by source: children, single parents, "
                "grandparents and other parents"
            ),
        )
    )
    return rows


if __name__ == "__main__":
    print(json.dumps(extract(), ensure_ascii=False))
