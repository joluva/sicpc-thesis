USE sicpc;

-- 1. Primero las tablas que dependen de otras (hijas)
DELETE FROM derivacion;
DELETE FROM correccion_manual;

-- 2. Correo depende de remitente, cuenta_correo y usuario
DELETE FROM correo;

-- 3. Ahora las que ya no tienen nada apuntándoles
DELETE FROM remitente;

-- 4. Cuentas de correo de prueba (dejamos la de la migración real, id=1, si corresponde)
DELETE FROM cuenta_correo WHERE id > 1;

-- 5. Usuarios de prueba (dejamos el usuario admin de la migración, id=1)
DELETE FROM usuario WHERE id > 1;

-- 6. Reiniciar los autoincrementales, para que el próximo insert empiece limpio
ALTER TABLE derivacion AUTO_INCREMENT = 1;
ALTER TABLE correccion_manual AUTO_INCREMENT = 1;
ALTER TABLE correo AUTO_INCREMENT = 1;
ALTER TABLE cuenta_correo AUTO_INCREMENT = 2;
ALTER TABLE usuario AUTO_INCREMENT = 2;