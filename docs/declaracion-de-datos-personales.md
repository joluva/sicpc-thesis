# Declaración de Manejo de Datos Personales

## 1. Objeto de esta declaración

Este documento formaliza el tratamiento de datos personales realizado en el
marco del proyecto de tesis **SICPC (Sistema Inteligente de Clasificación y
Priorización de Comunicaciones)**, en cumplimiento de la Ley 25.326 de
Protección de Datos Personales (Argentina).

## 2. Titularidad de los datos

Los datos personales procesados por el sistema provienen **exclusivamente de
una cuenta de correo electrónico personal del autor del proyecto**. El autor
es, por lo tanto, el titular de los datos tratados: no se procesan datos de
correo pertenecientes a terceros sin su consentimiento explícito.

## 3. Datos de terceros mencionados en los correos

Aunque la cuenta de correo es propia, los mensajes pueden contener referencias
a terceros (remitentes, destinatarios en copia, nombres mencionados en el
cuerpo del mensaje). Sobre estos datos se aplica lo siguiente:

- Se anonimizan mediante enmascarado de PII (nombres, correos, teléfonos,
  direcciones) antes de cualquier procesamiento o almacenamiento persistente.
- Los identificadores de remitente/destinatario se hashean, no se conservan
  en texto plano.
- No se realiza ninguna acción sobre estos datos más allá de su uso como
  insumo anonimizado para el entrenamiento y funcionamiento del modelo de
  clasificación.

## 4. Finalidad del tratamiento

Los datos se procesan con **fines exclusivamente académicos**, en el marco del
desarrollo de una tesis de Data Science. No se utilizan con fines comerciales,
no se comparten con terceros, y no se emplean para ningún propósito distinto
al desarrollo, evaluación y documentación del proyecto.

## 5. Consentimiento

- Al tratarse de una cuenta de correo propia, el autor otorga su propio
  consentimiento para el tratamiento de sus datos personales en el marco de
  este proyecto académico.
- No se solicita ni se requiere consentimiento de terceros, dado que no se
  procesan cuentas de correo ajenas y los datos de terceros que pudieran
  aparecer mencionados en los mensajes son anonimizados antes de su uso.

## 6. Derechos del titular

Como titular y único responsable de los datos tratados, el autor conserva en
todo momento la capacidad de:
- Acceder a los datos procesados
- Rectificar o corregir información
- Solicitar la eliminación total de los datos del proyecto
- Interrumpir el tratamiento en cualquier momento

## 7. Duración del tratamiento

Los datos se procesan durante el período de desarrollo de la tesis. Al
finalizar, se evaluará el borrado definitivo de los datos anonimizados
almacenados, o su anonimización adicional en caso de que algún material se
utilice como ejemplo en la documentación pública del proyecto (según lo
definido en el documento de gobierno de datos).

## 8. Referencia normativa

- Ley 25.326 de Protección de Datos Personales (Argentina)
- Este documento debe leerse en conjunto con `docs/gobierno-de-datos.md`, que
  detalla las medidas técnicas y organizativas aplicadas (anonimización,
  retención, control de acceso y seguridad).
EOF