---
description: "Check a paper draft for AI-generated writing patterns, overused filler words, and stylistic issues. Produces a quantified quality report with per-section grades and actionable fix suggestions."
name: "Check Writing Quality"
agent: academic-writer
argument-hint: "Paper slug to check (e.g. 'certia360-ieee-access')"
tools: [read, search, edit, agent, todo]
---

You are running a writing quality analysis on an existing paper draft. Your job is to delegate to the `writing-quality-check` agent and present actionable feedback.

Read these instructions completely before taking any action.

---

## Phase 1 — Identify the Draft

Determine the paper slug from the user's input. Confirm that `output/<paper-slug>/` exists and contains section `.md` files.

Also check if `output/knowledge/style-profile.md` exists (for style deviation detection).

---

## Phase 2 — Run Quality Check

Delegate to `writing-quality-check`:

> "Analyze all section files in `output/<paper-slug>/` for AI-generated writing patterns, overused terms, structural issues, and style profile deviations. Save the report to `output/<paper-slug>/writing-quality-report.md`."

---

## Phase 3 — Present Results

Summarize for the user:

1. **Overall grade** — A/B/C/D
2. **AI-Tell density** — overall and per section
3. **Top 5 most frequent AI-tell terms** — with counts
4. **Structural issues** — any em dash overuse, throat-clearing, burstiness problems
5. **Style deviations** — if profile exists, note where the draft doesn't sound like the author
6. **Priority fixes** — top 3 changes that would most improve the paper's naturalness

---

## Phase 4 — Offer Automated Fixes

If the user wants fixes applied, offer to:

1. Replace AI-tell terms with natural alternatives (using the substitution table)
2. Rewrite throat-clearing openers to start with the actual point
3. Vary sentence lengths in flagged paragraphs
4. Align vocabulary with the style profile

**Important**: Any automated fixes must preserve the academic meaning and technical accuracy. Never simplify a precise technical term to a simpler word for the sake of "naturalness."
