#!/usr/bin/env python3
"""Проверка целостности сайта: ключи лаб во всех реестрах, счётчики, ссылки, синтаксис JS.

Запуск из корня репозитория:  python3 tools/check-site.py
Код выхода 1, если нашлись проблемы. Ничего не меняет.
"""
import glob, os, re, subprocess, sys

problems, notes = [], []
def bad(msg): problems.append(msg)
def read(p): return open(p, encoding='utf-8').read()

# эталон: страницы works/<key>.html
keys = sorted(os.path.basename(p)[:-5] for p in glob.glob('works/*.html') if os.path.basename(p) not in ('changelog.html', 'progress.html', 'verification.html'))
N = len(keys)
notes.append(f'лаб (works/*.html): {N}')

idx, lab_js, anim_js = read('index.html'), read('works/js/lab.js'), read('works/js/lab-anime.js')
change, readme, prep = read('works/changelog.html'), read('README.md'), read('fixes/common/_tools/prep.py')
order, proof = read('fixes/common/_order.md'), read('fixes/common/_proofread.md')

# 1. реестры
def has_key(text, k): return re.search(r"""['"]%s['"]""" % re.escape(k), text) is not None
for k in keys:
    if not has_key(idx, k): bad(f'index.html: нет ключа {k!r}')
    if not re.search(r"^\s*%s\s*:\s*\{" % re.escape(k), lab_js, re.M) and not re.search(r"slug:\s*['\"]%s['\"]" % k, lab_js) and not has_key(lab_js, k):
        bad(f'works/js/lab.js: нет записи {k!r}')
    if not has_key(anim_js, k): bad(f'works/js/lab-anime.js: нет {k!r} (ORDER/TRACKS)')
    if not os.path.exists(f'works/images/thumbs/{k}.webp'): bad(f'нет works/images/thumbs/{k}.webp')
    if not re.search(r"['\"]?%s['\"]?\s*:\s*\{\s*label" % re.escape(k), change): bad(f'works/changelog.html: нет {k!r} в карте LABS')
    if not os.path.isdir(k): bad(f'нет папки подмодуля {k}/')
    if f"'{k}'" not in prep: bad(f'prep.py: нет {k!r} в LABS')
    if k not in proof: bad(f'_proofread.md: нет строки для {k}')
    lm = re.search(r"['\"]?%s['\"]?\s*:\s*\{\s*label:\s*'([^']+)'" % re.escape(k), change)
    names = [k] + ([re.sub(r'\s*Lab$', '', lm.group(1))] if lm else [])
    if not any(re.search(re.escape(n), order, re.I) for n in names): bad(f'_order.md: не упомянута {k}')
    page = read(f'works/{k}.html')
    if f"renderLabPage('{k}')" not in page or f"animeEnhance('{k}')" not in page: bad(f'works/{k}.html: ключ в renderLabPage/animeEnhance не {k}')
    for ref in re.findall(r'(?:src|href)="((?:js|css)/[^"]+)"', page):
        if not os.path.exists('works/' + ref): bad(f'works/{k}.html: нет файла {ref}')

m = re.search(r"var ORDER = \[(.*?)\]", anim_js)
order_keys = re.findall(r"'([^']+)'", m.group(1)) if m else []
if sorted(order_keys) != keys: bad(f'lab-anime.js ORDER не совпадает с works/*.html: {sorted(set(keys) ^ set(order_keys))}')

# 1б. оглавления для окна «Оглавление» (works/js/toc.json) не отстали от методичек
if subprocess.run([sys.executable, 'tools/build-toc.py', '--check']).returncode != 0:
    bad('works/js/toc.json устарел или отсутствует — запустите python3 tools/build-toc.py')

# 2. счётчик лаб в тексте сайта
wrong = sorted(set(re.findall(r'\b(\d{2})\s*(?:ЛАБ|лаб)', idx + readme)) - {str(N)})
if wrong: bad(f'счётчик лаб: найдено {wrong}, ожидалось {N}')

# 3. корневой README: таблица и разделы
for k in keys:
    if f'{k}/' not in readme: bad(f'README.md: нет ссылок на {k}/')

# 4. относительные ссылки в README и README лаб
for md in ['README.md'] + [f'{k}/README.md' for k in keys]:
    if not os.path.exists(md): bad(f'нет {md}'); continue
    base = os.path.dirname(md)
    for link in re.findall(r'\]\((?!https?:|#|mailto:)([^)\s]+)\)', read(md)):
        t = os.path.normpath(os.path.join(base, link.split('#')[0]))
        if link.split('#')[0] and not os.path.exists(t): bad(f'{md}: битая ссылка {link}')
    if md != 'README.md' and 'Статус' not in read(md): bad(f'{md}: нет строки «Статус:»')
    for l in re.findall(r'lab-fixes/blob/main/([\w/.-]+\.md)', read(md)):
        if not os.path.exists('fixes/' + l): bad(f'{md}: ссылка на fixes/{l} не существует')

# 5. синтаксис JS
for f in glob.glob('works/js/*.js'):
    r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
    if r.returncode: bad(f'{f}: {r.stderr.splitlines()[0] if r.stderr else "ошибка синтаксиса"}')
for f in ['index.html', 'works/changelog.html']:
    r = subprocess.run(['node', '-e', "const fs=require('fs');const h=fs.readFileSync(process.argv[1],'utf8');[...h.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)].forEach(m=>new Function(m[1]))", f], capture_output=True, text=True)
    if r.returncode: bad(f'{f}: инлайн-скрипт не компилируется')

