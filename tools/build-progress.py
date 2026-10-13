#!/usr/bin/env python3
"""Собирает works/progress.html — одну страницу со ссылками на все лабы и общим прогрессом по каждой.

Запуск из корня репозитория:  python3 tools/build-progress.py
Данные берёт из works/js/lab.js (ключ, название, путь к методичке, цвет) и из самих методичек
(slug и список ключей разделов/шагов — по ним считается прогресс). Сам прогресс страница читает
в браузере из localStorage тех же ключей, что пишут методички (lab-redesign-v1:<slug>), поэтому
работает только когда works/progress.html и методички открыты с одного адреса (боевой сайт, python -m http.server).
Запускать заново при добавлении лабы или смене структуры методичек. tools/patch-manuals.py вставляет
в каждую методичку ссылку на эту страницу.
"""
import html, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'fixes', 'common', '_tools'))
import bundle

BUCKET = 'https://meeymirita-files.storage.yandexcloud.net'

# лабы, которые владелец прошла целиком ДО появления прогресса на сайте и не отмечала в методичке:
# страница показывает их на 100% и в разделе «Пройдено». Сейчас пусто: RabbitMQ отмечена в методичке по-настоящему
# (с синхронизацией, 06.10.2026), статическая отметка скрывала бы возможные пропуски.
COMPLETED = set()

# лабы, которых ещё нет на сайте (нет методички/страницы): показываются отдельным разделом «Новые» со статусом «новая»,
# в общий прогресс не входят. При появлении методички — убрать отсюда и интегрировать по _checklist-new-lab.md.
PLANNED = [
    {'key': 'go-start', 'title': 'Go Start', 'subtitle': 'Go с нуля до middle (CoffeeGo)', 'difficulty': 'Базовая', 'accent': '#00ADD8',
     'note': 'методичка есть, но не принята и не интегрирована', 'repo': 'go-start-lab'},
    {'key': 'go-pro', 'title': 'Go Pro', 'subtitle': 'Go от middle до senior (CoffeeGo Platform)', 'difficulty': 'Высокая', 'accent': '#00ADD8',
     'note': 'методичка есть, но не вычитана и не интегрирована', 'repo': 'go-pro-lab'},
    {'key': 'ansible', 'title': 'Ansible Lab', 'subtitle': 'Управление серверами как кодом', 'difficulty': 'Средняя', 'accent': '#EE0000',
     'note': 'только план, методички нет', 'repo': 'ansible-lab'},
]

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
# Стандарт содержания лабы (решение владельца 12.10.2026, fixes/common/site.md): минимум 10 сессий,
# формат — как caddy/caddy.html (без инлайн-стилей, блок links на шаге). Считаем здесь же, из того же L.
SESSIONS_MIN = 10
for l in labs:
    local_path = PREP_LABS.get(l['key'])
    if not local_path:
        sys.exit(f"tools/build-progress.py: лабы {l['key']!r} нет в fixes/common/_tools/prep.py LABS")
    L, _ = json.JSONDecoder().raw_decode(bundle.load(local_path)[len('window.LAB='):])
    l['slug'] = L['slug']
    l['units'] = [u['key'] for u in L['units']]
    l['href'] = l['open']
    l['sessions'] = len(L.get('sessions') or [])
    dumped = json.dumps(L, ensure_ascii=False)
    inline_style = dumped.count('style=\\"')
    has_links = '"links"' in dumped
    l['format'] = 'standard' if inline_style < 100 else ('partial' if has_links else 'rework')

data = []
for title, keys in tracks:
    data.append({'title': title, 'labs': [{
        'key': k, 'title': by_key[k]['title'], 'subtitle': by_key[k]['subtitle'], 'difficulty': by_key[k]['difficulty'],
        'accent': by_key[k]['accent'], 'open': by_key[k]['href'], 'page': f'{k}.html',
        'thumb': f'{BUCKET}/{k}/thumb.webp', 'verified': k in verified, 'completed': k in COMPLETED, 'vstatus': vstatus.get(k, ('none', ''))[0], 'vnote': vstatus.get(k, ('none', ''))[1], 'storage': 'lab-redesign-v1:' + by_key[k]['slug'], 'units': by_key[k]['units'],
        'sessions': by_key[k]['sessions'], 'sessionsMin': SESSIONS_MIN, 'format': by_key[k]['format'],
    } for k in keys]})
