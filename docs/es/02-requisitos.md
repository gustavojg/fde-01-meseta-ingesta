# Requisitos — Ingesta de pedidos para Transportes Meseta

> Curso FDE · Encargo 01 · [English version](../en/02-requirements.md)
>
> Los identificadores (RF-xx, RNF-xx) son estables: se citan en commits, PRs y ADRs.
> Prioridad: **M** (debe), **S** (debería), **C** (podría).
>
> Estado de cada requisito:
> **Confirmado** = respaldado por la entrevista con la responsable de operaciones
> (octubre de 2026). **Supuesto** = viene del brief inicial o de nuestro criterio
> y el cliente no lo ha validado. Un requisito puede estar confirmado en su
> necesidad y tener criterios de aceptación supuestos; se indica en cada caso.

## 1. Modelo canónico de pedido

Todas las fuentes se traducen a un único modelo `Order`:

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `customer_code` | texto | sí | Código de cliente tal y como existe en Logiwin. |
| `external_ref` | texto | sí | Referencia del pedido en el sistema del cliente. |
| `pickup_address` | texto | sí | Dirección de recogida. |
| `delivery_address` | texto | sí | Dirección de entrega. |
| `delivery_contact_name` | texto | no | Encargado, jefe de obra o particular. **Dato personal.** |
| `delivery_contact_phone` | texto | no | Teléfono de contacto en destino. **Dato personal.** |
| `delivery_is_consumer` | booleano | sí | `true` si el destino es el domicilio de un particular (p. ej. Muebles Cifuentes). Activa la retención corta. |
| `requested_date` | fecha | sí | Fecha solicitada de recogida. |
| `lines[]` | lista | sí (≥ 1) | Descripción, cantidad, peso (kg) y volumen (m³) opcionales. |
| `notes` | texto | no | Observaciones libres. Pueden contener datos personales ("llamar antes, trabaja por la mañana"). |
| `source` | enum | sí | `excel` o `email`. |
| `source_id` | texto | sí | Ruta del fichero o `Message-ID` del correo. |

La clave de duplicado es `(customer_code, external_ref)`.

Los campos de contacto y `delivery_is_consumer` se añaden tras la entrevista:
los Excel traen nombre y teléfono del encargado y, en Cifuentes, del cliente
final. Cómo se detecta que un destino es un particular sigue abierto (Q13).

## 2. Requisitos funcionales

### RF-01 · Ingesta desde Excel · M · Confirmado

Los cuatro clientes principales envían Excel. El sistema lee los ficheros
`.xlsx` depositados en la carpeta de entrada y extrae un pedido por fila (o por
hoja, según configuración del cliente).

- CA-01.1 Un fichero con N filas válidas produce N pedidos. *(supuesto: un
  pedido por fila; no hemos visto las plantillas, Q3)*
- CA-01.2 El mapeo columna → campo canónico se define por cliente en un fichero
  de configuración, sin tocar código.
- CA-01.3 Un fichero procesado se mueve a `processed/`; uno ilegible, a
  `rejected/` con un informe del motivo.
- CA-01.4 Se aceptan fechas en los formatos `dd/mm/aaaa`, `aaaa-mm-dd` y fecha
  nativa de Excel.
- CA-01.5 El Excel del lunes de Agroalimentaria se procesa entero en un ciclo.
  Su tamaño está pendiente (Q8). *(confirmado como necesidad)*

### RF-02 · Ingesta desde correo electrónico · M · Confirmado (buzón), Supuesto (formato)

Existe un buzón de pedidos dedicado desde hace años. El sistema lo lee por IMAP
y procesa cada mensaje no leído posterior a una fecha de corte configurable.

- CA-02.1 Si el correo lleva un `.xlsx` adjunto, se procesa igual que en RF-01.
- CA-02.2 Si el cuerpo contiene pedidos en formato semiestructurado
  (`campo: valor` por línea), se extraen con las mismas reglas de validación.
  *(supuesto: la responsable describe texto libre; hay que ver correos reales)*
- CA-02.3 El remitente se usa para identificar al cliente mediante una tabla de
  correos autorizados; un remitente desconocido va a revisión manual.
- CA-02.4 Cada mensaje se procesa una sola vez (se marca como leído o se mueve
  a una carpeta `procesados`).
- CA-02.5 Los mensajes anteriores a `IMAP_SINCE` no se procesan nunca. El buzón
  acumula años de histórico. *(confirmado el histórico; la fecha de corte es Q9)*

### RF-03 · Normalización · M · Supuesto

Todo pedido se convierte al modelo canónico antes de cualquier otra operación.

- CA-03.1 Direcciones y referencias se recortan de espacios y se normalizan
  mayúsculas según regla configurable.
- CA-03.2 Un pedido que no pueda mapearse a todos los campos obligatorios se
  rechaza con una lista de campos faltantes.

### RF-04 · Validación de negocio · M · Confirmado (necesidad), Supuesto (reglas)

