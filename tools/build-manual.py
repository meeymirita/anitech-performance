#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает методичку лабы из Markdown-исходников: <лаба>/src/*.md -> <лаба>/<лаба>.html (формат «бандл»).

Запуск из корня репозитория:
    python3 tools/build-manual.py bash            # собрать, подставив сохранённые результаты запусков
    python3 tools/build-manual.py bash --run      # сначала выполнить блоки «run» в Docker (образ <лаба>-lab) и обновить результаты
    python3 tools/build-manual.py bash --check    # только проверка структуры
    python3 tools/build-manual.py docker --run --sessions 3,4   # (режим dind) выполнить только эти сессии, не сбрасывая стенд, результаты слить с прежними
Если рядом с исходниками есть `src/run.json` вида {"dind": true}, блоки выполняются в изолированном Docker-в-Docker (docker:dind):
свой демон, свои образы и тома — настоящий Docker Mac пользователя не затрагивается; HOME=/work, `localhost` указывает на демон.

Исходники (папка <лаба>/src/):
    00-meta.md   — поля `ключ: значение`, затем строка `---` и текст введения (Markdown)
    NN-*.md      — сессии:  `# Сессия N · Название`, `dur: ~3 ч`, затем шаги `## N.M Название | short: … | est: ~20 мин`
                   внутри шага разделы `### intro|result|why|deep <заголовок>|quiz|outro|links`
    ref-*.md     — справочные/теоретические блоки: `# <num> · Название | short: … | kind: ref|theory`, затем текст
    gloss.md     — глоссарий: строки `термин :: определение`
Разметка: абзацы, **жирный**, *курсив*, `код`, [текст](url), [[Ctrl]] (клавиша), списки `- ` / `1. `, таблицы `| a | b |`,
блоки кода ```bash / ```out, врезки `:::tip Заголовок` / `:::trap Заголовок` … `:::`.
Блок ```bash run выполняется в Docker; следующий за ним ```out auto заполняется настоящим выводом.
"""
import glob, hashlib, html, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'fixes/common/_tools'))
import bundle  # noqa: E402

BASE = 'centrifugo/centrifugo.html'   # любая интегрированная лаба: шаблон у всех одинаковый


# ───────────────────────── Markdown -> HTML ─────────────────────────
def inline(s):
    codes = []

    def keep(m):
        codes.append('<code>' + html.escape(m.group(1), quote=False) + '</code>')
        return '\x00%d\x00' % (len(codes) - 1)
    s = re.sub(r'`([^`]+)`', keep, s)
    s = html.escape(s, quote=False)
    s = re.sub(r'\[\[([^\]]+)\]\]', r'<kbd>\1</kbd>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+|#[\w-]+)\)',
               lambda m: '<a href="%s"%s>%s</a>' % (m.group(2), ' target="_blank" rel="noopener"' if m.group(2).startswith('http') else '', m.group(1)), s)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], s)


def pre(lang, body, cls=''):
    return '<pre class="%s" data-lang="%s"><code>%s</code></pre>' % (cls, lang, html.escape(body, quote=False))


def blocks(lines, outs=None, ctx=None):
    """Разбор строк Markdown в HTML. outs — подстановки для ```out auto (по порядку)."""
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        m = re.match(r'^```(\S*)\s*(.*)$', ln)
        if m:
            lang, flags = m.group(1) or 'text', m.group(2).split()
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            body = '\n'.join(lines[i + 1:j])
            if lang == 'svg':
                out.append('<div class="diagram" style="margin:14px 0;overflow-x:auto;text-align:center">%s</div>' % body)
                i = j + 1
                continue
            if lang == 'out':
                if 'auto' in flags and ctx is not None:
                    body = ctx['take']()
                out.append(pre('out', body, 'out'))
            else:
                if 'run' in flags and ctx is not None:
                    ctx['run'](body, 'hidden' in flags)
                if 'hidden' not in flags:
                    out.append(pre(lang, body))
            i = j + 1
            continue
        m = re.match(r'^:::(tip|trap)\s*(.*)$', ln)
        if m:
            j = i + 1
            while j < len(lines) and lines[j].strip() != ':::':
                j += 1
            ico = '💡' if m.group(1) == 'tip' else '🔨'
            out.append('<div class="%s"><b>%s %s</b>%s</div>' % (m.group(1), ico, inline(m.group(2)), blocks(lines[i + 1:j], outs, ctx)))
            i = j + 1
            continue
        if ln.lstrip().startswith('|'):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith('|'):
                j += 1
            rows = [[c.strip() for c in r.strip().strip('|').split('|')] for r in lines[i:j] if not re.match(r'^\s*\|[\s:|-]+\|\s*$', r)]
            t = '<table>\n<tr>' + ''.join('<th>%s</th>' % inline(c) for c in rows[0]) + '</tr>\n'
            for r in rows[1:]:
                t += '<tr>' + ''.join('<td>%s</td>' % inline(c) for c in r) + '</tr>\n'
            out.append(t + '</table>')
            i = j
            continue
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+', ln)
        if m:
            tag = 'ol' if m.group(2)[0].isdigit() else 'ul'
            items = []
            j = i
            while j < len(lines) and re.match(r'^(\s*)([-*]|\d+\.)\s+', lines[j]):
                items.append(re.sub(r'^\s*([-*]|\d+\.)\s+', '', lines[j]))
                j += 1
                while j < len(lines) and lines[j].startswith('  ') and lines[j].strip() and not re.match(r'^\s*([-*]|\d+\.)\s+', lines[j]):
                    items[-1] += ' ' + lines[j].strip()
                    j += 1
            out.append('<%s>\n%s\n</%s>' % (tag, '\n'.join('<li>%s</li>' % inline(x) for x in items), tag))
            i = j
            continue
        m = re.match(r'^(#{4,6})\s+(.*)$', ln)
        if m:
            out.append('<p><b>%s</b></p>' % inline(m.group(2)))
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].strip() and not re.match(r'^(```|:::|\||\s*([-*]|\d+\.)\s+|#{4,6}\s)', lines[j]):
            j += 1
        out.append('<p>%s</p>' % inline(' '.join(x.strip() for x in lines[i:j])))
        i = j
    return '\n'.join(out)


