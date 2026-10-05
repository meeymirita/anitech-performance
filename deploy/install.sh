#!/bin/bash
# Одноразовая установка на сервер (Ubuntu, от root):
#   curl -fsSL https://raw.githubusercontent.com/meeymirita/anitech-performance/main/deploy/install.sh | bash
# Что делает: ставит git и rsync, клонирует репозиторий в /opt/anitech-src, делает копию текущей папки сайта,
# выкладывает свежую версию и включает таймер. Повторный запуск безопасен.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "запустите от root" >&2; exit 1; }

WEB=/var/www/anitech-performance
SRC=/opt/anitech-src
REPO=https://github.com/meeymirita/anitech-performance.git

apt-get install -y -q git rsync >/dev/null

if [ -d "$WEB" ] && [ ! -f /var/lib/anitech-deploy.rev ]; then
  bak="$WEB.bak-$(date +%Y%m%d-%H%M%S)"
  cp -a "$WEB" "$bak" && echo "копия текущего сайта: $bak"
fi

[ -d "$SRC/.git" ] || git clone -q "$REPO" "$SRC"
chmod +x "$SRC/deploy/deploy-site.sh"
FORCE=1 "$SRC/deploy/deploy-site.sh"

cp "$SRC/deploy/anitech-deploy.service" "$SRC/deploy/anitech-deploy.timer" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now anitech-deploy.timer
echo
systemctl list-timers anitech-deploy.timer --no-pager
echo "готово: сайт обновляется сам раз в минуту"
