# Source discovery protocol

## Objective

A jurisdiction search is complete only when the relevant family-justice institutions and reporting pathways have been checked under a documented multilingual process. “No source found” is a reviewed research finding, not a default assigned after a cursory web search.

## Step 1 — map the system

Identify bodies responsible for:

- each in-scope family matter type;
- court administration and official court statistics;
- appeals and enforcement;
- legal aid and dispute resolution;
- child protection, maintenance, adoption, and family-violence protection;
- performance, audit, budget, and accountability reporting.

In federal or devolved systems, repeat this at the level that controls the function. Record customary, religious, or administrative pathways where material.

## Step 2 — search official domains

Search in relevant local/official languages and English where useful:

1. judiciary and court-administration sites;
2. ministry of justice, attorney-general, or equivalent;
3. national statistics offices and open-data portals;
4. parliamentary, audit, budget, and performance publications;
5. child-protection, maintenance, legal-aid, and family-service agencies;
6. regional and international bodies;
7. academic and non-government evidence sources;
8. catalogues, archives, and direct institutional enquiries where needed.

Suggested concepts should be translated and adapted locally:

- family court; family justice; domestic relations; matrimonial;
- divorce; custody; parenting; contact; maintenance; child protection; adoption; protection order;
- caseload; filings; disposals; pending; clearance;
- waiting time; duration; age of cases; time standard;
- annual report; statistics; dashboard; open data; performance;
- user survey; fairness; safety; compliance; enforcement; reapplication; wellbeing; evaluation.

Automated translation may support discovery but cannot by itself close a jurisdiction as searched complete.

## Step 3 — record the search

Complete a search log even when nothing is found. Record:

- date, reviewer, and coverage cycle;
- languages, terms, and local institutional names;
- institutions, domains, catalogues, and archives checked;
- candidate sources and reasons for inclusion/exclusion;
- inaccessible, discontinued, login-gated, or unclear sources;
- unresolved structural or terminology questions;
- whether direct contact was attempted;
- whether a second reviewer confirmed any negative finding;
- confidence and next review due.

## Step 4 — acquire and preserve provenance

For every source, record:

- canonical page and direct data location;
- publication and coverage dates;
- source version and retrieval date;
- format, access method, and retrieval recipe;
- API parameters, dashboard filters, or spreadsheet/table identifiers;
- licence/rights status and redistribution decision;
- checksum where a file is acquired;
- archival or storage reference where lawful;
- exact provenance for every extracted value.

Do not bypass authentication, access controls, confidentiality protections, or rate limits. Public visibility is not permission to redistribute a source file.

## Step 5 — classify before extracting

Assign:

- source type and official status;
- matter types and evidence/outcome domains;
- geographic and institutional detail;
- period coverage and update frequency;
- machine-readability and extraction method;
- source-quality grade;
- source status and next review date.

## Step 6 — extract with exact lineage

Retain original labels, definitions, language, footnotes, units, and period structure. Translation and harmonised mapping are separate fields. Every silver or gold value must point to a source version and page/table/cell/query/filter locator.

## Step 7 — independent review

A second reviewer checks:

- source identity, version, period, and official status;
- count unit and denominator;
- duration start/end events and excluded time;
- statistic and cohort type;
- matter and indicator mapping;
- transformations and conversions;
- source rights and disclosure risk;
- completeness of the search where the finding is negative.

Gold observations require independent second review and approved status.

## Step 8 — assign coverage status

Use only the controlled values:

- `not_started`;
- `search_in_progress`;
- `official_source_found`;
- `non_government_source_only`;
- `no_public_source_found`;
- `source_inaccessible`;
- `direct_contact_pending`;
- `verified_complete`;
- `review_due`;
- `withdrawn`.

`verified_complete` means complete for the documented review cycle and scope, not permanently complete. Negative and complete statuses require a completion date and second review.
