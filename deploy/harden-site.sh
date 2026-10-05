#!/bin/bash
# Заголовки безопасности + страница 404 для сайта. Запускать на сервере от root:
#   bash <(curl -fsSL https://raw.githubusercontent.com/meeymirita/anitech-performance/main/deploy/harden-site.sh)
# Создаёт /etc/caddy/anitech-hardening.conf и подключает его в блок сайта (рядом с protect-mira.sh).
# Сначала проверяет конфиг; если Caddy не принял или не перезагрузился — всё возвращается как было.
# Повторный запуск безопасен (файл пересоздаётся, import добавляется один раз).
# CSP не включаем: на страницах инлайн-скрипты и стили.
set -euo pipefail

CADDYFILE="${CADDYFILE:-/etc/caddy/Caddyfile}"
SNIPPET="${SNIPPET:-/etc/caddy/anitech-hardening.conf}"
CADDY_BIN="${CADDY_BIN:-caddy}"
ANCHOR='root * /var/www/anitech-performance'

[ -f "$CADDYFILE" ] || { echo "нет $CADDYFILE" >&2; exit 1; }
grep -qF "$ANCHOR" "$CADDYFILE" || { echo "в Caddyfile не нашёл строку '$ANCHOR' — вставьте вручную" >&2; exit 1; }

backup="$CADDYFILE.bak-$(date +%Y%m%d-%H%M%S)"
cp -a "$CADDYFILE" "$backup"
had_snippet=0; [ -f "$SNIPPET" ] && had_snippet=1 && cp -a "$SNIPPET" "$SNIPPET.prev"

cat > "$SNIPPET" <<'EOF'
# Заголовки безопасности и 404. Создано deploy/harden-site.sh — руками не править, скрипт пересоздаёт файл.
header {
	Strict-Transport-Security "max-age=31536000"
	X-Content-Type-Options "nosniff"
	X-Frame-Options "SAMEORIGIN"
	Referrer-Policy "strict-origin-when-cross-origin"
	Permissions-Policy "camera=(), microphone=(), geolocation=()"
	-Server
}
handle_errors {
	@notfound `{err.status_code} == 404`
	handle @notfound {
		rewrite * /404.html
		file_server
	}
}
EOF
if getent group caddy >/dev/null 2>&1; then chgrp caddy "$SNIPPET"; chmod 640 "$SNIPPET"; else chmod 644 "$SNIPPET"; fi

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

"$CADDY_BIN" validate --config "$CADDYFILE" >/dev/null 2>&1 || { "$CADDY_BIN" validate --config "$CADDYFILE" 2>&1 | tail -5 >&2; rollback "Caddy не принял конфиг"; }

if [ -z "${SKIP_RELOAD:-}" ]; then
  if ! systemctl reload caddy; then
    journalctl -u caddy -n 8 --no-pager >&2 || true
    cp -a "$backup" "$CADDYFILE"
    if [ "$had_snippet" = 1 ]; then mv "$SNIPPET.prev" "$SNIPPET"; else rm -f "$SNIPPET"; fi
    systemctl reload caddy || true
    echo "Caddy не перезагрузился — всё возвращено как было." >&2; exit 1
  fi
fi
rm -f "$SNIPPET.prev"
echo "ГОТОВО: заголовки безопасности и страница 404 включены. Копия прежнего Caddyfile: $backup"
