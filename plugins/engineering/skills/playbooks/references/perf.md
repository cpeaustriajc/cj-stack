# Performance

These rules also apply to eval scores and any other measured comparison. If the user asks only
for a ballpark, one run is enough: still count errors and work done, and say it is one run.
A choice between options is never a ballpark.

1. Name the metric a user feels (load time of a page, time to search results, memory after
   an hour) and write the expected claim first, such as "p50 render under 120ms".
2. Measure a baseline the same way you'll measure the fix: same build mode, data, device and
   network. Run at least 5 alternating before/after runs and report the median and range.
   Save the trace or profile.
   - Read the measurement script first: what it times, what it counts, what it ignores.
   - Every run records its error count and the work done (requests served, rows written). A
     run with errors or less work is not comparable.
   - Prove that the timed region ran the work: lazy work, unawaited promises and discarded
     results give a time for work that never ran.
   - Record the machine load (`uptime`, core count). On a busy machine, alternate the sides
     and say so.
   - To compare options, tune both sides like production first (release build, pool sizes,
     indexes, warm or cold caches). A side limited by a setting is untuned.
3. Explain the number: point at where the time or memory goes in the trace before proposing a
   change. No fix without a cause (Explain the Number).
4. Try in this order: don't do the work at all, do it less often, do it later, do less of it,
   then do it faster.
5. Make one change at a time and re-measure each one. Keep a change only if it moves the
   metric beyond the run-to-run spread; a smaller difference counts as no difference.
6. Re-run the feature's end-to-end checks. A faster wrong answer is a regression.
7. Lead the report with one verdict: faster, slower, no measurable difference or
   inconclusive. Then give the baseline, the result, the delta, the runs, the error counts and
   the method, plus the trace paths. Say whether the target was met.
