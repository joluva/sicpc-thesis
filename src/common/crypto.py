"""
Cifrado simetrico (Fernet) para las credenciales de cuenta_correo.
La clave maestra vive solo en el .env, nunca en el repo ni en la base.
"""

import os
import sys

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()


def generar_clave() -> str:
    """Genera una clave Fernet nueva. Se ejecuta una sola vez por entorno."""
    return Fernet.generate_key().decode()


def _fernet() -> Fernet:
    # Se crea al usarse, no al importar, para que importar el modulo
    # no falle si todavia no configuraste la clave.
    clave = os.getenv("ENCRYPTION_KEY")
    if not clave:
        raise RuntimeError(
            "Falta ENCRYPTION_KEY en el .env. "
            "Generala con: python3 -m src.common.crypto --generar-clave"
        )
    return Fernet(clave.encode())


def encrypt(texto: str) -> str:
    """Cifra un texto (ej. contraseña de aplicacion) y devuelve un string."""
    return _fernet().encrypt(texto.encode("utf-8")).decode("utf-8")


def decrypt(texto_cifrado: str) -> str:
    """Descifra un texto cifrado con encrypt()."""
    try:
        return _fernet().decrypt(texto_cifrado.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise ValueError("No se pudo descifrar: clave incorrecta o dato alterado")


if __name__ == "__main__":
    if "--generar-clave" in sys.argv:
        print(generar_clave())
    else:
        # Autotest: cifra y descifra sin mostrar ningun secreto
        original = "contraseña-de-prueba-123"
        cifrado = encrypt(original)
        assert cifrado != original
        assert decrypt(cifrado) == original
        print("Cifrado/descifrado OK")