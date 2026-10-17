# Explain the Number

**When:** before you trust, report or act on a number that you measured: a speedup, a
regression, a throughput, a latency or an eval score.

**Rule:**

- Ask "Why is it not double?" Name the resource or code path that limits the result: a core,
  a lock, the disk, the network or the load generator. Take it from a profile or from counters
  during a run, and map it to the source. A guess from reading the code is not a limiter.
- For an eval score, ask the same of the trials: did each run do the task? Does the gap hold
  across trials and models? Does the scenario matter?

**You skipped it when:** a number has no named limiter, or the time saved is larger than the
time the changed part took.

**Not:** [Prove It Works](prove-it-works.md) checks that an output is real. The perf playbook
holds the measuring steps.
