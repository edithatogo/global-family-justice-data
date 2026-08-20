# G2 proposed real-pilot intake — 2026-08-21

## Scope and result

This is a metadata-only selection of four exact official locations for a
future real-pilot campaign. The locations were selected for acquisition-route
diversity: API, spreadsheet, HTML/dashboard and PDF/manual. No source endpoint
or file was requested, downloaded, rendered, or inspected during the
repository intake check.

The offline candidate-intake guard passed: four candidates, zero cumulative
exposure overlaps and zero source-content accesses. That result is preparation
only. It does not verify that a location remains live, authenticate a source,
clear rights, or authorize acquisition.

The four locations were observed while preparing this intake. They are therefore
not candidates for a project-unseen holdout. They are proposed only for a
separately authorized known-source real-pilot route; any generalisation claim
would still require a fresh unseen-edition design.

## Proposed locations

| Route | Candidate ID | Exact location | Exact-edition rule |
| --- | --- | --- | --- |
| API | `G2-API-BRA-TJSP-2026` | `https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search` | Freeze the request body, endpoint, API-key mechanism, retrieval time and response digest before use. |
| Spreadsheet | `G2-ODS-GBR-EAW-2026Q1` | `https://assets.publishing.service.gov.uk/media/6a3b9c9230b491f55b3c482e/Family_Court_Tables__Jan-Mar_2026_.ods` | Freeze the retrieved ODS bytes and publication date. |
| Dashboard | `G2-DASH-GBR-EAW-2026Q1` | `https://app.powerbi.com/view?r=eyJrIjoiYzgwOWFjN2UtNjhjMC00MWFlLTg1NTItM2U0ODNkMGQyMGI4IiwidCI6ImM2ODc0NzI4LTcxZTYtNDFmZS1hOWUxLTJlOGMzNjc3NmFkOCIsImMiOjh9` | Freeze access time, visible filters, dashboard version/state and exported capture digest. |
| PDF/manual | `G2-PDF-AUS-FCFCOA-2024-25` | `https://www.fcfcoa.gov.au/sites/default/files/2025-12/federal_circuit_and_family_court_of_australia_annual_reports_2024-25_v2_web.pdf` | Freeze the retrieved PDF bytes, page locators and edition metadata. |

## Bound receipt

- Candidate intake:
  `data/methods/g2/G2PROPOSED-REAL-PILOT-20260821-01/intake/candidate-intake.json`
  — SHA-256 `d3ee890207b4a58d8b5808d43b78dbc0da47ea87eb46d5f0a304c26f96878ed5`.
- Offline preparation receipt:
  `data/methods/g2/G2PROPOSED-REAL-PILOT-20260821-01/intake/preparation-receipt.json`.
- Current exposure ledger: SHA-256
  `e43628df4592ab3386ad811d0871532d2fe40e6af7f169455994447572b8242d`.

## Required before any source processing

The source-specific rights/privacy/security screen, resource cap, access
controls, exact API request definition and stopping rules must be bound into
one campaign packet. A single grouped owner authorization can then cover its
bounded acquisition, private processing, role-separated review and factual
evidence production. No publication, release or G2 decision follows from that
authorization.
