# ビルドステージ
FROM node:18-alpine as build

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm install

# ソースコードのコピー
COPY . .

# 開発サーバーの起動
CMD ["npm", "run", "dev"]

# ホットリロードのためのポート公開
EXPOSE 5173 