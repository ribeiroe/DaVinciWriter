---
description: "Use when formatting in-text citations, reference lists, or bibliographies in academic papers. Covers IEEE, ACM, APA, and Springer/Elsevier citation conventions."
applyTo: "**"
---

# Citation Standards

## BibTeX Best Practices

- Use consistent, readable citation keys: `<FirstAuthorLastName><Year><FirstTitleWord>` (e.g., `Smith2023Attention`).
- Ensure all entries have the mandatory fields for their type (see below).
- Protect capitalization in titles with braces: `{BERT}`, `{GPT-4}`.
- Use `@string` macros for repeated venue names to ensure consistency.

## Mandatory Fields by Entry Type

| Type | Mandatory Fields |
|------|-----------------|
| `@article` | author, title, journal, year, volume, number, pages |
| `@inproceedings` | author, title, booktitle, year, pages |
| `@phdthesis` | author, title, school, year |
| `@mastersthesis` | author, title, school, year |
| `@techreport` | author, title, institution, year, number |
| `@misc` (preprint) | author, title, year, howpublished (arxiv URL) |

## IEEE Style (numbered citations)

- In-text: `[1]`, `[1, 2]`, `[1]–[3]`
- Reference list: numbered, sorted by order of appearance
- Journal abbreviations: use IEEE-standard abbreviations (e.g., *IEEE Trans. Neural Netw. Learn. Syst.*)
- Conference: *Proc. IEEE ICASSP*, *Proc. CVPR*

## ACM Style (numbered citations)

- In-text: `[1]`, `[1, 2]`
- Reference list: numbered, sorted alphabetically by first author
- Use ACM Digital Library DOI links when available

## APA Style (author-year)

- In-text: `(Smith, 2023)`, `(Smith & Jones, 2023)`, `(Smith et al., 2023)` for 3+ authors
- Reference list: sorted alphabetically by first author, then by year

## Springer / Elsevier

- Typically numbered; follow the specific journal template
- Use `et al.` after 3 authors in reference lists for Elsevier; after 6 for many Springer journals

## Do Not

- Do NOT cite any work that was not ingested from `sources/papers/`, `sources/theses/`, or `sources/artefacts/` (grey literature, cited as `@techreport`) and does not have a summary in `output/knowledge/sources/`. This is the single most important citation rule.
- Do NOT invent, hallucinate, or fabricate references — not even well-known papers. If the source was not provided by the user, it cannot be cited.
- Do NOT create BibTeX entries from memory. Every entry must come verbatim from an ingested source summary.
- Do NOT cite arXiv preprints when a published version exists.
- Do NOT include URLs for papers available via DOI — use the DOI instead.
