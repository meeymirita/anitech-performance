#!/usr/bin/env python3
"""Правит шаблон страницы у всех методичек-бандлов (идемпотентно, можно запускать повторно):

1. x-dc{display:none!important} сразу после <head> — без этого при запуске секунду виден «сырой» шаблон
   (в том числе оверлей поиска), пока загружаются скрипты;
2. рядом с «Поиск / Тёмная тема» — кнопка «Все работы» на works/progress.html (на главной странице методички, в боковой панели и в шапке; путь считается от глубины файла); старая ссылка внизу страницы удаляется.

3. переход по якорю: ссылки оглавления на странице лабы ведут на методичка.html#sec-3 / #step-2-1 — при загрузке и при смене
   хэша методичка открывает этот раздел (раньше URL менялся, а страница оставалась на месте).

Запуск из корня репозитория:  python3 tools/patch-manuals.py
Запускать после добавления лабы или перевыгрузки методички из дизайн-исходников.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

js = open('works/js/lab.js', encoding='utf-8').read()
paths = sorted(set(re.findall(r"open: '\.\./([^']+)'", js)))

STYLE = '<style>x-dc{display:none!important}<\\u002Fstyle>'
MARK = 'data-all-labs-nav'
OLD_MARK = 'data-all-labs-link'     # прежняя ссылка внизу страницы — убираем

def href_for(p):
    return '../' * p.count('/') + 'works/progress.html'

def btn_home(h):
    return ('<a ' + MARK + '=\\"1\\" href=\\"' + h + '\\" title=\\"Все работы и общий прогресс\\" style=\\"display:flex;gap:8px;align-items:center;padding:10px 14px;'
            'border:2px solid var(--ink);background:transparent;color:var(--ink);font:800 14px var(--font-body);cursor:pointer;text-decoration:none\\" '
            'style-hover=\\"background:var(--fill)\\">Все работы<\\u002Fa>\\n')

def btn_rail(h):
    return ('<a ' + MARK + '=\\"1\\" href=\\"' + h + '\\" title=\\"Все работы и общий прогресс\\" style=\\"width:40px;height:36px;border:1.5px solid var(--hair);'
            'background:transparent;color:var(--ink);cursor:pointer;display:grid;place-items:center;text-decoration:none\\" style-hover=\\"border-color:var(--ink)\\">'
            '<svg width=\\"17\\" height=\\"17\\" sc-camel-view-box=\\"0 0 24 24\\" fill=\\"none\\" stroke=\\"currentColor\\" stroke-width=\\"2\\">'
            '<rect x=\\"3\\" y=\\"3\\" width=\\"7\\" height=\\"7\\"><\\u002Frect><rect x=\\"14\\" y=\\"3\\" width=\\"7\\" height=\\"7\\"><\\u002Frect>'
            '<rect x=\\"3\\" y=\\"14\\" width=\\"7\\" height=\\"7\\"><\\u002Frect><rect x=\\"14\\" y=\\"14\\" width=\\"7\\" height=\\"7\\"><\\u002Frect><\\u002Fsvg><\\u002Fa>\\n')

def btn_head(h):
    return ('<a ' + MARK + '=\\"1\\" href=\\"' + h + '\\" title=\\"Все работы и общий прогресс\\" style=\\"display:flex;align-items:center;padding:8px 12px;'
            'border:1.5px solid var(--hair);background:transparent;color:var(--muted);font:400 14px var(--font-body);cursor:pointer;text-decoration:none\\" '
            'style-hover=\\"border-color:var(--ink)\\">Все работы<\\u002Fa>\\n')

HOME_ANCHOR = re.compile(r'(\{\{ themeLabel \}\}<\\u002Fbutton>\\n)')
RAIL_ANCHOR = re.compile(r'(title=\\"Тема\\".*?<\\u002Fbutton>\\n)(<\\u002Fdiv>\\n<\\u002Fnav>)', re.S)
HEAD_ANCHOR = '<button sc-camel-on-click=\\"{{ openSearch }}\\" style=\\"display:flex;gap:8px;align-items:center;padding:8px 12px;border:1.5px solid var(--hair)'
OLD_LINK = re.compile(r'<a ' + OLD_MARK + r'=\\"1\\".*?<\\u002Fa>\\n', re.S)

changed = 0
for p in paths:
    s = open(p, encoding='utf-8').read()
    m = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', s, re.S)
    if not m:
        print('нет шаблона:', p); continue
    raw = m.group(2)
    new = raw
    if 'x-dc{display:none' not in new:
        assert '<head>' in new, p
        new = new.replace('<head>', '<head>' + STYLE, 1)
    if 'goHash' not in new:
        pairs = [
            ("this.setState({ ready: true, ...keep });", "this.setState({ ready: true, ...keep }, () => this.goHash());"),
            ("window.addEventListener('keydown', this.onKey);", "window.addEventListener('keydown', this.onKey);\\n    this.onHash = () => this.goHash();\\n    window.addEventListener('hashchange', this.onHash);"),
            ("window.removeEventListener('keydown', this.onKey);", "window.removeEventListener('keydown', this.onKey); window.removeEventListener('hashchange', this.onHash);"),
            ("  scrollToId(id) {", "  goHash() {\\n    const h = decodeURIComponent((window.location.hash || '').slice(1));\\n    if (h && this.U && this.U[h]) this.go('u:' + h);\\n  }\\n  scrollToId(id) {"),
        ]
        for old, repl in pairs:
            assert new.count(old) == 1, (p, old)
            new = new.replace(old, repl)
    new = OLD_LINK.sub('', new)                      # убрать старую ссылку внизу
    h = href_for(p)
    if MARK in new:                                  # обновить путь у уже вставленных кнопок
        new = re.sub(r'(' + MARK + r'=\\"1\\" href=\\")[^"\\]+', lambda mm: mm.group(1) + h, new)
    else:
        m1 = HOME_ANCHOR.search(new); m2 = RAIL_ANCHOR.search(new); i3 = new.find(HEAD_ANCHOR)
        if not (m1 and m2 and i3 != -1):
            print('не нашёл места для кнопок:', p, bool(m1), bool(m2), i3 != -1); continue
        # вставляем с конца к началу, чтобы не сбивались индексы
        new = new[:i3] + btn_head(h) + new[i3:]
        new = new[:m2.end(1)] + btn_rail(h) + new[m2.end(1):]
        new = new[:m1.end(1)] + btn_home(h) + new[m1.end(1):]
    if new != raw:
        json.loads(new)   # остаётся валидной JSON-строкой (страница читает шаблон так)
        open(p, 'w', encoding='utf-8').write(s[:m.start(2)] + new + s[m.end(2):])
        changed += 1
        print('исправлено:', p)
print(f'всего методичек: {len(paths)}, изменено: {changed}')
