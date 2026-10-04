// Проверка Worker без Cloudflare: node tools/progress-worker/test.mjs
import worker from './worker.js';
import assert from 'node:assert/strict';

const store = new Map();
const PROGRESS = {
  async get(k) { return store.has(k) ? store.get(k) : null; },
  async put(k, v) { store.set(k, v); },
  async list({ prefix }) { return { keys: [...store.keys()].filter(k => k.startsWith(prefix)).map(name => ({ name })) }; },
};
const env = { PASSWORD: 'correct horse battery staple', PROGRESS };
const O = 'https://anitech.meeymirita.ru';
const call = (path, opt = {}) => worker.fetch(new Request('https://w.test' + path, opt), env);
const auth = (pw) => ({ Authorization: 'Bearer ' + pw, Origin: O });

let r = await call('/api/progress', { headers: { Origin: O } }); assert.equal(r.status, 401, 'без пароля — 401');
r = await call('/api/progress', { headers: auth('wrong') }); assert.equal(r.status, 401, 'неверный пароль — 401');
r = await call('/api/progress/php', { method: 'PUT', headers: auth(env.PASSWORD), body: JSON.stringify({ data: { done: { 'step-1-1': true } }, t: 5 }) });
assert.equal(r.status, 200);
r = await call('/api/progress', { headers: auth(env.PASSWORD) }); const all = await r.json();
assert.deepEqual(all.php, { data: { done: { 'step-1-1': true } }, t: 5 });
assert.equal(r.headers.get('Access-Control-Allow-Origin'), O);
r = await call('/api/progress/../x', { method: 'PUT', headers: auth(env.PASSWORD), body: '{}' }); assert.equal(r.status, 404);
r = await call('/api/progress/bad slug!', { method: 'PUT', headers: auth(env.PASSWORD), body: '{}' }); assert.equal(r.status, 400);
r = await call('/api/progress/php', { method: 'PUT', headers: auth(env.PASSWORD), body: 'не json' }); assert.equal(r.status, 400);
r = await call('/api/progress/php', { method: 'PUT', headers: auth(env.PASSWORD), body: JSON.stringify({ data: [], t: 1 }) }); assert.equal(r.status, 400);
r = await call('/api/progress/php', { method: 'PUT', headers: auth(env.PASSWORD), body: 'x'.repeat(200000) }); assert.equal(r.status, 413);
r = await call('/api/progress', { headers: { Authorization: 'Bearer ' + env.PASSWORD, Origin: 'https://evil.example' } }); assert.equal(r.status, 403, 'чужой origin — 403');
r = await call('/api/progress', { method: 'OPTIONS', headers: { Origin: O } }); assert.equal(r.status, 204);
// после 10 неудачных попыток — 429, даже с верным паролем
store.delete('fail:unknown');
for (let i = 0; i < 10; i++) await call('/api/progress', { headers: auth('bad' + i) });
r = await call('/api/progress', { headers: auth(env.PASSWORD) }); assert.equal(r.status, 429, 'после 10 попыток — блокировка');
console.log('worker: все проверки пройдены');
