#!/bin/bash
# сохранить и запушить всё по порядку: подмодули → родитель
cd /Users/mira/Documents/projects/lab-laroboti
MSG="${1:-Update}"
TR="Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
for d in $(git submodule status | awk '{print $2}'); do
  if [ -n "$(git -C $d status --short)" ]; then
    git -C $d add -A && git -C $d commit -q -m "$MSG" -m "$TR" && git -C $d push -q origin main && echo "ok $d" || echo "FAIL $d"
  fi
done
git submodule foreach --quiet 'b=$(git rev-list --count @{u}..HEAD 2>/dev/null); [ "${b:-0}" != 0 ] && echo "$name ahead $b"; true'
python3 tools/check-site.py | tail -1
git add -A . && git commit -q -m "$MSG" -m "$TR" && git pull -q --rebase origin main && git push -q origin main && git log --oneline -1
