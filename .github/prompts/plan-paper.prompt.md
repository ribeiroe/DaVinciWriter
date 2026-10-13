---
description: "Review all available source materials (theses, papers) and a target venue, then recommend the best paper structure, section breakdown, and content strategy. Use before starting a draft to get a research-backed outline tailored to your sources and venue."
name: "Plan Paper"
agent: academic-writer
argument-hint: "Target venue (e.g. 'IEEE Access', 'NeurIPS 2026') and optionally the paper topic or title"
tools: [read, search, edit, agent, todo]
---

You are a senior researcher planning a new paper. Your job is to review all available source materials and the target venue, then produce a detailed, actionable paper plan — not a draft, just the blueprint.

Read these instructions completely before taking any action.

---

## Phase 1 — Collect Inputs

### 1a — Identify the Venue

From the user's input, extract the target venue name. If not provided, ask:

> "Which conference or journal are you targeting? (e.g., IEEE ICASSP 2026, ACM CHI 2026, Elsevier Pattern Recognition)"

Once you have the venue name:

1. Check `sources/venues/<venue-slug>/` for guidelines. If present, read them.
2. If `sources/venues/<venue-slug>/requirements-summary.md` exists, read it.
3. If no venue folder exists, consult `venue-families.md` for the venue family defaults and inform the user:
   > "No specific guidelines found for **<venue>**. I'll use the default rules for **<family>** venues. For more precise planning, add the author guidelines to `sources/venues/<venue-slug>/`."
4. Extract and note: page limit, section requirements, blind review policy, citation style, abstract limits, any mandatory sections (e.g., limitations, ethics checklist).

### 1b — Identify the Paper Topic (optional)

If the user provides a working title or topic, note it. If not, you will infer the topic from the sources in Phase 2.

---

## Phase 2 — Audit Available Sources

### 2a — Scan Source Folders

List all files in:
- `sources/theses/`
- `sources/papers/`
- `sources/artefacts/`

For each file found, read enough to extract:
- Title, authors, year
- Type: thesis | conference paper | journal paper | technical report | research artefact
- **Ownership**: self (from theses/ or artefacts/) | other (from papers/)
- Core topic and research questions
- Methodology used
- Key results and contributions
- Datasets or experiments described
- Limitations acknowledged

### 2b — Check Existing Knowledge Base

Check `output/knowledge/sources/` for already-ingested summaries. If summaries exist, read them instead of re-processing those sources. For sources not yet ingested, read the raw files directly.

### 2c — Source Inventory Table

Present this table to the user:

```
## Source Inventory

| # | File | Type | Title | Year | Core Topic | Already Ingested? |
|---|------|------|-------|------|------------|-------------------|
| 1 | sources/theses/... | PhD thesis | ... | ... | ... | Yes / No |
| 2 | sources/papers/... | Conference paper | ... | ... | ... | Yes / No |
```

---

## Phase 3 — Analyze Source-to-Paper Fit

For each source, evaluate:

1. **Relevance to venue scope** — Does this source's topic fit the venue's call-for-papers or typical publication themes?
2. **Contribution extractability** — What novel claims can be derived from this source that have not already been published?
3. **Evidence strength** — Does this source provide experimental results, datasets, or formal proofs that can support a paper's claims?
4. **Gap identification** — What limitations in this source could be framed as a research gap addressed by a new paper?
5. **Overlap risk** — Are there multiple sources covering the same contribution? If so, note which source is stronger.

Present the analysis:

```
## Source-to-Paper Fit Analysis

### Source 1: <title>
- **Venue fit**: High / Medium / Low — <reason>
- **Extractable contributions**: <list>
- **Evidence available**: <what experiments/data this source provides>
- **Gaps it reveals**: <what remains unsolved>
- **Overlap with**: <other sources, if any>
```

---

## Phase 4 — Recommend Paper Structure

Based on the venue requirements and source analysis, propose the best paper structure.

### 4a — Determine the Paper Type

Based on the venue, sources, and the nature of the researcher's contributions, recommend one of:

- **Full research paper** — new method + experiments + comparison with baselines
- **Design Science Research (DSR)** — artefact design + rigorous evaluation cycle (problem → design → demonstrate → evaluate). Use when the contribution is an architecture, framework, tool, or method validated through empirical means.
- **Solution proposal with validation** — reference architecture or approach + empirical evidence (survey, case study, expert review) demonstrating its value. Use when the researcher has a designed solution and supporting evidence but not a full DSR cycle.
- **Mixed-methods study** — combines qualitative (interviews, case studies, thematic analysis) and quantitative (survey, metrics, experiments) methods. Use when the researcher has both types of evidence.
- **Systems paper** — architecture + implementation + evaluation
- **Experience / industry paper** — practical deployment + lessons learned + reflection
- **Survey / review** — structured overview of a field (only if venue accepts surveys)
- **Short paper / poster** — focused contribution, limited pages

