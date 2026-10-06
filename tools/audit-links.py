# -*- coding: utf-8 -*-
"""Проверка всех внешних ссылок (md, сайт, методички). Код 429 (лимит запросов) считается ОК. Запуск: python3 tools/audit-links.py
(в CI — .github/workflows/links.yml раз в неделю; падает, если есть битые ссылки)"""
import re,os,sys,json,glob,subprocess,urllib.request,urllib.error,ssl,socket
from concurrent.futures import ThreadPoolExecutor
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,'fixes/common/_tools'); import bundle
urls={}   # url -> set(источников)
def add(u,src):
    u=u.rstrip('.,;:!?)»"\'').replace('&amp;','&')
    if u.startswith('http'): urls.setdefault(u,set()).add(src)
# 1. md-файлы (родитель + сабмодули)
mds=subprocess.run(['git','ls-files','--recurse-submodules','*.md'],capture_output=True,text=True).stdout.split()
for f in mds:
    t=open(f,encoding='utf-8',errors='ignore').read()
    for u in re.findall(r'https?://[^\s<>"\'`\)\]]+',t): add(u,f)
# 2. html/js сайта
for f in ['index.html','site-private/mira/index.html','site-private/mira-login/index.html']+glob.glob('works/*.html')+glob.glob('works/js/*.js'):
    t=open(f,encoding='utf-8',errors='ignore').read()
    for u in re.findall(r'https?://[^\s<>"\'`\)\\]+',t): add(u,f)
# 3. методички
for d in sorted(x for x in os.listdir('.') if os.path.isfile(f'{x}/{x}.html')):
    t=bundle.load(f'{d}/{d}.html')
    for u in re.findall(r'https?://[^\s<>"\'`\)\\]+',t): add(u,f'{d}/{d}.html')
skip=re.compile(r'(localhost|127\.0\.0\.1|example\.(com|org)|\.localhost|0\.0\.0\.0|\$\{|\{|your-|<)',re.I)
todo=[u for u in urls if not skip.search(u)]
print('уникальных URL:',len(urls),'к проверке:',len(todo),flush=True)
ctx=ssl.create_default_context()
def chk(u):
    for meth in ('HEAD','GET'):
        try:
            r=urllib.request.Request(u.split('#')[0],method=meth,headers={'User-Agent':'Mozilla/5.0 (audit)'})
            with urllib.request.urlopen(r,timeout=15,context=ctx) as x: return u,x.status
        except urllib.error.HTTPError as e:
            if meth=='HEAD' and e.code in (403,405,400,501): continue
            return u,e.code
        except Exception as e:
            if meth=='HEAD': continue
            return u,str(e)[:60]
    return u,'?'
res={}
with ThreadPoolExecutor(12) as ex:
    for i,(u,s) in enumerate(ex.map(chk,todo)):
        res[u]=s
        if i%100==0: print(i,flush=True)
bad={u:s for u,s in res.items() if not (isinstance(s,int) and (s<400 or s==429)) and not re.search(r'%28|\(',u)}
out={'total':len(todo),'bad':[{'url':u,'status':s,'in':sorted(urls[u])[:4]} for u,s in sorted(bad.items())]}
for b in out['bad']: print(b['status'],b['url'],'←',', '.join(b['in']))
print('ГОТОВО. Всего',len(todo),'проблемных',len(bad))
sys.exit(1 if bad else 0)
