# Session Learnings Format

This file defines the schema for `output/knowledge/session-learnings.md`, the persistent
self-improvement log that the `academic-writer` agent appends to after every completed paper.

The agent reads this file at the start of every new session and applies accumulated lessons
to improve depth, quality, and compliance on the next paper.

**Do NOT delete `output/knowledge/session-learnings.md`.** It is the agent's long-term memory.

---

## File Location

```
output/knowledge/session-learnings.md
```

---

## File Structure

The file is append-only. Each completed paper session adds one entry block, separated by `---`.
Entries are ordered oldest-first so the agent can trace how lessons evolved over time.

```markdown
# Session Learnings

This file accumulates lessons from each paper-writing session.
Read at the start of every session. Never delete.

---

## Session: <ISO-date> | <paper-slug> | Venue: <venue-name>

### Section Depth
- **<SectionName>**: Target <N> words, first draft was ~<M> words. 
  Missing content: <what was absent>.
  Fix applied: <what was added in revision>.

### Quality Patterns That Worked
- <Pattern description>: <why it worked / what user response was>

### Quality Patterns To Avoid
- <Pattern description>: <why it failed / what was flagged>

### Compliance Failures (recurring)
- <Violation>: occurred in <N> of <M> drafts. Fix: <remedy>.

### Venue-Specific Notes (<venue-name>)
- <Observation>: <actionable rule for next time>

### Source Utilization
- <Source file or chapter>: mapped well to <section>. Used for: <what>.
- <Source file or chapter>: underutilized — map to <section> next time.

### User Corrections
- <What the user changed or asked to fix>: <lesson derived>

---
```

---

## Scoring Guidelines

When filling in "Section Depth":
- If a section was within ±10% of its page-budget target on the first draft → no entry needed.
- If a section was **>15% under target** → record it and document missing content.
- If a section was **>15% over target** → record what should be trimmed next time.

When filling in "Quality Patterns":
- Record only patterns that were **explicitly praised or corrected** by the user, or flagged by the compliance checker more than once.

When filling in "Venue-Specific Notes":
- Record rules that were not obvious from the venue guidelines but emerged from compliance failures or user feedback.

---

## Example Entry

```markdown
## Session: 2026-04-28 | certia360-ieee-access | Venue: IEEE Access

### Section Depth
- **Introduction**: Target 900 words, first draft ~550 words.
  Missing content: no industry motivation statistics; gap analysis referenced only one source.
  Fix applied: added IEC 62304 adoption statistics and a second gap paragraph citing thesis Ch.2.
- **Discussion**: Target 700 words, first draft ~400 words.
  Missing content: no threats-to-validity subsection; no scalability analysis.
  Fix applied: added "Threats to Validity" and "Scalability Considerations" subsections.

### Quality Patterns That Worked
- Opening Introduction with a concrete regulatory compliance failure statistic anchored the motivation effectively.
- Numbered step-by-step breakdown in Methodology improved reproducibility score in compliance check.

### Quality Patterns To Avoid
- Abstract opened with "In this paper, we present" — flagged by user; replace with the core problem statement.
- Related Work used a chronological list instead of thematic grouping — required full rewrite.

### Compliance Failures (recurring)
- Missing Keywords section: occurred in 2 of 3 drafts. Fix: always include Keywords immediately after Abstract for IEEE Access.
- Abstract over word limit (200): first draft was 240 words. Fix: enforce 200-word hard cap before writing.

### Venue-Specific Notes (IEEE Access)
- IEEE Access expects a "Threats to Validity" subsection inside Discussion — not optional.
- Author contributions statement required at end of paper (not mentioned in brief guidelines).

### Source Utilization
- thesis.txt Chapter 3 (Architecture): mapped well to Methodology. Used for component descriptions.
- thesis.txt Chapter 4 (Evaluation): underutilized — map to Experiments/Results next time.
- thesis.txt Chapter 5 (Conclusions): contributed to Discussion but also useful for Conclusion section.

### User Corrections
- User changed all "state-of-the-art" to "leading" or removed the phrase — avoid superlatives on own work.
- User asked to split Section 3 into 3.1 / 3.2 subsections — always use subsections for sections >500 words.
```

---

## Agent Instructions for Reading Learnings

When loading `output/knowledge/session-learnings.md` at session start:

1. **Scan all entries** for the current venue name — apply any venue-specific notes immediately.
2. **Identify recurring section depth issues** — for each section flagged more than once as too short, set an internal target 20% above the page budget minimum.
3. **Extract quality patterns to apply and avoid** — treat these as additional writing rules for this session, alongside the style profile.
4. **Note source utilization gaps** — if any source chapter was flagged as underutilized, prioritize it during source-to-section mapping.
5. **Apply compliance fixes proactively** — any compliance failure that recurred across sessions must be pre-checked before delegating to the compliance checker.
