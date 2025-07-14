from datetime import datetime, timedelta
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..models import TrendVideo, VideoStats
from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)

class YouTubeService:
    def __init__(self):
        self.settings = get_settings()
        self.youtube = build('youtube', 'v3', developerKey=self.settings.youtube_api_key)
        self.logger = logger

    async def get_trending_videos(
        self,
        region_code: str = "JP",
        max_results: int = 50,
        category_id: Optional[str] = None,
        time_period: str = "day"
    ) -> List[TrendVideo]:
        """
        トレンド動画を取得する

        Args:
            region_code: 地域コード
            max_results: 取得する動画の最大数
            category_id: カテゴリID
            time_period: 期間（day, week, month）

        Returns:
            List[TrendVideo]: トレンド動画リスト
        """
        try:
            # 期間の設定
            published_after = self._get_published_after(time_period)

            # トレンド動画の取得
            request = self.youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results,
                videoCategoryId=category_id,
                publishedAfter=published_after.isoformat() + "Z"
            )
            response = request.execute()

            # 動画情報の変換
            videos = []
            for item in response.get("items", []):
                video = self._convert_to_trend_video(item)
                if video:
                    videos.append(video)

            return videos

        except HttpError as e:
            self.logger.error(f"YouTube API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    def _get_published_after(self, time_period: str) -> datetime:
        """期間に応じた開始日時を取得"""
        now = datetime.utcnow()
        if time_period == "day":
            return now - timedelta(days=1)
        elif time_period == "week":
            return now - timedelta(weeks=1)
        elif time_period == "month":
            return now - timedelta(days=30)
        else:
            return now - timedelta(days=1)

    def _convert_to_trend_video(self, item: dict) -> Optional[TrendVideo]:
        """APIレスポンスをTrendVideoモデルに変換"""
        try:
            snippet = item["snippet"]
            statistics = item["statistics"]

            # 統計情報の取得
            stats = VideoStats(
                view_count=int(statistics.get("viewCount", 0)),
                like_count=int(statistics.get("likeCount", 0)),
                comment_count=int(statistics.get("commentCount", 0)),
                engagement_rate=self._calculate_engagement_rate(statistics)
            )

            # 動画情報の作成
            return TrendVideo(
                video_id=item["id"],
                title=snippet["title"],
                description=snippet["description"],
                published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                channel_id=snippet["channelId"],
                channel_title=snippet["channelTitle"],
                stats=stats,
                buzz_score=0.0  # 初期値。後で分析サービスで更新
            )

        except (KeyError, ValueError) as e:
            self.logger.error(f"Error converting video data: {str(e)}")
            return None

    def _calculate_engagement_rate(self, statistics: dict) -> float:
        """エンゲージメント率を計算"""
        try:
            views = int(statistics.get("viewCount", 0))
            if views == 0:
                return 0.0

            likes = int(statistics.get("likeCount", 0))
            comments = int(statistics.get("commentCount", 0))

            # エンゲージメント率 = (いいね数 + コメント数) / 視聴回数 * 100
            return ((likes + comments) / views) * 100

        except (ValueError, ZeroDivisionError):
            return 0.0 