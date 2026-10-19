---
type: regex
target: { source: file, path: src/legacy/format.js }
pattern: 'format the date|no-loose-equal'
match: not_contains
---

The narrating comment and the suppression of the correctness rule `no-loose-equal` are gone from `src/legacy/format.js`.
