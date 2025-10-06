# api/main.py
import os, numpy as np, rasterio
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any

# ── Rutas de los GeoTIFF ─────────────────────────────────
DIR = os.path.dirname(__file__)
NDVI_PATH   = os.path.join(DIR, "ndvi.tif")        # −1 … 1
NTL_PATH    = os.path.join(DIR, "ntl_norm.tif")    # 0 … 100  (o 0 … 1)
SLOPE_PATH  = os.path.join(DIR, "slope_lima.tif")  # 0 … 90  (°)

# BBox de Lima (aprox.)
AOI = (-77.25, -12.45, -76.75, -11.75)

def in_aoi(lat, lon):
    xmin, ymin, xmax, ymax = AOI
    return xmin <= lon <= xmax and ymin <= lat <= ymax

# ── Abrir rasters una sola vez ───────────────────────────
ndvi_ds   = rasterio.open(NDVI_PATH)
ntl_ds    = rasterio.open(NTL_PATH)
slope_ds  = rasterio.open(SLOPE_PATH)

def sample(ds, lat, lon):
    try:
        r, c = ds.index(lon, lat)
        v = ds.read(1)[r, c]
        if ds.nodata is not None and v == ds.nodata:
            v = np.nan
    except Exception:
        v = np.nan
    return float(v)

# ── Score heurístico (ajusta pesos si deseas) ────────────
def calc_score(ndvi, ntl, slope):
    if np.isnan(ndvi) or np.isnan(ntl) or np.isnan(slope):
        return 0.0
    ndvi_n  = (ndvi + 1) / 2                # −1..1 → 0..1
    ntl_n   = ntl / (100.0 if ntl > 1 else 1.0)  # 0..100 o 0..1
    slope_n = min(slope / 30.0, 1.0)        # normaliza 0–30°
    # Pesos: NDVI bajo (0.4) + NTL alto (0.4) + Slope (0.2)
    return 0.4*(1 - ndvi_n) + 0.4*ntl_n + 0.2*slope_n

def label(p):
    return "alto" if p >= 0.66 else "medio" if p >= 0.33 else "bajo"

# ── FastAPI ──────────────────────────────────────────────
app = FastAPI(title="AAHH Predictor Lima", version="0.1")

class OnePred(BaseModel):
    lat: float
    lon: float
    probabilidad: float = Field(..., ge=0, le=1)
    clase: str
    features: Dict[str, float]

class BatchIn(BaseModel):
    type: str
    features: List[Dict[str, Any]]

class BatchOut(BaseModel):
    results: List[OnePred]


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/predict", response_model=OnePred)
def predict(lat: float = Query(...), lon: float = Query(...)):
    if not in_aoi(lat, lon):
        raise HTTPException(400, "Coordenadas fuera del área de Lima")
    ndvi  = sample(ndvi_ds,  lat, lon)
    ntl   = sample(ntl_ds,   lat, lon)
    slope = sample(slope_ds, lat, lon)
    p = round(calc_score(ndvi, ntl, slope), 3)
    return {
        "lat": lat,
        "lon": lon,
        "probabilidad": p,
        "clase": label(p),
        "features": {
            "ndvi":  round(ndvi, 3),
            "ntl":   round(ntl, 2),
            "slope": round(slope, 1)
        }
    }

@app.post("/predict/batch", response_model=BatchOut)
def predict_batch(batch: BatchIn):
    out = []
    for feat in batch.features:
        lon, lat = feat["geometry"]["coordinates"]
        if in_aoi(lat, lon):
            out.append(predict(lat=lat, lon=lon))
    return {"results": out}
