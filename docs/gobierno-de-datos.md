cat > docs/gobierno-de-datos.md << 'EOF'
# Gobierno de Datos

## 1. Datos procesados

El sistema procesa correos electrónicos provenientes de cuentas de correo
configuradas por sus respectivos usuarios (tabla `cuenta_correo`), incluyendo:
asunto, cuerpo del mensaje, remitente, destinatario, fecha/hora y metadata
asociada (adjuntos, hilo de conversación). En la versión MVP de tesis, la
única cuenta configurada es personal del autor; el esquema de datos ya
contempla múltiples cuentas y usuarios para la evolución comercial del
proyecto.

## 2. Base legal y justificación

El tratamiento de estos datos se enmarca en la **Ley 25.326 de Protección de
Datos Personales** (Argentina). Para el MVP de tesis, el autor es titular
exclusivo de los datos procesados: no se utilizan correos de terceros sin su
consentimiento explícito. El tratamiento tiene fines exclusivamente
académicos. Para la evolución comercial (multiusuario), cada organización que
adopte el sistema será responsable del tratamiento de sus propios datos,
bajo un esquema de cuentas y usuarios independientes entre sí.

## 3. Política de anonimización

- **Qué se anonimiza**: nombres propios, direcciones de correo electrónico,
  números de teléfono y direcciones físicas mencionadas en el cuerpo del
  mensaje.
- **Herramienta**: Microsoft Presidio, sobre motor de NER en español
  (spaCy, modelo `es_core_news_lg`). Ver `docs/anonimizacion.md` para el
  detalle técnico y las limitaciones conocidas del modelo.
