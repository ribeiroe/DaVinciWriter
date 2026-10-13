---
description: "Integrate co-author or advisor feedback into the paper. Accepts freeform comments, maps them to sections, proposes specific edits, and tracks which feedback has been addressed vs. deferred. Formal peer reviews are routed to /draft-rebuttal and /revise-paper."
name: "Get Feedback"
agent: academic-writer
argument-hint: "Paper slug (e.g. 'certia360-ieee-access'). Then paste or describe the feedback."
tools: [read, search, edit, agent, todo]
---

You are helping a senior researcher integrate **co-author or advisor feedback** into their paper.

Read these instructions completely before taking any action.

---

## Phase 0 — Check the Feedback Type

If the pasted feedback is formal peer review (reviewer numbers, scores, decision language), say so and route: run `/draft-rebuttal` for the response letter and `/revise-paper` for the systematic revision — then stop.

Otherwise, continue below.

---

## Phase 1 — Collect Feedback

Ask the user to provide feedback in any format:
- Pasted comments (e.g., from a PDF review, email, or shared document)
- Section-specific notes (e.g., "In the methodology, the sample size justification is weak")
- General impressions (e.g., "The introduction doesn't grab me")

Also read all sections in `output/<paper-slug>/` and `output/<paper-slug>/brief.md` for context.

---

## Phase 2 — Parse and Map Feedback

For each distinct comment, extract:
1. **Comment ID** (sequential: F1, F2, F3...)
2. **Source** (who gave the feedback, if known)
3. **Target section** (which section it applies to)
4. **Target paragraph/element** (as specific as possible)
5. **Category**: Content | Structure | Argumentation | Style | Formatting | Factual
6. **Severity**: Critical (blocks submission) | Important (significantly weakens) | Minor (nice to fix) | Preference (subjective)

Present the parsed feedback as a table:

| ID | Source | Section | Category | Severity | Summary |
|---|---|---|---|---|---|
| F1 | Co-author A | Introduction | Argumentation | Important | Gap statement is too vague |
| F2 | Advisor | Methodology | Content | Critical | Missing justification for sample size |
| ... | ... | ... | ... | ... | ... |

Ask the user to confirm the parsing is correct before proceeding.

---

## Phase 3 — Propose Edits

For each comment (prioritized by severity), propose a specific edit:

```markdown
### F1: "Gap statement is too vague" (Introduction, Important)

**Current text** (paragraph 3):
> "There is a gap in the literature regarding..."

**Proposed revision**:
> "Despite advances in X [1,2] and Y [3], no existing approach addresses the combination of A and B under constraint C — a scenario common in <domain> [4]."

**Rationale**: Makes the gap concrete, cites specific prior work to establish what exists, and identifies the specific missing combination.

**Action**: Accept / Modify / Defer / Reject
```

---

## Phase 4 — Apply Accepted Edits

After the user reviews all proposals:
1. Collect all "Accept" items.
2. For each affected section, delegate to `paper-writer` with specific revision instructions.
3. Mark each applied edit in the feedback tracker.

---

## Phase 5 — Update Feedback Tracker

Save a feedback tracking file to `output/<paper-slug>/feedback-tracker.md`:

```markdown
# Feedback Tracker — <Paper Title>

**Last updated**: <date>

## Summary
- Total comments received: N
- Applied: M
- Deferred (future work): P
- Rejected (with reason): Q
- Pending: R

## Detailed Log

| ID | Comment | Section | Severity | Status | Resolution |
|---|---|---|---|---|---|
| F1 | Gap statement too vague | Introduction | Important | ✓ Applied | Rewrote gap paragraph with specific citations |
| F2 | Sample size justification | Methodology | Critical | ✓ Applied | Added paragraph with power analysis reference |
| F3 | Consider adding ablation | Results | Minor | Deferred | Noted as future work in Discussion |
```

---

## Phase 6 — Coherence Check

After applying edits, verify:
- No contradictions introduced between revised and unrevised sections
- Terminology remains consistent
- Cross-references still valid
- Word count still within page budget

If issues found, fix them before reporting completion.

---

## Constraints

- DO NOT ignore any feedback item — every comment must be explicitly accepted, modified, deferred, or rejected (with reason).
- DO NOT add new references not in `output/knowledge/sources/`.
- DO NOT change the paper's core contributions or research questions without explicit user approval.
- Preserve the researcher's voice (refer to style profile).
