# Xbot プロジェクト

## プロジェクト概要
このプロジェクトは、AIを活用したチャットボットシステムを構築するためのものです。

## システム構成
- フロントエンド: Vite + React + TypeScript + Tailwind CSS
- バックエンド: FastAPIベースのAPIサーバー

## 開発環境
- OS: Windows 10 (WSL2)
- フロントエンド: Vite, React, TypeScript, Tailwind CSS
- バックエンド: Python, FastAPI

## セットアップ手順
1. フロントエンドのセットアップ
   ```bash
   cd frontend
   npm install
   ```

2. バックエンドのセットアップ
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windowsの場合: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 環境変数の設定
   - フロントエンド: `.env`ファイルの作成
   - バックエンド: `.env`ファイルの作成

## 起動方法
1. バックエンドサーバーの起動
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. フロントエンドの起動
   ```bash
   cd frontend
   npm run dev
   ```

3. Storybookの起動
   ```bash
   cd frontend
   npm run storybook
   ```

## 開発ルール
1. コミットメッセージは日本語で記述
2. 機能追加時は必ずテストを実装
3. 環境変数は`.env`ファイルで管理
4. セキュリティを考慮した実装を心がける

## 注意事項
- バックエンドサーバーを先に起動してから、フロントエンドを起動すること
- 環境変数の設定漏れに注意
- APIキーなどの機密情報は適切に管理すること

## 更新履歴
- 2024-05-24: プロジェクト初期化

## 環境構成の記録
### 2024-05-24時点の環境
- フロントエンド
  - Vite
  - React 18
  - TypeScript
  - Tailwind CSS
  - Storybook 8.6.14
    - アドオン:
      - @storybook/addon-essentials
      - @storybook/addon-onboarding
      - @chromatic-com/storybook
      - @storybook/experimental-addon-test
    - ポート: 6006
  - Vitest
  - Playwright
  - ポート: 5173（Viteのデフォルト）
  - プロジェクト構造:
    - src/api/ - API関連のコード
    - src/components/ - 再利用可能なコンポーネント
    - src/pages/ - ページコンポーネント
    - src/stories/ - Storybookのストーリー

- バックエンド
  - Python 3.11
  - FastAPI
  - Uvicorn
  - ポート: 8000（デフォルト）

- 開発環境
  - Windows 10 (WSL2)
  - Git
  - VS Code

- データベース
  - PostgreSQL
  - ポート: 5432（デフォルト）

- その他
  - Docker Desktop
  - WSL2
  - Ubuntu 20.04 LTS 