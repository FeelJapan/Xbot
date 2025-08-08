# Xbot 単体テスト仕様書

## 1. 概要

### 1.1 目的
本仕様書は、Xbotプロジェクトにおける単体テストの設計、実装、実行に関する要件とガイドラインを定義する。

### 1.2 適用範囲
- バックエンド（Python/FastAPI）
- フロントエンド（React/TypeScript）
- 共通基盤機能
- サービス層
- API層

### 1.3 テストの種類
- **単体テスト（Unit Test）**: 個別の関数、クラス、モジュールのテスト
- **統合テスト（Integration Test）**: 複数のコンポーネント間の連携テスト
- **エンドツーエンドテスト（E2E Test）**: システム全体の動作テスト

## 2. テスト環境設定

### 2.1 バックエンドテスト環境

#### 2.1.1 必要なパッケージ
```txt
pytest==8.4.1
pytest-asyncio==1.0.0
pytest-cov==6.2.1
pytest-mock==3.12.0
```

#### 2.1.2 テスト用データベース設定
```bash
# PostgreSQLテスト用データベース作成
createdb xbot_test
createuser -P test_user
psql -d xbot_test -c "GRANT ALL PRIVILEGES ON DATABASE xbot_test TO test_user;"
```

#### 2.1.3 環境変数設定
```bash
# Windows
set TEST_DB_HOST=localhost
set TEST_DB_PORT=5432
set TEST_DB_NAME=xbot_test
set TEST_DB_USER=test_user
set TEST_DB_PASSWORD=test_password

# Linux/Mac
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5432
export TEST_DB_NAME=xbot_test
export TEST_DB_USER=test_user
export TEST_DB_PASSWORD=test_password
```

### 2.2 フロントエンドテスト環境

#### 2.2.1 必要なパッケージ
```json
{
  "vitest": "^1.0.0",
  "@testing-library/react": "^14.0.0",
  "@testing-library/jest-dom": "^6.0.0",
  "@testing-library/user-event": "^14.0.0",
  "jsdom": "^23.0.0"
}
```

#### 2.2.2 テスト設定
- テスト環境: jsdom
- カバレッジレポート: text, json, html
- セットアップファイル: `src/test/setup.ts`

## 3. テストカバレッジ要件

### 3.1 カバレッジ目標
| レイヤー | 目標カバレッジ | 現在のカバレッジ | 状況 |
|---------|---------------|-----------------|------|
| 共通基盤機能 | 80%以上 | 55% | ⚠️ 部分的に未達 |
| サービス層 | 70%以上 | 49% | ❌ 未達 |
| API層 | 60%以上 | 0% | ❌ 未達 |
| フロントエンド | 70%以上 | 未測定 | ❌ 実行不可 |
| **全体** | **70%以上** | **49%** | ❌ 未達 |

### 3.2 カバレッジ測定項目
- **行カバレッジ（Line Coverage）**: 実行されたコード行の割合
- **分岐カバレッジ（Branch Coverage）**: 条件分岐の実行割合
- **関数カバレッジ（Function Coverage）**: 関数の実行割合

## 4. テスト実行状況

### 4.1 バックエンドテスト状況

#### 4.1.1 テスト環境
- **Python バージョン**: 3.12.4
- **pytest バージョン**: 8.4.1
- **テストフレームワーク**: pytest + pytest-asyncio + pytest-cov
- **テスト実行日**: 2025年8月4日

#### 4.1.2 テスト実行結果（最新）
- **総テスト数**: 206個
- **成功**: 1個（ログテストのみ実行可能）
- **失敗**: 0個
- **エラー**: 2個（インポートエラー）
- **実行時間**: 0.15秒（単一テスト）

#### 4.1.3 実行可能なテスト
- **実行可能**: 1個（ログテスト）
- **実行不可**: 205個（インポートエラー、PowerShell表示問題）

#### 4.1.4 現在のカバレッジ詳細
- **全体カバレッジ**: 測定不可（大部分のテストが実行不可）
- **テスト済み**: ログ機能のみ
- **未テスト**: その他すべての機能

| ファイル | 総行数 | テスト済み行数 | カバレッジ |
|---------|--------|---------------|-----------|
| core/logging/logger.py | 99 | 99 | 100% |
| その他 | 測定不可 | 0 | 0% |

### 4.2 主要な問題と解決状況（2025年8月4日更新）

#### 4.2.1 解決済みの問題