Los tres errores que hoy se descubren en ruta son dirección, peso y repetido.
La validación debe cubrirlos y, ante la duda, **no cargar**: la responsable
prefiere doce pedidos en revisión a uno mal cargado.

- CA-04.1 `customer_code` debe existir en Logiwin (consulta cacheada).
- CA-04.2 `requested_date` no puede ser anterior a hoy ni posterior a 90 días.
  *(supuesto; pedidos para fecha pasada, Q4)*
- CA-04.3 Cada línea debe tener cantidad > 0.
- CA-04.4 El peso total del pedido debe estar dentro de un rango configurable
  por cliente; fuera de rango o sin peso cuando el cliente siempre lo manda, va
  a revisión. *(confirmado como necesidad; los rangos son Q11)*
- CA-04.5 La dirección de entrega debe superar una comprobación mínima
  (localidad reconocible, no vacía, no igual a la de recogida); contra qué
  maestro se valida es Q10. *(confirmado como necesidad)*
- CA-04.6 Un pedido inválido no se descarta: va a la cola de revisión con los
  motivos.

### RF-05 · Alta en Logiwin · M · Supuesto (API)

- CA-05.1 Un pedido válido y no duplicado se crea en Logiwin mediante su API y
  se guarda el identificador devuelto. *(supuesto: no se ha visto la API, Q1)*
- CA-05.2 Si la API falla de forma transitoria, se reintenta con espera
  exponencial (máximo configurable); si falla de forma definitiva, va a revisión.
- CA-05.3 En modo `DRY_RUN=true` no se escribe nada en Logiwin y se registra lo
  que se habría creado.
- CA-05.4 Al campo de observaciones de Logiwin solo pasa `notes` ya filtrado,
  nunca el cuerpo completo del correo. *(nuevo, derivado del riesgo de
  observaciones libres)*

### RF-06 · Deduplicación · M · Confirmado

Hoy los pedidos repetidos entran en Logiwin y se facturan dos veces. Logiwin no
los rechaza (pendiente de confirmar por sistemas, Q6), así que la
deduplicación es responsabilidad de este sistema.

- CA-06.1 Un pedido cuya clave `(customer_code, external_ref)` ya se haya
  cargado no se vuelve a crear.
- CA-06.2 Si el pedido duplicado difiere del original en algún campo, se marca
  como *posible corrección* y va a revisión manual.
- CA-06.3 El mismo fichero o correo procesado dos veces no produce efectos
  adicionales (idempotencia por `source_id`).
- CA-06.4 Si el cliente no manda referencia propia, se deriva una clave
  estable de (cliente, fecha, dirección de entrega, líneas) y una coincidencia
  va a revisión como *posible repetido*, nunca se carga. *(supuesto: no
  sabemos qué clientes mandan referencia, Q3)*

### RF-07 · Cola de revisión manual · M · Confirmado

Es el requisito central para la responsable: lo dudoso tiene que verse a media
mañana, no descubrirse en Alcalá. La revisan Pili, Rosa y Carmen.

- CA-07.1 Todo pedido que no pueda cargarse automáticamente queda registrado
  con su estado, motivos y datos originales.
- CA-07.2 Administración recibe una notificación por correo con el resumen de
  los pedidos pendientes de revisión en cada ciclo en que haya alguno, y en
  todo caso antes de la hora de corte configurable (propuesta: 11:00).
  *(confirmado: "a las once de la mañana")*
- CA-07.3 Un pedido revisado puede reprocesarse tras corregir el origen.
- CA-07.4 El resumen indica para cada pedido el motivo en lenguaje de oficina
  ("peso fuera de rango", "posible repetido del pedido 1234"), no códigos.

### RF-08 · Trazabilidad y auditoría · M · Supuesto

El cliente no lo pidió; lo mantenemos porque sostiene RF-06 y RF-07.

- CA-08.1 Para cada pedido se guarda: origen, `source_id`, fecha de recepción,
  resultado (creado / revisión / duplicado), identificador en Logiwin y errores.
- CA-08.2 Se puede consultar el histórico por `external_ref` y por `source_id`.

### RF-09 · Línea de comandos · S · Supuesto

- CA-09.1 `meseta-ingesta run` ejecuta un ciclo completo; `watch` lo repite
  cada `IMAP_POLL_SECONDS`.
- CA-09.2 `meseta-ingesta config` muestra la configuración efectiva con los
  secretos enmascarados.

### RF-10 · Informe de estado · C · Confirmado (reformulado)

El informe de fin de día del brief se sustituye por lo que la responsable
quiere ver: el estado del lote a la hora que importa.

- CA-10.1 A una hora configurable (propuesta: 13:30) se envía a operaciones un
  resumen: pedidos recibidos, creados, en revisión y duplicados, por cliente, y
  la lista de ficheros recibidos ese día que aún no están completos.
- CA-10.2 El resumen no incluye cifras de tiempo de oficina ni de pedidos por
  persona.

## 3. Requisitos no funcionales

