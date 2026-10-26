"""
Modulo de anonimizacion de correos electronicos para SICPC.
Enmascara PII (nombres, emails, telefonos, direcciones) antes de que el dato
llegue al modelo de clasificacion o a cualquier almacenamiento persistente.
"""

import hashlib
import os
import re
from dotenv import load_dotenv
from presidio_analyzer import Pattern, PatternRecognizer
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

_patrones_patente = [
    # Formato actual (desde 2016): AC 111 DF
    Pattern("patente_mercosur", r"\b[A-Z]{2}\s?\d{3}\s?[A-Z]{2}\b", 0.6),
    # Formato anterior: ABC 123 / ABC-123 / ABC123
    Pattern("patente_anterior", r"\b[A-Z]{3}[\s-]?\d{3}\b", 0.5),
    # Motos actuales: A 123 ABC
    Pattern("patente_moto", r"\b[A-Z]\s?\d{3}\s?[A-Z]{3}\b", 0.5),
]

_analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PATENTE",
        patterns=_patrones_patente,
        supported_language="es",
        # Sin IGNORECASE: solo mayusculas, para no confundir "mes 123" con una patente
        global_regex_flags=re.DOTALL | re.MULTILINE,
        name="PatenteArgentinaRecognizer",
    )
)


# Entidades que nos interesa detectar, segun el documento de gobierno de datos
ENTIDADES = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "PATENTE"]

OPERADORES = {
    "PERSON": OperatorConfig("replace", {"new_value": "[PERSONA]"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[TELEFONO]"}),
    "LOCATION": OperatorConfig("replace", {"new_value": "[DIRECCION]"}),
    "PATENTE": OperatorConfig("replace", {"new_value": "[PATENTE]"}),
}

# Palabras que el modelo de NER suele marcar por error (saludos, cierres).
# Se comparan en minusculas y sin signos de puntuacion en los bordes.
PALABRAS_PERMITIDAS = {
    "saludos", "saludos cordiales", "cordiales saludos", "gracias",
    "muchas gracias", "buenos dias", "buen dia", "buenas tardes",
    "buenas noches", "estimado", "estimados", "estimada", "atentamente",
    "cordialmente", "hola", "slds", "abrazo", "abrazos", "tene en cuenta", "ten en cuenta",
    "que tengas un buen dia", "que tengas un buen dia", "que tenga un buen dia",
    "transferencia", "transferencias", "transferencias bancarias",
    "ciudad",  "ciudades", "ciudades", "direccion", "direcciones",
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