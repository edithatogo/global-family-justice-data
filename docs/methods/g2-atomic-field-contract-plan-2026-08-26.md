# G2 atomic field-contract remediation — 2026-08-26

## Outcome and recommendation

The repository now adopts the existing atomic extraction-row schema as the
basis for any future validation cohort. Composite fields that caused the
terminal 18-difference result are replaced by separate source-native facets and
controlled codes. This is repository-owned preparation only.

### Option A — recommended and implemented

Use atomic locator fields, preserve source text with only Unicode NFC and
whitespace collapse, keep semantic codes separate, require explicit clock
wording for calendar or working time bases, and keep unstated dates null.
Validate these rules in code with source-independent fictional tests.

Trade-off: this materially reduces avoidable representational disagreement but
does not guarantee concordance or factual accuracy. Contingency: any ambiguity
remains coded and quarantined; a future cohort stops on any critical mismatch.

### Option B — retain the legacy composite row

This preserves compatibility but leaves delimiter, translation, completeness
and semantic-inference choices underdetermined. It is rejected because the
sealed evidence showed those choices generated 18 critical differences.

### Option C — encode answers from the failed four editions

This could manufacture agreement on known inputs but would be retrospective
calibration and would contaminate reproducibility evidence. It is prohibited.

## Implemented controls

- `schemas/g2_atomic_extraction_row.schema.json` remains the canonical atomic
  row shape;
- `data/methods/g2/G2ATOMIC-FIELD-CONTRACT-20260826-01/contract.json` freezes
  generic policies and existing thresholds;
- `gfjd.g2_atomic_rules` provides executable normalization, time-basis and
  cross-field validation;
- adversarial tests use fictional labels and contain no expected values or
  answer-bearing locators from the failed lineage;
- the failed outputs remain immutable and are not repaired or reused.

## Remaining boundary

This work does not select a cohort or authorize acquisition, extraction,
rights clearance, publication, release, maturity promotion or G2 passage. A
new cohort and execution packet require a later grouped owner decision.
