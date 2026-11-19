1. La Estructura Sagrada de Docker
Antes de lanzarnos, recuerda esta sintaxis universal:

bash
docker [objeto] [acción] [opciones/flags] [argumento]
Objeto: container, image, volume, network, system.

Acción: run, ls, rm, build, pull, exec.

2. Comandos sobre IMÁGENES (El plano de construcción)
Comando	Explicación de Uso
docker images	Lista todas las imágenes descargadas localmente.
docker pull <imagen>:<tag>	Descarga una imagen del registro (Docker Hub) sin ejecutarla.
docker build -t <nombre> .	Construye una imagen a partir de un Dockerfile en el directorio actual (.).
docker push <usuario>/<imagen>	Sube tu imagen creada a un registro remoto.
docker rmi <id_imagen>	Elimina una imagen local (IMPORTANTE: no debe estar en uso por un contenedor).
docker tag <id> <nuevo_nombre>	Crea un alias (tag) para una imagen existente.
docker history <imagen>	Muestra las capas (layers) que componen la imagen.

🧪 Ejemplo Práctico (Crear, instalar y borrar imágenes):

# 1. INSTALAR (Descargar) una imagen oficial
docker pull nginx:alpine

# 2. VER las imágenes instaladas
docker images

# 3. CREAR (Construir) nuestra propia imagen personalizada
# Crear un archivo llamado 'Dockerfile' y luego construir:
docker build -t mi-web:v1 .

# 4. PONER UNA ETIQUETA (Tag) para subirla a Docker Hub
docker tag mi-web:v1 miusuario/mi-web:latest

# 5. BORRAR una imagen (forzadamente si es necesario)
docker rmi nginx:alpine
# Si da error porque un contenedor la usa:
docker rmi -f nginx:alpine  # (Forzado, no recomendado si el contenedor está activo)

3. Comandos sobre CONTENEDORES (La casa en ejecución)
Aquí está el corazón de Docker. Dominar esto es dominar el 80% de tu trabajo.

Comando	Explicación de Uso
docker run <imagen>	Crea y arranca un contenedor desde una imagen.
docker run -d <imagen>	Arranca en modo demonio (background).
docker run -it <imagen>	Arranca en modo interactivo (para usar bash dentro).
docker ps	Lista los contenedores activos (en ejecución).
docker ps -a	Lista todos los contenedores (activos + detenidos).
docker stop <id>	Detiene un contenedor en ejecución (gracia elegantemente).
docker kill <id>	Mata un contenedor de forma abrupta (fuerza bruta).
docker start <id>	Arranca un contenedor que estaba detenido.
docker restart <id>	Reinicia un contenedor.
docker rm <id>	Borra un contenedor detenido (libera espacio).
docker rm -f <id>	Borra un contenedor forzadamente (lo mata y lo borra).
docker exec -it <id> bash	Entra a un contenedor en ejecución para inspeccionarlo.
docker logs <id>	Muestra los logs (salida en consola) del contenedor.
docker cp <id>:/ruta/archivo .	Copia archivos desde dentro del contenedor al host.
🧪 Ejemplo Práctico (Crear, instalar, ejecutar y borrar contenedores):

bash
# 1. CREAR E INSTALAR (correr) un contenedor de Ubuntu, ejecutando bash dentro
docker run -it --name mi_ubuntu ubuntu:22.04 bash
# (Dentro del contenedor) apt update && apt install nano
# (Salir con Ctrl+D o escribiendo 'exit')

# 2. VER que el contenedor existe pero está detenido
docker ps -a | grep mi_ubuntu

# 3. INICIAR el contenedor detenido
docker start mi_ubuntu

# 4. EJECUTAR un comando dentro del contenedor mientras corre (sin entrar)
docker exec mi_ubuntu ls -la

# 5. Ver los logs de lo que hizo
docker logs mi_ubuntu

# 6. BORRAR definitivamente el contenedor (Primero hay que detenerlo o usar -f)
docker stop mi_ubuntu
docker rm mi_ubuntu

# Alternativa directa y violenta (mata y borra):
docker rm -f mi_ubuntu
4. Mapeo de Puertos y Volúmenes (La conexión con el exterior)
Comando	Explicación de Uso
-p 8080:80	Mapea el puerto 80 del contenedor al puerto 8080 de tu PC.
-P	Mapea todos los puertos expuestos a puertos aleatorios altos del host.
-v /host:/contenedor	Monta un directorio del host dentro del contenedor (Persistencia).
--mount type=bind,...	Forma más explícita y moderna de montar volúmenes.
🧪 Ejemplo con mapeos:

