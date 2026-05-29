---
name: literature-deep-reader
description: Deep reading workflow for scientific papers and research PDFs. Use when the user gives a paper, PDF, DOI, arXiv ID, title, Zotero/Obsidian note, or paper folder and wants Codex to explain the scientific question, research gap, motivation, method pipeline, evidence chain, claims, limitations, and optionally turn each section into Markdown/HTML notes saved locally or backed up to GitHub after confirmation.
---

# Literature Deep Reader

Use this skill to read one paper deeply, then optionally preserve the useful parts as research notes. The default output language follows the user; for Chinese users, write in concise academic Chinese.

## Operating Rules

- Do not invent facts, citations, datasets, equations, metrics, or paper claims. Mark missing information as `unknown` or `needs source check`.
- Distinguish what the paper explicitly claims from your interpretation of its contribution.
- Prefer source-grounded reading: PDF text, abstract, figures, tables, author-provided code, project page, DOI/arXiv metadata, Zotero notes, or user-provided excerpts.
- If only metadata or abstract is available, keep conclusions narrow and say which parts require the full PDF.
- Ask before writing notes, editing a note vault, committing files, pushing to GitHub, or changing an existing note.
- Use Markdown notes by default. Use HTML only when the user asks for browser-openable notes or when an existing workflow expects HTML.

## Deep Reading Workflow

1. Resolve the paper source.
   - Local PDF: extract title, abstract, section headings, figures/tables if possible.
   - Title/DOI/arXiv only: look up metadata or ask for the PDF if the source is unavailable.
   - Multiple sources: link them as one paper entity and prefer the full paper over secondary summaries.
2. Build a paper map before explaining.
   - Bibliographic identity: title, authors, venue/year, DOI/arXiv if available.
   - Problem setting: domain, object of study, assumptions, intended audience.
   - Section map: introduction, related work, method, experiments/results, discussion/limitations.
3. Explain the research logic in this order:
   - Background: what field situation makes the paper necessary.
   - Research gap: what is missing, unresolved, impractical, under-tested, or poorly explained in prior work.
   - Scientific question: the concrete question or hypothesis proposed because of that gap.
   - Proposed answer: the paper's core thesis or mechanism.
   - Method/evidence: what method, dataset, experiment, theory, simulation, proof, ablation, case study, or qualitative analysis supports the thesis.
   - Conclusion boundary: what the evidence does and does not prove.
4. Reconstruct the method as a pipeline when relevant.
   - Inputs, outputs, modules, state, variables, algorithms, prompts/tools/retrieval/training/inference steps, evaluation, and failure handling.
   - Include pseudocode or a minimal implementation sketch only if it helps the user understand or reproduce the work.
5. End with a compact section checklist and ask what to save.
   - Present candidate note sections: `paper-card`, `research-gap`, `scientific-question`, `method-pipeline`, `evidence-chain`, `claims-and-limits`, `reproduction-notes`, `review-positioning`.
   - Ask whether to save all sections or only selected sections.

## Evidence Chain Format

For each important claim, use this structure:

```markdown
### Claim
<one sentence>

- Paper evidence: <experiment/result/table/figure/quote/paraphrase/source location>
- Method used: <empirical/theoretical/simulation/benchmark/ablation/case study/review>
- What it supports: <exact conclusion supported>
- What it does not prove: <boundary or missing evidence>
- Confidence: high | medium | low | needs source check
```

## Note Creation

Read `references/note-template.md` before writing notes.

Default note location if the user has not specified a vault or repo:

```text
notes/literature/<year-or-unknown>/<normalized-paper-title>.md
```

Use stable filenames:

- lowercase ASCII when possible;
- spaces converted to hyphens;
- remove punctuation that is awkward on Windows;
- append DOI/arXiv slug when titles collide.

When writing notes:

1. Show a short preview of headings and target path.
2. Ask for confirmation unless the user already explicitly said to save.
3. Preserve existing notes by updating relevant sections instead of overwriting unrelated content.
4. Add a `sources` section with local PDF path, DOI, arXiv URL, project page, code repo, and access date when known.

## GitHub Backup

Use GitHub only after explicit user confirmation.

Preferred options:

1. If a local Git repository is available and writable, save notes there and use normal git workflow.
2. If a GitHub connector is available and the target repository is writable, create or update files through the connector.
3. If the target repository is not writable, create a local backup folder and report the permission issue.

Never rely on a browser login session as proof of write access. Check repository permissions through the available GitHub tool or local git remote. If permissions are only `pull`, do not attempt to push; tell the user what permission is missing.

Recommended GitHub layout:

```text
codex-skills/literature-deep-reader/
notes/literature/
```

For backing up the skill itself, copy the skill folder unchanged so it remains installable:

```text
codex-skills/literature-deep-reader/SKILL.md
codex-skills/literature-deep-reader/references/note-template.md
codex-skills/literature-deep-reader/agents/openai.yaml
```

## Suggested User Prompts

```text
Use $literature-deep-reader to read this PDF and explain the research gap, scientific question, method pipeline, and evidence chain.
```

```text
Use $literature-deep-reader. After each section, ask whether I want to save it as a note and back it up to GitHub.
```

```text
Use $literature-deep-reader to turn this paper into Chinese notes for a literature review.
```
