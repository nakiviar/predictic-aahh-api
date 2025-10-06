# predictic-aahh-api

# 4Elementors · Informal-Settlement Risk API

FastAPI micro-service that predicts the **probability of informal-settlement presence (AA.HH.) in Lima, Peru** for any latitude/longitude pair.

The score fuses **three open Earth-observation layers**:

| Layer | Source | Why it matters |
|-------|--------|---------------|
| **NDVI** | Sentinel-2 / HLS | Vegetation loss → urban sprawl |
| **Night-time lights** | VIIRS Day/Night Band | Human activity density |
| **Slope** | SRTM 30 m | Hillside occupation risk |

The service returns a **probability \[0-1]** and a qualitative label **low / medium / high**, plus the raw feature values.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/predict?lat={lat}&lon={lon}` | Predict at a single point |
| `POST` | `/predict/batch` (GeoJSON FeatureCollection) | Predict multiple points |

Interactive docs: `GET /docs` (Swagger UI).

---

## Quick start (local)

```bash
git clone https://github.com/your-user/aahh-api.git
cd aahh-api
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000
# Open http://127.0.0.1:8000/docs
