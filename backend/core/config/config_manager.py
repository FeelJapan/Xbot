"""
Configuration management module for Xbot
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
from ..logging.logger import get_logger
from ..error_handling.error_handler import ConfigError
import shutil
import jsonschema

logger = get_logger("config_manager")

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
        self.load_config()
        
        # 設定スキーマの定義
        self.schema = {
            "type": "object",
            "properties": {
                "api_keys": {
                    "type": "object",
                    "properties": {
                        "x_api_key": {"type": "string"},
                        "youtube_api_key": {"type": "string"},
                        "openai_api_key": {"type": "string"},
                        "gemini_api_key": {"type": "string"}
                    },
                    "required": ["x_api_key", "youtube_api_key", "openai_api_key", "gemini_api_key"]
                },
                "settings": {
                    "type": "object",
                    "properties": {
                        "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                        "max_retries": {"type": "integer", "minimum": 1},
                        "retry_delay": {"type": "number", "minimum": 0.1}
                    },
                    "required": ["log_level", "max_retries", "retry_delay"]
                }
            },
            "required": ["api_keys", "settings"]
        }
    
    def load_config(self) -> None:
        """設定ファイルを読み込む"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = {}
                self.save_config()
        except Exception as e:
            logger.error(f"設定ファイルの読み込みに失敗: {str(e)}")
            raise ConfigError(f"設定ファイルの読み込みに失敗: {str(e)}")
    
    def save_config(self) -> None:
        """設定を保存する"""
        try:
            # バックアップを作成
            if self.config_file.exists():
                backup_file = self.backup_dir / f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(self.config_file, 'r', encoding='utf-8') as src, \
                     open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            # 設定を保存
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"設定の保存に失敗: {str(e)}")
            raise ConfigError(f"設定の保存に失敗: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """設定値を設定"""
        self._config[key] = value
        self.save_config()
    
    def delete(self, key: str) -> None:
        """設定値を削除"""
        if key in self._config:
            del self._config[key]
            self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """全ての設定を取得"""
        return self._config.copy()
    
    def restore_backup(self, backup_file: str) -> None:
        """バックアップから復元"""
        backup_path = self.backup_dir / backup_file
        if not backup_path.exists():
            raise ConfigError(f"バックアップファイルが見つかりません: {backup_file}")
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            self.save_config()
        except Exception as e:
            logger.error(f"バックアップからの復元に失敗: {str(e)}")
            raise ConfigError(f"バックアップからの復元に失敗: {str(e)}")
    
    def list_backups(self) -> list[str]:
        """利用可能なバックアップの一覧を取得"""
        return [f.name for f in self.backup_dir.glob("config_*.json")]
    
    def validate_config(self) -> bool:
        """設定の検証"""
        # 必須の設定項目をチェック
        required_keys = [
            "api_keys",
            "database",
            "logging"
        ]
        
        for key in required_keys:
            if key not in self._config:
                logger.error(f"必須の設定項目が不足しています: {key}")
                return False
        
        return True
    
    def validate_config_with_schema(self, config: Dict[str, Any]) -> None:
        """設定の検証"""
        try:
            jsonschema.validate(instance=config, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"設定の検証に失敗しました: {str(e)}")
            raise ValueError(f"設定の検証に失敗しました: {str(e)}")
    
    def create_backup(self, config_name: str) -> None:
        """設定のバックアップを作成"""
        config_file = self.config_dir / f"{config_name}.json"
        if not config_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{config_name}_{timestamp}.json"
        
        shutil.copy2(config_file, backup_file)
        logger.info(f"設定のバックアップを作成しました: {backup_file}")
    
    def restore_backup_with_timestamp(self, config_name: str, backup_timestamp: str) -> None:
        """バックアップからの復元"""
        backup_file = self.backup_dir / f"{config_name}_{backup_timestamp}.json"
        if not backup_file.exists():
            raise FileNotFoundError(f"バックアップファイルが見つかりません: {backup_file}")
        
        config_file = self.config_dir / f"{config_name}.json"
        
        # 現在の設定のバックアップを作成
        self.create_backup(config_name)
        
        # バックアップから復元
        shutil.copy2(backup_file, config_file)
        logger.info(f"設定をバックアップから復元しました: {backup_file}")
    
    def list_backups_with_details(self, config_name: str) -> list:
        """バックアップの一覧を取得"""
        backups = []
        for backup_file in self.backup_dir.glob(f"{config_name}_*.json"):
            timestamp = backup_file.stem.split("_")[-1]
            backups.append({
                "timestamp": timestamp,
                "file": str(backup_file),
                "size": backup_file.stat().st_size,
                "modified": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            })
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def cleanup_old_backups(self, days: int = 30) -> None:
        """古いバックアップの削除"""
        current_time = datetime.now()
        for backup_file in self.backup_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if (current_time - file_time).days > days:
                backup_file.unlink()
                logger.info(f"古いバックアップを削除しました: {backup_file}")

# シングルトンインスタンス
_config_manager_instance = None

def get_config_manager() -> ConfigManager:
    """設定マネージャーのインスタンスを取得"""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance 