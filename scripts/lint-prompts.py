"""Lint the frontmatter of the .github agent/prompt/instructions corpus.

Both runtimes silently ignore unknown frontmatter keys and invalid tool names,
so schema drift is invisible at runtime — this linter makes it a CI failure.

Usage: python scripts/lint-prompts.py   (exit 1 on any violation)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / ".github" / "agents"
PROMPTS_DIR = ROOT / ".github" / "prompts"
INSTR_DIR = ROOT / ".github" / "instructions"

VALID_TOOLS = {"read", "search", "edit", "agent", "todo"}
ALLOWED_KEYS = {
    "agent": {"name", "description", "tools", "agents", "user-invocable"},
    "prompt": {"name", "description", "tools", "agent", "argument-hint"},
    "instructions": {"description", "applyTo"},
}
REQUIRED_KEYS = {
    "agent": {"description"},
    "prompt": {"description"},
    "instructions": {"description", "applyTo"},
}


def _frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip("'\"")
    return fm


def _tool_tokens(raw: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[a-zA-Z_-]+", raw or "")]


def main() -> int:
    problems: list[str] = []
    agent_names = {f.name.removesuffix(".agent.md") for f in AGENTS_DIR.glob("*.agent.md")}

    def check(path: Path, kind: str) -> None:
        rel = path.relative_to(ROOT)
        fm = _frontmatter(path)
        if fm is None:
            problems.append(f"{rel}: missing frontmatter block")
            return
        for key in fm:
            if key not in ALLOWED_KEYS[kind]:
                problems.append(f"{rel}: unknown frontmatter key '{key}'")
        for key in REQUIRED_KEYS[kind]:
            if not fm.get(key):
                problems.append(f"{rel}: missing required key '{key}'")
        if "tools" in fm:
            for tok in _tool_tokens(fm["tools"]):
                if tok not in VALID_TOOLS:
                    problems.append(f"{rel}: unknown tool '{tok}' (valid: {sorted(VALID_TOOLS)})")
        if kind == "prompt" and fm.get("agent") and fm["agent"] not in agent_names:
            problems.append(f"{rel}: agent '{fm['agent']}' has no .github/agents/{fm['agent']}.agent.md")
        if kind == "agent" and fm.get("agents"):
            for tok in re.findall(r"[\w-]+", fm["agents"]):
                if tok not in agent_names:
                    problems.append(f"{rel}: delegation target '{tok}' has no agent file")

    for f in sorted(AGENTS_DIR.glob("*.agent.md")):
        check(f, "agent")
    for f in sorted(PROMPTS_DIR.glob("*.prompt.md")):
        check(f, "prompt")
    for f in sorted(INSTR_DIR.glob("*.instructions.md")):
        check(f, "instructions")

    if problems:
        print(f"{len(problems)} frontmatter problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    total = len(list(AGENTS_DIR.glob("*.agent.md"))) + len(list(PROMPTS_DIR.glob("*.prompt.md"))) + len(list(INSTR_DIR.glob("*.instructions.md")))
    print(f"Frontmatter OK across {total} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
