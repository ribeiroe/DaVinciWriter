---
description: "Ingest one or more academic source files (papers, theses, artefacts) into the knowledge base. Run this before starting a new paper to populate the sources available for citation and reference."
name: "Ingest Sources"
agent: academic-writer
argument-hint: "Path to file(s) or folder to ingest (e.g. 'sources/theses/' or 'sources/artefacts/' or 'sources/papers/Smith2023.pdf')"
tools: [read, search, edit, agent]
---

You are ingesting academic sources into the knowledge base.

## Instructions

1. Identify the target path from the user's input, or default to processing `sources/theses/`, `sources/papers/`, and `sources/artefacts/`.

2. List all files in the target path(s).

3. For each file found, delegate to the `source-ingestion` agent:
   > "Ingest the file at `<path>`. Detect the source type (thesis vs. paper vs. artefact) and ownership (self for theses/artefacts, other for papers). Apply the appropriate extraction strategy. For theses, produce multi-chapter summaries with cross-cutting themes and citable claims. For artefacts, extract research questions, design content, validation potential, and recommended citation approach. For papers, produce the standard summary. Tag ownership in the quality assessment. Save the summary to `output/knowledge/sources/`."

4. After all files are processed, print a summary table:

   | File | Type | Ownership | Status | Summary Path |
   |------|------|-----------|--------|-------------|
   | ... | thesis | self | ✓ ingested | output/knowledge/sources/... |
   | ... | artefact | self | ✓ ingested | output/knowledge/sources/... |
   | ... | paper | other | ✓ ingested | output/knowledge/sources/... |
   | ... | — | — | ✗ failed | — |

5. Report total ingested count, breakdown by type (theses vs. papers vs. artefacts), ownership distribution, and any failures to the user.

## Notes

- Already-ingested sources (summary file already exists) will be skipped unless the user explicitly requests re-ingestion.
- To re-ingest a specific file, say: "Re-ingest `sources/papers/<filename>`".
- Source summaries accumulate across sessions — the `output/knowledge/sources/` folder is persistent.
- Theses produce richer summaries than papers (multi-chapter, with cross-cutting themes and citable claims). This extra depth is used during drafting to map thesis content to paper sections.
- Artefacts are tagged with ownership=self and include validation potential and recommended citation approach (inline-description, technical-report, or replication-package).
- Ownership tagging is critical: self-owned material drives your paper's contributions; other-owned material is used for positioning.
