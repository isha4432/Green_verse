from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class IrrigationPlotInput(BaseModel):
    id: str
    name: str
    crop: str
    area: float = 1.0
    moisture: float = 45.0
    temp: float = 25.0
    growth_stage: int = 3
    priority: int = 1 # 1: normal, 2: high, 3: critical
    base_demand: float = 10.0 # in kL

class IrrigationOptimizeRequest(BaseModel):
    farm_id: Optional[str] = None
    plots: List[IrrigationPlotInput] = []
    water_budget: float = Field(45.0, description="Available water in kL")
    method: str = Field("classical_heuristic", description="classical_heuristic, linear_lp, or proportional")
    penalty_factor: float = 1.5

class PlotAllocation(BaseModel):
    plot_id: str
    name: str
    crop: str
    demand_kL: float
    allocated_kL: float
    deficit_kL: float
    coverage_pct: float
    stress_after: float

class IrrigationOptimizeResponse(BaseModel):
    allocations: List[PlotAllocation]
    total_water: float
    total_demand: float
    unmet_demand: float
    feasible: bool
    efficiency_score: float
    summary: str
