from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FarmerBase(BaseModel):
    id: str
    name: str
    village: str
    area: float
    crop: str
    cert: str = "pending" # approved, pending, changes
    plots: int = 3
    moist: float = 45.0

class FarmerCreate(BaseModel):
    name: str
    village: str
    area: float
    crop: str
    cert: Optional[str] = "pending"
    plots: Optional[int] = 3
    moist: Optional[float] = 50.0

class FarmerUpdate(BaseModel):
    name: Optional[str] = None
    village: Optional[str] = None
    area: Optional[float] = None
    crop: Optional[str] = None
    cert: Optional[str] = None
    plots: Optional[int] = None
    moist: Optional[float] = None

class CertificateBase(BaseModel):
    id: str
    farmer: str
    crop: str
    date: str
    status: str = "pending" # pending, approved, changes
    docs: List[str] = []

class CertificateCreate(BaseModel):
    farmer: str
    crop: str
    docs: Optional[List[str]] = ["Field photo", "Sowing log"]

class CertificateUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class CropGuideBase(BaseModel):
    id: str
    crop: str
    updated: str
    summary: str

class CropGuideCreate(BaseModel):
    crop: str
    summary: str

class CropGuideUpdate(BaseModel):
    crop: Optional[str] = None
    summary: Optional[str] = None

class RegionalInsightsResponse(BaseModel):
    total_farmers: int
    total_area_ha: float
    avg_soil_moisture: float
    cert_approval_rate: float
    crop_distribution: Dict[str, int]
    village_breakdown: List[Dict[str, Any]]
    water_risk_level: str
    is_demo: bool = True
