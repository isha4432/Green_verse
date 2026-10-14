from fastapi import APIRouter
from schemas.water_soil import CropRecommendationRequest, CropRecommendationResponse
from services.water_service import WaterService

router = APIRouter(prefix="/api/recommendations", tags=["Crop Recommendation"])

@router.post("/crops", response_model=CropRecommendationResponse)
async def recommend_crops(req: CropRecommendationRequest):
    return WaterService.recommend_crops(req)
