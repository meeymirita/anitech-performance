#!/bin/bash
# Закрывает страницу /mira/ паролем через красивую форму входа (/mira-login/). Запускать на сервере от root:
#   bash <(curl -fsSL https://raw.githubusercontent.com/meeymirita/anitech-performance/main/deploy/protect-mira.sh)
# Пароль спрашивается при запуске и в репозиторий не попадает: в Caddy лежит только его хеш (bcrypt)
# и случайный ключ сессии. Повторный запуск = смена пароля (и выход со всех устройств).
# Если Caddy не принимает конфиг или не перезагружается, всё откатывается.
set -euo pipefail

CADDYFILE="${CADDYFILE:-/etc/caddy/Caddyfile}"
SNIPPET="${SNIPPET:-/etc/caddy/mira-auth.conf}"
CADDY_BIN="${CADDY_BIN:-caddy}"
ANCHOR='root * /var/www/anitech-performance'
USER_NAME=mira

[ -f "$CADDYFILE" ] || { echo "нет $CADDYFILE" >&2; exit 1; }
grep -qF "$ANCHOR" "$CADDYFILE" || { echo "в Caddyfile не нашёл строку '$ANCHOR' — вставьте защиту вручную" >&2; exit 1; }

read -r -s -p "Новый пароль для /mira/ (печатайте на английской раскладке): " p1 < /dev/tty; echo
read -r -s -p "Повторите пароль: " p2 < /dev/tty; echo
[ -n "$p1" ] && [ "$p1" = "$p2" ] || { echo "пароли пустые или не совпали" >&2; exit 1; }
[ "${#p1}" -le 72 ] || { echo "пароль длиннее 72 символов — bcrypt столько не принимает" >&2; exit 1; }

hash="$("$CADDY_BIN" hash-password --plaintext "$p1")"
token="$(openssl rand -hex 32)"
unset p1 p2

write_snippet() {  # $1 = директива: basic_auth (Caddy 2.8+) или basicauth (старые версии)
  cat > "$SNIPPET" <<EOF
# Вход на /mira/ через форму /mira-login/. Создано deploy/protect-mira.sh — руками не править, скрипт пересоздаёт файл.
route /mira-api/login {
	header Cache-Control "no-store"
	$1 {
		$USER_NAME $hash
	}
	header Set-Cookie "mira_session=$token; Path=/; Max-Age=2592000; HttpOnly; Secure; SameSite=Strict"
	respond 204
}
route /mira-api/logout {
	header Cache-Control "no-store"
	header Set-Cookie "mira_session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict"
	redir * /mira-login/ 302
}
# неудачный вход: убираем WWW-Authenticate, иначе браузер покажет своё окошко вместо нашей формы
handle_errors {
	@login_fail path /mira-api/login
	header @login_fail -WWW-Authenticate
	respond @login_fail "unauthorized" 401
}
@mira_in path /mira /mira/*
handle @mira_in {
	@no_session not header_regexp Cookie (^|;\s*)mira_session=$token(;|\$)
	redir @no_session /mira-login/ 302
	header Cache-Control "no-store"
	file_server
}
EOF
  # Caddy работает под пользователем caddy: файл должен читаться им (проверка от root этого не покажет)
  if getent group caddy >/dev/null 2>&1; then chgrp caddy "$SNIPPET"; chmod 640 "$SNIPPET"; else chmod 644 "$SNIPPET"; fi
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
  echo "$1 — всё возвращено как было." >&2; exit 1
}

write_snippet basic_auth
if ! "$CADDY_BIN" validate --config "$CADDYFILE" >/dev/null 2>&1; then
  write_snippet basicauth
  "$CADDY_BIN" validate --config "$CADDYFILE" >/dev/null 2>&1 || { "$CADDY_BIN" validate --config "$CADDYFILE" 2>&1 | tail -5 >&2; rollback "Caddy не принял конфиг"; }
fi

if [ -z "${SKIP_RELOAD:-}" ]; then
  if ! systemctl reload caddy; then
    journalctl -u caddy -n 8 --no-pager >&2 || true
    cp -a "$backup" "$CADDYFILE"
    if [ "$had_snippet" = 1 ]; then mv "$SNIPPET.prev" "$SNIPPET"; else rm -f "$SNIPPET"; fi
    systemctl reload caddy || true
    echo "Caddy не перезагрузился с защитой — всё возвращено как было." >&2; exit 1
  fi
fi
rm -f "$SNIPPET.prev"
echo "ГОТОВО: /mira/ закрыта паролем через форму входа (логин: $USER_NAME). Копия прежнего Caddyfile: $backup"
