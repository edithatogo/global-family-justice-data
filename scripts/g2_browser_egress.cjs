'use strict';

// A fail-closed CONNECT transport. It never decrypts or retains tunnel payloads.
const http = require('node:http');
const net = require('node:net');
const dns = require('node:dns').promises;

function isPublicAddress(address) {
  if (typeof address !== 'string' || address.includes('%')) return false;
  const family = net.isIP(address);
  if (family === 4) {
    const [a, b, c] = address.split('.').map(Number);
    return !(a === 0 || a === 10 || a === 127 || a >= 224 ||
      (a === 100 && b >= 64 && b <= 127) ||
      (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && (b === 168 || b === 0 || (b === 88 && c === 99) ||
        (b === 0 && c === 2))) ||
      (a === 198 && (b === 18 || b === 19 || (b === 51 && c === 100))) ||
      (a === 203 && b === 0 && c === 113));
  }
  if (family !== 6 || address.includes('.')) return false;
  const halves = address.toLowerCase().split('::');
  const left = halves[0] ? halves[0].split(':') : [];
  const right = halves.length > 1 && halves[1] ? halves[1].split(':') : [];
  const words = [...left, ...Array(8 - left.length - right.length).fill('0'), ...right]
    .map(value => parseInt(value, 16));
  // Only ordinary global unicast; exclude special-use, transition and documentation.
  return words[0] >= 0x2000 && words[0] <= 0x3fff &&
    !(words[0] === 0x2001 && (words[1] <= 0x1ff || words[1] === 0xdb8)) &&
    words[0] !== 0x2002 && words[0] !== 0x3fff;
}

function validName(host) {
  return typeof host === 'string' && host.length <= 253 && host === host.toLowerCase() &&
    host.includes('.') && !net.isIP(host) && host.split('.').every(label =>
      /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(label));
}

function validateConnectHost(authority, allowedHosts) {
  if (typeof authority !== 'string' || !authority.endsWith(':443')) return null;
  const host = authority.slice(0, -4);
  return validName(host) && new Set(allowedHosts).has(host) ? host : null;
}

async function startGuard({allowedHosts, maxBytes = 100 * 1024 * 1024,
  maxConnections = 200, deadlineMs = 900000, offline = false, onStop = () => {}}) {
  const hosts = new Set(allowedHosts);
  if (!hosts.size || [...hosts].some(host => !validName(host)) ||
      !Number.isSafeInteger(maxBytes) || maxBytes <= 0 || maxBytes > 104857600 ||
      !Number.isSafeInteger(maxConnections) || maxConnections <= 0 || maxConnections > 200 ||
      !Number.isSafeInteger(deadlineMs) || deadlineMs <= 0 || deadlineMs > 900000 ||
      typeof onStop !== 'function') throw new Error('invalid_guard_configuration');
  const counters = {connections: 0, bytes: 0, stopReason: null};
  const sockets = new Set();
  let closed = false;
  let closing;
  let timer;
  const server = http.createServer({maxHeaderSize: 8192}, () => stop('plain_http_denied'));
  function close() {
    if (closing) return closing;
    closed = true;
    clearTimeout(timer);
    for (const socket of sockets) socket.destroy();
    closing = new Promise(resolve => server.close(() => resolve()));
    return closing;
  }
  function stop(reason) {
    if (closed) return;
    counters.stopReason = reason;
    void close();
    try { Promise.resolve(onStop(reason)).catch(() => {}); } catch { /* already closed */ }
  }
  function track(socket) {
    sockets.add(socket);
    socket.once('close', () => sockets.delete(socket));
    socket.on('error', () => stop('transport_error'));
    if (closed) socket.destroy();
  }
  server.on('connection', socket => {
    track(socket);
    if (++counters.connections > maxConnections) stop('connection_budget');
  });
  server.on('clientError', () => stop('protocol_error'));
  server.on('error', () => stop('transport_error'));
  server.on('upgrade', () => stop('protocol_error'));
  server.on('connect', async (request, client, head) => {
    client.pause();
    if (offline) return stop('offline_egress_denied');
    const host = validateConnectHost(request.url, hosts);
    if (!host) return stop('destination_denied');
    if (closed) return;
    try {
      const addresses = await dns.lookup(host, {all: true, verbatim: true});
      if (closed || client.destroyed) return;
      if (!addresses.length || addresses.some(item => !isPublicAddress(item.address))) {
        return stop('address_denied');
      }
      // Connect the vetted literal, never the hostname; no DNS rebinding/fallback.
      const upstream = net.connect({host: addresses[0].address, family: addresses[0].family, port: 443});
      track(upstream);
      function forward(destination, data) {
        if (closed) return;
        if (data.length > maxBytes - counters.bytes) return stop('byte_budget');
        counters.bytes += data.length;
        if (!destination.write(data)) return false;
        return true;
      }
      upstream.once('connect', () => {
        if (closed) return;
        client.write('HTTP/1.1 200 Connection Established\r\n\r\n');
        const headReady = !head.length || forward(upstream, head);
        if (closed) return;
        client.on('data', data => { if (forward(upstream, data) === false) client.pause(); });
        upstream.on('drain', () => { if (!closed) client.resume(); });
        upstream.on('data', data => { if (forward(client, data) === false) upstream.pause(); });
        client.on('drain', () => { if (!closed) upstream.resume(); });
        if (headReady) client.resume();
      });
      client.once('close', () => upstream.destroy());
      upstream.once('close', () => client.destroy());
      client.once('end', () => upstream.end());
      upstream.once('end', () => client.end());
    } catch { stop('transport_error'); }
  });
  await new Promise((resolve, reject) => {
    server.once('error', () => reject(new Error('guard_start_failed')));
    server.listen(0, '127.0.0.1', resolve);
  });
  timer = setTimeout(() => stop('wall_timeout'), deadlineMs);
  const port = server.address().port;
  return {server, port, close, counters};
}

module.exports = {startGuard, isPublicAddress, validateConnectHost};
