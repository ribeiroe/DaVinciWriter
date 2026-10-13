# DaVinci — High-Level Architecture

## System Overview

DaVinci's agent system is **pure prompt engineering with no executable source code**: every agent, command, and rule is defined in Markdown, and the AI runtime (Claude Code / GitHub Copilot Workspace) interprets these definitions to orchestrate agents, tools, and knowledge stores that produce publication-ready scientific papers. An optional Streamlit Web UI (`web/`) provides a browser front end over the same workspace; it is the only executable code in the repository and is not required for the agent workflow.

---

## Component Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER / RESEARCHER                            │
│                                                                         │
│  Slash commands: /start  /help  /write-paper  /improve-paper             │
│                  /new-paper  /plan-paper  /set-page-budget               │
│                  /ingest-sources  /learn-style  /set-venue               │
│                  /simulate-review  /draft-rebuttal  /get-feedback        │
│                  /plan-agenda  /prepare-submission  /revise-paper         │
│                  /verify-citations  /check-quality  /lit-review           │
│                  /convert-format  /coach-revision  /final-audit           │
│                  /import-paper  /check-plagiarism                         │
└──────────────────────────────────┤──────────────────────────────────────┘
                                   │ invokes
                                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    .github/prompts/  (24 prompt files)                  │
│  Route the user command to the correct agent and inject initial context │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ delegates to
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               ORCHESTRATOR — academic-writer  (user-invocable)          │
│                                                                         │
│  Responsibilities                                                       │
│  • Collect paper requirements (title, venue, contributions)             │
│  • Drive the end-to-end pipeline                                        │
│  • Build source-to-section maps from ingested summaries                 │
│  • Auto-generate venue requirements and page budgets when missing       │
│  • Coordinate all subagents in the correct sequence                     │
│  • Iterate compliance → revision up to 5 times (convergence-based)       │
│  • Assemble full paper and deliver a final summary                      │
│                                                                         │
│  Always-active instructions (applied to every agent call)               │
│  ├── academic-writing.instructions.md   (structure & tone rules)        │
│  ├── citation-standards.instructions.md (BibTeX & format rules)         │
│  └── venue-compliance.instructions.md  (IEEE / ACM / Elsevier rules)    │
└──────┬──────────┬──────────┬──────────┬──────────┬───────────────────────┘
       │          │          │          │          │
  delegates  delegates  delegates  delegates  delegates
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ source-  │ │  style-  │ │  paper-  │ │compliance│ │ reviewer │
│ingestion │ │ learner  │ │  writer  │ │-checker  │ │-simulator│
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │            │
     ▼            ▼            ▼            ▼            ▼
Reads PDFs    Reads PDFs   Reads         Reads all    Reads all
in theses/    in my-papers/ knowledge/   draft .md    draft .md
artefacts/    Writes        sources/ &   files +      files +
& papers/     style-        style-       venue        sources +
Writes        profile.md    profile.md   requirements venue reqs
summaries     (merged,      Writes 8     Writes       Writes
(+quality     cumulative,   section .md  compliance-  peer-review-
+ownership)   +argumen-     files +      report.md    simulation
to            tation)       references   (+strengths) .md (+vuln.
knowledge/                  .bib                      register)
sources/
```

`/write-paper` is a thin automation wrapper over the `academic-writer` agent — the agent definition owns the full workflow; the prompt only routes the command and injects initial context.

---

## Agents — Responsibilities & Tools

| Agent | Type | Tools | Key Responsibility |
|---|---|---|---|
| `academic-writer` | Orchestrator | read, search, edit, agent, todo | Drives the end-to-end pipeline; sole user-facing agent. Includes gap-statement stress-test and novelty validation per contribution |
| `source-ingestion` | Subagent | read, search, edit | Extracts key concepts from theses/papers/artefacts → structured summaries with quality assessment and ownership tagging |
| `style-learner` | Subagent | read, search, edit | Cross-analyzes researcher's past papers → cumulative style profile with argumentation patterns |
| `paper-writer` | Subagent | read, edit, search | Drafts each of the 8 paper sections. Applies claim-to-source tracing, canonical reference registry, statistical rigour checklist, and baseline completeness rule |
| `compliance-checker` | Subagent | read, search, edit | Validates draft against venue rules; checks citation density, generates ethics statement and reproducibility checklist; produces pass/warn/fail report with strengths |
| `reviewer-simulator` | Subagent | read, search, edit | Simulates 4-persona peer review (methodologist, domain expert, skeptic, reproducibility auditor); produces vulnerability register and pre-empted objections for rebuttal prep |
| `revision-specialist` | Subagent | read, search, edit | Revises papers based on real peer reviewer feedback; audits all source folders, builds reviewer response matrix, rewrites manuscript |
| `citation-verifier` | Subagent | read, search, edit | Verifies all references are real, traceable to ingested sources, and correctly attributed; flags fabricated citations |
| `writing-quality-check` | Subagent | read, search, edit | Detects AI-generated writing patterns and overused filler; produces per-section quality grades with substitution table |
| `integrity-check` | Subagent | read, search, edit | Content integrity gate + score trajectory; verifies cross-section consistency, temporal integrity, and AI research failure modes |
| `self-plagiarism-guard` | Subagent | read, search, edit | Compares new paper against prior publications in `sources/my-papers/`; flags textual overlap with risk classification |

## Alternative Interfaces

| Interface | Location | Requires |
|-----------|----------|----------|
| VS Code + Copilot Chat | `.github/prompts/` (slash commands) | VS Code + GitHub Copilot subscription |
| Web UI (Streamlit) | `web/app.py` (shared logic in `web/davinci_core.py`) | Python 3.10+ and an Anthropic API key (or a local Ollama/LiteLLM endpoint). Includes 14 goal cards with a 4-step wizard (3 steps for goals that skip venue selection), Sources Manager, Papers Editor, Output Manager, Responsible AI page, System/Dark/Light themes, session persistence, model selection with cost tracking, and prompt caching |
| Docker | `Dockerfile`, `docker-compose.yml` | Docker — runs the Web UI on port 8501 |
| GitHub Codespaces | `.devcontainer/` | GitHub account (free tier works) |

---

## Data Flow — End-to-End Pipeline

```
Phase 0 — Requirements + Portfolio Load
  User provides: venue (mandatory), title/contributions (optional), abstract timing
  Load session-learnings.md and portfolio-tracker.md (if they exist)
         │
         ▼
