#!/bin/bash
# сохранить и запушить всё по порядку: подмодули → родитель (при ошибке подмодуля родитель НЕ пушится)
cd /Users/mira/Documents/projects/lab-laroboti || exit 1
MSG="${1:-Update}"
TR="Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
for d in $(git submodule status | awk '{print $2}'); do
  if [ -n "$(git -C $d status --short)" ]; then
    git -C $d add -A && git -C $d commit -q -m "$MSG" -m "$TR" || { echo "FAIL commit $d"; exit 1; }
  fi
  # подмодуль может стоять в detached HEAD — пушим HEAD в main
  if [ "$(git -C $d rev-list --count origin/main..HEAD 2>/dev/null)" != 0 ]; then
    git -C $d push -q origin HEAD:main && echo "ok $d" || { echo "FAIL push $d"; exit 1; }
  fi
done
git submodule foreach --quiet 'git fetch -q origin main; b=$(git rev-list --count origin/main..HEAD 2>/dev/null); [ "${b:-0}" != 0 ] && echo "$name ahead $b"; true'
python3 tools/check-site.py | tail -1
# родитель: показать, что уйдёт в коммит, и остановиться на неизвестных (untracked) файлах — их нужно решить вручную (FORCE=1 пропускает проверку)
UNTR=$(git ls-files --others --exclude-standard)
if [ -n "$UNTR" ] && [ "$FORCE" != 1 ]; then echo "STOP: untracked-файлы в родителе:"; echo "$UNTR"; echo "добавьте в .gitignore или запустите FORCE=1 bash tools/save-push.sh ..."; exit 1; fi
git status --short | head -30
git add -A . && git commit -q -m "$MSG" -m "$TR" && git pull -q --rebase origin main && git push -q origin main && git log --oneline -1
# бакет: то же делает GitHub Actions после пуша; локально — только если есть ключи
[ -f ~/.config/anitech/yc.env ] && python3 tools/sync-bucket.py | tail -3
