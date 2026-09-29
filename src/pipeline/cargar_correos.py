
# Pipeline de carga: trae correos reales via IMAP, los anonimiza, y los
# inserta en la base de datos (tablas remitente y correo).
# Evita duplicados usando el UID de IMAP.


import imaplib
import email
from email.header import decode_header
import os
import mysql.connector
from dotenv import load_dotenv
from src.anonymization.anonymizer import anonymize_email

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
CANTIDAD_A_TRAER = 50  # ajustable


def decode_str(s):
    if s is None:
        return ""
    decoded, encoding = decode_header(s)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""


def obtener_cuenta_correo_id(cursor):
    cursor.execute(
        "SELECT id FROM cuenta_correo WHERE direccion = %s LIMIT 1", (GMAIL_USER,)
    )
    fila = cursor.fetchone()
    return fila[0] if fila else 1  # fallback a la cuenta de migracion


def upsert_remitente(cursor, remitente_hash):
    cursor.execute(
        "SELECT remitente_hash FROM remitente WHERE remitente_hash = %s",
        (remitente_hash,),
    )
    if cursor.fetchone():
        cursor.execute(
            "UPDATE remitente SET cantidad_correos = cantidad_correos + 1 "
            "WHERE remitente_hash = %s",
            (remitente_hash,),
        )
    else:
        cursor.execute(
            "INSERT INTO remitente (remitente_hash, cantidad_correos) "
            "VALUES (%s, 1)",
            (remitente_hash,),
        )


def main():
    # --- Conexion IMAP ---
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    mail.select("inbox")

    status, data = mail.uid("search", None, "ALL")
    uids = data[0].split()
    uids_a_traer = uids[-CANTIDAD_A_TRAER:] if len(uids) >= CANTIDAD_A_TRAER else uids
    print(f"Correos encontrados en la bandeja: {len(uids)}")
    print(f"Se van a procesar (ultimos): {len(uids_a_traer)}")

    # --- Conexion a MySQL ---
    conn = mysql.connector.connect(
        host="localhost", port=3306,
        user="sJorge", password=os.getenv("DB_PASSWORD"),
        database="sicpc",
    )
    cursor = conn.cursor()
    cuenta_correo_id = obtener_cuenta_correo_id(cursor)

    insertados, duplicados, errores = 0, 0, 0

    for uid in reversed(uids_a_traer):
        try:
            status, msg_data = mail.uid("fetch", uid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            remitente = decode_str(msg.get("From"))
            asunto = decode_str(msg.get("Subject"))
            cuerpo = get_body(msg)[:2000]  # limite razonable

            resultado = anonymize_email(remitente, asunto, cuerpo)
            upsert_remitente(cursor, resultado["remitente_hash"])

            cursor.execute(
                """
                INSERT INTO correo
                    (cuenta_correo_id, imap_uid, imap_folder, remitente_hash,
                     asunto_anonimizado, cuerpo_anonimizado)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    cuenta_correo_id,
                    uid.decode(),
                    "INBOX",
                    resultado["remitente_hash"],
                    resultado["asunto_anonimizado"],
                    resultado["cuerpo_anonimizado"],
                ),
            )
            conn.commit()
            insertados += 1

        except mysql.connector.errors.IntegrityError:
            # Ya existe (mismo cuenta_correo_id + imap_uid) -> se ignora
            conn.rollback()
            duplicados += 1
        except Exception as e:
            print(f"Error procesando UID {uid}: {e}")
            conn.rollback()
            errores += 1

    cursor.close()
    conn.close()
    mail.logout()

    print(f"\nInsertados: {insertados}")
    print(f"Duplicados (ya existian): {duplicados}")
    print(f"Errores: {errores}")


if __name__ == "__main__":
    main()
