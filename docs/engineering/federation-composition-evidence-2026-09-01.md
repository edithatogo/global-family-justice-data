# Fictional federation composition — supporting evidence

Status: repository-owned preparation, in review. This record does not establish
`E-FEDERATED-MEDALLION-REGISTRY`, partner registration or WI-G4-MED-05 acceptance.

## Scope and recommendation

Compose the reference, estate, standards, replay and interface adapters against
the same exact supplied inputs. The bounded fictional exercise covers four
metadata profiles, six estate roles, one replayed entity, one separate declared
Parquet object, two pinned partner contracts and two unavailable interfaces.

Keep component reports and their coverage limits explicit. A single blanket
"federation passed" label would hide pending facts and differing standards
coverage. A scope migration would add compatibility work without resolving those
facts. The selected additive bundle retains prior APIs and checks cross-input
format contradictions before returning any artifacts.

## Evidence and reproducibility

The implementation plan is
`docs/engineering/medallion-federation-preparation-plan-2026-08-31.md`.
The development-only rehearsal is `scripts/rehearse_federation_bundle.py`.
It uses checked-in fictional fixture builders, packaged technical assets and
fictionalised estate configuration, never empirical source acquisition.

The report records input bindings, compiler/fixture hashes, output hashes,
negative outcomes and explicit pending states. Generate and verify with the
repository command `make PYTHON=.venv/bin/python federation-bundle-rehearsal`.
The content-addressed build directory retains earlier reports rather than
overwriting them. A frozen report must be reproduced with its generating source
revision; later compiler changes do not retroactively repair historical evidence.

Preserve the generated fictional metadata bundle alongside its report, checking
the exact file set and every recorded digest. Source and input-bank payloads are
not part of that bundle. This makes the report's output references auditable
without relying on temporary CI artifact retention.

Preserved report: `data/federation/preparation-2026-09-01/report.json`, SHA-256
`e0d65f3d721522319715fc2aea14898c0a56bb8d250cf034b91a3555c4594da6`.
Its sibling `bundle/` preserves all 16 generated artifacts, each matched to the
report's digest map. Neither source bytes nor raw input-bank payloads are stored.
Generating implementation and preserved snapshot are committed at signed
`0462805`; the report's compiler and fixture hashes provide exact byte bindings.
The report proves a fictional rehearsal only; it is indexed separately as
`E-FEDERATION-COMPOSITION-FICTIONAL-20260901`, in review.

Focused execution: 17 composer tests passed in 2.38 seconds; 12 rehearsal tests
passed in 30.25 seconds before adding the preserved-evidence integrity assertion.
Ruff and module mypy passed. The initial interface-report assertion failed before
implementation, as did the composer's mandatory-sidecar test. Role-separated
advisory review of composer, rehearsal and documentation found no actionable
issues. These are agent engineering reviews, not independent assurance.

Full validation, final source revision and exact-head PR/CI delivery are still
pending and will be recorded in the implementation ledger at phase closeout.

The combined composer/rehearsal suite subsequently passed 30 tests in 99.75
seconds, including preserved-evidence integrity and non-acceptance mapping.
The persisted report also passed direct exact recomputation. Separate advisory
review reproduced both output digest maps and found no input-bank/source copies
or acceptance promotion. Project validation passed all 22 checks with zero
errors/warnings. These results do not stand in for the pending full gate or CI.

## Review correction and successor 02

The original source freeze `8699c2e` passed full local validation (1,623 tests
twice, 117.45s/121.70s, 84% coverage) and all 17 hosted checks. Hosted review
then identified that generated JSON/text artifact hashes were missing from the
non-Parquet contradiction set. These successful checks did not prove that
missing case. The original snapshot remains unchanged and is superseded for
current implementation validation, not repaired or promoted retrospectively.

Three new tests reproduced the issue using estate-manifest, provenance and
README hashes with consistently rebound declarations. The guard now includes
base artifacts and composed interface-report/README bytes. All 20 composer
tests pass (2.46s); the rehearsal adds a tenth negative case. Separate advisory
review found the correction adequate and no further actionable issue.

Successor report: `data/federation/preparation-2026-09-01-02/report.json`, SHA-256
`c4ba3dca52c23f51ead58674a8fba95a0d0ed8ffa73ca1b74c8cbf0f6592910e`.
Its 16 sibling bundle artifacts match the report digest map. It is separately
indexed as `E-FEDERATION-COMPOSITION-FICTIONAL-20260901-02`, in review. All original
factual/authority limitations remain. Corrected full validation and exact-head
CI/review are required before PR integration; earlier green results do not count
as validation of the correction.

Corrected focused closeout: all 34 composer/rehearsal tests passed in 43.09
seconds, including both immutable snapshot digest maps and non-acceptance
mappings. Successor 02 passed direct exact recomputation. Ruff and module mypy
passed. The original snapshot has no byte changes in the corrective diff.

## Limits and next evidence

- Parquet format, footer, schema, row statistics and payload digests are not
  verified. Known JSON, XLSX, TOML and other supplied text cannot be relabeled as
  Parquet; unknown hashes remain declarations only.
- Replay establishes bounded deterministic machinery, not real-source truth,
  semantic equivalence, custody or rights. Unselected entities stay pending.
- Partner schemas and reviewed text are pinned references, not executed partner
  services. Archive ownership excludes GFJD; GMA layer meanings are not aliases.
- Standards coverage remains the named bounded profiles, not full conformance.
- The unavailable reimbursement-atlas and dataset-estate-registry interfaces
  remain unavailable; no repository substitute or acceptance is inferred.
- Publication, source access, registration, release, maturity and gate acceptance
  remain unauthorized by this engineering evidence. The owner alone adjudicates
  any later acceptance on actual evidence.

Contingency: preserve missing evidence and unavailable references explicitly,
continue repository-owned validation work, and group factual/authority decisions
after the authorized queue. Do not invent receipts or request routine approvals
for changed test results or digests.
