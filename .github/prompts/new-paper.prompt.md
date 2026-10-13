---
description: "Start drafting a new paper when sources are already ingested and the venue is set. Collects topic, contributions, and target venue, creates the paper workspace, then launches the drafting workflow (skips source ingestion and style learning). Use /write-paper instead if sources have not been ingested yet."
name: "New Paper"
agent: academic-writer
argument-hint: "Paper title or topic (e.g. 'a paper on transformer-based speech enhancement for INTERSPEECH 2026')"
tools: [read, search, edit, agent, todo]
---

You are starting a new scientific paper. Sources should already be ingested (`output/knowledge/sources/` should contain summary files). If no sources are ingested, tell the user to run `/write-paper` instead (which includes ingestion) or `/ingest-sources` first.

## Step 1 — Collect Paper Details

Ask the user for the following (if not already provided):

1. **Working title or topic** — e.g., "Efficient Attention Mechanisms for Low-Resource NLP"
2. **Key contributions** — list the 2–4 main claims or novel aspects of this paper
3. **Target venue (MANDATORY)** — conference or journal name (e.g., "IEEE ICASSP 2026", "IEEE Access", "Elsevier Pattern Recognition"). This is **required** for page budgeting, formatting, citation style, and the compliance check. **Do NOT proceed to Step 2 until the user has confirmed a specific venue.** If the user is unsure, help them decide based on their topic and sources.
4. **Custom section names** (optional) — Does the user want non-standard section names? If not specified, use the default 8-section structure.

## Step 2 — Validate Prerequisites

Check that:
- [ ] At least one ingested source summary exists in `output/knowledge/sources/` — if not, stop and tell the user to run `/write-paper` or `/ingest-sources` first
- [ ] Venue guidelines exist in `sources/venues/` — if not, ask the user to add them or run `/set-venue` first
- [ ] `sources/venues/<venue-slug>/page-budget.md` exists — if not, auto-generate it now (target = page limit − 1)

## Step 3 — Create Paper Workspace

Create the folder `output/<paper-slug>/` where `<paper-slug>` is the title lowercased and hyphenated (e.g., `efficient-attention-nlp`).

Create `output/<paper-slug>/brief.md` with the collected information:

```markdown
# Paper Brief

**Title**: ...
**Venue**: ...
**Key Contributions**:
1. ...
2. ...
3. ...

**Sources Used**: [list]
**Style Profile**: [yes/no]
```

## Step 4 — Launch Workflow

Hand off to the `academic-writer` agent with the full brief and source paths.
