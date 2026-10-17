# Claude Code adapter

## Two design sketches (`design.md` step 3)

- Send two `Agent` calls in one message, each with `model: "sonnet"` and `effort: "medium"`.
- Give each the same brief: the criteria, the call sites, the files to read, and "read only:
  edit no file, return the sketch in your final reply".
- Do not tell either agent that the other exists, and do not pass one sketch to the other.
- Read both results in the main session. The main session scores, picks and grafts.
