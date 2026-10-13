# usage-pace

A mod (a plugin that adds hooks to Claude Code) that shows your weekly usage in the status row. It also tells you if the weekly allowance lasts until the reset.

## Why

A weekly usage limit is easy to burn through by mid-week. A percentage alone does not say if you are early or late. usage-pace compares the percentage with the time left until the reset.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install usage-pace@cj-stack
```

To see that it is on, run `claude plugin list` and look for `usage-pace`. The mod is optional: `cj-stack` does not install it.

## Example

You are four days into a seven-day week and you used 40%. The status row shows this:

```
Week 40% · lasts to Tue 4:00 PM · 20%/day left
```

Later, you have used 81% at the same point. The status row shows this:

```
Week 81% · out ~Sun 2:31 PM · 6%/day left
```

## What it does

| Status row | Meaning |
|---|---|
| `Week 40% · lasts to Tue 4:00 PM · 20%/day left` | At the current rate, the allowance lasts until the reset. |
| `Week 81% · out ~Sun 2:31 PM · 6%/day left` | At the current rate, the allowance ends at the time shown, before the reset. |
| `Week 0% · resets Tue 4:00 PM` | No projection. This also shows at 100% or more, and in the first 12 hours of the week. |
| Nothing | The reset time is missing or in the past, or no weekly reading exists. |

The `%/day left` figure is the unused percentage divided by the days until the reset. The week starts seven days before the reset. The times use the clock of your computer.

The mod reads the usage again every 60 seconds, when a turn changes the rate limits, and when a surface attaches or detaches. The status row shows only when a desktop or phone surface is attached. A terminal-only session shows nothing and reads no usage.

## Settings

No settings. To turn the mod off, run `claude plugin disable usage-pace@cj-stack`.

## Limits

- It shows the seven-day limit only. It ignores the five-hour limit.
- A non-interactive session reads nothing and shows nothing.
- If the read fails, the mod clears the status row. A hook call also throws "usage-pace: could not read weekly usage".
- The projection assumes the rate of the whole week so far continues. It does not use your recent pace.

## More

- [hooks/pace.ts](hooks/pace.ts): the text and the projection.
- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/pace.test.ts](hooks/pace.test.ts) and [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
