# Claude-Research-Briefing-Plugin

A Claude Code plugin that runs one research job from start to finish. You dictate a
brief, and you get back a private GitHub repo with the working notes, a typeset PDF
report, an educational two-host podcast episode, copies of both on Google Drive,
and an email with links.

Part of the [danielrosehill Claude Code marketplace](https://github.com/danielrosehill/Claude-Code-Plugins).

## Skills

| Skill | What it does |
|---|---|
| `research-briefing:run` | The whole pipeline: brief → workspace repo → research → PDF → podcast → Drive → email. Any stage can be switched off per run ("no podcast"). Resumable from the last completed stage. |
| `research-briefing:make-podcast` | Turns any document into a script and MP3. This is the podcast stage on its own. |
| `research-briefing:deliver` | Uploads existing outputs to Drive and sends the email. This is the delivery stage on its own. |

The stage procedures live in `skills/run/references/` and are read when needed. The
two standalone skills reuse the same references, so the procedures cannot drift
apart.

## The pipeline

1. **Brief**: keeps the raw dictation verbatim and writes a cleaned brief: a central
   question, 3–6 sub-questions, scope, audience, and the assumptions made.
2. **Workspace**: a new repo named `{Topic}-{MMYY}`, private by default, pushed to
   GitHub, with this layout: `brief/`, `notes/`, `sources/`, `report/`, `podcast/`,
   `outputs/`, `delivery.json`.
3. **Research**: one subagent per sub-question, all running at once. Each writes a
   note with an answer, the evidence and a confidence level, and logs its sources
   with access dates. The orchestrator then checks the claims the answer rests on
   against the cited pages.
4. **Report**: pandoc markdown → Typst → PDF, using `templates/report.typ`. The
   template gives a title block, a summary box, a table of contents and running
   headers.
5. **Podcast**: a two-host script written for listening (≈150 words/min). It is
   rendered with Gemini multi-speaker TTS by `scripts/podcast_tts.py` (standard
   library + ffmpeg).
6. **Delivery**: uploads to Drive (rclone, a Drive skill, or a Drive MCP), emails a
   summary with links and an optional attached PDF, checks that both arrived, and
   records every ID in `delivery.json`.

## Requirements

- `gh` (authenticated), `git`
- `pandoc` ≥ 3.1, `typst` ≥ 0.12, `pdftotext` (poppler) for checking the PDF
- `ffmpeg`, Python 3.9+
- A Gemini API key with TTS access (`$GEMINI_API_KEY` or a 1Password reference)
- For delivery: an `rclone` Drive remote (or a Drive skill/MCP), and a Gmail send
  tool (e.g. a Google Workspace MCP)

## Configuration

`~/.claude-plugins/research-briefing/config.json`, or the path in
`$RESEARCH_BRIEFING_CONFIG`. Start from `config.example.json`. If the file is
missing, the first run asks a few questions and writes it for you. Every field is
documented in `skills/run/references/config.md`.

## Scripts

```bash
scripts/render_pdf.sh report.md out.pdf [--toc]
scripts/podcast_tts.py script.md out.mp3 [--model gemini-3.8-flash-tts] \
    [--voices ALEX=Kore,SAM=Puck] [--op-ref op://Vault/Item/field]
```

## Gemini TTS: things learned building this (verified 2026-10-19)

- **The 3.x and 2.5 TTS models take incompatible request shapes.**
  - `gemini-3.x-*-tts` needs one content part per turn, each with
    `"speechMetadata": {"speaker": "<LABEL>"}`. A single part with inline
    `LABEL:` text is rejected: *"Multi-speaker generation requests must specify
    speech_metadata.speaker for each text part"*.
  - `gemini-2.5-*-preview-tts` is the reverse. It wants the inline labels and
    rejects `speechMetadata` (*"Speech metadata is not supported for this model"*).
- **3.x rejects `systemInstruction`** (*"Developer instruction is not enabled for
  this model"*), so you cannot pass a style prompt. Tone has to come from how the
  script is written. 2.5 accepts a style line prepended to the text.
- Multi-speaker mode takes exactly two speakers.
- Audio comes back as base64 raw PCM (16-bit, 24 kHz, mono) in `inlineData`.
- `podcast_tts.py` uses a key from `--op-ref` before `$GEMINI_API_KEY`. An exported
  shell key is often stale, and with the opposite order the script would quietly
  use it and fail with `API_KEY_INVALID`.

## Pandoc template trap

A custom pandoc template replaces the default one completely. Helpers the typst
writer emits, such as `#horizontalrule` and the `terms` show rule, must therefore be
defined in `templates/report.typ`, or `typst compile` fails with *"unknown variable:
horizontalrule"*. Pandoc also expands dollar-delimited variable names **inside
comments**, so never write one in a template comment.

## Related

- [Claude-Research-Space-Plugin](https://github.com/danielrosehill/Claude-Research-Space-Plugin):
  long-lived, open-ended research workspaces with many variants. Use this plugin
  instead when you want a single brief turned into finished deliverables.

## License

MIT
