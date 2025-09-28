"""
通知チャンネルの実装
"""

import smtplib
import requests
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """通知チャンネルの基底クラス"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def send(self, content: Dict[str, Any]) -> bool:
        """通知を送信"""
        pass
    
    def is_enabled(self) -> bool:
        """チャンネルが有効かどうか"""
        return self.enabled
    
    def log_send_attempt(self, success: bool, error: Optional[str] = None):
        """送信試行をログに記録"""
        if success:
            logger.info(f"{self.name}: 通知送信成功")
        else:
            logger.error(f"{self.name}: 通知送信失敗 - {error}")


class EmailChannel(NotificationChannel):
    """メール通知チャンネル"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = config.get("smtp_server", "")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.from_address = config.get("from_address", "")
        self.to_addresses = config.get("to_addresses", [])
        self.use_tls = config.get("use_tls", True)
    
    async def send(self, content: Dict[str, Any]) -> bool:
        """メール通知を送信"""
        if not self.is_enabled() or not self.to_addresses:
            return False
        
        try:
            msg = MIMEMultipart()
            msg["Subject"] = content.get("title", "Xbot通知")
            msg["From"] = self.from_address
            msg["To"] = ", ".join(self.to_addresses)
            
            # 本文の作成
            body = self._create_email_body(content)
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            # 添付ファイルがある場合
            if "attachments" in content:
                for attachment in content["attachments"]:
                    self._attach_file(msg, attachment)
            
            # SMTPサーバーに接続して送信
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.log_send_attempt(True)
            return True
            
        except Exception as e:
            error_msg = f"メール送信エラー: {str(e)}"
            self.log_send_attempt(False, error_msg)
            return False
    
    def _create_email_body(self, content: Dict[str, Any]) -> str:
        """メール本文を作成"""
        body = f"""
{content.get("title", "Xbot通知")}

{content.get("message", "")}

詳細情報:
- 通知レベル: {content.get("level", "INFO")}
- 送信時刻: {content.get("timestamp", datetime.now())}
- 送信元: {content.get("source", "Xbot")}

"""
        
        if "details" in content and content["details"]:
            body += "詳細データ:\n"
            for key, value in content["details"].items():
                body += f"- {key}: {value}\n"
        
        return body
    
    def _attach_file(self, msg: MIMEMultipart, attachment_path: str):
        """ファイルを添付"""
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {Path(attachment_path).name}"
            )
            msg.attach(part)
        except Exception as e:
            logger.warning(f"ファイル添付に失敗: {attachment_path} - {e}")


class SlackChannel(NotificationChannel):
    """Slack通知チャンネル"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url", "")
        self.channel = config.get("channel", "#general")
        self.username = config.get("username", "Xbot")
        self.icon_emoji = config.get("icon_emoji", ":robot_face:")
    
    async def send(self, content: Dict[str, Any]) -> bool:
        """Slack通知を送信"""
        if not self.is_enabled() or not self.webhook_url:
            return False
        
        try:
            # Slack用のメッセージ構造を作成
            slack_message = self._create_slack_message(content)
            
            # WebhookにPOST
            response = requests.post(
                self.webhook_url,
                json=slack_message,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_send_attempt(True)
                return True
            else:
                error_msg = f"Slack API エラー: {response.status_code}"
                self.log_send_attempt(False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Slack送信エラー: {str(e)}"
            self.log_send_attempt(False, error_msg)
            return False
    
    def _create_slack_message(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Slack用メッセージを作成"""
        # レベルに応じた色を設定
        color_map = {
            "INFO": "#36a64f",      # 緑
            "WARNING": "#ff9500",   # オレンジ
            "ERROR": "#ff0000",     # 赤
            "CRITICAL": "#8b0000"   # 濃い赤
        }
        
        level = content.get("level", "INFO")
        color = color_map.get(level, "#36a64f")
        
        # フィールドの作成
        fields = []
        if "details" in content and content["details"]:
            for key, value in content["details"].items():
                fields.append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
        
        # タイムスタンプ
        timestamp = content.get("timestamp", datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        return {
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "attachments": [{
                "color": color,
                "title": content.get("title", "Xbot通知"),
                "text": content.get("message", ""),
                "fields": fields,
                "footer": f"送信元: {content.get('source', 'Xbot')}",
                "ts": int(timestamp.timestamp())
            }]
        }


class WebhookChannel(NotificationChannel):
    """Webhook通知チャンネル"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url", "")
        self.method = config.get("method", "POST")
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 10)
    
    async def send(self, content: Dict[str, Any]) -> bool:
        """Webhook通知を送信"""
        if not self.is_enabled() or not self.webhook_url:
            return False
        
        try:
            # カスタムヘッダーを設定
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Xbot-Notification/1.0"
            }
            headers.update(self.headers)
            
            # リクエストを送信
            if self.method.upper() == "POST":
                response = requests.post(
                    self.webhook_url,
                    json=content,
                    headers=headers,
                    timeout=self.timeout
                )
            elif self.method.upper() == "PUT":
                response = requests.put(
                    self.webhook_url,
                    json=content,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                response = requests.get(
                    self.webhook_url,
                    params=content,
                    headers=headers,
                    timeout=self.timeout
                )
            
            if response.status_code in [200, 201, 202]:
                self.log_send_attempt(True)
                return True
            else:
                error_msg = f"Webhook API エラー: {response.status_code}"
                self.log_send_attempt(False, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Webhook送信エラー: {str(e)}"
            self.log_send_attempt(False, error_msg)
            return False

