# Jurisdiction census control

The jurisdiction census is a controlled readiness process, not an assertion of
global coverage. The committed seed register is only a candidate map. A row is
ready for methods review only when all of the following are recorded:

- one included, reviewed entry in `jurisdiction_universe_template.csv`;
- exactly one current (non-superseded), reviewed coverage assessment;
- at least one reviewed search log; and
- an explicit coverage state, supported by the referenced evidence path.

`gfjd census build` emits a checksum-bound matrix and gap register. It reads
`data/census/jurisdiction_universe.csv`, `data/census/coverage_assessment.csv`,
and `data/census/search_log.csv` when present, falling back to the corresponding
header-only seed templates for a clean baseline. Missing records are rendered as `unresolved`; the command never promotes a seed
`coverage_status`, a source-register entry, or a blank search log into a
coverage finding. The output is operational evidence only and cannot itself
accept a Conductor gate.

## Direct enquiries

Direct contact is required only for priority gaps under the source-discovery
protocol. To preserve a transparent closure record without publishing personal
contact data, a reviewed search-log `notes` field may contain one controlled
marker:

- `direct_enquiry:sent`
- `direct_enquiry:closed`

The marker does not establish that an enquiry was completed, answered, or
approved. The underlying dated correspondence or closure rationale must remain
in the controlled evidence location referenced by that log. Until such evidence
is reviewed, the report shows `not_required_or_unrecorded`.

## Review and freezing

The global universe can be frozen only through the accountable G3 decision.
The report's `ready_for_methods_review` state means that repository controls
are present for a row; it is neither an institutional map approval nor a
reviewed coverage conclusion. Any later change must supersede the assessment,
preserve prior evidence, and trigger a new report build.
