from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    アプリケーションの設定を管理するクラス
    
    Attributes:
        X_API_KEY (str): X APIのキー
        X_API_SECRET (str): X APIのシークレット
        X_ACCESS_TOKEN (str): Xアクセストークン
        X_ACCESS_TOKEN_SECRET (str): Xアクセストークンシークレット
        OPENAI_API_KEY (str): OpenAI APIキー
        DATABASE_URL (str): データベース接続URL
        HOST (str): サーバーホスト
        PORT (int): サーバーポート
        DEBUG (bool): デバッグモードフラグ
    """
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
        """
        設定クラスの設定
        
        Attributes:
            env_file (str): 環境変数ファイルのパス
        """
        env_file = ".env"

settings = Settings() 