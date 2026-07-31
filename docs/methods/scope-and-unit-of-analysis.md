# Scope and unit of analysis

## Primary unit

The primary unit is a **reported measure about a defined family-justice matter in a defined jurisdiction and period**.

A specialised family court is not required. Family matters may be heard by general civil courts, magistrates, district courts, religious or customary courts, administrative agencies or mixed tribunals.

## Versioned controlled vocabularies

The v0.3 controlled vocabulary is defined by the machine-readable registers:

- `data/seed/jurisdiction_register.csv` for sovereign and subnational units;
- `data/seed/institution_register.csv` for reporting institutions and their
  jurisdictional relationship; and
- `data/seed/matter_type_dictionary.csv` for harmonised matter types and their
  core or adjacent scope status.

An observation must use a registered jurisdiction and harmonised matter type.
Subnational units are first-class where responsibility, court structure or
reporting differs; they must not be silently folded into a national value. An
adjacent matter type is retained only when a source inseparably combines it with
the documented core family-justice measure, with that limitation carried in the
record and comparability assessment.

## Required structural distinctions

- sovereign state versus subnational jurisdiction;
- court or institution versus matter type;
- first instance, appellate and enforcement stages;
- public-law, private-law and protection proceedings;
- filed case, application, party, child, order and hearing as different count units;
- completed-case duration versus current listing wait versus age of pending caseload;
- interim versus final orders;
- court output versus downstream child/family outcome.

## Exclusions from the initial comparative layer

- individual judgments used to infer national rates;
- media estimates lacking a replicable source;
- case-level personal data;
- juvenile criminal justice unless specifically scoped;
- probate or mental-health matters merely because they share a court building;
- composite scores that conceal incompatible measures.

`proceeding_type`, `court_level`, `count_unit`, `cohort_basis` and
`population_scope` remain source-declared fields rather than a prematurely
closed global enumeration. They are mandatory semantic distinctions for every
normalised observation and are validated before promotion or comparison.
