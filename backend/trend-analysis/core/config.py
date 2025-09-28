import os
from typing import Optional
from pydantic import BaseSettings
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

class Settings(BaseSettings):
    """トレンド分析サービスの設定"""
    
    # YouTube API設定
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # データベース設定
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./trend_analysis.db")
    
    # ログ設定
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/trend_analysis.log")
    
    # スケジューラー設定
    default_collection_interval: int = int(os.getenv("DEFAULT_COLLECTION_INTERVAL", "60"))
    max_collection_results: int = int(os.getenv("MAX_COLLECTION_RESULTS", "50"))
    
    # 分析設定
    default_region_code: str = os.getenv("DEFAULT_REGION_CODE", "JP")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "ja")
    
    # API設定
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # キャッシュ設定
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # 1時間
    
    # データ保持設定
    data_retention_days: int = int(os.getenv("DATA_RETENTION_DAYS", "30"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# グローバル設定インスタンス
_settings = None

def get_settings() -> Settings:
    """設定インスタンスを取得する"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def update_settings(**kwargs) -> Settings:
    """設定を更新する"""
    global _settings
    if _settings is None:
        _settings = Settings()
    
    for key, value in kwargs.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
    
    return _settings 