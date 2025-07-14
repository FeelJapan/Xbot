# ビルドステージ
FROM python:3.11-slim as build

WORKDIR /app

# 依存関係のインストール
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . .

# 本番環境ステージ
FROM python:3.11-slim

WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ビルドステージからの依存関係とソースコードのコピー
COPY --from=build /app /app

# 環境変数の設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 