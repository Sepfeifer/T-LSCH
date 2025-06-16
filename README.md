````markdown
<!-- Badges -->
[![Django](https://img.shields.io/badge/Django-5.2-green)]()
[![Python](https://img.shields.io/badge/Python-3.10-blue)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey)]()

# Proyecto Traductor de Texto a Lengua de Señas Chilena

## 📖 Índice
- [Descripción](#descripción)  
- [Características](#características)  
- [Tecnologías](#tecnologías)  
- [Arquitectura](#arquitectura)  
- [Instalación](#instalación)  
- [Configuración](#configuración)  
- [Uso](#uso)  
- [Estructura de carpetas](#estructura-de-carpetas)  
- [Contribuir](#contribuir)  
- [Licencia](#licencia)  

---

## 🔍 Descripción
Este proyecto es una aplicación web en **Django** que traduce texto en español a **Lengua de Señas Chilena** utilizando:
1. Un servicio de IA para resumir/extractar keywords.  
2. Una base de datos de vídeos pregrabados asociados a cada término.  

---

## ✨ Características
- **Autenticación** con Django + ClaveÚnica.  
- **Roles de usuario**:  
  - Administrador: gestión de usuarios y vídeos.  
  - Funcionario: acceso a la herramienta de traducción.  
  - Visitante: contenido público.  
- **Extracción de keywords** con spaCy.  
- **Búsqueda inteligente de vídeos** (incluye sinónimos WordNet).  
- **Deletreo de nombres propios** (separando letra a letra).  

---

## 🛠️ Tecnologías
- **Framework**: Django 5.2  
- **Base de datos**: MySQL / MariaDB  
- **Entorno**: Python 3.10+  
- **Librerías IA/NLP**:  
  - `spacy` + `es_core_news_sm`  
  - `nltk` + WordNet (`omw-1.4`, `wordnet`)  

---

## 🏗️ Arquitectura
- **Apps**:  
  - `core/` → modelos, vistas, formularios, servicios.  
  - `claveunica_auth/` → integración con ClaveÚnica.  
- **Servicios** (`core/services/`):  
  - `spacy_extractor.py`  
  - `synonym_service.py`  
- **Modelos**:  
  - `Usuario` (extiende `AbstractUser`, añade `rol`).  
  - `Video` (nombre, tema, url_código, fecha_creación).  

---

## 🚀 Instalación

1. Clona el repositorio:  
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo
````

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Unix
   .venv\Scripts\activate      # Windows
   ```
3. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```
4. Configura variables de entorno en `.env` (usa `django-environ`):

   ```
   DATABASE_URL=mysql://user:pass@host:port/dbname
   SECRET_KEY=tu_secret_key
   ```
5. Aplica migraciones y crea superusuario:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. Ejecuta el servidor:

   ```bash
   python manage.py runserver
   ```

---

## ⚙️ Configuración

* **spaCy**:

  ```bash
  python -m spacy download es_core_news_sm
  ```
* **NLTK** (WordNet):

  ```python
  import nltk
  nltk.download('omw-1.4')
  nltk.download('wordnet')
  ```

---

## 🎮 Uso

* Accede a `/admin/`
* Crea usuarios y registra vídeos con su `tema` y `url_código`.
* Como funcionario, ve a `/funcionario/traductor/`, ingresa un texto y obtén los vídeos traducidos en señas.

---

## 📂 Estructura de carpetas

```
├── TLSCH/
│   ├── core/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── services/
│   │       ├── spacy_extractor.py
│   │       └── synonym_service.py
│   ├── claveunica_auth/
│   ├── templates/
│   ├── static/
│   └── settings.py
├── requirements.txt
├── .env
└── manage.py
```

---
## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
