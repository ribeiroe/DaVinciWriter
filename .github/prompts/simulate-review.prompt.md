---
description: "Simulate peer review of a paper draft. Generates realistic feedback from four reviewer personas (methodologist, domain expert, skeptic, reproducibility auditor) to help identify weaknesses before actual submission. Also produces a vulnerability register for rebuttal preparation."
name: "Simulate Review"
agent: academic-writer
argument-hint: "Paper slug to review (e.g. 'certia360-ieee-access'). Optionally specify the venue or particular concerns to focus on."
tools: [read, search, edit, agent, todo]
---

You are running a peer review simulation on an existing paper draft. Your job is to delegate to the `reviewer-simulator` agent and present actionable feedback to the researcher.

Read these instructions completely before taking any action.

---

## Phase 1 — Identify the Draft

Determine the paper slug from the user's input. Confirm that `output/<paper-slug>/` exists and contains section `.md` files.

Read:
1. All section files in `output/<paper-slug>/`
2. `output/<paper-slug>/references.bib`
3. All source summaries in `output/knowledge/sources/`
4. Venue guidelines in `sources/venues/<venue-slug>/` (if available)

---

## Phase 2 — Run Review Simulation

Delegate to `reviewer-simulator`:

> "Read all section files in `output/<paper-slug>/` and simulate peer review from four perspectives: a methodologist, a domain expert, a skeptic, and a reproducibility auditor (skip the reproducibility auditor if the paper is purely theoretical or conceptual). Calibrate expectations to the venue guidelines in `sources/venues/<venue>/`. Save the review to `output/<paper-slug>/peer-review-simulation.md`."

---

## Phase 3 — Present Results

Summarize for the user:

1. **Overall verdict** — average assessment across reviewers (Accept / Weak Accept / Borderline / Weak Reject / Reject)
2. **Consensus strengths** — aspects praised by 2+ reviewers (protect these during revision)
3. **Consensus weaknesses** — issues raised by 2+ reviewers (address these first)
4. **Critical risks** — any single reviewer's grounds for rejection
5. **Top 3 revision priorities** — ordered by impact on acceptance probability
6. **Vulnerability register** — table of weak points with defensive positions (for rebuttal preparation)

---

## Phase 4 — Offer Revision

Ask the user:

> "Would you like me to address any of the issues identified in the simulated review? I can revise affected sections and re-run the compliance check."

If yes, re-delegate affected sections to `paper-writer` with explicit instructions addressing reviewer concerns. Then re-run compliance check and optionally re-run the review simulation to verify improvements.

**Iteration cap**: run at most **2 automated revision cycles** (revise → re-run checks/simulation). If issues remain after the second cycle, stop iterating and present the remaining issues to the author with a recommendation on how to proceed.
