from fastapi import APIRouter
from typing import Dict, Any, List
from schemas.admin import RegionalInsightsResponse
from database import db_manager

router = APIRouter(prefix="/api/regional", tags=["Regional Insights"])

@router.get("/insights", response_model=RegionalInsightsResponse)
@router.get("/summary")
async def get_regional_insights():
    farmers = db_manager.memory_store.get("farmers", [])
    total_area = sum(f.get("area", 0) for f in farmers)
    total_moist = sum(f.get("moist", 50) for f in farmers)
    avg_moist = round(total_moist / max(1, len(farmers)), 1)
    
    approved_certs = len([c for c in db_manager.memory_store.get("certificates", []) if c.get("status") == "approved"])
    tot_certs = len(db_manager.memory_store.get("certificates", []))
    approval_rate = round((approved_certs / max(1, tot_certs)) * 100.0, 1)

    crops = {}
    for f in farmers:
        c = f.get("crop", "Unknown")
        crops[c] = crops.get(c, 0) + 1

    villages = [
        {"name": "Kavathe", "farmers": 2, "area_ha": 3.6, "water_status": "Adequate"},
        {"name": "Nandra", "farmers": 2, "area_ha": 5.1, "water_status": "Vulnerable"},
        {"name": "Welga", "farmers": 2, "area_ha": 5.8, "water_status": "Moderate"}
    ]

    return RegionalInsightsResponse(
        total_farmers=len(farmers),
        total_area_ha=round(total_area, 1),
        avg_soil_moisture=avg_moist,
        cert_approval_rate=approval_rate,
        crop_distribution=crops,
        village_breakdown=villages,
        water_risk_level="Moderate",
        is_demo=False
    )

@router.get("/crops")
async def get_regional_crops():
    farmers = db_manager.memory_store.get("farmers", [])
    crops = {}
    for f in farmers:
        c = f.get("crop", "Unknown")
        crops[c] = crops.get(c, 0) + 1
    return {"crop_distribution": crops, "total_records": len(farmers)}

@router.get("/water")
async def get_regional_water():
    return {
        "watershed_capacity_kL": 2400.0,
        "current_storage_kL": 1640.0,
        "aquifer_recharge_status": "Stable",
        "regional_stress_level": "Moderate",
        "monsoon_forecast_anomaly": "-8%"
    }

@router.get("/stress")
async def get_regional_stress():
    return {
        "heat_stress_alert": False,
        "drought_vulnerability_index": 0.38,
        "pest_outbreak_risk": "Low (2/10)",
        "actionable_advisories": [
            "Maintain night irrigation cycle in sandy loam zones",
            "Monitor sunflower seedling vigor following recent humidity shift"
        ]
    }
