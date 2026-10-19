# Workspace repo

## Name and place

- Name from `workspace.name_pattern`, default `{Topic}-{MMYY}` — e.g.
  `Heat-Pump-Payback-1026`. Topic is the subject, not the question: 2–5 words,
  Train-Case, no filler ("Research", "About", "Question").
- Parent: `workspace.parent_dir`. With `topic_subfolders: true`, choose the most
  specific existing group folder for the subject; if none fits, use the parent
  itself and say so — do not invent a group.
- If the directory or the GitHub repo name already exists, stop and ask; never
  overwrite.

## Layout

Create only these; no empty scaffolding beyond them.

```
<Name>/
├── README.md            what was asked, headline answer, links to outputs (written at stage 4, updated at 6)
├── CLAUDE.md            how to work in this repo (below)
├── .gitignore           *.mp3, *.wav, .render-*.typ
├── brief/
│   ├── raw-dictation.md verbatim brief, untouched
│   └── brief.md         cleaned brief
├── notes/               one file per sub-question: NN-<slug>.md
├── sources/sources.md   source log
├── report/report.md     the report (pandoc markdown with YAML front matter)
├── podcast/script.md    two-host script
├── outputs/             <Name>.pdf (committed), <Name>-podcast.mp3 (gitignored)
└── delivery.json        IDs and links of everything delivered
```

## `brief/brief.md`

```markdown
# <Central question, as a question>

Date: YYYY-MM-DD · Source: dictated brief (see raw-dictation.md)

## Assumptions
- <interpretations made of an unclear brief; empty if none>

## Sub-questions
1. ...
2. ...

## Scope
In: ... Out: ... Geography: ... Time frame: ...

## Audience and depth
...

## Deliverables
PDF report · podcast (~N min) · Drive · email   ← strike any the user switched off

## Prior beliefs to test
- ...
```

## `CLAUDE.md`

```markdown
# <Name>

Research notebook for: <central question>. Created YYYY-MM-DD by the
research-briefing plugin (danielrosehill/Claude-Research-Briefing-Plugin).

- `brief/brief.md` is the spec. Change it before changing direction.
- Every factual claim in `report/` traces to an entry in `sources/sources.md`.
- Notes are working material; `report/report.md` is the deliverable.
- Rebuild the PDF: `<plugin-root>/scripts/render_pdf.sh report/report.md outputs/<Name>.pdf --toc`
- `delivery.json` records what was sent where; update it rather than re-sending.
```

## Git

```bash
git init -b main && git add -A && git commit -m "Brief: <central question>"
gh repo create <owner>/<Name> --private --source . --push   # --public if configured
```

Commit and push at the end of every stage with a message naming the stage.
