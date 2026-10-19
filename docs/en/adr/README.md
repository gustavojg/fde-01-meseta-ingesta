# Architecture Decision Records (ADR)

[MADR](https://adr.github.io/madr/) format. Template: [0000-template.md](0000-template.md).
Every ADR also exists in Spanish in [docs/es/adr](../../es/adr/README.md) with the same number.

| No. | Title | Status |
| --- | --- | --- |
| [0001](0001-record-decisions-with-adr.md) | Record architecture decisions with ADRs in MADR format | Accepted |
| [0002](0002-node-typescript-stack.md) | Node 22 with strict TypeScript as the assignment stack | Accepted |

## How to add an ADR

1. Copy `0000-template.md` to `NNNN-title-in-kebab-case.md` using the next free number.
2. Fill in context, options and decision. Initial status: *Proposed*.
3. Create the Spanish version in `docs/es/adr/NNNN-titulo.md`.
4. Add the row to both indexes and link the ADR from the PR.
