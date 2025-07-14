from fastapi import APIRouter
from app.api.endpoints import settings

api_router = APIRouter()
api_router.include_router(settings.router, tags=["settings"]) 