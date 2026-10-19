---
name: deliver
description: Upload a research task's PDF and podcast to Google Drive and email the summary with links — the delivery module of modular-research, on its own. Use when outputs already exist and the user says "send it to me", "put it on Drive and email me", "re-send the report", or a run stopped before delivery.
---

# Deliver research outputs

1. **Plugin root and config** — resolve as in the `run` skill, step 0. Delivery
   needs the `drive` and `email` blocks of
   `~/.claude-plugins/modular-research/config.json`; if the file is missing, run
   the setup interview in `<plugin-root>/skills/run/references/config.md` first.
2. **Find the outputs** — in a modular-research workspace (has `brief/brief.md`),
   `outputs/<Name>.pdf`, `outputs/<Name>-podcast.mp3`, and the abstract from
   `report/report.md`. Outside one, ask which files to send.
3. **Already delivered?** — if `delivery.json` exists with `email.sent_at`, say so
   and ask before sending again. Re-uploading to the same Drive path replaces the
   file; that is fine and needs no question.
4. **Deliver** — follow `<plugin-root>/skills/run/references/delivery.md` in full:
   the one-line off-machine notice, Drive upload, email, verification, and the
   `delivery.json` record. Commit and push the workspace afterwards.
5. **Report** the Drive links and whether the email was confirmed in the sent folder.
