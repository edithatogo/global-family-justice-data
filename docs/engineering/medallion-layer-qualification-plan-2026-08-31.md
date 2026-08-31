# WI-G4-MED-03 — independent per-layer qualification preparation

Status: in-progress repository-owned preparation. The acceptance-bearing work
item remains planned behind WI-G4-MED-02; neither its dependencies nor acceptance
criteria are waived by this engineering plan.

Baseline: signed `fb3f277`, merged PR #137 at 2026-08-31T11:08:17Z. Both local
post-review suite passes ran 891 tests; coverage was 80.53%. The complete
`autonomy-full` harness passed, as did all 17 exact-head hosted checks. The source
manifest verifies 989 files; bounded bootstrap discovery passed. Prior branch
cleanup left one clean main checkout before this preparation branch was created.

## Recommendation, alternatives and trade-offs

Implement a recomputing qualification matrix over the canonical B0, B1, Silver,
Gold and Platinum layers. Report completeness, fixity, rights state, lineage,
reproducibility, quality, quarantine and restore separately for every layer.
Evidence is scoped to exact objects and layers; successful publication or a
later-layer result cannot satisfy an upstream requirement.

Recommended: reuse existing source-recomputing verifiers through explicit typed
adapters, bind every input and rule, and preserve pending or failed cells when
evidence cannot be verified. Keep technical qualification separate from the
owner's accountable promotion decision. This is more work than a status-only
checklist but produces executable, falsifiable evidence.

Alternative: require only populated evidence references. This is simpler but
already covered by the existing structural layer validator and is insufficient:
a digest or claimed pass does not prove the referenced assessment. Do not use it
as a maturity result. A universal new workflow engine is also unnecessary; use
bounded adapters and explicit unsupported-evidence dispositions instead.

## Ordered implementation

- [~] Obtain role-separated advisory review of reusable verifiers, evidence
  scope, requirements and adversarial cases. Freeze the concrete adapter contract
  before functional implementation.
- [ ] Implement bounded input resolution and exact object/layer/content binding.
  Missing, malformed, conflicting, unsupported or stale evidence must not pass.
- [ ] Recompute independently supported layer checks and emit an exhaustive
  matrix of verified, failed and pending requirements with evidence references
  and limitations. Do not turn self-reported review labels into verified facts.
- [ ] Preserve all lifecycle states in coverage. Quarantine, withdrawal and
  tombstoning prohibit downstream promotion without erasing valid upstream
  evidence. Missing layers remain visible rather than disappearing from counts.
- [ ] Enforce the Gold owner-decision and Platinum release boundaries separately
  from technical checks. Validate available decision bindings without inventing
  authority or treating advisory reports as accountable acceptance.
- [ ] Add adversarial tests, deterministic fictional fixtures and an independently
  recomputed rehearsal/report. Include cross-layer borrowing, digest/object
  substitution, false pass flags, missing predecessor evidence and quarantine.
- [ ] Record supporting evidence and explicitly scoped resume guidance without
  bypassing programme dependency checks or changing any gate/acceptance mapping.
- [ ] Advisory review, full local validation, signed commits, PR, exact-head CI,
  history-preserving merge and local branch cleanup.

## Contingencies and authority boundaries

Where a verifier only establishes structural consistency, report that limited
fact and keep factual assurance pending. Where no supported source adapter
exists, retain the missing capability explicitly; do not select an easier
format and claim complete cohort qualification. Rights, semantic equivalence,
real remote restoration and accountable decisions require their own genuine
evidence. A failed qualification must retain useful upstream evidence and its
public-safe disposition without promoting or hiding the failed layer.

No new network/source requests, source-byte acquisition, external contact,
cross-repository writes, rights clearance, maturity or Gold promotion,
publication, release or G2/G4 acceptance is authorized. This track prepares
repository-owned mechanisms; actual factual qualification remains separately
evidenced and subject to the existing owner-controlled process.
