# DaVinci — Academic Paper Writing System

An AI-powered multi-agent system that assists a senior researcher in authoring publication-ready scientific papers. It ingests academic sources (theses, papers, research artefacts), learns your writing style, respects target venue formatting requirements, and produces manuscripts suitable for conference or journal submission.

## Agent Overview

| Agent | Role | Invocable |
| ------- | ------ | ----------- |
| `academic-writer` | Orchestrator — drives the end-to-end workflow; includes gap-statement stress-test, pre-empted objections, and mid-pipeline reinforcement protocol | User |
| `source-ingestion` | Reads and digests academic sources (with quality assessment and ownership tagging) | Subagent only |
| `style-learner` | Analyzes your previous papers to capture your voice and argumentation patterns | Subagent only |
| `paper-writer` | Drafts individual paper sections with claim-to-source tracing, canonical reference registry, statistical rigour checks, and knowledge isolation (anti-leakage) protocol | Subagent only |
| `compliance-checker` | Validates the manuscript against venue requirements; checks citation density, generates ethics statement, AI disclosure, and reproducibility checklist | Subagent only |
| `reviewer-simulator` | Simulates peer review from 4 personas (methodologist, domain expert, skeptic, reproducibility auditor) with anti-sycophancy protocol | Subagent only |
| `revision-specialist` | Revises a submitted paper based on real peer reviewer feedback; audits all source folders, builds a reviewer response matrix, rewrites the manuscript directly, and produces 7 structured output reports | Subagent only |
| `citation-verifier` | Verifies all references are real, traceable to ingested sources, and correctly attributed; flags fabricated citations | Subagent only |
| `writing-quality-check` | Detects AI-generated writing patterns, overused filler words, and stylistic issues; produces quantified quality report | Subagent only |
| `integrity-check` | Content integrity gate + score trajectory tracking; verifies cross-section consistency, temporal integrity, AI research failure modes, and scores paper quality over time | Subagent only |
| `self-plagiarism-guard` | Compares new paper against author's prior publications; flags textual overlap that would trigger iThenticate/Turnitin | Subagent only |

## Workspace Structure

```text
sources/
  theses/              ← Master's and PhD theses to use as primary sources (ownership: self)
  artefacts/           ← Your unpublished materials: design docs, survey data, architectures, experimental results (ownership: self)
  papers/              ← Reference and related-work papers by other authors (ownership: other)
  my-papers/           ← Previously written papers (style learning only)
  venues/              ← Conference/journal guidelines, templates, and call-for-papers
  submitted-papers/    ← Papers written externally (PDF/TXT/MD) for import into the pipeline
  reviewer-feedback/   ← Real reviewer comments received after submission (one file per review round)
  my-response-letters/ ← Previously written rebuttal/response letters (response-letter style learning)
output/                ← Generated manuscript drafts and compliance reports
```

## Quick Start

### For beginners

Just type one command — the system will guide you through everything:

```text
> /start
```

See [QUICKSTART.md](docs/QUICKSTART.md) for a visual 3-step guide.

### Automated (recommended)

Run a single command to execute every phase automatically:

```text
> /write-paper
```

This drives the entire pipeline — source ingestion, style learning, drafting, the self-plagiarism check (Phase 5e), the integrity gate (Phase 5f), compliance checking with citation verification (Phase 6), revision, and peer review simulation — with minimal interruptions: the only pre-drafting pauses are venue confirmation and a single consolidated Paper Plan approval (after Phase 4e), and the 5e/5f loops run at most 2 automated cycles before escalating to you.

To improve and extend an existing draft to publication-ready length and quality:

```text
> /improve-paper
```

### Manual (step-by-step)

