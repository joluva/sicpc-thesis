# Resultados y hallazgos de calidad de datos

## Propósito

Este documento registra los problemas de calidad de datos detectados durante
la construcción del dataset de entrenamiento, cómo se resolvieron, y los
resultados de los modelos de clasificación de urgencia obtenidos en cada
etapa. Sirve como base para el capítulo de preparación de datos y
resultados de la tesis.

## 1. Resumen ejecutivo

- Se detectaron **siete hallazgos** de calidad de datos, seis de ellos
  corregidos y uno pendiente de verificación (sección 3).
- La contaminación de la bandeja por categorías de Gmail degradó el modelo:
  al corregirla, el F1 de "media" pasó de 0.42 a 0.56.
- Los embeddings multilingües superan levemente al baseline (macro F1 0.61
  contra 0.57), pero la diferencia **no es concluyente** con el tamaño de
  test disponible.
- Ambos modelos tienden a clasificar como "baja" los correos reales de
  urgencia media o alta. La causa probable es que el dataset de
  entrenamiento es mayormente sintético.
- La limitación principal es el **volumen de correos reales etiquetados**
  (34 en el conjunto de prueba).

## 2. Datos utilizados

| Fuente | Descripción | Volumen |
|---|---|---|
| Dataset de Kaggle (subset en español) | Tickets de soporte sintéticos con prioridad `low/medium/high`, mapeada a `baja/media/alta` | 812 filas |
| Correos reales propios | Categoría "Principal" de Gmail, anonimizados y etiquetados manualmente | Alrededor de 170 (34 en el test) |

Los correos reales se etiquetaron con los criterios de
`docs/criterios-clasificacion.md`, con el original a la vista para decidir
la urgencia. El modelo entrena y predice únicamente sobre el texto
anonimizado.

## 3. Hallazgos de calidad de datos

### 3.1 El dataset de Kaggle descargado no incluía español

- **Qué pasó:** la última versión del dataset contenía solo inglés y
  alemán, pese a que la descripción mencionaba español.
- **Cómo se detectó:** script de análisis exploratorio
  (`notebooks/01_eda_dataset_kaggle.py`).
- **Resolución:** se descargó otra versión (v8) con 4.000 filas: inglés
  1.391, alemán 848, **español 812**, francés 476 y portugués 473.
- **Verificación:** la proporción de prioridades es consistente entre
  idiomas (alta 39-43 %, media 38-43 %, baja 17-22 %), por lo que el
  idioma no actúa como señal espuria de urgencia.

### 3.2 El dataset de Kaggle es sintético

- **Qué implica:** los tickets están generados, no son correspondencia
  real. La urgencia tiende a expresarse con señales explícitas.
- **Tratamiento:** se usa para dar volumen, y se complementa con correos
  reales. Los resultados se reportan por fuente (sección 5.3).

### 3.3 Contaminación por categorías de Gmail

- **Qué pasó:** en IMAP, las pestañas Principal, Social, Promociones y
  Notificaciones conviven en la misma carpeta `INBOX`. La carga traía todo
  mezclado, incluyendo promociones y notificaciones automáticas.
- **Cómo se detectó:** la segunda corrida del modelo empeoró, con un
  aumento de la confusión media↔baja en la matriz. Al revisar los correos
  etiquetados se encontró la mezcla.
- **Resolución:** filtro `X-GM-RAW "category:primary"` en la búsqueda
  IMAP. Se borraron los 48 correos cargados (volumen bajo, más simple y
  confiable que depurarlos uno por uno) y se recargó el lote limpio.
- **Efecto medido:** F1 de "media" de 0.42 a 0.56 y accuracy de 0.53 a
  0.59 (ver sección 5.1).

### 3.4 Anonimización incompleta o excesiva

Revisando los correos reales se encontraron fallas del módulo de
anonimización, que combina el reconocimiento de entidades de Presidio con
spaCy (modelo `es_core_news_lg`):

