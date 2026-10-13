# Changelog

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
