# 0002. Node 22 with strict TypeScript as the assignment stack

- **Status:** Accepted
- **Date:** 2026-10-19
- **Deciders:** assignment team
- **Related requirements:** RF-01, RF-02, RF-05, RNF-07, RNF-08
- **Spanish version:** [docs/es/adr/0002-stack-node-typescript.md](../../es/adr/0002-stack-node-typescript.md)

## Context and problem statement

The service reads Excel, polls IMAP and calls a REST API, and must run on a
client-owned Linux server, with no cloud, packaged in Docker. Which language
and tooling do we build it with?

A first draft of this ADR proposed Python 3.12 with `uv`, `pydantic` and
`httpx`. It was never accepted: the Python skeleton was removed in step 2 of
the assignment, before any business logic was written.

## Decision drivers

- Team stack: Node 22 with strict TypeScript is the course's reference stack.
  One runtime the whole team knows and can maintain.
- Mature libraries for `.xlsx`, IMAP/MIME and HTTP.
- Declarative validation of the canonical model (the centre of the system).
- Reproducible environment, fast CI and a small Docker image (RNF-07).
- Portability with no cloud dependencies (RNF-08).

## Considered options

- Node 22 + strict TypeScript: `pnpm`, `vitest`, Biome; for the domain,
  `exceljs`, `imapflow` + `mailparser`, `zod` and native `fetch`.
- Python 3.12+ with `uv`, `openpyxl`, `pydantic`, `httpx`, `typer`.
- Low-code integration platform (n8n or similar).

## Decision outcome

Chosen option: Node 22 + strict TypeScript.

Node ≥ 22.18 runs `.ts` files directly (type stripping), so there is no build
step: `tsc` only checks types (`noEmit`, `erasableSyntaxOnly`,
`verbatimModuleSyntax`, `allowImportingTsExtensions`). The `pnpm` version is
pinned in `packageManager` and CI installs with `--frozen-lockfile`. Tests with
`vitest`, lint and formatting with Biome.

Domain libraries (Excel, IMAP, validation) are added when the matching RF is
implemented; with their own ADR if the choice is not obvious.

### Consequences

- Good, because there is a single runtime and toolchain, the team's, and the
  Docker image is `node:22` with no compile step.
- Good, because `pnpm-lock.yaml`, `packageManager` and `engines` make the
  environment reproducible locally and in CI.
- Good, because the canonical model is strictly typed from day one.
- Bad, because `erasableSyntaxOnly` forbids `enum`, `namespace` and parameter
  properties: literal unions and `as const` objects are used instead.
- Bad, because parsing free-text email will still need hand-written rules; the
  language does not solve that.
- Neutral, because the data ecosystem is narrower than Python's; not needed for
  300 rows per cycle.

### Confirmation

`package.json`, `tsconfig.json`, `biome.json` and `.github/workflows/ci.yml`
reflect this stack. The CI check `test` passes on Node 22 with
`pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm typecheck` and `pnpm test`.

## Pros and cons of the options

### Node 22 + TypeScript

- Good, because it is the team's stack and static typing is solid.
- Good, because `imapflow` and `mailparser` are more convenient than Python's
  standard `imaplib` and `email`.
- Good, because there is no build: the code under test is the code that runs.
- Bad, because there are fewer Excel options (`exceljs`, SheetJS); enough to
  read `.xlsx`.

### Python

- Good, because the data and file-handling ecosystem is the most complete.
- Bad, because it would be a second runtime next to the team's.
- Neutral, because performance is more than enough in both for 300 orders per
  cycle.

### Low-code

- Good, because it starts fast.
- Bad, because deduplication and traceability need logic that is hard to test
  and version on those platforms.
