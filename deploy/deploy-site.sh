#!/bin/bash
# Деплой сайта на сервер: подтянуть репозиторий и выложить в папку, которую раздаёт Caddy.
# Запускается таймером systemd раз в минуту (deploy/anitech-deploy.timer). Руками: sudo /opt/anitech-src/deploy/deploy-site.sh
# Страницы /mira/ и /mira-login/ защищены паролем на уровне Caddy (deploy/protect-mira.sh) — здесь только копируются.
# Меняется только содержимое /var/www/anitech-performance; если ничего не изменилось — выходит сразу.
set -euo pipefail

SRC="${SRC:-/opt/anitech-src}"                 # клон репозитория
WEB="${WEB:-/var/www/anitech-performance}"     # root в Caddyfile
STATE="${STATE:-/var/lib/anitech-deploy.rev}"  # какая версия уже выложена
export GIT_TERMINAL_PROMPT=0

cd "$SRC"
if [ -z "${SKIP_GIT:-}" ]; then
  git fetch -q origin main
  git reset -q --hard origin/main
  git submodule sync -q
  git submodule update -q --init --force works   # из подмодулей сайту нужен только works (страницы-витрины)
fi

[ -f "$SRC/index.html" ] && [ -d "$SRC/works/js" ] || { echo "в $SRC нет index.html или works/ — выкладывать нечего" >&2; exit 1; }

rev="$(git rev-parse HEAD)-$(git -C works rev-parse HEAD)-$(git hash-object "$SRC/deploy/deploy-site.sh")"   # скрипт в версии: правка фильтра выкладывается сама
if [ -z "${FORCE:-}" ] && [ -f "$STATE" ] && [ "$(cat "$STATE")" = "$rev" ]; then
  exit 0
fi

mkdir -p "$WEB"
# Выкладываем только то, что нужно сайту. Картинки, методички и обложки лаб отдаёт бакет, а не сервер.
rsync -a --delete --delete-excluded \
  --include=/index.html --include=/favicon.svg \
  --include=/404.html --include=/robots.txt --include=/sitemap.xml \
  --include=/images/ --include='/images/**' \
  --include=/mira/ --include='/mira/**' \
  --include=/mira-login/ --include='/mira-login/**' \
  --exclude=/works/images/ --exclude=/works/.git --exclude='/works/*.md' \
  --include=/works/ --include='/works/**' \
  --exclude='*' \
  "$SRC"/ "$WEB"/
chmod -R a+rX "$WEB"

echo "$rev" > "$STATE"
echo "выложено: $rev"
