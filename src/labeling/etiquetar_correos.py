"""
Etiquetado manual con contexto: muestra el correo ORIGINAL (recuperado
on-demand por IMAP, sin guardarlo) junto a su version anonimizada.
Solo se guarda la etiqueta; el modelo entrena con texto anonimizado.
"""

import imaplib
import email
from email.header import decode_header
import os
import re
from html.parser import HTMLParser

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

ETIQUETAS = {"1": "alta", "2": "media", "3": "baja"}


# ---------- Utilidades de decodificacion ----------

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
        # Ignorar adjuntos que no sean parte del cuerpo del mensaje.
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


# ---------- Recuperacion del correo original ----------

def traer_original(mail, uid):
    try:
        status, data = mail.uid("fetch", str(uid), "(BODY.PEEK[])")

        if status != "OK" or not data:
            return "(no disponible)", "(Gmail no devolvió el mensaje)"

        mensaje = next(
            (
                item[1]
                for item in data
                if isinstance(item, tuple)
                and len(item) > 1
                and isinstance(item[1], bytes)
            ),
            None,
        )

        if mensaje is None:
            return "(no disponible)", "(No se encontraron datos del mensaje)"

        msg = email.message_from_bytes(mensaje)
        return decode_str(msg.get("Subject")), get_body(msg)

    except (imaplib.IMAP4.error, OSError, IndexError, TypeError, ValueError) as e:
        return "(no disponible)", f"(Error al recuperar el original: {e})"


# ---------- Flujo principal ----------

def main():
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=30)
    mail.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
    mail.select("inbox", readonly=True)

    conn = mysql.connector.connect(
        host="localhost", port=3306,
        user=os.getenv("DB_USER", "sJorge"), password=os.getenv("DB_PASSWORD"),
        database="sicpc",
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, imap_uid, asunto_anonimizado, cuerpo_anonimizado "
        "FROM correo WHERE urgencia_real IS NULL"
    )
    pendientes = cursor.fetchall()
    print(f"Correos pendientes de etiquetar: {len(pendientes)}\n")

    etiquetados = 0
    for i, correo in enumerate(pendientes, start=1):
        asunto_o, cuerpo_o = traer_original(mail, correo["imap_uid"])

        print("=" * 70)
        print(f"[{i}/{len(pendientes)}]")
        print("--- ORIGINAL ---")
        print(f"Asunto: {asunto_o}")
        print(f"Cuerpo: {(cuerpo_o or '')[:600]}")
        print("\n--- ANONIMIZADO (lo que ve el modelo) ---")
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
    mail.logout()
    print(f"\nEtiquetado finalizado. Correos etiquetados en esta sesion: {etiquetados}")


if __name__ == "__main__":
    main()