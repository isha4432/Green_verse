from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from database import db_manager
from schemas.admin import CropGuideBase, CropGuideCreate, CropGuideUpdate

router = APIRouter(prefix="/api/crop-guides", tags=["Manage Crop Guides"])
guides_router = APIRouter(prefix="/api/guides", tags=["Manage Crop Guides"])

DEFAULT_GUIDES = [
    {"id": "G1", "crop": "Tomato", "updated": "02 Jun", "summary": "Nursery to harvest in ~90 days. Stake early, drip at 42 mm/wk peak."},
    {"id": "G2", "crop": "Durum wheat", "updated": "28 May", "summary": "Sow mid-Oct (demo calendar). Terminal heat watch in March."},
    {"id": "G3", "crop": "Chickpea", "updated": "20 May", "summary": "Low-water rabi option. Scout for pod borer from flowering."}
]

if not db_manager.memory_store["crop_guides"]:
    db_manager.memory_store["crop_guides"] = list(DEFAULT_GUIDES)

@router.get("", response_model=List[CropGuideBase])
@guides_router.get("", response_model=List[CropGuideBase])
async def get_crop_guides():
    if db_manager.is_connected and db_manager.db is not None:
        try:
            guides = await db_manager.db.crop_guides.find().to_list(100)
            if guides:
                return guides
        except Exception:
            pass
    return db_manager.memory_store["crop_guides"]

@router.post("", response_model=CropGuideBase)
@guides_router.post("", response_model=CropGuideBase)
async def create_crop_guide(guide: CropGuideCreate):
    count = len(db_manager.memory_store["crop_guides"]) + 1
    new_id = f"G{count}"
    g_dict = {
        "id": new_id,
        "crop": guide.crop,
        "updated": datetime.now().strftime("%d %b"),
        "summary": guide.summary
    }
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.crop_guides.insert_one(g_dict)
        except Exception:
            pass
    db_manager.memory_store["crop_guides"].insert(0, g_dict)
    return g_dict

@router.put("/{id}", response_model=CropGuideBase)
@guides_router.put("/{id}", response_model=CropGuideBase)
async def update_crop_guide(id: str, guide: CropGuideUpdate):
    update_data = {k: v for k, v in guide.dict().items() if v is not None}
    update_data["updated"] = datetime.now().strftime("%d %b")
    for i, g in enumerate(db_manager.memory_store["crop_guides"]):
        if g["id"] == id:
            db_manager.memory_store["crop_guides"][i].update(update_data)
            return db_manager.memory_store["crop_guides"][i]
    raise HTTPException(status_code=404, detail="Crop guide not found")

@router.delete("/{id}")
@guides_router.delete("/{id}")
async def delete_crop_guide(id: str):
    db_manager.memory_store["crop_guides"] = [g for g in db_manager.memory_store["crop_guides"] if g["id"] != id]
    return {"message": "Crop guide deleted", "id": id}

