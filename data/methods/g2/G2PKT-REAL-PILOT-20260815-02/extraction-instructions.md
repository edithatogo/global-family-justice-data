# Frozen G2 packet-02 atomic extraction instructions

Packet ID: `G2PKT-REAL-PILOT-20260815-02`

Each assigned analyst agent must inspect the four preserved exact source
editions directly and produce exactly four JSON objects validating against
`schemas/g2_atomic_extraction_row.schema.json` and the rules in
`config/g2_atomic_semantic_contract.json`.

Do not inspect packet 01 extraction outputs, receipts, differences, advisory
reports or any packet-02 output belonging to the other extraction role.
Procedural role separation does not establish cognitive, institutional,
specialist or human independence.

## Exact normalization

For every field ending `_source` or `_quote`:

1. transcribe only the instruction-bounded source text;
2. normalize Unicode to NFC;
3. replace every whitespace run, including line breaks, with one ASCII space;
4. trim leading and trailing whitespace;
5. preserve source case, punctuation, spelling and Unicode punctuation;
6. do not paraphrase, translate, repair or append interpretation.

Use `null` only where the row schema permits it and the contract boundary says
the field is absent or not stated. Record owner-supplied canonical codes exactly
as frozen in the atomic contract; codes classify the target but do not alter the
source quotation.

## Date rule

Populate `period_start` or `period_end` only if the exact edition states that
specific calendar date. A year, fiscal-year label or annual-report title alone
does not establish an ISO boundary. When no exact date is stated, use `null` and
`not_stated`. Always preserve the source period label in `period_label_source`.
`packet_bound_calendar` is unavailable in this packet.

## Numeric and denominator rules

- Transcribe the headline statistic into `value` exactly as displayed.
- Transcribe exactly the component keys named by the atomic contract; do not add
  or omit a key.
- Do not recalculate, reverse-engineer or repair a source number.
- Use `denominator_value` only when the exact edition displays the denominator
  selected by the target. Preserve any inconsistency in the ambiguity fields.
- Codes, exact excerpts, numeric values and required component keys are all
  critical and must compare exactly.

## Frozen four-row targets

### AUS-D1-CLEARANCE-2024-25

- edition: `ED-AUS-FCFCOA-ANNUAL-2024-25`
- bytes:
  `data/raw/files/FCFCOA-ANNUAL-2024-25/annual-report-2024-25.pdf`
- locator: PDF p.102 / printed p.84, section 3.3.2 and Figure 3.3.2(a)
- headline: displayed Division 1 final-order-application clearance percentage
- components: transferred, finalised and pending counts named by the contract
- exact excerpts: use the contract boundaries for cohort, denominator and the
  displayed-percentage/ratio-order conflict
- date rule: the pending sentence explicitly states the period end; the start
  is not stated as an exact date in the bounded source text
- disposition: `hard_quarantine`; do not resolve the ratio-order conflict

### USA-MN-FAMILY-CLEARANCE-FY24

- edition: `ED-USA-MN-MJB-PERF-2024`
- bytes:
  `data/raw/files/USA-MN-MJB/ACQ-USA-MN-MJB-20260814T144054Z-32931494/Annual-Report-2024-Performance-Measures.pdf`
- locator: PDF/printed p.14, section 3.2.2 and Table 4
- headline: statewide Family clearance percentage for FY24
- components: none; use `{}`
- exact excerpts: use the contract boundary for the clearance definition
- date rule: retain `FY24`; the bounded source text states no exact ISO dates
- disposition: `quarantine`

### BRA-PROTECTIVE-MEASURES-2026-04-30

- edition: `ED-BRA-CNJ-JUSTICA-2026`
- bytes: `data/raw/files/CNJ-JUSTICA-2026/justica-em-numeros-2026.pdf`
- locator: PDF/printed p.588, Figure 528
- headline: displayed total protective measures for the displayed 2026
  snapshot
- components: the six status cards named by the contract
- exact excerpts: transcribe the contract-bounded Portuguese labels and filter
  text from the embedded dashboard figure; do not translate
- date rule: the displayed through-date establishes the period end; the year
  label alone does not establish an exact period start
- disposition: `quarantine`; preserve protective-measure and partial-year
  semantics, not cases, people or an annual total

### ZAF-MAINTENANCE-90D-2024-25

- edition: `ED-ZAF-JUDICIARY-ANNUAL-2024-25`
- bytes:
  `data/raw/files/SA-JUDICIARY-2024-25/annual-judiciary-report-2024-25.pdf`
- locators: PDF p.52 / printed p.50, Table 20; PDF p.90 / printed p.88,
  Annexure C indicator 3
- headline: displayed percentage finalised within the Table 20 clock
- components: within-clock, exceeding-clock and reported-total counts named by
  the contract
- exact excerpts: use the contract boundaries for denominator, cohort,
  incomplete coverage and the 90-days/four-months conflict
- date rule: retain the source `2024/2025` label; the bounded passages state no
  exact ISO period boundaries
- disposition: `hard_quarantine`; do not repair the component-total mismatch,
  clock conflict or incomplete coverage

## Output and receipt boundary

Write only the four-row JSON array and a receipt validating against
`schemas/g2_extraction_run.schema.json`. The receipt must bind this packet,
instruction, atomic row schema, source manifests and output digest; record UTC
start/completion timestamps, role/session, warnings, limitations and procedural
blinding. Do not make a methods, rights, gate, publication or release decision.
