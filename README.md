# Green Verse — Quantum–AI for Climate-Resilient Agriculture

Green Verse is a full-stack decision-support system for climate-resilient agriculture, combining agronomic machine learning, Three.js 3D farm/cultivation visualizations, classical constrained optimization, and variational quantum algorithms (QAOA) powered by Qiskit Aer.

---

## Architecture Overview

```
Frontend (Vite / Three.js / Vanilla JS) — http://localhost:5173
       │
       ▼ (REST API / JSON / CORS)
Backend (FastAPI / Pydantic / Uvicorn) — http://127.0.0.1:8000
       ├── Agronomic ML & Stress Intelligence (Scikit-Learn / Heuristic Rule Engine)
       ├── Mathematical Solvers (Exact Combinatorial & Heuristics)
       ├── Quantum Optimization (QUBO & Qiskit Aer QAOA Statevector Simulator)
       ├── ReportLab PDF Generation Engine
       └── Persistence Layer (MongoDB with Seamless In-Memory Fallback)
```

---

## Features & Modules

1. **Overview Dashboard**: Live KPIs, water availability, regional risk aggregation, recent experiments, and real-time backend synchronization.
2. **Virtual Farm 3D**: Interactive plot management with live soil moisture, thermal metrics, stage tracking, and Three.js environmental rendering.
3. **Cultivation 3D Lifecycle**: 7-stage cultivation progression (Land Prep, Sowing, Crop Care, Irrigation, Pest Scouting, Harvest) with stateful history logging.
4. **Crop Recommendation**: Agronomic ranking engine evaluating N-P-K, pH, temperature, precipitation, season, and farmer goals (Income, Yield, Water-Saving, Resilience).
5. **AI Crop Stress Intelligence**: Predictive risk scoring, canopy heat stress assessment, waterlogging alerts, and actionable mitigation steps.
6. **Climate Simulator**: Parametric delta simulations (temperature, rainfall, soil moisture, water quota) with crop resilience scoring.
7. **Water Harvesting**: Catchment sizing, first-flush diversion, storage tank utilization, groundwater recharge estimation, and 3D visualization.
8. **Soil & Land Health**: Plot-level soil records, NPK balance, drainage indices, and organic amendment prescriptions.
9. **Multi-Cropping Planner**: Zone-based intercropping/strip-cropping compatibility evaluation and canopy resource synergy calculations.
10. **Irrigation Planner**: Constrained water allocation under strict budget constraints.
11. **Quantum Lab (QUBO & QAOA)**:
    - Formulation of irrigation scheduling as Quadratic Unconstrained Binary Optimization (QUBO).
    - Quantum Approximate Optimization Algorithm (QAOA) simulated with Qiskit Aer.
    - Side-by-side classical vs. quantum comparison (energy gap, runtime, feasibility, approximation ratio).
12. **Experiments & Reports**: Experiment database persistence, multi-run comparison, and branded PDF generation via ReportLab.
13. **Farmer Directory & Certificate Review**: Agricultural registry CRUD and compliance review workflow.
14. **Manage Crop Guides**: Knowledge base management with full create, update, and delete support.
15. **Regional Insights**: Watershed statistics, village breakdown, and aggregated crop distribution.

---

## Local Setup & Quick Start

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** & **npm**
- *(Optional)* **MongoDB** running locally on port 27017 (the app automatically falls back to in-memory persistence if MongoDB is not running).

---

### 2. Backend Startup

In a terminal:
```powershell
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

---

### 3. Frontend Startup

In a second terminal (from the project root):
```powershell
npm install
npm run dev
```

- **Frontend App**: `http://localhost:5173`

---

## Environment Variables (`backend/.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HOST` | `0.0.0.0` | Backend bind host |
| `PORT` | `8000` | Backend bind port |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins |
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `DATABASE_NAME` | `green_verse` | Database name |
| `JWT_SECRET` | `green-verse-secret-key-2026` | Secret key for JWT signing |

---

## Testing

Run the automated backend test suite covering all 21 core API endpoints:
```powershell
python -c "
import urllib.request, json
tests = [
    ('GET', '/api/health', None),
    ('GET', '/api/farms', None),
    ('POST', '/api/ai/crop-recommendation', {'soil_type': 'siltloam', 'soil_moisture': 55.0, 'temperature': 25.0, 'rainfall': 650.0, 'humidity': 50.0, 'ph': 6.8, 'nitrogen_n': 50.0, 'phosphorus_p': 25.0, 'potassium_k': 190.0, 'crop_season': 'rabi', 'location': 'Zone A', 'water_availability': 'Medium', 'crop_goal': 'income'}),
    ('POST', '/api/ai/crop-stress', {'plot_id': 'P-1', 'crop': 'tomato', 'soil_moisture': 58.0, 'temperature': 26.0, 'rainfall': 18.0, 'growth_stage': 3}),
    ('GET', '/api/ai/history/P-1', None),
    ('POST', '/api/cultivation/P-1/stage', {'plot_id': 'P-1', 'stage': 4, 'stage_name': 'Flowering & Irrigation', 'status': 'active', 'notes': 'Drip cycle engaged'}),
    ('GET', '/api/cultivation/P-1/history', None),
    ('POST', '/api/multicrop/analyze', {'zones': [{'id': 1, 'crops': ['Tomato', 'Chickpea'], 'mode': 'strip'}], 'water_budget': 45.0}),
    ('POST', '/api/quantum/compare', {'plots': [{'id': 'P-1', 'crop': 'Tomato', 'moisture': 45.0, 'priority': 2, 'base_demand': 12.0}, {'id': 'P-2', 'crop': 'Wheat', 'moisture': 35.0, 'priority': 3, 'base_demand': 10.0}], 'water_budget': 15.0, 'p_layers': 2, 'shots': 256}),
    ('POST', '/api/climate/simulate', {'temperature_delta': 2.0, 'rainfall_change': -15.0, 'soil_moisture_delta': -8.0, 'water_change': -10.0}),
    ('POST', '/api/water/calculate', {'rainfall': 25.0, 'catchment_area': 150.0, 'runoff_coefficient': 0.85, 'storage_capacity': 12.0, 'irrigation_demand': 6.0}),
    ('GET', '/api/soil/P-1', None),
    ('GET', '/api/farmers', None),
    ('GET', '/api/certificates', None),
    ('GET', '/api/crop-guides', None),
    ('GET', '/api/guides', None),
    ('GET', '/api/regional/summary', None),
    ('GET', '/api/regional/crops', None),
    ('GET', '/api/regional/water', None),
    ('GET', '/api/regional/stress', None),
    ('POST', '/api/reports/pdf', {'title': 'Test Report', 'summary': 'Suite validation'})
]
passed = sum(1 for m, ep, p in tests if urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000' + ep, headers={'Content-Type': 'application/json'}, data=json.dumps(p).encode() if p else None, method=m)).getcode() == 200)
print(f'Passed {passed} / {len(tests)} endpoints.')
"
```

---

## Troubleshooting

- **Socket Error `[WinError 10013]`**: Another process is occupying port 8000 or 5173. Terminate previous instances (`Stop-Process -Id <PID> -Force` or close existing terminal tabs).
- **`cd backend` error**: If your shell is already in the `backend/` directory, simply run `python -m uvicorn app:app --reload`.
- **Offline Backend Status**: The frontend displays a subtle status indicator in the sidebar footer (`API: Connected` vs `API: Offline (local demo fallback)`). Even if the backend is stopped, all pages and Three.js 3D visual scenes continue running locally without crashing.
