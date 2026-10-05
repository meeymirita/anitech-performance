// Cloudflare Worker: хранит прогресс методичек (и ничего больше) в KV.
// Секретов в этом файле нет: пароль лежит в секрете Worker с именем PASSWORD, хранилище — привязка KV с именем PROGRESS.
//
//   GET  /api/progress          → { "<slug>": { "data": {...}, "t": <мс> }, ... }
//   PUT  /api/progress/<slug>   тело: { "data": {...}, "t": <мс> }
//   Все запросы: заголовок  Authorization: Bearer <пароль>
//
// Защита: пароль (сравнение за постоянное время), ограничение числа неудачных попыток с одного IP,
// CORS только для наших адресов, ограничение размера и формата данных.

const ORIGINS = [
  'https://anitech.meeymirita.ru',
  'https://meeymirita-files.storage.yandexcloud.net',   // методички открываются из бакета Object Storage
];
const SLUG = /^[a-z0-9][a-z0-9._-]{0,80}$/i;
const MAX_BODY = 100_000;         // байт на одну лабу
const MAX_FAILS = 10;             // неудачных попыток за окно
const FAIL_WINDOW = 900;          // секунд

function cors(req, env) {
  const origin = req.headers.get('Origin') || '';
  const extra = (env.EXTRA_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  const ok = ORIGINS.includes(origin) || extra.includes(origin);
  return {
    'Access-Control-Allow-Origin': ok ? origin : ORIGINS[0],
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...headers } });
}

async function same(a, b) {            // сравнение за постоянное время через хеши одинаковой длины
  const enc = new TextEncoder();
  const [ha, hb] = await Promise.all([crypto.subtle.digest('SHA-256', enc.encode(a)), crypto.subtle.digest('SHA-256', enc.encode(b))]);
  const x = new Uint8Array(ha), y = new Uint8Array(hb);
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

export default {
  async fetch(req, env) {
    const h = cors(req, env);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
    const origin = req.headers.get('Origin');
    if (origin && !(h['Access-Control-Allow-Origin'] === origin)) return json({ error: 'origin' }, 403, h);

    const url = new URL(req.url);
    const m = url.pathname.match(/^\/api\/progress(?:\/([^/]+))?$/);
    if (!m) return json({ error: 'not found' }, 404, h);
    if (!env.PASSWORD || !env.PROGRESS) return json({ error: 'worker is not configured' }, 500, h);

    // лимит неудачных попыток по IP
    const ip = req.headers.get('CF-Connecting-IP') || 'unknown';
    const failKey = 'fail:' + ip;
    const fails = parseInt((await env.PROGRESS.get(failKey)) || '0', 10);
    if (fails >= MAX_FAILS) return json({ error: 'too many attempts' }, 429, { ...h, 'Retry-After': String(FAIL_WINDOW) });

    const auth = (req.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
    if (!auth || !(await same(auth, env.PASSWORD))) {
      await env.PROGRESS.put(failKey, String(fails + 1), { expirationTtl: FAIL_WINDOW });
      return json({ error: 'unauthorized' }, 401, h);
    }

    if (req.method === 'GET' && !m[1]) {
      const list = await env.PROGRESS.list({ prefix: 'p:' });
      const out = {};
      for (const k of list.keys) {
        const v = await env.PROGRESS.get(k.name);
        if (v) { try { out[k.name.slice(2)] = JSON.parse(v); } catch (e) {} }
      }
      return json(out, 200, h);
    }

    if (req.method === 'PUT' && m[1]) {
      const slug = decodeURIComponent(m[1]);
      if (!SLUG.test(slug)) return json({ error: 'bad slug' }, 400, h);
      const text = await req.text();
      if (text.length > MAX_BODY) return json({ error: 'too large' }, 413, h);
      let body;
      try { body = JSON.parse(text); } catch (e) { return json({ error: 'bad json' }, 400, h); }
      if (!body || typeof body !== 'object' || typeof body.t !== 'number' || !body.data || typeof body.data !== 'object' || Array.isArray(body.data)) {
        return json({ error: 'bad body' }, 400, h);
      }
      await env.PROGRESS.put('p:' + slug, JSON.stringify({ data: body.data, t: body.t }));
      return json({ ok: true }, 200, h);
    }

    return json({ error: 'method not allowed' }, 405, h);
  },
};
