---
type: regex
pattern: 'total case \d+.*\n.*total case \d+'
match: not_contains
---

The PR body does not paste the lines of test-output.log. A one-line summary such as "200 passed" is fine.
