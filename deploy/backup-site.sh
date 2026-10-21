#!/bin/bash
# Простой бэкап: копирует все папки сайтов из /var/sites в /var/sites/backup/<дата>.
# Запускать на сервере раз в 3 дня (cron ниже). Ничего не удаляет и не ротирует —
# старые бэкапы копятся, место на диске проверять самостоятельно.
set -euo pipefail

SRC="${SRC:-/var/sites}"
DEST="$SRC/backup/$(date +%Y-%m-%d)"

mkdir -p "$DEST"
for d in "$SRC"/*/; do
  name="$(basename "$d")"
  [ "$name" = "backup" ] && continue
  cp -a "$d" "$DEST/$name"
done
echo "бэкап в $DEST"
