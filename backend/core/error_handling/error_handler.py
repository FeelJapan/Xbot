"""
エラーハンドリングモジュール
アプリケーション全体で使用される共通のエラーハンドリング機能を提供
"""
import asyncio
from typing import Any, Callable, Optional, Type, Union, List
from functools import wraps
from core.logging.logger import get_logger
import functools
import time
import traceback
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from pathlib import Path

logger = get_logger("error_handler")

class XbotError(Exception):
    """Xbotの基本エラークラス"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class APIError(XbotError):
    """API関連のエラー"""
    pass

class ConfigError(XbotError):
    """設定関連のエラー"""
    pass

class ValidationError(XbotError):
    """バリデーション関連のエラー"""
    pass

class ImageGenerationError(XbotError):
    """画像生成関連のエラー"""
    pass

class VideoGenerationError(XbotError):
    """動画生成関連のエラー"""
    pass

class ContentGenerationError(XbotError):
    """コンテンツ生成関連のエラー"""
    pass

def handle_errors(
    error_types: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    fallback: Optional[Callable] = None
) -> Callable:
    """
    エラーハンドリングデコレータ
    
    Args:
        error_types: 捕捉するエラーの型
        retry_count: リトライ回数
        retry_delay: リトライ間隔（秒）
        fallback: エラー発生時のフォールバック関数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            
            for attempt in range(retry_count + 1):
                try:
                    return await func(*args, **kwargs)
                except error_types as e:
                    last_error = e
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    
                    if attempt < retry_count:
                        await asyncio.sleep(retry_delay)
                        continue
                    
                    if fallback:
                        try:
                            return await fallback(*args, **kwargs)
                        except Exception as fallback_error:
                            logger.error(f"Fallback error in {func.__name__}: {str(fallback_error)}")
                            raise fallback_error
                    
                    raise last_error
            
            return None
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except error_types as e:
                    last_error = e
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    
                    if attempt < retry_count:
                        import time
                        time.sleep(retry_delay)
                        continue
                    
                    if fallback:
                        try:
                            return fallback(*args, **kwargs)
                        except Exception as fallback_error:
                            logger.error(f"Fallback error in {func.__name__}: {str(fallback_error)}")
                            raise fallback_error
                    
                    raise last_error
            
            return None
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

def validate_input(
    validation_func: Callable[[Any], bool],
    error_message: str = "Invalid input"
) -> Callable:
    """
    入力バリデーションデコレータ
    
    Args:
        validation_func: バリデーション関数
        error_message: エラーメッセージ
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not validation_func(*args, **kwargs):
                raise ValidationError(error_message)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class ErrorHandler:
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.error_log_dir = Path("logs/errors")
        self.error_log_dir.mkdir(parents=True, exist_ok=True)
        
        # エラー通知の設定
        self.notification_config = self._load_notification_config()
    
    def _load_notification_config(self) -> dict:
        """通知設定の読み込み"""
        config_path = Path("config/notification.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": []
            }
        }
    
    def retry(self, exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception):
        """リトライデコレータ"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                for attempt in range(self.max_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay * (attempt + 1))
                        else:
                            self.handle_error(e, func.__name__, args, kwargs)
                            raise
                raise last_exception
            return wrapper
        return decorator
    
    def handle_error(self, error: Exception, function_name: str, args: tuple, kwargs: dict):
        """エラーの処理と通知"""
        # エラーログの保存
        self._save_error_log(error, function_name, args, kwargs)
        
        # エラー通知の送信
        self._send_notification(error, function_name)
    
    def _save_error_log(self, error: Exception, function_name: str, args: tuple, kwargs: dict):
        """エラーログの保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_log_file = self.error_log_dir / f"error_{timestamp}.json"
        
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "function_name": function_name,
            "args": str(args),
            "kwargs": str(kwargs),
            "traceback": traceback.format_exc()
        }
        
        with open(error_log_file, "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
    
    def _send_notification(self, error: Exception, function_name: str):
        """エラー通知の送信"""
        if not self.notification_config["email"]["enabled"]:
            return
        
        try:
            msg = MIMEMultipart()
            msg["Subject"] = f"Error Alert: {type(error).__name__} in {function_name}"
            msg["From"] = self.notification_config["email"]["from_address"]
            msg["To"] = ", ".join(self.notification_config["email"]["to_addresses"])
            
            body = f"""
            Error Type: {type(error).__name__}
            Error Message: {str(error)}
            Function: {function_name}
            Time: {datetime.now().isoformat()}
            
            Traceback:
            {traceback.format_exc()}
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(
                self.notification_config["email"]["smtp_server"],
                self.notification_config["email"]["smtp_port"]
            ) as server:
                server.starttls()
                server.login(
                    self.notification_config["email"]["username"],
                    self.notification_config["email"]["password"]
                )
                server.send_message(msg)
        except Exception as e:
            # 通知送信に失敗した場合はログに記録
            self._save_error_log(
                e,
                "_send_notification",
                (error, function_name),
                {}
            )
    
    def cleanup_old_error_logs(self, days: int = 30):
        """古いエラーログの削除"""
        current_time = datetime.now()
        for log_file in self.error_log_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if (current_time - file_time).days > days:
                log_file.unlink()

# シングルトンインスタンス
error_handler = ErrorHandler() 