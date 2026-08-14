# Frozen G2 four-row extraction instructions

Packet ID: `G2PKT-REAL-PILOT-20260815-01`

Each assigned analyst agent must inspect the four preserved source editions
directly and produce exactly four JSON objects validating against
`schemas/g2_extraction_row.schema.json`. Do not inspect any prior exploratory
extraction, the other formal extraction, comparator output or panel synthesis.

Procedural blinding is required. The shared single-person repository cannot
establish cognitive or institutional independence, and no such claim may be
made.

## General rules

- Transcribe source-native language and semantics. Do not harmonise, translate
  into a common denominator or infer missing facts.
- Use the fixed `source_record_key` below. The extractor-specific
  `extracted_row_id` must be unique and may differ between runs.
- Record the headline statistic in `value` and the named supporting numeric
  facts in `component_values`. Do not add unrequested source facts.
- Use `denominator_value` only where the source reports a denominator or the
  displayed rate has an explicit source denominator. Never reverse-engineer a
  denominator from a rounded percentage.
- Preserve source ambiguity in `extraction_uncertainty` and `notes`. Do not
  resolve an internal inconsistency by preference or arithmetic correction.
- Use ISO dates only when the source or its stated reporting period establishes
  them. Otherwise use `null` and explain the uncertainty.
- All four rows remain private evidence preparation and quarantined from
  comparison, publication and release.

## Frozen targets

### AUS-D1-CLEARANCE-2024-25

- `source_record_key`:
  `fef623eab55f14f9bbd888287ddf37de464ed287d2af5ac8f0d02150e0bf1b80`
- candidate/source/edition: `AUS`, `AUS-FCFCOA-AR`,
  `ED-AUS-FCFCOA-ANNUAL-2024-25`
- local edition:
  `data/raw/files/FCFCOA-ANNUAL-2024-25/annual-report-2024-25.pdf`
- locator target: PDF p.102 / printed p.84, Figure 3.3.2(a), with the
  surrounding clearance explanation.
- headline: reported Division 1 final-order-application clearance percentage.
- required component keys: `transferred_count`, `finalised_count`,
  `pending_count`.
- required semantics: Division 1 transferred/finalised population and the
  source's treatment of transferred applications.

### USA-MN-FAMILY-CLEARANCE-FY24

- `source_record_key`:
  `c0f8ec4b54648507110f35d5d4307213104ed31c412faa9225a95bcb38e6f89d`
- candidate/source/edition: `USA-MN`, `USA-MN-MJB`,
  `ED-USA-MN-MJB-PERF-2024`
- local edition:
  `data/raw/files/USA-MN-MJB/ACQ-USA-MN-MJB-20260814T144054Z-32931494/Annual-Report-2024-Performance-Measures.pdf`
- locator target: PDF/printed p.14, Table 4, with the surrounding clearance
  definition.
- headline: statewide Family clearance percentage for FY24.
- required component keys: none; use `{}`.
- required semantics: source definition of clearance and the Family case-group
  population.

### BRA-PROTECTIVE-MEASURES-2026-04-30

- `source_record_key`:
  `164cfa1e58300975fbe0a49e0cd223079d57574e1b5961026d06d073a7baf38a`
- candidate/source/edition: `BRA`, `BRA-CNJ-DATAJUD`,
  `ED-BRA-CNJ-JUSTICA-2026`
- local edition:
  `data/raw/files/CNJ-JUSTICA-2026/justica-em-numeros-2026.pdf`
- locator target: PDF/printed p.588, Figure 528.
- headline: displayed total protective measures in 2026 through the displayed
  snapshot date.
- required component keys: `granted_count`, `denied_count`, `revoked_count`,
  `extended_count`, `police_authority_granted_count`,
  `police_authority_revoked_count`.
- required semantics: partial-year dynamic-dashboard snapshot; protective
  measures rather than cases or people.

### ZAF-MAINTENANCE-90D-2024-25

- `source_record_key`:
  `bffeecd35b755dd473cb450f7c19a9c158e54e43aba88369686b4bb5f78e1243`
- candidate/source/edition: `ZAF`, `ZAF-JUD-ANNUAL`,
  `ED-ZAF-JUDICIARY-ANNUAL-2024-25`
- local edition:
  `data/raw/files/SA-JUDICIARY-2024-25/annual-judiciary-report-2024-25.pdf`
- locator targets: PDF p.52 / printed p.50, Table 20; PDF p.90 / printed
  p.88, Annexure C indicator 3.
- headline: reported percentage finalised within the table's stated clock.
- required component keys: `within_clock_count`, `exceeding_clock_count`,
  `reported_total_count`.
- required semantics: proper-service-conditioned denominator, incomplete court
  coverage, any arithmetic mismatch and the table/Annexure clock wording.

## Output boundary

Return or write only the four row objects and a receipt recording the packet
digest, instruction digest, source-manifest digests, start/completion times,
role, agent session, procedural-blinding declaration, warnings and limitations.
Do not produce a gate, rights, methods, publication or release decision.
