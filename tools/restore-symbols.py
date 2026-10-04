#!/usr/bin/env python3
"""Возвращает в методички символы (✅ ❌ ✓ ✕ ☰ ♥ …), потерянные при редизайне 02.10.2026.

В старой (до редизайна) HTML-версии методички такие символы были, в «бандле» их нет: из кода пропали маркеры
«❌ сначала так / ✅ порядок слоёв…», галочки списков, значок меню. Скрипт берёт последнюю версию файла из git
без бандла, находит каждый символ диапазона U+2600–U+27BF вместе с контекстом и вставляет его обратно в нынешний
текст методички там, где контекст совпал однозначно. Идемпотентен.

Запуск из корня:  python3 tools/restore-symbols.py [--dry] [лаба ...]   (по умолчанию все лабы со старой версией)
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'fixes', 'common', '_tools'))
import bundle

SYM = re.compile(r'[☀-➿]')
dry = '--dry' in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith('--')]

js = open('works/js/lab.js', encoding='utf-8').read()
opens = re.findall(r"key: '([\w-]+)',[\s\S]*?open: '\.\./([^']+)'", js)

def git(*a, cwd='.'):
    return subprocess.run(['git', '-C', cwd, *a], capture_output=True, text=True)

def old_version(path):
    folder, rel = path.split('/', 1)
    log = git('log', '--format=%h', '--', rel, cwd=folder).stdout.split()
    for c in log:
        t = git('show', f'{c}:{rel}', cwd=folder).stdout
        if t and '__bundler/manifest' not in t and SYM.search(t):
            return c, t
    return None, None

def contexts(old):
    out = []
    for m in SYM.finditer(old):
        i = m.start()
        strip = lambda x: re.sub(r'<[^>]+>', '', x)          # теги в старой и новой вёрстке разные — сверяем только текст
        left, right = strip(old[max(0, i - 160):i]), strip(old[i + 1:i + 161])
        out.append((m.group(0), left, right))
    return out

def walk(o, fn):
    if isinstance(o, str): return fn(o)
    if isinstance(o, list): return [walk(x, fn) for x in o]
    if isinstance(o, dict): return {k: walk(v, fn) for k, v in o.items()}
    return o

def restore(L, ctxs):
    stats = {'вставлено': 0, 'уже есть': 0, 'не найдено': []}
    for sym, left, right in ctxs:
        spl = left[-1:].isspace(); spr = right[:1].isspace()
        placed = False; last_note = None
        for n in (14, 9, 6):                               # от длинного контекста к короткому (теги в новой вёрстке мешают длинному)
            lt = re.sub(r'\s+', ' ', left)[-n:]; rh = re.sub(r'\s+', ' ', right)[:n]
            lt_s, rh_s = lt.rstrip(), rh.lstrip()
            if len(lt_s) < 3 or len(rh_s) < 3:
                last_note = f'контекст слишком короткий: {lt}|{rh}'; continue
            rx_new = re.compile(re.escape(lt_s) + r'(?: )?' + re.escape(rh_s))
            rx_have = re.compile(re.escape(lt_s) + r'\s?' + re.escape(sym) + r'\s?' + re.escape(rh_s))
            hits = []; have = []
            def scan(x):
                hits.extend(rx_new.findall(x)); have.extend(rx_have.findall(x)); return x
            walk(L, scan)
            if have and not hits:
                stats['уже есть'] += 1; placed = True; break
            if not hits:
                last_note = f'нет совпадений: {lt}|{rh}'; continue
            if len(hits) > 6:
                last_note = f'слишком много совпадений ({len(hits)}): {lt}|{rh}'; continue
            rep = lt_s + (' ' if spl else '') + sym + (' ' if spr else '') + rh_s
            L = walk(L, lambda x, rx=rx_new, rep=rep: rx.sub(lambda m: rep, x))
            stats['вставлено'] += 1; placed = True
            if '--verbose' in sys.argv: print('      +', rep.replace('\n', ' '))
            break
        if not placed:
            stats['не найдено'].append((sym, last_note or 'нет контекста'))
    return L, stats

total = {}
for key, path in opens:
    if only and key not in only: continue
    folder = path.split('/')[0]
    commit, old = old_version(path)
    if not old:
        print(f'{key:22s} нет старой версии — пропуск'); continue
    txt = bundle.load(path)
    head = 'window.LAB='
    L, end = json.JSONDecoder().raw_decode(txt[len(head):])
    tail = txt[len(head) + end:]
    ctxs = contexts(old)
    # символы, которые уже на месте в нынешней версии (вставленные раньше) не дублируем — restore() сам это проверяет
    L2, st = restore(L, ctxs)
    print(f'{key:22s} старая версия {commit}: символов {len(ctxs):3d} → вставлено {st["вставлено"]:3d}, уже есть {st["уже есть"]:3d}, не найдено {len(st["не найдено"]):3d}')
    for sym, c in st['не найдено'][:40]:
        print('      ?', sym, c.replace('\n', ' ')[:80])
    if st['вставлено'] and not dry:
        new = head + json.dumps(L2, ensure_ascii=False, separators=(',', ':')) + tail
        bundle.transform(path, lambda t, new=new: new)
print('готово' + (' (dry-run, ничего не записано)' if dry else ''))
