# Project plan

## 1. Aim

Build the first reproducible international inventory and harmonised dataset of publicly reported family-justice measures, then extend it to administrative and person-centred outcomes through jurisdiction partnerships.

The project should distinguish:

- **process and performance** — volumes, pending caseload, clearance, waits, duration, adjournments and compliance with time standards;
- **court outputs** — manner of disposal and types of orders;
- **administrative outcomes** — appeals, enforcement, reapplications, return to court and placement events;
- **child and family outcomes** — safety, stability, wellbeing, procedural justice and user experience;
- **system inputs and context** — staffing, expenditure, legal aid, court structure and procedural rules.

## 2. Definition of “complete”

The project should not claim that every outcome is publicly available. A defensible global claim is:

> Every in-scope jurisdiction has been searched under a documented multilingual protocol; every located public source has been catalogued; data gaps and inaccessible or unpublished measures have been explicitly coded; and all extracted observations retain traceable provenance.

The universe should begin with sovereign states and expand to any subnational jurisdiction that has independent responsibility for family justice. Federations therefore require state, province, territory or canton records rather than a single national row.

## 3. Scope

### Core matter types

1. divorce, dissolution and nullity;
2. private-law parenting, custody, residence, contact and parental responsibility;
3. public-law child protection, care and dependency;
4. civil family-violence and protection-order proceedings;
5. child and spousal maintenance or support;
6. property and financial relief following relationship breakdown;
7. adoption, guardianship and kinship care;
8. parentage and selected assisted-reproduction matters;
9. international child abduction, access and cross-border child protection.

Juvenile delinquency, probate and general domestic violence criminal proceedings should be tagged as adjacent domains and included only when they are inseparable from the reporting system or a specific research question.

### Time horizon

- Minimum pilot history: the most recent five reporting years.
- Preferred history: 2010 onward where definitions are stable.
- Preserve breaks in series rather than back-casting through them.

## 4. Work packages

### WP0 — Founding charter and governance (weeks 1–6)

- Appoint a small steering group, methods group and paid lived-experience/child-rights advisory group.
- Agree the project charter, core questions, publication principles and conflict-of-interest policy.
- Decide the institutional host, repository ownership, domain name, licensing and long-term preservation arrangements.
- Adopt the version 1.0 matter-type and indicator ontologies.
- Confirm that the public repository will contain aggregate data only.

**Gate:** signed charter, named data custodian and approved methods handbook.

### WP1 — Twelve-jurisdiction pilot (weeks 4–16)

Use a deliberately heterogeneous pilot:

- Australia;
- England and Wales;
- New Zealand;
- Singapore;
- British Columbia, Canada;
- one large and one smaller United States state;
- Spain;
- Brazil;
- India;
- Mexico;
- South Africa.

This tests federal and unitary systems, common-law and civil-law systems, API and dashboard sources, spreadsheets, HTML and PDF reports, and English plus several non-English languages.

Tasks:

- map each court and agency responsible for family matters;
- search official sources and complete a jurisdiction profile;
- ingest five years of high-priority measures;
- crosswalk local case types and measures;
- double-review a sample of at least 20% of extracted observations;
- publish a pilot comparability report, including failed comparisons.

**Gate:** at least 90% of pilot sources have working provenance; all gold-layer measures pass the comparability rules.

### WP2 — Global source census (months 4–10)

- Create records for all sovereign states and separate subnational court systems.
- Search official judiciary, justice ministry, statistics-office and open-data sources in local languages.
- Search annual reports, statistical yearbooks, parliamentary accountability reports, budget papers, performance plans and court dashboards.
- Add relevant international and regional sources.
- Record “no public family-specific source located” after a second reviewer checks the search log.
- Contact court administrations or justice ministries using a standard data enquiry where public sources are absent or ambiguous.

**Primary output:** a public atlas of data availability, publication frequency, machine-readability and measure coverage.

### WP3 — Reproducible acquisition and extraction (months 5–12)

