"""
投稿分析サービス
投稿のパフォーマンス分析、エンゲージメント統計、トレンド相関分析を行う
"""
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics

from core.logging.logger import get_logger
from app.services.post_manager import PostManager, Post, PostStatus, PostType
from app.services.trend_analysis.main import TrendAnalysisService

logger = get_logger("post_analytics")

class AnalyticsError(Exception):
    """分析関連のエラー"""
    pass

@dataclass
class EngagementMetrics:
    """エンゲージメント指標"""
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    impressions: int = 0
    clicks: int = 0
    profile_visits: int = 0
    follows: int = 0
    engagement_rate: float = 0.0  # (likes + retweets + replies) / impressions
    
    def calculate_engagement_rate(self) -> float:
        """エンゲージメント率を計算"""
        if self.impressions == 0:
            return 0.0
        return (self.likes + self.retweets + self.replies) / self.impressions * 100

@dataclass
class PostPerformance:
    """投稿パフォーマンス"""
    post_id: str
    posted_at: datetime
    content_type: PostType
    hashtags: List[str]
    metrics: EngagementMetrics
    performance_score: float = 0.0  # 0-100のスコア
    
@dataclass
class TimeSlotPerformance:
    """時間帯別パフォーマンス"""
    hour: int  # 0-23
    average_engagement_rate: float
    average_impressions: float
    post_count: int
    best_performing_type: PostType
    
@dataclass
class HashtagPerformance:
    """ハッシュタグパフォーマンス"""
    hashtag: str
    usage_count: int
    average_engagement_rate: float
    average_impressions: float
    trending_correlation: float  # トレンドとの相関度
    
@dataclass
class ContentTypePerformance:
    """コンテンツタイプ別パフォーマンス"""
    content_type: PostType
    post_count: int
    average_engagement_rate: float
    average_impressions: float
    best_time_slot: int  # 最も効果的な時間帯
    
@dataclass
class AnalyticsReport:
    """分析レポート"""
    period_start: datetime
    period_end: datetime
    total_posts: int
    total_impressions: int
    total_engagements: int
    average_engagement_rate: float
    best_post: Optional[PostPerformance]
    worst_post: Optional[PostPerformance]
    time_slot_performance: List[TimeSlotPerformance]
    hashtag_performance: List[HashtagPerformance]
    content_type_performance: List[ContentTypePerformance]
    recommendations: List[str]

