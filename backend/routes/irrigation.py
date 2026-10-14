from fastapi import APIRouter
from typing import List, Dict, Any
from schemas.irrigation import IrrigationOptimizeRequest, IrrigationOptimizeResponse
from schemas.quantum import QaoaRequest, OptimizationComparisonResponse
from services.irrigation_service import IrrigationService
from services.quantum_service import QuantumService
from database import db_manager

router = APIRouter(prefix="/api/irrigation", tags=["Irrigation Planner"])

@router.post("/optimize", response_model=IrrigationOptimizeResponse)
@router.post("/optimize/classical", response_model=IrrigationOptimizeResponse)
async def optimize_irrigation(req: IrrigationOptimizeRequest):
    return IrrigationService.optimize_allocation(req)

@router.post("/optimize/quantum", response_model=OptimizationComparisonResponse)
async def optimize_irrigation_quantum(req: QaoaRequest):
    return QuantumService.solve_qaoa(req)

@router.get("/plans", response_model=List[Dict[str, Any]])
async def get_irrigation_plans():
    return db_manager.memory_store.get("irrigation_plans", [])

@router.post("/plans")
async def save_irrigation_plan(plan: Dict[str, Any]):
    db_manager.memory_store.setdefault("irrigation_plans", []).insert(0, plan)
    return {"message": "Irrigation plan saved", "id": plan.get("id")}
