import time
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from database import db_manager
from schemas.experiment import ExperimentBase, ExperimentCreate, ExperimentUpdate

router = APIRouter(prefix="/api", tags=["Experiments & Reports"])

DEFAULT_EXPERIMENTS = [
    {
        "id": "EXP-014",
        "name": "QAOA water allocation",
        "type": "Optimization",
        "status": "Completed (Simulator)",
        "date": "04 Oct 2026",
        "metrics": {"energy": -42.8, "waterAllocated": 44.5, "feasibility": True, "shots": 512, "runtimeMs": 34.2},
        "data": {"p_layers": 2, "budget": 45.0, "algorithm": "QAOA (AerSimulator)"},
        "notes": "Quantum variational optimization run on 6-plot irrigation problem with budget constraint."
    },
    {
        "id": "EXP-013",
        "name": "Drought · rainfall −45 %",
        "type": "Scenario",
        "status": "Computed locally",
        "date": "12 May 2025",
        "metrics": {"riskMean": 58.4, "waterUse": 48.2, "score": 49},
        "data": {"clim": {"temp": 1.5, "rain": -45, "moist": -18, "water": -30}},
        "notes": "Simulated severe monsoon deficit and water table stress."
    },
    {
        "id": "EXP-012",
        "name": "Heatwave · +4.5 °C sweep",
        "type": "Scenario",
        "status": "Computed locally",
        "date": "10 May 2025",
        "metrics": {"riskMean": 64.2, "waterUse": 52.0, "score": 54},
        "data": {"clim": {"temp": 4.5, "rain": -10, "moist": -12, "water": -10}},
        "notes": "Thermal stress sweep across summer cropping calendar."
    }
]

if not db_manager.memory_store["experiments"]:
    db_manager.memory_store["experiments"] = list(DEFAULT_EXPERIMENTS)

@router.get("/experiments", response_model=List[ExperimentBase])
async def get_experiments():
    if db_manager.is_connected and db_manager.db is not None:
        try:
            exps = await db_manager.db.experiments.find().to_list(100)
            if exps:
                return exps
        except Exception:
            pass
    return db_manager.memory_store["experiments"]

@router.get("/experiments/{id}", response_model=ExperimentBase)
async def get_experiment(id: str):
    if db_manager.is_connected and db_manager.db is not None:
        try:
            exp = await db_manager.db.experiments.find_one({"id": id})
            if exp:
                return exp
        except Exception:
            pass
    for e in db_manager.memory_store["experiments"]:
        if e["id"] == id:
            return e
    raise HTTPException(status_code=404, detail="Experiment not found")

@router.post("/experiments", response_model=ExperimentBase)
async def create_experiment(exp: ExperimentCreate):
    count = len(db_manager.memory_store["experiments"]) + 15
    new_id = f"EXP-0{count}"
    exp_dict = {
        "id": new_id,
        "name": exp.name,
        "type": exp.type,
        "status": exp.status or "Completed",
        "date": datetime.now().strftime("%d %b %Y"),
        "metrics": exp.metrics or {},
        "data": exp.data or {},
        "notes": exp.notes or "Saved experiment run"
    }

    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.experiments.insert_one(exp_dict)
        except Exception:
            pass

    db_manager.memory_store["experiments"].insert(0, exp_dict)
    return exp_dict

@router.delete("/experiments/{id}")
async def delete_experiment(id: str):
    if db_manager.is_connected and db_manager.db is not None:
        try:
            await db_manager.db.experiments.delete_one({"id": id})
        except Exception:
            pass
    db_manager.memory_store["experiments"] = [e for e in db_manager.memory_store["experiments"] if e["id"] != id]
    return {"message": "Experiment deleted", "id": id}
