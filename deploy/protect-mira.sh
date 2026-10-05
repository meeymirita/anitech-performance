#!/bin/bash
# Ставит пароль (HTTP basic auth) на страницу /mira/ в Caddy. Запускать на сервере от root:
#   bash <(curl -fsSL https://raw.githubusercontent.com/meeymirita/anitech-performance/main/deploy/protect-mira.sh)
# Пароль спрашивается при запуске и в репозиторий/историю не попадает; в Caddy лежит только его хеш (bcrypt).
# Логин: mira. Повторный запуск = смена пароля. Если Caddy не принимает конфиг, всё откатывается.
set -euo pipefail

CADDYFILE="${CADDYFILE:-/etc/caddy/Caddyfile}"
SNIPPET="${SNIPPET:-/etc/caddy/mira-auth.conf}"
ANCHOR='root * /var/www/anitech-performance'
USER_NAME=mira

[ -f "$CADDYFILE" ] || { echo "нет $CADDYFILE" >&2; exit 1; }
grep -qF "$ANCHOR" "$CADDYFILE" || { echo "в Caddyfile не нашёл строку '$ANCHOR' — вставьте защиту вручную" >&2; exit 1; }

read -r -s -p "Новый пароль для /mira/: " p1 < /dev/tty; echo
read -r -s -p "Повторите пароль: " p2 < /dev/tty; echo
[ -n "$p1" ] && [ "$p1" = "$p2" ] || { echo "пароли пустые или не совпали" >&2; exit 1; }

if [ -n "${SKIP_CADDY:-}" ]; then hash='$2a$14$FAKEHASHFORTESTONLYxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
else hash="$(caddy hash-password --plaintext "$p1")"; fi
unset p1 p2

write_snippet() {  # $1 = имя директивы: basic_auth (Caddy 2.8+) или basicauth (старые версии)
  cat > "$SNIPPET" <<EOF
@mira path /mira /mira/*
$1 @mira {
	$USER_NAME $hash
}
EOF
  chmod 640 "$SNIPPET"
}

backup="$CADDYFILE.bak-$(date +%Y%m%d-%H%M%S)"
cp -a "$CADDYFILE" "$backup"
had_snippet=0; [ -f "$SNIPPET" ] && had_snippet=1 && cp -a "$SNIPPET" "$SNIPPET.prev"

# подключаем сниппет в блок anitech сразу после строки root (один раз)
if ! grep -qF "import $SNIPPET" "$CADDYFILE"; then
  python3 - "$CADDYFILE" "$ANCHOR" "$SNIPPET" <<'PY'
import sys
path, anchor, snippet = sys.argv[1:4]
out = []
for line in open(path):
    out.append(line)
    if anchor in line:
        indent = line[:len(line) - len(line.lstrip())]
        out.append(f"{indent}import {snippet}\n")
open(path, "w").write("".join(out))
PY
fi

rollback() {
  cp -a "$backup" "$CADDYFILE"
  if [ "$had_snippet" = 1 ]; then mv "$SNIPPET.prev" "$SNIPPET"; else rm -f "$SNIPPET"; fi
  echo "Caddy не принял конфиг — всё возвращено как было." >&2; exit 1
}

if [ -n "${SKIP_CADDY:-}" ]; then write_snippet basic_auth; echo "тест: Caddyfile и сниппет записаны"; exit 0; fi

write_snippet basic_auth
if ! caddy validate --config "$CADDYFILE" >/dev/null 2>&1; then
  write_snippet basicauth
  caddy validate --config "$CADDYFILE" >/dev/null 2>&1 || { caddy validate --config "$CADDYFILE" 2>&1 | tail -5 >&2; rollback; }
fi
systemctl reload caddy
rm -f "$SNIPPET.prev"
echo "ГОТОВО: /mira/ закрыта паролем (логин: $USER_NAME). Копия прежнего Caddyfile: $backup"
