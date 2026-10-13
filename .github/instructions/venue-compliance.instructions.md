---
description: "Use when preparing a paper for a specific conference or journal submission, checking page limits, formatting requirements, section requirements, blind review rules, or template compliance."
applyTo: "**"
---

# Venue Compliance Guidelines

## Locating Venue Requirements

Always check `sources/venues/<venue-name>/` first. Files may include:
- Call for papers (CFP) — contains topics, page limits, deadline
- Author guidelines (PDF or HTML) — contains formatting rules
- LaTeX / Word template — defines column layout, font sizes, margins

Official guidelines found there are **authoritative** — they override any family defaults. If no files exist, report the gap to the user (`/set-venue` can generate a provisional requirements summary from family defaults so work can proceed).

## Blind Review Checklist

When the venue requires anonymous submission:
- [ ] Remove author names and affiliations from the title block
- [ ] Replace self-citations with "Anonymous [year]" or remove altogether
- [ ] Remove acknowledgements or replace with "Omitted for blind review"
- [ ] Remove or anonymize links to code repositories, datasets, or personal websites
- [ ] Check PDF metadata for identifying information

## Venue Family Defaults

Detailed venue-family defaults (IEEE, ACM, Elsevier, Springer, NeurIPS/ICML, ACL, security venues) live in `.github/skills/academic-writer/references/venue-families.md` — the single source of truth. Consult that file rather than duplicating its values here; page-density heuristics and budget tracking are handled by `/set-page-budget` and the compliance checker.
