# Hosted metadata repair review — 2026-09-05

## Actual registry and bounded correction

The registry is the public Hugging Face dataset
`edithatogo/dataset-estate-registry`, not a GitHub repository of that name.
Its pinned revision is `2e85d5b56162d532caaa37c7d9f6a30e63621204`.
The catalog already contains four GFJD entries with stale private/scaffold states
and absent origin references. The source archive is unregistered.

`scripts/prepare_hosted_metadata_corrections.py` prepares four factual corrections
and one source-archive addition. All 47 unrelated entries are preserved. It binds
the input catalog SHA-256 `edf71865933c31b3047043db8844d7ea3edf54e546323e6793fe681cd2d0f26f`
and schema SHA-256 `92220ad58029e4d21ca3fb5e73c8ea8e45576d9b6ff712292ecbf57ed90b3a6f`.
Draft 2020-12 validation with date-time format checking passes.

The actual registry validator was inspected before execution. Its live Hub
inventory check reports 76 datasets versus 52 registered after the GFJD repair,
with 24 unrelated missing registrations and no stale entries. Its duplicate-ID,
canonical-reference and allowed-role checks raise no errors. This bounded change
cannot claim whole-estate reconciliation. The unrelated records should be
addressed in their owning projects.

Publish only `catalog.json` with parent revision matching the pinned revision.
Re-query the remote commit and retrieve the exact revision anonymously to verify
its digest and the five GFJD records. Preserve the prior catalog in the pinned
history. Rollback is a new commit restoring the four prior entries and removing
only the added GFJD entry, after checking for intervening changes; never reset
or overwrite another project's changes. Registration is descriptive metadata,
not interoperable product acceptance or gate passage.

## Source-archive policy correction

The current archive revision remains
`3f534c86d7b72978963049f6007df1dccd27e601`. Its inventory claims all six sources
are approved for public archive reuse. The canonical inventory instead records
unknown/review-required rights. The 2026-09-04 owner disposition grants no new
source-byte or derived-data publication and retains metadata/citation handling.
The correct repair must not manufacture a new rights finding.

Recommended minimal correction: replace the hosted inventory with the exact
canonical inventory and update its README to describe that file as the current
policy record, explaining that `local_metadata_only` is its historical policy
label and does not deny the separately observed hosted source files. The older
`public_b0_safety.json` must remain unchanged and be explicitly labelled a
historical byte-safety receipt bound to the prior inventory, not a current
rights or publication approval. Do not change its input hash to imply a rerun.
Preserve all prior artifacts in commit history, compare the six source identity
fields before publication, and use the exact current parent revision.
This corrects public policy claims; it does not remove previously hosted bytes
or resolve their rights. Any removal must be treated as a separate action.

## Explorer review

The owner-authenticated Space remains private at
`e3d9e838765c70d9d070d9d4a0476aa27a638ee4`. Its README, index and stylesheet are
the default static welcome template; no data, script, input collection or
product claims were found in those three exact files. A useful metadata-only
replacement can show project purpose, canonical repository link, current gate
status and the distinction between source records and accepted products.
Do not call the placeholder a functioning data Explorer. The current review
does not change visibility or deploy content.

Only owned-repository metadata/code was retrieved in this review. No source
documents were requested, no remote file was changed, and no rights, product,
release or gate acceptance was asserted.
