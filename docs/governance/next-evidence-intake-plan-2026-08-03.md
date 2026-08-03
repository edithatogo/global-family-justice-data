# Next evidence intake and gate-resolution plan — 2026-08-03

This is the next intake queue after the public-source refresh. It is linked to
`config/next_evidence_intake.toml` and the Conductor decision log.

## Intake order

1. **G1 authority packet (P0).** Bind the governance-owner decision to the
   exact packet digest and supply named owner/deputy assignments, escalation,
   ethics/security boundary and architecture/release authority evidence.
2. **G2 real pilot packet (P0).** Acquire the five approved real editions;
   preserve complete bytes and hashes; run a separate extraction; record row
   differences, methods adjudication and rights/security review.
3. **G3 coverage packet (P1).** Complete second review, local verification,
   source-preservation metadata and transparent enquiry closures for the global
   census.

## Gate transitions

An intake item may move from `queued` to `in_review` only when its artifact
path and retrieval receipt exist. It may move to `accepted` only after the
required independent review and owner adjudication. Draft, synthetic,
metadata-only, conditional or panel-only material cannot satisfy a gate.

## Blocker handling

- Rights or access failure → preserve the failure receipt and keep bytes out of
  public products.
- Missing local reviewer → retain `local_verification_missing`; do not infer
  coverage.
- Extraction disagreement → quarantine the measure and open methods
  adjudication.
- No response → close only with delivery/timing evidence and state the exact
  unanswered question.
- Missing authority → retain the current conditional decision and list the
  absent accountable fields.

The queue advances evidence readiness, not publication. GitHub releases and
Hugging Face datasets/Spaces remain blocked until G6 is accepted.
