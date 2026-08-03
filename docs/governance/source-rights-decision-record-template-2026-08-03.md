# Source rights decision record template — 2026-08-03

Use one record per exact source edition. This template does not grant rights;
it captures an accountable decision or a transparent deferral.

## Required fields

| Field | Value |
|---|---|
| Source ID | |
| Jurisdiction | |
| Edition/title and period | |
| Manifest path | |
| Payload SHA-256 | |
| Terms/licence URL | |
| Terms retrieval date | |
| Rights classification | `open_licence_verified`, `permission_required`, `unknown`, `restricted` |
| Preservation permitted | `yes`, `no`, `unknown` |
| Redistribution permitted | `yes`, `no`, `metadata_only`, `unknown` |
| Attribution requirements | |
| Accountable rights authority | |
| Decision date | ISO date |
| Immutable reference | |
| Conditions/expiry | |
| Status | `accepted`, `deferred`, `rejected` |

## Decision rules

- A public URL or download link is not a rights decision.
- Government origin may be treated as a project-policy presumption only; it
  never overrides explicit third-party, database, contractual or edition-
  specific restrictions.
- Rights attach to the exact edition and retained bytes, not merely a source
  family or institution.
- `unknown`, `restricted` or `permission_required` keeps redistribution
  disabled and routes the item to metadata/citation-only or quarantine.
- A panel recommendation may inform the decision but cannot provide legal
  authority.
- Any changed bytes, terms or edition invalidates the record and requires a
  new hash-bound decision.

## Verification checklist

1. Recompute the payload hash from the retained file.
2. Verify the manifest path and edition identity.
3. Check terms at the recorded URL and preserve a redacted receipt.
4. Confirm the decision authority and immutable reference.
5. Update `docs/governance/source-rights-review-queue.csv` and the source
   register without upgrading unresolved statuses.
6. Regenerate `MANIFEST.sha256` and rerun Conductor validation.
