from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from ..models import TrendAnalysisRequest, TrendAnalysisResponse, TrendVideo
from ..services.youtube import YouTubeService
from ..services.analysis import AnalysisService
from ..core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/videos", response_model=TrendAnalysisResponse)
async def get_trending_videos(
    request: TrendAnalysisRequest = Depends(),
    youtube_service: YouTubeService = Depends(),
    analysis_service: AnalysisService = Depends()
) -> TrendAnalysisResponse:
    """
    トレンド動画を取得し分析する

    Args:
        request: 分析リクエストパラメータ
        youtube_service: YouTube APIサービス
        analysis_service: 分析サービス

    Returns:
        TrendAnalysisResponse: 分析結果
    """
    try:
        # トレンド動画の取得
        videos = await youtube_service.get_trending_videos(
            region_code=request.region_code,
            max_results=request.max_results,
            category_id=request.category_id,
            time_period=request.time_period
        )

        # 動画の分析
        analyzed_videos = await analysis_service.analyze_trends(videos)

        return TrendAnalysisResponse(
            videos=analyzed_videos,
            total_count=len(analyzed_videos),
            analyzed_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error in get_trending_videos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze trending videos"
        )

@router.get("/videos/{video_id}", response_model=TrendVideo)
async def get_video_details(
    video_id: str,
    youtube_service: YouTubeService = Depends(),
    analysis_service: AnalysisService = Depends()
) -> TrendVideo:
    """
    特定の動画の詳細情報を取得する

    Args:
        video_id: 動画ID
        youtube_service: YouTube APIサービス
        analysis_service: 分析サービス

    Returns:
        TrendVideo: 動画の詳細情報
    """
    try:
        # 動画情報の取得
        videos = await youtube_service.get_trending_videos(
            max_results=1,
            video_id=video_id
        )

        if not videos:
            raise HTTPException(
                status_code=404,
                detail="Video not found"
            )

        # 動画の分析
        analyzed_videos = await analysis_service.analyze_trends(videos)
        return analyzed_videos[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_video_details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get video details"
        ) 