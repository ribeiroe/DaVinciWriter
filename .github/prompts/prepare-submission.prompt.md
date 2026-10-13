---
description: "Generate all submission artefacts beyond the paper itself: cover letter, highlights, suggested reviewers, data availability statement, and conflict-of-interest declarations."
name: "Prepare Submission"
agent: academic-writer
argument-hint: "Paper slug (e.g. 'certia360-ieee-access'). Optionally specify which artefacts to generate."
tools: [read, search, edit, agent, todo]
---

You are helping a senior researcher prepare the complete submission package for their paper. Beyond the manuscript itself, most venues require or benefit from additional documents.

Read these instructions completely before taking any action.

---

## Phase 0 — Read Context

Read the following:
1. All sections in `output/<paper-slug>/`
2. `output/<paper-slug>/brief.md` — title, venue, contributions
3. `output/<paper-slug>/elevator-pitch.md` — if it exists
4. `sources/venues/<venue-slug>/requirements-summary.md` — venue rules
5. All source summaries in `output/knowledge/sources/` — for suggested reviewers
6. `output/knowledge/portfolio-tracker.md` — for related work context

---

## Phase 1 — Cover Letter

Generate a professional cover letter to the editor or track chair:

```markdown
# Cover Letter

**To**: The Editor / Program Committee of <Venue>
**Re**: Submission of "<Paper Title>"
**Date**: <today>

---

Dear Editor,

We are pleased to submit our manuscript entitled "<Paper Title>" for consideration in <Venue>.

**Summary**: <2–3 sentences describing what the paper does and its main contribution — drawn from the elevator pitch>

**Significance**: <1–2 sentences on why this matters to the venue's audience>

**Fit with venue scope**: <1–2 sentences explaining why this venue is appropriate>

**Key contributions**:
1. <Contribution 1>
2. <Contribution 2>
3. <Contribution 3>

**Compliance statement**: This manuscript has not been submitted elsewhere and all authors have approved the submission. <Add blind review statement if applicable>.

We look forward to the reviewers' feedback.

Sincerely,
[Authors]
```

---

## Phase 2 — Highlights (Elsevier/Springer style)

Generate 3–5 bullet-point highlights (max 85 characters each):

```markdown
# Highlights

- <Highlight 1 — max 85 chars, states a key finding or contribution>
- <Highlight 2>
- <Highlight 3>
- <Highlight 4>
- <Highlight 5>
```

These should be self-contained, specific, and newsworthy — not generic.

---

## Phase 3 — Suggested Reviewers

From the ingested source summaries (papers by others in `output/knowledge/sources/`), identify 3–5 potential reviewers:

```markdown
# Suggested Reviewers

| # | Name | Affiliation | Expertise | Rationale |
|---|---|---|---|---|
| 1 | <Name from source> | <Institution> | <Area> | Author of [ingested paper] on related topic; would appreciate the contribution |
| 2 | ... | ... | ... | ... |

## Reviewers to Exclude (Conflicts of Interest)
- <Name> — <reason: co-author, same institution, collaborator>
```

Rules:
- Only suggest authors whose papers are in `output/knowledge/sources/` (so they are verifiably real)
- Prefer authors whose work you BUILD ON (they will see value in your contribution)
- Avoid suggesting authors whose work you CHALLENGE (likely to be defensive)
- Include affiliation diversity (different institutions, countries)

---

## Phase 4 — Data Availability Statement

```markdown
# Data Availability Statement

<Choose the appropriate template based on the paper's data situation>

**Option A — Open data**:
> The datasets and artefacts supporting this study are publicly available at [DOI/URL]. The replication package includes: [list contents].

**Option B — Available on request**:
> The data that support the findings of this study are available from the corresponding author upon reasonable request. [Explain any restrictions].

**Option C — No new data**:
> This paper does not report new experimental data. The analysis is based on [previously published data / architectural design / analytical framework].
```

---

## Phase 5 — Author Contributions (CRediT)

If the venue requires CRediT (Contributor Roles Taxonomy) statements:

```markdown
# Author Contributions (CRediT)

| Author | Roles |
|---|---|
| <Author 1> | Conceptualization, Methodology, Software, Writing — Original Draft |
| <Author 2> | Validation, Formal Analysis, Writing — Review & Editing |
| <Author 3> | Supervision, Project Administration, Funding Acquisition |
```

Ask the user to confirm or adjust author roles.

---

## Phase 6 — Pre-Submission Checklist

Produce a final checklist:

```markdown
# Pre-Submission Checklist

## Manuscript
- [ ] Title page matches venue requirements (authors, affiliations, corresponding author)
- [ ] Abstract within word limit (<limit> words)
- [ ] Keywords provided (if required)
- [ ] All figures are high-resolution and properly captioned
- [ ] References formatted per venue style
- [ ] Blind review compliance (no self-identifying text) — if applicable
- [ ] Page/word count within limits

## Submission Package
- [ ] Cover letter prepared
- [ ] Highlights prepared (if applicable)
- [ ] Suggested reviewers listed
- [ ] Conflict-of-interest statement
- [ ] Data availability statement
- [ ] Author contributions (CRediT)
- [ ] Copyright/license form identified
- [ ] Supplementary materials prepared (if any)

## Final Checks
- [ ] All co-authors have reviewed and approved the final version
- [ ] ORCID IDs collected for all authors
- [ ] Funding acknowledgments are complete and accurate
- [ ] Submission portal account created and tested
```

---

## Phase 7 — Save All Artefacts

Save to `output/<paper-slug>/submission/`:
- `cover-letter.md`
- `highlights.md`
- `suggested-reviewers.md`
- `data-availability.md`
- `author-contributions.md`
- `pre-submission-checklist.md`

Report what was generated and any items that need user input (e.g., co-author affiliations, ORCID IDs).

---

## Constraints

- Only suggest reviewers whose names come from ingested source summaries.
- DO NOT fabricate institutions, email addresses, or reviewer details not in the sources.
- Cover letter tone: professional, concise, confident but not boastful.
- Highlights: max 85 characters each, no abbreviations without expansion.
