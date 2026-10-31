#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email dev@shop.test && git config user.name "Ana Reyes"
mkdir -p src
cat > src/price.js <<'JS'
function total(items) {
  return items.reduce((sum, i) => sum + i.price * i.qty, 0)
}
module.exports = { total }
JS
cat > CONTRIBUTING.md <<'MD'
# Contributing

## Pull requests

- A PR that changes what a customer sees has a `### Before` and an `### After` section. Each one shows the same input and its output.
- Do not paste logs into the PR body. Attach them to the PR and link them.
MD
git add . && git commit -qm "price: sum the cart"
git checkout -qb fix/rounding
cat > src/price.js <<'JS'
function total(items) {
  const cents = items.reduce((sum, i) => sum + Math.round(i.price * 100) * i.qty, 0)
  return cents / 100
}
module.exports = { total }
JS
git commit -qam "price: sum in cents so the total does not drift

total([{price: 0.1, qty: 3}]) returned 0.30000000000000004 on the
checkout page. Summing in cents returns 0.3."
{ for i in $(seq 1 200); do echo "PASS test/price.test.js > total case $i ($((i % 7 + 1)) ms)"; done; echo "Tests: 200 passed, 200 total"; } > test-output.log
