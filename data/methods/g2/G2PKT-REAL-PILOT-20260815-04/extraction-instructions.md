# Frozen G2 packet-04 owner-amended atomic extraction instructions

Packet ID: `G2PKT-REAL-PILOT-20260815-04`

Each assigned analyst agent must inspect the four preserved exact source
editions directly and produce exactly four JSON objects validating against
`schemas/g2_atomic_extraction_row.schema.json`, the base rules in
`config/g2_atomic_semantic_contract.json`, and the owner-approved mappings and
uncertainty rule in `config/g2_atomic_methods_amendment_packet04.json`.

Do not inspect any packet 01, 02 or 03 extraction output, receipt, difference,
comparison or advisory report. Do not inspect any packet-04 output belonging to
the other extraction role. Procedural role separation does not establish
cognitive, institutional, specialist or human independence.

## Exact normalization

For every field ending `_source` or `_quote`:

1. transcribe only instruction-bounded source text;
2. normalize Unicode to NFC;
3. replace every whitespace run, including line breaks, with one ASCII space;
4. trim leading and trailing whitespace;
5. preserve source case, punctuation, spelling and Unicode punctuation;
6. do not paraphrase, translate, repair or append interpretation.

Use `null` only where the row schema permits it and the contract says the field
is absent or not stated. Record canonical codes exactly as frozen in the base
contract. Codes classify the target but do not alter source quotation.

## Owner-required packet-04 mappings

The following critical values are mandatory:

- BRA `coverage_limitation_quote`: `Tribunal Todos Grau Todos Órgão Julgador Todos Originário Todos Natureza Todos UF, Município Todos Formato Todos`
- BRA `locator_object_source`: `Figura 528 - Dados de processos de violência doméstica e familiar contra a mulher`
- BRA `measure_label_source`: `Medidas Protetivas em 2026`
- BRA `period_label_source`: `2026`
- BRA `series_label_source`: `Total`
- BRA `extraction_uncertainty`: `none`
- USA-MN `domain_label_source`: `Timeliness`
- AUS `extraction_uncertainty`: `unresolved`

For all four rows, `extraction_uncertainty` is deterministic:

- use `none` when every required source occurrence is legible and
  `ambiguity_codes` is empty;
- use `unresolved` when a required ambiguity code preserves a source conflict
  that this packet does not resolve;
- `low` and `material` are unavailable.

This yields AUS `unresolved`, USA-MN `none`, BRA `none` and ZAF `unresolved`.
If the source or bound ambiguity contract does not support one of these values,
fail the run; do not infer, waive or substitute.

The packet-03 corrected mappings not repeated above remain fixed by
`config/g2_atomic_boundary_correction_packet03.json`: the exact AUS
matter/series labels, USA-MN clock/series labels, BRA section heading, and ZAF
clock/object/measure labels.

## Date rule

Populate `period_start` or `period_end` only if the exact edition states that
specific calendar date. A year, fiscal-year label or annual-report title alone
does not establish an ISO boundary. When no exact date is stated, use `null` and
`not_stated`. Always preserve the source period label in `period_label_source`.
`packet_bound_calendar` is unavailable.

## Numeric and denominator rules

- Transcribe the headline statistic exactly as displayed.
- Transcribe exactly the component keys named by the base contract.
- Do not recalculate, reverse-engineer or repair a source number.
- Populate a denominator only when displayed for the selected target.
- Preserve source inconsistencies in the ambiguity fields.
- Codes, exact excerpts, facts, components, mappings, uncertainty and
  quarantine are critical and require exact conformance.

## Frozen four-row targets

### AUS-D1-CLEARANCE-2024-25

- edition: `ED-AUS-FCFCOA-ANNUAL-2024-25`
- bytes: `data/raw/files/FCFCOA-ANNUAL-2024-25/annual-report-2024-25.pdf`
- locator: PDF p.102 / printed p.84, section 3.3.2 and Figure 3.3.2(a)
- disposition: `hard_quarantine`; preserve the ratio-order conflict

### USA-MN-FAMILY-CLEARANCE-FY24

- edition: `ED-USA-MN-MJB-PERF-2024`
- bytes: `data/raw/files/USA-MN-MJB/ACQ-USA-MN-MJB-20260814T144054Z-32931494/Annual-Report-2024-Performance-Measures.pdf`
- locators: PDF/printed p.12 outer section 3.2 `Timeliness`; PDF/printed p.14
  subsection 3.2.2 and Table 4
- disposition: `quarantine`

### BRA-PROTECTIVE-MEASURES-2026-04-30

- edition: `ED-BRA-CNJ-JUSTICA-2026`
- bytes: `data/raw/files/CNJ-JUSTICA-2026/justica-em-numeros-2026.pdf`
- locator: PDF/printed p.588, Figure 528
- disposition: `quarantine`; preserve partial-year protective-measure semantics

### ZAF-MAINTENANCE-90D-2024-25

- edition: `ED-ZAF-JUDICIARY-ANNUAL-2024-25`
- bytes: `data/raw/files/SA-JUDICIARY-2024-25/annual-judiciary-report-2024-25.pdf`
- locators: PDF p.52 / printed p.50, Table 20; PDF p.90 / printed p.88,
  Annexure C indicator 3
- disposition: `hard_quarantine`; preserve component-total, clock and coverage
  conflicts

## Output and receipt boundary

Write only the four-row JSON array and a receipt validating against
`schemas/g2_extraction_run.schema.json`. The receipt must bind this packet,
instructions, atomic row schema, source manifests and output digest; record UTC
timestamps, role/session, warnings, limitations and procedural blinding. Do not
make a methods, rights, gate, publication or release decision.
