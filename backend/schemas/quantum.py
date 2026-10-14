from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QuboRequest(BaseModel):
    plots: List[Dict[str, Any]]
    water_budget: float
    penalty_weight: float = 2.0
    binary_bits_per_plot: int = 2

class QuboResponse(BaseModel):
    num_variables: int
    variable_names: List[str]
    linear_coefficients: Dict[str, float]
    quadratic_coefficients: Dict[str, float]
    matrix: List[List[float]]
    offset: float
    formulation_summary: str

class QaoaRequest(BaseModel):
    plots: List[Dict[str, Any]]
    water_budget: float
    p_layers: int = Field(2, ge=1, le=10)
    shots: int = Field(512, ge=100, le=4096)
    optimizer: str = "COBYLA"
    maxiter: int = 50
    backend_name: str = "aer_simulator"

class OptimizationComparisonResponse(BaseModel):
    status: str
    solution: Dict[str, Any]
    allocated_water: float
    objective: float
    feasible: bool
    constraint_violations: int
    runtime_ms: float
    shots: Optional[int] = None
    quantum_energy: Optional[float] = None
    backend: str
    is_quantum: bool
    approximation_ratio: Optional[float] = None
    disclaimer: str = "QAOA executed on Qiskit Aer statevector/qasm simulator. Classical baseline computed using exhaustive/heuristic solver."

class QuantumComparisonDualResponse(BaseModel):
    classical: OptimizationComparisonResponse
    quantum: OptimizationComparisonResponse
    qubo: Dict[str, Any]
    energy_gap: float
    runtime_speedup_ratio: float
    solutions_match: bool
    approximation_ratio: float
    summary: str

class QmlCropStressRequest(BaseModel):
    crop: str = "tomato"
    soil_moisture: float = 50.0
    temperature: float = 25.0
    rainfall: float = 12.0
    growth_stage: int = 2
    soil_ph: float = 6.8

class QmlCropStressResponse(BaseModel):
    crop: str
    qml_category: str
    stress_score: float
    quantum_fidelity: float
    circuit_qubits: int
    circuit_depth: int
    runtime_ms: float
    backend: str
    algorithm: str
    status: str
    disclaimer: str
    features_encoded: Dict[str, float]

