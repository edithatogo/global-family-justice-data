# G2 concordance policy owner decision — 2026-08-15

Decision ID: `D-G2-CONCORDANCE-POLICY-20260815`

Decision-maker: repository owner, founder and sole accountable decision-maker.

Advisory sample reference:
`docs/methods/g2-real-pilot-preflight-panel-2026-08-15.md`.

## Owner decision

> I approve the G2 concordance policy before the formal extraction rerun.
> Source edition, jurisdiction, provenance locator, value, denominator,
> statistic type, unit, clock or time basis, cohort or population basis,
> matter type and indicator are critical fields and require 100% concordance
> after documented clerical correction and rerun. Overall populated-field
> concordance must be at least 99%.
>
> No critical discrepancy may be waived into a passing result. Source ambiguity
> or unresolved discrepancies require quarantine or exclusion. The comparator
> must recompute concordance from two separately produced, digest-bound outputs.
>
> This approval applies to the four-row sample recorded in
> `g2-real-pilot-preflight-panel-2026-08-15.md`. It does not accept any extracted
> value, methods disposition, source rights, G2 passage, publication or release.

## Binding interpretation

- The four sample keys and source targets are frozen by the referenced preflight
  report and the subsequent evidence-packet manifest.
- `measure_original` is the source-native indicator field.
- The clock or time basis includes `period_start`, `period_end` and
  `time_basis`.
- The denominator includes both `denominator_value` and
  `denominator_definition`.
- Cohort or population basis includes `cohort_basis` and `population_scope`.
- `component_values` preserves additional numeric facts explicitly named in a
  frozen target; every populated component is critical.
- A correction is clerical only when the source and frozen instruction resolve
  it without discretionary interpretation. Both extraction paths must then be
  rerun and rebound.
- No publication, outbound contact, rights clearance or gate promotion is
  authorized.

Immutable binding: the signed Git commit containing this decision and the
machine-readable policy record. The exact commit is recorded in the frozen G2
evidence packet created after this decision.
