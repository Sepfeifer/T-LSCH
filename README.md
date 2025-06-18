El Proyecto Traductor de Texto a Lengua de Señas Chilena es una aplicación en Django cuya misión es permitir a funcionarios convertir textos en español a una secuencia de vídeos de señas pregrabados. No genera animaciones en tiempo real ni sustituye a un intérprete profesional, sino que funciona como herramienta de apoyo básica para mejorar la accesibilidad.
A continuación está el contenido completo del README en formato Markdown

<!-- Badges -->
[![Django](https://img.shields.io/badge/Django-5.2-green)]()
[![Python](https://img.shields.io/badge/Python-3.10-blue)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey)]()

# Proyecto Traductor de Texto a Lengua de Señas Chilena

## 📖 Índice
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

## ✅ ¿Qué hace?
1. Recibe un texto en español.  
2. Extrae verbos, sustantivos y expresiones clave con IA (spaCy).  
3. Busca vídeos pregrabados de señas (o usa sinónimos de WordNet).  
4. Deletrea nombres propios y números letra por letra.  
5. Devuelve un **playlist** de vídeos en el orden original.  
6. Permite reportar términos faltantes para ampliar la librería.

---

## ❌ ¿Qué NO hace?
- No genera vídeos o animaciones en tiempo real.  
- No traduce construcciones gramaticales complejas.  
- No reemplaza a un intérprete profesional.  
- No almacena permanentemente los textos ingresados.

---

## ✨ Características
- Autenticación con Django y ClaveÚnica.  
- Roles: **Administrador**, **Funcionario**, **Visitante**.  
- Extracción de keywords y deletreo con spaCy.  
- Búsqueda inteligente con sinónimos de WordNet.  
- Reporte y seguimiento de vídeos faltantes.  
- Generación de informes de uso por tema.

---

 ## 🛠️ Tecnologías
- **Django 5.2**, **Python 3.10+**  
- **MySQL / MariaDB**  
- **spaCy** (`es_core_news_sm`), **NLTK** (`omw-1.4`, `wordnet`)  
- **django-environ**, **mysqlclient**

---

## 🏗️ Arquitectura
- **Apps**  
  - `core/`: Modelos, vistas, formularios, servicios de traducción.  
  - `claveunica_auth/`: Integración con ClaveÚnica.  
- **Servicios NLP**  
  - `spacy_extractor.py`  
  - `synonym_service.py`  
- **Modelos**  
  - `Usuario`, `Tema`, `Video`, `Tramite`, `Informe`, `MissingVideoReport`

---

## 🚀 Instalación
```bash
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
python -m venv .venv
source .venv/bin/activate    # Unix/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt

⚙️ Configuración
Descarga componentes NLP:
python -m spacy download es_core_news_sm
python - <<EOF
import nltk
nltk.download('omw-1.4')
nltk.download('wordnet')
EOF

🎮 Uso
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Admin: /admin/ → usuarios, temas, videos

Funcionario: /funcionario/traductor/ → ingresa texto y obtén playlist

Visitante: /reportes/ → reporta términos faltantes

📂 Estructura de carpetas
text
Copiar
Editar
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


🤝 Contribuir
git checkout -b feature/mi-nueva-funcionalidad
# realizar cambios…
git commit -m "Descripción de mi aporte"
git push origin feature/mi-nueva-funcionalidad
# abre un Pull Request en GitHub

Este proyecto está bajo la Licencia MIT.
Consulta el archivo LICENSE para más detalles.
Copiar
Editar
