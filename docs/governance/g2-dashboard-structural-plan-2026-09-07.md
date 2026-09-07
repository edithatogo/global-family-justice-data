# Dashboard-only structural capture

The owner approved the preceding recommendation with “Proceed with your
recommendations.” This authorizes the separately scoped structural capture,
not re-execution of the terminal dynamic lineage, target querying, source
publication, rights clearance or G2 acceptance.

## Plan and controls

Freeze `data/methods/g2/G2-DASHBOARD-STRUCTURAL-20260907-01/plan.json` and
`scripts/capture_g2_dashboard_structural.py` in a signed commit before execution.
The fresh runner reuses a new instance of the reviewed transport/receipt engine,
configured only for the new one-request lineage. Historical files are unchanged.
Bind the exact URL, GET without body or credentials, public-peer TLS, no redirects
or retries, accepted body limit 10000000 bytes (plus one oversize probe byte),
and 30-second socket timeout. The timeout is not a total DNS/run deadline.

Keep existing model/visual identity and prohibited-data screening unchanged.
Retain only validated structural JSON in a new ignored 0700 vault with 0600
files; review retention by 2027-08-24. Public records contain hashes and receipt
metadata only. Screening is not comprehensive privacy assurance.

Exclusive checkpoint creation refuses a preexisting pending file or symlink.
An existing vault or receipt prevents re-execution. Any transport, schema,
identity, budget or custody failure stops. No downstream query or extraction
is reachable in this stage.

## Advisory options incorporated

Offline role-separated `dashboard_scope_review` recommended this independent
route because the prior DataJud timeout says nothing about dashboard access.
It identified the temporary-file symlink issue and byte/timeout distinctions;
the new runner and regression tests address those before the freeze.

Exact-original backup recovery remains preferable if a genuinely new location
emerges; none is currently identified. Pausing is the contingency for failure.
Do not guess endpoints, loosen screening, repair/reuse old outputs or infer
historical values. Success proves new structural capture and custody only.
Source-derived query/schema contracts and isolated empirical extraction remain
separate next-stage requirements. No gate, maturity or Gold promotion follows.

## Work sequence

1. Baseline full validation, bounded plan and offline tests.
2. Role-separated review; signed freeze; execute once.
3. Preserve outcome and register it in Conductor with before/after audit.
4. Full validation, reviewed PR, passing CI, merge and local branch cleanup.
