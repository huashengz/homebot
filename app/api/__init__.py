# API package initialization
from fastapi import APIRouter
from app.api.v1.api import api_router

router = APIRouter()

router.include_router(api_router)

@router.get("/models", tags=["LLM"])
async def list_models():
    models = ["qwen-plus"]
    return {"available_models": models}
