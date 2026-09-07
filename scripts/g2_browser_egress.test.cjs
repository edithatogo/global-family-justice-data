'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const net = require('node:net');
const dns = require('node:dns').promises;
const {once} = require('node:events');
const {Duplex} = require('node:stream');
const {startGuard, isPublicAddress, validateConnectHost} = require('./g2_browser_egress.cjs');

test('public addresses exclude private, mapped, scoped, documentation and transition space', () => {
  for (const address of ['0.0.0.0', '10.1.2.3', '100.64.0.1', '127.0.0.1',
    '169.254.169.254', '172.31.1.1', '192.168.0.1', '192.0.2.1', '198.18.0.1',
    '198.51.100.1', '203.0.113.1', '224.1.1.1', '255.255.255.255', '::', '::1',
    '::ffff:8.8.8.8', '::ffff:808:808', 'fe80::1%en0', 'fc00::1', 'ff02::1',
    '2001:db8::1', '2001::1', '2002:0808:0808::1', '3fff::1', 'garbage']) {
    assert.equal(isPublicAddress(address), false, address);
  }
  for (const address of ['8.8.8.8', '1.1.1.1', '2606:4700:4700::1111', '2001:4860:4860::8888']) {
    assert.equal(isPublicAddress(address), true, address);
  }
});

test('CONNECT authority is exact and cannot carry credentials, alternate ports or IPs', () => {
  const hosts = ['example.org'];
  assert.equal(validateConnectHost('example.org:443', hosts), 'example.org');
  for (const value of ['user@example.org:443', 'example.org:80', 'example.org:0443',
    'example.org:443/path', 'example.org.:443', 'EXAMPLE.ORG:443', 'other.example.org:443',
    'example.org:443\r\n', 'https://example.org:443', '127.0.0.1:443', '[::1]:443',
    '[::ffff:8.8.8.8]:443', '[fe80::1%en0]:443']) {
    assert.equal(validateConnectHost(value, hosts), null, value);
  }
});

async function exercise(request, expected, options = {}) {
  let notify;
  const stopped = new Promise(resolve => { notify = resolve; });
  const guard = await startGuard({allowedHosts: ['example.org'], onStop: notify, ...options});
  const socket = net.connect({host: '127.0.0.1', port: guard.port});
  socket.on('error', () => {});
  try {
    await once(socket, 'connect');
    socket.write(request);
    assert.equal(await stopped, expected);
    await Promise.all([guard.close(), guard.close()]);
    assert.equal(guard.counters.stopReason, expected);
    assert.equal(guard.server.listening, false);
  } finally { socket.destroy(); await guard.close(); }
}

test('plain HTTP and unexpected CONNECT terminate the entire guard', async () => {
  await exercise('GET http://example.org/ HTTP/1.1\r\nHost: example.org\r\n\r\n', 'plain_http_denied');
  await exercise('CONNECT other.example.org:443 HTTP/1.1\r\nHost: other.example.org\r\n\r\n', 'destination_denied');
});

test('offline mode rejects even allowlisted CONNECT before DNS', async t => {
  let lookups = 0;
  t.mock.method(dns, 'lookup', async () => { lookups++; throw new Error('must not resolve'); });
  await exercise('CONNECT example.org:443 HTTP/1.1\r\nHost: example.org\r\n\r\n', 'offline_egress_denied', {offline: true});
  assert.equal(lookups, 0);
});

test('mixed public/private DNS responses fail closed without connecting upstream', async t => {
  t.mock.method(dns, 'lookup', async () => [{address: '8.8.8.8', family: 4}, {address: '127.0.0.1', family: 4}]);
  await exercise('CONNECT example.org:443 HTTP/1.1\r\nHost: example.org\r\n\r\n', 'address_denied');
});

test('DNS errors reveal only the fixed category', async t => {
  t.mock.method(dns, 'lookup', async () => { throw new Error('sensitive detail'); });
  await exercise('CONNECT example.org:443 HTTP/1.1\r\nHost: example.org\r\n\r\n', 'transport_error');
});

test('wall timeout closes idle connections and repeated close resolves', async () => {
  let notify;
  const stopped = new Promise(resolve => { notify = resolve; });
  const guard = await startGuard({allowedHosts: ['example.org'], deadlineMs: 20, onStop: notify});
  assert.equal(await stopped, 'wall_timeout');
  await Promise.all([guard.close(), guard.close()]);
});

test('configuration cannot raise frozen maximum budgets', async () => {
  for (const option of [{maxBytes: 104857601}, {maxConnections: 201}, {deadlineMs: 900001},
    {allowedHosts: ['127.0.0.1']}, {allowedHosts: ['example.org.']}]) {
    await assert.rejects(startGuard({allowedHosts: ['example.org'], ...option}), /invalid_guard_configuration/);
  }
});

test('connection budget closes every accepted socket', async () => {
  let notify;
  const stopped = new Promise(resolve => { notify = resolve; });
  const guard = await startGuard({allowedHosts: ['example.org'], maxConnections: 1, onStop: notify});
  const first = net.connect({host: '127.0.0.1', port: guard.port});
  first.on('error', () => {});
  await once(first, 'connect');
  const second = net.connect({host: '127.0.0.1', port: guard.port});
  second.on('error', () => {});
  assert.equal(await stopped, 'connection_budget');
  await guard.close();
  first.destroy();
  second.destroy();
  assert.equal(guard.counters.connections, 2);
});

test('encrypted byte budget applies before forwarding and uses one vetted literal', async t => {
  const originalConnect = net.connect;
  const attempts = [];
  const forwarded = [];
  t.mock.method(dns, 'lookup', async () => [{address: '8.8.8.8', family: 4}, {address: '1.1.1.1', family: 4}]);
  t.mock.method(net, 'connect', options => {
    if (options.host === '127.0.0.1') return originalConnect(options);
    attempts.push(options);
    const upstream = new Duplex({read() {}, write(data, encoding, callback) {
      forwarded.push(data.length); callback();
    }});
    process.nextTick(() => upstream.emit('connect'));
    return upstream;
  });
  await exercise('CONNECT example.org:443 HTTP/1.1\r\nHost: example.org\r\n\r\n12345', 'byte_budget', {maxBytes: 4});
  assert.deepEqual(attempts, [{host: '8.8.8.8', family: 4, port: 443}]);
  assert.deepEqual(forwarded, []);
});
