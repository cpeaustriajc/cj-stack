---
name: launch-video
description: Make a narrated product launch or promo video (a trailer, teaser, feature reveal or social clip) from a live site or a brief, in every social shape (9:16, 1:1, 16:9), with a local voiceover, local music, thumbnails and cover images, and a launch kit of per-platform post copy. Use it whenever someone asks for a trailer, teaser, launch video, promo, reel, short, TikTok, ad, "something for social media", a voiceover or narrator for a video, thumbnails or marketing images for a launch, or post templates and captions to go with a video, and when they say an existing promo feels flat, "meh", robotic or unnatural.
---

# Launch video

A launch video fails in five ways, and the person reviewing it names them quickly:
- **Flat motion.** Everything fades and slides up on the same curve, cards appear one by one, captions sit over still screens. The reviewer says "meh" and can't say why.
- **A voice that gives itself away.** Monotone delivery, a heteronym read wrong ("lives" as *laives*), a brand name or domain mangled, an accent that sounds dubbed, or lines that sound like different people.
- **Off-message copy.** A claim the product will regret (a feature it might add later, a price not on sale), the category it refuses to be, or wording the brand rules forbid.
- **Broken frames.** A card that never arrives, a line hidden behind a panel, a twitch on a logo, text under platform UI, one shape cropped badly.
- **A video with nowhere to go.** No covers, no captions, no copy for each platform, and the files living in a scratch folder that gets deleted.

Each is cheap to prevent early and expensive late, so this skill is a workflow. Its rules come from a real launch where every one of these happened.

## References

Read the reference for a step when you reach it:
- `references/hyperframes.md`: the composition contract, the lint traps that bit, the format-aware pattern for 9:16, 1:1 and 16:9 from one source, and rendering.
- `references/voice.md`: choosing and directing a local TTS model, the one-take narration method, pronunciation fixes, and auditions.
- `references/music.md`: a local music bed, and mixing it under the voice.
- `references/models.md`: getting model weights when a hub is slow, and the Python environments.
- `references/launch-kit.md`: covers and thumbnails at each platform's size, post templates per platform, and publishing the kit.

Scripts, in `scripts/` (run each with `--help`):
- `modelscope_download.py`: parallel model download from ModelScope.
- `onetake_narrate.py`: the whole script in one VoiceDesign take.
- `split_take.py`: cut a take into lines from Whisper word timings.
- `musicgen.py`: music candidates.
- `audition.py`: join clips into one review file.
- `build_formats.sh`: generate the 1:1 and 16:9 projects from the master.
- `shoot_images.cjs`: render image variants at their sizes.

## The rules come from the project first

Before writing a word, find the project's own rules, because they decide what the video may say: brand guidelines (colours, type, mark, voice), positioning decisions (what the product is never framed as), legal or billing limits (no advice, no unpaid features), and the people who must not appear (an anonymous founder). They often live in a wiki, a `CLAUDE.md`, or memory notes. Read them, list the ones that bind copy, and check every script line, on-screen line and post against that list. When a rule is missing, ask with an example: "Can the video say 'no bank login'? If you might add bank connections later, it would have to be pulled."

The live site is the best source of copy and figures: its headline, its example numbers and its own components make the video look like the product and stop it inventing claims.

## Workflow

Skip a step only when it does not apply, and say so.

1. **Brief.** Settle four things with the person, one question each, each with an example of what it changes: the angle (what the first two seconds show), sound (voice, music, or silent for muted autoplay), the master shape (usually 9:16 for TikTok/Reels/Shorts, then 1:1 and 16:9), and where the files must end up (a wiki, a drive, the repo), because scratch folders are deleted.
2. **Capture.** Capture the live site for brand tokens, fonts, real copy and example figures. Rebuild the product's screens as live HTML components in its own style, rather than pasting screenshots: a rebuilt card can move, count up, and be scaled per shape.
3. **Storyboard.** Six or so frames, value stated by the second frame, the name saved for the payoff. Present it as a table (frame, beat, on screen, why) and get approval before building. Changing a frame here costs a minute; after the build it costs a render.
4. **Build the master.** One HTML/GSAP composition (`hyperframes.md`). Choreograph instead of fading: one continuous world the camera moves through, elements that become each other (scattered cards gather into the list), counts that land on a beat, varied energy (punchy entrances, calm settles, one playful spring at most). Lint, then snapshot key times and look at every one before rendering.
5. **Voice.** Write the script for the ear: short phrases, questions that rise, a pause written into the punctuation, the brand name respelled the way it is said. Generate it in one take, audition, and cut it into lines (`voice.md`). Then retime the film to the voice, not the voice to the film.
6. **Music.** Two or three candidates from a local model, looped to length, mixed well under the voice (`music.md`).
7. **Render and hand over.** Render, pull frames from the MP4 itself to check, and open the 9:16 for the person right away (see "Review loop").
8. **Adapt.** Generate 1:1 and 16:9 from the approved master with the format-aware pattern; give each shape its own layout where the content needs it (wide canvases spread content sideways, square ones shrink and recentre), snapshot, render.
9. **Launch kit.** Covers and thumbnails, then post templates per platform, checked against the project rules, published where the person asked (`launch-kit.md`).
10. **Clean up only on approval.** Downloaded models, environments and scratch projects stay until the person says the output is good; then remove what is no longer needed and say what was removed.

## Review loop

The person reviews by watching and listening, so make that instant and make each round small.

- **Open every render for them**, closing the player's open documents first: QuickTime keeps showing the old file when the same path is reopened. Also give them a one-line command they can paste to reopen it: `osascript -e 'tell application "QuickTime Player" to close every document' && open -a "QuickTime Player" <file>`.
- **Audition, don't argue.** For a voice, a line read or a music choice, render the candidates into one file back to back, say the order and the timestamps, and let them pick by ear. Keep any take they like ("keep take C just in case") in a named file before generating more.
- **Change one thing per round** and say exactly what changed and what did not. A mid-turn note ("the dots are off-centre", "the yellow dot jumps a bit") is a bug report: measure it from the rendered frames, fix the cause, and say what the cause was.
- **Verify from the output, not the source.** Pull frames from the MP4 at the moments that matter and look at them; track a moving element's position frame by frame when someone reports a twitch. A snapshot of the composition does not prove the encode.

## Checklist before handing over a render

- Every element that should appear does, at its time, in every shape (a time-shift or re-layout silently drops entrances).
- No text sits under another element, under platform UI (top 10%, bottom 18% of 9:16), or off the canvas.
- Lines and dots that should align are measured, not eyeballed.
- The voice is one person, says the brand and domain right, and every line ends before the next starts.
- Music sits under the voice; the mix peaks below 0 dB.
- Every claim, on screen or spoken, passes the project's copy rules.
- Files are where the person asked for them, not only in scratch.