1. **Ingest sources** — Run `/ingest-sources` and point it at `sources/theses/`, `sources/papers/`, or `sources/artefacts/`.
2. **Learn your style** — Run `/learn-style` and point it at `sources/my-papers/`.
3. **Set the venue** — Run `/set-venue` with the target conference or journal name and drop its guidelines into `sources/venues/`.
4. **Set page budget** — Run `/set-page-budget` to compute per-section word targets that keep the paper one page under the limit.
5. **Plan the paper** — Run `/plan-paper` to review your sources and get a recommended structure, contributions, and gap analysis for the venue.
6. **Write the paper** — Run `/new-paper` to start the drafting workflow (sources must already be ingested). Or use `/write-paper` for the full pipeline including ingestion.
7. **Improve the paper** — Run `/improve-paper` to deepen, expand, and polish an existing draft to meet venue page requirements.
8. **Simulate peer review** — Run `/simulate-review` to get realistic feedback from four simulated reviewer personas (the fourth, a reproducibility auditor, applies to empirical papers only) before actual submission.
9. **Revise after peer review** — Run `/revise-paper` to systematically revise a submitted paper based on real reviewer feedback. Audits all sources, builds a reviewer response matrix, rewrites the manuscript, and produces a change log and remaining-risks report.
10. **Verify citations** — Run `/verify-citations` to check that all references are real, traceable, and correctly attributed.
11. **Check writing quality** — Run `/check-quality` to detect AI-generated patterns, overused terms, and style deviations.
12. **Literature review** — Run `/lit-review` to produce a thematic literature map and gap analysis from ingested sources.
13. **Convert format** — Run `/convert-format` to convert a paper between venue formats (e.g., IEEE → Springer).
14. **Draft a rebuttal** — Run `/draft-rebuttal` to produce a point-by-point response to reviewer feedback.
15. **Integrate feedback** — Run `/get-feedback` to process and apply co-author or advisor comments.
16. **Plan publication agenda** — Run `/plan-agenda` to identify extractable papers from your sources and sequence them.
17. **Prepare submission package** — Run `/prepare-submission` to generate cover letter, highlights, suggested reviewers, and checklists.
18. **Coach revision** — Run `/coach-revision` for Socratic revision coaching that guides you through reviewer comments one by one, building a revision plan collaboratively.
19. **Final audit** — Run `/final-audit` for a fresh-context verification pass that re-reads the entire paper from scratch before submission to catch accumulated issues.
20. **Import paper** — Run `/import-paper` to bring an externally-written paper (PDF, TXT, MD) into the workspace. Splits it into section files in `output/<paper-slug>/` ready for revision, quality checking, or improvement.
21. **Check self-plagiarism** — Run `/check-plagiarism` to compare your new paper against previously published papers in `sources/my-papers/` and flag textual overlap.

## Conventions

- All manuscript drafts are written to `output/` as Markdown (`.md`) files.
- Section files follow the pattern `output/<paper-slug>/<section>.md`.
- A compliance report is written to `output/<paper-slug>/compliance-report.md` after each draft.
- Citations are collected in `output/<paper-slug>/references.bib` (BibTeX format).
- Ingested source summaries are stored in `output/knowledge/sources/` so they persist between sessions (length-capped: thesis ≤1500 words, paper ≤600, artefact ≤400). **Do not delete this folder.**
- Style profiles are stored in `output/knowledge/style-profile.md`. **Do not delete this file.**
- Response-letter style profiles are stored in `output/knowledge/response-letter-profile.md`. Created automatically when files exist in `sources/my-response-letters/`. Applied to all rebuttal drafts.
- The canonical reference registry is stored in `output/knowledge/canonical-refs.md`. Created automatically on first use.
- A novelty matrix (gap statements + pre-empted objections) is written to `output/<paper-slug>/novelty-matrix.md`.
- A reproducibility checklist is written to `output/<paper-slug>/reproducibility-checklist.md` by the compliance checker.
- When processing real peer review feedback, the `/revise-paper` pipeline writes the reviewer response matrix to `output/<paper-slug>/reviewer-response-matrix.md`, and `/draft-rebuttal` writes the rebuttal letter to `output/<paper-slug>/rebuttal-draft.md`.
- When running `/revise-paper`, the revision specialist writes: `reviewer-response-matrix.md`, `full-paper-revised.md`, `revision-change-log.md`, `remaining-risks.md`, `source-folder-assessment.md`, `source-utilisation-audit.md`, and `gap-analysis.md` — all under `output/<paper-slug>/`.
- Real reviewer comments should be saved to `sources/reviewer-feedback/` for traceability across revision rounds. Supports `.md`, `.txt`, and `.pdf` files (e.g., `<paper-slug>-round-1.md` or a forwarded PDF from the venue).
- A citation verification report is written to `output/<paper-slug>/citation-verification-report.md` by the citation verifier.
- A writing quality report is written to `output/<paper-slug>/writing-quality-report.md` by the quality checker.
- A quality scorecard is maintained at `output/<paper-slug>/quality-scorecard.md` by the integrity checker (appended with each run).
- An AI disclosure statement is generated at `output/<paper-slug>/ai-disclosure.md` by the compliance checker when required by venue.
- Literature reviews are saved to `output/knowledge/literature-review-<topic-slug>.md`.
- A final audit report is written to `output/<paper-slug>/final-audit-report.md` by the `/final-audit` command.
- A revision plan is written to `output/<paper-slug>/revision-plan.md` by the `/coach-revision` command.
- The AI research failure modes reference is at `.github/skills/academic-writer/references/ai-failure-modes.md`.

