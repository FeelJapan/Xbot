"""
投稿分析APIエンドポイント
投稿のパフォーマンス分析、エンゲージメント統計、レポート生成機能を提供
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.post_analytics import (
    PostAnalytics, EngagementMetrics, PostPerformance,
    TimeSlotPerformance, HashtagPerformance, ContentTypePerformance,
    AnalyticsReport, AnalyticsError
)
from core.logging.logger import get_logger

logger = get_logger("post_analytics_api")

router = APIRouter()

# サービスインスタンス
analytics = PostAnalytics()

# リクエストモデル
class UpdateMetricsRequest(BaseModel):
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    impressions: int = 0
    clicks: int = 0
    profile_visits: int = 0
    follows: int = 0

# レスポンスモデル
class EngagementMetricsResponse(BaseModel):
    likes: int
    retweets: int
    replies: int
    impressions: int
    clicks: int
    profile_visits: int
    follows: int
    engagement_rate: float

class PostPerformanceResponse(BaseModel):
    post_id: str
    posted_at: datetime
    content_type: str
    hashtags: List[str]
    metrics: EngagementMetricsResponse
    performance_score: float

class TimeSlotPerformanceResponse(BaseModel):
    hour: int
    average_engagement_rate: float
    average_impressions: float
    post_count: int
    best_performing_type: str

class HashtagPerformanceResponse(BaseModel):
    hashtag: str
    usage_count: int
    average_engagement_rate: float
    average_impressions: float
    trending_correlation: float

class ContentTypePerformanceResponse(BaseModel):
    content_type: str
    post_count: int
    average_engagement_rate: float
    average_impressions: float
    best_time_slot: int

class AnalyticsReportResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_posts: int
    total_impressions: int
    total_engagements: int
    average_engagement_rate: float
    best_post: Optional[PostPerformanceResponse]
    worst_post: Optional[PostPerformanceResponse]
    time_slot_performance: List[TimeSlotPerformanceResponse]
    hashtag_performance: List[HashtagPerformanceResponse]
    content_type_performance: List[ContentTypePerformanceResponse]
    recommendations: List[str]

@router.put("/posts/{post_id}/metrics", response_model=PostPerformanceResponse)
async def update_post_metrics(post_id: str, request: UpdateMetricsRequest):
    """投稿のメトリクスを更新"""
    try:
        metrics = EngagementMetrics(
            likes=request.likes,
            retweets=request.retweets,
            replies=request.replies,
            impressions=request.impressions,
            clicks=request.clicks,
            profile_visits=request.profile_visits,
            follows=request.follows
        )
        
        performance = analytics.update_post_metrics(post_id, metrics)
        
        logger.info(f"投稿のメトリクスを更新しました: {post_id}")
        return PostPerformanceResponse(
            post_id=performance.post_id,
            posted_at=performance.posted_at,
            content_type=performance.content_type.value,
            hashtags=performance.hashtags,
            metrics=EngagementMetricsResponse(
                likes=performance.metrics.likes,
                retweets=performance.metrics.retweets,
                replies=performance.metrics.replies,
                impressions=performance.metrics.impressions,
                clicks=performance.metrics.clicks,
                profile_visits=performance.metrics.profile_visits,
                follows=performance.metrics.follows,
                engagement_rate=performance.metrics.engagement_rate
            ),
            performance_score=performance.performance_score
        )
        
    except AnalyticsError as e:
        logger.error(f"メトリクス更新エラー: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"メトリクス更新エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/{post_id}/performance", response_model=PostPerformanceResponse)
async def get_post_performance(post_id: str):
    """投稿のパフォーマンスを取得"""
    try:
        performance = analytics.get_post_performance(post_id)
        
        if performance is None:
            raise HTTPException(status_code=404, detail=f"パフォーマンスデータが見つかりません: {post_id}")
        
        return PostPerformanceResponse(
            post_id=performance.post_id,
            posted_at=performance.posted_at,
            content_type=performance.content_type.value,
            hashtags=performance.hashtags,
            metrics=EngagementMetricsResponse(
                likes=performance.metrics.likes,
                retweets=performance.metrics.retweets,
                replies=performance.metrics.replies,
                impressions=performance.metrics.impressions,
                clicks=performance.metrics.clicks,
                profile_visits=performance.metrics.profile_visits,
                follows=performance.metrics.follows,
                engagement_rate=performance.metrics.engagement_rate
            ),
            performance_score=performance.performance_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"パフォーマンス取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/time-slots", response_model=List[TimeSlotPerformanceResponse])
async def analyze_time_slots(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """時間帯別パフォーマンスを分析"""
    try:
        results = analytics.analyze_time_slots(start_date, end_date)
        
        return [
            TimeSlotPerformanceResponse(
                hour=slot.hour,
                average_engagement_rate=slot.average_engagement_rate,
                average_impressions=slot.average_impressions,
                post_count=slot.post_count,
                best_performing_type=slot.best_performing_type.value
            )
            for slot in results
        ]
        
    except Exception as e:
        logger.error(f"時間帯分析エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/hashtags", response_model=List[HashtagPerformanceResponse])
async def analyze_hashtags(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """ハッシュタグパフォーマンスを分析"""
    try:
        results = analytics.analyze_hashtags(start_date, end_date)
        
        return [
            HashtagPerformanceResponse(
                hashtag=hashtag.hashtag,
                usage_count=hashtag.usage_count,
                average_engagement_rate=hashtag.average_engagement_rate,
                average_impressions=hashtag.average_impressions,
                trending_correlation=hashtag.trending_correlation
            )
            for hashtag in results
        ]
        
    except Exception as e:
        logger.error(f"ハッシュタグ分析エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/content-types", response_model=List[ContentTypePerformanceResponse])
async def analyze_content_types(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """コンテンツタイプ別パフォーマンスを分析"""
    try:
        results = analytics.analyze_content_types(start_date, end_date)
        
        return [
            ContentTypePerformanceResponse(
                content_type=ct.content_type.value,
                post_count=ct.post_count,
                average_engagement_rate=ct.average_engagement_rate,
                average_impressions=ct.average_impressions,
                best_time_slot=ct.best_time_slot
            )
            for ct in results
        ]
        
    except Exception as e:
        logger.error(f"コンテンツタイプ分析エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/report", response_model=AnalyticsReportResponse)
async def generate_analytics_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """分析レポートを生成"""
    try:
        report = analytics.generate_report(start_date, end_date)
        
        # レスポンスの構築
        response = AnalyticsReportResponse(
            period_start=report.period_start,
            period_end=report.period_end,
            total_posts=report.total_posts,
            total_impressions=report.total_impressions,
            total_engagements=report.total_engagements,
            average_engagement_rate=report.average_engagement_rate,
            best_post=None,
            worst_post=None,
            time_slot_performance=[
                TimeSlotPerformanceResponse(
                    hour=slot.hour,
                    average_engagement_rate=slot.average_engagement_rate,
                    average_impressions=slot.average_impressions,
                    post_count=slot.post_count,
                    best_performing_type=slot.best_performing_type.value
                )
                for slot in report.time_slot_performance
            ],
            hashtag_performance=[
                HashtagPerformanceResponse(
                    hashtag=hashtag.hashtag,
                    usage_count=hashtag.usage_count,
                    average_engagement_rate=hashtag.average_engagement_rate,
                    average_impressions=hashtag.average_impressions,
                    trending_correlation=hashtag.trending_correlation
                )
                for hashtag in report.hashtag_performance
            ],
            content_type_performance=[
                ContentTypePerformanceResponse(
                    content_type=ct.content_type.value,
                    post_count=ct.post_count,
                    average_engagement_rate=ct.average_engagement_rate,
                    average_impressions=ct.average_impressions,
                    best_time_slot=ct.best_time_slot
                )
                for ct in report.content_type_performance
            ],
            recommendations=report.recommendations
        )
        
        # ベスト/ワースト投稿の設定
        if report.best_post:
            response.best_post = PostPerformanceResponse(
                post_id=report.best_post.post_id,
                posted_at=report.best_post.posted_at,
                content_type=report.best_post.content_type.value,
                hashtags=report.best_post.hashtags,
                metrics=EngagementMetricsResponse(
                    likes=report.best_post.metrics.likes,
                    retweets=report.best_post.metrics.retweets,
                    replies=report.best_post.metrics.replies,
                    impressions=report.best_post.metrics.impressions,
                    clicks=report.best_post.metrics.clicks,
                    profile_visits=report.best_post.metrics.profile_visits,
                    follows=report.best_post.metrics.follows,
                    engagement_rate=report.best_post.metrics.engagement_rate
                ),
                performance_score=report.best_post.performance_score
            )
            
        if report.worst_post:
            response.worst_post = PostPerformanceResponse(
                post_id=report.worst_post.post_id,
                posted_at=report.worst_post.posted_at,
                content_type=report.worst_post.content_type.value,
                hashtags=report.worst_post.hashtags,
                metrics=EngagementMetricsResponse(
                    likes=report.worst_post.metrics.likes,
                    retweets=report.worst_post.metrics.retweets,
                    replies=report.worst_post.metrics.replies,
                    impressions=report.worst_post.metrics.impressions,
                    clicks=report.worst_post.metrics.clicks,
                    profile_visits=report.worst_post.metrics.profile_visits,
                    follows=report.worst_post.metrics.follows,
                    engagement_rate=report.worst_post.metrics.engagement_rate
                ),
                performance_score=report.worst_post.performance_score
            )
        
        logger.info(f"分析レポートを生成しました: {report.period_start} - {report.period_end}")
        return response
        
    except Exception as e:
        logger.error(f"レポート生成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """ダッシュボード用の統計情報を取得"""
    try:
        # 過去7日間のレポート
        week_report = analytics.generate_report()
        
        # 最新のパフォーマンスデータ
        recent_performances = sorted(
            analytics.performance_data.values(),
            key=lambda x: x.posted_at,
            reverse=True
        )[:10]
        
        # ダッシュボードデータを構築
        dashboard_data = {
            "summary": {
                "total_posts": week_report.total_posts,
                "total_impressions": week_report.total_impressions,
                "total_engagements": week_report.total_engagements,
                "average_engagement_rate": week_report.average_engagement_rate
            },
            "recent_posts": [
                {
                    "post_id": perf.post_id,
                    "posted_at": perf.posted_at.isoformat(),
                    "engagement_rate": perf.metrics.engagement_rate,
                    "performance_score": perf.performance_score
                }
                for perf in recent_performances
            ],
            "best_time_slots": [
                {
                    "hour": slot.hour,
                    "engagement_rate": slot.average_engagement_rate
                }
                for slot in week_report.time_slot_performance[:3]
            ],
            "top_hashtags": [
                {
                    "hashtag": hashtag.hashtag,
                    "engagement_rate": hashtag.average_engagement_rate,
                    "trending": hashtag.trending_correlation > 0.7
                }
                for hashtag in week_report.hashtag_performance[:5]
            ],
            "recommendations": week_report.recommendations
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"ダッシュボード取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 