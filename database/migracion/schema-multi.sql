USE sicpc;

-- 1. Usuarios del sistema
CREATE TABLE IF NOT EXISTS usuario (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(150) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    rol         VARCHAR(20) NOT NULL DEFAULT 'operador',
    fecha_alta  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Cuentas de correo configurables (reemplaza al .env como fuente de verdad)
CREATE TABLE IF NOT EXISTS cuenta_correo (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id              INT NOT NULL,
    proveedor               VARCHAR(20) NOT NULL,
    direccion               VARCHAR(255) NOT NULL,
    credenciales_cifradas   TEXT NOT NULL,
    activa                  BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_alta              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cuenta_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- 3. Insertar un usuario "migración" para no romper filas existentes de correo
INSERT INTO usuario (nombre, email, rol)
VALUES ('Jorge (admin)', 'jlv0362@gmail.com', 'admin');

-- 4. Insertar la cuenta actual (Gmail) como primera fila configurada
--    (las credenciales reales se cargan despues, cifradas, via codigo)
INSERT INTO cuenta_correo (usuario_id, proveedor, direccion, credenciales_cifradas)
VALUES (
    (SELECT id FROM usuario WHERE email = 'jlv0362@gmail.com'),
    'gmail',
    'jlv0362@gmail.com',
    'PENDIENTE_CIFRAR'
);

-- 5. Extender la tabla correo existente
ALTER TABLE correo
    ADD COLUMN cuenta_correo_id INT NULL AFTER id,
    ADD COLUMN asignado_a INT NULL AFTER remitente_hash;

-- 6. Asignar los correos ya existentes a la cuenta/usuario migrados
UPDATE correo
SET cuenta_correo_id = (SELECT id FROM cuenta_correo LIMIT 1),
    asignado_a = (SELECT id FROM usuario WHERE email = 'jlv0362@gmail.com')
WHERE cuenta_correo_id IS NULL;

-- 7. Ahora sí, agregar las foreign keys (una vez que no hay NULLs sueltos)
ALTER TABLE correo
    ADD CONSTRAINT fk_correo_cuenta
        FOREIGN KEY (cuenta_correo_id) REFERENCES cuenta_correo(id),
    ADD CONSTRAINT fk_correo_usuario
        FOREIGN KEY (asignado_a) REFERENCES usuario(id);

-- 8. Tabla de derivaciones
CREATE TABLE IF NOT EXISTS derivacion (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    correo_id           INT NOT NULL,
    de_usuario          INT NOT NULL,
    a_usuario           INT NOT NULL,
    nota                TEXT,
    fecha_derivacion    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_derivacion_correo
        FOREIGN KEY (correo_id) REFERENCES correo(id),
    CONSTRAINT fk_derivacion_de
        FOREIGN KEY (de_usuario) REFERENCES usuario(id),
    CONSTRAINT fk_derivacion_a
        FOREIGN KEY (a_usuario) REFERENCES usuario(id)
);