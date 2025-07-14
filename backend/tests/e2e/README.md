# E2Eテスト

このディレクトリには、システムのエンドツーエンドテストが含まれています。

## テストの種類

1. ユーザーフローテスト
   - 主要なユーザーフローのテスト
   - ユーザー操作のシミュレーション
   - UI/UXの検証

2. 機能テスト
   - 主要機能の動作テスト
   - エラーケースの検証
   - エッジケースの検証

3. 非機能テスト
   - パフォーマンステスト
   - セキュリティテスト
   - アクセシビリティテスト

## テストの実行方法

```bash
# すべてのE2Eテストを実行
python -m pytest tests/e2e/

# 特定のテストを実行
python -m pytest tests/e2e/test_user_flows.py
python -m pytest tests/e2e/test_functionality.py
python -m pytest tests/e2e/test_non_functional.py
```

## テスト環境の要件

1. ブラウザ
   - Chrome 最新版
   - Firefox 最新版
   - Safari 最新版

2. テストツール
   - Selenium WebDriver
   - Playwright
   - Cypress

3. テストデータ
   - テストユーザーアカウント
   - テストコンテンツ
   - テスト設定

## 注意事項

1. E2Eテストは時間がかかる可能性があります
2. テスト実行前に必要なサービスが起動していることを確認してください
3. テストデータは定期的に更新する必要があります
4. テスト実行中は他の操作を避けてください 