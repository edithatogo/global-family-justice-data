# GitHub and Hugging Face archival boundary

This repository is the canonical working archive. GitHub is the versioned
source and release-record surface. Hugging Face is an optional, private,
generated-only distribution surface configured in
`config/archive_targets.toml`.

Neither surface may publish a release, dataset or Space until G1 through G6
have accepted decisions. A passing local build, a conditional decision, or an
agent-panel recommendation is insufficient.

## Export classes

| Evidence class | GitHub archive | Hugging Face | Current rule |
|---|---|---|---|
| `open_licence_verified` | manifest-bound bytes and metadata | only the exact cleared edition or generated derivative | permitted after release-gate acceptance |
| `public_domain` | manifest-bound bytes and metadata | permitted when edition and provenance are bound | requires edition receipt |
| `unknown` | metadata, citation, access receipt | metadata/citation only | never upload source bytes |
| `restricted_or_unknown` | metadata, citation, access receipt | metadata/citation only | rights adjudication remains pending |
| generated products | source-controlled artefacts and lineage | permitted when generated-only policy is satisfied | no unreviewed source redistribution |

The current England and Wales Family Court Statistics 2026 Q1 archive is the
only local source artifact classified `open_licence_verified`. The Australia,
Brazil, South Africa and Sweden artifacts remain archival metadata/receipt
inputs until their exact-edition rights are resolved.

The row-level implementation of this boundary is
`data/raw/archive_inventory.csv`. Its paths and SHA-256 values are checked
against the acquisition manifests; changing a source artifact requires
regenerating the inventory and the repository manifest.

## Reproducible publication sequence

1. Run strict validation, manifest verification, Conductor generated-output
   checks, and the release builder.
2. Produce the candidate archive and a SHA-256 inventory. The inventory must
   identify every source edition, rights class, and transformation.
3. Run the rights filter described above. A single unresolved source byte
   blocks an HF byte upload; it does not block a metadata-only catalogue.
4. Commit the candidate and provenance receipts to the GitHub branch through
   the protected pull-request workflow. Do not force-push or rewrite history.
5. Publish to an exact, owner-approved Hugging Face repository only after the
   repository name, namespace, visibility, and payload class are confirmed.
   The upload receipt records the commit, archive hash, source manifest hash,
   target repository, and visibility.
6. Verify the remote dataset/space and retain the receipt in the release
   evidence pack. A failed or unauthorised upload is recorded as an access
   issue; it never changes a gate to accepted.

## Current execution boundary

The local implementation and target policy are now present. No remote GitHub
controls, GitHub release, Hugging Face repository creation, or Hugging Face
upload is performed by default. The bootstrap workflow remains plan-first and
requires an exact target plus explicit confirmation before remote mutation.
This preserves the single-analyst, agent-panel governance model and prevents
rights-restricted source material from entering a public or uncontrolled
dataset.
