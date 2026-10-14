from fastapi import APIRouter
from schemas.water_soil import WaterCalculateRequest, WaterCalculateResponse
from services.water_service import WaterService

router = APIRouter(prefix="/api/water", tags=["Water Harvesting"])

@router.post("/calculate", response_model=WaterCalculateResponse)
async def calculate_water(req: WaterCalculateRequest):
    return WaterService.calculate_water_harvesting(req)
