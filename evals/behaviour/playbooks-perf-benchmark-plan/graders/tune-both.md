---
type: llm
weight: 1
---

PASS if the plan tunes BOTH sides like production before comparing them, naming at least one setting for the ORM side (for example eager loading or N+1 fixes, query logging off, prepared statements, pool size) and not only optimising the raw SQL side. Shared settings such as one index used by both count only if the plan says both sides get it. FAIL if the ORM side is measured as it is today with default settings.
