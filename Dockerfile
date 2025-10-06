FROM python:3.11-slim
WORKDIR /app

# 1) Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
        gdal-bin libgdal-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 2) Copia el código (sin los rasters grandes)
COPY api/ api/
COPY requirements.txt .

# 3) Descargar GeoTIFF REALES desde un hosting público
#    — reemplaza las URLs por las tuyas —
RUN curl -L -o api/ndvi.tif        https://drive.google.com/uc?export=download&id=1rP8mHDvvcSuz8kWEr4OkQ1Ap7AxlPIjb \
 && curl -L -o api/ntl_norm.tif    https://drive.google.com/uc?export=download&id=1mZzexsB_6c4YUmi_UlCXc8uZr_uIQ_Fa \
 && curl -L -o api/slope_lima.tif  https://drive.google.com/uc?export=download&id=1ZNVvL28qsnegxkgoo6ysVm--RQDoURQ7

# 4) Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
