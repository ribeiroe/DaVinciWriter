---
description: "Learn writing style from previously published papers. Analyzes papers in sources/my-papers/ to build a style profile that the paper-writer will use to mirror the researcher's voice."
name: "Learn Style"
agent: academic-writer
argument-hint: "Optional: specific paper filename(s) to analyze, or leave blank to analyze all papers in sources/my-papers/"
tools: [read, search, edit, agent]
---

You are building a writing style profile from a researcher's previously published papers.

## Step 1 — Locate Source Papers

Check `sources/my-papers/` for existing files.

- If the folder is empty: inform the user — "No papers found in `sources/my-papers/`. Please add your previously published papers (PDF, Markdown, or text format) to this folder and run this prompt again."
- If files exist: list them and confirm with the user before proceeding.

## Step 2 — Delegate Style Analysis

Delegate to the `style-learner` agent:

> "Analyze the writing style from the following papers: [list of file paths]. Build a comprehensive style profile and save it to `output/knowledge/style-profile.md`. If a style profile already exists, merge the new observations."

## Step 3 — Review the Profile

After the style learner completes, read `output/knowledge/style-profile.md` and present a brief summary to the user:

- Voice and person (we / passive)
- Typical sentence length
- Characteristic phrases
- Citation density
- Number of papers analyzed

## Step 4 — Confirm

Ask the user if the profile looks accurate. If they want to add corrections:
- Accept freeform corrections and append them as a "User Overrides" section at the bottom of `output/knowledge/style-profile.md`.

User overrides take precedence over automatically learned patterns.
