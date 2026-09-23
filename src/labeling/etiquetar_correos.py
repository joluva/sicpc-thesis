"""
Script de etiquetado manual de correos.
Muestra cada correo sin etiqueta (urgencia_real) y guarda la clasificacion
que el usuario ingresa, segun los criterios de docs/criterios-clasificacion.md
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

ETIQUETAS = {"1": "alta", "2": "media", "3": "baja"}


def main():
    conn = mysql.connector.connect(
        host="localhost", port=3306,
        user="sJorge", password=os.getenv("DB_PASSWORD"),
        database="sicpc",
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, asunto_anonimizado, cuerpo_anonimizado FROM correo "
        "WHERE urgencia_real IS NULL"
    )
    pendientes = cursor.fetchall()
    print(f"Correos pendientes de etiquetar: {len(pendientes)}\n")

    etiquetados = 0
    for correo in pendientes:
        print("=" * 70)
        print(f"[{etiquetados + 1}/{len(pendientes)}]")
        print(f"Asunto: {correo['asunto_anonimizado']}")
        print(f"Cuerpo: {(correo['cuerpo_anonimizado'] or '')[:300]}")
        print("\n1) Alta   2) Media   3) Baja   s) Saltar   q) Salir y guardar")
        resp = input("Urgencia real: ").strip().lower()

        if resp == "q":
            break
        if resp == "s":
            continue
        if resp not in ETIQUETAS:
            print("Opcion invalida, se salta este correo.")
            continue

        cursor.execute(
            "UPDATE correo SET urgencia_real = %s WHERE id = %s",
            (ETIQUETAS[resp], correo["id"]),
        )
        conn.commit()
        etiquetados += 1
        print(f"-> Guardado como '{ETIQUETAS[resp]}'\n")

    cursor.close()
    conn.close()
    print(f"\nEtiquetado finalizado. Correos etiquetados en esta sesion: {etiquetados}")


if __name__ == "__main__":
    main()
