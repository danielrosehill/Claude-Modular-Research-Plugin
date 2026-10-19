// Pandoc template (pandoc -t typst --template=report.typ) for a research briefing.
// Pandoc fills title, subtitle, date, author, abstract and body from the
// markdown's YAML front matter. Never write a dollar-delimited variable name in a
// comment here: pandoc expands it even inside a comment and corrupts the file.
// Anything pandoc's typst writer emits that its own
// default template would have defined (horizontalrule, the terms show rule) is
// defined here, because a custom template replaces the default one wholesale.

#let horizontalrule = line(length: 100%, stroke: 0.5pt + luma(180))

#show terms: it => {
  it.children
    .map(child => [
      #strong[#child.term]
      #block(inset: (left: 1.5em, top: -0.4em))[#child.description]
    ])
    .join()
}

#let accent = rgb("#1f4e79")

#set document(title: [$title$])
#set page(
  paper: "a4",
  margin: (x: 2.2cm, top: 2.4cm, bottom: 2.4cm),
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: luma(120))
      $title$ #h(1fr) $date$
    ]
  },
  footer: context {
    set text(size: 8pt, fill: luma(120))
    h(1fr)
    counter(page).display("1 / 1", both: true)
  },
)
#set text(font: ("IBM Plex Sans", "Inter", "DejaVu Sans"), size: 10.5pt, lang: "en")
#set par(justify: true, leading: 0.7em, spacing: 1.1em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  v(1.2em)
  set text(size: 16pt, fill: accent, weight: "bold")
  it
  v(0.3em)
}
#show heading.where(level: 2): set text(size: 13pt, fill: accent)
#show heading.where(level: 3): set text(size: 11pt)
#show link: set text(fill: accent)
#show raw: set text(font: ("IBM Plex Mono", "DejaVu Sans Mono"), size: 9pt)
#set table(inset: 6pt, stroke: 0.5pt + luma(200))
#show table.cell.where(y: 0): set text(weight: "bold")
#show figure.where(kind: table): set figure.caption(position: top)
#show quote: it => block(
  inset: (left: 1em, y: 0.3em),
  stroke: (left: 2pt + accent),
  it.body,
)

// Title block
#block(width: 100%, inset: (bottom: 1em))[
  #text(size: 9pt, fill: luma(110), tracking: 0.08em)[RESEARCH BRIEFING]
  #v(0.2em)
  #text(size: 24pt, weight: "bold", fill: accent)[$title$]
$if(subtitle)$
  #v(0.1em)
  #text(size: 13pt, fill: luma(80))[$subtitle$]
$endif$
  #v(0.6em)
  #text(size: 9pt, fill: luma(110))[$if(author)$$for(author)$$author$$sep$, $endfor$ · $endif$$date$]
]
#line(length: 100%, stroke: 1pt + accent)

$if(abstract)$
#block(fill: luma(245), inset: 12pt, radius: 3pt, width: 100%)[
  #text(weight: "bold", fill: accent)[Summary]
  #v(0.2em)
  $abstract$
]
$endif$

$if(toc)$
#outline(depth: 2, indent: auto)
#pagebreak()
$endif$

$body$
