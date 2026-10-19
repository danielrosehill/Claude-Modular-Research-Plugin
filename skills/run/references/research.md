# Research

## Fan out

Launch one subagent per sub-question, **all in one message** so they run at once.
Brief each completely — it has no access to this conversation:

- the central question and its own sub-question, verbatim from `brief/brief.md`
- scope, time frame, geography, audience
- the absolute path of its output file `notes/NN-<slug>.md` and of
  `sources/sources.md`
- the note format and source rules below
- the web-access order: built-in search and fetch first; escalate to a real browser
  or other routes only when a target actually blocks or needs JavaScript
- "return a 5-line summary of your findings and the three claims you are least sure of"

Subagents append to `sources/sources.md` concurrently — tell each to append a block
under its own heading (`## NN-<slug>`) with a single write, not edit others' blocks.

## Note format (`notes/NN-<slug>.md`)

```markdown
# <Sub-question>

## Answer
<3–8 sentences, the direct answer>

## Evidence
- <claim> [S3]
- <claim> [S7] — confirmed in two independent sources [S7][S9]

## Disagreements and gaps
- <where sources conflict, and which way you lean and why>

## Confidence
High | Medium | Low — <one line why>
```

## Source log (`sources/sources.md`)

```markdown
## NN-<slug>
- [S3] <Title> — <publisher>, <date published or "undated">. <URL>. Accessed YYYY-MM-DD. Supports: <claim>.
```

Source IDs are global across the workspace: subagent NN uses `S<NN>01`, `S<NN>02`…
(e.g. `S0301`) so concurrent writers never collide. The report may renumber.

## Rules every subagent follows

- Read the page, not the search snippet. A snippet is not a source.
- Numbers, dates, prices and legal or medical statements need a source each; two
  independent sources when the claim carries the conclusion.
- Prefer primary sources (the regulator, the paper, the manufacturer, the dataset)
  over articles about them. Note the date of anything time-sensitive.
- Say what was confirmed and what was inferred; never present them in one voice.
- An empty search is a fact about the search, not about the world: rephrase before
  concluding something does not exist.

## Synthesis (you, after the agents return)

1. Read every note in full — agent summaries are reports to check, not facts.
2. Spot-check the load-bearing claims yourself: open the cited URL and confirm it
   says what the note says. Fix or drop what does not hold.
3. Resolve contradictions between notes; record the resolution in the relevant note.
4. If a sub-question came back thin and matters to the answer, send one more agent
   at it with a sharper brief. One retry, then report the gap honestly.
5. Commit: `Research: notes and sources`.
