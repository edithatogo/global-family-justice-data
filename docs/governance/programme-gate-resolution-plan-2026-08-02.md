# Programme gate resolution plan — 2026-08-02

This plan updates the track and gate view without asserting that any external
criterion has passed.

| Gate | Tracks | Remaining gate evidence | Recommended option | Contingency | Promotion rule |
|---|---|---|---|---|---|
| G1 Foundation | T0/T7/T9 | Charter, ethics, decision rights, risk/rights baseline, owner/deputy and pilot approvals | Owner acceptance plus named deputy; advisory panel pre-review | Keep foundation in review | No downstream acceptance without digest-bound authority record |
| G2 Pilot | T1/T2/T3/T8 | Pilot adjudication, 12 heterogeneous systems, rights/privacy/security, dual review, operations rehearsal | Complete panel triage then accountable methods/rights review | Quarantine unresolved pilot claims | No pilot readiness while required dimensions are missing |
| G3 Global census | T2/T3/T6/T9 | 23 reviewed assessments, local verification, second-reviewed negatives, rights/preservation, atlas | Public evidence plus local/regional review | Partial/descriptive-only; metadata-only rights | No coverage promotion with unresolved required dimensions |
| G4 Beta | T4/T5/T6/T7/T8/T9 | Core dataset, outcomes/context products, quality, threat/privacy/rights, operations, beta participation | Build candidate bundle and run bounded panel; obtain human reviews | Synthetic/metadata-only beta | No beta acceptance without evidence packet and authority |
| G5 Release candidate | T0/T1/T5/T6/T7/T8/T9 | Contract freeze, clean build, independent assurance, accessibility, operations, archive/provenance, funding | Rebuild exact digest and obtain all specialist sign-offs | Unsigned local candidate | No RC acceptance with open P0/P1 or missing authority |
| G6 v1 release | All tracks | Final criteria, signed release decision, no critical findings, two-location archive, live service, products, funding | Accountable release decision after all prior gates pass | Remain draft; no archive/publication | Archive only after every mandatory criterion is accepted |

## Status and contingency discipline

- `pending`: evidence or authority not supplied;
- `in_review`: repository packet exists and awaits review;
- `blocked`: required external dependency unavailable or failed;
- `accepted`: exact evidence and accountable authority are bound to the
  packet digest.

Subagent panels may identify, reproduce and triage findings. They cannot create
legal rights, local verification, human consent, independent assurance,
publication authority, signing identity, hosting custody or funding commitment.

## G1 execution decision

G1 remains the current critical-path gate. The approved implementation route
is to freeze and verify the G1 packet, run advisory panel checks, name a
consenting agent deputy, and obtain a signed digest-bound owner decision. A
formally delegated external governance authority is an acceptable alternative;
owner-only acceptance without a deputy is a continuity exception that should
keep G1 blocked unless explicitly documented and justified. Existing
conversation approvals are recorded as policy input only, not as the signed
authority record required for promotion.

If the deputy, signed decision, or any mandatory ethics/security/rights
criterion is absent, the fallback is `blocked_by_assurance` with a transparent
pending-authority record. Downstream gates remain dependency-blocked and no
track becomes archive-eligible.

## Dependency-elimination boundary

The agent panel reviewed the request to remove all external dependencies. It
concluded that owner decisions and agent evidence can remove ambiguity and
complete repository preparation, but cannot truthfully replace legal rights,
local/human verification, independent assurance, consent/safeguarding,
hosting/custody/signing, live support, staffing or funding.

For each such item the Conductor must use `pending_authority`,
`evidence_missing`, `adjudication_required`, `waived_for_scope` or `excluded`.
The only scope in which these dependencies can be removed is a private,
public-source metadata-only and synthetic-rehearsal product with no participant
data, uncertain-rights redistribution, live service, signed release or G6 claim.
That scope is explicitly deferred/excluded, not represented as a passed gate;
reopening it requires a new digest-bound decision and evidence packet.

## Critical-path blocker plans (G1–G3)

