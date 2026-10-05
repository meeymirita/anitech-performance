#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает sitemap.xml из страниц сайта (главная + works/*.html). Запуск: python3 tools/build-sitemap.py"""
import glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://anitech.meeymirita.ru'
PRIVATE = {'progress.html'}   # личные страницы (noindex) в карту не попадают
urls = [BASE + '/'] + [f'{BASE}/works/{os.path.basename(p)}' for p in sorted(glob.glob(os.path.join(ROOT, 'works', '*.html'))) if os.path.basename(p) not in PRIVATE]
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
      ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n'
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)
print(f'sitemap.xml: {len(urls)} адресов')
