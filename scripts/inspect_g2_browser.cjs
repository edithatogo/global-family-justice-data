'use strict';
// No CLI snapshots, traces, console/network dumps, screenshots or body reads.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const {startGuard} = require('./g2_browser_egress.cjs');
const {PLAN, hash, classify, requestMetadata, selectNavigation} = require('./g2_browser_policy.cjs');
const ROOT = path.resolve(__dirname, '..');
const PLAN_PATH = `data/methods/g2/${PLAN.lineage_id}/plan.json`;
const RECEIPT = 'docs/governance/g2-anonymous-browser-receipt-2026-09-07.json';

function checkpoint(filename, value) {
  const pending = filename + '.pending';
  const fd = fs.openSync(pending, 'wx', 0o600);
  try { fs.writeFileSync(fd, JSON.stringify(value, null, 2) + '\n'); fs.fsyncSync(fd); }
  finally { fs.closeSync(fd); }
  fs.renameSync(pending, filename);
}
function noSymlinks(filename) {
  let cursor = filename;
  for (;;) {
    try { if (fs.lstatSync(cursor).isSymbolicLink()) throw new Error('output_symlink'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = path.dirname(cursor);
    if (parent === cursor) return;
    cursor = parent;
  }
}
function runtime(playwrightRoot, executable) {
  // Fingerprint local installed inputs; do not install or update a browser.
  const packageBytes = fs.readFileSync(path.join(playwrightRoot, 'package.json'));
  const packageInfo = JSON.parse(packageBytes);
  return {playwright_version: packageInfo.version, package_sha256: hash(packageBytes),
    entry_sha256: hash(fs.readFileSync(path.join(playwrightRoot, 'index.js'))),
    browser_executable_sha256: hash(fs.readFileSync(executable))};
}

async function inspect({playwrightRoot, executable, preflight, freeze, attempt = '01'}) {
  const runtimeInfo = runtime(playwrightRoot, executable);
  if (!/^[0-9]{2}$/.test(attempt)) throw new Error('invalid_attempt');
  const filename = path.join(ROOT, preflight ? `build/g2-browser-preflight-${attempt}/receipt.json` : RECEIPT);
  const lock = path.join(ROOT, preflight ? `build/g2-browser-preflight-${attempt}/lock` : `data/raw/files/${PLAN.lineage_id}`);
  for (const target of [filename, lock]) {
    noSymlinks(target);
    if (fs.existsSync(target)) throw new Error('already_attempted');
  }
  fs.mkdirSync(path.dirname(lock), {recursive: true, mode: 0o700});
  fs.mkdirSync(lock, {mode: 0o700});
  fs.mkdirSync(path.dirname(filename), {recursive: true, mode: 0o700});
  const receipt = {lineage_id: preflight ? 'FICTIONAL-BROWSER-CONTROL-PREFLIGHT' : PLAN.lineage_id,
    freeze_commit: freeze || null, plan_sha256: hash(fs.readFileSync(path.join(ROOT, PLAN_PATH))),
    runtime: runtimeInfo, started_at: new Date().toISOString(), state: 'running',
    synthetic_offline: preflight, source_session_started: false, requests: [],
    navigations: 0, dashboard_loads: 0, optional_requests_blocked: 0,
    raw_response_retention: false, g2_acceptance: false};
  checkpoint(filename, receipt);
  let browser, context, guard, cdp;
  let stopReason = null;
  const networkIds = new Map();
  const trip = reason => {
    if (stopReason) return;
    stopReason = reason;
    if (guard) void guard.close();
    if (context) void context.close().catch(() => {});
  };
  try {
    guard = await startGuard({allowedHosts: PLAN.allowed_hosts, maxBytes: PLAN.max_encrypted_bytes,
      maxConnections: PLAN.max_connections, deadlineMs: preflight ? 60000 : PLAN.deadline_ms,
      offline: preflight, onStop: trip});
    delete process.env.DEBUG;
    delete process.env.PWDEBUG;
    const {chromium} = require(playwrightRoot);
    browser = await chromium.launch({executablePath: executable, headless: true, chromiumSandbox: true,
      proxy: {server: `http://127.0.0.1:${guard.port}`},
      args: ['--proxy-bypass-list=<-loopback>', '--disable-quic', '--dns-prefetch-disable',
        '--disable-background-networking', '--disable-component-update',
        '--disable-domain-reliability', '--no-first-run',
        '--disable-features=CaptivePortalDetection,NetworkTimeServiceQuerying',
        '--force-webrtc-ip-handling-policy=disable_non_proxied_udp']});
    context = await browser.newContext({acceptDownloads: false, serviceWorkers: 'block', ignoreHTTPSErrors: false});
    receipt.browser_version = browser.version();
    receipt.initial_cookie_count = (await context.cookies()).length;
    if (receipt.initial_cookie_count !== 0) throw new Error('inherited_session');
    const page = await context.newPage();
    context.on('page', extra => { if (extra !== page) { void extra.close().catch(() => {}); trip('extra_page'); } });
    page.on('download', download => { void download.cancel().catch(() => {}); trip('download_attempt'); });
    page.on('dialog', dialog => { void dialog.dismiss().catch(() => {}); trip('dialog_requires_decision'); });
    cdp = await context.newCDPSession(page);
    const tree = await cdp.send('Page.getFrameTree');
    const mainFrame = tree.frameTree.frame.id;
    await cdp.send('Network.enable');
    cdp.on('Network.responseReceived', event => {
      const item = networkIds.get(event.requestId);
      if (!item) return;
      item.status = event.response.status;
      if (Object.entries(event.response.headers).some(([key, value]) => key.toLowerCase() === 'content-disposition' && /attachment/i.test(String(value)))) trip('download_attempt');
      if ([401, 403].includes(item.status) || (item.status >= 400 && ['official_page', 'public_view', 'models', 'query'].includes(item.category))) trip('access_denied');
    });
    cdp.on('Fetch.requestPaused', event => {
      void (async () => {
        const info = requestMetadata(event.request.url, event.request.method, event.request.headers);
        if (info.optional) {
          receipt.optional_requests_blocked++;
          await cdp.send('Fetch.failRequest', {requestId: event.requestId, errorReason: 'BlockedByClient'});
          return;
        }
        if (info.deny) { trip(info.deny); return; }
        if (receipt.requests.length >= PLAN.max_requests) { trip('request_budget'); return; }
        if (event.resourceType === 'Document' && event.frameId === mainFrame) {
          if (++receipt.navigations > PLAN.max_navigations) { trip('navigation_budget'); return; }
          if (info.category === 'public_view' && ++receipt.dashboard_loads > PLAN.max_dashboard_loads) { trip('dashboard_budget'); return; }
        }
        const item = {...info, attempted_at: new Date().toISOString()};
        receipt.requests.push(item);
        if (event.networkId) networkIds.set(event.networkId, item);
        checkpoint(filename, receipt);
        if (preflight) {
          let body = '<html><body>FICTIONAL offline browser fixture</body></html>';
          if (info.category === 'official_page') body = `<html><script>console.log('FICTIONAL_SECRET_MUST_NOT_PERSIST');fetch('https://app.powerbi.com/public/reports/00000000-0000-0000-0000-000000000000/modelsAndExploration',{headers:{'X-PowerBI-ResourceKey':'FICTIONAL_SECRET_MUST_NOT_PERSIST'}}).then(()=>fetch('https://blocked.invalid/secret'))</script></html>`;
          await cdp.send('Fetch.fulfillRequest', {requestId: event.requestId, responseCode: 200,
            responseHeaders: [{name: 'Content-Type', value: info.category === 'official_page' ? 'text/html' : 'application/json'},
              {name: 'Access-Control-Allow-Origin', value: '*'}, {name: 'Access-Control-Allow-Headers', value: '*'}],
            body: Buffer.from(body).toString('base64')});
        } else await cdp.send('Fetch.continueRequest', {requestId: event.requestId});
      })().catch(() => { if (!stopReason) trip('control_failure'); });
    });
    await cdp.send('Fetch.enable', {patterns: [{urlPattern: '*', requestStage: 'Request'}]});
    receipt.source_session_started = !preflight;
    checkpoint(filename, receipt);
    const visited = new Set();
    let target = PLAN.entry;
    while (!stopReason && visited.size < PLAN.max_navigations) {
      visited.add(target);
      await page.goto(target, {waitUntil: 'domcontentloaded', timeout: 30000});
      if (preflight) { await page.waitForTimeout(3000); break; }
      const requiresDecision = async () => (await page.locator('input[type=password]').count()) > 0 ||
        await page.locator('dialog,[role=dialog],[aria-modal=true]').evaluateAll(elements => elements.some(el => /sign.in|log.in|terms|consent|accept/i.test(el.textContent || '')));
      if (await requiresDecision()) { trip('consent_or_authentication_ui'); break; }
      if (classify(target, 'GET').category === 'public_view') {
        await page.waitForTimeout(15000);
        if (await requiresDecision()) trip('consent_or_authentication_ui');
        break;
      }
      // Observe navigation metadata only; no dashboard cells, values or screenshots.
      const links = await page.locator('a[href],iframe[src]').evaluateAll(elements => elements.map(el => ({href: el.href || el.src, label: (el.textContent || '').slice(0, 300)})));
      target = selectNavigation(links, page.url(), visited);
      if (!target) { trip('navigation_context_unresolved'); break; }
    }
    receipt.state = stopReason ? 'terminal_stop' : 'metadata_inspection_complete';
  } catch {
    if (!stopReason) stopReason = 'browser_or_control_failure';
    receipt.state = 'terminal_stop';
  } finally {
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    if (guard) await guard.close();
    receipt.stop_reason = stopReason;
    receipt.transport = guard ? {...guard.counters} : null;
    receipt.finished_at = new Date().toISOString();
    if (preflight) receipt.preflight_passed = stopReason === 'destination_denied' && guard.counters.bytes === 0 &&
      receipt.initial_cookie_count === 0 && receipt.requests.some(x => x.header_names.includes('x-powerbi-resourcekey')) &&
      !JSON.stringify(receipt).includes('FICTIONAL_SECRET_MUST_NOT_PERSIST');
    receipt.models_observed_200 = receipt.requests.some(x => x.category === 'models' && x.status === 200);
    receipt.query_observed_200 = receipt.requests.some(x => x.category === 'query' && x.status === 200);
    receipt.request_contract_status = 'metadata_only_not_replay_qualified';
    checkpoint(filename, receipt);
  }
  return {receipt: path.relative(ROOT, filename), state: receipt.state, preflight_passed: receipt.preflight_passed};
}

async function main() {
  const args = process.argv.slice(2);
  const value = flag => args[args.indexOf(flag) + 1];
  const preflight = args.includes('--preflight');
  // Advisory review identified uncovered browser targets. Fail before any runtime
  // or source access until context-wide interception is empirically qualified.
  if (!preflight) throw new Error('browser_controls_not_qualified');
  const playwrightRoot = value('--playwright-root');
  const executable = value('--browser-executable');
  if (!args.includes('--playwright-root') || !args.includes('--browser-executable')) throw new Error('runtime_required');
  if (JSON.stringify(JSON.parse(fs.readFileSync(path.join(ROOT, PLAN_PATH)))) !== JSON.stringify(PLAN)) throw new Error('plan_binding');
  const freeze = preflight ? null : value('--freeze-commit');
  if (!preflight) {
    const git = (...cmd) => cp.execFileSync('git', cmd, {cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe']}).toString().trim();
    if (!args.includes('--freeze-commit') || git('rev-parse', 'HEAD') !== freeze) throw new Error('freeze_binding');
    git('-c', `gpg.ssh.allowedSignersFile=${path.join(ROOT, 'config/ssh_allowed_signers')}`, 'verify-commit', freeze);
    git('diff', '--quiet', freeze, '--');
    const qualified = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/governance/g2-browser-control-preflight-2026-09-07.json')));
    if (!qualified.preflight_passed || JSON.stringify(qualified.runtime) !== JSON.stringify(runtime(playwrightRoot, executable))) throw new Error('runtime_not_qualified');
  }
  const attempt = args.includes('--preflight-attempt') ? value('--preflight-attempt') : '01';
  const result = await inspect({playwrightRoot, executable, preflight, freeze, attempt});
  process.stdout.write(JSON.stringify(result) + '\n');
  process.exitCode = preflight ? (result.preflight_passed ? 0 : 2) : (result.state === 'terminal_stop' ? 2 : 0);
}
if (require.main === module) main().catch(() => { process.stdout.write('{"state":"pre_execution_control_failure"}\n'); process.exitCode = 2; });
module.exports = {runtime, checkpoint};
