# 0002. Python 3.12+ con uv, pydantic y httpx como stack del encargo

- **Estado:** Propuesta
- **Fecha:** 2026-10-19
- **Decisores:** equipo del encargo
- **Requisitos relacionados:** RF-01, RF-02, RF-05, RNF-07, RNF-08
- **Versión en inglés:** [docs/en/adr/0002-python-stack.md](../../en/adr/0002-python-stack.md)

## Contexto y problema

El servicio lee Excel, correo IMAP y llama a una API REST, y debe correr en un
servidor Linux del cliente. ¿Con qué lenguaje y herramientas lo construimos?

## Factores de decisión

- Librerías maduras para `.xlsx`, IMAP/MIME y HTTP.
- Validación de datos declarativa (el modelo canónico es el centro del sistema).
- Entorno reproducible y CI simple.
- Portabilidad sin dependencias de nube (RNF-08).

## Opciones consideradas

- Python 3.12+ con `uv`, `openpyxl`, `pydantic`, `httpx`, `typer`.
- Node.js / TypeScript con `exceljs`, `imapflow`, `zod`.
- Plataforma de integración low-code (n8n o similar).

## Decisión

Opción elegida: Python 3.12+. `openpyxl` y la librería estándar `email`/`imaplib`
cubren las fuentes; `pydantic` da el modelo canónico validado; `httpx` el
cliente ERP; `uv` fija dependencias con lockfile y acelera la CI. Linting y
formato con `ruff`, tests con `pytest`.

### Consecuencias

- Buena, porque todas las piezas son estándar y bien documentadas.
- Buena, porque el `uv.lock` hace reproducible el entorno local y la CI.
- Mala, porque el parseo de correo en texto libre seguirá exigiendo reglas a
  mano; el lenguaje no lo resuelve.

### Confirmación

`pyproject.toml` y `.github/workflows/ci.yml` reflejan este stack; la CI pasa
en Python 3.12 y 3.13.

## Pros y contras de las opciones

### Python

- Buena, porque el ecosistema de datos y ficheros es el más completo.
- Neutra, porque el rendimiento sobra para 300 pedidos por ciclo.

### Node.js / TypeScript

- Buena, porque el tipado estático es sólido.
- Mala, porque la lectura de Excel y MIME es menos madura.

### Low-code

- Buena, porque arranca rápido.
- Mala, porque la deduplicación y la trazabilidad exigen lógica difícil de
  testear y versionar en esas plataformas.