| Gate | Options | Recommendation and rationale | Contingencies | Evidence/authority boundary |
|---|---|---|---|---|
| G1 / T0 | Owner + agent-panel review; external delegation; owner-only exception; conversation-only approval | Owner + panel review with an agent continuity deputy. This fits a single-person repository while preserving human accountability. | Missing deputy, partial scope, changed packet, unresolved risk or no decision respectively means exception, quarantine, rerun, fail-closed or no-decision closure. | Requires digest-bound owner decision; panels cannot appoint authority or create acceptance. |
| G2 / T1 | Evidence-complete pilot; external consultancy; synthetic-only pilot | Evidence-complete pilot after panel triage and accountable methods adjudication. It is bounded and reproducible; synthetic-only cannot establish readiness. | Quarantine disputed measures, remain descriptive-only, require adjudication, exclude rights/privacy-uncertain sources, or block after failed rehearsal. | Requires real source receipts, independent re-extraction, rights/privacy/security and operations evidence plus methods authority. |
| G3 / T2–T3 | Verified subset; defer jurisdictions; metadata-only rights; authorised follow-ups | Verified subset plus metadata-only fallback. This maximises useful public evidence without overclaiming. | Unreviewed jurisdiction excluded; missing response remains pending then transparent closure; unclear rights excluded; mutated source triggers recapture. | Requires local/second review, complete assessments, exact-edition rights/preservation and explicit send authorisation; agents cannot supply these. |

Promotion is dependency-ordered: G1 before G2, G2 before G3. Repository controls
may be implemented earlier, but no gate or track is archive-eligible without
the required digest-bound evidence and accountable decision.

## G6 final-release blocker plan (T8/T9 dependencies)

Evidence sourcing and redundancy for this gate is governed by
`docs/governance/g6-evidence-sourcing-plan-2026-08-02.md`. It requires a
primary and redundant receipt for authority, assurance, custody/restore,
service/support, signing/provenance, staffing/funding and publication/takedown.
If either route fails, the narrower private/unsigned/metadata-only fallback is
recorded; redundancy never creates authority or release approval.

G6 is a release-authority gate, not a build milestone. The following options
are recorded so implementation can proceed without implying that a release is
authorised.

| Decision area | Recommended option | Alternative | Contingency / stop condition | Rationale |
|---|---|---|---|---|
| Release decision | Owner signs a digest-bound G6 decision after G1–G5 pass | Formal delegated release authority | Keep `blocked_by_authority`; never infer approval | Preserves accountability and fixes the exact candidate |
| Custody/restore | Two independent locations, signed manifest and witnessed restore | Encrypted local rehearsal | Remain private RC; no archive claim | Local unsigned copies do not establish durable custody |
| Operations | Named service manager/deputy, monitoring, incident route, support SLA and rehearsal | Static artifact handoff | No live-service or handover claim | Deployable code is not operational ownership |
| Products | Publish only verified, rights-cleared products | Metadata/citation-only preview | Exclude unresolved rights/accessibility findings | Limits publication to supported scope |
| Findings | Close all critical/high findings with evidence | Explicit non-critical exception | Any unresolved critical/high blocks G6 | Makes residual risk auditable |
| Sustainability | Costed 12-month staffing/support/funding commitment | Time-boxed pilot funding | No production or continuity claim | Ongoing operation is part of the release promise |

Repository-owned sequence: freeze the candidate digest; run role-separated
agent panels; verify every criterion against blocker registers; rehearse
backup/restore, correction, rollback and incident workflows; invalidate reports
after any digest change; prepare (but do not sign) the owner packet; and promote
only after the actual signed decision, complete evidence index and zero
critical/high findings are present. Archive additionally requires signing,
two-location custody and restore receipts. Failure at any step leaves the
candidate private, unsigned and non-archive-eligible. Panels may recommend
exceptions but cannot grant authority, custody, signing, consent or funding.

## G4 beta blocker plan (T4/T5/T6/T7/T8/T9)

