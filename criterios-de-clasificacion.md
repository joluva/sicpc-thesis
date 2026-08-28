# Criterios de Clasificación — Urgencia

## Propósito

Este documento define, de forma explícita y verificable, qué hace que un correo
se clasifique como urgencia **alta**, **media** o **baja**. Sirve como guía de
referencia para el etiquetado manual del dataset de entrenamiento y como
criterio de validación de las predicciones del modelo.

## Definición de las categorías

### Urgencia alta

Correos que requieren acción o respuesta en las próximas horas, cuya demora
genera un impacto negativo directo (pérdida de negocio, incumplimiento,
insatisfacción de un cliente).

**Señales típicas:**
- Palabras/expresiones que indican plazo inminente ("hoy", "urgente", "antes
  de", "vence")
- Reclamos o problemas reportados por un cliente
- Solicitudes con fecha límite explícita dentro de las 24-48 hs
- Remitente identificado como cliente activo o prioritario
- Tono que expresa frustración, enojo o insistencia (múltiples seguimientos
  sobre el mismo tema)

**Ejemplos:**
- "Necesito la propuesta antes de las 15hs de hoy, tenemos reunión con el
  directorio."
- "Llevo 3 días sin respuesta y el sistema sigue caído."
- "Última oportunidad: si no confirmamos hoy, perdemos el contrato."

### Urgencia media

Correos que requieren respuesta o acción, pero sin una fecha límite inmediata;
pueden esperar entre 2 y 5 días hábiles sin generar un impacto negativo grave.

**Señales típicas:**
- Consultas o solicitudes de información sin plazo explícito
- Seguimiento de un tema en curso, sin escalamiento de tono
- Coordinación de reuniones o tareas para la semana en curso
- Primer contacto de un potencial cliente (sin urgencia declarada)

**Ejemplos:**
- "¿Podrías pasarme el estado del proyecto cuando tengas un momento?"
- "Quería coordinar una reunión para la semana que viene."
- "Te escribo para consultar sobre los servicios que ofrecen."

### Urgencia baja

Correos informativos, administrativos o que no requieren una acción concreta
en el corto plazo.

**Señales típicas:**
- Newsletters, notificaciones automáticas, confirmaciones ya procesadas
- Información de referencia sin pedido de acción
- Agradecimientos o cierres de conversación
- Copias (CC) donde el destinatario no es el interlocutor principal

**Ejemplos:**
- "Te comparto el informe mensual, sin necesidad de respuesta."
- "Gracias por la reunión de hoy, quedamos en contacto."
- Notificaciones automáticas de sistemas (facturación, recordatorios genéricos)

## Casos límite (edge cases) y cómo resolverlos

| Caso | Resolución |
|---|---|
| Correo de un cliente prioritario, pero sin urgencia explícita en el texto | Se clasifica como **media**, salvo que el histórico de ese remitente indique que sus mensajes suelen requerir respuesta rápida (criterio a validar con metadata, no solo texto) |
| Correo urgente en el texto, pero de un remitente desconocido o sospechoso de spam | Se prioriza la señal de urgencia textual para el MVP; la detección de spam queda fuera de alcance de esta primera versión |
| Cadena de correos larga (varios "RE:") sin urgencia explícita en el último mensaje | Se evalúa el último mensaje de la cadena, no el hilo completo |
| Correos en otro idioma | Mismo criterio de señales, adaptando las palabras clave al idioma detectado (a definir si el MVP soporta multi-idioma o solo español) |
| Correo con múltiples temas (uno urgente, otro no) | Se clasifica por el tema de mayor urgencia presente en el mensaje |

## Relación con el pipeline

- Estos criterios son la base para el **etiquetado manual** del dataset de
  entrenamiento (Fase 4 del cronograma).
- Son también el criterio de referencia para evaluar cualitativamente los
  errores del modelo en la etapa de evaluación de impacto.
- El umbral de confianza que deriva un correo al agente IA (ver documentación
  de métricas de confianza) es independiente de estos criterios: un correo
  puede tener una urgencia clara para un humano pero baja confianza en el
  modelo, y viceversa.
EOF