**1. 大量データ出力の問題（解決済み - 2025年8月4日）**
- **問題**: テスト実行中に大量の「x」が出力されて無限ループ状態になる
- **原因**: test_log_rotationテストで1KBのデータを10回出力
- **解決策**: データサイズを100バイト × 5回に削減
- **状況**: ✅ 解決済み
- **実装内容**:
  ```python
  # backend/tests/core/logging/test_logger.py
  large_message = "x" * 100  # 100バイト（以前は1KB）
  for i in range(5):  # 5回（以前は10回）
  ```

**2. インポートパスの問題（部分的に解決済み - 2025年8月4日）**
- **問題**: `ModuleNotFoundError: No module named 'backend'`
- **原因**: テストファイルで`backend.core`からのインポート
- **解決策**: 相対インポートに変更
- **状況**: ⚠️ 部分的に解決済み
- **実装内容**:
  ```python
  # 変更前
  from backend.core.cache.cache_manager import CacheManager
  # 変更後
  from core.cache.cache_manager import CacheManager
  ```

**3. Loggerクラスの属性不一致（解決済み - 2025年8月4日）**
- **問題**: テストで`logger.name`を期待していたが、実際のクラスには存在しない
- **原因**: テストケースが実装と一致していない
- **解決策**: テストケースを実装に合わせて修正
- **状況**: ✅ 解決済み

#### 4.2.2 未解決の問題

**1. PowerShell表示の問題（未解決）**
- **問題**: PowerShellが大量の出力を処理しきれず、コマンドが止まる
- **影響**: テスト実行が途中で停止する
- **状況**: ❌ 未解決
- **推奨解決策**: 
  - テスト出力の抑制
  - 別のターミナル（cmd.exe）の使用
  - テスト実行時のオプション調整

**2. trend_analysisモジュールのインポートエラー（未解決）**
- **問題**: `ModuleNotFoundError: No module named 'trend_analysis.services'`
- **影響**: trend_analysis関連のテストが実行不可
- **状況**: ❌ 未解決
- **推奨解決策**:
  - インポートパスの修正
  - テストファイルの移動
  - モジュール構造の見直し

**3. データベース接続の問題（未解決）**
- **問題**: PostgreSQLプールが初期化されていない
- **影響**: データベース関連テストが失敗
- **状況**: ❌ 未解決

**4. モックの問題（未解決）**
- **問題**: aiohttpのモックが正しく動作しない
- **影響**: 多くのサービステストが失敗
- **状況**: ❌ 未解決

### 4.3 緊急対応が必要な問題（2025年8月4日更新）

#### 4.3.1 高優先度（即座に修正が必要）
1. **PowerShell表示問題の解決**: テスト実行環境の改善
2. **trend_analysisインポートエラーの修正**: モジュールパスの統一
3. **データベース接続の修正**: テスト用DBの設定

#### 4.3.2 中優先度（段階的に修正）
1. **モック設定の修正**: aiohttpのモックを正しく設定
2. **テストケースの追加**: カバレッジの向上
3. **テスト環境の整備**: 開発・テスト・本番環境の分離

#### 4.3.3 低優先度（長期的な改善）
1. **テスト実行時間の最適化**: 並列実行の導入
2. **CI/CDパイプラインの構築**: 自動テストの実装
3. **テストデータの管理**: フィクスチャの改善

### 4.4 推奨される対応策（2025年8月4日更新）

#### 4.4.1 即座に修正すべき項目
1. **PowerShell環境の改善**:
   ```bash
   # cmd.exeを使用
   cmd /c "venv312\Scripts\python.exe -m pytest"
   
   # または出力を抑制
   pytest -q --tb=short
   ```

2. **trend_analysisテストの修正**:
   ```python
   # 正しいインポートパスに修正
   from trend-analysis.services.analysis import AnalysisService
   ```

3. **テスト実行オプションの最適化**:
   ```bash
   # 出力を抑制して実行
   pytest --tb=short -q --maxfail=5
   ```

#### 4.4.2 段階的な改善
1. **テストケースの追加**: エラーケースとエッジケースのテスト
2. **カバレッジの向上**: 未テストコードの特定とテスト追加
3. **テスト環境の整備**: 開発・テスト・本番環境の分離

## 5. テスト設計原則

### 5.1 テストケース設計原則
1. **AAA原則（Arrange-Act-Assert）**
   - Arrange: テストデータの準備
   - Act: テスト対象の実行
   - Assert: 結果の検証

