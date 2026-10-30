# Quick Start Guide

Get your first paper written in **3 steps**. No technical knowledge required.

---

## Installation

Choose the method that suits you:

### Option A — Release Package (recommended for beginners)

The easiest way. Everything is included in the release zip.

**Prerequisites:**
- **Python 3.10+** — [Download Python](https://www.python.org/downloads/)
- **An Anthropic API key** — [Get one here](https://console.anthropic.com/) (add a payment method to your Anthropic account; or skip the key and use a local model)

**Steps:**
1. Download and unzip **`DaVinci-v1.1.1.zip`**.
2. Start the app:
   - macOS: double-click **`Start DaVinci.command`**
   - Windows: double-click **`start.bat`**
   - A terminal window opens showing **6-phase startup progress**:
     ```
     [1/6] Checking Python version... ✓
     [2/6] Virtual environment... ✓
     [3/6] Dependencies check... ✓
     [4/6] Configuration file found ✓
     [5/6] Application process started ✓
     [6/6] Application is ready ✓
     ```
   - Phase 3 installs dependencies on first run (or when `web/requirements.txt` changes), and is fast when already up to date
   - Your browser automatically opens to **http://localhost:8501** when ready
3. Open **⚙️ Settings** from the sidebar, paste your Anthropic API key in the **Connection** tab, and click **Save & Test**. (Or create a `.env` file manually:)
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
4. Stop the app when you're done:
   - macOS: double-click **`Stop DaVinci.command`**
   - Windows: double-click **`stop.bat`**
   - A terminal window opens showing **3-phase shutdown progress** and confirms the app has stopped

> **macOS security note:** If macOS blocks the `.command` file, right-click it → Open → Open. You only need to do this once.

### Option B — Docker (any OS, consistent environment)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Copy `.env.example` to `.env` and add your Anthropic API key.
3. In a terminal inside the DaVinci folder:
   ```bash
   docker compose up
   ```
4. Open **http://localhost:8501** in your browser.
   To stop: `docker compose down`

### Option C — Manual (any OS)

```bash
cd DaVinci_Writer/web
pip3 install -r requirements.txt
streamlit run app.py
```

OS-specific launcher scripts are also available in `scripts/macos/` and `scripts/windows/`.

Open **http://localhost:8501**.

### Option D — VS Code + GitHub Copilot (advanced)

Open the DaVinci folder as a workspace in VS Code, then see **Step 3** below.

> **API key:** All methods require an Anthropic API key from [console.anthropic.com](https://console.anthropic.com/). You can configure it in **⚙️ Settings → Connection** inside the app, or in a `.env` file.
>
> **No API key?** The Web UI can also run cost-free against a **local model** (Ollama or LM Studio). Choose **Local endpoint** in ⚙️ Settings → Connection and follow the built-in setup recipe. Expect lower quality than the cloud models.

---

## Step 1 — Add Your Materials

Drop your files into the right folders (or upload them in the web UI at Step 3):

| What you have | Where to put it |
|---------------|----------------|
| Your thesis (PDF, TXT, or MD) | `sources/theses/` |
| Your notes, data, designs, results | `sources/artefacts/` |
| Reference papers by other authors | `sources/papers/` |
| Your previously published papers | `sources/my-papers/` |

**Don't have files ready?** That's OK — the system will ask you about your research topic instead.

---

## Step 2 — Open the Web UI

Double-click **`Start DaVinci.command`** (macOS) or **`start.bat`** (Windows), or run `streamlit run web/app.py`.

Your browser opens at **http://localhost:8501** showing the DaVinci Writer home screen.

---

## Step 3 — Choose Your Goal and Write

1. **Click a goal card** — e.g., "✍️ Write a Paper" for a full pipeline from sources to finished manuscript
2. **Pick your venue** — select a journal or conference from the list (13 pre-configured options). Goals that work on an existing paper, such as Quality Check or Draft Rebuttal, skip this step.
3. **Add details** — optional title and contributions; upload files if you haven't already
4. **Click "Start Writing →"** — the AI works through the pipeline automatically

Your finished paper appears in the `output/` folder as Markdown files. Use the **📝 Papers Editor** in the sidebar to review and edit individual sections.

---

## What Happens Next?

The system works through these stages automatically:

```
Your files → Read & understand → Learn your style → Draft paper →
Check formatting → Fix issues → Simulate peer review → Deliver
```

---

## Common Questions

**Q: Which journals/conferences are supported?**
A: 13 venues are pre-configured (IEEE Access, IEEE TSE, ICSE, ACM CHI, NeurIPS, ICML, REFSQ, INForum, and more). You can also add any venue by dropping its guidelines into `sources/venues/`.

**Q: Can I improve an existing draft?**
A: Yes! Use the **📄 Output Manager** in the sidebar to find your draft, or choose "✨ Improve Draft" on the home screen.

**Q: How do I edit a generated section?**
A: Click **📝 Papers Editor** in the sidebar — select your paper and section, edit in the text area, and click Save.

**Q: What file formats are supported for sources?**
A: PDF, TXT, and Markdown (.md) files.

**Q: Do I need to know LaTeX?**
A: No. The system writes in Markdown. You can convert to LaTeX using Pandoc: `pandoc full-paper.md -o paper.tex`

**Q: Can I write multiple papers?**
A: Yes. Each paper gets its own folder under `output/`. Start a new session from the sidebar for each new paper.

**Q: How can I support DaVinci Writer?**
A: In the app sidebar, open **Help** and click **Support (Optional)**. The link also appears on the **About DaVinci** page and once after a pipeline completes. Tips are voluntary and help keep DaVinci free.

---

## All Available Commands (Web UI Goals)

| Goal | What it does |
|------|-------------|
| ✍️ Write a Paper | Full automated pipeline |
| ✨ Improve Draft | Expand and polish an existing draft |
| 🔬 Peer Review | 4 simulated reviewers find weaknesses |
| 🛡️ Quality Check | Citations, AI-tells, integrity scoring |
| 🔍 Final Audit | Fresh pre-submission check |
| 🔄 Revise Paper | Systematic revision after reviewer feedback |
| 💬 Draft Rebuttal | Point-by-point response letter |
| 🎓 Coach Revision | Guided walkthrough of each reviewer comment |
| 👥 Integrate Feedback | Apply co-author or advisor notes |
| 📚 Literature Review | Thematic map & gap analysis |
| 🔀 Convert Format | Move paper between venue formats |
| 📦 Prepare Submission | Cover letter, highlights, checklists |
| 🗺️ Plan Publications | Identify papers extractable from your research |
| 📥 Import Paper | Bring an existing PDF/TXT into the workspace |

See [README.md](../README.md) for the complete command reference including VS Code slash commands.