def plain(h):
    t = re.sub(r'<[^>]+>', ' ', h)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()


# ───────────────────────── разбор исходников ─────────────────────────
def read(path):
    return open(path, encoding='utf-8').read().replace('\r\n', '\n')


def fields(s):
    d = {}
    for part in s.split('|'):
        m = re.match(r'\s*(\w+):\s*(.*?)\s*$', part)
        if m:
            d[m.group(1)] = m.group(2)
    return d


def parse(lab):
    src = os.path.join(ROOT, lab, 'src')
    meta_txt = read(os.path.join(src, '00-meta.md'))
    head, intro = meta_txt.split('\n---\n', 1)
    meta = dict(re.findall(r'^(\w+):\s*(.*)$', head, re.M))
    sessions, theory, refs = [], [], []
    for f in sorted(glob.glob(src + '/*.md')):
        b = os.path.basename(f)
        if b.startswith('00-'):
            continue
        txt = read(f)
        if b == 'gloss.md':
            continue
        if b.startswith('ref-'):
            m = re.match(r'^#\s+(\S+)\s+·\s+([^|\n]+?)\s*(\|.*)?\n', txt)
            fl = fields(m.group(3) or '')
            u = dict(num=m.group(1), title=m.group(2).strip(), short=fl.get('short', m.group(2).strip()),
                     kind=fl.get('kind', 'ref'), body=txt[m.end():].split('\n'))
            (theory if u['kind'] == 'theory' else refs).append(u)
            continue
        # сессия
        m = re.match(r'^#\s+Сессия\s+(\d+)\s+·\s+(.+?)\n', txt)
        n = int(m.group(1))
        rest = txt[m.end():]
        mm = re.match(r'dur:\s*(.+)\n', rest)
        dur = mm.group(1).strip() if mm else ''
        rest = rest[mm.end():] if mm else rest
        parts = re.split(r'^## ', rest, flags=re.M)
        steps = []
        for p in parts[1:]:
            title_line, _, body = p.partition('\n')
            m2 = re.match(r'^(\d+\.\d+)\s+([^|]+?)\s*(\|.*)?$', title_line)
            fl = fields(m2.group(3) or '')
            sec = {'deep': []}
            cur = None
            for ln in body.split('\n'):
                h = re.match(r'^### (intro|result|why|deep|quiz|outro|links)\s*(.*)$', ln)
                if h:
                    cur = [h.group(1), h.group(2), []]
                    if h.group(1) == 'deep':
                        sec['deep'].append(cur)
                    else:
                        sec[h.group(1)] = cur
                elif cur is not None:
                    cur[2].append(ln)
            steps.append(dict(num=m2.group(1), title=m2.group(2).strip(), short=fl.get('short', m2.group(2).strip()),
                              est=fl.get('est', '~20 мин'), sec=sec, session=n))
        sessions.append(dict(n=n, title=m.group(2).strip(), dur=dur, steps=steps, file=b))
    gloss = []
    gp = os.path.join(src, 'gloss.md')
    if os.path.exists(gp):
        for ln in read(gp).split('\n'):
            if '::' in ln:
                t, d = ln.split('::', 1)
                gloss.append({'term': t.strip(), 'def': inline(d.strip())})
    return meta, intro.strip(), sessions, theory, refs, gloss


