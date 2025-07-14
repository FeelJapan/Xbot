import pytest
from datetime import datetime, timedelta
from backend.services.trend_analyzer import TrendAnalyzer
from backend.models.trend_data import TrendData

@pytest.fixture
def trend_analyzer():
    return TrendAnalyzer()

@pytest.fixture
def sample_trend_data():
    return [
        TrendData(
            id=1,
            keyword="test",
            category="technology",
            timestamp=datetime.now(),
            score=85,
            engagement_rate=0.15,
            comment_count=100,
            view_count=1000
        ),
        TrendData(
            id=2,
            keyword="test2",
            category="gaming",
            timestamp=datetime.now() - timedelta(days=1),
            score=75,
            engagement_rate=0.12,
            comment_count=80,
            view_count=800
        )
    ]

class TestTrendAnalyzer:
    def test_keyword_search(self, trend_analyzer, sample_trend_data):
        """キーワード検索機能のテスト"""
        # キーワード検索のテスト
        results = trend_analyzer.search_by_keyword(sample_trend_data, "test")
        assert len(results) == 1
        assert results[0].keyword == "test"

        # 部分一致のテスト
        results = trend_analyzer.search_by_keyword(sample_trend_data, "te")
        assert len(results) == 2

        # 大文字小文字を区別しないテスト
        results = trend_analyzer.search_by_keyword(sample_trend_data, "TEST")
        assert len(results) == 1

    def test_category_analysis(self, trend_analyzer, sample_trend_data):
        """カテゴリ別分析のテスト"""
        # カテゴリ別の集計テスト
        category_stats = trend_analyzer.analyze_by_category(sample_trend_data)
        assert "technology" in category_stats
        assert "gaming" in category_stats
        assert category_stats["technology"]["count"] == 1
        assert category_stats["gaming"]["count"] == 1

        # カテゴリ別の平均スコアテスト
        assert category_stats["technology"]["avg_score"] == 85
        assert category_stats["gaming"]["avg_score"] == 75

    def test_time_series_analysis(self, trend_analyzer, sample_trend_data):
        """時系列分析のテスト"""
        # 時系列でのトレンド変化のテスト
        time_series = trend_analyzer.analyze_time_series(sample_trend_data)
        assert len(time_series) == 2

        # 日付順のソートテスト
        assert time_series[0].timestamp > time_series[1].timestamp

        # スコアの推移テスト
        assert time_series[0].score == 85
        assert time_series[1].score == 75

    def test_empty_data_handling(self, trend_analyzer):
        """空データの処理テスト"""
        # 空のデータでの検索テスト
        results = trend_analyzer.search_by_keyword([], "test")
        assert len(results) == 0

        # 空のデータでのカテゴリ分析テスト
        category_stats = trend_analyzer.analyze_by_category([])
        assert len(category_stats) == 0

        # 空のデータでの時系列分析テスト
        time_series = trend_analyzer.analyze_time_series([])
        assert len(time_series) == 0 