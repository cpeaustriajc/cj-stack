---
type: llm
focus:
  source: file
  path: src/routes/goals.js
---

This is `src/routes/goals.js` after the run. Before it, the file was about 100 lines of helpers, validation, save logic and screen parts. Pass only if the file now holds only imports or re-exports, the `route` config and `Page` (a re-export of `Page`, or a short `Page` that calls a page from `src/features/`). Fail if any helper, validation, save logic or screen part is still in it.
