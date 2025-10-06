# Imagen base ligera con Python 3.11
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema para GDAL / Rasterio
RUN apt-get update && apt-get install -y \
        gdal-bin libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar código y requisitos
COPY api/ api/
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Puerto expuesto
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
