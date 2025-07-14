import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

class Logger:
    def __init__(self, name: str, log_dir: str = "logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # ログディレクトリの作成
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 通常ログの設定
        self.setup_rotating_file_handler("app.log")
        
        # エラーログの設定
        self.setup_rotating_file_handler("error.log", level=logging.ERROR)
        
        # コンソール出力の設定
        self.setup_console_handler()
    
    def setup_rotating_file_handler(self, filename: str, level: int = logging.INFO):
        """ローテーティングファイルハンドラーの設定"""
        log_file = self.log_dir / filename
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def setup_console_handler(self):
        """コンソール出力の設定"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """情報ログの出力"""
        self.logger.info(message)
    
    def error(self, message: str, exc_info: bool = True):
        """エラーログの出力"""
        self.logger.error(message, exc_info=exc_info)
        # エラーログの自動保存
        self.save_error_log(message)
    
    def warning(self, message: str):
        """警告ログの出力"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """デバッグログの出力"""
        self.logger.debug(message)
    
    def save_error_log(self, message: str):
        """エラーログの自動保存"""
        error_log_dir = self.log_dir / "errors"
        error_log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_log_file = error_log_dir / f"error_{timestamp}.log"
        
        with open(error_log_file, "w", encoding="utf-8") as f:
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Message: {message}\n")
            f.write("Stack Trace:\n")
            import traceback
            f.write(traceback.format_exc())
    
    def cleanup_old_logs(self, days: int = 30):
        """古いログファイルの削除"""
        current_time = datetime.now()
        for log_file in self.log_dir.glob("*.log*"):
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            if (current_time - file_time).days > days:
                log_file.unlink()

# シングルトンインスタンス
_logger_instance = None

def get_logger(name: str = "xbot") -> Logger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger(name)
    return _logger_instance 