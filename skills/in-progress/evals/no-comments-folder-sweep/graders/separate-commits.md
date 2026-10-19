---
type: regex
target: { source: file, path: .git/logs/HEAD }
pattern: '\tcommit: [\s\S]*\tcommit: [\s\S]*\tcommit: '
match: contains
---

Comment deletions, the reshape and the suppression removal land as three separate commits.
