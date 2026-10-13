---
name: academic-writer
description: "End-to-end workflow for writing a publication-ready scientific paper. Use when user wants to write a research paper, draft manuscript sections, ingest theses or papers as sources, learn writing style from prior work, or prepare a paper for a specific conference or journal."
argument-hint: "Paper topic, target venue, or specific task (e.g. 'write abstract for my ICASSP paper')"
---

# Academic Paper Writing Skill

This skill orchestrates the full lifecycle of writing a scientific paper at the level of a senior researcher, from raw academic sources to a publication-ready manuscript compliant with a target venue's requirements.

## When to Use

- Starting a new research paper from scratch
- Drafting or revising individual sections (abstract, introduction, methodology, etc.)
- Ingesting theses and papers to build a citable knowledge base
- Capturing your writing style from previous publications
- Preparing a submission for a specific conference or journal template
- Running a compliance check against author guidelines

## Workflow Overview

```
[Ingest Sources] → [Learn Style] → [Set Venue] → [Draft Sections] → [Compliance Check] → [Iterate]
```

Each step can be run independently or as part of the full pipeline.

## Procedure

### 1. Prepare the Knowledge Base

Run `/ingest-sources` to process all files in `sources/theses/`, `sources/papers/`, and `sources/artefacts/`.
Summaries are saved to `output/knowledge/sources/` and persist between sessions.

See [source summaries reference](./references/source-summary-format.md) for the expected format.

### 2. Build a Style Profile

Run `/learn-style` to analyze papers in `sources/my-papers/`.
The profile is saved to `output/knowledge/style-profile.md` and is automatically applied when writing.

See [style profile reference](./references/style-profile-format.md) for the expected format.

### 3. Configure the Venue

Run `/set-venue` and place author guidelines in `sources/venues/<venue-name>/`.
The compliance checker reads these guidelines when validating the draft.

See [supported venue families](./references/venue-families.md) for formatting details.

### 4. Write the Paper

Run `/write-paper` for the full pipeline (including source ingestion and style learning), or `/new-paper` to go straight to drafting when ingestion and style learning are already done. You can also ask the `academic-writer` agent directly:

> "Write the introduction for my paper titled '...' targeting IEEE ICASSP 2026."

Section files are saved to `output/<paper-slug>/`.

### 5. Validate Compliance

The orchestrator runs the compliance checker automatically at the end of each draft cycle.
To run it manually: "Check compliance of my paper against the venue guidelines."

The report is saved to `output/<paper-slug>/compliance-report.md`.

### 6. Revise After Peer Review

Run `/revise-paper` once you have received real reviewer comments.

The `revision-specialist` subagent will:
1. Parse every reviewer comment and detect conflicting requests
2. Audit all source folders for unused or underutilised evidence
3. Build a reviewer response matrix mapping each comment to an action
4. Rewrite sections directly — no suggestions, only done revisions
5. Enforce consistency across Abstract, Introduction, and Conclusion
6. Produce seven output reports: source folder assessment, reviewer response matrix, revised manuscript, change log, remaining risks, source utilisation audit, and gap analysis

Save real reviewer comments to `sources/reviewer-feedback/<paper-slug>-round-<N>.md` before running.

### 7. Verify Citation Integrity

Run `/verify-citations` to check that all references in your paper are:
- Traceable to an ingested source summary (not hallucinated)
- Metadata-consistent (correct title, year, authors)
- Actually cited in the text (no orphan BibTeX entries)
- Fresh enough (at least 30% from the last 5 years)

The report flags fabricated citations as critical issues.

### 8. Check Writing Quality

Run `/check-quality` to scan your paper for:
- AI-generated writing patterns (30 high-frequency AI-tell terms)
- Structural issues (em dash overuse, throat-clearing, burstiness deficit)
- Hedging/overclaiming imbalance
- Deviations from your style profile

Each section receives a grade (A/B/C/D) and a substitution table is provided.

### 9. Literature Review

Run `/lit-review` to produce a structured thematic analysis from your ingested sources:
- Thematic map grouping sources by theme
- Gap matrix identifying what's missing
- Research evolution timeline
- Optional Related Work section draft

### 10. Convert Between Venue Formats

Run `/convert-format` to move a paper from one venue's format to another:
- Citation style conversion (IEEE ↔ APA ↔ Springer)
- Section restructuring to match target venue
- Page budget recalculation
- Blind review compliance adjustments

### 11. Coach Revision (Socratic Mode)

