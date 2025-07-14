from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
from ..models import TrendVideo, VideoStats
from .youtube import YouTubeService
from ..repositories.trend_repository import TrendRepository
from ..core.logging import get_logger

logger = get_logger(__name__)

class TrendCollector:
    def __init__(self, youtube_service: YouTubeService, trend_repository: TrendRepository):
        self.youtube_service = youtube_service
        self.trend_repository = trend_repository
        self.logger = logger

    async def collect_trends(
        self,
        region_code: str = "JP",
        max_results: int = 50,
        category_id: Optional[str] = None,
        time_period: str = "day"
    ) -> List[TrendVideo]:
        """
        トレンド動画を収集する

        Args:
            region_code: 地域コード
            max_results: 取得する動画の最大数
            category_id: カテゴリID
            time_period: 期間（day, week, month）

        Returns:
            List[TrendVideo]: 収集したトレンド動画リスト
        """
        try:
            # トレンド動画の取得
            videos = await self.youtube_service.get_trending_videos(
                region_code=region_code,
                max_results=max_results,
                category_id=category_id,
                time_period=time_period
            )

            # 動画情報をデータベースに保存
            saved_videos = []
            for video in videos:
                saved_video = self.trend_repository.save_video(video)
                saved_videos.append(saved_video)

            # 古い動画を削除
            deleted_count = self.trend_repository.delete_old_videos(days=30)
            if deleted_count > 0:
                self.logger.info(f"Deleted {deleted_count} old videos")

            return saved_videos

        except Exception as e:
            self.logger.error(f"Error collecting trends: {str(e)}")
            raise

    async def start_collection_loop(
        self,
        interval_minutes: int = 60,
        region_code: str = "JP",
        max_results: int = 50,
        category_id: Optional[str] = None
    ):
        """
        定期的な収集を開始する

        Args:
            interval_minutes: 収集間隔（分）
            region_code: 地域コード
            max_results: 取得する動画の最大数
            category_id: カテゴリID
        """
        while True:
            try:
                await self.collect_trends(
                    region_code=region_code,
                    max_results=max_results,
                    category_id=category_id
                )
                self.logger.info(f"Successfully collected trends at {datetime.now()}")
            except Exception as e:
                self.logger.error(f"Error in collection loop: {str(e)}")

            await asyncio.sleep(interval_minutes * 60) 