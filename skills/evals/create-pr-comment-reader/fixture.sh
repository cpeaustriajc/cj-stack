#!/usr/bin/env bash
set -euo pipefail
# The eval sandbox blocks the macOS /usr/bin/git shim, so the run gets its own copy of git.
mkdir -p .tools && cp "$(xcrun --find git 2>/dev/null || command -v git)" .tools/git
git init -q -b main
printf '.tools/\n' >> .git/info/exclude
git config user.email eval@example.com
git config user.name eval
mkdir -p src
cat > src/cart.js <<'JS'
export function cartTotal(items) {
  return items.reduce((t, i) => t + i.priceCents * i.qty, 0);
}
JS
git add -A && git commit -qm "cart total"
git checkout -qb claude/cart-discount
cat > src/cart.js <<'JS'
export function cartTotal(items) {
  return items.reduce((t, i) => t + i.priceCents * i.qty, 0);
}

// Apply the discount to the cart total.
// Added for the spring sale ticket SHOP-142, used by the checkout page.
export function discountedTotal(items, percent) {
  // Loop over the items and add up the total.
  const total = cartTotal(items);
  // Round down: the payment provider rejects fractional cents.
  return Math.floor(total * (100 - percent) / 100);
}
JS
git add -A && git commit -qm "discounted cart total"
