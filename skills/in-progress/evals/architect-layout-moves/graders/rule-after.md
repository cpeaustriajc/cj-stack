---
type: regex
target: trace
pattern: "Rule after[\\s\\S]{0,400}?features\\b[\\s\\S]*Rule after[\\s\\S]{0,400}?features\\b"
---

Each of the two candidates showed a "rule after" line that says what goes to the fixture's `features` folder. The skill files hold "Rule after" but never the word `features` near it, so a file read alone cannot match.
