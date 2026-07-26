# Critical-state backup and clean-room restore

## Purpose

This control preserves and restores the public repository state needed to rebuild the programme conductor, contracts, tests, methods, seed registers and release tooling. It is a technical rehearsal, not evidence that a production continuity programme has been approved.

## Backup boundary

The default backup includes reviewed public repository inputs such as configuration, programme registers, schemas, source and evidence templates, documentation, examples, fixtures, source code, tests and GitHub workflow definitions. Generated build products, caches, local credentials, restricted source stores and the root repository manifest are excluded.

The archive contains:

- `BACKUP.json`, validated against `schemas/backup.schema.json`;
- `MANIFEST.sha256`, covering every archived payload file;
- the public critical-state payload under one fixed archive prefix.

`BACKUP.json` records the deterministic epoch, file count, required files, patterns and one digest over the sorted payload entry set.

## Safety and integrity controls

Verification occurs before extraction and checks:

- fixed archive prefix and safe relative member names;
- no absolute paths, traversal components, duplicate names or symbolic links;
- bounded entry count and total uncompressed bytes;
- ZIP CRC integrity;
- complete manifest coverage with no extra files;
- SHA-256 for every payload member;
- metadata and bundled schema validity;
- required-file presence and payload-set digest.

Restore uses manual member extraction rather than `extractall`, writes only beneath an empty controlled destination and verifies the restored snapshot before returning success.

## Commands

```bash
gfjd resilience backup \
  --output build/backup \
  --source-date-epoch 1784419200

gfjd resilience verify build/backup/gfjd-critical-state.zip

gfjd resilience restore-rehearsal \
  build/backup/gfjd-critical-state.zip \
  --output build/restore-rehearsal

gfjd resilience verify-restore \
  build/restore-rehearsal/restore-receipt.json
```

The final command rechecks the archive hash, restored manifest, every restored file, metadata and payload digest. Editing either archive or snapshot after the rehearsal invalidates the receipt.

## Stable-v1 evidence still required

Before G6, the project must additionally demonstrate protected and independently administered copies; encryption and key recovery where required; retention and deletion rules; recovery of restricted evidence stores under their rights conditions; timed service recovery; incident escalation; and primary/deputy ownership. The included rehearsal cannot establish those organisational facts.
