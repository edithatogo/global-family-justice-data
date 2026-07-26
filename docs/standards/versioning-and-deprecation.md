# Versioning, compatibility and deprecation

## 1. Version dimensions

The project tracks several related versions explicitly:

- **project release version** — the public bundle, using semantic versioning;
- **schema version** — structural contract for each data product;
- **ontology version** — matter types, indicators, clocks and controlled vocabularies;
- **pipeline version** — acquisition/transformation code used;
- **source edition/version** — publisher release or retrieval snapshot;
- **data vintage** — latest reporting period represented;
- **profile revision** — jurisdiction context document version.

A user must be able to determine all relevant versions from release metadata.

## 2. Project release semantics

### 0.x

Design and contracts may change. Breaking changes are documented but compatibility is not guaranteed.

### 1.x

- **Patch (`1.0.1`)** — corrections, metadata clarifications, security fixes and non-semantic technical fixes. No public contract break.
- **Minor (`1.1.0`)** — additive indicators, jurisdictions, fields or non-breaking product improvements. Existing valid 1.x data remain valid.
- **Major (`2.0.0`)** — breaking schema, identity, ontology or semantic contract changes.

A new annual data vintage does not automatically require a major version.

## 3. Stable IDs

- IDs are never reused.
- Renames do not change IDs.
- Mergers/splits create explicit lineage relationships.
- Retired entities remain resolvable and carry retirement reason/date.
- IDs do not encode labels or mutable hierarchy where avoidable.

## 4. Schema compatibility

In 1.x:

- required fields are not removed or redefined;
- optional additive fields are allowed in minor releases;
- enum additions require consumers to tolerate unknown future values or use version negotiation;
- field-type narrowing is breaking;
- semantic changes to a field are breaking even when JSON/CSV structure is unchanged;
- column order is not a semantic contract unless explicitly stated;
- compatibility fixtures are tested in CI.

## 5. Ontology change

Changes are classified as:

- editorial clarification;
- additive concept;
- mapping correction;
- split/merge with explicit lineage;
- breaking conceptual change.

Every change includes rationale, affected series, migration impact and reviewer approval. Breaking conceptual changes normally wait for v2.0.

## 6. Deprecation

- Announce deprecation in the changelog, schema metadata and documentation.
- Provide a replacement and migration path where possible.
- Maintain deprecated 1.x fields for at least two scheduled minor releases unless security/legal necessity requires faster action.
- Publish the planned removal version.
- Measure use of deprecated API fields only in privacy-preserving aggregate form.

## 7. Corrections and revisions

Publisher revisions and project corrections are distinct:

- a **publisher revision** updates the source edition and records the publisher’s change;
- a **project correction** fixes extraction, classification or transformation;
- a **methods revision** changes interpretation and may require series reclassification.

Released files are immutable. A correction produces a new release and a machine-readable change record linking old and new observations.

## 8. Emergency exception

A breaking 1.x change is permitted only to address an immediate security, legal, privacy or material-integrity risk. It requires:

- executive, methods and technical approval;
- public incident/decision record;
- migration support where practicable;
- explicit compatibility impact;
- expedited move to the next major version if the break cannot be contained.
