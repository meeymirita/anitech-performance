#!/usr/bin/env python3
"""Синхронизация репозитория с бакетом Yandex Object Storage (meeymirita-files).

Репозиторий — источник правды, бакет — только раздача. Скрипт строит список «файл → ключ в бакете»,
сравнивает с бакетом по MD5 (ETag), загружает новое и изменённое, удаляет лишнее в управляемых папках.

    python3 tools/sync-bucket.py --dry-run   # ничего не меняет, ключи не нужны (листинг бакета публичный)
    python3 tools/sync-bucket.py             # загрузить и удалить; нужны ключи (ниже) и `pip install boto3`

Ключи — статический ключ сервисного аккаунта с ролью storage.editor на бакет:
    YC_ACCESS_KEY_ID, YC_SECRET_ACCESS_KEY  (переменные окружения или файл ~/.config/anitech/yc.env)

Что лежит в бакете:
    <лаба>/<лаба>.html      методичка        ← <лаба>/<лаба>.html
    <лаба>/README.md        README           ← <лаба>/README.md
    <лаба>/thumb.webp       миниатюра        ← works/images/thumbs/<лаба>.webp
    <лаба>/og.jpg           картинка для превью ссылок (SEO) ← works/images/og/<лаба>.jpg (jpeg 1200 px; `sips -s format jpeg -s formatOptions 65 -Z 1200`)
    <лаба>/<имя>.png        обложка          ← works/images/<лаба>.png (имя — из ссылки `image:` в index.html)
    site/me.jpg             фото автора      ← works/images/me.jpg
    site/screenshots/*.jpg  скрины «О проекте» ← docs/screenshots/*.jpg
Удаляется всё, что лежит в этих папках (<лаба>/, site/), но не описано выше. Остальное (например old_files/) не трогается.

Страховка: перед каждой загрузкой, которая что-то меняет или удаляет, прежние версии этих файлов копируются в
old_files/last-sync/<тот же ключ>; предыдущее содержимое этой папки при этом стирается (хранится ровно один шаг назад).
Вернуть файл — скопировать его из old_files/last-sync/ на прежнее место.
Лаба = папка с `<папка>/<папка>.html` в корне (подмодуль).
"""
import hashlib, os, re, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET

BUCKET = 'meeymirita-files'
PUBLIC = f'https://{BUCKET}.storage.yandexcloud.net'
ENDPOINT = 'https://storage.yandexcloud.net'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BACKUP = 'old_files/last-sync/'
TYPES = {'.html': 'text/html; charset=utf-8', '.md': 'text/markdown; charset=utf-8', '.png': 'image/png',
         '.jpg': 'image/jpeg', '.webp': 'image/webp'}


def build_manifest():
    """{ключ в бакете: локальный путь}"""
    idx = open('index.html', encoding='utf-8').read()
    covers = dict(re.findall(re.escape(PUBLIC) + r'/([\w-]+)/([^\'"\s]+\.png)', idx))
    m = {}
    labs = sorted(d for d in os.listdir('.') if os.path.isfile(f'{d}/{d}.html'))
    for k in labs:
        m[f'{k}/{k}.html'] = f'{k}/{k}.html'
        if os.path.isfile(f'{k}/README.md'):
            m[f'{k}/README.md'] = f'{k}/README.md'
        m[f'{k}/thumb.webp'] = f'works/images/thumbs/{k}.webp'
        if os.path.isfile(f'works/images/og/{k}.jpg'):
            m[f'{k}/og.jpg'] = f'works/images/og/{k}.jpg'
        if k in covers:
            m[f'{k}/{covers[k]}'] = f'works/images/{k}.png'
        else:
            print(f'! нет ссылки на обложку {k} в index.html — обложка не загружается')
    m['site/me.jpg'] = 'works/images/me.jpg'
    for f in sorted(os.listdir('docs/screenshots')):
        m[f'site/screenshots/{f}'] = f'docs/screenshots/{f}'
    missing = [p for p in m.values() if not os.path.isfile(p)]
    if missing:
        sys.exit('нет локальных файлов: ' + ', '.join(missing))
    return m, labs


