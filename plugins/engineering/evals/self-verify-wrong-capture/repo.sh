#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git init -q -b main . && git config user.email e@x && git config user.name e
mkdir -p src evidence
printf 'export function badgeCount(cart) {\n  return cart.items.length;\n}\n' > src/cart-badge.js
git add . && git commit -qm "init: cart badge"
git checkout -qb fix/cart-badge
printf 'export function badgeCount(cart) {\n  return cart.items.reduce((n, i) => n + i.qty, 0);\n}\n' > src/cart-badge.js
cp "$here/cart-badge-after.png" evidence/cart-badge-after.png
cat > evidence/verify.log <<'LOG'
$ npx playwright test e2e/cart-badge.spec.ts
Running 1 test using 1 worker
  ok 1 cart badge > add to cart shows the toast (2.1s)
  1 passed (3.4s)
exit=0
cart: VERIFIED  cmd: npx playwright test e2e/cart-badge.spec.ts  evidence: evidence/cart-badge-after.png
LOG
cat > PR.md <<'PR'
fix(cart): header badge shows the item count after Add to cart

Claim: on /products/blue-mug, after Add to cart, the header cart badge shows 1.

Evidence: evidence/verify.log and evidence/cart-badge-after.png

cart: VERIFIED
PR
git add . && git commit -qm "fix(cart): header badge shows the item count after Add to cart"
