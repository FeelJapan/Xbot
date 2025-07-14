from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import os
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

from backend.core.logging.logger import get_logger

# 環境変数を読み込む
load_dotenv()

logger = get_logger("youtube_client")

class YouTubeClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key is not set")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    async def get_trending_videos(
        self,
        region_code: str = "JP",
        max_results: int = 10,
        category_id: Optional[str] = None
    ) -> List[Dict]:
        """
        トレンド動画を取得する
        
        Args:
            region_code (str): 地域コード（デフォルト: "JP"）
            max_results (int): 取得する動画の最大数（デフォルト: 10）
            category_id (Optional[str]): カテゴリID（オプション）
            
        Returns:
            List[Dict]: トレンド動画のリスト
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results,
                videoCategoryId=category_id if category_id else None
            )
            
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                video = {
                    "id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"],
                    "channel_id": item["snippet"]["channelId"],
                    "channel_title": item["snippet"]["channelTitle"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "comment_count": int(item["statistics"].get("commentCount", 0)),
                    "duration": item["contentDetails"]["duration"]
                }
                videos.append(video)
            
            return videos
            
        except HttpError as e:
            logger.error(f"An HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

    async def get_video_comments(
        self,
        video_id: str,
        max_results: int = 100
    ) -> List[Dict]:
        """
        動画のコメントを取得する
        
        Args:
            video_id (str): 動画ID
            max_results (int): 取得するコメントの最大数（デフォルト: 100）
            
        Returns:
            List[Dict]: コメントのリスト
        """
        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order="relevance"
            )
            
            response = request.execute()
            
            comments = []
            for item in response.get("items", []):
                comment = {
                    "id": item["id"],
                    "author": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                    "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                    "like_count": item["snippet"]["topLevelComment"]["snippet"]["likeCount"],
                    "published_at": item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                }
                comments.append(comment)
            
            return comments
            
        except HttpError as e:
            logger.error(f"An HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

    async def analyze_video_trends(
        self,
        video_id: str,
        days: int = 7
    ) -> Dict:
        """
        動画のトレンド分析を行う
        
        Args:
            video_id (str): 動画ID
            days (int): 分析期間（日数）
            
        Returns:
            Dict: 分析結果
        """
        try:
            # 動画の基本情報を取得
            video_request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            video_response = video_request.execute()
            
            if not video_response.get("items"):
                raise ValueError(f"Video not found: {video_id}")
            
            video = video_response["items"][0]
            
            # コメントを取得
            comments = await self.get_video_comments(video_id)
            
            # 分析結果を構築
            analysis = {
                "video_id": video_id,
                "title": video["snippet"]["title"],
                "channel_title": video["snippet"]["channelTitle"],
                "view_count": int(video["statistics"].get("viewCount", 0)),
                "like_count": int(video["statistics"].get("likeCount", 0)),
                "comment_count": int(video["statistics"].get("commentCount", 0)),
                "engagement_rate": self._calculate_engagement_rate(video["statistics"]),
                "comment_analysis": self._analyze_comments(comments),
                "analyzed_at": datetime.now().isoformat()
            }
            
            return analysis
            
        except HttpError as e:
            logger.error(f"An HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

    def _calculate_engagement_rate(self, statistics: Dict) -> float:
        """
        エンゲージメント率を計算する
        
        Args:
            statistics (Dict): 動画の統計情報
            
        Returns:
            float: エンゲージメント率
        """
        view_count = int(statistics.get("viewCount", 0))
        if view_count == 0:
            return 0.0
            
        like_count = int(statistics.get("likeCount", 0))
        comment_count = int(statistics.get("commentCount", 0))
        
        engagement = like_count + comment_count
        return (engagement / view_count) * 100

    def _analyze_comments(self, comments: List[Dict]) -> Dict:
        """
        コメントを分析する
        
        Args:
            comments (List[Dict]): コメントのリスト
            
        Returns:
            Dict: 分析結果
        """
        if not comments:
            return {
                "total_comments": 0,
                "average_likes": 0,
                "sentiment": "neutral"
            }
        
        total_likes = sum(comment["like_count"] for comment in comments)
        average_likes = total_likes / len(comments)
        
        # TODO: 感情分析の実装
        
        return {
            "total_comments": len(comments),
            "average_likes": average_likes,
            "sentiment": "neutral"  # 仮の実装
        } 