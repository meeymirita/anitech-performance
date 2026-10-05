#!/usr/bin/env python3
"""Собирает works/verification.html из fixes/common/_verification.md (страница «что чем проверено»).

Запуск из корня:  python3 tools/build-verification.py
ПРАВИЛО: оба файла — одно целое. Правишь _verification.md → запусти этот скрипт (html пересоберётся).
Правишь works/verification.html руками → внеси то же в _verification.md (источник правды — .md).
В html зашит хеш .md; tools/check-site.py падает, если они разошлись.
"""
import hashlib, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'fixes', 'common', '_verification.md')
OUT = os.path.join(ROOT, 'works', 'verification.html')

FIXES_URL = 'https://github.com/meeymirita/lab-fixes/blob/main/'

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    # [текст](https://…) — обычная ссылка
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    # `fixes/<направление>/<файл>.md` — ссылка на файл подробностей в репозитории lab-fixes
    s = re.sub(r'<code>fixes/((?:backend|devops|frontend|common)/[\w.-]+\.md)</code>',
               lambda m: f'<a href="{FIXES_URL}{m.group(1)}" target="_blank" rel="noopener"><code>fixes/{m.group(1)}</code></a>', s)
    return s

def cell(s):
    s = inline(s.strip())
    cls = {'✅': 'ok', '🟡': 'part', '⚠️': 'warn', '📖': 'txt', '⬜': 'todo', '🔄': 'part'}
    for k, v in cls.items():
        if s.startswith(k) or s == k:
            return f'<td class="{v}">{s}</td>'
    return f'<td>{s}</td>'

def convert(md):
    out, lines, i = [], md.split('\n'), 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c for c in lines[i].strip().strip('|').split('|')]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = '<div class="tw"><table><thead><tr>' + ''.join(f'<th>{inline(c.strip())}</th>' for c in head) + '</tr></thead><tbody>'
            for r in body:
                t += '<tr>' + ''.join(cell(c) for c in r) + '</tr>'
            out.append(t + '</tbody></table></div>'); continue
        m = re.match(r'(#{1,3}) (.*)', l)
        if m:
            n = len(m.group(1)); out.append(f'<h{n}>{inline(m.group(2))}</h{n}>')
        elif l.strip() == '---':
            out.append('<hr>')
        elif l.strip():
            out.append(f'<p>{inline(l)}</p>')
        i += 1
    return '\n'.join(out)

