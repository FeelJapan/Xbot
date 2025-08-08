from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from ..models import TrendAnalysisRequest, TrendAnalysisResponse, TrendVideo
from ..services.youtube import YouTubeService
from ..services.analysis import AnalysisService
from ..services.scheduler import TrendScheduler
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

@router.get("/search")
async def search_videos(
    query: str = Query(..., description="検索クエリ"),
    max_results: int = Query(50, description="取得する最大結果数"),
    order: str = Query("relevance", description="ソート順（relevance, date, rating, viewCount）"),
    region_code: str = Query("JP", description="地域コード"),
    language: str = Query("ja", description="言語コード"),
    youtube_service: YouTubeService = Depends()
):
    """
    キーワード検索で動画を取得する

    Args:
        query: 検索クエリ
        max_results: 取得する最大結果数
        order: ソート順
        region_code: 地域コード
        language: 言語コード
        youtube_service: YouTube APIサービス

    Returns:
        List[Dict]: 検索結果
    """
    try:
        videos = await youtube_service.search_videos(
            query=query,
            max_results=max_results,
            order=order,
            region_code=region_code,
            language=language
        )
        
        return {
            "status": "success",
            "data": videos,
            "total_count": len(videos),
            "query": query,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in search_videos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search videos: {str(e)}"
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

@router.get("/videos/{video_id}/comprehensive")
async def get_comprehensive_analysis(
    video_id: str,
    youtube_service: YouTubeService = Depends(),
    analysis_service: AnalysisService = Depends()
):
    """
    動画の包括的な分析を取得する

    Args:
        video_id: 動画ID
        youtube_service: YouTube APIサービス
        analysis_service: 分析サービス

    Returns:
        Dict: 包括的な分析結果
    """
    try:
        # 動画情報の取得
        video_details = await youtube_service.get_video_details(video_id)
        if not video_details:
            raise HTTPException(
                status_code=404,
                detail="Video not found"
            )

        # コメントの取得
        comments = await youtube_service.get_video_comments(video_id, max_results=100)
        
        # TrendVideoオブジェクトの作成
        from ..models import TrendVideo, VideoStats
        video = TrendVideo(
            video_id=video_details["video_id"],
            title=video_details["title"],
            description=video_details["description"],
            published_at=datetime.fromisoformat(video_details["published_at"].replace("Z", "+00:00")),
            channel_id=video_details["channel_id"],
            channel_title=video_details["channel_title"],
            stats=VideoStats(
                view_count=video_details["view_count"],
                like_count=video_details["like_count"],
                comment_count=video_details["comment_count"],
                engagement_rate=video_details["engagement_rate"]
            )
        )
        
        # コメントを追加
        video.comments = comments

        # 包括的な分析の実行
        analysis_result = await analysis_service.analyze_comprehensive_trends(video)

        return {
            "status": "success",
            "video_id": video_id,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_comprehensive_analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze video: {str(e)}"
        )

@router.get("/videos/{video_id}/comments")
async def get_video_comments(
    video_id: str,
    max_results: int = Query(100, description="取得するコメントの最大数"),
    order: str = Query("relevance", description="ソート順（relevance, time）"),
    youtube_service: YouTubeService = Depends()
):
    """
    動画のコメントを取得する

    Args:
        video_id: 動画ID
        max_results: 取得するコメントの最大数
        order: ソート順
        youtube_service: YouTube APIサービス

    Returns:
        List[Dict]: コメントリスト
    """
    try:
        comments = await youtube_service.get_video_comments(
            video_id=video_id,
            max_results=max_results,
            order=order
        )

        return {
            "status": "success",
            "video_id": video_id,
            "comments": comments,
            "total_count": len(comments),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in get_video_comments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get comments: {str(e)}"
        )

@router.post("/scheduler/start")
async def start_scheduler(
    collection_interval: int = Query(60, description="収集間隔（分）"),
    scheduler: TrendScheduler = Depends()
):
    """
    トレンド収集スケジューラーを開始する

    Args:
        collection_interval: 収集間隔（分）
        scheduler: スケジューラーサービス

    Returns:
        Dict: スケジューラーの状態
    """
    try:
        # バックグラウンドでスケジューラーを開始
        import asyncio
        asyncio.create_task(scheduler.start_scheduler(collection_interval))
        
        return {
            "status": "success",
            "message": f"Scheduler started with {collection_interval} minute intervals",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scheduler: {str(e)}"
        )

@router.post("/scheduler/stop")
async def stop_scheduler(
    scheduler: TrendScheduler = Depends()
):
    """
    トレンド収集スケジューラーを停止する

    Args:
        scheduler: スケジューラーサービス

    Returns:
        Dict: スケジューラーの状態
    """
    try:
        scheduler.stop_scheduler()
        
        return {
            "status": "success",
            "message": "Scheduler stopped",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop scheduler: {str(e)}"
        )

@router.get("/scheduler/status")
async def get_scheduler_status(
    scheduler: TrendScheduler = Depends()
):
    """
    スケジューラーの状態を取得する

    Args:
        scheduler: スケジューラーサービス

    Returns:
        Dict: スケジューラーの状態情報
    """
    try:
        status = scheduler.get_scheduler_status()
        
        return {
            "status": "success",
            "scheduler_status": status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scheduler status: {str(e)}"
        )

@router.post("/collect/category/{category_id}")
async def collect_by_category(
    category_id: str,
    region_code: str = Query("JP", description="地域コード"),
    scheduler: TrendScheduler = Depends()
):
    """
    特定カテゴリのトレンドを収集する

    Args:
        category_id: カテゴリID
        region_code: 地域コード
        scheduler: スケジューラーサービス

    Returns:
        Dict: 収集結果
    """
    try:
        videos = await scheduler.collect_by_category(category_id, region_code)
        
        return {
            "status": "success",
            "category_id": category_id,
            "region_code": region_code,
            "collected_videos": len(videos),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error collecting category trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect category trends: {str(e)}"
        )

@router.post("/collect/keyword")
async def collect_by_keyword(
    keyword: str = Query(..., description="検索キーワード"),
    region_code: str = Query("JP", description="地域コード"),
    scheduler: TrendScheduler = Depends()
):
    """
    キーワードベースでトレンドを収集する

    Args:
        keyword: 検索キーワード
        region_code: 地域コード
        scheduler: スケジューラーサービス

    Returns:
        Dict: 収集結果
    """
    try:
        videos = await scheduler.collect_by_keyword(keyword, region_code)
        
        return {
            "status": "success",
            "keyword": keyword,
            "region_code": region_code,
            "collected_videos": len(videos),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error collecting keyword trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect keyword trends: {str(e)}"
        ) 