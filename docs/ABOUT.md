# About DaVinci Writer

**DaVinci Writer** is an AI-powered multi-agent system that helps researchers turn theses, research data, and unpublished materials into publication-ready scientific papers.

**Version 1.0.2** · October 2026

## Why DaVinci?

Writing a journal or conference paper is one of the most time-consuming tasks in academia. Researchers spend weeks structuring arguments, formatting to venue rules, and iterating through review cycles — often while juggling teaching, supervision, and new research.

DaVinci Writer automates the mechanical parts of paper writing so you can focus on the science:

- **Source ingestion** — reads your thesis, experiment data, and reference papers
- **Style learning** — captures your personal writing voice from prior publications
- **Drafting** — produces each section following your venue's structure and page limits
- **Compliance checking** — validates formatting against IEEE, ACM, Elsevier, and Springer templates; checks citation density, ethics statements, and reproducibility
- **Peer-review simulation** — four reviewer personas (including a Reproducibility Auditor) critique the draft before real reviewers do
- **Formal review feedback loop** — processes real reviewer scores and generates a revision matrix and rebuttal letter
- **Citation verification** — checks that all references are real, traceable to ingested sources, and correctly attributed
- **Writing quality analysis** — detects AI-generated patterns, scores each section, and provides substitution suggestions
- **Self-plagiarism detection** — compares your new paper against prior publications and flags textual overlap
- **Session persistence** — auto-saves your progress; resume any of your five most recent sessions from the sidebar after closing the browser
- **Sources Manager** — browse, preview, upload, and delete workspace source files in the browser
- **Papers Editor** — view and edit any generated paper section directly in the browser
- **Output Manager** — browse, preview, and download all generated manuscripts and reports
- **Model choice & cost control** — pick Sonnet 5, Opus 5, or Haiku 4.5 from comparison cards; optional Economy routing sends lightweight tasks to the cheapest model; live per-session cost tracking; automatic prompt caching cuts input costs by 70–90%
- **Local model support** — run cost-free against Ollama (via a LiteLLM proxy), LM Studio, or any Anthropic-compatible endpoint, configured entirely from Settings
- **Themes** — System, Dark, or Light appearance, switchable from Settings or the top-bar toggle
- **Responsible AI page** — EU AI Act notice and cloud-vs-local data-flow details, one click from the sidebar
- **Community-supported sustainability** — optional Ko-fi tips are available from the sidebar, the About page, and after a pipeline completes to help cover development, maintenance, and hosting costs (no paywalls or feature gating)

## Getting Started

The easiest way to use DaVinci Writer is the **Web UI**:

1. Unzip the release folder
2. Start the app:
  - macOS: double-click **`Start DaVinci.command`** — Terminal shows 6-phase startup progress
  - Windows: double-click **`start.bat`** — Terminal shows 6-phase startup progress
  - A terminal window will appear showing progress at each step; browser opens automatically when ready
  - Dependencies are installed on first run (or when `web/requirements.txt` changes), and startup is faster when already up to date
3. Open **⚙️ Settings → Connection**, add your API key, and click **Save & Test** (or set it in a `.env` file).
4. Stop the app when you're done:
  - macOS: double-click **`Stop DaVinci.command`** — Terminal shows 3-phase shutdown progress
  - Windows: double-click **`stop.bat`** — Terminal shows 3-phase shutdown progress
  - Terminal window shows progress and confirms the application has stopped

OS-specific launcher scripts are also available in `scripts/macos/` and `scripts/windows/`.

