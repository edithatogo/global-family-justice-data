# Non-substitutable evidence intake register — 2026-08-03

This is an execution register, not evidence itself. A row can move to
`received` only when the stated receipt, identity/role, scope, date and digest
are present. `panel_advice` is advisory and never satisfies an authority field.

| ID | Gate | Primary route | Triangulation | Required receipt | Status | Fallback |
|---|---|---|---|---|---|---|
| EXT-GOV-001 | G1 | Owner packet acceptance | RACI/charter consistency panel | immutable owner reference and packet digest | pending_authority | retain conditional G1 |
| EXT-MTH-001 | G2 | Methods/accountable adjudication | panel re-extraction and row diff | adjudication record bound to frozen manifest | pending_authority | quarantine disputed measures |
| EXT-RGT-001 | G2/G3 | Exact licence/terms or permission | official terms plus edition manifest | edition rights decision and SHA-256 | pending_authority | metadata/citation-only |
| EXT-COV-001 | G3 | Named local/regional verification | second map/search review | reviewer identity, scope, date and receipts | pending_authority | partial coverage |
| EXT-COV-002 | G3 | Source-language second review | negative-finding/access audit | search-log rows and review ledger | pending_review | mark inaccessible/incomplete |
| EXT-ENQ-001 | G3 | Existing mailbox response monitoring | delivery/autoresponse receipt | response or dated no-response closure | pending_response | transparent no-response closure |
| EXT-OPS-001 | G5/G6 | Host/archive/signing commitments | restore rehearsal and custody receipt | named service, archive and signing records | pending_authority | private unsigned candidate |
| EXT-PAR-001 | G4/G6 | Consent/safeguarding protocol | panel red-team and comprehension check | consent, safeguarding, staff and funding records | pending_authority | synthetic rehearsal only |

## Intake controls

- No outbound message is sent without explicit owner approval for the exact
  recipient list and content.
- Every received item is stored as a redacted receipt where personal data is
  unnecessary, then hashed and linked to the relevant evidence ID.
- Contradictory or incomplete evidence is quarantined; it is never silently
  upgraded by panel consensus.
- The owner adjudicates each authority field after panel options and rationale
  are recorded.
- Gate status is rebuilt after each accepted receipt; no receipt alone promotes
  a gate.

## Next executable order

1. Run the role-separated panel against the current digest and generate the
   G1/G2 contradiction and gap report.
2. Prepare (but do not send) exact enquiry packets and recipient manifests.
3. Recheck existing mailbox responses and log closures.
4. Capture public exact-edition terms and update the rights queue.
5. Rebuild the pilot evidence bundle and present the owner adjudication packet.