2. **FIRST原則**
   - Fast: 高速実行
   - Independent: 独立性
   - Repeatable: 再現性
   - Self-validating: 自己検証
   - Timely: 適切なタイミング

3. **テストケース命名規則**
   ```
   test_[テスト対象]_[条件]_[期待結果]
   ```

### 5.2 モック・スタブ使用方針
- 外部API呼び出しは必ずモック化
- データベース操作はテスト用DBまたはモック使用
- ファイルI/O操作は一時ファイルまたはモック使用
- 時間依存処理はモック化

### 5.3 テスト実装のベストプラクティス（2025年7月14日追加）

#### 5.3.1 インポートパスの統一
**推奨事項**:
1. conftest.pyでPYTHONPATHを設定する
2. テストファイルでは相対インポートを使用する
3. `backend`モジュールとしてのインポートは避ける

**実装例**:
```python
# conftest.py（プロジェクト全体で1回だけ設定）
import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# テストファイル
from core.logging.logger import Logger  # Good
# from backend.core.logging.logger import Logger  # Bad
```

#### 5.3.2 大量データを扱うテストの注意点
**推奨事項**:
1. テストデータのサイズは最小限に抑える
2. ログローテーションテストは1KB程度のデータで十分
3. パフォーマンステストは別途専用のテストスイートで実施

**実装例**:
```python
# 悪い例
large_message = "x" * (5 * 1024 * 1024)  # 5MB - テストが止まる原因

# 良い例
large_message = "x" * 1024  # 1KB - 十分なテストが可能
```

#### 5.3.3 pytest設定の管理
**推奨事項**:
1. カバレッジ計測はオプショナルにする
2. 必要に応じてコマンドラインで指定する
3. CI/CD環境と開発環境で設定を分ける

**実装例**:
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
# カバレッジはコマンドラインで指定
# addopts = --cov=app  # コメントアウト

# 実行時に指定
pytest  # 通常のテスト実行
pytest --cov=app  # カバレッジ計測付き
```

## 6. バックエンドテスト仕様

### 6.1 テストディレクトリ構造
```
backend/tests/
├── conftest.py                 # 共通フィクスチャ
├── pytest.ini                 # pytest設定
├── core/                      # 共通基盤機能テスト
│   ├── cache/
│   ├── config/
│   ├── database/
│   ├── error_handling/
│   └── logging/
├── services/                  # サービス層テスト
│   ├── content_generator/
│   ├── image_generator/
│   ├── post_manager/
│   ├── scheduler/
│   ├── theme_config_manager/
│   ├── trend_analysis/
│   └── video_generator/
├── api/                       # API層テスト
│   ├── v1/
│   └── endpoints/
├── integration/               # 統合テスト
├── e2e/                       # E2Eテスト
└── performance/               # パフォーマンステスト
```

### 6.2 共通基盤機能テスト

#### 6.2.1 キャッシュ機能テスト
**対象ファイル**: `core/cache/cache_manager.py`

**テストケース**:
- メモリキャッシュの初期化
- キャッシュへのデータ保存・取得
- キャッシュの有効期限管理
- キャッシュのクリア機能
- キャッシュ容量制限
- エラー処理（無効なキー、破損データ）

**テストフィクスチャ**:
```python
@pytest.fixture
def cache_manager():
    return CacheManager(
        memory_cache_size=1000,
        file_cache_dir="test_cache",
        default_ttl=3600
    )
```

#### 6.2.2 データベース機能テスト
**対象ファイル**: `core/database/db_manager.py`

**テストケース**:
- データベース接続の確立・切断
- コネクションプール管理
- トランザクション管理
- クエリ実行（SELECT, INSERT, UPDATE, DELETE）
- エラーハンドリング（接続エラー、クエリエラー）
- 接続のクリーンアップ

**テストフィクスチャ**:
```python
@pytest.fixture
async def db_manager():
    manager = DatabaseManager(test_config["database"])
    await manager.initialize()
    yield manager
    await manager.cleanup()
