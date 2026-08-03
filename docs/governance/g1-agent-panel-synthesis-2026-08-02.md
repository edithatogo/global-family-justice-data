# G1 agent-panel synthesis — 2026-08-02

This is an advisory, digest-bound panel record prepared under
`docs/methods/subagent-panel-assurance-protocol.md`. It does not constitute a
G1 acceptance, signature, appointment, legal review, or release decision.

## Packet identity

- Repository revision: `543976f41639d4d3ea84dc979942d30ee2fb2045`
- `MANIFEST.sha256` SHA-256: `00d4a67dac4afd7278cad61d285558851e4bd0bc20dd7d71b138594da275716e`
- Scope: G1 charter, ethics/security boundary, decision rights, owner/deputy
  model, pilot-scope decision, risk/rights baseline, and downstream gate
  dependencies.
- Orchestrator: repository analyst agent.
- Accountable owner: repository owner; no owner adjudication is asserted by
  this record.

## Role reports

| Role | Verdict | Recommendation | Key rationale | Contingency |
|---|---|---|---|---|
| Governance/decision rights | conditional | Owner remains accountable; use an agent deputy for continuity only | Fits a single-person repository without confusing execution with authority | No deputy → record exception and keep continuity criterion blocked |
| Assurance independence | conditional | Run role-separated panels for methods, rights, security, accessibility, safeguarding and operations | Panels provide structured challenge and traceability | Missing role or unresolved conflict → `pending_authority`/`adjudication_required` |
| Execution/workflow | conditional | Freeze packet, run panels, reconcile findings, present owner decision packet | Creates a repeatable digest-bound path | Packet mutation → invalidate reports and rerun |
| Adversarial challenge | fail-closed on acceptance | Do not treat panel consensus or prior conversation approval as G1 acceptance | Authority, signature, rights and consent cannot be inferred | Keep G1 `blocked_by_assurance` and quarantine affected scope |

## Panel synthesis

### Options

- **A (recommended):** owner adjudication after role-separated agent-panel
  pre-review, with an agent deputy for operational continuity.
- **B:** formal delegation to an external host or governance authority.
- **C:** owner-only decision with an explicit no-deputy continuity exception.
- **D (prohibited):** treat conversation approval or panel consensus as
  acceptance.

### Recommendation and rationale

Choose A. It matches the single-person repository model, provides structured
advice and adversarial challenge, preserves traceability, and keeps the owner
as the accountable decision-maker. The deputy is an execution/continuity role,
not an approver. Specialist panel outputs remain advisory prerequisites for
downstream owner decisions.

### Required owner decisions

The owner must still decide, in a separate digest-bound record:

1. whether to accept the G1 charter and boundaries;
2. whether to designate a named agent deputy or record a continuity exception;
3. whether to accept, condition, defer or reject each panel finding;
4. whether the approved pilot scope and escalation rules are authorised; and
5. whether any residual risks are accepted for the applicable gate.

### Fail-closed contingencies

- Missing evidence or role: `evidence_missing` or `pending_authority`.
- Conflicting or conditional reports: `adjudication_required`; quarantine the
  affected scope.
- Changed packet digest: invalidate all reports and rerun the panel.
- No owner decision: transparent no-decision closure; G1 and all downstream
  gates remain blocked.
- Rights, consent, security, safeguarding, hosting, custody, signing, staffing
  or funding not established: do not infer them from panel advice.

## Disposition

Panel work is complete as advisory preparation only. G1 remains
`blocked_by_assurance`, `not_evaluated`, and non-archive-eligible pending the
owner's separate digest-bound adjudication and any required accountable or
specialist evidence.
