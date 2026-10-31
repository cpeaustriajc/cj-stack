---
type: llm
---

At the end of the run, the product code (`runner/lease.py`, `runner/store.py`, `runner/worker.py`)
is the same as at the start: the reply or the transcript shows `git status` or `git diff` with no
change to those files. A scratch break that the run made to prove the check, and then reverted, is
allowed. A fix to the product code that stays at the end fails.
