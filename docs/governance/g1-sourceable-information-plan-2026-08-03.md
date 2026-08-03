# G1 sourceable-information plan — 2026-08-03

This plan covers information the repository can obtain from public sources or
its own deterministic controls. It explicitly excludes authority facts that
cannot be inferred from public information or agent review.

## Sourceable lanes

| Lane | Information we can source | Primary route | Required receipt | Safe use |
|---|---|---|---|---|
| Public governance context | Public host terms, institutional governance pages, published programme policies | Official institutional websites and archived documents | URL, retrieval date, language, edition/title, access state, SHA-256 when downloaded | Context and verification lead; not sponsor appointment |
| Public ethics/security standards | Official standards, regulator guidance and repository policy references | Official standards/regulator publications | Citation, version/date, URL, local copy hash, applicability note | Control cross-reference; not ethics approval |
| Public architecture/security guidance | Official platform, standards and supply-chain documentation | Primary vendor/standards documentation | URL, version, retrieval date, hash and mapped control | Technical design input; not architecture authority |
| Public rights/licensing terms | Publisher licence pages, terms, open-data notices and edition metadata | Official source-owner pages | Edition identifier, terms URL, retrieval date, exact bytes/hash, rights classification | Rights triage; not legal clearance where ambiguous |
| Public source metadata | Official datasets, dashboards, reports, APIs and catalogues | Official source-owner endpoints | Search log, language, status, access issue, receipt, bytes/hash if lawful | Discovery and preservation; not coverage verification |
| Repository controls | Hashes, test results, manifests, panel reports and generated Conductor state | Local deterministic commands | Command, revision, artifact hash, result digest, timestamp | Engineering evidence only |

## Non-substitutable facts

The following cannot be sourced into acceptance by public search or agents:

- appointment of a host, sponsor, deputy or accountable authority;
- consent, safeguarding or participation;
- independent assurance or human/local review;
- legal rights determination where terms are ambiguous;
- owner or specialist gate acceptance;
- funding, staffing, custody, signing or live-service commitments.

These remain `pending_authority`, `evidence_missing` or `pending_review` until
their accountable records are supplied.

## Intake and verification sequence

1. Search only official or primary sources; record every query/result,
   language, date and access issue in `data/census/search_log.csv`.
2. Preserve lawful copies or metadata receipts with SHA-256 bindings.
3. Map each receipt to a G1 criterion without upgrading its status.
4. Run agent-panel consistency and contradiction review.
5. Update the evidence index, blocker register and owner bundle.
6. Recompute `MANIFEST.sha256` and run strict validation.
7. Keep authority-dependent criteria blocked until the relevant accountable
   record exists.

## Contingencies

- Official page unavailable: retain URL/access receipt and mark inaccessible.
- Terms unclear: metadata/citation-only or quarantine; do not infer rights.
- Source changes: invalidate the prior receipt and rebind the edition hash.
- Conflicting official sources: preserve both, route to adjudication and do
  not promote the claim.
- No public evidence: record transparent absence; do not treat silence as
  approval or evidence of non-existence.

## Recommended use

Proceed with public-source discovery and repository verification in parallel,
but present the resulting evidence as context or technical support only. Keep
G1 authority, reviewer, rights, consent and acceptance boundaries fail-closed.