- Build automated connectors for stable APIs, CSV/XLSX downloads and HTML tables.
- Use controlled manual extraction for complex PDFs and interactive dashboards.
- Store retrieval date, checksum, source version, query parameters and table/page/cell provenance.
- Detect source changes and broken URLs automatically.
- Retain source-native labels and definitions alongside translated text.

**Rule:** scraping must respect access controls, terms of use, rate limits and confidentiality restrictions. Raw documents are redistributed only where licensing permits.

### WP4 — Harmonisation and first analytical release (months 7–14)

- Produce bronze, silver and gold data layers.
- Apply case-type, procedural-stage and indicator crosswalks.
- Grade comparability at observation level.
- Standardise units only where the underlying clocks are compatible.
- Publish country/jurisdiction profiles and metric-specific comparisons.
- Do not publish an omnibus league table.

**First release products:**

1. global source register;
2. methods and data-quality handbook;
3. harmonised core dataset;
4. interactive data-availability map;
5. 12 pilot jurisdiction profiles;
6. thematic report on timeliness and backlog reporting.

### WP5 — Outcomes extension (months 12–24)

Routine court reporting rarely captures downstream family outcomes. This work package therefore builds a second evidence stream:

- catalogue court-user surveys, legal-needs surveys, programme evaluations and cohort studies;
- identify administrative datasets that permit lawful linkage to child protection, education, health, social security or enforcement data;
- develop standard outcome definitions for return to court, compliance, safety recurrence, placement stability and user-reported procedural justice;
- negotiate data-sharing partnerships separately from the open aggregate repository;
- publish study metadata and aggregate results, not disclosive records.

### WP6 — Maintenance and institutionalisation (from month 12)

- Establish quarterly automated checks and annual full jurisdiction reviews.
- Version every release and issue a DOI-backed archive.
- Maintain a public corrections log.
- Invite national correspondents to verify profiles without giving any institution veto over independent analysis.
- Run an annual methods workshop and a biennial international family-justice data report.

## 5. Common data model

Every observation should identify:

- jurisdiction and subnational unit;
- reporting institution and court level;
- original and harmonised matter type;
- original and harmonised measure;
- start event and end event for duration measures;
- statistic type: count, mean, median, percentile, rate or proportion;
- unit and denominator;
- reporting period and cohort basis;
- inclusion and exclusion rules;
- geographic and demographic strata;
- source ID and exact provenance;
- extraction method and reviewer;
- quality grade and comparability tier.

## 6. Minimum viable international indicator set

The first comparative release should prioritise measures most often obtainable and most interpretable:

1. incoming matters;
2. resolved matters;
3. pending matters;
4. clearance rate;
5. age distribution of pending matters;
6. median filing-to-disposition time;
7. mean filing-to-disposition time, retained separately;
8. proportion completed within the jurisdiction’s time standard;
9. ready-to-first-available-hearing wait;
10. filing-to-first-substantive-hearing wait;
11. adjournment/continuance rate;
12. self-representation rate;
13. mediation referral and settlement rates;
14. consent versus contested disposition;
15. appeal, enforcement or return-to-court rate where available.

All other measures remain valuable, but should initially be descriptive unless definitions can be aligned.

## 7. Quality and comparability framework

### Source quality

- **A:** official, machine-readable data with definitions and stable identifiers;
- **B:** official tabular publication with adequate definitions;
- **C:** official narrative or dashboard requiring substantial interpretation;
- **D:** credible research or non-government source;
- **E:** secondary report, unverified or insufficiently documented.

### Comparability

- **Tier 1:** same matter type, clock, statistic, cohort and denominator; direct comparison reasonable.
- **Tier 2:** transparent transformation or restricted interpretation required.
- **Tier 3:** descriptive comparison only.
- **Tier 4:** not comparable; retained for source mapping and local analysis.

## 8. Repository and technical architecture

