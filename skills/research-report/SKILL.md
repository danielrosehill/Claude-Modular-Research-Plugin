---
name: research-report
description: Research a question inside the current project repo by delegating to research subagents, then turn the result into a timestamped executive report - a Typst PDF (IBM Plex Sans) with the bottom line, findings, open questions and numbered sources, stamped with the agent and model that did the research and the exact start and finish time. Saves the markdown, sources and PDF into the repo, commits and pushes, and emails it (Google Drive too when asked). Use when the user says "research X and give me a report", "send an agent to research this and PDF it", "research report on…", or asks for research to be written up as a PDF in this repo. For a standalone research task with its own new repo and a podcast, use `run` instead.
---

# Research report, in the repo you're in

Question → research agents → checked findings → executive report PDF → repo, email, (Drive).
`run` makes a new repo per task; this skill works inside the current project repo and adds
the provenance stamp. It reuses `run`'s research rules, renderer and delivery steps, so they
cannot drift. First written 2026-10-24.

## 0. Setup

- **Plugin root and config:** as in `run` step 0 (`${CLAUDE_PLUGIN_ROOT}`, else `plugin_clone`
  in `~/.claude-plugins/modular-research/config.json`, else clone
  `danielrosehill/Claude-Modular-Research-Plugin`). `references/…` below means
  `<plugin-root>/skills/run/references/…`. Delivery uses the config's `email` and `drive` blocks.
- **Start the clock first:** `date +%Y-%m-%dT%H:%M:%S%:z` before any research call. That is
  `started`. Precise to the second, with the offset.
- **Folder:** `research/YYYY-MM-DD-<slug>/` at the repo root, unless the repo's `CLAUDE.md`
  names another place. Not in a git repo: ask where it goes.

## 1. Brief (`brief.md`)

The user's request verbatim, then: the central question in one sentence, 2–6 sub-questions,
scope (in/out, geography, time frame), what the repo's context already establishes (read its
`CLAUDE.md`, plan and earlier `research/` folders first, and don't research what's already
settled there), and *Assumptions*. Ask one question only if the central question itself is
ambiguous.

## 2. Delegate the research

Follow `references/research.md` (fan-out, note format, source log, rules, synthesis) with these
paths: notes in `research/<date>-<slug>/notes/NN-<slug>.md`, sources in
`research/<date>-<slug>/sources.md`. One agent per sub-question, all in one message; a narrow
question with one sub-question gets one agent. Give each agent the repo context it needs in the
brief: it can't see this conversation.

Record for the stamp: the model of each agent (the `Agent` tool result or its own report; ask it
to state its model ID in its summary) and your own model ID. Never guess a model name.

Then synthesise per `references/research.md`: read every note, open the URLs behind the claims
the answer rests on, resolve conflicts, one retry for a thin answer that matters. Take
`completed` (`date +%Y-%m-%dT%H:%M:%S%:z`) when synthesis is done.

## 3. The executive report (`report.md`)

Front matter (all fields render; leave none blank):

```yaml
---
title: "<subject>"
subtitle: "<the central question>"
kicker: "EXECUTIVE RESEARCH REPORT"
date: YYYY-MM-DD
author: "<pdf.author from config>"
researched_by: "Claude Code · <model name> (<model id>)"
started: "YYYY-MM-DD HH:MM:SS ±HH:MM"
completed: "YYYY-MM-DD HH:MM:SS ±HH:MM"
sources_count: "<N> sources, accessed YYYY-MM-DD"
method: "<n> research agents (<model id>) in parallel; load-bearing claims checked against the cited pages by the orchestrator"
requested_by: "<user name>, for <repo name>"
abstract: |
  <the answer in 3–5 sentences>
---
```

When agents ran on a different model from yours, name both in `researched_by`
("Claude Code · Opus 5.5 (claude-opus-5-5), agents Sonnet 5.5 (claude-sonnet-5-5)").

Body, in this order (rules from `references/report.md`):

1. **Bottom line:** the answer, the confidence, what would change it.
2. **Key findings:** a table, one row per finding: finding | confidence | sources.
3. **Findings:** one section per sub-question, conclusion first, then evidence. Mark what's
   confirmed and what's inferred.
4. **Implications for this project:** what it means for the repo's plan, tasks or decisions,
   with the files it affects.
5. **Open questions.**
6. **Sources:** numbered `[1]`… in order of first citation: title, publisher, date, URL,
   accessed date.

Short is fine: 2–6 pages typical for an executive report.

## 4. Render and check

```bash
<plugin-root>/scripts/render_pdf.sh research/<date>-<slug>/report.md research/<date>-<slug>/<Slug>-research-report.pdf
```

Add `--toc` only past ~5 pages. Check the PDF, not the exit code: `pdftotext -layout <pdf> - |
head -40` shows the title, the provenance block (researched by, started, completed, sources) and
the summary, with no raw markup. Rasterise a table page and look at it.

## 5. Save and ship

- Link the report from the repo: one line in `README.md` (or the project's docs index) and, if the
  findings change the plan or tasks, update those files in the same commit and say which.
- Commit `Research: <title>` and push.

## 6. Deliver

Email is on by default; Drive only when the user asks (or the config sets `drive.enabled` and
the user didn't say otherwise). Follow `references/delivery.md`: the one-line notice that the PDF
is leaving the machine, Drive upload to `<drive.folder>/<repo name>/` when asked, the email with
the PDF attached (subject `Research: <title>`; body: the abstract, key findings, open questions,
links to the PDF in the repo on GitHub and on Drive), sent-folder check. Write
`research/<date>-<slug>/delivery.json` as in the reference, commit `Delivered`, push.

## Report back

The PDF path, the GitHub link, whether the email was confirmed in the sent folder, the Drive
link if any, and the open questions. Nothing else.
