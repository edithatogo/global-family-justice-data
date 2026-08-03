# External authority gate execution plan

This plan supplements the external blocker register and makes authority
requirements explicit for track promotion.

| Gate family | Authority required | Evidence packet | Recommended route | Contingency | Track transition |
|---|---|---|---|---|---|
| Governance (T0) | Owner or delegated accountable authority | Charter, RACI, ethics boundary, decision-rights record, digest and signature | Owner acceptance with named deputy | Keep G1 in review | `in_review` → `accepted` only with signed record |
| Methods (T1) | Accountable methods authority plus panel record | Frozen v0.3 methods, pilot register, panel reports, conflict matrix | Panel pre-review followed by accountable adjudication | Quarantine disputed measures | No G2 promotion without adjudication |
| Coverage (T2/T3) | Named local/regional reviewer and rights authority | Search receipts, second-review ledger, maps, terms, edition hashes | Public evidence plus local review; metadata-only rights route | Partial/descriptive-only or exclude | No readiness promotion on unresolved required dimensions |
| Product (T6) | Human accessibility/localisation/publication authority | Exact product digest, WCAG review, language review, usability/harm findings | Independent human review | Candidate-only, no publication | G5 evidence remains missing |
| Security/legal (T7) | Independent legal, privacy, security and supply-chain reviewers | Threat model, rights register, SBOM, action audit, risk acceptance | Panel pre-review plus specialist sign-off | Unsigned metadata/synthetic candidate | G5/G6 assurance remains missing |
| Operations (T8) | Service owner, deputy, host, custodian and signing authority | Host test, custody receipt, signed provenance, support/incident and restore evidence | Approved host plus independent archive | Local unsigned rehearsal only | No service handover/archive closure |
| Participation (T9) | Safeguarding authority, owner and consented contributors | Consent protocol, safeguards, remuneration, feedback and disposition records | Compensated consent-based review | Synthetic rehearsal only | No representation claim |
| Sustainability (T9) | Accountable funder/owner | Costed 12-month plan, staffing, succession and funding commitment | Commit before release candidate | No production release | G6 funding evidence remains missing |

## Status discipline

- `pending`: authority or evidence has not been supplied.
- `in_review`: repository packet exists and awaits accountable review.
- `accepted`: exact evidence and authority are recorded against the packet
  digest; this is the only state that can satisfy a gate criterion.
- `blocked`: a required external dependency is unavailable or failed.

Subagent consensus, owner assertions without a signed digest-bound record,
local green tests and generated artefacts cannot create `accepted` status.
Archive eligibility requires every required gate and dependency to be accepted.

## Approved operating policy (D-EXT-2026-08-02)

The owner-approved operating policy applies to every authority row in this
plan:

- governance and final release remain with the owner; specialist rows require
  named independent reviewers;
- pilot claims are limited to an evidence-complete subset, not the full
  jurisdiction universe;
- publication is limited to sources with clearly permissive rights;
- each outbound enquiry requires an exact recipient, message, disclosure,
  scope and send-window packet approved immediately before sending; drafts are
  not sends;
- the candidate remains private and unpublished through G5/G6; and
- absence of an authority or evidence packet is recorded as
  `pending_authority`, `evidence_missing`, `adjudication_required`,
  `no_response_pending` or exclusion as applicable. It must not be inferred as
  acceptance.

This policy changes no gate to `accepted` and does not appoint reviewers,
create rights, authorise contact, or provide hosting, custody, signing,
staffing or funding evidence.

## G1 blocker resolution plan

G1 is the current critical-path blocker. It is not a missing software
feature; it is an accountable governance acceptance gate. The repository can
prepare and verify the packet, but only the owner or a formally delegated
authority can accept it.

### Required sequence

1. Freeze the candidate commit and regenerate the governance/G1 pack and
   `MANIFEST.sha256`.
2. Verify that the pack contains the charter, aggregate-only ethics and
   security boundary, decision-rights/RACI record, risk and rights baseline,
   pilot-scope decision, owner/deputy assignments, escalation route and
   unsigned release-decision template.
3. Run the role-separated subagent pre-review for completeness, conflicts,
   prohibited-data boundaries and downstream dependencies. Record its digest,
   findings and abstentions; it is advisory only.
4. Obtain the named deputy's acceptance or record that no deputy is available.
5. Obtain the accountable owner's digest-bound decision, with authority,
   decision date, decision reference, scope and explicit conditions.
6. Re-run conductor validation and promote G1 only if every mandatory work,
   evidence, risk, maturity and dependency criterion is satisfied.

### Options, recommendation and rationale

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| A | Owner accepts after a role-separated agent-panel review; a named agent deputy provides operational continuity | **Recommended** | Fits the single-person repository while producing structured options, recommendations, contingencies and rationale for every review |
| B | Owner delegates G1 to a formally identified external host or governance body | Viable alternative | Stronger institutional separation, but introduces an external appointment and slower dependency |
| C | Owner-only acceptance with no deputy, with agent-panel continuity advice | Not recommended | Agents can advise and execute but cannot silently become an accountable deputy; keep deputy-dependent criteria blocked unless an exception is recorded |
| D | Treat the existing owner approval in conversation as acceptance | Prohibited | It is not a signed, digest-bound authority record and cannot satisfy G1 |

### Contingencies

- If a deputy cannot be named or consent cannot be recorded: retain
  `in_review`/`pending_authority`; do not promote G1.
- If the owner accepts only part of the scope: record conditions and keep any
  dependent criterion blocked; downstream gates cannot overrule them.
- If the pack changes after review: invalidate the review, regenerate the
  digest, and repeat review/acceptance.
- If an ethics, security, rights or independence concern is unresolved:
  quarantine the affected scope and retain G1 `blocked_by_assurance`.
- If no accountable decision arrives by the review deadline: record a
  transparent no-decision closure and keep all downstream gates blocked.

### Promotion rule

G1 may transition only from `in_review`/`blocked_by_assurance` to `accepted`
when the exact pack digest, named authority, named deputy (or formally
approved exception), signed decision record, decision reference and all
mandatory conductor criteria are present. No local test, panel consensus,
owner conversation, or generated artefact alone can perform that transition.

### Single-person repository agent-panel workflow

Because this repository has one human owner, all preparatory advice and
specialist-review requests must be routed to a role-separated panel of agents.
The panel is an advisory evidence-gathering mechanism, not a substitute for
accountable authority. Each agent receives the same frozen packet digest and
must return a structured report containing: options, recommendation, rationale,
contingencies, evidence references, conflicts/abstentions and a verdict
(`pass`, `conditional`, or `fail-closed`). The orchestrator produces a
digest-bound synthesis and presents it to the owner for the actual decision.

The minimum G1 roles are governance/charter, ethics/security boundary,
methods/dependencies, rights/disclosure, continuity/operations, and adversarial
challenge. Run roles independently, reconcile disagreements explicitly, and
preserve minority findings. A panel report may close repository-owned
preparation work, but cannot create a signature, appoint an external authority,
attest legal rights, or promote G1.

Panel outcomes and contingencies:

- unanimous `pass`: prepare the owner decision packet; G1 remains pending until
  the owner records the digest-bound decision;
- mixed `pass`/`conditional`: adopt the strictest conditions, quarantine the
  affected scope, and keep G1 `blocked_by_assurance`;
- any `fail-closed` or unresolved conflict: record the finding and remediation;
  do not promote;
- missing or unavailable role: record an abstention and retain the gate pending;
- packet mutation after review: invalidate reports and rerun against the new
  digest.
