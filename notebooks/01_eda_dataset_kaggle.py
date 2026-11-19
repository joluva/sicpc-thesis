"""
EDA y preparacion del dataset de Kaggle (Customer IT Support - Ticket Dataset).
Valida balance de prioridad por idioma antes de decidir el split para cada
enfoque de modelado.
"""

import pandas as pd

df = pd.read_csv("data/raw/kaggle/tickets.csv")

print("Columnas disponibles:")
print(df.columns.tolist())
print(f"\nTotal de filas: {len(df)}")

# --- Distribucion de idiomas ---
print("\nDistribucion por idioma:")
print(df["language"].value_counts())

# --- Chequeo de sesgo: balance de prioridad POR idioma ---
print("\nBalance de prioridad por idioma (en %):")
tabla_balance = pd.crosstab(df["language"], df["priority"], normalize="index") * 100
print(tabla_balance.round(1), "\n")

# Si las proporciones difieren mucho entre idiomas (ej. mas de ~15-20 puntos
# porcentuales de diferencia en alguna categoria), documentar el sesgo antes
# de decidir si se puede usar el dataset completo sin balancear.

# Filtrar solo español
df_es = df[df["language"] == "es"].copy()

# Mapeo de prioridad -> tu esquema de urgencia
MAPEO_PRIORIDAD = {"low": "baja", "medium": "media", "high": "alta"}
df_es["urgencia"] = df_es["priority"].map(MAPEO_PRIORIDAD)

# Guardar para el notebook de modelado
df_es[["subject", "body", "urgencia"]].to_csv(
    "data/processed/kaggle_es_baseline.csv", index=False
)
print(f"Dataset en español listo: {len(df_es)} filas")
print(df_es["urgencia"].value_counts())
