# Security and responsible disclosure

## Project security boundary

The public repository is designed for aggregate, publicly reportable family-justice information. Do not submit:

- identifiable or linkable case/person records;
- sealed, protected or unlawfully obtained material;
- credentials, tokens, private keys or access cookies;
- restricted source files whose redistribution is not authorised;
- exploit code or sensitive vulnerability detail in a public issue.

Person-level linkage research, if undertaken, belongs in a separately governed secure environment and is not part of this public repository.

## Reporting a vulnerability or sensitive issue

Until a dedicated private reporting channel is configured by the host, contact the project’s designated security/privacy owner through the host institution and mark the report confidential. Do not open a public issue when disclosure could create harm.

A mature v1.0 must publish and test a private vulnerability/privacy reporting channel before release.

Include, where safe:

- affected version or service;
- issue type and potential impact;
- steps to reproduce using non-sensitive data;
- evidence without personal information;
- suggested containment if known;
- preferred contact method.

## Response objectives

- acknowledge reports within five working days;
- triage critical issues immediately on detection;
- protect reporters acting in good faith;
- preserve evidence and avoid unnecessary collection of sensitive data;
- publish a proportionate incident/correction record after containment;
- rotate exposed credentials and invalidate compromised artefacts/keys.

## Baseline controls on the path to v1.0

- protected branches and reviewed changes;
- least-privilege named accounts and MFA for privileged systems;
- secrets outside source control;
- dependency, secret and artefact scanning;
- rights and disclosure review before publication;
- threat model and privacy/disclosure impact assessment;
- signed/checksummed release artefacts;
- backup, restore and incident exercises;
- no unresolved critical security or privacy finding at release.

See `docs/architecture/v1-architecture.md`, `docs/operations/release-and-operations.md` and `V1_0_RELEASE_CRITERIA.md`.
