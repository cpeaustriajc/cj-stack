---
type: regex
pattern: '(?:[^\s.!?]+[ \t]+){25,}[^\s.!?]+'
match: not_contains
---

No sentence in the reply has more than 25 words (ASD-STE100). A period inside a file name ends the count early, so the check is lenient.
