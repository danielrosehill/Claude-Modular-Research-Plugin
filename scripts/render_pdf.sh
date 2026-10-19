#!/usr/bin/env bash
# Render a markdown report to PDF: pandoc (markdown -> typst, via the plugin's
# report template) then typst compile.
#
#   render_pdf.sh <report.md> <out.pdf> [--toc]
#
# Title, subtitle, date, author and abstract come from the report's YAML front
# matter. Needs pandoc >= 3.1 and typst on PATH.
set -euo pipefail

src=${1:?usage: render_pdf.sh <report.md> <out.pdf> [--toc]}
out=${2:?usage: render_pdf.sh <report.md> <out.pdf> [--toc]}
shift 2
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
template="$here/../templates/report.typ"

extra=()
[[ "${1:-}" == "--toc" ]] && extra+=(-V toc=true)

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Images referenced relatively in the markdown resolve against the source dir,
# so compile with --root at the source directory and put the .typ beside it.
srcdir="$(cd "$(dirname "$src")" && pwd)"
typ="$srcdir/.render-$$.typ"
trap 'rm -rf "$tmp" "$typ"' EXIT

pandoc "$src" -f markdown -t typst --standalone --template="$template" "${extra[@]}" -o "$typ"
typst compile --root / "$typ" "$out"
echo "$out"
