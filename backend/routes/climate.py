from fastapi import APIRouter
from typing import List, Dict, Any
from schemas.climate import ClimateSimulateRequest, ClimateSimulateResponse
from services.climate_service import ClimateService
from database import db_manager

router = APIRouter(prefix="/api/climate", tags=["Climate Simulator"])

@router.post("/simulate", response_model=ClimateSimulateResponse)
async def simulate_climate(req: ClimateSimulateRequest):
    return ClimateService.simulate_scenario(req)

@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def get_climate_scenarios():
    return db_manager.memory_store.get("climate_scenarios", [])

@router.post("/scenarios")
async def save_climate_scenario(scenario: Dict[str, Any]):
    db_manager.memory_store.setdefault("climate_scenarios", []).insert(0, scenario)
    return {"message": "Scenario saved", "id": scenario.get("id")}
