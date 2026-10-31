# Music: a local bed under the voice

MusicGen (Meta, `facebook/musicgen-medium`) runs locally through `transformers` on Apple MPS. It
generates up to about 30 seconds from a text prompt; it ignores BPM and key arguments, so put the mood
in the prompt. The transformers loader needs `pytorch_model.bin` (8 GB for medium) plus the config and
tokenizer files; `state_dict.bin` is AudioCraft's format and is not needed. ModelScope mirrors it under
the same name (`models.md`).

1. Generate two or three candidates with `scripts/musicgen.py`, in different moods: one that matches
   the voice's tone (a quirky narrator wants something playful, such as pizzicato, claps and marimba)
   and one safer option.
2. Loop the chosen one to the film's length with a crossfade, and fade the ends:
   ```sh
   ffmpeg -i track.wav -i track.wav -filter_complex \
     "[0][1]acrossfade=d=2:c1=tri:c2=tri,atrim=0:36,afade=t=in:d=0.4,afade=t=out:st=33.5:d=2.5" bed.wav
   ```
3. Mix it at about 20% under a voice at full level (`data-volume="0.2"`), then measure the render:
   `ffmpeg -i out.mp4 -af volumedetect -vn -f null -` should show a max below 0 dB.
4. Tell the person which track is in and offer the other: music is a taste call, settled by ear.
