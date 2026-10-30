"""
Core (Streamlit-free) logic for the DaVinci Web UI: workspace paths, the
model catalog and per-goal routing, filename/slug helpers, the Claude tool
schemas, the sandboxed tool executor, and prompt-cache marker helpers.

Deliberately imports no streamlit so it can be unit-tested directly.
"""

import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
SOURCES_DIR = WORKSPACE / "sources"
OUTPUT_DIR = WORKSPACE / "output"
KNOWLEDGE_DIR = OUTPUT_DIR / "knowledge"
VENUES_DIR = SOURCES_DIR / "venues"


_DEFAULT_MODEL = "claude-sonnet-5"
# USD per 1M tokens (input, output) — used for the session cost estimate
_MODEL_PRICES = {
    "claude-sonnet-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
    # Prompts over 100K tokens cost $0.50 / $2.50 on Haiku 5.5
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-fable-5-1": (10.00, 50.00),
}
# Lightweight goals routed to ANTHROPIC_MODEL_FAST when configured in Settings
_FAST_MODEL_GOALS = {"import", "convert", "quality"}


def _custom_base_url() -> str:
    """Custom Anthropic-format endpoint (e.g. a LiteLLM proxy in front of a
    local Ollama model). Empty string means the Anthropic cloud API."""
    return os.getenv("ANTHROPIC_BASE_URL", "").strip()


def _model_for_goal(goal: str | None) -> str:
    """Pick the model for this turn: the economy model for lightweight goals
    (when enabled in Settings), the main model for everything else.

    Economy routing is ignored on a custom endpoint — the fast-model ID is a
    Claude ID that a local server wouldn't recognize.
    """
    fast = os.getenv("ANTHROPIC_MODEL_FAST", "").strip()
    if fast and goal in _FAST_MODEL_GOALS and not _custom_base_url():
        return fast
    return os.getenv("ANTHROPIC_MODEL", _DEFAULT_MODEL)


def _slugify(text: str, fallback: str = "session") -> str:
    """Reduce free text to a filesystem-safe slug: lowercase, [a-z0-9-] only."""
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug[:60] or fallback


def _paper_version_key(f: Path):
    """Sort key for full-paper-vN files: numeric version, then mtime."""
    m = re.search(r"-v(\d+)$", f.stem)
    return (int(m.group(1)) if m else 0, f.stat().st_mtime)


_MANUAL_IMAGE_LINE = re.compile(r"^!\[([^\]]*)\]\(images/([^)\s]+)\)[ \t]*$", re.MULTILINE)


def _split_manual_images(markdown: str) -> list[tuple[str, str, str]]:
    """Split manual markdown into ('text', chunk, '') and ('image', filename, alt)
    segments so each docs/images/ screenshot can be rendered with st.image
    (st.markdown can't load local files). Only bare `images/<name>` lines are
    treated as images; other markdown is passed through untouched."""
    segments: list[tuple[str, str, str]] = []
    pos = 0
    for m in _MANUAL_IMAGE_LINE.finditer(markdown):
        chunk = markdown[pos:m.start()]
        if chunk.strip():
            segments.append(("text", chunk, ""))
        segments.append(("image", m.group(2), m.group(1)))
        pos = m.end()
    tail = markdown[pos:]
    if tail.strip():
        segments.append(("text", tail, ""))
    return segments


_CLAUDE_TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file in the workspace. Use relative paths from workspace root. Files longer than 30000 characters are returned in chunks — pass 'offset' to read the next chunk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from workspace root (e.g., 'output/my-paper/introduction.md' or 'sources/reviewer-feedback/paper-round-1.md')",
                },
                "offset": {
                    "type": "integer",
                    "description": "Character offset to start reading from (default 0). Use the offset suggested in a truncation notice to continue reading a large file.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates parent directories if needed. Use relative paths from workspace root.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from workspace root (e.g., 'output/my-paper/abstract.md')",
                },
                "content": {
                    "type": "string",
                    "description": "The full content to write to the file.",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and subdirectories in a directory. Returns names with '/' suffix for directories.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from workspace root (e.g., 'output/' or 'sources/reviewer-feedback/'). Use '' or '.' for root.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_files",
        "description": "Search for files matching a glob pattern in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern (e.g., 'output/my-paper/*.md' or 'sources/**/*.txt')",
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "search_text",
        "description": "Search for text content within files. Returns matching lines with file paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for (case-insensitive substring match).",
                },
                "path": {
                    "type": "string",
                    "description": "Directory or file to search within (relative path). Defaults to entire workspace.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_pdf",
        "description": "Extract text from a PDF file using pdfplumber. Returns the full text content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the PDF file.",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "verify_reference",
        "description": (
            "Verify a bibliographic reference against the Crossref database of published works "
            "(requires internet). Returns the closest published records so you can confirm the "
            "citation exists and its metadata (title, authors, year, venue, DOI) matches. "
            "Use during citation verification; if the lookup fails (offline), fall back to "
            "source-traceability checks only."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Bibliographic query: title plus first author and year, e.g. 'Attention is all you need Vaswani 2017'.",
                },
                "doi": {
                    "type": "string",
                    "description": "DOI to look up directly (preferred when the reference includes one).",
                },
            },
        },
    },
]


