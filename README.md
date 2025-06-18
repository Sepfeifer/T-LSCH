````markdown
<!-- Badges -->
[![Django](https://img.shields.io/badge/Django-5.2-green)]()
[![Python](https://img.shields.io/badge/Python-3.10-blue)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey)]()

# Proyecto Traductor de Texto a Lengua de Señas Chilena

## 📖 Índice
- [Descripción](#descripción)  
- [¿Qué hace?](#qué-hace)  
- [¿Qué NO hace?](#qué-no-hace)  
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
Proyecto Traductor de Texto a Lengua de Señas Chilena es una aplicación web en **Django** que facilita la comunicación con personas sordas, convirtiendo textos en español a videos pregrabados de señas chilenas.

---

## ✅ ¿Qué hace?
1. **Toma un texto** en español ingresado por el usuario.  
2. **Extrae** verbos infinitivos, sustantivos y expresiones clave con IA/NLP.  
3. **Busca** videos en la base de datos que correspondan a cada término (o a sus sinónimos).  
4. **Deletrea** nombres propios y números letra por letra si están entre comillas.  
5. **Muestra** al final un playlist de videos en el orden de las palabras procesadas.  
6. **Permite reportar** términos “faltantes” para ampliar la librería de videos.

---

## ❌ ¿Qué NO hace?
- **No genera** videos en tiempo real ni animaciones automáticas.  
- **No traduce** gramática completa (sintaxis o construcciones complejas).  
- **No sustituye** a un intérprete profesional; sirve como apoyo básico.  
- **No almacena** permanentemente textos ingresados (solo el playlist y reportes).

---

## ✨ Características
- **Autenticación** con Django y ClaveÚnica.  
- **Roles de usuario**:  
  - **Administrador**: crea/edita/baja usuarios y videos.  
  - **Funcionario**: traduce textos, ve reportes y genera informes.  
  - **Visitante**: accede a contenido público y reporta términos faltantes.  
- **Extracción de keywords** con spaCy (modelo `es_core_news_sm`).  
- **Búsqueda inteligente** de videos: usa sinónimos de WordNet si no hay coincidencia exacta.  
- **Deletreo** automático de nombres y números.  
- **Reportes** de vídeos faltantes y generación de informes.

---

## 🛠️ Tecnologías
- **Framework**: Django 5.2  
- **Python**: 3.10+  
- **Base de datos**: MySQL / MariaDB  
- **NLP / IA**:  
  - `spacy` + `es_core_news_sm`  
  - `nltk` + WordNet (`omw-1.4`, `wordnet`)  
- **Otros**: `django-environ`, `mysqlclient`

---

## 🏗️ Arquitectura
- **Apps**:  
  - `core/` → modelos, vistas, formularios, servicios de traducción.  
  - `claveunica_auth/` → integración con ClaveÚnica.  
- **Servicios NLP** (`core/services/`):  
  - `spacy_extractor.py` → extracción de keywords y deletreo.  
  - `synonym_service.py` → generación de sinónimos con WordNet.  
- **Modelos principales**: `Usuario`, `Tema`, `Video`, `Tramite`, `Informe`, `MissingVideoReport`.

---

## 🚀 Instalación

1. **Clona el repositorio**  
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo
````

2. **Crea y activa un entorno virtual**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Unix/macOS
   .venv\Scripts\activate      # Windows
   ```
3. **Instala dependencias**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configura tu `.env`** (con `django-environ`):

   ```dotenv
   DATABASE_URL=mysql://user:pass@host:port/dbname
   SECRET_KEY=tu_secret_key
   ```
5. **Aplica migraciones y crea superusuario**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. **Ejecuta el servidor**

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

1. **Admin**

   * Accede a `/admin/`
   * Crea usuarios, temas y videos (asociados a uno o varios temas).
2. **Funcionario**

   * Accede a `/funcionario/traductor/`
   * Ingresa tu frase, envía y ve los videos en señas en el orden de las keywords.
3. **Visitante**

   * Puede ver contenido público y **reportar** keywords faltantes en `/reportes/`.

---

## 📂 Estructura de carpetas

```
TLSCH/
├── core/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── services/
│       ├── spacy_extractor.py
│       └── synonym_service.py
├── claveunica_auth/
├── templates/
│   ├── admin_usuario/
│   ├── funcionario/
│   └── traductor.html
├── static/
└── settings.py
manage.py
requirements.txt
.env
```

---

## 🤝 Contribuir

1. Haz **fork** del repositorio.
2. Crea una rama:

   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```
3. Realiza tus cambios y haz **commit**:

   ```bash
   git commit -m "Agrega descripción clara de X"
   ```
4. Empuja tu rama y abre un **Pull Request**.

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Consulta [LICENSE](LICENSE) para más detalles.

```
```
