from fastapi import APIRouter
from config import settings

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
