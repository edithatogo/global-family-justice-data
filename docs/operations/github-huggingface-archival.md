# Public GitHub and Hugging Face archival boundary

GFJD uses public remote custody as the durable system of record. GitHub is the
public code, contract, manifest and Conductor control plane. Hugging Face is the
primary public source-archive and medallion data plane. Every release-bound byte
object must also have a verified public replica on a provider-separated
persistent service.

Local storage is bounded ephemeral staging only. It is not an authoritative
archive, backup or release source. A staging copy is eligible for deletion only
after two public retrieval receipts verify its size and canonical digest.

## Repository roles

| Repository | Role | Permitted payload |
| --- | --- | --- |
| GitHub `global-family-justice-data` | control plane | code, schemas, public-safe metadata, manifests, lineage, decisions and builders |
| HF `gfjd-source-archive` | B0 source archive | public-safe exact editions, native bytes, WARC/WACZ and capture receipts |
| HF `gfjd-source-catalogue` | catalogue | sources, editions, rights states, availability, negative findings and public locators |
| HF `gfjd-observations` | canonical medallion dataset | B1 Bronze, Silver and accepted Gold configurations |
| HF `gfjd-outcomes-evidence` | evidence product | governed public-safe evidence records and lineage |
| HF `gfjd-extraction-benchmark` | benchmark | synthetic and specifically approved public-safe source-backed cases |
| HF `gfjd-explorer` | Platinum access product | accepted Gold/Platinum outputs only |
| Provider-separated snapshot | preservation replica | exact B0 and immutable release objects with public retrieval receipts |

All roles and canonical relationships must be registered in
`edithatogo/dataset-estate-registry`.

## Publication classes

Public discovery metadata is required for every in-scope source. Exact bytes
are published when they pass archive safety and prohibited-data controls. A
rights state remains visible metadata and does not silently alter source facts.

No public object may contain credentials, tokens, private endpoints, personal
case records, identifying narrative, unsafe contact information or disclosive
small cells. If safe public preservation is impossible, GFJD publishes only a
non-sensitive metadata/tombstone record and does not keep a hidden local
substitute.

Gold and Platinum remain programme-gated even though B0, catalogue, Bronze or
Silver objects may already be public. Public hosting is not Gold promotion,
gate passage or stable release authorization.

## Reproducible public archival sequence

1. Assign stable source, edition, acquisition and snapshot identities.
2. Capture native bytes or WARC/WACZ plus request/response metadata.
3. Run secret, prohibited-data, identifying-content, disclosure, link/path,
   compression and media-type controls.
4. Compute SHA-256, BLAKE3, size and canonical manifest entries.
5. Publish B0 to `gfjd-source-archive` and verify anonymous retrieval.
6. Publish a provider-separated replica and verify the same bytes anonymously.
7. Publish the catalogue, capture and replication receipts.
8. Build B1 Bronze and downstream layers from public B0 objects, recording
   field-level lineage and transformation-code digests.
9. Append changed editions and `supersedes` edges; never overwrite history.
10. Delete bounded local staging only after both public receipts verify.

## Failure and recovery

A single-provider object is `replication_status=pending` and cannot satisfy
preservation maturity or a release-candidate restore gate. Provider loss starts
replication from the surviving public copy. Digest conflict, unsafe content or
missing provenance quarantines the object and all dependent promotions. Public
correction or removal retains a safe tombstone, reason and supersession link.

The complete architecture, contingencies and Conductor maturity path are in
`docs/programme/maximal-public-medallion-federation-plan-2026-08-26.md`.
