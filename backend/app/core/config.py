from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    アプリケーションの設定を管理するクラス
    
    Attributes:
        X_API_KEY (str): X APIのキー
        X_API_SECRET (str): X APIのシークレット
        X_ACCESS_TOKEN (str): Xアクセストークン
        X_ACCESS_TOKEN_SECRET (str): Xアクセストークンシークレット
        OPENAI_API_KEY (str): OpenAI APIキー
        GEMINI_API_KEY (str): Google Gemini APIキー
        GEMINI_MODEL (str): Geminiモデル名
        GEMINI_MAX_TOKENS (int): 最大トークン数
        DATABASE_URL (str): データベース接続URL
        HOST (str): サーバーホスト
        PORT (int): サーバーポート
        DEBUG (bool): デバッグモードフラグ
    """
    # X API設定（開発環境用のデフォルト値）
    X_API_KEY: str = "your_x_api_key"
    X_API_SECRET: str = "your_x_api_secret"
    X_ACCESS_TOKEN: str = "your_x_access_token"
    X_ACCESS_TOKEN_SECRET: str = "your_x_access_token_secret"
    
    # ChatGPT API設定
    OPENAI_API_KEY: str = "your_openai_api_key"
    
    # Gemini API設定
    GEMINI_API_KEY: str = "your_gemini_api_key"
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_MAX_TOKENS: int = 2048
    
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