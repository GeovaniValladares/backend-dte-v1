# Usamos una versión específica de Debian (Bookworm) para mayor estabilidad
FROM python:3.9-slim-bookworm

# 1. Instalar dependencias de sistema
# Hemos corregido el nombre de libgdk-pixbuf-2.0-0
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Preparar carpeta de trabajo
WORKDIR /app

# 3. Copiar archivos del proyecto
COPY . /app

# 4. Instalar librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Exponer el puerto
EXPOSE 10000

# 6. Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
