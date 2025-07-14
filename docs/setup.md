# セットアップ手順

## 前提条件
- Node.js 18.0.0以上
- Python 3.11以上
- Docker Desktop
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

   # バックエンド（各サービス）
   cd ../services
   for service in */; do
     cd $service
     python -m venv venv
     source venv/bin/activate  # Windows: .\venv\Scripts\activate
     pip install -r requirements.txt
     cd ..
   done
   ```

4. データベースのセットアップ
   ```bash
   # PostgreSQLの起動
   docker-compose up -d db

   # マイグレーションの実行
   cd services
   for service in */; do
     cd $service
     source venv/bin/activate  # Windows: .\venv\Scripts\activate
     alembic upgrade head
     cd ..
   done
   ```

## 起動手順
1. バックエンドサービスの起動
   ```bash
   # 各サービスを起動
   cd services
   for service in */; do
     cd $service
     source venv/bin/activate  # Windows: .\venv\Scripts\activate
     uvicorn main:app --reload --port 8001
     cd ..
   done
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
   - PostgreSQLが起動しているか確認
   - 接続情報が正しいか確認
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
- バックエンド: `services/*/logs/`
- Docker: `docker logs <container_name>` 