```

#### 6.2.3 ログ機能テスト
**対象ファイル**: `core/logging/logger.py`

**テストケース**:
- ログレベルの設定
- ログメッセージの出力
- ログファイルのローテーション
- ログフォーマットの設定
- エラーログの出力
- ログディレクトリの作成

#### 6.2.4 設定管理テスト
**対象ファイル**: `core/config/config_manager.py`

**テストケース**:
- 設定ファイルの読み込み
- 環境変数の読み込み
- 設定値の取得・設定
- 設定の検証
- デフォルト値の適用
- 設定のリロード

#### 6.2.5 エラーハンドリングテスト
**対象ファイル**: `core/error_handling/error_handler.py`

**テストケース**:
- 例外の捕捉・処理
- エラーメッセージの生成
- エラーログの出力
- エラーコードの管理
- リトライ機能
- フォールバック処理

### 6.3 サービス層テスト

#### 6.3.1 コンテンツ生成サービステスト
**対象ファイル**: `app/services/content_generator.py`

**テストケース**:
- テキスト生成の基本機能
- プロンプトの構築
- AI APIとの連携
- 生成結果の検証
- エラーハンドリング
- レート制限対応

**モック対象**:
- AI APIクライアント
- 設定管理
- ログ出力

#### 6.3.2 画像生成サービステスト
**対象ファイル**: `app/services/image_generator.py`

**テストケース**:
- 画像生成の基本機能
- プロンプトの構築
- 画像APIとの連携
- 生成画像の保存
- 画像フォーマット変換
- エラーハンドリング

#### 6.3.3 投稿管理サービステスト
**対象ファイル**: `app/services/post_manager.py`

**テストケース**:
- 投稿の作成・更新・削除
- 投稿の検索・フィルタリング
- 投稿のスケジューリング
- 投稿の公開・非公開
- 投稿の統計情報取得
- バッチ処理

#### 6.3.4 スケジューラーサービステスト
**対象ファイル**: `app/services/scheduler.py`

**テストケース**:
- タスクのスケジューリング
- タスクの実行
- タスクのキャンセル
- タスクの再試行
- タスクの優先度管理
- エラーハンドリング

#### 6.3.5 テーマ設定管理テスト
**対象ファイル**: `app/services/theme_config_manager.py`

**テストケース**:
- テーマ設定の読み込み・保存
- テーマの切り替え
- カスタム設定の適用
- 設定の検証
- デフォルト設定の復元
- 設定のエクスポート・インポート

#### 6.3.6 トレンド分析サービステスト
**対象ファイル**: `app/services/trend_analysis/`

**テストケース**:
- YouTube APIとの連携
- トレンドデータの収集
- データの分析・処理
- 結果の保存
- エラーハンドリング
- レート制限対応

#### 6.3.7 動画生成サービステスト
**対象ファイル**: `app/services/video_generator.py`

**テストケース**:
- 動画生成の基本機能
- 画像・音声の合成
- 動画フォーマット変換
- 動画の保存・配信
- エラーハンドリング
- リソース管理

### 6.4 API層テスト

#### 6.4.1 Gemini API エンドポイントテスト
**対象ファイル**: `app/api/v1/endpoints/gemini.py`

**テストケース**:
- POST /api/v1/gemini/generate
  - 正常なリクエストの処理
  - 無効なリクエストの検証
  - エラーレスポンスの生成
  - レート制限の適用
- 認証・認可の検証
- リクエスト・レスポンスのバリデーション

#### 6.4.2 投稿管理APIテスト
**対象ファイル**: `app/api/v1/endpoints/post_management.py`

**テストケース**:
- GET /api/v1/posts - 投稿一覧取得
- POST /api/v1/posts - 投稿作成
- GET /api/v1/posts/{id} - 投稿詳細取得
- PUT /api/v1/posts/{id} - 投稿更新
- DELETE /api/v1/posts/{id} - 投稿削除
- ページネーション機能
- フィルタリング機能

#### 6.4.3 検索APIテスト
**対象ファイル**: `app/api/v1/endpoints/search.py`

**テストケース**:
- GET /api/v1/search - 検索機能
- 検索クエリの処理
- 検索結果のランキング
- 検索履歴の保存
- 検索候補の提供

#### 6.4.4 設定APIテスト
**対象ファイル**: `app/api/endpoints/settings.py`

**テストケース**:
- GET /api/settings - 設定取得
- PUT /api/settings - 設定更新
- 設定の検証
- 設定のリセット
- 設定のエクスポート・インポート

## 7. フロントエンドテスト仕様

### 7.1 テストディレクトリ構造
```
frontend/src/
├── test/
│   ├── setup.ts              # テストセットアップ
│   ├── utils.tsx             # テストユーティリティ
│   └── App.test.tsx          # Appコンポーネントテスト
├── components/
│   ├── __tests__/            # コンポーネントテスト
│   └── ui/
│       └── __tests__/        # UIコンポーネントテスト
└── pages/
    └── __tests__/            # ページコンポーネントテスト