_WORKSPACE_RESOLVED = WORKSPACE.resolve()
# Model-issued writes are confined to the paper workspace folders.
_WRITE_ALLOWED_ROOTS = ("output", "sources")


def _safe_workspace_path(rel_path: str, for_write: bool = False):
    """Resolve a model-supplied path strictly inside the workspace.

    Returns (Path, None) on success or (None, error_message) on refusal.
    Hidden files and directories (.env, .git, web/.sessions, ...) are
    off-limits; .github is allowed read-only. Writes are confined to
    output/ and sources/ so the model cannot alter app code or prompts.
    """
    try:
        p = (WORKSPACE / rel_path).resolve()
    except (OSError, ValueError):
        return None, f"Error: Invalid path: {rel_path}"
    if p != _WORKSPACE_RESOLVED and _WORKSPACE_RESOLVED not in p.parents:
        return None, "Error: Path is outside the workspace."
    rel_parts = p.relative_to(_WORKSPACE_RESOLVED).parts
    for part in rel_parts:
        if part.startswith(".") and not (part == ".github" and not for_write):
            return None, f"Error: Access to hidden files/directories is not allowed: {rel_path}"
    if for_write and (not rel_parts or rel_parts[0] not in _WRITE_ALLOWED_ROOTS):
        return None, "Error: Writes are only allowed inside output/ and sources/."
    return p, None


