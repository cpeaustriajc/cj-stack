# Motion example library

Each effect is named by its term in `../references/animation-vocabulary.md` and has a good and a
bad version. For each version:

- `<version>.html`: the demo page. Its CSS is the recipe.
- `<version>.gif`: the motion as it plays, for the owner. Claude sees only its first frame.
- `<version>-frames.png`: for Claude. Twelve frames evenly spaced in time, each labelled with its
  time, above a plot of the planned curve (line) and the measured progress (dots).
- `<version>-samples.json`: the measured progress at every frame.

| Term | Good | Bad |
|---|---|---|
| Scale in | [good](scale-in/good.html): a popover grows from its trigger, `scale(0.95)` and opacity, 200ms `cubic-bezier(0.23, 1, 0.32, 1)` | [bad](scale-in/bad.html): grows from `scale(0)` at its own centre, 400ms `ease-in` |
| Slide in | [good](slide-in/good.html): a toast rises from the bottom edge with opacity, 400ms `cubic-bezier(0.23, 1, 0.32, 1)` | [bad](slide-in/bad.html): the same path on 500ms `ease-in`, so it crawls, then stops dead |

## Re-make

```
bash lab/microinteraction/library/remake.sh [effect ...]
```

It needs node, the `playwright` npm package with its Chromium, and ffmpeg. It re-records every
demo (or the effects named), writes the GIF, the frame sheet and the samples next to it, and fails
when a GIF is wider than 480px or larger than 150 KB.

## Add an effect

1. Make a folder named after the glossary term, in lower case with dashes.
2. Write `good.html` and `bad.html` at 480x270. Copy a demo here as the start.
3. Give the moving element `data-measure` (x, y, w, h or o), `data-duration` and `data-easing`.
4. Define `window.play()` to start the motion with one class change.
5. Run `remake.sh <folder>` and add a row to the table above.
