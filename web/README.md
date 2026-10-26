# DaVinci Web UI

A browser-based interface for DaVinci that requires no VS Code or Copilot knowledge.

## Setup

1. Install dependencies (Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your Anthropic API key (choose one method):
   - **In the app:** Open **⚙️ Settings → Connection** from the sidebar, paste your key, and click **Save & Test**.
   - **Manual:** Create a `.env` file in the DaVinci root:
     ```
     ANTHROPIC_API_KEY=sk-ant-...
     ```
   Without an API key, the UI still works as a guided wizard — it will show
   the configuration and prompt structure but cannot generate text.
   Alternatively, choose **Local endpoint** in Settings → Connection to run
   cost-free against a local model (Ollama via LiteLLM, LM Studio) — no key needed.

3. Run:
   ```bash
   streamlit run app.py
   ```

4. Open http://localhost:8501 in your browser.

Prefer a container? From the repository root, copy `.env.example` to `.env`, add
your API key, and run `docker compose up`.

## How It Works

The web UI provides a step-by-step wizard:

1. **Choose goal** — 14 goal cards in three groups: *Create & Draft* (write, import,
   literature review, plan publications), *Improve & Review* (improve, peer review,
   quality check, final audit, convert format, prepare submission), and
   *Respond to Reviewers* (revise, rebuttal, coach revision, integrate feedback)
2. **Pick venue** — from 13 pre-configured options or add your own
3. **Add details** — optional title, contributions, and file uploads
4. **Generate** — interactive chat powered by Claude

Goals that work on an existing paper or on your sources alone (quality check,
final audit, convert format, rebuttal, coach revision, integrate feedback, import,
literature review) skip the venue step and use a shorter 3-step wizard.

The sidebar also provides a **Papers Editor**, **Sources Manager**, and
**Output Manager**, recent-session resume, and a Help section with the
**User Manual**, **About**, **Responsible AI** notice, **Settings**
(provider, API key, model, theme), and **Support (Optional)**.

Files uploaded through the UI are saved to the standard `sources/` folders,
so they're also available if you switch to the VS Code workflow later.

The sidebar **Help** section also includes **Support (Optional)**, which opens
the Ko-fi page for voluntary tips. The same link also appears on the About page
and once after a pipeline completes. The app remains free with no paywalls or
feature gating.

## For VS Code Users

If you prefer the VS Code + Copilot Chat experience, just open the DaVinci
folder in VS Code and type `/start` in Copilot Chat. The web UI and VS Code
workflows are fully compatible — they share the same workspace.
