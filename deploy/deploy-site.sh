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
  git submodule update -q --init --force works site-private   # из подмодулей сайту нужны works (страницы-витрины) и site-private (mira, mira-login, 404)
fi

[ -f "$SRC/index.html" ] && [ -d "$SRC/works/js" ] && [ -f "$SRC/site-private/404.html" ] || { echo "в $SRC нет index.html, works/ или site-private/ — выкладывать нечего" >&2; exit 1; }

rev="$(git rev-parse HEAD)-$(git -C works rev-parse HEAD)-$(git -C site-private rev-parse HEAD)-$(git hash-object "$SRC/deploy/deploy-site.sh")"   # скрипт в версии: правка фильтра выкладывается сама
if [ -z "${FORCE:-}" ] && [ -f "$STATE" ] && [ "$(cat "$STATE")" = "$rev" ]; then
  exit 0
fi

mkdir -p "$WEB"
# Собираем готовое дерево в STAGE: файлы сайта + служебные страницы из site-private, потом одним rsync --delete в WEB (без мерцания /mira/).
STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT
# Картинки, методички и обложки лаб отдаёт бакет, а не сервер.
rsync -a \
  --include=/index.html --include=/favicon.svg \
  --include=/robots.txt --include=/sitemap.xml \
  --include=/images/ --include='/images/**' \
  --exclude=/works/images/ --exclude=/works/.git --exclude='/works/*.md' \
  --include=/works/ --include='/works/**' \
  --exclude='*' \
  "$SRC"/ "$STAGE"/
cp -R "$SRC/site-private/mira" "$SRC/site-private/mira-login" "$STAGE"/
cp "$SRC/site-private/404.html" "$STAGE"/
rsync -a --delete "$STAGE"/ "$WEB"/
chmod -R a+rX "$WEB"

echo "$rev" > "$STATE"
echo "выложено: $rev"
