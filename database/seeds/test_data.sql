USE sicpc;

-- ============================================
-- USUARIOS
-- ============================================
INSERT INTO usuario (nombre, email, rol) VALUES
    ('Jorge Vasquez', 'jorge@sicpc-test.com', 'admin'),
    ('Ana Ledesma', 'ana@sicpc-test.com', 'operador'),
    ('Martin Rios', 'martin@sicpc-test.com', 'operador');

-- ============================================
-- CUENTAS DE CORREO
-- (credenciales_cifradas: placeholder de prueba, no es cifrado real todavia)
-- ============================================
INSERT INTO cuenta_correo (usuario_id, proveedor, direccion, credenciales_cifradas, activa) VALUES
    (1, 'gmail', 'soporte@empresa-test.com', 'CIFRADO_PLACEHOLDER_001', TRUE),
    (2, 'gmail', 'ventas@empresa-test.com', 'CIFRADO_PLACEHOLDER_002', TRUE),
    (3, 'outlook', 'contacto@empresa-test.com', 'CIFRADO_PLACEHOLDER_003', FALSE);

-- ============================================
-- REMITENTES (hashes de prueba, no son hashes reales de ningun email)
-- ============================================
INSERT INTO remitente (remitente_hash, primer_contacto, cantidad_correos) VALUES
    ('a1b2c3d4e5f60001aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0001', '2026-08-20 09:15:00', 4),
    ('a1b2c3d4e5f60002aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0002', '2026-08-22 14:30:00', 2),
    ('a1b2c3d4e5f60003aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0003', '2026-09-01 11:00:00', 1),
    ('a1b2c3d4e5f60004aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0004', '2026-09-03 08:45:00', 3);

-- ============================================
-- CORREOS
-- ============================================
INSERT INTO correo (cuenta_correo_id, remitente_hash, asignado_a, asunto_anonimizado, cuerpo_anonimizado, fecha_ingesta, categoria_predicha, confianza) VALUES
    (1, 'a1b2c3d4e5f60001aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0001', 2,
     'Reclamo urgente por [PERSONA] sobre pedido sin entregar',
     'Hola, soy [PERSONA]. Llevo 3 dias sin respuesta sobre mi pedido. Necesito solucion hoy mismo.',
     '2026-09-05 09:20:00', 'alta', 0.92),

    (1, 'a1b2c3d4e5f60002aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0002', 2,
     'Consulta sobre disponibilidad de stock',
     'Buenos dias, queria saber si tienen disponibilidad del producto para la semana que viene.',
     '2026-09-05 10:05:00', 'media', 0.78),

    (2, 'a1b2c3d4e5f60003aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0003', 3,
     'Newsletter mensual - Novedades de septiembre',
     'Te compartimos las novedades del mes, sin necesidad de respuesta.',
     '2026-09-06 08:00:00', 'baja', 0.95),

    (1, 'a1b2c3d4e5f60004aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0004', NULL,
     'Reunion propuesta para evaluar contrato',
     'Estimados, quisiera coordinar una reunion la semana que viene para revisar el contrato.',
     '2026-09-06 15:40:00', 'media', 0.55),

    (1, 'a1b2c3d4e5f60001aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff0001', 2,
     'RE: Reclamo urgente - sigue sin resolverse',
     'Escribo de nuevo porque el problema anterior sigue sin resolverse. Es urgente.',
     '2026-09-07 09:00:00', 'alta', 0.88);

-- ============================================
-- CORRECCIONES MANUALES (human-in-the-loop)
-- ============================================
INSERT INTO correccion_manual (correo_id, categoria_original, categoria_corregida, fecha_correccion) VALUES
    (4, 'media', 'alta', '2026-09-06 16:10:00');

-- ============================================
-- DERIVACIONES
-- ============================================
INSERT INTO derivacion (correo_id, de_usuario, a_usuario, nota, fecha_derivacion) VALUES
    (1, 1, 2, 'Paso este reclamo, es un cliente prioritario', '2026-09-05 09:25:00'),
    (4, 2, 3, 'Martin, podes encargarte de coordinar la reunion?', '2026-09-06 16:00:00');