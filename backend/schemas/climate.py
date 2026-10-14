from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ClimateSimulateRequest(BaseModel):
    farm_id: Optional[str] = "farm-mixed-default"
    temperature_delta: float = Field(0.0, description="Temperature change in °C")
    rainfall_change: float = Field(0.0, description="Rainfall change in %")
    soil_moisture_delta: float = Field(0.0, description="Soil moisture change in pts")
    water_change: float = Field(0.0, description="Water budget change in %")
    plots: Optional[List[Dict[str, Any]]] = None

class SimulatedPlot(BaseModel):
    id: str
    name: str
    crop: str
    baseline_moisture: float
    simulated_moisture: float
    baseline_temp: float
    simulated_temp: float
    stress_risk: float
    status: str
    water_demand_kL: float

class ClimateSimulateResponse(BaseModel):
    scenario: Dict[str, Any]
    plots: List[SimulatedPlot]
    mean_risk: float
    water_demand: float
    water_available: float
    shortage: float
    resilience_score: float
    is_demo: bool = True
