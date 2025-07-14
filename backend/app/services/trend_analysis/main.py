from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from backend.app.services.trend_analysis.youtube_client import YouTubeClient

# 環境変数の読み込み
load_dotenv()

app = FastAPI(title="Trend Analysis Service")

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発環境では全てのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# YouTubeクライアントの初期化
youtube_client = YouTubeClient()

@app.get("/")
async def root():
    return {"message": "Trend Analysis Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# YouTube API関連のエンドポイント
@app.get("/api/v1/trends/youtube")
async def get_youtube_trends(
    region_code: str = "JP",
    max_results: int = 10,
    category_id: Optional[str] = None
):
    try:
        videos = await youtube_client.get_trending_videos(
            region_code=region_code,
            max_results=max_results,
            category_id=category_id
        )
        return {
            "status": "success",
            "data": videos,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# トレンド分析のエンドポイント
@app.get("/api/v1/trends/analyze")
async def analyze_trends(
    video_id: str,
    days: int = 7
):
    try:
        analysis = await youtube_client.analyze_video_trends(
            video_id=video_id,
            days=days
        )
        return {
            "status": "success",
            "data": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 