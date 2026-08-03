# G2 agent-panel re-extraction control — 2026-08-03

This packet implements the repository-owned re-extraction and concordance
control using role-separated analyst agents. It is a technical rehearsal and
does not claim independent assurance or real-source pilot evidence.

## Control

1. Freeze the input manifest and record its SHA-256.
2. Run a separate extraction path over the same synthetic pilot fixture.
3. Compare row identifiers, values, denominators, clocks and suppression flags.
4. Record every difference and disposition in a digest-bound report.
5. Panel roles review the diff for methods, quality, rights/privacy and
   adversarial failure modes.

## Boundary

The current packet demonstrates the control path only. It does not satisfy the
G2 real-pilot requirement for independent re-extraction, accountable methods
adjudication, rights/security clearance or gate acceptance. Real-source rows
remain pending or quarantined until their receipts and reviews exist.

## Required real-pilot promotion evidence

- source-edition receipt and checksum;
- two separately produced extraction outputs;
- row-level diff and concordance threshold;
- methods-owner adjudication;
- rights/privacy/security disposition;
- owner decision bound to the complete packet.
