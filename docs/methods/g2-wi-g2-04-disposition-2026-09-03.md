# WI-G2-04 disposition record — 2026-09-03

Status: repository-owned evidence reconciliation; not G2 acceptance.

This record indexes the available dual-extraction, comparator and advisory
materials for the real-pilot cohort and states the fail-closed disposition.
It does not create new empirical observations, repair failed outputs, or
substitute an owner adjudication.

## Cohort disposition

| source | primary/secondary evidence | comparator | disposition | blocking condition |
|---|---|---|---|---|
| AUS | formal-run index (digest-bound outputs) | diagnostic receipt | hard quarantine | 18 critical differences; ratio wording and court coverage are not safely comparable |
| USA-MN | formal-run index (digest-bound outputs) | diagnostic receipt | quarantine | critical semantic/contract differences; source-defined statewide statistic requires fresh contract |
| BRA | formal-run index (digest-bound outputs) | diagnostic receipt | quarantine | partial-year protective-measures snapshot; critical field differences |
| ZAF | formal-run index (digest-bound outputs) | diagnostic receipt | hard quarantine | conflicting clock arithmetic, component mismatch and incomplete coverage |

## Controls verified

- Four source keys are present in both sealed extraction outputs.
- The diagnostic comparator is fail-closed and recorded 58/76 critical and
  59/82 populated-field matches; this is below the approved thresholds.
- Existing failed packets and sealed artifacts remain immutable.
- No owner adjudication, rights clearance, publication or release is inferred.
- No row is eligible for gold promotion or G2-C04 acceptance.

## Required closure evidence

WI-G2-04 can move out of `in_review` only after a fresh, digest-bound
role-separated run produces threshold-passing exact concordance, a methods
disposition for every row, and an explicit owner adjudication bound to the
packet and manifest. Until then the register and Conductor remain blocked.

## Provenance

Primary source index: `docs/methods/g2-real-pilot-formal-run-evidence-index-2026-08-15.md`.
Execution register: `data/methods/real_pilot_execution_register.csv`.
Acceptance-bearing evidence remains `E-PILOT-REVIEW`; this record is supporting
reconciliation evidence only.