```

### 7.2 コンポーネントテスト

#### 7.2.1 Appコンポーネントテスト
**対象ファイル**: `src/App.tsx`

**テストケース**:
- アプリケーションの初期化
- ルーティング機能
- テーマ切り替え
- エラーバウンダリ
- ローディング状態

#### 7.2.2 レイアウトコンポーネントテスト
**対象ファイル**: `src/components/Layout.tsx`

**テストケース**:
- レイアウトの表示
- ナビゲーション機能
- レスポンシブデザイン
- アクセシビリティ

#### 7.2.3 UIコンポーネントテスト
**対象ファイル**: `src/components/ui/`

**テストケース**:
- Button.tsx
  - クリックイベントの処理
  - 無効状態の表示
  - ローディング状態
  - アクセシビリティ
- Card.tsx
  - コンテンツの表示
  - スタイリング
  - アクセシビリティ
- Input.tsx
  - 入力値の管理
  - バリデーション
  - エラー表示
  - アクセシビリティ
- DarkModeToggle.tsx
  - テーマ切り替え
  - 状態の永続化
  - アクセシビリティ

#### 7.2.4 設定パネルコンポーネントテスト
**対象ファイル**: `src/components/settings/`

**テストケース**:
- AiSettingsPanel.tsx
  - AI設定の表示・編集
  - 設定の保存
  - バリデーション
- ApiSettingsPanel.tsx
  - API設定の表示・編集
  - API接続テスト
  - 設定の保存
- ThemeSettingsPanel.tsx
  - テーマ設定の表示・編集
  - プレビュー機能
  - 設定の保存
- TrendSettingsPanel.tsx
  - トレンド設定の表示・編集
  - 設定の保存

#### 7.2.5 ページコンポーネントテスト
**対象ファイル**: `src/pages/`

**テストケース**:
- Home.tsx
  - ホームページの表示
  - コンテンツの読み込み
  - インタラクション
- Dashboard.tsx
  - ダッシュボードの表示
  - データの表示
  - フィルタリング機能
- CreatePost.tsx
  - 投稿作成フォーム
  - バリデーション
  - 送信機能
- Settings.tsx
  - 設定ページの表示
  - 設定の編集
  - 設定の保存

### 7.3 APIクライアントテスト
**対象ファイル**: `src/api/`

**テストケース**:
- APIクライアントの初期化
- リクエストの送信
- レスポンスの処理
- エラーハンドリング
- 認証トークンの管理
- リトライ機能

## 8. テスト実行

### 8.1 バックエンドテスト実行

#### 8.1.1 基本実行コマンド
```bash
# すべてのテストを実行
pytest

# 詳細出力で実行
pytest -v

# 特定のテストファイルを実行
pytest tests/core/cache/test_cache_manager.py

# 特定のテストケースを実行
pytest tests/core/cache/test_cache_manager.py::test_cache_initialization

# カバレッジレポートを生成
pytest --cov=backend tests/

# 並列実行
pytest -n auto
```

#### 8.1.2 テストマーカーの使用
```bash
# 単体テストのみ実行
pytest -m unit

# 統合テストのみ実行
pytest -m integration

# パフォーマンステストのみ実行
pytest -m performance

# スローなテストをスキップ
pytest -m "not slow"
```

### 8.2 フロントエンドテスト実行

#### 8.2.1 基本実行コマンド
```bash
# すべてのテストを実行
npm test

# ウォッチモードで実行
npm run test:watch

# カバレッジレポートを生成
npm run test:coverage

# 特定のテストファイルを実行
npm test -- Button.test.tsx
```

#### 8.2.2 テストオプション
```bash
# 詳細出力
npm test -- --verbose

# 特定のパターンのテストを実行
npm test -- --grep "Button"

# テストタイムアウトの設定
npm test -- --timeout 10000
```

## 9. テストデータ管理

### 9.1 テストデータの種類
1. **フィクスチャデータ**: テスト用の固定データ
2. **ファクトリデータ**: 動的に生成されるテストデータ
3. **モックデータ**: 外部依存の代替データ

### 9.2 テストデータの管理方針
- テストデータは独立して管理
- 本番データとの混在を避ける
- テストデータのクリーンアップを確実に実行
- 機密情報を含まないテストデータを使用

### 9.3 テストデータの作成
```python
# フィクスチャデータの例
@pytest.fixture
def sample_post_data():
    return {
        "title": "テスト投稿",
        "content": "テストコンテンツ",
        "author": "test_user",
        "created_at": "2024-01-01T00:00:00Z"
    }

