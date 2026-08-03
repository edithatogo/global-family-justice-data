# Subagent panel assurance protocol

This protocol provides repository-level triage and remediation evidence. It is
not scientific, legal, ethical, accessibility or publication certification.

## Panel composition

Run blinded, role-specific subagents over one frozen, digest-bound evidence
packet:

1. methods and ontology;
2. evidence, provenance and rights routing;
3. data quality and independent re-extraction;
4. coverage, localisation and negative-finding review;
5. ethics, privacy and safeguarding;
6. product, accessibility and responsible use;
7. security, supply chain, reliability and provenance.

## Required report

Each report must include the packet digest, role, timestamp, tool/model version,
verdict (`pass`, `conditional` or `fail`), finding IDs and severities, exact
evidence references, uncertainty, abstentions and required remediation. Agents
must not invent reviewer identities, legal permissions, local verification,
consent, empirical data or release authority.

## Orchestration and adjudication

The orchestrator verifies packet identity, report schema, role completeness and
independence, then writes a conflict matrix. The owner adjudicates every finding
as `accept`, `fix`, `defer` or `reject`, recording rationale, residual risk and
deadline. A panel consensus is never treated as external acceptance.

The sequence is: freeze candidate → run panel in parallel → validate reports
and digests → resolve conflicts → owner adjudication → rerun affected roles →
update gate evidence.

## Blocking rules and contingencies

- Any critical/high finding, disagreement or missing report remains blocking.
- Unavailable subagent: record a missing report; do not close the gate.
- Inaccessible source: retain `source_inaccessible` or metadata-only status.
- Missing local evidence or consent: use unresolved/synthetic-only status.
- Missing host, custody or signing authority: retain an unsigned local candidate.

Archive eligibility still requires the applicable external rights, governance,
participation, assurance, operational and funding evidence.
