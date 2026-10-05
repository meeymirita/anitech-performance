#!/usr/bin/env python3
"""Собирает works/progress.html — одну страницу со ссылками на все лабы и общим прогрессом по каждой.

Запуск из корня репозитория:  python3 tools/build-progress.py
Данные берёт из works/js/lab.js (ключ, название, путь к методичке, цвет) и из самих методичек
(slug и список ключей разделов/шагов — по ним считается прогресс). Сам прогресс страница читает
в браузере из localStorage тех же ключей, что пишут методички (lab-redesign-v1:<slug>), поэтому
работает только когда works/progress.html и методички открыты с одного адреса (GitHub Pages, python -m http.server).
Запускать заново при добавлении лабы или смене структуры методичек. tools/patch-manuals.py вставляет
в каждую методичку ссылку на эту страницу.
"""
import html, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'fixes', 'common', '_tools'))
import bundle

BUCKET = 'https://meeymirita-files.storage.yandexcloud.net'

# fixes/common/_tools/prep.py runs its CLI main() on import (no __main__ guard), so we can't
# just `import prep` — pull its LABS dict (key -> local path) out of the source instead.
_prep_src = open('fixes/common/_tools/prep.py', encoding='utf-8').read()
_m = re.search(r'\nLABS = \{(.*?)\n\}\n', _prep_src, re.S)
PREP_LABS = eval('{' + _m.group(1) + '}')

# 1. лабы из lab.js (через node: файл — обычный JS-массив LABS)
js = open('works/js/lab.js', encoding='utf-8').read()
a = js.index('var LABS = ['); b = js.index('\n];\n', a) + 3
code = js[a:b] + "\nprocess.stdout.write(JSON.stringify(LABS.map(l => ({key:l.key,title:l.title,subtitle:l.subtitle,open:l.open.replace('../',''),accent:l.accent,difficulty:l.difficulty}))));"
# code can exceed the OS arg-length limit once lab.js is big enough (hit with 22 labs) — run from a temp file, not -e
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
    tf.write(code)
    code_path = tf.name
try:
    labs = json.loads(subprocess.run(['node', code_path], capture_output=True, text=True, check=True).stdout)
finally:
    os.unlink(code_path)

# 2. порядок и направления — как на главной (ORDER/TRACKS в lab-anime.js)
anim = open('works/js/lab-anime.js', encoding='utf-8').read()
tracks = []
for m in re.finditer(r"\{\s*n:\s*\d+,\s*title:\s*'([^']+)',\s*keys:\s*\[(.*?)\]\s*\}", anim, re.S):
    tracks.append((m.group(1), re.findall(r"'([^']+)'", m.group(2))))
by_key = {l['key']: l for l in labs}

# «полностью вычитана и проверена»: в fixes/common/_verification.md уровень ✅ и пустая колонка «Что не проверено» (начинается с «—»);
# ключ лабы — имя файла из колонки «Где подробности» (fixes/<направление>/<лаба>.md)
verified = set()
vstatus = {}      # ключ -> ('full' | 'mostly' | 'partial', что не проверено)
for row in open('fixes/common/_verification.md', encoding='utf-8'):
    c = [x.strip() for x in row.strip().strip('|').split('|')]
    if len(c) == 6 and (c[1].startswith('✅') or c[1].startswith('🟡')):
        m = re.search(r'fixes/[^/]+/([\w-]+)\.md', c[5])
        if not (m and m.group(1) in by_key): continue
        key, left = m.group(1), re.sub(r'`', '', c[4])
        if c[1].startswith('🟡'): vstatus[key] = ('partial', left)
        elif left.startswith('—'): vstatus[key] = ('full', left[1:].strip(' ()')); verified.add(key)
        else: vstatus[key] = ('mostly', left)

