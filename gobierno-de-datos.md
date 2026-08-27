# Gobierno de Datos

## 1. Datos procesados

El sistema procesa correos electrónicos provenientes de una cuenta personal de
Gmail, incluyendo: asunto, cuerpo del mensaje, remitente, destinatario, fecha/hora
y metadata asociada (adjuntos, hilo de conversación). El volumen y período
utilizados como dataset inicial se documentan en el capítulo de preparación de
datos de la tesis.

## 2. Base legal y justificación

El tratamiento de estos datos se enmarca en la **Ley 25.326 de Protección de
Datos Personales** (Argentina). El autor es titular exclusivo de los datos
procesados: no se utilizan correos de terceros sin su consentimiento explícito.
El tratamiento tiene fines exclusivamente académicos, en el marco de una tesis
de Data Science.

## 3. Política de anonimización

- **Qué se anonimiza**: nombres propios, direcciones de correo electrónico,
  números de teléfono y direcciones físicas mencionadas en el cuerpo del mensaje.
- **Herramienta**: Microsoft Presidio, sobre motor de NER (spaCy).
- **Momento del pipeline**: la anonimización ocurre inmediatamente después de la
  ingesta y antes de que el dato llegue al modelo de clasificación o a cualquier
  almacenamiento persistente ("anonimización en el punto de ingesta").
- **Identificadores de remitente/destinatario**: se reemplazan por un hash
  irreversible, no se eliminan por completo, para permitir detectar patrones
  (ej. remitente recurrente) sin exponer la identidad real.

## 4. Política de retención

- **Correos crudos** (sin anonimizar): se procesan en memoria y se descartan
  dentro de las 24-48 horas posteriores a su ingesta. No se almacenan de forma
  persistente en texto plano.
- **Versión anonimizada**: se conserva en la base de datos del proyecto mientras
  dure el desarrollo de la tesis.
- **Mapeo real → anonimizado** (si se conserva para trazabilidad interna): se
  guarda cifrado, en un almacenamiento separado del resto del pipeline.

## 5. Control de acceso

- El autor del proyecto es el único administrador con acceso a los datos crudos
  y al mapeo real → anonimizado.
- El tutor y, eventualmente, el tribunal de tesis acceden únicamente al
  dashboard con datos ya anonimizados — nunca a los correos originales.
- Las credenciales de acceso (cuenta de correo, base de datos, API keys) se
  gestionan mediante variables de entorno (`.env`), excluidas del control de
  versiones.

## 6. Seguridad técnica

- **En tránsito**: la conexión IMAP se realiza sobre SSL/TLS (puerto 993).
- **En reposo**: se evalúa cifrado del volumen de la base de datos según el
  motor final elegido (PostgreSQL o MySQL).
- **Credenciales**: nunca se versionan en el repositorio (excluidas vía
  `.gitignore`); se gestionan mediante contraseñas de aplicación específicas
  para el proyecto, no la contraseña principal de la cuenta.

## 7. Alcance y limitaciones declaradas

- Este es un proyecto de alcance **académico**, no un producto comercial en
  producción con usuarios externos.
- Al finalizar la tesis, se evaluará el borrado definitivo de los datos
  anonimizados o su anonimización adicional en caso de que algún material se
  utilice como ejemplo en la documentación pública del proyecto.
- El sistema no garantiza disponibilidad ni soporte fuera del período de
  desarrollo de la tesis.
EOF