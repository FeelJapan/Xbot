"""
V1 API Router
すべてのv1エンドポイントを統合するルーター
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    posts,
    trends,
    settings,
    content_generation,
    video_generation,
    image_generation,
    post_management,
    post_analytics
)

api_router = APIRouter()

# 各エンドポイントをルーターに追加
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(content_generation.router, prefix="/content", tags=["content"])
api_router.include_router(video_generation.router, prefix="/video", tags=["video"])
api_router.include_router(image_generation.router, prefix="/image", tags=["image"])
api_router.include_router(post_management.router, prefix="/post-management", tags=["post-management"])
api_router.include_router(post_analytics.router, prefix="/analytics", tags=["analytics"]) 