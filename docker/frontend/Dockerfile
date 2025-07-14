# ビルドステージ
FROM node:18-alpine as build

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm install

# ソースコードのコピーとビルド
COPY . .
RUN npm run build

# 本番環境ステージ
FROM nginx:alpine

# Nginx設定のコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ビルド成果物のコピー
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 