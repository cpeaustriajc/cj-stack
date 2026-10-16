# Feature

The feature request is the go for every step below. A step ends in a question only for a fact
no tool can find, or a call of taste or business.

1. Run `grill`. Settle what done looks like as an observable outcome before any code.
2. Find the spec, the design and the closest existing pattern in the app. Follow them. Where the
   spec is silent, use the closest existing pattern and name it in the PR. Ask only when the spec
   and a recorded decision conflict. For UI with no approved design, run the prototype playbook
   first, so I see the look before the build.
3. Cut the work into slices that each end in a state you can check in the running app, each
   touching about 2-3 files. Prefer more, smaller slices.
4. Per slice: build it, run its end-to-end check, save the evidence, commit. Never commit
   red. Take each expected value in a check from the spec, a literal or a worked example,
   never by computing it the way the code does: such a check cannot fail.
5. For anything with UI, run `ui-polish` against the design, then `break-it` on the finished
   flow. Fix every row, then run them again until clean.
6. Create or update the feature file for the area.
7. Push, open the PR with each slice's evidence, and stop the servers, containers and tunnels
   you started. Then report. Merge and deploy follow the project's rule.
