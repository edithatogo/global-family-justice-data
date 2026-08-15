# G2 work acceptance and mapping — owner decision packet — 2026-08-16

Decision requested from: repository owner and sole accountable decision-maker

Decision scope:

- A — accept the completed, already evidence-accepted `WI-G2-08` rehearsal;
- B — correct the acceptance-bearing evidence mapping for `WI-G2-07` without
  accepting that work item or its failed/expired evidence.

This packet was prepared offline. It does not authorize network or source
access, accept `WI-G2-07`, pass G2, publish, deploy or release.

## Immutable input bindings

| Input | SHA-256 | Relevant state |
|---|---|---|
| `programme/work_items.csv` | `3dce2d5d6b115d3d158248cb1b12798e0665e08b1fd2dfd76f12fc237347a325` | `WI-G2-07` `in_review`; `WI-G2-08` `done` |
| `programme/evidence_register.csv` | `554828703d51f449b16272627b89b4fa60cfa647db2edc439247e773632f2e9d` | states listed below |
| `config/stage_gates.toml` | `87b0d89d5197d3bc54fefeeb4e902c2620963ea7661a7318068707d5d5999245` | `G2-C07` requires only `E-PILOT-INDEPENDENT-ASSURANCE`; `G2-C08` requires only `E-PILOT-OPERATIONS-REHEARSAL` |
| `docs/programme/audits/g2-evidence-acceptance-audit-2026-08-16.md` | `9980a8ec3532655f3e3886f8d6fe5f70068c28f5e058098ebc25a8a03eda4344` | offline acceptance-mapping audit |
| `docs/operations/pilot-operations-rehearsal-2026-08-03.md` | `03931cb42a59ab07dc2c2a6c65c8ea8fcd83ee9276ceeed15b339c272a83968c` | `E-PILOT-OPERATIONS-REHEARSAL` accepted |
| `docs/methods/g2-real-pilot-packet05-evidence-index-2026-08-15.md` | `65147505740202c429687e961feee9bc8a7ce4df4dbddad60858aff31d0e0c7d` | `E-PILOT-INDEPENDENT-ASSURANCE` remains `in_review`; failed calibration preserved |
| `docs/methods/g2-prospective-blind-holdout-plan-2026-08-15.md` | `5a8bee0524970cc25831461be8c5bb9164ca328907c9090220d9c104d640d5ad` | `E-PILOT-HOLDOUT-DESIGN` expired |
| `docs/methods/g2-blind-holdout-metadata-intake-evidence-2026-08-15.md` | `10f003c6e6892a414f3fccf30da1bd0933dafe91838eb9a08894d8a1f2d48b43` | `E-PILOT-HOLDOUT-METADATA-INTAKE` expired |

The other historical/supporting `WI-G2-07` evidence records are correctly
bound but remain `in_review`:

| Evidence ID | SHA-256 |
|---|---|
| `E-PILOT-STRUCTURAL-PREFLIGHT-DESIGN` | `6483c448e7d6306247395b4fdb72683c410dec89a6fe80a27e20a162e04bc638` |
| `E-PILOT-URL-RESOLUTION-20260815` | `ccc3420c844604a1885a7f192d718acf748197f1a022ec83f9f46c7860c774a7` |
| `E-PILOT-METADATA-EXPANSION-DESIGN-20260815` | `a214693c9ee9175f1fe07250fc835d621b73dbc4a1f8ce0ba2ba9329791748ed` |
| `E-PILOT-METADATA-SEARCH-STOP-20260816` | `41c2a4166546502f9b5f2d5f72fae9fc9a7639866417488a4fcbe9bdd1830142` |
| `E-PILOT-METADATA-SEARCH-SUCCESSOR-DESIGN-20260816` | `1c9b0d144b321f8351a72abc98b65c42d762718a17949e37dd579dcf8d535491` |

## Decision A — `WI-G2-08`

The work item requires rehearsal of the pilot release process, correction path
and artifact restoration. Its sole required evidence is already accepted and
digest-bound. The note properly limits the result to a private synthetic
rehearsal; live service ownership and release authorization remain later-gate
requirements.

### Options

**A1 — accept now through the controlled two-step transition (recommended).**

Move `WI-G2-08` from `done` to `in_review`, then to `accepted`, recording that
acceptance covers only the bound private synthetic rehearsal.

- Benefit: makes work status agree with accepted evidence and the exact G2-C08
  criterion; removes one false work-item blocker.
- Trade-off: readers could overread “accepted” unless the existing synthetic,
  private and no-release limitations remain explicit.
- Contingency: if the evidence digest, work-item definition or Conductor state
  has changed before implementation, stop, regenerate this packet and obtain a
  fresh decision.

**A2 — leave the item `done` until the complete G2 packet is adjudicated.**

- Benefit: minimizes immediate register mutation.
- Trade-off: preserves a known inconsistency and makes a completed accepted
  rehearsal appear unresolved; it does not improve assurance.
- Contingency: revisit immediately before G2 adjudication.

**A3 — require a new rehearsal before acceptance.**

- Benefit: produces fresher evidence if the implementation or artifact has
  materially changed.
