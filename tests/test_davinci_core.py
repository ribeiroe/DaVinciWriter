"""Unit tests for web/davinci_core.py — the Streamlit-free logic of the Web UI.

Covers the security boundary (workspace containment, hidden-file denial,
write confinement), slug/version helpers, model routing, prompt-cache
markers, and the sandboxed tool executor.
"""

import time

import davinci_core as core


# ---------------------------------------------------------------------------
# _safe_workspace_path — the security boundary
# ---------------------------------------------------------------------------

class TestSafeWorkspacePath:
    def test_plain_read_inside_workspace_allowed(self, ws):
        p, err = core._safe_workspace_path("sources/notes.md")
        assert err is None
        assert p == (ws / "sources" / "notes.md").resolve()

    def test_workspace_root_itself_allowed_for_read(self, ws):
        p, err = core._safe_workspace_path(".")
        assert err is None

    def test_dotenv_read_denied(self, ws):
        _, err = core._safe_workspace_path(".env")
        assert err is not None and "hidden" in err.lower()

    def test_git_dir_denied(self, ws):
        _, err = core._safe_workspace_path(".git/config")
        assert err is not None

    def test_sessions_dir_denied(self, ws):
        _, err = core._safe_workspace_path("web/.sessions/chat.json")
        assert err is not None

    def test_github_readable(self, ws):
        _, err = core._safe_workspace_path(".github/prompts/write-paper.prompt.md")
        assert err is None

    def test_github_not_writable(self, ws):
        _, err = core._safe_workspace_path(".github/prompts/x.md", for_write=True)
        assert err is not None

    def test_parent_escape_denied(self, ws):
        _, err = core._safe_workspace_path("../outside.txt")
        assert err is not None and "outside" in err.lower()

    def test_sibling_prefix_bypass_denied(self, ws):
        # A sibling dir sharing the workspace's name prefix must NOT pass
        # (the old startswith() check accepted this).
        sibling = ws.parent / (ws.name + "-evil")
        sibling.mkdir()
        _, err = core._safe_workspace_path(f"../{sibling.name}/secret.txt")
        assert err is not None

    def test_write_allowed_in_output_and_sources(self, ws):
        for rel in ("output/paper/abstract.md", "sources/theses/t.md"):
            _, err = core._safe_workspace_path(rel, for_write=True)
            assert err is None, rel

    def test_write_denied_elsewhere(self, ws):
        for rel in ("web/app.py", "README.md", "scripts/x.ps1", "."):
            _, err = core._safe_workspace_path(rel, for_write=True)
            assert err is not None, rel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_basic(self):
        assert core._slugify("My Paper: v2!") == "my-paper-v2"

    def test_windows_illegal_chars_removed(self):
        assert ":" not in core._slugify('a:b*c?"d<e>f|g')

    def test_truncated_to_60(self):
        assert len(core._slugify("x" * 200)) <= 60

    def test_fallback_on_empty(self):
        assert core._slugify("", fallback="paper") == "paper"
        assert core._slugify("!!!", fallback="") == ""


class TestPaperVersionKey:
    def test_v10_outranks_v2(self, tmp_path):
        v2 = tmp_path / "full-paper-v2.md"
        v10 = tmp_path / "full-paper-v10.md"
        v2.write_text("a")
        time.sleep(0.01)
        v10.write_text("b")
        ordered = sorted([v10, v2], key=core._paper_version_key, reverse=True)
        assert ordered[0] == v10

    def test_unversioned_sorts_below_versioned(self, tmp_path):
        plain = tmp_path / "full-paper.md"
        v3 = tmp_path / "full-paper-v3.md"
        plain.write_text("a")
        v3.write_text("b")
        ordered = sorted([plain, v3], key=core._paper_version_key, reverse=True)
        assert ordered[0] == v3


