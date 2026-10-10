# Local model adapter

Any OpenAI-compatible server works: llama.cpp `llama-server`, Ollama or LM Studio.

- Find a running one: `curl -s localhost:<port>/v1/models` (llama.cpp's default port is 8080,
  Ollama's 11434, LM Studio's 1234).
- If none is running and llama.cpp is installed, start a coding model in the background and
  wait for `/health` to report ok:
  `llama-server -hf <hf-repo>:<quant> --port 8089 -c 32768 --jinja`. Pick a size that fits in
  about half the machine's RAM, such as a 14B model at Q4 on 32 GB.
- Name the model with `--alias <id>` so clients can address it.
- **Through OpenCode** (preferred when it's installed, since the review then runs the same way
  as a hosted vendor's): add the server as a provider in `~/.config/opencode/opencode.jsonc`,
  then use `llama.cpp/<id>` with the steps in `opencode.md`:
  ```jsonc
  "provider": { "llama.cpp": {
    "npm": "@ai-sdk/openai-compatible", "name": "llama-server (local)",
    "options": { "baseURL": "http://127.0.0.1:8089/v1" },
    "models": { "<id>": { "name": "<label>", "limit": { "context": 65536, "output": 16384 } } } } }
  ```
- **Without OpenCode**, send the bundle as the user message:
  ```bash
  jq -n --rawfile b bundle.md --arg p "<review prompt>" \
    '{messages:[{role:"user",content:($p+"\n\n"+$b)}],temperature:0.2}' |
  curl -s localhost:8089/v1/chat/completions -H 'content-type: application/json' -d @- |
  jq -r '.choices[0].message.content' > local-review.md
  ```
- A local 7-14B model is not a real second opinion. Qwen2.5-Coder-14B answered "no findings"
  on a diff with two obvious bugs that Claude caught, even when told to walk each line against
  the intent. Count it as a reviewer only if it finds something you can verify. Never let its
  silence count as agreement. Qwen3-Coder-30B-A3B (Q4, about 19 GB, 32k context with `-ctk q8_0 -ctv q8_0
  -fa on`) found both bugs, citing the correct lines, in about 4 minutes on an M4 with 32 GB, so
  use a model at least that strong. Its context limit is the `-c` value. Trim the bundle to the
  changed hunks plus the surrounding functions if it doesn't fit.
- Stop the server when the review is done, unless I started it myself.
