# Propósito

Script interactivo de consola que permite asignar la **urgencia real**
(ground truth) a los correos ya cargados en la base, aplicando los
criterios definidos en `docs/criterios-clasificacion.md`. Es el paso que
genera los datos de entrenamiento reales para el modelo de clasificación.

Correos en la base (sin etiqueta) → Etiquetado manual → urgencia_real guardada


## Ubicación y forma de ejecución

src/labeling/etiquetar_correos.py


```bash
python src/labeling/etiquetar_correos.py
```

(Este script no importa nada de otro paquete propio del proyecto, por eso
se puede correr directo, a diferencia de `cargar_correos.py`.)

## Requisito previo en el esquema

Depende de que la tabla `correo` tenga la columna `urgencia_real`:

```sql
ALTER TABLE correo ADD COLUMN urgencia_real VARCHAR(20) NULL;
```

Esta columna es intencionalmente distinta de `categoria_predicha` (lo que
el modelo predice) y de la tabla `correccion_manual` (el historial de
correcciones post-predicción) — `urgencia_real` es la etiqueta de
referencia usada para *entrenar*, no para operar.

## Variables de entorno requeridas

Del `.env` de la raíz:

(el resto de los parámetros de conexión — host, puerto, usuario, base —
están fijos en el propio script, no parametrizados por entorno)

## Estructura de datos

### `ETIQUETAS`
```python
ETIQUETAS = {"1": "alta", "2": "media", "3": "baja"}
```
Diccionario que traduce la tecla que aprieta el usuario a la etiqueta real
que se guarda en la base — mantiene la interacción simple (un solo dígito)
sin sacrificar la claridad del dato guardado.

## Función

### `main()`

1. **Conexión a MySQL**, con `cursor(dictionary=True)` — esto hace que cada
   fila se devuelva como diccionario (`correo['asunto_anonimizado']`) en
   vez de tupla posicional, más legible en el resto del código.

2. **Consulta de pendientes**:
```sql
   SELECT id, asunto_anonimizado, cuerpo_anonimizado FROM correo
   WHERE urgencia_real IS NULL
```
   Trae únicamente los correos que **todavía no fueron etiquetados** — por
   eso el script se puede cortar y retomar en cualquier momento sin repetir
   trabajo ya hecho.

3. **Por cada correo pendiente**:
   - Muestra un contador de progreso (`[3/50]`), el asunto completo, y los
     primeros 300 caracteres del cuerpo (ya anonimizados) — suficiente
     contexto para decidir la urgencia sin saturar la pantalla.
   - Pide la clasificación por teclado: `1` (alta), `2` (media), `3`
     (baja), `s` (saltar este correo sin decidir todavía), `q` (salir y
     guardar el progreso hecho hasta ese punto).
   - Si la respuesta no es ninguna de las opciones válidas, avisa y pasa al
     siguiente correo sin guardar nada (lo deja pendiente para la próxima
     sesión).
   - Si la respuesta es válida, ejecuta el `UPDATE` puntual sobre ese
     correo y hace `commit()` **inmediatamente** — igual que en
     `cargar_correos.py`, esto asegura que ningún progreso se pierda si el
     usuario corta el proceso a mitad de camino.

4. **Cierre y resumen**: al terminar (por fin de la lista o por `q`),
   cierra la conexión e imprime cuántos correos se etiquetaron en esa
   sesión puntual.

## Por qué el diseño es deliberadamente simple

- **Sin interfaz gráfica**: para el volumen que maneja el MVP (decenas a
  pocos cientos de correos), una consola interactiva es más rápida de usar
  y de mantener que construir una pantalla dedicada — la complejidad de una
  UI de etiquetado queda como posible extensión futura, no como parte del
  MVP.
- **Guardado inmediato por fila**: prioriza nunca perder trabajo manual ya
  hecho por el usuario, por sobre la eficiencia de hacer un solo `commit`
  al final.
- **Retomable**: como la consulta siempre filtra por `urgencia_real IS
  NULL`, el mismo comando sirve para la primera sesión de etiquetado y para
  todas las siguientes, sin parámetros adicionales.

## Relación con el resto del proyecto

- Depende de que `cargar_correos.py` ya haya insertado correos en la tabla
  `correo`.
- Su salida (`urgencia_real` poblada) es la fuente de datos reales que
  consume `notebooks/02_baseline.py` para entrenar y evaluar el modelo,
  combinada con el subset en español del dataset de Kaggle.


## Procedimiento realizado

Como parte de la documentación y versionado del proyecto se realizaron los
siguientes pasos:

1. Se documentó el funcionamiento del script
   `src/labeling/etiquetar_correos.py`.

2. Se revisó el contenido del documento antes de incorporarlo al repositorio.

3. Se agregó el documento al área de preparación de Git mediante:
   `git add docs/etiquetar_correos.md`

4. Se creó el commit correspondiente mediante:
   `git commit -m "Documenta el script de etiquetado manual de correos"`

5. Se publicó el commit en el repositorio remoto mediante:
   `git push`

### Resultado

La documentación del script quedó incorporada al proyecto y versionada en
la rama `feature/nuevo-script`.