## Agent Capabilities

### `academic-writer` (Orchestrator)

- **Gap Statement Stress-Test** — Before drafting, for each stated contribution the orchestrator forces identification of: (1) the strongest competing prior work, (2) a measurable differentiator, and (3) a one-sentence gap statement. Contributions that cannot be differentiated are flagged `[GAP NOT CONFIRMED — author input required]`.
- **Pre-empted Objections** — Records the adversarial reviewer objection for each contribution in `output/<paper-slug>/novelty-matrix.md` under `## Pre-empted Objections`, so rebuttal preparation starts before submission.
- **Mid-Pipeline Reinforcement Protocol** — At every major phase transition (before drafting, compliance, and review simulation), re-injects critical rules (anti-leakage, citation integrity, style adherence, claim-source tracing) into the delegated agent's context. Prevents context drift in long sessions.

### `paper-writer` (Subagent)

- **Claim-to-Source Trace** — Every factual claim in a drafted section must trace to a specific passage in an ingested source summary. Claims with no traceable evidence are flagged `[UNSUPPORTED — author to verify]`; no audit comment is written into section files.
- **Canonical Reference Registry** — Reads `output/knowledge/canonical-refs.md` to ensure the same concept always resolves to the same BibTeX key. Creates the registry template if the file is absent.
- **Statistical Rigour Checklist** — Applied to every `### Experiments / Results` section: correct test selection (t-test, ANOVA, Pearson, Chi-square, Wilcoxon), effect sizes, confidence intervals alongside p-values, and named baselines. Missing baselines are flagged `[TODO: baseline required]`.
- **Knowledge Isolation (Anti-Leakage Protocol)** — Only uses workspace sources (`output/knowledge/sources/`) for factual content. Never fills gaps from parametric memory. Flags material gaps with `[MATERIAL GAP]` markers instead of fabricating content.

### `compliance-checker` (Subagent)

- **Citation Density Check** — Benchmarks the reference list count against venue family norms: IEEE 8-page ≈ 20–30, ACM CHI ≈ 25–40, journals ≈ 30–60. Flags both sparse and padded lists. Scans all sections for `[UNSUPPORTED]` markers left by the paper writer.
- **Baseline Completeness Flag** — Critical flag for empirical papers when no named baseline system or method appears in the results section.
- **Statistical Rigour Flag** — Warns when p-values appear without effect sizes or confidence intervals.
- **Ethics Statement Generator** — Auto-generates a ready-to-use ethics statement with two templates (human subjects / technical artefacts only), marked `[AUTHOR: review and confirm]`.
- **Reproducibility Checklist** — Creates `output/<paper-slug>/reproducibility-checklist.md` covering code availability, dataset description, hyperparameters, seeds, compute environment, evaluation protocol, and pre-registration status.

### `reviewer-simulator` (Subagent)

- **Reviewer 3 — The Skeptic** — Now required to produce a verbatim *Strongest Objection* statement: *"The fundamental weakness of this paper is that [specific claim] is not supported by [specific missing evidence], which means [consequence for validity]."*
- **Reviewer 4 — The Reproducibility Auditor** *(empirical papers only)* — Fourth persona focused exclusively on: hyperparameter completeness, dataset description adequacy, statistical test appropriateness, random seeds, hardware specs. Skipped for purely theoretical papers.

### `style-learner` (Subagent)

- **Manuscript style profile** — Analyzes papers in `sources/my-papers/` and produces `output/knowledge/style-profile.md` covering voice, tone, sentence structure, argumentation patterns, hedging, and citation style.
- **Response-letter style profile** — Analyzes rebuttal/response letters in `sources/my-response-letters/` and produces `output/knowledge/response-letter-profile.md` covering opening formula, tone, push-back strategy, concession pattern, change-announcement style, response length, reviewer labeling, and closing formula. Applied automatically by `/draft-rebuttal` and `/revise-paper`.

### `/get-feedback` — Co-Author/Advisor Feedback

- **Single purpose** — `/get-feedback` handles freeform co-author or advisor feedback only: parse and map comments to sections, propose specific edits, apply accepted ones, and track everything in `output/<paper-slug>/feedback-tracker.md`.
- **Routing** — If the pasted feedback is a formal peer review (reviewer numbers, scores, decision language), the prompt says so and routes instead: `/draft-rebuttal` for the response letter and `/revise-paper` for the systematic revision.

### `revision-specialist` (Subagent)

