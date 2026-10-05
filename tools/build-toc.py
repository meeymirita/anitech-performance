#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает works/js/toc.json — оглавления всех методичек для окна «Оглавление» на страницах works/<лаба>.html.

Раньше окно скачивало методичку из бакета и разбирало её в браузере — это падало везде, кроме боевого домена
(CORS бакета), и на медленной сети. Теперь данные лежат рядом со страницей. Логика — та же, что tocItemsFromLab в lab.js.
Запуск из корня:  python3 tools/build-toc.py   (идемпотентен; check-site.py ловит устаревший файл)
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'fixes/common/_tools')
import bundle


def items_for(lab):
    units = lab.get('units') or []
    steps = [u for u in units if u.get('kind') == 'step']
    items = [{'id': u['key'], 'title': (u['num'] + '. ' if u.get('num') else '') + u['title'], 'subs': []}
             for u in units if u.get('kind') != 'step']
    strip = lambda t: re.sub(r'^🔨\s*', '', t)
    subs = [s['num'] + ' ' + strip(s['title']) for s in steps]
    host = next((i for i in items if re.search(r'пошагов|задани|сесси', i['title'], re.I)), None)
    if host:
        host['subs'] = subs
    elif steps:
        items.append({'id': steps[0]['key'], 'title': 'Шаги по сессиям', 'subs': subs})
    return items


def build():
    out = {}
    for k in sorted(d for d in os.listdir('.') if os.path.isfile(f'{d}/{d}.html')):
        txt = bundle.load(f'{k}/{k}.html')[len('window.LAB='):]
        lab, _ = json.JSONDecoder().raw_decode(txt)
        out[k] = items_for(lab)
    return json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n'


if __name__ == '__main__':
    data = build()
    path = 'works/js/toc.json'
    if '--check' in sys.argv:
        sys.exit(0 if os.path.exists(path) and open(path, encoding='utf-8').read() == data else 1)
    open(path, 'w', encoding='utf-8').write(data)
    print(f'{path}: {len(json.loads(data))} лаб, {len(data) // 1024} КБ')
