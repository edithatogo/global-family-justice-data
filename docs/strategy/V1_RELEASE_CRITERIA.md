# v1.0 release criteria and definition of done

## Status of this document

This is the controlling release-readiness specification for version 1.0. A criterion may be changed only through the documented methods and governance decision process. The release authority must record evidence against every mandatory criterion.

## Meaning of “stable”

Stable means all of the following:

- **semantic stability:** released identifiers and definitions have a compatibility policy;
- **data stability:** published values are reviewed, traceable, and correctable without silent overwrite;
- **technical stability:** releases can be rebuilt from documented inputs in supported environments;
- **operational stability:** named people can monitor, update, correct, restore, and archive the product;
- **governance stability:** decisions, conflicts, funding, and institutional influence are transparent;
- **user stability:** users can understand, cite, download, and interpret the release without private assistance.

Stable does not mean that every source remains unchanged or that every jurisdiction publishes comparable data. It means change and incompleteness are detected, represented, and managed predictably.

## Release decision categories

- **Mandatory:** failure blocks v1.0.
- **Conditional:** may be waived only with a published rationale, owner, risk control, and target release.
- **Advisory:** desirable but not release-blocking.

There is no waiver for identifiable public data, unresolved critical security issues, untraceable gold observations, or the absence of an accountable release owner.

## Gate 1 — Product boundary and governance

Mandatory evidence:

- approved charter and v1 product boundary;
- definitive in-scope jurisdiction universe and federal/subnational rule;
- named steering, methods, data-operations, security, and release-authority roles;
- declared funding and conflicts;
- decision, dispute, correction, retraction, and appeal processes;
- succession plan and at least two trained operators for each critical function;
- published non-goals, including no composite country ranking in v1.

Pass condition: an external reader can identify who decides scope, methods, release, correction, and incident response.

## Gate 2 — Global discovery completeness

Mandatory evidence:

- every in-scope jurisdiction has a registry row;
- every row records status, languages searched, institutions checked, search date, reviewer, confidence, and next review due;
- search logs follow the approved discovery protocol;
- all “no public source found”, “inaccessible”, and “non-government source only” conclusions receive second review;
- federal and devolved systems are represented at the level that controls the relevant family-justice function;
- excluded territories or court systems are listed with rationale.

Pass condition: no jurisdiction is absent merely because data were difficult to locate or institutions were not named “family court”.

## Gate 3 — Source catalogue and preservation

Mandatory evidence for every high-priority source:

- stable source ID;
- publisher and official status;
- source type, matter coverage, measure domains, language, frequency, and period coverage;
- canonical URL and retrieval route;
- last verified and next review dates;
- rights/licence status and redistribution decision;
- checksum or equivalent source-version evidence when a file is acquired;
- archival or preservation reference where lawful and feasible;
- exact dashboard filters, API parameters, table identifiers, or file locations;
- status for active, changed, superseded, unavailable, or withdrawn sources.

Pass condition: another reviewer can locate the same source version or understand why it is no longer available.

## Gate 4 — Ontology and data contracts

Mandatory evidence:

- v1 matter taxonomy, indicator dictionary, procedural-stage vocabulary, units, statistic types, quality grades, and comparability tiers are versioned;
- every public table has a machine-readable schema and human-readable data contract;
- identifier rules and deprecation policy are documented;
- breaking versus non-breaking change rules are documented;
- source-native wording is retained separately from translated and harmonised wording;
- duration measures require explicit start event, end event, cohort basis, and statistic type;
- missing, not applicable, suppressed, not published, and not searched are distinct states.

Pass condition: the schema prevents common false comparisons rather than relying solely on analyst memory.

## Gate 5 — Extraction, transformation, and lineage

Mandatory evidence:

- every silver and gold value has a source ID and exact provenance locator;
- every automated or manual transformation has a stable ID, code or documented rule, version, author/reviewer, and input/output references;
- source-native bronze data or a lawful source manifest is retained;
- manual extraction uses controlled templates and independent checks;
- translated values and labels retain the original text;
- any imputation, aggregation, currency conversion, or unit conversion is explicit;
- transformations are idempotent or otherwise have documented state handling.

Pass condition: all gold values can be reproduced from retained inputs or transparently re-acquired sources.

## Gate 6 — Scientific and data quality

Mandatory evidence:

- structural, referential, temporal, range, unit, duplication, and lineage checks pass;
- every gold observation has second review and an approved comparability tier;
- cross-source totals and published headline values are reconciled where feasible;
- a stratified independent audit covers jurisdictions, languages, source formats, matter types, and extraction methods;
- the audit reaches at least 99% agreement on copied numeric values and required semantic fields after adjudication;
- all material discrepancies are corrected or explicitly excluded;
- quality metrics and known limitations are published with the release;
- Tier 3 and Tier 4 observations are not silently included in direct comparative products.

