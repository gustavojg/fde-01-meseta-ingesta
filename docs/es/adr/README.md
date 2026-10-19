# Registro de decisiones de arquitectura (ADR)

Formato [MADR](https://adr.github.io/madr/). Plantilla: [0000-plantilla.md](0000-plantilla.md).
Cada ADR existe también en inglés en [docs/en/adr](../../en/adr/README.md) con el mismo número.

| Nº | Título | Estado |
| --- | --- | --- |
| [0001](0001-registrar-decisiones-con-adr.md) | Registrar decisiones de arquitectura con ADR en formato MADR | Aceptada |
| [0002](0002-stack-node-typescript.md) | Node 22 con TypeScript estricto como stack del encargo | Aceptada |

## Cómo añadir una ADR

1. Copia `0000-plantilla.md` a `NNNN-titulo-en-kebab-case.md` con el siguiente número libre.
2. Rellena contexto, opciones y decisión. Estado inicial: *Propuesta*.
3. Crea la versión en inglés en `docs/en/adr/NNNN-title.md`.
4. Añade la fila en ambos índices y enlaza la ADR desde el PR.
