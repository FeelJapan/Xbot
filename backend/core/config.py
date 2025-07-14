from typing import Dict, List, Optional
import os
from pydantic import BaseSettings
import json
import logging

logger = logging.getLogger(__name__)

class ServiceConfig(BaseSettings):
    """サービス設定の基本クラス"""
    service_name: str
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # JWT設定
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_token_expire_minutes: int = 30
    
    # サービス間通信設定
    service_dependencies: List[Dict[str, str]] = []
    
    # ヘルスチェック設定
    health_check_interval: int = 30  # 秒
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def load_from_file(cls, file_path: str) -> "ServiceConfig":
        """設定ファイルから設定を読み込む"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return cls(**config_data)
        except Exception as e:
            logger.error(f"Failed to load config from {file_path}: {str(e)}")
            raise

    def save_to_file(self, file_path: str) -> None:
        """設定をファイルに保存"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save config to {file_path}: {str(e)}")
            raise

    def get_service_url(self, service_name: str) -> Optional[str]:
        """依存サービスのURLを取得"""
        for dep in self.service_dependencies:
            if dep["name"] == service_name:
                return dep["url"]
        return None 