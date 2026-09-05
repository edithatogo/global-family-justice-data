# G2 L2 evidence availability and recovery plan

## Completed repository-owned audit

Base: merge commit `708b279679e15647caefd6691cd9e58c0580e2bf`.
This is an availability audit, not a new maturity or owner acceptance.

Inputs before adding this record:

| Input | SHA-256 |
|---|---|
| `programme/maturity_assessment.csv` | `36cd8ff95715bd4e9373080aa8a7cf2ae06d0ac85ed21943a6d3e367c7bb500a` |
| `programme/evidence_register.csv` | `c268b751e2feda548e321c32f31016a2776ea12e9ce1a50f89befa874078ce94` |
| `docs/governance/g2-l2-reassessment-2026-08-26.md` | `a9d9dbc65d7116ae016297dbb93650e6d4a09508fe6aa69a60078b98fa13d707` |

All 21 maturity references resolve through 11 distinct evidence IDs to nine
existing files. Every file matches its registered SHA-256. This removes
uncertainty about baseline record integrity, not substantive L2 sufficiency.

The previously documented `build/g2-material-distinct-20260826-01/` directory
is absent in this checkout. A bounded digest-only scan of JSON metadata in
`build/` and `data/methods/` examined 339 files totalling 6,325,144 bytes.
One file over the 8 MB per-file limit was skipped. Limits were 10,000 files
and 200 MB total; neither was reached. No JSON contents were printed, source
documents opened, network used or artifacts modified. This is not an
exhaustive disk or backup search and does not prove permanent loss.

| Historical supporting record | Observation |
|---|---|
| M06 terminal, `cb403a429945a03198516356b7c0784ef05b800be1e2346caeb6e9986d9ae7e2` | Exact match at `data/methods/g2/G2PKT-MATERIAL-DISTINCT-20260826-01/terminal-stop.json`; remains failed evidence |
| M07 product rehearsal, `22c0275bcc945525fbf4388f04be1c4a736059cc4531ebd2a06042847d1b34a1` | Not found in bounded scan; narrative citation exists, underlying receipt not currently verified |
| M10 language review, `6c555099144139a2c0f7b72e7e51a7098ff0dc0adafb39623191b5fd59df803d` | Not found in bounded scan; narrative citation exists, underlying receipt not currently verified |

The terminal digest is therefore recoverable from public repository metadata;
it should not be reported as necessarily private or missing. The original
reassessment remains immutable. The M07/M10 records must not be reconstructed
from their narrative summaries or assigned their historical hashes.

## Ordered next work and contingencies

1. **Preferred: recover exact M07/M10 receipts from a documented retained
   backup.** Verify each original hash, input bindings and referenced artifact
   availability before review. Recovery preserves the exact historical record
   for review and
   avoids unnecessary reruns. A backup locator is not presently established;
   do not speculate about credentials, contact third parties or search unrelated
   private storage. Finding a receipt alone does not prove its underlying
   artifacts are currently reproducible.
2. **Contingency: prepare fresh bounded evidence.** If no recoverable copy is
   available, freeze a new product rehearsal and source-language advisory
   review using available authorized inputs, with new identities and honest
   dates. Verify deterministic downloads/builds for M07 and publisher/context
   support plus the existing owner resource commitment for M10. This costs
   more work and cannot recreate the historical event. If necessary inputs
   are missing, stop before acquisition and identify the exact missing inputs.
   Failed extraction lineages are never repaired or rerun by this plan.
3. Reconcile M06 against the approved pilot scope using
   `docs/methods/g2-successor-scope-reconciliation-2026-09-05.md`.
   The successful SWE/AUS sample remains valid supporting evidence; it is not
   the complete four-route pilot. A reduced-scope choice is one material owner
   decision, not a routine hash approval.
4. Verify substantive L2 support dimension by dimension and present one
   grouped accountable disposition. Until then preserve canonical maturity,
   WI-G2-04/WI-G2-07 in-review status, quarantine and downstream gate blocks.

Recommendation: preserve approved scope and exact historical records; prefer
verified recovery, then new explicitly labelled evidence where recovery is
unavailable. Do not turn receipt absence into a demand for independent humans,
repeat unchanged approval packets or infer L2 from accepted policy documents.
Agent review remains advisory; no rights, publication, release or G2 acceptance
is conferred by this audit or recovery plan.

## Advisory review

Role-separated agent `l2_availability_review` verified the 21-reference count,
baseline hashes and terminal receipt, found no blocking defect and recommended
the recovery-first plan. It distinguished record authenticity from claim
validity; that wording correction is applied above. Scan counts are based on
the orchestrator's execution, not an independently repeated scan. Review is
agent advice only; the evidence remains in review.
