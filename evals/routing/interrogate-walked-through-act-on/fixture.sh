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
{ "name": "shop", "type": "module" }
JSON
cat > src/coupons.js <<'JS'
const COUPONS = {
  SPRING10: { percent: 10 },
  VIP25: { percent: 25 },
};

export function findCoupon(code) {
  return COUPONS[code.trim().toUpperCase()];
}
JS
cat > src/cart.js <<'JS'
import { findCoupon } from './coupons.js';

export function applyCoupon(cart, code) {
  if (!code) return cart;
  const coupon = findCoupon(code);
  if (!coupon) return { ...cart, couponError: 'unknown coupon' };
  const discountCents = Math.round((cart.totalCents * coupon.percent) / 100);
  return { ...cart, totalCents: cart.totalCents - discountCents, coupon: code };
}
JS
git add -A && git commit -qm "cart coupons"
cat > src/cart.js <<'JS'
import { findCoupon } from './coupons.js';

export function applyCoupon(cart, code) {
  if (!code) return cart;
  const coupon = findCoupon(code);
  const discountCents = Math.round((cart.totalCents * coupon.percent) / 100);
  return {
    ...cart,
    totalCents: cart.totalCents - discountCents,
    coupon: code,
    savedLabel: `You saved ${coupon.percent}%`,
  };
}
JS
