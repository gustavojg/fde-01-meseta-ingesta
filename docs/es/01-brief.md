# Brief — Ingesta de pedidos para Transportes Meseta

> Curso FDE · Encargo 01 · [English version](../en/01-brief.md)
>
> Transportes Meseta es un cliente ficticio del curso. Los datos de contexto
> marcados como *supuesto* deben confirmarse con el cliente antes de implementar.

## 1. El cliente

Transportes Meseta es una empresa de transporte de mercancía por carretera con
sede en Castilla y León. Opera una flota propia de unos 40 vehículos y trabaja
con una cartera estable de unos 60 clientes industriales y de distribución
(*supuesto*). Gestiona su operativa en un ERP sectorial que ya tiene módulo de
pedidos, planificación y facturación.

## 2. El problema

Los clientes envían sus pedidos de transporte por dos canales:

1. **Ficheros Excel.** Cada cliente usa su propia plantilla (columnas, orden,
   idioma de las cabeceras y formatos de fecha distintos). Llegan por correo
   como adjunto o se dejan en una carpeta compartida.
2. **Correo electrónico.** Texto libre o semiestructurado en el cuerpo del
   mensaje, a veces con el Excel adjunto, a veces con los datos solo en el texto.

Hoy, dos personas de administración leen cada pedido y lo teclean a mano en el
ERP. Esto produce:

- **Errores de transcripción** en direcciones, fechas y cantidades, que se
  descubren cuando el camión ya está en ruta.
- **Pedidos duplicados** cuando el cliente reenvía el mismo correo o corrige el
  Excel y lo vuelve a mandar.
- **Retrasos**: los pedidos que llegan por la tarde no entran en el ERP hasta
  la mañana siguiente y quedan fuera de la planificación del día.
- **Falta de trazabilidad**: nadie sabe si un pedido concreto se llegó a cargar,
  quién lo cargó ni desde qué correo salió.

Volumen estimado: 80-150 pedidos al día, con picos de 300 a fin de mes
(*supuesto*).

## 3. Objetivo

Construir un servicio de ingesta que lea los pedidos de ambos canales, los
normalice a un modelo único, los valide, descarte duplicados y los dé de alta
en el ERP sin intervención humana en los casos claros, enviando a una cola de
revisión los casos dudosos.

## 4. Criterios de éxito

| Métrica | Hoy | Objetivo |
| --- | --- | --- |
| Pedidos dados de alta sin intervención manual | 0 % | ≥ 80 % |
| Tiempo desde recepción hasta alta en ERP | 2-18 h | < 15 min |
| Pedidos duplicados en el ERP | varios por semana | 0 |
| Pedidos con origen trazable (fichero / correo) | 0 % | 100 % |

## 5. Alcance

**Dentro del alcance**

- Lectura de ficheros `.xlsx` desde una carpeta de entrada.
- Lectura de correos de un buzón IMAP dedicado (cuerpo y adjuntos `.xlsx`).
- Mapeo configurable por cliente de las columnas de su plantilla al modelo canónico.
- Validación de negocio y detección de duplicados.
- Alta del pedido en el ERP a través de su API.
- Cola de revisión manual con notificación a operaciones.
- Registro de auditoría de cada pedido procesado.
- Modo *dry-run* para probar sin escribir en el ERP.

**Fuera del alcance (en este encargo)**

- Interfaz web para la cola de revisión: se usará el propio ERP o el correo.
- Pedidos en PDF, imágenes o llamadas telefónicas.
- Modificación o anulación de pedidos ya cargados.
- Cambios en el ERP o en sus datos maestros (clientes, direcciones).

## 6. Interesados

| Rol | Interés |
| --- | --- |
| Dirección de operaciones | Que la planificación del día tenga todos los pedidos a primera hora. |
| Administración (2 personas) | Dejar de teclear; revisar solo las excepciones. |
| Responsable de sistemas | Que la pieza sea desplegable, observable y no toque el ERP a mano. |
| Clientes finales | Que no se les pida cambiar su forma de enviar pedidos. |

## 7. Restricciones

- El ERP expone una API REST con autenticación por clave (*supuesto*); no se
  puede escribir directamente en su base de datos.
- Las plantillas Excel de los clientes **no se pueden cambiar**.
- Los datos de pedidos contienen datos personales (contactos, direcciones) y
  están sujetos al RGPD.
- El servicio correrá en un servidor Linux del cliente, sin dependencias de
  nube obligatorias.

## 8. Riesgos y supuestos

- Los correos en texto libre son el canal con más ambigüedad: el porcentaje
  de pedidos que acaben en revisión manual puede ser alto al principio.
- La API del ERP puede no exponer todo lo necesario (por ejemplo, búsqueda de
  duplicados). Hay que confirmarlo en la primera semana.
- Las plantillas Excel cambian sin aviso; el mapeo debe ser configuración, no
  código.

## 9. Entregables del encargo

1. Este brief y los requisitos ([02-requisitos.md](02-requisitos.md)).
2. Decisiones de arquitectura registradas como ADR ([adr/](adr/README.md)).
3. Código fuente con tests y CI.
4. Guía de despliegue y operación (pendiente).
