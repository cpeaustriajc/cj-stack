# Performance

1. Name the metric a user feels (load time of a page, time to search results, memory after
   an hour) and write the expected claim first, such as "p50 render under 120ms".
2. Measure a baseline the same way you'll measure the fix: same build mode, data, device and
   network. Run at least 5 alternating before/after runs and report the median and range.
   Save the trace or profile.
3. Explain the number: point at where the time or memory goes in the trace before proposing a
   change. No fix without a cause.
4. Try in this order: don't do the work at all, do it less often, do it later, do less of it,
   then do it faster.
5. Make one change at a time and re-measure each one. Keep a change only if it moves the
   metric beyond the run-to-run spread; a smaller difference counts as no difference.
6. Re-run the feature's end-to-end checks. A faster wrong answer is a regression.
7. Report the baseline, the result, the delta and the method, plus the trace paths. Say
   whether the target was met.
