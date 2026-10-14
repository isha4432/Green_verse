from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from database import db_manager
from schemas.admin import CertificateBase, CertificateCreate, CertificateUpdate

router = APIRouter(prefix="/api/certificates", tags=["Certificate Review"])

DEFAULT_CERTS = [
    {"id": "CERT-021", "farmer": "A. Kaur", "crop": "Durum wheat · 2.0 ha", "date": "02 Jun", "status": "pending", "docs": ["Field photo", "Sowing log"]},
    {"id": "CERT-020", "farmer": "L. Haddad", "crop": "Olive · 2.0 ha", "date": "31 May", "status": "pending", "docs": ["Field photo"]},
    {"id": "CERT-019", "farmer": "M. Okafor", "crop": "Chickpea · 0.8 ha", "date": "28 May", "status": "approved", "docs": ["Field photo", "Moisture log", "Yield note"]},
    {"id": "CERT-018", "farmer": "J. Mendoza", "crop": "Onion · 1.8 ha", "date": "24 May", "status": "changes", "docs": ["Sowing log"]}
]

if not db_manager.memory_store["certificates"]:
    db_manager.memory_store["certificates"] = list(DEFAULT_CERTS)

@router.get("", response_model=List[CertificateBase])
async def get_certificates():
    if db_manager.is_connected and db_manager.db is not None:
        try:
            certs = await db_manager.db.certificates.find().to_list(100)
            if certs:
                return certs
        except Exception:
            pass
    return db_manager.memory_store["certificates"]

@router.get("/{id}", response_model=CertificateBase)
async def get_certificate(id: str):
    for c in db_manager.memory_store["certificates"]:
        if c["id"] == id:
            return c
    raise HTTPException(status_code=404, detail="Certificate not found")

@router.post("", response_model=CertificateBase)
async def submit_certificate(cert: CertificateCreate):
    count = len(db_manager.memory_store["certificates"]) + 22
    new_id = f"CERT-0{count}"
    c_dict = {
        "id": new_id,
        "farmer": cert.farmer,
        "crop": cert.crop,
        "date": datetime.now().strftime("%d %b"),
        "status": "pending",
        "docs": cert.docs or ["Field photo", "Sowing log"]
    }
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.certificates.insert_one(c_dict)
        except Exception:
            pass
    db_manager.memory_store["certificates"].insert(0, c_dict)
    return c_dict

@router.put("/{id}", response_model=CertificateBase)
async def update_certificate(id: str, cert: CertificateUpdate):
    for i, c in enumerate(db_manager.memory_store["certificates"]):
        if c["id"] == id:
            c["status"] = cert.status
            if db_manager.is_connected and db_manager.db is not None:
                try:
                    await db_manager.db.certificates.update_one({"id": id}, {"$set": {"status": cert.status}})
                except Exception:
                    pass
            return c
    raise HTTPException(status_code=404, detail="Certificate not found")
