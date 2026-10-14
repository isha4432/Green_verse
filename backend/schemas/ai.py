from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CropStressRequest(BaseModel):
    plot_id: Optional[str] = None
    crop: str = "tomato"
    soil_moisture: float = 62.0
    temperature: float = 24.0
    rainfall: float = 16.0
    growth_stage: int = 3
    soil_ph: Optional[float] = 6.8
    organic_matter: Optional[float] = 2.1

class CropStressResponse(BaseModel):
    plot_id: Optional[str] = None
    crop: str = "tomato"
    risk: float = Field(..., description="Risk score between 0 and 100")
    category: str = Field(..., description="Risk status e.g. Good, Stressed, Critical")
    confidence: float = Field(..., description="Model confidence score")
    factors: List[str] = Field(default_factory=list, description="Key stress factors detected")
    recommendations: List[str] = Field(default_factory=list, description="Actionable mitigation recommendations")
    features_used: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = ""
    is_demo: bool = False
    model_version: str = "v1.2-crop-stress-engine"

class CropRecommendationRequest(BaseModel):
    soil_type: str = "siltloam"
    soil_moisture: float = 52.0
    temperature: float = 24.0
    rainfall: float = 620.0
    humidity: float = 55.0
    ph: float = 6.8
    nitrogen_n: float = 48.0
    phosphorus_p: float = 24.0
    potassium_k: float = 190.0
    crop_season: str = "rabi"
    location: str = "Semi-Arid Zone"
    water_availability: str = "Medium"
    crop_goal: str = "income" # income, water_saving, resilience, yield

class CropRecommendationItem(BaseModel):
    crop: str
    rank: int
    suitability_score: int
    confidence: float
    water_need: str
    season: str
    duration_days: int
    expected_yield_tons_ha: float
    contributing_factors: List[str]
    reasons: List[str]

class CropRecommendationResponse(BaseModel):
    recommendations: List[CropRecommendationItem]
    top_recommendation: str
    explanation: str
    model_info: Dict[str, Any]

class CultivationStageRequest(BaseModel):
    plot_id: str
    stage: int = Field(..., ge=1, le=7) # 1: Land Prep, 2: Seed Selection, 3: Sowing, 4: Crop Care, 5: Irrigation, 6: Pest Scouting, 7: Harvest
    stage_name: Optional[str] = None
    status: str = "active" # active, completed, delayed
    notes: Optional[str] = ""

class CultivationStageRecord(BaseModel):
    plot_id: str
    stage: int
    stage_name: str
    status: str
    notes: str
    timestamp: str

class MulticropZoneConfig(BaseModel):
    id: int
    crop_a: str
    crop_b: str
    mode: str = "strip" # strip, inter, border

class MulticropAnalyzeRequest(BaseModel):
    zones: List[Dict[str, Any]]
    water_budget: float = 45.0
    season: str = "rabi"
    soil_type: str = "siltloam"

class MulticropAnalyzeResponse(BaseModel):
    compatibility_score: int
    water_demand_kL: float
    resource_synergy: str
    pest_barrier_efficiency: str
    recommended_modifications: List[str]
    zone_assessments: List[Dict[str, Any]]

class AIChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class AIChatResponse(BaseModel):
    reply: str
    intent: str
    context_used: Dict[str, Any]
    timestamp: str
    model: str

