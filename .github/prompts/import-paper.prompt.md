---
description: "Import an externally-written paper (PDF, TXT, or MD) into the DaVinci workspace. Extracts text, identifies sections, and creates structured section files in output/<paper-slug>/ ready for revision, quality checking, or resubmission workflows."
name: "Import Paper"
agent: academic-writer
argument-hint: "Path to the paper file (e.g. 'sources/submitted-papers/my-paper.pdf') and a slug name (e.g. 'certia360-ieee-access')"
tools: [read, search, edit, agent, todo]
---

You are importing an externally-written paper into the DaVinci workspace so it can be revised, checked, or improved using the full agent pipeline.

Read these instructions completely before taking any action.

---

## Phase 1 — Locate and Read the Paper

1. Ask the user (or determine from their input) the **file path** of the paper to import.
   - Check `sources/submitted-papers/` first
   - Also check `sources/artefacts/` and `sources/theses/`
   - The user may provide any path in the workspace

2. Determine the **paper slug** — a short kebab-case identifier (e.g., `certia360-ieee-access`). Ask the user if not provided.

3. Read the paper file:
   - **PDF files**: Attempt to read the file and extract the full text first — PDF support varies by runtime, so try before assuming it will fail. Only if extraction actually fails, ask the user:
     > "I couldn't extract text from this PDF. Please convert it to text first (`pdftotext paper.pdf paper.txt`) or paste the content into a `.txt` file."
   - **TXT/MD files**: Read directly.

---

## Phase 2 — Identify Sections

Parse the paper text and identify standard academic sections. Look for headings such as:
- Abstract
- Introduction
- Related Work / Background / Literature Review
- Methodology / Approach / Method / Design
- Implementation
- Results / Experiments / Evaluation / Validation
- Discussion
- Conclusion
- References / Bibliography

Also identify:
- The paper title
- Author list (if visible — for venue compliance later)
- Any numbered section scheme (e.g., "1. Introduction", "II. METHODOLOGY")

---

## Phase 3 — Create Section Files

Create the output directory and split the paper into individual section files:

```
output/<paper-slug>/
  abstract.md
  introduction.md
  related-work.md            (also used for Background / Literature Review content)
  methodology.md             (also used for Approach / Method / Design content)
  experiments-or-results.md  (also used for Evaluation / Validation content; fold Implementation here or into methodology.md as appropriate)
  discussion.md
  conclusion.md
  references.bib             (if extractable, otherwise references.md)
```

These unnumbered filenames are the canonical section set that the rest of the pipeline (write-paper, improve-paper, and the agents) reads — do not use numbered prefixes. Section order is implied by the canonical reading order: abstract → introduction → related-work → methodology → experiments-or-results → discussion → conclusion.

**Rules:**
- Preserve the original text exactly — do NOT rewrite, improve, or rephrase anything
- Keep the section headings as H1 (`#`) in each file
- If the paper has a non-standard structure, adapt the filenames to match
- If you cannot reliably split (e.g., no clear headings), create a single `full-paper.md` and inform the user

---

## Phase 4 — Extract References

If the paper contains a reference list:
1. Attempt to convert it to BibTeX format → save as `references.bib`
2. If conversion is unreliable, save as `references.md` with the raw reference list
3. Flag: `[AUTHOR: verify BibTeX entries — auto-extracted from prose]`

---

## Phase 5 — Also Ingest as Source

Copy the paper's knowledge into the source ingestion pipeline:
- Create a source summary in `output/knowledge/sources/<paper-slug>-submitted.md` following the standard source summary format
- Mark ownership as `self`
- This ensures the revision specialist can trace claims back to the original submission

---

## Phase 6 — Report to User

Present a summary:

```
✅ Paper imported: <paper-slug>

Sections created:
  - abstract.md (XX words)
  - introduction.md (XX words)
  - ...

Total: ~XXXX words across N sections

Next steps:
  • /revise-paper — to revise based on reviewer feedback
  • /improve-paper — to expand and strengthen
  • /check-quality — to scan for AI-tells and integrity
  • /final-audit — for pre-submission verification
  • /simulate-review — to get simulated peer feedback
```

---

## Notes

- This prompt does NOT modify the paper content — it only structures it for the pipeline
- The original file in `sources/` remains untouched (immutable sources principle)
- For PDFs, recommend the user also keeps the PDF in `sources/submitted-papers/` for reference
- If the paper was co-authored, note this in the summary for blind-review awareness