- **Source Folder Audit** — Exhaustively inspects every folder in the workspace before revising. Identifies content that is present in the sources but missing from the paper. Produces a per-folder inventory with `[SOURCE UNUSED — candidate for revision]` flags.
- **Missing Folder Recommendations** — For each reviewer concern lacking supporting material, recommends creating a new folder (e.g., `sources/additional-experiments/`, `sources/ablation-studies/`, `sources/statistical-analysis/`) and explains what content to add and which reviewer comment it addresses.
- **Reviewer Response Matrix** — Builds `reviewer-response-matrix.md` mapping every reviewer comment to: interpretation, severity, action taken, sections updated, and evidence used.
- **Conflict Detection** — Identifies conflicting reviewer requests and proposes resolution strategies before revising.
- **Consistency Enforcement** — After revising any section, propagates changes to Abstract, Introduction, and Conclusion to eliminate cross-section inconsistencies.
- **Source Utilisation Audit** — Produces `source-utilisation-audit.md` listing used vs. unused sources, with reasons.
- **Gap Analysis** — Produces `gap-analysis.md` identifying unresolved concerns, missing evidence, missing experiments, weak arguments, and potential future reviewer objections.

### `citation-verifier` (Subagent)

- **Source Traceability Check** — Every BibTeX entry must trace back to at least one ingested source summary in `output/knowledge/sources/`. Entries with no trace are flagged `[FABRICATED]` or `[UNVERIFIABLE]`.
- **Metadata Consistency** — Compares BibTeX metadata (title, authors, year, venue) against source summaries. Flags mismatches.
- **Self-Citation Audit** — Reports self-citation count and percentage; flags rates exceeding 20%.
- **Citation Freshness Analysis** — Computes age distribution of references; flags stale literature reviews (fewer than 30% from last 5 years).
- **Orphan Detection** — Identifies citations in text with no BibTeX entry, and BibTeX entries never cited.

### `writing-quality-check` (Subagent)

- **AI-Tell Detection** — Scans for 30 high-frequency AI-generated terms (Moreover, Furthermore, Delve, Leverage, etc.) and reports per-section density.
- **Structural Pattern Detection** — Flags em dash overuse (>2 per 500 words), throat-clearing openers, triple-adjective stacking, and sentence length uniformity (burstiness deficit).
- **Hedging Analysis** — Detects over-hedging (>3 hedge phrases/page) and under-hedging (absolute claims without qualification).
- **Style Profile Deviation** — When style profile exists, compares sentence length, vocabulary, and argumentation patterns against the author's known style.
- **Per-Section Grading** — Each section receives a grade (A/B/C/D) based on AI-tell density and structural issues.
- **Substitution Table** — Provides concrete replacement suggestions for every flagged term.

### `integrity-check` (Subagent)

- **Cross-Section Consistency** — Verifies Abstract↔Conclusion alignment, Introduction claims↔Results, Methodology↔Results, RQ↔Results mapping. Flags contradictions.
- **Claim-Evidence Integrity** — Ensures factual claims trace to sources and quantitative claims match their sources.
- **Self-Contradiction Detection** — Scans for same metric reported with different values, conflicting limitation characterizations, and timeline inconsistencies.
- **Score Trajectory Tracking** — Scores the paper on 8 dimensions (Clarity, Evidence, Argumentation, Novelty Signal, Completeness, Flow, Technical Precision, Literature Integration) each 1–10. Tracks deltas across revision rounds. Flags regressions as mandatory checkpoints.
- **Gate Decision** — Mandatory gate run automatically as Phase 5f of the pipeline. Produces PASS / PASS WITH WARNINGS / FAIL verdict. Paper should not proceed to compliance check if FAIL. Critical failure-mode flags block submission; Major flags yield PASS WITH WARNINGS; Minor flags are informational.
- **Temporal Integrity Verification** — Checks for 5 temporal failure patterns: retrospective arithmetic errors, anachronistic citations, comparators that couldn't exist at experiment time, causal inversions, and deictic-present tense issues.
- **AI Research Failure Mode Check** — Screens for 7 failure modes from Lu et al. (2026): implementation bugs, hallucinated results, shortcut reliance, bug-as-insight reframing, methodology fabrication, frame-lock, and citation hallucination. Any critical flag blocks submission.

### `reviewer-simulator` — Anti-Sycophancy Protocol

- **Concession Threshold** — When the author pushes back on a criticism, the reviewer scores the rebuttal 1–5 and only concedes at score ≥4.
- **No Consecutive Concessions** — If the reviewer conceded on the previous point, they hold firm on the next unless evidence is overwhelming (score 5).
- **Escalation on Weak Rebuttals** — Score-1 rebuttals (bare assertions) cause the reviewer to *strengthen* their objection.
- **Structured Pushback Format** — Every response includes: Rebuttal Score, Verdict (Maintained/Partially Conceded/Conceded), Reasoning, and What Would Change My Mind.

