# v1.0 gap analysis and recommended improvements

## Priority 0 — earn G1 rather than relabel the baseline

1. Appoint the host, sponsor, steering authority, track owners and deputies.
2. Review, amend and formally accept the charter, scope, architecture, aggregate-data boundary, threat model, rights workflow, pilot universe and RACI.
3. Replace draft/missing evidence states with independently reviewed evidence, correct hashes and dated approvals.
4. Review residual risks and record the G1 decision only after the conductor reports `ready_for_decision`.

This is the critical next step. The code should not auto-accept its own governance evidence.

## Priority 1 — complete the pilot vertical slices

- Select twelve heterogeneous pilot systems under an approved sampling rationale.
- Build at least one maintained connector each for an API, structured file, HTML table and difficult PDF/dashboard path.
- Introduce source-edition records, immutable acquisitions, source-native bronze tables, mapping files, extraction records and review records.
- Populate representative silver observations and promote only dual-reviewed, lineage-complete rows.
- Perform an independent re-extraction sample and establish quantitative concordance thresholds.
- Rehearse correction, re-release and restoration of the pilot bundle.

## Priority 2 — production engineering hardening

- Add a dependency lock strategy and produce a resolved-environment SBOM in release CI.
- Add signed provenance/attestations and independently administered release preservation.
- Separate controlled source storage from the public monorepo and test retention and restore.
- Add source-specific connector contracts, fixtures, retries, backoff, conditional requests and drift fingerprints.
- Add property-based and mutation testing around identifiers, promotion and release manifests.
- Add cross-platform deterministic-build verification in two clean environments.
- Formalise schema migrations and backward-compatibility fixtures before G4.
- Introduce structured logging, metrics and alert ownership for scheduled acquisition and publication jobs.

## Priority 3 — data and methods maturity

- Freeze a jurisdiction identity authority and rules for disputed, federal and devolved systems.
- Expand the matter ontology and clock model using pilot evidence, not abstract harmonisation alone.
- Define quantitative gold-layer audit thresholds, missingness semantics and series-break rules.
- Build the outcomes evidence catalogue as a separate evidence product rather than inferring wellbeing from case speed.
- Publish the v1 comparative cohort and explicit exclusions before release-candidate assurance.

## Priority 4 — public product and safeguards

- Build the source-availability atlas first; it is the least misleading global product.
- Constrain any comparison interface so Tier 3/4 observations cannot appear as direct comparisons.
- Complete WCAG-oriented accessibility testing, low-bandwidth downloads and reviewed launch translations.
- User-test interpretation with court administrators, researchers, people with lived experience and child-rights advisers.
- Add misuse monitoring and a documented process for contextual harm, correction and takedown.

## Priority 5 — operational maturity

- Establish a release calendar, support rota, incident and correction service objectives.
- Run release, rollback, republish, backup and restore exercises with deputies rather than the primary implementer.
- Close all P0/P1 defects and disposition P2 findings before G5.
- Run the frozen release candidate in a production-like environment for at least 30 calendar days.
- Secure committed funding and named capacity for at least 12 months of the 1.x line.

## Recommended architectural refinements after the pilot

The current file-based control plane is appropriate for a transparent, reviewable baseline. Reassess it only when concurrency, contributor volume or operational integration justifies a service database. If that transition occurs, keep CSV/JSON exports as the public audit format and preserve stable identifiers and event history.

The public API/dashboard should remain a derived product. Immutable release files and their provenance should continue to be authoritative.