| Id | Requisito | Prioridad | Estado |
| --- | --- | --- | --- |
| RNF-01 | **Idempotencia.** Reprocesar cualquier entrada no crea pedidos adicionales. | M | Confirmado |
| RNF-02 | **Secretos fuera del código.** Credenciales solo por variables de entorno o `.env` no versionado. | M | Supuesto |
| RNF-03 | **RGPD.** Los datos personales no se escriben en logs. Los ficheros y correos originales, y los pedidos con `delivery_is_consumer`, se borran a los 60 días; el resto de pedidos, a los 90. Plazos revisables por la asesoría. | M | Confirmado (1-2 meses bastan) |
| RNF-04 | **Observabilidad.** Logs estructurados con `source_id` en cada línea; métricas básicas de pedidos por resultado. | S | Supuesto |
| RNF-05 | **Rendimiento.** Un ciclo con 300 pedidos termina en menos de 5 minutos. El Excel del lunes de Agroalimentaria se termina dentro de la hora siguiente a su llegada. | S | Confirmado (objetivo), Supuesto (tamaño) |
| RNF-06 | **Resiliencia.** Una caída de Logiwin o del IMAP no pierde pedidos: se reintentan en el siguiente ciclo. | M | Supuesto |
| RNF-07 | **Mantenibilidad.** Cobertura de tests ≥ 80 % en parseo y validación; CI en verde obligatoria para fusionar. | M | Supuesto |
| RNF-08 | **Portabilidad.** Corre en Linux x86-64; sin dependencias de nube obligatorias. | M | Supuesto |
| RNF-09 | **Configuración por cliente.** El mapeo de plantillas, los remitentes autorizados y los rangos de peso son ficheros de configuración versionados. | M | Supuesto |
| RNF-10 | **Precisión antes que cobertura.** Ningún umbral de automatización justifica cargar un pedido con dudas. No se definen objetivos de porcentaje de auto-alta. | M | Confirmado |

## 4. Fuera del alcance

Ver sección 5 del [brief](01-brief.md).

## 5. Preguntas abiertas

| # | Pregunta | Para quién | Estado |
| --- | --- | --- | --- |
| Q1 | ¿La API de Logiwin permite buscar pedidos por referencia externa? | Responsable de sistemas | Abierta |
| Q2 | ¿Hay un buzón dedicado o hay que filtrar el buzón general? | Administración | **Respondida**: hay buzón de pedidos dedicado desde hace años |
| Q3 | ¿Qué plantillas Excel hay hoy, cuántos clientes usan cada una y cuáles traen referencia propia? | Administración | Abierta |
| Q4 | ¿Qué hacer con pedidos para fecha pasada: rechazar o cargar con aviso? | Operaciones | Abierta |
| Q5 | ¿Dónde se despliega: servidor interno, contenedor, cron? | Responsable de sistemas | Abierta |
| Q6 | ¿Logiwin acepta dos pedidos con la misma referencia de cliente, o los rechaza? | Javier / sistemas | Abierta (la entrevista sugiere que los acepta) |
| Q7 | ¿Existe entorno de pruebas de Logiwin, o solo producción? | Responsable de sistemas | Abierta |
| Q8 | ¿Cuántas filas trae el Excel del lunes de Agroalimentaria y a qué hora llega? | Pili, Rosa o Carmen | Abierta |
| Q9 | ¿Qué fecha de corte aplicamos al histórico del buzón al arrancar? | Administración | Abierta |
| Q10 | ¿Contra qué se valida una dirección: maestro de Logiwin, geocodificación, lista de obras del cliente? | Luis | Abierta |
| Q11 | ¿Qué rango de peso es sospechoso, por cliente o por tipo de mercancía? | Luis | Abierta |
| Q12 | ¿Las observaciones del cliente final deben pasar a Logiwin tal cual o solo lo operativo? | Operaciones | Abierta |
| Q13 | ¿Cómo distinguimos en el Excel de Cifuentes una entrega a tienda de una a domicilio particular? | Administración | Abierta |
| Q14 | Plazo de conservación y base legal de los datos de particulares (Cifuentes). ¿Valen 60 días en nuestro sistema? | Javier y la asesoría | Abierta (no es decisión de operaciones) |
| Q15 | ¿Cómo se reparten los pedidos el resto de la semana y a lo largo del día? Solo conocemos el lunes. | Administración | Abierta |

## 6. Glosario

- **Pedido**: solicitud de un cliente para transportar mercancía de A a B en una fecha.
- **Porte**: el servicio de transporte realizado y facturado; un pedido duplicado produce un porte facturado dos veces.
- **Línea**: cada bulto o grupo de bultos de un pedido.
- **Referencia externa**: identificador del pedido en el sistema del cliente.
- **Cola de revisión**: conjunto de pedidos que requieren decisión humana.
- **Logiwin**: ERP de Transportes Meseta donde viven los pedidos definitivos, la planificación y la facturación.
- **Hora de corte**: hora límite para que lo dudoso esté revisado antes de montar rutas (propuesta: 11:00 revisión, 14:00 lote completo).
