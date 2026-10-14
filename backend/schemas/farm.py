from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SensorSchema(BaseModel):
    id: str
    x: float
    y: float
    type: str

class TreeSchema(BaseModel):
    id: str
    x: float
    y: float
    kind: Optional[str] = "tree"

class PipeSchema(BaseModel):
    id: str
    pts: List[Dict[str, float]]

class ReservoirSchema(BaseModel):
    x: float
    y: float
    w: float
    h: float

class PlotBase(BaseModel):
    id: Optional[str] = None
    plot_id: Optional[str] = None
    farm_id: Optional[str] = None
    name: str
    plot_name: Optional[str] = None
    crop: str
    condition: str = "good"
    stage: int = 2
    crop_stage: Optional[int] = 2
    moisture: float = 50.0
    temp: float = 24.0
    rain: float = 15.0
    x: float = 6.0
    y: float = 6.0
    w: float = 20.0
    h: float = 15.0
    area: Optional[float] = None
    irrig: str = "drip"

class PlotCreate(PlotBase):
    pass

class PlotUpdate(BaseModel):
    name: Optional[str] = None
    crop: Optional[str] = None
    condition: Optional[str] = None
    stage: Optional[int] = None
    moisture: Optional[float] = None
    temp: Optional[float] = None
    rain: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    w: Optional[float] = None
    h: Optional[float] = None
    area: Optional[float] = None
    irrig: Optional[str] = None

class FarmBase(BaseModel):
    id: Optional[str] = None
    farm_id: Optional[str] = None
    name: str
    farm_name: Optional[str] = None
    farmer_id: Optional[str] = "F-101"
    country: Optional[str] = "India"
    state: Optional[str] = ""
    district: Optional[str] = ""
    city: Optional[str] = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[str] = None
    plots: List[PlotBase] = []
    sensors: List[SensorSchema] = []
    trees: List[TreeSchema] = []
    pipes: List[PipeSchema] = []
    greenhouses: List[Dict[str, Any]] = []
    reservoir: Optional[ReservoirSchema] = None
    paths: Optional[List[Dict[str, Any]]] = []
    area_ha: Optional[float] = 2.5
    area: Optional[float] = None

class FarmCreate(FarmBase):
    pass

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    farm_name: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    plots: Optional[List[PlotBase]] = None
    sensors: Optional[List[SensorSchema]] = None
    trees: Optional[List[TreeSchema]] = None
    pipes: Optional[List[PipeSchema]] = None
    greenhouses: Optional[List[Dict[str, Any]]] = None
    reservoir: Optional[ReservoirSchema] = None
    paths: Optional[List[Dict[str, Any]]] = None
    area_ha: Optional[float] = None
    area: Optional[float] = None
