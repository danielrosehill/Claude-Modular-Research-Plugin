# Report and PDF

## `report/report.md`

Pandoc markdown. The YAML front matter feeds the PDF title block:

```markdown
---
title: "<Short title — the subject>"
subtitle: "<The central question>"
date: YYYY-MM-DD
author: "<pdf.author from config>"
abstract: |
  <The answer in 3–5 sentences. Someone who reads only this knows what to do or think.>
---
```

Body structure — adapt headings to the subject, keep the order:

1. **Bottom line** — the answer, the confidence, and what would change it.
2. **Background** — only what the reader needs to follow the rest.
3. **Findings** — one section per sub-question (or regroup if that reads better).
   Lead each with its conclusion, then the evidence. Tables for anything compared
   across more than two options.
4. **Open questions** — what the research could not settle and why.
5. **Recommendations / next steps** — if the brief asked for a decision.
6. **Sources** — numbered list; renumber the `[S0301]`-style IDs to `[1]`, `[2]`…
   in order of first citation, and cite inline as `[1]`.

Writing rules: lead with arithmetic when there are numbers; state uncertainty
precisely ("two sources, both from the vendor"); no filler, no "in conclusion".
No unresolved TODOs or gap placeholders — move them to *Open questions*.

Length follows the question: 4–12 pages is typical.

## Render

```bash
<plugin-root>/scripts/render_pdf.sh report/report.md outputs/<Name>.pdf --toc
```

pandoc → typst using `templates/report.typ`, then `typst compile`. Warnings about
unknown fonts are harmless (it falls back through IBM Plex Sans → Inter → DejaVu
Sans). Drop `--toc` for reports under ~4 pages (or set `pdf.toc: false`).

## Check the output, not the exit code

- `pdftotext -layout outputs/<Name>.pdf - | head -60` — title, abstract and first
  section present, no raw markup (`#`, `$`, `\[`) leaking through.
- For anything with tables, rasterise a table page
  (`pdftoppm -r 60 -png -f N -l N`) and look at it.

Then write `README.md` (question, the abstract, links to `outputs/<Name>.pdf` and
`report/report.md`), commit `Report: <title>` and push.
