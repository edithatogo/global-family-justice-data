# T1 acceptance runbook

This runbook prepares the Scope, ontology and methods track for independent
review. It does not create pilot evidence, methods approval, a contract freeze,
or a stage-gate decision.

## 1. Prepare a fixed review revision

The maintainer records a clean commit, then runs:

```bash
make PYTHON='uv run python' autonomy-full
gfjd governance build --output build/governance --gate-output build/gate-packs
gfjd governance verify --output build/governance --gate-output build/gate-packs
gfjd conductor gate G1
gfjd conductor gate G2
```

Reviewers receive the commit identifier plus the checksum-bound G1 and G2 gate
packs. They must verify each registered evidence file against the corresponding
entry in `programme/evidence_register.csv`; a branch tip, a local test result or
a rendered document alone is not a review record.

## 2. G1 scope and ontology approval

For `E-METHODS-SCOPE` and `E-INDICATOR-FRAMEWORK`, an independent methods
reviewer checks the primary unit, exclusions, controlled vocabularies, clocks,
statistics, count units, denominators and the prohibition on composite rankings.
The reviewer supplies a genuine review reference, date, role and disposition.
Only then may the maintainer record the supplied decision:

```bash
gfjd conductor evidence E-METHODS-SCOPE \
  --status accepted \
  --reviewer "GENUINE INDEPENDENT METHODS REVIEWER ROLE" \
  --reviewed-on YYYY-MM-DD \
  --notes "Immutable review reference"

gfjd conductor evidence E-INDICATOR-FRAMEWORK \
  --status accepted \
  --reviewer "GENUINE INDEPENDENT METHODS REVIEWER ROLE" \
  --reviewed-on YYYY-MM-DD \
  --notes "Immutable review reference"
```

These commands record a decision; they do not replace the independent review.
`WI-G1-02` remains unaccepted until both records are accepted and the wider G1
controls and accountable decision are satisfied.

## 3. G2 pilot adjudication evidence

`E-PILOT-METHODS-ADJUDICATION` is not satisfied by synthetic fixtures or the
presence of a template. Before review, retain real pilot source editions,
preservation checksums, extraction and second-review records, and the exact
comparability audit inputs and outputs:

```bash
gfjd comparability build --input 'data/gold/pilot/**/*.csv' --output build/comparability
gfjd comparability verify --output build/comparability
```

For every material clock, denominator, missingness or ontology question, record
the original definition, adjudication decision, impacted observation/series IDs,
comparability-tier outcome and immutable evidence reference in the review
ledger. An accountable methods lead and an independent reviewer must both review
that packet. Only their supplied evidence can move the T1 record forward.

## 4. G5 contract freeze

The v1 contract freeze occurs only after the preceding gate dependencies are
accepted. It requires an accountable methods decision over the versioned
ontology, methods, identifiers and public contracts, including migration impact
and compatibility baseline. Do not accept `E-V1-CONTRACT-FREEZE` from this
runbook, a draft policy or a local validation run.

## Non-delegable boundary

The maintainer may prepare hashes, deterministic packs, templates and commands.
The maintainer cannot supply reviewer independence, real pilot material, methods
adjudications, accountable acceptance or an external gate decision. Until those
inputs exist, T1 remains implemented but not accepted or archive-eligible.
