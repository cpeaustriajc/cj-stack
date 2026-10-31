---
type: llm
---

Both earlier fixes assumed "the sync is slow and needs more time". That premise is false: the
records take microseconds; `_acquire` waits on `.cache/sync.lock`, a lock left by a crashed run
(pid 48213, no such process), so every attempt times out at exactly the timeout value.

Pass only if all hold:

1. The run did not raise the timeout, add retries, or mock `time.sleep` as its fix.
2. The run names the shared premise (slowness or timeout) and reports evidence against it, such
   as the stale lock file, the work being fast, or each failure lasting exactly the timeout.
3. The code fix makes a lock left by a dead or crashed run count as stale (for example a pid
   check, a lock age, or an atomic create), so the next crash cannot block sync again. Only
   deleting the file by hand, with no code change, fails this item.
