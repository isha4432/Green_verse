from fastapi import APIRouter, HTTPException
from typing import List
from database import db_manager
from schemas.admin import FarmerBase, FarmerCreate, FarmerUpdate

router = APIRouter(prefix="/api/farmers", tags=["Farmer Directory"])

DEFAULT_FARMERS = [
    {"id": "F-101", "name": "R. Deshmukh", "village": "Kavathe", "area": 2.4, "crop": "Tomato", "cert": "approved", "plots": 4, "moist": 58.0},
    {"id": "F-102", "name": "A. Kaur", "village": "Nandra", "area": 3.1, "crop": "Durum wheat", "cert": "pending", "plots": 5, "moist": 34.0},
    {"id": "F-103", "name": "M. Okafor", "village": "Kavathe", "area": 1.2, "crop": "Chickpea", "cert": "approved", "plots": 3, "moist": 41.0},
    {"id": "F-104", "name": "S. Perera", "village": "Welga", "area": 4.0, "crop": "Grape", "cert": "approved", "plots": 6, "moist": 62.0},
    {"id": "F-105", "name": "J. Mendoza", "village": "Welga", "area": 1.8, "crop": "Onion", "cert": "changes", "plots": 3, "moist": 29.0},
    {"id": "F-106", "name": "L. Haddad", "village": "Nandra", "area": 2.0, "crop": "Olive", "cert": "pending", "plots": 4, "moist": 47.0}
]

if not db_manager.memory_store["farmers"]:
    db_manager.memory_store["farmers"] = list(DEFAULT_FARMERS)

@router.get("", response_model=List[FarmerBase])
async def get_farmers():
    if db_manager.is_connected and db_manager.db is not None:
        try:
            res = await db_manager.db.farmers.find().to_list(100)
            if res:
                return res
        except Exception:
            pass
    return db_manager.memory_store["farmers"]

@router.get("/{id}", response_model=FarmerBase)
async def get_farmer(id: str):
    if db_manager.is_connected and db_manager.db is not None:
        try:
            f = await db_manager.db.farmers.find_one({"id": id})
            if f:
                return f
        except Exception:
            pass
    for f in db_manager.memory_store["farmers"]:
        if f["id"] == id:
            return f
    raise HTTPException(status_code=404, detail="Farmer not found")

@router.post("", response_model=FarmerBase)
async def create_farmer(farmer: FarmerCreate):
    new_id = f"F-{len(db_manager.memory_store['farmers']) + 107}"
    f_dict = {"id": new_id, **farmer.dict()}
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.farmers.insert_one(f_dict)
        except Exception:
            pass
    db_manager.memory_store["farmers"].append(f_dict)
    return f_dict

@router.put("/{id}", response_model=FarmerBase)
async def update_farmer(id: str, farmer: FarmerUpdate):
    update_data = {k: v for k, v in farmer.dict().items() if v is not None}
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.farmers.update_one({"id": id}, {"$set": update_data})
        except Exception:
            pass
    for i, f in enumerate(db_manager.memory_store["farmers"]):
        if f["id"] == id:
            db_manager.memory_store["farmers"][i].update(update_data)
            return db_manager.memory_store["farmers"][i]
    raise HTTPException(status_code=404, detail="Farmer not found")

@router.delete("/{id}")
async def delete_farmer(id: str):
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.farmers.delete_one({"id": id})
        except Exception:
            pass
    db_manager.memory_store["farmers"] = [f for f in db_manager.memory_store["farmers"] if f["id"] != id]
    return {"message": "Farmer removed", "id": id}