missing = set(by_key) - {l['key'] for g in data for l in g['labs']}
if missing:
    sys.exit(f'лабы не вошли ни в одно направление (lab-anime.js TRACKS): {sorted(missing)}')


# ───────── вкладка «Порядок и содержание»: порядок, зависимости, сессии, часы ─────────
# Порядок и зависимости — works/js/prereq.js (ORDER, LABS.before/know/meet), содержание — из самих методичек
# (сессии, шаги, часы по длительности сессий), для лаб без методички — из плана (<лаба>/<лаба>_lab_plan.md).
def _scan_block(text, start, open_ch, close_ch):
    """Возвращает срез от open_ch до парной close_ch с учётом строк в кавычках."""
    i = text.index(open_ch, start); depth = 0; q = None; j = i
    while j < len(text):
        c = text[j]
        if q:
            if c == '\\': j += 1
            elif c == q: q = None
        elif c in '\'"`': q = c
        elif c == open_ch: depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0: return text[i:j + 1]
        j += 1
    raise ValueError('нет парной скобки')

_pre = open('works/js/prereq.js', encoding='utf-8').read()
_order_js = _scan_block(_pre, _pre.index('var ORDER ='), '[', ']')
_labs_js = _scan_block(_pre, _pre.index('var LABS ='), '{', '}')
_lev_js = _scan_block(_pre, _pre.index('var LEVELS ='), '{', '}')
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
    tf.write('var ORDER=' + _order_js + ';var LABS=' + _labs_js + ';var LEVELS=' + _lev_js
             + ';process.stdout.write(JSON.stringify({order:ORDER,labs:LABS,levels:LEVELS}));')
    _pp = tf.name
try:
    PRE = json.loads(subprocess.run(['node', _pp], capture_output=True, text=True, check=True).stdout)
finally:
    os.unlink(_pp)

def _minutes(txt):
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:[–-]\s*(\d+(?:[.,]\d+)?))?\s*(ч|час|мин)', txt or '')
    if not m: return 0
    a = float(m.group(1).replace(',', '.')); b = float(m.group(2).replace(',', '.')) if m.group(2) else a
    v = (a + b) / 2
    return v * 60 if m.group(3) in ('ч', 'час') else v

def _norm_h(txt):
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:[–-]\s*(\d+(?:[.,]\d+)?))?\s*(?:ч|час)', txt or '')
    if not m: return ''
    a = m.group(1).replace('.', ','); b = (m.group(2) or '').replace('.', ',')
    return '~' + a + ('–' + b if b else '') + ' ч'

def lab_content(key):
    path = PREP_LABS.get(key)
    if not path: return None
    L, _ = json.JSONDecoder().raw_decode(bundle.load(path)[len('window.LAB='):])
    um = {u['key']: u for u in L['units']}
    sess, tot, steps_n = [], 0.0, 0
    for sx in L.get('sessions') or []:
        st = [um[x] for x in sx['steps'] if x in um]
        mins = _minutes(sx.get('dur', '')) or sum(_minutes(u.get('est')) for u in st)
        tot += mins / 60; steps_n += len(st)
        sess.append({'n': sx['n'], 't': sx['title'], 'h': _norm_h(sx.get('dur', '')) or ('~%.1f ч' % (mins / 60)).replace('.', ','), 'steps': len(st)})
    refs = [u['title'] for u in L['units'] if u.get('kind') in ('theory', 'ref')]
    return {'sessions': sess, 'steps': steps_n, 'hours': round(tot, 1), 'refs': refs}

