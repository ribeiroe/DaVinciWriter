# Supported Venue Families

Quick reference for formatting rules by venue family. When submitting to one of these venues, the compliance checker uses these as baseline rules and then refines them with the specific guidelines found in `sources/venues/`.

---

## IEEE Conferences

**Examples**: ICASSP, CVPR, ICCV, ECCV, IROS, ICRA, GLOBECOM

| Property | Value |
|----------|-------|
| Template | `IEEEtran` (conference mode) |
| Layout | Two-column |
| Font | 10pt Times New Roman |
| Margins | Standard IEEEtran (top 0.75in, bottom 1in, sides 0.625in) |
| Typical page limit | 4–6 pages (body) + 1 page (references) |
| Citation style | Numbered, order of appearance `[1]` |
| Abstract | 150–200 words, no citations |
| Blind review | Yes for most double-blind venues (CVPR, ICCV) |
| Keywords | Required (Index Terms) |

---

## IEEE Transactions & Journals

**Examples**: IEEE TNNLS, IEEE TASLP, IEEE TMI, IEEE TPAMI

| Property | Value |
|----------|-------|
| Template | `IEEEtran` (journal mode) |
| Layout | Two-column (single-column for initial submission at some journals) |
| Font | 10pt Times New Roman |
| Typical length | 8–14 pages final; no strict limit for submission |
| Citation style | Numbered, order of appearance `[1]` |
| Abstract | < 250 words |
| Blind review | Typically no (single-blind) |
| Keywords | Required |

---

## ACM Proceedings

**Examples**: CHI, SIGIR, SIGMOD, MM, RecSys, CSCW

| Property | Value |
|----------|-------|
| Template | `acmart` with `sigconf` option |
| Layout | Two-column |
| Font | 10pt Linux Libertine |
| Typical page limit | 10–12 pages (body) + unlimited references |
| Citation style | Numbered, alphabetical order `[1]` |
| Abstract | 150–300 words |
| Blind review | Yes (most venues) — use `\acmSubmissionID` |
| Rights block | Auto-inserted by ACM during production |

---

## ACM Journals

**Examples**: TOIS, CACM, JACM

| Property | Value |
|----------|-------|
| Template | `acmart` with `acmsmall` or `acmlarge` option |
| Layout | Single-column |
| Font | 10pt Linux Libertine |
| Citation style | Numbered or author-year depending on journal |
| Abstract | < 300 words, structured or unstructured |

---

## Elsevier Journals

**Examples**: Pattern Recognition, Neural Networks, Computers & Security, Information Sciences

| Property | Value |
|----------|-------|
| Template | Elsevier LaTeX (`elsarticle.cls`) or Word template |
| Layout | Single-column double-spaced **for submission** |
| Font | 12pt Times or Computer Modern |
| Citation style | Numbered `[1]` or author-year `(Smith, 2023)` — journal-specific |
| Abstract | Structured (Highlights + Abstract) or unstructured — journal-specific |
| Highlights | 3–5 bullet points (max 85 chars each) — required by most Elsevier journals |
| Blind review | Double-blind for most journals |

---

## Springer Journals and Conferences

**Examples**: LNCS proceedings (ECCV book), Springer journals (Machine Learning, IJCV)

| Property | Value |
|----------|-------|
| Template | `llncs` (LNCS proceedings) or `svjour3` (journal) |
| Layout | Single-column |
| Font | 10pt Computer Modern or Times |
| Page limit | Defined per volume/conference |
| Citation style | Numbered, order of appearance `[1]` |
| Abstract | < 250 words, no citations |

---

## Custom / Unknown Venues

When the venue does not match any of the above families:

1. Place all available guidelines (PDF, HTML, text) in `sources/venues/<venue-name>/`.
2. The compliance checker will parse them and extract requirements.
3. If key parameters cannot be determined, the checker will list them as `[CANNOT VERIFY]` and ask the user to clarify.

---

## NeurIPS / ICML / ICLR

**Examples**: NeurIPS, ICML, ICLR, AISTATS

| Property | Value |
|----------|-------|
| Template | NeurIPS: `neurips_2024.sty`; ICML: `icml2024.sty`; ICLR: OpenReview template |
| Layout | Single-column |
| Font | 10pt Times or Computer Modern |
| Typical page limit | 8–9 pages (body) + unlimited references |
| Citation style | Numbered author-year `[Smith et al., 2023]` |
| Abstract | < 250 words, no citations |
| Blind review | Double-blind (all three venues) |
| Checklist | NeurIPS requires a reproducibility and ethics checklist (mandatory since 2021) |
| Limitations | Mandatory section since NeurIPS 2022 |
| Keywords | Optional (NeurIPS) / Required (ICML area tracks) |

---

## ACL / EMNLP / NAACL (ACL Anthology venues)

**Examples**: ACL, EMNLP, NAACL, EACL, COLING, AAAI (NLP track)

| Property | Value |
|----------|-------|
| Template | `acl_latex.sty` (ACL Rolling Review template, shared by all) |
| Layout | Two-column |
| Font | 11pt Times New Roman |
| Typical page limit | 8 pages (long paper) / 4 pages (short paper), unlimited references |
| Citation style | Author-year, parenthetical `(Smith et al., 2023)` |
| Abstract | < 300 words |
| Blind review | Double-blind |
| Limitations | Mandatory section since ACL 2023 |
| Ethics statement | Mandatory if human subjects, crowdsourcing, or dual-use concerns |
| Keywords | Not required |

---

## USENIX Security / CCS / IEEE S&P (Security venues)

**Examples**: USENIX Security, ACM CCS, IEEE S&P (Oakland), NDSS

| Property | Value |
|----------|-------|
| Template | USENIX: custom `usenix2019_v3.sty`; CCS: `acmart` sigconf; S&P: IEEEtran |
| Layout | Two-column |
| Font | 10pt |
| Typical page limit | 12–14 pages (USENIX, CCS); 13 pages (S&P) — references count toward limit |
| Citation style | Numbered `[1]` |
| Abstract | < 250 words |
| Blind review | Double-blind (USENIX, CCS, S&P, NDSS all double-blind as of 2024) |
| Artifact evaluation | Optional badge program (all four venues); authors encouraged to submit |
| Ethics | IRB or equivalent expected for human-subjects research |
