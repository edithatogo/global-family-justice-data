# Offline schema-contract redesign

Scope: repository-only preparation after PR #132's immutable terminal outcome.
No new request, response replay, source access, candidate selection or G2 promotion.

- [x] Verify clean manifest and full baseline `make check` on `9fb0a79`.
- [x] Obtain separate network-prohibited design advice (`metadata_schema_design_advice`).
- [x] Implement a separate pure structural diagnostic (`dc96b49`) with fictional inputs,
  strict JSON/resource checks and no values, transport or candidate evaluation.
- [x] Test disclosure boundaries and malformed inputs (39 tests); separate
  advisory code review completed with the parser-budget distinction clarified.
- [~] Bind the prospective design, index it in Conductor, run full validation
  and deliver signed commits via checked PR.

## Options and recommendation

1. Documentation only: low cost, but leaves future schema failures opaque.
2. **Recommended:** offline structural diagnostics plus schema-discovery-first
   design. It improves future diagnosis without guessing a live API contract.
3. Widen the failed parser or substitute the existing monitor: rejected. The
   former repairs a failed lineage; the latter mixes discovery and eligibility.

The retained receipt proves failure categories, not the identities of unexpected
keys or correct API semantics. Existing synthetic fixtures are not authoritative
interface evidence. Never infer missing schema details from the nine locators.

## Prospective sequence and remaining boundary

1. Complete this synthetic-only repository preparation.
2. Separately bind and authorize schema discovery: exact official endpoint,
   purpose, byte/count/time budgets, output/retention policy and stopping rules.
   No such executable access packet or authority is created here.
3. Discovery ends with structural evidence only; no automatic selection or link access.
4. Qualify semantics using authoritative interface documentation under separately
   authorized access: required/optional/prohibited fields, total/start/pagination,
   format and publication-time meaning. Type-only diagnostics cannot prove them.
5. Freeze a distinct successor evaluation contract and tests before seeking its
   external execution authorization. Preserve all accumulated exposure and stops.

Contingency: if structure exceeds limits or documentation is insufficient, retain
uncertainty; do not guess, silently expand retention or retry. Existing separately
authorized future-edition monitoring remains unchanged as redundancy.

Agent advice is not independent assurance. Unknown-name hashes are fingerprints,
not anonymization: low-entropy names can be guessed. Publication of actual future
diagnostics remains separately governed. G2-C04/C07 and M06 remain blocked.
