#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEO-теги в <head>: title, description, canonical, Open Graph, Twitter, JSON-LD.
works/<ключ>.html — из LABS (works/js/lab.js); index.html — общий блок. Идемпотентно (блок между маркерами seo:start/seo:end).
Запуск: python3 tools/build-seo.py   (после новой лабы или смены desc/subtitle/image в lab.js)"""
import json, os, re, subprocess, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
BASE = 'https://anitech.meeymirita.ru'
src = open('works/js/lab.js', encoding='utf-8').read()
arr = src[src.index('var LABS = ['):]
arr = arr[:arr.index('\n];') + 3]
js = arr + '\nprocess.stdout.write(JSON.stringify(LABS.map(l=>({key:l.key,title:l.title,subtitle:l.subtitle,desc:l.desc,image:l.image,difficulty:l.difficulty}))))'
labs = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)
E = lambda s: html.escape(s, quote=True)

def short(s, n=200):
    s = s.strip()
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0].rstrip(',;:') + '…'

def block(url, title, desc, image, ld):
    return ('<!-- seo:start -->\n'
        f'<link rel="canonical" href="{url}">\n'
        '<meta property="og:type" content="website">\n<meta property="og:site_name" content="ANITECH PERFORMANCE">\n<meta property="og:locale" content="ru_RU">\n'
        f'<meta property="og:title" content="{E(title)}">\n<meta property="og:description" content="{E(desc)}">\n<meta property="og:url" content="{url}">\n'
        + (f'<meta property="og:image" content="{image}">\n' if image else '')
        + f'<meta name="twitter:card" content="{"summary_large_image" if image else "summary"}">\n<meta name="twitter:title" content="{E(title)}">\n<meta name="twitter:description" content="{E(desc)}">\n'
        + (f'<meta name="twitter:image" content="{image}">\n' if image else '')
        + '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>\n<!-- seo:end -->\n')

def apply(path, title, desc, blk):
    t = open(path, encoding='utf-8').read()
    t = re.sub(r'<!-- seo:start -->.*?<!-- seo:end -->\n?', '', t, flags=re.S)
    t = re.sub(r'<title>.*?</title>', lambda m: f'<title>{E(title)}</title>', t, count=1, flags=re.S)
    d = f'<meta name="description" content="{E(desc)}">'
    if re.search(r'<meta name="description"[^>]*>', t): t = re.sub(r'<meta name="description"[^>]*>', lambda m: d, t, count=1)
    else: t = t.replace('</title>', '</title>\n' + d, 1)
    t = re.sub(r'(<meta name="description"[^>]*>\n?)', lambda m: m.group(1).rstrip('\n') + '\n' + blk, t, count=1)
    open(path, 'w', encoding='utf-8').write(t)

author = {'@type': 'Person', 'name': 'meeymirita', 'url': 'https://github.com/meeymirita'}
n = 0
for l in labs:
    p = f'works/{l["key"]}.html'
    if not os.path.exists(p): continue
    url = f'{BASE}/works/{l["key"]}.html'
    title = f'{l["title"]} — {l["subtitle"]} · ANITECH'
    desc = short(l['desc'])
    ld = {'@context': 'https://schema.org', '@type': 'Course', 'name': l['title'], 'description': desc, 'url': url,
          'inLanguage': 'ru', 'educationalLevel': l.get('difficulty') or '', 'author': author,
          'provider': {'@type': 'Organization', 'name': 'ANITECH PERFORMANCE', 'url': BASE + '/'}}
    apply(p, title, desc, block(url, title, desc, l['image'], ld)); n += 1
# главная
t = open('index.html', encoding='utf-8').read()
m = re.search(r'<meta name="description" content="([^"]*)"', t)
idesc = html.unescape(m.group(1))
ititle = 'ANITECH PERFORMANCE — лабораторные работы'
ld = {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'ANITECH PERFORMANCE', 'url': BASE + '/', 'inLanguage': 'ru', 'author': author}
apply('index.html', ititle, idesc, block(BASE + '/', ititle, short(idesc, 300), f'{BASE.replace("anitech.meeymirita.ru","anitech.meeymirita.ru")}/images/hero.jpg' if os.path.exists('images/hero.jpg') else '', ld))
print(f'SEO-теги: {n} страниц лаб + index.html')
