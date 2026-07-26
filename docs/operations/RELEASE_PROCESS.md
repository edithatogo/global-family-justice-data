# Release process

## Release roles

- **Release manager:** coordinates the candidate and records evidence.
- **Data steward:** approves data contracts, lineage, and data-quality results.
- **Methods chair:** approves ontology, comparability, and interpretation.
- **Security/privacy lead:** approves security, rights, and disclosure checks.
- **Release authority:** makes the final go/no-go decision and cannot be the sole build operator.

## Release types

- **Patch:** corrections, source-status updates, documentation, and non-breaking operational fixes.
- **Minor:** backwards-compatible indicators, fields, jurisdictions, or product functions.
- **Major:** breaking data contracts, ontology meaning, identifiers, or product boundary.

## Candidate workflow

1. Freeze candidate inputs and record source versions.
2. Build from a clean checkout in a supported environment.
3. Run validation, tests, linting, type checks, schema compatibility, and manifest checks.
4. Generate quality, coverage, lineage, and prior-release-difference reports.
5. Resolve or formally classify every finding.
6. Perform independent data and methods review.
7. Run disclosure, rights, security, accessibility, and documentation checks.
8. Test backup, restore, correction, withdrawal, and rollback procedures.
9. Produce release notes, known limitations, checksums, citation metadata, and archive package.
10. Obtain role-based sign-offs and release-authority approval.
11. Tag and publish immutable artifacts.
12. Verify public downloads and archive integrity.
13. Open the post-release monitoring period and record any incident or correction.

## Release blocking conditions

A release is blocked by:

- an unresolved critical or high-severity defect;
- any untraceable gold observation;
- privacy or source-rights uncertainty affecting public artifacts;
- failed clean-room build or failed restore;
- missing release owner or support route;
- unreviewed breaking schema or ontology change;
- material divergence between generated artifacts and documented methods.

## Corrections

Corrections require:

- issue and severity record;
- affected release and record IDs;
- root cause and scope assessment;
- corrected source/transformation evidence;
- regression test where applicable;
- patch release, new checksums, and changelog;
- notification proportionate to the impact.

No released file is silently replaced under the same version.