md = open(SRC, encoding='utf-8').read()
h = hashlib.sha256(md.encode()).hexdigest()[:16]
page = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Что чем проверено — ANITECH</title>
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<!-- АВТОГЕНЕРАЦИЯ из fixes/common/_verification.md (tools/build-verification.py). Менять .md и пересобирать; правка здесь — внести и в .md. -->
<!-- verification-md-hash: {h} -->
<style>
:root {{ --bg:#faf9f5; --ink:#17140f; --muted:#5d584f; --hair:#d9d4c8; --card:#fff; --accent:#ec3013; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#12110f; --ink:#f1ede4; --muted:#a39d90; --hair:#2f2c26; --card:#1a1815; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:28px 16px 64px; }}
.back {{ font-size:14px; color:var(--muted); text-decoration:none; }} .back:hover {{ color:var(--ink); }}
h1 {{ margin:12px 0 8px; font-size:clamp(26px,4.5vw,40px); letter-spacing:-.02em; line-height:1.1; }}
h2 {{ margin:36px 0 8px; font-size:20px; }} h3 {{ margin:24px 0 6px; font-size:16px; }}
p {{ margin:6px 0; color:var(--muted); }}
code {{ font:13px ui-monospace,Menlo,monospace; background:var(--card); border:1px solid var(--hair); padding:0 4px; }}
hr {{ border:0; border-top:1px solid var(--hair); margin:32px 0; }}
.tw {{ overflow-x:auto; margin:10px 0; max-width:100%; }}
html,body {{ overflow-x:hidden; }}  /* широкие таблицы листаются внутри .tw, страница целиком не уезжает (телефон) */
table {{ border-collapse:collapse; width:100%; font-size:14px; background:var(--card); }}
th,td {{ text-align:left; vertical-align:top; padding:7px 10px; border:1px solid var(--hair); }}
th {{ font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }}
a {{ color:var(--accent); }} a code {{ color:inherit; }}
td.ok {{ background:rgba(40,160,80,.12); }} td.part {{ background:rgba(230,170,0,.16); }}
td.warn {{ background:rgba(236,48,19,.12); }} td.todo {{ background:rgba(128,128,128,.12); }}
</style>
</head>
<body><div class="wrap">
<a class="back" href="progress.html">← Все работы и прогресс</a>
{convert(md)}
</div></body></html>
'''
open(OUT, 'w', encoding='utf-8').write(page)
print('works/verification.html собран, hash', h)

# ── works/js/status.js: статус каждой лабы для карточки на главной и страницы лабы (единый источник — таблица «По лабам») ──
KEYS = {'Algorithms PHP': 'algorithms-php', 'Laravel Performance': 'laravel-performance', 'CSS': 'css', 'Tailwind': 'tailwind',
        'Inertia': 'inertia', 'Kubernetes': 'kubernetes', 'Docker': 'docker', 'Traefik': 'traefik', 'Caddy': 'caddy',
        'ООП (php-coffee)': 'php-coffee', 'Чистый PHP': 'php', 'PostgreSQL': 'postgresql', 'Redis': 'redis', 'RabbitMQ': 'rabbitmq',
        'Laravel': 'laravel', 'NestJS': 'nestjs', 'GraphQL': 'graphql', 'JS': 'js', 'TypeScript': 'typescript', 'Vue': 'vue',
        'Nuxt': 'nuxt', 'Angular': 'angular'}
import json
status = {}
sec = md.split('## По лабам', 1)[1].split('\n## ', 1)[0]
for line in sec.split('\n'):
    if not line.startswith('|') or line.startswith('|---') or line.startswith('| Лаба'):
        continue
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) < 6 or c[0] not in KEYS:
        continue
    name, level, method, _done, todo, detail = c[:6]
    partial = level.startswith('🟡')
    rest, own = '', False
    if todo.strip() not in ('—', ''):
        t = todo.strip()
        m = re.match(r'^—\s*\((.*)\)\s*$', t)       # «— (…)»: проверено, остаётся только то, что делает сам пользователь
        t = m.group(1) if m else t
        own = bool(re.search(r'сами\b', t))                # «проверите сами» / «решаете сами» — остаётся пользователю
        t = re.sub(r'\s*[—-]\s*(проверите|решаете|проверит)\s+сами\s*$', '', t)
        t = re.sub(r'^нужны внешние ресурсы:\s*', '', t)
        rest = t.replace('`', '')
    d = re.search(r'fixes/((?:backend|devops|frontend|common)/[\w.-]+\.md)', detail)
    status[KEYS[name]] = {'level': 'part' if partial else 'ok',
                          'head': 'Вычитана, проверена частично' if partial else 'Вычитана и проверена',
                          'tail': 'не проверено' if partial else ('вам остаётся проверить самим' if own else 'не запускалось'),
                          'method': [m for m, k in (('запуск в Docker', 'D'), ('проверка в браузере', 'B')) if k in method.split('+')],
                          'rest': rest, 'detail': FIXES_URL + d.group(1) if d else ''}
missing = sorted(set(KEYS.values()) - set(status))
assert not missing, f'нет строк в таблице «По лабам»: {missing}'
js = ('/* АВТОГЕНЕРАЦИЯ из fixes/common/_verification.md (tools/build-verification.py) — руками не править. */\n'
      f'/* verification-md-hash: {h} */\n'
      'window.LAB_STATUS = ' + json.dumps(status, ensure_ascii=False, indent=1) + ';\n')
open(os.path.join(ROOT, 'works', 'js', 'status.js'), 'w', encoding='utf-8').write(js)
print('works/js/status.js собран:', len(status), 'лаб')
