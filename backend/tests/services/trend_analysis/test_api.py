import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

@pytest.fixture
def client():
    # YouTubeClientの初期化をモックしてテスト用に置き換える
    with patch('app.services.trend_analysis.youtube_client.YouTubeClient'):
        from app.services.trend_analysis.main import app
        return TestClient(app)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Trend Analysis Service is running"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

@pytest.mark.asyncio
async def test_get_youtube_trends(client):
    mock_videos = [
        {
            "id": "test_video_id",
            "title": "Test Video",
            "description": "Test Description",
            "published_at": "2024-01-01T00:00:00Z",
            "channel_id": "test_channel_id",
            "channel_title": "Test Channel",
            "view_count": 1000,
            "like_count": 100,
            "comment_count": 50,
            "duration": "PT10M30S"
        }
    ]
    
    with patch('app.services.trend_analysis.main.youtube_client.get_trending_videos') as mock_get_trends:
        mock_get_trends.return_value = mock_videos
        
        response = client.get("/api/v1/trends/youtube")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "test_video_id"
        assert "timestamp" in data

@pytest.mark.asyncio
async def test_analyze_trends(client):
    mock_analysis = {
        "video_id": "test_video_id",
        "title": "Test Video",
        "channel_title": "Test Channel",
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 50,
        "engagement_rate": 15.0,
        "comment_analysis": {
            "total_comments": 1,
            "average_likes": 10.0,
            "sentiment": "neutral"
        },
        "analyzed_at": "2024-01-01T00:00:00Z"
    }
    
    with patch('app.services.trend_analysis.main.youtube_client.analyze_video_trends') as mock_analyze:
        mock_analyze.return_value = mock_analysis
        
        response = client.get("/api/v1/trends/analyze?video_id=test_video_id")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["video_id"] == "test_video_id"
        assert data["data"]["title"] == "Test Video"
        assert "timestamp" in data

def test_get_youtube_trends_error(client):
    with patch('app.services.trend_analysis.main.youtube_client.get_trending_videos') as mock_get_trends:
        mock_get_trends.side_effect = Exception("API Error")
        
        response = client.get("/api/v1/trends/youtube")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

def test_analyze_trends_error(client):
    with patch('app.services.trend_analysis.main.youtube_client.analyze_video_trends') as mock_analyze:
        mock_analyze.side_effect = Exception("API Error")
        
        response = client.get("/api/v1/trends/analyze?video_id=test_video_id")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data 