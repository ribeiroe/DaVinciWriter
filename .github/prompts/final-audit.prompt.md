---
description: "Fresh-context final audit before submission. Re-reads the entire paper from scratch (no session history) to catch inconsistencies, AI-tells, missing content, and formatting issues that accumulated during drafting."
name: "Final Audit"
agent: academic-writer
argument-hint: "Paper slug (e.g. 'certia360-ieee-access'). Optionally specify venue if not already set."
tools: [read, search, edit, agent, todo]
---

You are running a **final audit** on a paper that is about to be submitted. This is a fresh-context verification pass — treat the paper as if you are reading it for the first time, with no memory of how it was drafted.

Read these instructions completely before taking any action.

---

## Purpose

Long drafting sessions accumulate context rot: inconsistencies introduced in later phases that contradict earlier ones, markers left unresolved, style drift, and hidden assumptions from the authoring process. This audit catches issues that in-context passes miss because it operates with zero prior assumptions.

---

## Phase 1 — Cold Read

Read the paper in this exact order (fresh, no skipping):

1. `output/<paper-slug>/abstract.md`
2. All section files in canonical order (introduction.md, related-work.md, methodology.md, experiments-or-results.md, discussion.md, conclusion.md)
3. `output/<paper-slug>/references.bib`

While reading, note your impressions as a first-time reader — confusion, jarring transitions, unexplained terms, or claims that feel unsupported.

---

## Phase 2 — Seven-Point Check

Apply these checks independently:

### Check 1 — Unresolved Markers
Search all section files for these work-marker patterns:
- `[TODO`
- `[UNSUPPORTED`
- `[MATERIAL GAP`
- `[CITATION NEEDED`
- `[GAP NOT CONFIRMED`
- `[AUTHOR`
- `<!-- TODO` / `<!-- FIXME` and any other work-note HTML comments

Any unresolved work marker is a **critical finding**. These must never appear in a submitted paper.

**Exempt** the bookkeeping comment the pipeline requires at the end of each section — `<!-- Word count: N / target: M -->` — and the legacy `<!-- Claim-Evidence Spot-Check ... -->` comment (no longer emitted, but present in papers drafted by earlier versions). Neither is a finding.

### Check 2 — Number Consistency
Extract every quantitative claim. Verify the same number is never reported differently:
- Abstract vs. Results
- Introduction vs. Conclusion
- Tables vs. prose

### Check 3 — AI Writing Tells (smoke test)
This check is a smoke test, not a substitute for the full writing-quality pass:

1. Grep all section files for the FULL Category-1 term list defined in `.github/agents/writing-quality-check.agent.md` — read the list from that file; it is the single source of truth, so do not maintain a copy here. Flag any occurrence with its location and a replacement suggestion.
2. Verify that `output/<paper-slug>/writing-quality-report.md` exists for this paper. If it does not, recommend running `/check-quality` rather than treating the smoke grep as sufficient.

### Check 4 — Contribution Consistency
- Do the contributions listed in the Introduction match those claimed in the Conclusion?
- Are all research questions answered in the Results?
- Is the Abstract consistent with both Introduction and Conclusion?

### Check 5 — Reference Integrity
- Are all `\cite{}` or `[n]` references present in `references.bib`?
- Are there orphan BibTeX entries (never cited)?
- Does the reference count match venue norms?

### Check 6 — Formatting and Structure
- Section headings follow venue template conventions
- No section exceeds its page budget by >15%
- No section is suspiciously short (<200 words for a major section)
- Figures and tables are referenced in text

### Check 7 — Readability Gut-Check
- Can the Abstract stand alone (no forward references)?
- Does the Introduction end with a clear paper structure paragraph?
- Does each section have a clear opening sentence stating its purpose?
- Is the Conclusion forward-looking (not just a summary)?

---

## Phase 3 — Verdict

Produce a final audit report saved to `output/<paper-slug>/final-audit-report.md`:

```markdown
# Final Audit Report — <paper-slug>

**Date**: <today>
**Verdict**: READY FOR SUBMISSION / NEEDS REVISION / NOT READY

## Critical Issues (must fix)
<list>

## Warnings (should fix)
<list>

## Suggestions (nice to fix)
<list>

## AI-Tell Instances
| Term | Section | Line | Suggested Replacement |
|------|---------|------|-----------------------|

## Number Consistency Check
| Claim | Location 1 | Location 2 | Match? |
|-------|------------|------------|--------|

## Unresolved Markers
| Marker | Section | Action Required |
|--------|---------|-----------------|
```

---

## Phase 4 — Present to User

Summarize:
1. The verdict (READY / NEEDS REVISION / NOT READY)
2. Count of critical issues, warnings, and suggestions
3. The single most important thing to fix before submission

If READY FOR SUBMISSION, congratulate and suggest running `/prepare-submission` next.
If NEEDS REVISION, offer to fix the critical issues automatically or coach through them with `/coach-revision`.
