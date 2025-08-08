"""
投稿スケジューラーサービス
投稿のスケジュール管理と実行を行う機能
"""
import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from core.logging.logger import get_logger
from core.async_tasks import get_task_manager
from app.services.post_manager import PostManager, Post, PostStatus

logger = get_logger("scheduler")

class SchedulerError(Exception):
    """スケジューラー関連のエラー"""
    pass

class ScheduleType(Enum):
    """スケジュールタイプ"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class OptimalTimeSlot(Enum):
    """最適な投稿時間帯"""
    MORNING = "morning"      # 7:00-9:00
    LUNCH = "lunch"          # 12:00-13:00
    EVENING = "evening"      # 18:00-20:00
    NIGHT = "night"          # 21:00-23:00

@dataclass
class ScheduleConfig:
    """スケジュール設定"""
    schedule_type: ScheduleType
    start_time: datetime
    end_time: Optional[datetime] = None
    interval_hours: int = 24
    days_of_week: List[int] = None  # 0=月曜日, 6=日曜日
    optimal_time_slots: List[OptimalTimeSlot] = None
    max_posts_per_day: int = 5
    enabled: bool = True

@dataclass
class PostSchedule:
    """投稿スケジュール"""
    id: str
    post_id: str
    scheduled_time: datetime
    schedule_type: ScheduleType
    status: str  # "pending", "executed", "failed", "cancelled"
    created_at: datetime
    executed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class PostScheduler:
    """投稿スケジューラークラス"""
    
    def __init__(self, data_dir: str = "data/scheduler"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.schedules_file = self.data_dir / "schedules.json"
        self.config_file = self.data_dir / "config.json"
        
        # サービス初期化
        self.post_manager = PostManager()
        self.task_manager = get_task_manager()
        
        # データ読み込み
        self.schedules: Dict[str, PostSchedule] = {}
        self.config: ScheduleConfig = None
        self.load_data()
        
        # スケジューラー開始
        self.running = False
        self.start_scheduler()
        
    def load_data(self) -> None:
        """データを読み込み"""
        try:
            # スケジュールデータの読み込み
            if self.schedules_file.exists():
                with open(self.schedules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.schedules = {
                        schedule_id: self._dict_to_schedule(schedule_data)
                        for schedule_id, schedule_data in data.items()
                    }
            
            # 設定データの読み込み
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    try:
                        self.config = ScheduleConfig(
                            schedule_type=ScheduleType(data["schedule_type"]),
                            start_time=datetime.fromisoformat(data["start_time"]),
                            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
                            interval_hours=data["interval_hours"],
                            days_of_week=data["days_of_week"],
                            optimal_time_slots=[OptimalTimeSlot(slot) for slot in data["optimal_time_slots"]] if data.get("optimal_time_slots") else [],
                            max_posts_per_day=data["max_posts_per_day"],
                            enabled=data["enabled"]
                        )
                    except (ValueError, KeyError) as e:
                        logger.warning(f"設定ファイルの読み込みでエラーが発生しました: {str(e)}。デフォルト設定を使用します。")
                        self._create_default_config()
                        return
            else:
                self._create_default_config()
                    
            logger.info("スケジューラーデータを読み込みました")
            
        except Exception as e:
            logger.error(f"スケジューラーデータの読み込みに失敗しました: {str(e)}")
            self._create_default_config()
    
    def save_data(self) -> None:
        """データを保存"""
        try:
            # スケジュールデータの保存
            schedules_data = {
                schedule_id: self._schedule_to_dict(schedule)
                for schedule_id, schedule in self.schedules.items()
            }
            with open(self.schedules_file, 'w', encoding='utf-8') as f:
                json.dump(schedules_data, f, indent=2, ensure_ascii=False)
            
            # 設定データの保存（Enumを文字列に変換）
            if self.config:
                config_data = {
                    "schedule_type": self.config.schedule_type.value,
                    "start_time": self.config.start_time.isoformat(),
                    "end_time": self.config.end_time.isoformat() if self.config.end_time else None,
                    "interval_hours": self.config.interval_hours,
                    "days_of_week": self.config.days_of_week,
                    "optimal_time_slots": [slot.value for slot in self.config.optimal_time_slots] if self.config.optimal_time_slots else [],
                    "max_posts_per_day": self.config.max_posts_per_day,
                    "enabled": self.config.enabled
                }
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logger.info("スケジューラーデータを保存しました")
            
        except Exception as e:
            logger.error(f"スケジューラーデータの保存に失敗しました: {str(e)}")
            raise SchedulerError(f"スケジューラーデータの保存に失敗しました: {str(e)}")
    
    def _create_default_config(self) -> None:
        """デフォルト設定を作成"""
        self.config = ScheduleConfig(
            schedule_type=ScheduleType.DAILY,
            start_time=datetime.now(),
            interval_hours=24,
            days_of_week=[0, 1, 2, 3, 4, 5, 6],  # 毎日
            optimal_time_slots=[
                OptimalTimeSlot.MORNING,
                OptimalTimeSlot.EVENING
            ],
            max_posts_per_day=3,
            enabled=True
        )
        
        self.save_data()
        logger.info("デフォルトスケジューラー設定を作成しました")
    
    def start_scheduler(self) -> None:
        """スケジューラーを開始"""
        if not self.running:
            try:
                # イベントループが実行中かチェック
                loop = asyncio.get_running_loop()
                self.running = True
                asyncio.create_task(self._scheduler_loop())
                logger.info("投稿スケジューラーを開始しました")
            except RuntimeError:
                # イベントループが実行されていない場合はスケジューラーを開始しない
                logger.info("イベントループが実行されていないため、スケジューラーの開始をスキップしました")
    
    def stop_scheduler(self) -> None:
        """スケジューラーを停止"""
        self.running = False
        logger.info("投稿スケジューラーを停止しました")
    
    async def _scheduler_loop(self) -> None:
        """スケジューラーのメインループ"""
        while self.running:
            try:
                # 実行予定のスケジュールをチェック
                await self._check_scheduled_posts()
                
                # 1分待機
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"スケジューラーループでエラーが発生: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_scheduled_posts(self) -> None:
        """スケジュール済み投稿をチェック"""
        now = datetime.now()
        
        for schedule_id, schedule in self.schedules.items():
            if (schedule.status == "pending" and 
                schedule.scheduled_time <= now):
                
                try:
                    # 投稿を実行
                    success = await self.post_manager.post_now(schedule.post_id)
                    
                    if success:
                        schedule.status = "executed"
                        schedule.executed_at = now
                        logger.info(f"スケジュール投稿を実行しました: {schedule_id}")
                    else:
                        schedule.status = "failed"
                        schedule.error_message = "投稿実行に失敗しました"
                        logger.error(f"スケジュール投稿の実行に失敗しました: {schedule_id}")
                    
                    self.save_data()
                    
                except Exception as e:
                    schedule.status = "failed"
                    schedule.error_message = str(e)
                    self.save_data()
                    logger.error(f"スケジュール投稿の実行でエラーが発生: {schedule_id} - {str(e)}")
    
    def schedule_post(
        self,
        post_id: str,
        scheduled_time: datetime,
        schedule_type: ScheduleType = ScheduleType.ONCE
    ) -> PostSchedule:
        """投稿をスケジュール"""
        try:
            schedule_id = self._generate_schedule_id()
            now = datetime.now()
            
            schedule = PostSchedule(
                id=schedule_id,
                post_id=post_id,
                scheduled_time=scheduled_time,
                schedule_type=schedule_type,
                status="pending",
                created_at=now
            )
            
            self.schedules[schedule_id] = schedule
            self.save_data()
            
            logger.info(f"投稿をスケジュールしました: {schedule_id} -> {scheduled_time}")
            return schedule
            
        except Exception as e:
            logger.error(f"投稿のスケジュールに失敗しました: {str(e)}")
            raise SchedulerError(f"投稿のスケジュールに失敗しました: {str(e)}")
    
    def cancel_schedule(self, schedule_id: str) -> bool:
        """スケジュールをキャンセル"""
        try:
            if schedule_id not in self.schedules:
                return False
            
            schedule = self.schedules[schedule_id]
            if schedule.status == "pending":
                schedule.status = "cancelled"
                self.save_data()
                logger.info(f"スケジュールをキャンセルしました: {schedule_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"スケジュールのキャンセルに失敗しました: {str(e)}")
            raise SchedulerError(f"スケジュールのキャンセルに失敗しました: {str(e)}")
    
    def get_schedule(self, schedule_id: str) -> Optional[PostSchedule]:
        """スケジュールを取得"""
        return self.schedules.get(schedule_id)
    
    def get_schedules(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[PostSchedule]:
        """スケジュール一覧を取得"""
        schedules = list(self.schedules.values())
        
        if status:
            schedules = [s for s in schedules if s.status == status]
        
        # 日時順にソート
        schedules.sort(key=lambda x: x.scheduled_time, reverse=True)
        
        return schedules[:limit]
    
    def get_pending_schedules(self) -> List[PostSchedule]:
        """実行待ちスケジュール一覧を取得"""
        return [
            schedule for schedule in self.schedules.values()
            if schedule.status == "pending"
        ]
    
    def suggest_optimal_times(
        self,
        date: datetime,
        max_suggestions: int = 3
    ) -> List[datetime]:
        """最適な投稿時間を提案"""
        try:
            if not self.config.optimal_time_slots:
                return []
            
            suggestions = []
            base_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            for slot in self.config.optimal_time_slots:
                if slot == OptimalTimeSlot.MORNING:
                    suggestions.append(base_date.replace(hour=8, minute=0))
                elif slot == OptimalTimeSlot.LUNCH:
                    suggestions.append(base_date.replace(hour=12, minute=30))
                elif slot == OptimalTimeSlot.EVENING:
                    suggestions.append(base_date.replace(hour=19, minute=0))
                elif slot == OptimalTimeSlot.NIGHT:
                    suggestions.append(base_date.replace(hour=22, minute=0))
            
            # 現在時刻より後の時間のみを返す
            now = datetime.now()
            valid_suggestions = [
                suggestion for suggestion in suggestions
                if suggestion > now
            ]
            
            return valid_suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"最適な投稿時間の提案に失敗しました: {str(e)}")
            return []
    
    def create_recurring_schedule(
        self,
        post_template: str,
        schedule_config: ScheduleConfig
    ) -> List[PostSchedule]:
        """定期的なスケジュールを作成"""
        try:
            schedules = []
            current_date = schedule_config.start_time
            
            while (schedule_config.end_time is None or 
                   current_date <= schedule_config.end_time):
                
                # 曜日チェック
                if (schedule_config.days_of_week and 
                    current_date.weekday() not in schedule_config.days_of_week):
                    current_date += timedelta(days=1)
                    continue
                
                # 最適な時間を取得
                optimal_times = self.suggest_optimal_times(current_date)
                
                for optimal_time in optimal_times:
                    # 投稿を作成
                    post = self.post_manager.create_post_from_template(
                        post_template,
                        date=current_date.strftime("%Y-%m-%d")
                    )
                    
                    # スケジュールを作成
                    schedule = self.schedule_post(
                        post_id=post.id,
                        scheduled_time=optimal_time,
                        schedule_type=schedule_config.schedule_type
                    )
                    
                    schedules.append(schedule)
                    
                    # 1日の最大投稿数チェック
                    if len(schedules) >= schedule_config.max_posts_per_day:
                        break
                
                # 次の日付に移動
                if schedule_config.schedule_type == ScheduleType.DAILY:
                    current_date += timedelta(days=1)
                elif schedule_config.schedule_type == ScheduleType.WEEKLY:
                    current_date += timedelta(weeks=1)
                elif schedule_config.schedule_type == ScheduleType.MONTHLY:
                    # 月の加算（簡易版）
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
            
            logger.info(f"定期的なスケジュールを作成しました: {len(schedules)}件")
            return schedules
            
        except Exception as e:
            logger.error(f"定期的なスケジュールの作成に失敗しました: {str(e)}")
            raise SchedulerError(f"定期的なスケジュールの作成に失敗しました: {str(e)}")
    
    def update_config(self, **kwargs) -> None:
        """設定を更新"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            self.save_data()
            logger.info("スケジューラー設定を更新しました")
            
        except Exception as e:
            logger.error(f"スケジューラー設定の更新に失敗しました: {str(e)}")
            raise SchedulerError(f"スケジューラー設定の更新に失敗しました: {str(e)}")
    
    def get_config(self) -> ScheduleConfig:
        """設定を取得"""
        return self.config
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        try:
            total_schedules = len(self.schedules)
            pending_schedules = len([s for s in self.schedules.values() if s.status == "pending"])
            executed_schedules = len([s for s in self.schedules.values() if s.status == "executed"])
            failed_schedules = len([s for s in self.schedules.values() if s.status == "failed"])
            cancelled_schedules = len([s for s in self.schedules.values() if s.status == "cancelled"])
            
            # 今日のスケジュール数
            today = datetime.now().date()
            today_schedules = len([
                s for s in self.schedules.values()
                if s.scheduled_time.date() == today
            ])
            
            return {
                "total_schedules": total_schedules,
                "pending_schedules": pending_schedules,
                "executed_schedules": executed_schedules,
                "failed_schedules": failed_schedules,
                "cancelled_schedules": cancelled_schedules,
                "today_schedules": today_schedules,
                "success_rate": (executed_schedules / total_schedules * 100) if total_schedules > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"統計情報の取得に失敗しました: {str(e)}")
            return {}
    
    def _generate_schedule_id(self) -> str:
        """スケジュールIDを生成"""
        import uuid
        return str(uuid.uuid4())
    
    def _schedule_to_dict(self, schedule: PostSchedule) -> Dict[str, Any]:
        """PostScheduleオブジェクトを辞書に変換"""
        return {
            "id": schedule.id,
            "post_id": schedule.post_id,
            "scheduled_time": schedule.scheduled_time.isoformat(),
            "schedule_type": schedule.schedule_type.value if hasattr(schedule.schedule_type, 'value') else str(schedule.schedule_type),
            "status": schedule.status,
            "created_at": schedule.created_at.isoformat(),
            "executed_at": schedule.executed_at.isoformat() if schedule.executed_at else None,
            "error_message": schedule.error_message
        }
    
    def _dict_to_schedule(self, data: Dict[str, Any]) -> PostSchedule:
        """辞書をPostScheduleオブジェクトに変換"""
        return PostSchedule(
            id=data["id"],
            post_id=data["post_id"],
            scheduled_time=datetime.fromisoformat(data["scheduled_time"]),
            schedule_type=ScheduleType(data["schedule_type"]),
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            executed_at=datetime.fromisoformat(data["executed_at"]) if data.get("executed_at") else None,
            error_message=data.get("error_message")
        ) 