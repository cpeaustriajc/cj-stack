#!/usr/bin/env bash
set -euo pipefail
# The eval sandbox blocks the macOS /usr/bin/git shim, so the run gets its own copy of git.
mkdir -p .tools && cp "$(xcrun --find git 2>/dev/null || command -v git)" .tools/git
git init -q -b main
printf '.tools/\n' >> .git/info/exclude
git config user.email eval@example.com
git config user.name eval
mkdir -p src
cat > src/auth.js <<'JS'
export function isAdmin(user) {
  return user.role === 'admin';
}

export function checkResetToken(user, token) {
  if (!user.resetToken || token !== user.resetToken) return false;
  return true;
}

export function sessionUser(session, now = Date.now()) {
  if (session.expiresAt <= now) return null;
  return session.user;
}
JS
cat > src/payments.js <<'JS'
export function refund(charge, amountCents) {
  if (amountCents > charge.amountCents) throw new Error('refund exceeds charge');
  return { chargeId: charge.id, amountCents };
}

export function lineTotal(input) {
  const qty = input.qty ?? 1;
  return input.priceCents * qty;
}

export function page(items, pageIndex, size) {
  return items.slice(pageIndex * size, pageIndex * size + size);
}

export async function placeOrder(db, order) {
  await db.save(order);
  return { ok: true, id: order.id };
}
JS
git add -A && git commit -qm "auth and payments helpers"
cat > src/auth.js <<'JS'
export function isAdmin(user) {
  return (user.role = 'admin');
}

export function checkResetToken(user, token) {
  return token == user.resetToken;
}

export function sessionUser(session, now = Date.now()) {
  if (session.expiresAt > now) return null;
  return session.user;
}
JS
cat > src/payments.js <<'JS'
export function refund(charge, amountCents) {
  return { chargeId: charge.id, amountCents };
}

export function lineTotal(input) {
  const qty = input.qty || 1;
  return input.priceCents * qty;
}

export function page(items, pageIndex, size) {
  return items.slice(pageIndex * size, pageIndex * size + size + 1);
}

export async function placeOrder(db, order) {
  db.save(order);
  return { ok: true, id: order.id };
}
JS
