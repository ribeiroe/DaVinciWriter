---
description: "Revise a submitted paper based on real peer reviewer feedback. Audits all source folders, builds a reviewer response matrix, rewrites the manuscript directly, produces a change log and remaining risks report. Designed to maximise acceptance probability in the next review round."
name: "Revise Paper"
agent: academic-writer
argument-hint: "Paper slug (e.g. 'certia360-ieee-access'). Then paste the reviewer comments, or place them in sources/reviewer-feedback/."
tools: [read, search, edit, agent, todo]
---

You are orchestrating a systematic, evidence-grounded revision of a submitted paper based on peer reviewer feedback. Your goal is to maximise the probability of acceptance in the next review round.

This prompt drives the `revision-specialist` subagent through the full revision pipeline. Read these instructions completely before taking any action.

---

## Step 0 — Identify the Paper and Feedback

1. Ask the user for the **paper slug** (e.g., `certia360-ieee-access`) if not already provided.
2. Locate the draft in `output/<paper-slug>/`. Confirm that section `.md` files exist.
3. Collect the reviewer feedback:
   - Check `sources/reviewer-feedback/` for any saved review files (`.md`, `.txt`, or `.pdf`).
   - If none exist, ask the user to paste the reviewer comments directly.
   - If saving for traceability, write them to `sources/reviewer-feedback/<paper-slug>-round-<N>.md`.
4. **Load the response-letter style profile** per the canonical procedure in `.github/skills/academic-writer/references/response-letter-loading.md`, and pass the profile to the revision specialist so the reviewer response matrix and author-response tone match the researcher's established voice. (The standalone rebuttal letter is produced separately by `/draft-rebuttal` — see Step 4.)
5. **Confirm the parsed concerns with the user (mandatory, before delegation)**: Parse the reviewer feedback yourself into a concerns table — reviewer ID, overall recommendation, major concerns, minor concerns, questions for authors, plus detected conflicts and consensus issues (the same structure the revision specialist uses in its Phase 1). Present this table to the user and get ONE confirmation. Only then proceed to Step 1. This is the single user pause in the flow: the delegated subagent runs fire-and-forget and cannot pause, so the confirmation must happen here.

---

## Step 1 — Delegate to Revision Specialist

Delegate the full revision pipeline to the `revision-specialist` subagent with this instruction:

> "Perform a complete systematic revision of the paper at `output/<paper-slug>/` based on the following reviewer feedback. The user has confirmed the parsed reviewer concerns (attached below) — do not pause for confirmation. Execute all phases: parse reviewer feedback, audit all source folders, build the reviewer response matrix, revise the manuscript directly, run the statistical rigour check, produce the source utilisation audit, generate the gap analysis, and write all seven required output files (reviewer-response-matrix.md, full-paper-revised.md, revision-change-log.md, remaining-risks.md, source-folder-assessment.md, source-utilisation-audit.md, gap-analysis.md). Do not suggest edits — rewrite sections directly. Apply the response-letter style profile from `output/knowledge/response-letter-profile.md` (if it exists) to the reviewer response matrix and to any response-to-reviewer tone in `full-paper-revised.md`. Do not write a rebuttal letter — that is produced separately by `/draft-rebuttal`."

Pass to the subagent:
- The paper slug
- The raw reviewer feedback text
- The user-confirmed parsed concerns table from Step 0 item 5 (including any corrections the user made)
- The target venue (read from `output/<paper-slug>/brief.md` or ask the user)
- The response-letter style profile path (if it exists)

---

## Step 2 — Post-Revision Compliance Check

After the revision specialist completes, run the compliance checker:

> "Run a compliance check on the revised paper at `output/<paper-slug>/full-paper-revised.md` against the venue guidelines at `sources/venues/<venue-slug>/`. Flag any violations introduced during revision. Save the report to `output/<paper-slug>/compliance-report-revised.md`."

**Iteration cap**: if the compliance check (or any other gate in this flow) fails, run at most **2 automated fix → recheck cycles** per gate. If issues remain after the second cycle, stop iterating and present the remaining issues to the author with a recommendation on how to proceed.

---

## Step 3 — Summary Report to User

Present the user with a concise summary:

```
## Revision Complete

**Paper**: <title>
**Venue**: <venue>
**Revision round**: <N>

### What Was Done
- <N> reviewer concerns addressed (Critical: X, Important: Y, Minor: Z)
- <N> sections substantially revised
- <N> new citations added
- Source utilisation: <N>/<total> sources used

### Key Files Written
Seven files from the revision specialist:
- output/<paper-slug>/reviewer-response-matrix.md
- output/<paper-slug>/full-paper-revised.md
- output/<paper-slug>/revision-change-log.md
- output/<paper-slug>/remaining-risks.md
- output/<paper-slug>/source-folder-assessment.md
- output/<paper-slug>/source-utilisation-audit.md
- output/<paper-slug>/gap-analysis.md

Plus one from the Step 2 compliance check:
- output/<paper-slug>/compliance-report-revised.md

### Remaining Risks
<Brief summary of unresolved concerns — see remaining-risks.md for details>

### Recommendation
<Ready to resubmit / Needs author action on X items before resubmission>
```

---

## Step 4 — Optional: Draft Rebuttal Letter

Ask the user:

> "Would you like me to draft a point-by-point rebuttal letter for the journal or conference submission system? This will map every reviewer concern to the specific changes made in the revised manuscript."

If yes, invoke `/draft-rebuttal` with the paper slug and the revision matrix as input.