# 3. из методичек: slug и ключи разделов — читаем ЛОКАЛЬНУЮ копию (prep.LABS), а не бакет
# (l['open'] из lab.js — это уже полный URL бакета, его используем только как ссылку, не как путь для чтения)
for l in labs:
    local_path = PREP_LABS.get(l['key'])
    if not local_path:
        sys.exit(f"tools/build-progress.py: лабы {l['key']!r} нет в fixes/common/_tools/prep.py LABS")
    L, _ = json.JSONDecoder().raw_decode(bundle.load(local_path)[len('window.LAB='):])
    l['slug'] = L['slug']
    l['units'] = [u['key'] for u in L['units']]
    l['href'] = l['open']

data = []
for title, keys in tracks:
    data.append({'title': title, 'labs': [{
        'key': k, 'title': by_key[k]['title'], 'subtitle': by_key[k]['subtitle'], 'difficulty': by_key[k]['difficulty'],
        'accent': by_key[k]['accent'], 'open': by_key[k]['href'], 'page': f'{k}.html',
        'thumb': f'{BUCKET}/{k}/thumb.webp', 'verified': k in verified, 'vstatus': vstatus.get(k, ('none', ''))[0], 'vnote': vstatus.get(k, ('none', ''))[1], 'storage': 'lab-redesign-v1:' + by_key[k]['slug'], 'units': by_key[k]['units'],
    } for k in keys]})
missing = set(by_key) - {l['key'] for g in data for l in g['labs']}
if missing:
    sys.exit(f'лабы не вошли ни в одно направление (lab-anime.js TRACKS): {sorted(missing)}')

