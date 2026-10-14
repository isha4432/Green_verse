from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from schemas.quantum import (
    QuboRequest, QuboResponse, QaoaRequest, OptimizationComparisonResponse, QuantumComparisonDualResponse,
    QmlCropStressRequest, QmlCropStressResponse
)
from services.quantum_service import QuantumService

router = APIRouter(prefix="/api", tags=["Quantum Lab & Optimization"])

@router.post("/quantum/qubo", response_model=QuboResponse)
async def generate_qubo(req: QuboRequest):
    qubo_data = QuantumService.build_qubo_formulation(
        plots=req.plots,
        water_budget=req.water_budget,
        penalty_weight=req.penalty_weight
    )
    return QuboResponse(
        num_variables=qubo_data["num_variables"],
        variable_names=qubo_data["variable_names"],
        linear_coefficients=qubo_data["linear_coefficients"],
        quadratic_coefficients=qubo_data["quadratic_coefficients"],
        matrix=qubo_data["matrix"],
        offset=qubo_data["offset"],
        formulation_summary=qubo_data["formulation_summary"]
    )

@router.post("/quantum/qaoa", response_model=OptimizationComparisonResponse)
async def run_qaoa(req: QaoaRequest):
    return QuantumService.solve_qaoa(req)

@router.post("/optimization/classical", response_model=OptimizationComparisonResponse)
async def run_classical_optimization(req: QaoaRequest):
    return QuantumService.solve_classical(plots=req.plots, water_budget=req.water_budget)

@router.post("/quantum/compare", response_model=QuantumComparisonDualResponse)
async def compare_quantum_classical(req: QaoaRequest):
    return QuantumService.compare_quantum_classical(req)

@router.post("/quantum/qml/predict", response_model=QmlCropStressResponse)
@router.post("/quantum/qml/classify", response_model=QmlCropStressResponse)
async def classify_crop_stress_qml(req: QmlCropStressRequest):
    return QuantumService.classify_crop_stress_qml(req)

