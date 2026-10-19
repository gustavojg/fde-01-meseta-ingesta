# fde-01-meseta-ingesta

> **English** · [Español](README.es.md)

Order ingestion from Excel files and email into the ERP of **Transportes Meseta**.
FDE course, assignment 01. Transportes Meseta is a fictional client.

[![CI](https://github.com/gustavojg/fde-01-meseta-ingesta/actions/workflows/ci.yml/badge.svg)](https://github.com/gustavojg/fde-01-meseta-ingesta/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## What it does

Customers send transport orders as Excel attachments and emails; today the
back office keys them into the ERP by hand. This service reads both channels,
normalises every order into one canonical model, validates it, discards
duplicates and creates it in the ERP, routing doubtful cases to a manual
review queue with a full audit trail.

Read the [brief](docs/en/01-brief.md) and the [requirements](docs/en/02-requirements.md).

## Status

Skeleton only. Tooling and CI are in place and `src/` holds just the entry
point. The canonical model, the sources and the ERP client come in the next
steps.

## Stack

Node 22 (runs `.ts` directly, no build) · strict TypeScript · [pnpm](https://pnpm.io/) 12 · vitest · [Biome](https://biomejs.dev/).
Rationale in [ADR-0002](docs/en/adr/0002-node-typescript-stack.md).

## Quick start

```bash
nvm use                          # Node 22, from .nvmrc
corepack enable                  # pnpm 12, from package.json "packageManager"
pnpm install --frozen-lockfile
cp .env.example .env
pnpm check                       # biome + tsc + vitest
pnpm dev                         # runs src/main.ts with --watch
```

`DRY_RUN=true` is the default: nothing is written to the ERP until you turn it off.

## Repository layout

```
.
├── .github/workflows/ci.yml   # check `test`: lint + typecheck + tests on push and PR
├── docs/
│   ├── es/                    # Spanish: brief, requisitos, proceso, handoff, adr/
│   └── en/                    # English: brief, requirements, process, handoff, adr/
├── src/
│   ├── main.ts                # entry point (`pnpm dev` / `pnpm start`)
│   └── app.ts                 # side-effect-free app identity and run mode
├── test/
│   ├── smoke.test.ts          # vitest
│   ├── acceptance/            # `pnpm test:acceptance`
│   └── fixtures/              # sample files for tests
├── samples/                   # anonymised example inputs (never real data)
├── .env.example
├── biome.json                 # lint + format
├── tsconfig.json              # strict, noEmit, erasableSyntaxOnly
└── package.json               # pnpm 12 pinned in "packageManager"
```

## Conventions

- **Bilingual docs.** Every document under `docs/` exists in `es/` and `en/`
  and both are updated in the same PR. Code, comments and commit messages are
  in English.
- **Decisions are ADRs** in [MADR](https://adr.github.io/madr/) format, one per
  language, same number. Start from the [template](docs/en/adr/0000-template.md).
- **Requirement ids** (`RF-xx`, `RNF-xx`) are cited in commits, PRs and ADRs.
- **Secrets** live only in `.env` (ignored). `.env.example` documents every variable.
- **Real customer data never enters the repository.** `*.xlsx` and `*.eml` are
  ignored except under `samples/` and `test/fixtures/`.
- **Green CI is required to merge.** Run `pnpm check` before pushing.

## License

[MIT](LICENSE).
