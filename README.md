# SICPC — Sistema Inteligente de Clasificación y Priorización de Comunicaciones

Proyecto de tesis de Data Science. Sistema que ingiere correos electrónicos de forma continua, los anonimiza, los clasifica automáticamente por categoría, urgencia y sentimiento mediante modelos de Machine Learning, y presenta los resultados en un dashboard interactivo en tiempo real. La orquestación del pipeline se realiza con n8n, y una capa complementaria de IA generativa asiste en casos de baja confianza.

## Objetivo

Construir un producto de datos funcional y operativo que combine investigación (comparación de modelos de NLP), ingeniería de datos (pipeline productivo automatizado) y diseño de producto (dashboard interactivo), aplicado a un caso de uso real de priorización de comunicaciones.

## Arquitectura

```
┌─────────────┐     ┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌───────────┐
│ Cuenta de   │────▶│   n8n    │────▶│ Anonimización │────▶│  API modelo  │────▶│ PostgreSQL │
│ correo(IMAP)│     │(orquesta)│     │  (Presidio)   │     │  (FastAPI)   │     │            │
└─────────────┘     └────┬─────┘     └───────────────┘     └──────────────┘     └─────┬─────┘
                          │                                                             │
                          ▼                                                             ▼
                   ┌─────────────┐                                            ┌──────────────────┐
                   │ Agente IA   │                                            │ Dashboard         │
                   │(baja conf.) │                                            │ (Power BI/Tableau │
                   └─────────────┘                                            │  o Streamlit)     │
                                                                               └──────────────────┘
```

## Estructura del repositorio

```
sicpc-thesis/
├── data/
│   ├── raw/              # Datos crudos (NUNCA se commitea contenido real, solo estructura)
│   └── processed/        # Datos anonimizados y etiquetados, listos para entrenamiento
├── src/
│   ├── ingestion/         # Conexión IMAP y extracción de correos
│   ├── anonymization/     # Módulo de PII scrubbing (Presidio/NER) y hasheo
│   ├── modeling/          # Entrenamiento y evaluación de modelos (baseline, embeddings, transformer)
│   └── api/               # API de inferencia (FastAPI) + Dockerfile
├── notebooks/             # Exploración de datos y experimentos
├── n8n-workflows/         # Workflows de n8n exportados como JSON (versionados)
├── docs/                  # Documento de gobierno de datos, propuesta formal, experimentos, tesis
├── tests/                 # Tests unitarios (anonimización, API, etc.)
├── .env.example           # Plantilla de variables de entorno (sin credenciales reales)
├── .gitignore
└── README.md
```

## Stack tecnológico

- **Ingesta**: IMAP + contraseña de aplicación (cuentas personales gratuitas)
- **Orquestación**: n8n (self-hosted, Docker)
- **Anonimización**: Microsoft Presidio / spaCy NER
- **Modelado**: scikit-learn, Sentence-Transformers, HuggingFace Transformers
- **Servido del modelo**: FastAPI + Docker
- **Base de datos**: PostgreSQL
- **Visualización**: Power BI / Tableau o Streamlit
- **Desarrollo**: Google Antigravity (IDE agent-first)

## Estado del proyecto

🚧 En desarrollo — proyecto de tesis en curso.

| Fase | Estado |
|---|---|
| Definición y marco ético | ⬜ Pendiente |
| Ingesta de datos | ⬜ Pendiente |
| Anonimización | ⬜ Pendiente |
| Etiquetado del dataset | ⬜ Pendiente |
| Modelado | ⬜ Pendiente |
| Servido del modelo | ⬜ Pendiente |
| Orquestación n8n | ⬜ Pendiente |
| Capa de agente IA | ⬜ Pendiente |
| Dashboard | ⬜ Pendiente |
| Evaluación de impacto | ⬜ Pendiente |

## Privacidad y ética de datos

Este proyecto utiliza exclusivamente cuentas de correo personales del autor (no de terceros), procesadas bajo un esquema de anonimización previo a cualquier análisis. El manejo de datos personales se rige por la Ley 25.326 de Protección de Datos Personales (Argentina). Ver `docs/gobierno-de-datos.md` para el detalle completo.

## Autor

Jorge — Práctica Profesionalizante Data Science, Instituto Teclab
