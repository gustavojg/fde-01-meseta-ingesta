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

Skeleton only. The domain model, settings and CLI exist; the Excel source,
email source and ERP client are stubs that raise `NotImplementedError`.

## Stack

Python 3.12+ · [uv](https://docs.astral.sh/uv/) · pydantic · openpyxl · httpx · typer · ruff · pytest.
Rationale in [ADR-0002](docs/en/adr/0002-python-stack.md).

## Quick start

```bash
uv sync --group dev
cp .env.example .env
make check          # ruff + pytest
uv run meseta-ingesta --help
```

`DRY_RUN=true` is the default: nothing is written to the ERP until you turn it off.

## Repository layout

```
.
├── .github/workflows/ci.yml   # lint + tests on push and PR
├── docs/
│   ├── es/                    # Spanish: brief, requisitos, adr/
│   └── en/                    # English: brief, requirements, adr/
├── src/meseta_ingesta/
│   ├── cli.py                 # `meseta-ingesta` entry point
│   ├── config.py              # settings from env / .env
│   ├── domain/models.py       # canonical Order model
│   ├── sources/               # excel.py, email.py
│   └── erp/client.py          # the only module that talks to the ERP
├── tests/                     # pytest; fixtures/ for sample files
├── samples/                   # anonymised example inputs (never real data)
├── .env.example
├── Makefile
└── pyproject.toml
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
  ignored except under `samples/` and `tests/fixtures/`.
- **Green CI is required to merge.** Run `make check` before pushing.

## License

[MIT](LICENSE).
