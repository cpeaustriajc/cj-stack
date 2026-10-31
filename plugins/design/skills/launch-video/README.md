# launch-video

A skill that makes a narrated launch video from a live site or a brief. It produces every social shape, with local voiceover and music, thumbnails and post copy for each platform.

## When to use it

Claude loads this skill when you ask for a trailer, teaser, launch video, promo, reel, short or ad. It also loads for a voiceover, thumbnails, launch images or captions, or when a promo feels flat or robotic.

It guards against five failures: flat motion, a voice that sounds synthetic, off-message copy, broken frames, and a video with nowhere to go.

## Example

You say: "Make a 20-second TikTok launch video for our site, with a voiceover."

1. Claude reads your brand and copy rules, then asks four questions: angle, sound, master shape and where the files go.
2. Claude captures the live site and shows a storyboard table for your approval.
3. Claude builds the video, adds a local voice and music, and opens the 9:16 render for you.

You get MP4 files in 9:16, 1:1 and 16:9, covers and thumbnails, and post text per platform.

## Install

The `design` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install design@cj-stack
```

The skill then loads as `/design:launch-video`.

## What it does

- Claude changes one thing per review round and tells you what changed.
- Claude builds the film in HyperFrames, a tool that renders an HTML and GSAP page to MP4. It installs as a separate Claude Code plugin.
- The voice comes from a local text-to-speech model. The music comes from a local MusicGen model. Both models download to your machine.
- Claude checks frames from the rendered MP4, not only the source.
- Claude removes downloaded models and scratch projects only after you approve the output.

The scripts in `scripts/` handle model download, narration, music, formats and images. Run each with `--help`. They need `ffmpeg`, Playwright and Python packages listed in `references/models.md`.

## Limits

- It does not post to social platforms. It writes the post text and publishes the kit where you ask.
- It stops to ask when a brand rule is missing.
- Model downloads are large. Claude tells you each size before it starts.
- The voice script uses `mlx-audio`, which runs on Apple Silicon. `musicgen.py` uses MPS or falls back to the CPU.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the workflow and the pre-handover checklist.
- [references/hyperframes.md](references/hyperframes.md), [voice.md](references/voice.md), [music.md](references/music.md), [models.md](references/models.md) and [launch-kit.md](references/launch-kit.md): details per step.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
