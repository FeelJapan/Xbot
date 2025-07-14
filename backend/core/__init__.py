"""
共通基盤モジュール
このモジュールは、アプリケーション全体で使用される共通機能を提供します。
"""

from .logging.logger import Logger, get_logger

__all__ = [
    'Logger',
    'get_logger',
] 