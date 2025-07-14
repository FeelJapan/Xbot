from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class VideoStats(BaseModel):
    """動画の統計情報"""
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    engagement_rate: float = 0.0

class ForeignReaction(BaseModel):
    """外国人視点からの反応"""
    sentiment_score: float = Field(..., description="感情分析スコア")
    reaction_type: str = Field(..., description="反応タイプ（笑い、驚き、共感など）")
    comment_examples: List[str] = Field(..., description="代表的なコメント例")

class TrendVideo(BaseModel):
    """トレンド動画情報"""
    video_id: str
    title: str
    description: str
    published_at: datetime
    channel_id: str
    channel_title: str
    stats: VideoStats
    buzz_score: float = 0.0
    collected_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class TrendAnalysisRequest(BaseModel):
    """トレンド分析リクエスト"""
    region_code: str = "JP"
    max_results: int = 50
    category_id: Optional[str] = None
    time_period: str = "day"

class TrendAnalysisResponse(BaseModel):
    """トレンド分析レスポンス"""
    videos: List[TrendVideo]
    total_count: int
    analyzed_at: datetime 