| Falla | Tipo | Resolución |
|---|---|---|
| Nombre propio del autor sin enmascarar en el cuerpo | Falso negativo | Reconocedor determinista con lista de nombres (`NOMBRES_PROPIOS`, en el `.env`, no en el código) |
| Patentes automotrices argentinas (ej. `AC 111 DF`) sin enmascarar | Falso negativo | Reconocedor por expresión regular (formato actual, formato anterior y motos) |
| Palabras de cierre ("Saludos", "Cordialmente") marcadas como persona o lugar | Falso positivo | Lista de palabras permitidas (`PALABRAS_PERMITIDAS`), comparada sin distinguir mayúsculas |
| Direcciones compuestas ("Av. Corrientes 1234") enmascaradas solo en parte | Falso negativo parcial | **Limitación conocida**, sin resolver |
| Otros identificadores argentinos (DNI, CUIT/CUIL, CBU) | Posible falso negativo | **Pendiente de verificar** en los correos reales |

Lección: los reconocedores de Presidio cubren datos internacionales
(email, teléfono), pero no los formatos locales. Los datos propios y los de
formato argentino requieren reglas explícitas. Un modelo de NER no
garantiza detectar todos los nombres, y su recall en español es menor que
en inglés.

### 3.5 El etiquetado sobre texto anonimizado perdía contexto

- **Qué pasó:** con nombres y datos enmascarados, a veces no se podía
  decidir la urgencia real.
- **Resolución:** el script de etiquetado muestra el **original**,
  recuperado por IMAP en el momento y sin guardarlo, junto al texto
  anonimizado. Se guarda solo la etiqueta.
- **Compromiso de diseño:** privacidad y utilidad. El modelo sigue viendo
  únicamente texto anonimizado, de modo que si la anonimización destruye la
  señal de urgencia, el rendimiento lo refleja.

### 3.6 Problemas técnicos de la ingesta

| Problema | Resolución |
|---|---|
| Encoding declarado inexistente (`unknown-8bit`) hacía fallar correos | Decodificación tolerante con fallback a UTF-8 |
| Correos solo HTML devolvían cuerpo vacío | Fallback que convierte HTML a texto |
| La lectura marcaba los correos como leídos en la bandeja real | `BODY.PEEK[]` y sesión en solo lectura |
| Columnas `categoria_predicha` y `confianza` obligatorias antes de existir un modelo | Migración a `NULL` |
| Falta de límite de tiempo en la conexión | `timeout=30` |

### 3.7 Sesgo hacia "baja" en correos reales

- **Observación:** ambos modelos clasifican como "baja" la mayoría de los
  errores sobre correos reales (12 de 14).
- **Estado:** hipótesis sin verificar, ver sección 5.3.

## 4. Metodología de evaluación

- Modelos: TF-IDF más Regresión Logística (baseline) y embeddings
  multilingües (`paraphrase-multilingual-mpnet-base-v2`) más Regresión
  Logística.
- Split 80/20, estratificado por urgencia, `random_state=42`. Ambos
  modelos usan el mismo test en la comparación final.
- Métricas: precision, recall y F1 por clase, matriz de confusión, y
  desglose por fuente (Kaggle contra correos reales). No se usa solo el
  accuracy, por el desbalance de clases (la clase "baja" es minoritaria).

## 5. Resultados

### 5.1 Efecto de la limpieza (baseline en tres corridas)

| Métrica | Solo Kaggle | Kaggle + 48 reales contaminados | Kaggle + reales limpios |
|---|---|---|---|
| F1 alta | 0.71 | 0.71 | 0.70 |
| F1 media | 0.51 | 0.42 | 0.56 |
| F1 baja | 0.43 | 0.40 | 0.47 |
| Accuracy | 0.58 | 0.53 | 0.59 |
| Tamaño del test | 163 | 172 | 193 |

Los conjuntos de prueba difieren entre corridas, por lo que la
comparación es orientativa. La conclusión sólida es que los datos
contaminados empeoraban el modelo y que la limpieza lo recuperó. La mejora
sobre "solo Kaggle" (0.58 a 0.59) no es concluyente.

### 5.2 Baseline contra embeddings (mismo test, n = 193)

