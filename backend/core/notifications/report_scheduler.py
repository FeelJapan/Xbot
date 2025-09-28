"""
レポート通知のスケジューリング機能
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import schedule
import time
from pathlib import Path

from .notification_manager import notification_manager
from .notification_types import NotificationType, NotificationLevel

logger = logging.getLogger(__name__)


class ReportScheduler:
    """レポート通知のスケジューラー"""
    
    def __init__(self):
        self.scheduler = schedule.Scheduler()
        self.is_running = False
        self.report_tasks = {}
        
        # レポート設定
        self.report_configs = {
            "daily": {
                "enabled": True,
                "time": "09:00",
                "template": "daily_report",
                "channels": ["email", "slack"]
            },
            "weekly": {
                "enabled": True,
                "time": "09:00",
                "day": "monday",
                "template": "weekly_report",
                "channels": ["email", "slack"]
            },
            "monthly": {
                "enabled": True,
                "time": "09:00",
                "day": 1,
                "template": "monthly_report",
                "channels": ["email"]
            }
        }
        
        self._setup_schedules()
    
    def _setup_schedules(self):
        """スケジュールを設定"""
        try:
            # 日次レポート
            if self.report_configs["daily"]["enabled"]:
                self.scheduler.every().day.at(self.report_configs["daily"]["time"]).do(
                    self._generate_daily_report
                )
            
            # 週次レポート
            if self.report_configs["weekly"]["enabled"]:
                self.scheduler.every().monday.at(self.report_configs["weekly"]["time"]).do(
                    self._generate_weekly_report
                )
            
            # 月次レポート
            if self.report_configs["monthly"]["enabled"]:
                self.scheduler.every().month.at(self.report_configs["monthly"]["time"]).do(
                    self._generate_monthly_report
                )
                
            logger.info("レポートスケジュールを設定しました")
            
        except Exception as e:
            logger.error(f"レポートスケジュールの設定に失敗: {e}")
    
    def start(self):
        """スケジューラーを開始"""
        if self.is_running:
            logger.warning("スケジューラーは既に実行中です")
            return
        
        self.is_running = True
        logger.info("レポートスケジューラーを開始しました")
        
        # バックグラウンドでスケジューラーを実行
        asyncio.create_task(self._run_scheduler())
    
    def stop(self):
        """スケジューラーを停止"""
        self.is_running = False
        logger.info("レポートスケジューラーを停止しました")
    
    async def _run_scheduler(self):
        """スケジューラーを実行"""
        while self.is_running:
            try:
                self.scheduler.run_pending()
                await asyncio.sleep(60)  # 1分ごとにチェック
            except Exception as e:
                logger.error(f"スケジューラー実行中にエラーが発生: {e}")
                await asyncio.sleep(60)
    
    async def _generate_daily_report(self):
        """日次レポートを生成・送信"""
        try:
            logger.info("日次レポートを生成中...")
            
            # レポートデータを収集
            report_data = await self._collect_daily_data()
            
            # レポートを生成
            report_content = self._format_daily_report(report_data)
            
            # 通知を送信
            await notification_manager.send_notification(
                notification_type=NotificationType.REPORT,
                title="日次レポート",
                message=report_content,
                level=NotificationLevel.INFO,
                source="ReportScheduler",
                details=report_data,
                channels=self.report_configs["daily"]["channels"]
            )
            
            logger.info("日次レポートを送信しました")
            
        except Exception as e:
            logger.error(f"日次レポートの生成に失敗: {e}")
            await notification_manager.send_error_notification(
                e, "_generate_daily_report", "ReportScheduler"
            )
    
    async def _generate_weekly_report(self):
        """週次レポートを生成・送信"""
        try:
            logger.info("週次レポートを生成中...")
            
            # レポートデータを収集
            report_data = await self._collect_weekly_data()
            
            # レポートを生成
            report_content = self._format_weekly_report(report_data)
            
            # 通知を送信
            await notification_manager.send_notification(
                notification_type=NotificationType.REPORT,
                title="週次レポート",
                message=report_content,
                level=NotificationLevel.INFO,
                source="ReportScheduler",
                details=report_data,
                channels=self.report_configs["weekly"]["channels"]
            )
            
            logger.info("週次レポートを送信しました")
            
        except Exception as e:
            logger.error(f"週次レポートの生成に失敗: {e}")
            await notification_manager.send_error_notification(
                e, "_generate_weekly_report", "ReportScheduler"
            )
    
    async def _generate_monthly_report(self):
        """月次レポートを生成・送信"""
        try:
            logger.info("月次レポートを生成中...")
            
            # レポートデータを収集
            report_data = await self._collect_monthly_data()
            
            # レポートを生成
            report_content = self._format_monthly_report(report_data)
            
            # 通知を送信
            await notification_manager.send_notification(
                notification_type=NotificationType.REPORT,
                title="月次レポート",
                message=report_content,
                level=NotificationLevel.INFO,
                source="ReportScheduler",
                details=report_data,
                channels=self.report_configs["monthly"]["channels"]
            )
            
            logger.info("月次レポートを送信しました")
            
        except Exception as e:
            logger.error(f"月次レポートの生成に失敗: {e}")
            await notification_manager.send_error_notification(
                e, "_generate_monthly_report", "ReportScheduler"
            )
    
    async def _collect_daily_data(self) -> Dict[str, Any]:
        """日次データを収集"""
        try:
            # 今日の日付
            today = datetime.now().date()
            
            # 通知統計
            notification_stats = notification_manager.get_notification_statistics()
            
            # 今日の通知履歴
            today_notifications = await notification_manager.get_notification_history(
                start_date=datetime.combine(today, datetime.min.time()),
                end_date=datetime.combine(today, datetime.max.time())
            )
            
            # システム状態（簡易版）
            system_status = {
                "database_size": self._get_database_size(),
                "log_file_size": self._get_log_file_size(),
                "uptime": self._get_system_uptime()
            }
            
            return {
                "date": today.isoformat(),
                "notification_count": len(today_notifications),
                "notification_stats": notification_stats,
                "system_status": system_status,
                "report_type": "daily"
            }
            
        except Exception as e:
            logger.error(f"日次データの収集に失敗: {e}")
            return {"error": str(e), "report_type": "daily"}
    
    async def _collect_weekly_data(self) -> Dict[str, Any]:
        """週次データを収集"""
        try:
            # 今週の開始日
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            # 今週の通知履歴
            weekly_notifications = await notification_manager.get_notification_history(
                start_date=datetime.combine(week_start, datetime.min.time()),
                end_date=datetime.combine(week_end, datetime.max.time())
            )
            
            # 週次統計
            weekly_stats = {
                "total_notifications": len(weekly_notifications),
                "error_count": len([n for n in weekly_notifications if n["level"] == "error"]),
                "warning_count": len([n for n in weekly_notifications if n["level"] == "warning"]),
                "success_rate": self._calculate_success_rate(weekly_notifications)
            }
            
            return {
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "weekly_stats": weekly_stats,
                "notification_details": weekly_notifications[:10],  # 最新10件
                "report_type": "weekly"
            }
            
        except Exception as e:
            logger.error(f"週次データの収集に失敗: {e}")
            return {"error": str(e), "report_type": "weekly"}
    
    async def _collect_monthly_data(self) -> Dict[str, Any]:
        """月次データを収集"""
        try:
            # 今月の開始日
            today = datetime.now().date()
            month_start = today.replace(day=1)
            if today.month == 12:
                month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            
            # 今月の通知履歴
            monthly_notifications = await notification_manager.get_notification_history(
                start_date=datetime.combine(month_start, datetime.min.time()),
                end_date=datetime.combine(month_end, datetime.max.time())
            )
            
            # 月次統計
            monthly_stats = {
                "total_notifications": len(monthly_notifications),
                "type_breakdown": self._get_type_breakdown(monthly_notifications),
                "level_breakdown": self._get_level_breakdown(monthly_notifications),
                "success_rate": self._calculate_success_rate(monthly_notifications)
            }
            
            return {
                "month": today.strftime("%Y-%m"),
                "month_start": month_start.isoformat(),
                "month_end": month_end.isoformat(),
                "monthly_stats": monthly_stats,
                "report_type": "monthly"
            }
            
        except Exception as e:
            logger.error(f"月次データの収集に失敗: {e}")
            return {"error": str(e), "report_type": "monthly"}
    
    def _format_daily_report(self, data: Dict[str, Any]) -> str:
        """日次レポートをフォーマット"""
        if "error" in data:
            return f"日次レポートの生成に失敗しました: {data['error']}"
        
        content = f"""
