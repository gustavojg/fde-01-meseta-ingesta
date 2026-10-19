# Brief — Ingesta de pedidos para Transportes Meseta

> Curso FDE · Encargo 01 · [English version](../en/01-brief.md)
>
> Transportes Meseta es un cliente ficticio del curso. Los datos de contexto
> marcados como *supuesto* deben confirmarse con el cliente antes de implementar.
> Los marcados como *confirmado* salen de la entrevista con la responsable de
> operaciones (octubre de 2026); ver [03-proceso.md](03-proceso.md).

## 1. El cliente

Transportes Meseta es una empresa de transporte de mercancía por carretera con
sede en Castilla y León. Opera una flota propia de unos 40 vehículos y trabaja
con una cartera estable de unos 60 clientes industriales y de distribución
(*supuesto*). Gestiona su operativa en **Logiwin**, un ERP sectorial con módulo
de pedidos, planificación y facturación (*confirmado*). Logiwin guarda todos los
pedidos desde 2017 porque sirven para facturar y para atender reclamaciones.

Los clientes con más volumen son cuatro (*confirmado*):

| Cliente | Qué envía | A quién entrega |
| --- | --- | --- |
| Agroalimentaria | Un Excel grande el lunes a primera hora | Almacenes y supermercados |
| Logística Sanz | Excel | Almacenes y supermercados |
| Cerámicas | Excel | Obras y almacenes de construcción |
| Muebles Cifuentes | Excel y correo | Tiendas y, a veces, domicilio del cliente final |

## 2. El problema

Los clientes envían sus pedidos de transporte por dos canales:

1. **Ficheros Excel.** Cada cliente usa su propia plantilla (columnas, orden,
   idioma de las cabeceras y formatos de fecha distintos). Llegan por correo
   como adjunto o se dejan en una carpeta compartida.
2. **Correo electrónico.** Texto libre o semiestructurado en el cuerpo del
   mensaje, a veces con el Excel adjunto, a veces con los datos solo en el texto.
   Existe un buzón dedicado de pedidos desde hace años (*confirmado*).

Hoy, tres personas de administración (Pili, Rosa y Carmen) leen cada pedido y
lo teclean a mano en Logiwin, incluidas las observaciones en un campo de texto
libre (*confirmado*). Esto produce:

- **Errores de transcripción** en direcciones, pesos y cantidades, que se
  descubren cuando el camión ya está en ruta. Hoy unos 4 de cada 100 pedidos
  tienen algún error: dirección, peso o repetido (*confirmado*).
- **Pedidos duplicados** cuando el cliente reenvía el mismo correo o corrige el
  Excel y lo vuelve a mandar. Logiwin los acepta y llegan a facturación: a fin
  de mes el cliente llama por un porte facturado dos veces (*confirmado*).
- **Retrasos**: el lunes a las 14:00 el Excel de Agroalimentaria todavía no
  está metido entero y a las 16:00 Luis monta las rutas del martes con lo que
  hay (*confirmado*). Los pedidos de la tarde entran a la mañana siguiente.
- **Falta de trazabilidad**: nadie sabe si un pedido concreto se llegó a cargar,
  quién lo cargó ni desde qué correo salió.

Volumen estimado: 80-150 pedidos al día, con picos de 300 a fin de mes
(*supuesto*). El pico semanal real es el lunes por la mañana (*confirmado*).

## 3. Objetivo

Construir un servicio de ingesta que lea los pedidos de ambos canales, los
normalice a un modelo único, los valide, descarte duplicados y los dé de alta
en Logiwin sin intervención humana en los casos claros, enviando a una cola de
revisión los casos dudosos **antes de que salga el camión**.

En palabras de la responsable de operaciones: que sea el programa el que no se
atreva, no que lo meta mal con toda la cara. La precisión importa más que el
porcentaje de automatización.

## 4. Criterios de éxito

Plazo: un mes desde la puesta en marcha. Fuente: entrevista con la responsable
de operaciones, salvo donde se indica.

| Métrica | Hoy | Objetivo |
| --- | --- | --- |
| Hito del lunes: Excel de Agroalimentaria entero en Logiwin | a las 16:00 falta parte | a las 14:00 está completo y Luis monta rutas con todo |
| Tiempo desde recepción hasta alta o cola de revisión | 2-18 h | ≤ 1 h habitual, 2 h como máximo |
| Pedidos con error detectado tras la carga (dirección, peso, repetido) | 4 de cada 100 | ≤ 1 de cada 100 |
| Pedidos dudosos marcados antes de que salga el camión | 0 % | 100 % de los que el sistema no tenga claros |
| Portes facturados dos veces a fin de mes | varios al mes | 0 |
| Pedidos con origen trazable (fichero / correo) | 0 % | 100 % (*supuesto*, no lo pidió el cliente) |

Se retira el criterio inicial de "≥ 80 % de pedidos dados de alta sin
intervención manual": empuja a cargar con dudas, que es justo lo que el cliente
no quiere.

**No se mide ni se publica el ahorro en horas de oficina.** La responsable lo
pidió expresamente: la cifra se convertiría en un argumento para reducir
plantilla y las tres personas de administración hacen también todo lo demás de
la oficina. Las métricas son de camiones y clientes.

## 5. Alcance

**Dentro del alcance**

