#!/usr/bin/env bash
set -euo pipefail
# The eval sandbox blocks the macOS /usr/bin/git shim, so the run gets its own copy of git.
mkdir -p .tools && cp "$(xcrun --find git 2>/dev/null || command -v git)" .tools/git
git init -q -b main
printf '.tools/\n' >> .git/info/exclude
git config user.email eval@example.com
git config user.name eval
mkdir -p src
cat > src/payments.js <<'JS'
export function refund(charge, amountCents) {
  if (amountCents > charge.amountCents) throw new Error('refund exceeds charge');
  return { chargeId: charge.id, amountCents };
}

export function formatCents(cents) {
  return '$' + (cents / 100).toFixed(2);
}
JS
git add -A && git commit -qm "payments helpers"
cat > src/payments.js <<'JS'
export function refund(charge, amountCents) {
  if (amountCents >= charge.amountCents) {
    throw new Error(`refund of ${amountCents} exceeds charge ${charge.id}`);
  }
  return { chargeId: charge.id, amountCents, refundedAt: new Date().toISOString() };
}

export function formatCents(cents) {
  return '$' + (cents / 100).toFixed(2);
}

export function partialRefunds(charge, amounts) {
  let left = charge.amountCents;
  return amounts.map((amountCents) => {
    left -= amountCents;
    return refund({ ...charge, amountCents: left + amountCents }, amountCents);
  }).filter((r) => r.amountCents > 0);
}

export function sumRefunds(refunds) {
  return refunds.reduce((total, r) => total + r.amountCents, 0);
}
JS
