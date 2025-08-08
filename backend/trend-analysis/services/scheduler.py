import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Optional
from ..services.collector import TrendCollector
from ..services.youtube import YouTubeService
from ..repositories.trend_repository import TrendRepository
from ..core.logging import get_logger

logger = get_logger(__name__)

class TrendScheduler:
    def __init__(self):
        self.youtube_service = YouTubeService()
        self.trend_repository = TrendRepository()
        self.collector = TrendCollector(self.youtube_service, self.trend_repository)
        self.logger = logger
        self.is_running = False

    async def start_scheduler(self, collection_interval: int = 60):
        """
        トレンド収集スケジューラーを開始する

        Args:
            collection_interval: 収集間隔（分）
        """
        try:
            self.is_running = True
            self.logger.info(f"Starting trend collection scheduler with {collection_interval} minute intervals")

            # スケジュールの設定
            schedule.every(collection_interval).minutes.do(self._collect_trends_job)

            # 初回収集を即座に実行
            await self._collect_trends_job()

            # スケジューラーの実行
            while self.is_running:
                schedule.run_pending()
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Error in scheduler: {str(e)}")
            self.is_running = False
            raise

    def stop_scheduler(self):
        """スケジューラーを停止する"""
        self.is_running = False
        self.logger.info("Trend collection scheduler stopped")

    async def _collect_trends_job(self):
        """
        トレンド収集ジョブを実行する
        """
        try:
            self.logger.info("Starting trend collection job")

            # 複数の地域でトレンドを収集
            regions = ["JP", "US", "GB", "CA", "AU"]
            all_videos = []

            for region in regions:
                try:
                    videos = await self.collector.collect_trends(
                        region_code=region,
                        max_results=20,
                        time_period="day"
                    )
                    all_videos.extend(videos)
                    self.logger.info(f"Collected {len(videos)} videos from region {region}")

                    # API制限を考慮して少し待機
                    await asyncio.sleep(1)

                except Exception as e:
                    self.logger.error(f"Error collecting trends for region {region}: {str(e)}")
                    continue

            # 重複を除去
            unique_videos = self._remove_duplicates(all_videos)
            
            # 古いデータの削除
            deleted_count = self.trend_repository.delete_old_videos(days=30)
            
            self.logger.info(f"Collection job completed. Collected {len(unique_videos)} unique videos, deleted {deleted_count} old videos")

        except Exception as e:
            self.logger.error(f"Error in collection job: {str(e)}")

    def _remove_duplicates(self, videos: List) -> List:
        """
        重複する動画を除去する

        Args:
            videos: 動画リスト

        Returns:
            List: 重複を除去した動画リスト
        """
        seen_video_ids = set()
        unique_videos = []

        for video in videos:
            if video.video_id not in seen_video_ids:
                seen_video_ids.add(video.video_id)
                unique_videos.append(video)

        return unique_videos

    async def collect_by_category(self, category_id: str, region_code: str = "JP"):
        """
        特定カテゴリのトレンドを収集する

        Args:
            category_id: カテゴリID
            region_code: 地域コード
        """
        try:
            videos = await self.collector.collect_trends(
                region_code=region_code,
                max_results=50,
                category_id=category_id,
                time_period="day"
            )
            
            self.logger.info(f"Collected {len(videos)} videos for category {category_id}")
            return videos

        except Exception as e:
            self.logger.error(f"Error collecting category trends: {str(e)}")
            raise

    async def collect_by_keyword(self, keyword: str, region_code: str = "JP"):
        """
        キーワードベースでトレンドを収集する

        Args:
            keyword: 検索キーワード
            region_code: 地域コード
        """
        try:
            # YouTube APIでキーワード検索を実行
            search_results = await self.youtube_service.search_videos(
                query=keyword,
                max_results=50,
                region_code=region_code
            )

            # 検索結果をTrendVideo形式に変換
            videos = []
            for result in search_results:
                video = self._convert_search_result_to_trend_video(result)
                if video:
                    videos.append(video)

            # データベースに保存
            saved_videos = []
            for video in videos:
                saved_video = self.trend_repository.save_video(video)
                saved_videos.append(saved_video)

            self.logger.info(f"Collected {len(saved_videos)} videos for keyword '{keyword}'")
            return saved_videos

        except Exception as e:
            self.logger.error(f"Error collecting keyword trends: {str(e)}")
            raise

    def _convert_search_result_to_trend_video(self, search_result: dict):
        """
        検索結果をTrendVideo形式に変換する

        Args:
            search_result: 検索結果

        Returns:
            TrendVideo: 変換された動画情報
        """
        try:
            from ..models import TrendVideo, VideoStats

            stats = VideoStats(
                view_count=search_result.get("view_count", 0),
                like_count=search_result.get("like_count", 0),
                comment_count=search_result.get("comment_count", 0),
                engagement_rate=0.0  # 後で計算
            )

            return TrendVideo(
                video_id=search_result["video_id"],
                title=search_result["title"],
                description=search_result["description"],
                published_at=datetime.fromisoformat(search_result["published_at"].replace("Z", "+00:00")),
                channel_id=search_result.get("channel_id", ""),
                channel_title=search_result["channel_title"],
                stats=stats
            )

        except Exception as e:
            self.logger.error(f"Error converting search result: {str(e)}")
            return None

    def get_scheduler_status(self) -> dict:
        """
        スケジューラーの状態を取得する

        Returns:
            dict: スケジューラーの状態情報
        """
        return {
            "is_running": self.is_running,
            "next_run": schedule.next_run(),
            "last_run": getattr(self, '_last_run', None),
            "total_jobs": len(schedule.jobs)
        } 