from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..services.youtube_service import YouTubeService

router = APIRouter()
youtube_service = YouTubeService()

@router.get("/search")
async def search_videos(
    query: str = Query(..., description="検索クエリ"),
    max_results: int = Query(10, description="取得する最大結果数"),
    order: str = Query("relevance", description="ソート順（relevance, date, rating, viewCount）"),
    region_code: str = Query("JP", description="地域コード"),
    language: str = Query("ja", description="言語コード")
) -> List[dict]:
    """
    YouTubeで動画を検索する

    Args:
        query (str): 検索クエリ
        max_results (int): 取得する最大結果数
        order (str): ソート順
        region_code (str): 地域コード
        language (str): 言語コード

    Returns:
        List[dict]: 検索結果のリスト
    """
    try:
        videos = await youtube_service.search_videos(
            query=query,
            max_results=max_results,
            order=order,
            region_code=region_code,
            language=language
        )
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/videos/{video_id}")
async def get_video_details(video_id: str) -> dict:
    """
    特定の動画の詳細情報を取得する

    Args:
        video_id (str): 動画ID

    Returns:
        dict: 動画の詳細情報
    """
    try:
        video = await youtube_service.get_video_details(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        return video
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 