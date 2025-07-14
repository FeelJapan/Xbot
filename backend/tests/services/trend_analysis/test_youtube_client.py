import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.trend_analysis.youtube_client import YouTubeClient

@pytest.fixture
def mock_youtube():
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube
        yield mock_youtube

@pytest.fixture
def youtube_client(mock_youtube):
    with patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'}):
        client = YouTubeClient()
        yield client

@pytest.mark.asyncio
async def test_get_trending_videos(youtube_client, mock_youtube):
    # モックのレスポンスを設定
    mock_response = {
        'items': [
            {
                'id': 'test_video_id',
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test Description',
                    'publishedAt': '2024-01-01T00:00:00Z',
                    'channelId': 'test_channel_id',
                    'channelTitle': 'Test Channel'
                },
                'statistics': {
                    'viewCount': '1000',
                    'likeCount': '100',
                    'commentCount': '50'
                },
                'contentDetails': {
                    'duration': 'PT10M30S'
                }
            }
        ]
    }
    
    mock_youtube.videos().list().execute.return_value = mock_response
    
    # テスト実行
    videos = await youtube_client.get_trending_videos()
    
    # アサーション
    assert len(videos) == 1
    video = videos[0]
    assert video['id'] == 'test_video_id'
    assert video['title'] == 'Test Video'
    assert video['view_count'] == 1000
    assert video['like_count'] == 100
    assert video['comment_count'] == 50

@pytest.mark.asyncio
async def test_get_video_comments(youtube_client, mock_youtube):
    # モックのレスポンスを設定
    mock_response = {
        'items': [
            {
                'id': 'test_comment_id',
                'snippet': {
                    'topLevelComment': {
                        'snippet': {
                            'authorDisplayName': 'Test User',
                            'textDisplay': 'Test Comment',
                            'likeCount': 10,
                            'publishedAt': '2024-01-01T00:00:00Z'
                        }
                    }
                }
            }
        ]
    }
    
    mock_youtube.commentThreads().list().execute.return_value = mock_response
    
    # テスト実行
    comments = await youtube_client.get_video_comments('test_video_id')
    
    # アサーション
    assert len(comments) == 1
    comment = comments[0]
    assert comment['id'] == 'test_comment_id'
    assert comment['author'] == 'Test User'
    assert comment['text'] == 'Test Comment'
    assert comment['like_count'] == 10

@pytest.mark.asyncio
async def test_analyze_video_trends(youtube_client, mock_youtube):
    # モックのレスポンスを設定
    mock_video_response = {
        'items': [
            {
                'id': 'test_video_id',
                'snippet': {
                    'title': 'Test Video',
                    'channelTitle': 'Test Channel'
                },
                'statistics': {
                    'viewCount': '1000',
                    'likeCount': '100',
                    'commentCount': '50'
                }
            }
        ]
    }
    
    mock_comment_response = {
        'items': [
            {
                'id': 'test_comment_id',
                'snippet': {
                    'topLevelComment': {
                        'snippet': {
                            'authorDisplayName': 'Test User',
                            'textDisplay': 'Test Comment',
                            'likeCount': 10,
                            'publishedAt': '2024-01-01T00:00:00Z'
                        }
                    }
                }
            }
        ]
    }
    
    mock_youtube.videos().list().execute.return_value = mock_video_response
    mock_youtube.commentThreads().list().execute.return_value = mock_comment_response
    
    # テスト実行
    analysis = await youtube_client.analyze_video_trends('test_video_id')
    
    # アサーション
    assert analysis['video_id'] == 'test_video_id'
    assert analysis['title'] == 'Test Video'
    assert analysis['channel_title'] == 'Test Channel'
    assert analysis['view_count'] == 1000
    assert analysis['like_count'] == 100
    assert analysis['comment_count'] == 50
    assert 'engagement_rate' in analysis
    assert 'comment_analysis' in analysis
    assert 'analyzed_at' in analysis

def test_calculate_engagement_rate(youtube_client):
    # テストケース1: 正常なケース
    statistics = {
        'viewCount': '1000',
        'likeCount': '100',
        'commentCount': '50'
    }
    rate = youtube_client._calculate_engagement_rate(statistics)
    assert rate == 15.0  # (100 + 50) / 1000 * 100
    
    # テストケース2: 視聴回数が0の場合
    statistics = {
        'viewCount': '0',
        'likeCount': '100',
        'commentCount': '50'
    }
    rate = youtube_client._calculate_engagement_rate(statistics)
    assert rate == 0.0

def test_analyze_comments(youtube_client):
    # テストケース1: コメントがある場合
    comments = [
        {'like_count': 10},
        {'like_count': 20},
        {'like_count': 30}
    ]
    analysis = youtube_client._analyze_comments(comments)
    assert analysis['total_comments'] == 3
    assert analysis['average_likes'] == 20.0
    assert analysis['sentiment'] == 'neutral'
    
    # テストケース2: コメントがない場合
    comments = []
    analysis = youtube_client._analyze_comments(comments)
    assert analysis['total_comments'] == 0
    assert analysis['average_likes'] == 0
    assert analysis['sentiment'] == 'neutral' 