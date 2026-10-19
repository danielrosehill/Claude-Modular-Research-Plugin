---
name: make-podcast
description: Turn a document — a research report, a PDF, a markdown file, a repo's README — into a two-host educational podcast episode (script plus MP3) using Gemini multi-speaker TTS. Use when the user says "make a podcast of this", "turn this report into audio", "I want to listen to this", or wants to (re)generate only the podcast module of a modular-research task.
---

# Make a podcast from a document

The podcast stage of the `run` skill, usable on its own.

1. **Plugin root and config** — resolve exactly as in the `run` skill, step 0
   (`${CLAUDE_PLUGIN_ROOT}` → config `plugin_clone` → clone
   `danielrosehill/Claude-Modular-Research-Plugin`). Only the `podcast` block of
   `~/.claude-plugins/modular-research/config.json` matters here; with no config,
   use the defaults (`gemini-3.8-flash-tts`, hosts `ALEX=Kore,SAM=Puck`, 15 minutes,
   key from `$GEMINI_API_KEY`).
2. **Source** — read the whole document. A PDF: `pdftotext -layout`. The document is
   the only source; the episode adds no facts of its own.
3. **Script and render** — follow `<plugin-root>/skills/run/references/podcast.md`
   in full: script format, length, shape, writing for the ear, the render command
   and the output checks.
4. **Where files go** — inside a modular-research workspace: `podcast/script.md`
   and `outputs/<Name>-podcast.mp3`. Anywhere else: next to the source document,
   `<stem>-podcast.md` and `<stem>-podcast.mp3`, unless the user names a place.
5. **Report** the MP3 path and its length in minutes. Do not upload or email unless
   asked; for that, use the `deliver` skill.
