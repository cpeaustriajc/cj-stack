# Pick

Read this when the owner replies `Pick A` or `Pick B`. The phases are in `SKILL.md`.

1. Write the picked sketch as real stub files: its types, signatures and module map, with `not implemented` bodies and `// TODO` pseudocode as shown. Change only what the sketch names.
2. Fill the rationale's "Pick decision" section: the picked candidate and its model, why it was picked (the owner's words if they gave a reason, else your recommendation line, marked as yours), the candidate not picked with its tradeoff line, and what was taken from it.
3. The rationale, with the picked shape, its tradeoffs accepted and the alternatives not picked, is the body of the pull request for this work. Open the pull request with it as the body, or put it in the body of the one already open.

A layout pick runs **Pick a layout** in `references/layout.md` instead of these steps.

The picked sketch can ship as its own commit, as the "scaffold first" mode of the **foundational-thinking** principle. Planned and scoped breakage during fill-in is fine, per the **outcome-oriented-execution** principle. For adversarial pressure on the design before implementing, run the **interrogate** skill on the picked sketch.