- Lectura de ficheros `.xlsx` desde una carpeta de entrada.
- Lectura de correos de un buzón IMAP dedicado (cuerpo y adjuntos `.xlsx`).
- Mapeo configurable por cliente de las columnas de su plantilla al modelo canónico.
- Validación de negocio (dirección, peso, fecha, cantidad) y detección de duplicados.
- Alta del pedido en Logiwin a través de su API.
- Cola de revisión manual con notificación a administración antes de media mañana.
- Registro de auditoría de cada pedido procesado.
- Modo *dry-run* para probar sin escribir en Logiwin.

**Fuera del alcance (en este encargo)**

- Interfaz web para la cola de revisión: se usará el propio Logiwin o el correo.
- Pedidos en PDF, imágenes o llamadas telefónicas.
- Modificación o anulación de pedidos ya cargados.
- Cambios en Logiwin o en sus datos maestros (clientes, direcciones).
- Limpieza del histórico de datos personales que ya existe en el buzón, el
  servidor de ficheros y Logiwin. Es un asunto para gerencia y la asesoría.

## 6. Interesados

| Rol | Quién | Interés |
| --- | --- | --- |
| Responsable de operaciones | (entrevistada) | Que el lunes a las 14:00 esté todo metido y que lo dudoso se vea antes de salir el camión. |
| Planificación de rutas | Luis | Montar las rutas del día siguiente con todos los pedidos y sin direcciones ni pesos erróneos. |
| Administración (3 personas) | Pili, Rosa y Carmen | Dejar de teclear; revisar lo raro y llamar a los clientes. Que el proyecto no se use para recortar plantilla. |
| Gerencia | Javier | Costes y nóminas; conservación de facturas por Hacienda. Interlocutor con la asesoría. |
| Asesoría externa | (RGPD) | Plazos de conservación y base legal de los datos de particulares. |
| Responsable de sistemas | (por identificar) | Que la pieza sea desplegable, observable y no toque Logiwin a mano. |
| Clientes finales | Agroalimentaria, Sanz, Cerámicas, Cifuentes | Que no se les pida cambiar su forma de enviar pedidos. |

## 7. Restricciones

- Logiwin expone una API REST con autenticación por clave (*supuesto*); no se
  puede escribir directamente en su base de datos.
- Las plantillas Excel de los clientes **no se pueden cambiar**.
- Los datos de pedidos contienen datos personales y están sujetos al RGPD. En
  los clientes B2B son nombre y teléfono de un encargado o jefe de obra. En
  Muebles Cifuentes son datos de particulares: nombre y apellidos, dirección,
  móvil y observaciones como horarios de trabajo o "tercero sin ascensor"
  (*confirmado*).
- Para la operación bastan uno o dos meses de pedidos en nuestro sistema. La
  facturación y las reclamaciones viven en Logiwin, no hace falta duplicarlas
  (*confirmado*).
- El servicio correrá en un servidor Linux del cliente, sin dependencias de
  nube obligatorias.

## 8. Riesgos y supuestos

Del brief inicial:

- Los correos en texto libre son el canal con más ambigüedad: el porcentaje
  de pedidos que acaben en revisión manual puede ser alto al principio.
- La API de Logiwin puede no exponer todo lo necesario (por ejemplo, búsqueda
  de duplicados). Hay que confirmarlo en la primera semana.
- Las plantillas Excel cambian sin aviso; el mapeo debe ser configuración, no
  código.

Detectados en la entrevista:

- **Logiwin no rechaza duplicados.** Hoy los repetidos entran y se facturan.
  La deduplicación tiene que ser nuestra y no puede depender del ERP.
- **No se sabe si existe entorno de pruebas de Logiwin.** Sin él, el *dry-run*
  es la única red y la primera alta real se hace en producción.
- **Datos de particulares en el flujo.** Guardar el correo o el Excel original
  para auditoría replica esos datos. La retención y la exclusión de logs
  (RNF-03) tienen que aplicarse también a los originales.
- **Nadie es dueño del RGPD.** Hoy no se borra nada: buzón, carpetas y Logiwin
  acumulan años. La responsable lo delega a gerencia y la asesoría. Nuestro
  sistema puede cumplir su parte, pero el problema de fondo no es nuestro.
- **El buzón tiene años de histórico.** Al conectar el IMAP hay que fijar una
  fecha de corte o se reprocesan miles de correos el primer día.
- **El pico es un fichero grande un lunes.** El objetivo de latencia se mide
  sobre ese lote, no sobre un goteo de correos.
- **Riesgo de adopción.** Si el proyecto se presenta como ahorro de personal,
  administración lo verá como amenaza. Las métricas y la comunicación deben ser
  operativas.
- **Observaciones libres.** El campo de observaciones de Logiwin es un canal de
  datos sin control. No debemos volcar ahí el cuerpo del correo tal cual.

## 9. Entregables del encargo

1. Este brief, los requisitos ([02-requisitos.md](02-requisitos.md)) y el
   proceso as-is / to-be ([03-proceso.md](03-proceso.md)).
2. Decisiones de arquitectura registradas como ADR ([adr/](adr/README.md)).
3. Documento de traspaso ([04-handoff.md](04-handoff.md)).
4. Código fuente con tests y CI.
5. Guía de despliegue y operación (pendiente).
