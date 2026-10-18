# 0002. Python 3.12+ with uv, pydantic and httpx as the assignment stack

- **Status:** Proposed
- **Date:** 2026-10-19
- **Deciders:** assignment team
- **Related requirements:** RF-01, RF-02, RF-05, RNF-07, RNF-08
- **Spanish version:** [docs/es/adr/0002-stack-python.md](../../es/adr/0002-stack-python.md)

## Context and problem statement

The service reads Excel, polls IMAP and calls a REST API, and must run on a
client-owned Linux server. Which language and tooling do we build it with?

## Decision drivers

- Mature libraries for `.xlsx`, IMAP/MIME and HTTP.
- Declarative data validation (the canonical model is the centre of the system).
- Reproducible environment and simple CI.
- Portability with no cloud dependencies (RNF-08).

## Considered options

- Python 3.12+ with `uv`, `openpyxl`, `pydantic`, `httpx`, `typer`.
- Node.js / TypeScript with `exceljs`, `imapflow`, `zod`.
- Low-code integration platform (n8n or similar).

## Decision outcome

Chosen option: Python 3.12+. `openpyxl` and the standard `email`/`imaplib`
modules cover the sources; `pydantic` provides the validated canonical model;
`httpx` the ERP client; `uv` pins dependencies with a lockfile and speeds up
CI. Linting and formatting with `ruff`, tests with `pytest`.

### Consequences

- Good, because every piece is standard and well documented.
- Good, because `uv.lock` makes the local environment and CI reproducible.
- Bad, because parsing free-text email will still need hand-written rules; the
  language does not solve that.

### Confirmation

`pyproject.toml` and `.github/workflows/ci.yml` reflect this stack; CI passes
on Python 3.12 and 3.13.

## Pros and cons of the options

### Python

- Good, because the data and file-handling ecosystem is the most complete.
- Neutral, because performance is more than enough for 300 orders per cycle.

### Node.js / TypeScript

- Good, because static typing is solid.
- Bad, because Excel and MIME parsing are less mature.

### Low-code

- Good, because it starts fast.
- Bad, because deduplication and traceability need logic that is hard to test
  and version on those platforms.
