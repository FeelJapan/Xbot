from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router

app = FastAPI(title="X Auto Post Bot")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発環境では全てのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを追加
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "X Auto Post Bot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 