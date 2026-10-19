# fde-01-meseta-ingesta

> [English](README.md) · **Español**

Ingesta de pedidos desde ficheros Excel y correo electrónico hacia el ERP de
**Transportes Meseta**. Curso FDE, encargo 01. Transportes Meseta es un cliente ficticio.

[![CI](https://github.com/gustavojg/fde-01-meseta-ingesta/actions/workflows/ci.yml/badge.svg)](https://github.com/gustavojg/fde-01-meseta-ingesta/actions/workflows/ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Qué hace

Los clientes envían pedidos de transporte como adjuntos Excel y correos; hoy
administración los teclea a mano en el ERP. Este servicio lee ambos canales,
normaliza cada pedido a un modelo canónico único, lo valida, descarta
duplicados y lo da de alta en el ERP, enviando los casos dudosos a una cola de
revisión manual con trazabilidad completa.

Lee el [brief](docs/es/01-brief.md) y los [requisitos](docs/es/02-requisitos.md).

## Estado

Solo esqueleto. El tooling y la CI están montados y `src/` tiene solo el punto
de entrada. El modelo canónico, las fuentes y el cliente ERP llegan en los
siguientes pasos.

## Stack

Node 22 (ejecuta `.ts` directamente, sin build) · TypeScript estricto · [pnpm](https://pnpm.io/) 12 · vitest · [Biome](https://biomejs.dev/).
Justificación en la [ADR-0002](docs/es/adr/0002-stack-node-typescript.md).

## Arranque rápido

```bash
nvm use                          # Node 22, desde .nvmrc
corepack enable                  # pnpm 12, desde "packageManager" en package.json
pnpm install --frozen-lockfile
cp .env.example .env
pnpm check                       # biome + tsc + vitest
pnpm dev                         # ejecuta src/main.ts con --watch
```

`DRY_RUN=true` es el valor por defecto: no se escribe nada en el ERP hasta que lo desactives.

## Estructura del repositorio

```
.
├── .github/workflows/ci.yml   # check `test`: lint + typecheck + tests en push y PR
├── docs/
│   ├── es/                    # Español: brief, requisitos, proceso, handoff, adr/
│   └── en/                    # English: brief, requirements, process, handoff, adr/
├── src/
│   ├── main.ts                # punto de entrada (`pnpm dev` / `pnpm start`)
│   └── app.ts                 # identidad de la app y modo de ejecución, sin efectos
├── test/
│   ├── smoke.test.ts          # vitest
│   ├── acceptance/            # `pnpm test:acceptance`
│   └── fixtures/              # ficheros de ejemplo para tests
├── samples/                   # entradas de ejemplo anonimizadas (nunca datos reales)
├── .env.example
├── biome.json                 # lint + formato
├── tsconfig.json              # strict, noEmit, erasableSyntaxOnly
└── package.json               # pnpm 12 fijado en "packageManager"
```

## Convenciones

- **Documentación bilingüe.** Cada documento de `docs/` existe en `es/` y `en/`
  y ambos se actualizan en el mismo PR. Código, comentarios y mensajes de
  commit, en inglés.
- **Las decisiones son ADR** en formato [MADR](https://adr.github.io/madr/),
  una por idioma, mismo número. Parte de la [plantilla](docs/es/adr/0000-plantilla.md).
- **Los identificadores de requisito** (`RF-xx`, `RNF-xx`) se citan en commits, PRs y ADRs.
- **Los secretos** viven solo en `.env` (ignorado). `.env.example` documenta cada variable.
- **Los datos reales de clientes nunca entran en el repositorio.** `*.xlsx` y
  `*.eml` están ignorados salvo en `samples/` y `test/fixtures/`.
- **La CI en verde es obligatoria para fusionar.** Ejecuta `pnpm check` antes de subir.

## Licencia

[MIT](LICENSE).
