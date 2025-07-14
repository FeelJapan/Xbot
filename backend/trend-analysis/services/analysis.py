from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..models import TrendVideo, ForeignReaction, VideoStats
from ..core.logging import get_logger
from textblob import TextBlob
import numpy as np

logger = get_logger(__name__)

class AnalysisService:
    def __init__(self):
        self.logger = logger

    async def analyze_trends(self, videos: List[TrendVideo]) -> List[TrendVideo]:
        """
        動画のトレンドを分析する

        Args:
            videos: 分析対象の動画リスト

        Returns:
            List[TrendVideo]: 分析結果を含む動画リスト
        """
        analyzed_videos = []
        for video in videos:
            try:
                # バズり度スコアの計算
                video.buzz_score = self._calculate_buzz_score(video)
                
                # 時系列分析の実行
                trend_analysis = self._analyze_trends_over_time(video)
                
                # コメントの感情分析
                sentiment_analysis = self._analyze_sentiment(video)
                
                # 分析結果を動画オブジェクトに追加
                video.analysis = {
                    "trend_analysis": trend_analysis,
                    "sentiment_analysis": sentiment_analysis
                }
                
                analyzed_videos.append(video)
                
            except Exception as e:
                self.logger.error(f"Error analyzing video {video.video_id}: {str(e)}")
                continue
                
        return analyzed_videos

    def _calculate_buzz_score(self, video: TrendVideo) -> float:
        """
        バズり度スコアを計算する

        スコアの計算要素:
        - 視聴回数の増加率（0-30点）
        - エンゲージメント率（0-25点）
        - コメントの活性度（0-20点）
        - チャンネルの影響力（0-15点）
        - 感情分析スコア（0-10点）

        Returns:
            float: バズり度スコア（0-100）
        """
        try:
            # 視聴回数スコア（0-30点）
            # 10万回視聴で30点、それ以上は30点固定
            view_score = min(video.stats.view_count / 100000 * 30, 30)

            # エンゲージメントスコア（0-25点）
            # エンゲージメント率が10%で25点、それ以上は25点固定
            engagement_score = min(video.stats.engagement_rate * 2.5, 25)

            # コメント活性度スコア（0-20点）
            # 1000コメントで20点、それ以上は20点固定
            comment_score = min(video.stats.comment_count / 1000 * 20, 20)

            # チャンネル影響力スコア（0-15点）
            channel_score = self._calculate_channel_score(video)

            # 感情分析スコア（0-10点）
            sentiment_score = self._calculate_sentiment_score(video)

            # 合計スコア
            total_score = view_score + engagement_score + comment_score + channel_score + sentiment_score

            return min(total_score, 100)

        except Exception as e:
            self.logger.error(f"Error calculating buzz score: {str(e)}")
            return 0.0

    def _calculate_channel_score(self, video: TrendVideo) -> float:
        """
        チャンネルの影響力スコアを計算する

        Args:
            video: 分析対象の動画

        Returns:
            float: チャンネル影響力スコア（0-15）
        """
        try:
            # チャンネルの過去の動画の平均視聴回数を取得
            channel_videos = self._get_channel_videos(video.channel_id)
            if not channel_videos:
                return 5.0  # デフォルト値

            # 平均視聴回数を計算
            avg_views = sum(v.stats.view_count for v in channel_videos) / len(channel_videos)
            
            # スコアの計算（10万回視聴で15点、それ以上は15点固定）
            score = min(avg_views / 100000 * 15, 15)
            
            return score

        except Exception as e:
            self.logger.error(f"Error calculating channel score: {str(e)}")
            return 5.0  # エラー時はデフォルト値を返す

    def _get_channel_videos(self, channel_id: str, limit: int = 10) -> List[TrendVideo]:
        """
        チャンネルの過去の動画を取得する

        Args:
            channel_id: チャンネルID
            limit: 取得する動画の最大数

        Returns:
            List[TrendVideo]: チャンネルの動画リスト
        """
        try:
            # TODO: 実際のデータベースから取得する実装に変更
            return []
        except Exception as e:
            self.logger.error(f"Error getting channel videos: {str(e)}")
            return []

    def _analyze_trends_over_time(self, video: TrendVideo) -> Dict:
        """
        時系列での統計情報の変化を分析する

        Args:
            video: 分析対象の動画

        Returns:
            Dict: 時系列分析結果
        """
        try:
            if not video.stats.history:
                return {
                    "view_growth_rate": 0.0,
                    "engagement_growth_rate": 0.0,
                    "comment_growth_rate": 0.0,
                    "trend_direction": "stable"
                }

            # 最新と最古の統計情報を取得
            latest_stats = video.stats.history[-1]
            oldest_stats = video.stats.history[0]
            
            # 経過時間（時間）
            time_diff = (latest_stats.recorded_at - oldest_stats.recorded_at).total_seconds() / 3600
            
            if time_diff == 0:
                return {
                    "view_growth_rate": 0.0,
                    "engagement_growth_rate": 0.0,
                    "comment_growth_rate": 0.0,
                    "trend_direction": "stable"
                }

            # 成長率の計算（1時間あたり）
            view_growth = (latest_stats.view_count - oldest_stats.view_count) / time_diff
            engagement_growth = (latest_stats.engagement_rate - oldest_stats.engagement_rate) / time_diff
            comment_growth = (latest_stats.comment_count - oldest_stats.comment_count) / time_diff

            # トレンドの方向を判定
            trend_direction = self._determine_trend_direction(
                view_growth, engagement_growth, comment_growth
            )

            return {
                "view_growth_rate": view_growth,
                "engagement_growth_rate": engagement_growth,
                "comment_growth_rate": comment_growth,
                "trend_direction": trend_direction
            }

        except Exception as e:
            self.logger.error(f"Error analyzing trends over time: {str(e)}")
            return {
                "view_growth_rate": 0.0,
                "engagement_growth_rate": 0.0,
                "comment_growth_rate": 0.0,
                "trend_direction": "stable"
            }

    def _analyze_sentiment(self, video: TrendVideo) -> Dict:
        """
        コメントの感情分析を行う

        Args:
            video: 分析対象の動画

        Returns:
            Dict: 感情分析結果
        """
        try:
            if not hasattr(video, 'comments') or not video.comments:
                return {
                    "sentiment_score": 0.0,
                    "sentiment_distribution": {
                        "positive": 0.0,
                        "neutral": 0.0,
                        "negative": 0.0
                    },
                    "dominant_sentiment": "neutral"
                }

            sentiments = []
            for comment in video.comments:
                blob = TextBlob(comment.text)
                sentiments.append(blob.sentiment.polarity)

            if not sentiments:
                return {
                    "sentiment_score": 0.0,
                    "sentiment_distribution": {
                        "positive": 0.0,
                        "neutral": 0.0,
                        "negative": 0.0
                    },
                    "dominant_sentiment": "neutral"
                }

            # 感情スコアの計算
            avg_sentiment = np.mean(sentiments)
            
            # 感情分布の計算
            positive = len([s for s in sentiments if s > 0.1]) / len(sentiments)
            neutral = len([s for s in sentiments if -0.1 <= s <= 0.1]) / len(sentiments)
            negative = len([s for s in sentiments if s < -0.1]) / len(sentiments)

            # 主要な感情を判定
            dominant_sentiment = self._determine_dominant_sentiment(positive, neutral, negative)

            return {
                "sentiment_score": avg_sentiment,
                "sentiment_distribution": {
                    "positive": positive,
                    "neutral": neutral,
                    "negative": negative
                },
                "dominant_sentiment": dominant_sentiment
            }

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "sentiment_score": 0.0,
                "sentiment_distribution": {
                    "positive": 0.0,
                    "neutral": 0.0,
                    "negative": 0.0
                },
                "dominant_sentiment": "neutral"
            }

    def _calculate_sentiment_score(self, video: TrendVideo) -> float:
        """
        感情分析スコアを計算する

        Args:
            video: 分析対象の動画

        Returns:
            float: 感情分析スコア（0-10）
        """
        try:
            sentiment_analysis = self._analyze_sentiment(video)
            sentiment_score = sentiment_analysis["sentiment_score"]
            
            # 感情スコアを0-10の範囲に変換
            normalized_score = (sentiment_score + 1) * 5  # -1から1の範囲を0から10に変換
            
            return min(max(normalized_score, 0), 10)
            
        except Exception as e:
            self.logger.error(f"Error calculating sentiment score: {str(e)}")
            return 0.0

    def _determine_trend_direction(
        self,
        view_growth: float,
        engagement_growth: float,
        comment_growth: float
    ) -> str:
        """
        トレンドの方向を判定する

        Args:
            view_growth: 視聴回数の成長率
            engagement_growth: エンゲージメントの成長率
            comment_growth: コメント数の成長率

        Returns:
            str: トレンドの方向（"increasing", "stable", "decreasing"）
        """
        # 成長率の重み付け
        weighted_growth = (
            view_growth * 0.5 +
            engagement_growth * 0.3 +
            comment_growth * 0.2
        )

        if weighted_growth > 100:
            return "increasing"
        elif weighted_growth < -100:
            return "decreasing"
        else:
            return "stable"

    def _determine_dominant_sentiment(
        self,
        positive: float,
        neutral: float,
        negative: float
    ) -> str:
        """
        主要な感情を判定する

        Args:
            positive: ポジティブな感情の割合
            neutral: ニュートラルな感情の割合
            negative: ネガティブな感情の割合

        Returns:
            str: 主要な感情（"positive", "neutral", "negative"）
        """
        if positive > neutral and positive > negative:
            return "positive"
        elif negative > neutral and negative > positive:
            return "negative"
        else:
            return "neutral"

    def _analyze_foreign_reaction(self, video: TrendVideo) -> ForeignReaction:
        """
        外国人視点からの反応を分析する

        Args:
            video: 分析対象の動画

        Returns:
            ForeignReaction: 外国人視点からの反応
        """
        try:
            if not hasattr(video, 'comments') or not video.comments:
                return ForeignReaction(
                    sentiment_score=0.0,
                    reaction_type="unknown",
                    comment_examples=[]
                )

            # 外国人コメントの抽出（英語コメントを想定）
            foreign_comments = [
                comment for comment in video.comments
                if self._is_foreign_comment(comment.text)
            ]

            if not foreign_comments:
                return ForeignReaction(
                    sentiment_score=0.0,
                    reaction_type="unknown",
                    comment_examples=[]
                )

            # 感情分析の実行
            sentiments = []
            for comment in foreign_comments:
                blob = TextBlob(comment.text)
                sentiments.append(blob.sentiment.polarity)

            # 感情スコアの計算
            sentiment_score = np.mean(sentiments) if sentiments else 0.0

            # 反応タイプの判定
            reaction_type = self._determine_reaction_type(foreign_comments, sentiment_score)

            # 代表的なコメント例の抽出
            comment_examples = self._extract_representative_comments(foreign_comments)

            return ForeignReaction(
                sentiment_score=sentiment_score,
                reaction_type=reaction_type,
                comment_examples=comment_examples
            )

        except Exception as e:
            self.logger.error(f"Error analyzing foreign reaction: {str(e)}")
            return ForeignReaction(
                sentiment_score=0.0,
                reaction_type="unknown",
                comment_examples=[]
            )

    def _is_foreign_comment(self, text: str) -> bool:
        """
        コメントが外国人によるものかどうかを判定する

        Args:
            text: コメントテキスト

        Returns:
            bool: 外国人コメントの場合True
        """
        # 英語の文字が含まれているかチェック
        english_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        text_chars = set(text)
        return bool(english_chars.intersection(text_chars))

    def _determine_reaction_type(self, comments: List[Dict], sentiment_score: float) -> str:
        """
        反応タイプを判定する

        Args:
            comments: コメントリスト
            sentiment_score: 感情スコア

        Returns:
            str: 反応タイプ
        """
        # 感情スコアに基づく基本的な判定
        if sentiment_score > 0.3:
            return "positive"
        elif sentiment_score < -0.3:
            return "negative"
        else:
            return "neutral"

    def _extract_representative_comments(self, comments: List[Dict], max_examples: int = 3) -> List[str]:
        """
        代表的なコメント例を抽出する

        Args:
            comments: コメントリスト
            max_examples: 抽出するコメントの最大数

        Returns:
            List[str]: 代表的なコメント例
        """
        if not comments:
            return []

        # いいね数でソート
        sorted_comments = sorted(comments, key=lambda x: x.get('like_count', 0), reverse=True)
        
        # 上位のコメントを抽出
        return [comment['text'] for comment in sorted_comments[:max_examples]] 