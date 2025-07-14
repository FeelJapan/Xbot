# セットアップ手順

## 前提条件
- Node.js 18.0.0以上
- Python 3.11以上
- Git
- 各APIのアクセスキー
  - X API
  - YouTube Data API
  - OpenAI API
  - Google Gemini API

## インストール手順
1. リポジトリのクローン
   ```bash
   git clone https://github.com/yourusername/xbot.git
   cd xbot
   ```

2. シークレット情報の設定
   - `secrets.memo.md`ファイルを作成
   - 必要なAPIキーと設定情報を記入
   - ファイルはGitにコミットされないように設定済み

3. 依存関係のインストール
   ```bash
   # フロントエンド
   cd frontend
   npm install

   # バックエンド
   cd ../backend
   python -m venv venv312
   # Windows: 
   .\venv312\Scripts\activate
   # Linux/Mac:
   # source venv312/bin/activate
   pip install -r requirements.txt
   ```

4. データベースのセットアップ
   ```bash
   # SQLiteを使用するため、特別な設定は不要
   # マイグレーションの実行（必要な場合）
   cd backend
   .\venv312\Scripts\activate  # Windows
   alembic upgrade head
   ```

## 起動手順
1. バックエンドサービスの起動
   ```bash
   # バックエンドの起動
   cd backend
   .\venv312\Scripts\activate  # Windows
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. フロントエンドの起動
   ```bash
   cd frontend
   npm run dev
   ```

3. Storybookの起動（開発時）
   ```bash
   cd frontend
   npm run storybook
   ```

## トラブルシューティング
### よくある問題と解決方法
1. API接続エラー
   - 環境変数が正しく設定されているか確認
   - APIキーの有効期限を確認
   - ネットワーク接続を確認

2. データベース接続エラー
   - SQLiteファイルの権限を確認
   - データベースファイルが存在するか確認
   - マイグレーションが実行されているか確認

3. フロントエンドのビルドエラー
   - Node.jsのバージョンを確認
   - 依存関係を再インストール
   - キャッシュをクリア

4. バックエンドの起動エラー
   - Pythonのバージョンを確認
   - 仮想環境が有効化されているか確認
   - 依存関係を再インストール

### ログの確認方法
- フロントエンド: `frontend/logs/`
- バックエンド: `backend/logs/` 