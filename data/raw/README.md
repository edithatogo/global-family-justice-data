# Raw layer

The raw layer is immutable and source-faithful.

For each acquired source record:

- keep the original filename;
- record source ID, retrieval date and SHA-256 checksum;
- record licence/access conditions;
- preserve API query parameters or dashboard filters;
- do not edit source files in place.

Large or restricted source files should live in approved object storage or an archival repository. This Git repository should retain a manifest and access/provenance information. Do not commit documents when redistribution is not permitted.
