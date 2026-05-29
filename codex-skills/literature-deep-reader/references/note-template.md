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
- Title translation:
- Authors:
- Author affiliations:
- Affiliation translation:
- Source files: <local PDF / DOI / arXiv / URL>
- Reading purpose: <why the user is reading this paper>

## One-Sentence Thesis

<The paper's central claim in one sentence.>

- Source anchor:
- Status: directly supported | interpretation | uncertain

## Research Background and Gap

- Background: <field context>
- Existing limitation: <what prior work cannot answer or do>
- Gap type: <unresolved mechanism | method limitation | missing evidence | untested setting | application gap | theory gap>
- Why the gap matters: <consequence for the field or user's project>
- Source anchor:
- Status: directly supported | interpretation | uncertain

## Scientific Question

<The concrete question, hypothesis, or objective proposed because of the gap.>

- Source anchor:
- Status: directly supported | interpretation | uncertain

## Method Pipeline

1. Input:
2. Core modules or steps:
3. Intermediate representation/state:
4. Output:
5. Evaluation or verification:
6. Failure handling or assumptions:

For each inferred step, mark `interpretation` unless the paper explicitly states it.

## Evidence Chain

### Claim 1

- Source anchor:
- Paper evidence:
- Method used:
- What it supports:
- What it does not prove:
- Confidence:
- Status: directly supported | interpretation | uncertain

## Main Contributions

- <contribution 1>
- <contribution 2>
- <contribution 3>

## Limitations and Risks

- Internal limitation:
- External validity limitation:
- Reproducibility risk:
- Evidence gap:

## Conclusion Translation

<Translate the explicit conclusion section or final synthesis paragraph. If no explicit conclusion section exists, identify the source paragraph.>

- Source anchor:
- Status: directly supported | interpretation | uncertain

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
- Use source-only reading by default. Do not add external context unless the user explicitly asks.
- Label any synthesis beyond the paper's explicit statements as `interpretation`.
