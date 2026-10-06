# Propósito

Este script es el **tercer eslabón del pipeline** (después de la conexión
IMAP de prueba y el módulo de anonimización): conecta ambos en un único
flujo automatizado que trae correos reales desde Gmail, los anonimiza, y
los inserta en la base de datos MySQL, evitando duplicados.


## Ubicación y forma de ejecución
src/pipeline/cargar_correos.py


Se ejecuta como **módulo**, no como script suelto, parado en la raíz del
proyecto:

```bash
python3 -m src.pipeline.cargar_correos
```

Esto es necesario porque el script importa `anonymize_email` desde otro
paquete (`src.anonymization`) — ejecutarlo como archivo directo
(`python3 src/pipeline/cargar_correos.py`) rompe esa importación, porque
Python no agrega la raíz del proyecto al path de búsqueda de módulos en ese
modo.

## Variables de entorno requeridas

Del `.env` de la raíz del proyecto:

GMAIL_USER=...
GMAIL_APP_PASSWORD=...
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sicpc
DB_USER=sJorge
DB_PASSWORD=...


## Constante de configuración

```python
CANTIDAD_A_TRAER = 50
```

Controla cuántos correos (los más recientes) se procesan en cada ejecución.
Se puede subir (ej. a 150-200) para traer más volumen de una sola vez.

## Funciones

### `decode_str(s)`

Decodifica encabezados de email (`Subject`, `From`), que en el protocolo de
correo pueden venir codificados en formatos no estándar (MIME
encoded-words).

- Si el valor es `None`, devuelve cadena vacía.
- Intenta decodificar con `email.header.decode_header`.
- Si el encoding declarado en el header no existe para Python (error
  `LookupError`, caso real encontrado: `unknown-8bit`) o falla la
  decodificación (`UnicodeDecodeError`), cae a `utf-8` con
  `errors="ignore"` — descarta los caracteres problemáticos en vez de
  interrumpir el procesamiento de ese correo completo.
- Cualquier otra excepción al leer el header devuelve el valor crudo como
  string, para no perder el correo por un header atípico.

### `get_body(msg)`

Extrae el cuerpo de texto plano de un mensaje de email.

- Si el mensaje es multipart (la mayoría de los correos modernos, con
  HTML + texto plano + posibles adjuntos), recorre cada parte
  (`msg.walk()`) y devuelve la primera de tipo `text/plain`.
- Si no es multipart, devuelve el payload directo decodificado.
- Si no encuentra texto plano en ningún lado, devuelve cadena vacía (nunca
  lanza excepción por esto).

### `obtener_cuenta_correo_id(cursor)`

Resuelve a qué fila de la tabla `cuenta_correo` pertenece esta ejecución.

- Busca en la base la cuenta cuya `direccion` coincide con `GMAIL_USER`.
- Si la encuentra, devuelve su `id`.
- Si no la encuentra (por ejemplo, en un entorno nuevo sin la migración
  corrida), devuelve `1` como *fallback*, asumiendo que es la cuenta de
  migración insertada originalmente.

Esta función es la que conecta el pipeline con el diseño multiusuario: cada
correo insertado queda asociado a una cuenta configurada, no a un valor
fijo hardcodeado.

### `upsert_remitente(cursor, remitente_hash)`

Mantiene actualizada la tabla `remitente` (patrón "insertar o actualizar").

- Si el hash del remitente ya existe en la tabla, incrementa en 1 su
  contador `cantidad_correos`.
- Si no existe todavía, inserta una fila nueva con contador en 1.

Esto es lo que permite, con el tiempo, identificar remitentes recurrentes
sin nunca haber guardado su email real — solo el hash.

### `main()`

Orquesta todo el proceso, en este orden:

1. **Conexión IMAP**: se loguea en Gmail y selecciona la carpeta `inbox`.
2. **Búsqueda de UIDs**: pide todos los identificadores de correo
   (`mail.uid("search", None, "ALL")`) y se queda con los últimos
   `CANTIDAD_A_TRAER`. Se usa **UID** (identificador estable del mensaje en
   el servidor) y no el número de secuencia, porque el UID no cambia aunque
   se reordene o elimine correo de la bandeja — es la clave que después
   evita duplicados.
3. **Conexión a MySQL** y resolución de `cuenta_correo_id` (ver función de
   arriba).
4. **Por cada correo** (procesados del más viejo al más nuevo entre los
   seleccionados, por el `reversed()`):
   - Trae el mensaje completo (`RFC822`) por su UID.
   - Extrae remitente, asunto y cuerpo (limitado a 2000 caracteres, un
     límite razonable para no inflar la base con adjuntos codificados en
     texto).
   - Llama a `anonymize_email(...)` del módulo de anonimización — acá es
     donde el correo deja de tener PII antes de tocar la base.
   - Actualiza/inserta el remitente (`upsert_remitente`).
   - Inserta la fila en `correo`, guardando también `imap_uid` e
     `imap_folder` (la referencia al mensaje original, no el contenido
     real — ver `docs/gobierno-de-datos.md`, sección 5).
   - Hace `commit()` **por cada correo individualmente**, no al final del
     lote — así, si el script se corta a mitad de camino (por ejemplo, con
     `Ctrl+C`), los correos ya procesados no se pierden.
5. **Manejo de errores por fila, no por lote completo**:
   - `IntegrityError` (MySQL): significa que ya existe una fila con esa
     combinación `cuenta_correo_id` + `imap_uid` (la restricción `UNIQUE
     KEY` del esquema) — se cuenta como "duplicado", se hace `rollback()`
     de esa fila puntual, y el script continúa con el siguiente correo.
   - Cualquier otra excepción: se imprime el UID afectado y el error, se
     hace `rollback()`, se cuenta como "error", y se continúa — un correo
     problemático (ej. encoding irrecuperable) nunca frena todo el lote.
6. **Cierre de conexiones** (`cursor`, `conn`, `mail.logout()`) y resumen
   final: cantidad insertados, duplicados y errores.

## Por qué está diseñado para ser re-ejecutable

El script se puede correr múltiples veces sin preocuparse por traer los
mismos correos dos veces: la restricción `UNIQUE KEY (cuenta_correo_id,
imap_uid)` en la base hace que cualquier intento de reinsertar un correo ya
cargado falle de forma controlada (se cuenta como duplicado), en vez de
crear una fila repetida.

## Relación con el resto del proyecto

- Depende de `src/anonymization/anonymizer.py` (anonimización).
- Depende de las tablas `cuenta_correo`, `remitente` y `correo` del schema
  multiusuario (`database/migrations/002_multiusuario.sql`).
- Alimenta directamente al script de etiquetado manual
  (`src/labeling/etiquetar_correos.py`) y, en consecuencia, al notebook de
  modelado (`02_baseline.py`).