G4 is a controlled beta decision, not a publication decision. The orchestrator
must freeze one candidate digest and route it to role-separated agent panels
before owner adjudication.

| Option | Scope | Recommendation | Rationale | Contingency |
|---|---|---|---|---|
| A | Consent-backed beta from an evidence-complete subset, with synthetic fixtures for unresolved dimensions | **Recommended** | Produces useful operational evidence without overstating population or jurisdiction coverage | Convert to private dry-run if consent, safeguarding, or rights evidence is absent |
| B | Synthetic/metadata-only beta | Fallback | Exercises contracts and workflows while avoiding human or rights exposure | No participant, outcome, or readiness claims; retain G4 blocked |
| C | Full 23-jurisdiction beta | Not recommended | Current coverage and second-review gaps make this misleading | Quarantine incomplete jurisdictions and revert to A or B |

Required G4 packet: frozen core schema and lineage; outcomes/context product
specification; quality/comparability report; current threat/privacy/rights
assessment; accessibility/localisation findings; live-like operations rehearsal;
safeguarding plan; participant consent records; and panel reports bound to the
packet digest. The panel may recommend conditions but cannot supply consent,
rights, human review, hosting authority, or funding.

Promotion rule: G4 may move from `blocked_by_dependency` to `in_review` only
when the packet is complete and all mandatory panel roles report. It may move
to `accepted` only after the owner records a digest-bound decision, no critical
or high finding remains open (or an explicitly permitted exception is recorded),
and all participant/rights boundaries are evidenced. Any packet mutation,
missing panel role, unresolved high finding, or absent consent resets G4 to
`adjudication_required`/`evidence_missing` and blocks G5.

## G5 release-candidate blocker plan (T0/T1/T5/T6/T7/T8/T9)

Detailed redundant acquisition routes, receipt requirements and failure rules
for G4/G5 are recorded in
`docs/governance/g4-g5-evidence-sourcing-plan-2026-08-02.md`.

G5 validates reproducibility and operational readiness of a private release
candidate; it does not authorise public publication.

| Option | Scope | Recommendation | Rationale | Contingency |
|---|---|---|---|---|
| A | Exact-digest rebuild plus independent methods, security/legal, accessibility, operations, and archive reviews | **Recommended** | Gives the strongest traceability and separates implementation from assurance | Keep candidate private and unsigned until every specialist result is present |
| B | Owner-only technical sign-off with automated checks | Not sufficient | Automated checks cannot replace independent assurance, rights, accessibility, or custody | Record local candidate only; no G5 acceptance |
| C | Unsigned local candidate with metadata-only sources | Interim fallback | Preserves reproducibility work while avoiding rights and signing claims | Mark `candidate_only`; no archive/publication eligibility |

Required G5 packet: contract-lock digest; clean reproducible build receipt;
independent methods/security/privacy/legal/accessibility/localisation reports;
signed provenance statement; SBOM and supply-chain review; archive and custody
plan; tested restore receipt; service/support/incident rehearsal; named operating
owners and deputy; and a committed 12-month operating plan. Agent panels must
record options, recommendation, rationale, contingencies, evidence references,
conflicts and abstentions for each role.

Promotion rule: G5 is `in_review` only after a clean rebuild reproduces the
frozen digest and every mandatory report is attached. G5 is `accepted` only
with owner adjudication, no unresolved P0/P1 (critical/high) findings, valid
provenance/signing and archive evidence, and an operating plan with accountable
owners. If any specialist authority, custody location, restore test, funding
commitment, or accessibility/legal review is missing, G5 remains blocked and
the candidate remains private. A changed contract or source-rights decision
invalidates the candidate and requires a fresh rebuild and panel cycle.

## Evidence sourcing and redundancy

All external evidence acquisition follows
[external-evidence-sourcing-plan-2026-08-02.md](external-evidence-sourcing-plan-2026-08-02.md).
Primary and redundant routes are recorded separately with receipt digests,
access outcomes, reviewer roles and limitations. Redundancy improves resilience
but cannot substitute for accountable authority or specialist assurance.
