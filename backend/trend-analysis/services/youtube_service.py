from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key is not set in environment variables")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    async def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: str = "relevance",
        region_code: str = "JP",
        language: str = "ja"
    ) -> List[Dict]:
        """
        YouTubeで動画を検索する

        Args:
            query (str): 検索クエリ
            max_results (int): 取得する最大結果数
            order (str): ソート順（relevance, date, rating, viewCount）
            region_code (str): 地域コード
            language (str): 言語コード

        Returns:
            List[Dict]: 検索結果のリスト
        """
        try:
            search_response = self.youtube.search().list(
                q=query,
                part="snippet",
                maxResults=max_results,
                order=order,
                regionCode=region_code,
                relevanceLanguage=language,
                type="video"
            ).execute()

            videos = []
            for item in search_response.get("items", []):
                video_id = item["id"]["videoId"]
                video_details = self.youtube.videos().list(
                    part="statistics,contentDetails",
                    id=video_id
                ).execute()

                if video_details["items"]:
                    video_info = video_details["items"][0]
                    videos.append({
                        "video_id": video_id,
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "published_at": item["snippet"]["publishedAt"],
                        "channel_title": item["snippet"]["channelTitle"],
                        "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
                        "view_count": int(video_info["statistics"].get("viewCount", 0)),
                        "like_count": int(video_info["statistics"].get("likeCount", 0)),
                        "comment_count": int(video_info["statistics"].get("commentCount", 0)),
                        "duration": video_info["contentDetails"]["duration"]
                    })

            return videos

        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []

    async def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        特定の動画の詳細情報を取得する

        Args:
            video_id (str): 動画ID

        Returns:
            Optional[Dict]: 動画の詳細情報
        """
        try:
            response = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            ).execute()

            if not response["items"]:
                return None

            video = response["items"][0]
            return {
                "video_id": video_id,
                "title": video["snippet"]["title"],
                "description": video["snippet"]["description"],
                "published_at": video["snippet"]["publishedAt"],
                "channel_title": video["snippet"]["channelTitle"],
                "thumbnail_url": video["snippet"]["thumbnails"]["high"]["url"],
                "view_count": int(video["statistics"].get("viewCount", 0)),
                "like_count": int(video["statistics"].get("likeCount", 0)),
                "comment_count": int(video["statistics"].get("commentCount", 0)),
                "duration": video["contentDetails"]["duration"]
            }

        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None 