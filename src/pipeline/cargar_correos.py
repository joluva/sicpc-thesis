# Pipeline de carga: trae correos reales (solo categoria Principal de Gmail)
# via IMAP, los anonimiza, y los inserta en la base de datos (tablas
# remitente y correo). Evita duplicados usando el UID de IMAP.


import imaplib
import email
from email.header import decode_header
import os
import re
from html.parser import HTMLParser

import mysql.connector
from dotenv import load_dotenv
from src.anonymization.anonymizer import anonymize_email

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
CANTIDAD_A_TRAER = 150


# ---------- Utilidades de decodificacion (iguales a etiquetar_correos.py) ----------

def decode_str(s):
    if s is None:
        return ""
    try:
        decoded, encoding = decode_header(s)[0]
    except Exception:
        return str(s)
    if isinstance(decoded, bytes):
        try:
            return decoded.decode(encoding or "utf-8", errors="ignore")
        except (LookupError, UnicodeDecodeError):
            return decoded.decode("utf-8", errors="ignore")
    return decoded


class _HTMLATexto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes = []
        self._ignorar = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._ignorar = True
        elif tag in ("br", "p", "div", "tr", "li"):
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._ignorar = False

    def handle_data(self, data):
        if not self._ignorar:
            self.partes.append(data)


def _html_a_texto(contenido):
    parser = _HTMLATexto()
    parser.feed(contenido)
    texto = "".join(parser.partes)
    return re.sub(r"\n\s*\n+", "\n\n", texto).strip()


def _decodificar(part):
    payload = part.get_payload(decode=True)
    if payload is None:
        return None
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")


def get_body(msg):
    partes = list(msg.walk()) if msg.is_multipart() else [msg]
    html_fallback = None

    for part in partes:
        if part.get_content_disposition() == "attachment":
            continue
        tipo = part.get_content_type()

        if tipo == "text/plain":
            texto = _decodificar(part)
            if texto and texto.strip():
                return texto
        elif tipo == "text/html" and html_fallback is None:
            texto = _decodificar(part)
            if texto and texto.strip():
                html_fallback = _html_a_texto(texto)

    return html_fallback or ""


# ---------- Base de datos ----------

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


# ---------- Flujo principal ----------

def main():
    # --- Conexion IMAP (solo lectura, no marca correos como leidos) ---
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=30)
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    mail.select("inbox", readonly=True)

    # Solo la categoria Principal (excluye Social, Promociones, Notificaciones)
    status, data = mail.uid("search", None, 'X-GM-RAW "category:primary"')
    uids = data[0].split()
    uids_a_traer = uids[-CANTIDAD_A_TRAER:] if len(uids) >= CANTIDAD_A_TRAER else uids
    print(f"Correos encontrados (solo Principal): {len(uids)}")
    print(f"Se van a procesar (ultimos): {len(uids_a_traer)}")

    # --- Conexion a MySQL ---
    conn = mysql.connector.connect(
        host="localhost", port=3306,
        user=os.getenv("DB_USER", "sJorge"), password=os.getenv("DB_PASSWORD"),
        database="sicpc",
    )
    cursor = conn.cursor()
    cuenta_correo_id = obtener_cuenta_correo_id(cursor)

    insertados, duplicados, errores = 0, 0, 0

    for uid in reversed(uids_a_traer):
        try:
            status, msg_data = mail.uid("fetch", uid, "(BODY.PEEK[])")
            if status != "OK" or not msg_data:
                raise ValueError("Gmail no devolvio el mensaje")

            raw = next(
                (
                    item[1]
                    for item in msg_data
                    if isinstance(item, tuple)
                    and len(item) > 1
                    and isinstance(item[1], bytes)
                ),
                None,
            )
            if raw is None:
                raise ValueError("sin datos del mensaje")

            msg = email.message_from_bytes(raw)

            remitente = decode_str(msg.get("From"))
            asunto = decode_str(msg.get("Subject"))
            cuerpo = get_body(msg)[:2000]

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