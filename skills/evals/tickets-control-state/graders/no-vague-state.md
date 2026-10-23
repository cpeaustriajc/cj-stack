---
type: regex
pattern: '## Done When(?:(?!\n## )[\s\S])*?(?:offers no|does nothing|shows no|unavailable|not available|blocked)'
match: not_contains
---

No Done When line describes the button's state with a vague phrase such as "offers nothing".
