# Requisitos — Ingesta de pedidos para Transportes Meseta

> Curso FDE · Encargo 01 · [English version](../en/02-requirements.md)
>
> Los identificadores (RF-xx, RNF-xx) son estables: se citan en commits, PRs y ADRs.
> Prioridad: **M** (debe), **S** (debería), **C** (podría).

## 1. Modelo canónico de pedido

Todas las fuentes se traducen a un único modelo `Order`:

| Campo | Tipo | Obligatorio | Notas |
| --- | --- | --- | --- |
| `customer_code` | texto | sí | Código de cliente tal y como existe en el ERP. |
| `external_ref` | texto | sí | Referencia del pedido en el sistema del cliente. |
| `pickup_address` | texto | sí | Dirección de recogida. |
| `delivery_address` | texto | sí | Dirección de entrega. |
| `requested_date` | fecha | sí | Fecha solicitada de recogida. |
| `lines[]` | lista | sí (≥ 1) | Descripción, cantidad, peso (kg) y volumen (m³) opcionales. |
| `notes` | texto | no | Observaciones libres. |
| `source` | enum | sí | `excel` o `email`. |
| `source_id` | texto | sí | Ruta del fichero o `Message-ID` del correo. |

La clave de duplicado es `(customer_code, external_ref)`.

## 2. Requisitos funcionales

### RF-01 · Ingesta desde Excel · M

El sistema lee los ficheros `.xlsx` depositados en la carpeta de entrada y
extrae un pedido por fila (o por hoja, según configuración del cliente).

- CA-01.1 Un fichero con N filas válidas produce N pedidos.
- CA-01.2 El mapeo columna → campo canónico se define por cliente en un fichero
  de configuración, sin tocar código.
- CA-01.3 Un fichero procesado se mueve a `processed/`; uno ilegible, a
  `rejected/` con un informe del motivo.
- CA-01.4 Se aceptan fechas en los formatos `dd/mm/aaaa`, `aaaa-mm-dd` y fecha
  nativa de Excel.

### RF-02 · Ingesta desde correo electrónico · M

El sistema lee un buzón IMAP dedicado y procesa cada mensaje no leído.

- CA-02.1 Si el correo lleva un `.xlsx` adjunto, se procesa igual que en RF-01.
- CA-02.2 Si el cuerpo contiene pedidos en formato semiestructurado
  (`campo: valor` por línea), se extraen con las mismas reglas de validación.
- CA-02.3 El remitente se usa para identificar al cliente mediante una tabla de
  correos autorizados; un remitente desconocido va a revisión manual.
- CA-02.4 Cada mensaje se procesa una sola vez (se marca como leído o se mueve
  a una carpeta `procesados`).

### RF-03 · Normalización · M

Todo pedido se convierte al modelo canónico antes de cualquier otra operación.

- CA-03.1 Direcciones y referencias se recortan de espacios y se normalizan
  mayúsculas según regla configurable.
- CA-03.2 Un pedido que no pueda mapearse a todos los campos obligatorios se
  rechaza con una lista de campos faltantes.

### RF-04 · Validación de negocio · M

- CA-04.1 `customer_code` debe existir en el ERP (consulta cacheada).
- CA-04.2 `requested_date` no puede ser anterior a hoy ni posterior a 90 días.
- CA-04.3 Cada línea debe tener cantidad > 0.
- CA-04.4 Un pedido inválido no se descarta: va a la cola de revisión con los
  motivos.

### RF-05 · Alta en el ERP · M

- CA-05.1 Un pedido válido y no duplicado se crea en el ERP mediante su API y
  se guarda el identificador devuelto.
- CA-05.2 Si la API falla de forma transitoria, se reintenta con espera
  exponencial (máximo configurable); si falla de forma definitiva, va a revisión.
- CA-05.3 En modo `DRY_RUN=true` no se escribe nada en el ERP y se registra lo
  que se habría creado.

### RF-06 · Deduplicación · M

- CA-06.1 Un pedido cuya clave `(customer_code, external_ref)` ya se haya
  cargado no se vuelve a crear.
