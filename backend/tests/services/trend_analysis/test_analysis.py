import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from trend_analysis.services.analysis import AnalysisService
from trend_analysis.models import TrendVideo, VideoStats, VideoStatsHistory, ForeignReaction

@pytest.fixture
def analysis_service():
    return AnalysisService()

@pytest.fixture
def mock_video():
    stats = VideoStats(
        view_count=1000,
        like_count=100,
        comment_count=50,
        engagement_rate=15.0
    )
    
    # 時系列データの追加
    history = [
        VideoStatsHistory(
            view_count=500,
            like_count=50,
            comment_count=25,
            engagement_rate=10.0,
            recorded_at=datetime.now() - timedelta(hours=2)
        ),
        VideoStatsHistory(
            view_count=1000,
            like_count=100,
            comment_count=50,
            engagement_rate=15.0,
            recorded_at=datetime.now()
        )
    ]
    stats.history = history
    
    return TrendVideo(
        video_id="test_video_id",
        title="Test Video",
        description="Test Description",
        published_at=datetime.now(),
        channel_id="test_channel_id",
        channel_title="Test Channel",
        stats=stats
    )

@pytest.mark.asyncio
async def test_analyze_trends(analysis_service, mock_video):
    # テスト実行
    analyzed_videos = await analysis_service.analyze_trends([mock_video])
    
    # 検証
    assert len(analyzed_videos) == 1
    video = analyzed_videos[0]
    assert video.buzz_score > 0
    assert "trend_analysis" in video.analysis
    assert "sentiment_analysis" in video.analysis

def test_analyze_trends_over_time(analysis_service, mock_video):
    # テスト実行
    trend_analysis = analysis_service._analyze_trends_over_time(mock_video)
    
    # 検証
    assert "view_growth_rate" in trend_analysis
    assert "engagement_growth_rate" in trend_analysis
    assert "comment_growth_rate" in trend_analysis
    assert "trend_direction" in trend_analysis
    assert trend_analysis["trend_direction"] in ["increasing", "stable", "decreasing"]

def test_analyze_sentiment(analysis_service, mock_video):
    # モックコメントの追加
    mock_video.comments = [
        Mock(text="素晴らしい動画です！", like_count=10),
        Mock(text="普通の動画ですね", like_count=5),
        Mock(text="あまり良くない動画です", like_count=2)
    ]
    
    # テスト実行
    sentiment_analysis = analysis_service._analyze_sentiment(mock_video)
    
    # 検証
    assert "sentiment_score" in sentiment_analysis
    assert "sentiment_distribution" in sentiment_analysis
    assert "dominant_sentiment" in sentiment_analysis
    assert sentiment_analysis["dominant_sentiment"] in ["positive", "neutral", "negative"]

def test_calculate_sentiment_score(analysis_service, mock_video):
    # モックコメントの追加
    mock_video.comments = [
        Mock(text="素晴らしい動画です！", like_count=10),
        Mock(text="普通の動画ですね", like_count=5),
        Mock(text="あまり良くない動画です", like_count=2)
    ]
    
    # テスト実行
    score = analysis_service._calculate_sentiment_score(mock_video)
    
    # 検証
    assert 0 <= score <= 10

def test_determine_trend_direction(analysis_service):
    # テストケース1: 増加トレンド
    direction = analysis_service._determine_trend_direction(200, 150, 100)
    assert direction == "increasing"
    
    # テストケース2: 減少トレンド
    direction = analysis_service._determine_trend_direction(-200, -150, -100)
    assert direction == "decreasing"
    
    # テストケース3: 安定トレンド
    direction = analysis_service._determine_trend_direction(50, 30, 20)
    assert direction == "stable"

def test_determine_dominant_sentiment(analysis_service):
    # テストケース1: ポジティブ
    sentiment = analysis_service._determine_dominant_sentiment(0.6, 0.2, 0.2)
    assert sentiment == "positive"
    
    # テストケース2: ネガティブ
    sentiment = analysis_service._determine_dominant_sentiment(0.2, 0.2, 0.6)
    assert sentiment == "negative"
    
    # テストケース3: ニュートラル
    sentiment = analysis_service._determine_dominant_sentiment(0.3, 0.4, 0.3)
    assert sentiment == "neutral"

def test_analyze_foreign_reaction(analysis_service, mock_video):
    # モックコメントの追加
    mock_video.comments = [
        Mock(text="This is amazing! 😍", like_count=100),
        Mock(text="普通の動画ですね", like_count=5),
        Mock(text="I love this content! ❤️", like_count=50),
        Mock(text="Not bad at all", like_count=20)
    ]
    
    # テスト実行
    foreign_reaction = analysis_service._analyze_foreign_reaction(mock_video)
    
    # 検証
    assert isinstance(foreign_reaction, ForeignReaction)
    assert -1 <= foreign_reaction.sentiment_score <= 1
    assert foreign_reaction.reaction_type in ["positive", "neutral", "negative"]
    assert len(foreign_reaction.comment_examples) <= 3
    assert all(isinstance(comment, str) for comment in foreign_reaction.comment_examples)

def test_is_foreign_comment(analysis_service):
    # 英語コメント
    assert analysis_service._is_foreign_comment("This is a test comment")
    assert analysis_service._is_foreign_comment("Hello! 👋")
    
    # 日本語コメント
    assert not analysis_service._is_foreign_comment("これはテストコメントです")
    assert not analysis_service._is_foreign_comment("こんにちは！👋")

def test_determine_reaction_type(analysis_service):
    # ポジティブな反応
    assert analysis_service._determine_reaction_type([], 0.5) == "positive"
    
    # ネガティブな反応
    assert analysis_service._determine_reaction_type([], -0.5) == "negative"
    
    # ニュートラルな反応
    assert analysis_service._determine_reaction_type([], 0.0) == "neutral"

def test_extract_representative_comments(analysis_service):
    comments = [
        {"text": "Great video!", "like_count": 100},
        {"text": "Nice content", "like_count": 50},
        {"text": "Good job", "like_count": 30},
        {"text": "Average", "like_count": 10}
    ]
    
    # テスト実行
    examples = analysis_service._extract_representative_comments(comments)
    
    # 検証
    assert len(examples) == 3
    assert examples[0] == "Great video!"
    assert examples[1] == "Nice content"
    assert examples[2] == "Good job"

def test_calculate_buzz_score(analysis_service, mock_video):
    # モックデータの設定
    mock_video.stats.view_count = 150000  # 15万回視聴
    mock_video.stats.engagement_rate = 12.0  # 12%のエンゲージメント率
    mock_video.stats.comment_count = 1500  # 1500コメント
    mock_video.stats.like_count = 10000  # 1万いいね
    
    # テスト実行
    score = analysis_service._calculate_buzz_score(mock_video)
    
    # 検証
    assert 0 <= score <= 100
    assert score > 0  # スコアは必ず正の値

def test_calculate_channel_score(analysis_service, mock_video):
    # モックデータの設定
    mock_video.channel_id = "test_channel"
    
    # テスト実行
    score = analysis_service._calculate_channel_score(mock_video)
    
    # 検証
    assert 0 <= score <= 15
    assert score == 5.0  # デフォルト値（チャンネル動画が取得できない場合）

def test_get_channel_videos(analysis_service, mock_video):
    # テスト実行
    videos = analysis_service._get_channel_videos(mock_video.channel_id)
    
    # 検証
    assert isinstance(videos, list)
    assert len(videos) == 0  # 現在は空のリストを返す実装 