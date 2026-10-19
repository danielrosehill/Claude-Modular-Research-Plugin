# Podcast

An educational two-host episode made from the report. The report is the only
source: the episode explains it, it does not add to it.

## Script (`podcast/script.md`)

Format — one turn per paragraph, label then colon. Labels must match the keys of
`podcast.hosts` in the config (default `ALEX` and `SAM`):

```
# <Episode title>
[Production notes in square brackets are never read aloud.]

ALEX: ...
SAM: ...
```

Lines starting `#` or `[` are skipped by the renderer. Exactly two speakers.

**Length:** `podcast.target_minutes × 150` words (15 min ≈ 2,250 words). Count
before rendering: `grep -E '^[A-Z]+:' podcast/script.md | wc -w`.

**Shape:**
1. Cold open — the question and why it matters, in two or three turns.
2. One segment per major finding. One host leads, the other asks the questions
   a smart listener would ask and pushes back where the evidence is thin.
3. What we don't know — the open questions, plainly.
4. Close — the bottom line in three sentences and what to do with it.

**Write for the ear:**
- Short sentences. One idea per turn; turns of 1–5 sentences.
- Numbers rounded and spoken: "about four and a half thousand shekels", not "4,500 ILS".
- No URLs, citation markers, tables, bullet points or abbreviations the TTS will
  mangle — spell out or rephrase.
- Attribute in passing: "the regulator's own figures say…".
- No invented anecdotes, guests, listener mail or sound effects. No sponsor reads.
- Hosts address each other by label name sparingly; they do not name the show
  unless the user gave it one.

## Render

```bash
python3 <plugin-root>/scripts/podcast_tts.py podcast/script.md outputs/<Name>-podcast.mp3 \
  --model <podcast.model> --voices ALEX=Kore,SAM=Puck \
  [--op-ref "<podcast.api_key_op_ref>"]
```

Splits the script into ~3,000-character chunks of whole turns, synthesises them
three at a time, joins them with a short pause and encodes MP3 (96 kbps mono).
Prints a JSON line with `duration_seconds`. A 15-minute episode takes roughly
2–4 minutes; run it in the background and do something else meanwhile.

Check the result: duration within ±30% of target, and
`ffmpeg -i <mp3> -af volumedetect -f null -` shows a mean volume well above
−50 dB (silence means a chunk came back empty).

## Model notes (verified 2026-10-19)

- `gemini-3.x-*-tts` needs one content part per turn with
  `speechMetadata.speaker`; it rejects a single inline-labelled part, and rejects
  `systemInstruction`, so no style prompt can be passed — tone comes from the
  writing.
- `gemini-2.5-*-preview-tts` is the reverse: one text part with `SPEAKER:` labels
  inline, and it rejects `speechMetadata`. `--style` applies only here.
- Multi-speaker config takes exactly two speakers.
- Output is raw 16-bit PCM, 24 kHz mono, base64 in `inlineData`.