- CA-06.2 Si el pedido duplicado difiere del original en algún campo, se marca
  como *posible corrección* y va a revisión manual.
- CA-06.3 El mismo fichero o correo procesado dos veces no produce efectos
  adicionales (idempotencia por `source_id`).

### RF-07 · Cola de revisión manual · M

- CA-07.1 Todo pedido que no pueda cargarse automáticamente queda registrado
  con su estado, motivos y datos originales.
- CA-07.2 Operaciones recibe una notificación por correo con el resumen de los
  pedidos pendientes de revisión.
- CA-07.3 Un pedido revisado puede reprocesarse tras corregir el origen.

### RF-08 · Trazabilidad y auditoría · M

- CA-08.1 Para cada pedido se guarda: origen, `source_id`, fecha de recepción,
  resultado (creado / revisión / duplicado), identificador en el ERP y errores.
- CA-08.2 Se puede consultar el histórico por `external_ref` y por `source_id`.

### RF-09 · Línea de comandos · S

- CA-09.1 `meseta-ingesta run` ejecuta un ciclo completo; `watch` lo repite
  cada `IMAP_POLL_SECONDS`.
- CA-09.2 `meseta-ingesta config` muestra la configuración efectiva con los
  secretos enmascarados.

### RF-10 · Informe diario · C

- CA-10.1 Al final del día se envía un resumen: pedidos recibidos, creados,
  en revisión y duplicados, por cliente.

## 3. Requisitos no funcionales

| Id | Requisito | Prioridad |
| --- | --- | --- |
| RNF-01 | **Idempotencia.** Reprocesar cualquier entrada no crea pedidos adicionales. | M |
| RNF-02 | **Secretos fuera del código.** Credenciales solo por variables de entorno o `.env` no versionado. | M |
| RNF-03 | **RGPD.** Los datos personales no se escriben en logs; los ficheros originales se conservan como máximo 90 días. | M |
| RNF-04 | **Observabilidad.** Logs estructurados con `source_id` en cada línea; métricas básicas de pedidos por resultado. | S |
| RNF-05 | **Rendimiento.** Un ciclo con 300 pedidos termina en menos de 5 minutos. | S |
| RNF-06 | **Resiliencia.** Una caída del ERP o del IMAP no pierde pedidos: se reintentan en el siguiente ciclo. | M |
| RNF-07 | **Mantenibilidad.** Cobertura de tests ≥ 80 % en parseo y validación; CI en verde obligatoria para fusionar. | M |
| RNF-08 | **Portabilidad.** Corre en Linux x86-64 con Python 3.12+; sin dependencias de nube obligatorias. | M |
| RNF-09 | **Configuración por cliente.** El mapeo de plantillas y los remitentes autorizados son ficheros de configuración versionados. | M |

## 4. Fuera del alcance

Ver sección 5 del [brief](01-brief.md).

## 5. Preguntas abiertas

| # | Pregunta | Para quién | Estado |
| --- | --- | --- | --- |
| Q1 | ¿La API del ERP permite buscar pedidos por referencia externa? | Responsable de sistemas | Abierta |
| Q2 | ¿Hay un buzón dedicado o hay que filtrar el buzón general? | Administración | Abierta |
| Q3 | ¿Qué plantillas Excel hay hoy y cuántos clientes usan cada una? | Administración | Abierta |
| Q4 | ¿Qué hacer con pedidos para fecha pasada: rechazar o cargar con aviso? | Operaciones | Abierta |
| Q5 | ¿Dónde se despliega: servidor interno, contenedor, cron? | Responsable de sistemas | Abierta |

## 6. Glosario

- **Pedido**: solicitud de un cliente para transportar mercancía de A a B en una fecha.
- **Línea**: cada bulto o grupo de bultos de un pedido.
- **Referencia externa**: identificador del pedido en el sistema del cliente.
- **Cola de revisión**: conjunto de pedidos que requieren decisión humana.
- **ERP**: sistema de gestión de Transportes Meseta donde viven los pedidos definitivos.
