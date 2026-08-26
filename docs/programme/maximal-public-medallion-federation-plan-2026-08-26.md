# Maximal public medallion and federation plan

Date: 2026-08-26

Owner: repository owner and sole accountable decision-maker

Status: approved direction; implementation evidence remains fail-closed

## Decision and recommendation

GFJD will use a preservation-first medallion architecture with public remote
custody as the system of record. Durable source bytes, metadata, underlying
structured data, transformations and accepted products must not depend on an
offline or local-only copy. Local storage is permitted only as bounded
ephemeral staging and must be removed after two provider-separated public
replicas and their retrieval receipts verify against the canonical manifest.

The recommended topology combines the strongest patterns already used across
the owner's repository estate:

- content-addressed native payloads and WARC/WACZ captures from
  `archive-govt-nz`;
- source-truth and Bronze-maturity separation from
  `global-medicines-atlas`;
- immutable snapshots, replay, supersession and field lineage from
  `reimbursement-atlas`;
- role-separated Hugging Face source-archive, canonical-dataset and immutable
  snapshot repositories recorded in `edithatogo/dataset-estate-registry`.

## Options, trade-offs and contingencies

### Option A — repository-only medallion

Store manifests and all layer outputs in GitHub. This is simple but Git is a
poor store for large source payloads, replayable snapshots and provider-level
redundancy. It is not recommended.

### Option B — one public data host

Use Hugging Face for every payload and product. This is operationally simple
and highly discoverable, but one provider or account event could make the
complete archive unavailable. It is an acceptable temporary bootstrap only.

### Option C — public federated preservation-first medallion

Use GitHub as the control plane, Hugging Face as the primary public data and
distribution plane, and at least one provider-separated public archive such as
Zenodo, Internet Archive or an equivalent persistent repository for every
preserved byte object. This is recommended. It adds manifest and synchronising
complexity but provides the strongest provenance, restoration and federation
model.

If a secondary provider is temporarily unavailable, an object may enter the
public primary archive with `replication_status=pending`; it cannot satisfy
preservation maturity or Gold/Platinum release evidence until the second
replica and anonymous retrieval verification pass. If a payload contains a
credential, prohibited personal information, identifying narrative or unsafe
small-cell data, publication is prohibited: the acquisition must stop or
produce only a safe public metadata record. GFJD will not retain a secret local
substitute for material that cannot enter the public boundary.

## Canonical layers

| Layer | Meaning | Required public artefacts | Promotion boundary |
| --- | --- | --- | --- |
| B0 Preservation | Exact source edition and capture context | Native bytes or WARC/WACZ, request/response metadata, SHA-256 and BLAKE3, media type, byte count, timestamps, edition and supersession identifiers | Acquisition, safety scan and two public custody receipts |
| B1 Bronze | Source-faithful analytical representation | Typed Parquet/JSONL, original labels and locators, extraction contract and receipt | Rebuilds exactly from B0 and retains all source semantics |
| Silver | Canonical harmonised evidence | Normalised Parquet, mappings, bitemporal fields, definitions, exclusions and field lineage | Contract validation, semantic review and explicit quarantine disposition |
| Gold | Accountably accepted aggregate observations | Comparison-eligible Parquet/DuckDB tables, quality and limitations records | Owner adjudication; all quality, disclosure and comparability controls pass |
| Platinum | Federated public products | Croissant/RO-Crate/DCAT metadata, APIs, explorer, knowledge graph, release bundles and immutable snapshots | Accepted Gold inputs and release gate |

Quarantine is an orthogonal state, never a medallion layer. A quarantined
object retains its public-safe metadata and lineage but cannot be promoted or
silently omitted from coverage reporting.

## Public repository estate

1. GitHub `edithatogo/global-family-justice-data` remains the public control
   plane for code, schemas, Conductor state, manifests, lineage contracts and
   reproducible builders.
2. Hugging Face `edithatogo/gfjd-source-archive` becomes the public B0 source
   archive for exact source editions and capture objects.
3. `edithatogo/gfjd-source-catalogue` becomes the public source and edition
   catalogue, including negative findings and unavailable states.
4. `edithatogo/gfjd-observations` becomes the canonical medallion dataset with
   B1 Bronze, Silver and Gold configurations and immutable version tags.
5. `edithatogo/gfjd-outcomes-evidence` remains a separately governed evidence
   product linked through shared identifiers and provenance.
6. `edithatogo/gfjd-extraction-benchmark` contains public-safe synthetic and
   approved source-backed benchmark material, never hidden sealed evidence.
7. `edithatogo/gfjd-explorer` reads only accepted Gold or Platinum releases.
8. Stable releases receive a provider-separated immutable snapshot and, where
   supported, a persistent identifier.
9. Every repository and snapshot is registered in
   `edithatogo/dataset-estate-registry` with its family, role, canonical target,
   rights state, operational status and supersession relationship.

## Federation contracts

All layers use stable jurisdiction, institution, source, edition, acquisition,
observation, transformation and release identifiers. Public manifests expose
DCAT-AP and schema.org/Croissant discovery metadata, RO-Crate packages, PROV-O
and OpenLineage-compatible lineage, and content-addressed zero-copy Parquet
references. Federation with `archive-govt-nz`, `global-medicines-atlas` and
`reimbursement-atlas` must not copy canonical records merely to rename them;
it uses declared ownership, immutable identities and checksum-bound references.

## Controls and stopping rules

- No public object may contain secrets, tokens, private endpoints or prohibited
  personal, case-level or identifying data.
- The aggregate-only GFJD product boundary remains unchanged.
- Every byte object has an exact edition ID, capture receipt, SHA-256, BLAKE3,
  size, media type and public retrieval locator.
- Changed bytes append a new snapshot and an acyclic `supersedes` edge; nothing
  overwrites historical evidence.
- A public catalogue record distinguishes `observed`, `preserved`, `bronze`,
  `silver`, `gold`, `platinum`, `quarantined`, `withdrawn` and `tombstoned`.
- The canonical manifest must reconcile every public replica and medallion
  projection. Missing, conflicting or unverified objects fail closed.
- Anonymous restore samples must retrieve bytes from both providers and
  regenerate downstream layers without relying on a local cache.
- Public removal, correction and takedown preserve a public tombstone,
  supersession reason and non-sensitive audit receipt.
- Fixture, catalogue, archive, transformation, publication and live-service
  evidence remain distinct; success in a later layer never proves an earlier
  layer mature.

## Maturity path

### G3 — preservation foundation

Establish the public B0 archive, complete source and edition metadata, publish
the exposure/rights/safety state, verify dual public custody and operate source
monitoring without a durable local dependency.

### G4 — complete medallion beta

Build B1 Bronze and Silver deterministically from B0, enforce quarantine and
Gold promotion, publish typed Parquet/DuckDB outputs and register the GFJD
estate and federation contracts.

### G5 — release-candidate assurance

Qualify every layer independently, prove anonymous provider-separated restore,
replay corrections and supersessions, verify public-boundary scanning, and
freeze release contracts.

### G6 — stable federated publication

Publish immutable, version-linked Gold/Platinum products, persistent snapshots,
machine-readable federation metadata and complete public provenance. G6 is not
passed merely because source bytes or pre-release layers are publicly hosted.

## Definition of maximal

GFJD reaches the requested maximal archival posture only when every in-scope
source edition has a public catalogue record; every acquired safe payload has
two independently retrievable public replicas; every structured and derived
field is traceable to exact source bytes and transformation code; all layers
can be rebuilt from public artefacts alone; every unavailable, quarantined,
withdrawn and superseded state remains visible; and no unique durable archive
exists only on a local disk.
