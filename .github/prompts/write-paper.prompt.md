---
description: "Full end-to-end automation of every phase of a scientific paper — from source ingestion and style learning through drafting, compliance checking, and revision. A single command that drives the entire DaVinci workflow without requiring the user to invoke individual prompts."
name: "Write Paper"
agent: academic-writer
argument-hint: "Describe the paper: title or topic, key contributions, and target venue (e.g. 'a paper on transformer-based speech enhancement for IEEE ICASSP 2026'). Optionally add: sources ready, style learning enabled/disabled."
tools: [read, search, edit, agent, todo]
---

You are running the full DaVinci paper-writing pipeline from start to finish, automating every phase with minimal interruptions to the user.

## Execution Contract

The complete phase workflow (0–11) is defined in your academic-writer agent instructions — execute it end to end with the following automation overrides. Do not re-derive or improvise phases: the agent instructions are the single source of truth for what each phase does, its delegation messages, its artifacts, and its integrity rules.

## Automation Overrides

- **Run continuously.** Do not pause between phases. The only user pauses are the four listed in the Interruption Policy below (plus hard error escalations such as missing prerequisites or a failing subagent).
- **Phase 1 requirements** — ask all Phase 1 questions (venue, topic/contributions, sources, style learning, custom section names, abstract timing, ZIP files to import) as a single grouped message, not one question at a time. If the user's initial message already answers an item, do not ask again. Only the venue is strictly required upfront. After the answers, build the todo list below and confirm the plan before proceeding.
- **Phases 2b–4e accumulate silently** into the single Paper Plan approval checkpoint after Phase 4e — do not pause at 2b (proposal), 3 (style summary), 4 (brief), 4c (novelty), or 4d (framing) individually.
- **Phase 5e and 5f run automatically** — each has a cap of 2 automated fix/rewrite cycles; pause only if 5f is still FAIL (or 5e still HIGH/CRITICAL) after 2 cycles, presenting the remaining flags.
- **Phase 6 citation verification runs automatically** — no user input required.
- **Phase 7 warnings** — fix automatically when possible without restructuring; roll unresolved warnings into the final delivery summary instead of pausing. Escalate only if the 5-iteration hard cap is reached with critical issues remaining.
- **Phase 11 runs automatically** after the final delivery summary — no user input required.

## Todo List

Create these todos at start (all `pending`) and update status in real time — one todo `in_progress` at a time:

```
[ ] Phase 0  — Load session learnings
[ ] Phase 0b — Load portfolio context
[ ] Phase 1  — Understand the task (venue + preferences confirmation)
[ ] Phase 2  — Ingest sources
[ ] Phase 2b — Propose title, contributions, and structure
[ ] Phase 3  — Learn writing style
[ ] Phase 4  — Venue setup, page budget, workspace, and source-to-section map (4a)
[ ] Phase 4b — RQ-validation traceability matrix
[ ] Phase 4c — Novelty validation
[ ] Phase 4d — Contribution framing workshop
[ ] Phase 4e — Methodology stress-test → Paper Plan approval checkpoint
[ ] Phase 5  — Draft all sections + coherence pass
[ ] Phase 5b — "So What?" significance test
[ ] Phase 5d — Figure and table planning
[ ] Phase 5e — Self-plagiarism check
[ ] Phase 5f — Integrity gate
[ ] Phase 6  — Compliance check + citation verification
[ ] Phase 7  — Revise (converge until pass)
[ ] Phase 8  — Peer review simulation → assembly confirmation
[ ] Phase 9  — Assemble full paper + elevator pitch
[ ] Phase 10 — Final delivery summary
[ ] Phase 11 — Session learnings + portfolio tracker (11b)
```

## Interruption Policy

| Moment | Why |
|--------|-----|
| Phase 1 — venue + preferences confirmation | Cannot proceed without a confirmed venue; title and contributions are optional |
| Paper Plan approval (after Phase 4e) | User approves or adjusts, once: title/contributions, style summary, brief + source map, RQ evidence gaps, novelty flags incl. `[GAP NOT CONFIRMED]` items, recommended framing, high-severity threats |
| Phase 5f — persistent FAIL | Only if the integrity verdict is still FAIL after 2 automated fix cycles (same rule for a persistent 5e HIGH/CRITICAL) |
| Phase 8→9 checkpoint | User decides whether to address simulated-review issues AND confirms full-paper assembly |