📊 日次レポート ({data['date']})

📈 通知統計
- 総通知数: {data['notification_count']}件
- 成功率: {data['notification_stats'].get('success_rate', 0)}%

💾 システム状態
- データベースサイズ: {data['system_status']['database_size']}
- ログファイルサイズ: {data['system_status']['log_file_size']}
- システム稼働時間: {data['system_status']['uptime']}

詳細な統計情報は添付の詳細データをご確認ください。
"""
        return content.strip()
    
    def _format_weekly_report(self, data: Dict[str, Any]) -> str:
        """週次レポートをフォーマット"""
        if "error" in data:
            return f"週次レポートの生成に失敗しました: {data['error']}"
        
        content = f"""
📊 週次レポート ({data['week_start']} 〜 {data['week_end']})

📈 週次統計
- 総通知数: {data['weekly_stats']['total_notifications']}件
- エラー数: {data['weekly_stats']['error_count']}件
- 警告数: {data['weekly_stats']['warning_count']}件
- 成功率: {data['weekly_stats']['success_rate']}%

詳細な通知履歴は添付の詳細データをご確認ください。
"""
        return content.strip()
    
    def _format_monthly_report(self, data: Dict[str, Any]) -> str:
        """月次レポートをフォーマット"""
        if "error" in data:
            return f"月次レポートの生成に失敗しました: {data['error']}"
        
        content = f"""
