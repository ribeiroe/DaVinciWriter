---
description: "Convert a paper's formatting between venue families (e.g., IEEE → Springer LNCS, ACM → Elsevier). Handles citation style conversion, section restructuring, page budget recalculation, and template compliance."
name: "Convert Format"
agent: academic-writer
argument-hint: "Paper slug and target venue (e.g. 'certia360-ieee-access to springer-emse')"
tools: [read, search, edit, agent, todo]
---

You are converting an existing paper draft from one venue format to another. This is common when a paper is rejected from one venue and resubmitted elsewhere, or when an author wants to expand a conference paper into a journal article.

Read these instructions completely before taking any action.

---

## Phase 1 — Identify Source and Target

From the user's input, determine:
- **Source paper**: slug in `output/<paper-slug>/`
- **Target venue**: slug in `sources/venues/<venue-slug>/`

Read:
1. All section files in `output/<paper-slug>/`
2. `output/<paper-slug>/references.bib`
3. Source venue guidelines: `sources/venues/<source-venue>/requirements-summary.md`
4. Target venue guidelines: `sources/venues/<target-venue>/requirements-summary.md`
5. Target page budget: `sources/venues/<target-venue>/page-budget.md` (if exists)

If the target venue doesn't have guidelines, ask the user to provide them or run `/set-venue`.

---

## Phase 2 — Conversion Analysis

Produce a conversion plan showing what needs to change:

```markdown
## Conversion Plan: <source-venue> → <target-venue>

### Format Changes
| Aspect | Source Format | Target Format | Action |
|---|---|---|---|
| Citation style | IEEE numbered [1] | APA (Author, Year) | Convert all citations |
| Column layout | Two-column | Single-column | Affects word count estimate |
| Page limit | 8 pages | 15 pages | Room to expand |
| Abstract limit | 200 words | 250 words | Minor expansion possible |
| Section naming | Roman numerals (I, II) | Numbered (1, 2) | Rename all sections |
| Blind review | No | Double-blind | Remove identifying info |

### Structural Changes
| Source Structure | Target Structure | Action |
|---|---|---|
| Combined Results+Discussion | Separate Results, Discussion | Split section |
| No Related Work (in Intro) | Dedicated Related Work section | Extract and expand |
| Missing Data Availability | Required | Add new section |

### Content Implications
- Page limit change: +7 pages → expand methodology and results
- Audience change: [e.g., "SE practitioners → empirical researchers"] → adjust framing
- Contribution expectations: [e.g., "practical contribution → empirical rigor needed"]
```

Present this plan to the user for approval before proceeding.

---

## Phase 3 — Citation Style Conversion

Convert all citations in the paper to the target venue's style:

| From | To | Rule |
|---|---|---|
| IEEE `[1]` | APA `(Author, Year)` | Map each number to its BibTeX entry's author+year |
| APA `(Author, Year)` | IEEE `[1]` | Number sequentially by first appearance |
| ACM inline `Author [Year]` | IEEE `[1]` | Convert to numbered |
| Any | Springer `[Author Year]` | Use abbreviated author + year |

Update `references.bib` format if needed (e.g., add/remove `url` fields, adjust field ordering).

---

## Phase 4 — Section Restructuring

Based on the target venue's required structure:

1. **Add missing sections** — create placeholder files for sections the target requires but source lacks (e.g., Data Availability, Threats to Validity, Limitations)
2. **Merge sections** — if target venue has fewer sections (e.g., conference → shorter format)
3. **Split sections** — if target has more granularity requirements
4. **Rename sections** — match target venue's naming conventions
5. **Reorder sections** — match target venue's expected order

---

## Phase 5 — Page Budget Recalculation

If the target venue has a different page limit:

1. Compute current word count per section
2. Load target page budget (or compute one using `/set-page-budget` logic)
3. For each section, determine: expand / keep / compress
4. Update section files with expansion/compression markers:
   - `<!-- EXPAND: +300 words needed to meet budget -->` 
   - `<!-- COMPRESS: -200 words needed to fit budget -->`

---

## Phase 6 — Blind Review Compliance

If converting from non-blind to double-blind:

1. Remove all author names, affiliations, and funding acknowledgements from body
2. Convert self-citations: "In our previous work [3]" → "Previous work [3] showed..."
3. Remove or anonymize institutional references
4. Flag any remaining identifying information

If converting from blind to non-blind:

1. Note that author information can be restored (user's responsibility)
2. Self-citations can be made explicit again

---

## Phase 7 — Write Converted Draft

Create a new output folder: `output/<paper-slug>-<target-venue>/`

Write all converted section files there. Do NOT overwrite the original paper.

Save a conversion report to `output/<paper-slug>-<target-venue>/conversion-report.md`:

```markdown
# Conversion Report

**Source**: <paper-slug> (<source-venue>)
**Target**: <target-venue>
**Date**: <today>

## Changes Made
1. [Citation style converted from IEEE to APA — N citations updated]
2. [Section "Background" renamed to "Related Work"]
3. [Data Availability section added (placeholder)]
4. ...

## Manual Actions Required
- [ ] [Expand methodology by ~500 words to meet page budget]
- [ ] [Add Threats to Validity content]
- [ ] [Verify blind review compliance — check for hidden author references]
- [ ] [Update abstract to match new venue's limit]

## Page Budget Status
| Section | Current Words | Target Words | Status |
|---|---|---|---|
| Introduction | 800 | 1200 | Needs expansion |
| ... | ... | ... | ... |
```

---

## Phase 8 — Run Compliance Check

After conversion, delegate to `compliance-checker` to validate the converted paper against the target venue:

> "Run a compliance check on `output/<paper-slug>-<target-venue>/` against venue `<target-venue>`."

Report any remaining issues to the user.

---

## Rules

- **Never delete the original** — always create a new folder for the converted version.
- **Preserve all content** — conversion should not lose information, only restructure it.
- **Flag uncertainties** — if a conversion decision is ambiguous, ask the user rather than guessing.
- **Citation conversion must be complete** — every single citation must be converted, no mixing of styles.
