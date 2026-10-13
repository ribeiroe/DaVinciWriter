# Portfolio Tracker Format

The portfolio tracker persists at `output/knowledge/portfolio-tracker.md` across sessions. It maintains coherence across multiple papers from the same research programme.

## Schema

```markdown
# Portfolio Tracker

## Published Papers

| # | Paper Slug | Title | Venue | Status | Date |
|---|-----------|-------|-------|--------|------|
| 1 | paper-slug-here | Paper Title | Venue Name | Published / In-Progress / Planned | YYYY-MM |

## Terminology Registry

Consistent terms and acronyms used across the paper series:

| Term / Acronym | Definition | First Used In |
|---------------|-----------|---------------|
| TERM | Full definition | paper-slug |

## Source Material Coverage

Tracks which source chapters/files have been used in which papers:

| Source File | Used In | Sections | Notes |
|------------|---------|----------|-------|
| theses/my-thesis.pdf Ch.3 | paper-slug-1 | Methodology | Core framework |
| theses/my-thesis.pdf Ch.5 | paper-slug-2 | Results | Evaluation data |

## Self-Plagiarism Notes

Passages that overlap between papers — future papers must rewrite differently:

| Paper A | Paper B | Section | Overlap Type | Action Required |
|---------|---------|---------|-------------|----------------|
| paper-1 | paper-2 | Background | Paraphrased (40%) | Rewrite in paper-2 |
```

## Usage Rules

1. **Read at session start** — The orchestrator loads this file in Phase 0b to avoid cross-paper overlap.
2. **Update at session end** — Phase 11b updates status, adds terms, and records source usage.
3. **Never delete** — This file is persistent knowledge across the paper series.
4. **Status values**: `Published`, `In-Progress`, `Planned`, `Abandoned`.
5. **All agents** with `portfolio-tracker` references should check `if it exists` before reading — first-time users won't have it.
