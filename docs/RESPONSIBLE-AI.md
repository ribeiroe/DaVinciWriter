# Responsible AI & EU AI Act Notice

> **Last reviewed:** September 2026 — the EU AI Act's transparency provisions (Article 50) and GPAI rules phased in through 2025–2026; this notice will be revisited as guidance evolves.

This page explains how DaVinci Writer relates to the [EU Artificial Intelligence Act](https://artificialintelligenceact.eu/) and what that means in practice for anyone using it to draft academic papers.

## What DaVinci Writer is (and isn't)

DaVinci Writer is an **application layer**, not an AI model. It orchestrates prompts and tool calls against a general-purpose AI (GPAI) model — either Anthropic's Claude (cloud) or a locally hosted open-weight model (via Ollama, LM Studio, or a compatible endpoint). DaVinci Writer does not train, fine-tune, or distribute any model.

Under the Act's role definitions:

- **Model provider** — Anthropic (or whoever supplies the local model, e.g. Qwen/Meta via Ollama). Chapter V obligations for GPAI models (technical documentation, copyright policy, systemic-risk evaluation) sit with them, not with this project.
- **Deployer** — you, the researcher running DaVinci Writer. As a deployer of a GPAI-based system, your main obligations are transparency (Article 50) and general AI literacy (Article 4), not the heavier high-risk-system requirements in Annex III.

## Risk classification (self-assessment)

DaVinci Writer is used to draft, structure, and check academic manuscripts. This use case is **not listed in Annex III** (e.g., employment screening, credit scoring, biometric identification, law enforcement, education/exam scoring) and is not a prohibited practice under Article 5. Our self-assessment is that DaVinci Writer falls under the Act's general **transparency obligations for AI systems that generate content** (Article 50), rather than the high-risk regime.

This is a good-faith self-assessment, not legal advice. If you plan to use DaVinci Writer in a context that could plausibly fall under Annex III (for example, using it to help score or rank other people), stop and seek your own legal review before proceeding.

## Transparency (Article 50) — what this means for your papers

Article 50 requires that AI-generated or AI-assisted content be identifiable, and that people know when they are interacting with an AI system. In practice:

- **Every manuscript produced or substantially assisted by DaVinci Writer should carry an AI-use disclosure.** The `compliance-checker` agent auto-generates one (`output/<paper-slug>/ai-disclosure.md`) using a template appropriate to your venue — review and adapt it before submission.
- **Venue policies vary and can be stricter than the Act.** Check your target journal/conference's own AI-use policy (see `sources/venues/<venue>/`) — some prohibit AI-drafted text outright, others require specific disclosure wording or word-level attribution.
- **You are the author of record.** Disclosure does not transfer responsibility — you remain accountable for the accuracy, originality, and integrity of anything you submit under your name.

## Human oversight — non-negotiable

DaVinci Writer is built around the assumption that a human reviews everything before it leaves the workspace:

- Unresolved `[UNSUPPORTED — author to verify]`, `[CITATION NEEDED]`, `[DATA NEEDED]`, and `[GAP NOT CONFIRMED]` markers must be resolved manually — they are deliberately not auto-filled.
- The `citation-verifier`, `integrity-check`, and `self-plagiarism-guard` agents are safeguards that catch common failure modes; they reduce risk but do not certify a paper is publication-ready. Read their reports.
- Never submit a manuscript, dataset, or claim you have not personally verified against your sources.

## Data flow & privacy

What happens to your data depends on which provider is active in **⚙️ Settings → Connection**:

| Mode | Where your text goes | Notes |
|------|----------------------|-------|
| Anthropic Cloud | Sent to Anthropic's API over HTTPS | Subject to Anthropic's own data-handling and retention terms |
| Local endpoint (Ollama / LM Studio / LiteLLM) | Stays on your machine (or your own network) | No API key or external transmission required |

If your sources contain personal data (e.g., study participant records, unpublished collaborator material), prefer local mode, or confirm your cloud provider's terms satisfy your institution's data protection / GDPR obligations before uploading.

## AI literacy (Article 4)

The Act encourages providers and deployers to ensure users understand the capabilities and limitations of the AI systems they use. Keep in mind:

- Outputs can be factually wrong, cite non-existent sources if verification steps are skipped, or vary between runs and model providers.
- Automated checks (citation verification, integrity scoring) improve reliability but are themselves AI-assisted and imperfect — treat their output as a checklist, not a guarantee.
- Local models are meaningfully weaker than cloud models on this pipeline (tool-calling reliability, context length, writing quality) — expect to do more manual verification when using them.

## Questions this notice doesn't answer

This document is a transparency aid, not a compliance certificate for your specific use, institution, or jurisdiction. For binding guidance, consult your institution's legal/compliance office or the resources at [artificialintelligenceact.eu](https://artificialintelligenceact.eu/).
