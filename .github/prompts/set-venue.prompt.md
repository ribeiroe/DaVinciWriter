---
description: "Set or change the target conference or journal for the current paper. Registers the venue and validates that its guidelines are available in the sources/venues/ folder."
name: "Set Venue"
agent: academic-writer
argument-hint: "Conference or journal name (e.g. 'IEEE ICASSP 2026', 'ACM CHI 2026', 'Elsevier Pattern Recognition')"
tools: [read, search, edit]
---

You are configuring the target publication venue for a paper.

## Step 1 — Identify the Venue

From the user's input, extract:
- **Venue name** (e.g., IEEE ICASSP 2026)
- **Venue type**: conference | journal
- **Venue family**: IEEE | ACM | Elsevier | Springer | Other

## Step 2 — Check for Existing Guidelines

Look for files in `sources/venues/`:
- If a subfolder matching the venue name exists, list its contents.
- If no guidelines are found, instruct the user:

  > "No guidelines found for **<venue>**. Please add the author guidelines to `sources/venues/<venue>/`. You can typically download them from the venue's official website. Accepted formats: PDF, Markdown, or plain text."

  Then offer two options:
  1. **Wait** — pause until the user confirms the files have been added, then continue with Step 3.
  2. **Proceed provisionally** — generate a PROVISIONAL `requirements-summary.md` from the venue family defaults in `.github/skills/academic-writer/references/venue-families.md`, so the pipeline can proceed. Use the Step 3 format, with this banner as the first line after the title:

     > **PROVISIONAL — generated from venue family defaults. Replace with the official guidelines before submission.**

     Remind the user to add the official guidelines to `sources/venues/<venue>/` and re-run `/set-venue` before submitting.

## Step 3 — Parse Key Requirements

Once guidelines are available, read them and extract a concise requirements summary:

```markdown
# Venue Requirements — <Venue Name>

**Submission Format**: PDF | LaTeX | Word
**Template**: IEEE / ACM / Elsevier / Custom
**Page Limit**: X pages (body) + Y pages (references)
**Column Layout**: single | double
**Font**: ...
**Abstract Word Limit**: ~X words
**Blind Review**: yes | no
**Citation Style**: numbered [1] | author-year (Smith, 2023)
**Supplementary Allowed**: yes | no | yes with limits
**Submission Deadline**: ...
**Special Notes**: ...
```

Save this file to `sources/venues/<venue-slug>/requirements-summary.md`.

## Step 4 — Register the Venue

If a paper brief exists at `output/<paper-slug>/brief.md`, update the **Venue** field with the confirmed venue name.

Confirm to the user that the venue is set and the compliance checker is ready to validate against it.
