# G2 fresh replay semantic review — 2026-09-10

Status: `advisory_repository_review`

This review is explicitly bound to the fresh replay outputs and comparator
receipt. It is repository-owned advisory review, not independent assurance.

## Findings

- Both extraction outputs contain the same four source-record keys and the same
  source-faithful values.
- The exact comparator reports 100% critical-field concordance and 100% overall
  populated-field concordance.
- No fuzzy matching, critical waiver, output repair or failed-output reuse was
  observed in the run metadata.
- Cross-jurisdiction semantic equivalence is not established; rows remain
  comparison-ineligible outside the frozen cohort.
- Rights, privacy, security and redistribution status remain unresolved; source
  bytes stay under controlled custody.

## Bindings

- extractor A: `c0f9623085f7836a70e7b5da5980642541751b9407129f1bff539594ce399b9f`
- extractor B: `285a98470bd8d6ac2427a4f9684aa22566ce1d1540c956e97ee49bdd61e02baf`
- comparator: `194e0a860fbae8b1285da45d7a4f4a72d16d01b5431e458c484156c2f53ad6e7`

Conclusion: the fresh replay satisfies the approved concordance thresholds for
its bounded cohort, subject to owner adjudication. This record does not pass
G2 or authorize publication or release.
