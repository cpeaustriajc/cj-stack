---
type: regex
target: { source: file, path: src/legacy/format.js }
pattern: 'prettier-ignore[\s\S]*tc39\.es/ecma262[\s\S]*lint-disable-next-line max-line'
match: contains
---

The `prettier-ignore`, the date-parsing note with its spec link, and the style-only `max-line` suppression stay.
