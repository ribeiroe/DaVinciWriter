---
description: "Use when writing or reviewing any academic paper, scientific manuscript, or research article. Covers paper structure, scholarly argumentation, academic tone, technical precision, and peer-review readiness."
applyTo: "**"
---

# Academic Writing Standards

## Paper Structure

A full research paper follows this canonical structure (adapt to venue requirements):

1. **Abstract** — self-contained summary: problem, approach, results, significance
2. **Introduction** — motivation, gap, contributions, paper organization
3. **Related Work** — thematically grouped, positioned fairly against your work
4. **Methodology** — reproducible description of the proposed approach
5. **Experiments / Results** — setup, baselines, quantitative comparison
6. **Discussion** — interpretation, limitations, broader implications
7. **Conclusion** — contributions restated, future work
8. **References** — consistent, complete, venue-format compliant

## Argumentation Principles

- Every claim must be either self-evident, mathematically proven, empirically supported, or cited.
- Introduce a problem before proposing a solution; introduce a solution before evaluating it.
- Quantify limitations: "X% slower" is more useful than "somewhat slower".
- Distinguish between validation (does it work?) and evaluation (how well does it work?).

## Academic Tone

- Write in formal, hedged language: "results suggest" not "results prove".
- Avoid colloquialisms, contractions, and rhetorical questions.
- Use consistent tense: past for what you did (experiments), present for what the paper says and what the proposed system does.
- When using "we", keep it consistent throughout — do not mix with passive voice.

## Technical Precision

- Define every acronym at first use: "convolutional neural network (CNN)".
- Introduce mathematical notation in a definition before using it in equations.
- Units must always accompany numerical measurements (ms, %, dB, BLEU, etc.).
- Never use "significant" without a statistical test — prefer "substantial" or "notable".

## Citation Guidelines

- **Only cite works that have been ingested from `sources/papers/`, `sources/theses/`, or `sources/artefacts/` (grey literature, cited as `@techreport`) and have a summary in `output/knowledge/sources/`.** This is a hard constraint — no exceptions, no matter how relevant or well-known a paper may be.
- Do not invent, hallucinate, or fabricate any reference. If the source was not provided by the user, it cannot appear in the paper.
- Cite at the point of the claim, not at the end of the paragraph.
- When multiple ingested papers support the same claim, cite all of them.
- Avoid citing only your own previous work without also citing competing approaches (from ingested sources).
- If a claim needs a citation but no ingested source supports it, either rewrite the claim as a general statement without a citation, or mark it with `[CITATION NEEDED — <what is needed>]` for the user to provide.

## Results Integrity (hard rule)

- Every quantitative value in a manuscript — numbers, percentages, participant counts, effect sizes, timings, dataset statistics — must trace to an ingested source in `output/knowledge/sources/` or to material the user provided.
- Never invent, extrapolate, or "estimate" a quantitative result, and never imply an experiment was run that does not appear in the sources.
- When a needed value is missing, write the marker `[DATA NEEDED: <what is missing>]` in place of the number and continue.
- This rule outranks any instruction to expand, deepen, or complete a section.

## Common Mistakes to Avoid

- Burying the contribution — state it explicitly in the introduction.
- Comparing against outdated baselines — use the most recent competitive methods.
- Over-claiming — distinguish between "our model outperforms X on dataset Y" and "our model is the best".
- Under-specifying the experimental setup — a reader must be able to reproduce your results.