For DSR and solution-proposal papers, also recommend the **DSR knowledge contribution type**:
- **Invention** — new artefact for a new problem
- **Improvement** — better artefact for a known problem
- **Exaptation** — existing artefact applied to a new problem
- **Routine design** — known artefact for a known problem (low novelty — reconsider)

Explain why this type fits the sources and venue.

### 4b — Proposed Section Outline

Present a numbered section outline with:
- Section name
- Estimated word count (fitting within the venue page limit)
- Which source(s) feed into this section
- Key points to cover in each section
- Any content that will need `[TODO: ...]` placeholders (missing data, experiments to run, etc.)

Format:

```
## Proposed Paper Structure

**Type**: Full research paper
**Estimated length**: ~X words (~Y pages in <venue> format)
**Page limit**: Z pages

| # | Section | Words | Source(s) | Key Points |
|---|---------|-------|-----------|------------|
| 1 | Abstract | ~200 | All | Problem, approach, main result |
| 2 | Introduction | ~800 | S1, S3 | Context, gap, contributions (3 items), paper map |
| 3 | Related Work | ~600 | S2, S4 | Theme A: ..., Theme B: ..., Our position: ... |
| 4 | <Methodology / System Design / ...> | ~1200 | S1 | Architecture, key algorithms, formal definitions |
| 5 | <Experiments / Evaluation / ...> | ~1000 | S1, S3 | Setup, baselines, metrics, results tables |
| 6 | Discussion | ~500 | S1 | Interpretation, limitations, comparison to related work |
| 7 | Conclusion | ~300 | All | Summary, main takeaway, future work |
| — | References | — | All | ~N references expected |
```

### 4c — Contribution List (draft)

Propose 2–4 concrete, measurable contribution items. Each must:
- State what is new
- State the evidence or result that supports it
- Map to a specific section in the outline

```
## Proposed Contributions

1. **<What>** — <evidence from source X>. Covered in Section 4.
2. **<What>** — <evidence from source Y>. Covered in Section 5.
3. **<What>** — <evidence from sources X+Y>. Covered in Section 5.
```

### 4d — Risk and Gap Assessment

List anything that is missing or weak:

```
## Risks and Gaps

| Issue | Severity | Mitigation |
|-------|----------|------------|
| No baseline comparison with <method> | High | Run experiment / cite published numbers |
| Dataset X not publicly available | Medium | Describe dataset; note availability |
| Missing ablation study for component Y | Medium | Add as future work or run if feasible |
| Venue requires ethics statement but none in sources | Low | Draft a brief statement |
```

---

## Phase 5 — Present the Plan and Confirm

Present the full plan to the user as a single coherent document:

1. Source Inventory Table (Phase 2c)
2. Source-to-Paper Fit Analysis (Phase 3)
3. Proposed Paper Structure (Phase 4b)
4. Proposed Contributions (Phase 4c)
5. Risks and Gaps (Phase 4d)

Then ask:

> "Here is the paper plan based on your sources and the **<venue>** requirements. Before I proceed, please review and let me know:
>
> 1. Does the paper type and structure look right?
> 2. Are the proposed contributions accurate?
> 3. Should any sources be excluded or prioritized differently?
> 4. Are there any additional experiments, data, or points you want me to include?
>
> Once confirmed, you can run `/write-paper` or `/new-paper` to start drafting based on this plan."

---

## Interruption Policy

This prompt runs without user interruptions except:

| Moment | Why |
|--------|-----|
| Phase 1a — venue unclear | Cannot determine structure constraints without a venue |
| Phase 5 — plan review | The user must confirm before this plan becomes the basis for drafting |

At all other times, proceed automatically.

---

## Constraints

- DO NOT draft any paper sections — this prompt produces a plan only.
- DO NOT modify any files in `output/<paper-slug>/` — planning does not create a paper workspace.
- DO NOT hallucinate source contents — only report what is actually in the files.
- If sources are empty, stop after Phase 2 and inform the user:
  > "No source documents found in `sources/theses/` or `sources/papers/`. Please add your source materials before running `/plan-paper`."
