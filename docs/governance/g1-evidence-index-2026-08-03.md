# G1 evidence index — 2026-08-03

This is the current, manifest-bound index for G1. Hashes are SHA-256 values
of the repository files at index assembly time. `in_review`, `draft`, and
`conditional` are not acceptance: the Conductor remains fail-closed until an
accountable authority records acceptance against the exact digest.

| Criterion / work item | Evidence and exact path | SHA-256 | Reviewer / status | Missing authority or action |
|---|---|---|---|---|
| G1-C01 / WI-G1-01 Charter, host, sponsor, decision rights | E-GOV-CHARTER — `GOVERNANCE.md` | `0a00f9f0f987e21e5b746688588b264670a12ecf7c03014f94c059a248d233a8` | Programme executive / in_review | Genuine host/sponsor and independent accountable acceptance |
| G1-C02 / WI-G1-02 Methods scope and indicator framework | E-METHODS-SCOPE, E-INDICATOR-FRAMEWORK — `docs/methods/v0.3-methods-contract-manifest.json` | `69ee79e6404366379311517a78d30f563e799a199f158c55a3f46ce1d1530de5` | Methods lead; independent analyst-agent review / accepted technical review | Accountable methods authority acceptance for G1 |
| G1-C03 / WI-G1-03 Ethics and prohibited-data boundary | E-ETHICS-BOUNDARY — `docs/methods/data-governance-ethics.md`; E-SECURITY-POLICY — `SECURITY.md` | `2f82e869c622f9fb35dba3bcdd58be62433038bfcc63223fcd997eb513ad1955`; `d89873c5b5df0b595918ca1242d7ff985c3b76041b8abd1cfbcc5145e35ec4eb` | Security/data-governance owner / draft | Accountable security/privacy and ethics acceptance |
| G1-C04 / WI-G1-04 Architecture and release authority | E-ARCH-V1 — `docs/architecture/v1-architecture.md` | `0426a3d39141610d7d6a5a2687f865653dd877749a636073f33ad360ecb4a6ec` | Technical lead / draft | Independent technical authority approval |
| G1-C05 / WI-G1-05 Owners, deputies, escalation | E-RACI — `docs/governance/roles-and-raci.md`; E-TRACK-CHARTERS — `docs/programme/track-charters.md` | `4ff7e67c4afc6cd97d5ebc417caf2bf0b5c30af3db792b73abe0fe6e75207e63`; `779fe49d38f95e752161b8593d3c95fcd7e14cb961ec848f55df3a13a3d372ce` | Programme executive / in_review | Named appointments, deputy consent and accountable acceptance |
| G1-C06 / WI-G1-06 Risk, threat, rights, disclosure baseline | E-RISK-REGISTER — `docs/programme/risk-register.md`; E-THREAT-BASELINE — `docs/security/threat-model.md`; E-RIGHTS-BASELINE — `docs/security/rights-and-redistribution.md` | `7621ecf6f91cfd2c12f14ee44289d9e8a9c26f1273061e9517c16c7a574afe8d`; `23e7c04db906497bb9672d4902af7d4022495db31bcb14cfc82fc96f36c88812`; `2f41db254e1ff995a7eace4a28f3d218058c0866051fadbe71a16cfdfbb5a722` | Security/data-governance owner / in_review or draft | Specialist rights, legal, privacy and security review; residual-risk adjudication |
| G1-C06 / WI-G1-06 Exact-edition rights screening | E-RIGHTS-SCREEN — `docs/methods/exact-edition-rights-screening-2026-08-03.md`; queue — `docs/governance/source-rights-review-queue.csv`; register — `data/seed/source_register.csv` | `3f1011855467ec386c7b6e1c64935668d12038e0332f89ef731f9fffc3101e1b`; `de79622cf628bfe74c69c89c9f1019998a535d0bda93228c74fe9db3d6045926`; `a9eb7e1eca782b31066cd3fe8ec2310b4a91d7087fc7f23d37226d1a912a0f62` | Analyst-agent / metadata-only dispositions recorded | Accountable rights authority must clear exact bytes/extracts or approve exclusion; metadata/citation reuse remains conditional |
| G1-C07 / WI-G1-07 Conductor control | E-CONDUCTOR-BASELINE — `docs/architecture/conductor-system.md` | `ea31c9006b4f0d037c44894fa943103dc8e4a622ced6a04082ad7c8ce697916c` | Technical validation / done internally | None for repository control; does not replace authority for other criteria |
| G1-C08 / WI-G1-08 Pilot universe and local verification | E-PILOT-UNIVERSE — `data/seed/jurisdiction_register.csv` | `23283ff0e5c2659055863fdccac173cdd5b1d85fd2eb672d6310103ace7520f7` | Independent census reviewer / accepted internal scope check | Governance-owner scope decision plus local/second-review evidence |

## Packet binding and acceptance

- Current packet: `docs/governance/g1-owner-decision-packet-2026-08-03.md`
- Packet SHA-256: `c32b6dbf613ea1e342a704c4f72b5124cf536fa63a75e078b1e68909c30e4e6c`
- Owner decision: Option A, repository owner/founder, accepted without conditions;
  recorded as conditional readiness pending in `programme/gate_decisions.csv`.
- No panel report, test result, conversation approval or generated artefact
  substitutes for the missing authorities above.

## Closure rule

The index is an evidence map, not a G1 acceptance. Rebuild it whenever any
bound file changes. G1 may move to `accepted` only after every mandatory row
has accepted evidence, required reviewer records, closed critical/high risks,
and the accountable owner decision references this exact packet and manifest.
