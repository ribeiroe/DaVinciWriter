---
description: "Conduct a structured literature review from ingested sources. Generates a thematic literature map, identifies research gaps, and produces a Related Work section draft with proper positioning."
name: "Literature Review"
agent: academic-writer
argument-hint: "Topic or research question to review (e.g. 'agile methods in safety-critical systems'). Optionally specify the target venue."
tools: [read, search, edit, agent, todo]
---

You are conducting a structured literature review based on the sources already ingested in the workspace. Your goal is to produce a comprehensive thematic analysis, identify gaps, and optionally draft a Related Work section.

Read these instructions completely before taking any action.

---

## Phase 1 — Scope the Review

Determine the topic/research question from the user's input. Then read:

1. All source summaries in `output/knowledge/sources/`
2. Venue guidelines in `sources/venues/<venue-slug>/` (if the user specified a venue)
3. Any existing paper outline in `output/<paper-slug>/` (if writing for an existing paper)

If no sources have been ingested, inform the user and suggest running `/ingest-sources` first.

---

## Phase 2 — Thematic Classification

Classify all ingested sources into themes. For each source, determine:

| Field | Content |
|---|---|
| Source | BibTeX key or filename |
| Title | Full title |
| Year | Publication year |
| Theme(s) | 1–3 thematic categories |
| Contribution type | Empirical study / Framework / Tool / Theory / Survey / Case study |
| Relevance | High / Medium / Low (to the stated research question) |
| Key finding | One-sentence summary of main result |

Group sources by theme and present a **thematic map**:

```markdown
## Thematic Map

### Theme 1: [Name]
- Source A (2023) — [key finding]
- Source B (2021) — [key finding]
**Sub-themes**: ...
**Trend**: [What's the direction of research in this theme?]

### Theme 2: [Name]
...
```

---

## Phase 3 — Gap Analysis

For each theme, identify:

1. **What is well-covered** — aspects with strong evidence from multiple sources
2. **What is partially covered** — aspects with only 1–2 sources, or conflicting findings
3. **What is missing** — aspects mentioned but not studied, or completely absent

Produce a gap matrix:

```markdown
## Gap Matrix

| Research Aspect | Coverage | Sources | Gap Type |
|---|---|---|---|
| Aspect A | Well-covered | [src1, src2, src3] | None |
| Aspect B | Partial | [src4] | Only one study; no replication |
| Aspect C | Missing | — | No empirical evidence found |
```

Highlight the **most significant gap** — the one that represents the strongest opportunity for a new contribution.

---

## Phase 4 — Chronological Evolution

Produce a timeline showing how the research area evolved:

```markdown
## Research Evolution Timeline

| Period | Key Development | Representative Work |
|---|---|---|
| 2015–2018 | [Early work on X] | [Source] |
| 2019–2021 | [Shift to Y] | [Source] |
| 2022–2024 | [Current trend Z] | [Source] |
| 2025+ | [Emerging direction] | [Source or gap] |
```

---

## Phase 5 — Related Work Draft (Optional)

If the user is writing for a specific paper, draft a Related Work section that:

1. Opens with a framing paragraph explaining how the literature is organized
2. Covers each theme in a subsection
3. Positions each cited work relative to the user's contribution
4. Ends with a positioning paragraph: "Unlike [X, Y, Z], our work differs in that..."
5. Uses the author's style profile from `output/knowledge/style-profile.md` (if available)

Save the draft to `output/<paper-slug>/related-work-draft.md` (or present inline if no paper exists yet).

---

## Phase 6 — Output

Save the full literature review to `output/knowledge/literature-review-<topic-slug>.md`:

```markdown
# Literature Review — <Topic>

**Date**: <today>
**Sources analyzed**: N
**Themes identified**: N
**Research question**: <as stated by user>

## Thematic Map
[from Phase 2]

## Gap Matrix
[from Phase 3]

## Research Evolution
[from Phase 4]

## Key Insights
1. [Most important finding across all sources]
2. [Second insight]
3. ...

## Recommended Research Directions
1. [Direction that addresses the biggest gap]
2. [Direction that extends the strongest theme]
3. ...
```

---

## Rules

- **Only cite sources present in `output/knowledge/sources/`** — never fabricate references.
- **Be honest about coverage** — if the ingested sources are insufficient for a comprehensive review, say so and recommend additional papers to ingest.
- **Distinguish between themes and topics** — a theme is a cross-cutting concern, not just a subject area.
- **Identify contradictions** — if sources disagree, highlight the disagreement explicitly.
