# G2 BRA aggregate replay execution packet

This packet binds one prospective, aggregate-only DataJud request to the
merged fail-closed adapter. It is preparation evidence, not an execution
receipt. No network request is made by committing this packet.

## Required owner decision

The owner may authorize the exact request in
`data/federation/bra-aggregate-replay-execution-packet-20260911.json` for one
provider call, zero retries and zero redirects. The response must remain in
restricted ephemeral handling; only its digest-bound receipt may be retained
in the repository. The adapter must reject case-level data, schema drift,
approximate or contradictory buckets and any request/response digest mismatch.

Authorization would permit repository-owned replay preparation only. It would
not clear rights, accept semantics, promote maturity, pass G2, publish or
release anything. A failed stop condition terminates the lineage and returns
an immutable failed receipt.

## Current blocker

The adapter is merged and tested, but no fresh response is currently bound to
this packet. Until the exact owner authorization and response receipt exist,
BRA remains `pending_no_bounded_adapter_response` and WI-G4-MED-02 remains
`in_review`.
