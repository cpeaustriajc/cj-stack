---
type: regex
target: { source: file, path: src/legacy/cart.js }
pattern: 'loop over the lines|multiply price|return the rounded|old version|totalOld|HACK|====='
match: not_contains
---

The narration, the banner, the commented-out code and the workaround note are gone from `src/legacy/cart.js`.
