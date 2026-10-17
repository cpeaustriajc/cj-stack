---
type: llm
---

The fixture saves a note in this order: `web/editor.js` debounces edits and sends a PUT with `if-match`; `src/http/router.js` `route` calls `requireUser`, then `src/notes/save.js` `saveNote` runs `validate` (422), checks the owner (403) and the version (409), writes through `src/store/notes-store.js` `put` (a temp file, then a rename), calls `enqueueIndex` and publishes `note.saved` through `src/events/bus.js`; `worker/index-worker.js` polls the queue file and reindexes.

Pass only if all hold:

1. The final reply has the headings Overview, Key Concepts, How It Works and Where Things Live, in that order. A Gotchas heading may follow.
2. How It Works is split into numbered stages that name the files and functions above, and at least the editor, validate, version-check, store and worker steps.
3. The reply shows the stages either as a stepper widget or, without one, as a numbered list plus a mermaid flowchart.
