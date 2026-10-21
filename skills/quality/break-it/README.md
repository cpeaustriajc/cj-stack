# break-it

A skill that drives your running app or a design prototype as a careless, impatient or confused user with worst-case data. It hands back ranked bugs with repro steps and video.

## When to use it

Use it after you change a user flow, such as a form, a checkout or a multi-step flow, and before review. It finds what breaks before QA or a customer does.

Say "break it", "monkey test", "bug bash", "dogfood" or "QA this like a user".

- For visual sign-off against a design, use `ui-polish`.
- For a security or logic review of a diff, use `interrogate`.
- To fix a known bug, use `playbooks`.

## Example

You say: "Try to break the signup flow like a careless user before I send it to review."

1. Claude checks that the URL is not production and reads the feature file for that area, if one exists.
2. Claude picks two to four user types and says why. It drives the app as each one.
3. Claude writes a report folder and a short summary in chat.

You get three groups: Broken, Ugly and Fragile. Each bug has a title, repro steps, expected versus actual, and a screenshot or video timestamp.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`.

Requirement: a browser skill or tool that Claude can drive. Video or GIF recording is optional and depends on that tool.

## What it does

- Claude runs only against localhost, a preview deploy, staging, a sandbox or the design file. If the URL looks like production, Claude stops and asks.
- Claude uses throwaway test accounts and the payment provider's test cards. It sends no real email, SMS or webhook.
- For worst-case data, Claude first finds each field's limit in the schema, then seeds values from the catalog through a dev-only fixture. The fixture stays as a regression test.
- Claude gives each user type one goal and notes what that user expected and what happened. It checks the console and failed network requests.
- Claude writes `break-it-<date>-<flow>/` with `report.md`, numbered screenshots and the video. The report starts with the URL, the commit and the users run.
- The chat summary adds Decisions for you, What held up and Not tested.

## Limits

- It reports and fixes nothing until you name what to fix.
- It does not review visual design. It does not review a diff.
- A setup failure, such as a dead app or missing test data, is reported as a setup problem and not as a bug.
- A confusing behavior that the spec asks for is a decision for you, not a bug.
- If you ask to file the bugs, Claude files each bug it reproduced in the running app as a Bug through `tickets`. A bug found only in a design prototype goes back to the design's fix list, not the tracker.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/catalog.md](references/catalog.md): the worst-case values Claude seeds, by field type.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