Pass condition: there is quantitative evidence that the release process is reliable, not only reviewer confidence.

## Gate 7 — Outcomes evidence integrity

Mandatory evidence:

- routine administrative reporting is separated from user surveys, evaluations, cohort studies, qualitative studies, and linked-data research;
- evidence records include population, matter type, setting, design, period, outcome domains, data source, and limitations;
- causal language is not used for descriptive or uncontrolled evidence;
- risk-of-bias or evidence-quality assessment is recorded where synthesis is attempted;
- absence of outcome evidence is distinguishable from an adverse outcome;
- no downstream child or family outcome is inferred solely from throughput or timeliness.

Pass condition: the project can describe what outcome evidence exists without overstating what it proves.

## Gate 8 — Security, privacy, ethics, and legal compliance

Mandatory evidence:

- public repository contains aggregate or non-identifiable metadata only;
- disclosure-risk review and suppression rules are applied to all public breakdowns;
- source rights, code licence, data licence, and third-party restrictions are documented separately;
- threat model covers supply chain, credential exposure, malicious contributions, source tampering, and disclosive data;
- dependency, code, and secret scanning are enabled;
- no unresolved critical security finding remains;
- vulnerability reporting, incident response, takedown, and legal challenge routes are published;
- research involving restricted person-level data is kept outside the public repository under separate ethics, legal, and secure-environment controls.

Pass condition: release does not expose families, violate source rights, or rely on unmanaged credentials or dependencies.

## Gate 9 — Engineering and reproducibility

Mandatory evidence:

- supported runtime and dependency versions are declared;
- clean checkout validation and release build succeed in continuous integration;
- tests cover validators, schemas, transformation logic, packaging, and representative edge cases;
- linting, type checking, and manifest verification pass;
- generated artifacts include version, build time, input versions, schema versions, checksums, and release notes;
- deterministic output is used where practical; any unavoidable non-determinism is documented;
- prior release artifacts remain available and immutable;
- at least one independent clean-room build reproduces the candidate release.

Pass condition: the public release is a build result, not a manually assembled folder.

## Gate 10 — Product, documentation, and accessibility

Mandatory evidence:

- data are downloadable without proprietary software;
- README, methods handbook, data dictionary, schema documentation, jurisdiction profiles, citation instructions, licensing, limitations, and worked examples are complete;
- user-facing pages identify release version and data currency;
- charts and tables expose underlying values and definitions;
- public interfaces meet the host’s adopted accessibility standard;
- terminology avoids implying direct comparability where none exists;
- at least two users outside the core team complete a documented usability test.

Pass condition: a technically competent new user can obtain, interpret, cite, and reproduce a core result.

## Gate 11 — Operations, resilience, and support

Mandatory evidence:

- release, monitoring, source-change, correction, retraction, rollback, backup, restore, and disaster-recovery runbooks exist;
- backup and restore have been tested against the candidate release;
- source freshness and pipeline failure signals have named owners;
- support channels and response targets are published;
- severity levels and escalation routes are defined;
- a correction rehearsal and a rollback rehearsal have been completed;
- two consecutive release-candidate builds complete without critical regression;
- a post-release review date and ownership are recorded.

Pass condition: the project can recover from foreseeable failures and correct data without improvising.

## Gate 12 — Sustainability and preservation

Mandatory evidence:

- an institutional home or binding preservation arrangement exists;
- code, metadata, data, and documentation are archived together with a persistent identifier;
- maintenance resources cover at least two planned post-release review cycles;
- key-person dependencies and regional/language gaps have mitigation plans;
- service and data-refresh commitments are realistic and published;
- adoption, citation, correction, coverage, and user-feedback measures are defined.

Pass condition: v1.0 is not an unfunded one-off publication.

## Defect thresholds

- **Severity 1 — critical:** privacy breach, source-rights breach, unreproducible release, material systemic data corruption, compromised credentials, or misleading comparison likely to cause harm. Zero permitted.
- **Severity 2 — high:** material error affecting a jurisdiction, indicator family, or core feature; broken primary download; failed restore; unsupported schema migration. Zero permitted at release unless the affected output is removed.
- **Severity 3 — moderate:** bounded error with workaround and no material effect on conclusions. May be accepted only with published limitation and assigned correction.
- **Severity 4 — low:** editorial, cosmetic, or minor documentation issue. May be scheduled after release.

## Required release evidence pack

The v1.0 tag must link to:

1. signed release-readiness record;
2. coverage and quality metrics;
3. methods version and schema versions;
4. audit summary and resolved findings;
5. privacy, legal, and security sign-offs;
6. clean-room build record;
7. backup/restore and correction-rehearsal records;
8. release notes and known limitations;
9. checksums and build metadata;
10. archival persistent identifier;
11. named operational owners and next review dates.
