# Claude Code

- The ask tool is `AskUserQuestion`.
- A layout or look option is a mockup in a visualize widget: one card per option, with a
  `sendPrompt` button on each. Without the visualize tools, the option's `preview` holds an
  ASCII sketch.
- The ignored work folder is `.claude/work/<topic>/`.
- A diagram is an inline widget: call `mcp__visualize__read_me` once, then
  `mcp__visualize__show_widget`. Each node gets a `sendPrompt`, so a click asks about it.
  Without the visualize tools (terminal, headless evals), print a mermaid block.
