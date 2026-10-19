# Traspaso — Estado del encargo y cómo continuar

> Curso FDE · Encargo 01 · [English version](../en/04-handoff.md)
>
> Documento para quien coja el encargo a partir de aquí, persona o agente.
> Última actualización: 2026-10-19.

## 1. En una frase

Servicio que lee pedidos de Excel y correo, los valida, quita repetidos y los
da de alta en Logiwin, mandando a revisión lo que no tenga claro antes de que
Luis monte las rutas a las 14:00.

## 2. Dónde está cada cosa

| Qué | Dónde |
| --- | --- |
| Contexto del cliente y criterios de éxito | [01-brief.md](01-brief.md) |
| Requisitos con estado confirmado / supuesto y preguntas abiertas | [02-requisitos.md](02-requisitos.md) |
| Proceso as-is y to-be con diagramas | [03-proceso.md](03-proceso.md) |
| Decisiones de arquitectura | [adr/README.md](adr/README.md) |
| Código | `src/meseta_ingesta/` (modelo canónico, configuración, CLI y fuentes en esqueleto) |
| Tests y CI | `tests/`, `.github/workflows/ci.yml` |

Cada documento existe en español e inglés y deben mantenerse sincronizados.

## 3. Lo que ya sabemos y no estaba en el brief

Sale de la entrevista con la responsable de operaciones (octubre de 2026):

- El ERP es Logiwin. Guarda todo desde 2017. Tiene observaciones en texto libre.
- Administración son tres personas (Pili, Rosa, Carmen), no dos. Luis monta
  rutas. Javier es gerencia y habla con la asesoría de RGPD.
- El pico es el lunes: el Excel de Agroalimentaria. El hito es tenerlo entero
  a las 14:00. Latencia aceptable: 1 hora, 2 como máximo.
- Hoy 4 de cada 100 pedidos tienen error (dirección, peso, repetido). Objetivo:
  1 de cada 100, y que lo dudoso se vea antes de que salga el camión.
- Los repetidos hoy entran en Logiwin y se facturan dos veces.
- Muebles Cifuentes manda datos de particulares (nombre, dirección, móvil,
  observaciones sensibles). Nadie ha decidido cuánto tiempo guardarlos.
- No se publica ahorro en horas de oficina. Es una condición de la responsable.

## 4. Decisiones tomadas

- ADR-0001: decisiones como ADR en formato MADR. Aceptada.
- ADR-0002: stack Python 3.12 con uv, pydantic, httpx. **Propuesta, no
  aceptada.** El stack de referencia del curso es Node 22 con TypeScript
  estricto; hay que decidir si se migra el esqueleto antes de escribir lógica.
- Precisión antes que cobertura: no hay objetivo de porcentaje de auto-alta
  (RNF-10). Se retiró el "≥ 80 %" del brief.
- La deduplicación es nuestra, no se delega en Logiwin (RF-06).
- Retención: 60 días para originales y pedidos a particulares, 90 para el
  resto, a falta de que la asesoría diga otra cosa (RNF-03).
- Al campo de observaciones de Logiwin solo pasa `notes` filtrado, nunca el
  correo entero (CA-05.4).

## 5. Lo que no sabemos y bloquea

Las preguntas completas están en [02-requisitos.md](02-requisitos.md#5-preguntas-abiertas).
Las que condicionan el diseño antes de escribir código:

| Pregunta | Para quién | Qué bloquea |
| --- | --- | --- |
| Q1 / Q6: ¿la API de Logiwin busca por referencia y acepta repetidos? | Responsable de sistemas, Javier | Diseño del cliente ERP y de la deduplicación |
| Q7: ¿hay entorno de pruebas de Logiwin? | Responsable de sistemas | Plan de pruebas y primera puesta en marcha |
| Q3: ¿qué plantillas hay y cuáles traen referencia propia? | Administración | Mapeo por cliente y clave de duplicado alternativa (CA-06.4) |
| Q8: ¿cuántas filas trae el Excel del lunes? | Administración | Si RNF-05 es realista |
| Q13: ¿cómo se distingue entrega a particular en Cifuentes? | Administración | `delivery_is_consumer` y la retención corta |
| Q14: plazo legal de conservación de datos de particulares | Javier y asesoría | Confirmar o cambiar los 60 días |

Para Q3, Q8 y Q13 lo más rápido es pedir a administración un Excel real de
cada cliente (anonimizado si hace falta) y tres o cuatro correos de pedido
reales. Van en `samples/`, que hoy está vacío.

## 6. Siguiente paso recomendado

1. Decidir el stack (cerrar ADR-0002 o escribir ADR-0003 con la migración a
   Node 22 + TypeScript) antes de implementar parseo.
2. Conseguir muestras reales de Excel y correo y meterlas en `samples/` y
   `tests/fixtures/`.
3. Implementar en este orden, cada paso con tests: modelo canónico y
   normalización (RF-03), parseo Excel (RF-01), validación (RF-04),
   deduplicación (RF-06), cola de revisión y notificación (RF-07), cliente
   Logiwin en modo dry-run (RF-05), correo (RF-02).
4. Primera prueba con el cliente: un lunes, en dry-run, contra el Excel real de
   Agroalimentaria. Medir cuánto tarda y cuántos pedidos van a revisión.

## 7. Cosas que no hay que hacer

- No presentar el proyecto como ahorro de personal, ni en métricas ni en
  informes.
- No cargar un pedido "por si acaso". Ante la duda, cola de revisión.
- No conectar el IMAP sin fecha de corte: el buzón tiene años de correos.
- No volcar el cuerpo del correo en observaciones de Logiwin.
- No escribir datos personales en logs.
- No tocar el histórico de Logiwin, el buzón ni las carpetas del servidor:
  eso es de gerencia y la asesoría.

## 8. Convenciones del repositorio

- Docs bilingües, mismos ficheros en `docs/es` y `docs/en`.
- ADR en formato MADR, numeradas, con versión en ambos idiomas.
- Los identificadores RF-xx, RNF-xx, CA-xx y Qx son estables: se citan en
  commits, PRs y ADRs.
- Los cambios se dejan preparados en el índice de git, no se hacen commits
  sin que lo pida el responsable del repositorio.
