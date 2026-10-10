# Models

Which model does what in this stack, from my Claude Code transcripts (July–October 2026), T3 Code
delegations and Codex reviews on GitHub. Re-check when a new model ships; the picks below are
dated by the models they name.

## Who does what

```
            implement            review                 scout / research
 workday    GPT-6 luna (T3)  ──▶ Codex · GPT-6.1 sol ──▶ fix ──▶ merge
            Opus 5.5 (main)      on every PR
 personal   Opus 5.5 (main)  ──▶ interrogate: fresh Claude reviewers (no GPT sub)
 any day    builder: Haiku 5.5 → Sonnet 5.5 → Opus 5.5 after failed reviews
            researcher: Sonnet 5.5 · Explore: Haiku 5.5 · Fable: hardest calls only
```

| Model | Where I lean on it | Evidence |
|---|---|---|
| Opus 5 → 5.5 | the main session, nearly always | ~71k of ~85k main-session turns; Opus 5.5 took over in September |
| Fable 5 / 5.1 | switched to for the hardest work, never as a subagent | ~9.5k turns; 19 of the named `/model` switches |
| Sonnet 5.5 | subagents: research, browser runs, builder retries | "use sonnet 5.5, it's new, more intelligent and faster" (Sept 29) |
| Haiku 5.5 | swarms, scouts, builder default | "Make sure the swarms are haiku 5.5 trust in that model" (Oct 10); 5.9k turns in October alone |
| GPT-6 luna | bulk implementation through T3 Code, the only GPT model on fast mode | 116 of 194 T3 delegations |
| GPT-6 / 6.1 sol | the reviewer, at high effort; some implementation | 14 review delegations, 36 builds |
| GPT-6 astra | not used for routine work; no fast mode | "no fast mode on gpt 6 or 6.1 sol, especially astra" |

## Cross-vendor review is the one constant

On workdays every PR gets a Codex review, because sol catches what Opus misses. Of the last 60
PRs in marketplace-strangedomains, 39 got a Codex review. 38 were written by Claude (one by T3), and all
39 had at least one finding: 162 findings in total, with 32 on #401 alone.

The catch: it needs a GPT subscription, which I have only at work. On personal projects, review
falls back to `interrogate` with fresh Claude reviewers.

## Picks

| Task | Model |
|---|---|
| Plan, spec, decide | Opus 5.5 (main session); Fable when Opus stalls |
| Mechanical or well-specced code | Haiku 5.5 builder, or GPT-6 luna on workdays |
| Code that needs design calls | Sonnet 5.5 or Opus 5.5 builder |
| Find files and call sites | Haiku 5.5 (Explore) |
| Read the web and weigh sources | Sonnet 5.5 (researcher) |
| Final PR review | GPT-6.1 sol on workdays; Claude-only `interrogate` otherwise |