Hard error escalations (not approval gates): missing prerequisites in Phase 1 (no sources, no venue guidelines), a subagent failure (ask retry / skip / abort), or the Phase 7 iteration cap reached with critical issues remaining. At all other times, proceed automatically without asking for confirmation.

## Phase 10 — Final Delivery Summary Template

Present the Phase 10 summary in this format:

```
## Paper Complete

**Title**: <title>
**Venue**: <venue>
**Slug**: <paper-slug>

---

### Full Paper
| File | Description |
|------|-------------|
| output/<paper-slug>/full-paper.md | Complete assembled manuscript |
| output/<paper-slug>/elevator-pitch.md | 1-paragraph summary for cover letters |
| output/<paper-slug>/peer-review-simulation.md | Simulated 4-persona peer review |
| output/<paper-slug>/novelty-matrix.md | Contribution novelty validation |
| output/<paper-slug>/citation-verification-report.md | Citation traceability verification |
| output/<paper-slug>/figure-plan.md | Figure/table strategy with captions |

### Individual Sections
| Section | File | Words | Target |
|---------|------|-------|--------|
| Abstract | output/<paper-slug>/abstract.md | ~N | ~M |
| Introduction | output/<paper-slug>/introduction.md | ~N | ~M |
| Related Work | output/<paper-slug>/related-work.md | ~N | ~M |
| Methodology | output/<paper-slug>/methodology.md | ~N | ~M |
| Experiments / Results | output/<paper-slug>/experiments-or-results.md | ~N | ~M |
| Discussion | output/<paper-slug>/discussion.md | ~N | ~M |
| Conclusion | output/<paper-slug>/conclusion.md | ~N | ~M |
| **Total body** | | **~N** | **~M** |
| References | output/<paper-slug>/references.bib | — | — |
| Compliance Report | output/<paper-slug>/compliance-report.md | — | — |
| Paper Brief | output/<paper-slug>/brief.md | — | — |

### Page Estimate
- Total body words: ~N
- Estimated pages: ~Y (venue format)
- Venue limit: Z pages
- Paper target: Z − 1 = W pages
- Status: <within target / over / under>

### Compliance Status
<PASS | PASS WITH WARNINGS | status from final report>

### Peer Review Simulation Verdict
<Average assessment across the 4 reviewer personas (3 for purely theoretical papers): Accept / Weak Accept / Borderline / etc.>
<Top consensus strength to protect>
<Top consensus weakness addressed (or remaining)>

### Word Count Evolution
| Section | First Draft | Final | Delta |
|---------|-------------|-------|-------|
| ... | ~N | ~M | +/- K |

### Remaining TODO Placeholders
<list any [TODO: ...] markers still present in sections, with section name and line>

### Next Steps
- Review `output/<paper-slug>/full-paper.md` for the complete manuscript.
- Review any [TODO: ...] placeholders and fill in missing experimental data.
- <If PASS WITH WARNINGS:> Address remaining warnings listed in output/<paper-slug>/compliance-report.md.
- Review the peer review simulation in `output/<paper-slug>/peer-review-simulation.md` and prepare rebuttals for vulnerabilities noted.
- Use the elevator pitch in `output/<paper-slug>/elevator-pitch.md` for your cover letter.
- Run `/improve-paper <paper-slug>` to deepen, expand, and polish the draft.
- Run `/simulate-review <paper-slug>` to re-run peer review after revisions.
- When ready, run a final proofreading pass with your co-authors.
```

## Automated-Mode Constraints

- Save progress to disk after each section — do not hold sections in memory only.
- Mark todos in real time — one todo `in_progress` at a time.
- All integrity rules (reference integrity, `[MATERIAL GAP]` handling, knowledge-base persistence, assembly confirmation) are defined in the agent instructions and apply unchanged in automated mode.
