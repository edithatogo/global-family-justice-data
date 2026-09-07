# Anonymous browser control readiness

Status: implementation preparation; source execution disabled; G2 unchanged.

## Follow-up implementation checkpoint

Unknown paths on allowed hosts no longer default to static assets. Explicit
authentication/export/download paths and source-file extensions are rejected.
PR review additionally closed the `oauth2` path variant with regression cases.
It also rejects encoded forbidden paths and ambiguous double encoding. The
offline output helper creates a missing build parent while rejecting symlinks
and preserving exclusive attempt directories.
A dedicated offline CDP pipe prototype now has bounded framing, redacted errors,
recursive target setup, a terminal latch and independent deny-all proxies for
the default browser and test context. It has **no live execution mode**.

The installed Playwright implementation automatically continues redirected
requests instead of rerunning the route handler. Therefore merely replacing
page routing with context routing would not qualify same-host redirect safety.
The prototype investigates interception of each hop without a competing
Playwright session. API references: [Playwright context routing](https://playwright.dev/docs/api/class-browsercontext#browser-context-route)
and [CDP target attachment](https://chromedevtools.github.io/devtools-protocol/tot/Target/#method-setAutoAttach).

Four failed offline attempts are preserved in
`g2-cdp-offline-evidence-2026-09-07.json`. Attempts 01–02 failed during initial
setup; 03–04 reached context-target creation but stopped on an unsupported
target. Every attempt recorded zero proxy-forwarded bytes and zero admitted
fixture requests. Neither iframe interception nor proxy isolation was qualified.
Historical receipts bind the controller and protocol hashes, not complete
runtime/source snapshots; they must not be presented as reproducible empirical
source evidence. The original two startup failures above remain unchanged.

The Conductor bounded fix loop stopped further browser attempts. Offline review
then fixed malformed protocol-envelope handling, post-stop dispatch, child-exit
cleanup and target-detachment handling. It also added safe target-type labels
and policy/transport hashes for future receipts. Those post-stop corrections
have unit coverage; the browser experiment has not been rerun after them.
Future experiment success also requires confirmed graceful process cleanup;
forced termination cannot yield a passing receipt.
Future success additionally requires zero default-proxy connections and no
default-proxy stop reason, so blocked default-profile traffic cannot mask an
escape from the instrumented context. This stricter condition is unqualified.

Navigation and dashboard counters in the experiment count attempted document
loads, including the rejected over-budget attempt; `requests` contains admitted
requests only. Simulated checkpoint and observation-deadline cases are stop-path
fixtures, not proof of real I/O failure or whole-controller timeout recovery.
All cases after the first failed iframe fixture remain **unexecuted**.

Next: identify the unsupported target using the sanitized type diagnostic,
implement its safe lifecycle (or explicitly reject it), and qualify the entire
offline matrix. Then integrate a source controller with response-stage handling,
all-frame consent observation, complete bindings and a positive success predicate.
Keep the existing live runner disabled until that separate qualification passes.
These are repository-owned engineering tasks under the existing direction;
no additional owner approval is currently required.

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

### Browser UI target correction and worker stop

Attempts 05 and 06 are preserved separately in
`g2-browser-ui-offline-evidence-2026-09-07.json`; earlier failures remain intact.
The exact attempt-06 controller is retained as non-executable evidence in
`g2-browser-ui-attempt06-controller.cjs.txt`, SHA-256
`21b44a84206ee0a26912d03bb61f3a22fc027d8ff1a0fbe33bb73447b206e8ef`,
matching the receipt. The current controller subsequently corrected only the
unsupported-target diagnostic label for second-page stops; that change is not
claimed as browser-qualified by attempt 06.
Chromium identifies its own toolbar as `browser_ui`
([upstream change](https://chromium.googlesource.com/chromium/src/+/327d939af510cc32a34b28cfa3a6fa82fe5d7418)).
The controller now admits exactly that auxiliary type, installs interception
before resume, rejects all its requests before admission, and never selects it
as the source page. Unknown targets and second pages remain terminal.

Attempt 06 passed the fictional iframe case with zero proxy connections or
forwarded bytes. Its worker case failed at `Fetch.enable`; that worker was not
resumed. This is a new concrete interception blocker, not a passing worker test.
All subsequent cases remain unexecuted. Unit tests check auxiliary classification,
initialization order and failure-before-resume; they do not replace browser proof.

Recommendation: investigate a protocol-supported worker interception mechanism
and prove pre-resume request control offline. If unavailable, retain the stop or
qualify a compatible runtime; do not skip worker interception to obtain a pass.
No source acquisition or owner acceptance has occurred.

### Offline matrix result (2026-09-08)

Attempts 07–10 completed the protocol-compatible correction. Worker and
shared-worker sessions omit unsupported per-worker `Fetch.enable`; context Fetch
interception is installed before any target resumes, and the deny-all proxy
remains the physical egress backstop. The complete 13-case fictional matrix
passed in attempt 10, including proxy isolation. Attempts 07–09 remain preserved
as intermediate evidence. Receipt hashes and target/request metadata are in
`g2-cdp-offline-qualification-2026-09-08.json`.

This is an engineering qualification of the offline harness only. It does not
establish live browser/source safety, source rights, factual data, G2 passage or
release readiness. The approved source inspection remains disabled pending its
separate source-execution interlock and owner-approved evidence handling.

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
