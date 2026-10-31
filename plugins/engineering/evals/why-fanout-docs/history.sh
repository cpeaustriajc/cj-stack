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
echo "# shop" > README.md
v="$HOME/Vaults/Shop"
mkdir -p "$v"
printf 'Decisions: obsidian: ~/Vaults/Shop\n' > CLAUDE.md
git add . && c 2026-06-01T09:00:00 "docs: readme and decision log pointer (#41)"
cat > "$v/Home.md" <<'MD'
# Shop

The README is the product spec. The decisions record why.

| Page | What it answers |
|---|---|
| [[Decisions]] | every decision, newest first |
| [[Decision 001 Order Worker Queue]] | why the order worker uses one queue |
| [[Mobile App Versions]] | which app versions are live and when old ones retire |
MD
cat > "$v/Decisions.md" <<'MD'
# Decisions

| # | Decision | Status | Date | Issue |
|---|---|---|---|---|
| 001 | [[Decision 001 Order Worker Queue]] | Accepted | 2026-01-08 | none recorded |
MD
cat > "$v/Decision 001 Order Worker Queue.md" <<'MD'
# Decision 001: Order Worker Queue

**Status:** Accepted
**Date:** 2026-01-08 · **Issue:** none recorded

## Context
Orders arrive from web and mobile checkout.

## Decision
One queue, one worker pool, retries with backoff.

## Consequences
A poison message can block the pool until it is dead-lettered.
MD
cat > "$v/Mobile App Versions.md" <<'MD'
# Mobile App Versions

Researched 2026-09-30.

- iOS app 4.x is current. App 3.x still sends about 0.4% of orders (analytics, week of 2026-09-22).
- App 3.x support ends on 2026-11-30. After that date the API rejects its requests with HTTP 426.
- The legacy checkout in 3.x restores a saved cart without an `items` field.
MD
