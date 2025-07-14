import pytest
from unittest.mock import Mock, patch
from ..services.youtube_service import YouTubeService

@pytest.fixture
def youtube_service():
    with patch("googleapiclient.discovery.build") as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        service = YouTubeService()
        service.youtube = mock_youtube
        yield service

@pytest.mark.asyncio
async def test_search_videos(youtube_service):
    # モックの設定
    mock_search_response = {
        "items": [
            {
                "id": {"videoId": "test_video_id"},
                "snippet": {
                    "title": "Test Video",
                    "description": "Test Description",
                    "publishedAt": "2024-03-14T00:00:00Z",
                    "channelTitle": "Test Channel",
                    "thumbnails": {"high": {"url": "https://example.com/thumbnail.jpg"}}
                }
            }
        ]
    }
    
    mock_video_details = {
        "items": [
            {
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100",
                    "commentCount": "50"
                },
                "contentDetails": {"duration": "PT10M30S"}
            }
        ]
    }
    
    youtube_service.youtube.search().list().execute.return_value = mock_search_response
    youtube_service.youtube.videos().list().execute.return_value = mock_video_details
    
    # テスト実行
    results = await youtube_service.search_videos("test query")
    
    # 検証
    assert len(results) == 1
    video = results[0]
    assert video["video_id"] == "test_video_id"
    assert video["title"] == "Test Video"
    assert video["view_count"] == 1000
    assert video["like_count"] == 100
    assert video["comment_count"] == 50

@pytest.mark.asyncio
async def test_get_video_details(youtube_service):
    # モックの設定
    mock_response = {
        "items": [
            {
                "snippet": {
                    "title": "Test Video",
                    "description": "Test Description",
                    "publishedAt": "2024-03-14T00:00:00Z",
                    "channelTitle": "Test Channel",
                    "thumbnails": {"high": {"url": "https://example.com/thumbnail.jpg"}}
                },
                "statistics": {
                    "viewCount": "1000",
                    "likeCount": "100",
                    "commentCount": "50"
                },
                "contentDetails": {"duration": "PT10M30S"}
            }
        ]
    }
    
    youtube_service.youtube.videos().list().execute.return_value = mock_response
    
    # テスト実行
    video = await youtube_service.get_video_details("test_video_id")
    
    # 検証
    assert video is not None
    assert video["video_id"] == "test_video_id"
    assert video["title"] == "Test Video"
    assert video["view_count"] == 1000
    assert video["like_count"] == 100
    assert video["comment_count"] == 50 