def plan_content(path):
    """Ansible: сессии из плана (### Сессия N · Название (~X ч))."""
    sess, tot = [], 0.0
    for m in re.finditer(r'^### Сессия (\d+) · (.+?) \(~?(\d+(?:[.,]\d+)?)\s*ч\)', open(path, encoding='utf-8').read(), re.M):
        h = float(m.group(3).replace(',', '.')); tot += h
        sess.append({'n': int(m.group(1)), 't': m.group(2), 'h': '~%s ч' % m.group(3), 'steps': 0})
    return {'sessions': sess, 'steps': 0, 'hours': round(tot, 1), 'refs': []}

_dir_of = {k: t for t, ks in tracks for k in ks}
_planned_by = {p['key']: p for p in PLANNED}
ORDERDATA = []
for k in PRE['order'] + [p['key'] for p in PLANNED]:
    pl = PRE['labs'].get(k, {})
    base = by_key.get(k) or _planned_by.get(k) or {}
    c = lab_content(k) if k != 'ansible' else (plan_content('ansible/ansible_lab_plan.md') if os.path.exists('ansible/ansible_lab_plan.md') else None)
    c = c or {'sessions': [], 'steps': 0, 'hours': 0, 'refs': []}
    lev = PRE['levels'].get(pl.get('level'), {})
    before = []
    for b in pl.get('before', []):
        t = (by_key.get(b['key']) or _planned_by.get(b['key']) or {}).get('title', b['key'])
        before.append({'key': b['key'], 'title': t, 'kind': b['kind'], 'why': b.get('why', '')})
    ORDERDATA.append({
        'key': k, 'title': base.get('title') or pl.get('name', k), 'subtitle': base.get('subtitle', ''), 'difficulty': base.get('difficulty', ''),
        'accent': base.get('accent') or pl.get('accent', '#888'), 'dir': _dir_of.get(k, 'Инфраструктура' if k == 'ansible' else 'Бэкенд'),
        'level': lev.get('label', ''), 'levelNote': lev.get('note', ''), 'headline': pl.get('headline', ''),
        'know': pl.get('know', []), 'meet': pl.get('meet', []), 'before': before, 'tip': pl.get('tip', ''),
        'sessions': c['sessions'], 'steps': c['steps'], 'hours': c['hours'], 'refs': c['refs'],
        'vstatus': vstatus.get(k, ('none', ''))[0], 'planned': k in _planned_by, 'note': _planned_by.get(k, {}).get('note', ''),
        'page': f'{k}.html' if k in by_key else '', 'open': by_key[k]['href'] if k in by_key else '',
        'format': by_key[k]['format'] if k in by_key else '',
    })

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
.lab { display:grid; grid-template-columns:32px 64px minmax(0,1fr) minmax(110px,170px) minmax(130px,160px); gap:6px 16px; align-items:center; padding:12px 0; border-top:1px solid var(--hair); }
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
.stats { grid-column:5; grid-row:1 / span 2; text-align:right; font-size:12px; line-height:1.6; }
.stats > span { display:block; }
.sess-ok { color:var(--muted); }
.sess-bad { color:#b3261e; font-weight:700; }
.fmt-ok { color:#1f8a47; font-weight:700; }
.fmt-partial { color:#c98a00; font-weight:700; }
.fmt-bad { color:#b3261e; font-weight:700; }
@media (prefers-color-scheme: dark) { .sess-bad, .fmt-bad { color:#ff8a80; } .fmt-ok { color:#4cc87a; } .fmt-partial { color:#e0ab2e; } }
.lab.collapsed .stats { display:none; }
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
.new { display:inline-flex; align-items:center; gap:6px; color:var(--muted); font-weight:700; }
.new i { padding:0 6px; border-radius:8px; background:var(--accent); color:#fff; font:700 11px/16px sans-serif; font-style:normal; }
.name .new { margin-left:10px; font-size:12px; }
.lab.planned { grid-template-columns:32px minmax(0,1fr); }
.lab.planned .name, .lab.planned .meta { grid-column:2; }
.dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--c); margin-right:8px; }
@media (max-width:620px) {
  .lab { grid-template-columns:26px 52px minmax(0,1fr); }
  .thumb { width:52px; height:52px; }
  .lab .pct, .lab .bar { grid-column:3; grid-row:auto; text-align:left; }
  .stats { grid-column:3; grid-row:auto; text-align:left; margin-top:4px; }
  .stats > span { display:inline; margin-right:10px; }
}

.tabs { display:flex; gap:6px; margin:0 0 22px; border-bottom:2px solid var(--ink); }
.tabs button { font:inherit; font-weight:800; font-size:14px; padding:9px 16px; border:2px solid var(--ink); border-bottom:none; background:var(--card); color:var(--muted); cursor:pointer; margin-bottom:-2px; }
.tabs button[aria-selected="true"] { background:var(--ink); color:var(--bg); }
[hidden] { display:none !important; }
.ord-sum { background:var(--card); border:2px solid var(--ink); padding:16px 20px; margin-bottom:18px; font-size:14px; }
.ord-sum b { font-size:20px; }
.ord-sum .row { display:flex; flex-wrap:wrap; gap:6px 22px; }
.ord-leg { font-size:13px; color:var(--muted); margin:0 0 14px; }
.chip { display:inline-block; padding:1px 8px; border:1px solid var(--hair); font-size:12px; margin:2px 4px 2px 0; background:var(--card); }
.chip.need { border-color:#b3261e; color:#b3261e; font-weight:700; } .chip.know { border-color:#c98a00; color:#a06c00; font-weight:700; } .chip.help { color:var(--muted); }
@media (prefers-color-scheme: dark) { .chip.need { color:#ff8a80; border-color:#ff8a80; } .chip.know { color:#e0ab2e; border-color:#e0ab2e; } }
details.ord { border-top:1px solid var(--hair); }
details.ord:last-of-type { border-bottom:1px solid var(--hair); }
details.ord > summary { display:grid; grid-template-columns:34px minmax(0,1fr) auto; gap:4px 14px; align-items:center; padding:12px 0; cursor:pointer; list-style:none; }
details.ord > summary::-webkit-details-marker { display:none; }
details.ord > summary:hover .on { color:var(--c); }
.on { font-weight:800; font-size:17px; }
.on i { font-style:normal; display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--c); margin-right:8px; }
.ono { font:700 13px ui-monospace,Menlo,monospace; color:var(--muted); }
.om { grid-column:2; font-size:13px; color:var(--muted); }
.ot { grid-column:3; grid-row:1 / span 2; text-align:right; font:700 13px ui-monospace,Menlo,monospace; line-height:1.5; }
.ot small { display:block; color:var(--muted); font-weight:400; }
.obody { padding:2px 0 18px 48px; font-size:14px; }
.obody h3 { margin:14px 0 4px; font-size:12px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); }
.obody ul { margin:4px 0; padding-left:18px; }
.obody table { border-collapse:collapse; width:100%; font-size:13px; margin:4px 0; }
.obody th, .obody td { padding:4px 8px; border-bottom:1px solid var(--hair); text-align:left; vertical-align:top; }
.obody th { color:var(--muted); font-weight:700; font-size:12px; }
.obody td.h { white-space:nowrap; font-family:ui-monospace,Menlo,monospace; }
.obody .lk a { margin-right:14px; }
.ord-h { margin:26px 0 8px; font-size:13px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); }
@media (max-width:620px) { .obody { padding-left:0; } details.ord > summary { grid-template-columns:28px minmax(0,1fr); } .ot { grid-column:2; grid-row:auto; text-align:left; } }
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="../index.html">← ANITECH PERFORMANCE</a>
  <a class="back" style="float:right" href="verification.html">Что чем проверено →</a>
  <h1>Все работы и прогресс</h1>
  <p class="sub">Отмечайте разделы и шаги в методичках — здесь они сложатся в общий прогресс по каждой лабе. Вкладка «Порядок и содержание» — в каком порядке проходить лабы и что в каждой внутри.</p>
  <div class="tabs" role="tablist"><button type="button" role="tab" id="tabP" aria-selected="true">Прогресс</button><button type="button" role="tab" id="tabO" aria-selected="false">Порядок и содержание</button></div>
  <div id="panelP">
  <div class="total" id="total"></div>
  <p class="legend">«новая» — лаба задумана или в работе, на сайте её ещё нет; в общий прогресс не входит. ✓ — вычитана и проверена полностью. «*» — нужен аккаунт, домен или ключи: такой пункт считается выполненным, его проверяете сами при реальном прохождении. Справа: сессий сейчас / не хватает до минимума 10–14 на лабу; формат — «эталон» (как `caddy.html`: без инлайн-стилей, quiz/links/outro на шаге), «частично» или «переделать» (решение владельца 12.10.2026, подробности — `fixes/common/site.md`).</p>
  <div class="tools"><button type="button" id="foldAll">Свернуть все</button><button type="button" id="unfoldAll">Развернуть все</button></div>
  <div id="list"></div>
  </div>
  <div id="panelO" hidden></div>
</div>
<script src="js/sync.js"></script>
<script>
var GROUPS = __DATA__;
var PLANNED = __PLANNED__;

function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

function readProgress(lab) {
  var done = 0, secs = 0;
  try {
    var saved = JSON.parse(localStorage.getItem(lab.storage) || '{}');
    var map = saved.done || {};
    done = lab.units.filter(function (k) { return map[k]; }).length;
    secs = saved.tTotal || 0;
  } catch (e) {}
  if (lab.completed) done = lab.units.length;      // пройдена целиком (список COMPLETED в tools/build-progress.py)
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

function sessBadge(lab) {
  if (lab.sessions >= lab.sessionsMin) return '<span class="sess-ok">' + lab.sessions + ' сессий · хватает</span>';
  return '<span class="sess-bad">' + lab.sessions + ' сессий · не хватает ' + (lab.sessionsMin - lab.sessions) + '</span>';
}
function fmtBadge(lab) {
  if (lab.format === 'standard') return '<span class="fmt-ok">формат: эталон</span>';
  if (lab.format === 'partial') return '<span class="fmt-partial">формат: частично</span>';
  return '<span class="fmt-bad">формат: переделать</span>';
}

function labRow(it, n, fold) {
  var lab = it.lab, p = it.p, pct = p.total ? Math.round(p.done / p.total * 100) : 0;
  return '<div class="lab' + (fold[lab.key] ? ' collapsed' : '') + '" data-key="' + lab.key + '" style="--c:' + lab.accent + '">'
    + '<button type="button" class="fold" title="Свернуть / развернуть" aria-label="Свернуть или развернуть"></button>'
    + '<span class="num">' + String(n).padStart(2, '0') + '</span>'
    + '<img class="thumb" src="' + esc(lab.thumb) + '" alt="" width="64" height="64" loading="lazy">'
    + '<a class="name" href="' + esc(lab.open) + '"><span class="dot"></span>' + esc(lab.title) + (lab.vstatus !== 'none' ? statusBadge(lab, true) : '') + '</a>'
    + '<span class="pct">' + pct + '% · ' + p.done + '/' + p.total + '</span>'
    + '<span class="meta">' + esc(it.dir) + ' · ' + esc(lab.subtitle) + ' · ' + esc(lab.difficulty)
    + (p.secs ? ' · ' + fmtTime(p.secs) : '') + '<br>'
    + (lab.vstatus !== 'none' ? statusBadge(lab, false) + (lab.vnote ? ' <span class="note">' + (lab.vstatus === 'full' ? '· * ' : '· не проверено: ') + esc(lab.vnote) + '</span>' : '') + '<br>' : '')
    + '<a href="' + esc(lab.open) + '">Методичка ↗</a><a href="' + esc(lab.page) + '">Страница лабы</a></span>'
    + '<div class="bar"><i style="width:' + pct + '%"></i></div>'
    + '<span class="stats">' + sessBadge(lab) + fmtBadge(lab) + '</span>'
    + '</div>';
}

function plannedRow(p) {
  return '<div class="lab planned" style="--c:' + p.accent + '"><span class="num"></span>'
    + '<span class="name"><span class="dot"></span>' + esc(p.title) + '<span class="new"><i>новая</i></span></span>'
    + '<span class="meta">' + esc(p.subtitle) + ' · ' + esc(p.difficulty) + ' · ' + esc(p.note) + '<br>'
    + '<a href="https://github.com/meeymirita/' + esc(p.repo) + '">Репозиторий ↗</a></span></div>';
}

function render() {
  var fold = folded();
  var allDone = 0, allTotal = 0, started = 0, finished = 0, secs = 0, html = '', items = [];
  GROUPS.forEach(function (g) {
    g.labs.forEach(function (lab) {
      var p = readProgress(lab);
      items.push({ lab: lab, p: p, dir: g.title });
      allDone += p.done; allTotal += p.total; secs += p.secs;
      if (p.done) started++; if (p.total && p.done === p.total) finished++;
    });
  });
  // порядок: сначала то, что в процессе, потом пройденное, потом ещё не начатое (внутри — как на главной)
  function stage(it) { return it.p.total && it.p.done === it.p.total ? 1 : it.p.done ? 0 : 2; }
  var n = 0;
  [[0, 'В процессе'], [1, 'Пройдено'], [2, 'Ещё не начато']].forEach(function (sec) {
    var part = items.filter(function (it) { return stage(it) === sec[0]; });
    if (!part.length) return;
    html += '<h2>' + sec[1] + ' · ' + part.length + '</h2>';
    part.forEach(function (it) { html += labRow(it, ++n, fold); });
  });
  if (PLANNED.length) {
    html += '<h2>Новые · ' + PLANNED.length + '</h2>';
    PLANNED.forEach(function (p) { html += plannedRow(p); });
  }
  document.getElementById('list').innerHTML = html;
  var all = allTotal ? Math.round(allDone / allTotal * 100) : 0;
  document.getElementById('total').innerHTML =
    '<div class="total-top"><span>Общий прогресс</span><span>' + all + '%</span></div>'
    + '<div class="bar"><i style="width:' + all + '%"></i></div>'
    + '<div class="total-note">отмечено ' + allDone + ' из ' + allTotal + ' разделов и шагов · начато лаб: ' + started + ' из ' + items.length
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
var ORDER = __ORDER__;
var KIND = { need: 'нужна', know: 'нужно знать', help: 'полезна' };
function hh(x) { return (Math.round(x * 10) / 10).toString().replace('.', ','); }
function renderOrder() {
  var tot = { labs: 0, sess: 0, steps: 0, hours: 0 }, run = 0, html = '', planned = [];
  ORDER.forEach(function (l) { if (!l.planned || l.key === 'ansible' || l.sessions.length) { } });
  var live = ORDER.filter(function (l) { return !l.planned; }), plan = ORDER.filter(function (l) { return l.planned; });
  live.forEach(function (l) { tot.labs++; tot.sess += l.sessions.length; tot.steps += l.steps; tot.hours += l.hours; });
  html += '<div class="ord-sum"><div class="row"><span><b>' + tot.labs + '</b> лаб на сайте</span><span><b>' + tot.sess + '</b> сессий</span><span><b>' + tot.steps + '</b> шагов</span><span><b>~' + Math.round(tot.hours) + '</b> часов по длительности сессий</span></div>'
    + '<div class="total-note">Порядок — рекомендуемый (источник: <code>works/js/prereq.js</code>, <code>fixes/common/_order.md</code>): сначала то, на чём стоят остальные. Часы считаются из длительности сессий в методичках; у лаб без прохождения это оценка автора, а не ваше время. Нажмите на строку, чтобы увидеть сессии и зависимости.</div></div>'
    + '<p class="ord-leg"><span class="chip need">нужна</span> без этой лабы шаги не выполнить · <span class="chip know">нужно знать</span> методичка опирается на её знания · <span class="chip help">полезна</span> можно и без неё</p>';
  function row(l, n, cum) {
    var b = '<details class="ord" style="--c:' + l.accent + '"><summary><span class="ono">' + (n ? String(n).padStart(2, '0') : '·') + '</span>'
      + '<span class="on"><i></i>' + esc(l.title) + '</span>'
      + '<span class="ot">' + (l.sessions.length ? l.sessions.length + ' сесс · ' + (l.steps ? l.steps + ' шаг · ' : '') + '~' + hh(l.hours) + ' ч' : 'в плане')
      + (cum != null ? '<small>с начала пути: ~' + Math.round(cum) + ' ч</small>' : '') + '</span>'
      + '<span class="om">' + esc(l.dir) + (l.level ? ' · вход: ' + esc(l.level) : '') + (l.difficulty ? ' · ' + esc(l.difficulty) : '') + (l.subtitle ? ' · ' + esc(l.subtitle) : '') + '</span></summary><div class="obody">';
    if (l.headline) b += '<p><b>' + esc(l.headline) + '</b></p>';
    if (l.note) b += '<p class="note">' + esc(l.note) + '</p>';
    if (l.before.length) { b += '<h3>Что пройти раньше</h3><p>' + l.before.map(function (x) { return '<span class="chip ' + x.kind + '">' + esc(KIND[x.kind] || x.kind) + ': ' + esc(x.title) + '</span> ' + esc(x.why); }).join('<br>') + '</p>'; }
    else b += '<h3>Что пройти раньше</h3><p>Ничего: лаба самостоятельная.</p>';
    if (l.know.length) b += '<h3>Что нужно знать</h3><ul>' + l.know.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>';
    if (l.meet.length) b += '<h3>С чем встретитесь</h3><p>' + l.meet.map(function (x) { return '<span class="chip">' + esc(x) + '</span>'; }).join('') + '</p>';
    if (l.sessions.length) b += '<h3>Сессии</h3><table><tr><th>№</th><th>Тема</th><th>Время</th>' + (l.steps ? '<th>Шагов</th>' : '') + '</tr>'
      + l.sessions.map(function (s) { return '<tr><td>' + s.n + '</td><td>' + esc(s.t) + '</td><td class="h">' + esc(s.h) + '</td>' + (l.steps ? '<td>' + s.steps + '</td>' : '') + '</tr>'; }).join('') + '</table>';
    if (l.refs.length) b += '<h3>Справочные разделы</h3><p>' + l.refs.map(function (x) { return '<span class="chip">' + esc(x) + '</span>'; }).join('') + '</p>';
    if (l.tip) b += '<h3>Заметка</h3><p>' + esc(l.tip) + '</p>';
    b += '<p class="lk">' + (l.open ? '<a href="' + esc(l.open) + '">Методичка ↗</a><a href="' + esc(l.page) + '">Страница лабы</a>' : '') + '</p></div></details>';
    return b;
  }
  html += '<div class="ord-h">Путь · ' + live.length + ' лаб</div>';
  live.forEach(function (l, i) { run += l.hours; html += row(l, i + 1, run); });
  if (plan.length) { html += '<div class="ord-h">В плане, на сайте нет · ' + plan.length + '</div>'; plan.forEach(function (l) { html += row(l, 0, null); }); }
  document.getElementById('panelO').innerHTML = html;
}
function showTab(o) {
  document.getElementById('panelP').hidden = o; document.getElementById('panelO').hidden = !o;
  document.getElementById('tabP').setAttribute('aria-selected', o ? 'false' : 'true'); document.getElementById('tabO').setAttribute('aria-selected', o ? 'true' : 'false');
  if (o && !document.getElementById('panelO').innerHTML) renderOrder();
  if (history.replaceState) history.replaceState(null, '', o ? '#order' : location.pathname);
}
document.getElementById('tabP').onclick = function () { showTab(false); };
document.getElementById('tabO').onclick = function () { showTab(true); };
if (location.hash === '#order') showTab(true);
</script>
</body>
</html>
'''

out = TEMPLATE.replace('__ORDER__', json.dumps(ORDERDATA, ensure_ascii=False, separators=(',', ':'))).replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':'))).replace('__PLANNED__', json.dumps(PLANNED, ensure_ascii=False, separators=(',', ':')))
open('works/progress.html', 'w', encoding='utf-8').write(out)
print(f'works/progress.html: {sum(len(g["labs"]) for g in data)} лаб, {len(out) // 1024} КБ')
