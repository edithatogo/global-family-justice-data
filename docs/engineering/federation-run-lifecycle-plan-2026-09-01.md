# Federation RunEvent lifecycle and replay association

Status: in progress, repository-owned preparation only. This continues the
federation track; it neither completes WI-G4-MED-05 nor accepts factual execution.
Baseline: signed `e3e206e0a57e2e6d0d7c17cc8f2e09762cf3115e`, merged PR #146,
full local validation and 17 hosted checks passed. Source manifest verified.

## Options and recommendation

Implement a separately versioned, bounded GFJD RunEvent sequence profile and
an exact declared association with regenerated replay evidence. Keep the
existing design-event API unchanged. Schema-only validation would miss ordering,
identity and terminal-state contradictions. Treating generic run metadata as
observed execution would exceed its evidence. A live producer is a later
operational integration, not needed for this offline validation work.

The already retained, unchanged OpenLineage 2-0-2 schema has SHA-256
`69f68bee00b9beac88a87059c0102410e7bb05f3f43c46d02a0409831eceb0d2`.
It requires one START and one COMPLETE/FAIL/ABORT in descriptive text, and permits
OTHER metadata after completion. `eventType` is not schema-required, so the GFJD
profile must require it explicitly. Role-separated advisory review recommends
explicit direction membership, unbound datasets and post-terminal-only association
reporting. These are profile rules, not universal OpenLineage restrictions.

## Frozen sequence contract

`assess_run_sequence(sequence_raw, expected_sequence_sha256, schema_raw)` returns
a deterministic report; `verify_run_sequence` adds the report and recomputes it.
Envelope keys are exactly `contract_version` (`gfjd-openlineage-run-sequence-v1`)
and `events`. Require 2–256 events, at most 1 MiB, shared strict JSON depth/node/
string limits, and a matching lowercase SHA-256. Validate the exact pinned schema
using an explicit local-only registry; no network or resource-loader fallback.

Every event requires eventTime, producer, schemaURL, eventType, run and job;
only optional inputs/outputs are allowed. schemaURL is the pinned root identifier
or that identifier plus `#/$defs/RunEvent`. Producer is bounded HTTPS syntax,
never requested. Run has exactly runId and optionally empty facets. runId is a
canonical lowercase hyphenated UUID, without an invented version requirement.
Job has nonempty namespace/name and optional empty facets. Dataset declarations
have nonempty namespace/name and optional empty facets plus the matching empty
inputFacets or outputFacets only. Reject unknown nested keys and nonempty facets.
Bound each direction to 100 dataset declarations per event; reject duplicate
namespace/name pairs within a direction. Recurrence across events and the same
pair in both directions are allowed, without asserting in-place semantics.

The exact run ID, job namespace/name and producer stay constant. Require a first
START, then RUNNING/OTHER until exactly one COMPLETE/FAIL/ABORT, then only OTHER.
No missing terminal, second START, conflicting terminal or post-terminal RUNNING.
Reject duplicate canonical JSON events. Preserve original input bytes and hash;
compare explicit offset timestamps as nondecreasing UTC instants. Accept at most
six fractional digits; reject unknown -00:00 offsets, leap seconds, invalid dates,
offsets and UTC-conversion overflow. Equal instants are allowed. This precision
limit is a GFJD profile limitation, not a universal timestamp rule.

Report sequence_profile_validated, declared terminal type/index, run/job/producer,
event types and canonical event hashes, dataset membership with indices/types and
post_terminal_only flags, input/schema/compiler hashes and exact limitations.
All observed execution, source truth, full conformance and authority remain
unverified/false. Fixed exceptions must not disclose rejected event contents.

## Frozen replay association contract

`assess_replayed_run` takes the eight existing `prepare_replayed_bundle` arguments,
then sequence_raw, expected_sequence_sha256, binding_raw, expected_binding_sha256.
`verify_replayed_run` adds a report and regenerates it. Use the pinned schema from
the supplied standards bank. Regenerate the complete replayed bundle first;
accept no precomputed manifest, lifecycle report or provenance artifact.

The binding is strict bounded JSON with exactly contract_version
(`gfjd-openlineage-replay-association-v1`), run_id, job_namespace, job_name,
producer, terminal_type, direction, dataset_namespace, dataset_name, object_id,
canonical_id and entity_sha256. It must match the sequence's declared identity
and terminal, and the exact selected replay object/canonical ID/entity digest.
Direction is input or output; require the chosen dataset pair in that direction.
This is an explicit declared association, not proof of job inputs or production.
FAIL/ABORT and post-terminal-only metadata associations must remain visibly
distinguished and never imply successful production. Do not infer semantic
equivalence or ownership from byte equality. Report all other dataset/direction
pairs and scoped objects as unbound/pending.

Bind the sequence, binding, scope, replay, replay-bank and regenerated bundle
digests and component compiler fingerprints. Return metadata only, no source or
event payload copies. Reports have false execution_observed/production_verified
and authority flags. Disclose helper/compiler fingerprint reads; no source loader,
network, signing, publication, rights, maturity or gate acceptance occurs.

## Implementation and validation order

- [~] Sequence schema/profile validator with positive START/RUNNING/OTHER/terminal
  cases, including FAIL/ABORT and post-terminal OTHER; negative types, identity,
  ordering, timestamps, facets, bounds, schema drift and duplicate events.
- [ ] Exact replay association and verifier, with wrong-direction/unrelated replay,
  forged reports, failed-terminal and post-terminal-only association tests.
- [ ] Role-separated review, focused/full validation, implementation ledger,
  exact-head hosted review/CI, signed history-preserving merge and local cleanup.

No new runtime dependency or external input is required. Unsupported facets or
formats fail closed; actual runtime records and full standards coverage remain
separate requirements. Keep actual-config drafts, canonical ownership/reference
checks and remaining standards/partner coverage on the federation queue.
