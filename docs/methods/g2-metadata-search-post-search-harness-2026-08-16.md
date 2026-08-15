# G2 metadata-search post-search harness

## Scope

This network-disabled harness processes a future registrar bundle only after the
frozen successor verifier passes. It does not execute searches, open result
URLs, inspect candidate or source content, contact anyone, make an owner
decision, or advance G2.

The harness has two terminal routes:

1. produce a digest-bound verification receipt and descriptor-only advisory
   panel input index; or
2. produce a terminal fail-closed stop receipt.

It never edits, repairs, filters, retries, or promotes registrar output.

## Required future inputs

- the exact registrar execution bundle;
- a separate registrar boundary receipt explicitly binding that bundle and
  recording 208 search-provider calls, 208 logical submissions, zero non-search
  network requests, zero URL/file/HEAD/redirect requests, zero contacts, no
  candidate/source content opening, and no violations. It must also bind the
  run ID, execution date, tool and version, query/design/authority descriptors,
  provider configuration digest, complete query-event transcript digest, first
  and last call timestamps, retry count, and cumulative-lineage counts; and
- a complete 209-event registrar log: 208 query-call completion events projected
  exactly from the bundle plus a zero-network, zero-contact, zero-content-access
  boundary-closure event; and
- a post-execution attestation naming the registrar session and run. Its signed
  Git commit must descend from the owner-decision commit and tree-bind the exact
  registrar bundle, boundary receipt, and event-log bytes; and
- the immutable query, design, authority, decision, commit, and historical-stop
  chain already required by the frozen successor verifier.

Absence is not interpreted as zero. A missing or invalid registrar boundary
receipt fails closed.

## Machine controls

`src/gfjd/g2_metadata_search_post_search.py` provides:

- safe repository-relative artifact descriptors with traversal and symlink
  rejection;
- immutable JSON binding verification;
- Git commit-object, signature, ancestry, and tree-blob verification for the
  post-execution attestation;
- complete upstream successor re-verification;
- zero-boundary and zero-contact validation;
- field-by-field reconstruction of the registrar boundary receipt from the
  immutable execution bundle;
- timestamp ordering and future-time rejection;
- deterministic post-search receipt reconstruction;
- deterministic descriptor-only advisory panel input assembly and
  reverification; and
- deterministic terminal stop-receipt construction and reverification,
  including safe-path, digest, schema, future-time and backdating checks.

Schemas:

- `data/methods/g2/G2HOLDOUT-METADATA-SEARCH-POSTRUN-20260816-01/schemas/g2_metadata_search_post_search_registrar_boundary.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-SEARCH-POSTRUN-20260816-01/schemas/g2_metadata_search_post_search_registrar_event_log.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-SEARCH-POSTRUN-20260816-01/schemas/g2_metadata_search_post_search_commit_attestation.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-SEARCH-POSTRUN-20260816-01/schemas/g2_metadata_search_post_search_receipt.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-SEARCH-POSTRUN-20260816-01/schemas/g2_metadata_search_post_search_panel_input.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-SEARCH-POSTRUN-20260816-01/schemas/g2_metadata_search_post_search_stop.schema.json`

All successful outputs remain advisory-only, require an owner decision, and
record `g2_passage: false`.
