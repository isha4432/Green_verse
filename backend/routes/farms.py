import math
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from database import db_manager
from schemas.farm import FarmBase, FarmCreate, FarmUpdate, PlotBase, PlotCreate, PlotUpdate

router = APIRouter(prefix="/api", tags=["Farms & Plots"])

def haversine_km(lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]) -> float:
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float('inf')
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Location-specific initial farms in database
DEFAULT_FARMS = [
    {
        "id": "farm-kurnool-1",
        "farm_id": "farm-kurnool-1",
        "name": "Kurnool Sun Farm",
        "farm_name": "Kurnool Sun Farm",
        "farmer_id": "F-101",
        "country": "India",
        "state": "Andhra Pradesh",
        "district": "Kurnool",
        "city": "Kurnool",
        "latitude": 15.8289,
        "longitude": 78.0360,
        "area_ha": 2.4,
        "area": 752.0,
        "created_at": "2026-03-01T08:00:00Z",
        "plots": [
            {"id": "P-101", "plot_id": "P-101", "name": "North Tomato Block", "crop": "tomato", "condition": "good", "stage": 3, "crop_stage": 3, "moisture": 52.0, "temp": 28.0, "rain": 12.0, "x": 6.0, "y": 6.0, "w": 18.0, "h": 16.0, "area": 288.0, "irrig": "drip"},
            {"id": "P-102", "plot_id": "P-102", "name": "East Durum Wheat", "crop": "wheat", "condition": "good", "stage": 2, "crop_stage": 2, "moisture": 46.0, "temp": 28.0, "rain": 8.0, "x": 26.0, "y": 6.0, "w": 15.0, "h": 16.0, "area": 240.0, "irrig": "sprinkler"},
            {"id": "P-103", "plot_id": "P-103", "name": "Olive Terrace", "crop": "olive", "condition": "good", "stage": 4, "crop_stage": 4, "moisture": 49.0, "temp": 28.0, "rain": 10.0, "x": 43.0, "y": 6.0, "w": 14.0, "h": 16.0, "area": 224.0, "irrig": "drip"}
        ],
        "sensors": [
            {"id": "s-1", "x": 15.0, "y": 14.0, "type": "moisture"},
            {"id": "s-2", "x": 33.0, "y": 14.0, "type": "temp"},
            {"id": "s-3", "x": 50.0, "y": 14.0, "type": "moisture"}
        ],
        "trees": [
            {"id": "t-1", "x": 12.0, "y": 42.0, "kind": "olive"},
            {"id": "t-2", "x": 28.0, "y": 42.0, "kind": "olive"},
            {"id": "t-3", "x": 45.0, "y": 42.0, "kind": "olive"}
        ],
        "pipes": [
            {"id": "pip-1", "pts": [{"x": 70.0, "y": 40.0}, {"x": 50.0, "y": 40.0}, {"x": 50.0, "y": 14.0}, {"x": 10.0, "y": 14.0}]}
        ],
        "reservoir": {"x": 68.0, "y": 38.0, "w": 20.0, "h": 9.0},
        "paths": [{"x": 0.0, "y": 23.0, "w": 100.0, "h": 2.4}],
        "greenhouses": []
    }
]

# Initialize memory store if empty
if not db_manager.memory_store["farms"]:
    db_manager.memory_store["farms"] = list(DEFAULT_FARMS)

@router.get("/farms", response_model=List[FarmBase])
async def get_farms(
    lat: Optional[float] = Query(None, description="Location latitude"),
    lon: Optional[float] = Query(None, description="Location longitude"),
    city: Optional[str] = Query(None, description="City name"),
    district: Optional[str] = Query(None, description="District name"),
    state: Optional[str] = Query(None, description="State name"),
    radius_km: Optional[float] = Query(65.0, description="Match radius in kilometers")
):
    all_farms = db_manager.memory_store["farms"]
    if db_manager.is_connected and db_manager.db is not None:
        try:
            db_farms = await db_manager.db.farms.find().to_list(100)
            if db_farms:
                all_farms = db_farms
        except Exception:
            pass

    # If no filtering parameters provided, return all farms
    if lat is None and lon is None and not city and not district and not state:
        return all_farms

    matched = []
    for f in all_farms:
        f_lat = f.get("latitude")
        f_lon = f.get("longitude")
        f_city = (f.get("city") or "").strip().lower()
        f_district = (f.get("district") or "").strip().lower()
        f_state = (f.get("state") or "").strip().lower()
        f_name = (f.get("name") or "").strip().lower()

        # 1. Geographic distance match if coordinates given
        if lat is not None and lon is not None and f_lat is not None and f_lon is not None:
            dist = haversine_km(lat, lon, f_lat, f_lon)
            if dist <= (radius_km or 65.0):
                matched.append(f)
                continue

        # 2. Textual city/district/state match
        q_city = (city or "").strip().lower()
        q_dist = (district or "").strip().lower()
        q_state = (state or "").strip().lower()

        if q_city and (q_city in f_city or f_city in q_city or q_city in f_name):
            matched.append(f)
        elif q_dist and (q_dist in f_district or f_district in q_dist):
            matched.append(f)
        elif q_state and q_state == f_state and not q_city and not q_dist:
            matched.append(f)

    return matched

