"""
Script de prueba de conexión IMAP a Gmail.
Objetivo: confirmar que la conexión funciona, listando los últimos 5 correos.
No procesa, no anonimiza, no clasifica todavía — solo valida el acceso.
"""

import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


def decode_str(s):
    if s is None:
        return ""
    decoded, encoding = decode_header(s)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def main():
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("Faltan GMAIL_USER o GMAIL_APP_PASSWORD en el archivo .env")
        return

    print(f"Conectando a {IMAP_SERVER} como {GMAIL_USER} ...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    print("Conexion exitosa.")

    mail.select("inbox")

    status, data = mail.search(None, "ALL")
    email_ids = data[0].split()
    ultimos_5 = email_ids[-5:] if len(email_ids) >= 5 else email_ids

    print(f"\nUltimos {len(ultimos_5)} correos en la bandeja:\n")

    for eid in reversed(ultimos_5):
        status, msg_data = mail.fetch(eid, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        asunto = decode_str(msg.get("Subject"))
        remitente = decode_str(msg.get("From"))
        fecha = msg.get("Date")

        print(f"- De: {remitente}")
        print(f"  Asunto: {asunto}")
        print(f"  Fecha: {fecha}")
        print()

    mail.logout()
    print("Conexion cerrada correctamente.")


if __name__ == "__main__":
    main()