# ───────────────────────── запуск блоков в Docker ─────────────────────────
def transcript(body, hidden):
    """Скрипт для одного блока: строки команд печатаются как `$ команда`, затем идёт их вывод (как в терминале)."""
    import shlex
    if hidden:
        return '{\n' + body + '\n} >/dev/null 2>&1'
    lines = body.split('\n')
    compound = re.search(r'<<|^\s*(for|while|if|case|until|function)\b|\)\s*\{|\\$|^\s*\w+\(\)', body, re.M)
    if compound:
        shown = '$ ' + lines[0] + (' …' if len(lines) > 1 else '')
        return '__rc=$?; printf "%s\\n" ' + shlex.quote(shown) + '; (exit $__rc)\n' + body
    out = []
    for l in lines:
        if not l.strip():
            continue
        out.append('__rc=$?; printf "%s\\n" ' + shlex.quote(('' if l.lstrip().startswith('#') else '$ ') + l) + '; (exit $__rc)')
        out.append(l)
    return '\n'.join(out)


DIND_PRELUDE = """exec 2>&1
export HOME=/work
cd /work
mkdir -p /opt/ch; echo 'connect-to = localhost::%(dind)s:' > /opt/ch/.curlrc; export CURL_HOME=/opt/ch
"""


def dind_up(lab, reset):
    """Поднимает изолированный демон <lab>-dind (docker:dind) с общим томом /work; при reset пересоздаёт всё с нуля."""
    net, dind, data, work = lab + '-net', lab + '-dind', lab + '-dind-data', lab + '-work'
    sh = lambda *a, **k: subprocess.run(list(a), capture_output=True, text=True, **k)
    if reset:
        sh('docker', 'rm', '-f', dind)
        sh('docker', 'volume', 'rm', '-f', data, work)
        sh('docker', 'network', 'rm', net)
    sh('docker', 'network', 'create', net)
    if sh('docker', 'inspect', '-f', '{{.State.Running}}', dind).stdout.strip() != 'true':
        sh('docker', 'rm', '-f', dind)
        r = sh('docker', 'run', '-d', '--name', dind, '--network', net, '--privileged', '-e', 'DOCKER_TLS_CERTDIR=',
               '-v', data + ':/var/lib/docker', '-v', work + ':/work', 'docker:dind', '--dns', '1.1.1.1', '--dns', '8.8.8.8')
        assert r.returncode == 0, r.stderr
    import time
    for _ in range(60):
        if sh('docker', 'exec', dind, 'docker', 'info').returncode == 0:
            return net, dind, work
        time.sleep(1)
    raise SystemExit('демон dind не поднялся')


