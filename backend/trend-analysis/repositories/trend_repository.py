from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database.models import TrendVideo, VideoStats
from ..models import TrendVideo as TrendVideoModel

class TrendRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_video(self, video: TrendVideoModel) -> TrendVideo:
        """
        動画情報を保存する

        Args:
            video: 保存する動画情報

        Returns:
            TrendVideo: 保存された動画情報
        """
        # 既存の動画を検索
        existing_video = self.db.query(TrendVideo).filter_by(video_id=video.video_id).first()

        if existing_video:
            # 既存の動画を更新
            existing_video.title = video.title
            existing_video.description = video.description
            existing_video.channel_title = video.channel_title
            existing_video.buzz_score = video.buzz_score
            existing_video.updated_at = datetime.now()

            # 統計情報を更新
            if existing_video.stats:
                existing_video.stats.view_count = video.stats.view_count
                existing_video.stats.like_count = video.stats.like_count
                existing_video.stats.comment_count = video.stats.comment_count
                existing_video.stats.engagement_rate = video.stats.engagement_rate
                existing_video.stats.updated_at = datetime.now()
            else:
                # 新しい統計情報を作成
                stats = VideoStats(
                    video_id=video.video_id,
                    view_count=video.stats.view_count,
                    like_count=video.stats.like_count,
                    comment_count=video.stats.comment_count,
                    engagement_rate=video.stats.engagement_rate
                )
                existing_video.stats = stats

            self.db.commit()
            return existing_video

        else:
            # 新しい動画を作成
            db_video = TrendVideo(
                video_id=video.video_id,
                title=video.title,
                description=video.description,
                published_at=video.published_at,
                channel_id=video.channel_id,
                channel_title=video.channel_title,
                buzz_score=video.buzz_score,
                collected_at=datetime.now()
            )

            # 統計情報を作成
            stats = VideoStats(
                video_id=video.video_id,
                view_count=video.stats.view_count,
                like_count=video.stats.like_count,
                comment_count=video.stats.comment_count,
                engagement_rate=video.stats.engagement_rate
            )
            db_video.stats = stats

            self.db.add(db_video)
            self.db.commit()
            self.db.refresh(db_video)
            return db_video

    def get_video(self, video_id: str) -> Optional[TrendVideo]:
        """
        動画情報を取得する

        Args:
            video_id: 動画ID

        Returns:
            Optional[TrendVideo]: 動画情報
        """
        return self.db.query(TrendVideo).filter_by(video_id=video_id).first()

    def get_trending_videos(
        self,
        limit: int = 50,
        offset: int = 0,
        min_buzz_score: float = 0.0
    ) -> List[TrendVideo]:
        """
        トレンド動画のリストを取得する

        Args:
            limit: 取得する最大数
            offset: スキップする数
            min_buzz_score: 最小バズり度スコア

        Returns:
            List[TrendVideo]: トレンド動画のリスト
        """
        return self.db.query(TrendVideo)\
            .filter(TrendVideo.buzz_score >= min_buzz_score)\
            .order_by(TrendVideo.buzz_score.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

    def delete_old_videos(self, days: int = 30) -> int:
        """
        古い動画を削除する

        Args:
            days: 削除する動画の日数

        Returns:
            int: 削除された動画の数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = self.db.query(TrendVideo)\
            .filter(TrendVideo.collected_at < cutoff_date)\
            .delete()
        self.db.commit()
        return deleted 