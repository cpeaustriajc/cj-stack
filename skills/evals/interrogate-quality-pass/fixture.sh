#!/usr/bin/env bash
set -euo pipefail
# The eval sandbox blocks the macOS /usr/bin/git shim, so the run gets its own copy of git.
mkdir -p .tools && cp "$(xcrun --find git 2>/dev/null || command -v git)" .tools/git
git init -q -b main
printf '.tools/\n' >> .git/info/exclude
git config user.email eval@example.com
git config user.name eval
mkdir -p src
cat > src/money.js <<'JS'
export function formatCents(cents) {
  return '$' + (cents / 100).toFixed(2);
}
JS
cat > src/receipt.js <<'JS'
import { formatCents } from './money.js';

export function receiptLine(item) {
  return `${item.name}: ${formatCents(item.priceCents * item.qty)}`;
}
JS
git add -A && git commit -qm "receipt lines"
cat > src/receipt.js <<'JS'
import { formatCents } from './money.js';

export function receiptLine(item) {
  return `${item.name}: ${formatCents(item.priceCents * item.qty)}`;
}

export function receiptTotal(items) {
  let total = 0;
  let count = 0;
  for (const item of items) {
    if (item) {
      if (item.qty) {
        if (item.qty > 0) {
          total = total + item.priceCents * item.qty;
          count = count + 1;
        }
      }
    }
  }
  const dollars = Math.floor(total / 100);
  const cents = String(total % 100).padStart(2, '0');
  return { text: 'Total: $' + dollars + '.' + cents, count: count, lines: count };
}
JS
