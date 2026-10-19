---
name: run
description: End-to-end research briefing from a (usually dictated) research brief — creates a new GitHub repo as the research notebook, researches the question with parallel subagents and logged sources, writes a typeset PDF report, turns it into a two-host educational podcast (MP3), uploads both to Google Drive and emails the results. Use when the user dictates or pastes a research brief and wants "the usual" research run, says "research this and send me the PDF/podcast", "do a research briefing on X", or asks for a research repo plus PDF plus podcast. Any stage can be skipped (e.g. "no podcast", "don't email").
---

# Research briefing — end to end

Brief → workspace repo → research → report PDF → podcast → Drive → email.
Each stage writes to the workspace and commits, so a run that stops can be resumed
from the last completed stage (see **Resuming**).

## 0. Locate the plugin and load config

**Plugin root** (scripts and templates live there, not in this file):
`${CLAUDE_PLUGIN_ROOT}` if set; otherwise the `plugin_clone` path in the config;
otherwise `gh repo clone danielrosehill/Claude-Research-Briefing-Plugin` into a
scratch directory. `git -C <root> pull --ff-only` before use if it is a clone.
Every `references/…` path below means `<plugin-root>/skills/run/references/…`.

**Config**, first hit wins:
1. `$RESEARCH_BRIEFING_CONFIG`
2. `~/.claude-plugins/research-briefing/config.json`

If neither exists, run the setup interview in `references/config.md` and write the
file before continuing. Read `references/config.md` for every field's meaning.

Report which config file you loaded in one line.

## 1. Take the brief

The brief usually arrives as dictation: run-on, no punctuation, mis-heard words, the
point arriving halfway through. If it is an audio file, transcribe it first with
whatever transcription tool the session has.

1. Keep the **verbatim** text — it goes to `brief/raw-dictation.md` unchanged.
2. Write a cleaned brief (`brief/brief.md`, template in `references/workspace.md`):
   - the central question in one sentence
   - 3–6 sub-questions that together answer it
   - scope: what is in, what is out, geography and time frame
   - audience and depth (default: the user, an informed non-specialist)
   - deliverables and any stage the user switched off
   - anything the user already believes or wants tested
3. Fix obvious mis-hearings silently; do **not** guess at ambiguous ones. If the
   central question itself is ambiguous, ask **one** question. Otherwise proceed
   and list your interpretations at the top of `brief.md` under *Assumptions*.

## 2. Create the workspace repo

Follow `references/workspace.md`: name, parent directory, scaffold, private GitHub
repo, first commit and push. Commit the brief as the first content.

## 3. Research

Follow `references/research.md`. In short: one subagent per sub-question, launched
together in a single message; each writes `notes/NN-<slug>.md` with sources logged
in `sources/sources.md`. Then you read every note, check the load-bearing claims
yourself, and resolve contradictions. Commit and push.

## 4. Write the report and render the PDF

Follow `references/report.md`. Output: `report/report.md` →
`outputs/<Name>.pdf` via `<plugin-root>/scripts/render_pdf.sh`. Read the rendered PDF
back (`pdftotext`, or rasterise page 1 and look at it) before going on. Commit and
push the markdown and the PDF.

## 5. Podcast

Skip if `podcast.enabled` is false or the user said no podcast. Otherwise follow
`references/podcast.md` (shared with the `make-podcast` skill): write
`podcast/script.md` from the report, then render `outputs/<Name>-podcast.mp3` with
`<plugin-root>/scripts/podcast_tts.py`. Commit the script; the MP3 is gitignored.

## 6. Deliver

Follow `references/delivery.md`: upload the PDF (and MP3) to Drive, then send the
email. **Say in one line before uploading that the files are leaving this machine.**
Record every ID and link in `delivery.json` at the workspace root, commit and push.

## 7. Report back

Reply with: the repo URL, the Drive links, whether the email went out (and to whom),
podcast length in minutes, and anything the research could not settle. No recap of
the process.

## Resuming

`delivery.json` and the files on disk say how far a run got:

| Present | Resume at |
|---|---|
| `brief/brief.md` only | 3. Research |
| `notes/*.md` but no `report/report.md` | 3, synthesis step |
| `report/report.md` but no PDF | 4, render |
| PDF, no `podcast/script.md` (and podcast enabled) | 5 |
| script, no MP3 | 5, render only |
| outputs present, `delivery.json` missing or without `email.sent_at` | 6 |

Never redo a stage whose output exists unless the user asks.
