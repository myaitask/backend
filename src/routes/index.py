from fastapi import APIRouter
from datetime import datetime
import time

from .auth import router as auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": time.monotonic()  # close enough approximation
    }
