import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from ...trend_analysis.services.collector import TrendCollector
from ...trend_analysis.models import TrendVideo, VideoStats
from ...trend_analysis.repositories.trend_repository import TrendRepository

@pytest.fixture
def mock_youtube_service():
    return Mock()

@pytest.fixture
def mock_trend_repository():
    return Mock(spec=TrendRepository)

@pytest.fixture
def trend_collector(mock_youtube_service, mock_trend_repository):
    return TrendCollector(mock_youtube_service, mock_trend_repository)

@pytest.mark.asyncio
async def test_collect_trends(trend_collector, mock_youtube_service, mock_trend_repository):
    # モックの設定
    mock_video = TrendVideo(
        video_id="test_video_id",
        title="Test Video",
        description="Test Description",
        published_at=datetime.now(),
        channel_id="test_channel_id",
        channel_title="Test Channel",
        stats=VideoStats(
            view_count=1000,
            like_count=100,
            comment_count=50,
            engagement_rate=15.0
        ),
        buzz_score=0.0
    )

    mock_youtube_service.get_trending_videos.return_value = [mock_video]
    mock_trend_repository.save_video.return_value = mock_video
    mock_trend_repository.delete_old_videos.return_value = 0

    # テスト実行
    result = await trend_collector.collect_trends()

    # 検証
    assert len(result) == 1
    assert result[0].video_id == "test_video_id"
    mock_youtube_service.get_trending_videos.assert_called_once()
    mock_trend_repository.save_video.assert_called_once_with(mock_video)
    mock_trend_repository.delete_old_videos.assert_called_once_with(days=30)

@pytest.mark.asyncio
async def test_collect_trends_error(trend_collector, mock_youtube_service):
    # エラーを発生させる
    mock_youtube_service.get_trending_videos.side_effect = Exception("API Error")

    # テスト実行と検証
    with pytest.raises(Exception) as exc_info:
        await trend_collector.collect_trends()
    assert str(exc_info.value) == "API Error"

@pytest.mark.asyncio
async def test_start_collection_loop(trend_collector, mock_youtube_service, mock_trend_repository):
    # モックの設定
    mock_video = TrendVideo(
        video_id="test_video_id",
        title="Test Video",
        description="Test Description",
        published_at=datetime.now(),
        channel_id="test_channel_id",
        channel_title="Test Channel",
        stats=VideoStats(
            view_count=1000,
            like_count=100,
            comment_count=50,
            engagement_rate=15.0
        ),
        buzz_score=0.0
    )

    mock_youtube_service.get_trending_videos.return_value = [mock_video]
    mock_trend_repository.save_video.return_value = mock_video
    mock_trend_repository.delete_old_videos.return_value = 0

    # テスト実行（短い間隔で1回だけ実行）
    with patch('asyncio.sleep') as mock_sleep:
        mock_sleep.side_effect = Exception("Stop loop")
        with pytest.raises(Exception) as exc_info:
            await trend_collector.start_collection_loop(interval_minutes=0.1)
        assert str(exc_info.value) == "Stop loop"

    # 検証
    mock_youtube_service.get_trending_videos.assert_called_once()
    mock_trend_repository.save_video.assert_called_once_with(mock_video)
    mock_trend_repository.delete_old_videos.assert_called_once_with(days=30) 