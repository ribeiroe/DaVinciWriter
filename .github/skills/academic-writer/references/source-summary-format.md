# Source Summary Format

Each ingested source document is summarized using the following structure and saved to `output/knowledge/sources/<sanitized-filename>.md` (derived from the source file name, lowercased and hyphenated — not from the title).

Length caps: thesis summary ≤ 1500 words, paper summary ≤ 600 words, artefact summary ≤ 400 words — dense over complete; when trimming, keep claims, evidence, and exact numbers first.

```markdown
# <Title>

**Authors**: Firstname Lastname, Firstname Lastname
**Year**: YYYY
**Venue**: Conference Name / Journal Name
**Type**: thesis | conference paper | journal article | preprint
**DOI / URL**: https://doi.org/...

## Key Contributions
- Contribution one (one sentence each)
- Contribution two

## Methodology
- Step or component description
- Datasets used
- Training or experimental setup (briefly)

## Datasets / Experiments
- Dataset name: description, size, domain
- Baseline methods compared against

## Main Results
- Metric: X.XX (standard benchmark, condition)
- Improvement over baseline: +Y%

## Limitations
- Stated limitation one
- Stated limitation two

## Quotable Passages
> "Exact verbatim quote from the paper." (page X / section Y)

## BibTeX
@inproceedings{Key2023Title,
  author    = {Lastname, Firstname and Lastname, Firstname},
  title     = {Full Paper Title},
  booktitle = {Proceedings of Conference Name},
  year      = {2023},
  pages     = {100--110},
  doi       = {10.0000/...}
}

## Quality Assessment

| Dimension | Assessment | Notes |
|---|---|---|
| Publication tier | Top venue / Reputable / Workshop / Preprint / Thesis | Based on venue reputation |
| Recency | Current (≤3 years) / Recent (3–5 years) / Dated (>5 years) | Relative to current year |
| Methodological rigor | Strong / Adequate / Weak | Study design, sample size, statistical methods |
| Evidence strength | Empirical (quantitative) / Empirical (qualitative) / Conceptual / Survey | Type of evidence |
| Relevance | Primary / Supporting / Contextual | How central to paper being written |
| Recommended usage | Foreground / Background / Context-only | Citation prominence guidance |
```

## Field Guidelines

| Field | Notes |
|-------|-------|
| **Authors** | Full names as they appear in the paper |
| **Type** | Use "thesis" for both Master's and PhD; specify in parentheses if relevant |
| **Key Contributions** | 2–5 bullets; each starts with a verb ("Proposes...", "Demonstrates...") |
| **Quotable Passages** | Verbatim only — never paraphrase in this field |
| **BibTeX key** | Format: `<FirstAuthorLastName><Year><FirstSignificantTitleWord>` |

## Example

```markdown
# Attention Is All You Need

**Authors**: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
**Year**: 2017
**Venue**: Advances in Neural Information Processing Systems (NeurIPS)
**Type**: conference paper
**DOI / URL**: https://arxiv.org/abs/1706.03762

## Key Contributions
- Proposes the Transformer, a sequence-to-sequence model relying entirely on attention mechanisms without recurrence or convolutions.
- Demonstrates that multi-head self-attention enables parallelization and achieves superior translation quality.

## Methodology
- Encoder-decoder architecture with multi-head self-attention and position-wise feed-forward layers
- Positional encoding added to embeddings to retain sequence order
- Trained on WMT 2014 EN-DE and EN-FR translation tasks

## Main Results
- 28.4 BLEU on WMT 2014 EN-DE (new state of the art at time of publication)
- 41.8 BLEU on WMT 2014 EN-FR

## Limitations
- Quadratic complexity in sequence length limits applicability to very long sequences

## Quotable Passages
> "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely." (Abstract)

## BibTeX
@inproceedings{Vaswani2017Attention,
  author    = {Vaswani, Ashish and Shazeer, Noam and ...},
  title     = {Attention Is All You Need},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2017},
  pages     = {5998--6008}
}

## Quality Assessment

| Dimension | Assessment | Notes |
|---|---|---|
| Publication tier | Top venue | NeurIPS — premier ML venue |
| Recency | Dated (>5 years) | 2017, but foundational and still highly relevant |
| Methodological rigor | Strong | Large-scale experiments with clear ablations |
| Evidence strength | Empirical (quantitative) | BLEU scores on standard benchmarks |
| Relevance | Supporting | Foundational architecture, not direct comparison |
| Recommended usage | Background | Cite when discussing attention mechanisms |
```
