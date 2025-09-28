# 通知システム

Xbotの包括的な通知システムです。エラー通知、システム通知、レポート通知を複数のチャンネル（メール、Slack、Webhook）を通じて送信できます。

## 機能概要

### 🚨 エラー通知
- アプリケーション内で発生したエラーの自動通知
- エラーの詳細情報（タイプ、メッセージ、関数名、スタックトレース）
- 設定可能な通知条件とレベル

### 🔔 システム通知
- バックアップ完了
- システム更新完了
- クォータ警告
- その他のシステムイベント

### 📊 レポート通知
- **日次レポート**: 毎日9:00に自動送信
- **週次レポート**: 毎週月曜9:00に自動送信
- **月次レポート**: 毎月1日9:00に自動送信
- カスタムレポートスケジュールの追加対応

### 📧 通知チャンネル
- **メール**: SMTP対応（Gmail、Outlook等）
- **Slack**: Webhook対応
- **カスタムWebhook**: 任意のエンドポイント

## アーキテクチャ

```
NotificationManager (中心管理)
├── NotificationTypes (通知タイプ定義)
├── NotificationChannels (送信チャンネル)
│   ├── EmailChannel
│   ├── SlackChannel
│   └── WebhookChannel
├── ReportScheduler (レポートスケジューラー)
└── SQLite Database (通知履歴)
```

## セットアップ

### 1. 設定ファイルの作成

`backend/config/notification.json` を作成し、必要な設定を行います：

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "from_address": "your-email@gmail.com",
    "to_addresses": ["admin@example.com"],
    "use_tls": true
  },
  "slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "channel": "#general",
    "username": "Xbot",
    "icon_emoji": ":robot_face:"
  },
  "general": {
    "enable_quota_warnings": true,
    "enable_system_notifications": true,
    "enable_report_notifications": true
  }
}
```

### 2. 依存関係のインストール

```bash
pip install schedule requests
```

## 使用方法

### 基本的な通知送信

```python
from core.notifications.notification_manager import notification_manager
from core.notifications.notification_types import NotificationType, NotificationLevel

# システム通知
await notification_manager.send_system_notification(
    "データベースバックアップ",
    "完了",
    {"backup_size": "2.5MB"}
)

# クォータ警告
await notification_manager.send_quota_warning(
    "YouTube API",
    87.5,
    {"quota_type": "daily"}
)

# カスタム通知
await notification_manager.send_notification(
    notification_type=NotificationType.SYSTEM,
    title="カスタム通知",
    message="これはカスタム通知です",
    level=NotificationLevel.INFO,
    source="MyService"
)
```

### エラー通知

```python
from core.notifications.notification_manager import notification_manager

try:
    # 何らかの処理
    result = some_function()
except Exception as e:
    # エラー通知を送信
    await notification_manager.send_error_notification(
        e, "some_function", "MyService"
    )
```

### レポートスケジューラーの使用

```python
from core.notifications.report_scheduler import report_scheduler

# レポートスケジューラーを開始
report_scheduler.start()

# カスタムスケジュールを追加
report_scheduler.add_custom_schedule(
    schedule_id="custom_daily",
    schedule_type="daily",
    time="15:00",
    template="custom_template",
    channels=["email"]
)
```

## 通知テンプレート

事前定義済みのテンプレートが利用できます：

- `error_notification`: エラー通知用
- `system_notification`: システム通知用
- `quota_warning`: クォータ警告用
- `backup_complete`: バックアップ完了用
- `trend_analysis_complete`: トレンド分析完了用
- `content_generation_complete`: コンテンツ生成完了用

### テンプレートの使用例

```python
await notification_manager.send_notification(
    notification_type=NotificationType.ERROR,
    title="",  # テンプレートで自動生成
    message="",  # テンプレートで自動生成
    template_id="error_notification",
    details={
        "error_type": "ValueError",
        "error_message": "無効な値です",
        "function_name": "validate_input"
    }
)
```

## 通知履歴の管理

### 履歴の取得

```python
# 最新の通知履歴
history = await notification_manager.get_notification_history(limit=10)

# エラー通知のみ
error_history = await notification_manager.get_notification_history(
    notification_type=NotificationType.ERROR
)

# 特定期間の通知
from datetime import datetime, timedelta
start_date = datetime.now() - timedelta(days=7)
weekly_history = await notification_manager.get_notification_history(
    start_date=start_date
)
```

### 統計情報の取得

```python
stats = notification_manager.get_notification_statistics()
print(f"総通知数: {stats['total_notifications']}")
print(f"成功率: {stats['success_rate']}%")
print(f"タイプ別内訳: {stats['type_counts']}")
```

## データベース

通知履歴はSQLiteデータベース（`data/notifications.db`）に保存されます。

### テーブル構造

```sql
CREATE TABLE notifications (
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
);
```

## 設定オプション

### メール設定

| 項目 | 説明 | デフォルト |
|------|------|------------|
| `enabled` | メール通知の有効/無効 | `false` |
| `smtp_server` | SMTPサーバーのアドレス | - |
| `smtp_port` | SMTPポート番号 | `587` |
| `username` | SMTPユーザー名 | - |
| `password` | SMTPパスワード | - |
| `from_address` | 送信元メールアドレス | - |
| `to_addresses` | 送信先メールアドレス（配列） | `[]` |
| `use_tls` | TLS暗号化の使用 | `true` |

### Slack設定

| 項目 | 説明 | デフォルト |
|------|------|------------|
| `enabled` | Slack通知の有効/無効 | `false` |
| `webhook_url` | Slack Webhook URL | - |
| `channel` | 通知を送信するチャンネル | `#general` |
| `username` | ボットの表示名 | `Xbot` |
| `icon_emoji` | ボットのアイコン絵文字 | `:robot_face:` |

### 一般設定

| 項目 | 説明 | デフォルト |
|------|------|------------|
| `enable_quota_warnings` | クォータ警告の有効/無効 | `true` |
| `enable_system_notifications` | システム通知の有効/無効 | `true` |
| `enable_report_notifications` | レポート通知の有効/無効 | `true` |

## トラブルシューティング

### よくある問題

1. **メール送信が失敗する**
   - SMTP設定を確認
   - アプリパスワードの使用（Gmailの場合）
   - ファイアウォール設定

2. **Slack通知が送信されない**
   - Webhook URLの確認
   - チャンネル名の確認（#を含む）
   - Slackアプリの権限設定

3. **通知が記録されない**
   - データディレクトリの権限確認
   - SQLiteデータベースの初期化確認

### ログの確認

通知システムのログは以下の場所で確認できます：

- アプリケーションログ: `logs/` ディレクトリ
- 通知データベース: `data/notifications.db`
- エラーログ: `logs/errors/` ディレクトリ

## 拡張性

### 新しい通知チャンネルの追加

```python
from core.notifications.notification_channels import NotificationChannel

class CustomChannel(NotificationChannel):
    def __init__(self, config):
        super().__init__(config)
        # カスタム初期化
    
    async def send(self, content):
        # カスタム送信ロジック
        pass
```

### 新しい通知タイプの追加

```python
from core.notifications.notification_types import NotificationType

class CustomNotificationType(str, Enum):
    CUSTOM = "custom"
```

## パフォーマンス

- 通知は非同期で送信されます
- データベース操作は最適化されています
- 大量の通知にも対応可能です

## セキュリティ

- 機密情報（パスワード、APIキー）は設定ファイルで管理
- 通知内容のログ記録は設定可能
- 外部APIへの接続はタイムアウト設定付き

## ライセンス

この通知システムはXbotプロジェクトの一部として提供されています。