- Trade-off: duplicates a valid accepted rehearsal without a present drift
  trigger and delays G2 unnecessarily.
- Contingency: use this option only if hash, control or implementation drift is
  discovered.

### Recommendation and rationale

Approve A1. Evidence acceptance is already recorded, the digest matches, and
the criterion is limited to rehearsal. This decision must not be represented
as live operations, custody, publication or release readiness.

## Decision B — `WI-G2-07` acceptance mapping

`G2-C07` requires one acceptance-bearing record:
`E-PILOT-INDEPENDENT-ASSURANCE`. The work item currently adds seven supporting
design, failed-stop and lineage records to `evidence_ids`. Two are expired.
The Conductor correctly requires every evidence ID attached to a work item to
be accepted or waived before accepting the work item. The present mapping is
therefore structurally incapable of honest acceptance: expired failed-scope
evidence must remain expired and must never be upgraded merely to unblock the
state machine.

### Options

**B1 — align the acceptance mapping with `G2-C07` (recommended).**

Set `WI-G2-07.evidence_ids` to `E-PILOT-INDEPENDENT-ASSURANCE`. Preserve every
other design, stop, expired and successor record as immutable supporting
lineage in the work-item notes and the G2 evidence index. Keep `WI-G2-07`
`in_review`; do not accept `E-PILOT-INDEPENDENT-ASSURANCE` until a successful
prospectively frozen blind holdout passes the approved thresholds and receives
owner adjudication.

- Benefit: makes gate and work acceptance semantics consistent without erasing
  history or weakening evidence.
- Trade-off: the CSV field no longer enumerates all lineage; discoverability
  must be maintained through the evidence index and note.
- Contingency: add a dedicated `supporting_evidence_ids` contract later if
  machine-readable lineage is required, with tests proving that it cannot
  satisfy acceptance.

**B2 — require the primary record plus a new final-successor execution record.**

Remove historical/expired records from the acceptance field, but eventually
map both `E-PILOT-INDEPENDENT-ASSURANCE` and a new final, successful,
acceptance-bearing successor evidence ID.

- Benefit: exposes the successful execution artifact directly in the work-item
  acceptance contract.
- Trade-off: adds coupling and a new register contract before the final
  artifact exists; the primary assurance record should already bind it.
- Contingency: use if the future evidence index cannot provide an independently
  verified binding to the successful execution.

**B3 — retain the mapping and waive or accept expired records.**

- Benefit: no mapping change.
- Trade-off: misstates immutable failed/expired evidence and weakens the
  fail-closed model. Not recommended and not authorized by this packet.

**B4 — retain the mapping and leave the item permanently blocked.**

- Benefit: no mutation and no false promotion.
- Trade-off: prevents legitimate future acceptance even after a successful
  holdout; the block would be a schema-design artifact rather than an evidence
  finding.

### Recommendation and rationale

Approve B1. It preserves all history while separating acceptance evidence from
supporting lineage. The correction is structural only: it does not accept a
result, repair the failed calibration, authorize a successor search, or move
`WI-G2-07` out of `in_review`.

## Precise approval wording

> I approve Options A1 and B1 in the G2 work acceptance and mapping owner
> decision packet dated 2026-08-16.
>
> For `WI-G2-08`, I accept the completed private synthetic pilot release,
> correction and artifact-restoration rehearsal bound to
> `E-PILOT-OPERATIONS-REHEARSAL` and SHA-256
> `03931cb42a59ab07dc2c2a6c65c8ea8fcd83ee9276ceeed15b339c272a83968c`.
> I authorize the controlled transitions `done -> in_review -> accepted`.
> This acceptance establishes only the G2 rehearsal criterion; it does not
> establish live service ownership, provider-separated custody, signing,
> publication, deployment, release readiness or G2 passage.
>
> For `WI-G2-07`, I approve correction of its acceptance-bearing
> `evidence_ids` to `E-PILOT-INDEPENDENT-ASSURANCE`, matching `G2-C07`.
> Historical failed, expired, design, stop and successor-preparation records
> must remain unchanged and referenced as supporting lineage in the work-item
> note and G2 evidence index. They must not be accepted, waived, deleted or
> relabelled to satisfy the work-item state machine.
>
> `WI-G2-07` and `E-PILOT-INDEPENDENT-ASSURANCE` remain `in_review`. Their
> acceptance still requires a successful prospectively frozen blind holdout at
> the approved thresholds, complete digest-bound evidence, role-separated
> agent-panel advice and my separate owner adjudication. This decision does not
> authorize network access, source access, extraction, publication, release or
> G2 passage.
>
> If any bound input hash or status has changed before implementation, stop and
> return an updated packet rather than applying this decision to drifted state.

## Post-decision implementation checks

If the owner approves the wording above:

1. record a separately digest-bound owner decision;
2. verify every binding against the current tree before mutation;
3. apply the two controlled `WI-G2-08` transitions;
4. amend only the `WI-G2-07` acceptance mapping and lineage note;
5. render and check generated Conductor views;
6. run validation and confirm that G2 remains fail-closed;
7. bind the decision, register diff and validation result in the evidence
   manifest.
