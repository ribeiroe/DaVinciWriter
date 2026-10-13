# Research Artefacts

Place your own unpublished materials here — internal reports, design documents, architecture descriptions, experimental results, technical notes, survey data, and any other self-authored material that drives your paper's **main contribution**.

## Accepted Formats

- Markdown (`.md`)
- Plain text (`.txt`)
- PDF (`.pdf`)

## What Goes Here (vs. Other Folders)

| Material | Put in | Reason |
|----------|--------|--------|
| Your architecture / design documents | `artefacts/` | Drives your contribution (Section: Methodology / Solution Design) |
| Your survey results or experimental data | `artefacts/` | Drives your validation (Section: Evaluation / Results) |
| Your internal technical reports | `artefacts/` | Supporting evidence for claims |
| Your research questions / problem statement | `artefacts/` | Frames the paper's scope |
| Published papers by **others** | `papers/` | Positioning and related work |
| Your own **published** papers | `my-papers/` | Style learning only (not content) |
| Your Master's / PhD thesis | `theses/` | Deep primary source (multi-chapter extraction) |

## How These Are Used

- Artefacts are ingested with **ownership = self** (the system knows this is YOUR work, not others').
- Content from artefacts drives the **main contribution sections**: Methodology, Solution Design, Validation, Results.
- Artefacts are NEVER placed in Related Work as "prior art" — they are your novel work.
- If an artefact is unpublished, it will be cited transparently as a technical report or referenced inline (see grey literature rules).

## Example Contents

```
artefacts/
  reference-architecture-v2.md
  survey-results-practitioners-2025.md
  experimental-setup-and-metrics.md
  design-rationale-notes.md
  rq-and-hypotheses.md
```

## Notes

- Run `/ingest-sources` after adding new files to update the knowledge base.
- Each artefact will be summarized and stored in `output/knowledge/sources/` with ownership tagged as "self".
