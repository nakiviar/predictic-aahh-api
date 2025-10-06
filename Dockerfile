# ---------------- Imagen base ----------------
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# ---------------- Dependencias OS ----------------
# gdal-bin + libgdal-dev   → Rasterio funciona
RUN apt-get update && apt-get install -y --no-install-recommends \
        gdal-bin libgdal-dev git-lfs ca-certificates curl && \
    rm -rf /var/lib/apt/lists/* 

# ---------------- Copiar código ----------------
COPY . .

# ----------- Instalar dependencias Python -------
RUN pip install --no-cache-dir -r requirements.txt

# -------------- Puerto de exposición ------------
EXPOSE 8000

# ---------------- Comando final -----------------
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
