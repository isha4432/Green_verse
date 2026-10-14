from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class WaterCalculateRequest(BaseModel):
    rainfall: float = Field(25.0, description="Rainfall in mm")
    catchment_area: float = Field(150.0, description="Catchment roof area in m²")
    runoff_coefficient: float = Field(0.85, ge=0.0, le=1.0)
    storage_capacity: float = Field(12.0, description="Tank capacity in kL / m³")
    irrigation_demand: float = Field(6.0, description="Field irrigation demand in kL")
    first_flush_mm: float = 0.5

class WaterCalculateResponse(BaseModel):
    harvested_water: float
    first_flush_diverted: float
    net_inflow: float
    stored_water: float
    irrigation_supplied: float
    overflow: float
    recharge_potential: float
    storage_utilization_pct: float
    cycles_analyzed: int = 1

class SoilAnalyzeRequest(BaseModel):
    farm_id: Optional[str] = None
    texture: str = "siltloam"
    ph: float = 6.8
    moisture: float = 52.0
    drainage: str = "Good"
    organic_matter: float = 2.1
    slope: float = 4.0
    crop: str = "tomato"

class SoilAnalyzeResponse(BaseModel):
    texture: str
    ph: float
    moisture: float
    drainage: str
    organic_matter: float
    slope: float
    crop: str
    suitability_score: float
    fertility_index: str
    recommendations: List[str]
    amendments: List[str]

class CropRecommendationRequest(BaseModel):
    soil: str = "siltloam"
    ph: float = 6.8
    temperature: float = 24.0
    rainfall: float = 620.0
    season: str = "rabi"
    water_availability: str = "Medium"
    farm_area: float = 1.2
    crop_goal: str = "income" # income, yield, water_saving, resilience

class CropRecommendationItem(BaseModel):
    crop: str
    score: int
    water_need: str
    season: str
    duration_days: int
    expected_yield_tons_ha: float
    reasons: List[str]

class CropRecommendationResponse(BaseModel):
    recommendations: List[CropRecommendationItem]
    top_recommendation: str
    explanation: str
    is_demo: bool = True
