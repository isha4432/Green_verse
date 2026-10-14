from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import connect_to_mongo, close_mongo_connection

# Import all routers
from routes.health import router as health_router
from routes.farms import router as farms_router
from routes.ai import router as ai_router
from routes.climate import router as climate_router
from routes.irrigation import router as irrigation_router
from routes.quantum import router as quantum_router
from routes.experiments import router as experiments_router
from routes.water import router as water_router
from routes.soil import router as soil_router
from routes.crops import router as crops_router
from routes.farmers import router as farmers_router
from routes.certificates import router as certificates_router
from routes.guides import router as crop_guides_router, guides_router
from routes.regional import router as regional_router
from routes.reports import router as reports_router
from routes.auth import router as auth_router
from routes.location import router as location_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|\[::1\]|0\.0\.0\.0|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All API Routers
app.include_router(health_router)
app.include_router(farms_router)
app.include_router(ai_router)
app.include_router(climate_router)
app.include_router(irrigation_router)
app.include_router(quantum_router)
app.include_router(experiments_router)
app.include_router(water_router)
app.include_router(soil_router)
app.include_router(crops_router)
app.include_router(farmers_router)
app.include_router(certificates_router)
app.include_router(crop_guides_router)
app.include_router(guides_router)
app.include_router(regional_router)
app.include_router(reports_router)
app.include_router(auth_router)
app.include_router(location_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Green Verse API",
        "docs": "/docs",
        "health": "/api/health",
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)
