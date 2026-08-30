# Métrica de Confianza del Modelo

## Propósito

Este documento define formalmente cómo se calcula la confianza de las
predicciones del modelo de clasificación, y cómo esa métrica se utiliza dentro
del sistema: como disparador de la capa de agente IA y como señal de
monitoreo del modelo en producción.

## Definición: confianza de una predicción individual

La confianza de una predicción es la **probabilidad máxima que el modelo
asigna entre todas las clases posibles** para un correo dado.

confianza_i = max( P(clase = c | correo_i) ) para c en {alta, media, baja}


Por ejemplo, si el modelo predice para un correo: 80% urgencia alta, 15%
media, 5% baja — la confianza de esa predicción puntual es **0.80**.

## Cómo se obtiene según el modelo utilizado

| Modelo | Fuente de la probabilidad |
|---|---|
| Logistic Regression / SVM (scikit-learn) | `modelo.predict_proba(x)` — con SVM, instanciar con `probability=True` o calibrar con `CalibratedClassifierCV` |
| Embeddings + clasificador | Igual que el anterior, si el clasificador final sobre los embeddings es Logistic Regression/SVM |
| Transformer (DistilBERT) | `softmax` sobre los logits de salida del modelo; la probabilidad máxima es la confianza |
| LLM few-shot | El prompt debe solicitar explícitamente un score (0-1) junto con la etiqueta, o utilizar el `logprob` del token de respuesta si la API lo expone |

## Definición: confianza promedio de un período

Es el promedio aritmético de las confianzas individuales de todos los correos
clasificados dentro del período filtrado (día, semana, etc.), tal como se
muestra en el dashboard.

confianza_promedio = ( Σ confianza_i ) / n correos en el período


En Python, sobre la tabla de resultados:
```python
df_periodo["confianza"].mean()
```

## Uso de la métrica dentro del sistema

### 1. Disparador de la capa de agente IA
Cuando la confianza de una predicción individual cae por debajo de un umbral
definido (valor inicial propuesto: **0.6**, sujeto a ajuste durante la
evaluación del modelo), ese correo se deriva al agente IA para asistencia
adicional (resumen, sugerencia de respuesta o escalamiento a revisión manual).

### 2. Señal de monitoreo / drift
Si el **promedio** de confianza de un período desciende de forma sostenida
respecto al promedio histórico, es una señal temprana de que el modelo está
recibiendo correos con características distintas a las vistas durante el
entrenamiento (nuevo vocabulario, nuevos remitentes, cambio de contexto), y
puede requerir reentrenamiento.

## Limitación importante: confianza no es precisión

La confianza reportada por el modelo **no garantiza que la predicción sea
correcta** — es la certeza que el modelo tiene sobre sí mismo, no una medida
directa de acierto real. Un modelo mal calibrado puede reportar alta confianza
en predicciones erróneas.

### Validación de calibración (análisis propuesto)
Para verificar que la confianza reportada es representativa de la precisión
real, se propone construir una **curva de calibración**: agrupar las
predicciones por rango de confianza (ej. 0.5-0.6, 0.6-0.7, ...) y comparar,
dentro de cada grupo, la confianza promedio reportada contra la tasa de
acierto real observada. Un modelo bien calibrado debería mostrar ambos valores
alineados. Este análisis se documentará en el capítulo de evaluación de la
tesis.

## Relación con otros documentos

- El umbral de confianza que deriva al agente IA es independiente de los
  criterios de urgencia definidos en `docs/criterios-clasificacion.md`: un
  correo puede tener urgencia clara para un humano pero baja confianza en el
  modelo, y viceversa.
- El monitoreo de drift descripto aquí complementa la arquitectura productiva
  del sistema, orquestada por n8n.
EOF