class PostAnalytics:
    """投稿分析クラス"""
    
    def __init__(self, data_dir: str = "data/analytics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.performance_file = self.data_dir / "performance.json"
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # サービス初期化
        self.post_manager = PostManager()
        self.trend_service = TrendAnalysisService()
        
        # データ読み込み
        self.performance_data: Dict[str, PostPerformance] = {}
        self.load_data()
        
    def load_data(self) -> None:
        """データを読み込み"""
        try:
            if self.performance_file.exists():
                with open(self.performance_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.performance_data = {
                        post_id: self._dict_to_performance(perf_data)
                        for post_id, perf_data in data.items()
                    }
                    
            logger.info("分析データを読み込みました")
            
        except Exception as e:
            logger.error(f"分析データの読み込みに失敗しました: {str(e)}")
            
    def save_data(self) -> None:
        """データを保存"""
        try:
            data = {
                post_id: self._performance_to_dict(performance)
                for post_id, performance in self.performance_data.items()
            }
            
            with open(self.performance_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info("分析データを保存しました")
            
        except Exception as e:
            logger.error(f"分析データの保存に失敗しました: {str(e)}")
            raise AnalyticsError(f"分析データの保存に失敗しました: {str(e)}")
            
    def update_post_metrics(
        self,
        post_id: str,
        metrics: EngagementMetrics
    ) -> PostPerformance:
        """投稿のメトリクスを更新"""
        try:
            post = self.post_manager.get_post(post_id)
            if post is None:
                raise AnalyticsError(f"投稿が見つかりません: {post_id}")
                
            # エンゲージメント率を計算
            metrics.engagement_rate = metrics.calculate_engagement_rate()
            
            # パフォーマンススコアを計算
            performance_score = self._calculate_performance_score(metrics)
            
            performance = PostPerformance(
                post_id=post_id,
                posted_at=post.posted_at or post.created_at,
                content_type=post.post_type,
                hashtags=post.content.hashtags or [],
                metrics=metrics,
                performance_score=performance_score
            )
            
            self.performance_data[post_id] = performance
            
            # 投稿のengagement_statsも更新
            post.engagement_stats = {
                "likes": metrics.likes,
                "retweets": metrics.retweets,
                "replies": metrics.replies,
                "impressions": metrics.impressions,
                "engagement_rate": metrics.engagement_rate,
                "performance_score": performance_score
            }
            self.post_manager.save_data()
            
            self.save_data()
            logger.info(f"投稿のメトリクスを更新しました: {post_id}")
            return performance
            
        except Exception as e:
            logger.error(f"投稿メトリクスの更新に失敗しました: {str(e)}")
            raise AnalyticsError(f"投稿メトリクスの更新に失敗しました: {str(e)}")
            
    def get_post_performance(self, post_id: str) -> Optional[PostPerformance]:
        """投稿のパフォーマンスを取得"""
        return self.performance_data.get(post_id)
        
    def analyze_time_slots(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TimeSlotPerformance]:
        """時間帯別パフォーマンスを分析"""
        try:
            # 期間の設定
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=30)
                
            # 時間帯別にデータを集計
            time_slot_data: Dict[int, Dict[str, List[float]]] = {}
            
            for performance in self.performance_data.values():
                if start_date <= performance.posted_at <= end_date:
                    hour = performance.posted_at.hour
                    
                    if hour not in time_slot_data:
                        time_slot_data[hour] = {
                            "engagement_rates": [],
                            "impressions": [],
                            "content_types": []
                        }
                        
                    time_slot_data[hour]["engagement_rates"].append(
                        performance.metrics.engagement_rate
                    )
                    time_slot_data[hour]["impressions"].append(
                        performance.metrics.impressions
                    )
                    time_slot_data[hour]["content_types"].append(
                        performance.content_type
                    )
                    
            # 統計を計算
            results = []
            for hour, data in time_slot_data.items():
                if data["engagement_rates"]:
                    # 最も多いコンテンツタイプを特定
                    content_type_counts = {}
                    for ct in data["content_types"]:
                        content_type_counts[ct] = content_type_counts.get(ct, 0) + 1
                    best_type = max(content_type_counts, key=content_type_counts.get)
                    
                    results.append(TimeSlotPerformance(
                        hour=hour,
                        average_engagement_rate=statistics.mean(data["engagement_rates"]),
                        average_impressions=statistics.mean(data["impressions"]),
                        post_count=len(data["engagement_rates"]),
                        best_performing_type=best_type
                    ))
                    
            return sorted(results, key=lambda x: x.average_engagement_rate, reverse=True)
            
        except Exception as e:
            logger.error(f"時間帯別分析に失敗しました: {str(e)}")
            return []
            
    def analyze_hashtags(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HashtagPerformance]:
        """ハッシュタグパフォーマンスを分析"""
        try:
            # 期間の設定
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=30)
                
            # ハッシュタグ別にデータを集計
            hashtag_data: Dict[str, Dict[str, List[float]]] = {}
            
            for performance in self.performance_data.values():
                if start_date <= performance.posted_at <= end_date:
                    for hashtag in performance.hashtags:
                        if hashtag not in hashtag_data:
                            hashtag_data[hashtag] = {
                                "engagement_rates": [],
                                "impressions": []
                            }
                            
                        hashtag_data[hashtag]["engagement_rates"].append(
                            performance.metrics.engagement_rate
                        )
                        hashtag_data[hashtag]["impressions"].append(
                            performance.metrics.impressions
                        )
                        
            # トレンドデータを取得
            trending_hashtags = self._get_trending_hashtags()
            
            # 統計を計算
            results = []
            for hashtag, data in hashtag_data.items():
                if data["engagement_rates"]:
                    # トレンドとの相関を計算
                    trending_correlation = 1.0 if hashtag in trending_hashtags else 0.5
                    
                    results.append(HashtagPerformance(
                        hashtag=hashtag,
                        usage_count=len(data["engagement_rates"]),
                        average_engagement_rate=statistics.mean(data["engagement_rates"]),
                        average_impressions=statistics.mean(data["impressions"]),
                        trending_correlation=trending_correlation
                    ))
                    
            return sorted(results, key=lambda x: x.average_engagement_rate, reverse=True)
            
        except Exception as e:
            logger.error(f"ハッシュタグ分析に失敗しました: {str(e)}")
            return []
            
    def analyze_content_types(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ContentTypePerformance]:
        """コンテンツタイプ別パフォーマンスを分析"""
        try:
            # 期間の設定
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=30)
                
            # コンテンツタイプ別にデータを集計
            content_type_data: Dict[PostType, Dict[str, Any]] = {}
            
            for performance in self.performance_data.values():
                if start_date <= performance.posted_at <= end_date:
                    ct = performance.content_type
                    
                    if ct not in content_type_data:
                        content_type_data[ct] = {
                            "engagement_rates": [],
                            "impressions": [],
                            "hours": []
                        }
                        
                    content_type_data[ct]["engagement_rates"].append(
                        performance.metrics.engagement_rate
                    )
                    content_type_data[ct]["impressions"].append(
                        performance.metrics.impressions
                    )
                    content_type_data[ct]["hours"].append(
                        performance.posted_at.hour
                    )
                    
            # 統計を計算
            results = []
            for content_type, data in content_type_data.items():
                if data["engagement_rates"]:
                    # 最も効果的な時間帯を特定
                    hour_performance = {}
                    for i, hour in enumerate(data["hours"]):
                        if hour not in hour_performance:
                            hour_performance[hour] = []
                        hour_performance[hour].append(data["engagement_rates"][i])
                        
                    best_hour = max(
                        hour_performance.items(),
                        key=lambda x: statistics.mean(x[1])
                    )[0]
                    
                    results.append(ContentTypePerformance(
                        content_type=content_type,
                        post_count=len(data["engagement_rates"]),
                        average_engagement_rate=statistics.mean(data["engagement_rates"]),
                        average_impressions=statistics.mean(data["impressions"]),
                        best_time_slot=best_hour
                    ))
                    
            return sorted(results, key=lambda x: x.average_engagement_rate, reverse=True)
            
        except Exception as e:
            logger.error(f"コンテンツタイプ分析に失敗しました: {str(e)}")
            return []
            
    def generate_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AnalyticsReport:
        """分析レポートを生成"""
        try:
            # 期間の設定
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=30)
                
            # 期間内のパフォーマンスデータを取得
            period_performance = [
                p for p in self.performance_data.values()
                if start_date <= p.posted_at <= end_date
            ]
            
            if not period_performance:
                # データがない場合の空レポート
                return AnalyticsReport(
                    period_start=start_date,
                    period_end=end_date,
                    total_posts=0,
                    total_impressions=0,
                    total_engagements=0,
                    average_engagement_rate=0.0,
                    best_post=None,
                    worst_post=None,
                    time_slot_performance=[],
                    hashtag_performance=[],
                    content_type_performance=[],
                    recommendations=["投稿データがありません。投稿を開始してください。"]
                )
                
            # 統計を計算
            total_posts = len(period_performance)
            total_impressions = sum(p.metrics.impressions for p in period_performance)
            total_engagements = sum(
                p.metrics.likes + p.metrics.retweets + p.metrics.replies
                for p in period_performance
            )
            average_engagement_rate = statistics.mean(
                p.metrics.engagement_rate for p in period_performance
            )
            
            # ベスト/ワースト投稿
            sorted_performance = sorted(
                period_performance,
                key=lambda x: x.performance_score,
                reverse=True
            )
            best_post = sorted_performance[0] if sorted_performance else None
            worst_post = sorted_performance[-1] if sorted_performance else None
            
            # 詳細分析
            time_slot_performance = self.analyze_time_slots(start_date, end_date)
            hashtag_performance = self.analyze_hashtags(start_date, end_date)
            content_type_performance = self.analyze_content_types(start_date, end_date)
            
            # レコメンデーションを生成
            recommendations = self._generate_recommendations(
                time_slot_performance,
                hashtag_performance,
                content_type_performance
            )
            
            report = AnalyticsReport(
                period_start=start_date,
                period_end=end_date,
                total_posts=total_posts,
                total_impressions=total_impressions,
                total_engagements=total_engagements,
                average_engagement_rate=average_engagement_rate,
                best_post=best_post,
                worst_post=worst_post,
                time_slot_performance=time_slot_performance,
                hashtag_performance=hashtag_performance,
                content_type_performance=content_type_performance,
                recommendations=recommendations
            )
            
            # レポートを保存
            self._save_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"レポート生成に失敗しました: {str(e)}")
            raise AnalyticsError(f"レポート生成に失敗しました: {str(e)}")
            
    def _calculate_performance_score(self, metrics: EngagementMetrics) -> float:
        """パフォーマンススコアを計算（0-100）"""
        try:
            # 各指標の重み付け
            engagement_weight = 0.4
            impression_weight = 0.3
            interaction_weight = 0.3
            
            # エンゲージメント率スコア（最大40点）
            engagement_score = min(metrics.engagement_rate * 4, 40)
            
            # インプレッションスコア（最大30点）
            impression_score = min(metrics.impressions / 1000, 30)
            
            # インタラクションスコア（最大30点）
            interaction_score = min(
                (metrics.clicks + metrics.profile_visits + metrics.follows) / 10,
                30
            )
            
            total_score = (
                engagement_score * engagement_weight +
                impression_score * impression_weight +
                interaction_score * interaction_weight
            )
            
            return min(total_score, 100.0)
            
        except Exception as e:
            logger.error(f"スコア計算エラー: {str(e)}")
            return 0.0
            
    def _get_trending_hashtags(self) -> List[str]:
        """現在のトレンドハッシュタグを取得"""
        try:
            # トレンド分析サービスから取得
            trends = self.trend_service.get_latest_trends(limit=50)
            hashtags = []
            
            for trend in trends:
                if hasattr(trend, 'hashtags'):
                    hashtags.extend(trend.hashtags)
                    
            return list(set(hashtags))
            
        except Exception as e:
            logger.error(f"トレンドハッシュタグ取得エラー: {str(e)}")
            return []
            
    def _generate_recommendations(
        self,
        time_slots: List[TimeSlotPerformance],
        hashtags: List[HashtagPerformance],
        content_types: List[ContentTypePerformance]
    ) -> List[str]:
        """レコメンデーションを生成"""
        recommendations = []
        
        # 時間帯の推奨
        if time_slots:
            best_slots = time_slots[:3]
            slot_times = [f"{slot.hour}時" for slot in best_slots]
            recommendations.append(
                f"最も効果的な投稿時間: {', '.join(slot_times)}"
            )
            
        # ハッシュタグの推奨
        if hashtags:
            trending_tags = [h for h in hashtags if h.trending_correlation > 0.7][:3]
            if trending_tags:
                tag_names = [h.hashtag for h in trending_tags]
                recommendations.append(
                    f"トレンドと相関の高いハッシュタグ: {', '.join(tag_names)}"
                )
                
        # コンテンツタイプの推奨
        if content_types:
            best_type = content_types[0]
            recommendations.append(
                f"最も効果的なコンテンツタイプ: {best_type.content_type.value}"
            )
            
        # パフォーマンス向上のヒント
        if len(self.performance_data) > 10:
            avg_score = statistics.mean(
                p.performance_score for p in self.performance_data.values()
            )
            if avg_score < 50:
                recommendations.append(
                    "エンゲージメント率向上のため、ユーザーとの対話を増やしましょう"
                )
                
        return recommendations
        
    def _save_report(self, report: AnalyticsReport) -> None:
        """レポートを保存"""
        try:
            filename = f"report_{report.period_start.strftime('%Y%m%d')}_{report.period_end.strftime('%Y%m%d')}.json"
            filepath = self.reports_dir / filename
            
            report_data = self._report_to_dict(report)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"レポートを保存しました: {filename}")
            
        except Exception as e:
            logger.error(f"レポート保存エラー: {str(e)}")
            
    def _performance_to_dict(self, performance: PostPerformance) -> Dict[str, Any]:
        """PostPerformanceを辞書に変換"""
        return {
            "post_id": performance.post_id,
            "posted_at": performance.posted_at.isoformat(),
            "content_type": performance.content_type.value,
            "hashtags": performance.hashtags,
            "metrics": asdict(performance.metrics),
            "performance_score": performance.performance_score
        }
        
    def _dict_to_performance(self, data: Dict[str, Any]) -> PostPerformance:
        """辞書をPostPerformanceに変換"""
        metrics = EngagementMetrics(**data["metrics"])
        
        return PostPerformance(
            post_id=data["post_id"],
            posted_at=datetime.fromisoformat(data["posted_at"]),
            content_type=PostType(data["content_type"]),
            hashtags=data["hashtags"],
            metrics=metrics,
            performance_score=data["performance_score"]
        )
        
    def _report_to_dict(self, report: AnalyticsReport) -> Dict[str, Any]:
        """AnalyticsReportを辞書に変換"""
        return {
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "total_posts": report.total_posts,
            "total_impressions": report.total_impressions,
            "total_engagements": report.total_engagements,
            "average_engagement_rate": report.average_engagement_rate,
            "best_post": self._performance_to_dict(report.best_post) if report.best_post else None,
            "worst_post": self._performance_to_dict(report.worst_post) if report.worst_post else None,
            "time_slot_performance": [asdict(ts) for ts in report.time_slot_performance],
            "hashtag_performance": [asdict(hp) for hp in report.hashtag_performance],
            "content_type_performance": [
                {
                    "content_type": ctp.content_type.value,
                    "post_count": ctp.post_count,
                    "average_engagement_rate": ctp.average_engagement_rate,
                    "average_impressions": ctp.average_impressions,
                    "best_time_slot": ctp.best_time_slot
                }
                for ctp in report.content_type_performance
            ],
            "recommendations": report.recommendations
        } 