Phase 1 — Prerequisites
  Bootstrap output/knowledge/sources/ directory if absent
  Validate sources (theses OR papers OR artefacts), venue guidelines, style learning opt-in
  Auto-generate requirements-summary.md and page-budget.md if absent
         │
         ▼
Phase 2 — Source Ingestion (with Quality Assessment + Ownership Tagging)
  sources/theses/*.pdf    ──┐  → source-ingestion (thesis mode: multi-chapter + quality, ownership=self)
  sources/artefacts/*.md  ──┤  → source-ingestion (artefact mode: RQs + validation potential, ownership=self)
  sources/papers/*.pdf    ──┤  → source-ingestion (paper mode: standard summary + quality, ownership=other)
                            │  → output/knowledge/sources/*.md (includes quality + ownership)
                            │
Phase 2b — Propose Paper Plan (if title/contributions not provided)
  Read all summaries → recommend paper type (DSR / solution proposal / mixed-methods / etc.)
  Propose: title, RQs, contributions, structure with ownership-aware source mapping
  Plan held for the consolidated Paper Plan approval (after Phase 4e)
                            │
Phase 3 — Style Learning (with Argumentation Patterns)
  sources/my-papers/*.pdf ┘  →  style-learner  →  output/knowledge/style-profile.md
         │                      (now includes: argument construction, limitation handling,
         │                       competitive positioning, claim calibration, reviewer appeal)
         ▼
Phase 4 — Workspace Creation + Source-to-Section Mapping
  output/<paper-slug>/brief.md  (title, slug, venue, contributions, ownership-aware source map)
         │
         ▼
Phase 4b — RQ-Validation Traceability
  Map each research question → validation method → evidence source (artefact/thesis chapter)
  output/<paper-slug>/rq-traceability.md
  Flag any RQ without validation evidence
         │
         ▼
Phase 4c — Novelty Validation
  Each contribution validated against ingested sources
  output/<paper-slug>/novelty-matrix.md  →  Clear / Marginal / Unclear per contribution
  "Unclear" differentiators queued for the consolidated Paper Plan approval
         │
         ▼
Phase 4d — Contribution Framing Workshop
  Evaluate 2–3 alternative framings (methodological, empirical, DSR, etc.)
  Score each against venue review criteria (novelty, rigor, significance weights)
  Recommended framing recorded in brief.md (confirmed at Paper Plan approval)
         │
         ▼
Phase 4e — Methodology Stress-Test
  Identify threats: construct, internal, external, conclusion validity
  Flag missing baselines, confounders, reproducibility gaps
  output/<paper-slug>/methodology-stress-test.md
  High-severity threats surfaced in the Paper Plan approval
  Consolidated Paper Plan approval — second and final pre-drafting pause
  (venue confirmation in Phase 0 is the first)
         │
         ▼
Phase 5 — Section Drafting  (paper-writer × 8 passes + coherence pass)
  Inputs: knowledge/sources/ + style-profile.md + page-budget.md + source-to-section map
         + portfolio context (terminology, self-plagiarism guard) + session learnings
         + rq-traceability + novelty matrix + methodology stress-test
  Each section reads all prior sections for narrative continuity
  Quick validation after each section (word count, reference traceability, no duplication)
  Coherence pass: reference traceability, contribution alignment, abstract↔results, acronyms
  Outputs:
    output/<paper-slug>/abstract.md  (or deferred to after conclusion if "abstract last")
    output/<paper-slug>/introduction.md
    output/<paper-slug>/related-work.md
    output/<paper-slug>/methodology.md
    output/<paper-slug>/experiments-or-results.md
    output/<paper-slug>/discussion.md
    output/<paper-slug>/conclusion.md
    output/<paper-slug>/references.bib
         │
         ▼
Phase 5b — "So What?" Significance Test
  Flag: dead-end paragraphs, uninterpreted results, unjustified decisions, missing implications
  Re-delegate affected sections if > 3 items flagged
         │
         ▼
Phase 5d — Figure and Table Planning
  Scan sections for visual opportunities
  output/<paper-slug>/figure-plan.md  →  prioritized figures/tables with captions
  Insert [FIGURE: ...] placeholders into section files
         │
         ▼
Phase 5e — Self-Plagiarism Check
  Runs when sources/my-papers/ or sources/theses/ contains files
  self-plagiarism-guard compares against sources/my-papers/ and sources/theses/
  output/<paper-slug>/self-plagiarism-report.md
  HIGH/CRITICAL risk → automatic rewrite of flagged sections (max 2 automated cycles, then escalate to the user)
         │
         ▼
Phase 5f — Integrity Gate
  integrity-check verifies cross-section consistency, temporal integrity,
  AI research failure modes, and score trajectory
  output/<paper-slug>/quality-scorecard.md  →  PASS / PASS WITH WARNINGS / FAIL
  Critical failure-mode flags block submission; Major → PASS WITH WARNINGS; Minor informational
  FAIL blocks the compliance check (max 2 automated fix cycles before escalating to the user)
         │
         ▼
Phase 6 — Compliance Check + Citation Verification
  compliance-checker validates all sections against venue rules + page budget
  + session learnings enforcement (recurring failures checked proactively)
  output/<paper-slug>/compliance-report.md  →  PASS / WARN / FAIL
  Report now includes: Strengths section + word count delta
  citation-verifier checks every reference is real, traceable, and correctly attributed
  output/<paper-slug>/citation-verification-report.md
         │  (if FAIL or WARN → enter Phase 7)
         ▼
Phase 7 — Revise  (convergence-based, until PASS, max 5 iterations)
  Re-delegate affected sections to paper-writer with correction instructions
  Re-run compliance check after each round
  Convergence: stop when 0 critical + warnings stabilize (or max 5 reached)
  Integrated depth improvement: expand sections below page-budget minimum
  Track word count deltas between iterations
         │
         ▼
Phase 8 — Peer Review Simulation
  reviewer-simulator reads all sections + sources + venue guidelines
  Produces 4 venue-calibrated reviews (methodologist, domain expert, skeptic,
  reproducibility auditor — the fourth for empirical papers only)
  output/<paper-slug>/peer-review-simulation.md
  Includes: vulnerability register for rebuttal preparation
  User may address issues → re-draft → re-check compliance
         │  (user confirms before assembly)
         ▼
Phase 9 — Full Paper Assembly + Deliverables
  Concatenate all sections → output/<paper-slug>/full-paper.md
  Generate elevator pitch → output/<paper-slug>/elevator-pitch.md
  Verify section numbering, cross-references, total word count within (limit − 1)
         │
         ▼
Phase 10 — Final Delivery
  academic-writer summarises: artefact paths, word counts (with deltas), page estimate,
  compliance status, peer review verdict, elevator pitch, remaining TODOs
         │
         ▼
Phase 11 — Session Learnings
  Self-reflection pass → append to output/knowledge/session-learnings.md
  Update portfolio-tracker.md with new paper entry + terminology + coverage
```

---

## Workspace — Folder Responsibilities

```
DaVinci/
├── .github/
│   ├── agents/          ← Agent definitions (11 × .agent.md) — "source code"
│   ├── prompts/         ← Slash-command entry points (24 × .prompt.md)
│   ├── instructions/    ← Always-active writing / citation / venue rules
│   └── skills/
│       └── academic-writer/
│           ├── SKILL.md              ← Skill entrypoint
│           └── references/
│               ├── humanizer.md              ← 37 patterns to remove AI tells (used by /check-quality)
│               ├── academic-tells.md         ← Compact AI-tell patterns applied during drafting
│               ├── source-summary-format.md  ← Schema for ingested summaries
│               ├── style-profile-format.md   ← Schema for style profiles (incl. argumentation)
│               ├── session-learnings-format.md ← Schema for session learnings
│               ├── portfolio-tracker-format.md ← Schema for multi-paper coherence tracker
│               ├── ai-failure-modes.md       ← AI research failure modes checklist
│               └── venue-families.md         ← Quick-ref formatting table
│
├── sources/             ← READ-ONLY inputs provided by the researcher
│   ├── theses/          ← Primary source PDFs (Master's / PhD theses) — ownership: self
│   ├── artefacts/       ← Unpublished materials: design docs, surveys, experiments — ownership: self
│   ├── papers/          ← Third-party reference papers — ownership: other
│   ├── my-papers/       ← Researcher's own past publications (style learning only)
│   ├── submitted-papers/ ← Externally-written papers for import into the pipeline
│   ├── reviewer-feedback/ ← Real reviewer comments received after submission
│   ├── my-response-letters/ ← Previously written rebuttal/response letters
│   └── venues/          ← Venue guidelines & requirements summaries
│
└── output/              ← ALL generated artefacts (never manually edit)
    ├── knowledge/        ← Persistent cross-session memory (DO NOT DELETE)
    │   ├── style-profile.md      ← Writing style + argumentation patterns
    │   ├── response-letter-profile.md ← Rebuttal/response letter style
    │   ├── canonical-refs.md     ← Concept → BibTeX key registry
    │   ├── portfolio-tracker.md  ← Multi-paper coherence + self-plagiarism guard
    │   ├── session-learnings.md  ← Accumulated lessons from past sessions
    │   └── sources/              ← One .md summary per ingested source (with quality + ownership)
    └── <paper-slug>/    ← One folder per paper
        ├── brief.md, rq-traceability.md, novelty-matrix.md, figure-plan.md
        ├── methodology-stress-test.md
        ├── 8 section .md files + references.bib
        ├── compliance-report.md, peer-review-simulation.md
        ├── citation-verification-report.md, writing-quality-report.md
        ├── quality-scorecard.md, self-plagiarism-report.md
        ├── reviewer-response-matrix.md, rebuttal-draft.md, feedback-tracker.md
        ├── elevator-pitch.md
        ├── submission/ (cover letter, highlights, suggested reviewers, checklists)
        └── full-paper.md
```

Outside the agent workflow, the repository also contains `web/` (optional Streamlit Web UI), `docs/` (user documentation and screenshots), `scripts/` (Windows/macOS launchers and release tooling), and `tests/` (pytest suite for `web/davinci_core.py`).

---

## Knowledge Architecture

```
                ┌─────────────────────────────────────────┐
                │           KNOWLEDGE STORE               │
                │       output/knowledge/                  │
                │                                         │
                │  style-profile.md                       │
                │  ┌─────────────────────────────────┐    │
                │  │ Sentence rhythm & length        │    │
                │  │ Paragraph structure patterns    │    │
                │  │ Preferred connectives & hedges  │    │
                │  │ Citation integration style      │    │
                │  │ Section-level writing voice     │    │
                │  │ Argumentation patterns:         │    │
                │  │  • Argument construction mode   │    │
                │  │  • Limitation handling style    │    │
                │  │  • Competitive positioning      │    │
                │  │  • Claim strength calibration   │    │
                │  │  • Reviewer appeal strategy     │    │
                │  └─────────────────────────────────┘    │
                │                                         │
                │  portfolio-tracker.md                    │
                │  ┌─────────────────────────────────┐    │
                │  │ Published papers registry       │    │
                │  │ Terminology consistency table   │    │
                │  │ Self-plagiarism guard           │    │
                │  │ Source material coverage map    │    │
                │  └─────────────────────────────────┘    │
                │                                         │
                │  session-learnings.md                    │
                │  ┌─────────────────────────────────┐    │
                │  │ Per-session lessons learned     │    │
                │  │ Recurring compliance failures   │    │
                │  │ Venue-specific observations     │    │
                │  │ Source utilization gaps         │    │
                │  └─────────────────────────────────┘    │
                │                                         │
                │  sources/<slug>.md  (one per source)    │
                │  ┌─────────────────────────────────┐    │
                │  │ Metadata (authors, year, type)  │    │
                │  │ Research questions & objectives │    │
                │  │ Methodology summary             │    │
                │  │ Key findings & contributions    │    │
                │  │ Limitations                     │    │
                │  │ Citeable claims (with locations)│    │
                │  │ Quality assessment (tier,       │    │
                │  │   recency, rigor, relevance)    │    │
                │  └─────────────────────────────────┘    │
                └─────────────────────────────────────────┘
                     ▲                        ▲
           written by                    written by
        source-ingestion              style-learner
                     │                        │
               read by all subagents during drafting
```

---

## Supported Venue Families

| Family | Sub-types | Template Format |
|---|---|---|
| **IEEE** | Conference (two-column), Journal / Transactions, Access | LaTeX `.cls` |
| **ACM** | SIG Proceedings, Journals | LaTeX `acmart.cls` |
| **Elsevier** | All journals | LaTeX or Word |
| **Springer** | LNCS, journals | LaTeX |
| **NeurIPS / ICML / ICLR** | ML conference proceedings | LaTeX |
| **ACL / EMNLP / NAACL** | NLP conference proceedings | LaTeX |
| **USENIX / CCS / IEEE S&P** | Security conference proceedings | LaTeX |
| **Custom** | Any venue | Raw guidelines in `sources/venues/` |

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Zero executable code** | The agent system is Markdown prompts only; no build step, no dependencies, no runtime beyond the AI model. The optional Web UI is a separate front end and is never required |
| **Persistent knowledge store** | Summaries, style profiles, portfolio tracker, and session learnings survive between sessions so sources do not need to be re-ingested each run |
| **Single user-facing agent** | `academic-writer` is the only entry point; internal agents are hidden, preventing misuse of partial pipelines |
| **Venue as mandatory blocker** | Every entry point (`/write-paper`, `/new-paper`, `/improve-paper`) requires a confirmed target venue before proceeding — needed for page budget, formatting, citation style, and compliance |
| **Reference integrity** | Hard constraint at every layer: only sources ingested from `sources/papers/`, `sources/theses/`, or `sources/artefacts/` (artefacts cited as grey literature / `@techreport`) may be cited. Verified at drafting, coherence pass, and compliance check — no hallucinated references |
| **Source quality assessment** | Each ingested source receives a quality score (publication tier, recency, rigor, relevance) guiding how prominently it is cited — foreground, background, or context-only |
| **Novelty validation before drafting** | Explicitly validates each stated contribution against ingested sources to prevent "incremental contribution" rejections — flags unclear novelty before writing begins |
| **Source conflict resolution** | When multiple sources cover overlapping topics, the orchestrator applies explicit rules: combine complementary sources, present stronger-evidenced claims for contradictions, prefer more recent/detailed for redundancy |
| **Deep style learning** | Style profile captures not just surface patterns (sentence length, hedging) but deep argumentation patterns (how arguments are built, how limitations are handled, how the researcher positions competitively) |
| **Multi-paper coherence** | Portfolio tracker prevents self-plagiarism, enforces consistent terminology across paper series, and tracks which thesis material has been published |
| **Convergence-based iteration** | The compliance → revise loop continues until 0 critical issues + warnings stabilize (max 5), with integrated depth improvement — rather than arbitrary fixed 3× cap |
| **Peer review simulation** | Four-persona simulated review (methodologist, domain expert, skeptic, reproducibility auditor — the fourth for empirical papers only) anticipates real objections before submission; vulnerability register prepares rebuttal positions |
| **Abstract-first or abstract-last** | Supports both workflows: outline-driven (abstract first) or synthesis-driven (abstract last) per researcher preference |
| **Figure/table planning** | Dedicated phase ensures visual strategy is deliberate, not afterthought — produces prioritized figure list with captions and placement directives |
| **Session learnings enforcement** | Learnings are passed as explicit inputs to all subagents (not just orchestrator), ensuring lessons from past sessions are applied at the point of writing and checking |
| **Custom section names** | The pipeline supports non-standard section names (e.g., "System Design" instead of "Methodology") configured during Phase 1, enabling flexibility across venue types |
| **Humanizer reference** | Drafting applies the compact `academic-tells.md` (academic AI-tell patterns + vocabulary list); the full `humanizer.md` (37 concrete before/after patterns, PERSONALITY AND SOUL section excluded for academic writing) is applied by `/check-quality` only |
| **Single source of truth for schemas** | Agent definitions reference the format files in `skills/academic-writer/references/` rather than embedding inline templates, preventing divergence |