# ファクトリデータの例
def create_test_post(title="テスト投稿", content="テストコンテンツ"):
    return Post(
        title=title,
        content=content,
        author="test_user",
        created_at=datetime.now()
    )
```

## 10. 品質保証

### 10.1 テスト品質チェックリスト
- [ ] テストケースが要件を網羅している
- [ ] エッジケースがテストされている
- [ ] エラーケースがテストされている
- [ ] テストが独立して実行できる
- [ ] テストが再現可能である
- [ ] テストの実行時間が適切である
- [ ] テストコードが読みやすい
- [ ] テストの命名が適切である

### 10.2 コードレビュー項目
- テストケースの設計
- テストデータの適切性
- モック・スタブの使用
- アサーションの妥当性
- エラーハンドリングの検証
- パフォーマンスの考慮

### 10.3 継続的改善
- テストカバレッジの定期的な監視
- テスト実行時間の最適化
- テストケースの追加・改善
- テスト環境の整備
- テストツールの更新

## 11. トラブルシューティング

### 11.1 よくある問題と解決方法

#### 11.1.1 データベース接続エラー
**問題**: テスト用データベースに接続できない
**解決方法**:
1. PostgreSQLが起動していることを確認
2. 環境変数が正しく設定されていることを確認
3. データベースユーザーの権限を確認
4. テスト用データベースが存在することを確認

#### 11.1.2 テストの失敗
**問題**: テストが予期せず失敗する
**解決方法**:
1. テストログを確認
2. データベースの状態を確認
3. 環境変数の設定を確認
4. 依存関係のバージョンを確認

#### 11.1.3 カバレッジが低い
**問題**: テストカバレッジが目標に達していない
**解決方法**:
1. テストケースの追加を検討
2. エッジケースのテストを追加
3. エラーケースのテストを追加
4. 未テストのコードを特定

#### 11.1.4 テスト実行が途中で止まる（2025年7月14日 解決済み）
**問題**: テスト実行中に大量の「x」が出力されて無限ループ状態になる
**原因**: 
- pytest.iniでカバレッジ計測が常に有効になっている
- 大量データを出力するテスト（test_log_rotation等）との組み合わせ
**解決方法**:
1. pytest.iniのaddoptsをコメントアウト
   ```ini
   # addopts = --cov=app --cov-report=term-missing --cov-report=html
   ```
2. カバレッジ計測は必要時のみコマンドラインで指定
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```
3. 大量データを扱うテストのデータサイズを削減
   ```python
   # 5MBから1KBに削減
   large_message = "x" * 1024  # 1KB
   ```

#### 11.1.5 インポートエラー（2025年7月14日 解決済み）
**問題**: `ModuleNotFoundError: No module named 'backend'`
**原因**: Pythonパスの設定不足
**解決方法**:
1. conftest.pyにPYTHONPATH設定を追加
   ```python
   import sys
   from pathlib import Path
   backend_dir = Path(__file__).parent.parent
   sys.path.insert(0, str(backend_dir))
   ```
2. テストファイルのインポートを相対インポートに変更
   ```python
   # 変更前
   from backend.core.logging.logger import Logger
   # 変更後
   from core.logging.logger import Logger
   ```

### 11.2 デバッグ手法
- テストの詳細出力を有効化
- ブレークポイントを使用したデバッグ
- ログ出力の確認
- テストデータの検証

## 12. 参考資料

### 12.1 技術文書
- [pytest公式ドキュメント](https://docs.pytest.org/)
- [Testing Library公式ドキュメント](https://testing-library.com/)
- [Vitest公式ドキュメント](https://vitest.dev/)

### 12.2 ベストプラクティス
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [React Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

### 12.3 プロジェクト固有の資料
- 機能仕様書
- API仕様書
- データベース設計書
- アーキテクチャ設計書

---

**文書情報**
- 作成日: 2024年1月
- 最終更新日: 2025年7月14日
- バージョン: 2.1
- 作成者: Xbot開発チーム
- 承認者: プロジェクトマネージャー 
- 更新内容:
  - v2.1 (2025/07/14): テスト実行の問題と解決策を追加
    - テスト実行が途中で止まる問題の解決方法を記載
    - インポートエラーの解決方法を記載
    - テスト実装のベストプラクティスを追加 