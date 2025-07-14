from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import router as trend_router
from .services.youtube import YouTubeService
from .services.analysis import AnalysisService
from .api.youtube import router as youtube_router

app = FastAPI(
    title="Xbot Trend Analysis Service",
    description="YouTubeトレンド分析サービス",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発環境用。本番環境では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# サービスの初期化
youtube_service = YouTubeService()
analysis_service = AnalysisService()

# ルーターの登録
app.include_router(trend_router, prefix="/api/v1/trends", tags=["trends"])
app.include_router(youtube_router, prefix="/api/youtube", tags=["youtube"])

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Trend Analysis Service is running"}
