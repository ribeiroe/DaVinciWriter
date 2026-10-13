---
description: "Verify all citations in a paper draft are real, traceable to ingested sources, and correctly attributed. Flags fabricated references, metadata mismatches, and citation freshness issues."
name: "Verify Citations"
agent: academic-writer
argument-hint: "Paper slug to verify (e.g. 'certia360-ieee-access')"
tools: [read, search, edit, agent, todo]
---

You are running a citation integrity verification on an existing paper draft. Your job is to delegate to the `citation-verifier` agent and present the results.

Read these instructions completely before taking any action.

---

## Phase 1 — Identify the Draft

Determine the paper slug from the user's input. Confirm that `output/<paper-slug>/` exists and contains:
- Section `.md` files
- `references.bib`

Also confirm that `output/knowledge/sources/` contains at least one ingested source summary.

If sources haven't been ingested, warn the user that verification will be limited.

---

## Phase 2 — Run Verification

Delegate to `citation-verifier`:

> "Verify all citations in `output/<paper-slug>/` against the source summaries in `output/knowledge/sources/`. Check for fabricated references, metadata inconsistencies, orphan citations, and citation freshness. If a `verify_reference` tool is available in this runtime, use it to look up every `[UNVERIFIABLE]` entry online (by DOI or bibliographic query) and reclassify it as `VERIFIED (external)` or `[LIKELY FABRICATED]` based on the result. Save the report to `output/<paper-slug>/citation-verification-report.md`."

If the `verify_reference` tool is not available, the verifier should note in its report that online verification was skipped.

---

## Phase 3 — Present Results

Summarize for the user:

1. **Verification status** — PASS / FAIL
2. **Fabricated references** — list any with `[FABRICATED]` or `[UNVERIFIABLE]` flags (CRITICAL)
3. **Metadata issues** — any year/title/author mismatches
4. **Citation freshness** — whether the literature is current enough
5. **Self-citation rate** — and whether it's within acceptable bounds
6. **Recommended actions** — prioritized list of what to fix

If any references are flagged as fabricated, emphasize this is a **critical issue** that must be resolved before submission.

---

## Phase 4 — Offer Fixes

If issues are found, offer to:
1. Remove fabricated entries from `references.bib`
2. Correct metadata mismatches
3. Remove orphan citations from the text
4. Suggest replacement references from ingested sources for removed entries
