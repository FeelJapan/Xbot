from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # X API設定
    X_API_KEY: str
    X_API_SECRET: str
    X_ACCESS_TOKEN: str
    X_ACCESS_TOKEN_SECRET: str
    
    # ChatGPT API設定
    OPENAI_API_KEY: str
    
    # データベース設定
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/xbot"
    
    # サーバー設定
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings() 