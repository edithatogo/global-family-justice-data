# Anonymous browser control readiness

Status: implementation preparation; source execution disabled; G2 unchanged.

The owner approved the bounded anonymous-browser recommendation in the public
context outcome. No additional owner decision is needed for repository-owned
control remediation. The proposed plan is in
`data/methods/g2/G2-ANONYMOUS-BROWSER-20260907-01/plan.json`.
It is not a qualified execution freeze.

The installed Playwright CLI writes automatic snapshots and its documented
origin filter does not constrain redirects. Preparation therefore uses the
installed Playwright engine directly, without snapshots, HAR, console dumps,
screenshots, persistent profiles or source-body reads.

## Observed preflight failures

Two synthetic startup attempts failed before `source_session_started`, with
zero forwarded transport bytes and no recorded page requests. Attempt 1 stopped
on `plain_http_denied`; attempt 2, after disabling additional startup features,
stopped on `destination_denied`. These do not establish source access or a
successful offline browser fixture. Private original receipts remain under
`build/g2-browser-preflight/` and `build/g2-browser-preflight-02/`.
Their redacted copies and hashes are bound in the adjacent preflight evidence
JSON. No raw destination, credential, source body or browser log was retained.

Subsequent hardening rejects every preflight CONNECT before DNS/upstream access,
closes the transport immediately on a controller stop, and disables every real
execution invocation. These changes have unit coverage but have not qualified
an end-to-end browser fixture.

## Role-separated advisory review and implementation order

The `browser_boundary_review` analyst identified these must-fix items:

1. Install context-wide request interception before page creation, and prove
   coverage of cross-origin frames, workers and popup initial requests.
2. Count dashboard loads across all frames. Observe an already embedded dashboard
   instead of navigating to it again.
3. Keep fixture transport physically offline. Check terminal state after launch
   and before context creation, navigation or source-session initiation.
4. Detect authentication and consent across frames throughout observation.
5. Require an explicit dashboard metadata success predicate; reaching a loop
   bound is not success.
6. Bind qualification to controller, policy and transport hashes as well as
   runtime fingerprints.
7. Restrict allowed-host navigation and active paths; unknown GETs must not be
   implicitly approved as static assets, especially authentication/export paths.
8. Exercise redirects, duplicate iframe loads, credentials, timeouts and
   controller exceptions in negative fixtures before freezing source execution.

The transport specialist supplied the CONNECT guard and offline unit tests.
Both roles provide advisory engineering input, not accountable acceptance or
independent assurance. There is no recorded dissent from retaining the stop.

## Options and recommendation

- **Recommended:** complete the above context-wide controls and negative fixtures,
  then freeze the same approved bounded inspection. This requires engineering
  work but preserves the authorized scope and avoids another approval packet.
- **Contingency:** if Chrome startup cannot satisfy the transport boundary, test
  a clean compatible browser runtime offline. Do not permit unknown hosts or
  plain HTTP merely to obtain a passing fixture.
- **Stop:** retain current failed preflight evidence and defer browser inspection.
  This is safe but provides no new dashboard evidence.

No login, terms acceptance, filter manipulation, manual query replay, exports,
publication, release or G2 acceptance is authorized by this preparation.
WI-G2-04 and WI-G2-07 remain in review. The implementation is not complete.
