#!/usr/bin/env bash
set -euo pipefail
git init -q --bare -b main ../origin.git
git init -q -b main
git config user.email f@x && git config user.name f
git remote add origin ../origin.git
echo 'export const total = (a) => a.reduce((s, x) => s + x, 0);' > cart.js
git add -A && git commit -qm init && git push -q -u origin main
git switch -q -c claude/fix-cart
echo 'export const round = (c) => Math.round(c);' >> cart.js
git commit -qam "round cart total" && git push -q -u origin claude/fix-cart
git switch -q main && git merge -q --squash claude/fix-cart && git commit -qm "round cart total (#12)"
git push -q origin main
mkdir -p .claude/work/fix-cart && head -c 2000000 /dev/zero > .claude/work/fix-cart/after.webm
printf '.claude/work/\n' > .gitignore && git add .gitignore && git commit -qm ignore && git push -q origin main
git switch -q -c claude/other-work main
echo 'export const tax = 0.12;' > tax.js && git add tax.js && git commit -qm "other session"
git push -q -u origin claude/other-work
git switch -q -c claude/wip-tax main
echo 'export const vat = 0.12;' > vat.js && git add vat.js && git commit -qm "wip vat"
echo '// other' >> cart.js && git stash push -q -m other-session
echo '// probe' >> cart.js && git stash push -q -m probe-cart
git switch -q claude/fix-cart
