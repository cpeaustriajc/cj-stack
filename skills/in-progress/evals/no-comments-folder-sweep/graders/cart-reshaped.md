---
type: regex
target: { source: file, path: src/legacy/cart.js }
pattern: 'legacy'
match: not_contains
---

The `legacy` flag that the workaround note excused is gone from `applyDiscount`: the reshape landed.
