# Literature Note Template

Use this template as a flexible schema. Remove empty sections rather than filling them with generic text.

```markdown
---
title: "<paper title>"
authors: []
year: unknown
venue: unknown
doi: unknown
arxiv: unknown
tags: [literature-note]
status: draft
---

# <paper title>

## Basic Information

- Citation: <short citation>
- Source files: <local PDF / DOI / arXiv / URL>
- Reading purpose: <why the user is reading this paper>

## One-Sentence Thesis

<The paper's central claim in one sentence.>

## Research Background and Gap

- Background: <field context>
- Existing limitation: <what prior work cannot answer or do>
- Gap type: <unresolved mechanism | method limitation | missing evidence | untested setting | application gap | theory gap>
- Why the gap matters: <consequence for the field or user's project>

## Scientific Question

<The concrete question, hypothesis, or objective proposed because of the gap.>

## Method Pipeline

1. Input:
2. Core modules or steps:
3. Intermediate representation/state:
4. Output:
5. Evaluation or verification:
6. Failure handling or assumptions:

## Evidence Chain

### Claim 1

- Paper evidence:
- Method used:
- What it supports:
- What it does not prove:
- Confidence:

## Main Contributions

- <contribution 1>
- <contribution 2>
- <contribution 3>

## Limitations and Risks

- Internal limitation:
- External validity limitation:
- Reproducibility risk:
- Evidence gap:

## Reproduction Notes

- Data:
- Code:
- Environment:
- Key parameters:
- Expected outputs:

## Review Positioning

- Use in literature review as:
- Related papers to compare with:
- Possible citation role:

## Open Questions

- <question to revisit>

## Sources

- <source list with access date when relevant>
```

Quality rules:

- Every important claim should point to a source location, figure/table, experiment, theorem, or explicit paper passage.
- Keep `unknown` when the source does not support a field.
- Prefer a few high-quality claims over many vague bullets.
