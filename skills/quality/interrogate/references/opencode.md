# OpenCode adapter

- List what's reachable: `opencode models`. Ids look like `<provider>/<model>`. Pick one model
  per vendor: for example the newest GPT, Gemini and Grok the account can run.
- Probe before use: `opencode run -m <id> --agent plan "reply OK"`. Errors such as "subscription
  is required" or "Reconnect OpenCode Console" mean that provider is unavailable. Tell me the
  fix (`opencode auth login`) and move on to the next model.
- Run a review read-only from the repo root, attaching the bundle:
  `opencode run -m <id> --agent plan -f <bundle.md> "<review prompt>" > <id-slug>.md`
- `plan` is the read-only agent. Never use `--auto`, and never use an agent that can edit.
- Run reviewers in parallel as background commands. Each prints its own output file.
- Pay-per-use providers bill by tokens. A bundle over about 100k tokens is too big; split it
  by area.
