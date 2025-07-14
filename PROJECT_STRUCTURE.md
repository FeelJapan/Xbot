# プロジェクト構造

このドキュメントでは、プロジェクトのフォルダ構成と各ディレクトリの目的について説明します。

## ルートディレクトリ

- `frontend/`: フロントエンドアプリケーション（React + TypeScript）
- `backend/`: バックエンドアプリケーション（Python + FastAPI）
- `docker/`: Docker関連の設定ファイル
- `.git/`: Gitリポジトリの管理ファイル
- `README.md`: プロジェクトの概要と基本的な説明
- `package.json`: プロジェクト全体の依存関係管理
- `docker-compose.yml`: コンテナの構成定義
- `.gitignore`: Gitの除外設定
- `secrets.memo.md`: 機密情報のメモ（Git管理対象外）

## フロントエンド（`frontend/`）

- `src/`: ソースコード
- `node_modules/`: 依存パッケージ
- `.storybook/`: Storybookの設定とコンポーネント
- `package.json`: フロントエンドの依存関係管理
- `package-lock.json`: 依存関係の詳細なバージョン管理
- `vite.config.ts`: Viteの設定
- `tailwind.config.js`: Tailwind CSSの設定
- `postcss.config.js`: PostCSSの設定
- `Dockerfile`: フロントエンドのDockerイメージ構築設定
- `vitest.config.ts`: Vitestの設定
- `vitest.workspace.ts`: Vitestワークスペース設定

## バックエンド（`backend/`）

- `app/`: メインアプリケーションコード
- `core/`: コア機能の実装
- `trend-analysis/`: トレンド分析機能
- `settings-management/`: 設定管理機能
- `post-management/`: 投稿管理機能
- `content-generation/`: コンテンツ生成機能
- `tests/`: テストコード
- `logs/`: ログファイル
- `requirements.txt`: 本番環境の依存パッケージ
- `requirements-dev.txt`: 開発環境の依存パッケージ
- `Dockerfile`: バックエンドのDockerイメージ構築設定
- `pytest.ini`: pytestの設定

## Docker関連（`docker/`）

- `frontend/`: フロントエンドのDocker関連設定
- `backend/`: バックエンドのDocker関連設定

## 開発ガイドライン

1. 新しい機能を追加する際は、適切なディレクトリに配置してください
2. 設定ファイルは、各ディレクトリのルートに配置してください
3. テストコードは、対応する機能と同じディレクトリ構造で配置してください
4. 環境変数や機密情報は、適切に管理し、Gitにコミットしないでください
5. Docker関連の設定は、`docker/`ディレクトリに集約してください

## 注意事項

- 機密情報は`secrets.memo.md`に記載し、Git管理対象外としています
- ログファイルは`backend/logs/`に保存されます
- テストコードは各機能ディレクトリ内の`tests/`に配置してください
- 環境変数は`.env`ファイルで管理し、Git管理対象外としています 