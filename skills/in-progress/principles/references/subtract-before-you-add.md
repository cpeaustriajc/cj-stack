# Subtract Before You Add

**When:** you plan an addition, a refactor or a rewrite.

**Rule:** Remove first, then build.

- Delete dead code, unused validators, stub references and duplicate instructions in the area
  before you add to it.
- Leave the design a little simpler, with the same or a smaller surface.
- Add no validator, parser or guard that the spec or an observed use does not need.

**You skipped it when:** the new code works around dead code, or the diff only adds lines
while the touched files held lines that it could remove.

**Not:** [Laziness Protocol](laziness-protocol.md) keeps the new change small. [Minimize
Reader Load](minimize-reader-load.md) measures the result for the next reader.
