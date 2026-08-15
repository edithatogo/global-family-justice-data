# G2 packet-04 methods owner decision packet — 2026-08-15

Status: awaiting sole-owner decision. This packet is advisory and does not
itself authorize packet 04, accept a method or promote G2.

## Decision required

Packet 03 failed because six exact source hierarchy/boundary fields and two
`extraction_uncertainty` classifications were not deterministic. No empirical
value, canonical code, date, component, ambiguity code or quarantine state
disagreed.

### Option A — rerun without changing the contract

Trade-off: preserves the current contract verbatim but is likely to repeat the
same critical discrepancies. It does not address the discovered ambiguity and
is not recommended.

Contingency: if selected, packet 03 remains failed and no further formal run is
started until a different deterministic resolution is approved.

### Option B — freeze hierarchy and uncertainty rules, then rerun

Recommended. Bind the eight reconciled values below, define a deterministic
two-state uncertainty rubric for this four-row exercise, freeze packet 04 and
rerun both role-separated extraction paths from the exact editions.

Trade-off: adds a narrowly scoped methods rule after observing disagreement.
The risk of overfitting is controlled by preserving packet 03 as immutable
failed evidence, binding the rule before either fresh run, applying it to both
runs, and retaining the original thresholds and quarantines.

Contingency: any packet-04 critical difference, unsupported exact boundary or
new source ambiguity stops the run without waiver. The affected row is then
excluded or requires a further explicit owner decision; sealed outputs are
never patched.

### Option C — make uncertainty noncritical or lower the threshold

Trade-off: reduces repeated adjudication but conflicts with the approved
all-critical 100% policy and weakens the evidence standard after observing a
failure. Not recommended.

Contingency: this option would require a separate policy amendment and a new
pre-extraction design; it cannot retroactively pass packet 03.

## Recommended exact methods boundary

For packet 04 only:

- `extraction_uncertainty = none` when all required source occurrences are
  legible and `ambiguity_codes` is empty;
- `extraction_uncertainty = unresolved` when a required ambiguity code records
  a source conflict that the packet does not resolve;
- `low` and `material` are unavailable unless a future pre-extraction owner
  decision supplies deterministic predicates.

Required values:

- BRA coverage: `Tribunal Todos Grau Todos Órgão Julgador Todos Originário Todos Natureza Todos UF, Município Todos Formato Todos`;
- BRA locator: `Figura 528 - Dados de processos de violência doméstica e familiar contra a mulher`;
- BRA measure: `Medidas Protetivas em 2026`;
- BRA series: `Total`;
- BRA period: `2026`;
- BRA uncertainty: `none`;
- USA-MN domain: `Timeliness`, while `Clearance Rates` remains the measure;
- AUS uncertainty: `unresolved`.

## Rationale

The BRA visual hierarchy distinguishes the figure caption, dashboard measure
heading, aggregate card label, selected year and through-date. Minnesota page
12 supplies the enclosing `Timeliness` domain and page 14 supplies the nested
`Clearance Rates` measure. AUS retains an unresolved source-definition conflict;
BRA has no required ambiguity code. The proposed mapping is therefore
deterministic without changing any empirical fact.

The source-only panel preferred `Clearance Rates` as the Minnesota domain and
recommended `low`/`material` uncertainty categories. The reconciliation panel
preferred the domain/measure hierarchy and rejected judgment-only categories
without deterministic predicates. The recommendation follows the latter and
preserves the dissent.

## Recommended owner wording

> I approve Option B in the G2 packet-04 methods owner decision packet dated
> 2026-08-15. For this four-row rerun, I approve the exact BRA, USA-MN and AUS
> field mappings listed in the packet and the deterministic uncertainty rule:
> `none` applies when all required source occurrences are legible and no
> ambiguity code is required; `unresolved` applies when a required ambiguity
> code preserves a source conflict that the packet does not resolve. `low` and
> `material` are unavailable for this rerun.
>
> I authorize a fresh digest-bound packet 04 and two new role-separated
> extraction paths from the same exact source editions. Packet 03 remains an
> immutable failed record. The 100% critical and at least 99% overall thresholds,
> explicit-only date rule, AUS/ZAF hard quarantine, BRA/USA-MN quarantine,
> local-private evidence handling and metadata/citation-only public boundary
> remain unchanged. No fuzzy matching, critical waiver, sealed-output repair,
> source-rights acceptance, G2 passage, outbound contact, publication or release
> is authorized. Any further critical discrepancy stops the run for exclusion
> or a new explicit owner decision.

## Evidence bindings

- Evidence index:
  `docs/methods/g2-real-pilot-packet03-evidence-index-2026-08-15.md`.
- Packet-03 SHA-256:
  `6e9e21f8ffeaeb217f93b0d279cd0bb21de2dbf23f0766604b3660ec1ade542d`.
- Concordance SHA-256:
  `9fb7fb1be5a8f330f4c721712565566ad08de8bb75ba477aae22b4d0187d1c2d`.
- Differences SHA-256:
  `f111fb2be081bc1681b91685fe449ecd0ee3a2a9971d3d1a5d72524661a327fd`.
- Methods report SHA-256:
  `1739823a2633428e1607fdc04d33adf550700a05c9f9ab64a00feed9bfe30465`.
- Rights/security report SHA-256:
  `f3676cdfbcefe3309986b2e195cea5041de64af2986828feefa2411a90975dd2`.
- Reconciliation report SHA-256:
  `7fe7a64de4611ad09ca360ccb6b3a94464a66b05b5bcffb8cfedfc6f5af60c12`.