### `compliance-checker` — AI Disclosure Generation

- **Venue-Specific AI Disclosure** — Auto-generates AI usage disclosure statements using venue-appropriate templates (IEEE, ACM, Nature/Science, NeurIPS/ICML, generic). Covers which tools were used and for what purpose.
- **Placement Guidance** — Specifies where the disclosure belongs (Acknowledgements, before References, Methods section, etc.) based on venue family.

### `self-plagiarism-guard` (Subagent)

- **Paragraph-Level Comparison** — Compares each paragraph in the new paper against all files in `sources/my-papers/` and `sources/theses/`. Detects verbatim reuse, paraphrased recycling, and structural cloning.
- **Section-Specific Thresholds** — Different acceptable overlap levels per section type: Introduction (30%), Related Work (40%), Methodology (50%), Results (20%), Conclusion (30%).
- **Thesis-to-Paper Detection** — Specifically checks for direct chapter-to-section lifts from thesis material, flagging passages likely indexed in institutional repositories.
- **Differentiation Analysis** — For each flagged passage, identifies what is genuinely new in this paper vs. the prior one, helping articulate distinct contributions.
- **Risk Classification** — 🔴 Critical (>80% verbatim), 🟠 High (50–80% paraphrased), 🟡 Moderate (30–50% structural), 🟢 Low (<30% acceptable).
- **Pipeline Integration** — Runs automatically at Phase 5e (after drafting and the coherence pass, before the integrity gate and compliance check) whenever `sources/my-papers/` or `sources/theses/` contains files. HIGH/CRITICAL risk triggers automatic rewrite of flagged sections.

## Supported Venue Formats

The compliance checker understands the following template families:

- **IEEE** — conferences (two-column) and transactions (journal)
- **ACM** — SIG proceedings and journals
- **Elsevier / Springer** — LaTeX and Word journal templates
- **Custom** — place raw guidelines in `sources/venues/` and the checker will parse them

## Tools Used

Agent frontmatter uses abstract tool names; each runtime maps them to its own tool IDs:

| Abstract name | Purpose | Claude Code | Web UI (Streamlit) |
| ------ | --------- | ------ | ------ |
| `read` | Read source documents and knowledge files | `Read` | `read_file`, `read_pdf` |
| `search` | Find related content within the workspace | `Grep`, `Glob` | `search_files`, `search_text` |
| `edit` | Write and update manuscript sections | `Edit`, `Write` | `write_file` |
| `agent` | Delegate to specialist subagents | `Task` | (inline — single conversation) |
| `todo` | Track paper sections and action items | `TodoWrite` | (pipeline tracker) |

The Web UI additionally provides `list_directory` and `verify_reference` (Crossref citation lookup). The `.claude/` wrappers are generated with the Claude Code column applied — see below.

## Web UI

A browser-based interface is available at `web/app.py` (Streamlit). Access it with:

```bash
cd web
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501. The Web UI provides:

- **4-step wizard** — Goal → Venue → Details → Write
- **📂 Sources Manager** — browse and preview all files in `sources/` subfolders; view ingested knowledge summaries
- **📝 Papers Editor** — select any generated paper, choose a section from the list, edit it in a full-height text area, and save to disk
- **Always-visible sidebar** — Workspace status, Completed papers list, Pipeline progress tracker (during generation), and labelled navigation buttons

## Usage with Claude Code

Claude Code support is native via generated wrappers in `.claude/`:

- `.claude/commands/<name>.md` — every prompt below is a real slash command
- `.claude/agents/<name>.md` — every agent is Task-invocable as a subagent

The wrappers are thin pointers; the `.github/` files remain the single source of
truth. After editing any `.github/agents/*.agent.md` or `.github/prompts/*.prompt.md`,
regenerate with:

```bash
python scripts/sync-claude.py          # regenerate
python scripts/sync-claude.py --check  # verify (runs in CI)
```

Run the orchestrator directly:

```text
> Use the academic-writer agent to write a paper titled "..." for IEEE ICASSP 2026.
```

Or invoke individual prompts:

```text
> /start
> /help
> /write-paper
> /improve-paper
> /plan-paper
> /set-page-budget
> /new-paper
> /ingest-sources
> /set-venue
> /learn-style
> /simulate-review
> /revise-paper
> /verify-citations
> /check-quality
> /lit-review
> /convert-format
> /draft-rebuttal
> /get-feedback
> /plan-agenda
> /prepare-submission
> /coach-revision
> /final-audit
> /import-paper
> /check-plagiarism
```
