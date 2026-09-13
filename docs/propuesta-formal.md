# Objetivo y Alcance del Proyecto

## Objetivo general

Diseñar, desarrollar y poner en funcionamiento un sistema de Machine Learning que
clasifique y priorice comunicaciones por correo electrónico de forma automática y
continua, integrando un pipeline productivo, una capa de asistencia con inteligencia
artificial generativa y un dashboard interactivo que traduzca los resultados en
decisiones operativas para el usuario final.

## Objetivos específicos

1. Diseñar un pipeline de ingesta de correos electrónicos desde una cuenta personal,
   con anonimización de datos personales previa a cualquier procesamiento.
2. Entrenar y evaluar un modelo de clasificación de urgencia sobre comunicaciones
   reales, documentando su desempeño con métricas apropiadas.
3. Productivizar el modelo mediante una API de inferencia, orquestada de forma
   automática con n8n.
4. Incorporar una capa de agente de IA generativa que asista en los casos de baja
   confianza del modelo (resumen, sugerencia de respuesta, escalamiento).
5. Construir un dashboard interactivo que permita visualizar los resultados en
   tiempo real y habilite la corrección manual de clasificaciones
   (human-in-the-loop).
6. Evaluar el impacto del sistema combinando métricas técnicas del modelo con una
   validación cualitativa de valor de negocio.

## Alcance del proyecto (MVP)

El Producto Mínimo Viable delimita la primera entrega funcional del sistema:

- Ingesta desde una única cuenta de correo (Gmail), vía IMAP con contraseña de
  aplicación.
- Anonimización básica de datos personales (PII) con Microsoft Presidio.
- Un modelo de clasificación bien evaluado, sobre una única dimensión: **urgencia**
  (alta / media / baja).
- Orquestación mediante un flujo simple en n8n (trigger → clasificación → guardado).
- Almacenamiento en una base de datos relacional con un esquema simple.
- Dashboard con una vista: lista de correos clasificados, filtrable por fecha,
  categoría y remitente.

## Extensiones fuera del alcance del MVP

Quedan documentadas como trabajo futuro, a incorporar una vez validado el MVP:

- Comparación de múltiples enfoques de modelado (TF-IDF, embeddings, transformer/LLM).
- Clasificación multi-etiqueta (categoría y sentimiento, además de urgencia).
- Capa de agente IA para casos de baja confianza.
- Alertas automáticas ante correos de alta urgencia.
- Panel de corrección manual (human-in-the-loop) en el dashboard.
- Soporte para múltiples cuentas de correo (incluyendo Outlook).
- Reentrenamiento periódico del modelo y monitoreo de drift.

## Fuera de alcance del proyecto

- El sistema no constituye un producto comercial en producción con usuarios
  externos reales; su alcance es académico, en el marco de una tesis de Data
  Science.
- No se procesan datos de correo de terceros sin su consentimiento explícito.
- No se garantiza disponibilidad ni soporte del sistema fuera del período de
  desarrollo de la tesis.
EOF