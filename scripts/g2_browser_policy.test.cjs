'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {PLAN, classify, requestMetadata, selectNavigation} = require('./g2_browser_policy.cjs');
const {checkpoint} = require('./inspect_g2_browser.cjs');

test('unqualified controller refuses real execution before runtime access', () => {
  const result = require('node:child_process').spawnSync(process.execPath,
    [path.join(__dirname, 'inspect_g2_browser.cjs')], {encoding: 'utf8'});
  assert.equal(result.status, 2);
  assert.deepEqual(JSON.parse(result.stdout), {state: 'pre_execution_control_failure'});
  assert.equal(result.stderr, '');
});

test('unknown and non-HTTPS destinations cannot become permitted browser requests', () => {
  for (const url of ['http://www.gov.uk/', 'https://user:pass@app.powerbi.com/view',
    'https://app.powerbi.com:444/view', 'https://app.powerbi.com.evil.invalid/',
    'file:///private/secret', 'https://127.0.0.1/', 'https://login.microsoftonline.com/']) {
    assert.ok(classify(url, 'GET').deny);
  }
});
test('only automatic model/query routes can POST; ordinary telemetry is blocked', () => {
  assert.equal(classify('https://app.powerbi.com/public/reports/querydata?synchronous=true', 'POST').category, 'query');
  assert.ok(classify('https://www.gov.uk/submit', 'POST').deny);
  assert.ok(classify('https://app.powerbi.com/submit', 'POST').deny);
  assert.ok(classify('https://dc.services.visualstudio.com/v2/track', 'POST').optional);
});
test('request metadata contains neither resource nor header values', () => {
  const result = requestMetadata('https://app.powerbi.com/view?r=FICTIONAL_SECRET', 'GET', {'X-PowerBI-ResourceKey': 'FICTIONAL_SECRET', Cookie: 'FICTIONAL_SECRET'});
  assert.deepEqual(result.header_names, ['x-powerbi-resourcekey']);
  assert.ok(!JSON.stringify(result).includes('FICTIONAL_SECRET'));
  assert.ok(requestMetadata(PLAN.entry, 'GET', {Authorization: 'Bearer FICTIONAL_SECRET'}).deny);
});
test('navigation uses fresh explicit links, rejects ambiguous views and follows bulletin detail', () => {
  const release = 'https://www.gov.uk/government/statistics/family-court-statistics-quarterly-january-to-march-2020';
  const detail = release + '/family-court-statistics-quarterly-january-to-march-2020';
  assert.equal(selectNavigation([{href: release, label: 'Quarter'}], PLAN.entry, new Set()), release);
  assert.equal(selectNavigation([{href: detail, label: 'Family Court Statistics Quarterly'}], release, new Set()), detail);
  const views = [{href:'https://app.powerbi.com/view?r=A',label:'Dashboard'}, {href:'https://app.powerbi.com/view?r=B',label:'Dashboard'}];
  assert.equal(selectNavigation(views, detail, new Set()), null);
  assert.equal(selectNavigation([views[0]], detail, new Set()), views[0].href);
});
test('exclusive checkpoint refuses a preexisting symlink without changing its target', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'gfjd-checkpoint-'));
  const file = path.join(temp, 'receipt.json');
  const target = path.join(temp, 'target');
  fs.writeFileSync(target, 'preserve');
  try {
    try { fs.symlinkSync(target, file + '.pending'); }
    catch (e) { if (e.code !== 'EPERM') throw e; fs.writeFileSync(file + '.pending', 'preserve'); }
    assert.throws(() => checkpoint(file, {}));
    assert.equal(fs.readFileSync(target, 'utf8'), 'preserve');
  } finally { fs.rmSync(temp, {recursive:true,force:true}); }
});
