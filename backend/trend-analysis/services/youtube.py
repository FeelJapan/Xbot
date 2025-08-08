from datetime import datetime, timedelta
from typing import List, Optional, Dict
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

    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        order: str = "relevance",
        region_code: str = "JP",
        language: str = "ja",
        published_after: Optional[datetime] = None
    ) -> List[Dict]:
        """
        キーワード検索で動画を取得する

        Args:
            query: 検索クエリ
            max_results: 取得する動画の最大数
            order: ソート順（relevance, date, rating, viewCount）
            region_code: 地域コード
            language: 言語コード
            published_after: 公開日時の下限

        Returns:
            List[Dict]: 検索結果の動画リスト
        """
        try:
            # 検索リクエストの構築
            search_params = {
                "q": query,
                "part": "snippet",
                "maxResults": max_results,
                "order": order,
                "regionCode": region_code,
                "relevanceLanguage": language,
                "type": "video"
            }

            if published_after:
                search_params["publishedAfter"] = published_after.isoformat() + "Z"

            # 検索実行
            search_response = self.youtube.search().list(**search_params).execute()

            # 動画IDの抽出
            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

            if not video_ids:
                return []

            # 動画の詳細情報を取得
            videos_response = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(video_ids)
            ).execute()

            # 結果の変換
            videos = []
            for item in videos_response.get("items", []):
                video_info = self._convert_to_video_dict(item)
                if video_info:
                    videos.append(video_info)

            return videos

        except HttpError as e:
            self.logger.error(f"YouTube API search error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected search error: {str(e)}")
            raise

    async def get_video_comments(
        self,
        video_id: str,
        max_results: int = 100,
        order: str = "relevance"
    ) -> List[Dict]:
        """
        動画のコメントを取得する

        Args:
            video_id: 動画ID
            max_results: 取得するコメントの最大数
            order: ソート順（relevance, time）

        Returns:
            List[Dict]: コメントリスト
        """
        try:
            comments_response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order=order
            ).execute()

            comments = []
            for item in comments_response.get("items", []):
                comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                
                comment = {
                    "id": item["id"],
                    "author": comment_snippet["authorDisplayName"],
                    "text": comment_snippet["textDisplay"],
                    "like_count": comment_snippet["likeCount"],
                    "published_at": comment_snippet["publishedAt"],
                    "updated_at": comment_snippet["updatedAt"],
                    "author_channel_id": comment_snippet.get("authorChannelId", {}).get("value", "")
                }
                comments.append(comment)

            return comments

        except HttpError as e:
            if "commentsDisabled" in str(e):
                self.logger.info(f"Comments disabled for video {video_id}")
                return []
            else:
                self.logger.error(f"YouTube API comments error: {str(e)}")
                raise
        except Exception as e:
            self.logger.error(f"Unexpected comments error: {str(e)}")
            raise

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

    async def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        特定の動画の詳細情報を取得する

        Args:
            video_id: 動画ID

        Returns:
            Optional[Dict]: 動画の詳細情報
        """
        try:
            response = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            ).execute()

            if not response.get("items"):
                return None

            return self._convert_to_video_dict(response["items"][0])

        except HttpError as e:
            self.logger.error(f"YouTube API video details error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected video details error: {str(e)}")
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

    def _convert_to_video_dict(self, item: dict) -> Optional[Dict]:
        """APIレスポンスを辞書形式に変換"""
        try:
            snippet = item["snippet"]
            statistics = item["statistics"]
            content_details = item.get("contentDetails", {})

            return {
                "video_id": item["id"],
                "title": snippet["title"],
                "description": snippet["description"],
                "published_at": snippet["publishedAt"],
                "channel_id": snippet["channelId"],
                "channel_title": snippet["channelTitle"],
                "thumbnail_url": snippet["thumbnails"]["high"]["url"],
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "duration": content_details.get("duration", ""),
                "engagement_rate": self._calculate_engagement_rate(statistics)
            }

        except (KeyError, ValueError) as e:
            self.logger.error(f"Error converting video dict: {str(e)}")
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