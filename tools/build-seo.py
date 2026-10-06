#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEO-теги в <head>: title, description, canonical, Open Graph, Twitter, JSON-LD.
works/<ключ>.html — из LABS (works/js/lab.js); index.html — общий блок. Идемпотентно (блок между маркерами seo:start/seo:end).
Запуск: python3 tools/build-seo.py   (после новой лабы или смены desc/subtitle/image в lab.js)"""
import glob, json, os, re, subprocess, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
BASE = 'https://anitech.meeymirita.ru'
src = open('works/js/lab.js', encoding='utf-8').read()
arr = src[src.index('var LABS = ['):]
arr = arr[:arr.index('\n];') + 3]
js = arr + '\nprocess.stdout.write(JSON.stringify(LABS.map(l=>({key:l.key,title:l.title,subtitle:l.subtitle,desc:l.desc,image:l.image,difficulty:l.difficulty,stack:l.stack||[],repo:l.repo,learn:(l.learn||[]).map(x=>({tab:x.tab,title:x.title,text:x.text,points:x.points||[]}))}))))'
labs = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)
E = lambda s: html.escape(s, quote=True)

def short(s, n=200):
    s = s.strip()
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0].rstrip(',;:') + '…'

def block(url, title, desc, image, ld, extra=''):
    return ('<!-- seo:start -->\n'
        f'<link rel="canonical" href="{url}">\n'
        '<meta property="og:type" content="website">\n<meta property="og:site_name" content="ANITECH PERFORMANCE">\n<meta property="og:locale" content="ru_RU">\n'
        f'<meta property="og:title" content="{E(title)}">\n<meta property="og:description" content="{E(desc)}">\n<meta property="og:url" content="{url}">\n'
        + (f'<meta property="og:image" content="{image}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="1200">\n<meta property="og:image:alt" content="{E(title)}">\n' if image else '')
        + f'<meta name="twitter:card" content="{"summary_large_image" if image else "summary"}">\n<meta name="twitter:title" content="{E(title)}">\n<meta name="twitter:description" content="{E(desc)}">\n'
        + (f'<meta name="twitter:image" content="{image}">\n' if image else '')
        + ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>\n' for x in (ld if isinstance(ld, list) else [ld])) + extra + '<!-- seo:end -->\n')

def apply(path, title, desc, blk, static=None):
    t = open(path, encoding='utf-8').read()
    t = re.sub(r'<!-- seo:start -->.*?<!-- seo:end -->\n?', '', t, flags=re.S)
    t = re.sub(r'<title>.*?</title>', lambda m: f'<title>{E(title)}</title>', t, count=1, flags=re.S)
    d = f'<meta name="description" content="{E(desc)}">'
    if re.search(r'<meta name="description"[^>]*>', t): t = re.sub(r'<meta name="description"[^>]*>', lambda m: d, t, count=1)
    else: t = t.replace('</title>', '</title>\n' + d, 1)
    t = re.sub(r'(<meta name="description"[^>]*>\n?)', lambda m: m.group(1).rstrip('\n') + '\n' + blk, t, count=1)
    t = re.sub(r'<!-- seo-static:start -->.*?<!-- seo-static:end -->', '', t, flags=re.S)
    if static: t = t.replace('<div id="lab-root"></div>', '<div id="lab-root"><!-- seo-static:start -->' + static + '<!-- seo-static:end --></div>', 1)
    open(path, 'w', encoding='utf-8').write(t)

author = {'@type': 'Person', 'name': 'meeymirita', 'url': 'https://github.com/meeymirita'}
BUCKET = 'https://meeymirita-files.storage.yandexcloud.net'
toc = json.load(open('works/js/toc.json', encoding='utf-8')) if os.path.exists('works/js/toc.json') else {}
crumbs = lambda items: {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
    {'@type': 'ListItem', 'position': i + 1, 'name': n_, 'item': u_} for i, (n_, u_) in enumerate(items)]}

def static_html(l, prev, nxt):
    h = [f'<main class="seo-static"><nav aria-label="Навигация"><a href="/">ANITECH PERFORMANCE</a> › <a href="/#projects">Лабораторные</a></nav>',
         f'<h1>{E(l["title"])}</h1><p>{E(l["subtitle"])}</p><p>{E(l["desc"])}</p>']
    if l['stack']: h.append('<p>Стек: ' + E(', '.join(l['stack'])) + '. Уровень: ' + E(l.get('difficulty') or '—') + '.</p>')
    for x in l['learn']:
        h.append(f'<section><h2>{E(x["title"])}</h2><p>{E(x["text"])}</p>' + ('<ul>' + ''.join(f'<li>{E(q)}</li>' for q in x['points']) + '</ul>' if x['points'] else '') + '</section>')
    heads = toc.get(l['key'], [])
    if heads:
        h.append('<section><h2>Содержание методички</h2><ol>' + ''.join(f'<li>{E(s["title"])}</li>' for s in heads) + '</ol></section>')
    h.append(f'<p><a href="{E(l["repo"])}">Репозиторий лабы на GitHub</a></p>' if l.get('repo') else '')
    h.append(f'<p><a href="{prev["key"]}.html">← {E(prev["title"])}</a> · <a href="{nxt["key"]}.html">{E(nxt["title"])} →</a></p></main>')
    return ''.join(h)

n = 0
for i, l in enumerate(labs):
    p = f'works/{l["key"]}.html'
    if not os.path.exists(p): continue
    url = f'{BASE}/works/{l["key"]}.html'
    title = f'{l["title"]} — {l["subtitle"]} · ANITECH'
    desc = short(l['desc'])
    img = f'{BUCKET}/{l["key"]}/og.jpg'
    ld = [{'@context': 'https://schema.org', '@type': 'Course', 'name': l['title'], 'description': desc, 'url': url,
           'inLanguage': 'ru', 'educationalLevel': l.get('difficulty') or '', 'author': author, 'image': img,
           'provider': {'@type': 'Organization', 'name': 'ANITECH PERFORMANCE', 'url': BASE + '/'}},
          crumbs([('ANITECH PERFORMANCE', BASE + '/'), (l['title'], url)])]
    apply(p, title, desc, block(url, title, desc, img, ld), static_html(l, labs[i - 1], labs[(i + 1) % len(labs)])); n += 1

# главная
t = open('index.html', encoding='utf-8').read()
m = re.search(r'<meta name="description" content="([^"]*)"', t)
idesc = html.unescape(m.group(1))
ititle = 'ANITECH PERFORMANCE — лабораторные работы'
ld = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'ANITECH PERFORMANCE', 'url': BASE + '/', 'inLanguage': 'ru', 'author': author}
apply('index.html', ititle, idesc, block(BASE + '/', ititle, short(idesc, 300), BASE + '/images/hero.jpg' if os.path.exists('images/hero.jpg') else '', ld))

# служебные страницы витрины
SERVICE = {
 'changelog': ('Хронология проекта — ANITECH PERFORMANCE', None, True),
 'verification': ('Что чем проверено — ANITECH PERFORMANCE', 'Таблица проверок: какие лабы вычитаны построчно и проверены запуском в Docker и браузере, что проверить не удалось и почему.', True),
 'progress': ('Мой прогресс — ANITECH PERFORMANCE', 'Личная страница прогресса прохождения лабораторных.', False),   # личная: noindex
}
for k, (ttl, dsc, index) in SERVICE.items():
    p = f'works/{k}.html'
    if not os.path.exists(p): continue
    tt = open(p, encoding='utf-8').read()
    cur = re.search(r'<meta name="description" content="([^"]*)"', tt)
    d = dsc or (html.unescape(cur.group(1)) if cur else ttl)
    url = f'{BASE}/works/{k}.html'
    blk = block(url, ttl, short(d, 300), '', {'@context': 'https://schema.org', '@type': 'WebPage', 'name': ttl, 'url': url, 'inLanguage': 'ru'},
                extra='' if index else '<meta name="robots" content="noindex, nofollow">\n')
    apply(p, ttl, d, blk)

# личные страницы — noindex (mira — уже, форма входа — тоже)
for p in ('site-private/mira-login/index.html',):
    if os.path.exists(p):
        tt = open(p, encoding='utf-8').read()
        if 'name="robots"' not in tt:
            tt = tt.replace('<head>', '<head>\n<meta name="robots" content="noindex, nofollow">', 1)
            open(p, 'w', encoding='utf-8').write(tt)
print(f'SEO-теги: {n} страниц лаб + index.html + служебные')
