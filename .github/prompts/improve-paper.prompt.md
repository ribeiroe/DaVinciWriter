---
description: "Improve and extend an existing draft paper to publication-ready quality. Deepens discussion, strengthens argumentation, improves academic tone and coherence, and expands length to meet venue page requirements — using only the sources and materials already in the workspace."
name: "Improve Paper"
agent: academic-writer
argument-hint: "Paper slug of the draft to improve (e.g. 'certia360-ieee-access'). Optionally specify target length (e.g. 'IEEE Access 15–20 pages') or sections to prioritise."
tools: [read, search, edit, agent, todo]
---

You are improving and extending an existing draft paper to publication-ready quality. Your job is to produce a complete, polished manuscript that is deeper, more rigorous, and more coherent than the current draft — without introducing any new sources, citations, or external knowledge not already present in the workspace.

Read these instructions completely before taking any action.

---

## Constraints — Read First, Never Violate

- **Sources only**: Every claim, example, and citation must come exclusively from sources already ingested in `output/knowledge/sources/` or explicitly present in the paper's existing `references.bib`. Do not introduce any new references, authors, tools, studies, or external facts.
- **Preserve research intent**: Do not change the paper's research question, core contributions, methodology, or conclusions. You are improving expression and depth, not re-researching the topic.
- **Citation integrity**: All existing `[@key]` or `\cite{key}` markers must be preserved exactly as they appear. Do not add citation keys that are not in `references.bib`.
- **No hallucination**: If you cannot expand a point using existing source material, deepen it through better explanation, synthesis, and argumentation — not by inventing new facts or studies.

---

## Phase 0 — Identify the Draft

Determine the paper slug from the user's input. Confirm that `output/<paper-slug>/` exists and contains section `.md` files.

Read the following before proceeding:

1. All section files in `output/<paper-slug>/` (abstract, introduction, related-work, methodology, experiments-or-results, discussion, conclusion)
2. `output/<paper-slug>/brief.md` — for the paper's title, venue, key contributions, and source-to-section map
3. `output/<paper-slug>/compliance-report.md` — for any previously identified issues
4. `output/<paper-slug>/references.bib` — the complete allowed citation pool
5. All source summaries in `output/knowledge/sources/` — the factual foundation
6. `output/knowledge/style-profile.md` — the author's voice (if it exists)
7. `sources/venues/<venue-slug>/requirements-summary.md` — the venue's length and formatting requirements
8. `sources/venues/<venue-slug>/page-budget.md` — the per-section word targets (if it exists)

### Venue Verification (MANDATORY)

After reading the brief, verify that a target venue is set. If `brief.md` does not specify a venue, or if `sources/venues/<venue-slug>/` does not contain guidelines, **stop and ask the user**:

> "Which conference or journal is this paper targeting? I need the venue to enforce the correct page limits, formatting rules, citation style, and compliance checks."

