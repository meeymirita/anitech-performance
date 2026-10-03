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
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'fixes', 'common', '_tools'))
import bundle

# 1. лабы из lab.js (через node: файл — обычный JS-массив LABS)
js = open('works/js/lab.js', encoding='utf-8').read()
a = js.index('var LABS = ['); b = js.index('\n];\n', a) + 3
code = js[a:b] + "\nprocess.stdout.write(JSON.stringify(LABS.map(l => ({key:l.key,title:l.title,subtitle:l.subtitle,open:l.open.replace('../',''),accent:l.accent,difficulty:l.difficulty}))));"
labs = json.loads(subprocess.run(['node', '-e', code], capture_output=True, text=True, check=True).stdout)

# 2. порядок и направления — как на главной (ORDER/TRACKS в lab-anime.js)
anim = open('works/js/lab-anime.js', encoding='utf-8').read()
tracks = []
for m in re.finditer(r"\{\s*n:\s*\d+,\s*title:\s*'([^']+)',\s*keys:\s*\[(.*?)\]\s*\}", anim, re.S):
    tracks.append((m.group(1), re.findall(r"'([^']+)'", m.group(2))))
by_key = {l['key']: l for l in labs}

# 3. из методичек: slug и ключи разделов
for l in labs:
    L, _ = json.JSONDecoder().raw_decode(bundle.load(l['open'])[len('window.LAB='):])
    l['slug'] = L['slug']
    l['units'] = [u['key'] for u in L['units']]
    depth = l['open'].count('/')
    l['href'] = l['open']

data = []
for title, keys in tracks:
    data.append({'title': title, 'labs': [{
        'key': k, 'title': by_key[k]['title'], 'subtitle': by_key[k]['subtitle'], 'difficulty': by_key[k]['difficulty'],
        'accent': by_key[k]['accent'], 'open': '../' + by_key[k]['href'], 'page': f'{k}.html',
        'thumb': f'images/thumbs/{k}.webp', 'storage': 'lab-redesign-v1:' + by_key[k]['slug'], 'units': by_key[k]['units'],
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
  <h1>Все работы и прогресс</h1>
  <p class="sub">Отмечайте разделы и шаги в методичках — здесь они сложатся в общий прогресс по каждой лабе.</p>
  <div class="total" id="total"></div>
  <div id="list"></div>
</div>
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

function render() {
  var allDone = 0, allTotal = 0, started = 0, finished = 0, secs = 0, html = '', n = 0;
  GROUPS.forEach(function (g) {
    html += '<h2>' + esc(g.title) + '</h2>';
    g.labs.forEach(function (lab) {
      n++;
      var p = readProgress(lab), pct = p.total ? Math.round(p.done / p.total * 100) : 0;
      allDone += p.done; allTotal += p.total; secs += p.secs;
      if (p.done) started++; if (p.total && p.done === p.total) finished++;
      html += '<div class="lab" style="--c:' + lab.accent + '">'
        + '<span class="num">' + String(n).padStart(2, '0') + '</span>'
        + '<img class="thumb" src="' + esc(lab.thumb) + '" alt="" width="64" height="64" loading="lazy">'
        + '<a class="name" href="' + esc(lab.open) + '"><span class="dot"></span>' + esc(lab.title) + '</a>'
        + '<span class="pct">' + pct + '% · ' + p.done + '/' + p.total + '</span>'
        + '<span class="meta">' + esc(lab.subtitle) + ' · ' + esc(lab.difficulty)
        + (p.secs ? ' · ' + fmtTime(p.secs) : '') + '<br>'
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
