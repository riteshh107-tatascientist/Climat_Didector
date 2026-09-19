from fastapi import APIRouter
from app.ml.predictors import preload_all_models
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["system"])
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@router.get("/models/status", tags=["system"])
def model_status():
    return preload_all_models()
