# G2 Statistics Canada family-law metadata route

## Outcome

This route prospectively observes four exact Statistics Canada family-law table identifiers through the publisher's documented Web Data Service metadata endpoint. It is a distinct official structured route and does not use search providers.

The monitor records only product identity, title, issue date, cube end date, and release time. It never requests table values, downloads, catalogue pages, or returned locators. A post-cutoff release time stops for review: it is a signal that the table changed, not proof that a new exact edition is eligible.

## Frozen products

- `35100222`: Family law cases, by type of case
- `35100223`: Number of events in active family law cases, by type of event
- `35100224`: Family law cases, by elapsed time and median days from case initiation to first disposition
- `35100225`: Active and inactive family law cases, by number of fiscal years since case initiation

## Fail-closed controls

- one exact HTTPS metadata endpoint and one batched POST;
- exact four-product allowlist and exact English-title bindings;
- zero retries and no redirects;
- one MiB response cap;
- any missing, duplicate, unexpected, failed, or title-drifted record terminates the run;
- a post-cutoff update requires a new pre-source decision and reference-period identity check;
- metadata observation cannot establish eligibility, G2 acceptance, rights clearance, publication, or release.

## G2 effect

This closes a route-preparation gap only. It does not change `G2-C04`, `G2-C07`, `WI-G2-04`, `WI-G2-07`, or the L1 maturity assessment. Those still require a passing fresh extraction/concordance result and accountable adjudication.
