---
type: llm
---

The fixture is a library holds service with a `GLOSSARY.md`. The reply under test explains again an earlier message about a holds bug and its fix. It may speak as the one who made the fix.

Pass only if both hold:

1. The final reply says that the pickup window is 7 days, and that it starts when a copy is given to a hold, while the copy can still be in transit (on the van).
2. That explanation appears before the paragraph that describes the change to the sweep (the skip for copies in transit).
