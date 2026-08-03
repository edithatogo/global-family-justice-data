# Real pilot evidence sourcing plan — 2026-08-03

This plan is the operational route for producing real, reviewable G2 pilot
evidence for `INT`, `AUS`, `USA-MN`, `BRA` and `ZAF`. It is preparation and
control logic, not evidence itself. The machine-readable source is
`config/real_pilot_evidence_sourcing.toml`.

## Sequence

1. Freeze the pilot scope and current repository commit. Create a per-candidate
   acquisition folder and source-edition identifier.
2. Use the primary official route. Record URL, language, access date, browser
   or HTTP result, query/filter state, complete bytes, MIME type and SHA-256.
3. If blocked, record the exact access issue and use the documented fallback.
   A fallback may produce metadata/citation evidence only; it cannot silently
   become source bytes.
4. Classify rights for the exact edition. `unknown` or restricted material is
   retained locally as metadata/receipt only and excluded from public outputs.
5. Build the institutional map, coverage assessment, search-log rows and
   extraction recipe. Record negative findings as bounded findings, never as
   proof of absence.
6. Run a second extraction from the preserved edition using a separate receipt
   root. Compare row-level outputs, definitions, clocks, denominators and
   missingness.
7. Route both packets to separate methods/quality panel roles. Record options,
   recommendation, rationale, conflicts and unresolved questions.
8. Obtain owner adjudication and, where required, accountable rights,
   local-verification, security/privacy and operations authority. No agent
   panel can substitute for those authorities.
9. Promote only evidence items whose paths, hashes and independent review are
   complete. Keep all other items draft, quarantined or metadata-only.

## Redundancy and contingencies

- Official export unavailable → preserve official landing-page and access
  failure receipts, then use an official report or controlled request route.
- HTTP 403, CAPTCHA or authentication → record the boundary; do not bypass it
  or claim a negative finding. An owner-approved enquiry is required before any
  new outbound message.
- Rights unclear → retain citation/metadata only and substitute a clearly
  licensed edition if the owner approves the narrowed scope.
- Mapping disagreement → quarantine the measure and request local/second
  review; do not pool or publish it.
- Independent extraction mismatch → preserve both outputs, open a methods
  adjudication item and keep the candidate descriptive-only.
- No response by the documented deadline → record a transparent no-response
  closure with delivery evidence; do not infer coverage or rights.

## Completion criteria

The plan is complete only when every candidate has a source-edition receipt,
rights class, institution map, reviewed coverage assessment, search log,
independent extraction comparison, methods review and owner disposition. Until
then, `E-PILOT-*`, G3 and G2 remain fail-closed. No outbound contact, public
release, Hugging Face upload or gate acceptance is authorized by this plan.
