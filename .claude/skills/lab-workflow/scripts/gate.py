#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Шлюз перед тем как сказать "готово". НЕ заменяет tools/check-site.py —
дополняет его проверкой того, что люди (и модели) забывают чаще всего:
записи в changelog/state-log за сегодня и чистоту git-статуса.
Запускать из корня репозитория: python3 .claude/skills/lab-workflow/scripts/gate.py
"""
import datetime
import os
import re
import subprocess
import sys

ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
if not ROOT:
    ROOT = os.getcwd()
os.chdir(ROOT)

today_iso = datetime.date.today().isoformat()          # 2026-10-14 (changelog)
today_ru = datetime.date.today().strftime("%d.%m.%Y")  # 14.10.2026 (state-log, README)

lines = []
problems = []


def ok(msg):
    lines.append(f"  OK   {msg}")


def warn(msg):
    lines.append(f"  ?    {msg}")


def bad(msg):
    lines.append(f"  НЕТ  {msg}")
    problems.append(msg)


print(f"=== Шлюз lab-workflow — {today_ru} ===\n")

# 1. check-site.py — источник правды по реестрам
print("1) tools/check-site.py")
r = subprocess.run(["python3", "tools/check-site.py"], capture_output=True, text=True)
out = (r.stdout + r.stderr).strip()
if r.returncode == 0:
    ok("check-site.py: OK")
else:
    bad("check-site.py нашёл проблемы:\n" + "\n".join("         " + l for l in out.splitlines()))
print("\n".join(lines[-1:]))
lines_before = len(lines)

# 2. changelog.html — запись за сегодня
print("\n2) works/changelog.html")
try:
    changelog = open("works/changelog.html", encoding="utf-8").read()
    if f"date:'{today_iso}'" in changelog or f'date:"{today_iso}"' in changelog:
        ok(f"есть запись в DAYS за {today_iso}")
    else:
        warn(f"нет записи в DAYS за {today_iso} — добавить, если сегодня что-то менялось по сути "
             f"(не нужно для совсем служебной правки без видимых изменений)")
except FileNotFoundError:
    bad("works/changelog.html не найден")
print("\n".join(lines[-1:]))

# 3. _state-log.md — запись за сегодня в начале журнала
print("\n3) fixes/common/_state-log.md")
try:
    state_log = open("fixes/common/_state-log.md", encoding="utf-8").read()
    m = re.search(r"## Журнал\s*\n+### ([\d.]+)", state_log)
    top_date = m.group(1) if m else None
    if top_date == today_ru:
        ok(f"верхняя запись журнала датирована сегодня ({today_ru})")
    elif today_ru in state_log:
        warn(f"запись за {today_ru} есть, но не первая в журнале — новые записи кладутся В НАЧАЛО")
    else:
        warn(f"нет записи за {today_ru} в начале журнала — дописать, что сделано и что осталось")
except FileNotFoundError:
    bad("fixes/common/_state-log.md не найден")
print("\n".join(lines[-1:]))

# 4. git — чистота и подмодули
print("\n4) git status")
status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
if status.strip():
    warn("есть незакоммиченные изменения (это нормально, если git ещё не просили делать):\n"
         + "\n".join("         " + l for l in status.splitlines()))
else:
    ok("git status чистый")
print("\n".join(lines[-1:]))

ahead = subprocess.run(
    ["git", "submodule", "foreach", "--quiet",
     'b=$(git rev-list --count @{u}..HEAD 2>/dev/null); [ "${b:-0}" != 0 ] && echo "$name ahead $b"; true'],
    capture_output=True, text=True,
).stdout.strip()
if ahead:
    warn("подмодули опережают origin (запушить ПЕРЕД пушем родителя):\n"
         + "\n".join("         " + l for l in ahead.splitlines()))
else:
    ok("ни один подмодуль не опережает origin")
print("\n".join(lines[-1:]))

print("\n=== Итог ===")
for l in lines:
    print(l)

print(
    "\nЭтот скрипт не проверяет (сделать руками, если применимо к задаче):\n"
    "  - видимый текст методички в Chromium (bundle.py может поменять только скрытый text);\n"
    "  - README лабы / корневой README / CLAUDE.md, если менялся статус;\n"
    "  - Actions после пуша (gh run list --limit 4)."
)

if problems:
    sys.exit(1)
sys.exit(0)
