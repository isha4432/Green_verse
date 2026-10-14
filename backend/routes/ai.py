from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from schemas.ai import (
    CropStressRequest, CropStressResponse,
    CropRecommendationRequest, CropRecommendationResponse,
    CultivationStageRequest, CultivationStageRecord,
    MulticropAnalyzeRequest, MulticropAnalyzeResponse,
    AIChatRequest, AIChatResponse
)
from services.ai_service import AIService
from database import db_manager

router = APIRouter(prefix="/api", tags=["AI & Agronomic Intelligence"])

@router.post("/ai/chat", response_model=AIChatResponse)
async def chat_with_ai(req: AIChatRequest):
    return AIService.chat(req)


@router.post("/ai/crop-stress", response_model=CropStressResponse)
@router.post("/ai/crop-stress/predict", response_model=CropStressResponse)
async def predict_crop_stress(req: CropStressRequest):
    return AIService.predict_crop_stress(req)

@router.get("/ai/history/{plot_id}", response_model=List[Dict[str, Any]])
@router.get("/ai/history", response_model=List[Dict[str, Any]])
async def get_ai_history(plot_id: Optional[str] = None):
    return AIService.get_crop_stress_history(plot_id or "")

@router.post("/ai/crop-recommendation", response_model=CropRecommendationResponse)
@router.post("/ai/crop-recommend/recommend", response_model=CropRecommendationResponse)
@router.post("/recommendations/crops", response_model=CropRecommendationResponse)
async def recommend_crops(req: CropRecommendationRequest):
    return AIService.recommend_crops(req)

@router.post("/cultivation/{plot_id}/stage", response_model=CultivationStageRecord)
async def set_cultivation_stage(plot_id: str, req: CultivationStageRequest):
    req.plot_id = plot_id
    return AIService.record_cultivation_stage(req)

@router.get("/cultivation/{plot_id}/history", response_model=List[Dict[str, Any]])
async def get_cultivation_history(plot_id: str):
    return AIService.get_cultivation_history(plot_id)

@router.post("/multicrop/analyze", response_model=MulticropAnalyzeResponse)
async def analyze_multicrop(req: MulticropAnalyzeRequest):
    return AIService.analyze_multicrop(req)

@router.get("/multicrop/plans", response_model=List[Dict[str, Any]])
async def get_multicrop_plans():
    return db_manager.memory_store.get("multicrop_plans", [])

@router.post("/multicrop/plans")
async def save_multicrop_plan(plan: Dict[str, Any]):
    db_manager.memory_store.setdefault("multicrop_plans", []).insert(0, plan)
    return {"message": "Plan saved", "id": plan.get("id")}
