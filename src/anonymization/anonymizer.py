"""
Modulo de anonimizacion de correos electronicos para SICPC.
Enmascara PII (nombres, emails, telefonos, direcciones) antes de que el dato
llegue al modelo de clasificacion o a cualquier almacenamiento persistente.
"""

import hashlib
import os
from dotenv import load_dotenv
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

load_dotenv()

HASH_SALT = os.getenv("HASH_SALT", "cambiar-este-salt-en-produccion")

# --- Configuracion del motor de NLP en espanol ---
NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "es", "model_name": "es_core_news_lg"}],
}

_provider = NlpEngineProvider(nlp_configuration=NLP_CONFIG)
_nlp_engine = _provider.create_engine()

_analyzer = AnalyzerEngine(nlp_engine=_nlp_engine, supported_languages=["es"])
_anonymizer = AnonymizerEngine()

# Entidades que nos interesa detectar, segun el documento de gobierno de datos
ENTIDADES = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION"]

OPERADORES = {
    "PERSON": OperatorConfig("replace", {"new_value": "[PERSONA]"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[TELEFONO]"}),
    "LOCATION": OperatorConfig("replace", {"new_value": "[DIRECCION]"}),
}


def anonymize_text(texto: str) -> str:
    """Recibe un texto (asunto o cuerpo) y devuelve la version anonimizada."""
    if not texto:
        return texto

    resultados = _analyzer.analyze(text=texto, entities=ENTIDADES, language="es")
    resultado = _anonymizer.anonymize(
        text=texto, analyzer_results=resultados, operators=OPERADORES
    )
    return resultado.text


def hash_identifier(identificador: str) -> str:
    """
    Genera un hash irreversible de un identificador (ej: direccion de email
    del remitente), usando un salt propio del proyecto para evitar ataques
    de diccionario/rainbow table sobre direcciones comunes.
    """
    if not identificador:
        return ""
    valor = f"{HASH_SALT}:{identificador.strip().lower()}"
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def anonymize_email(remitente: str, asunto: str, cuerpo: str) -> dict:
    """
    Punto de entrada principal: recibe los datos crudos de un correo y
    devuelve el diccionario ya anonimizado, listo para pasar al modelo
    de clasificacion o para insertar en la base de datos.
    """
    return {
        "remitente_hash": hash_identifier(remitente),
        "asunto_anonimizado": anonymize_text(asunto),
        "cuerpo_anonimizado": anonymize_text(cuerpo),
    }


if __name__ == "__main__":
    # Prueba rapida manual
    ejemplo = anonymize_email(
        remitente="maria.gomez@ejemplo.com",
        asunto="Consulta de Maria Gomez sobre el pedido",
        cuerpo="Hola, soy Maria Gomez, mi telefono es 011-4555-1234 "
               "y vivo en Av. Corrientes 1234, Buenos Aires. Saludos.",
    )
    for k, v in ejemplo.items():
        print(f"{k}: {v}")
#EOF