# Dockerfile

# 1) Partimos de la imagen oficial de Python 3.10
FROM python:3.10-slim

# 2) Instalamos dependencias del SO necesarias para mysqlclient y compilación
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      default-libmysqlclient-dev \
      pkg-config \
      libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# 3) Prepara el directorio de trabajo
WORKDIR /app

# 4) Copia el requirements y actualiza pip
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install numpy==1.23.5
# 5) Instala las dependencias Python
RUN pip install -r requirements.txt

# 6) Copia el resto de tu código
COPY . .

# 7) Expone el puerto y lanza el servidor
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
