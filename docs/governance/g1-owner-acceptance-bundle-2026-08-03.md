# G1 owner acceptance bundle — 2026-08-03

This bundle is the current owner-ready handoff. It assembles repository-owned
evidence and advisory review; it does not create missing authorities or force
gate acceptance.

## Bound artefacts

| Artefact | SHA-256 |
|---|---|
| `docs/governance/g1-owner-decision-packet-2026-08-03.md` | `c32b6dbf613ea1e342a704c4f72b5124cf536fa63a75e078b1e68909c30e4e6c` |
| `docs/governance/g1-evidence-index-2026-08-03.md` | `18f9e148de53e19cc082fde0967adbe5356ee4e973e27bc4b70e7a0ecc16a513` |
| `docs/governance/g1-control-gap-matrix-2026-08-03.md` | `00bbe85cd506c64be8f54a678e67e38932bfce1bef5435ccfab57989cb15c872` |
| `docs/governance/g1-panel-pre-assurance-2026-08-03.md` | `d579b735fb57c74b383ef295106eaaaa5f5521932ac85ccbf0d01205b3c1d20c` |
| `docs/methods/exact-edition-rights-screening-2026-08-03.md` | `3f1011855467ec386c7b6e1c64935668d12038e0332f89ef731f9fffc3101e1b` |
| `docs/governance/source-rights-review-queue.csv` | `de79622cf628bfe74c69c89c9f1019998a535d0bda93228c74fe9db3d6045926` |
| `data/seed/source_register.csv` | `a9eb7e1eca782b31066cd3fe8ec2310b4a91d7087fc7f23d37226d1a912a0f62` |

The authoritative file-level bindings are also recorded in `MANIFEST.sha256`.

## Owner decision command

After all mandatory G1 evidence and authority fields are genuinely complete,
the owner may run:

```bash
PYTHONPATH=src uv run python -m gfjd conductor decision G1 \
  --status accepted \
  --authority "repository owner (founder; account/repository owner)" \
  --reference "docs/governance/g1-owner-decision-packet-2026-08-03.md@c32b6dbf613ea1e342a704c4f72b5124cf536fa63a75e078b1e68909c30e4e6c" \
  --conditions "none" \
  --notes "Owner decision bound to the current packet and manifest."
```

The Conductor will reject this command while required work, evidence,
reviewers, risks or maturity remain incomplete.

## Remaining non-substitutable fields

- genuine host/sponsor and independent decision rights;
- named, consenting deputies and escalation routes;
- accountable ethics/security/architecture/risk/rights acceptance;
- any required independent or human review;
- pilot-scope selection and external evidence.

Agent panels provide options, recommendations, rationale and contingencies
only. They cannot sign, appoint authorities, create rights or consent, or
accept G1.
