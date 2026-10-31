# Screenshots and video for the Evidence line

Read this before you capture or attach a screenshot or a video for a PR. Step 7 of `SKILL.md` says when.

Evidence shows before and after of the same state. A visual change gets a screenshot
cropped to the change. A flow, a motion or a timing also gets a short video. Each video
and screenshot:
- shows where each click lands and which key was pressed, with no test code on screen.
  Use the project's helper when it has one, else the recorder's own marks
  (`references/<recorder>.md`).
- plays at a person's pace: the hero script pauses before each action, types at human
  speed and holds where the viewer reads.
  Failure: a 16-second clip of two whole flows that a reviewer could not follow.
- starts after sign-in and setup and ends before cleanup, so it shows only the user's
  steps.
- comes from a hero script: a standalone script made only for the video, run outside the
  test runner, that reuses the tests' setup helpers. Never film a test run with tracing on:
  tracing claims the page capture first, and the video shows a small corner of the page at
  about one frame a second.
- opens each step with a chapter card and reaches each page by the click a person would
  make, never a URL jump. Without both, the video jumps from page to page and the viewer gets lost.
- closes on screen each tool it opens (a dev panel, a QA menu) before the user's next
  step, so no state changes without a visible cause.

Before you attach a video, run `scripts/check-video.sh <file>` on the file you attach. It
fails a file over the upload limit or a frame padded with grey, and lists each still over
3 s: a chapter card is fine, a frozen step is not. Then read a contact sheet of its
frames for the marks. Upload each file to the code host and reference it in the body by
its relative path, as the host's adapter says (`references/github.md`). Put a video alone
in its paragraph.
