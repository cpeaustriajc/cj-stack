#!/usr/bin/env bash
set -euo pipefail
# The eval sandbox blocks the macOS /usr/bin/git shim, so the run gets its own copy of git.
mkdir -p .tools && cp "$(xcrun --find git 2>/dev/null || command -v git)" .tools/git
git init -q -b main
printf '.tools/\n' >> .git/info/exclude
git config user.email eval@example.com
git config user.name eval
mkdir -p src
cat > package.json <<'JSON'
{ "name": "shop", "type": "module", "dependencies": { "@acme/pay": "^3.2.0" } }
JSON
cat > src/checkout.js <<'JS'
export async function checkout(db, order) {
  const totalCents = order.items.reduce((sum, i) => sum + i.priceCents * i.qty, 0);
  await db.save({ ...order, totalCents, status: 'unpaid' });
  return { ok: true, totalCents };
}
JS
git add -A && git commit -qm "checkout saves unpaid orders"
cat > src/checkout.js <<'JS'
import { charge } from '@acme/pay';

export async function checkout(db, order) {
  const totalCents = order.items.reduce((sum, i) => sum + i.priceCents, 0);
  const receipt = await charge(order.customerId, totalCents, { timeoutMs: 5000 });
  await db.save({ ...order, totalCents, status: 'paid', receiptId: receipt.id });
  return { ok: true, totalCents, receiptId: receipt.id };
}
JS
