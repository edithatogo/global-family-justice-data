# Comparability and quality

## Source quality grade

| Grade | Meaning |
|---|---|
| A | Official, machine-readable, documented, and versionable. |
| B | Official table or publication with usable definitions. |
| C | Official source requiring substantial interpretation or manual extraction. |
| D | Credible academic, professional, or non-government source. |
| E | Secondary, unverified, or inadequately documented. |

The grade applies to a source or observation for a specified use. It is not a judgment about the quality of a country’s justice system.

## Comparability tier

| Tier | Meaning | Comparative use |
|---|---|---|
| 1 | Matter, clock, cohort, statistic, unit, and denominator align. | Direct comparison reasonable. |
| 2 | A transparent restriction or bounded transformation is required. | Compare only under the stated method. |
| 3 | Material definitional differences remain. | Descriptive juxtaposition only. |
| 4 | The measure is not comparable for the intended use. | Retain for discovery and local analysis. |

Gold comparative tables contain only approved Tier 1 and Tier 2 observations. Tier 3 and Tier 4 remain discoverable in silver with their limitations.

## Minimum checks for a duration measure

- What event starts the clock?
- What event stops the clock?
- Are inactive, stayed, transferred, or administratively closed periods excluded?
- Is the unit a case, application, child, family, party, order, or hearing?
- Is the cohort completed during the period, filed during the period, or pending at a point in time?
- Is the statistic a mean, median, percentile, threshold proportion, or prospective listing estimate?
- Are urgent, consent, uncontested, reopened, or transferred matters included?
- Is the measure national, court-level, registry-level, or modelled?
- Are days calendar or working days?
- Has a legal or reporting change created a break in series?

## Quality assurance layers

1. **Structural:** schema, required values, IDs, dates, and allowed values.
2. **Referential:** jurisdiction, source, indicator, and transformation links resolve.
3. **Semantic:** matter, clock, statistic, cohort, and denominator are correctly interpreted.
4. **Numerical:** values reconcile with source totals and plausible ranges where possible.
5. **Lineage:** source version and exact provenance are complete.
6. **Review:** independent reviewer and adjudication record.
7. **Release:** prior-release differences, quality metrics, and known limitations are approved.

## Release rule

A value may enter gold only when its source, definition, calculation, lineage, mapping, quality grade, comparability tier, and independent review are complete. Generated gold data are never hand-edited. A material uncertainty results in exclusion or a lower comparative tier, not an undocumented analyst assumption.