# 5b. методички-«бандлы»: текст читается и это валидный JSON (иначе страница не откроется)
sys.path.insert(0, 'fixes/common/_tools')
try:
    import bundle
    for p in sorted(glob.glob('*/*.html') + glob.glob('*/docs/*.html')):
        if p.startswith(('works/', 'fixes/', 'mira/', 'mira-login/')):
            continue
        try:
            bundle._check_json(bundle.load(p))
        except Exception as e:
            bad(f'{p}: методичка: невалидный JSON ({str(e)[:60]})')
except ImportError:
    bad('fixes/common/_tools/bundle.py не найден')

# 5a. у каждой карточки на главной есть сноска `note:` (что требуется: Docker, аккаунт, домен, ключи)
_idx = read('index.html'); _pr = _idx[_idx.index('var projects = ['):_idx.index('\n  ];', _idx.index('var projects = ['))]
if _pr.count("      note: '") != _pr.count("      key: '"):
    bad('index.html: у части карточек нет note: (сноска «что требуется»)')

# 5b. works/verification.html — пара к fixes/common/_verification.md (tools/build-verification.py)
import hashlib as _hl
_md = open('fixes/common/_verification.md', 'rb').read().decode('utf-8')
if not os.path.exists('works/verification.html') or ('verification-md-hash: ' + _hl.sha256(_md.encode()).hexdigest()[:16]) not in read('works/verification.html'):
    bad('works/verification.html не соответствует fixes/common/_verification.md (python3 tools/build-verification.py)')
if not os.path.exists('works/js/status.js') or ('verification-md-hash: ' + _hl.sha256(_md.encode()).hexdigest()[:16]) not in read('works/js/status.js'):
    bad('works/js/status.js не соответствует fixes/common/_verification.md (python3 tools/build-verification.py)')

# 5c. страница прогресса и правки шаблона методичек (tools/build-progress.py, tools/patch-manuals.py)
if not os.path.exists('works/progress.html'):
    bad('нет works/progress.html (python3 tools/build-progress.py)')
else:
    prog = read('works/progress.html')
    for k in keys:
        if f'"key":"{k}"' not in prog: bad(f'works/progress.html: нет лабы {k!r} (python3 tools/build-progress.py)')
try:
    import re as _re, json as _json
    for p in sorted(set(_re.findall(r"open: '\.\./([^']+)'", lab_js))):
        raw = _re.search(r'<script type="__bundler/template">(.*?)</script>', read(p), _re.S).group(1)
        if 'data-all-labs-nav' not in raw or 'data-all-labs-link' in raw or 'x-dc{display:none' not in raw or 'goHash' not in raw:
            bad(f'{p}: нет ссылки «все работы» или правки x-dc (python3 tools/patch-manuals.py)')
        if 'works/js/sync.js' not in raw:
            bad(f'{p}: нет скрипта синхронизации прогресса (python3 tools/patch-manuals.py)')
        if 'works/js/prereq.js' not in raw or 'this.__ps' not in raw:
            bad(f'{p}: нет окна «Что нужно знать» или правки прокрутки (python3 tools/patch-manuals.py)')
    if 'js/sync.js' not in read('works/progress.html'): bad('works/progress.html без sync.js (python3 tools/build-progress.py)')
    # окно «Что нужно знать до старта»: запись на каждую лабу и общий порядок (works/js/prereq.js)
    pq = read('works/js/prereq.js')
    for k in keys:
        if not _re.search(r"(^|\n)\s*'?%s'?: \{\s*\n\s*name:" % _re.escape(k), pq): bad(f'works/js/prereq.js: нет записи для лабы {k!r}')
        if not _re.search(r"ORDER = \[[^\]]*'%s'" % _re.escape(k), pq): bad(f'works/js/prereq.js: лабы {k!r} нет в ORDER')
except Exception as e:
    bad(f'проверка шаблонов методичек: {e}')

# 5d. sitemap.xml, robots.txt, 404.html (tools/build-sitemap.py)
_n = len(glob.glob('works/*.html'))   # главная + страницы витрины − progress.html (личная, noindex)
if not os.path.exists('sitemap.xml') or read('sitemap.xml').count('<loc>') != _n:
    bad('sitemap.xml не соответствует страницам сайта (python3 tools/build-sitemap.py)')
for _f in ('robots.txt', '404.html'):
    if not os.path.exists(_f): bad(f'нет {_f}')

# 5e. SEO-теги (tools/build-seo.py): canonical, Open Graph, JSON-LD на главной и страницах лаб
for _f in ['index.html'] + sorted(glob.glob('works/*.html')):
    if os.path.basename(_f) in ('changelog.html', 'progress.html', 'verification.html'): continue
    _t = read(_f)
    if '<!-- seo:start -->' not in _t or 'rel="canonical"' not in _t or 'og:title' not in _t:
        bad(f'{_f}: нет SEO-тегов (python3 tools/build-seo.py)')
    if _f.startswith('works/') and 'og:image' in _t:
        _k = os.path.basename(_f)[:-5]
        if not os.path.exists(f'works/images/og/{_k}.jpg'): bad(f'нет works/images/og/{_k}.jpg для превью ссылок')

# 6. подмодули не опережают origin
r = subprocess.run(['git', 'submodule', 'foreach', '--quiet', 'b=$(git rev-list --count @{u}..HEAD 2>/dev/null); [ "${b:-0}" != 0 ] && echo "$name ahead $b"; true'], capture_output=True, text=True)
for line in r.stdout.splitlines(): bad(f'подмодуль опережает origin: {line}')

print('\n'.join(notes))
if problems:
    print(f'\nПроблем: {len(problems)}'); print('\n'.join(' - ' + p for p in problems)); sys.exit(1)
print('OK: проблем не найдено')
