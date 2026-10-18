# 0001. Record architecture decisions with ADRs in MADR format

- **Status:** Accepted
- **Date:** 2026-10-19
- **Deciders:** assignment team
- **Related requirements:** RNF-07
- **Spanish version:** [docs/es/adr/0001-registrar-decisiones-con-adr.md](../../es/adr/0001-registrar-decisiones-con-adr.md)

## Context and problem statement

The assignment will make decisions (stack, deduplication approach, how to talk
to the ERP) whose rationale is lost if it only lives in code or conversations.
How do we record decisions so that someone arriving later understands the
context and the discarded alternatives?

## Decision drivers

- Low writing cost: it must fit in a PR review.
- A format known outside the course.
- Bilingual documentation (es/en), like the rest of the repository.

## Considered options

- MADR (Markdown Any Decision Records).
- Nygard template (context / decision / consequences).
- No ADRs: document in the README.

## Decision outcome

Chosen option: MADR, because it is a public, maintained standard, fits in one
Markdown file and its options section forces the discarded alternatives to be
written down. Every ADR is written in Spanish and English with the same number.

### Consequences

- Good, because decisions become linkable from PRs and requirements.
- Good, because the template forces alternatives to be listed.
- Bad, because maintaining two languages doubles the writing effort.

### Confirmation

Every PR that changes the architecture links an ADR; the PR template reminds it.

## Pros and cons of the options

### MADR

- Good, because it has a stable template and a community.
- Neutral, because it is somewhat longer than Nygard.

### Nygard

- Good, because it is very short.
- Bad, because it does not force listing discarded options.

### No ADRs

- Bad, because the README grows without structure and history is lost.
