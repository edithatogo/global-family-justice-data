# Indicator framework

## Versioned indicator dictionary

`data/seed/indicator_dictionary.csv` is the v0.3 machine-readable indicator
dictionary. It fixes each indicator ID, definition, preferred statistic and
unit, numerator, denominator and core-release status. The observation contract
in `schemas/observation.schema.json` carries the corresponding record-level
fields. Narrative domain headings below are a readable crosswalk; the CSV values
are authoritative where names differ.

| Narrative heading | Dictionary domain values |
|---|---|
| Demand and access | `demand`, `access` |
| Flow and backlog | `flow` |
| Timeliness | `timeliness` |
| Process quality | `process` |
| Court outputs | `outputs` |
| Administrative outcomes | `administrative_outcome` |
| Child and family outcomes | `child_family_outcome` |
| Equity | `equity` |
| Inputs and context | `inputs` |
| User experience | `experience` |

## Domains

### 1. Demand and access

Filings, application rates, legal aid, representation, fee waivers, mode of access and legal-needs prevalence.

### 2. Flow and backlog

Incoming, resolved, pending, clearance, reopened/reactivated matters and pending age.

### 3. Timeliness

Each duration must specify a start event, end event, statistic and denominator
definition. `TIME_*` observations with a blank `stage_start`, `stage_end` or
`denominator_definition` fail semantic validation; a reported denominator value
is retained whenever the source provides one. Core clocks include
filing-to-first substantive hearing, ready-to-hearing, filing-to-interim order,
filing-to-final disposition and age of active pending caseload.

### 4. Process quality

Adjournments, hearings per matter, mediation, expert/child-welfare reports, case management, continuity of judicial officer, remote participation and representation.

### 5. Court outputs

Consent/contested status, withdrawal, dismissal, order type, interim/final status and manner of disposition.

### 6. Administrative outcomes

Appeals, reversals, enforcement, non-compliance, repeat applications, return to court, placement changes and repeat protective proceedings.

### 7. Child and family outcomes

Safety, stability, wellbeing, family functioning, procedural justice, trust, satisfaction and perceived fairness. These generally require surveys, evaluations, cohorts or linked data.

### 8. Equity

Differences by sex/gender, age, disability, Indigenous status or ethnicity where lawful, language, migration status, geography, rurality and socioeconomic disadvantage.

### 9. Inputs and context

Judicial and staff resources, expenditure, legal aid, procedural rules, statutory time standards and major reforms.

## Timeliness rule

Never pool or rank the following as though they were the same:

- retrospective duration of completed cases;
- prospective first-available hearing wait;
- age of currently pending cases;
- time excluding inactive periods;
- mean versus median versus percentile;
- calendar days versus working days;
- case-level versus application-level duration.
