'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const {PassThrough} = require('node:stream');
const {CdpPipe} = require('./g2_cdp_pipe.cjs');
test('browser UI is auxiliary and cannot admit any request or replace the root page', () => {
  const {targetPolicy, requestStop} = require('./g2_cdp_offline.cjs');
  assert.equal(targetPolicy('browser_ui', false), null);
  assert.equal(targetPolicy('browser_ui', true), null);
  assert.equal(targetPolicy('page', false), null);
  assert.equal(targetPolicy('page', true), 'extra_page');
  assert.equal(targetPolicy('unknown', false), 'unsupported_target');
  assert.equal(requestStop({type: 'browser_ui', initialized: true}), 'browser_ui_network');
  assert.equal(requestStop({type: 'browser_ui', initialized: false}), 'uninitialized_target');
});
test('auxiliary target guards are installed before resume without Page assumptions', async () => {
  const {initializeTarget} = require('./g2_cdp_offline.cjs');
  const calls = [], record = {type: 'browser_ui', initialized: false, resumed: false};
  await initializeTarget(async (method, params, session) => { calls.push({method, params, session}); return {}; }, record, 'fictional');
  assert.deepEqual(calls.map(x => x.method), ['Target.setAutoAttach', 'Fetch.enable', 'Runtime.enable', 'Runtime.runIfWaitingForDebugger']);
  assert.equal(calls[1].params.handleAuthRequests, true);
  assert.deepEqual(calls[1].params.patterns.map(x => x.requestStage), ['Request', 'Response']);
  assert.ok(calls.every(x => x.session === 'fictional'));
  assert.equal(record.resumed, true); assert.equal(record.mainFrame, undefined);
});
test('failed or interrupted auxiliary initialization never resumes the target', async () => {
  const {initializeTarget} = require('./g2_cdp_offline.cjs');
  for (const failedMethod of ['Target.setAutoAttach', 'Fetch.enable', 'Runtime.enable']) {
    const calls = [], record = {type: 'browser_ui', initialized: false, resumed: false};
    await assert.rejects(initializeTarget(async method => {
      calls.push(method); if (method === failedMethod) throw new Error('fixture_stop'); return {};
    }, record, 'fictional'), /fixture_stop/);
    assert.equal(record.resumed, false);
    assert.equal(calls.includes('Runtime.runIfWaitingForDebugger'), false);
  }
});
test('offline output creates the missing build parent but refuses reuse and symlinks', () => {
  const fs = require('node:fs'), os = require('node:os'), path = require('node:path');
  const {prepareOutput} = require('./g2_cdp_offline.cjs');
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'gfjd-fixture-output-')));
  try {
    const output = prepareOutput(root, '01');
    assert.equal(fs.existsSync(path.dirname(output)), true);
    assert.throws(() => prepareOutput(root, '01'), /EEXIST/);
    fs.symlinkSync(path.join(root, 'build', 'g2-cdp-offline-01'), path.join(root, 'build', 'g2-cdp-offline-02'), 'junction');
    assert.throws(() => prepareOutput(root, '02'), /output_symlink/);
  } finally { fs.rmSync(root, {recursive: true, force: true}); }
});
test('target type diagnostics cannot retain URLs, titles or credentials', () => {
  const {targetTypeLabel} = require('./g2_cdp_offline.cjs');
  assert.equal(targetTypeLabel('background_page'), 'background_page');
  for (const value of ['https://example.org/token', 'PRIVATE TITLE', 'x'.repeat(41), null]) {
    assert.equal(targetTypeLabel(value), 'unknown');
  }
});
test('pipe correlates fragmented replies and nested session events without logging', async () => {
  const input = new PassThrough(), output = new PassThrough(); let failure;
  const client = new CdpPipe(input, output, value => { failure = value; });
  const pending = client.send('Target.getTargets');
  output.write('{"id":1,"res'); output.write('ult":{"ok":true}}\0');
  assert.deepEqual(await pending, {ok: true});
  let event; client.on('event', value => { event = value; });
  output.write('{"method":"Fetch.requestPaused","sessionId":"fixture","params":{}}\0');
  assert.equal(event.sessionId, 'fixture'); assert.equal(failure, undefined); client.close();
});
test('pipe redacts remote errors and closes unknown or oversized messages', async () => {
  const input = new PassThrough(), output = new PassThrough(); const failures = [];
  const client = new CdpPipe(input, output, value => failures.push(value));
  const pending = client.send('Fictional.command');
  output.write('{"id":1,"error":{"message":"FICTIONAL_SECRET"}}\0');
  await assert.rejects(pending, /^Error: protocol_command_failed$/);
  output.write('{"id":99}\0'); assert.deepEqual(failures, ['protocol_unknown_reply']);
  const second = new CdpPipe(new PassThrough(), new PassThrough(), value => failures.push(value));
  second.receive(Buffer.alloc(4 * 1024 * 1024 + 1));
  assert.equal(failures.at(-1), 'protocol_size_limit');
});
test('terminal pipe state rejects subsequent sends', async () => {
  const client = new CdpPipe(new PassThrough(), new PassThrough(), () => {});
  client.close(); await assert.rejects(client.send('Browser.getVersion'), /protocol_closed/);
});
test('malformed envelopes stop without exposing their contents', () => {
  for (const value of [null, [], {id: 'secret'}, {id: -1}, {method: 'secret'}, {method: 'Target.event', params: null}]) {
    let failure;
    const client = new CdpPipe(new PassThrough(), new PassThrough(), reason => { failure = reason; });
    client.receive(Buffer.from(JSON.stringify(value) + '\0'));
    assert.equal(failure, 'protocol_invalid');
    assert.equal(client.closed, true);
  }
});
