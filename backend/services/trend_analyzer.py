from typing import List, Dict
from datetime import datetime
from backend.models.trend_data import TrendData

class TrendAnalyzer:
    def search_by_keyword(self, data: List[TrendData], keyword: str) -> List[TrendData]:
        """
        キーワードでトレンドデータを検索する
        
        Args:
            data: 検索対象のトレンドデータリスト
            keyword: 検索キーワード
            
        Returns:
            キーワードに一致するトレンドデータのリスト
        """
        if not data:
            return []
            
        keyword = keyword.lower()
        return [item for item in data if keyword in item.keyword.lower()]

    def analyze_by_category(self, data: List[TrendData]) -> Dict[str, Dict]:
        """
        カテゴリ別にトレンドデータを分析する
        
        Args:
            data: 分析対象のトレンドデータリスト
            
        Returns:
            カテゴリ別の統計情報を含む辞書
        """
        if not data:
            return {}
            
        category_stats = {}
        for item in data:
            if item.category not in category_stats:
                category_stats[item.category] = {
                    "count": 0,
                    "total_score": 0,
                    "avg_score": 0
                }
            
            stats = category_stats[item.category]
            stats["count"] += 1
            stats["total_score"] += item.score
            stats["avg_score"] = stats["total_score"] / stats["count"]
            
        return category_stats

    def analyze_time_series(self, data: List[TrendData]) -> List[TrendData]:
        """
        時系列でトレンドデータを分析する
        
        Args:
            data: 分析対象のトレンドデータリスト
            
        Returns:
            タイムスタンプでソートされたトレンドデータのリスト
        """
        if not data:
            return []
            
        return sorted(data, key=lambda x: x.timestamp, reverse=True) 