You need an **Anthropic API key** from [console.anthropic.com](https://console.anthropic.com/) and Python 3.10+ installed. Configure the key in **⚙️ Settings → Connection** (with one-click **Save & Test** verification), or add it to a `.env` file in the folder:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Prefer not to use the cloud? Choose **Local endpoint** in Settings → Connection to run against a local Ollama/LM Studio model instead — no API key needed.

## How It Works

DaVinci Writer is a **browser-based AI assistant** backed by a multi-agent prompt system. The Web UI guides you through a 4-step wizard:

1. **Choose your goal** — 14 goal cards in three groups: *Create & Draft*, *Improve & Review*, and *Respond to Reviewers*
2. **Pick your venue** — 13 pre-configured journals and conferences with formatting rules built in
3. **Add details** — optional title, contributions, and source file uploads
4. **Generate** — the AI works through the pipeline, writing to your `output/` folder

Goals that work on an existing paper (Quality Check, Final Audit, Rebuttal, Coach Revision, Integrate Feedback, Convert Format) or on your sources alone (Import Paper, Literature Review) skip the venue step and use a shorter three-step wizard.

Eleven specialized agents collaborate through an orchestrator:

| Agent | Responsibility |
|-------|---------------|
| Academic Writer | Orchestrates the end-to-end pipeline with gap-statement stress-test and mid-pipeline reinforcement |
| Source Ingestion | Reads and summarizes academic sources with quality assessment and ownership tagging |
| Style Learner | Analyzes your writing patterns and argumentation style |
| Paper Writer | Drafts individual sections with claim-to-source tracing, statistical rigour checks, and anti-leakage protocol |
| Compliance Checker | Validates venue requirements, citation density, ethics, reproducibility, and AI disclosure |
| Reviewer Simulator | Simulates peer review from 4 personas (methodologist, domain expert, skeptic, reproducibility auditor) |
| Revision Specialist | Revises papers based on real peer reviewer feedback; audits sources and builds response matrix |
| Citation Verifier | Verifies all references are real, traceable, and correctly attributed |
| Writing Quality Check | Detects AI-generated patterns and overused filler; produces per-section grades |
| Integrity Check | Content integrity gate + score trajectory tracking; verifies cross-section consistency |
| Self-Plagiarism Guard | Compares new paper against prior publications; flags textual overlap |

## Responsible & Transparent AI

DaVinci Writer generates AI-assisted content — it is a drafting and checking tool, not a substitute for your own judgment. Every output should be reviewed before it leaves the workspace:

- **Human oversight is mandatory.** You remain the author of record and are responsible for the accuracy, originality, and integrity of anything you submit. Resolve every `[UNSUPPORTED]`, `[CITATION NEEDED]`, and `[GAP NOT CONFIRMED]` marker before publishing.
- **AI-use disclosure.** The compliance checker auto-generates an `ai-disclosure.md` for each paper — check your venue's own AI-use policy and adapt the wording before submission.
- **EU AI Act self-assessment.** DaVinci Writer is a deployer of third-party general-purpose AI models (Anthropic Claude, or a local model via Ollama/LM Studio) — it does not train or provide any model itself. This use case falls under the Act's transparency obligations (Article 50) rather than the high-risk regime. See the full **[Responsible AI & EU AI Act Notice](https://github.com/ribeiroe/DaVinci_Writer/blob/main/docs/RESPONSIBLE-AI.md)** for details, including data-flow (cloud vs. local) information.

## Origins & Credits

DaVinci Writer brings together work from distinct sources. Each is credited and cited separately below to avoid confusion.

### 1. This application — DaVinci Writer

- **Author**: J. Eduardo Ferreira Ribeiro
- **Contributors**: António Campos, Nuno Pessoa Soares

If DaVinci Writer helped produce a paper, thesis, or report, please cite it as:

```bibtex
@software{ribeiro2026davinci,
  author  = {Ferreira Ribeiro, J. Eduardo and Campos, António and Pessoa Soares, Nuno},
  title   = {DaVinci Writer: An AI-Powered Multi-Agent System for Academic Paper Writing},
  year    = {2026},
  version = {1.0.2},
  url     = {https://github.com/ribeiroe/DaVinci_Writer}
}
```

### 2. Research behind the failure-mode checks

The integrity gate and the AI research failure-mode checklist are based on the limitations reported by Lu et al. (2026), *Nature* 651:914–919, the first fully autonomous AI research system to publish through blind peer review. If you cite the underlying findings, cite that work directly.

### 3. AI models and frameworks

DaVinci Writer does not train or provide any model. The Web UI uses Anthropic Claude through the Anthropic API (or a local model via Ollama, LM Studio, or LiteLLM) and is built with [Streamlit](https://streamlit.io/). Credit for those components belongs to their respective authors.

## License

**DaVinci Writer** itself is released under the [GNU General Public License v3.0](https://github.com/ribeiroe/DaVinci_Writer/blob/main/LICENSE.md). It is provided as-is, without warranty of any kind (see the license, Sections 15 and 16).

## Links

- [User Manual](https://github.com/ribeiroe/DaVinci_Writer/blob/main/docs/USER-MANUAL.md) — complete walkthrough with screenshots
- [Quick Start](https://github.com/ribeiroe/DaVinci_Writer/blob/main/docs/QUICKSTART.md) — get your first paper in 3 steps
- [Architecture](https://github.com/ribeiroe/DaVinci_Writer/blob/main/docs/ARCHITECTURE.md) — detailed system design
- [Agent System](https://github.com/ribeiroe/DaVinci_Writer/blob/main/AGENTS.md) — agent definitions and commands
- [Responsible AI & EU AI Act Notice](https://github.com/ribeiroe/DaVinci_Writer/blob/main/docs/RESPONSIBLE-AI.md) — transparency, risk self-assessment, and data-flow notes