**Do NOT proceed to Phase 1 until a venue is confirmed and guidelines are available** (either in `sources/venues/` or via defaults from `venue-families.md` with the user's agreement).

Build the todo list immediately after completing this phase.

---

## Phase 1 — Assess the Current Draft

Before writing any improvements, produce an internal assessment (do not show this to the user — use it to guide your work):

For each section, note:
- **Thin areas**: Arguments stated but not explained, claims without elaboration, single-sentence paragraphs that should be developed
- **Weak transitions**: Abrupt topic shifts, missing signposting, sections that don't flow from the previous one
- **Redundancy**: Points repeated across sections without adding new insight
- **Missed synthesis opportunities**: Places where two or more ingested sources could be brought into dialogue to strengthen an argument
- **Tone issues**: Informal language, vague hedging, imprecise terminology, or inconsistent use of defined terms
- **Structural gaps**: Missing subsections that the venue or section type typically requires

Also determine the current approximate word/page count and the gap to the venue's minimum length requirement.

---

## Phase 2 — Determine Target Length and Expansion Plan

From the venue requirements summary, establish:
- **Minimum pages / recommended target range**: read from the venue's requirements summary. Where the venue has a hard limit, use it; where it publishes only a recommended length (e.g., IEEE Access has no hard page limit), treat the recommended range (e.g., 15–20 pages) as the target.
- **Current estimated pages**: (approximate from word count — use the words-per-page rate from the venue: single-column ≈ 500 words/page, double-column ≈ 800 words/page)
- **Expansion needed**: Pages to add = minimum − current

Distribute the required expansion across sections proportionally to their thinness and importance. Typical expansion priorities, in order:

1. **Related Work** — deepen thematic groupings, add more synthesis between cited works, explicitly map each cited work to the research gap
2. **Methodology** — expand design decisions with rationale, add more detail on implementation choices, explain trade-offs
3. **Results** — add richer interpretation of each table/figure, deepen comparative analysis across participant groups or conditions where the source data supports it, discuss statistical or practical significance
4. **Discussion** — develop each sub-point more fully, connect findings back to each RQ explicitly, expand limitations with nuance
5. **Introduction** — strengthen the motivation narrative, sharpen the problem statement, add context sentences
6. **Conclusion** — expand future work with more specific, actionable directions

Do not pad. Every added sentence must carry analytical or explanatory weight grounded in existing sources.

**Thin-source stopping rule**: If, at any point during expansion, the ingested material cannot honestly support the remaining expansion for a section, STOP expanding that section. Record the per-section shortfall (words still needed) and what material or evidence the researcher must supply to close it, then continue with the other improvements (tone, transitions, coherence, compliance). Report the shortfalls in the final report. A shorter honest paper beats a padded one — never dilute existing content or fabricate material to hit a length target. This rule is subordinate only to the Results Integrity rule.

---

## Phase 3 — Improve and Extend Each Section

Process sections one at a time in this order: abstract → introduction → related-work → methodology → experiments-or-results → discussion → conclusion.

For each section:

### 3a — Improve Existing Content

Apply these improvements to the existing text:

- **Academic tone**: Replace informal or vague phrases with precise academic language. Replace "shows" with "demonstrates", "a lot of" with "substantial", "hard" with "challenging", etc.
- **Precision**: Replace vague quantifiers with specific ones where the source material supports it. Replace "many studies" with the actual counts from the source material if available.
- **Transitions and signposting**: Add lead-in sentences at the start of subsections, transition sentences between paragraphs, and closing synthesis sentences at the end of subsections.
- **Consistency**: Ensure all defined abbreviations are used consistently. Ensure all terms introduced in one section are used identically in later sections.
- **Paragraph structure**: Each paragraph should have a clear topic sentence, 3–6 supporting sentences, and a closing sentence that either summarises or bridges to the next point.
- **Remove redundancy**: If the same point is made in two places, keep the fuller version in the more appropriate location and remove or condense the other.

### 3b — Expand Thin Areas

For each thin area identified in Phase 1, expand using only existing source material:

- **Draw on source summaries**: Use methodology, results, limitations, and quotable passages from `output/knowledge/sources/` to add depth.
- **Synthesise across sources**: Where two or more cited works address the same theme, bring them into explicit comparison or dialogue: "While [A] focuses on X, [B] extends this by addressing Y, suggesting that Z."
- **Explain, don't just state**: Every claim should be followed by an explanation of *why* it is true, *how* it was demonstrated, or *what* it implies for the research.
- **Add worked examples or scenarios**: Where the methodology section describes a process, add a concrete worked example drawn from the ingested source material.
- **Strengthen argumentation**: Replace single-evidence claims with multi-evidence arguments where the source pool allows.

### 3c — Save the Improved Section

Save each improved section back to `output/<paper-slug>/<section-name>.md`, overwriting the previous version.

Mark the section todo as completed before moving to the next section.

---

## Phase 4 — Coherence and Consistency Pass

After all sections have been individually improved, perform a cross-section pass:

- **Contributions alignment**: Verify that every contribution stated in the Introduction is addressed in the Results and revisited in the Conclusion. If any contribution is understated in the Results, add a sentence making the connection explicit.
- **RQ alignment**: Verify that every Research Question stated in the Introduction is explicitly answered — by name (e.g., "Returning to RQ1...") — in the Discussion or Conclusion.
- **Terminology consistency**: Extract the key domain terms from the paper's existing Introduction and Methodology sections. Confirm each term is used with the same meaning throughout and is defined at first use in the body.
- **Abstract update**: After all sections are improved, rewrite the abstract to accurately reflect the expanded paper. The abstract must: respect the venue's abstract length requirement where one exists (check `sources/venues/<venue>/requirements-summary.md`); contain no undefined abbreviations; include the key quantitative results; follow the Background → Problem → Approach → Results → Impact structure.
- **Section length balance**: Confirm no single section is disproportionately long or short relative to its importance.

Save updated files as needed.

---

## Phase 5 — Compliance Re-Check

Run a compliance check against the venue requirements:

- [ ] Word count meets minimum page requirement or recommended target (estimated)
- [ ] Word count does not exceed maximum page limit, where the venue has one (estimated)
- [ ] Abstract within the venue's word range, where the venue specifies one (check `sources/venues/<venue>/requirements-summary.md`)
- [ ] Index terms / keywords within venue-specified range, where the venue requires them
- [ ] No undefined acronyms anywhere in the body
- [ ] No `[TODO: ...]` markers remaining
- [ ] All citations have entries in `references.bib`
- [ ] No citation keys referenced in the text that are absent from `references.bib`
- [ ] All tables and figures referenced by name/number in the body
- [ ] Author biographies present (if required by venue)
- [ ] Acknowledgements present (if required by venue)

Write the updated compliance report to `output/<paper-slug>/compliance-report.md`.

If any critical issues remain, fix them before proceeding.

---

## Phase 5b — Re-Assemble Full Paper

After all sections are improved and compliance passes, re-assemble the full paper:

1. Read all individual section files in order.
2. Concatenate them into `output/<paper-slug>/full-paper.md` with proper section numbering.
3. Verify all cross-references match actual section numbers.
4. Verify total word count fits within (page limit − 1).

If `output/<paper-slug>/full-paper.md` already exists, overwrite it with the improved version.

---

## Phase 6 — Final Report

Present a concise summary to the user:

```
## Improvement Complete

**Paper**: <paper-slug>
**Venue**: <venue>

### Changes Made
| Section | Key Improvements | Approx. Words Added |
|---------|-----------------|---------------------|
| Abstract | ... | ... |
| Introduction | ... | ... |
| Related Work | ... | ... |
| Methodology | ... | ... |
| Results | ... | ... |
| Discussion | ... | ... |
| Conclusion | ... | ... |

### Estimated Length
- Before: ~<N> pages
- After: ~<N> pages
- Venue requirement: <min>–<max> pages
- Status: <within range / still short / over limit>

### Compliance Status
<PASS | PASS WITH WARNINGS | FAIL>
<List any remaining warnings>

### Next Steps
- Review the improved sections in output/<paper-slug>/
- If further length expansion is needed, re-run /improve-paper with specific sections to target
```

---

## Interruption Policy

This prompt runs without user interruptions except:

| Moment | Why |
|--------|-----|
| Phase 0 — paper slug unclear | Cannot proceed without identifying the correct draft |
| Phase 2 — venue length requirements missing | Cannot determine expansion targets without venue guidelines |
| Phase 5 — critical compliance failure that requires user input (e.g. missing author bios) | User must supply missing information |

---

## Quality Bar

The improved paper must meet this bar before the prompt declares completion:

- Every paragraph has a clear topic sentence and a closing synthesis sentence.
- Every claim drawn from a source is followed by an explanation, not just a citation.
- No section is thinner than it needs to be to make its argument fully.
- The Related Work section explicitly maps each cited work to the research gap the paper addresses.
- The Discussion section answers every Research Question by name.
- The Conclusion's future work is specific, actionable, and grounded in the identified limitations.
- The abstract accurately reflects the full improved paper.
- The paper reads as a unified, coherent argument — not as a collection of independently written sections.
