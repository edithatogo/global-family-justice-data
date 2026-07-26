# v1.0 release checklist

This checklist implements `V1_0_RELEASE_CRITERIA.md`. Every item must link to evidence in the release record.

## Scope and freeze

- [ ] v1 product boundary and non-goals confirmed.
- [ ] Jurisdiction universe and coverage-status snapshot frozen.
- [ ] Analytical cohort and indicator set frozen.
- [ ] Ontology, schema and public file-contract versions frozen.
- [ ] Feature freeze announced; exception process active.

## Data and methods

- [ ] Every jurisdiction has exactly one current status.
- [ ] Negative findings have second-review evidence.
- [ ] Every released observation has exact provenance.
- [ ] Every source has rights, retrieval and preservation metadata.
- [ ] All gold series have dual review and approved comparability tier.
- [ ] Independent re-extraction threshold passed.
- [ ] Release diff and anomaly review completed.
- [ ] Methods, limitations and series-break notes finalised.
- [ ] No Tier 3/4 series enters direct-comparison output.

## Build and technical assurance

- [ ] Clean-room build succeeds from approved inputs.
- [ ] Schemas, tests, static checks and compatibility checks pass.
- [ ] Current and previous minor release reproduce.
- [ ] Release files open in supported tools and match documented contracts.
- [ ] Dashboard/API/site regenerate from release artefacts.
- [ ] Rollback/republish rehearsal succeeds.
- [ ] No undocumented manual production step remains.

## Security, privacy and rights

- [ ] Prohibited-data and secret scans pass.
- [ ] Manual disclosure/contextual-harm review complete.
- [ ] Rights/redistribution review complete.
- [ ] Threat model and privacy/disclosure assessment current.
- [ ] Dependency and supply-chain findings dispositioned.
- [ ] Signing keys and release provenance controls verified.
- [ ] Vulnerability, incident and takedown channels tested.

## Product and documentation

- [ ] Source census, core dataset, outcomes catalogue and context library included.
- [ ] README, dictionary, methods, quality statement and citation guidance complete.
- [ ] Charts/tables expose source, unit, period, definition and limitations.
- [ ] Accessibility review passes or approved P2 exceptions are public.
- [ ] Launch translations have human review.
- [ ] Download and low-bandwidth access paths tested.

## Operations and continuity

- [ ] Monitoring and alerts tested with named owners.
- [ ] Backup restoration exercise passed.
- [ ] Immutable artefacts copied to second location.
- [ ] Archival deposit created or queued with verified package.
- [ ] Release, correction, incident and source-change runbooks current.
- [ ] Primary/deputy ownership complete.
- [ ] Twelve-month release calendar and budget approved.

## Defects and assurance

- [ ] No open P0 defect.
- [ ] No open P1 defect.
- [ ] Every open P2 has public, time-limited acceptance and owner.
- [ ] External methods review and project response published.
- [ ] Independent release assurance recommendation received.
- [ ] Release candidate stability soak completed without material regression.

## Publication and handover

- [ ] `RELEASE.json`, citation metadata, changelog and manifest finalised.
- [ ] Checksums and signatures verified independently.
- [ ] Data, methods, profiles and quality reports published.
- [ ] Derived services display correct version/vintage.
- [ ] Correction/support channels active.
- [ ] Go-live sign-off completed by data, methods, technical, security/privacy and executive owners.
- [ ] Post-release review scheduled.
