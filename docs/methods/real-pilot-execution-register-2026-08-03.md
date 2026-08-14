# Real pilot execution register — 2026-08-03

`data/methods/real_pilot_execution_register.csv` is the machine-readable
fail-closed handoff for the G2 real-pilot sequence. It deliberately contains
no fabricated receipts, hashes, reviews or authority decisions. A candidate
may move from `pending` only when every required field is populated with a
repository-relative artifact and the artifact is manifest-bound.

## Required promotion chain

`acquisition_receipt` → `content_sha256` → `rights_status` →
`coverage_assessment` → `extraction_primary` + `extraction_secondary` →
`comparison_report` → `methods_review` + `rights_security_review` →
`agent_panel_assurance` → `owner_adjudication`.

Historical review ledgers may retain `independent_assurance` as a deprecated
value for backwards compatibility. New G2 records use
`agent_panel_assurance` and must not describe analyst-agent work as independent
or specialist assurance.

Each artifact must identify the exact source edition, retrieval timestamp,
language, route/outcome and reviewer role. `unknown`, `metadata_only`,
`blocked`, `draft` or missing values are non-promoting states. The register
does not authorize an outbound enquiry; an enquiry requires a separately
recorded owner-approved recipient, message and scope.

GBR-EAW is intentionally absent because it remains outside the approved
five-candidate scope. Its preparation packet remains subject to the separate
scope decision in `D-PILOT-SCOPE-2026-08-03`.

## Safe operating rules

- Preserve failed access and fallback receipts even when no bytes are
  available.
- Keep uncertain-rights material metadata/citation-only and out of public
  outputs.
- Do not infer local-human verification from an official landing page or an
  agent-panel review; use source-language authoritative triangulation and
  disclose its limits.
- Do not mark a row complete based on synthetic fixtures or a single
  extraction.
- The register cannot itself change G2 evidence status or gate state; only
  the Conductor acceptance workflow can do that after accountable review.