Run `/coach-revision` for interactive revision guidance:
- Walks through each reviewer comment one by one
- Asks questions rather than auto-rewriting
- Helps you decide: accept, partial accept, rebuttal only, or defer
- Builds a revision plan collaboratively
- Produces a rebuttal skeleton for response letter drafting

### 12. Final Audit (Pre-Submission)

Run `/final-audit` for a fresh-context verification pass:
- Cold-reads the entire paper with zero session memory
- Checks for unresolved markers (`[TODO]`, `[MATERIAL GAP]`, etc.)
- Verifies number consistency across sections
- Scans for AI writing tells
- Validates contribution consistency (Intro ↔ Conclusion)
- Checks reference integrity and formatting
- Produces a READY / NEEDS REVISION / NOT READY verdict

### 13. Import External Paper

Run `/import-paper` to bring in a paper written outside DaVinci:
- Reads PDF, TXT, or MD files from `sources/submitted-papers/`
- Identifies section headings and splits into individual files
- Creates structured output in `output/<paper-slug>/`
- Extracts references into `references.bib`
- Ingests the paper as a source for the knowledge base
- Ready for `/revise-paper`, `/improve-paper`, or `/check-quality`

### 14. Self-Plagiarism Check

Run `/check-plagiarism` to compare your new paper against prior publications:
- Paragraph-level comparison against all files in `sources/my-papers/`
- Thesis-to-paper overlap detection (institutional repository risk)
- Section-specific thresholds (higher tolerance for Methodology, lower for Results)
- Risk classification: Critical (>80% verbatim), High (50–80%), Moderate (30–50%), Low (<30%)
- Differentiation analysis: what’s actually new in this paper
- Essential when publishing multiple papers from one thesis

## Asset Index

| Asset | Purpose |
|-------|---------|
| [source-summary-format.md](./references/source-summary-format.md) | Template for ingested source summaries |
| [style-profile-format.md](./references/style-profile-format.md) | Template for writing style profiles |
| [venue-families.md](./references/venue-families.md) | Formatting details for IEEE, ACM, Elsevier, Springer |
| [academic-tells.md](./references/academic-tells.md) | Compact academic AI-tell patterns and vocabulary list, applied during drafting |
| [humanizer.md](./references/humanizer.md) | 37 before/after patterns to remove AI writing tells (used by `/check-quality`) |
| [session-learnings-format.md](./references/session-learnings-format.md) | Schema for the self-improvement log written after every session |
| [portfolio-tracker-format.md](./references/portfolio-tracker-format.md) | Schema for multi-paper coherence tracker |
| [revision-specialist.agent.md](../../agents/revision-specialist.agent.md) | Full revision pipeline for post-submission reviewer feedback |
| [revise-paper.prompt.md](../../prompts/revise-paper.prompt.md) | `/revise-paper` command — orchestrates the revision specialist |
| [citation-verifier.agent.md](../../agents/citation-verifier.agent.md) | Citation integrity verification pipeline |
| [writing-quality-check.agent.md](../../agents/writing-quality-check.agent.md) | AI-tell detection and writing quality grading |
| [integrity-check.agent.md](../../agents/integrity-check.agent.md) | Content integrity gate and score trajectory tracking |
| [ai-failure-modes.md](./references/ai-failure-modes.md) | AI research failure modes checklist (Lu et al. 2026) |
| [coach-revision.prompt.md](../../prompts/coach-revision.prompt.md) | `/coach-revision` command — Socratic revision coaching |
| [final-audit.prompt.md](../../prompts/final-audit.prompt.md) | `/final-audit` command — fresh-context pre-submission check |
| [import-paper.prompt.md](../../prompts/import-paper.prompt.md) | `/import-paper` command — import external papers into the pipeline |
| [self-plagiarism-guard.agent.md](../../agents/self-plagiarism-guard.agent.md) | Self-plagiarism detection against prior publications |
| [check-plagiarism.prompt.md](../../prompts/check-plagiarism.prompt.md) | `/check-plagiarism` command — overlap check against prior papers |

## Tips

- Drop PDF, Markdown, or plain-text versions of sources into `sources/` — the system handles all formats.
- The `output/knowledge/` folder is your persistent memory — never delete it between sessions.
- Add user overrides to `output/knowledge/style-profile.md` to correct any style patterns the learner missed.
- For a paper targeting a venue not listed in `venue-families.md`, place the raw guidelines in `sources/venues/` and the compliance checker will parse them.
- After every completed paper, the agent appends a structured entry to `output/knowledge/session-learnings.md`. This file accumulates lessons about section depth, quality patterns, compliance failures, and venue quirks. The agent reads it at the start of every new session and applies the lessons automatically — the more papers you write, the better the drafts get on the first pass.
