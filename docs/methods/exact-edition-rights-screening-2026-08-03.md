# Exact-edition rights screening

**Screening date:** 2026-08-03 (Australia/Sydney)  
**Policy:** government-origin material is presumptively reusable only where no contrary term, third-party right, database right, or agreement applies. This screen is not legal advice and does not itself grant permission.

## Findings

| Source | Edition/material screened | Evidence | Finding | Disposition |
|---|---|---|---|---|
| AUS-FCFCOA-AR | FCFCOA annual-report pages/PDFs | [FCFCOA AI practice direction](https://www.fcfcoa.gov.au/pd/pd-ai); [FCFCOA publication example](https://www.fcfcoa.gov.au/ko/node/8138) | Court guidance requires users to respect IP rights and identify original sources. A current annual-report-specific licence was not established; third-party images/artwork may be present. | **metadata/citation only**; exact-edition permission or licence evidence required before byte redistribution |
| BRA-CNJ-DATAJUD | DataJud public API and derived responses | [CNJ API terms (PDF)](https://formularios.cnj.jus.br/wp-content/uploads/2023/05/Termos-de-uso-api-publica-V1.1.pdf); [CNJ DataJud overview](https://www.cnj.jus.br/sistemas/datajud/sobre/) | API use is subject to accepted terms. The terms prohibit modifying, distributing, selling, or commercially exploiting the API or derived information without prior written CNJ authorisation, and protect confidential data. | **metadata/API citation only**; no redistribution of API responses or derived extracts until written authorisation or a later exact-edition-compatible permission is recorded |
| SWE-DOMSTOLSVERKET | Official court-statistics data (not report artwork) | [Swedish official court statistics](https://www.domstol.se/domstolsverket/om-sveriges-domstolar/statistik-styrning-och-utveckling/statistik/officiell-domstolsstatistik/) | The page states official statistics may be used free of charge. That statement does not establish rights for the exact XLSX/CSV edition, report layout, artwork, or third-party content. | **data candidate, edition check open**; preserve citation and edition hash, but do not redistribute report/PDF/artwork until edition terms are captured |
| ZAF-JUD-ANNUAL | Judiciary annual reports and performance PDFs | [South African Judiciary annual-report example](https://www.judiciary.org.za/index.php/judicial-service-commission/jsc-annual-reports/annual?download=11057%3Ajsc-annual-report-2020-2021); [Judiciary court-roll terms example](https://www.judiciary.org.za/landcourt/index.php/court-rolls) | Official-hosted pages contain explicit copyright notices; at least some publications identify third-party media copyright and “all rights reserved”. No general reuse licence for the exact annual-report editions was found. | **metadata/citation only**; permission/licence and third-party component review required |

## Clear edition

| Source edition | Evidence | Reuse status | Required attribution and conditions |
|---|---|---|---|
| `ED-GBR-EAW-MOJ-FCSQ-2026Q1` | [Family Court Statistics Quarterly collection](https://www.gov.uk/government/collections/family-court-statistics-quarterly); locally retained manifest `ACQ-GBR-EAW-MOJ-FAMILY-Q-20260731T222608Z-8EA47087` | **Reusable with attribution** under Open Government Licence v3, except material identified as otherwise licensed | Attribute Ministry of Justice; link the canonical publication; retain edition ID and SHA-256; preserve any third-party exclusions; do not imply endorsement; clearance applies only to this exact 2026 Q1 archive and not other editions or derived taxonomy decisions |

## Ambiguous/restricted editions: metadata-only reuse

The following editions may be referenced publicly as metadata and citations, but are **not** cleared for redistribution of source bytes, screenshots, report layouts, API responses, or derived extracts:

| Source | Safe reuse | Attribution and conditions |
|---|---|---|
| AUS-FCFCOA annual reports | Title, publisher, canonical URL, edition/date, retrieval date, checksum and descriptive notes | Credit FCFCOA; link the official edition; do not reproduce pages, images, logos or third-party material; do not imply a licence |
| BRA CNJ DataJud | API name, endpoint documentation, edition/query metadata and citation | Credit CNJ; link the API terms; do not redistribute responses or derived extracts; comply with confidentiality and API-use restrictions |
| SWE Domstolsverket 2025 workbook/report | Statistical-series metadata, definitions, edition ID, URL, retrieval date and checksum | Credit Domstolsverket; link the official statistics page; do not redistribute workbook/report/artwork until exact-edition terms are recorded |
| ZAF Judiciary annual reports | Title, publisher, canonical URL, edition/date, retrieval date, checksum and descriptive notes | Credit the Judiciary; preserve third-party copyright notices; do not reproduce report bytes, photographs, artwork or layouts |

This is a citation/metadata permission boundary, not a source-content licence. Any reuse beyond these fields requires an exact-edition licence, permission, or accountable rights decision.

## Decision rules applied

1. A public URL or government origin is not a redistribution licence.
2. A free-use statement for official statistics is scoped to the stated statistical material; it does not automatically cover reports, artwork, logos, tables supplied by third parties, or bulk/API extracts.
3. Any explicit API term, signed agreement, or “all rights reserved” notice controls over the project presumption.
4. Ambiguous database-rights, privacy, or edition terms remain quarantined. The source queue and release boundary must remain unchanged until an accountable rights decision records the exact edition, permitted acts, attribution, and exclusions.

## Result

The queued AUS, BRA, SWE and ZAF sources are not cleared for byte redistribution by this screen. The one clear edition is the already acquired `ED-GBR-EAW-MOJ-FCSQ-2026Q1`, which is reusable with the conditions above. The screen supplies source-backed exception evidence and narrows the next authority actions: obtain exact-edition licence/permission for AUS and ZAF, written CNJ authorisation for BRA, and capture the precise Swedish edition terms plus a separation of statistical data from report/artwork content.
