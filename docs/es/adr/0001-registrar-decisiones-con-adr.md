# 0001. Registrar decisiones de arquitectura con ADR en formato MADR

- **Estado:** Aceptada
- **Fecha:** 2026-10-19
- **Decisores:** equipo del encargo
- **Requisitos relacionados:** RNF-07
- **Versión en inglés:** [docs/en/adr/0001-record-decisions-with-adr.md](../../en/adr/0001-record-decisions-with-adr.md)

## Contexto y problema

El encargo tomará decisiones (stack, forma de deduplicar, cómo hablar con el
ERP) cuyo porqué se pierde si solo queda en el código o en conversaciones.
¿Cómo dejamos constancia de las decisiones de forma que alguien que llegue
después entienda el contexto y las alternativas descartadas?

## Factores de decisión

- Bajo coste de escritura: debe caber en una revisión de PR.
- Formato conocido fuera del curso.
- Documentación bilingüe (es/en), como el resto del repositorio.

## Opciones consideradas

- MADR (Markdown Any Decision Records).
- Plantilla de Nygard (contexto / decisión / consecuencias).
- Sin ADR: documentar en el README.

## Decisión

Opción elegida: MADR, porque es un estándar público y mantenido, cabe en un
fichero Markdown y su sección de opciones obliga a dejar por escrito lo que se
descartó. Cada ADR se escribe en español e inglés con el mismo número.

### Consecuencias

- Buena, porque las decisiones quedan enlazables desde PRs y requisitos.
- Buena, porque la plantilla fuerza a listar alternativas.
- Mala, porque mantener dos idiomas duplica el esfuerzo de escritura.

### Confirmación

Todo PR que cambie la arquitectura enlaza una ADR; la plantilla de PR lo recuerda.

## Pros y contras de las opciones

### MADR

- Buena, porque tiene plantilla estable y comunidad.
- Neutra, porque es algo más larga que Nygard.

### Nygard

- Buena, porque es muy breve.
- Mala, porque no obliga a listar las opciones descartadas.

### Sin ADR

- Mala, porque el README crece sin estructura y se pierde el histórico.