| Métrica | Baseline | Embeddings |
|---|---|---|
| Accuracy | 0.59 | 0.61 |
| F1 macro | 0.57 | 0.61 |
| F1 alta | 0.70 | 0.72 |
| F1 media | 0.56 | 0.55 |
| F1 baja | 0.47 | 0.55 |
| Aciertos | 113 | 118 |
| Errores alta↔baja | 15 | 10 |

Matriz de confusión del baseline (filas: real, columnas: predicho, en
orden alta, media, baja):

[[49 16 8]
[12 41 20]
[ 7 17 23]]


Matriz de confusión de embeddings:

[[49 17 7]
[11 40 22]
[ 3 15 29]]


- Los errores se concentran en categorías vecinas: media↔baja y
  alta↔media. Los extremos (alta↔baja) son poco frecuentes.
- Los embeddings mejoran sobre todo la clase "baja" (recall de 0.49 a
  0.62). "Media" sigue siendo la clase más difícil, coherente con que su
  límite es el más difuso en los criterios de clasificación.
- La diferencia total es de 5 aciertos sobre 193. El margen de error del
  accuracy con ese tamaño es de aproximadamente ±7 puntos, por lo que la
  tendencia es favorable pero no concluyente.

### 5.3 Resultados por fuente

| | Baseline | Embeddings |
|---|---|---|
| Accuracy sobre Kaggle (n = 159) | 0.58 | 0.62 |
| Accuracy sobre correos reales (n = 34) | 0.59 | 0.59 |
| Recall "baja" en correos reales | 0.92 | 0.92 |
| Precisión "baja" en correos reales | 0.50 | 0.50 |

- La mejora de los embeddings aparece sobre Kaggle, no sobre correos
  reales, donde empatan.
- En los correos reales, los dos modelos predicen "baja" 24 veces y
  acaban acertando 12. Ante un correo real, el modelo tiende a asignarle la
  urgencia menor.
- **Hipótesis (sin verificar):** en los tickets sintéticos la urgencia se
  marca con palabras explícitas, y en los correos reales es más sutil. Sin
  esas señales, el modelo se inclina por "baja". Se verifica revisando los
  correos reales "alta" y "media" mal clasificados.
- Con 34 correos reales, el margen de error es de aproximadamente ±17
  puntos. Las diferencias entre modelos en esta fuente son de uno o dos
  correos y no son interpretables.

## 6. Limitaciones

1. **Volumen de correos reales etiquetados:** insuficiente para
   conclusiones estadísticas sobre correos reales.
2. **Dataset de entrenamiento mayormente sintético:** puede sobreestimar el
   desempeño y sesgar hacia "baja".
3. **Anonimización imperfecta:** direcciones compuestas y otros datos
   locales pueden quedar sin enmascarar.
4. **Un solo etiquetador:** no hay medida de acuerdo entre anotadores,
   por lo que la etiqueta puede reflejar criterio personal.
5. **Evaluación con un único split:** no se usó validación cruzada.
6. **Todavía no se responde** si sumar correos reales mejora el modelo
   respecto de entrenar solo con Kaggle. Responderlo exige entrenar solo
   con Kaggle y evaluar sobre los mismos correos reales de prueba.

## 7. Próximos pasos

- Etiquetar más correos reales (objetivo de unos 100 adicionales).
- Revisar los errores sobre correos reales para verificar la hipótesis de
  la sección 5.3.
- Entrenar solo con Kaggle y evaluar sobre los correos reales del test,
  para aislar el aporte de los datos reales.
- Revisar la presencia de DNI, CUIT/CUIL y CBU en los correos y, si
  aparecen, agregar reconocedores.
- Evaluar la calibración de la confianza del modelo (curva de
  calibración), según `docs/metrica-confianza.md`.
- Clasificar los correos y guardar `categoria_predicha` y `confianza` en
  la base de datos.

## 8. Documentos relacionados

- `docs/criterios-clasificacion.md`
- `docs/gobierno-de-datos.md`
- `docs/anonimizacion.md`
- `docs/cargar_correos.md`
- `docs/etiquetar_correos.md`
- `docs/metrica-confianza.md`