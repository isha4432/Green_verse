from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ExperimentBase(BaseModel):
    id: str
    name: str
    type: str # Optimization, Scenario, Irrigation, Quantum
    status: str
    date: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ExperimentCreate(BaseModel):
    name: str
    type: str
    status: Optional[str] = "Completed"
    metrics: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
