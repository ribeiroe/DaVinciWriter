# AI Research Failure Modes Checklist

Based on Lu et al. (2026, Nature 651:914–919) — the first fully autonomous AI research system to publish through blind peer review (ICLR 2025 workshop, 6.33/10). Their Limitations section enumerates failure modes that any AI-assisted research pipeline inherits.

DaVinci uses this checklist at the integrity-check gate (Stages A5 + A6) to catch these patterns before submission.

## The 7 Failure Modes

### FM1 — Implementation Bug
**What it is**: Results that couldn't have come from the described method. A disconnect between what the methodology says was done and what the results show happened.

**Detection signals**:
- Results section reports outcomes impossible given the described methodology
- Metrics reported for experiments not described in methodology
- Performance numbers that violate theoretical bounds

**Example**: Paper claims a sorting algorithm runs in O(n), but the described algorithm clearly requires O(n log n).

---

### FM2 — Hallucinated Results
**What it is**: Numbers, statistics, or data that appear in the paper but have no traceable origin in any source material.

**Detection signals**:
- Quantitative claims that don't appear in any source summary
- Statistics cited without a corresponding source
- Precision of results exceeding what the described method could produce

**Example**: "Our method achieves 94.7% accuracy on the benchmark" — but no benchmark results appear in any ingested artefact.

---

### FM3 — Shortcut Reliance
**What it is**: A trivial or well-known approach presented as a novel contribution by renaming components.

**Detection signals**:
- The "novel" method is structurally identical to an existing approach in Related Work
- Novelty claims rest on terminology changes rather than algorithmic differences
- The contribution section uses superlatives but the method section is generic

**Example**: Standard CRUD system renamed "Autonomous Document Lifecycle Orchestrator" and presented as an architectural contribution.

---

### FM4 — Bug-as-Insight Reframing
**What it is**: An unexpected or incorrect result celebrated as a finding without investigating whether it's caused by a methodology flaw.

**Detection signals**:
- "Surprising" results presented positively without investigating alternative explanations
- Anomalous data points interpreted as evidence rather than errors
- No discussion of threats to validity for the surprising finding

**Example**: "Interestingly, removing the validation step improved accuracy by 15%" — without investigating whether this means the validation step was broken.

---

### FM5 — Methodology Fabrication
**What it is**: Methods described in detail but never actually executed. Results section has no data corresponding to the described methodology.

**Detection signals**:
- Methodology describes an experiment but Results has no corresponding data
- Evaluation plan mentions participants/datasets but no evidence of actual collection
- Future tense in methodology ("will be evaluated") left uncorrected

**Example**: Paper describes a user study protocol in detail but Results only contains automated metric evaluations.

---

### FM6 — Frame-Lock
**What it is**: The entire paper operates within a single rigid framing that was never questioned. Alternative perspectives are absent.

**Detection signals**:
- Every section frames the problem identically
- Discussion doesn't consider alternative interpretations
- No "limitations of our framing" or "alternative approaches" discussion
- Threats to validity section is generic boilerplate

**Example**: Paper assumes "more automation = better" throughout, without ever questioning whether the domain actually needs more automation.

---

### FM7 — Citation Hallucination
**What it is**: References that don't exist or are misattributed. The most directly verifiable failure mode.

**Detection signals**:
- Any `[FABRICATED]` or `[UNVERIFIABLE]` flag from the citation verifier
- BibTeX entries with no trace in `output/knowledge/sources/`
- Papers cited for claims they don't actually make

**Example**: "Smith and Jones (2024) demonstrated that..." — but no paper by Smith and Jones on this topic exists in any ingested source.

---

## Severity Classification

| Failure Mode | Severity | Consequence |
|---|---|---|
| FM1 | Critical | Results section is invalid |
| FM2 | Critical | Paper contains fabricated data |
| FM3 | Major | Contribution claim is fraudulent |
| FM4 | Major | Conclusions are unreliable |
| FM5 | Critical | Paper claims work not done |
| FM6 | Minor | Paper lacks depth; reviewer will flag |
| FM7 | Critical | Academic integrity violation |

## When to Apply

- **Mandatory**: Before any submission (integrity-check gate)
- **Recommended**: After each major revision round
- **Optional**: During improve-paper cycles

## Integration with DaVinci Pipeline

The integrity-check agent runs FM1–FM7 as check A6. Any Critical flag blocks the gate (FAIL verdict). Major flags produce PASS WITH WARNINGS. Minor flags are informational.
