#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email dev@shop.test && git config user.name "Ana Reyes"
mkdir -p src
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -qam "$2"; }
cat > src/order.js <<'JS'
function parseOrder(order) {
  return order.items.map((i) => ({ sku: i.sku, qty: Number(i.qty) }));
}
module.exports = { parseOrder };
JS
git add . && c 2026-01-10T10:00:00 "orders: parse order payload (#14)"
cat > src/order.js <<'JS'
function parseOrder(order) {
  if (!order.items) return [];
  return order.items.map((i) => ({ sku: i.sku, qty: Number(i.qty) }));
}
module.exports = { parseOrder };
JS
c 2026-03-02T16:40:00 "fix: guard null items from legacy checkout (#31)

INC-42: the legacy iOS checkout (app 3.x) sends orders with no items
field while a cart is restored. parseOrder threw, the order worker
crashed in a loop and 1,900 orders were stuck for 40 minutes.
Keep this guard until app 3.x is retired."
cat > src/order.js <<'JS'
function parseOrder(order) {
  if (!order.items) {
    return [];
  }
  return order.items.map((item) => ({ sku: item.sku, qty: Number(item.qty) }));
}

module.exports = { parseOrder };
JS
c 2026-05-20T09:00:00 "style: run prettier on src (#40)"
echo "# shop" > README.md && git add . && c 2026-06-01T09:00:00 "docs: readme (#41)"
