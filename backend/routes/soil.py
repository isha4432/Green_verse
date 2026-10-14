from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from schemas.water_soil import SoilAnalyzeRequest, SoilAnalyzeResponse
from services.water_service import WaterService
from database import db_manager

router = APIRouter(prefix="/api/soil", tags=["Soil & Land Health"])

DEFAULT_SOIL_RECORDS = [
    {"id": "SOIL-P1", "plot_id": "P-1", "texture": "siltloam", "ph": 6.8, "moisture": 62.0, "drainage": "Good", "organic_matter": 2.4, "slope": 3.0, "n_ppm": 55, "p_ppm": 28, "k_ppm": 210},
    {"id": "SOIL-P2", "plot_id": "P-2", "texture": "clayloam", "ph": 7.2, "moisture": 48.0, "drainage": "Moderate", "organic_matter": 1.8, "slope": 5.0, "n_ppm": 42, "p_ppm": 20, "k_ppm": 180},
    {"id": "SOIL-P3", "plot_id": "P-3", "texture": "sandyloam", "ph": 6.5, "moisture": 55.0, "drainage": "Good", "organic_matter": 2.1, "slope": 2.0, "n_ppm": 60, "p_ppm": 32, "k_ppm": 195}
]

if not db_manager.memory_store.get("soil_records"):
    db_manager.memory_store["soil_records"] = list(DEFAULT_SOIL_RECORDS)

@router.get("/{plot_id}")
async def get_plot_soil(plot_id: str):
    records = db_manager.memory_store.get("soil_records", [])
    for r in records:
        if r.get("plot_id") == plot_id or r.get("id") == plot_id:
            return r
    return {
        "id": f"SOIL-{plot_id}",
        "plot_id": plot_id,
        "texture": "siltloam",
        "ph": 6.8,
        "moisture": 52.0,
        "drainage": "Good",
        "organic_matter": 2.1,
        "slope": 4.0,
        "nitrogen_ppm": 48.0,
        "phosphorus_ppm": 24.0,
        "potassium_ppm": 190.0,
        "salinity_ec": 0.45
    }

@router.post("")
async def create_soil_record(record: Dict[str, Any]):
    new_id = f"SOIL-{len(db_manager.memory_store['soil_records']) + 1}"
    record["id"] = record.get("id", new_id)
    db_manager.memory_store["soil_records"].insert(0, record)
    return record

@router.put("/{record_id}")
async def update_soil_record(record_id: str, record: Dict[str, Any]):
    for i, r in enumerate(db_manager.memory_store["soil_records"]):
        if r.get("id") == record_id or r.get("plot_id") == record_id:
            db_manager.memory_store["soil_records"][i].update(record)
            return db_manager.memory_store["soil_records"][i]
    raise HTTPException(status_code=404, detail="Soil record not found")

@router.post("/analyze", response_model=SoilAnalyzeResponse)
async def analyze_soil(req: SoilAnalyzeRequest):
    return WaterService.analyze_soil(req)
