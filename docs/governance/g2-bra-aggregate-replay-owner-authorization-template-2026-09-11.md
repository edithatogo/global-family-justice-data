# BRA aggregate replay owner-authorization template

This is a template, not an authorization record. It must not be copied into
the evidence register as accepted evidence until the sole owner has completed
and signed the exact fields below.

## Required decision wording

> I authorize execution of packet `G2-BRA-AGGREGATE-REPLAY-20260911-01`,
> SHA-256 `4620b15a9b96c8b9a66429ebff63d7f770c1b89b80b346c306f06541edb64855`,
> using exactly one HTTPS POST to the bound endpoint, zero retries and zero
> redirects. I authorize restricted ephemeral response handling only; no raw
> response or source bytes may be retained. Publication, release, rights
> clearance, Gold promotion and G2 passage remain unauthorized. Any transport,
> identity, schema, size, digest, prohibited-data or ambiguity failure
> terminates the lineage and produces a terminal non-retryable receipt. A
> successful receipt returns for semantic review, maturity reassessment and
> separate grouped G2 adjudication.

## Machine-readable fields

```json
{
  "schema_version": "1.0",
  "decision_id": "D-G2-BRA-REPLAY-<owner-chosen-immutable-id>",
  "decided_at": "<owner-supplied ISO-8601 timestamp>",
  "decision_status": "authorized",
  "owner_identity": "<owner-supplied identity>",
  "owner_role": "repository owner and sole accountable decision-maker",
  "packet_id": "G2-BRA-AGGREGATE-REPLAY-20260911-01",
  "packet_sha256": "4620b15a9b96c8b9a66429ebff63d7f770c1b89b80b346c306f06541edb64855",
  "network_access": true,
  "publication": false,
  "release": false,
  "rights_clearance": false,
  "immutable_reference": "<owner-supplied commit or decision reference>",
  "conditions": ["exact packet only", "one call and zero retries", "ephemeral response handling"],
  "reopen_triggers": ["any stop condition", "owner withdrawal", "packet digest drift"]
}
```

Until this record exists and is bound to the packet, the executor must refuse
to access the provider. The template does not authorize network access.