@router.get("/farms/{farm_id}", response_model=FarmBase)
async def get_farm(farm_id: str):
    all_farms = db_manager.memory_store["farms"]
    if db_manager.is_connected and db_manager.db is not None:
        try:
            farm = await db_manager.db.farms.find_one({"$or": [{"id": farm_id}, {"farm_id": farm_id}]})
            if farm:
                return farm
        except Exception:
            pass
    
    for f in all_farms:
        if f.get("id") == farm_id or f.get("farm_id") == farm_id:
            return f
    raise HTTPException(status_code=404, detail=f"Farm '{farm_id}' not found")

@router.post("/farms", response_model=FarmBase)
async def create_farm(farm: FarmCreate):
    farm_dict = farm.dict()
    if not farm_dict.get("id"):
        farm_dict["id"] = f"farm-{int(datetime.now().timestamp())}"
    if not farm_dict.get("farm_id"):
        farm_dict["farm_id"] = farm_dict["id"]
    if not farm_dict.get("created_at"):
        farm_dict["created_at"] = datetime.now().isoformat()
    
    # Calculate area and ensure plots have plot_id and area
    plots = farm_dict.get("plots", [])
    total_area = 0.0
    for p in plots:
        if not p.get("area"):
            p["area"] = round(float(p.get("w", 20.0)) * float(p.get("h", 15.0)), 1)
        total_area += p["area"]
        if not p.get("plot_id"):
            p["plot_id"] = p.get("id")
    farm_dict["area"] = total_area

    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.farms.insert_one(farm_dict)
        except Exception:
            pass
    db_manager.memory_store["farms"].append(farm_dict)
    return farm_dict

@router.put("/farms/{farm_id}", response_model=FarmBase)
async def update_farm(farm_id: str, farm: FarmUpdate):
    update_data = {k: v for k, v in farm.dict().items() if v is not None}
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.farms.update_one({"$or": [{"id": farm_id}, {"farm_id": farm_id}]}, {"$set": update_data})
        except Exception:
            pass
    for i, f in enumerate(db_manager.memory_store["farms"]):
        if f.get("id") == farm_id or f.get("farm_id") == farm_id:
            db_manager.memory_store["farms"][i].update(update_data)
            return db_manager.memory_store["farms"][i]
    raise HTTPException(status_code=404, detail="Farm not found")

@router.delete("/farms/{farm_id}")
async def delete_farm(farm_id: str):
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.farms.delete_one({"$or": [{"id": farm_id}, {"farm_id": farm_id}]})
        except Exception:
            pass
    db_manager.memory_store["farms"] = [f for f in db_manager.memory_store["farms"] if f.get("id") != farm_id and f.get("farm_id") != farm_id]
    return {"message": "Farm deleted", "id": farm_id}

# PLOTS ENDPOINTS
@router.get("/farms/{farm_id}/plots", response_model=List[PlotBase])
async def get_farm_plots(farm_id: str):
    farm = await get_farm(farm_id)
    plots = farm.get("plots", [])
    for p in plots:
        if not p.get("area"):
            p["area"] = round(float(p.get("w", 20.0)) * float(p.get("h", 15.0)), 1)
        if not p.get("plot_id"):
            p["plot_id"] = p.get("id")
    return plots

@router.post("/farms/{farm_id}/plots", response_model=PlotBase)
async def add_farm_plot(farm_id: str, plot: PlotCreate):
    farm = await get_farm(farm_id)
    plot_dict = plot.dict()
    if not plot_dict.get("id"):
        plot_dict["id"] = f"P-{len(farm.get('plots', [])) + 1}"
    if not plot_dict.get("plot_id"):
        plot_dict["plot_id"] = plot_dict["id"]
    if not plot_dict.get("area"):
        plot_dict["area"] = round(float(plot_dict.get("w", 20.0)) * float(plot_dict.get("h", 15.0)), 1)
    
    farm.setdefault("plots", []).append(plot_dict)
    farm["area"] = sum(p.get("area", 0) for p in farm["plots"])
    
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.farms.update_one({"$or": [{"id": farm_id}, {"farm_id": farm_id}]}, {"$set": {"plots": farm["plots"], "area": farm["area"]}})
        except Exception:
            pass
    return plot_dict

@router.put("/plots/{plot_id}", response_model=PlotBase)
async def update_plot(plot_id: str, plot: PlotUpdate):
    for f in db_manager.memory_store["farms"]:
        for i, p in enumerate(f.get("plots", [])):
            if p.get("id") == plot_id or p.get("plot_id") == plot_id:
                update_data = {k: v for k, v in plot.dict().items() if v is not None}
                f["plots"][i].update(update_data)
                return f["plots"][i]
    raise HTTPException(status_code=404, detail="Plot not found")

@router.delete("/plots/{plot_id}")
async def delete_plot(plot_id: str):
    found = False
    for f in db_manager.memory_store["farms"]:
        orig_len = len(f.get("plots", []))
        f["plots"] = [p for p in f.get("plots", []) if p.get("id") != plot_id and p.get("plot_id") != plot_id]
        if len(f["plots"]) < orig_len:
            found = True
    if found:
        return {"message": "Plot deleted", "id": plot_id}
    raise HTTPException(status_code=404, detail="Plot not found")

