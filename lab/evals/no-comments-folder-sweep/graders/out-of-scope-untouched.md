---
type: regex
target: { source: file, path: src/core/money.js }
pattern: 'round half up to whole cents'
match: contains
---

The comment in `src/core/money.js`, outside the folder, stays.
