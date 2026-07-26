# v1 data quality and assurance plan

## 1. Objective

The quality system must make two failures difficult:

1. publishing the wrong value or provenance; and
2. publishing a technically correct value in a misleading comparison.

Quality therefore covers source integrity, extraction accuracy, semantic classification, transformation, comparability, disclosure, documentation and release operations.

## 2. Quality dimensions

| Dimension | Core question |
|---|---|
| Coverage | Was every in-scope jurisdiction/source family searched and status-coded? |
| Validity | Does each field conform to its type, domain and business rules? |
| Accuracy | Does the extracted value match the source? |
| Completeness | Are required fields, periods and provenance present? |
| Uniqueness | Are IDs and observations free from unintentional duplication? |
| Consistency | Do related values and periods agree within and across releases? |
| Timeliness | Is the source/review status current for the stated cycle? |
| Provenance | Can the value be located and verified in preserved evidence? |
| Interpretability | Are definition, clock, denominator, cohort and exclusions clear? |
| Comparability | Is the proposed cross-jurisdiction use justified? |
| Disclosure safety | Could the data identify or harm children/families? |
| Reproducibility | Can transformations and release artefacts be recreated? |

## 3. Layer promotion

### Raw to bronze

Required:

- source and edition ID;
- rights/storage status;
- retrieval date and checksum;
- exact locator/query/filter;
- extraction method and original labels;
- no silent alteration of values or units.

Failure result: source remains catalogued but extraction is quarantined.

### Bronze to silver

Required:

- valid schema and stable IDs;
- normalised period, unit and statistic fields;
- original definitions retained;
- matter/indicator mapping with ontology version;
- transformation rule recorded;
- referential and duplication checks pass;
- ambiguity explicitly coded.

Failure result: bronze remains available for review; no normalised release.

### Silver to gold

Required:

- specified analytical use;
- quality grade and comparability tier;
- complete clock, cohort, denominator and inclusion/exclusion definition;
- source/series-level second review;
- all automated checks pass;
- disclosure review where relevant;
- no unresolved material ambiguity;
- mapping/transformation approval by authorised reviewer.

Failure result: silver may be released as descriptive data only, with restrictions, or quarantined.

## 4. Review model

### First review

The extractor verifies the value, locator, unit, period, original definition and extraction method.

### Second review

A different reviewer verifies the source/series end to end, including mapping, clock, denominator, comparability and transformations. Gold status cannot be self-approved.

### Adjudication

Disagreement is recorded and resolved by the methods/quality lead or designated panel. The losing interpretation is not deleted; the decision and rationale are retained.

### Independent assurance sample

Before v1.0, an assurer independently selects and re-extracts a risk-based sample stratified by:

- source format and extraction method;
- jurisdiction/region/language;
- matter and indicator family;
- quality grade and comparability tier;
- manual transformation complexity;
- high-visibility analytical outputs.

Minimum release threshold:

- at least 99% exact concordance on values and provenance;
- 100% concordance on critical classification fields: jurisdiction, matter type, indicator, statistic type, unit, clock and cohort;
- root-cause analysis and expanded sampling after any material failure.

## 5. Automated checks

The v1 pipeline should include:

- schema and allowed-value validation;
- ID uniqueness and referential integrity;
- missing required provenance;
- invalid date ranges and reporting periods;
- duplicate observation keys;
- unit/statistic incompatibilities;
- impossible rates or negative counts where not permitted;
- numerator/denominator consistency;
- cross-footing and subtotal checks where source structure allows;
- large release-to-release changes and trend breaks;
- source freshness and checksum change;
- orphaned/reused retired IDs;
- gold observations without second review;
- Tier 3/4 observations entering direct-comparison outputs;
- small-cell/disclosure flags;
- broken citations and absent source manifests.

Checks produce machine-readable results and a human release summary.

## 6. Quality scoring

A score may help triage but cannot replace categorical release gates. The score should combine:

- source authority/documentation;
- provenance completeness;
- extraction method/review status;
- definitional clarity;
- transformation complexity;
- comparability limitations;
- source recency and continuity.

A high score does not make incompatible measures comparable. Comparability remains a separate judgement.

## 7. Quarantine and exceptions

Quarantine reasons include:

- uncertain source authenticity;
- missing exact provenance;
- ambiguous unit/clock/denominator;
- unexplained source revision;
- rights restriction incompatible with release;
- extraction discrepancy;
- suspected disclosure risk;
- unreconciled duplicate or series break;
- failed audit sample.

An exception must include owner, rationale, scope, compensating control and expiry. No exception can permit identifiable/sealed data or knowingly false comparison.

## 8. Release diff and anomaly review

Every candidate release compares against the previous release for:

- added/removed jurisdictions, sources, indicators and series;
- revised values and reasons;
- schema/ontology changes;
- major trend discontinuities;
- changes in quality/comparability status;
- deleted or inaccessible source evidence;
- changes in analytical cohort.

Material changes require a changelog entry and, where appropriate, a jurisdiction/context note.

## 9. Corrections

- Preserve the reported issue, triage, evidence and decision.
- Correct through a patch or scheduled release; never silently edit a published artefact.
- Identify affected series, analyses and derived products.
- Re-run relevant validation and audit sampling.
- Publish severity, impact and correction note.
- Escalate a material false comparison or disclosure issue as a P0 incident.

## 10. Quality governance

The quality lead owns the system. The methods group owns semantic rules. Data operations implements controls. Release authority accepts residual risk. External assurance challenges the evidence before v1.0.

Monthly reporting should show coverage, review backlog, audit concordance, quarantine, corrections, source drift and unresolved anomalies.
