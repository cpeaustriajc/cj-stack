# work-folder

A mod (a plugin that adds a hook to Claude Code) that denies a new agent working file outside `.claude/work/`. Plans, evidence, prototypes and reports then stay out of your repo. At session start it also removes old entries from `.claude/work/`.

## Why

Agents write plans, scratch notes, reports and probe tests into the repo as they work. These files end up in commits.

work-folder denies the write and tells Claude to use `.claude/work/<topic>/` instead. That folder is gitignored. Nobody deletes its folders afterwards, and probe runs can fill them with gigabytes, so work-folder removes each entry that has not changed for a day.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install work-folder@cj-stack
```

To see that it is on, run `claude plugin list` and look for `work-folder`. The mod is optional: `cj-stack` does not install it.

## Example

1. Claude tries to create `reports/x.md` with the Write tool.
2. The hook finds that the file does not exist and that `reports/` is a planning folder.
3. The hook denies the write. Claude reads: "work-folder: reports/x.md looks like an agent working file (a reports/ or docs/ planning folder). Write it under .claude/work/<topic>/ instead; that folder is gitignored."
4. Claude writes the file under `.claude/work/` instead.

If you keep such files in the repo on purpose, add them to the allow list below.

## What it does

The hook checks the Write and NotebookEdit tools. It judges the path from the nearest folder that holds a `.git` entry.

| Event | Decision |
|---|---|
| A new file matches a deny pattern | Deny, and name the pattern and the fix. |
| A new file matches an allow entry | Pass. |
| The file already exists | Pass. |
| The path is under a tool folder such as `.claude/` or `.github/` | Pass. |
| The path is outside any git repo | Pass. |
| The allow file is not valid | Deny, and name the file and the fix. |
| The file system check fails on a path that could match | Deny with "could not check". |

The deny patterns are:

| Pattern | Example |
|---|---|
| Prototype, scratch, recovery, spike or `.local` folders | `prototypes/x/index.html` |
| `reports/` and planning folders under `docs/` | `docs/plans/x.md` |
| Test artifact and evidence folders | `.e2e-evidence/run.sh` |
| A loose `.md`, `.html` or `.txt` file at the repo root | `validate.html` |
| Findings, report, plan or numbered evidence file names | `107-EVIDENCE.md` |
| Probe and temporary test file names | `zz-probe-load.spec.ts` |

Root files such as `README.md` and `CLAUDE.md` pass. The full lists are in [hooks/register.ts](hooks/register.ts).

### Cleanup at session start

At session start, the hook finds the repo root from the session folder and lists `.claude/work/`. It judges each entry there (a topic folder or a loose file) by the newest file in it.

| Entry | Decision |
|---|---|
| No file in it changed for `keepDays` days | Remove it with `git clean -ffdX`, and show a toast that names it. |
| One file in it changed in the last `keepDays` days | Keep the whole entry. |
| A file in it is tracked by git | Keep that file: `git clean -X` removes only ignored files. |
| `keepDays` is 0 | Do nothing. |
| `keepDays` is not valid | Do nothing, and show a toast that names the file and the fix. |
| `git clean` fails | The session starts. The debug log names the failed hook. |

### The allow list

To keep a file in the repo, create `.claude/work-folder.json` at the repo root:

```
{ "allow": ["path/prefix/", "glob/**/*.md"] }
```

An entry that ends with `/` is a path prefix. Any other entry is a glob.

## Settings

`keepDays` in `.claude/work-folder.json`: the days without a change before the cleanup removes an entry. The default is `1`; `0` turns the cleanup off. Example: `{ "allow": [], "keepDays": 7 }` keeps evidence for a week of review.

To turn the mod off, run `claude plugin disable work-folder@cj-stack`.

## Limits

- It checks only the Write and NotebookEdit tools. Edit, and a shell command that writes a file, pass.
- It does not add `.claude/work/` to `.gitignore`. If git does not ignore that folder, the cleanup removes nothing.
- The cleanup runs only in the repo of the session folder; a worktree's `.claude/work/` is cleaned by a session there.
- A removed entry does not go to the trash. To keep an old entry, touch a file in it or raise `keepDays`.
- The file name patterns are a fixed list. A working file with another name passes.
- If the file system check fails on a path that could match, the hook denies. Write under `.claude/work/` or retry.

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts) and [hooks/cleanup.test.ts](hooks/cleanup.test.ts): the tests.
- [marketplace.json](../../.claude-plugin/marketplace.json): the manifest, in this mod's entry.
