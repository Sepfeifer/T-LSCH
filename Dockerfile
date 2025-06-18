# Dockerfile

FROM python:3.10-slim

# Instala dependencias del sistema
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      default-libmysqlclient-dev \
      pkg-config \
      libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# Prepara el directorio de trabajo
WORKDIR /app

# Copia requirements y actualiza pip
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install numpy==1.23.5
RUN pip install -r requirements.txt

# Copia el resto del código
COPY . .

# Establece una ruta común para datos nltk
ENV NLTK_DATA=/usr/share/nltk_data
RUN mkdir -p /usr/share/nltk_data \
 && python -m nltk.downloader -d /usr/share/nltk_data wordnet omw-1.4

# Exponer puerto y ejecutar
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
