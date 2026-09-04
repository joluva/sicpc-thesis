-- SICPC — Esquema de base de datos
-- Basado en el diagrama entidad-relación: Remitente, Correo, Correccion_Manual

CREATE DATABASE IF NOT EXISTS sicpc
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sicpc;

-- Tabla: remitentes (hasheados, nunca la identidad real)
CREATE TABLE IF NOT EXISTS remitente (
    remitente_hash   VARCHAR(64) PRIMARY KEY,
    primer_contacto  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cantidad_correos INT NOT NULL DEFAULT 0
);

-- Tabla: correos ya anonimizados y clasificados
CREATE TABLE IF NOT EXISTS correo (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    remitente_hash      VARCHAR(64) NOT NULL,
    asunto_anonimizado  VARCHAR(500),
    cuerpo_anonimizado  TEXT,
    fecha_ingesta       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    categoria_predicha  VARCHAR(20) NOT NULL,
    confianza           FLOAT NOT NULL,
    CONSTRAINT fk_correo_remitente
        FOREIGN KEY (remitente_hash) REFERENCES remitente(remitente_hash),
    INDEX idx_categoria (categoria_predicha),
    INDEX idx_fecha (fecha_ingesta)
);

-- Tabla: historial de correcciones manuales (human-in-the-loop)
CREATE TABLE IF NOT EXISTS correccion_manual (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    correo_id             INT NOT NULL,
    categoria_original    VARCHAR(20) NOT NULL,
    categoria_corregida   VARCHAR(20) NOT NULL,
    fecha_correccion      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_correccion_correo
        FOREIGN KEY (correo_id) REFERENCES correo(id)
);