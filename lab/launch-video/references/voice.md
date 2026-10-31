# Voice: a local narrator that sounds like a person

## Pick the model by evidence, not memory

Models move monthly. Before choosing, check a current arena (Artificial Analysis TTS leaderboard,
TTS Arena) and each candidate's licence: many top open-weights models are non-commercial, which rules
them out for an ad. For an Apple Silicon Mac, `mlx-audio` (MIT) runs most current models on the GPU.

What happened with each option at the October 2026 launch:

| Model | Result |
|---|---|
| Kokoro-82M | Fast and small, but flat. Read "lives" as *laives*, "Renav" as *ruh-NAV*. Its phonemiser looked for espeak data in a hard-coded CI path; needed Homebrew `espeak-ng`. Pitch-shifting phrases with ffmpeg to fake emotion still sounded synthetic. |
| Qwen3-TTS CustomVoice (preset speakers) | Expressive, but the speakers are Chinese-native and sounded like dubbed television to an English listener. |
| Qwen3-TTS VoiceDesign, one call per line | Natural with a specific description, but every call designs a new voice: the lines sounded like different people. |
| Qwen3-TTS Base, cloning one reference clip | One consistent voice, but flat: Base takes no delivery instructions. |
| **Qwen3-TTS VoiceDesign, the whole script in one call** | **One voice, natural, directed per paragraph. Used.** |

## The one-take method

1. **Describe the voice specifically.** Vague descriptions get a generic or foreign-sounding voice.
   Name the accent and what to avoid, the age, the timbre and the register:
   > A native General American English speaker, a woman in her late twenties from California. Neutral
   > standard American accent with crisp American R sounds and vowels; absolutely no foreign, Asian or
   > British accent. Warm, slightly husky mid-range, natural and unpolished. A real person talking to a
   > friend in a casual social-media video. Not a news anchor, not a commercial announcer, not a
   > dubbed drama or anime voice. Natural breaths, small pauses between phrases, relaxed rhythm.
2. **Direct each paragraph inside the same instruction** ("Paragraph 1: puzzled, a mild curious
   upward inflection on each item … Paragraph 4: light rising questions, the pitch lifting most on
   'Lisbon' …"). Separate the script's lines with blank lines so the take pauses between them.
3. **Generate three seeds** with `scripts/onetake_narrate.py`, join them with `scripts/audition.py`,
   and let the person choose by ear. Changing any text regenerates the whole take, so when they ask
   for an edit, keep the take they liked in a named file and generate the edited text on that seed
   and two neighbours.
4. **Cut the chosen take into lines** with `scripts/split_take.py`: Whisper word timestamps find the
   gaps between lines (Whisper may drop a word like "Euros?"; find that onset from the audio level
   between its neighbours). It writes one WAV per line and a timing file with each line's
   duration and word onsets, which drive the film's cues: a card lands on the word that names it.
5. **Retime the film to the voice.** Place each line at its frame, check no line overlaps the next,
   and move visual cues to the word onsets.

Whisper's weights download from OpenAI's own server (`openai-whisper`, `small.en` is enough), not a
model hub.

## Writing for the ear

- Short phrases, and punctuation as direction: `?` rises, `…` pauses, `?!` lifts with surprise.
  "Checking… here? Savings, over there? Euros? A card… and a loan?!" reads as confused; the same items
  with `!` read as stressed. Match what the person asks for, then adjust one word at a time.
- Stretch a vowel in the direction, not the spelling: "riiight" was read *reeet*; "All right there!"
  with "draw out 'right', the long 'eye' vowel as in 'bright'" worked.
- **Respell names for the voice only**, never on screen. Check the phonemes before generating:
  `espeak-ng -q --ipa -v en-us "Ree-nav"` → `ɹˈiːnˈæv`. Record the pronunciation in the project's
  memory so the next video gets it right.
- A line the model rambles past (a 22-second take of a 5-second line) is a failed generation: regenerate
  on another seed, and do not use the "fixed" spelling that caused it.
