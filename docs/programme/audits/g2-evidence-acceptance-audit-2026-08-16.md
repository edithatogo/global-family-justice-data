# G2 evidence-acceptance audit — 2026-08-16

Scope: offline audit of `WI-G2-01` through `WI-G2-08`. No candidate URL,
source content, network service, frozen successor design, authority record or
programme register was changed.

## Bound inputs

| Input | SHA-256 |
|---|---|
| `programme/work_items.csv` | `3dce2d5d6b115d3d158248cb1b12798e0665e08b1fd2dfd76f12fc237347a325` |
| `programme/evidence_register.csv` | `554828703d51f449b16272627b89b4fa60cfa647db2edc439247e773632f2e9d` |
| `config/stage_gates.toml` | `87b0d89d5197d3bc54fefeeb4e902c2620963ea7661a7318068707d5d5999245` |
| `docs/programme/generated/status.md` | `f6f3b168c561d7ba49e71fd3c1a1859fdd423c97257f1cb904d6df6151c28418` |

The live offline calculation reports G2 `blocked_by_maturity`, 4/13 controls
complete, all eight required work items not accepted, and evidence-assured
maturity L1 below the required L2.

## Work-item audit

| Work item | Work status | Criterion evidence state | Finding and required acceptance action |
|---|---|---|---|
| `WI-G2-01` / `G2-C01` | `in_review` | `E-PILOT-CENSUS` is `draft`; file SHA-256 `a81bbdc101d5caf7d8bb2ec95cdefd26cfe180a1b9c3438a5d3ea42cf4f79f28`; register digest blank | Keep unaccepted. Complete and review the bounded pilot maps, logs and coverage states; bind the final digest; then seek owner acceptance. |
| `WI-G2-02` / `G2-C02` | `in_review` | `E-PILOT-ACQUISITION` is `in_review`; declared and actual SHA-256 `6e4817e166b05c898a5bb13c3d194d6452d430e82e35a3ee2ea87f38d59d9267` | Keep unaccepted. The record itself says real API and reproducible HTML/dashboard receipts are missing. |
| `WI-G2-03` / `G2-C03` | `done` | `E-PILOT-PIPELINE` is accepted and correctly bound at `704b3d0e6c9d2cf2ab30e937d97393122e3c62371864f098bcba50ba3853454d`; `E-CLEAN-BUILD` is `in_review`, has blank registered digest, and its file hashes to `ec8246b0d58ce8b4d18c22a5679673a007e287a4fa23eb90a72456e9b81595e8` | `done` correctly means implementation completed, not acceptance. Do not accept it yet: the mandatory second evidence record explicitly lacks real frozen-pilot and accountable acceptance evidence. When that run exists, replace or complete its evidence record with the exact run artifact and digest, accept the evidence, move the item `done -> in_review -> accepted`. |
| `WI-G2-04` / `G2-C04` | `in_review` | `E-PILOT-REVIEW` is `in_review`; declared and actual SHA-256 `65147505740202c429687e961feee9bc8a7ce4df4dbddad60858aff31d0e0c7d` | Keep unaccepted. The bound record preserves a failed calibration and quarantine, not a passing review outcome. |
| `WI-G2-05` / `G2-C05` | `in_review` | `E-PILOT-METHODS-ADJUDICATION` is `draft`; file SHA-256 `e2404ecbc7c716af18682db9435504ca60723fe81dff08415da9ab5ba2f1a776`; register digest blank | Keep unaccepted. Final methods-panel advice and digest-bound owner adjudication are absent. |
| `WI-G2-06` / `G2-C06` | `in_review` | `E-PILOT-RIGHTS-SECURITY` is `in_review`; file SHA-256 `12fc259e3d4826b37c9a15cabf81d35fc300e0efc3b6790415e51c87519b365d`; register digest blank | Keep unaccepted. The generic control packet is not a completed source-specific finding set or owner adjudication. |
| `WI-G2-07` / `G2-C07` | `in_review` | Gate criterion requires only `E-PILOT-INDEPENDENT-ASSURANCE`, currently `in_review` and correctly bound at `65147505740202c429687e961feee9bc8a7ce4df4dbddad60858aff31d0e0c7d`. The work item additionally maps seven design/lineage records, including two `expired` records. | Keep unaccepted. Correct the mapping before eventual acceptance: expired or historical lineage records cannot satisfy the work-status acceptance guard and must not be converted to accepted. Retain them as immutable supporting lineage, but remove them from the work item's acceptance-bearing `evidence_ids`; align that field with `G2-C07`'s primary acceptance evidence, or add only a final successful successor record that is expressly acceptance-bearing. |
| `WI-G2-08` / `G2-C08` | `done` | `E-PILOT-OPERATIONS-REHEARSAL` is accepted; declared and actual SHA-256 `03931cb42a59ab07dc2c2a6c65c8ea8fcd83ee9276ceeed15b339c272a83968c` | This is the sole current status inconsistency. The exact G2 criterion asks for rehearsal, and its only evidence is accepted. Live service authority belongs to later gates and should remain a limitation, not block this G2 work item. Move `done -> in_review -> accepted` with an audit note preserving the synthetic/private scope and no-release boundary. |

## Register inconsistencies and recommended changes

1. **Actionable now — `WI-G2-08`:** change the work status through the valid
   two-step state-machine path `done -> in_review -> accepted`. Do not alter the
   accepted evidence or imply live operations, publication or release.
2. **Actionable before eventual `WI-G2-07` acceptance:** narrow its
   acceptance-bearing evidence mapping. The current mapping includes
   `E-PILOT-HOLDOUT-DESIGN` and `E-PILOT-HOLDOUT-METADATA-INTAKE`, both
   `expired`; the Conductor correctly refuses to accept a work item unless
   every mapped evidence record is accepted or waived. Historical failed,
   expired, design and stop evidence should remain referenced in notes or an
   evidence index, not be relabelled to manufacture acceptance.
3. **Not actionable as acceptance — `WI-G2-03`:** keep the item unaccepted
   until a real frozen-pilot clean-build artifact replaces the generic control
   packet as the acceptance basis for `E-CLEAN-BUILD`. Merely filling its blank
   digest would bind an insufficient document and must not promote it.
4. **Digest gaps are not automatic acceptance gaps:** blank hashes on the
   draft/in-review records for `WI-G2-01`, `WI-G2-03`, `WI-G2-05` and
   `WI-G2-06` accurately prevent accidental acceptance. Populate them only
   when the final acceptance artifact exists; do not bind current placeholders
   as if they satisfy the criterion.
5. Keep `WI-G2-01`, `02`, `04`, `05`, `06` and `07` in review until their
   stated factual evidence is complete. A signed owner decision may accept
   evidence, but cannot replace the absent facts or a passing blind-holdout
   concordance result.

## Expected effect

Accepting only `WI-G2-08` removes one work-item blocker without changing the
truth of any evidence or gate. G2 remains blocked by seven unaccepted work
items, seven non-passing criteria, the L2 maturity floor, open critical/high
risks and the absence of a G2 gate decision. No publication or release follows.
