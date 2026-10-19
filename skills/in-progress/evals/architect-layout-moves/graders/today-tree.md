---
type: regex
target: trace
pattern: "## Today[\\s\\S]{0,600}goals\\.js[^0-9]{0,40}\\d{2,3}"
---

The owner saw today's file tree, with the goals route's line count, above the candidates. The skill files hold `## Today` but never `goals.js`, so a file read alone cannot match.
