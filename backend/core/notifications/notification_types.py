"""
通知の種類とレベルを定義
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class NotificationType(str, Enum):
    """通知の種類"""
    ERROR = "error"                    # エラー通知
    SYSTEM = "system"                   # システム通知
    REPORT = "report"                   # レポート通知
    QUOTA_WARNING = "quota_warning"     # クォータ警告
    BACKUP_COMPLETE = "backup_complete" # バックアップ完了
    UPDATE_COMPLETE = "update_complete" # 更新完了
    TREND_ANALYSIS = "trend_analysis"   # トレンド分析完了
    CONTENT_GENERATION = "content_generation"  # コンテンツ生成完了


class NotificationLevel(str, Enum):
    """通知の重要度レベル"""
    INFO = "info"       # 情報
    WARNING = "warning"  # 警告
    ERROR = "error"      # エラー
    CRITICAL = "critical"  # 致命的


class NotificationContent(BaseModel):
    """通知内容の基本クラス"""
    title: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()
    level: NotificationLevel = NotificationLevel.INFO
    source: Optional[str] = None
    user_id: Optional[str] = None


class NotificationTemplate(BaseModel):
    """通知テンプレート"""
    template_id: str
    type: NotificationType
    title_template: str
    message_template: str
    level: NotificationLevel
    channels: list[str]  # 使用する通知チャンネル
    enabled: bool = True

