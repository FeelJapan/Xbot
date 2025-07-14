# テスト実行ガイド

## 環境設定

### 1. テスト用データベースの準備

```bash
# PostgreSQLのインストール（必要な場合）
# Windowsの場合
choco install postgresql

# テスト用データベースの作成
createdb xbot_test

# テスト用ユーザーの作成
createuser -P test_user
# パスワードを入力（test_password）

# 権限の付与
psql -d xbot_test -c "GRANT ALL PRIVILEGES ON DATABASE xbot_test TO test_user;"
```

### 2. 環境変数の設定

```bash
# Windowsの場合
set TEST_DB_HOST=localhost
set TEST_DB_PORT=5432
set TEST_DB_NAME=xbot_test
set TEST_DB_USER=test_user
set TEST_DB_PASSWORD=test_password

# Linux/Macの場合
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5432
export TEST_DB_NAME=xbot_test
export TEST_DB_USER=test_user
export TEST_DB_PASSWORD=test_password
```

## テストの実行

### 1. 依存パッケージのインストール

```bash
pip install -r requirements-test.txt
```

### 2. テストの実行

```bash
# すべてのテストを実行
pytest

# 特定のテストファイルを実行
pytest tests/core/cache/test_cache.py
pytest tests/core/database/test_database.py

# カバレッジレポートを生成
pytest --cov=backend tests/

# 詳細な出力で実行
pytest -v

# 特定のテストケースを実行
pytest tests/core/cache/test_cache.py::test_cache_initialization
```

## テストカバレッジ要件

- 共通基盤機能: 80%以上
- サービス層: 70%以上
- API層: 60%以上
- 全体: 70%以上

## テストの構成

### 1. キャッシュ機能のテスト
- メモリキャッシュのテスト
- ファイルキャッシュのテスト
- キャッシュの有効期限管理
- キャッシュのクリア機能
- エラー処理

### 2. データベースアクセスのテスト
- コネクションプール管理
- トランザクション管理
- クエリ実行
- エラーハンドリング
- 接続のクリーンアップ

## 注意事項

1. テスト実行前にデータベースが起動していることを確認してください。
2. テスト用のデータベースは本番環境とは別のものを使用してください。
3. テスト実行中にエラーが発生した場合は、ログを確認してください。
4. テストデータは自動的にクリーンアップされます。

## トラブルシューティング

### データベース接続エラー
1. PostgreSQLが起動していることを確認
2. 環境変数が正しく設定されていることを確認
3. データベースユーザーの権限を確認

### テストの失敗
1. テストログを確認
2. データベースの状態を確認
3. 環境変数の設定を確認

### カバレッジが低い場合
1. テストケースの追加を検討
2. エッジケースのテストを追加
3. エラーケースのテストを追加 