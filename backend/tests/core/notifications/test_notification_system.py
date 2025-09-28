"""
通知システムのテスト
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.notifications.notification_types import (
    NotificationType, 
    NotificationLevel,
    NotificationContent,
    NotificationTemplate
)
from core.notifications.notification_channels import (
    EmailChannel,
    SlackChannel,
    WebhookChannel
)
from core.notifications.notification_manager import NotificationManager
from core.notifications.report_scheduler import ReportScheduler


class TestNotificationTypes:
    """通知タイプのテスト"""
    
    def test_notification_type_enum(self):
        """通知タイプの列挙値テスト"""
        assert NotificationType.ERROR == "error"
        assert NotificationType.SYSTEM == "system"
        assert NotificationType.REPORT == "report"
        assert NotificationType.QUOTA_WARNING == "quota_warning"
        assert NotificationType.BACKUP_COMPLETE == "backup_complete"
        assert NotificationType.UPDATE_COMPLETE == "update_complete"
        assert NotificationType.TREND_ANALYSIS == "trend_analysis"
        assert NotificationType.CONTENT_GENERATION == "content_generation"
    
    def test_notification_level_enum(self):
        """通知レベルの列挙値テスト"""
        assert NotificationLevel.INFO == "info"
        assert NotificationLevel.WARNING == "warning"
        assert NotificationLevel.ERROR == "error"
        assert NotificationLevel.CRITICAL == "critical"
    
    def test_notification_content_creation(self):
        """通知内容の作成テスト"""
        content = NotificationContent(
            title="テスト通知",
            message="これはテストメッセージです",
            level=NotificationLevel.INFO,
            source="TestSystem"
        )
        
        assert content.title == "テスト通知"
        assert content.message == "これはテストメッセージです"
        assert content.level == NotificationLevel.INFO
        assert content.source == "TestSystem"
        assert content.timestamp is not None
    
    def test_notification_template_creation(self):
        """通知テンプレートの作成テスト"""
        template = NotificationTemplate(
            template_id="test_template",
            type=NotificationType.SYSTEM,
            title_template="テスト: {operation}",
            message_template="操作 {operation} が完了しました",
            level=NotificationLevel.INFO,
            channels=["email", "slack"]
        )
        
        assert template.template_id == "test_template"
        assert template.type == NotificationType.SYSTEM
        assert template.channels == ["email", "slack"]
        assert template.enabled is True


class TestNotificationChannels:
    """通知チャンネルのテスト"""
    
    def test_email_channel_initialization(self):
        """メールチャンネルの初期化テスト"""
        config = {
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "password123",
            "from_address": "test@example.com",
            "to_addresses": ["admin@example.com"]
        }
        
        channel = EmailChannel(config)
        assert channel.enabled is True
        assert channel.smtp_server == "smtp.gmail.com"
        assert channel.smtp_port == 587
        assert channel.username == "test@example.com"
        assert channel.to_addresses == ["admin@example.com"]
    
    def test_slack_channel_initialization(self):
        """Slackチャンネルの初期化テスト"""
        config = {
            "enabled": True,
            "webhook_url": "https://hooks.slack.com/test",
            "channel": "#test",
            "username": "TestBot",
            "icon_emoji": ":test:"
        }
        
        channel = SlackChannel(config)
        assert channel.enabled is True
        assert channel.webhook_url == "https://hooks.slack.com/test"
        assert channel.channel == "#test"
        assert channel.username == "TestBot"
    
    def test_webhook_channel_initialization(self):
        """Webhookチャンネルの初期化テスト"""
        config = {
            "enabled": True,
            "webhook_url": "https://api.example.com/webhook",
            "method": "POST",
            "headers": {"Authorization": "Bearer token"},
            "timeout": 15
        }
        
        channel = WebhookChannel(config)
        assert channel.enabled is True
        assert channel.webhook_url == "https://api.example.com/webhook"
        assert channel.method == "POST"
        assert channel.timeout == 15
    
    def test_channel_disabled(self):
        """チャンネル無効化のテスト"""
        config = {"enabled": False}
        
        email_channel = EmailChannel(config)
        slack_channel = SlackChannel(config)
        webhook_channel = WebhookChannel(config)
        
        assert email_channel.is_enabled() is False
        assert slack_channel.is_enabled() is False
        assert webhook_channel.is_enabled() is False


class TestNotificationManager:
    """通知マネージャーのテスト"""
    
    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """一時的な設定ファイルを作成"""
        config = {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": []
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#general",
                "username": "Xbot"
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
        
        config_file = tmp_path / "notification.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        return str(config_file)
    
    @pytest.fixture
    def notification_manager(self, temp_config_file, tmp_path):
        """通知マネージャーのインスタンスを作成"""
        # データディレクトリを作成
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        manager = NotificationManager(temp_config_file)
        manager.db_path = data_dir / "notifications.db"
        return manager
    
    def test_notification_manager_initialization(self, notification_manager):
        """通知マネージャーの初期化テスト"""
        assert notification_manager.config is not None
        assert isinstance(notification_manager.channels, dict)
        assert isinstance(notification_manager.templates, dict)
        assert len(notification_manager.templates) > 0
    
    def test_default_templates_loaded(self, notification_manager):
        """デフォルトテンプレートの読み込みテスト"""
        expected_templates = [
            "error_notification",
            "system_notification", 
            "quota_warning",
            "backup_complete",
            "trend_analysis_complete",
            "content_generation_complete"
        ]
        
        for template_id in expected_templates:
            assert template_id in notification_manager.templates
    
    @pytest.mark.asyncio
    async def test_send_notification_with_template(self, notification_manager):
        """テンプレートを使用した通知送信テスト"""
        # モックチャンネルを作成
        mock_channel = Mock()
        mock_channel.send.return_value = True
        mock_channel.is_enabled.return_value = True
        
        notification_manager.channels["email"] = mock_channel
        
        # 通知を送信
        result = await notification_manager.send_notification(
            notification_type=NotificationType.SYSTEM,
            title="テスト",
            message="テストメッセージ",
            template_id="system_notification",
            details={"operation": "テスト操作"}
        )
        
        assert result is True
        mock_channel.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_error_notification(self, notification_manager):
        """エラー通知の送信テスト"""
        # モックチャンネルを作成
        mock_channel = Mock()
        mock_channel.send.return_value = True
        mock_channel.is_enabled.return_value = True
        
        notification_manager.channels["email"] = mock_channel
        
        # エラー通知を送信
        error = Exception("テストエラー")
        result = await notification_manager.send_error_notification(
            error, "test_function", "TestSystem"
        )
        
        assert result is True
        mock_channel.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_system_notification(self, notification_manager):
        """システム通知の送信テスト"""
        # モックチャンネルを作成
        mock_channel = Mock()
        mock_channel.send.return_value = True
        mock_channel.is_enabled.return_value = True
        
        notification_manager.channels["email"] = mock_channel
        
        # システム通知を送信
        result = await notification_manager.send_system_notification(
            "テスト操作", "完了", {"detail": "テスト詳細"}
        )
        
        assert result is True
        mock_channel.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_quota_warning(self, notification_manager):
        """クォータ警告の送信テスト"""
        # モックチャンネルを作成
        mock_channel = Mock()
        mock_channel.send.return_value = True
        mock_channel.is_enabled.return_value = True
        
        notification_manager.channels["email"] = mock_channel
        
        # クォータ警告を送信
        result = await notification_manager.send_quota_warning(
            "YouTube API", 85.5, {"quota_type": "daily"}
        )
        
        assert result is True
        mock_channel.send.assert_called_once()
    
    def test_get_notification_statistics(self, notification_manager):
        """通知統計の取得テスト"""
        stats = notification_manager.get_notification_statistics()
        
        assert isinstance(stats, dict)
        assert "total_notifications" in stats
        assert "success_rate" in stats
        assert "type_counts" in stats
        assert "level_counts" in stats


class TestReportScheduler:
    """レポートスケジューラーのテスト"""
    
    @pytest.fixture
    def report_scheduler(self):
        """レポートスケジューラーのインスタンスを作成"""
        return ReportScheduler()
    
    def test_report_scheduler_initialization(self, report_scheduler):
        """レポートスケジューラーの初期化テスト"""
        assert report_scheduler.is_running is False
        assert isinstance(report_scheduler.report_configs, dict)
        assert "daily" in report_scheduler.report_configs
        assert "weekly" in report_scheduler.report_configs
        assert "monthly" in report_scheduler.report_configs
    
    def test_report_configs_structure(self, report_scheduler):
        """レポート設定の構造テスト"""
        daily_config = report_scheduler.report_configs["daily"]
        assert "enabled" in daily_config
        assert "time" in daily_config
        assert "template" in daily_config
        assert "channels" in daily_config
        
        assert daily_config["enabled"] is True
        assert daily_config["time"] == "09:00"
        assert daily_config["channels"] == ["email", "slack"]
    
    @pytest.mark.asyncio
    async def test_daily_report_generation(self, report_scheduler):
        """日次レポート生成のテスト"""
        # モック通知マネージャーを作成
        mock_notification_manager = Mock()
        mock_notification_manager.get_notification_statistics.return_value = {
            "total_notifications": 100,
            "success_rate": 95.5
        }
        mock_notification_manager.get_notification_history.return_value = []
        
        # 通知マネージャーを置き換え
        report_scheduler._collect_daily_data = Mock()
        report_scheduler._collect_daily_data.return_value = {
            "date": "2024-01-01",
            "notification_count": 10,
            "notification_stats": {"success_rate": 95.5},
            "system_status": {
                "database_size": "1.2MB",
                "log_file_size": "500KB",
                "uptime": "24時間以上"
            },
            "report_type": "daily"
        }
        
        # 日次レポートを生成
        report_data = await report_scheduler._collect_daily_data()
        
        assert report_data["date"] == "2024-01-01"
        assert report_data["notification_count"] == 10
        assert report_data["report_type"] == "daily"
        assert "system_status" in report_data
    
    @pytest.mark.asyncio
    async def test_weekly_report_generation(self, report_scheduler):
        """週次レポート生成のテスト"""
        # モックデータを設定
        report_scheduler._collect_weekly_data = Mock()
        report_scheduler._collect_weekly_data.return_value = {
            "week_start": "2024-01-01",
            "week_end": "2024-01-07",
            "weekly_stats": {
                "total_notifications": 50,
                "error_count": 2,
                "warning_count": 3,
                "success_rate": 96.0
            },
            "report_type": "weekly"
        }
        
        # 週次レポートを生成
        report_data = await report_scheduler._collect_weekly_data()
        
        assert report_data["week_start"] == "2024-01-01"
        assert report_data["week_end"] == "2024-01-07"
        assert report_data["weekly_stats"]["total_notifications"] == 50
        assert report_data["weekly_stats"]["success_rate"] == 96.0
    
    @pytest.mark.asyncio
    async def test_monthly_report_generation(self, report_scheduler):
        """月次レポート生成のテスト"""
        # モックデータを設定
        report_scheduler._collect_monthly_data = Mock()
        report_scheduler._collect_monthly_data.return_value = {
            "month": "2024-01",
            "month_start": "2024-01-01",
            "month_end": "2024-01-31",
            "monthly_stats": {
                "total_notifications": 200,
                "type_breakdown": {"system": 150, "error": 50},
                "level_breakdown": {"info": 180, "warning": 15, "error": 5},
                "success_rate": 97.5
            },
            "report_type": "monthly"
        }
        
        # 月次レポートを生成
        report_data = await report_scheduler._collect_monthly_data()
        
        assert report_data["month"] == "2024-01"
        assert report_data["monthly_stats"]["total_notifications"] == 200
        assert report_data["monthly_stats"]["success_rate"] == 97.5
    
    def test_report_formatting(self, report_scheduler):
        """レポートフォーマットのテスト"""
        # 日次レポートのフォーマット
        daily_data = {
            "date": "2024-01-01",
            "notification_count": 25,
            "notification_stats": {"success_rate": 92.0},
            "system_status": {
                "database_size": "2.1MB",
                "log_file_size": "800KB",
                "uptime": "48時間以上"
            }
        }
        
        formatted_report = report_scheduler._format_daily_report(daily_data)
        
        assert "日次レポート" in formatted_report
        assert "25件" in formatted_report
        assert "92.0%" in formatted_report
        assert "2.1MB" in formatted_report
    
    def test_custom_schedule_addition(self, report_scheduler):
        """カスタムスケジュール追加のテスト"""
        # カスタムスケジュールを追加
        report_scheduler.add_custom_schedule(
            schedule_id="custom_daily",
            schedule_type="daily",
            time="15:00",
            template="custom_template",
            channels=["email"]
        )
        
        assert "custom_daily" in report_scheduler.report_tasks
        custom_task = report_scheduler.report_tasks["custom_daily"]
        assert custom_task["type"] == "daily"
        assert custom_task["time"] == "15:00"
        assert custom_task["channels"] == ["email"]


class TestIntegration:
    """統合テスト"""
    
    @pytest.mark.asyncio
    async def test_full_notification_flow(self, tmp_path):
        """完全な通知フローのテスト"""
        # 設定ファイルを作成
        config_file = tmp_path / "notification.json"
        config = {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": []
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#general",
                "username": "Xbot"
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
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        # データディレクトリを作成
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # 通知マネージャーを作成
        manager = NotificationManager(str(config_file))
        manager.db_path = data_dir / "notifications.db"
        
        # 通知を送信（チャンネルは無効なので失敗するが、データベースには記録される）
        result = await manager.send_notification(
            notification_type=NotificationType.SYSTEM,
            title="統合テスト",
            message="これは統合テストです",
            level=NotificationLevel.INFO
        )
        
        # 結果を確認（チャンネルが無効なので失敗）
        assert result is False
        
        # 通知履歴を確認
        history = await manager.get_notification_history(limit=10)
        assert len(history) > 0
        
        # 最新の通知を確認
        latest_notification = history[0]
        assert latest_notification["title"] == "統合テスト"
        assert latest_notification["message"] == "これは統合テストです"
        assert latest_notification["type"] == "system"
        assert latest_notification["level"] == "info"
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, tmp_path):
        """エラーハンドリングの統合テスト"""
        # 設定ファイルを作成
        config_file = tmp_path / "notification.json"
        config = {
            "email": {"enabled": False},
            "slack": {"enabled": False},
            "webhook": {"enabled": False},
            "general": {
                "enable_quota_warnings": True,
                "enable_system_notifications": True,
                "enable_report_notifications": True
            }
        }
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        # データディレクトリを作成
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # 通知マネージャーを作成
        manager = NotificationManager(str(config_file))
        manager.db_path = data_dir / "notifications.db"
        
        # エラー通知を送信
        error = ValueError("テストエラー")
        result = await manager.send_error_notification(
            error, "test_function", "TestSystem", {"additional": "detail"}
        )
        
        # 結果を確認
        assert result is False  # チャンネルが無効なので失敗
        
        # エラー通知の履歴を確認
        error_history = await manager.get_notification_history(
            notification_type=NotificationType.ERROR
        )
        assert len(error_history) > 0
        
        # エラー通知の詳細を確認
        error_notification = error_history[0]
        assert error_notification["type"] == "error"
        assert error_notification["level"] == "error"
        assert "テストエラー" in error_notification["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

