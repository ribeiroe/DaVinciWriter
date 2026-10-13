---
description: "Check a paper draft for self-plagiarism against your previously published papers. Flags textual overlap that would be caught by iThenticate/Turnitin. Essential when publishing multiple papers from one thesis."
name: "Check Plagiarism"
agent: academic-writer
argument-hint: "Paper slug (e.g. 'certia360-ieee-access'). Optionally specify which prior paper to focus comparison on."
tools: [read, search, edit, agent, todo]
---

You are running a self-plagiarism check on a paper draft against the researcher's prior publications and thesis material.

Read these instructions completely before taking any action.

---

## Phase 1 — Identify Materials

1. Determine the paper slug from the user's input.
2. Confirm that `output/<paper-slug>/` exists with section files.
3. Check for prior publications in `sources/my-papers/` — list what's available.
4. Check for thesis material in `sources/theses/`.

If BOTH `sources/my-papers/` AND `sources/theses/` are empty:
> "No comparison material found in `sources/my-papers/` or `sources/theses/`. Self-plagiarism check requires at least one prior paper or thesis to compare against. Add your published papers to `sources/my-papers/` (or thesis material to `sources/theses/`) and try again."

If either folder has files, proceed — thesis-to-paper text lift is one of the primary things this check detects.

---

## Phase 2 — Run Self-Plagiarism Guard

Delegate to `self-plagiarism-guard`:

> "Compare all sections in `output/<paper-slug>/` against all files in `sources/my-papers/` and `sources/theses/`. Produce a detailed self-plagiarism report with paragraph-level overlap detection. Save to `output/<paper-slug>/self-plagiarism-report.md`."

---

## Phase 3 — Present Results

Summarize for the user:

1. **Overall risk level** — LOW / MODERATE / HIGH / CRITICAL
2. **Most problematic sections** — which sections have highest overlap
3. **Top overlapping source** — which prior paper has most shared text
4. **Critical passages** — list any verbatim or near-verbatim matches that MUST be rewritten
5. **Recommendations** — specific actions to reduce risk

If risk is HIGH or CRITICAL, suggest:
> "Run `/improve-paper` to rewrite the flagged sections, or I can rewrite them now focusing on the overlapping passages."

---

## When This Matters Most

- Publishing multiple papers from one thesis/dissertation
- Extending a conference paper to a journal version
- Writing follow-up papers in the same research program
- Resubmitting a rejected paper to a different venue (if the original is now published elsewhere)