def list_public():
    """{ключ: md5} — публичный листинг, без ключей"""
    ns = {'s': 'http://s3.amazonaws.com/doc/2006-03-01/'}
    out, token = {}, None
    while True:
        url = f'{PUBLIC}/?list-type=2&max-keys=1000' + (f'&continuation-token={urllib.parse.quote(token)}' if token else '')
        root = ET.fromstring(urllib.request.urlopen(url, timeout=30).read())
        for c in root.findall('s:Contents', ns):
            out[c.find('s:Key', ns).text] = c.find('s:ETag', ns).text.strip('"')
        t = root.find('s:NextContinuationToken', ns)
        if t is None:
            return out
        token = t.text


def load_keys():
    env = os.path.expanduser('~/.config/anitech/yc.env')
    if os.path.isfile(env):
        for line in open(env):
            if '=' in line and not line.lstrip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ.setdefault(k, v.strip().strip('"\''))
    return os.environ.get('YC_ACCESS_KEY_ID'), os.environ.get('YC_SECRET_ACCESS_KEY')


def main():
    dry = '--dry-run' in sys.argv
    manifest, labs = build_manifest()
    if len(manifest) < 50:
        sys.exit(f'в списке всего {len(manifest)} файлов — похоже на пустой чекаут (подмодули?), удалять нечего не буду')
    remote = list_public()
    managed = tuple(f'{k}/' for k in labs) + ('site/',)
    md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
    up = [k for k, p in manifest.items() if remote.get(k) != md5(p)]
    rm = sorted(k for k in remote if k.startswith(managed) and k not in manifest and not k.endswith('/'))
    unmanaged = sorted(k for k in remote if not k.startswith(managed))
    for k in up:
        print(('+ новое    ' if k not in remote else '~ изменено ') + k)
    for k in rm:
        print('- удалить   ' + k)
    print(f'итого: загрузить {len(up)}, удалить {len(rm)}, без изменений {len(manifest) - len(up)}'
          + (f'; не трогаю (вне управляемых папок): {len(unmanaged)}' if unmanaged else ''))
    if dry or not (up or rm):
        return
    kid, secret = load_keys()
    if not kid or not secret:
        sys.exit('нет ключей: задайте YC_ACCESS_KEY_ID и YC_SECRET_ACCESS_KEY (или ~/.config/anitech/yc.env)')
    try:
        import boto3
    except ImportError:
        sys.exit('нужен boto3: pip install boto3')
    s3 = boto3.client('s3', endpoint_url=ENDPOINT, region_name='ru-central1',
                      aws_access_key_id=kid, aws_secret_access_key=secret)
    # страховка: прежние версии изменяемого и удаляемого — в old_files/last-sync/ (прошлая копия стирается)
    before = [k for k in up if k in remote] + rm
    if before:
        stale = [k for k in remote if k.startswith(BACKUP)]
        for i in range(0, len(stale), 1000):
            s3.delete_objects(Bucket=BUCKET, Delete={'Objects': [{'Key': k} for k in stale[i:i + 1000]], 'Quiet': True})
        for k in before:
            s3.copy_object(Bucket=BUCKET, Key=BACKUP + k, CopySource={'Bucket': BUCKET, 'Key': k},
                           MetadataDirective='COPY')
        print(f'копия прежних версий: {len(before)} файлов → {BACKUP}')
    for k in up:
        ext = os.path.splitext(k)[1]
        with open(manifest[k], 'rb') as f:
            s3.put_object(Bucket=BUCKET, Key=k, Body=f, ContentType=TYPES.get(ext, 'application/octet-stream'),
                          CacheControl='no-cache')
    for i in range(0, len(rm), 1000):
        s3.delete_objects(Bucket=BUCKET, Delete={'Objects': [{'Key': k} for k in rm[i:i + 1000]], 'Quiet': True})
    ok = list_public()
    bad = [k for k, p in manifest.items() if ok.get(k) != md5(p)]
    if bad:
        sys.exit('после загрузки не совпали: ' + ', '.join(bad))
    print('готово: бакет совпадает с репозиторием')


if __name__ == '__main__':
    main()
