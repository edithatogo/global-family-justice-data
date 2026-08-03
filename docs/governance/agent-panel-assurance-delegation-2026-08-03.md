# Agent-panel assurance delegation — 2026-08-03

## Decision

For this single-developer repository, repository-owned assurance preparation is
delegated to a role-separated panel of analyst agents rather than an
"independent review" workflow. The panel produces digest-bound findings,
options, recommendations, contingencies, contradictions and residual risks.

Panel roles are separated by task: governance/ethics, methods/data quality,
rights/privacy, security/supply chain, accessibility/localisation, operations/
release and adversarial challenge. Each agent receives the same immutable
input manifest and must disclose conflicts or inability to assess.

## Decision boundary

Panel output is advisory. It may replace repository-owned preparation and
second-pass analysis, but it must not be labelled independent assurance or be
used to fabricate legal clearance, human consent, specialist authority,
custody, signing, funding or gate acceptance. Where a gate requires a
non-substitutable external or accountable authority, the panel records the
vacancy and a fail-closed contingency (quarantine, metadata-only, defer or
exclude).

## Required panel packet

Every panel run must include:

1. input commit and SHA-256 manifest;
2. role, model/agent identity and assessment scope;
3. finding severity and evidence locator;
4. options with trade-offs, recommendation, rationale and contingency;
5. dissent or uncertainty record;
6. owner adjudication field and resulting disposition.

The owner remains the accountable authority for decisions. Panel reports do
not promote a gate; they only make the owner decision and remaining authority
gaps explicit.

## Replacement mapping

| Former workflow | Delegated workflow | Gate effect |
|---|---|---|
| Independent review preparation | Role-separated agent-panel pre-assurance | Advisory evidence only |
| Independent re-extraction preparation | Separate analyst-agent re-extraction and panel concordance review | Technical discrepancy report; no assurance claim |
| Specialist/legal/accessibility review preparation | Rights, security and accessibility panel analyses | Authority vacancy remains until accountable acceptance |

This policy applies to future intake and review packets. Existing records
described as independent remain historical labels and must not be expanded into
authority claims.