def _is_hidden_in_workspace(p: Path) -> bool:
    """True if any path component under the workspace is a dotfile (except .github)."""
    try:
        rel_parts = p.resolve().relative_to(_WORKSPACE_RESOLVED).parts
    except (OSError, ValueError):
        return True
    return any(part.startswith(".") and part != ".github" for part in rel_parts)


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        if tool_name == "read_file":
            file_path, err = _safe_workspace_path(tool_input["path"])
            if err:
                return err
            if not file_path.exists():
                return f"Error: File not found: {tool_input['path']}"
            if not file_path.is_file():
                return f"Error: Path is not a file: {tool_input['path']}"
            content = file_path.read_text(encoding="utf-8", errors="replace")
            # Serve large files in 30K-char chunks to avoid overwhelming context
            total_len = len(content)
            offset = max(0, int(tool_input.get("offset") or 0))
            chunk = content[offset:offset + 30000]
            if offset > 0:
                chunk = f"[... continuing from char {offset} of {total_len} ...]\n" + chunk
            if offset + 30000 < total_len:
                chunk += f"\n\n[... truncated at char {offset + 30000} of {total_len}. Call read_file again with offset={offset + 30000} to continue. ...]"
            return chunk

        elif tool_name == "write_file":
            file_path, err = _safe_workspace_path(tool_input["path"], for_write=True)
            if err:
                return err
            backed_up = ""
            if file_path.exists() and file_path.is_file():
                # Keep a copy before overwriting so hand edits are recoverable.
                backup_root = OUTPUT_DIR / ".backups"
                day_dir = backup_root / datetime.now().strftime("%Y%m%d")
                day_dir.mkdir(parents=True, exist_ok=True)
                backup_name = f"{datetime.now().strftime('%H%M%S')}-{file_path.parent.name}-{file_path.name}"
                shutil.copy2(file_path, day_dir / backup_name)
                backed_up = " (previous version backed up to output/.backups/)"
                # Prune day-folders older than 7 days (names sort lexicographically)
                cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
                for d in backup_root.iterdir():
                    if d.is_dir() and d.name < cutoff:
                        shutil.rmtree(d, ignore_errors=True)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(tool_input["content"], encoding="utf-8")
            return f"Successfully wrote {len(tool_input['content'])} characters to {tool_input['path']}{backed_up}"

        elif tool_name == "list_directory":
            dir_path, err = _safe_workspace_path(tool_input["path"] or ".")
            if err:
                return err
            if not dir_path.exists():
                return f"Error: Directory not found: {tool_input['path']}"
            if not dir_path.is_dir():
                return f"Error: Path is not a directory: {tool_input['path']}"
            entries = []
            for item in sorted(dir_path.iterdir()):
                if item.name.startswith("."):
                    continue
                if item.is_dir():
                    entries.append(f"{item.name}/")
                else:
                    entries.append(item.name)
            return "\n".join(entries) if entries else "(empty directory)"

        elif tool_name == "search_files":
            import glob
            pattern = tool_input["pattern"]
            matches = sorted(glob.glob(str(WORKSPACE / pattern), recursive=True))
            # Filter to workspace only, excluding hidden files/dirs
            results = []
            for m in matches:
                mp = Path(m)
                if mp.is_file() and not _is_hidden_in_workspace(mp):
                    results.append(str(mp.resolve().relative_to(_WORKSPACE_RESOLVED)))
                if len(results) >= 50:
                    break
            return "\n".join(results) if results else "No files found matching pattern."

        elif tool_name == "search_text":
            query = tool_input["query"].lower()
            search_path, err = _safe_workspace_path(tool_input.get("path", "."))
            if err:
                return err
            results = []
            search_extensions = {".md", ".txt", ".bib", ".py", ".json"}
            if search_path.is_file():
                files_to_search = [search_path]
            else:
                files_to_search = [
                    f for f in search_path.rglob("*")
                    if f.is_file() and f.suffix in search_extensions and not _is_hidden_in_workspace(f)
                ]
            for fp in files_to_search[:100]:
                try:
                    content = fp.read_text(encoding="utf-8", errors="replace")
                    for i, line in enumerate(content.split("\n"), 1):
                        if query in line.lower():
                            rel = str(fp.relative_to(WORKSPACE))
                            results.append(f"{rel}:{i}: {line.strip()[:120]}")
                            if len(results) >= 30:
                                break
                except (OSError, UnicodeDecodeError):
                    continue
                if len(results) >= 30:
                    break
            return "\n".join(results) if results else "No matches found."

        elif tool_name == "read_pdf":
            file_path, err = _safe_workspace_path(tool_input["path"])
            if err:
                return err
            if not file_path.exists():
                return f"Error: File not found: {tool_input['path']}"
            try:
                import pdfplumber
                text_parts = []
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                content = "\n\n".join(text_parts)
                total_len = len(content)
                if total_len > 30000:
                    content = content[:30000] + f"\n\n[... PDF truncated at 30KB ({total_len} total chars). The full text was extracted but trimmed to fit context. ...]"
                return content if content else "Error: No text could be extracted from this PDF."
            except ImportError:
                return "Error: pdfplumber not installed. Run: pip install pdfplumber"
            except Exception as e:
                return f"Error reading PDF: {e}"

        elif tool_name == "verify_reference":
            import requests
            from urllib.parse import quote
            headers = {"User-Agent": "DaVinci-Writer (academic paper assistant; citation verification)"}
            try:
                if tool_input.get("doi"):
                    doi = tool_input["doi"].strip().removeprefix("https://doi.org/").removeprefix("doi.org/")
                    r = requests.get(f"https://api.crossref.org/works/{quote(doi)}", headers=headers, timeout=10)
                    if r.status_code == 404:
                        return f"NOT FOUND: DOI '{doi}' does not exist in Crossref. The DOI is wrong or the reference may be fabricated."
                    r.raise_for_status()
                    items = [r.json()["message"]]
                else:
                    query = (tool_input.get("query") or "").strip()
                    if not query:
                        return "Error: provide 'query' (title + author + year) or 'doi'."
                    r = requests.get(
                        "https://api.crossref.org/works",
                        params={"query.bibliographic": query, "rows": 3},
                        headers=headers,
                        timeout=10,
                    )
                    r.raise_for_status()
                    items = r.json()["message"]["items"]
                if not items:
                    return "NO MATCHES: Crossref returned no records. The reference may be fabricated, misspelled, or too recent to be indexed."
                lines = []
                for it in items:
                    title = (it.get("title") or ["(no title)"])[0]
                    authors = ", ".join(a.get("family", "") for a in (it.get("author") or [])[:4]) or "(no authors listed)"
                    year = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
                    venue = (it.get("container-title") or [""])[0]
                    lines.append(f"- {title} — {authors} ({year}) · {venue} · DOI: {it.get('DOI', 'n/a')}")
                return (
                    "Closest Crossref records:\n" + "\n".join(lines)
                    + "\n\nCompare title, authors, year, and venue against the reference under verification."
                )
            except Exception as e:
                return f"Error: Crossref lookup failed ({e}). Network may be unavailable — fall back to source-traceability verification only."

        else:
            return f"Error: Unknown tool '{tool_name}'"

    except Exception as e:
        return f"Error executing {tool_name}: {e}"


def _strip_cache_markers(messages: list) -> None:
    """Remove cache_control from all dict content blocks (max 4 allowed per request)."""
    for m in messages:
        content = m.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    block.pop("cache_control", None)


def _mark_cache_breakpoint(messages: list) -> None:
    """Put a cache breakpoint on the last cacheable block of the newest message.

    Prompt caching is a prefix match: marking the newest message lets each loop
    iteration (and each chat turn) reuse everything sent before it at ~10% of
    the input price. Assistant messages holding SDK block objects are skipped —
    the tool_result message that follows them carries the marker instead.
    """
    if not messages:
        return
    last = messages[-1]
    content = last.get("content")
    if isinstance(content, str):
        last["content"] = [{"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}]
    elif isinstance(content, list) and content and isinstance(content[-1], dict):
        content[-1]["cache_control"] = {"type": "ephemeral"}
