# Downstream gate blocker matrix — 2026-09-05

This matrix is a repository-owned readiness aid. It does not accept a gate,
clear rights, establish hosted availability, create partner registration,
authorize publication or release, or substitute for the owner’s accountable
decision.

## Current dependency chain

| Gate/work | Current state | Evidence still required | Repository-owned work that can continue now | Blocking boundary |
|---|---|---|---|---|
| G2 / WI-G2-04 | `in_review` | Scope-matched route evidence for BRA API and GBR-EAW routes, plus owner disposition | Preserve the passing SWE/AUS successor, reconcile it against the approved cohort, and keep failed lineages immutable | No scope waiver or G2 passage |
| G2 / WI-G2-07 | `in_review` | Fresh blinded evidence covering the approved pilot scope and owner adjudication | Maintain the exact comparator, evidence lineage and acceptance packet; identify uncovered route cells | No promotion from the two-source supporting run |
| G3 / WI-G3-01..08 | `in_review` | Complete reviewed census, rights metadata, enquiry, local-verification and live monitoring evidence | Run deterministic register audits, coverage-gap reports, receipt/hash checks and panel consistency reviews | No completeness, local-human validation or rights-clearance claim |
| G4 / WI-G4-01..09 | `in_review` | Real B0 bytes, custody receipts, empirical replay, accessibility and operational evidence | Validate schemas, replay harnesses, synthetic controls, public-safe manifests and readiness packets | No empirical layer qualification or hosted publication claim |
| G4 / WI-G4-MED-02 | `in_review` | Verified public B0 bytes and independent B0→B1/Silver replay receipts | Test replay code against available fixtures and verify contracts/lineage metadata | Fixtures cannot substitute for real B0 evidence |
| G4 / WI-G4-MED-03 | `in_review` | Layer-specific qualification and owner Gold adjudication | Run contract, quarantine, lineage and negative tests; prepare qualification matrix | No maturity promotion from later-layer or synthetic evidence |
| G4 / WI-G4-MED-04 | `planned` | Verified public Hugging Face estate and anonymous retrieval receipts | Prepare manifests, role labels, link checks and publication checklist | Hosted upload and availability remain unverified |
| G4 / WI-G4-MED-05 | `planned` | Actual federation registration and provider/partner interoperability receipts | Validate DCAT-AP, RO-Crate, Croissant, PROV-O and OpenLineage locally | Standards conformance does not establish partner acceptance |
| G5 / WI-G5-MED-01..03 | `planned` | Two-provider anonymous restore, lifecycle rehearsal and release safety evidence | Exercise offline restore/correction controls and inspect manifests | No public restore or release-candidate claim |
| G6 / WI-G6-01..09 | `in_review` | Signed owner release decision, final quality/security/rights evidence, public products, custody and continuity | Keep the final criteria matrix current and fail closed on missing evidence | No release authorization or publication claim |

## Priority order

1. Complete the approved G2 route-matched empirical cohort and owner
   adjudication. This is the direct dependency for G3 and all later gates.
2. In parallel, close repository-owned G3 register/hash/coverage/enquiry
   consistency findings without changing factual statuses.
3. Prepare G4 replay, accessibility and operational evidence packets, but do
   not label them empirical until real B0 bytes and receipts are present.
4. Keep Hugging Face and federation work at preparation/verification-plan
   status until hosted retrieval and partner-registration facts are observed.
5. Reconcile G5/G6 matrices only after the upstream evidence is accepted.

## Fail-closed rules

- A passing local test is readiness evidence, not hosted availability or gate
  acceptance.
- Synthetic, fixture, metadata-only or two-source evidence cannot satisfy an
  approved broader cohort requirement.
- Unknown or unresolved rights, privacy, disclosure, custody and provider
  states remain quarantined or metadata-only.
- Every promotion must cite an exact evidence identifier, path, digest and
  review/disposition record.
- The owner remains the sole accountable decision-maker; agent panels provide
  options, trade-offs, rationale and contingencies only.

## Recommended next repository-owned slice

Generate a fresh route-cell reconciliation receipt from the current
`programme/work_items.csv`, `programme/evidence_register.csv` and G2 scope-gap
matrix, then bind that receipt to the next execution/owner-decision packet.
Do not alter the approved cohort or infer missing route evidence.