def run_all(lab, sessions, only=None):
    """Выполняет блоки `run` сессий по порядку в одной рабочей папке; возвращает {(сессия, номер блока): вывод}."""
    image = lab + '-check'
    subprocess.run(['docker', 'build', '-q', '-t', image, os.path.join(ROOT, lab)], check=True, stdout=subprocess.DEVNULL)
    conf_path = os.path.join(ROOT, lab, 'src', 'run.json')
    conf = json.load(open(conf_path)) if os.path.exists(conf_path) else {}
    if conf.get('dind'):
        net, dind, work = dind_up(lab, reset=only is None)
    else:
        work = tempfile.mkdtemp(prefix=lab + '-work-')
    res = {}
    for s in sessions:
        if only and s['n'] not in only:
            continue
        codes = []
        ctx = {'run': lambda b, h=False: codes.append((b, h)), 'take': lambda: ''}
        for st in s['steps']:
            for key in ('intro', 'result', 'why', 'outro'):
                if key in st['sec']:
                    blocks(st['sec'][key][2], None, ctx)
            for d in st['sec']['deep']:
                blocks(d[2], None, ctx)
        script = (DIND_PRELUDE % {'dind': dind}) if conf.get('dind') else 'exec 2>&1\ncd /work\n'
        for k, (c, hid) in enumerate(codes):
            script += transcript(c, hid) + '\necho "@@END:%d"\n' % k
        sp_name = '.s%d.sh' % s['n']
        if conf.get('dind'):
            subprocess.run(['docker', 'exec', '-i', dind, 'sh', '-c', 'cat > /work/' + sp_name], input=script, text=True, check=True)
            cmd = ['docker', 'run', '--rm', '-i', '--network', net, '-e', 'DOCKER_HOST=tcp://%s:2375' % dind, '-v', work + ':/work', image, 'bash', '/work/' + sp_name]
        else:
            open(os.path.join(work, sp_name), 'w', encoding='utf-8').write(script)
            cmd = ['docker', 'run', '--rm', '-i', '-v', work + ':/work', image, 'bash', '/work/' + sp_name]
        r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1800)
        txt = r.stdout + r.stderr
        txt = re.sub(r'/work/\.s\d+\.sh: (line \d+: )?', 'bash: ', txt)   # сообщения как в интерактивной оболочке
        if conf.get('dind'):   # без терминала docker печатает все стадии загрузки слоёв; в терминале остаются только итоговые строки
            txt = re.sub(r'^[0-9a-f]{12}: (Pulling fs layer|Download complete|Waiting|Verifying Checksum|Downloading|Extracting).*\n', '', txt, flags=re.M)
        chunks = re.split(r'@@END:\d+\n?', txt)
        for k in range(len(codes)):
            res['%d:%d' % (s['n'], k)] = chunks[k].rstrip('\n') if k < len(chunks) else ''
        print('сессия %d: выполнено блоков %d' % (s['n'], len(codes)))
    return res


