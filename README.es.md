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

Solo esqueleto. Existen el modelo de dominio, la configuración y la CLI; el
origen Excel, el origen email y el cliente ERP son stubs que lanzan
`NotImplementedError`.

## Stack

Python 3.12+ · [uv](https://docs.astral.sh/uv/) · pydantic · openpyxl · httpx · typer · ruff · pytest.
Justificación en la [ADR-0002](docs/es/adr/0002-stack-python.md).

## Arranque rápido

```bash
uv sync --group dev
cp .env.example .env
make check          # ruff + pytest
uv run meseta-ingesta --help
```

`DRY_RUN=true` es el valor por defecto: no se escribe nada en el ERP hasta que lo desactives.

## Estructura del repositorio

```
.
├── .github/workflows/ci.yml   # lint + tests en push y PR
├── docs/
│   ├── es/                    # Español: brief, requisitos, adr/
│   └── en/                    # English: brief, requirements, adr/
├── src/meseta_ingesta/
│   ├── cli.py                 # punto de entrada `meseta-ingesta`
│   ├── config.py              # configuración desde entorno / .env
│   ├── domain/models.py       # modelo canónico Order
│   ├── sources/               # excel.py, email.py
│   └── erp/client.py          # único módulo que habla con el ERP
├── tests/                     # pytest; fixtures/ para ficheros de ejemplo
├── samples/                   # entradas de ejemplo anonimizadas (nunca datos reales)
├── .env.example
├── Makefile
└── pyproject.toml
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
  `*.eml` están ignorados salvo en `samples/` y `tests/fixtures/`.
- **La CI en verde es obligatoria para fusionar.** Ejecuta `make check` antes de subir.

## Licencia

[MIT](LICENSE).
