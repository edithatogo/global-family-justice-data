'use strict';
// Dedicated pipe client: never prints protocol messages, errors or source data.
const {EventEmitter} = require('node:events');
class CdpPipe extends EventEmitter {
  constructor(input, output, onFailure) {
    super(); this.input = input; this.output = output; this.onFailure = onFailure;
    this.serial = 0; this.pending = new Map(); this.buffer = Buffer.alloc(0); this.closed = false;
    output.on('data', data => this.receive(data));
    output.on('error', () => this.fail('protocol_io_failure'));
    input.on('error', () => this.fail('protocol_io_failure'));
    output.on('end', () => { if (!this.closed) this.fail('protocol_closed'); });
  }
  fail(reason) {
    if (this.closed) return;
    this.close(); this.onFailure(reason);
  }
  close() {
    this.closed = true;
    for (const {reject, timer} of this.pending.values()) { clearTimeout(timer); reject(new Error('protocol_closed')); }
    this.pending.clear(); this.buffer = Buffer.alloc(0);
  }
  receive(data) {
    if (this.closed) return;
    if (data.length + this.buffer.length > 4 * 1024 * 1024) return this.fail('protocol_size_limit');
    this.buffer = Buffer.concat([this.buffer, data]);
    for (;;) {
      const end = this.buffer.indexOf(0); if (end < 0) return;
      const bytes = this.buffer.subarray(0, end); this.buffer = this.buffer.subarray(end + 1);
      let message;
      try { message = JSON.parse(bytes.toString('utf8')); } catch { return this.fail('protocol_invalid'); }
      if (!message || typeof message !== 'object' || Array.isArray(message)) return this.fail('protocol_invalid');
      if (Object.hasOwn(message, 'id')) {
        if (!Number.isSafeInteger(message.id) || message.id <= 0) return this.fail('protocol_invalid');
        const item = this.pending.get(message.id);
        if (!item) return this.fail('protocol_unknown_reply');
        clearTimeout(item.timer); this.pending.delete(message.id);
        if (message.error) item.reject(new Error('protocol_command_failed'));
        else item.resolve(message.result || {});
      } else if (typeof message.method === 'string' && /^[A-Za-z]+\.[A-Za-z]+$/.test(message.method) &&
        (!Object.hasOwn(message, 'params') || (message.params && typeof message.params === 'object' && !Array.isArray(message.params)))) this.emit('event', message);
      else return this.fail('protocol_invalid');
    }
  }
  send(method, params = {}, sessionId) {
    if (this.closed) return Promise.reject(new Error('protocol_closed'));
    const id = ++this.serial;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => this.fail('protocol_timeout'), 10000);
      this.pending.set(id, {resolve, reject, timer});
      try { this.input.write(JSON.stringify({id, method, params, ...(sessionId ? {sessionId} : {})}) + '\0'); }
      catch { this.fail('protocol_io_failure'); }
    });
  }
}
module.exports = {CdpPipe};
