# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added

- Process doc (as-is / to-be, Mermaid) and handoff doc in both languages.

### Changed

- Stack switched to Node 22 + strict TypeScript (ADR-0002 accepted, replaces the Python
  proposal): pnpm 12 pinned via `packageManager`, frozen lockfile, vitest, Biome, single
  CI check `test` (lint, typecheck, tests).
- Brief and requirements updated after the interview with the head of operations:
  Logiwin named, stakeholders corrected, success criteria rewritten around the Monday
  14:00 milestone and precision over coverage, every RF marked confirmed / assumed,
  weight and address validation added, retention tightened, open questions Q6-Q15.

### Removed

- Python skeleton (`pyproject.toml`, `uv.lock`, `src/meseta_ingesta/`, `tests/`, `Makefile`).

### Added (initial)

- Repository skeleton: bilingual docs (brief, requirements, ADR template, ADR-0001, ADR-0002),
  canonical `Order` model, settings, CLI stub, smoke tests, CI workflow, MIT license.
