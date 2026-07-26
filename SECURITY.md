# Security and responsible disclosure

## Security boundary

This public repository is designed for aggregate public data, metadata, documentation, and code. It must not contain identifiable court records, sealed material, credentials, private API keys, or restricted linked datasets.

## Reporting a vulnerability or sensitive data exposure

Do not open a public issue for a vulnerability, exposed credential, or potentially identifying family/child record. Contact the project security role through the private channel published by the institutional host. Until a host is appointed, security reports should be handled privately by the repository owner and recorded in a restricted incident log.

A mature v1 deployment must publish:

- monitored security contact details;
- acknowledgement and triage targets;
- severity and escalation rules;
- coordinated disclosure process;
- emergency takedown authority.

## Maintainer controls

- least-privilege repository and storage access;
- multi-factor authentication for maintainers;
- protected default branch and required reviews;
- no long-lived secrets in code or workflows;
- dependency, code, and secret scanning;
- pinned or reviewed automation dependencies;
- provenance and checksums for release artifacts;
- periodic access review and immediate revocation on role change.

## Data safety controls

- aggregate-only public release;
- disclosure and small-cell review;
- no attempt to re-identify people;
- no public person-level linkage keys;
- documented suppression and withdrawal process;
- source-rights and redistribution review;
- separation of public and restricted research environments.

## Incident classes

- privacy or disclosure incident;
- compromised credential or maintainer account;
- malicious or tampered source/contribution;
- dependency or build-chain compromise;
- material data-integrity failure;
- legal or rights-based takedown request;
- loss of release or backup availability.

The operations runbook must define containment, preservation of evidence, assessment, notification, correction, rollback, and post-incident review for each class.
