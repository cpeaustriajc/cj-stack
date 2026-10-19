---
type: llm
---

The fixture is a library holds service with a `GLOSSARY.md`. The reply under test explains again an earlier message about a holds bug and its fix. It may speak as the one who made the fix.

Pass only if the final reply says, in plain words, that a lapse passes the copy to the next hold in the queue, and that this next hold can lapse too, so it repeats down the queue.
