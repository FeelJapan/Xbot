import logging
import os
from datetime import datetime
from typing import Optional
from .config import get_settings

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    ロガーを設定する

    Args:
        name: ロガー名
        level: ログレベル

    Returns:
        logging.Logger: 設定されたロガー
    """
    settings = get_settings()
    
    # ログレベルの設定
    log_level = level or settings.log_level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # ロガーの作成
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # 既存のハンドラーをクリア
    logger.handlers.clear()
    
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # ファイルハンドラーの設定
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
    file_handler.setLevel(numeric_level)
    
    # フォーマッターの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # ハンドラーの追加
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得する

    Args:
        name: ロガー名

    Returns:
        logging.Logger: ロガーインスタンス
    """
    return setup_logger(name)

# デフォルトロガー
default_logger = get_logger("trend_analysis")

def log_function_call(func_name: str, **kwargs):
    """
    関数呼び出しをログに記録する

    Args:
        func_name: 関数名
        **kwargs: 関数の引数
    """
    default_logger.info(f"Function call: {func_name} with args: {kwargs}")

def log_error(error: Exception, context: str = ""):
    """
    エラーをログに記録する

    Args:
        error: エラーオブジェクト
        context: エラーのコンテキスト
    """
    error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    default_logger.error(error_msg, exc_info=True)

def log_performance(operation: str, duration: float, **kwargs):
    """
    パフォーマンス情報をログに記録する

    Args:
        operation: 操作名
        duration: 実行時間（秒）
        **kwargs: 追加情報
    """
    additional_info = f" - {kwargs}" if kwargs else ""
    default_logger.info(f"Performance: {operation} took {duration:.2f}s{additional_info}")

def log_api_request(method: str, endpoint: str, status_code: int, duration: float):
    """
    APIリクエストをログに記録する

    Args:
        method: HTTPメソッド
        endpoint: エンドポイント
        status_code: ステータスコード
        duration: 実行時間（秒）
    """
    default_logger.info(f"API Request: {method} {endpoint} - {status_code} ({duration:.2f}s)") 