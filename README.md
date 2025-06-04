# Proyecto TLSCH

Aplicación web en Django para gestionar trámites usando procesamiento de lenguaje natural. También integra autenticación mediante Clave Única.

## Instalación de los lenguajes

1. **Python**
   - Debian/Ubuntu:
     ```bash
     sudo apt update && sudo apt install python3 python3-venv
     ```
   - macOS:
     ```bash
     brew install python
     ```

2. **Django**
   - Se instala dentro del entorno virtual mediante pip:
     ```bash
     pip install django==5.2
     ```

3. **MariaDB**
   - Debian/Ubuntu:
     ```bash
     sudo apt install mariadb-server
     sudo service mariadb start
     ```
   - macOS:
     ```bash
     brew install mariadb
     brew services start mariadb
     ```

## Instalar dependencias
1. Crear y activar un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Instalar paquetes requeridos (incluye Django y spaCy):
   ```bash
   pip install -r requirements.txt
   ```
3. Crear un archivo `.env` en la raíz con las siguientes variables:
   ```
   HF_ACCESS_TOKEN=tu_token_de_hugging_face
   CLIENT_ID=tu_client_id
   CLIENT_SECRET=tu_client_secret
   ```

## Configurar la base de datos
Dentro de MariaDB crea la base y el usuario necesarios. Ingresa a la consola:
```bash
mysql -u root -p
```
y ejecuta:
```sql
CREATE DATABASE tlsch_db CHARACTER SET utf8mb4;
CREATE USER 'tlsch_user'@'localhost' IDENTIFIED BY '1qa2ws3edTlsch';
GRANT ALL PRIVILEGES ON tlsch_db.* TO 'tlsch_user'@'localhost';
FLUSH PRIVILEGES;
```

En `TLSCH/settings.py` se espera esta configuración:
```
'NAME': 'tlsch_db'
'USER': 'tlsch_user'
'PASSWORD': '1qa2ws3edTlsch'
'HOST': 'localhost'
'PORT': '3306'
```
Aplica las migraciones de Django:
```bash
python manage.py migrate
```

## Servidor de desarrollo
Con todo configurado, ejecuta:
```bash
python manage.py runserver
```
y abre `http://localhost:8000` en tu navegador.
