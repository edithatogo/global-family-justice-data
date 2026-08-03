# External blocker snapshot — 2026-08-03

This is a digest-bound implementation handoff for the current Conductor
state. It records what the repository can prepare and what still requires an
accountable external authority or evidence source. It does not accept a gate,
authorize contact, or authorize publication.

## Frozen blocker queue

| ID | Gate/track | Required input | Current assignment | Safe repository fallback |
|---|---|---|---|---|
| EXT-GOV-001 | G1/T0 | Signed charter, ethics/security boundary and decision rights | Governance owner | Retain conditional G1; no promotion |
| EXT-MTH-001 | G2/T1 | Independent methods assurance and owner adjudication | Methods/quality authority | Descriptive-only methods; quarantine disputed measures |
| EXT-COV-001 | G2–G3/T2 | Local/regional verification and institutional maps | Named local reviewer | Partial coverage; no unsupported absence claims |
| EXT-COV-002 | G2–G3/T2 | Second review of multilingual/inaccessible searches | Independent quality reviewer | Preserve `search_incomplete`/`source_inaccessible` states |
| EXT-RGT-001 | G2–G3/T3 | Edition-specific rights and redistribution decision | Rights/legal authority | Metadata/citation-only or quarantine |
| EXT-ENQ-001 | G3/T2 | Responses or eligible no-response closures | Programme owner | Monitor only; follow-up remains draft until explicit send approval |
| EXT-OPS-001 | G5–G6/T8 | Hosting, custody, signing and support commitments | Service/release authority | Local unsigned candidate; no release claim |
| EXT-PAR-001 | G4–G6/T9 | Safeguarding, consent, staffing and funding | Safeguarding/funding authority | Synthetic rehearsal only; no participation claim |

## Scope guard

The GBR-EAW packet is preparation-only. It remains outside the approved
five-candidate G2 scope until the governance owner records a scope decision;
its rights-cleared status must not be treated as pilot acceptance.

## Decision and contact boundary

Agent panels may prepare options, evidence checks and contingencies. They may
not sign, appoint authorities, grant rights, establish consent, authorize an
outbound enquiry, or promote a gate. No outbound contact or public release is
authorized by this snapshot.

The authoritative machine-readable assignments remain in
`docs/governance/external-evidence-blocker-register.csv` and
`config/next_evidence_intake.toml`.
