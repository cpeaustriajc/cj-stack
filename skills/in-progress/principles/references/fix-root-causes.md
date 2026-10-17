# Fix Root Causes

**When:** you debug a failure that you reproduced.

**Rule:** Ask "why" until the answer is a wrong decision in the code, not a result of an
earlier one.

- Ask if the state that caused the symptom is legitimate. If the system may be in that state,
  the code that broke on it is the cause: handle the state there. If the state must never
  exist, a check at the break hides the bug: find what made the state.
- If the failure occurs only after a restart, suspect persisted state first: config, caches,
  lock files and serialized state.
- Fix the pattern, not the instance. Search for each place with the same fault and fix all of
  them.
- If a workaround needs a long comment to justify it, fix the code instead.
- If the cause took a deep search, propose the cheap, always-on signal that would show it at
  first look: a log line, an assertion or a metric.

**You skipped it when:** a guard handles a state that must never exist, or sibling files keep
the same bug.

**Not:** [Attack the Premise](attack-the-premise.md) starts after fixes failed. [Prove It
Works](prove-it-works.md) checks the fix.
