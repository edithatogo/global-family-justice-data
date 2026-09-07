'use strict';
// Experimental, OFFLINE ONLY. Both browser proxies reject every upstream request.
// This command has no source-execution mode and is not an acquisition runner.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const cp = require('node:child_process');
const {CdpPipe} = require('./g2_cdp_pipe.cjs');
const {startGuard} = require('./g2_browser_egress.cjs');
const {PLAN, hash, requestMetadata} = require('./g2_browser_policy.cjs');
const {checkpoint} = require('./inspect_g2_browser.cjs');
const ENTRY = 'https://www.gov.uk/government/statistics/fictional-browser-fixture';
const VIEW = 'https://app.powerbi.com/view?r=FICTIONAL_SECRET';
const MODEL = 'https://app.powerbi.com/public/reports/00000000-0000-0000-0000-000000000000/modelsAndExploration';
const WORKER = 'https://www.gov.uk/assets/fictional-worker.js';
const CASES = ['iframe', 'worker', 'shared_worker', 'popup', 'redirect_same_host',
  'redirect_other_host', 'redirect_loop', 'authorization', 'duplicate_dashboard',
  'child_consent', 'simulated_checkpoint_stop', 'observation_deadline_stop', 'proxy_isolation'];
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const targetTypeLabel = value => typeof value === 'string' && /^[a-z_]{1,40}$/.test(value) ? value : 'unknown';
function prepareOutput(root, attempt) {
  if (!/^[0-9]{2}$/.test(attempt)) throw new Error('arguments');
  const directory = path.join(root, 'build', `g2-cdp-offline-${attempt}`);
  for (let cursor = directory;; cursor = path.dirname(cursor)) {
    try { if (fs.lstatSync(cursor).isSymbolicLink()) throw new Error('output_symlink'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (path.dirname(cursor) === cursor) break;
  }
  fs.mkdirSync(path.dirname(directory), {recursive: true, mode: 0o700});
  fs.mkdirSync(directory, {mode: 0o700}); // Exclusive attempt; never repair/reuse.
  return path.join(directory, 'receipt.json');
}
const autoAttach = {autoAttach: true, waitForDebuggerOnStart: true, flatten: true,
  filter: [{type: 'tab', exclude: true}, {type: 'browser', exclude: true}, {}]};
function consentScript() {
  // Sends a fixed signal only; no DOM text or values cross the pipe.
  const check = () => {
    if (document.querySelector('input[type=password]') ||
      [...document.querySelectorAll('dialog,[role=dialog],[aria-modal=true]')]
        .some(el => /sign.in|log.in|terms|consent|accept/i.test(el.textContent || ''))) {
      globalThis.__gfjdStop('consent_or_authentication_ui');
    }
  };
  new MutationObserver(check).observe(document, {subtree: true, childList: true, attributes: true}); check();
}
function fixture(caseName, url) {
  const fetchModel = `fetch('${MODEL}',{headers:{'X-PowerBI-ResourceKey':'FICTIONAL_SECRET'}})`;
  if (url === WORKER) return {mime: 'application/javascript', body:
    caseName === 'shared_worker' ? `onconnect=()=>{${fetchModel}}` : fetchModel};
  if (url === MODEL) return {mime: 'application/json', body: '{}'};
  if (url === VIEW) return {mime: 'text/html', body: caseName === 'child_consent' ?
    '<input type="password">' : `<script>${fetchModel}</script>`};
  if (caseName === 'redirect_same_host') return {status: 302, location: 'https://www.gov.uk/login'};
  if (caseName === 'redirect_other_host') return {status: 302, location: 'https://blocked.invalid/'};
  if (caseName === 'redirect_loop') return {status: 302, location: url.includes('?') ? ENTRY : ENTRY + '?loop=1'};
  let body = '<p>FICTIONAL browser-control fixture only</p>';
  if (['iframe', 'child_consent', 'duplicate_dashboard'].includes(caseName)) body += `<iframe src="${VIEW}"></iframe>`;
  if (caseName === 'duplicate_dashboard') body += `<iframe src="${VIEW}"></iframe>`;
  if (caseName === 'worker') body += `<script>new Worker('${WORKER}')</script>`;
  if (caseName === 'shared_worker') body += `<script>globalThis.fixtureWorker=new SharedWorker('${WORKER}')</script>`;
  if (caseName === 'popup') body += `<script>window.open('${ENTRY}?popup=1')</script>`;
  if (caseName === 'authorization') body += `<script>fetch('${MODEL}',{headers:{Authorization:'FICTIONAL_SECRET'}})</script>`;
  return {mime: 'text/html', body};
}
async function runCase(executable, caseName) {
  const result = {case: caseName, source_access: false, requests: [], targets: [],
    dashboard_loads: 0, top_navigations: 0, stop_reason: null, passed: false};
  let browser, pipe, defaultGuard, sourceGuard, contextId, rootSession, rootTarget;
  let closing = false; const sessions = new Map();
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'gfjd-offline-cdp-'));
  const stop = reason => {
    if (result.stop_reason || closing) return;
    result.stop_reason = reason;
    if (sourceGuard) void sourceGuard.close();
    if (pipe) pipe.close();
    if (browser && browser.exitCode === null && browser.signalCode === null) browser.kill('SIGTERM');
  };
  const deadline = setTimeout(() => stop('controller_deadline'), 15000);
  const safeSend = async (method, params, sessionId) => {
    if (result.stop_reason) throw new Error('terminal');
    result.control_stage = method;
    return pipe.send(method, params, sessionId);
  };
  try {
    defaultGuard = await startGuard({allowedHosts: PLAN.allowed_hosts, offline: true});
    sourceGuard = await startGuard({allowedHosts: PLAN.allowed_hosts, offline: true, onStop: stop});
    browser = cp.spawn(executable, ['--headless=new', '--remote-debugging-pipe',
      `--user-data-dir=${profile}`, `--proxy-server=http://127.0.0.1:${defaultGuard.port}`,
      '--proxy-bypass-list=<-loopback>', '--disable-quic', '--dns-prefetch-disable',
      '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost',
      '--disable-background-networking', '--disable-component-update', '--disable-extensions',
      '--disable-sync', '--no-first-run', '--no-default-browser-check', '--disable-popup-blocking',
      '--force-webrtc-ip-handling-policy=disable_non_proxied_udp', 'about:blank'],
      {stdio: ['ignore', 'ignore', 'ignore', 'pipe', 'pipe']});
    browser.on('error', () => stop('browser_launch_failure'));
    pipe = new CdpPipe(browser.stdio[3], browser.stdio[4], stop);
    pipe.on('event', event => { void (async () => {
      if (result.stop_reason || closing) return;
      const p = event.params || {}, session = sessions.get(event.sessionId);
      if (event.method === 'Target.detachedFromTarget' && sessions.has(p.sessionId)) return stop('target_detached');
      if (event.method === 'Target.attachedToTarget') {
        if (!contextId || p.targetInfo.browserContextId !== contextId) {
          await pipe.send('Runtime.runIfWaitingForDebugger', {}, p.sessionId); return;
        }
        if (!['page', 'iframe', 'worker', 'shared_worker'].includes(p.targetInfo.type)) {
          result.unsupported_target_type = targetTypeLabel(p.targetInfo.type);
          return stop('unsupported_target');
        }
        if (p.targetInfo.type === 'page' && rootTarget) return stop('extra_page');
        if (p.targetInfo.type === 'page') rootTarget = p.targetInfo.targetId;
        const record = {type: p.targetInfo.type, initialized: false, resumed: false};
        result.targets.push(record); sessions.set(p.sessionId, record);
        await safeSend('Target.setAutoAttach', autoAttach, p.sessionId);
        await safeSend('Fetch.enable', {patterns: [{urlPattern: '*', requestStage: 'Request'},
          {urlPattern: '*', requestStage: 'Response'}], handleAuthRequests: true}, p.sessionId);
        await safeSend('Runtime.enable', {}, p.sessionId);
        if (['page', 'iframe'].includes(record.type)) {
          await safeSend('Page.enable', {}, p.sessionId);
          const tree = await safeSend('Page.getFrameTree', {}, p.sessionId);
          record.mainFrame = tree.frameTree.frame.id;
          await safeSend('Runtime.addBinding', {name: '__gfjdStop'}, p.sessionId);
          await safeSend('Page.addScriptToEvaluateOnNewDocument', {source: `(${consentScript.toString()})()`}, p.sessionId);
        }
        record.initialized = true;
        await safeSend('Runtime.runIfWaitingForDebugger', {}, p.sessionId); record.resumed = true;
        if (record.type === 'page') rootSession = p.sessionId;
        return;
      }
      if (event.method === 'Runtime.bindingCalled' && p.name === '__gfjdStop') return stop('consent_or_authentication_ui');
      if (event.method === 'Fetch.authRequired') return stop('authentication_challenge');
      if (event.method !== 'Fetch.requestPaused') return;
      if (result.stop_reason) return;
      if (!session || !session.initialized) return stop('uninitialized_target');
      if (p.responseStatusCode !== undefined || p.responseErrorReason) {
        // The experiment fulfills at request stage. Unexpected real responses fail.
        return stop('unexpected_response');
      }
      const info = requestMetadata(p.request.url, p.request.method, p.request.headers);
      if (info.deny || info.optional) return stop(info.deny || 'optional_blocked');
      if (result.requests.length >= PLAN.max_requests) return stop('request_budget');
      if (p.resourceType === 'Document') {
        if (!['official_page', 'public_view'].includes(info.category)) return stop('document_path_denied');
        if (session.type === 'page' && p.frameId === session.mainFrame && ++result.top_navigations > PLAN.max_navigations) return stop('navigation_budget');
        if (info.category === 'public_view' && ++result.dashboard_loads > 1) return stop('dashboard_budget');
      }
      if (caseName === 'simulated_checkpoint_stop') return stop('checkpoint_failure');
      result.requests.push({...info, target_type: session.type});
      if (caseName === 'proxy_isolation') {
        await safeSend('Fetch.continueRequest', {requestId: p.requestId}, event.sessionId); return;
      }
      const reply = fixture(caseName, p.request.url);
      await safeSend('Fetch.fulfillRequest', {requestId: p.requestId, responseCode: reply.status || 200,
        responseHeaders: reply.location ? [{name: 'Location', value: reply.location}] :
          [{name: 'Content-Type', value: reply.mime}, {name: 'Access-Control-Allow-Origin', value: '*'},
            {name: 'Access-Control-Allow-Headers', value: '*'}],
        body: Buffer.from(reply.body || '').toString('base64')}, event.sessionId);
    })().catch(() => stop('controller_failure')); });
    await safeSend('Target.setAutoAttach', autoAttach);
    contextId = (await safeSend('Target.createBrowserContext', {
      proxyServer: `http://127.0.0.1:${sourceGuard.port}`, proxyBypassList: '<-loopback>'})).browserContextId;
    await safeSend('Target.createTarget', {url: 'about:blank', browserContextId: contextId});
    const started = Date.now();
    while (!rootSession && !result.stop_reason && Date.now() - started < 10000) await pause(20);
    if (!rootSession) stop('target_setup_timeout');
    if (!result.stop_reason) {
      await safeSend('Page.navigate', {url: ENTRY}, rootSession);
      const limit = Date.now() + (caseName === 'observation_deadline_stop' ? 40 : 2000);
      while (!result.stop_reason && Date.now() < limit) await pause(20);
      if (caseName === 'observation_deadline_stop') stop('wall_timeout');
    }
  } catch { stop('controller_failure'); }
  finally {
    closing = true;
    clearTimeout(deadline);
    if (sourceGuard) await sourceGuard.close();
    if (defaultGuard) await defaultGuard.close();
    if (pipe) pipe.close();
    let profileMayBeRemoved = true;
    if (browser && browser.exitCode === null && browser.signalCode === null) {
      const terminated = new Promise(resolve => browser.once('exit', resolve));
      browser.kill('SIGTERM');
      await Promise.race([terminated, pause(2000)]);
      if (browser.exitCode === null && browser.signalCode === null) {
        profileMayBeRemoved = false;
        browser.kill('SIGKILL');
        await Promise.race([terminated, pause(2000)]);
      }
    }
    // Only the exact temporary profile created above, containing fictional data.
    result.profile_cleanup = profileMayBeRemoved ? 'removed_after_exit' : 'retained_after_forced_termination';
    if (profileMayBeRemoved) fs.rmSync(profile, {recursive: true, force: true});
    result.default_transport = defaultGuard ? {...defaultGuard.counters} : null;
    result.context_transport = sourceGuard ? {...sourceGuard.counters} : null;
    for (const record of result.targets) delete record.mainFrame;
  }
  const expected = {popup: 'extra_page', redirect_same_host: 'path_denied', redirect_other_host: 'destination_denied',
    redirect_loop: 'navigation_budget', authorization: 'authentication_header', duplicate_dashboard: 'dashboard_budget',
    child_consent: 'consent_or_authentication_ui', simulated_checkpoint_stop: 'checkpoint_failure', observation_deadline_stop: 'wall_timeout',
    proxy_isolation: 'offline_egress_denied'};
  const modelSeen = result.requests.some(x => x.category === 'models');
  const success = expected[caseName] ? result.stop_reason === expected[caseName] :
    !result.stop_reason && modelSeen && result.targets.some(x => x.type === (caseName === 'iframe' ? 'iframe' : caseName) && x.initialized && x.resumed);
  result.passed = success && result.profile_cleanup === 'removed_after_exit' &&
    result.default_transport?.connections === 0 && result.default_transport?.stopReason === null &&
    result.default_transport?.bytes === 0 && result.context_transport?.bytes === 0 &&
    !JSON.stringify(result).includes('FICTIONAL_SECRET');
  return result;
}
async function main() {
  const args = process.argv.slice(2);
  if (args.length !== 4 || args[0] !== '--browser-executable' || args[2] !== '--attempt' || !/^[0-9]{2}$/.test(args[3])) throw new Error('arguments');
  const output = prepareOutput(path.resolve(__dirname, '..'), args[3]);
  const receipt = {kind: 'fictional_offline_cdp_experiment', source_execution_enabled: false,
    started_at: new Date().toISOString(), browser_sha256: hash(fs.readFileSync(args[1])),
    controller_sha256: hash(fs.readFileSync(__filename)),
    protocol_sha256: hash(fs.readFileSync(path.join(__dirname, 'g2_cdp_pipe.cjs'))),
    policy_sha256: hash(fs.readFileSync(path.join(__dirname, 'g2_browser_policy.cjs'))),
    transport_sha256: hash(fs.readFileSync(path.join(__dirname, 'g2_browser_egress.cjs'))),
    cases: [], passed: false};
  checkpoint(output, receipt);
  for (const caseName of CASES) {
    receipt.cases.push(await runCase(args[1], caseName)); checkpoint(output, receipt);
    if (!receipt.cases.at(-1).passed) break;
  }
  receipt.passed = receipt.cases.length === CASES.length && receipt.cases.every(item => item.passed);
  receipt.finished_at = new Date().toISOString(); checkpoint(output, receipt);
  process.stdout.write(JSON.stringify({receipt: path.relative(process.cwd(), output), passed: receipt.passed,
    cases: receipt.cases.map(x => ({case: x.case, passed: x.passed, stop_reason: x.stop_reason}))}) + '\n');
  process.exitCode = receipt.passed ? 0 : 2;
}
if (require.main === module) main().catch(() => { process.stdout.write('{"state":"offline_preflight_control_failure"}\n'); process.exitCode = 2; });
module.exports = {runCase, CASES, targetTypeLabel, prepareOutput};
