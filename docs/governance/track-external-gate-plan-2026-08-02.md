# Track external-gate plan — 2026-08-02

All T0–T9 repository implementation slices are complete. The following plan
records the remaining external gates and keeps track status fail-closed.

| Track | External gate | Option A (recommended) | Option B | Contingency | Authority boundary |
|---|---|---|---|---|---|
| T0 | Governance acceptance | Owner signs digest-bound charter and names deputy | Delegate to accountable authority | Keep G1 in review | Owner/delegated authority |
| T1 | Methods assurance | Subagent panel pre-review plus independent methods adjudication | External consultancy | Descriptive-only/quarantine | Methods authority |
| T2 | Coverage/enquiries | Evidence-complete pilot subset; public evidence plus local/second review; dated closure rules | Defer unresolved jurisdictions | Partial/descriptive-only; unresolved rows remain excluded | Local reviewer and explicit owner approval of an exact enquiry packet |
| T3 | Rights/preservation | Metadata-only until exact-edition rights decision | Request permission per source | Exclude restricted material | Rights/legal authority |
| T4 | Architecture/release | Independent architecture and reproducibility review | External technical assurance | Draft release only | Independent reviewer |
| T5 | Quality/comparability | Independent re-extraction and adjudication | External quality review | Quarantine disputed measures | Quality authority |
| T6 | Product assurance | Human accessibility, localisation, usability and harms review | Technical preview with explicit exceptions | Candidate-only | Accessibility/publication authority |
| T7 | Security/legal | Independent security, privacy, legal and supply-chain review | Separate specialists | Unsigned, metadata-only candidate | Security/legal authority |
| T8 | Operations/custody | Host, independent archive, signing, support and recovery evidence | Offline encrypted custody rehearsal | No deployment/archive | Service/signing/custody authority |
| T9 | Participation/funding | Consented safeguarded participation plus funded staffing plan | Synthetic rehearsal while recruiting | No representation or handover claim | Safeguarding, owner and funder |

## Execution and status rules

1. Freeze the exact candidate digest before each review.
2. Run role-separated subagent pre-review and record findings/conflicts.
3. Obtain the named external evidence or authority for the applicable row.
4. Adjudicate findings and update the external blocker register.
5. Rebuild and verify the candidate after any accepted change.
6. Promote a track only when its required evidence and authority are present.
7. Archive only tracks whose dependencies, evidence and approvals are all
   complete; otherwise retain `pending`, `in_review` or `blocked` status.

No panel consensus, local green test, checksum or owner assertion substitutes
for legal rights, human consent, independent assurance, publication authority,
host custody, signing or funding evidence.

## Evidence sourcing and redundancy

The dependency-ordered acquisition workflow, primary/redundant routes,
receipt minimums, failure handling and digest invalidation rules are defined
in [external-evidence-sourcing-plan-2026-08-02.md](external-evidence-sourcing-plan-2026-08-02.md).
It applies to T0–T9 and is part of the Conductor handoff. Redundant collection
improves resilience but never substitutes for the accountable authority or
specialist evidence required by a gate.

## G4/G5 implementation sequence and track controls

The following dependency sequence applies to T4–T9 and is intentionally
fail-closed:

1. Orchestrator freezes the candidate and records its manifest/contract digests.
2. Role-separated agent panels independently review beta/release concerns,
   returning options, recommendation, rationale, contingencies, evidence,
   conflicts, abstentions and verdict.
3. Repository-owned controls run: contract lock, clean rebuild, SBOM, product
   accessibility markers, census/rights checks, backup/restore rehearsal and
   operations packet validation.
4. Missing or conflicting evidence is assigned `evidence_missing`,
   `adjudication_required` or `pending_authority`; it is never inferred closed.
5. Owner adjudicates the digest-bound synthesis. Only then may a gate move to
   `accepted`; downstream promotion remains blocked on upstream acceptance.

For G4, T4/T5/T6/T7/T8/T9 remain candidate or dry-run work until consent,
rights/privacy, human accessibility/localisation, live-like operations and
quality/comparability evidence are attached. For G5, T0/T1/T5/T6/T7/T8/T9
remain non-archive-eligible until independent assurance, signed provenance,
tested custody/restore, named support, and committed operating resources are
recorded. Any source, contract or packet change invalidates dependent reports
and triggers a new digest-bound review cycle.

## Approved operating policy (D-EXT-2026-08-02)

The owner approved the recommended options for all tracks:

- retain owner governance and release authority, with independent named
  reviewers for specialist gates;
- use an evidence-complete pilot subset rather than claiming all jurisdictions
  are ready;
- publish only sources with clearly permissive rights, retaining uncertain
  material as metadata/citation-only;
- require explicit approval for each outbound enquiry using an exact recipient,
  message and scope packet;
- keep the release candidate private and unpublished through G5/G6; and
- apply fail-closed statuses (`pending_authority`, `evidence_missing`,
  `adjudication_required`, `no_response_pending`, or exclusion) whenever the
  corresponding external condition is absent.

This updates the operating disposition of T0–T9 but does not create the
specialist appointments, external evidence, signed gate decisions, or release
authority required for promotion or archive.

### T0/G1 implementation mapping

The T0 track now carries the G1 blocker as an explicit dependency sequence:

1. build and freeze the digest-bound G1 packet;
2. complete advisory subagent-panel checks and record conflicts/abstentions;
3. identify and obtain a consenting deputy (or record a formally approved
   exception);
4. obtain the owner's signed, scoped, digest-bound decision; and
5. re-run conductor readiness before any promotion.