📊 月次レポート ({data['month']})

📈 月次統計
- 総通知数: {data['monthly_stats']['total_notifications']}件
- 成功率: {data['monthly_stats']['success_rate']}%

📊 通知タイプ別内訳
{self._format_type_breakdown(data['monthly_stats']['type_breakdown'])}

📊 通知レベル別内訳
{self._format_level_breakdown(data['monthly_stats']['level_breakdown'])}

詳細な統計情報は添付の詳細データをご確認ください。
"""
        return content.strip()
    
    def _format_type_breakdown(self, breakdown: Dict[str, int]) -> str:
        """タイプ別内訳をフォーマット"""
        if not breakdown:
            return "- データなし"
        
        lines = []
        for notification_type, count in breakdown.items():
            lines.append(f"- {notification_type}: {count}件")
        return "\n".join(lines)
    
    def _format_level_breakdown(self, breakdown: Dict[str, int]) -> str:
        """レベル別内訳をフォーマット"""
        if not breakdown:
            return "- データなし"
        
        lines = []
        for level, count in breakdown.items():
            lines.append(f"- {level}: {count}件")
        return "\n".join(lines)
    
    def _get_database_size(self) -> str:
        """データベースサイズを取得"""
        try:
            db_path = Path("data/notifications.db")
            if db_path.exists():
                size_bytes = db_path.stat().st_size
                if size_bytes < 1024:
                    return f"{size_bytes}B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f}KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f}MB"
            return "0B"
        except Exception:
            return "不明"
    
    def _get_log_file_size(self) -> str:
        """ログファイルサイズを取得"""
        try:
            log_path = Path("logs")
            if log_path.exists():
                total_size = sum(f.stat().st_size for f in log_path.rglob('*') if f.is_file())
                if total_size < 1024:
                    return f"{total_size}B"
                elif total_size < 1024 * 1024:
                    return f"{total_size / 1024:.1f}KB"
                else:
                    return f"{total_size / (1024 * 1024):.1f}MB"
            return "0B"
        except Exception:
            return "不明"
    
    def _get_system_uptime(self) -> str:
        """システム稼働時間を取得（簡易版）"""
        try:
            # 実際の実装では、システム起動時刻を記録して計算する
            return "24時間以上"
        except Exception:
            return "不明"
    
    def _calculate_success_rate(self, notifications: List[Dict[str, Any]]) -> float:
        """成功率を計算"""
        if not notifications:
            return 0.0
        
        total_sent = sum(n.get("success_count", 0) + n.get("failure_count", 0) for n in notifications)
        if total_sent == 0:
            return 0.0
        
        total_success = sum(n.get("success_count", 0) for n in notifications)
        return round((total_success / total_sent) * 100, 2)
    
    def _get_type_breakdown(self, notifications: List[Dict[str, Any]]) -> Dict[str, int]:
        """通知タイプ別の内訳を取得"""
        breakdown = {}
        for notification in notifications:
            notification_type = notification.get("type", "unknown")
            breakdown[notification_type] = breakdown.get(notification_type, 0) + 1
        return breakdown
    
    def _get_level_breakdown(self, notifications: List[Dict[str, Any]]) -> Dict[str, int]:
        """通知レベル別の内訳を取得"""
        breakdown = {}
        for notification in notifications:
            level = notification.get("level", "unknown")
            breakdown[level] = breakdown.get(level, 0) + 1
        return breakdown
    
    def add_custom_schedule(
        self,
        schedule_id: str,
        schedule_type: str,
        time: str,
        template: str,
        channels: List[str],
        **kwargs
    ):
        """カスタムスケジュールを追加"""
        try:
            if schedule_type == "daily":
                self.scheduler.every().day.at(time).do(
                    self._generate_custom_report, schedule_id, template, channels
                )
            elif schedule_type == "weekly":
                day = kwargs.get("day", "monday")
                getattr(self.scheduler.every(), day).at(time).do(
                    self._generate_custom_report, schedule_id, template, channels
                )
            elif schedule_type == "monthly":
                day = kwargs.get("day", 1)
                self.scheduler.every().month.at(time).do(
                    self._generate_custom_report, schedule_id, template, channels
                )
            
            self.report_tasks[schedule_id] = {
                "type": schedule_type,
                "time": time,
                "template": template,
                "channels": channels,
                "kwargs": kwargs
            }
            
            logger.info(f"カスタムスケジュール '{schedule_id}' を追加しました")
            
        except Exception as e:
            logger.error(f"カスタムスケジュールの追加に失敗: {e}")
    
    async def _generate_custom_report(self, schedule_id: str, template: str, channels: List[str]):
        """カスタムレポートを生成・送信"""
        try:
            logger.info(f"カスタムレポート '{schedule_id}' を生成中...")
            
            # カスタムレポートの内容を生成（実装は用途に応じてカスタマイズ）
            report_content = f"カスタムレポート '{schedule_id}' が生成されました。"
            
            await notification_manager.send_notification(
                notification_type=NotificationType.REPORT,
                title=f"カスタムレポート: {schedule_id}",
                message=report_content,
                level=NotificationLevel.INFO,
                source="ReportScheduler",
                details={"schedule_id": schedule_id, "template": template},
                channels=channels
            )
            
            logger.info(f"カスタムレポート '{schedule_id}' を送信しました")
            
        except Exception as e:
            logger.error(f"カスタムレポート '{schedule_id}' の生成に失敗: {e}")
            await notification_manager.send_error_notification(
                e, "_generate_custom_report", "ReportScheduler"
            )


# シングルトンインスタンス
report_scheduler = ReportScheduler()

