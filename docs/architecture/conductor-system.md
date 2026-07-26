# Programme conductor system

## Purpose

The conductor is the programme control plane for the route to v1.0. It does not declare delivery complete merely because a document exists. It joins the ten programme tracks, six stage gates, 58 work packages, evidence register, maturity assessment, risk register, defect register, exceptions and explicit gate decisions.

## Authoritative records

The control model intentionally uses one source of truth per record family:

- `config/tracks.toml` defines the ten durable tracks and their dependencies;
- `config/stage_gates.toml` defines G1–G6 and mandatory evidence criteria;
- `programme/work_items.csv` records executable delivery state;
- `programme/evidence_register.csv` records reviewable evidence and checksums;
- `programme/maturity_assessment.csv` records self-assessed and evidence-assured maturity;
- `programme/risk_register.csv`, `defect_register.csv` and `exception_register.csv` record assurance controls;
- `programme/gate_decisions.csv` records formal governance decisions;
- `programme/audit-log.jsonl` records every state mutation made through the CLI.

The repository does not maintain a parallel JSON programme state. JSON and Markdown status outputs are generated views.

## Gate semantics

A gate is **ready for decision** only when:

1. all dependency gates have an accepted, unexpired decision;
2. every mandatory criterion has accepted or formally waived evidence;
3. every non-closure work package for the gate is accepted or waived;
4. no configured blocking defect remains unresolved;
5. no configured blocking residual risk remains open;
6. the evidence-assured programme maturity floor meets the gate threshold.

A gate is **passed** only after it is ready and an authorised accepted decision is recorded. Work completion, self-assessment or document presence cannot substitute for this decision.

## Four-eyes evidence control

Accepted evidence must have a repository-contained evidence path, a matching SHA-256 checksum, a review date and a reviewer role distinct from the evidence owner role. Expired evidence blocks any dependent criterion. Evidence status changes are audit logged.

## Concurrency and auditability

Programme mutation commands take an advisory lock, update CSV state atomically and append an immutable JSON Lines audit event containing the actor, timestamp, record key, before state and after state. Direct manual edits remain visible in Git but bypass the runtime audit log and should therefore be prohibited on protected branches.

## Core commands

```bash
gfjd validate
gfjd conductor status
gfjd conductor gate G1
gfjd conductor next
gfjd conductor work WI-G1-07 --status in_review --actor "technical lead"
gfjd conductor evidence E-CONDUCTOR-BASELINE --status accepted --reviewer "independent reviewer"
gfjd conductor decision G1 --status accepted --authority "steering committee" --reference "MIN-2026-001"
```

The conductor is deliberately conservative: an absent record is a blocker, not an implied pass.