The recommended route is owner acceptance with a named agent deputy. External
specialist reviewers remain required for methods, rights, security/privacy,
accessibility, safeguarding and operations gates. If any G1 prerequisite is
missing, T0 remains implemented but `blocked_by_assurance` and non-archive-
eligible; the repository must not infer acceptance from the owner's prior
conversation approval.

## Agent-panel routing for all tracks

In this single-person repository, preparatory advice and specialist-review
requests for T0–T9 route to role-separated agent panels. Each panel works from
the same frozen digest and returns options, a recommendation, rationale,
contingencies, evidence references, conflicts/abstentions and a verdict. An
orchestrator preserves each role report and produces a digest-bound synthesis
for owner adjudication. Panel advice can close repository-owned preparation
tasks, but cannot create authority, rights, consent, signatures, funding,
hosting or gate acceptance. Disagreement, missing roles, absent evidence or a
mutated packet keeps the affected track fail-closed and triggers
`adjudication_required`, `pending_authority`, `evidence_missing` or a rerun.

## G1–G3 / T0–T3 blocker playbooks

### G1 / T0 — foundation acceptance

Options: (A) owner acceptance after role-separated agent-panel review with an
agent continuity deputy; (B) formal delegation to an external governance body;
(C) owner-only continuity exception; (D) conversation approval as acceptance.
**Recommendation: A.** It fits the single-person model while retaining a
human decision boundary. B is stronger but depends on an appointment; C weakens
continuity; D is prohibited. Freeze the packet, run governance/ethics,
methods/dependencies, rights/disclosure, continuity and adversarial panels,
preserve dissent, and present the digest-bound synthesis to the owner. Record
decision, scope, conditions, date and immutable reference. No deputy, partial
approval, packet mutation, unresolved ethics/security concern or absent decision
keeps G1 blocked (with continuity exception, quarantine, rerun or transparent
no-decision closure as applicable).

### G2 / T1 — methods and pilot assurance

Options: (A) panel triage followed by accountable methods adjudication and a
small evidence-complete pilot; (B) external consultancy; (C) synthetic-only
pilot. **Recommendation: A.** Required evidence is a frozen methods digest,
pilot register, real source receipts, independent re-extraction,
rights/privacy/security review, comparability notes and operations rehearsal.
Agents may reproduce and flag issues, but cannot sign the methods decision or
turn synthetic results into pilot evidence. Quarantine disputed measures; keep
missing-real-data pilots descriptive-only; use `adjudication_required` for
panel disagreement; exclude sources with rights/privacy uncertainty; failed
rehearsal blocks promotion.

### G3 / T2–T3 — coverage, enquiries and rights

Options: (A) evidence-complete jurisdiction subset with public-source search,
local/second review and permissive-rights-only publication; (B) defer unresolved
jurisdictions; (C) metadata/citation-only for uncertain sources; (D) follow-up
enquiries. **Recommendation: A plus C**, with D only after an exact
recipient/message/scope packet receives explicit owner authorization. Required
evidence is the search log (language, date, result and access issue), maps,
completed assessments, local verification, multilingual/inaccessible second
review, response or dated transparent closure, exact-edition identity/hash,
terms and preservation disposition. Unknown or inaccessible is never absence.
No reviewer keeps a jurisdiction unresolved; no second review excludes it from
readiness; no response remains `no_response_pending`; unclear rights are
metadata-only or excluded; source mutation requires recapture and invalidates
dependent review. No enquiry is sent automatically.

G1 must be accepted before G2, and G2 before G3 claims can be promoted. T0–T3
remain non-archive-eligible until evidence and accountable decisions are bound
to the exact digest. Panels recommend options and contingencies but cannot
supply local verification, legal rights, consent, signatures, funding or
publication authority.

## T8/T9 and G6 blocker implementation plan

The G6 evidence-sourcing and redundancy sequence is specified in
`docs/governance/g6-evidence-sourcing-plan-2026-08-02.md`. T8/T9 work must
capture primary and backup receipts for custody, restore, service, signing,
staffing, funding and publication/takedown; failed or conflicting routes keep
the affected track fail-closed.

T8 (operations/custody) and T9 (participation/sustainability) are the final
operational dependencies of G6. Their repository-owned preparation can proceed;
acceptance cannot be inferred.

### T8 options and controls

- **A — Recommended:** prepare named service-manager/deputy, host/support,
  incident/monitoring, signed-provenance, two-location custody and witnessed
  restore packets; run each through the role-separated agent panels.
- **B:** retain an offline encrypted rehearsal while recruiting a host,
  independent custodian and signing authority.
- **Contingency:** label receipts `local-rehearsal-only` and `unsigned`; disable
  deployment, archive closure and live-service claims.

Deterministic code and a local restore prove repeatability, not independent
custody, signing, support or ownership. A packet mutation invalidates reports
and requires a fresh rehearsal.

### T9 options and controls

- **A — Recommended:** prepare consent, safeguarding, remuneration,
  feedback/localisation and a costed 12-month staffing/funding packet; route
  every component through the agent panels before owner review.
- **B:** run a synthetic, non-participatory rehearsal while recruiting
  contributors and securing funding.
- **Contingency:** make no lived-experience or representation claim; retain
  participation evidence as `pending_authority` and keep G5/G6 blocked.

Agents can test forms, translations, threats and operating arithmetic, but
cannot supply consent, safeguarding authority, remuneration, staff or funding.

The orchestrator may assemble a digest-bound G6 packet and present options and
recommendations. It must not mark G6 accepted, publish, sign artifacts, claim
two-location custody or archive any track unless all prior gates pass and the
actual release decision plus custody, signing, operations, participation and
12-month resource evidence are attached. Otherwise retain
`blocked_by_dependency` or `blocked_by_assurance` with a transparent reason.
