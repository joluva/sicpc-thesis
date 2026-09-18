📊 Presidio-Analyzer: La Biblioteca Definitiva para Detección de PII en Python
🔍 ¿Qué es Presidio-Analyzer?
Presidio-Analyzer es el componente principal del framework Microsoft Presidio, una herramienta de código abierto diseñada para detectar Información de Identificación Personal (PII) en texto no estructurado . Su objetivo principal es identificar automáticamente datos sensibles como nombres, números de teléfono, direcciones de correo electrónico, números de tarjetas de crédito, y más, para luego poder anonimizarlos o protegerlos según las normativas de privacidad como GDPR, HIPAA o CCPA .

🎯 Mecanismo de Funcionamiento
El funcionamiento de Presidio-Analyzer se basa en una arquitectura de múltiples reconocedores (recognizers) . Durante el análisis, la biblioteca ejecuta un conjunto de estos reconocedores, cada uno especializado en detectar un tipo específico de entidad utilizando diferentes estrategias:

Patrones Regulares (Regex): Para entidades con formatos definidos como emails o números de teléfono .

Modelos de Lenguaje (NLP): Basado en spaCy, reconoce entidades como personas o ubicaciones en contexto .

Lógica Personalizada: Permite a los desarrolladores crear sus propios reconocedores para casos de uso específicos .

🚀 Instalación y Configuración Inicial
Instalación Básica

pip install presidio-analyzer

Instalación con Soporte para LLMs
Presidio-Analyzer también permite la detección de PII utilizando Modelos de Lenguaje Extensos (LLMs) o modelos pequeños (SLMs) para un reconocimiento más flexible, por ejemplo, usando Ollama o Azure OpenAI :

pip install presidio-analyzer[langextract]

⚙️ Uso Fundamental
Ejemplo 1: Análisis Básico
El uso más directo es inicializar el motor (AnalyzerEngine) y analizar un texto :

from presidio_analyzer import AnalyzerEngine

# Inicializar el motor (carga modelos NLP y reconocedores predefinidos)
analyzer = AnalyzerEngine()

# Texto a analizar
texto = "Mi nombre es Juan Pérez y mi correo es juan.perez@email.com"

# Realizar el análisis
resultados = analyzer.analyze(text=texto, language="es")

# Mostrar resultados
for resultado in resultados:
    print(f"Entidad: {resultado.entity_type}")
    print(f"Texto encontrado: {texto[resultado.start:resultado.end]}")
    print(f"Puntuación de confianza: {resultado.score}")
    print("-" * 20)

Salida esperada: Detectaría Juan Pérez como PERSON y juan.perez@email.com como EMAIL_ADDRESS.

Ejemplo 2: Filtrar Entidades y Establecer Umbral de Confianza
Para evitar falsos positivos, puedes especificar qué entidades buscar y un umbral de puntuación mínimo :

from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
texto = "Mi número es 212-555-5555"

# Buscar solo teléfonos y personas, con una confianza > 0.7
resultados = analyzer.analyze(
    text=texto,
    language="en",
    entities=["PHONE_NUMBER", "PERSON"],
    score_threshold=0.7
)

print(resultados)

🛠️ Personalización Avanzada: Crear un Reconocedor Personalizado
Una de las características más potentes es la habilidad de añadir reconocedores para entidades no cubiertas por defecto, como un código interno de empresa.

Usando Reconocedor por Lista de Denegación (Deny-List) :

from presidio_analyzer import PatternRecognizer, AnalyzerEngine

# 1. Definir la lista de términos a detectar
titles_list = ["Sr.", "Sra.", "Dr.", "Prof."]

# 2. Crear el reconocedor basado en esa lista
titles_recognizer = PatternRecognizer(
    supported_entity="TITULO",
    deny_list=titles_list
)

# 3. Añadirlo al motor de análisis
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(titles_recognizer)

# 4. Probar el nuevo reconocedor
texto = "El Dr. Pérez y la Sra. Gómez asistirán a la reunión."
resultados = analyzer.analyze(text=texto, language="es")

for resultado in resultados:
    print(f"- {texto[resultado.start:resultado.end]} como {resultado.entity_type} (Score: {resultado.score})")

Resultado esperado: Detectará "Dr." y "Sra." como TITULO.

Usando Reconocedor por Patrón Regex :
Para entidades con un formato específico:

from presidio_analyzer import PatternRecognizer, Pattern

# Definir un patrón regex para un ID interno (ej: ID-XX-123456)
internal_id_recognizer = PatternRecognizer(
    supported_entity="INTERNAL_ID",
    patterns=[
        Pattern(
            name="internal_id_regex",
            regex=r"ID-[A-Z]{2}-\d{6}",
            score=0.9  # Alta confianza
        )
    ]
)

# Añadirlo al engine y usarlo...

🧠 Uso con Modelos de Lenguaje (Nuevo en Versiones Recientes)
Presidio-Analyzer permite integrar LLMs para una detección más contextual y flexible de PII, algo muy útil para entidades no estándar o lenguaje informal .

Con Ollama (Modelos Locales):

from presidio_analyzer.predefined_recognizers import BasicLangExtractRecognizer

# Usa la configuración por defecto para Ollama
recognizer = BasicLangExtractRecognizer()

📊 Entidades Soportadas (Lista Parcial)
Presidio-Analyzer incluye una amplia gama de reconocedores predefinidos para diferentes idiomas y contextos .

Categoría	Entidades Soportadas
Datos Personales	PERSON, LOCATION, NATIONALITY, RELIGION, POLITICAL_ORIENTATION (NRP)
Contacto	EMAIL_ADDRESS, PHONE_NUMBER, IP_ADDRESS, URL
Financieros	CREDIT_CARD, IBAN_CODE, CRYPTO, US_BANK_NUMBER
Identificadores	US_SSN, US_PASSPORT, US_DRIVER_LICENSE, MEDICAL_LICENSE, UK_NHS
Tiempo	DATE_TIME

⚠️ Consideraciones Importantes
Precisión no Garantizada: Presidio es una herramienta automatizada. Es fundamental evaluar la calidad de las detecciones en tu caso de uso particular y ajustar los umbrales de confianza para minimizar falsos positivos y negativos .

Rendimiento: Para grandes volúmenes de datos, considera procesar en lote (batch processing) o desplegar el análisis como un servicio .

GPU: Actualmente, la aceleración por GPU (como CUDA para NVIDIA) está disponible, pero el soporte para MPS (Apple Silicon) es limitado, usando la CPU por defecto para operaciones de PyTorch .

📚 Recursos Adicionales
Repositorio de Ejemplos: Microsoft proporciona una serie de notebooks de Python que cubren desde el uso básico hasta la integración con servicios externos y el procesamiento de imágenes o PDFs .

Documentación Oficial: La referencia completa está disponible en el sitio de Microsoft Presidio .

Despliegue: Puedes desplegar presidio-analyzer como un servicio web (REST API) usando Docker, lo que facilita su integración en otras aplicaciones .

Integración con LLMs: La característica de LangExtract es especialmente útil para entornos donde se desea combinar la flexibilidad de un LLM con la robustez de un sistema de reglas .

