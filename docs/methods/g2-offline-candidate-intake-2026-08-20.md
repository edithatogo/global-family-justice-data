# G2 offline candidate intake — 2026-08-20

The current G2 campaign has no candidate manifest: every checked-in source
register URL is already in the complete cumulative exposure chain. This
repository-owned intake guard prepares the next factual-evidence boundary
without discovering, fetching, opening or assessing a source.

Use `scripts/validate_g2_candidate_intake.py --input <repository-relative-file>`
only with metadata already placed in the repository. The input must conform to
`data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/schemas/g2_evidence_campaign_candidate_intake.schema.json`.

The guard does three things:

1. requires explicit metadata-only, no-network and no-source-content claims;
2. canonicalises each proposed URL and checks it against the current ledger and
   every digest-bound predecessor ledger; and
3. stops the entire intake if any candidate overlaps exposure or if candidate
   identifiers/URLs are duplicated.

A successful result means only that the supplied metadata is non-overlapping
and is ready for a *future* source-specific screen. It does not verify the
publisher or edition; it does not clear rights, privacy, security or disclosure
conditions; and it does not authorize external access or move G2.

This supports the proportional decision policy: once a real non-exposed frame
exists, the owner can make one grouped campaign decision that binds it. Routine
intake validation does not create a sequence of approval requests.
