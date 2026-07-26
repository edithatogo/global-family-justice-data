# Raw layer

The raw layer preserves source identity and version. It contains source manifests and only those source files that may lawfully be redistributed.

Each source manifest records:

- source ID and source version;
- canonical URL and retrieval recipe;
- retrieval timestamp and operator/job;
- query parameters or dashboard filters;
- original filename, media type, size, and SHA-256 checksum;
- rights review and redistribution decision;
- storage or archival reference;
- source status and supersession history.

Raw inputs are immutable within a release. New source versions receive new manifest entries. Large, restricted, or licence-uncertain files belong in approved object or archival storage, not Git. Restricted person-level data do not belong in this public architecture.
