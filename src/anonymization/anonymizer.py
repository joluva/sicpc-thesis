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

# Palabras que el modelo de NER suele marcar por error (saludos, cierres).
# Se comparan en minusculas y sin signos de puntuacion en los bordes.
PALABRAS_PERMITIDAS = {
    "saludos", "saludos cordiales", "cordiales saludos", "gracias",
    "muchas gracias", "buenos dias", "buen dia", "buenas tardes",
    "buenas noches", "estimado", "estimados", "estimada", "atentamente",
    "cordialmente", "hola", "slds", "abrazo", "abrazos",
}


def _es_permitida(fragmento: str) -> bool:
    limpio = fragmento.strip().strip(".,;:!¡?¿()\"'").lower()
    return limpio in PALABRAS_PERMITIDAS


def anonymize_text(texto: str) -> str:
    """Recibe un texto (asunto o cuerpo) y devuelve la version anonimizada."""
    if not texto:
        return texto

    resultados = _analyzer.analyze(text=texto, entities=ENTIDADES, language="es")

    # Descartar falsos positivos conocidos antes de enmascarar
    resultados = [
        r for r in resultados if not _es_permitida(texto[r.start:r.end])
    ]

    resultado = _anonymizer.anonymize(
        text=texto, analyzer_results=resultados, operators=OPERADORES
    )
    return resultado.text


def hash_identifier(identificador: str) -> str:
    """
    Hash irreversible (SHA-256 con salt propio del proyecto) de un
    identificador, ej. la direccion de email del remitente.
    """
    if not identificador:
        return ""
    valor = f"{HASH_SALT}:{identificador.strip().lower()}"
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def anonymize_email(remitente: str, asunto: str, cuerpo: str) -> dict:
    """
    Punto de entrada principal: devuelve el diccionario ya anonimizado,
    listo para el modelo de clasificacion o para insertar en la base.
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