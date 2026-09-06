# Módulo de Anonimización — `anonymizer.py`

## Propósito

Este módulo implementa la capa de anonimización de datos personales (PII) del
proyecto SICPC. Es el paso obligatorio entre la ingesta de un correo (vía
IMAP) y cualquier uso posterior de ese dato — clasificación, almacenamiento o
visualización — según lo establecido en `docs/gobierno-de-datos.md`.

Ningún correo debe llegar al modelo de clasificación ni a la base de datos
sin pasar antes por este módulo.

## Ubicación

src/anonymization/anonymizer.py


## Librerías utilizadas

| Librería | Rol en el módulo |
|---|---|
| [`presidio-analyzer`](https://microsoft.github.io/presidio/) | Motor de detección de entidades PII (nombres, emails, teléfonos, direcciones) sobre texto libre. |
| [`presidio-anonymizer`](https://microsoft.github.io/presidio/) | Aplica la transformación de enmascarado sobre las entidades detectadas. |
| [`spaCy`](https://spacy.io/) | Motor de NLP subyacente (NER). Se usa el modelo `es_core_news_lg`, en español. |
| `hashlib` (estándar de Python) | Genera el hash irreversible (SHA-256) de identificadores como el email del remitente. |
| `python-dotenv` | Carga las variables de entorno del `.env` (en este módulo, `HASH_SALT`). |

### Por qué un modelo de NER en español

Presidio, por defecto, viene configurado para inglés. Como los correos de
este proyecto están mayormente en español, el módulo instancia explícitamente
el motor de NLP con `es_core_news_lg` — sin este paso, la detección de
nombres y lugares sería muy imprecisa.

## Funcionamiento interno

### 1. Inicialización (una sola vez, a nivel de módulo)

- `NlpEngineProvider`: arma el motor de NLP en español.
- `AnalyzerEngine`: detecta las entidades PII.
- `AnonymizerEngine`: aplica el reemplazo/enmascarado.

### 2. Entidades detectadas

| Entidad Presidio | Reemplazo aplicado |
|---|---|
| `PERSON` | `[PERSONA]` |
| `EMAIL_ADDRESS` | `[EMAIL]` |
| `PHONE_NUMBER` | `[TELEFONO]` |
| `LOCATION` | `[DIRECCION]` |

### 3. Funciones principales

#### `anonymize_text(texto: str) -> str`
Recibe un texto libre (asunto o cuerpo) y devuelve la versión con las
entidades PII reemplazadas. Maneja texto vacío o `None` sin lanzar error.

#### `hash_identifier(identificador: str) -> str`
Genera un hash SHA-256 **con salt** de un identificador (ej. email del
remitente). El salt (`HASH_SALT` en el `.env`) evita revertir el hash por
diccionario/rainbow table. El mismo identificador siempre produce el mismo
hash, lo que permite detectar remitentes recurrentes sin conocer su
identidad real.

#### `anonymize_email(remitente, asunto, cuerpo) -> dict`
Punto de entrada principal. Devuelve:

```python
{
    "remitente_hash": "...",
    "asunto_anonimizado": "...",
    "cuerpo_anonimizado": "...",
}
```

## Variables de entorno requeridas

En el `.env` de la **raíz del proyecto** (no en la carpeta del módulo):
HASH_SALT=<valor generado con: openssl rand -hex 16>


> Este módulo no tiene `.env` propio: al ser código Python de la aplicación
> (no un servicio independiente como n8n o MySQL), comparte el mismo `.env`
> raíz que el resto de los scripts (`GMAIL_USER`, `GMAIL_APP_PASSWORD`, etc.).

## Limitaciones conocidas

Validado sobre correos reales, se detectaron dos imprecisiones esperables:

- **Direcciones compuestas** ("Av. Corrientes 1234"): puede anonimizarse solo
  parte de la dirección, dejando el número suelto.
- **Falsos positivos**: palabras comunes como "Saludos" pueden marcarse
  incorrectamente como `LOCATION`.

Quedan documentadas como riesgo conocido y oportunidad de mejora (reglas
custom con regex, o un modelo de NER más especializado) para una versión
posterior.

## Instalación de dependencias

```bash
pip install presidio-analyzer presidio-anonymizer spacy
python -m spacy download es_core_news_lg
```

## Pruebas

- **Unitarias** (`tests/test_anonymizer.py`): casos controlados —
  enmascarado de nombre/teléfono/email, consistencia del hash, texto vacío.
- **Manual sobre correos reales**
  (`src/anonymization/test_sobre_correos_reales.py`): trae correos reales vía
  IMAP y muestra el resultado antes/después, para revisión humana.

```bash
pytest tests/test_anonymizer.py -v
python src/anonymization/test_sobre_correos_reales.py
```

## Relación con el pipeline

Ingesta (IMAP) → anonymizer.py → Modelo de clasificación → Base de datos (MySQL) → Dashboard


Segundo eslabón del pipeline, inmediatamente después de la ingesta,
consistente con el principio de "anonimización en el punto de ingesta"
definido en el gobierno de datos.
DOCEOF