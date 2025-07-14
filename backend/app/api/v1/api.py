"""
V1 API Router
すべてのv1エンドポイントを統合するルーター
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    gemini,
    search,
    post_management,
    post_analytics
)

api_router = APIRouter()

# 各エンドポイントをルーターに追加
api_router.include_router(gemini.router, prefix="/gemini", tags=["gemini"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(post_management.router, prefix="/post-management", tags=["post-management"])
api_router.include_router(post_analytics.router, prefix="/analytics", tags=["analytics"]) 