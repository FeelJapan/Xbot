import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ..services.youtube import YouTubeService
from ..models import TrendVideo, VideoStats

class TestYouTubeService:
    """YouTubeサービスのテストクラス"""

    @pytest.fixture
    def youtube_service(self):
        """YouTubeサービスのインスタンスを作成"""
        with patch('trend_analysis.services.youtube.get_settings') as mock_settings:
            mock_settings.return_value.youtube_api_key = "test_api_key"
            with patch('trend_analysis.services.youtube.build') as mock_build:
                mock_youtube = Mock()
                mock_build.return_value = mock_youtube
                service = YouTubeService()
                service.youtube = mock_youtube
                return service

    @pytest.mark.asyncio
    async def test_get_trending_videos_success(self, youtube_service):
        """トレンド動画の取得テスト（成功）"""
        # モックレスポンスの設定
        mock_response = {
            "items": [
                {
                    "id": "test_video_id",
                    "snippet": {
                        "title": "Test Video",
                        "description": "Test Description",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "channelId": "test_channel_id",
                        "channelTitle": "Test Channel"
                    },
                    "statistics": {
                        "viewCount": "1000",
                        "likeCount": "100",
                        "commentCount": "50"
                    }
                }
            ]
        }

        # YouTube APIのモック設定
        mock_videos_list = Mock()
        mock_videos_list.execute.return_value = mock_response
        youtube_service.youtube.videos.return_value.list.return_value = mock_videos_list

        # テスト実行
        result = await youtube_service.get_trending_videos(
            region_code="JP",
            max_results=1
        )

        # 結果の検証
        assert len(result) == 1
        assert isinstance(result[0], TrendVideo)
        assert result[0].video_id == "test_video_id"
        assert result[0].title == "Test Video"
        assert result[0].stats.view_count == 1000
        assert result[0].stats.like_count == 100
        assert result[0].stats.comment_count == 50

    @pytest.mark.asyncio
    async def test_search_videos_success(self, youtube_service):
        """動画検索のテスト（成功）"""
        # 検索レスポンスのモック
        mock_search_response = {
            "items": [
                {
                    "id": {"videoId": "test_video_id"}
                }
            ]
        }

        # 動画詳細レスポンスのモック
        mock_videos_response = {
            "items": [
                {
                    "id": "test_video_id",
                    "snippet": {
                        "title": "Test Video",
                        "description": "Test Description",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "channelId": "test_channel_id",
                        "channelTitle": "Test Channel",
                        "thumbnails": {
                            "high": {"url": "http://example.com/thumbnail.jpg"}
                        }
                    },
                    "statistics": {
                        "viewCount": "1000",
                        "likeCount": "100",
                        "commentCount": "50"
                    },
                    "contentDetails": {
                        "duration": "PT10M30S"
                    }
                }
            ]
        }

        # YouTube APIのモック設定
        mock_search = Mock()
        mock_search.execute.return_value = mock_search_response
        youtube_service.youtube.search.return_value.list.return_value = mock_search

        mock_videos = Mock()
        mock_videos.execute.return_value = mock_videos_response
        youtube_service.youtube.videos.return_value.list.return_value = mock_videos

        # テスト実行
        result = await youtube_service.search_videos(
            query="test query",
            max_results=1
        )

        # 結果の検証
        assert len(result) == 1
        assert result[0]["video_id"] == "test_video_id"
        assert result[0]["title"] == "Test Video"
        assert result[0]["view_count"] == 1000

    @pytest.mark.asyncio
    async def test_get_video_comments_success(self, youtube_service):
        """動画コメント取得のテスト（成功）"""
        # コメントレスポンスのモック
        mock_comments_response = {
            "items": [
                {
                    "id": "comment_id_1",
                    "snippet": {
                        "topLevelComment": {
                            "snippet": {
                                "authorDisplayName": "Test User",
                                "textDisplay": "Great video!",
                                "likeCount": 10,
                                "publishedAt": "2024-01-01T00:00:00Z",
                                "updatedAt": "2024-01-01T00:00:00Z",
                                "authorChannelId": {"value": "user_channel_id"}
                            }
                        }
                    }
                }
            ]
        }

        # YouTube APIのモック設定
        mock_comments = Mock()
        mock_comments.execute.return_value = mock_comments_response
        youtube_service.youtube.commentThreads.return_value.list.return_value = mock_comments

        # テスト実行
        result = await youtube_service.get_video_comments(
            video_id="test_video_id",
            max_results=1
        )

        # 結果の検証
        assert len(result) == 1
        assert result[0]["id"] == "comment_id_1"
        assert result[0]["author"] == "Test User"
        assert result[0]["text"] == "Great video!"
        assert result[0]["like_count"] == 10

    @pytest.mark.asyncio
    async def test_get_video_comments_disabled(self, youtube_service):
        """コメント無効動画のテスト"""
        # コメント無効エラーのモック
        from googleapiclient.errors import HttpError
        mock_error = HttpError(Mock(status=403), b'{"error": {"message": "Comments disabled"}}')

        # YouTube APIのモック設定
        mock_comments = Mock()
        mock_comments.execute.side_effect = mock_error
        youtube_service.youtube.commentThreads.return_value.list.return_value = mock_comments

        # テスト実行
        result = await youtube_service.get_video_comments(
            video_id="test_video_id"
        )

        # 結果の検証
        assert result == []

    def test_calculate_engagement_rate(self, youtube_service):
        """エンゲージメント率計算のテスト"""
        # テストデータ
        statistics = {
            "viewCount": "1000",
            "likeCount": "100",
            "commentCount": "50"
        }

        # テスト実行
        result = youtube_service._calculate_engagement_rate(statistics)

        # 結果の検証
        expected_rate = ((100 + 50) / 1000) * 100  # 15%
        assert result == expected_rate

    def test_calculate_engagement_rate_zero_views(self, youtube_service):
        """視聴回数0の場合のエンゲージメント率計算テスト"""
        # テストデータ
        statistics = {
            "viewCount": "0",
            "likeCount": "100",
            "commentCount": "50"
        }

        # テスト実行
        result = youtube_service._calculate_engagement_rate(statistics)

        # 結果の検証
        assert result == 0.0

    def test_get_published_after(self, youtube_service):
        """期間設定のテスト"""
        # テスト実行
        day_result = youtube_service._get_published_after("day")
        week_result = youtube_service._get_published_after("week")
        month_result = youtube_service._get_published_after("month")
        default_result = youtube_service._get_published_after("invalid")

        # 結果の検証
        assert isinstance(day_result, datetime)
        assert isinstance(week_result, datetime)
        assert isinstance(month_result, datetime)
        assert isinstance(default_result, datetime)

    def test_convert_to_trend_video_success(self, youtube_service):
        """動画データ変換のテスト（成功）"""
        # テストデータ
        item = {
            "id": "test_video_id",
            "snippet": {
                "title": "Test Video",
                "description": "Test Description",
                "publishedAt": "2024-01-01T00:00:00Z",
                "channelId": "test_channel_id",
                "channelTitle": "Test Channel"
            },
            "statistics": {
                "viewCount": "1000",
                "likeCount": "100",
                "commentCount": "50"
            }
        }

        # テスト実行
        result = youtube_service._convert_to_trend_video(item)

        # 結果の検証
        assert isinstance(result, TrendVideo)
        assert result.video_id == "test_video_id"
        assert result.title == "Test Video"
        assert result.stats.view_count == 1000
        assert result.buzz_score == 0.0

    def test_convert_to_trend_video_invalid_data(self, youtube_service):
        """無効なデータでの動画変換テスト"""
        # 無効なテストデータ
        invalid_item = {
            "id": "test_video_id",
            "snippet": {
                "title": "Test Video"
                # 必要なフィールドが不足
            }
        }

        # テスト実行
        result = youtube_service._convert_to_trend_video(invalid_item)

        # 結果の検証
        assert result is None 