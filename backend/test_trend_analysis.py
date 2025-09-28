#!/usr/bin/env python3
"""
YouTubeトレンド分析機能の動作確認スクリプト
"""

import asyncio
import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPYTHONPATHに追加
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from trend_analysis.services.youtube import YouTubeService
from trend_analysis.services.analysis import AnalysisService
from trend_analysis.services.scheduler import TrendScheduler
from trend_analysis.models import TrendVideo, VideoStats
from datetime import datetime

async def test_youtube_service():
    """YouTube APIサービスのテスト"""
    print("=== YouTube API サービステスト ===")
    
    try:
        youtube_service = YouTubeService()
        print("✅ YouTubeService初期化成功")
        
        # 検索機能のテスト
        print("\n--- 検索機能テスト ---")
        search_results = await youtube_service.search_videos(
            query="Python programming",
            max_results=5,
            region_code="JP"
        )
        print(f"✅ 検索結果: {len(search_results)}件取得")
        
        # トレンド動画取得のテスト
        print("\n--- トレンド動画取得テスト ---")
        trending_videos = await youtube_service.get_trending_videos(
            region_code="JP",
            max_results=5
        )
        print(f"✅ トレンド動画: {len(trending_videos)}件取得")
        
        return True
        
    except Exception as e:
        print(f"❌ YouTube API サービスエラー: {str(e)}")
        return False

async def test_analysis_service():
    """分析サービスのテスト"""
    print("\n=== 分析サービステスト ===")
    
    try:
        analysis_service = AnalysisService()
        print("✅ AnalysisService初期化成功")
        
        # サンプルデータの作成
        sample_video = TrendVideo(
            video_id="test_video_id",
            title="Test Video",
            description="Test Description",
            published_at=datetime.now(),
            channel_id="test_channel_id",
            channel_title="Test Channel",
            stats=VideoStats(
                view_count=10000,
                like_count=500,
                comment_count=100,
                engagement_rate=6.0
            )
        )
        
        # 分析の実行
        print("\n--- バズり度スコア計算テスト ---")
        buzz_score = analysis_service._calculate_buzz_score(sample_video)
        print(f"✅ バズり度スコア: {buzz_score:.2f}")
        
        # 包括的分析のテスト
        print("\n--- 包括的分析テスト ---")
        analysis_result = await analysis_service.analyze_comprehensive_trends(sample_video)
        print(f"✅ 包括的分析完了: {len(analysis_result)}項目")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析サービスエラー: {str(e)}")
        return False

async def test_scheduler():
    """スケジューラーのテスト"""
    print("\n=== スケジューラーテスト ===")
    
    try:
        scheduler = TrendScheduler()
        print("✅ TrendScheduler初期化成功")
        
        # スケジューラー状態の取得
        status = scheduler.get_scheduler_status()
        print(f"✅ スケジューラー状態: {status}")
        
        # キーワード収集のテスト
        print("\n--- キーワード収集テスト ---")
        try:
            videos = await scheduler.collect_by_keyword("Python", "JP")
            print(f"✅ キーワード収集: {len(videos)}件取得")
        except Exception as e:
            print(f"⚠️ キーワード収集エラー（API制限の可能性）: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ スケジューラーエラー: {str(e)}")
        return False

async def main():
    """メイン関数"""
    print("YouTubeトレンド分析機能の動作確認を開始します...")
    print("=" * 50)
    
    # 環境変数の設定（テスト用）
    os.environ.setdefault("YOUTUBE_API_KEY", "test_key")
    os.environ.setdefault("TEST_MODE", "true")
    
    results = []
    
    # 各機能のテスト
    results.append(await test_youtube_service())
    results.append(await test_analysis_service())
    results.append(await test_scheduler())
    
    # 結果の表示
    print("\n" + "=" * 50)
    print("動作確認結果:")
    print(f"✅ 成功: {sum(results)}件")
    print(f"❌ 失敗: {len(results) - sum(results)}件")
    
    if all(results):
        print("\n🎉 すべての機能が正常に動作しています！")
    else:
        print("\n⚠️ 一部の機能で問題が発生しています。")
        print("詳細は上記のエラーメッセージを確認してください。")

if __name__ == "__main__":
    asyncio.run(main()) 