class TestModelRouting:
    def test_default_model(self):
        assert core._model_for_goal("write") == core._DEFAULT_MODEL

    def test_env_model_respected(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_MODEL", "claude-opus-5")
        assert core._model_for_goal("write") == "claude-opus-5"

    def test_fast_routing_for_light_goals_only(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5")
        monkeypatch.setenv("ANTHROPIC_MODEL_FAST", "claude-haiku-4-5")
        for goal in ("import", "convert", "quality"):
            assert core._model_for_goal(goal) == "claude-haiku-4-5", goal
        for goal in ("write", "revise", "review", None):
            assert core._model_for_goal(goal) == "claude-sonnet-5", goal

    def test_fast_routing_ignored_on_custom_endpoint(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_MODEL", "ollama_chat/qwen2.5:14b")
        monkeypatch.setenv("ANTHROPIC_MODEL_FAST", "claude-haiku-4-5")
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://localhost:4000")
        assert core._model_for_goal("import") == "ollama_chat/qwen2.5:14b"

    def test_custom_base_url_stripped(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "  http://x:1  ")
        assert core._custom_base_url() == "http://x:1"
        monkeypatch.delenv("ANTHROPIC_BASE_URL")
        assert core._custom_base_url() == ""


# ---------------------------------------------------------------------------
# Prompt-cache markers
# ---------------------------------------------------------------------------

class _FakeBlock:
    """Stands in for an SDK content-block object (not a dict)."""
    type = "text"


class TestCacheMarkers:
    def test_string_content_converted_and_marked(self):
        msgs = [{"role": "user", "content": "hello"}]
        core._mark_cache_breakpoint(msgs)
        block = msgs[-1]["content"][-1]
        assert block["cache_control"] == {"type": "ephemeral"}
        assert block["text"] == "hello"

    def test_dict_list_content_marks_last_block(self):
        msgs = [{"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "a", "content": "r1"},
            {"type": "tool_result", "tool_use_id": "b", "content": "r2"},
        ]}]
        core._mark_cache_breakpoint(msgs)
        assert "cache_control" in msgs[-1]["content"][-1]
        assert "cache_control" not in msgs[-1]["content"][0]

    def test_sdk_object_content_skipped(self):
        msgs = [{"role": "assistant", "content": [_FakeBlock()]}]
        core._mark_cache_breakpoint(msgs)  # must not raise or mutate

    def test_strip_then_mark_leaves_exactly_one_marker(self):
        msgs = [
            {"role": "user", "content": [{"type": "text", "text": "a", "cache_control": {"type": "ephemeral"}}]},
            {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "x", "content": "r",
                                          "cache_control": {"type": "ephemeral"}}]},
        ]
        core._strip_cache_markers(msgs)
        core._mark_cache_breakpoint(msgs)
        markers = sum(
            1
            for m in msgs
            for b in (m["content"] if isinstance(m["content"], list) else [])
            if isinstance(b, dict) and "cache_control" in b
        )
        assert markers == 1

    def test_empty_messages_no_crash(self):
        core._mark_cache_breakpoint([])
        core._strip_cache_markers([])


# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

def test_tool_schema_sanity():
    names = [t["name"] for t in core._CLAUDE_TOOLS]
    assert len(names) == len(set(names)), "duplicate tool names"
    for t in core._CLAUDE_TOOLS:
        assert t["description"]
        assert t["input_schema"]["type"] == "object"


# ---------------------------------------------------------------------------
# _execute_tool — the sandboxed executor
# ---------------------------------------------------------------------------

class TestReadFile:
    def test_reads_content(self, ws):
        (ws / "sources" / "a.md").write_text("hello world", encoding="utf-8")
        assert core._execute_tool("read_file", {"path": "sources/a.md"}) == "hello world"

    def test_missing_file(self, ws):
        assert "not found" in core._execute_tool("read_file", {"path": "sources/nope.md"}).lower()

    def test_dotenv_blocked(self, ws):
        (ws / ".env").write_text("ANTHROPIC_API_KEY=sk-secret", encoding="utf-8")
        out = core._execute_tool("read_file", {"path": ".env"})
        assert "sk-secret" not in out
        assert "Error" in out

    def test_chunking_with_offset(self, ws):
        big = "x" * 70000
        (ws / "sources" / "big.md").write_text(big, encoding="utf-8")
        first = core._execute_tool("read_file", {"path": "sources/big.md"})
        assert "offset=30000" in first
        second = core._execute_tool("read_file", {"path": "sources/big.md", "offset": 30000})
        assert "continuing from char 30000" in second
        assert "offset=60000" in second
        third = core._execute_tool("read_file", {"path": "sources/big.md", "offset": 60000})
        assert "offset=" not in third  # final chunk carries no continuation notice


