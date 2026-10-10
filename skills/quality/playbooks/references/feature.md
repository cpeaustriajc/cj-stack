# Feature

1. Run `triage`. Settle what done looks like as an observable outcome before any code.
2. Find the spec, the design and the closest existing pattern in the app. Follow them; flag
   any deviation as a question, not a decision.
3. Cut the work into slices that each end in a state you can check in the running app, each
   touching about 2-3 files. Prefer more, smaller slices.
4. Per slice: build it, run its end-to-end check, save the evidence, commit. Never commit
   red.
5. For anything with UI, run `ui-polish` against the design, then `break-it` on the finished
   flow. Fix only what I name.
6. Create or update the feature file for the area.
7. Report each slice's evidence, then offer `/create-pr`.
