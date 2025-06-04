# Proyecto TLSCH

Este proyecto es una aplicacion web desarrollada con Django que emplea procesamiento de lenguaje natural con spaCy e integra autenticacion mediante Clave Unica.

## Requisitos
- Python 3.10 o superior
- virtualenv (puedes usar `python -m venv`)

## Instalación
1. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Instalar MariaDB en tu sistema.
   En Debian/Ubuntu puedes ejecutar:
   ```bash
   sudo apt update && sudo apt install mariadb-server
   sudo service mariadb start  # o mysql dependiendo de la distribución
   ```
   En macOS con Homebrew:
   ```bash
   brew install mariadb
   brew services start mariadb
   ```
4. Crear un archivo `.env` en la raíz con las credenciales necesarias:
   ```
   HF_ACCESS_TOKEN=tu_token_de_hugging_face
   CLIENT_ID=tu_client_id
   CLIENT_SECRET=tu_client_secret
   ```
   Los dos últimos valores corresponden a las credenciales de Clave Única.

## Configuración de la base de datos
Tras instalar MariaDB, crea la base y el usuario que la aplicación utilizará. Entra a la consola de MariaDB:
```bash
mysql -u root -p
```
Y ejecuta los siguientes comandos:
```sql
CREATE DATABASE tlsch_db CHARACTER SET utf8mb4;
CREATE USER 'tlsch_user'@'localhost' IDENTIFIED BY '1qa2ws3edTlsch';
GRANT ALL PRIVILEGES ON tlsch_db.* TO 'tlsch_user'@'localhost';
FLUSH PRIVILEGES;
```

En `TLSCH/settings.py` se definen las credenciales por defecto para MariaDB (utilizando el backend de Django para MySQL):
```
'NAME': 'tlsch_db'
'USER': 'tlsch_user'
'PASSWORD': '1qa2ws3edTlsch'
'HOST': 'localhost'
'PORT': '3306'
```
Asegúrate de crear la base y el usuario en tu servidor MySQL.
Luego aplica las migraciones ejecutando:
```bash
python manage.py migrate
```

## Servidor de desarrollo
Con el entorno virtual activo y todo instalado, inicia el servidor con:
```bash
python manage.py reset_db
python manage.py runserver
```
Visita `http://localhost:8000` para comprobar que la aplicación funciona.
