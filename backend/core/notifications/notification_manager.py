"""
通知システムの中心となるマネージャークラス
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import asdict

from .notification_types import (
    NotificationType, 
    NotificationLevel, 
    NotificationContent,
    NotificationTemplate
)
from .notification_channels import (
    EmailChannel, 
    SlackChannel, 
    WebhookChannel
)

logger = logging.getLogger(__name__)


class NotificationManager:
    """通知システムの中心マネージャー"""
    
    def __init__(self, config_path: str = "config/notification.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.channels = self._initialize_channels()
        self.templates = self._load_templates()
        self.db_path = Path("data/notifications.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # 通知履歴の管理
        self.notification_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # レポート通知のスケジュール
        self.report_schedules = {
            "daily": {"hour": 9, "minute": 0},      # 毎日9:00
            "weekly": {"day": "monday", "hour": 9, "minute": 0},  # 毎週月曜9:00
            "monthly": {"day": 1, "hour": 9, "minute": 0}        # 毎月1日9:00
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """通知設定を読み込み"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"通知設定の読み込みに失敗: {e}")
        
        # デフォルト設定
        return {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": [],
                "use_tls": True
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#general",
                "username": "Xbot",
                "icon_emoji": ":robot_face:"
            },
            "webhook": {
                "enabled": False,
                "webhook_url": "",
                "method": "POST",
                "headers": {},
                "timeout": 10
            },
            "general": {
                "retry_attempts": 3,
                "retry_delay": 5,
                "batch_size": 10,
                "enable_quota_warnings": True,
                "enable_system_notifications": True,
                "enable_report_notifications": True
            }
        }
    
    def _initialize_channels(self) -> Dict[str, Any]:
        """通知チャンネルを初期化"""
        channels = {}
        
        if self.config.get("email", {}).get("enabled", False):
            channels["email"] = EmailChannel(self.config["email"])
        
        if self.config.get("slack", {}).get("enabled", False):
            channels["slack"] = SlackChannel(self.config["slack"])
        
        if self.config.get("webhook", {}).get("enabled", False):
            channels["webhook"] = WebhookChannel(self.config["webhook"])
        
        return channels
    
    def _load_templates(self) -> Dict[str, NotificationTemplate]:
        """通知テンプレートを読み込み"""
        templates = {}
        
        # デフォルトテンプレート
        default_templates = [
            NotificationTemplate(
                template_id="error_notification",
                type=NotificationType.ERROR,
                title_template="エラー通知: {error_type}",
                message_template="関数 {function_name} でエラーが発生しました: {error_message}",
                level=NotificationLevel.ERROR,
                channels=["email", "slack"]
            ),
            NotificationTemplate(
                template_id="system_notification",
                type=NotificationType.SYSTEM,
                title_template="システム通知: {operation}",
                message_template="システム操作 {operation} が完了しました",
                level=NotificationLevel.INFO,
                channels=["email", "slack"]
            ),
            NotificationTemplate(
                template_id="quota_warning",
                type=NotificationType.QUOTA_WARNING,
                title_template="クォータ警告: {service}",
                message_template="サービス {service} のクォータ使用量が {usage}% に達しています",
                level=NotificationLevel.WARNING,
                channels=["email", "slack"]
            ),
            NotificationTemplate(
                template_id="backup_complete",
                type=NotificationType.BACKUP_COMPLETE,
                title_template="バックアップ完了",
                message_template="データベースのバックアップが正常に完了しました",
                level=NotificationLevel.INFO,
                channels=["email"]
            ),
            NotificationTemplate(
                template_id="trend_analysis_complete",
                type=NotificationType.TREND_ANALYSIS,
                title_template="トレンド分析完了",
                message_template="トレンド分析が完了しました。{video_count}件の動画を分析しました。",
                level=NotificationLevel.INFO,
                channels=["email", "slack"]
            ),
            NotificationTemplate(
                template_id="content_generation_complete",
                type=NotificationType.CONTENT_GENERATION,
                title_template="コンテンツ生成完了",
                message_template="コンテンツ生成が完了しました。{content_type}を{count}件生成しました。",
                level=NotificationLevel.INFO,
                channels=["email"]
            )
        ]
        
        for template in default_templates:
            templates[template.template_id] = template
        
        return templates
    
    def _init_database(self):
        """通知データベースを初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        type TEXT NOT NULL,
                        level TEXT NOT NULL,
                        title TEXT NOT NULL,
                        message TEXT NOT NULL,
                        source TEXT,
                        details TEXT,
                        sent_channels TEXT,
                        success_count INTEGER DEFAULT 0,
                        failure_count INTEGER DEFAULT 0
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"通知データベースの初期化に失敗: {e}")
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        template_id: Optional[str] = None,
        channels: Optional[List[str]] = None
    ) -> bool:
        """通知を送信"""
        try:
            # テンプレートを使用する場合
            if template_id and template_id in self.templates:
                template = self.templates[template_id]
                title = template.title_template.format(**details or {})
                message = template.message_template.format(**details or {})
                level = template.level
                if not channels:
                    channels = template.channels
            
            # 通知内容を作成
            content = {
                "title": title,
                "message": message,
                "level": level.value,
                "timestamp": datetime.now().isoformat(),
                "source": source or "Xbot",
                "details": details or {}
            }
            
            # 指定されたチャンネルまたは有効なチャンネルに送信
            if channels:
                target_channels = [ch for ch in channels if ch in self.channels]
            else:
                target_channels = list(self.channels.keys())
            
            # 通知を送信
            success_count = 0
            failure_count = 0
            
            for channel_name in target_channels:
                channel = self.channels[channel_name]
                if await channel.send(content):
                    success_count += 1
                else:
                    failure_count += 1
            
            # 通知履歴に記録
            await self._record_notification(
                notification_type, level, title, message, 
                source, details, target_channels, success_count, failure_count
            )
            
            # 成功した通知があれば成功とする
            return success_count > 0
            
        except Exception as e:
            logger.error(f"通知送信中にエラーが発生: {e}")
            return False
    
    async def send_error_notification(
        self,
        error: Exception,
        function_name: str,
        source: Optional[str] = None,
        additional_details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """エラー通知を送信"""
        details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "function_name": function_name
        }
        
        if additional_details:
            details.update(additional_details)
        
        return await self.send_notification(
            notification_type=NotificationType.ERROR,
            title=f"エラー通知: {type(error).__name__}",
            message=f"関数 {function_name} でエラーが発生しました",
            level=NotificationLevel.ERROR,
            source=source,
            details=details,
            template_id="error_notification"
        )
    
    async def send_system_notification(
        self,
        operation: str,
        status: str = "完了",
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """システム通知を送信"""
        if not self.config.get("general", {}).get("enable_system_notifications", True):
            return True
        
        notification_details = {
            "operation": operation,
            "status": status
        }
        
        if details:
            notification_details.update(details)
        
        return await self.send_notification(
            notification_type=NotificationType.SYSTEM,
            title=f"システム通知: {operation}",
            message=f"システム操作 {operation} が{status}しました",
            level=NotificationLevel.INFO,
            details=notification_details,
            template_id="system_notification"
        )
    
    async def send_quota_warning(
        self,
        service: str,
        usage_percentage: float,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """クォータ警告を送信"""
        if not self.config.get("general", {}).get("enable_quota_warnings", True):
            return True
        
        warning_details = {
            "service": service,
            "usage": f"{usage_percentage:.1f}%"
        }
        
        if details:
            warning_details.update(details)
        
        return await self.send_notification(
            notification_type=NotificationType.QUOTA_WARNING,
            title=f"クォータ警告: {service}",
            message=f"サービス {service} のクォータ使用量が {usage_percentage:.1f}% に達しています",
            level=NotificationLevel.WARNING,
            details=warning_details,
            template_id="quota_warning"
        )
    
    async def send_backup_complete_notification(
        self,
        backup_path: str,
        file_size: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """バックアップ完了通知を送信"""
        backup_details = {
            "backup_path": backup_path,
            "file_size": file_size
        }
        
        if details:
            backup_details.update(details)
        
        return await self.send_notification(
            notification_type=NotificationType.BACKUP_COMPLETE,
            title="バックアップ完了",
            message="データベースのバックアップが正常に完了しました",
            level=NotificationLevel.INFO,
            details=backup_details,
            template_id="backup_complete"
        )
    
    async def send_trend_analysis_complete_notification(
        self,
        video_count: int,
        analysis_duration: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """トレンド分析完了通知を送信"""
        analysis_details = {
            "video_count": video_count,
            "analysis_duration": analysis_duration
        }
        
        if details:
            analysis_details.update(details)
        
        return await self.send_notification(
            notification_type=NotificationType.TREND_ANALYSIS,
            title="トレンド分析完了",
            message=f"トレンド分析が完了しました。{video_count}件の動画を分析しました。",
            level=NotificationLevel.INFO,
            details=analysis_details,
            template_id="trend_analysis_complete"
        )
    
    async def send_content_generation_complete_notification(
        self,
        content_type: str,
        count: int,
        generation_time: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """コンテンツ生成完了通知を送信"""
        generation_details = {
            "content_type": content_type,
            "count": count,
            "generation_time": generation_time
        }
        
        if details:
            generation_details.update(details)
        
        return await self.send_notification(
            notification_type=NotificationType.CONTENT_GENERATION,
            title="コンテンツ生成完了",
            message=f"コンテンツ生成が完了しました。{content_type}を{count}件生成しました。",
            level=NotificationLevel.INFO,
            details=generation_details,
            template_id="content_generation_complete"
        )
    
    async def _record_notification(
        self,
        notification_type: NotificationType,
        level: NotificationLevel,
        title: str,
        message: str,
        source: Optional[str],
        details: Optional[Dict[str, Any]],
        channels: List[str],
        success_count: int,
        failure_count: int
    ):
        """通知をデータベースに記録"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications 
                    (timestamp, type, level, title, message, source, details, 
                     sent_channels, success_count, failure_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    notification_type.value,
                    level.value,
                    title,
                    message,
                    source,
                    json.dumps(details) if details else None,
                    json.dumps(channels),
                    success_count,
                    failure_count
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"通知の記録に失敗: {e}")
    
    async def get_notification_history(
        self,
        limit: int = 100,
        notification_type: Optional[NotificationType] = None,
        level: Optional[NotificationLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """通知履歴を取得"""
        try:
            query = "SELECT * FROM notifications WHERE 1=1"
            params = []
            
            if notification_type:
                query += " AND type = ?"
                params.append(notification_type.value)
            
            if level:
                query += " AND level = ?"
                params.append(level.value)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # カラム名を取得
                columns = [description[0] for description in cursor.description]
                
                # 辞書のリストに変換
                result = []
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    # JSONフィールドをパース
                    if row_dict.get("details"):
                        try:
                            row_dict["details"] = json.loads(row_dict["details"])
                        except:
                            pass
                    if row_dict.get("sent_channels"):
                        try:
                            row_dict["sent_channels"] = json.loads(row_dict["sent_channels"])
                        except:
                            pass
                    result.append(row_dict)
                
                return result
                
        except Exception as e:
            logger.error(f"通知履歴の取得に失敗: {e}")
            return []
    
    def get_notification_statistics(self) -> Dict[str, Any]:
        """通知統計を取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 総通知数
                cursor.execute("SELECT COUNT(*) FROM notifications")
                total_count = cursor.fetchone()[0]
                
                # タイプ別通知数
                cursor.execute("SELECT type, COUNT(*) FROM notifications GROUP BY type")
                type_counts = dict(cursor.fetchall())
                
                # レベル別通知数
                cursor.execute("SELECT level, COUNT(*) FROM notifications GROUP BY level")
                level_counts = dict(cursor.fetchall())
                
                # 成功・失敗率
                cursor.execute("SELECT SUM(success_count), SUM(failure_count) FROM notifications")
                success_total, failure_total = cursor.fetchone()
                success_total = success_total or 0
                failure_total = failure_total or 0
                total_sent = success_total + failure_total
                success_rate = (success_total / total_sent * 100) if total_sent > 0 else 0
                
                return {
                    "total_notifications": total_count,
                    "type_counts": type_counts,
                    "level_counts": level_counts,
                    "success_count": success_total,
                    "failure_count": failure_total,
                    "success_rate": round(success_rate, 2)
                }
                
        except Exception as e:
            logger.error(f"通知統計の取得に失敗: {e}")
            return {}
    
    def cleanup_old_notifications(self, days: int = 30):
        """古い通知を削除"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notifications WHERE timestamp < ?", (cutoff_date,))
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"{deleted_count}件の古い通知を削除しました")
                
        except Exception as e:
            logger.error(f"古い通知の削除に失敗: {e}")


# シングルトンインスタンス
notification_manager = NotificationManager()

