# Fase 1: Imagen ligera de Python
FROM python:3.10-slim

# Evitar generación de archivos .pyc y asegurar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Directorio de trabajo en el contenedor
WORKDIR /app

# INSTALACIÓN DE DEPENDENCIAS GEOSPATIAL (Crítico para GeoPandas y validación de rutas)
# Instalamos dependencias de sistema necesarias para procesar GeoJSONs pesados
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables para que pip encuentre las librerías de C (necesario para fiona/pyproj)
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copiar requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend y datos
COPY . .

# Comando de inicio
# Cloud Run inyecta automáticamente la variable $PORT (usualmente 8080)
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