# ───────────────────────── сборка ─────────────────────────
def build(lab, run=False, check_only=False, only=None):
    meta, intro, sessions, theory, refs, gloss = parse(lab)
    cache_path = os.path.join(ROOT, lab, 'src', 'outputs.json')
    if run:
        res = run_all(lab, sessions, only)
        if only and os.path.exists(cache_path):
            old = json.load(open(cache_path, encoding='utf-8'))
            old = {k: v for k, v in old.items() if int(k.split(':')[0]) not in only}
            old.update(res)
            res = old
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        json.dump(res, open(cache_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    cache = json.load(open(cache_path, encoding='utf-8')) if os.path.exists(cache_path) else {}

    units, sess_out = [], []
    for u in theory:
        h = blocks(u['body'])
        units.append(dict(key='sec-' + u['num'], kind='theory', num=u['num'], title=u['title'], short=u['short'], html=h, text=plain(h)))
    for s in sessions:
        counter = {'k': 0}
        keys = []
        for st in s['steps']:
            ctx = {'run': lambda b: None, 'take': None}
            outs_taken = []

            def take(_s=s, _c=counter):
                pass
            # номера блоков run нумеруются сквозь сессию в том же порядке, что и в run_all
            def mk_ctx():
                state = {'pending': []}

                def runner(body, hidden=False):
                    if not hidden:
                        state['pending'].append('%d:%d' % (s['n'], counter['k']))
                    counter['k'] += 1

                def taker():
                    ids, state['pending'] = state['pending'], []
                    if not ids:
                        return '(нет вывода)'
                    return '\n'.join(cache.get(i, '(вывод не получен: запусти сборку с --run)') for i in ids)
                return {'run': runner, 'take': taker}
            ctx = mk_ctx()
            d = dict(key='step-%s' % st['num'].replace('.', '-'), kind='step', num=st['num'], title=st['title'], short=st['short'],
                     est=st['est'], session=s['n'])
            order = ['intro', 'result']
            conv = {}
            # intro и result идут в порядке текста: блоки run нумеруются в порядке intro, result, why, outro, deep
            for key in ('intro', 'result', 'why', 'outro'):
                if key in st['sec']:
                    conv[key] = blocks(st['sec'][key][2], None, ctx)
            deep = []
            for dd in st['sec']['deep']:
                deep.append({'summary': dd[1] or 'Подробнее', 'html': blocks(dd[2], None, ctx)})
            d['intro'] = conv.get('intro', '')
            d['result'] = conv.get('result') or None
            d['why'] = plain(conv['why']) if False else (conv.get('why') or '')
            # поле why — HTML-строка без обёртки <p> (как в других лабах)
            if d['why'].startswith('<p>') and d['why'].count('<p>') == 1:
                d['why'] = d['why'][3:-4]
            d['deep'] = deep
            q = [re.sub(r'^\s*[-*]\s+', '', x) for x in st['sec'].get('quiz', [0, 0, []])[2] if x.strip()]
            d['quiz'] = [inline(x) for x in q]
            lk = []
            for x in st['sec'].get('links', [0, 0, []])[2]:
                p = [t.strip() for t in re.sub(r'^\s*[-*]\s+', '', x).split('|')]
                if len(p) == 3:
                    lk.append({'u': p[0], 'n': p[1], 't': p[2]})
            d['links'] = lk
            d['outro'] = conv.get('outro') or None
            d['text'] = plain(' '.join([d['intro'], d['result'] or '', d['why']] + [x['summary'] + ' ' + x['html'] for x in deep] + [d['outro'] or '']))
            units.append(d)
            keys.append(d['key'])
        sess_out.append(dict(n=s['n'], code=str(s['n']), title=s['title'], dur=s['dur'], steps=keys))
    for u in refs:
        h = blocks(u['body'])
        units.append(dict(key='sec-' + u['num'], kind='ref', num=u['num'], title=u['title'], short=u['short'], html=h, text=plain(h)))
    gkey = None
    if gloss:
        gkey = next(u['key'] for u in units if u['title'] == 'Глоссарий')
        g = next(u for u in units if u['key'] == gkey)
        g['gloss'] = gloss
        g['html'] = ''.join('<div id="g-%d"><b>%s</b> — %s</div>' % (i, html.escape(x['term'], quote=False), x['def']) for i, x in enumerate(gloss))
        g['text'] = ' '.join(x['term'] + ' ' + plain(x['def']) for x in gloss)

    toc = '<b style="font-weight:800">Содержание</b>\n<ol style="margin:0 0 14px;padding-left:22px">' + ''.join(
        '<li style="margin:4px 0;line-height:1.6;font-size:15px"><a href="#%s" style="color:var(--accent-ink);text-decoration:underline;text-underline-offset:2px">%s</a></li>'
        % (u['key'], html.escape(u['title'], quote=False)) for u in units if u['kind'] != 'step') + '</ol>'
    lab_json = dict(slug=meta['slug'], title=meta['title'], subtitle=meta['subtitle'], accent=meta['accent'], planned=meta['planned'],
                    introHtml=blocks(intro.split('\n')), tocHtml=toc, glossKey=gkey, units=units, sessions=sess_out)

    # проверка структуры
    keys = {u['key'] for u in units}
    assert len(keys) == len(units), 'повторяются ключи'
    for s in sess_out:
        for k in s['steps']:
            assert k in keys
    for u in units:
        if u['kind'] == 'step':
            assert u['intro'] and u['quiz'], 'пустой intro или quiz: ' + u['key']
            assert '(вывод не получен' not in json.dumps(u, ensure_ascii=False), 'нет вывода запусков: ' + u['key']
    print('структура ок: сессий %d, шагов %d, блоков теории/справки %d' % (len(sess_out), sum(1 for u in units if u['kind'] == 'step'), sum(1 for u in units if u['kind'] != 'step')))
    if check_only:
        return
    dst = os.path.join(ROOT, lab, lab + '.html')
    if not os.path.exists(dst):
        open(dst, 'w', encoding='utf-8').write(open(os.path.join(ROOT, BASE), encoding='utf-8').read())
    payload = 'window.LAB=' + json.dumps(lab_json, ensure_ascii=False) + ';'
    bundle.transform(dst, lambda old: payload)
    print('собрано:', dst)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    only = None
    if '--sessions' in a:
        only = {int(x) for x in a[a.index('--sessions') + 1].split(',')}
    build(a[0], run='--run' in a, check_only='--check' in a, only=only)
