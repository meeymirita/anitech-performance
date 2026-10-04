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

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
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
<script>if(location.protocol==='http:'&&location.hostname==='anitech.meeymirita.ru')location.replace('https://'+location.host+location.pathname+location.search+location.hash);</script>
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
.tw {{ overflow-x:auto; margin:10px 0; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; background:var(--card); }}
th,td {{ text-align:left; vertical-align:top; padding:7px 10px; border:1px solid var(--hair); }}
th {{ font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }}
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
