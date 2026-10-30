# Changelog

## v1.1.0 — 2026-10-30

### Changes

- Settings → Models: new **Use another Claude model** section lists every model on your Anthropic account, so new releases can be selected without an app update.
- Settings → Connection: local endpoint presets for Ollama, LM Studio, and LiteLLM with auto-filled addresses and a plain-language setup guide.
- Updated Sonnet 5 pricing to \$2 / \$10 per 1M tokens and added cost estimates for Sonnet 5.5, Opus 5.5, Haiku 5.5, and Fable 5.1.
- Disabled primary buttons are now visibly greyed out.

## v1.0.2 — 2026-10-26

### Changes

- Reworded the optional Ko-fi support text to "tips" (voluntary, unlocks no features) and listed all in-app locations of the Support link, including the post-pipeline hint.
- Removed prize and sponsor detail from the INForum venue summary.

## v1.0.1 — 2026-10-13

First public release of DaVinci Writer.

### Highlights

- **Multi-agent academic writing system** — orchestrator plus specialist agents for source ingestion, style learning, section drafting, compliance checking, citation verification, writing-quality checks, integrity gating, self-plagiarism checks, peer-review simulation, and post-review revision (see `AGENTS.md`).
- **Slash-command workflows** — `/start`, `/write-paper`, `/improve-paper`, `/revise-paper`, `/draft-rebuttal`, `/final-audit`, and more; available in VS Code Copilot and natively in Claude Code via generated `.claude/` wrappers.
- **Web UI (Streamlit)** — 4-step wizard, Sources Manager, Papers Editor, in-app User Manual, light/dark/system themes, per-session token usage and cost estimates, and support for Anthropic Claude or a local model (Ollama / LM Studio).
- **Venue support** — IEEE, ACM, Elsevier, Springer, and custom venues via `sources/venues/`.
- **Launchers** — `start.bat` / `stop.bat` (Windows), `Start DaVinci.command` / `Stop DaVinci.command` (macOS), and Docker (`docker compose up`).

### Requirements

- Python 3.10+ **or** Docker.
- An Anthropic API key, or a local model via Ollama / LM Studio.

### Notes

- Licensed under the GNU General Public License v3.0.
- macOS Gatekeeper may require first-run confirmation for `.command` launchers on downloaded zips (right-click → Open → Open).