TEMPLATE = r'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Все работы и прогресс — ANITECH</title>
<meta name="description" content="Все лабораторные ANITECH PERFORMANCE одним списком: ссылки на методички и общий прогресс по каждой.">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<style>
:root { --bg:#faf9f5; --ink:#17140f; --muted:#5d584f; --hair:#d9d4c8; --card:#fff; --track:#e8e3d6; --accent:#ec3013; }
@media (prefers-color-scheme: dark) { :root { --bg:#12110f; --ink:#f1ede4; --muted:#a39d90; --hair:#2f2c26; --card:#1a1815; --track:#2b2823; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
.wrap { max-width:960px; margin:0 auto; padding:32px 16px 64px; }
a { color:inherit; }
.back { font-size:14px; color:var(--muted); text-decoration:none; }
.back:hover { color:var(--ink); }
h1 { margin:12px 0 4px; font-size:clamp(28px,5vw,44px); line-height:1.05; letter-spacing:-.02em; }
.sub { margin:0 0 24px; color:var(--muted); }
.total { background:var(--card); border:2px solid var(--ink); padding:18px 20px; margin-bottom:32px; }
.total-top { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; font-weight:800; }
.bar { height:10px; background:var(--track); margin-top:10px; overflow:hidden; }
.bar > i { display:block; height:100%; width:0; background:var(--c, var(--accent)); transition:width .4s; }
.total-note { margin-top:8px; font-size:13px; color:var(--muted); }
h2 { margin:32px 0 10px; font-size:13px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }
.lab { display:grid; grid-template-columns:32px 64px minmax(0,1fr) minmax(130px,220px); gap:6px 16px; align-items:center; padding:12px 0; border-top:1px solid var(--hair); }
.thumb { grid-column:2; grid-row:1 / span 2; width:64px; height:64px; object-fit:cover; border:1px solid var(--hair); background:var(--track); display:block; }
.lab:last-child { border-bottom:1px solid var(--hair); }
.num { font:700 13px ui-monospace,Menlo,monospace; color:var(--muted); }
.name { font-weight:800; font-size:17px; text-decoration:none; }
.name:hover { color:var(--c); }
.name { grid-column:3; }
.meta { grid-column:3; font-size:13px; color:var(--muted); }
.meta a { margin-right:12px; }
.pct { text-align:right; font:700 13px ui-monospace,Menlo,monospace; }
.lab .bar { grid-column:4; grid-row:2; margin-top:0; }
.lab .pct { grid-column:4; grid-row:1; }
.fold { grid-column:1; grid-row:1; width:28px; height:28px; padding:0; border:1px solid var(--hair); background:var(--card); color:var(--muted); font:700 14px ui-monospace,Menlo,monospace; cursor:pointer; }
.fold:hover { color:var(--ink); border-color:var(--ink); }
.fold::before { content:'−'; } .lab.collapsed .fold::before { content:'+'; }
.lab.collapsed { padding:7px 0; }
.lab.collapsed .thumb, .lab.collapsed .meta, .lab.collapsed .bar { display:none; }
.lab.collapsed .name, .lab.collapsed .pct { grid-row:1; }
.lab.collapsed .name { grid-column:2 / 4; }
.lab .num { display:none; }
.ok { display:inline-flex; align-items:center; gap:6px; color:#1f8a47; font-weight:700; }
.ok i { width:16px; height:16px; border-radius:50%; background:#1f8a47; color:#fff; font:700 11px/16px sans-serif; text-align:center; font-style:normal; }
.name .ok { margin-left:10px; vertical-align:1px; font-size:12px; }
.part { display:inline-flex; align-items:center; gap:6px; color:var(--muted); font-weight:700; }
.part i { width:16px; height:16px; border-radius:50%; background:#c98a00; color:#fff; font:700 11px/16px sans-serif; text-align:center; font-style:normal; }
.name .part { margin-left:10px; font-size:12px; }
.note { font-size:12px; color:var(--muted); }
.legend { margin:0 0 10px; font-size:13px; color:var(--muted); }
.tools { display:flex; gap:8px; margin:0 0 8px; }
.tools button { font:inherit; font-size:13px; padding:4px 10px; border:1px solid var(--hair); background:var(--card); color:var(--ink); cursor:pointer; }
@media (prefers-color-scheme: dark) { .ok { color:#4cc87a; } .ok i { background:#2f9e5a; } }
.dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--c); margin-right:8px; }
@media (max-width:620px) {
  .lab { grid-template-columns:26px 52px minmax(0,1fr); }
  .thumb { width:52px; height:52px; }
  .lab .pct, .lab .bar { grid-column:3; grid-row:auto; text-align:left; }
}
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="../index.html">← ANITECH PERFORMANCE</a>
  <a class="back" style="float:right" href="verification.html">Что чем проверено →</a>
  <h1>Все работы и прогресс</h1>
  <p class="sub">Отмечайте разделы и шаги в методичках — здесь они сложатся в общий прогресс по каждой лабе.</p>
  <div class="total" id="total"></div>
  <p class="legend">✓ — вычитана и проверена полностью. «*» — нужен аккаунт, домен или ключи: такой пункт считается выполненным, его проверяете сами при реальном прохождении.</p>
  <div class="tools"><button type="button" id="foldAll">Свернуть все</button><button type="button" id="unfoldAll">Развернуть все</button></div>
  <div id="list"></div>
</div>
<script src="js/sync.js"></script>
<script>
var GROUPS = __DATA__;

function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

function readProgress(lab) {
  var done = 0, secs = 0;
  try {
    var saved = JSON.parse(localStorage.getItem(lab.storage) || '{}');
    var map = saved.done || {};
    done = lab.units.filter(function (k) { return map[k]; }).length;
    secs = saved.tTotal || 0;
  } catch (e) {}
  return { done: done, total: lab.units.length, secs: secs };
}

function fmtTime(s) {
  if (!s) return '';
  var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
  return h ? h + ' ч ' + m + ' мин' : m + ' мин';
}

var FOLD_KEY = 'anitech-progress-folded';
function folded() { try { return JSON.parse(localStorage.getItem(FOLD_KEY) || '{}'); } catch (e) { return {}; } }
function setFolded(m) { try { localStorage.setItem(FOLD_KEY, JSON.stringify(m)); } catch (e) {} }
function statusBadge(lab, short) {
  if (lab.vstatus === 'full') return okBadge(short);
  var t = esc(lab.vnote || '');
  if (lab.vstatus === 'mostly') return '<span class="part" title="Не проверено: ' + t + '"><i>~</i>' + (short ? 'в основном' : 'Вычитана, проверена в основном') + '</span>';
  if (lab.vstatus === 'partial') return '<span class="part" title="Не проверено: ' + t + '"><i>½</i>' + (short ? 'частично' : 'Вычитана, проверена частично') + '</span>';
  return '';
}
function okBadge(short) { return '<span class="ok"><i>✓</i>' + (short ? 'проверена' : 'Полностью вычитана и проверена') + '</span>'; }

function render() {
  var fold = folded();
  var allDone = 0, allTotal = 0, started = 0, finished = 0, secs = 0, html = '', n = 0;
  GROUPS.forEach(function (g) {
    html += '<h2>' + esc(g.title) + '</h2>';
    g.labs.forEach(function (lab) {
      n++;
      var p = readProgress(lab), pct = p.total ? Math.round(p.done / p.total * 100) : 0;
      allDone += p.done; allTotal += p.total; secs += p.secs;
      if (p.done) started++; if (p.total && p.done === p.total) finished++;
      html += '<div class="lab' + (fold[lab.key] ? ' collapsed' : '') + '" data-key="' + lab.key + '" style="--c:' + lab.accent + '">'
        + '<button type="button" class="fold" title="Свернуть / развернуть" aria-label="Свернуть или развернуть"></button>'
        + '<span class="num">' + String(n).padStart(2, '0') + '</span>'
        + '<img class="thumb" src="' + esc(lab.thumb) + '" alt="" width="64" height="64" loading="lazy">'
        + '<a class="name" href="' + esc(lab.open) + '"><span class="dot"></span>' + esc(lab.title) + (lab.vstatus !== 'none' ? statusBadge(lab, true) : '') + '</a>'
        + ''        + '<span class="pct">' + pct + '% · ' + p.done + '/' + p.total + '</span>'
        + '<span class="meta">' + esc(lab.subtitle) + ' · ' + esc(lab.difficulty)
        + (p.secs ? ' · ' + fmtTime(p.secs) : '') + '<br>'
        + (lab.vstatus !== 'none' ? statusBadge(lab, false) + (lab.vnote ? ' <span class="note">' + (lab.vstatus === 'full' ? '· * ' : '· не проверено: ') + esc(lab.vnote) + '</span>' : '') + '<br>' : '')
        + '<a href="' + esc(lab.open) + '">Методичка ↗</a><a href="' + esc(lab.page) + '">Страница лабы</a></span>'
        + '<div class="bar"><i style="width:' + pct + '%"></i></div>'
        + '</div>';
    });
  });
  document.getElementById('list').innerHTML = html;
  var all = allTotal ? Math.round(allDone / allTotal * 100) : 0;
  document.getElementById('total').innerHTML =
    '<div class="total-top"><span>Общий прогресс</span><span>' + all + '%</span></div>'
    + '<div class="bar"><i style="width:' + all + '%"></i></div>'
    + '<div class="total-note">отмечено ' + allDone + ' из ' + allTotal + ' разделов и шагов · начато лаб: ' + started + ' из ' + n
    + ' · пройдено целиком: ' + finished + (secs ? ' · времени в методичках: ' + fmtTime(secs) : '') + '</div>';
}
document.addEventListener('click', function (e) {
  var b = e.target.closest && e.target.closest('.fold');
  if (b) { var row = b.parentNode, m = folded(); row.classList.toggle('collapsed'); m[row.getAttribute('data-key')] = row.classList.contains('collapsed') ? 1 : 0; setFolded(m); }
});
function foldAll(on) { var m = {}; GROUPS.forEach(function (g) { g.labs.forEach(function (l) { m[l.key] = on ? 1 : 0; }); }); setFolded(m); render(); }
document.getElementById('foldAll').onclick = function () { foldAll(true); };
document.getElementById('unfoldAll').onclick = function () { foldAll(false); };
render();
window.addEventListener('focus', render);          // вернулись из методички — обновить цифры
window.addEventListener('storage', render);
</script>
</body>
</html>
'''

out = TEMPLATE.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
open('works/progress.html', 'w', encoding='utf-8').write(out)
print(f'works/progress.html: {sum(len(g["labs"]) for g in data)} лаб, {len(out) // 1024} КБ')
