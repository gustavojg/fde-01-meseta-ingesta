# 0002. Node 22 con TypeScript estricto como stack del encargo

- **Estado:** Aceptada
- **Fecha:** 2026-10-19
- **Decisores:** equipo del encargo
- **Requisitos relacionados:** RF-01, RF-02, RF-05, RNF-07, RNF-08
- **Versión en inglés:** [docs/en/adr/0002-node-typescript-stack.md](../../en/adr/0002-node-typescript-stack.md)

## Contexto y problema

El servicio lee Excel, correo IMAP y llama a una API REST, y debe correr en un
servidor Linux del cliente, sin nube, empaquetado en Docker. ¿Con qué lenguaje
y herramientas lo construimos?

Un primer borrador de esta ADR proponía Python 3.12 con `uv`, `pydantic` y
`httpx`. Nunca se aceptó: el esqueleto en Python se retiró en el paso 2 del
encargo antes de escribir lógica de negocio.

## Factores de decisión

- Stack del equipo: Node 22 con TypeScript estricto es el stack de referencia
  del curso. Un único runtime que todo el equipo conoce y puede mantener.
- Librerías maduras para `.xlsx`, IMAP/MIME y HTTP.
- Validación declarativa del modelo canónico (es el centro del sistema).
- Entorno reproducible, CI rápida y una imagen Docker pequeña (RNF-07).
- Portabilidad sin dependencias de nube (RNF-08).

## Opciones consideradas

- Node 22 + TypeScript estricto: `pnpm`, `vitest`, Biome; para el dominio,
  `exceljs`, `imapflow` + `mailparser`, `zod` y el `fetch` nativo.
- Python 3.12+ con `uv`, `openpyxl`, `pydantic`, `httpx`, `typer`.
- Plataforma de integración low-code (n8n o similar).

## Decisión

Opción elegida: Node 22 + TypeScript estricto.

Node ≥ 22.18 ejecuta los `.ts` directamente (*type stripping*), así que no hay
paso de build: `tsc` solo comprueba tipos (`noEmit`, `erasableSyntaxOnly`,
`verbatimModuleSyntax`, `allowImportingTsExtensions`). La versión de `pnpm`
va fijada en `packageManager` y la CI instala con `--frozen-lockfile`. Tests
con `vitest`, lint y formato con Biome.

Las librerías de dominio (Excel, IMAP, validación) se incorporan cuando se
implemente el RF correspondiente; si la elección no es obvia, con su propia ADR.

### Consecuencias

- Buena, porque hay un único runtime y toolchain, el del equipo, y la imagen
  Docker es `node:22` sin paso de compilación.
- Buena, porque `pnpm-lock.yaml`, `packageManager` y `engines` hacen el
  entorno reproducible en local y en CI.
- Buena, porque el modelo canónico tiene tipado estricto desde el primer día.
- Mala, porque `erasableSyntaxOnly` prohíbe `enum`, `namespace` y
  *parameter properties*: se usan uniones de literales y objetos `as const`.
- Mala, porque el parseo de correo en texto libre seguirá exigiendo reglas a
  mano; el lenguaje no lo resuelve.
- Neutra, porque el ecosistema de datos es menos amplio que el de Python; para
  300 filas por ciclo no hace falta.

### Confirmación

`package.json`, `tsconfig.json`, `biome.json` y `.github/workflows/ci.yml`
reflejan este stack. El check `test` de la CI pasa en Node 22 con
`pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm typecheck` y `pnpm test`.

## Pros y contras de las opciones

### Node 22 + TypeScript

- Buena, porque es el stack del equipo y el tipado estático es sólido.
- Buena, porque `imapflow` y `mailparser` son más cómodos que `imaplib` y
  `email` de la librería estándar de Python.
- Buena, porque no hay build: el código que se prueba es el que se ejecuta.
- Mala, porque hay menos opciones para Excel (`exceljs`, SheetJS); suficientes
  para leer `.xlsx`.

### Python

- Buena, porque el ecosistema de datos y ficheros es el más completo.
- Mala, porque sería un segundo runtime respecto al del equipo.
- Neutra, porque el rendimiento sobra en ambos para 300 pedidos por ciclo.

### Low-code

- Buena, porque arranca rápido.
- Mala, porque la deduplicación y la trazabilidad exigen lógica difícil de
  testear y versionar en esas plataformas.
