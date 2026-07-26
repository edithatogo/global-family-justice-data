# Source discovery protocol

## Step 1 — map the system

Identify the bodies responsible for family matters, court administration, official statistics, legal aid, child protection, maintenance enforcement and judicial performance. In federations, repeat this at the relevant subnational level.

## Step 2 — search official domains

Search, in the local language and English where useful:

1. judiciary and court-administration sites;
2. ministry of justice or attorney-general sites;
3. national statistics offices and open-data portals;
4. parliamentary, audit and budget/performance publications;
5. child protection and family service agencies;
6. regional or international bodies;
7. academic and non-government evidence sources.

Suggested local-language concepts:

- family court; family justice; domestic relations; matrimonial;
- divorce; custody; parenting; contact; maintenance; child protection; adoption; protection order;
- caseload; filings; disposals; pending; clearance;
- waiting time; duration; age of cases; time standard;
- annual report; statistics; dashboard; open data; performance;
- user survey; satisfaction; fairness; compliance; enforcement; reapplication.

## Step 3 — record the search

Complete a search log even when nothing is found. Record:

- date and reviewer;
- languages and search terms;
- institutions and domains checked;
- candidate sources and reasons for exclusion;
- unresolved questions;
- whether a second reviewer confirmed a negative finding.

## Step 4 — acquire and preserve provenance

For every source, record the canonical page, direct download or API endpoint, publication and coverage dates, retrieval date, format, access method, licence status and checksum where a file is acquired.

Do not bypass authentication, access controls or confidentiality protections. Redistribute raw files only when lawful.

## Step 5 — classify before extracting

Assign:

- source type;
- official/non-official status;
- matter types covered;
- measure domains;
- geographic detail;
- update frequency;
- machine-readability;
- source-quality grade.

## Step 6 — extract with exact provenance

Retain original labels and definitions. Every value must point to page/table/cell or dashboard/API query. Translation and harmonised mapping are separate fields.

## Step 7 — second review

A second reviewer checks:

- source identity and period;
- count unit and denominator;
- start/end events for durations;
- statistic type;
- case-type mapping;
- transformations;
- disclosure risk.

Gold-layer observations require second review.

## Step 8 — update status

Jurisdiction coverage status:

- `not_started`;
- `search_in_progress`;
- `official_source_found`;
- `non_government_source_only`;
- `no_public_source_found`;
- `source_inaccessible`;
- `direct_contact_pending`;
- `verified_complete`.

`verified_complete` is always qualified by a recorded review-cycle date. A negative status requires a completed search log and second reviewer.
