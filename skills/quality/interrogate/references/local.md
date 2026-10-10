# Local model adapter

Any OpenAI-compatible server works: llama.cpp `llama-server`, Ollama or LM Studio.

- Find a running one: `curl -s localhost:<port>/v1/models` (llama.cpp's default port is 8080,
  Ollama's 11434, LM Studio's 1234).
- If none is running and llama.cpp is installed, start a coding model in the background and
  wait for `/health` to report ok:
  `llama-server -hf <hf-repo>:<quant> --port 8089 -c 32768 --jinja`. Pick a size that fits in
  about half the machine's RAM, such as a 14B model at Q4 on 32 GB.
- Review, sending the bundle as the user message:
  ```bash
  jq -n --rawfile b bundle.md --arg p "<review prompt>" \
    '{messages:[{role:"user",content:($p+"\n\n"+$b)}],temperature:0.2}' |
  curl -s localhost:8089/v1/chat/completions -H 'content-type: application/json' -d @- |
  jq -r '.choices[0].message.content' > local-review.md
  ```
- A local 7-14B model is not a real second opinion. Qwen2.5-Coder-14B answered "no findings"
  on a diff with two obvious bugs that Claude caught, even when told to walk each line against
  the intent. Count it as a reviewer only if it finds something you can verify. Never let its
  silence count as agreement. Prefer an OpenCode vendor, or a local model of 30B or more if the
  machine can hold one. Its context limit is the `-c` value. Trim the bundle to the
  changed hunks plus the surrounding functions if it doesn't fit.
- Stop the server when the review is done, unless I started it myself.
