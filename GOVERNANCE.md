# Governance framework

## Purpose

Governance exists to protect scientific quality, public value, independence, safety, and continuity. No single funder, court, contributor, or maintainer may control source selection, methods, data approval, and publication.

## Bodies and roles

### Steering group

Sets strategy, approves the annual programme, appoints release authority, secures the institutional home, and protects independence. Membership should cover judicial administration, comparative family law, child rights, family violence, statistics, economics, data engineering, open science, accessibility, and lived experience.

### Methods and standards group

Owns the jurisdiction universe, matter taxonomy, indicator dictionary, procedural-stage vocabulary, quality grades, comparability tiers, suppression rules, evidence-quality methods, and semantic schema decisions. Decisions and rationales are public.

### Data operations group

Owns source discovery operations, acquisition, extraction, transformation, validation, release builds, monitoring, corrections, and preservation.

### Security, privacy, legal, and ethics function

Owns threat modelling, disclosure controls, source-rights decisions, incident response, takedown requests, and the separation between the public aggregate repository and restricted research environments.

### Release authority

Makes the final go/no-go decision against `docs/strategy/V1_RELEASE_CRITERIA.md`. The release authority cannot be the sole build operator or sole data approver.

### Jurisdiction and language network

Local correspondents verify institutional structures, terminology, translations, and source interpretation. Verification is recorded. Disagreement is preserved in notes or decision records rather than silently erased.

### Lived-experience and child-rights advisory group

Shapes outcome domains, harm controls, interpretation, user experience, and dissemination. Participation is remunerated and organised to avoid disclosure, coercion, or retraumatisation.

## Decision rules

- Method and semantic changes require a versioned proposal, evidence, impact assessment, compatibility analysis, and recorded decision.
- Previously released values are never silently overwritten; corrections create a new release and changelog.
- Breaking changes require migration guidance and the appropriate semantic-version increment.
- Funders and participating courts may comment on factual accuracy but do not control analytical conclusions.
- Contributors and decision-makers declare financial, professional, advocacy, and institutional conflicts.
- Material dissent is recorded when consensus is not reached.
- Emergency security/privacy withdrawal may occur before full committee review, followed by retrospective review.

## Separation of duties

At minimum:

- data preparation and final data approval are separated;
- methods approval and release execution are separated;
- security/privacy approval is independent of delivery pressure;
- no person can alone publish a production release;
- critical roles have named deputies.

## Release governance

A stable release requires:

- completed release-readiness record;
- data steward approval;
- methods approval;
- security/privacy/legal approval;
- release manager build record;
- release-authority go/no-go decision;
- public release notes, limitations, quality metrics, and checksums.

Waivers are time-limited, public, assigned to an owner, and never permitted for critical privacy, security, rights, lineage, or reproducibility failures.

## Publication safeguards

- aggregate or non-identifiable metadata only in the public repository;
- minimum-cell and dominance controls where breakdowns create disclosure risk;
- no protected judgments, sealed material, credentials, or data obtained in breach of access conditions;
- context notes accompany comparisons affected by statutory targets, case mix, legal reform, or reporting changes;
- no composite international ranking in v1;
- outcome claims reflect study design and limitations.

## Transparency records

The project should publish:

- charter and terms of reference;
- membership and role register;
- funding and conflicts register;
- methods and decision log;
- release-readiness records;
- corrections, retractions, and incidents at an appropriate level of detail;
- annual coverage, quality, service, and sustainability report.

## Institutional continuity

Before v1, the host must define:

- repository and domain ownership;
- data and archival custody;
- maintainer appointment/removal;
- succession if the host changes;
- preservation if funding ends;
- transfer of security contacts, keys, storage, and operational knowledge.
