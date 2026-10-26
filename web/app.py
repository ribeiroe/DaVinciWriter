"""
DaVinci Web UI — Streamlit app for academic paper writing.
A modern, minimal browser-based interface that wraps the DaVinci agent prompts
and calls the Anthropic Claude API to generate papers.

Design principles: Clean, spacious, card-based, progress-driven, delightful.
"""

import html
import json
import os
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Streamlit stops a running script by raising these at the next st.* call
# (e.g. when the user clicks Stop or interacts mid-run). They must never be
# swallowed by our generic error handlers, or generation becomes uncancelable.
try:
    from streamlit.runtime.scriptrunner import RerunException, StopException
    _ST_CONTROL_EXC = (RerunException, StopException)
except Exception:
    _ST_CONTROL_EXC = ()

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# `streamlit run` puts this file's folder on sys.path, but other launchers
# (AppTest, embedding) don't — make the local import work everywhere.
import sys
_WEB_DIR = str(Path(__file__).resolve().parent)
if _WEB_DIR not in sys.path:
    sys.path.insert(0, _WEB_DIR)

# Optional brand logo — drop a PNG or JPEG at web/assets/logo.(png|jpg|jpeg)
# to enable it in the sidebar header and the landing-page hero. Absent by
# default, so the app keeps working with the text-only "✦ DaVinci Writer"
# mark until it's added.
_LOGO_PATH = next(
    (p for ext in ("png", "jpg", "jpeg") if (p := Path(_WEB_DIR) / "assets" / f"logo.{ext}").exists()),
    None,
)
_HAS_LOGO = _LOGO_PATH is not None

from davinci_core import (
    KNOWLEDGE_DIR,
    OUTPUT_DIR,
    SOURCES_DIR,
    VENUES_DIR,
    WORKSPACE,
    _CLAUDE_TOOLS,
    _DEFAULT_MODEL,
    _MODEL_PRICES,
    _custom_base_url,
    _execute_tool,
    _mark_cache_breakpoint,
    _model_for_goal,
    _paper_version_key,
    _slugify,
    _split_manual_images,
    _strip_cache_markers,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERSION = "1.0.2"
RELEASE_DATE = "October 2026"
KOFI_URL = "https://ko-fi.com/ribeirolabs"


VENUE_PRESETS = sorted(
    [d.name for d in VENUES_DIR.iterdir() if d.is_dir() and d.name != "__pycache__"]
    if VENUES_DIR.exists()
    else []
)

SESSIONS_DIR = WORKSPACE / "web" / ".sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


# Keys to persist between browser sessions
_PERSIST_KEYS = [
    "step", "goal", "venue", "title", "contributions", "messages",
    "paper_slug", "pipeline_phase", "theme", "reviewer_feedback",
    "paper_slug_revise", "support_hint_shown",
]


def _feedback_round(slug: str) -> int:
    """Feedback round number for this wizard run (stable within the session).

    AGENTS.md promises multi-round traceability (<slug>-round-<N>), so new runs
    get the next free round number instead of clobbering round 1.
    """
    if st.session_state.get("_fb_round_slug") != slug:
        fb_dir = SOURCES_DIR / "reviewer-feedback"
        rounds = [
            int(m.group(1))
            for f in (fb_dir.glob(f"{slug}-round-*.*") if fb_dir.exists() else [])
            if (m := re.match(re.escape(slug) + r"-round-(\d+)\.", f.name))
        ]
        st.session_state["_fb_round"] = max(rounds, default=0) + 1
        st.session_state["_fb_round_slug"] = slug
    return st.session_state["_fb_round"]


def _save_reviewer_feedback_upload(uploaded_feedback) -> None:
    """Persist an uploaded reviewer-feedback file once, mirroring it into state.

    Guarded per file name: the uploader widget retains its file across reruns,
    and an unguarded write would overwrite the user's textarea edits on every
    script run.
    """
    if st.session_state.get("_fb_file_applied") == uploaded_feedback.name:
        return
    slug = _slugify(st.session_state.paper_slug_revise, fallback="paper")
    fb_dir = SOURCES_DIR / "reviewer-feedback"
    fb_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(uploaded_feedback.name).suffix or ".md"
    dest = fb_dir / f"{slug}-round-{_feedback_round(slug)}{ext}"
    dest.write_bytes(uploaded_feedback.getvalue())
    if ext == ".pdf":
        st.session_state.reviewer_feedback = f"[PDF uploaded: {dest.name} — the agent will read it from sources/reviewer-feedback/]"
    else:
        st.session_state.reviewer_feedback = uploaded_feedback.getvalue().decode("utf-8", errors="replace")
    st.session_state["_fb_file_applied"] = uploaded_feedback.name
    st.toast(f"Saved reviewer feedback to {dest.name}", icon=":material/check_circle:")
    st.rerun()


def _save_session(session_id: str | None = None):
    """Save current session state to a JSON file."""
    data = {}
    for key in _PERSIST_KEYS:
        val = st.session_state.get(key)
        if val is not None:
            data[key] = val
    data["_saved_at"] = datetime.now().isoformat()
    data["_goal_label"] = data.get("goal", "")
    data["_title"] = data.get("title", "")

    # Reuse the session's existing ID so resumed sessions update in place
    # instead of minting a new file on every message.
    if not session_id:
        session_id = st.session_state.get("_session_id")
    if not session_id:
        slug = _slugify(data.get("paper_slug_revise") or data.get("paper_slug") or data.get("goal") or "")
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        session_id = f"{slug}-{ts}"
    st.session_state["_session_id"] = session_id

    path = SESSIONS_DIR / f"{session_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return session_id


def _load_session(session_id: str) -> bool:
    """Load a saved session from disk. Returns True on success."""
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    for key in _PERSIST_KEYS:
        if key in data:
            st.session_state[key] = data[key]
    st.session_state["_session_id"] = session_id
    return True


def _list_sessions() -> list[dict]:
    """List all saved sessions, newest first."""
    sessions = []
    if SESSIONS_DIR.exists():
        for f in sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                sessions.append({
                    "id": f.stem,
                    "goal": data.get("_goal_label", ""),
                    "title": data.get("_title", ""),
                    "saved_at": data.get("_saved_at", ""),
                    "messages_count": len(data.get("messages", [])),
                })
            except (json.JSONDecodeError, OSError):
                continue
    return sessions


def _delete_session(session_id: str):
    """Delete a saved session file."""
    path = SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        path.unlink()


def _set_env_vars(updates: dict) -> None:
    """Update .env and os.environ together. A value of None removes the variable."""
    env_path = WORKSPACE / ".env"
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    for key, val in updates.items():
        lines = [l for l in lines if not l.startswith(f"{key}=")]
        if val is not None:
            lines.append(f"{key}={val}")
            os.environ[key] = val
        else:
            os.environ.pop(key, None)
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _reset_session():
    """Clear session state for a fresh start, preserving the UI theme choice."""
    theme_mode = st.session_state.get("theme_mode")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    if theme_mode:
        st.session_state["theme_mode"] = theme_mode


def _test_anthropic_key(key: str):
    """Verify an API key with one cheap call. Returns (ok, message)."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        ids = [m.id for m in client.models.list().data]
        st.session_state["_cloud_models"] = ids
        return True, f"Key verified — {len(ids)} models available on your account."
    except Exception as e:
        if "authentication" in type(e).__name__.lower() or "401" in str(e):
            return False, "Invalid API key — Anthropic rejected it. Double-check you copied the whole key."
        return False, f"Could not verify the key: {e}"


def _test_local_endpoint(url: str):
    """Probe an Anthropic-format proxy (e.g. LiteLLM). Returns (ok, message, model_ids)."""
    import requests
    base = url.rstrip("/")
    try:
        r = requests.get(f"{base}/v1/models", timeout=6)
        if r.ok:
            try:
                ids = [m.get("id", "") for m in r.json().get("data", []) if m.get("id")]
            except Exception:
                ids = []
            if ids:
                st.session_state["_endpoint_models"] = ids
                return True, f"Endpoint reachable — {len(ids)} model(s) served.", ids
            return True, "Endpoint reachable (no model list exposed — enter the model ID manually).", []
        return False, f"Endpoint answered HTTP {r.status_code} on /v1/models.", []
    except Exception as e:
        return False, f"Could not reach the endpoint: {e}", []


def _confirm_button(label: str, key: str, armed_label: str = ":material/warning: Sure?", **kwargs) -> bool:
    """Two-click destructive button: first click arms it, second click confirms."""
    armed = st.session_state.get("_confirm_armed") == key
    if armed:
        # Danger styling for the armed state — scoped to this widget's key class
        # (Streamlit >= 1.39). If the selector misses, type="primary" is the fallback.
        safe_key = re.sub(r"[^a-zA-Z0-9_-]", "-", key)
        st.markdown(
            f"<style>.st-key-{safe_key} button {{ background: var(--danger) !important; "
            f"border-color: var(--danger) !important; color: #15171C !important; }}</style>",
            unsafe_allow_html=True,
        )
        kwargs["type"] = "primary"
    if st.button(armed_label if armed else label, key=key, **kwargs):
        if armed:
            st.session_state.pop("_confirm_armed", None)
            return True
        st.session_state["_confirm_armed"] = key
        st.rerun()
    return False


# ---------------------------------------------------------------------------
# Goal families — color coding for the goal picker and config bar
# ---------------------------------------------------------------------------
_GOAL_FAMILIES = {
    "write": "create", "import": "create",
    "improve": "refine", "revise": "refine", "feedback": "refine", "coach": "refine",
    "review": "verify", "quality": "verify", "audit": "verify", "lit-review": "verify",
    "submit": "ship", "convert": "ship", "plan": "ship",
}
_FAMILY_COLORS = {  # (fg, soft bg) per family — dark-theme friendly, also fine on light
    "create": ("var(--primary)", "rgba(143, 174, 255, 0.13)"),
    "refine": ("var(--accent)", "rgba(76, 196, 184, 0.13)"),
    "verify": ("var(--warning)", "rgba(229, 164, 76, 0.14)"),
    "ship":   ("var(--success)", "rgba(71, 194, 131, 0.13)"),
}


def _pipeline_outputs_exist() -> bool:
    """True when the paper folder actually contains generated sections.

    Guards the completion banner: phase detection is keyword-based and can
    overshoot, so only celebrate when output files really exist.
    """
    slug = st.session_state.get("paper_slug_revise") or st.session_state.get("paper_slug")
    if not slug:
        return True  # nothing to verify against — don't block the banner
    d = OUTPUT_DIR / slug
    return d.exists() and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DaVinci Writer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS — Modern, clean, glassmorphism-inspired
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ---- Base Typography & Colors ---- */
:root {
    --primary: #8FAEFF;
    --primary-light: #A8C0FF;
    --primary-dark: #5B82E0;
    --accent: #4CC4B8;
    --bg-dark: #15171C;
    --card-bg: rgba(255, 255, 255, 0.03);
    --card-border: rgba(255, 255, 255, 0.08);
    --text-primary: #E9EAEE;
    --text-secondary: #A2A7B3;
    --success: #47C283;
    --warning: #E5A44C;
    --danger: #F07E7E;
}

/* Hide Streamlit default elements for cleaner look */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* Smoother fonts */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Editorial serif for display type — the manuscript identity.
   Headings only; body copy stays on the quiet sans. */
h1, h2, h3,
.hero-title,
.section-header,
.section-header-center {
    font-family: "Charter", "Bitstream Charter", "Sitka Text", Cambria, Georgia, serif !important;
    letter-spacing: -0.01em;
}

/* Main container breathing room */
.block-container {
    padding-top: 0.9rem;
    padding-bottom: 1.5rem;
    max-width: 1100px;
}

/* ---- Hero Section ---- */
.hero-container {
    text-align: center;
    padding: 0.45rem 1rem 0.35rem;
    margin-bottom: 0.2rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    font-weight: 300;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ---- Progress Stepper ---- */
.stepper {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    margin: 0.45rem auto 0.95rem;
    max-width: 500px;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 0;
}
.step-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 600;
    transition: all 0.3s ease;
}
.step-active {
    background: var(--primary);
    color: #15171C;
    box-shadow: 0 0 0 4px rgba(143, 174, 255, 0.15);
}
.step-done {
    background: rgba(71, 194, 131, 0.15);
    color: var(--success);
    border: 1.5px solid var(--success);
}
.step-pending {
    background: rgba(255, 255, 255, 0.09);
    color: var(--text-secondary);
    border: 1px solid rgba(255, 255, 255, 0.15);
}
.step-line {
    width: 60px;
    height: 2px;
    background: rgba(255, 255, 255, 0.15);
    margin: 0 4px;
}
.step-line-done {
    background: var(--success);
}

/* ---- Stat Pills (sidebar) ---- */
.stat-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    margin-bottom: 4px;
    width: fit-content;
}
.stat-ready {
    background: rgba(74, 222, 128, 0.14);
    color: var(--success);
    border: 1px solid rgba(74, 222, 128, 0.20);
}
.stat-empty {
    background: rgba(255, 255, 255, 0.07);
    color: var(--text-secondary);
    border: 1px solid rgba(255, 255, 255, 0.10);
}

/* ---- Chat Area ---- */
.stChatMessage {
    border-radius: 16px !important;
    margin-bottom: 0.5rem;
}

/* ---- Buttons — base reset ----
   Descendant selectors: buttons with help= are wrapped in a tooltip element,
   so `.stButton > button` would miss them. */
.stButton button {
    border-radius: 10px;
    font-weight: 500;
    padding: 0.55rem 1.5rem;
    transition: all 0.2s ease;
    min-height: 2.6rem !important;
}
.stButton button[kind="primary"] {
    background: var(--primary) !important;
    border: none;
}
.stButton button[kind="primary"]:hover {
    box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 4px 14px rgba(0,0,0,0.3);
    transform: translateY(-1px);
}
/* Focus ring — accessibility */
.stButton button:focus-visible {
    outline: 2px solid var(--primary) !important;
    outline-offset: 2px !important;
}

/* ---- Navigation buttons (Back / Next / Start Writing) ---- */
.st-key-nav_back button, .st-key-nav_next button,
.st-key-nav_back2 button, .st-key-nav_next2 button {
    height: 2.6rem !important;
    min-height: 2.6rem !important;
    max-height: 2.6rem !important;
    padding: 0 1.4rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
}

/* ---- Action bar (Step 3) ---- */
.st-key-action_restart button, .st-key-action_output button, .st-key-action_export button,
.st-key-action_restart .stDownloadButton > button, .st-key-action_export .stDownloadButton > button {
    height: 2.4rem !important;
    min-height: 2.4rem !important;
    max-height: 2.4rem !important;
    padding: 0 0.9rem !important;
    font-size: 0.82rem !important;
    white-space: nowrap !important;
}

/* ---- Non-goal horizontal blocks — reset flex/height on buttons ---- */
[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-goal_"])) > [data-testid="stColumn"] .stButton > button,
[data-testid="stHorizontalBlock"]:not(:has([class*="st-key-goal_"])) > [data-testid="stColumn"] .stDownloadButton > button {
    flex: none !important;
    min-height: 2.6rem !important;
    height: auto !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* ---- Equal-height goal cards — SCOPED to landing page only ---- */
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) {
    align-items: stretch !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] > div {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] > div > div {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] > div > div > div {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button {
    flex: 1 !important;
    height: auto !important;
    min-height: 130px !important;
    white-space: normal !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 4px 14px rgba(0,0,0,0.3) !important;
    border-color: rgba(143, 174, 255, 0.35) !important;
}

/* Goal card inner content — uniform icon, title, desc heights */
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button [data-testid="stMarkdownContainer"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    gap: 0.2rem !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button [data-testid="stMarkdownContainer"] > p:first-child {
    font-size: 1.8rem !important;
    line-height: 1 !important;
    min-height: 2.2rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button [data-testid="stMarkdownContainer"] > p:nth-child(2) {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    min-height: 2.4rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    margin: 0 !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button [data-testid="stMarkdownContainer"] > p:nth-child(3) {
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    line-height: 1.4 !important;
    min-height: 2.4rem !important;
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
    opacity: 0.65;
    text-align: center !important;
    margin: 0 !important;
}

/* ---- Venue selection cards (Step 1) ---- */
[class*="st-key-va_"] button, [class*="st-key-vj_"] button, [class*="st-key-vc_"] button {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: var(--text-primary) !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    min-height: 2.5rem !important;
    height: 2.5rem !important;
    max-height: 2.5rem !important;
    text-align: left !important;
    padding: 0 0.9rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    justify-content: flex-start !important;
}
[class*="st-key-va_"] button:hover, [class*="st-key-vj_"] button:hover, [class*="st-key-vc_"] button:hover {
    background: rgba(143, 174, 255, 0.10) !important;
    border-color: rgba(143, 174, 255, 0.35) !important;
    transform: none !important;
}

/* ---- Sidebar nav buttons (Manual/About in sidebar) ---- */
.st-key-nav_manual button, .st-key-nav_about button {
    height: 2.4rem !important;
    min-height: 2.4rem !important;
    max-height: 2.4rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    font-size: 0.82rem !important;
}

/* ---- Sidebar support link (intentionally subtle) ---- */
.st-key-nav_support a,
.st-key-nav_support button {
    opacity: 0.86 !important;
    font-size: 0.81rem !important;
    color: var(--text-secondary) !important;
    text-decoration: none !important;
    background: var(--card-bg) !important;
    border-color: var(--card-border) !important;
}
.st-key-nav_support a p,
.st-key-nav_support a span,
.st-key-nav_support button p,
.st-key-nav_support button span {
    color: inherit !important;
}
.st-key-nav_support a:hover,
.st-key-nav_support button:hover {
    opacity: 1 !important;
    color: var(--text-primary) !important;
    background: rgba(143, 174, 255, 0.08) !important;
    border-color: rgba(143, 174, 255, 0.35) !important;
}

/* ---- Inputs ---- */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 10px;
}

/* ---- Section Headers ---- */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
}
.section-header-center {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
    text-align: center;
}
.section-desc {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
    line-height: 1.6;
}
.section-desc-center {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
    line-height: 1.6;
    text-align: center;
}

/* ---- Wizard step page headings ---- */
.step-page-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0.5rem 0 0.25rem 0;
    letter-spacing: -0.01em;
}
.step-page-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 1.4rem;
    line-height: 1.5;
}

/* ---- Tab labels — venue step ---- */
[data-testid="stTabs"] [role="tab"] {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom-color: var(--primary) !important;
}

/* ---- Config Summary Bar ---- */
.config-bar {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    padding: 0.8rem 1.2rem;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
.config-item {
    font-size: 0.82rem;
    color: var(--text-secondary);
}
.config-item strong {
    color: var(--text-primary);
}

/* Animation for step transitions */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Completion celebration pulse */
@keyframes successPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.2); }
    50% { box-shadow: 0 0 0 8px rgba(74, 222, 128, 0); }
}

/* Category header separators */
.goal-category {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin: 0.8rem 0 0.6rem 0.2rem;
    font-weight: 600;
}

/* Onboarding card */
.onboarding-card {
    text-align: center;
    padding: 1.2rem 2rem;
    background: rgba(143, 174, 255, 0.06);
    border: 1px solid rgba(143, 174, 255, 0.15);
    border-radius: 16px;
    margin-bottom: 2rem;
}

/* Success banner */
.success-banner {
    animation: successPulse 2s ease-in-out 3;
}

/* Sidebar quick action button override */
.st-key-nav_new_session button, .st-key-nav_fresh button {
    background: var(--primary) !important;
    color: #15171C !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}
.st-key-nav_new_session button:hover, .st-key-nav_fresh button:hover {
    box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 4px 14px rgba(0,0,0,0.3) !important;
    transform: translateY(-1px) !important;
}

/* Sidebar logo/home button — gradient text branding */
.st-key-nav_home button p:first-child {
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: var(--primary) !important;
    -webkit-text-fill-color: var(--primary) !important;
}
.st-key-nav_home button p:last-child {
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    color: var(--text-secondary) !important;
    -webkit-text-fill-color: var(--text-secondary) !important;
}

/* Session resume buttons — keep each title on one line in the narrow sidebar column */
[class*="st-key-load_sess_"] button {
    padding: 0 0.75rem !important;
    height: 2.4rem !important;
    min-height: 2.4rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
}
[class*="st-key-load_sess_"] button p {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Session delete buttons — compact inline */
[class*="st-key-del_sess_"] button, .st-key-clear_all_sessions button {
    min-height: 0 !important;
    height: 2rem !important;
    width: 2rem !important;
    padding: 0 !important;
    font-size: 0.75rem !important;
    opacity: 0.5 !important;
    border: none !important;
    background: transparent !important;
}
[class*="st-key-del_sess_"] button:hover, .st-key-clear_all_sessions button:hover {
    opacity: 1 !important;
    color: var(--danger) !important;
    background: rgba(240, 126, 126, 0.1) !important;
}


/* Sidebar — always visible, no collapse/expand toggle */
[data-testid="stSidebar"] { min-width: 280px; }
[data-testid="collapsedControl"] { display: none; }
[data-testid="stSidebarCollapseButton"] { display: none; }
section[data-testid="stSidebar"] { display: block !important; transform: none !important; }

/* Sidebar top inset — tighten to align with main hero spacing */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0.2rem !important;
}

/* Sidebar — compact vertical rhythm (Streamlit's defaults leave large gaps) */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.35rem !important; }
[data-testid="stSidebar"] hr { margin: 0.4rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Theme — inject light overrides when selected
# ---------------------------------------------------------------------------
_LIGHT_CSS = """
<style>
:root {
    --bg-dark: #F6F4EF;
    --card-bg: rgba(0, 0, 0, 0.02);
    --card-border: rgba(0, 0, 0, 0.08);
    --text-primary: #23262B;
    --text-secondary: #5C6470;
}

/* Streamlit overrides for light mode */
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], section[data-testid="stSidebar"] {
    background-color: #F6F4EF !important;
    /* Subtle paper grain — gives the light theme a material quality */
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23g)' opacity='0.04'/%3E%3C/svg%3E") !important;
    color: #23262B !important;
}
[data-testid="stSidebar"] > div {
    background-color: #EFECE4 !important;
}
.stApp [data-testid="stMainBlockContainer"] {
    background-color: #F6F4EF !important;
}
.stChatMessage {
    background-color: #FFFFFF !important;
}