- Git-based public monorepo for code, schemas, metadata, documentation and redistributable aggregate data.
- Object storage or preservation repository for large or licensed raw files; the Git repository holds manifests, checksums and access links.
- CSV for human-edited registers; Parquet and DuckDB for analytical releases.
- JSON Schema for structural validation.
- Python ingestion and validation pipelines.
- Static documentation/dashboard generated from the same versioned data.
- Continuous integration for schema checks, duplicate IDs, broken links, date validity and source-change alerts.
- Tagged releases with semantic versioning and an archival DOI.

## 9. Governance

### Steering group

Family-law judiciary/court administration, comparative law, statistics, child rights, family violence, economics, data engineering, open science and lived experience.

### Methods group

Owns definitions, crosswalks, comparability rules and revisions. Decisions are published with rationales.

### Jurisdiction correspondents

Local experts verify institutional maps, translations and procedural definitions. They do not alter extracted findings without a documented evidence trail.

### Independence safeguards

- public methods and change logs;
- declared funding and conflicts;
- reproducible calculations;
- separation of source verification from policy interpretation;
- paid participation for people with lived experience;
- no public identification of children, parties or small cells.

## 10. Staffing and indicative resource envelope

### Lean 12-jurisdiction pilot

- project lead: 0.3–0.5 FTE;
- programme/research manager: 1.0 FTE;
- comparative family-law researcher: 0.8 FTE;
- data engineer: 1.0 FTE;
- data/research analysts: 1.5–2.0 FTE;
- statistician/methodologist: 0.3 FTE;
- multilingual reviewers and advisers: commissioned.

Indicative Australian-dollar envelope: **A$500,000–A$900,000**, depending on institutional overheads and the amount of manual extraction and translation.

### Credible first global release

A 12–18 month programme generally needs 5–8 core FTE plus paid jurisdiction reviewers, translation, legal advice, infrastructure and dissemination. Indicative envelope: **A$1.5–A$3.0 million**.

These are planning ranges, not quotations.

## 11. Key risks and controls

| Risk | Control |
|---|---|
| “Family court” means different things | Use matter type, institutional map and court level as separate fields. |
| Mean, median and prospective waits are mixed | Store statistic and start/end events explicitly; prohibit automatic pooling. |
| Federal systems are collapsed into one number | Model subnational jurisdictions as first-class units. |
| Data disappear or dashboards change | Retrieval dates, checksums, archived releases and change detection. |
| Copyright or terms prevent redistribution | Store metadata and provenance; keep controlled raw copies only when lawful. |
| Poor translation changes meaning | Preserve original labels; require local-language review for gold data. |
| Outcomes are confused with orders | Maintain separate process, output, administrative-outcome and person-outcome domains. |
| Rankings create misleading incentives | Publish measure-specific profiles and comparability grades before any benchmarking. |
| Global South is under-represented | Paid regional leads, multilingual searches and explicit coverage targets. |
| Small-cell or sensitive data create harm | Aggregate-only public release, suppression rules and ethics review. |

## 12. First 90 days

### Days 1–30

- confirm founding group and host;
- approve scope and governance;
- freeze indicator dictionary v0.1;
- establish the repository, issue workflow and data licence approach;
- create the 12 pilot jurisdiction records.

### Days 31–60

- complete institutional maps and source searches for six pilot jurisdictions;
- ingest at least two source families end-to-end;
- test provenance, validation and source-change workflows;
- convene the first methods review.

### Days 61–90

- complete all pilot source registers;
- publish the first data-availability map;
- release a small, fully reproducible timeliness dataset;
- document every non-comparable measure and revise the ontology;
- prepare the global census work allocation and external engagement pack.

## 13. Success criteria for the first public release

- 100% of in-scope jurisdictions have a coverage-status record.
- At least 90% of located official sources have valid URLs, retrieval dates and provenance.
- Every gold observation has a source-quality grade and comparability tier.
- All transformations are reproducible from bronze to gold.
- At least two independent reviewers reproduce a sample of published indicators.
- The project publishes data gaps as prominently as available data.
- External users can download the source register, indicator dictionary and harmonised data without proprietary software.
