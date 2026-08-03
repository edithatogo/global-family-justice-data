# G1 role-separated panel pre-assurance report — 2026-08-03

## Purpose and boundary

This is an advisory, repository-owned pre-assurance pass. It reviews the fixed
G1 governance, ethics/security, architecture, RACI, risk, rights and pilot-scope
materials. It does not create an appointment, consent, legal opinion,
independent assurance, signature or gate acceptance. The report must be bound
to its commit and manifest digest before an owner uses it as decision evidence.

## Inputs reviewed

| Area | Current artifact | Finding |
|---|---|---|
| Governance | `docs/governance/g1-owner-decision-packet-2026-08-03.md`; `g1-control-gap-matrix-2026-08-03.md` | Current owner approval is recorded, but readiness controls remain in review. |
| Roles/RACI | `docs/governance/roles-and-raci.md`; `docs/programme/track-charters.md` | Generic roles and deputy requirement are defined; named consenting appointments are absent. |
| Ethics | `docs/methods/data-governance-ethics.md`; `docs/governance/governance-assurance.md` | Aggregate-only and child-safety boundaries are clear; accountable ethics acceptance is absent. |
| Security/privacy | `docs/security/threat-model.md`; `docs/security/rights-and-redistribution.md` | Baseline controls exist; current specialist review and residual-risk acceptance are absent. |
| Architecture/contracts | `docs/development/implementation-status.md`; `docs/methods/v0.3-methods-contract-manifest.json`; `docs/operations/release-and-operations.md` | Reproducibility and contract intent are documented; technical authority sign-off and clean-room receipt are absent. |
| Risk | `docs/programme/risk-register.md`; `docs/governance/external-blocker-snapshot-2026-08-03.md` | Risks and external blockers are enumerated; accountable owners, dates and accepted residual-risk decisions are incomplete. |
| Rights/scope | `docs/security/rights-and-redistribution.md`; `docs/governance/pilot-scope-substitution-options-2026-08-03.md`; `docs/methods/real-pilot-execution-register-2026-08-03.md` | Rights routing and scope options exist; final pilot scope and rights decisions are pending. |

## Role-separated findings

### Governance and independence reviewer

**Finding:** Option A (owner accountable; analyst-agent deputy operational only)
is coherent for a single-person repository, but the charter, host/sponsor,
decision-rights confirmation, deputy consent and independent-assurer appointment
are not evidenced as signed, current records.

**Recommendation:** retain Option A and add a short owner-signed role record
listing the owner, operational deputy, escalation route, conflict rule and
independent-assurance vacancy. Do not treat the agent panel as the assurer.

**Contingency:** if no human deputy or host can be appointed, keep G1
conditional and restrict the project to preparation/metadata-only work.

### Ethics and security reviewer

**Finding:** The aggregate-only public boundary, prohibited personal data,
threat controls and disclosure safeguards are internally aligned. A current
privacy/rights threat review, security exception register and accountable
acceptance are missing.

**Recommendation:** create a digest-bound control acceptance checklist with
explicit residual risks, data classes, incident route and review expiry; route
it to the accountable security/privacy and rights authority.

**Contingency:** unknown rights, small-cell risk or unresolved threat remains
quarantined and may be represented only as metadata or a redacted aggregate.

### Architecture and contracts reviewer

**Finding:** Contract/versioning and reproducibility requirements are
documented, but there is no current clean-room build receipt bound to the G1
packet and no named technical authority accepting the architecture.

**Recommendation:** run the repository-native strict validation and clean-build
receipt, hash the outputs, and attach a technical review checklist. Keep this
evidence descriptive until a technical authority accepts it.

**Contingency:** if clean build or contract checks fail, freeze schema changes,
record the failure and keep all downstream gates blocked.

### RACI and operations reviewer

**Finding:** RACI correctly separates accountable, responsible and independent
roles, but it assumes real appointments and consent that are not present in the
repository. A single agent cannot be both delivery deputy and independent
assurer.

**Recommendation:** maintain the agent as operational deputy only; add named
human or institutional role holders as they become available and record
consent/term dates. Keep independent assurance as a separate vacancy.

**Contingency:** no named deputy or assurer means no pilot execution and no
release promotion; continue runbook and test preparation only.

### Risk and rights reviewer

**Finding:** The risk register identifies critical risks (comparability,
rights, disclosure, staffing, independence and maintenance), but most lack a
current accountable disposition and review date. Rights classes for the
approved pilot candidates remain unresolved or metadata-only.

**Recommendation:** create a residual-risk table keyed to the risk IDs and
source manifests, with disposition (`open`, `mitigated`, `accepted` only by
authority), owner, due date and evidence hash.

**Contingency:** unresolved critical/high risks remain blockers; use the
evidence-complete subset only when scope and authority explicitly permit it.

### Pilot-scope reviewer

**Finding:** The original five-candidate pilot remains the approved working
scope, while GBR-EAW is rights-cleared preparation outside that scope. The
scope decision packet is pending and no candidate has complete qualifying
real-pilot evidence.

**Recommendation:** retain the original five by default; add GBR-EAW only via
an explicit owner decision recorded against its manifest and candidate packet.
For each selected candidate require bytes, hash, edition, rights, second
extraction, methods adjudication and independent review before G2.

**Contingency:** if a candidate cannot satisfy rights or bytes requirements,
quarantine it and proceed only with a smaller explicitly approved subset; do
not lower the evidence standard or substitute synthetic data.

## Cross-panel options

| Option | Description | Recommendation | Contingency |
|---|---|---|---|
| A | Close documentation and role records first; keep G1 conditional pending authorities | **Recommended** | If authority cannot be sourced, maintain preparation-only mode. |
| B | Seek a minimal real pilot with one rights-cleared candidate | Viable fallback after scope approval | No promotion if independent review or methods authority is unavailable. |
| C | Treat current panel output as G1 assurance | Not recommended and prohibited | None; panel output cannot substitute for accountable authority. |
| D | Metadata-only pilot while external evidence is pending | Safe fallback | No G2/G3 maturity or publication claims. |

## Remediation register

1. Add current owner/agent operating record and immutable packet binding.
2. Produce clean-build and contract-check receipt.
3. Add residual-risk and authority-assignment fields to the G1 evidence index.
4. Resolve pilot-scope choice, including the GBR-EAW boundary.
5. Obtain rights/security, methods and independent-assurance decisions from
   accountable authorities.
6. Re-run this panel against the resulting fixed digests and preserve dissent.

## Owner decision fields

The owner must decide: (a) pilot scope A/B/C/D; (b) whether to accept the
listed residual risks or leave them open; and (c) who, if anyone, is the
independent assurer and security/rights authority. The panel recommends A for
scope (retain five) and D as the safe operational fallback. No decision here
is an acceptance of G1 or G2.