/* Chat message avatars (user / assistant) — override dark bg */
[data-testid="stChatMessage"] > div:first-child {
    background: rgba(48, 86, 211, 0.12) !important;
    color: #23262B !important;
}

/* Code block container (stCode) — override dark toolbar wrapper */
[data-testid="stCode"] {
    background: #EFECE4 !important;
    border-radius: 6px !important;
}
[data-testid="stCode"] > div,
[data-testid="stCode"] > div > div {
    background: transparent !important;
}

/* ============================================================
   LIGHT MODE — Universal text color reset
   Streamlit dark theme sets all text to rgba(250,250,250,1).
   Override every problematic element type explicitly.
   ============================================================ */

/* Form / widget labels (Working title, Key contributions, file uploader labels) */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label,
label[data-testid="stWidgetLabel"],
label[data-testid="stWidgetLabel"] * { color: #23262B !important; }

/* Button children — inherit from parent button (which we set to correct color).
   This fixes secondary buttons (inherit #23262B) AND primary buttons (inherit #FFFFFF). */
.stButton button p, .stButton button span,
.stButton button div, .stButton button small,
.stDownloadButton button p, .stDownloadButton button span,
.stDownloadButton button div { color: inherit !important; }

/* Chat message text */
[data-testid="stChatMessageContent"],
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] span,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] strong { color: #23262B !important; }

/* Main content area — broad reset for all text not inside code/pre */
[data-testid="stMainBlockContainer"] p:not(pre p),
[data-testid="stMainBlockContainer"] span:not(pre span):not(code span),
[data-testid="stMainBlockContainer"] li,
[data-testid="stMainBlockContainer"] label,
[data-testid="stMainBlockContainer"] h1,
[data-testid="stMainBlockContainer"] h2,
[data-testid="stMainBlockContainer"] h3,
[data-testid="stMainBlockContainer"] h4 { color: #23262B; }

/* Sidebar text */
[data-testid="stSidebar"] p:not(code p),
[data-testid="stSidebar"] span:not(code span),
[data-testid="stSidebar"] label { color: #23262B; }

/* Tab labels */
[data-testid="stTabs"] [role="tab"] p,
[data-testid="stTabs"] [role="tab"] span { color: #3E434B !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
[data-testid="stTabs"] [role="tab"][aria-selected="true"] span { color: #3056D3 !important; }

/* Caption / secondary text */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * { color: #5C6470 !important; }

/* Expander header — override dark emotion-cache background */
[data-testid="stExpander"] summary {
    background-color: rgba(0, 0, 0, 0.03) !important;
    border-bottom-color: rgba(0, 0, 0, 0.08) !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary div { color: #23262B !important; }
[data-testid="stExpander"] [data-testid="stWidgetLabel"],
[data-testid="stExpander"] [data-testid="stWidgetLabel"] * { color: #23262B !important; }
[data-testid="stExpander"] details { border-color: rgba(0, 0, 0, 0.15) !important; }
[data-testid="stExpanderDetails"] { border-top-color: rgba(0, 0, 0, 0.08) !important; }

/* Tooltip / popover content */
[data-testid="stTooltipContent"] *,
[data-testid="stPopoverBody"] * { color: #23262B !important; }

/* Alert / info boxes */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span { color: #23262B !important; }

/* File uploader instructions */
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] * { color: #5C6470 !important; }

/* Stat pill overrides (keep their own colors) */
.stat-ready, .stat-ready * { color: inherit; }
.stat-empty, .stat-empty * { color: inherit; }

/* Hero subtitle */
.hero-subtitle { color: #5C6470 !important; }

/* Stepper */
.step-pending {
    background: rgba(0, 0, 0, 0.05) !important;
    color: #7A8089 !important;
    border: 1px solid rgba(0, 0, 0, 0.14) !important;
}
.step-line { background: rgba(0, 0, 0, 0.12) !important; }

/* Stat pills */
.stat-ready {
    background: rgba(74, 222, 128, 0.12) !important;
    border-color: rgba(74, 222, 128, 0.22) !important;
}
.stat-empty {
    background: rgba(0, 0, 0, 0.05) !important;
    color: #5C6470 !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
}

/* Config bar */
.config-bar {
    background: rgba(0, 0, 0, 0.02) !important;
    border-color: rgba(0, 0, 0, 0.08) !important;
}
.config-item { color: #5C6470 !important; }
.config-item strong { color: #23262B !important; }

/* Section headers */
.section-header { color: #23262B !important; }
.section-header-center { color: #23262B !important; }
.section-desc { color: #5C6470 !important; }
.section-desc-center { color: #5C6470 !important; }
.step-page-title { color: #23262B !important; }
.step-page-subtitle { color: #5C6470 !important; }

/* Theme toggle — softer on paper */
.st-key-theme_toggle button {
    background: rgba(48, 86, 211, 0.10) !important;
    border-color: rgba(48, 86, 211, 0.25) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.10) !important;
}
.st-key-theme_toggle button:hover {
    background: rgba(48, 86, 211, 0.18) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

/* Buttons — reset dark backgrounds.
   Descendant selectors: buttons with help= are wrapped in a tooltip element,
   so `.stButton > button` would miss them and leave them dark. */
.stButton button,
.stDownloadButton button {
    background: #FFFFFF !important;
    color: #23262B !important;
    border: 1px solid #DDD8CC !important;
}
.stButton button:hover,
.stDownloadButton button:hover {
    background: #EFECE4 !important;
    border-color: rgba(48, 86, 211, 0.30) !important;
}
.stButton button[kind="primary"],
.stDownloadButton button[kind="primary"] {
    background: #3056D3 !important;
    color: #FFFFFF !important;
    border: none !important;
}
.stButton button[kind="primary"]:hover,
.stDownloadButton button[kind="primary"]:hover {
    background: #2748B8 !important;
}

/* Compact session delete buttons stay borderless */
[class*="st-key-del_sess_"] button, .st-key-clear_all_sessions button {
    background: transparent !important;
    border: none !important;
}

/* File upload dropzones */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] * {
    background: #EFECE4 !important;
    border-color: #DDD8CC !important;
    color: #23262B !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #FFFFFF !important;
    color: #23262B !important;
    border: 1px solid #DDD8CC !important;
}
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {
    color: #5C6470 !important;
}

/* Goal cards — lighter background (light mode, scoped) */
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button {
    background: #FFFFFF !important;
    border: 1px solid #DDD8CC !important;
    color: #23262B !important;
}
[data-testid="stHorizontalBlock"]:has([class*="st-key-goal_"]) > [data-testid="stColumn"] .stButton > button:hover {
    background: rgba(48, 86, 211, 0.04) !important;
    border-color: rgba(48, 86, 211, 0.35) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
}

/* Venue cards — light mode */
[class*="st-key-va_"] button, [class*="st-key-vj_"] button, [class*="st-key-vc_"] button {
    background: #FFFFFF !important;
    border-color: #DDD8CC !important;
    color: #23262B !important;
}
[class*="st-key-va_"] button:hover, [class*="st-key-vj_"] button:hover, [class*="st-key-vc_"] button:hover {
    background: rgba(48, 86, 211, 0.06) !important;
    border-color: rgba(48, 86, 211, 0.30) !important;
}

/* Nav and action buttons — keep same light bg, just ensure correct text */
.st-key-nav_back button, .st-key-nav_next button,
.st-key-nav_back2 button, .st-key-nav_next2 button,
.st-key-action_restart button, .st-key-action_output button,
.st-key-action_export button,
.st-key-nav_manual button, .st-key-nav_about button,
.st-key-footer_manual button, .st-key-footer_about button {
    background: #FFFFFF !important;
    color: #23262B !important;
    border: 1px solid #DDD8CC !important;
}
.st-key-nav_manual button p, .st-key-nav_about button p,
.st-key-nav_manual button span, .st-key-nav_about button span,
.st-key-footer_manual button p, .st-key-footer_about button p,
.st-key-footer_manual button span, .st-key-footer_about button span {
    color: #23262B !important;
}

/* Sidebar support link button — explicit light mode override */
.st-key-nav_support a,
.st-key-nav_support button {
    background: #FFFFFF !important;
    color: #3E434B !important;
    border: 1px solid #DDD8CC !important;
    text-decoration: none !important;
}
.st-key-nav_support a p,
.st-key-nav_support a span,
.st-key-nav_support button p,
.st-key-nav_support button span {
    color: inherit !important;
}
.st-key-nav_support a:hover,
.st-key-nav_support button:hover {
    background: #EFECE4 !important;
    color: #23262B !important;
    border-color: rgba(48, 86, 211, 0.30) !important;
}

/* Sidebar collapse / expand button icon */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stBaseButton-headerNoPadding"] span {
    color: #3E434B !important;
}

/* Chat input bar */
[data-testid="stBottom"] > div {
    background-color: #EFECE4 !important;
    border-top: 1px solid rgba(0, 0, 0, 0.06) !important;
}
/* Chat send button icon */
[data-testid="stChatInputSubmitButton"] {
    color: #3E434B !important;
}
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #23262B !important;
    border-color: #DDD8CC !important;
}
[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border-color: #DDD8CC !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #FFFFFF !important;
    color: #23262B !important;
    border-color: #DDD8CC !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    color: #23262B !important;
}

/* Markdown text */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1,
.stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: #23262B !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p {
    color: #23262B !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(0, 0, 0, 0.08) !important;
}

/* Body / root background */
html, body, [data-testid="stApp"] {
    background-color: #F6F4EF !important;
}

/* Code blocks — override dark syntax-highlighting theme */
pre {
    background: #EFECE4 !important;
    border: 1px solid rgba(0, 0, 0, 0.10) !important;
}
pre code {
    background: transparent !important;
    color: #23262B !important;
}
code:not(pre code) {
    background: rgba(48, 86, 211, 0.08) !important;
    color: #2748B8 !important;
}

/* Text / textarea input container */
[data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"],
[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="base-input"] {
    background: #FFFFFF !important;
    border-color: #DDD8CC !important;
}
[data-testid="stTextInputRootElement"] input,
[data-testid="stTextAreaRootElement"] textarea {
    background: #FFFFFF !important;
    color: #23262B !important;
}
[data-testid="stTextInputRootElement"] input::placeholder,
[data-testid="stTextAreaRootElement"] textarea::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="base-input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder { color: #7A8089 !important; opacity: 1 !important; }
</style>
"""

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
# First load follows the OS/browser color-scheme preference; the sidebar
# toggle still overrides it for the rest of the session.
# Detected once: on later reruns st.context.theme reports the app's configured
# (dark) Streamlit theme instead, which would flip "System" back to dark.
if "_system_theme" not in st.session_state:
    try:
        st.session_state["_system_theme"] = "light" if st.context.theme.type == "light" else "dark"
    except Exception:
        st.session_state["_system_theme"] = "dark"
_initial_theme = st.session_state["_system_theme"]

for key, default in {
    "step": 0,
    "goal": None,
    "venue": None,
    "title": "",
    "contributions": "",
    "messages": [],
    "generating": False,
    "paper_slug": None,
    "pipeline_phase": 0,
    "page": "main",
    "theme": _initial_theme,
    "theme_mode": "system",
    "reviewer_feedback": "",
    "paper_slug_revise": "",
    "support_hint_shown": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Resolve the active theme from the chosen mode ("system" follows the OS/browser)
_theme_mode = st.session_state.get("theme_mode", "system")
st.session_state.theme = _initial_theme if _theme_mode == "system" else _theme_mode

# Apply light theme CSS at top level so it covers main content
if st.session_state.theme == "light":
    st.markdown(_LIGHT_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Pipeline phase definitions per goal
# ---------------------------------------------------------------------------
PIPELINE_PHASES = {
    "write": [
        ("Collect Requirements", "Venue, title, contributions"),
        ("Ingest Sources", "Reading theses, papers, artefacts"),
        ("Learn Style", "Analyzing your writing patterns"),
        ("Plan Paper", "Structure, RQs, contributions"),
        ("Validate Novelty", "Contribution framing & stress-test"),
        ("Draft Sections", "Writing each section"),
        ("Coherence Pass", "Cross-references & consistency"),
        ("Integrity Check", "Content consistency & quality scoring"),
        ("Compliance Check", "Venue rules & page budget"),
        ("Revise", "Fix issues & improve depth"),
        ("Peer Review", "4-persona simulated review"),
        ("Assemble Paper", "Final manuscript & pitch"),
        ("Complete", "Paper ready for submission"),
    ],
    "improve": [
        ("Read Draft", "Understanding current state"),
        ("Analyze Gaps", "Finding areas to improve"),
        ("Expand Sections", "Deepening content"),
        ("Coherence Pass", "Consistency & flow"),
        ("Integrity Check", "Content consistency & quality scoring"),
        ("Compliance Check", "Venue rules & page budget"),
        ("Revise", "Iterative improvement"),
        ("Complete", "Draft improved"),
    ],
    "review": [
        ("Read Paper", "Understanding the manuscript"),
        ("Methodologist", "Rigor & validity review"),
        ("Domain Expert", "Technical depth review"),
        ("Skeptic", "Challenging assumptions"),
        ("Compile Report", "Unified review summary"),
        ("Complete", "Review delivered"),
    ],
    "submit": [
        ("Read Context", "Paper, venue, authors"),
        ("Cover Letter", "Drafting cover letter"),
        ("Highlights", "Key findings summary"),
        ("Reviewers", "Suggesting reviewers"),
        ("Checklists", "Pre-submission checks"),
        ("Complete", "Package ready"),
    ],
    "plan": [
        ("Inventory Sources", "Scanning available material"),
        ("Identify Papers", "Extractable publications"),
        ("Sequence", "Dependencies & timeline"),
        ("Self-Plagiarism", "Prevention rules"),
        ("Complete", "Agenda delivered"),
    ],
    "revise": [
        ("Parse Feedback", "Extracting reviewer concerns"),
        ("Audit Sources", "Inventorying all workspace files"),
        ("Response Matrix", "Mapping comments to actions"),
        ("Revise Manuscript", "Rewriting sections directly"),
        ("Rigour Check", "Statistics, baselines, evidence"),
        ("Consistency Pass", "Abstract, intro, conclusion sync"),
        ("Source Audit", "Used vs. unused sources"),
        ("Gap Analysis", "Remaining risks & missing evidence"),
        ("Compliance Check", "Venue rules & formatting"),
        ("Complete", "Revised manuscript ready"),
    ],
    "quality": [
        ("Read Paper", "Loading manuscript sections"),
        ("Verify Citations", "Checking reference traceability"),
        ("Writing Quality", "AI-tell detection & grading"),
        ("Integrity Check", "Cross-section consistency"),
        ("Generate Reports", "Scores & substitution table"),
        ("Complete", "Quality reports delivered"),
    ],
    "lit-review": [
        ("Load Sources", "Reading ingested summaries"),
        ("Thematic Classification", "Grouping by theme"),
        ("Gap Analysis", "What's missing in the literature"),
        ("Evolution Timeline", "How the field developed"),
        ("Draft Related Work", "Writing the section"),
        ("Complete", "Literature review ready"),
    ],
    "convert": [
        ("Read Paper", "Loading source manuscript"),
        ("Conversion Plan", "Analyzing format differences"),
        ("Convert Citations", "Changing citation style"),
        ("Restructure", "Sections, naming, order"),
        ("Page Budget", "Recalculating word targets"),
        ("Complete", "Converted paper ready"),
    ],
    "rebuttal": [
        ("Parse Feedback", "Extracting reviewer comments"),
        ("Read Paper", "Loading manuscript sections"),
        ("Classify Comments", "Accept, partial, rebuttal, defer"),
        ("Draft Response", "Point-by-point letter"),
        ("Evidence Check", "Supporting each response"),
        ("Complete", "Rebuttal letter ready"),
    ],
    "coach": [
        ("Load Feedback", "Reading reviewer comments"),
        ("Categorize", "Type, severity, effort"),
        ("Socratic Walk", "Guided per-comment discussion"),
        ("Build Plan", "Compiling revision plan"),
        ("Complete", "Revision plan ready"),
    ],
    "audit": [
        ("Cold Read", "Reading paper fresh"),
        ("Marker Check", "Unresolved TODOs & gaps"),
        ("Number Check", "Cross-section consistency"),
        ("AI-Tell Scan", "Detecting machine patterns"),
        ("Full Audit", "References, structure, readability"),
        ("Complete", "Audit report delivered"),
    ],
    "feedback": [
        ("Parse Comments", "Reading advisor/co-author feedback"),
        ("Read Paper", "Loading current draft"),
        ("Triage", "Prioritizing suggestions"),
        ("Apply Changes", "Integrating feedback"),
        ("Coherence Pass", "Consistency after edits"),
        ("Complete", "Feedback integrated"),
    ],
    "import": [
        ("Read File", "Extracting text from paper"),
        ("Identify Sections", "Finding headings & structure"),
        ("Split Sections", "Creating individual section files"),
        ("Extract References", "Building references.bib"),
        ("Ingest as Source", "Creating knowledge summary"),
        ("Complete", "Paper imported"),
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _count_files(folder: Path, exclude: set[str] | None = None) -> int:
    exclude = exclude or {"README.md"}
    if not folder.exists():
        return 0
    return sum(
        1 for f in folder.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.name not in exclude
    )


def _save_uploaded(files, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        target = dest / f.name
        target.write_bytes(f.getvalue())


def _read_venue_summary(venue_key: str) -> str | None:
    path = VENUES_DIR / venue_key / "requirements-summary.md"
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return None


def _list_output_papers() -> list[str]:
    if not OUTPUT_DIR.exists():
        return []
    return sorted(
        d.name
        for d in OUTPUT_DIR.iterdir()
        if d.is_dir() and d.name != "knowledge"
        and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())
    )


def _detect_phase(response: str, goal: str) -> int:
    """Detect which pipeline phase Claude is working on from its response text."""
    text = response.lower()
    current = st.session_state.get("pipeline_phase", 0)
    phases = PIPELINE_PHASES.get(goal, [])

    if goal == "write":
        phase_keywords = [
            ["requirement", "venue", "target conference", "target journal"],
            ["ingest", "reading source", "reading your thesis", "source summar"],
            ["style", "writing pattern", "prose pattern", "style profile"],
            ["plan", "structure", "research question", "paper type", "contribution"],
            ["novelty", "framing", "stress-test", "validity threat"],
            ["draft", "writing the", "writing section", "introduction", "methodology", "related work", "abstract"],
            ["coherence", "cross-reference", "consistency", "acronym"],
            ["integrity", "cross-section", "contradiction", "score", "quality scoring"],
            ["compliance", "page budget", "formatting", "venue rule"],
            ["revis", "fix", "iteration", "improving"],
            ["peer review", "reviewer", "methodologist", "domain expert", "skeptic"],
            ["assembl", "full paper", "concatenat", "elevator pitch"],
            ["complete", "finished", "ready for submission", "delivered"],
        ]
    elif goal == "improve":
        phase_keywords = [
            ["reading", "current draft", "analyzing your"],
            ["gap", "weakness", "area to improve", "missing"],
            ["expand", "deepen", "adding content", "writing"],
            ["coherence", "consistency", "flow"],
            ["integrity", "cross-section", "contradiction", "score"],
            ["compliance", "page budget", "formatting"],
            ["revis", "fix", "iteration"],
            ["complete", "improved", "finished"],
        ]
    elif goal == "review":
        phase_keywords = [
            ["reading", "understanding", "manuscript"],
            ["methodolog", "rigor", "validity"],
            ["domain", "technical", "depth"],
            ["skeptic", "assumption", "challenge"],
            ["compil", "summary", "overall"],
            ["complete", "review delivered", "finished"],
        ]
    elif goal == "submit":
        phase_keywords = [
            ["reading", "context", "paper and venue"],
            ["cover letter"],
            ["highlight"],
            ["reviewer", "suggest"],
            ["checklist", "pre-submission"],
            ["complete", "package ready", "finished"],
        ]
    elif goal == "plan":
        phase_keywords = [
            ["inventory", "scanning", "available material"],
            ["identify", "extractable", "potential paper"],
            ["sequence", "timeline", "dependency"],
            ["self-plagiarism", "overlap"],
            ["complete", "agenda", "finished"],
        ]
    elif goal == "revise":
        phase_keywords = [
            ["parse", "reviewer comment", "feedback", "major concern", "minor concern"],
            ["audit", "source folder", "inventory", "workspace"],
            ["response matrix", "reviewer response", "action item", "mapping"],
            ["revis", "rewriting", "section", "methodology", "introduction"],
            ["statistical rigour", "baseline", "effect size", "p-value"],
            ["consistency", "coherence", "abstract", "conclusion"],
            ["source utilisation", "unused source", "used source"],
            ["gap analysis", "unresolved", "missing evidence", "remaining risk"],
            ["compliance", "formatting", "page budget"],
            ["complete", "revised manuscript", "finished", "ready"],
        ]
    elif goal == "rebuttal":
        phase_keywords = [
            ["parse", "reviewer comment", "feedback", "extracting"],
            ["reading", "manuscript", "section"],
            ["classify", "accept", "partial", "rebuttal only", "defer"],
            ["draft", "response", "point-by-point", "letter"],
            ["evidence", "support", "source"],
            ["complete", "rebuttal", "finished", "ready"],
        ]
    elif goal == "coach":
        phase_keywords = [
            ["load", "reading", "reviewer", "feedback"],
            ["categoriz", "classify", "type", "severity"],
            ["socratic", "question", "what do you think", "which approach"],
            ["revision plan", "compiling", "building plan"],
            ["complete", "plan ready", "finished"],
        ]
    elif goal == "audit":
        phase_keywords = [
            ["cold read", "reading", "fresh", "from scratch"],
            ["marker", "unresolved", "todo", "material gap"],
            ["number", "consistency", "quantitative"],
            ["ai-tell", "ai tell", "writing pattern", "delve", "moreover"],
            ["reference", "structure", "formatting", "readability"],
            ["complete", "audit report", "verdict", "ready", "finished"],
        ]
    elif goal == "feedback":
        phase_keywords = [
            ["parse", "reading", "comment", "advisor", "co-author"],
            ["reading", "current draft", "manuscript"],
            ["triage", "prioritiz", "categoriz"],
            ["apply", "integrat", "rewriting", "edit"],
            ["coherence", "consistency", "flow"],
            ["complete", "integrated", "finished"],
        ]
    elif goal == "import":
        phase_keywords = [
            ["reading", "extract", "text", "pdf", "file"],
            ["identify", "section", "heading", "structure"],
            ["split", "creating", "section file", "abstract.md", "introduction"],
            ["reference", "bibtex", "bib"],
            ["ingest", "knowledge", "source summary"],
            ["complete", "imported", "finished", "ready"],
        ]
    elif goal == "quality":
        phase_keywords = [
            ["reading", "loading", "manuscript", "section"],
            ["citation", "reference", "traceab", "bibtex"],
            ["ai-tell", "writing quality", "delve", "moreover", "filler"],
            ["integrity", "cross-section", "consistency", "contradiction"],
            ["report", "score", "grade", "substitution"],
            ["complete", "delivered", "finished"],
        ]
    elif goal == "lit-review":
        phase_keywords = [
            ["reading", "loading", "source", "ingested"],
            ["thematic", "theme", "group", "classif"],
            ["gap", "missing", "underexplored"],
            ["evolution", "timeline", "development"],
            ["draft", "writing", "related work"],
            ["complete", "ready", "finished"],
        ]
    elif goal == "convert":
        phase_keywords = [
            ["reading", "loading", "source", "manuscript"],
            ["conversion", "format", "difference", "plan"],
            ["citation", "reference", "style"],
            ["restructur", "section", "naming", "reorder"],
            ["page budget", "word", "target", "recalcul"],
            ["complete", "converted", "ready", "finished"],
        ]
    else:
        return current

    # Find the highest matching phase
    detected = current
    for i, keywords in enumerate(phase_keywords):
        if i >= current and any(kw in text for kw in keywords):
            detected = i
    # Don't jump more than 2 phases at once (avoids false positives)
    return min(detected, current + 2, len(phases) - 1)


def _render_pipeline_tracker(goal: str, current_phase: int):
    """Render a vertical pipeline tracker in the sidebar."""
    phases = PIPELINE_PHASES.get(goal, [])
    if not phases:
        return

    html = '<div style="padding: 0.5rem 0;">'
    html += '<p style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 0.8rem;">Pipeline Progress</p>'

    for i, (name, desc) in enumerate(phases):
        if i < current_phase:
            # Completed
            circle_style = "background: var(--success); color: var(--bg-dark);"
            circle_content = "✓"
            name_style = "color: var(--success);"
            desc_style = "color: #555;"
            line_color = "var(--success)"
        elif i == current_phase:
            # Active
            circle_style = "background: var(--primary); color: #15171C; box-shadow: 0 0 0 4px rgba(143, 174, 255, 0.15);"
            circle_content = "●"
            name_style = "color: var(--text-primary); font-weight: 600;"
            desc_style = "color: var(--primary);"
            line_color = "rgba(255,255,255,0.08)"
        else:
            # Pending
            circle_style = "background: rgba(255,255,255,0.04); color: #555; border: 1px solid rgba(255,255,255,0.08);"
            circle_content = "○"
            name_style = "color: #555;"
            desc_style = "color: #3a3a4a;"
            line_color = "rgba(255,255,255,0.04)"

        html += f'''
        <div style="display: flex; gap: 10px; align-items: flex-start; position: relative;">
            <div style="display: flex; flex-direction: column; align-items: center; min-width: 28px;">
                <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; {circle_style}">
                    {circle_content}
                </div>
                {"" if i == len(phases) - 1 else f'<div style="width: 2px; height: 20px; background: {line_color};"></div>'}
            </div>
            <div style="padding-top: 3px;">
                <div style="font-size: 0.78rem; {name_style}">{name}</div>
                <div style="font-size: 0.68rem; {desc_style}">{desc}</div>
            </div>
        </div>
        '''

    # Progress percentage
    pct = int((current_phase / max(len(phases) - 1, 1)) * 100)
    html += f'''
    <div style="margin-top: 1rem; background: rgba(255,255,255,0.04); border-radius: 6px; height: 4px; overflow: hidden;">
        <div style="width: {pct}%; height: 100%; background: var(--primary); border-radius: 6px; transition: width 0.5s ease;"></div>
    </div>
    <p style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 4px; text-align: center;">{pct}% complete</p>
    '''

    html += '</div>'
    st.html(html)


def _render_stepper(current: int):
    """Render a visual step progress indicator with contextual labels."""
    goal = st.session_state.get("goal")
    # Goals that skip the venue step (the wizard jumps 0 → 2) get a 3-step
    # indicator with the wizard index remapped, so the highlighted step
    # matches the screen the user is actually on.
    _three_step = {
        "rebuttal": ["Goal", "Paper & Feedback", "Revise"],
        "coach": ["Goal", "Paper & Feedback", "Coach"],
        "feedback": ["Goal", "Paper & Feedback", "Integrate"],
        "quality": ["Goal", "Select Paper", "Analyze"],
        "audit": ["Goal", "Select Paper", "Audit"],
        "import": ["Goal", "Upload", "Import"],
        "convert": ["Goal", "Convert", "Process"],
        "lit-review": ["Goal", "Topic", "Analyze"],
    }
    if goal in _three_step:
        steps = _three_step[goal]
        current = {0: 0, 1: 1, 2: 1, 3: 2}.get(current, current)
    elif goal == "revise":
        steps = ["Goal", "Venue", "Paper & Feedback", "Revise"]
    elif goal == "improve":
        steps = ["Goal", "Venue", "Paper", "Improve"]
    elif goal == "review":
        steps = ["Goal", "Venue", "Paper", "Review"]
    elif goal == "submit":
        steps = ["Goal", "Venue", "Paper", "Package"]
    else:
        steps = ["Goal", "Venue", "Details", "Write"]
    html_parts = ['<div class="stepper" style="flex-direction: column; max-width: 560px; margin: 1.5rem auto 2rem;">']
    # Top row: circles + lines
    html_parts.append('<div style="display: flex; justify-content: center; align-items: center; gap: 0;">')
    for i, label in enumerate(steps):
        if i < current:
            cls = "step-done"
            icon = "✓"
        elif i == current:
            cls = "step-active"
            icon = str(i + 1)
        else:
            cls = "step-pending"
            icon = str(i + 1)
        html_parts.append(f'<div class="step-item"><div class="step-circle {cls}">{icon}</div></div>')
        if i < len(steps) - 1:
            line_cls = "step-line step-line-done" if i < current else "step-line"
            html_parts.append(f'<div class="{line_cls}" style="width:80px;"></div>')
    html_parts.append('</div>')
    # Bottom row: labels
    html_parts.append('<div style="display: flex; justify-content: center; align-items: flex-start; gap: 0; margin-top: 6px;">')
    for i, label in enumerate(steps):
        active_color = "var(--primary)" if i == current else ("var(--success)" if i < current else "var(--text-secondary)")
        fw = "600" if i == current else "400"
        html_parts.append(
            f'<div style="width:36px; text-align:center; font-size:0.65rem; font-weight:{fw}; color:{active_color}; white-space:nowrap; transform: translateX(0);">{label}</div>'
        )
        if i < len(steps) - 1:
            html_parts.append('<div style="width:80px;"></div>')
    html_parts.append('</div>')
    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def _build_system_prompt(goal: str, venue: str, title: str, contributions: str) -> str:
    prompt_map = {
        "write": "write-paper",
        "improve": "improve-paper",
        "review": "simulate-review",
        "submit": "prepare-submission",
        "plan": "plan-agenda",
        "revise": "revise-paper",
        "quality": "check-quality",
        "lit-review": "lit-review",
        "convert": "convert-format",
        "rebuttal": "draft-rebuttal",
        "coach": "coach-revision",
        "audit": "final-audit",
        "feedback": "get-feedback",
        "import": "import-paper",
    }
    prompt_file = WORKSPACE / ".github" / "prompts" / f"{prompt_map.get(goal, 'write-paper')}.prompt.md"
    base_prompt = ""
    agent_context = ""
    if prompt_file.exists():
        raw = prompt_file.read_text(encoding="utf-8", errors="replace")
        frontmatter, base_prompt = "", raw
        if raw.startswith("---"):
            end = raw.find("---", 3)
            if end != -1:
                frontmatter = raw[3:end]
                base_prompt = raw[end + 3:].strip()
        # Prompts that run under an agent (VS Code: `agent: academic-writer`)
        # rely on the agent file for the full workflow — prepend it, mirroring
        # what the VS Code runtime does.
        m = re.search(r"^agent:\s*['\"]?([\w-]+)['\"]?\s*$", frontmatter, re.MULTILINE)
        if m:
            agent_file = WORKSPACE / ".github" / "agents" / f"{m.group(1)}.agent.md"
            if agent_file.exists():
                agent_body = agent_file.read_text(encoding="utf-8", errors="replace")
                if agent_body.startswith("---"):
                    a_end = agent_body.find("---", 3)
                    if a_end != -1:
                        agent_body = agent_body[a_end + 3:].strip()
                agent_context = (
                    f"## Your Agent Instructions ({m.group(1)})\n\n{agent_body}\n\n"
                    f"---\n\n## Command Workflow\n\n"
                )
    base_prompt = agent_context + base_prompt

    knowledge_context = ""
    sources_dir = KNOWLEDGE_DIR / "sources"
    if sources_dir.exists():
        source_files = sorted(sources_dir.glob("*.md"))
        # Cap at 10 sources, 2000 chars each to avoid bloating system prompt (~20K chars max)
        for f in source_files[:10]:
            content = f.read_text(encoding="utf-8", errors="replace")
            knowledge_context += f"\n\n### Source: {f.stem}\n{content[:2000]}"
        if len(source_files) > 10:
            knowledge_context += f"\n\n*(+{len(source_files) - 10} more sources available — use read_file tool to access them)*"

    style_path = KNOWLEDGE_DIR / "style-profile.md"
    style_context = ""
    if style_path.exists():
        style_context = f"\n\n### Style Profile\n{style_path.read_text(encoding='utf-8', errors='replace')[:2000]}"

    venue_context = ""
    venue_summary = _read_venue_summary(venue) if venue else None
    if venue_summary:
        venue_context = f"\n\n### Venue Requirements\n{venue_summary}"

    reviewer_feedback = st.session_state.get("reviewer_feedback", "")
    paper_slug_revise = st.session_state.get("paper_slug_revise", "")
    revise_context = ""

    # For goals that operate on an existing paper, include the paper slug
    if goal in ("quality", "audit", "convert", "feedback", "coach", "rebuttal", "import", "improve", "review", "submit") and paper_slug_revise:
        revise_context = f"\n## Paper Slug\n{paper_slug_revise}\n"
        if reviewer_feedback and goal in ("rebuttal", "coach", "feedback"):
            revise_context += f"\n## Reviewer Feedback\n{reviewer_feedback}\n"

    if goal == "revise":
        # Check if paper exists in output/ or needs to be imported from submitted-papers
        paper_exists = False
        if paper_slug_revise:
            paper_dir = OUTPUT_DIR / paper_slug_revise
            paper_exists = paper_dir.exists() and any(f.suffix == ".md" for f in paper_dir.iterdir() if f.is_file())
        submitted_papers_dir = SOURCES_DIR / "submitted-papers"
        submitted_files = list(submitted_papers_dir.iterdir()) if submitted_papers_dir.exists() else []
        import_note = ""
        if not paper_exists and submitted_files:
            import_note = f"\n\n**IMPORTANT:** The paper has not been imported yet. First run the import-paper workflow to split the submitted paper at `sources/submitted-papers/` into section files under `output/{paper_slug_revise or '<slug>'}/`, then proceed with revision."

        revise_context = f"""
## Paper Slug
{paper_slug_revise or 'Not specified — look for paper drafts in output/'}
{import_note}

## Reviewer Feedback
{reviewer_feedback[:8000] if reviewer_feedback else 'No reviewer feedback provided yet — check sources/reviewer-feedback/ for uploaded files, or ask the user to paste the comments.'}
{"[... feedback truncated in system prompt — use read_file on sources/reviewer-feedback/ for the full text ...]" if reviewer_feedback and len(reviewer_feedback) > 8000 else ""}
"""

    return f"""You are DaVinci, an AI academic paper writing assistant.

{base_prompt}

## User Context
- Goal: {goal}
- Venue: {venue or 'Not specified'}
- Title: {title or 'To be determined'}
- Contributions: {contributions or 'To be determined from sources'}
{revise_context}
## Available Knowledge
{knowledge_context}
{style_context}
{venue_context}

## Tool Usage
You have access to file system tools: read_file, write_file, list_directory, search_files, search_text, and read_pdf — plus verify_reference, which checks a citation against the Crossref database of published works (use it during citation verification; if it errors, the machine is offline — fall back to source-traceability checks).
USE THESE TOOLS to:
- Read source documents, reviewer feedback, and existing paper sections
- Write new section files and output documents to the workspace
- List directories to discover available content
- Search for specific content across files
- Extract text from PDF files

IMPORTANT: Always use tools to read files before referencing their content. Always use write_file to save outputs — do NOT just print the content in your response. Save all paper sections to `output/<paper-slug>/` as individual `.md` files.

When importing a paper, use read_file (or read_pdf for PDFs) to get the content, then use write_file to create each section file.
When revising a paper, read all relevant sections and reviewer feedback with tools, then write the revised content back with write_file.

Respond in Markdown. Be thorough and scholarly. Follow the pipeline phases.

IMPORTANT: At the start of each pipeline phase, clearly announce it with a heading like:
## Phase: Parsing Reviewer Feedback
## Phase: Auditing Source Folders
## Phase: Revising Introduction
This helps the UI track your progress visually.
"""


# ---------------------------------------------------------------------------
# Tool definitions for the agentic loop
# ---------------------------------------------------------------------------


def _call_claude(system_prompt: str, user_message: str, progress_placeholder=None) -> str:
    """Call the model with an agentic tool-use loop. Continues until it stops calling tools.

    Talks to the Anthropic cloud API by default, or to any Anthropic-format
    endpoint (e.g. a LiteLLM proxy in front of Ollama) when ANTHROPIC_BASE_URL
    is set — see Settings → Model & Costs → Local / Custom Endpoint.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    base_url = _custom_base_url()
    if not api_key and not base_url:
        return (
            "⚠️ **API key not configured.**\n\n"
            "To use the web UI with live generation, create a `.env` file "
            "in the DaVinci root folder:\n\n"
            "```\nANTHROPIC_API_KEY=sk-ant-...\n```\n\n"
            "Or configure a local endpoint in **Settings → Model & Costs**, "
            "or use the VS Code Copilot Chat with `/start` — no API key needed."
        )

    try:
        import anthropic
        client = anthropic.Anthropic(
            # Local endpoints usually need no real key, but the SDK requires one.
            api_key=api_key or "sk-local-no-key",
            base_url=base_url or None,
        )

        # Reuse the full agentic history (including tool exchanges) from earlier
        # turns in this browser session so the model keeps what it already read
        # instead of re-reading every file each turn. Falls back to the display
        # history on the first turn (or after Start Over).
        messages = list(st.session_state.get("_agent_messages") or [])
        if not messages:
            history = st.session_state.messages
            if len(history) > 20:
                # Keep first message (initial context) + last 18 messages
                history = history[:2] + history[-18:]
            messages = [{"role": m["role"], "content": m["content"]} for m in history]
        elif len(messages) > 40:
            # Trim old turns at an assistant boundary (keeps tool pairs adjacent)
            start = max(1, len(messages) - 30)
            while start < len(messages) and messages[start]["role"] != "assistant":
                start += 1
            if start < len(messages):
                messages = messages[:1] + messages[start:]
        # Callers append the user message to session history before calling us —
        # only add it if it isn't already the last message (avoids sending it twice).
        if not messages or messages[-1]["role"] != "user" or messages[-1]["content"] != user_message:
            messages.append({"role": "user", "content": user_message})

        # Cache the (static) tool definitions + system prompt together: tools
        # render before system, so one breakpoint on the system block covers
        # both across every loop iteration and every turn in the session.
        # Custom/local endpoints may reject Anthropic cache markers — send a
        # plain system prompt there instead.
        if base_url:
            cached_system = system_prompt
        else:
            cached_system = [{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }]

        # Agentic loop: keep calling until model stops using tools
        max_iterations = 40  # Safety limit
        all_text_parts = []
        tool_log = []
        finished_cleanly = False
        response = None
        model = _model_for_goal(st.session_state.get("goal"))
        usage_totals = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
        _MAX_TOOL_RESULT_CHARS = 30000  # Cap individual tool results to ~7.5K tokens

        for iteration in range(max_iterations):
            # Move the conversation cache breakpoint to the newest message so
            # each request reuses the previous request's prefix (cloud only).
            _strip_cache_markers(messages)
            if not base_url:
                _mark_cache_breakpoint(messages)
            # Ephemeral slot for this iteration's streamed text; tool lines
            # below it accumulate as a permanent activity timeline.
            stream_ph = progress_placeholder.empty() if progress_placeholder else None
            try:
                # Stream so long drafting turns show live progress and avoid
                # HTTP timeouts on large max_tokens responses.
                with client.messages.stream(
                    model=model,
                    max_tokens=16384,
                    system=cached_system,
                    messages=messages,
                    tools=_CLAUDE_TOOLS,
                ) as stream:
                    streamed = ""
                    last_shown = 0
                    for text in stream.text_stream:
                        streamed += text
                        # Throttle placeholder updates to keep the UI responsive
                        if stream_ph and len(streamed) - last_shown > 300:
                            stream_ph.markdown(":material/stylus_note: …" + streamed[-1500:])
                            last_shown = len(streamed)
                    response = stream.get_final_message()
                if stream_ph:
                    stream_ph.empty()
                usage = response.usage
                usage_totals["input"] += usage.input_tokens or 0
                usage_totals["output"] += usage.output_tokens or 0
                usage_totals["cache_read"] += getattr(usage, "cache_read_input_tokens", 0) or 0
                usage_totals["cache_write"] += getattr(usage, "cache_creation_input_tokens", 0) or 0
            except anthropic.BadRequestError as e:
                # Context window overflow — trim the middle of the conversation.
                # Cut only at an assistant-message boundary so tool_use blocks are
                # never separated from their adjacent tool_result message (a split
                # pair makes every subsequent request fail with a 400).
                if "too long" in str(e).lower() or "token" in str(e).lower():
                    start = max(1, len(messages) - 5)
                    while start < len(messages) and messages[start]["role"] != "assistant":
                        start += 1
                    if start < len(messages) - 1 and len(messages) > 4:
                        messages = messages[:1] + messages[start:]
                        all_text_parts.append("\n\n⚠️ *Context limit reached — trimmed conversation history to continue.*\n\n")
                        continue
                    return f"⚠️ **Context limit exceeded.** The system prompt and inputs are too large for a single API call. Try with fewer sources or shorter reviewer feedback.\n\nError: {e}"
                raise

            # Collect text blocks and tool-use blocks
            text_parts = []
            tool_uses = []
            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            # Accumulate text output
            if text_parts:
                all_text_parts.extend(text_parts)

            # If no tool calls, or max_tokens reached, we're done
            if not tool_uses or response.stop_reason == "max_tokens":
                if response.stop_reason == "max_tokens":
                    all_text_parts.append("\n\n⚠️ *Response cut off due to token limit — type 'continue' to resume.*")
                finished_cleanly = True
                break

            # Execute tools and build tool_result messages
            # Add the assistant message with all content blocks
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool and collect results
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use.name
                tool_input = tool_use.input

                # Append a permanent line to the activity timeline
                if progress_placeholder:
                    action_desc = _tool_action_description(tool_name, tool_input)
                    progress_placeholder.markdown(f":material/arrow_forward: {action_desc}")

                result = _execute_tool(tool_name, tool_input)
                # Truncate large tool results to prevent context overflow
                if len(result) > _MAX_TOOL_RESULT_CHARS:
                    result = result[:_MAX_TOOL_RESULT_CHARS] + f"\n\n[... truncated at {_MAX_TOOL_RESULT_CHARS // 1000}KB — use read_file with a specific section if you need more ...]"
                tool_log.append(f"🔧 `{tool_name}({', '.join(f'{k}={repr(v)[:60]}' for k, v in tool_input.items())})`")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})

        if not finished_cleanly:
            all_text_parts.append(
                f"\n\n⚠️ *Stopped after {max_iterations} tool iterations — the task may be incomplete. Type 'continue' to resume.*"
            )

        # Accumulate session-wide usage and an estimated cost for the sidebar
        # (a local endpoint costs nothing)
        p_in, p_out = (0.0, 0.0) if base_url else _MODEL_PRICES.get(model, (3.00, 15.00))
        turn_cost = (
            usage_totals["input"] * p_in
            + usage_totals["cache_read"] * p_in * 0.1
            + usage_totals["cache_write"] * p_in * 1.25
            + usage_totals["output"] * p_out
        ) / 1_000_000
        session_usage = st.session_state.setdefault("_session_usage", {"in": 0, "out": 0, "cost": 0.0})
        session_usage["in"] += usage_totals["input"] + usage_totals["cache_read"] + usage_totals["cache_write"]
        session_usage["out"] += usage_totals["output"]
        session_usage["cost"] += turn_cost
        # Per-turn history for the sidebar sparkline (last 12 turns)
        turn_costs = st.session_state.setdefault("_turn_costs", [])
        turn_costs.append(turn_cost)
        del turn_costs[:-12]

        # Persist the agentic history (with tool exchanges) for the next turn.
        # On a clean finish the final assistant message hasn't been appended yet.
        if finished_cleanly and response is not None:
            st.session_state["_agent_messages"] = messages + [{"role": "assistant", "content": response.content}]
        else:
            st.session_state["_agent_messages"] = messages

        # Expose the call count so the caller can label the activity timeline
        st.session_state["_last_tool_count"] = len(tool_log)

        # Combine all text output
        final_text = "\n\n".join(all_text_parts)

        # Append tool activity log if tools were used
        if tool_log:
            log_summary = "\n".join(tool_log[:20])
            if len(tool_log) > 20:
                log_summary += f"\n... and {len(tool_log) - 20} more tool calls"
            uncached = usage_totals["input"]
            cached = usage_totals["cache_read"]
            cache_pct = (cached / (cached + uncached) * 100) if (cached + uncached) else 0
            log_summary += (
                f"\n\n📊 Tokens: {uncached + cached:,} in ({cache_pct:.0f}% from cache) · "
                f"{usage_totals['output']:,} out · {usage_totals['cache_write']:,} cache write"
            )
            final_text += f"\n\n---\n<details><summary>🔧 Tool Activity ({len(tool_log)} calls)</summary>\n\n{log_summary}\n\n</details>"

        return final_text

    except _ST_CONTROL_EXC:
        # Streamlit is stopping/rerunning the script (e.g. the user clicked
        # Stop) — let it through, never convert it to an error message.
        raise
    except Exception as e:
        # Transient API failures are surfaced via st.error at the call site
        # rather than persisted into chat history (where they would be re-sent
        # to the model as context on every later turn). Any text generated
        # before the failure is still returned and kept.
        st.session_state["_last_call_error"] = str(e)
        partial = "\n\n".join(locals().get("all_text_parts") or [])
        return partial or None


def _tool_action_description(tool_name: str, tool_input: dict) -> str:
    """Generate a human-readable description of a tool action."""
    if tool_name == "read_file":
        return f"Reading `{tool_input.get('path', '...')}`"
    elif tool_name == "write_file":
        return f"Writing `{tool_input.get('path', '...')}`"
    elif tool_name == "list_directory":
        return f"Listing `{tool_input.get('path', '.')}/`"
    elif tool_name == "search_files":
        return f"Searching for `{tool_input.get('pattern', '...')}`"
    elif tool_name == "search_text":
        return f"Searching text: \"{tool_input.get('query', '...')[:30]}\""
    elif tool_name == "read_pdf":
        return f"Extracting PDF: `{tool_input.get('path', '...')}`"
    return f"Running {tool_name}"


# ---------------------------------------------------------------------------
# Sidebar — Minimal Status Panel
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Theme toggle — top-right of main content, always visible
# ---------------------------------------------------------------------------
_theme_css = """
<style>
.st-key-theme_toggle {
    position: fixed;
    top: 0.6rem;
    right: 1rem;
    z-index: 999;
}
.st-key-theme_toggle button {
    background: rgba(143, 174, 255, 0.18) !important;
    border: 1.5px solid rgba(143, 174, 255, 0.35) !important;
    border-radius: 50% !important;
    width: 2.6rem !important;
    height: 2.6rem !important;
    min-height: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.3rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 4px 14px rgba(0,0,0,0.3) !important;
    cursor: pointer !important;
    backdrop-filter: blur(8px) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}
.st-key-theme_toggle button:hover {
    background: rgba(143, 174, 255, 0.28) !important;
    border-color: rgba(143, 174, 255, 0.50) !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 4px 14px rgba(0,0,0,0.3) !important;
    transform: scale(1.08) !important;
}
.st-key-theme_toggle button p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}
.st-key-theme_toggle button div {
    padding: 0 !important;
    min-height: 0 !important;
    gap: 0 !important;
}
</style>
"""
st.markdown(_theme_css, unsafe_allow_html=True)
_theme_icon = ":material/light_mode:" if st.session_state.theme == "dark" else ":material/dark_mode:"
if st.button(_theme_icon, key="theme_toggle"):
    # Explicit toggle overrides "system" mode for the rest of the session
    st.session_state.theme_mode = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

with st.sidebar:
    # ── Logo (clickable — returns to home) ────────────────────────────────
    st.markdown("""
    <style>
    .st-key-nav_home {
        margin-top: -2rem !important;
    }
    .st-key-nav_home button {
        background: none !important;
        border: none !important;
        padding: 0.25rem 0 0.3rem 0 !important;
        text-align: left !important;
        width: 100% !important;
        cursor: pointer !important;
        min-height: 0 !important;
        height: auto !important;
    }
    .st-key-nav_home button:hover {
        opacity: 0.8 !important;
        background: none !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .st-key-nav_home button div[data-testid="stMarkdownContainer"] {
        text-align: left !important;
    }
    .st-key-nav_home button p {
        margin: 0 !important;
        text-align: left !important;
    }
    .st-key-nav_home button img {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        max-height: none !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if _HAS_LOGO:
        # Data-URI so the image can live inside the button's markdown label
        # (st.button can't wrap arbitrary child elements like st.image).
        import base64
        _logo_mime = "image/png" if _LOGO_PATH.suffix.lower() == ".png" else "image/jpeg"
        _logo_b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode()
        _brand_label = f"![DaVinci Writer](data:{_logo_mime};base64,{_logo_b64})"
    else:
        _brand_label = "✦ **DaVinci Writer**\n\nAI-Powered Academic Paper Assistant"
    if st.button(_brand_label, key="nav_home", width="stretch"):
        st.session_state.step = 0
        st.session_state.page = "main"
        st.rerun()

    # ── Shared data (computed once, used in summary + expanders) ──────────
    sources_info = {
        "Theses":    _count_files(SOURCES_DIR / "theses"),
        "Artefacts": _count_files(SOURCES_DIR / "artefacts"),
        "Papers":    _count_files(SOURCES_DIR / "papers"),
        "My Papers": _count_files(SOURCES_DIR / "my-papers"),
        "Reviewer Feedback": _count_files(SOURCES_DIR / "reviewer-feedback"),
        "Response Letters": _count_files(SOURCES_DIR / "my-response-letters"),
    }
    n_sources = _count_files(KNOWLEDGE_DIR / "sources") if (KNOWLEDGE_DIR / "sources").exists() else 0
    has_style = (KNOWLEDGE_DIR / "style-profile.md").exists()
    completed = _list_output_papers()

    # ── 1-line status summary ─────────────────────────────────────────────
    _parts = []
    _total_files = sum(sources_info.values())
    if _total_files > 0:
        _parts.append(f"{_total_files} source{'s' if _total_files != 1 else ''}")
    if n_sources > 0:
        _parts.append("ingested")
    if has_style:
        _parts.append("style learned")
    if st.session_state.venue:
        _parts.append(st.session_state.venue.replace("-", " ").upper())
    _status_line = " · ".join(_parts) if _parts else "No sources yet"
    st.markdown(
        f'<p style="font-size: 0.72rem; color: var(--text-secondary); margin: 0 0 0.35rem 0;">{_status_line}</p>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── PRIMARY ACTION ────────────────────────────────────────────────────
    if st.session_state.step == 3:
        if st.button("✦ New Session", width="stretch", key="nav_new_session", type="primary"):
            _reset_session()
            st.rerun()
    else:
        if st.button("✦ Start Writing", width="stretch", key="nav_fresh", type="primary"):
            _reset_session()
            st.rerun()

    st.markdown("---")

    # ── TOOLS ─────────────────────────────────────────────────────────────
    st.markdown('<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.5;margin:8px 0 10px 2px">Tools</p>', unsafe_allow_html=True)
    if st.button(":material/edit_note: Papers Editor", width="stretch", key="nav_papers"):
        st.session_state.page = "papers"
        st.rerun()
    if st.button(":material/folder_open: Sources Manager", width="stretch", key="nav_sources"):
        st.session_state.page = "sources"
        st.rerun()
    if st.button(":material/description: Output Manager", width="stretch", key="nav_output"):
        st.session_state.page = "output"
        st.rerun()

    st.markdown("---")

    # ── STATUS ────────────────────────────────────────────────────────────
    st.markdown('<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.5;margin:8px 0 10px 2px">Status</p>', unsafe_allow_html=True)

    # Source files (auto-expand once there's something worth showing)
    _core_ready = sources_info["Theses"] > 0 or sources_info["My Papers"] > 0
    _ws_needs_attention = _core_ready and not has_style
    with st.expander(":material/bar_chart: Sources & Knowledge", expanded=_ws_needs_attention):
        for label, count in sources_info.items():
            cls  = "stat-ready" if count > 0 else "stat-empty"
            icon = "●" if count > 0 else "○"
            st.markdown(f'<span class="stat-pill {cls}">{icon} {label}: {count}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<span class="stat-pill {"stat-ready" if n_sources > 0 else "stat-empty"}">'
            f'{"●" if n_sources > 0 else "○"} Ingested: {n_sources}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="stat-pill {"stat-ready" if has_style else "stat-empty"}">'
            f'{"●" if has_style else "○"} Style: {"Learned" if has_style else "Not yet"}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.5rem;">'
            f'{len(VENUE_PRESETS)} venues available</p>',
            unsafe_allow_html=True,
        )
        _usage = st.session_state.get("_session_usage")
        if _usage:
            _cost_txt = "local endpoint" if _custom_base_url() else f"~${_usage['cost']:.2f}"
            st.markdown(
                f'<p style="font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.3rem;">'
                f'{_usage["in"]:,} in · {_usage["out"]:,} out · {_cost_txt} this session</p>',
                unsafe_allow_html=True,
            )
            # Per-turn cost sparkline: single series in the accent hue, thin
            # bars on a hairline baseline; exact values live in the caption
            # above and in each bar's tooltip.
            _tc = st.session_state.get("_turn_costs") or []
            if len(_tc) >= 2 and max(_tc) > 0:
                _mx = max(_tc)
                _bars = "".join(
                    f'<span title="Turn {i + 1}: ${c:.2f}" style="display:inline-block;width:7px;'
                    f'height:{max(2, round(c / _mx * 22))}px;background:var(--primary);'
                    f'border-radius:1.5px 1.5px 0 0;"></span>'
                    for i, c in enumerate(_tc)
                )
                st.markdown(
                    f'<div role="img" aria-label="Cost per turn, last {len(_tc)} turns" '
                    f'style="display:flex;align-items:flex-end;gap:2px;height:24px;max-width:130px;'
                    f'margin-top:2px;padding-bottom:1px;border-bottom:1px solid var(--card-border);">{_bars}</div>',
                    unsafe_allow_html=True,
                )

    # Completed papers
    if completed:
        with st.expander(f":material/check_circle: Completed ({len(completed)})", expanded=True):
            for slug in completed:
                st.markdown(f'<span class="stat-pill stat-ready">✓ {slug}</span>', unsafe_allow_html=True)

    # Pipeline tracker (only during generation, step 3)
    if st.session_state.step == 3 and st.session_state.goal:
        with st.expander(":material/fact_check: Pipeline", expanded=True):
            _render_pipeline_tracker(st.session_state.goal, st.session_state.pipeline_phase)

    # ── RECENT SESSIONS ───────────────────────────────────────────────────
    saved_sessions = _list_sessions()
    if saved_sessions:
        st.markdown("---")
        _sess_header_col, _sess_clear_col = st.columns([3, 1])
        with _sess_header_col:
            st.markdown('<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.5;margin:0 0 4px 2px">Recent Sessions</p>', unsafe_allow_html=True)
        with _sess_clear_col:
            if _confirm_button(":material/delete:", key="clear_all_sessions", armed_label=":material/warning:", help="Clear all saved sessions (click twice to confirm)"):
                for s in saved_sessions:
                    _delete_session(s["id"])
                st.toast("All sessions cleared", icon=":material/delete:")
                st.rerun()
        for sess in saved_sessions[:5]:  # Show last 5
            goal_icon = {"write": ":material/edit_note:", "improve": ":material/draw:",
                         "review": ":material/rate_review:", "revise": ":material/refresh:",
                         "rebuttal": ":material/forum:", "coach": ":material/school:",
                         "quality": ":material/shield:", "audit": ":material/fact_check:",
                         "feedback": ":material/chat:", "lit-review": ":material/menu_book:",
                         "convert": ":material/swap_horiz:", "submit": ":material/inventory_2:",
                         "plan": ":material/checklist:", "import": ":material/upload_file:",
                         }.get(sess["goal"], ":material/description:")
            label = sess["title"][:22] or sess["goal"] or sess["id"][:18]
            msgs = sess["messages_count"]
            _load_col, _del_col = st.columns([5, 1])
            with _load_col:
                if st.button(f"{goal_icon} {label} ({msgs})", key=f"load_sess_{sess['id']}", width="stretch", help=f"Resume session: {sess.get('saved_at', '')[:16]}"):
                    _load_session(sess["id"])
                    st.session_state.page = "main"
                    st.rerun()
            with _del_col:
                if _confirm_button(":material/close:", key=f"del_sess_{sess['id']}", armed_label=":material/warning:", help="Delete this session (click twice to confirm)"):
                    _delete_session(sess["id"])
                    st.toast(f"Session deleted", icon=":material/delete:")
                    st.rerun()

    # ── HELP ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.5;margin:8px 0 10px 2px">Help</p>', unsafe_allow_html=True)
    if st.button(":material/menu_book: User Manual", width="stretch", key="nav_manual"):
        st.session_state.page = "manual"
        st.rerun()
    if st.button(":material/info: About DaVinci", width="stretch", key="nav_about"):
        st.session_state.page = "about"
        st.rerun()
    if st.button(":material/policy: Responsible AI", width="stretch", key="nav_responsible_ai"):
        st.session_state.page = "responsible-ai"
        st.rerun()
    if st.button(":material/settings: Settings", width="stretch", key="nav_settings"):
        st.session_state.page = "settings"
        st.rerun()
    st.link_button(
        ":material/volunteer_activism: Support (Optional)",
        KOFI_URL,
        key="nav_support",
        type="secondary",
        width="stretch",
        help="Optional support to help cover development, maintenance, and hosting costs.",
    )
# ===========================================================================
# MAIN CONTENT
# ===========================================================================

# ---- Output Manager Page ----
if st.session_state.page == "output":
    if st.button("← Back to Writer", key="back_from_output"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("## :material/description: Output Papers")
    st.caption("Browse, preview, and download your generated manuscripts, reports, and references.")

    papers = sorted([d for d in OUTPUT_DIR.iterdir() if d.is_dir() and d.name != "knowledge"]) if OUTPUT_DIR.exists() else []

    if not papers:
        st.markdown("""
        <div style="padding: 2rem; text-align: center; background: rgba(143, 174, 255, 0.04); border: 1px dashed rgba(143, 174, 255, 0.2); border-radius: 12px; margin-bottom: 1.25rem;">
            <p style="font-size: 1.5rem; margin: 0 0 0.5rem 0;">📄</p>
            <p style="font-size: 1rem; font-weight: 500; margin: 0 0 0.5rem 0;">No output papers yet</p>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">
                Run the writing pipeline to generate your first paper.
            </p>
        </div>
        """, unsafe_allow_html=True)
        _cta_l, _cta_c, _cta_r = st.columns([2, 1.6, 2])
        with _cta_c:
            if st.button(":material/edit_note: Start writing", key="output_empty_cta", type="primary", width="stretch"):
                st.session_state.page = "main"
                st.rerun()
    else:
        # Quick stats
        total_files = sum(len([f for f in p.iterdir() if f.is_file()]) for p in papers)
        st.markdown(f'<div style="display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap;">'
                    f'<span class="stat-pill stat-ready">● {len(papers)} paper{"s" if len(papers) != 1 else ""}</span>'
                    f'<span class="stat-pill stat-ready">● {total_files} files total</span>'
                    f'</div>', unsafe_allow_html=True)

        for paper_dir in papers:
            all_files = sorted([f for f in paper_dir.iterdir() if f.is_file()])
            total_size = sum(f.stat().st_size for f in all_files)
            size_label = f"{total_size / 1024:.0f} KB" if total_size < 1024 * 1024 else f"{total_size / (1024*1024):.1f} MB"

            with st.expander(f":material/folder_open: **{paper_dir.name}** — {len(all_files)} files ({size_label})", expanded=len(papers) == 1):
                # Categorize files
                _section_files = []
                _full_papers = []
                _reports = []
                _bib_files = []
                _other_files = []
                _report_keywords = {"compliance", "reviewer-response", "revision", "remaining-risks",
                                    "source-folder", "source-utilisation", "gap-analysis",
                                    "novelty-matrix", "reproducibility", "rebuttal",
                                    "citation-verification", "writing-quality", "quality-scorecard",
                                    "ai-disclosure", "final-audit", "revision-plan", "reviewer-response-matrix"}
                for f in all_files:
                    if f.name.startswith("full-paper"):
                        _full_papers.append(f)
                    elif f.suffix == ".bib":
                        _bib_files.append(f)
                    elif any(kw in f.name for kw in _report_keywords):
                        _reports.append(f)
                    elif f.suffix == ".md" and (
                        f.name[0:2].isdigit()
                        or f.name in (
                            "abstract.md", "introduction.md", "related-work.md",
                            "methodology.md", "experiments-or-results.md",
                            "discussion.md", "conclusion.md",
                        )
                    ):
                        _section_files.append(f)
                    else:
                        _other_files.append(f)

                # Full paper download (prominent) — numeric version sort, so
                # full-paper-v10 outranks full-paper-v2
                if _full_papers:
                    _full_papers = sorted(_full_papers, key=_paper_version_key, reverse=True)
                    _latest_fp = _full_papers[0]
                    _fp_content = _latest_fp.read_text(encoding="utf-8", errors="replace")
                    _fp_words = len(_fp_content.split())
                    st.download_button(
                        f":material/download: Download Full Paper ({_latest_fp.name} — {_fp_words:,} words)",
                        _fp_content,
                        file_name=f"{paper_dir.name}.md",
                        mime="text/markdown",
                        width="stretch",
                        key=f"out_dl_fp_{paper_dir.name}",
                        type="primary",
                    )
                    if len(_full_papers) > 1:
                        st.caption(f"Older versions: {', '.join(f.name for f in _full_papers[1:])}")

                # Sections
                if _section_files:
                    st.markdown("**:material/edit_note: Sections**")
                    for sf in _section_files:
                        _sf_size = sf.stat().st_size
                        _sf_label = f"{_sf_size // 1024} KB" if _sf_size > 1024 else f"{_sf_size} B"
                        col_name, col_size, col_view, col_dl = st.columns([4, 1, 1, 1])
                        col_name.markdown(f"`{sf.name}`")
                        col_size.caption(_sf_label)
                        if col_view.button(":material/visibility:", key=f"outv_{paper_dir.name}_{sf.name}", help="Preview"):
                            st.session_state["_out_preview_file"] = str(sf)
                            st.session_state["_out_preview_name"] = sf.name
                            st.rerun()
                        col_dl.download_button(
                            ":material/download:",
                            sf.read_text(encoding="utf-8", errors="replace"),
                            file_name=sf.name,
                            mime="text/markdown",
                            key=f"outdl_{paper_dir.name}_{sf.name}",
                        )

                # Reports
                if _reports:
                    st.markdown("**:material/bar_chart: Reports**")
                    for rf in _reports:
                        _rf_size = rf.stat().st_size
                        _rf_label = f"{_rf_size // 1024} KB" if _rf_size > 1024 else f"{_rf_size} B"
                        col_name, col_size, col_view, col_dl = st.columns([4, 1, 1, 1])
                        col_name.markdown(f"`{rf.name}`")
                        col_size.caption(_rf_label)
                        if col_view.button(":material/visibility:", key=f"outv_{paper_dir.name}_{rf.name}", help="Preview"):
                            st.session_state["_out_preview_file"] = str(rf)
                            st.session_state["_out_preview_name"] = rf.name
                            st.rerun()
                        col_dl.download_button(
                            ":material/download:",
                            rf.read_text(encoding="utf-8", errors="replace"),
                            file_name=rf.name,
                            mime="text/markdown",
                            key=f"outdl_{paper_dir.name}_{rf.name}",
                        )

                # References
                if _bib_files:
                    st.markdown("**:material/menu_book: References**")
                    for bf in _bib_files:
                        _bf_size = bf.stat().st_size
                        _entries = bf.read_text(encoding="utf-8", errors="replace").count("@")
                        col_name, col_info, col_dl = st.columns([4, 2, 1])
                        col_name.markdown(f"`{bf.name}`")
                        col_info.caption(f"~{_entries} entries")
                        col_dl.download_button(
                            ":material/download:",
                            bf.read_text(encoding="utf-8", errors="replace"),
                            file_name=bf.name,
                            mime="application/x-bibtex",
                            key=f"outdl_{paper_dir.name}_{bf.name}",
                        )

                # Other files
                if _other_files:
                    st.markdown("**:material/attach_file: Other**")
                    for of in _other_files:
                        _of_size = of.stat().st_size
                        _of_label = f"{_of_size // 1024} KB" if _of_size > 1024 else f"{_of_size} B"
                        col_name, col_size, col_view, col_dl = st.columns([4, 1, 1, 1])
                        col_name.markdown(f"`{of.name}`")
                        col_size.caption(_of_label)
                        if col_view.button(":material/visibility:", key=f"outv_{paper_dir.name}_{of.name}", help="Preview"):
                            st.session_state["_out_preview_file"] = str(of)
                            st.session_state["_out_preview_name"] = of.name
                            st.rerun()
                        col_dl.download_button(
                            ":material/download:",
                            of.read_text(encoding="utf-8", errors="replace"),
                            file_name=of.name,
                            mime="text/markdown" if of.suffix == ".md" else "text/plain",
                            key=f"outdl_{paper_dir.name}_{of.name}",
                        )

                # Edit shortcut
                if st.button(f":material/edit_note: Open in Papers Editor", key=f"out_edit_{paper_dir.name}", width="stretch"):
                    st.session_state.page = "papers"
                    st.session_state["paper_select"] = paper_dir.name
                    st.rerun()

    # Preview panel
    if st.session_state.get("_out_preview_file"):
        st.markdown("---")
        st.markdown(f"### :material/visibility: Preview: `{st.session_state['_out_preview_name']}`")
        try:
            content = Path(st.session_state["_out_preview_file"]).read_text(encoding="utf-8", errors="replace")
            st.markdown(content[:12000] + ("\n\n*… (truncated)*" if len(content) > 12000 else ""))
        except Exception as e:
            st.error(f"Cannot read file: {e}")
        if st.button("Close preview", key="close_out_preview"):
            st.session_state.pop("_out_preview_file", None)
            st.session_state.pop("_out_preview_name", None)
            st.rerun()

# ---- Sources Manager Page ----
elif st.session_state.page == "sources":
    if st.button("← Back to Writer", key="back_from_sources"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("## :material/folder_open: Source Files")
    st.caption("Your research materials. Upload files here or drop them directly into the `sources/` folder on disk.")

    # Quick status bar
    total_files = sum(_count_files(SOURCES_DIR / d) for d in ["theses", "artefacts", "papers", "my-papers", "reviewer-feedback", "my-response-letters"])
    if total_files == 0:
        st.markdown("""
        <div style="padding: 1.5rem; text-align: center; background: rgba(143, 174, 255, 0.04); border: 1px dashed rgba(143, 174, 255, 0.2); border-radius: 12px; margin-bottom: 1.5rem;">
            <p style="font-size: 1.2rem; margin: 0 0 0.5rem 0;">📂</p>
            <p style="font-size: 0.9rem; font-weight: 500; margin: 0 0 0.3rem 0;">No source files yet</p>
            <p style="font-size: 0.82rem; color: var(--text-secondary); margin: 0;">
                Upload your thesis, research papers, or artefacts below to get started.<br>
                The AI will use these as the foundation for your paper.
            </p>
        </div>
        """, unsafe_allow_html=True)

    source_folders = {
        ":material/menu_book: Theses": (SOURCES_DIR / "theses", "Your own theses — primary contribution material"),
        ":material/science: Artefacts": (SOURCES_DIR / "artefacts", "Design docs, survey data, experimental results"),
        ":material/article: Papers": (SOURCES_DIR / "papers", "Reference papers by other authors"),
        ":material/stylus_note: My Papers": (SOURCES_DIR / "my-papers", "Previously published papers for style learning"),
        ":material/chat: Reviewer Feedback": (SOURCES_DIR / "reviewer-feedback", "Real reviewer comments received after submission"),
        ":material/edit_note: My Response Letters": (SOURCES_DIR / "my-response-letters", "Previously written rebuttal/response letters (style learning)"),
    }

    for folder_label, (folder_path, folder_desc) in source_folders.items():
        folder_path.mkdir(parents=True, exist_ok=True)
        files = sorted(folder_path.iterdir())
        files = [f for f in files if f.is_file() and not f.name.startswith(".") and f.name != "README.md"]
        folder_key = folder_path.name
        with st.expander(f"{folder_label} — {len(files)} file{'s' if len(files) != 1 else ''}", expanded=len(files) > 0):
            st.caption(folder_desc)
            if not files:
                st.info("No files yet. Upload below or copy files to `" + str(folder_path.relative_to(WORKSPACE)) + "`")
            else:
                for f in files:
                    size_kb = f.stat().st_size / 1024
                    col_name, col_size, col_view, col_del = st.columns([4, 1, 1, 1])
                    col_name.markdown(f"**{f.name}**")
                    col_size.caption(f"{size_kb:.1f} KB")
                    if col_view.button("View", key=f"view_{folder_key}_{f.name}"):
                        st.session_state["_preview_file"] = str(f)
                        st.session_state["_preview_name"] = f.name
                    with col_del:
                        if _confirm_button(":material/delete:", key=f"del_{folder_key}_{f.name}", armed_label=":material/warning:", help="Delete file (click twice to confirm)"):
                            f.unlink()
                            st.toast(f"Deleted {f.name}", icon=":material/delete:")
                            st.rerun()
            # Upload widget
            uploaded = st.file_uploader(
                f"Add files to {folder_label}",
                accept_multiple_files=True,
                type=["pdf", "txt", "md", "docx", "doc", "tex"],
                key=f"upload_{folder_key}",
                label_visibility="collapsed",
            )
            if uploaded:
                # The uploader keeps its files across reruns — only save a given
                # batch once, or the save→rerun cycle repeats forever.
                batch_sig = ",".join(sorted(f"{uf.name}:{uf.size}" for uf in uploaded))
                if st.session_state.get(f"_uploaded_{folder_key}") != batch_sig:
                    saved = []
                    for uf in uploaded:
                        dest = folder_path / uf.name
                        dest.write_bytes(uf.getbuffer())
                        saved.append(uf.name)
                    st.session_state[f"_uploaded_{folder_key}"] = batch_sig
                    st.toast(f"Saved {len(saved)} file(s) to {folder_label}", icon=":material/check_circle:")
                    st.rerun()

    # File preview panel
    if st.session_state.get("_preview_file"):
        st.markdown("---")
        st.markdown(f"### :material/visibility: Preview: `{st.session_state['_preview_name']}`")
        try:
            content = Path(st.session_state["_preview_file"]).read_text(encoding="utf-8", errors="replace")
            st.text_area("File content (read-only)", value=content[:8000] + ("…" if len(content) > 8000 else ""), height=400, disabled=True, key="_file_preview_area")
        except Exception as e:
            st.error(f"Cannot read file: {e}")
        if st.button("Close preview", key="close_preview"):
            st.session_state.pop("_preview_file", None)
            st.session_state.pop("_preview_name", None)
            st.rerun()

    # Knowledge base status
    st.markdown("---")
    st.markdown("### :material/psychology: Knowledge Base")
    kb_dir = KNOWLEDGE_DIR / "sources"
    kb_files = sorted(kb_dir.iterdir()) if kb_dir.exists() else []
    kb_files = [f for f in kb_files if f.is_file() and f.suffix == ".md"]
    st.caption(f"{len(kb_files)} ingested summaries in `output/knowledge/sources/`")
    if kb_files:
        for kf in kb_files:
            col_kname, col_kview = st.columns([5, 1])
            col_kname.markdown(f":material/description: `{kf.name}`")
            if col_kview.button("View", key=f"kbview_{kf.name}"):
                st.session_state["_preview_file"] = str(kf)
                st.session_state["_preview_name"] = kf.name
                st.rerun()
    else:
        st.info("No source summaries yet. Run the pipeline to ingest sources.")

    # Style profiles
    st.markdown("**Style Profiles**")
    _profile_files = [
        (KNOWLEDGE_DIR / "style-profile.md", "Manuscript style", ":material/edit_note:"),
        (KNOWLEDGE_DIR / "response-letter-profile.md", "Response-letter style", ":material/mail:"),
    ]
    for prof_path, prof_label, prof_icon in _profile_files:
        if prof_path.exists():
            col_p, col_pv = st.columns([5, 1])
            col_p.markdown(f"{prof_icon} `{prof_path.name}` — ✓ Learned")
            if col_pv.button("View", key=f"profview_{prof_path.name}"):
                st.session_state["_preview_file"] = str(prof_path)
                st.session_state["_preview_name"] = prof_path.name
                st.rerun()
        else:
            st.markdown(f'<span class="stat-pill stat-empty">○ {prof_label}: Not yet learned</span>', unsafe_allow_html=True)

# ---- Papers Page (section editor) ----
elif st.session_state.page == "papers":
    if st.button("← Back to Writer", key="back_from_papers"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("## :material/description: Draft Papers")
    st.caption("View and edit your generated paper sections. Changes are saved to disk immediately.")

    papers = [d for d in OUTPUT_DIR.iterdir() if d.is_dir() and d.name != "knowledge"] if OUTPUT_DIR.exists() else []
    if not papers:
        st.markdown("""
        <div style="padding: 2rem; text-align: center; background: rgba(143, 174, 255, 0.04); border: 1px dashed rgba(143, 174, 255, 0.2); border-radius: 12px; margin-bottom: 1.25rem;">
            <p style="font-size: 1.5rem; margin: 0 0 0.5rem 0;">📝</p>
            <p style="font-size: 1rem; font-weight: 500; margin: 0 0 0.5rem 0;">No papers yet</p>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">
                Write a new paper from your sources, or import one you've already written.
            </p>
        </div>
        """, unsafe_allow_html=True)
        _cta_l, _cta_a, _cta_b, _cta_r = st.columns([1.4, 1.6, 1.6, 1.4])
        with _cta_a:
            if st.button(":material/edit_note: Write a paper", key="papers_empty_write", type="primary", width="stretch"):
                st.session_state.page = "main"
                st.rerun()
        with _cta_b:
            if st.button(":material/upload_file: Import paper", key="papers_empty_import", width="stretch"):
                _reset_session()
                st.session_state.page = "main"
                st.session_state.goal = "import"
                st.session_state.step = 2
                st.rerun()
    else:
        paper_names = [p.name for p in sorted(papers)]
        selected_paper = st.selectbox("Select paper", paper_names, key="paper_select")
        paper_dir = OUTPUT_DIR / selected_paper

        # List sections
        _report_names = {
            "compliance-report.md", "compliance-report-v2.md", "compliance-report-v3.md",
            "compliance-report-v4.md", "compliance-report-revised.md",
            "reviewer-response-matrix.md", "revision-change-log.md",
            "remaining-risks.md", "source-folder-assessment.md",
            "source-utilisation-audit.md", "gap-analysis.md",
            "rebuttal-draft.md",
            "novelty-matrix.md", "reproducibility-checklist.md",
        }
        section_files = sorted([
            f for f in paper_dir.iterdir()
            if f.is_file() and f.suffix == ".md" and f.name not in _report_names
        ]) if paper_dir.exists() else []
        bib_file = paper_dir / "references.bib"

        col_sections, col_editor = st.columns([1, 3])

        with col_sections:
            st.markdown("**Sections**")
            section_key = "edit_section_" + selected_paper
            if section_key not in st.session_state:
                st.session_state[section_key] = section_files[0].name if section_files else None

            for sf in section_files:
                is_active = st.session_state.get(section_key) == sf.name
                label = ("▶ " if is_active else "  ") + sf.stem.replace("-", " ").title()
                if st.button(label, key=f"sec_{selected_paper}_{sf.name}", width="stretch"):
                    st.session_state[section_key] = sf.name
                    st.rerun()

            if bib_file.exists():
                is_active = st.session_state.get(section_key) == "references.bib"
                label = ("▶ " if is_active else "  ") + "References (BibTeX)"
                if st.button(label, key=f"sec_{selected_paper}_bib", width="stretch"):
                    st.session_state[section_key] = "references.bib"
                    st.rerun()

            # Compliance reports
            compliance_files = sorted([
                f for f in paper_dir.iterdir()
                if f.is_file() and "compliance-report" in f.name
            ]) if paper_dir.exists() else []
            if compliance_files:
                st.markdown("**Compliance**")
                for cf in compliance_files:
                    is_active = st.session_state.get(section_key) == cf.name
                    label = ("▶ " if is_active else "  ") + cf.stem.replace("-", " ").title()
                    if st.button(label, key=f"rep_{selected_paper}_{cf.name}", width="stretch"):
                        st.session_state[section_key] = cf.name
                        st.rerun()

            # Revision reports
            _revision_report_names = [
                "reviewer-response-matrix.md", "revision-change-log.md",
                "remaining-risks.md", "source-folder-assessment.md",
                "source-utilisation-audit.md", "gap-analysis.md",
                "rebuttal-draft.md",
                "novelty-matrix.md", "reproducibility-checklist.md",
            ]
            revision_files = [
                paper_dir / n for n in _revision_report_names
                if (paper_dir / n).exists()
            ] if paper_dir.exists() else []
            if revision_files:
                st.markdown("**Revision Reports**")
                for rf in revision_files:
                    is_active = st.session_state.get(section_key) == rf.name
                    label = ("▶ " if is_active else "  ") + rf.stem.replace("-", " ").title()
                    if st.button(label, key=f"revr_{selected_paper}_{rf.name}", width="stretch"):
                        st.session_state[section_key] = rf.name
                        st.rerun()

        with col_editor:
            active_name = st.session_state.get(section_key)
            if active_name:
                active_file = paper_dir / active_name
                if active_file.exists():
                    file_content = active_file.read_text(encoding="utf-8", errors="replace")
                    word_count = len(file_content.split())
                    st.markdown(f"**Editing:** `{active_name}` — {word_count:,} words")
                    editor_key = f"editor_{selected_paper}_{active_name}"
                    edited = st.text_area(
                        "Section content",
                        value=file_content,
                        height=520,
                        key=editor_key,
                        label_visibility="collapsed",
                    )
                    save_col, discard_col, _ = st.columns([1, 1, 4])
                    if save_col.button(":material/save: Save", key=f"save_{active_name}", type="primary"):
                        active_file.write_text(edited, encoding="utf-8")
                        st.toast(f"Saved {active_name}", icon=":material/check_circle:")
                        st.rerun()
                    if discard_col.button(":material/undo: Discard", key=f"discard_{active_name}"):
                        # Drop the widget's retained state so the on-disk content
                        # is reloaded — a bare rerun keeps the edited text.
                        st.session_state.pop(editor_key, None)
                        st.rerun()
                else:
                    st.info(f"File `{active_name}` not found.")
            else:
                st.info("Select a section on the left to edit it.")

# ---- Settings Page ----
elif st.session_state.page == "settings":
    if st.button("← Back to Writer", key="back_from_settings"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("## :material/settings: Settings")

    # --- Status bar ---
    env_path = WORKSPACE / ".env"
    current_key = os.getenv("ANTHROPIC_API_KEY", "")
    current_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

    _MODEL_INFO = {
        "claude-sonnet-5": {
            "label": "Sonnet 5",
            "badge": "Recommended",
            "desc": "Best balance of quality, speed, and cost. Excellent for academic writing with strong reasoning.",
            "speed": "Fast",
            "quality": "High",
            "cost_input": "$3.00",
            "cost_output": "$15.00",
            "context": "1M tokens",
            "best_for": "Full paper generation, revisions, reviews — best value for most users.",
        },
        "claude-opus-5": {
            "label": "Opus 5",
            "badge": "Premium",
            "desc": "Most capable model. Superior reasoning and nuanced academic argumentation.",
            "speed": "Slower",
            "quality": "Highest",
            "cost_input": "$5.00",
            "cost_output": "$25.00",
            "context": "1M tokens",
            "best_for": "Complex papers, novel argumentation, final polishing passes.",
        },
        "claude-haiku-4-5": {
            "label": "Haiku 4.5",
            "badge": "Economy",
            "desc": "Fastest and cheapest. Good for quick drafts, summaries, and source ingestion.",
            "speed": "Fastest",
            "quality": "Good",
            "cost_input": "$1.00",
            "cost_output": "$5.00",
            "context": "200K tokens",
            "best_for": "Source ingestion, quick outlines, iterating on structure before final generation.",
        },
    }

    _model_label = _MODEL_INFO.get(current_model, {}).get("label", current_model)

    # --- Status chips: connection · model · routing · theme · session cost ---
    def _chip(text, fg, bg, dot=True):
        d = f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{fg};margin-right:6px;"></span>' if dot else ""
        return (f'<span style="display:inline-flex;align-items:center;background:{bg};color:{fg};'
                f'border-radius:999px;padding:4px 12px;font-size:0.8rem;font-weight:600;">{d}{text}</span>')

    if _custom_base_url():
        _chips = [_chip("Local endpoint", "var(--primary)", "rgba(143,174,255,0.13)")]
    elif current_key:
        _chips = [_chip("Connected", "var(--success)", "rgba(71,194,131,0.13)")]
    else:
        _chips = [_chip("Not configured", "var(--danger)", "rgba(240,126,126,0.13)")]
    _chips.append(_chip(f"Model: {html.escape(_model_label)}", "var(--text-primary)", "var(--card-bg)", dot=False))
    if os.getenv("ANTHROPIC_MODEL_FAST") and not _custom_base_url():
        _chips.append(_chip("Economy routing on", "var(--accent)", "rgba(76,196,184,0.13)", dot=False))
    _chips.append(_chip(f"Theme: {st.session_state.get('theme_mode', 'system').capitalize()}", "var(--text-secondary)", "var(--card-bg)", dot=False))
    _su = st.session_state.get("_session_usage")
    if _su:
        _cost_chip = "local — free" if _custom_base_url() else f"~${_su['cost']:.2f}"
        _chips.append(_chip(f"Session: {_cost_chip}", "var(--text-secondary)", "var(--card-bg)", dot=False))
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px;">' + "".join(_chips) + "</div>",
        unsafe_allow_html=True,
    )

    # --- Tabs ---
    _tab_conn, _tab_model, _tab_appearance = st.tabs([":material/key: Connection", ":material/tune: Models", ":material/palette: Appearance"])

    # ══════════════════════════════════════════════════════════════════════
    # TAB 1 — Connection
    # ══════════════════════════════════════════════════════════════════════
    with _tab_conn:
        _local_active = bool(_custom_base_url())

        # The first decision: where should DaVinci run?
        st.markdown("#### Where should DaVinci run?")
        _provider = st.radio(
            "Provider",
            [":material/cloud: Anthropic Cloud", ":material/computer: Local endpoint (Ollama · LM Studio · LiteLLM)"],
            index=1 if _local_active else 0,
            horizontal=True,
            label_visibility="collapsed",
        )
        _viewing_cloud = "Anthropic Cloud" in _provider
        st.markdown("")
        st.caption(
            "🔎 Transparency: with Anthropic Cloud, your source text and drafts are sent to Anthropic's API. "
            "With a local endpoint, nothing leaves your machine. See **Responsible AI** in the sidebar for the "
            "full EU AI Act notice."
        )

        if _viewing_cloud:
            # ---- Anthropic Cloud pane ----
            if _local_active:
                st.info(
                    "A **local endpoint is currently active**. Configure your key below, then "
                    "click *Switch to Anthropic Cloud* to change over.",
                    icon=":material/computer:",
                )
            elif current_key:
                masked_key = current_key[:10] + "..." + current_key[-4:] if len(current_key) > 14 else "****"
                st.success(f"Key active: `{masked_key}`")
            else:
                st.error("No API key configured yet — add one below (takes ~2 minutes).")

            # Result of the last Save & Test (stored across the rerun)
            _test_result = st.session_state.pop("_conn_test", None)
            if _test_result:
                (st.success if _test_result[0] else st.error)(_test_result[1])

            with st.expander(":material/info: How to get an Anthropic API key", expanded=not bool(current_key) and not _local_active):
                st.markdown("""
**Step 1** — Create an account at [console.anthropic.com](https://console.anthropic.com/)

**Step 2** — Go to **Settings → API Keys** ([direct link](https://console.anthropic.com/settings/keys))

**Step 3** — Click **"Create Key"**, name it (e.g., "DaVinci Writer"), and copy the key

**Step 4** — Paste it below and click **Save & Test**

> Your key starts with `sk-ant-api03-...` and is ~100 characters long.
> It is stored **locally** in `.env` — never sent anywhere except Anthropic's API.

**Billing:** Add a payment method at [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing). See the **Models** tab for price estimates.
""")

            new_key = st.text_input(
                "Anthropic API Key",
                type="password",
                placeholder="sk-ant-api03-...",
                help="Saved to `.env` in the project root. Never leaves your machine except to call Anthropic.",
            )

            _col_save, _col_test, _col_delete = st.columns([1.3, 1, 1])
            with _col_save:
                if st.button(":material/save: Save & Test", type="primary", disabled=not new_key, width="stretch"):
                    _set_env_vars({"ANTHROPIC_API_KEY": new_key})
                    st.session_state["_conn_test"] = _test_anthropic_key(new_key)
                    st.rerun()
            with _col_test:
                if st.button(":material/check_circle: Test key", disabled=not current_key, width="stretch"):
                    _ok, _msg = _test_anthropic_key(current_key)
                    (st.success if _ok else st.error)(_msg)
            with _col_delete:
                if _confirm_button(":material/delete: Remove key", key="remove_api_key",
                                   armed_label=":material/warning: Sure?", disabled=not current_key,
                                   width="stretch"):
                    _set_env_vars({"ANTHROPIC_API_KEY": None})
                    st.toast("API key removed.", icon=":material/delete:")
                    st.rerun()

            if _local_active and current_key:
                if st.button(":material/cloud: Switch to Anthropic Cloud", type="primary", width="stretch"):
                    _set_env_vars({"ANTHROPIC_BASE_URL": None, "ANTHROPIC_MODEL": _DEFAULT_MODEL})
                    st.toast("Switched to the Anthropic cloud API", icon=":material/cloud:")
                    st.rerun()

            # Ready → hand the user their next step
            if current_key and not _local_active:
                st.markdown("")
                _r1, _r2, _r3 = st.columns([2, 1.6, 2])
                with _r2:
                    if st.button("✦ Start writing", key="conn_ready_cta", width="stretch"):
                        st.session_state.page = "main"
                        st.rerun()

        else:
            # ---- Local endpoint pane ----
            st.caption(
                "Run DaVinci cost-free against a local model through any server that speaks the "
                "Anthropic Messages API — for example a LiteLLM proxy in front of Ollama. "
                "No API key required."
            )
            if _local_active:
                st.success(
                    f"Active: `{html.escape(_custom_base_url())}` · model `{html.escape(os.getenv('ANTHROPIC_MODEL', ''))}`"
                )
            with st.expander(":material/computer: How to set up Ollama + LiteLLM", expanded=not _local_active):
                st.markdown("""
1. Install [Ollama](https://ollama.com/) and pull a **tool-capable** model:
   ```
   ollama pull qwen2.5:14b
   ```
   (Also good: `llama3.1:8b` / `llama3.1:70b`, `mistral-nemo`. The model **must** support tool calling.)
2. Start a [LiteLLM](https://docs.litellm.ai/) proxy that translates Anthropic ↔ Ollama:
   ```
   pip install "litellm[proxy]"
   litellm --model ollama_chat/qwen2.5:14b --port 4000
   ```
3. Enter `http://localhost:4000` below, click **Test connection**, pick the model, and activate.

:material/warning: **Expectations:** local models are much weaker than Claude on this pipeline
(tool-calling reliability, context length, writing quality). Best for imports,
format conversion, and early drafts — switch back to the cloud for final papers.
""")
            _in_url = st.text_input(
                "Endpoint base URL",
                value=_custom_base_url(),
                placeholder="http://localhost:4000",
                key="custom_base_url_input",
            )
            if st.button(":material/search: Test connection", disabled=not _in_url.strip(), width="content"):
                _ok, _msg, _ids = _test_local_endpoint(_in_url.strip())
                (st.success if _ok else st.error)(_msg)

            # Model: picker when the endpoint told us what it serves, free text otherwise
            _served = st.session_state.get("_endpoint_models") or []
            _CUSTOM_OPT = "Other (type below)…"
            _picked = None
            if _served:
                _current_local_model = os.getenv("ANTHROPIC_MODEL", "") if _local_active else ""
                _opts = _served + [_CUSTOM_OPT]
                _picked = st.selectbox(
                    "Model served by this endpoint",
                    options=_opts,
                    index=_opts.index(_current_local_model) if _current_local_model in _served else 0,
                )
            if not _served or _picked == _CUSTOM_OPT:
                _in_model = st.text_input(
                    "Model ID at this endpoint",
                    value=os.getenv("ANTHROPIC_MODEL", "") if _local_active else "",
                    placeholder="ollama_chat/qwen2.5:14b",
                    key="custom_model_id_input",
                )
            else:
                _in_model = _picked

            _col_apply, _col_back = st.columns(2)
            with _col_apply:
                if st.button(
                    ":material/save: Use this endpoint",
                    type="primary",
                    disabled=not (_in_url.strip() and (_in_model or "").strip()),
                    width="stretch",
                ):
                    _set_env_vars({
                        "ANTHROPIC_BASE_URL": _in_url.strip(),
                        "ANTHROPIC_MODEL": _in_model.strip(),
                        "ANTHROPIC_MODEL_FAST": None,  # Claude-only feature
                    })
                    st.toast("Local endpoint active — generation now uses your local model", icon=":material/computer:")
                    st.rerun()
            with _col_back:
                if st.button(":material/cloud: Back to Anthropic cloud", disabled=not _local_active, width="stretch"):
                    _set_env_vars({"ANTHROPIC_BASE_URL": None, "ANTHROPIC_MODEL": _DEFAULT_MODEL})
                    st.toast(f"Back to the Anthropic cloud API (model reset to {_DEFAULT_MODEL})", icon=":material/cloud:")
                    st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # TAB 2 — Model & Costs
    # ══════════════════════════════════════════════════════════════════════
    with _tab_model:
        _base_url_active = _custom_base_url()

        if _base_url_active:
            st.markdown("#### Model")
            st.info(
                f"**Local endpoint active** (`{html.escape(_base_url_active)}`) — model "
                f"`{html.escape(os.getenv('ANTHROPIC_MODEL', ''))}`.\n\n"
                "The Claude model catalog and Economy routing apply to the Anthropic cloud only. "
                "Manage your local model in the **Connection** tab.",
                icon=":material/computer:",
            )
        else:
            st.markdown("#### Choose your model")
            st.caption("All three are configured and ready — pick the balance of quality and cost for this work.")

            _cloud_models = st.session_state.get("_cloud_models")
            _esc = lambda s: s.replace("$", chr(92) + "$")
            _card_keys = {m: f"modelcard_{re.sub(r'[^a-zA-Z0-9_-]', '-', m)}" for m in _MODEL_INFO}
            # Equal-height cards; highlight the selected one. Injected once, above the
            # columns, so no column gets an extra element that pushes its card down.
            _cards_css = "".join(
                f".st-key-{k} button {{ min-height: 10.5rem; }} " for k in _card_keys.values()
            )
            if current_model in _card_keys:
                _cards_css += (
                    f".st-key-{_card_keys[current_model]} button {{ border: 1.5px solid var(--primary) !important; "
                    f"box-shadow: 0 0 0 3px rgba(143,174,255,0.15) !important; }}"
                )
            st.markdown(f"<style>{_cards_css}</style>", unsafe_allow_html=True)
            _card_cols = st.columns(3)
            for (_mid, _mi), _cc in zip(_MODEL_INFO.items(), _card_cols):
                with _cc:
                    _is_sel = _mid == current_model
                    _card_key = _card_keys[_mid]
                    _sel_mark = ":material/check_circle: " if _is_sel else ""
                    _label = (
                        f"{_sel_mark}**{_mi['label']}** · {_mi['badge']}\n\n"
                        f"{_esc(_mi['cost_input'])} in · {_esc(_mi['cost_output'])} out /1M\n\n"
                        f"{_mi['speed']} speed · {_mi['quality']} quality\n\n"
                        f"{_mi['context']} context"
                    )
                    if st.button(_label, key=_card_key, width="stretch"):
                        if not _is_sel:
                            _set_env_vars({"ANTHROPIC_MODEL": _mid})
                            st.toast(f"Model changed to {_mi['label']}", icon=":material/check_circle:")
                            st.rerun()
                    if _cloud_models is not None:
                        if any(_mid in m for m in _cloud_models) or _mid in _cloud_models:
                            st.caption(":material/check_circle: available on your account")
                        else:
                            st.caption(":material/warning: not listed on your account")

            _sel_info = _MODEL_INFO.get(current_model)
            if _sel_info:
                st.caption(f":material/lightbulb: **Best for:** {_sel_info['best_for']}")
            if _cloud_models is None and current_key:
                st.caption("Tip: *Save & Test* your key in the Connection tab to check per-model availability.")

            st.markdown("---")

            # --- Economy model routing ---
            st.markdown("#### Economy Model Routing")
            _current_fast = os.getenv("ANTHROPIC_MODEL_FAST", "")
            _routing_on = st.toggle(
                "Use the Economy model (Haiku 4.5) for lightweight tasks",
                value=bool(_current_fast),
                help="Routes low-stakes goals to a cheaper, faster model. Writing, revision, and review always use the main model above.",
            )
            st.markdown(
                '<div style="display:flex;gap:6px;flex-wrap:wrap;margin:2px 0 6px 0;">'
                + "".join(
                    f'<span style="background:var(--card-bg);border:1px solid var(--card-border);color:var(--text-secondary);'
                    f'border-radius:999px;padding:2px 10px;font-size:0.75rem;">{g}</span>'
                    for g in ("paper import", "format conversion", "quality check")
                )
                + '<span style="color:var(--text-secondary);font-size:0.75rem;padding:2px 4px;">← these goals go to Haiku</span></div>',
                unsafe_allow_html=True,
            )
            _desired_fast = "claude-haiku-4-5" if _routing_on else ""
            if _desired_fast != _current_fast:
                _set_env_vars({"ANTHROPIC_MODEL_FAST": _desired_fast or None})
                st.toast("Economy routing " + ("enabled" if _desired_fast else "disabled"), icon=":material/check_circle:")

        st.markdown("---")

        # --- Token Consumption Guide ---
        with st.expander(":material/bar_chart: Token Consumption & Cost Estimates", expanded=False):
            _su2 = st.session_state.get("_session_usage")
            if _su2:
                st.markdown(
                    f"**Your current session:** {_su2['in']:,} tokens in · {_su2['out']:,} out · "
                    + ("free (local endpoint)" if _custom_base_url() else f"~\\${_su2['cost']:.2f}")
                )
                st.markdown("---")
            st.markdown(
                "Each paper generation session uses tokens for **input** (your sources + prompts) "
                "and **output** (generated text). Estimates per task:"
            )

            _cost_tab_sonnet, _cost_tab_opus, _cost_tab_haiku = st.tabs([":material/paid: Sonnet 5", ":material/diamond: Opus 5", ":material/bolt: Haiku 4.5"])

            with _cost_tab_sonnet:
                st.markdown("**$3.00 USD / 1M input** · **$15.00 USD / 1M output**")
                st.markdown("""
| Task | Input Tokens | Output Tokens | Cost (USD) |
|------|-------------|---------------|------------|
| Ingest 1 source | ~5K–15K | ~2K–4K | ~$0.05–$0.08 |
| Write full paper | ~30K–80K | ~15K–30K | ~$0.30–$0.70 |
| Improve/revise | ~40K–100K | ~10K–25K | ~$0.25–$0.50 |
| Peer review sim | ~20K–50K | ~5K–10K | ~$0.15–$0.25 |
| Full pipeline | ~100K–200K | ~40K–60K | ~$1.00–$1.50 |
""")

            with _cost_tab_opus:
                st.markdown("**$5.00 USD / 1M input** · **$25.00 USD / 1M output**")
                st.markdown("""
| Task | Input Tokens | Output Tokens | Cost (USD) |
|------|-------------|---------------|------------|
| Ingest 1 source | ~5K–15K | ~2K–4K | ~$0.08–$0.18 |
| Write full paper | ~30K–80K | ~15K–30K | ~$0.55–$1.15 |
| Improve/revise | ~40K–100K | ~10K–25K | ~$0.45–$1.15 |
| Peer review sim | ~20K–50K | ~5K–10K | ~$0.25–$0.50 |
| Full pipeline | ~100K–200K | ~40K–60K | ~$1.50–$2.50 |
""")
                st.caption(":material/warning: Opus is roughly 1.7× the cost of Sonnet. Use for final polishing or complex argumentation.")

            with _cost_tab_haiku:
                st.markdown("**$1.00 USD / 1M input** · **$5.00 USD / 1M output**")
                st.markdown("""
| Task | Input Tokens | Output Tokens | Cost (USD) |
|------|-------------|---------------|------------|
| Ingest 1 source | ~5K–15K | ~2K–4K | ~$0.02–$0.04 |
| Write full paper | ~30K–80K | ~15K–30K | ~$0.11–$0.23 |
| Improve/revise | ~40K–100K | ~10K–25K | ~$0.09–$0.23 |
| Peer review sim | ~20K–50K | ~5K–10K | ~$0.05–$0.10 |
| Full pipeline | ~100K–200K | ~40K–60K | ~$0.30–$0.50 |
""")
                st.caption(":material/lightbulb: Best value for import/convert/quality-check tasks — enable Economy Model Routing above.")

            st.info(
                "**Cost savers built in:** prompt caching serves repeated context at ~10% of the "
                "input price (watch the token-usage line in each Tool Activity log), and Economy Model Routing "
                "sends lightweight tasks to Haiku automatically. Actual session cost shows in the sidebar.",
                icon=":material/lightbulb:",
            )
            st.caption("Prices as of mid-2026. Check [anthropic.com/pricing](https://www.anthropic.com/pricing) for updates.")

    # ══════════════════════════════════════════════════════════════════════
    # TAB 3 — Appearance
    # ══════════════════════════════════════════════════════════════════════
    with _tab_appearance:
        st.markdown("#### Theme")
        _mode_options = ["system", "dark", "light"]
        _mode_labels = {"system": ":material/computer: System", "dark": ":material/dark_mode: Dark", "light": ":material/light_mode: Light"}
        _cur_mode = st.session_state.get("theme_mode", "system")
        _picked_mode = st.radio(
            "Choose appearance",
            _mode_options,
            index=_mode_options.index(_cur_mode) if _cur_mode in _mode_options else 0,
            format_func=lambda m: _mode_labels[m],
            horizontal=True,
            label_visibility="collapsed",
        )
        if _picked_mode != _cur_mode:
            st.session_state.theme_mode = _picked_mode
            st.rerun()

        st.caption(
            "**System** follows your operating system's light/dark preference; "
            "Dark and Light lock the interface to one scheme. The ☾/☀ toggle in the "
            "top bar is a quick override."
        )

elif st.session_state.page in ("manual", "about", "responsible-ai"):
    # Back button
    if st.button("← Back to Writer", key="back_from_page"):
        st.session_state.page = "main"
        st.rerun()

    if st.session_state.page == "manual":
        manual_path = WORKSPACE / "docs" / "USER-MANUAL.md"
        if manual_path.exists():
            content = manual_path.read_text(encoding="utf-8")
            images_dir = (WORKSPACE / "docs" / "images").resolve()
            for kind, value, alt in _split_manual_images(content):
                if kind == "text":
                    st.markdown(value, unsafe_allow_html=True)
                    continue
                img_path = (images_dir / value).resolve()
                if img_path.parent == images_dir and img_path.is_file():
                    st.image(str(img_path), caption=alt, width="stretch")
        else:
            st.warning("User manual not found. Expected at `docs/USER-MANUAL.md`.")

    elif st.session_state.page == "about":
        about_path = WORKSPACE / "docs" / "ABOUT.md"
        st.caption(f"Version {VERSION} · {RELEASE_DATE}")
        if about_path.exists():
            st.markdown(about_path.read_text(encoding="utf-8"), unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(
                """
                <div style="padding: 1rem 1.1rem; border-radius: 12px; border: 1px solid var(--card-border); background: var(--card-bg); margin: 0.4rem 0 0.8rem 0;">
                    <p style="margin: 0 0 0.4rem 0; font-size: 1.02rem; font-weight: 600;">Keep DaVinci Free</p>
                    <p style="margin: 0; color: var(--text-secondary); line-height: 1.55; font-size: 0.9rem;">
                        DaVinci Writer is free and will remain free. If it supports your work, optional tips help
                        RibeiroLabs cover development, maintenance, and hosting costs. No paywalls. No feature gating.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(
                ":material/volunteer_activism: Support on Ko-fi",
                KOFI_URL,
                type="secondary",
                width="content",
                help="Opens Ko-fi in a new tab.",
            )
            st.caption("Thank you for helping keep research tooling open and accessible.")
            if st.button(":material/policy: Responsible AI & EU AI Act Notice", key="about_to_responsible_ai"):
                st.session_state.page = "responsible-ai"
                st.rerun()
        else:
            st.warning("About page not found. Expected at `docs/ABOUT.md`.")

    elif st.session_state.page == "responsible-ai":
        responsible_ai_path = WORKSPACE / "docs" / "RESPONSIBLE-AI.md"
        if responsible_ai_path.exists():
            st.markdown(responsible_ai_path.read_text(encoding="utf-8"), unsafe_allow_html=True)
        else:
            st.warning("Responsible AI notice not found. Expected at `docs/RESPONSIBLE-AI.md`.")

# ---- Step 0: Landing / Choose Goal ----
elif st.session_state.step == 0:
    # Hero — text only; the logo already lives in the persistent sidebar
    st.markdown("""
    <div class="hero-container animate-in">
        <div class="hero-title">DaVinci Writer</div>
        <div class="hero-subtitle">
            Transform your research into publication-ready papers.<br>
            Powered by AI. Guided by your expertise.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _render_stepper(0)

    # ── Resume the most recent session ──
    _recent_sessions = _list_sessions()
    if (
        _recent_sessions
        and not st.session_state.get("messages")
        and not st.session_state.get("_resume_dismissed")
    ):
        _last_sess = _recent_sessions[0]
        with st.container(border=True):
            _r_text, _r_btn, _r_x = st.columns([6.5, 2.2, 0.6])
            with _r_text:
                _saved = (_last_sess.get("saved_at") or "")[:16].replace("T", " · ")
                _label = _last_sess.get("title") or _last_sess.get("goal") or _last_sess["id"]
                st.markdown(
                    f":material/refresh: **Continue where you left off**  \n"
                    f"<span style='color: var(--text-secondary); font-size: 0.85rem;'>"
                    f"{html.escape(str(_label))} — {_last_sess.get('messages_count', 0)} messages · {html.escape(_saved)}</span>",
                    unsafe_allow_html=True,
                )
            with _r_btn:
                if st.button("Resume", key="resume_last", type="primary", width="stretch"):
                    _load_session(_last_sess["id"])
                    st.session_state.page = "main"
                    st.rerun()
            with _r_x:
                if st.button(":material/close:", key="resume_dismiss", help="Dismiss"):
                    st.session_state["_resume_dismissed"] = True
                    st.rerun()

    # ── Smart onboarding: detect first-time users or recommend next step ──
    _total_src = sum(sources_info.values())
    _has_papers = bool(completed)
    _has_sources = _total_src > 0

    if not _has_sources and not _has_papers:
        # First-time user — show friendly onboarding
        st.markdown("""
        <div style="text-align: center; padding: 1rem 2rem; background: rgba(143, 174, 255, 0.06); border: 1px solid rgba(143, 174, 255, 0.15); border-radius: 16px; margin-bottom: 2rem;">
            <p style="font-size: 1rem; font-weight: 600; margin: 0 0 0.5rem 0;">Welcome! Let's get started</p>
            <p style="font-size: 0.88rem; color: var(--text-secondary); margin: 0; line-height: 1.6;">
                Start by <strong>writing a new paper</strong> from your thesis or research, or <strong>import an existing paper</strong> you want to improve.<br>
                Just pick an action below — the wizard will guide you through each step.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif _has_papers and not st.session_state.get("_dismissed_recommendation"):
        # Returning user — suggest next logical action
        _last_paper = _list_output_papers()[-1] if _list_output_papers() else ""
        _rec_col, _rec_dismiss = st.columns([9, 1])
        with _rec_col:
            st.markdown(f"""
            <div style="padding: 0.8rem 1.2rem; background: rgba(74, 222, 128, 0.06); border: 1px solid rgba(74, 222, 128, 0.18); border-radius: 12px; margin-bottom: 0.5rem;">
                <p style="font-size: 0.85rem; margin: 0; line-height: 1.5;">
                    <strong>Suggested next step:</strong> You have a draft <code>{_last_paper}</code> — consider running
                    <strong>Improve</strong>, <strong>Quality Check</strong>, or <strong>Peer Review</strong> to strengthen it.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with _rec_dismiss:
            if st.button("✕", key="dismiss_recommendation", help="Dismiss suggestion"):
                st.session_state["_dismissed_recommendation"] = True
                st.rerun()

    # ── Categorised goal selection ──
    st.markdown('<p class="section-header-center">What would you like to do?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc-center">Choose your goal — each one guides you through a focused workflow.</p>', unsafe_allow_html=True)

    # Family-colored icon chips on the goal cards: the Material icon (first <p>
    # of each card button) is rendered inside a 40px rounded chip tinted with
    # its family's soft background, with the icon itself in the family's
    # foreground color. Cards are plain st.buttons, so this is done via
    # per-key scoped CSS rather than HTML in the label.
    _all_goal_keys = [
        "write", "import", "lit-review", "plan",
        "improve", "review", "quality", "audit", "convert", "submit",
        "revise", "rebuttal", "coach", "feedback",
    ]
    _chip_rules = []
    for _gkey in _all_goal_keys:
        _fam_fg, _fam_bg = _FAMILY_COLORS[_GOAL_FAMILIES.get(_gkey, "refine")]
        _chip_rules.append(
            f'.st-key-goal_{_gkey} button [data-testid="stMarkdownContainer"] > p:first-child '
            f'{{ background: {_fam_bg}; width: 40px; height: 40px; border-radius: 10px; }}'
        )
        _chip_rules.append(
            f'.st-key-goal_{_gkey} button span[data-testid="stIconMaterial"] '
            f'{{ color: {_fam_fg}; font-size: 1.5rem; }}'
        )
    st.markdown("<style>" + "\n".join(_chip_rules) + "</style>", unsafe_allow_html=True)

    # Category: Create & Draft
    st.markdown("""
    <p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); margin: 0.2rem 0 0.6rem 0.2rem; font-weight: 600;">✦ Create & Draft</p>
    """, unsafe_allow_html=True)

    _create_goals = [
        ("write", ":material/edit_note:", "Write a Paper", "Full pipeline: sources → style → draft → review"),
        ("import", ":material/upload_file:", "Import Paper", "Bring in an existing PDF/TXT for revision"),
        ("lit-review", ":material/menu_book:", "Literature Review", "Thematic map & gap analysis from sources"),
        ("plan", ":material/checklist:", "Plan Publications", "What papers can you extract from your research?"),
    ]
    cols = st.columns(4 if len(_create_goals) == 4 else 3)
    for i, (key, icon, label, desc) in enumerate(_create_goals):
        with cols[i]:
            if st.button(f"{icon}\n\n**{label}**\n\n{desc}", key=f"goal_{key}", width="stretch"):
                st.session_state.goal = key
                if key == "plan":
                    st.session_state.step = 3
                    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                    st.session_state["_session_id"] = f"{key}-{ts}"
                elif key in ("lit-review", "import"):
                    st.session_state.step = 2
                else:
                    st.session_state.step = 1
                st.rerun()

    # Category: Improve & Review
    st.markdown("""
    <p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); margin: 1.8rem 0 0.6rem 0.2rem; font-weight: 600;">✦ Improve & Review</p>
    """, unsafe_allow_html=True)

    _improve_goals = [
        ("improve", ":material/draw:", "Improve Draft", "Expand, deepen, and polish your paper"),
        ("review", ":material/rate_review:", "Peer Review", "4 simulated reviewers find weaknesses"),
        ("quality", ":material/shield:", "Quality Check", "Citations, AI-tells, integrity scoring"),
        ("audit", ":material/fact_check:", "Final Audit", "Fresh pre-submission check"),
        ("convert", ":material/swap_horiz:", "Convert Format", "Move paper between venue formats"),
        ("submit", ":material/inventory_2:", "Prepare Submission", "Cover letter, highlights, checklists"),
    ]
    cols = st.columns(3)
    for i, (key, icon, label, desc) in enumerate(_improve_goals):
        with cols[i % 3]:
            if st.button(f"{icon}\n\n**{label}**\n\n{desc}", key=f"goal_{key}", width="stretch"):
                st.session_state.goal = key
                if key in ("quality", "convert", "audit", "submit"):
                    st.session_state.step = 2
                elif key == "improve":
                    st.session_state.step = 1
                else:
                    st.session_state.step = 1
                st.rerun()

    # Category: Respond & Revise
    st.markdown("""
    <p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); margin: 1.8rem 0 0.6rem 0.2rem; font-weight: 600;">✦ Respond to Reviewers</p>
    """, unsafe_allow_html=True)

    _respond_goals = [
        ("revise", ":material/refresh:", "Revise Paper", "Systematically address reviewer comments"),
        ("rebuttal", ":material/forum:", "Draft Rebuttal", "Point-by-point response letter"),
        ("coach", ":material/school:", "Coach Revision", "Guided walkthrough of each comment"),
        ("feedback", ":material/chat:", "Integrate Feedback", "Apply co-author or advisor notes"),
    ]
    cols = st.columns(4)
    for i, (key, icon, label, desc) in enumerate(_respond_goals):
        with cols[i]:
            if st.button(f"{icon}\n\n**{label}**\n\n{desc}", key=f"goal_{key}", width="stretch"):
                st.session_state.goal = key
                if key in ("rebuttal", "coach", "feedback"):
                    st.session_state.step = 2
                else:
                    st.session_state.step = 1
                st.rerun()


# ---- Step 1: Choose Venue ----
elif st.session_state.step == 1:
    _render_stepper(1)

    st.markdown('<p class="step-page-title">Where are you publishing?</p>', unsafe_allow_html=True)
    st.markdown('<p class="step-page-subtitle">This determines formatting rules, page limits, and citation style. Not sure yet? Pick the closest match — you can convert later.</p>', unsafe_allow_html=True)

    venue_data = {
        "ieee-access": ("IEEE Access", "Open access journal · No page limit · IF ~3.4"),
        "ieee-tse": ("IEEE TSE", "Top SE journal · 25 pages · IF ~6.5"),
        "ieee-icassp": ("IEEE ICASSP", "Signal processing · 4+1 pages"),
        "icse": ("ICSE", "Top SE conference · 10+2 pages · ~22% accept"),
        "acm-fse": ("ACM FSE", "SE foundations · 12+2 pages · ~22% accept"),
        "acm-chi": ("ACM CHI", "HCI · No hard limit · ~26% accept"),
        "neurips": ("NeurIPS", "ML/AI · 9 pages · ~26% accept"),
        "icml": ("ICML", "ML · 8 pages · ~26% accept"),
        "springer-emse": ("Springer EMSE", "Empirical SE · No limit · IF ~4.0"),
        "elsevier-jss": ("Elsevier JSS", "Systems & Software · No limit · IF ~3.5"),
        "elsevier-ist": ("Elsevier IST", "Info & Software Tech · No limit · IF ~3.8"),
        "inforum": ("INForum", "PT/EN · Springer LNCS · 12 pages · Sep 2026"),
        "refsq": ("REFSQ 2027", "RE conference · 15 pages · Double-blind · Apr 2027"),
    }

    # Category tabs for easy filtering
    tab_all, tab_journal, tab_conf = st.tabs(["All Venues", ":material/book: Journals", ":material/menu_book: Conferences"])

    journals = ["ieee-access", "ieee-tse", "springer-emse", "elsevier-jss", "elsevier-ist"]
    conferences = ["icse", "acm-fse", "acm-chi", "neurips", "icml", "ieee-icassp", "inforum", "refsq"]

    def _render_venue_grid(venue_keys, prefix):
        cols = st.columns(3)
        for i, key in enumerate(venue_keys):
            if key not in VENUE_PRESETS:
                continue
            name, desc = venue_data.get(key, (key, ""))
            with cols[i % 3]:
                selected = st.session_state.venue == key
                label = f"**{name}**" + (" ✓" if selected else "")
                if st.button(label, key=f"{prefix}_{key}", width="stretch", help=desc):
                    st.session_state.venue = key
                    st.rerun()
                st.caption(desc)

    with tab_all:
        _render_venue_grid(list(venue_data.keys()), "va")
    with tab_journal:
        _render_venue_grid(journals, "vj")
    with tab_conf:
        _render_venue_grid(conferences, "vc")

    # Custom venue option
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(":material/tune: Use a different venue", expanded=False):
        st.markdown('<p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.8rem;">Don\'t see your venue? Type its name below. For best results, also add the venue\'s author guidelines to <code>sources/venues/your-venue/requirements-summary.md</code>.</p>', unsafe_allow_html=True)
        custom = st.text_input("Venue name:", placeholder="e.g., AAAI 2026, IEEE IoT Journal")
        if custom:
            st.session_state.venue = custom.lower().replace(" ", "-")
            st.caption(f"Will use: `sources/venues/{st.session_state.venue}/requirements-summary.md`")

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Back", key="nav_back", width="stretch"):
            st.session_state.step = 0
            st.session_state.venue = None
            st.rerun()
    with col3:
        next_disabled = not st.session_state.venue
        if st.button("Next →", key="nav_next", type="primary", width="stretch", disabled=next_disabled):
            st.session_state.step = 2
            st.rerun()

    if st.session_state.venue:
        st.success(f"Selected: **{venue_data.get(st.session_state.venue, (st.session_state.venue, ''))[0]}**")
    else:
        st.markdown("""
        <div style="text-align: center; margin-top: 0.5rem;">
            <p style="font-size: 0.8rem; color: var(--text-secondary);">
                Not sure which venue? Pick the closest match — you can always convert formats later with <strong>"Convert Format"</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ---- Step 2: Paper Details ----
elif st.session_state.step == 2:
    _render_stepper(2)

    st.markdown('<p class="step-page-title">Paper details</p>', unsafe_allow_html=True)
    st.markdown('<p class="step-page-subtitle">All fields are optional — the AI will propose these from your source materials if left blank. Fill in what you know to get more focused results.</p>', unsafe_allow_html=True)

    # ---- Quality Check / Lit-Review / Convert specific inputs ----
    if st.session_state.goal == "quality":
        st.markdown('<p class="section-header">Quality Check Options</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Select which paper to check. The agent will verify citations, detect AI writing patterns, and score integrity.</p>', unsafe_allow_html=True)

        # List available paper slugs
        paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                               if d.is_dir() and d.name != "knowledge"
                               and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []
        st.session_state.paper_slug_revise = st.selectbox(
            "Paper to check",
            options=paper_folders,
            index=0 if paper_folders else None,
            key="quality_paper_slug",
            help="Select the paper folder to run quality checks on.",
        )

    elif st.session_state.goal == "lit-review":
        st.markdown('<p class="section-header">Literature Review</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Specify the topic or research question. The agent will analyze ingested sources and produce a thematic map with gap analysis.</p>', unsafe_allow_html=True)

        st.session_state.title = st.text_input(
            "Research topic or question",
            value=st.session_state.title,
            placeholder="e.g., agile methods in safety-critical software development",
        )

    elif st.session_state.goal == "convert":
        st.markdown('<p class="section-header">Format Conversion</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Select the source paper and target venue. The agent will convert citation styles, restructure sections, and recalculate page budgets.</p>', unsafe_allow_html=True)

        paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                               if d.is_dir() and d.name != "knowledge"
                               and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []
        st.session_state.paper_slug_revise = st.selectbox(
            "Paper to convert",
            options=paper_folders,
            index=0 if paper_folders else None,
            key="convert_paper_slug",
            help="Select the paper folder to convert.",
        )
        st.session_state.venue = st.selectbox(
            "Target venue",
            options=VENUE_PRESETS,
            index=0 if VENUE_PRESETS else None,
            key="convert_target_venue",
            help="The venue format to convert to.",
        )

    elif st.session_state.goal == "rebuttal":
        st.markdown('<p class="section-header">Draft Rebuttal</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Select the paper and provide reviewer comments. The agent will draft a point-by-point response letter.</p>', unsafe_allow_html=True)

        paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                               if d.is_dir() and d.name != "knowledge"
                               and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []
        st.session_state.paper_slug_revise = st.selectbox(
            "Paper slug",
            options=paper_folders,
            index=0 if paper_folders else None,
            key="rebuttal_paper_slug",
            help="Select the paper this rebuttal is for.",
        )

        st.session_state.reviewer_feedback = st.text_area(
            "Paste reviewer comments here",
            value=st.session_state.reviewer_feedback,
            placeholder="Reviewer 1:\nMajor concern 1: ...\nMinor concern 1: ...\n\nReviewer 2:\n...",
            height=280,
        )

        uploaded_feedback = st.file_uploader(
            "Or upload a reviewer feedback file (.txt, .md, .pdf)",
            accept_multiple_files=False,
            type=["txt", "md", "pdf"],
            key="up_rebuttal_feedback",
        )
        if uploaded_feedback:
            _save_reviewer_feedback_upload(uploaded_feedback)

    elif st.session_state.goal == "coach":
        st.markdown('<p class="section-header">Coach Revision</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Select the paper. The agent will walk through reviewer comments one by one, asking questions to help you decide how to address each point.</p>', unsafe_allow_html=True)

        paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                               if d.is_dir() and d.name != "knowledge"
                               and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []
        st.session_state.paper_slug_revise = st.selectbox(
            "Paper slug",
            options=paper_folders,
            index=0 if paper_folders else None,
            key="coach_paper_slug",
            help="Select the paper to coach revision for.",
        )

        st.session_state.reviewer_feedback = st.text_area(
            "Paste reviewer comments (or ensure they exist in sources/reviewer-feedback/)",
            value=st.session_state.reviewer_feedback,
            placeholder="Reviewer 1:\nMajor concern 1: ...\n\nReviewer 2:\n...",
            height=200,
        )

    elif st.session_state.goal == "audit":
        st.markdown('<p class="section-header">Final Audit</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Select the paper for a fresh-context pre-submission check. The agent will cold-read the entire manuscript and flag unresolved issues.</p>', unsafe_allow_html=True)

        paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                               if d.is_dir() and d.name != "knowledge"
                               and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []
        st.session_state.paper_slug_revise = st.selectbox(
            "Paper to audit",
            options=paper_folders,
            index=0 if paper_folders else None,
            key="audit_paper_slug",
            help="Select the paper folder for the final audit.",
        )

    elif st.session_state.goal == "feedback":
        st.markdown('<p class="section-header">Integrate Feedback</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Paste co-author or advisor feedback. The agent will triage, apply changes, and ensure consistency.</p>', unsafe_allow_html=True)

        paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                               if d.is_dir() and d.name != "knowledge"
                               and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []
        st.session_state.paper_slug_revise = st.selectbox(
            "Paper slug",
            options=paper_folders,
            index=0 if paper_folders else None,
            key="feedback_paper_slug",
            help="Select the paper to apply feedback to.",
        )

        st.session_state.reviewer_feedback = st.text_area(
            "Paste co-author/advisor comments",
            value=st.session_state.reviewer_feedback,
            placeholder="e.g., 'Section 3 needs more detail on the validation protocol'\n'The related work is missing Smith et al. 2024'\n'Tone in Discussion is too assertive'",
            height=200,
        )

    elif st.session_state.goal == "import":
        st.markdown('<p class="section-header">Import Paper</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Upload your submitted paper (PDF, TXT, or MD). The agent will split it into section files for revision workflows.</p>', unsafe_allow_html=True)

        st.session_state.paper_slug_revise = _slugify(st.text_input(
            "Paper slug (folder name for output/)",
            value=st.session_state.paper_slug_revise,
            placeholder="e.g., my-paper-ieee-access",
            help="A short kebab-case identifier for this paper.",
        ), fallback="")

        uploaded_paper = st.file_uploader(
            "Upload your paper file",
            accept_multiple_files=False,
            type=["pdf", "txt", "md"],
            key="up_import_paper",
            help="The paper you submitted and want to import for revision.",
        )
        if uploaded_paper:
            dest_dir = SOURCES_DIR / "submitted-papers"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / uploaded_paper.name
            dest.write_bytes(uploaded_paper.getvalue())
            st.toast(f"Saved to sources/submitted-papers/{uploaded_paper.name}", icon=":material/check_circle:")
            st.session_state.title = str(dest)  # Pass file path via title field

        st.info("**Tip for PDFs:** If the agent cannot extract text from your PDF, convert it first:\n```\npdftotext paper.pdf paper.txt\n```\nOr copy-paste the content into a `.txt` file.", icon=":material/lightbulb:")

    else:
        # For improve, review, and submit — need a paper selector + title/contributions
        if st.session_state.goal in ("improve", "review", "submit"):
            st.markdown('<p class="section-header">Select Paper</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-desc">Choose which paper to work on.</p>', unsafe_allow_html=True)

            paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                                   if d.is_dir() and d.name != "knowledge"
                                   and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []
            if paper_folders:
                st.session_state.paper_slug_revise = st.selectbox(
                    "Paper to work on",
                    options=paper_folders,
                    index=paper_folders.index(st.session_state.paper_slug_revise) if st.session_state.paper_slug_revise in paper_folders else 0,
                    key=f"{st.session_state.goal}_paper_slug",
                    help="Select the paper folder in output/ that contains your draft sections.",
                )
            else:
                st.warning("No papers found in output/. Write or import a paper first.")
                st.session_state.paper_slug_revise = ""

            st.markdown("<br>", unsafe_allow_html=True)

        st.session_state.title = st.text_input(
            "Working title",
            value=st.session_state.title,
            placeholder="e.g., A Digital Platform for Aerospace Compliance Documentation",
        )

        st.session_state.contributions = st.text_area(
            "Key contributions (2–4 bullet points)",
            value=st.session_state.contributions,
            placeholder="• A novel framework for...\n• An empirical evaluation showing...\n• A reusable tool that...",
            height=100,
        )

    # ---- Revise-specific inputs ----
    if st.session_state.goal == "revise":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">Original Paper</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Select an existing paper from your drafts, or upload the submitted paper (PDF, TXT, MD). The agent will import and split it automatically.</p>', unsafe_allow_html=True)

        # List existing paper folders
        paper_folders = sorted([d.name for d in OUTPUT_DIR.iterdir()
                               if d.is_dir() and d.name != "knowledge"
                               and any(f.suffix == ".md" for f in d.iterdir() if f.is_file())]) if OUTPUT_DIR.exists() else []

        # Option to select existing or upload new
        revise_paper_source = st.radio(
            "Paper source",
            options=["Select existing draft", "Upload submitted paper"],
            horizontal=True,
            key="revise_paper_source",
            label_visibility="collapsed",
        )

        if revise_paper_source == "Select existing draft":
            if paper_folders:
                st.session_state.paper_slug_revise = st.selectbox(
                    "Paper to revise",
                    options=paper_folders,
                    index=paper_folders.index(st.session_state.paper_slug_revise) if st.session_state.paper_slug_revise in paper_folders else 0,
                    key="revise_existing_slug",
                    help="Select the paper folder in output/ that contains your draft sections.",
                )
            else:
                st.warning("No existing papers found in output/. Upload your submitted paper below instead.")
                st.session_state.paper_slug_revise = _slugify(st.text_input(
                    "Paper slug",
                    value=st.session_state.paper_slug_revise,
                    placeholder="e.g., my-paper-ieee-access",
                    key="revise_new_slug_fallback",
                ), fallback="")
        else:
            st.session_state.paper_slug_revise = _slugify(st.text_input(
                "Paper slug (short name for this paper)",
                value=st.session_state.paper_slug_revise,
                placeholder="e.g., my-paper-ieee-access",
                key="revise_upload_slug",
                help="A short kebab-case identifier. The paper will be saved to output/<slug>/ and sources/submitted-papers/.",
            ), fallback="")
            uploaded_paper = st.file_uploader(
                "Upload your submitted paper (PDF, TXT, or MD)",
                accept_multiple_files=False,
                type=["pdf", "txt", "md"],
                key="up_revise_paper",
                help="The original paper you submitted for review.",
            )
            if uploaded_paper:
                # Save to sources/submitted-papers/
                dest_dir = SOURCES_DIR / "submitted-papers"
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / uploaded_paper.name
                dest.write_bytes(uploaded_paper.getvalue())
                st.toast(f"Saved paper to sources/submitted-papers/{uploaded_paper.name}", icon=":material/check_circle:")
                st.info("The agent will automatically import and split this paper into sections before revising.", icon=":material/lightbulb:")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">Reviewer Feedback</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Paste the reviewer comments below, or upload a feedback file (PDF, TXT, or MD). The agent will parse every comment and build a systematic revision plan.</p>', unsafe_allow_html=True)

        st.session_state.reviewer_feedback = st.text_area(
            "Paste reviewer comments here",
            value=st.session_state.reviewer_feedback,
            placeholder="Reviewer 1:\nMajor concern 1: ...\nMinor concern 1: ...\n\nReviewer 2:\n...",
            height=280,
        )

        # Save feedback to disk for traceability
        uploaded_feedback = st.file_uploader(
            "Or upload a reviewer feedback file (.txt, .md, .pdf)",
            accept_multiple_files=False,
            type=["txt", "md", "pdf"],
            key="up_reviewer_feedback",
        )
        if uploaded_feedback:
            _save_reviewer_feedback_upload(uploaded_feedback)

    # File upload section (not shown for goals that don't need source uploads)
    if st.session_state.goal not in ("revise", "rebuttal", "coach", "audit", "feedback", "import"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">Upload source materials</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Drag & drop your research files below. These are the raw materials the AI will use to write your paper. Already have files in <code>sources/</code>? They\'ll be detected automatically.</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            theses = st.file_uploader(
                ":material/description: Thesis or dissertation",
                accept_multiple_files=True,
                key="up_theses",
                help="Your Master's or PhD thesis — this is your primary contribution material. Supports PDF, TXT, MD.",
            )
            artefacts = st.file_uploader(
                ":material/science: Research artefacts",
                accept_multiple_files=True,
                key="up_artefacts",
                help="Design documents, survey data, architecture diagrams, experimental results, evaluation metrics.",
            )
        with col2:
            papers = st.file_uploader(
                ":material/menu_book: Reference papers",
                accept_multiple_files=True,
                key="up_papers",
                help="Papers by other authors — used for positioning your work and building the Related Work section.",
            )
            my_papers = st.file_uploader(
                ":material/stylus_note: Your published papers",
                accept_multiple_files=True,
                key="up_my_papers",
                help="Your previously published papers — the AI will learn your writing style from these (highly recommended!).",
            )
            my_letters = st.file_uploader(
                ":material/mail: Your response letters",
                accept_multiple_files=True,
                key="up_my_letters",
                help="Previously written rebuttal or response-to-reviewers letters — used to learn your response style for rebuttals.",
            )
    else:
        theses = artefacts = papers = my_papers = my_letters = []

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 3, 2])
    with col1:
        if st.button("← Back", key="nav_back2", width="stretch"):
            # Goals that skip venue selection go back to goal picker
            if st.session_state.goal in ("quality", "lit-review", "convert", "rebuttal", "coach", "audit", "feedback", "import"):
                st.session_state.step = 0
            else:
                st.session_state.step = 1
            st.rerun()
    with col3:
        start_labels = {
            "revise": "Start Revision →",
            "quality": "Run Quality Check →",
            "lit-review": "Start Review →",
            "convert": "Start Conversion →",
            "rebuttal": "Draft Rebuttal →",
            "coach": "Start Coaching →",
            "audit": "Run Audit →",
            "feedback": "Integrate Feedback →",
            "import": "Import Paper →",
        }
        start_label = start_labels.get(st.session_state.goal, "Start Writing →")

        # Disabled-with-reason: block clearly incomplete starts and say why,
        # instead of letting the pipeline fail later.
        _blockers = []
        _g = st.session_state.goal
        if _g == "import":
            if not st.session_state.paper_slug_revise:
                _blockers.append("enter a paper slug")
            if not st.session_state.title:
                _blockers.append("upload your paper file")
        elif _g in ("revise", "rebuttal", "feedback"):
            if not st.session_state.paper_slug_revise:
                _blockers.append("select or name a paper")
            if not st.session_state.reviewer_feedback:
                _blockers.append("paste or upload the feedback")
        elif _g in ("improve", "review", "submit", "quality", "audit", "coach", "convert"):
            if not st.session_state.paper_slug_revise:
                _blockers.append("select a paper to work on")
        _start_disabled = bool(_blockers)
        if _start_disabled:
            st.caption(":material/info: To continue, " + " and ".join(_blockers) + ".")
        if st.button(start_label, key="nav_next2", type="primary", width="stretch", disabled=_start_disabled):
            if theses:
                _save_uploaded(theses, SOURCES_DIR / "theses")
            if artefacts:
                _save_uploaded(artefacts, SOURCES_DIR / "artefacts")
            if papers:
                _save_uploaded(papers, SOURCES_DIR / "papers")
            if my_papers:
                _save_uploaded(my_papers, SOURCES_DIR / "my-papers")
            if my_letters:
                _save_uploaded(my_letters, SOURCES_DIR / "my-response-letters")
            # Save reviewer feedback to disk if provided inline (overwrite this
            # run's round so textarea edits win over an uploaded file). Skip the
            # PDF placeholder text — the real PDF is already on disk.
            if (
                st.session_state.goal in ("revise", "rebuttal", "coach", "feedback")
                and st.session_state.reviewer_feedback
                and not st.session_state.reviewer_feedback.startswith("[PDF uploaded:")
            ):
                slug = _slugify(st.session_state.paper_slug_revise, fallback="paper")
                fb_path = SOURCES_DIR / "reviewer-feedback" / f"{slug}-round-{_feedback_round(slug)}.md"
                fb_path.parent.mkdir(parents=True, exist_ok=True)
                fb_path.write_text(st.session_state.reviewer_feedback, encoding="utf-8")
            st.session_state.step = 3
            # Assign a session ID for auto-save
            if "_session_id" not in st.session_state:
                slug = _slugify(st.session_state.paper_slug_revise or st.session_state.goal or "")
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                st.session_state["_session_id"] = f"{slug}-{ts}"
            st.rerun()


# ---- Step 3: Generation / Chat ----
elif st.session_state.step == 3:
    _render_stepper(3)

    # Sidebar is always forced open via global CSS

    # Compact config summary bar
    goal_labels = {
        "write": "Writing Paper",
        "import": "Importing Paper",
        "improve": "Improving Draft",
        "review": "Peer Review",
        "revise": "Revising After Review",
        "rebuttal": "Drafting Rebuttal",
        "coach": "Coaching Revision",
        "audit": "Final Audit",
        "feedback": "Integrating Feedback",
        "quality": "Quality Check",
        "lit-review": "Literature Review",
        "convert": "Converting Format",
        "submit": "Submission Prep",
        "plan": "Publication Planning",
    }

    venue_display = ""
    if st.session_state.venue:
        venue_display = st.session_state.venue.replace("-", " ").title()

    config_items = [
        f"<strong>Task:</strong> {goal_labels.get(st.session_state.goal, 'Working')}",
    ]
    if venue_display:
        config_items.append(f"<strong>Venue:</strong> {html.escape(venue_display)}")
    if st.session_state.title:
        title_short = st.session_state.title[:50] + ('...' if len(st.session_state.title) > 50 else '')
        config_items.append(f"<strong>Title:</strong> {html.escape(title_short)}")
    if st.session_state.get("paper_slug_revise"):
        config_items.append(f"<strong>Paper:</strong> {html.escape(st.session_state.paper_slug_revise)}")

    config_html = " &nbsp;·&nbsp; ".join(f'<span class="config-item">{item}</span>' for item in config_items)
    _fam_color = _FAMILY_COLORS[_GOAL_FAMILIES.get(st.session_state.goal, "refine")][0]
    st.markdown(
        f'<div class="config-bar" style="border-left: 3px solid {_fam_color};">{config_html}</div>',
        unsafe_allow_html=True,
    )

    # System prompt
    system_prompt = _build_system_prompt(
        st.session_state.goal,
        st.session_state.venue,
        st.session_state.title,
        st.session_state.contributions,
    )

    # Chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=":material/smart_toy:" if msg["role"] == "assistant" else ":material/person:"):
            # unsafe_allow_html so the assistant's collapsible Tool Activity
            # <details> block renders instead of showing literal tags
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Auto-start on first visit
    if not st.session_state.messages:
        initial_msg = (
            f"Please proceed with the full pipeline. "
            f"Venue: {st.session_state.venue or 'not set'}. "
            f"Title: {st.session_state.title or 'propose one from my sources'}. "
            f"Contributions: {st.session_state.contributions or 'propose from my sources'}."
        )
        st.session_state.messages.append({"role": "user", "content": initial_msg})
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(initial_msg)

        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.caption(":material/stop: To interrupt generation, use the Stop button in the top-right toolbar.")
            activity = st.status("DaVinci Writer is working…", expanded=True)
            response = _call_claude(system_prompt, initial_msg, progress_placeholder=activity)
            _err = st.session_state.pop("_last_call_error", None)
            _calls = st.session_state.pop("_last_tool_count", 0)
            if _err:
                activity.update(label="Generation failed", state="error", expanded=False)
                st.error(f"Generation failed: {_err}\n\nYour request is kept — type 'continue' to retry.")
            else:
                activity.update(
                    label=f"Done — {_calls} tool call{'s' if _calls != 1 else ''}",
                    state="complete", expanded=False,
                )
            if response:
                st.markdown(response, unsafe_allow_html=True)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            # Update pipeline phase
            st.session_state.pipeline_phase = _detect_phase(response, st.session_state.goal)
            # Auto-save session
            _save_session(st.session_state.get("_session_id"))
            st.rerun()

    # User input
    if user_input := st.chat_input("Type 'continue' to proceed, ask a question, or give feedback..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar=":material/person:"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.caption(":material/stop: To interrupt generation, use the Stop button in the top-right toolbar.")
            activity = st.status("DaVinci Writer is working…", expanded=True)
            response = _call_claude(system_prompt, user_input, progress_placeholder=activity)
            _err = st.session_state.pop("_last_call_error", None)
            _calls = st.session_state.pop("_last_tool_count", 0)
            if _err:
                activity.update(label="Generation failed", state="error", expanded=False)
                st.error(f"Generation failed: {_err}\n\nYour message is kept — type 'continue' to retry.")
            else:
                activity.update(
                    label=f"Done — {_calls} tool call{'s' if _calls != 1 else ''}",
                    state="complete", expanded=False,
                )
            if response:
                st.markdown(response, unsafe_allow_html=True)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            # Update pipeline phase
            st.session_state.pipeline_phase = _detect_phase(response, st.session_state.goal)
            # Auto-save session
            _save_session(st.session_state.get("_session_id"))
            st.rerun()

    # Completion detection — show success banner only when output files exist
    phases = PIPELINE_PHASES.get(st.session_state.goal, [])
    if phases and st.session_state.pipeline_phase >= len(phases) - 1 and _pipeline_outputs_exist():
        st.markdown("""
        <div style="text-align: center; padding: 1.2rem 2rem; margin: 1rem 0; background: rgba(74, 222, 128, 0.08); border: 1px solid rgba(74, 222, 128, 0.25); border-radius: 16px;">
            <p style="font-size: 1.5rem; margin: 0 0 0.3rem 0;">🎉</p>
            <p style="font-size: 1rem; font-weight: 600; margin: 0 0 0.3rem 0; color: var(--success);">Pipeline Complete!</p>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">
                Your files are saved in <code>output/</code>. Use the <strong>Papers Editor</strong> in the sidebar to review and edit sections.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.get("support_hint_shown", False):
            st.markdown(
                f"""
                <div style="text-align: center; margin: -0.2rem 0 0.9rem 0; font-size: 0.84rem; color: var(--text-secondary);">
                    If this workflow helped, optional support keeps RibeiroLabs free for everyone.
                    <a href="{KOFI_URL}" target="_blank" rel="noopener noreferrer" style="margin-left: 0.25rem; color: var(--text-secondary); text-decoration: underline;">Support on Ko-fi</a>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.session_state.support_hint_shown = True

    # Quick action hints (shown when chat is idle)
    if st.session_state.messages and st.session_state.pipeline_phase < len(phases) - 1 if phases else True:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem; opacity: 0.5; font-size: 0.75rem;">
            Tip: Say <strong>"continue"</strong> to advance the pipeline, or ask questions to refine the output.
        </div>
        """, unsafe_allow_html=True)

    # Bottom action bar
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if _confirm_button(":material/refresh: Start Over", key="action_restart", width="stretch", help="Reset everything and start a new session (click twice to confirm)"):
            # Clean up saved session if it exists
            sid = st.session_state.get("_session_id")
            if sid:
                _delete_session(sid)
            _reset_session()
            st.rerun()
    with col2:
        if st.button(":material/edit_note: Edit Papers", key="action_output", width="stretch", help="Open the Papers Editor to view and edit generated sections"):
            st.session_state.page = "papers"
            st.rerun()
    with col3:
        if st.session_state.messages:
            chat_export = "\n\n---\n\n".join(
                f"**{m['role'].title()}:**\n{m['content']}"
                for m in st.session_state.messages
            )
            st.download_button(
                ":material/save: Export Chat",
                chat_export,
                key="action_export",
                file_name="davinci-session.md",
                mime="text/markdown",
                width="stretch",
                help="Download the full conversation as a Markdown file",
            )
    with col4:
        msg_count = len(st.session_state.messages)
        tool_count = sum(1 for m in st.session_state.messages if "🔧" in m.get("content", ""))
        st.markdown(
            f'<p style="text-align:center; color: var(--text-secondary); font-size: 0.75rem; padding-top: 0.6rem;">{msg_count} messages</p>',
            unsafe_allow_html=True,
        )