class TestWriteFile:
    def test_write_creates_parents(self, ws):
        msg = core._execute_tool("write_file", {"path": "output/p/abstract.md", "content": "text"})
        assert "Successfully wrote" in msg
        assert (ws / "output" / "p" / "abstract.md").read_text(encoding="utf-8") == "text"

    def test_write_outside_allowed_roots_denied(self, ws):
        (ws / "web").mkdir()
        msg = core._execute_tool("write_file", {"path": "web/app.py", "content": "evil"})
        assert "Error" in msg
        assert not (ws / "web" / "app.py").exists()

    def test_overwrite_creates_backup(self, ws):
        core._execute_tool("write_file", {"path": "output/p/s.md", "content": "v1"})
        msg = core._execute_tool("write_file", {"path": "output/p/s.md", "content": "v2"})
        assert "backed up" in msg
        backups = list((ws / "output" / ".backups").rglob("*-p-s.md"))
        assert len(backups) == 1
        assert backups[0].read_text(encoding="utf-8") == "v1"
        assert (ws / "output" / "p" / "s.md").read_text(encoding="utf-8") == "v2"

    def test_old_backups_pruned(self, ws):
        stale = ws / "output" / ".backups" / "20200101"
        stale.mkdir(parents=True)
        (stale / "old.md").write_text("ancient", encoding="utf-8")
        core._execute_tool("write_file", {"path": "output/p/s.md", "content": "v1"})
        core._execute_tool("write_file", {"path": "output/p/s.md", "content": "v2"})  # triggers prune
        assert not stale.exists()


class TestListSearch:
    def test_list_directory_hides_dotfiles(self, ws):
        (ws / "sources" / ".gitkeep").write_text("", encoding="utf-8")
        (ws / "sources" / "real.md").write_text("x", encoding="utf-8")
        (ws / "sources" / "sub").mkdir()
        out = core._execute_tool("list_directory", {"path": "sources"})
        assert "real.md" in out and "sub/" in out and ".gitkeep" not in out

    def test_search_files_excludes_hidden(self, ws):
        (ws / "sources" / "a.md").write_text("x", encoding="utf-8")
        hidden = ws / ".secrets"
        hidden.mkdir()
        (hidden / "b.md").write_text("x", encoding="utf-8")
        out = core._execute_tool("search_files", {"pattern": "**/*.md"})
        assert "a.md" in out and ".secrets" not in out

    def test_search_text_finds_line(self, ws):
        (ws / "sources" / "notes.md").write_text("alpha\nneedle here\nomega", encoding="utf-8")
        out = core._execute_tool("search_text", {"query": "NEEDLE"})
        assert "notes.md:2" in out

    def test_search_text_skips_hidden_dirs(self, ws):
        sessions = ws / "web" / ".sessions"
        sessions.mkdir(parents=True)
        (sessions / "chat.json").write_text("needle secret", encoding="utf-8")
        out = core._execute_tool("search_text", {"query": "needle"})
        assert "chat.json" not in out


class TestMisc:
    def test_unknown_tool(self, ws):
        assert "Unknown tool" in core._execute_tool("frobnicate", {})

    def test_verify_reference_requires_input(self, ws):
        out = core._execute_tool("verify_reference", {})
        assert "Error" in out and "query" in out

    def test_executor_never_raises(self, ws):
        # Even malformed input must come back as an error string, not an exception
        out = core._execute_tool("read_file", {})
        assert isinstance(out, str) and "Error" in out


# ---------------------------------------------------------------------------
# _split_manual_images — in-app manual screenshot rendering
# ---------------------------------------------------------------------------

class TestSplitManualImages:
    def test_text_and_images_in_order(self):
        md = "Intro\n\n![Step 1](images/a.png)\n\nMiddle\n![Step 2](images/b.png)\nEnd\n"
        assert core._split_manual_images(md) == [
            ("text", "Intro\n\n", ""),
            ("image", "a.png", "Step 1"),
            ("text", "\n\nMiddle\n", ""),
            ("image", "b.png", "Step 2"),
            ("text", "\nEnd\n", ""),
        ]

    def test_no_images_is_single_text_segment(self):
        assert core._split_manual_images("# Title\n\nBody") == [("text", "# Title\n\nBody", "")]

    def test_external_and_inline_images_left_as_text(self):
        md = "![x](https://example.com/a.png)\ntext ![y](images/c.png) more"
        segs = core._split_manual_images(md)
        assert [s[0] for s in segs] == ["text"]

    def test_empty_input(self):
        assert core._split_manual_images("") == []