- **Momento del pipeline**: la anonimización ocurre inmediatamente después de
  la ingesta y antes de que el dato llegue al modelo de clasificación o a
  cualquier almacenamiento persistente ("anonimización en el punto de
  ingesta").
- **Identificadores de remitente**: se reemplazan por un hash irreversible
  (SHA-256 con salt), no se almacenan en texto plano. Permite detectar
  remitentes recurrentes sin exponer su identidad real.
- **El modelo de Machine Learning nunca opera sobre datos sin anonimizar**:
  el entrenamiento y la inferencia se realizan exclusivamente sobre texto ya
  anonimizado (`asunto_anonimizado`, `cuerpo_anonimizado`). El cifrado
  reversible descrito en la sección 5 es un mecanismo operativo, ajeno por
  completo al pipeline de modelado.

## 4. Política de retención

- **Correos crudos** (sin anonimizar): se procesan en memoria durante la
  ingesta y no se almacenan de forma persistente en texto plano en ningún
  momento — ni siquiera temporalmente. El contenido original solo se
  recupera on-demand cuando es necesario (ver sección 5).
- **Versión anonimizada**: se conserva en la base de datos del proyecto
  mientras dure el desarrollo de la tesis (o, en la versión comercial,
  mientras la cuenta del cliente esté activa).
- **Referencia al mensaje original**: se conserva únicamente el identificador
  técnico del mensaje en el servidor de correo (`imap_uid`, `imap_folder`),
  que no constituye en sí mismo un dato personal.

## 5. Acceso al contenido original del correo

Un correo anonimizado no permite, por diseño, que un operador responda al
remitente real. Para resolver esta necesidad operativa sin comprometer el
principio de minimización de datos, se adoptó el siguiente esquema:

- **No se almacena el contenido original** (ni en texto plano ni cifrado) en
  la base de datos del proyecto.
- Cuando un usuario autorizado necesita ver o responder un correo, el sistema
  se conecta on-demand al servidor de correo de la cuenta correspondiente
  (usando las credenciales cifradas de `cuenta_correo`, ver sección 6),
  recupera el mensaje puntual por su `imap_uid`, lo muestra, y **no lo
  vuelve a persistir** en ningún almacenamiento propio.
- El acceso al contenido original está sujeto al esquema de roles y
  asignación descrito en la sección 7, y cada acceso queda registrado en la
  tabla de auditoría `acceso_contenido_original` (correo, usuario, fecha).

## 6. Cifrado de credenciales de cuentas de correo

- Las credenciales de cada cuenta configurada (`cuenta_correo.
  credenciales_cifradas`) se almacenan cifradas mediante `cryptography.
  fernet`, nunca en texto plano.
- La clave maestra de cifrado se gestiona exclusivamente mediante variable de
  entorno del servidor, nunca en el repositorio ni en la base de datos.
- El descifrado ocurre únicamente en memoria, en el momento puntual en que el
  sistema necesita conectarse a esa cuenta de correo (para ingesta o para
  recuperar un mensaje on-demand, sección 5).

## 7. Roles y control de acceso

El sistema define tres roles, aplicables tanto a la operación diaria como al
acceso a datos sensibles:

| Acción | Admin | Supervisor | Operador |
|---|---|---|---|
| Configurar cuentas de correo | Sí | No | No |
| Ver correos de todas las cuentas | Sí | Sí (de su equipo) | No |
| Ver correos asignados a él | Sí | Sí | Sí |
| Derivar un correo a otro usuario | Sí | Sí | Sí (solo los propios) |
| Corregir clasificación (human-in-the-loop) | Sí | Sí | Sí |
| Ver contenido original del correo | Sí | Sí (de su equipo) | Sí (solo si está asignado a él) |
| Gestionar usuarios y roles | Sí | No | No |

Ver el contenido original de un correo es una acción sensible que depende
del rol **y** de la asignación vigente (`correo.asignado_a`), no del rol por
sí solo: un operador no puede acceder al contenido real de un correo que no
le fue asignado, aunque otro operador con el mismo rol sí pueda acceder al
suyo.

- El autor del proyecto (o, en la versión comercial, el administrador de
  cada organización) es responsable de la asignación de roles.
- Las credenciales de acceso al sistema (login) y a la base de datos se
  gestionan mediante variables de entorno (`.env`), excluidas del control de
  versiones.

## 8. Auditoría de accesos

Cada vez que un usuario accede al contenido original de un correo (sección
5), se registra en la tabla `acceso_contenido_original`: qué correo, qué
usuario, y en qué momento. Este registro permite reconstruir en cualquier
momento quién accedió a qué información sensible, sin necesidad de almacenar
el dato sensible en sí.

## 9. Seguridad técnica

- **En tránsito**: la conexión IMAP se realiza sobre SSL/TLS (puerto 993).
- **En reposo**: se evalúa cifrado a nivel de volumen de la base de datos
  (MySQL).
- **Credenciales**: nunca se versionan en el repositorio (excluidas vía
  `.gitignore`); se gestionan mediante contraseñas de aplicación específicas
  para el proyecto y, en la tabla `cuenta_correo`, cifradas con clave
  maestra (sección 6).

## 10. Datos de origen externo (datasets públicos)

Para robustecer el entrenamiento del modelo de clasificación, se incorporan
datasets públicos (ej. de Kaggle) con licencias abiertas (CC0 o
equivalente), citados en la bibliografía de la tesis. Antes de su uso se
verifica que:

- No contengan datos personales reales sin anonimizar. Si un dataset incluye
  nombres o direcciones de correo reales de personas (se detectó este caso en
  al menos un dataset evaluado), se procesa con el mismo módulo de
  anonimización (`anonymizer.py`) antes de utilizarlo, aplicando el mismo
  criterio que a los datos propios.
- Su licencia permita el uso académico (y, de corresponder, comercial).
- Su distribución de clases (idioma, prioridad) sea revisada para evitar
  sesgos no deseados en el modelo (ver notebook de EDA correspondiente).

## 11. Alcance y limitaciones declaradas

- Este es un proyecto de alcance **académico** en su versión de tesis, con
  una evolución comercial planificada (multiusuario/configurable) cuyo
  diseño de datos ya se contempla en el esquema actual, aunque su
  implementación completa (interfaz de configuración, lógica de permisos en
  aplicación) exceda el alcance del MVP.
- Al finalizar la tesis, se evaluará el borrado definitivo de los datos
  anonimizados o su anonimización adicional en caso de que algún material se
  utilice como ejemplo en la documentación pública del proyecto.
- El sistema no garantiza disponibilidad ni soporte fuera del período de
  desarrollo de la tesis.

## 12. Limitaciones conocidas de la anonimización (MVP)

El modelo de NER en español (es_core_news_lg) presenta imprecisiones esperables:
- Direcciones compuestas (ej. "Av. Corrientes 1234") pueden anonimizarse
  parcialmente, dejando números sueltos sin enmascarar.
- Palabras de cierre comunes (ej. "Saludos") pueden generar falsos positivos,
  siendo marcadas incorrectamente como entidades de tipo LOCATION.

Estas limitaciones quedan documentadas como riesgo conocido y como oportunidad
de mejora (reglas custom con regex, o modelo de NER mas especializado) para
una version posterior del sistema.
