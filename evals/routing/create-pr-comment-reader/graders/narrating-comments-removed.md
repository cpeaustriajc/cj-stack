---
type: regex
target:
  source: file
  path: src/cart.js
pattern: 'Apply the discount|SHOP-142|Loop over the items'
match: not_contains
---

The three narrating comments in src/cart.js are gone.
