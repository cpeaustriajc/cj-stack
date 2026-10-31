# HyperFrames: composing and rendering

HyperFrames renders an HTML page with a seekable GSAP timeline to a deterministic MP4. Install it as a
Claude Code plugin (`claude plugin marketplace add heygen-com/hyperframes`, then
`claude plugin install hyperframes@hyperframes`) and read its `hyperframes-core` skill before writing a
composition. In a plugin install, run the CLI through the bundled launcher, not `npx`:

```sh
printf '#!/bin/sh\nexec node %s/skills/hyperframes/scripts/plugin-cli.mjs "$@"\n' \
  "$(ls -d ~/.claude/plugins/cache/hyperframes/hyperframes/* | tail -1)" > hf && chmod +x hf
./hf init videos/<project> --non-interactive --example=blank --skill=product-launch-video
./hf lint · ./hf snapshot --at 2.4,8.1,12.6 · ./hf render --quality high --output renders/<name>.mp4
```

Its `product-launch-video` workflow (brief, capture, storyboard, build, render) is a good spine;
`./hf capture <url> -o ./capture --json` gives brand tokens, fonts, visible text and screenshots.
Its audio script only *retrieves* music from HeyGen's library; it never generates. Use
`music.md` and `voice.md` instead, and add the files as `<audio id=… src=… data-start data-duration
data-volume>` elements (every `<audio>` needs an `id` or it is silently not mixed).

## One composition, one timeline

Author the whole film as one monolithic `index.html` with a single paused timeline registered at
`window.__timelines["main"]`, and let a continuous `#world` element carry frames that share space,
moving a camera (translate/scale on the world) rather than cutting between slides. Lint warns that
nested sections "need sub-compositions"; that warning is about Studio's timeline view and can be
ignored for a monolithic film.

## Traps that cost a render each

- **Initial hidden state:** set it with `gsap.set(...)` outside the timeline, not `tl.set(..., 0)`
  (a zero-duration set at 0 does not render at t=0). Include `opacity: 0` with any `yPercent` hide:
  a word moved below its line still counts as visible text to `check`, and a container without
  `overflow: hidden` shows it.
- **`fromTo` on a hidden element must put `opacity: 1` in the destination,** or a cold-seeking render
  worker restores the hidden state and the element never appears (`gsap_cold_seek_hidden_fromto_missing_reveal`).
- **A second `fromTo` on the same element needs `immediateRender: false`,** or its from-values become
  the element's state before the first tween.
- **Text that changes over time is a pure function of a tweened proxy** (`onUpdate` reading
  `proxy.v`), never `tl.call(...)`: calls do not undo when the renderer seeks backwards.
- **`tl.shiftChildren(amount, false, after)` moves every tween authored before it whose start is
  after `after`,** including ones you meant to keep. Add tweens that must keep their times *after* the
  shift call. A retime once dropped three of five cards this way; the snapshot caught it.
- **Opaque children cover lines drawn behind them.** A route line under white row backgrounds read as
  dashed. Fade the backgrounds once the rows sit on their card, or draw the line above them.
- **Round line caps show at full dash offset.** A path "not drawn yet" still shows its cap as a dot;
  keep it at `opacity: 0` until the draw starts.
- **Springs that travel look like glitches.** A dot that drops 200 px in one frame then overshoots
  reads as a twitch. Pop it in place (scale from 0, damping ≥ 0.9) instead.
- **Measure alignment.** A dot centred at x=155 on a 6 px line at x=155–161 is 3 px off and the
  viewer sees it. Compute centres.
- `check` reports overlaps that are intentional (a drawer over a list). Read each one; fix the real
  ones, and say which you left on purpose.

## Format-aware master (9:16, 1:1, 16:9 from one source)

Keep one master `index.html` at 1080×1920 and generate the other shapes from it, so every later edit
reaches all three.

1. Give the root a `data-format="9x16"` attribute and wrap the world in a `#frame-world` element.
2. Read the format in the script and apply a static view transform to the wrapper, per shape:
   ```js
   const FORMAT = document.getElementById("root").dataset.format || "9x16";
   const VIEW = { "9x16": { tx: 0, ty: 0, s: 1 }, "1x1": { tx: 151, ty: -104, s: 0.72 },
                  "16x9": { tx: 881, ty: -352, s: 0.85 } }[FORMAT];
   document.getElementById("frame-world").style.transform =
     `translate(${VIEW.tx}px, ${VIEW.ty}px) scale(${VIEW.s})`;
   ```
   Anything positioned outside the world that points at something inside it (a touch ripple on a
   figure) is computed from `VIEW`, not hard-coded.
3. Put per-shape layout in CSS keyed on the attribute: `#root[data-format="16x9"] .headline { … }`.
   Wide canvases put words on the left and the world on the right; square canvases shrink and
   recentre. Scatter positions and other choreography that depends on space get a per-format table.
4. Generate the siblings with `scripts/build_formats.sh`, which copies the project (minus renders,
   snapshots, capture) and rewrites the root size, `data-format`, the body size and the viewport.
   Never keep two root compositions in one project folder (lint error `multiple_root_compositions`),
   including backups; keep backups outside.
5. Snapshot each shape at the moments that matter before rendering it.
