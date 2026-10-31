---
type: regex
pattern: '^#{2,4}\s*Before\b[\s\S]*^#{2,4}\s*After\b'
flags: im
match: contains
---

The PR body has a Before section and then an After section, as CONTRIBUTING.md asks for a change that a customer sees.
