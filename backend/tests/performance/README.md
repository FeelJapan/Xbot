# パフォーマンステスト

このディレクトリには、システムのパフォーマンステストが含まれています。

## テストの種類

1. 負荷テスト
   - 同時接続数のテスト
   - リクエスト処理能力のテスト
   - スループットの測定

2. ストレステスト
   - 限界値のテスト
   - エラー発生時の動作確認
   - リカバリー能力の検証

3. 耐久テスト
   - 長時間運用のテスト
   - メモリリークの検証
   - リソース使用量の監視

## テストの実行方法

```bash
# すべてのパフォーマンステストを実行
python -m pytest tests/performance/

# 特定のテストを実行
python -m pytest tests/performance/test_load.py
python -m pytest tests/performance/test_stress.py
python -m pytest tests/performance/test_endurance.py
```

## テストツール

1. 負荷テストツール
   - Locust
   - JMeter
   - k6

2. モニタリングツール
   - Prometheus
   - Grafana
   - New Relic

3. プロファイリングツール
   - cProfile
   - line_profiler
   - memory_profiler

## パフォーマンス要件

1. レスポンスタイム
   - API応答時間: 200ms以下
   - ページロード時間: 2秒以下
   - データベースクエリ: 100ms以下

2. スループット
   - 同時接続数: 1000以上
   - リクエスト/秒: 100以上
   - データベース接続: 100以上

3. リソース使用量
   - CPU使用率: 70%以下
   - メモリ使用率: 80%以下
   - ディスクI/O: 70%以下

## 注意事項

1. パフォーマンステストは本番環境に影響を与える可能性があります
2. テスト実行前にバックアップを取得してください
3. テスト実行中は他の操作を避けてください
4. テスト結果は定期的に分析し、改善点を特定してください 