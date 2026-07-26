# Analytical warehouse and public products

The public build is intentionally portable. A user must be able to inspect the release without a hosted dashboard or proprietary service.

## Warehouse

`gfjd warehouse build` reads the reviewed table contracts in `config/data_contracts.toml`, validates headers and source records, and constructs a deterministic SQLite database. It creates table metadata, useful indexes, and contextual views where the required tables are present.

The sidecar receipt records:

- build version and source date epoch;
- database digest and integrity result;
- input paths, row counts, headers, and SHA-256 digests;
- created tables, views, indexes, and schema metadata.

`gfjd warehouse verify` detects changes to the database, receipt, or any recorded input. Query and export commands open the database read-only, reject mutating statements, and enforce row limits.

## Public product bundle

`gfjd products build` produces:

- source CSV tables copied from controlled canonical inputs;
- JSON API-shaped resources for static hosting;
- the portable SQLite database;
- a Frictionless-style `datapackage.json` with fields and resource hashes;
- an accessible static HTML landing page and catalogue products;
- a machine-readable summary and artifact hash inventory.

`gfjd products verify` checks every declared artifact, data-package resource, checksum, database integrity, and required product. The release builder includes this verified product bundle rather than maintaining a separate publication path.

## Compatibility and correction

Schemas, identifiers, and deprecation rules are governed by `docs/standards/versioning-and-deprecation.md`. Released bytes are immutable. Corrections create a new patch release with a documented change; they do not silently replace an archived release.