bash
# Levantar un servidor web Nginx, mapear puertos y montar mi código local
docker run -d --name web_server -p 8080:80 -v /home/usuario/mi_sitio:/usr/share/nginx/html nginx

# Ahora abre tu navegador en http://localhost:8080 y verás tu sitio
5. Comandos sobre VOLÚMENES (Persistencia de datos)
Los contenedores son efímeros; los volúmenes son eternos.

Comando	Explicación de Uso
docker volume create <nombre>	Crea un volumen gestionado por Docker.
docker volume ls	Lista todos los volúmenes.
docker volume inspect <vol>	Muestra detalles (dónde guarda los datos físicamente).
docker volume rm <vol>	Elimina un volumen (cuidado, datos perdidos).
docker volume prune	Elimina TODOS los volúmenes no utilizados por contenedores.
🧪 Ejemplo Práctico:

bash
# 1. CREAR un volumen
docker volume create base_datos_mysql

# 2. INSTALAR y CORRER MySQL usando ese volumen
docker run -d --name mysql_db -v base_datos_mysql:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=1234 mysql:8

# 3. BORRAR el contenedor (los datos siguen en el volumen)
docker rm -f mysql_db

# 4. BORRAR el volumen (ADIÓS DATOS)
docker volume rm base_datos_mysql
6. Gestión de Redes (La comunicación interna)
Comando	Explicación de Uso
docker network ls	Lista las redes.
docker network create mi_red	Crea una red personalizada (bridge) para aislar contenedores.
docker network connect red contenedor	Conecta un contenedor a una red.
docker network disconnect red contenedor	Desconecta.
docker network rm red	Elimina una red.
🧪 Ejemplo:

bash
# 1. CREAR una red interna
docker network create app_network

# 2. EJECUTAR dos contenedores en esa red (pueden comunicarse por su nombre)
docker run -d --name api --network app_network node:18
docker run -d --name base_datos --network app_network mongo

# 3. El contenedor 'api' puede hacer ping a 'base_datos' por su nombre, sin necesidad de IPs.
7. Comandos de Mantenimiento y Limpieza (El "Aseo del Ninja")
Comando	Explicación de Uso
docker system df	Muestra el espacio en disco usado por imágenes, contenedores y volúmenes.
docker system prune	PELIGRO: Elimina contenedores detenidos, redes no usadas e imágenes colgantes.
docker system prune -a	PELIGRO TOTAL: Elimina TODAS las imágenes no usadas por contenedores activos.
docker container prune	Elimina solo contenedores detenidos.
docker image prune	Elimina imágenes colgantes (dangling).
docker volume prune	Elimina volúmenes no usados.
8. Tabla de "Comandos Equivalentes" (Lo que un Dev usa a diario)
Acción Deseada	Comando Docker
"Necesito una terminal Linux rápida"	docker run -it --rm ubuntu bash (el --rm lo borra al salir).
"¿Qué está corriendo ahora mismo?"	docker ps
"Quiero ver las IPs de mis contenedores"	docker inspect -f '{{.Name}} - {{.NetworkSettings.IPAddress }}' $(docker ps -aq)
"Quiero borrar todo y empezar de cero"	docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker rmi $(docker images -q) -f
"Quiero ver los logs en tiempo real"	docker logs -f <id>
"Copio este archivo a mi contenedor"	docker cp ./mi_archivo.txt contenedor:/app/
💡 El Truco del Experto (Bonus Track)
El flag --rm es tu mejor amigo para pruebas.
Si estás probando algo y no quieres llenar tu sistema de contenedores detenidos, úsalo:

bash
# Este contenedor se borra SOLO cuando sale de la terminal
docker run -it --rm --name temporal alpine sh
Comando estrella para liberar espacio de forma segura:

bash
docker system prune -f --volumes
📝 Resumen Rápido (La chuleta para tu primera clase)
Crear y correr: docker run -d --name mi_app -p 80:80 nginx

Entrar a debuggear: docker exec -it mi_app bash

Parar y borrar: docker stop mi_app && docker rm mi_app

Construir imagen: docker build -t mi_version:v1 .

Limpiar todo: docker system prune -a