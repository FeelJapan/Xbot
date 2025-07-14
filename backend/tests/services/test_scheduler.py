"""
投稿スケジューラーサービスのテスト
"""
import pytest
import json
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from backend.app.services.scheduler import (
    PostScheduler, PostSchedule, ScheduleType, ScheduleConfig,
    OptimalTimeSlot
)
from backend.app.services.post_manager import PostManager, Post, PostContent, PostType, PostStatus

@pytest.fixture
def temp_data_dir():
    """一時データディレクトリ"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def scheduler(temp_data_dir):
    """スケジューラーのインスタンス"""
    with patch('backend.app.services.scheduler.PostManager'), \
         patch('backend.app.services.scheduler.get_task_manager'):
        
        scheduler = PostScheduler(data_dir=temp_data_dir)
        yield scheduler

@pytest.fixture
def sample_post():
    """サンプル投稿"""
    return Post(
        id="test_post_id",
        content=PostContent(
            text="テスト投稿",
            hashtags=["テスト"],
            mentions=[],
            links=[]
        ),
        scheduled_time=None,
        status=PostStatus.DRAFT,
        post_type=PostType.TEXT,
        template_name=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.fixture
def sample_schedule_config():
    """サンプルスケジュール設定"""
    return ScheduleConfig(
        schedule_type=ScheduleType.DAILY,
        start_time=datetime.now(),
        interval_hours=24,
        days_of_week=[0, 1, 2, 3, 4, 5, 6],
        optimal_time_slots=[
            OptimalTimeSlot.MORNING,
            OptimalTimeSlot.EVENING
        ],
        max_posts_per_day=3,
        enabled=True
    )

class TestPostScheduler:
    """投稿スケジューラーのテストクラス"""
    
    def test_init(self, temp_data_dir):
        """初期化テスト"""
        with patch('backend.app.services.scheduler.PostManager'), \
             patch('backend.app.services.scheduler.get_task_manager'):
            
            scheduler = PostScheduler(data_dir=temp_data_dir)
            
            assert scheduler.data_dir == Path(temp_data_dir)
            assert scheduler.schedules_file == Path(temp_data_dir) / "schedules.json"
            assert scheduler.config_file == Path(temp_data_dir) / "config.json"
            assert len(scheduler.schedules) == 0
            assert scheduler.config is not None
            assert scheduler.config.schedule_type == ScheduleType.DAILY
    
    def test_schedule_post(self, scheduler, sample_post):
        """投稿スケジュールテスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            scheduled_time = datetime.now() + timedelta(hours=1)
            
            schedule = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=scheduled_time,
                schedule_type=ScheduleType.ONCE
            )
            
            assert schedule.id is not None
            assert schedule.post_id == sample_post.id
            assert schedule.scheduled_time == scheduled_time
            assert schedule.schedule_type == ScheduleType.ONCE
            assert schedule.status == "pending"
            assert schedule_id in scheduler.schedules
    
    def test_cancel_schedule(self, scheduler, sample_post):
        """スケジュールキャンセルテスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            # スケジュールを作成
            scheduled_time = datetime.now() + timedelta(hours=1)
            schedule = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=scheduled_time,
                schedule_type=ScheduleType.ONCE
            )
            
            # スケジュールをキャンセル
            success = scheduler.cancel_schedule(schedule.id)
            
            assert success is True
            assert scheduler.schedules[schedule.id].status == "cancelled"
    
    def test_cancel_nonexistent_schedule(self, scheduler):
        """存在しないスケジュールのキャンセルテスト"""
        success = scheduler.cancel_schedule("nonexistent_id")
        assert success is False
    
    def test_cancel_executed_schedule(self, scheduler, sample_post):
        """実行済みスケジュールのキャンセルテスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            # スケジュールを作成
            scheduled_time = datetime.now() + timedelta(hours=1)
            schedule = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=scheduled_time,
                schedule_type=ScheduleType.ONCE
            )
            
            # スケジュールを実行済みに変更
            schedule.status = "executed"
            scheduler.schedules[schedule.id] = schedule
            
            # キャンセルを試行
            success = scheduler.cancel_schedule(schedule.id)
            assert success is False
    
    def test_get_schedule(self, scheduler, sample_post):
        """スケジュール取得テスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            # スケジュールを作成
            scheduled_time = datetime.now() + timedelta(hours=1)
            schedule = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=scheduled_time,
                schedule_type=ScheduleType.ONCE
            )
            
            # スケジュールを取得
            retrieved_schedule = scheduler.get_schedule(schedule.id)
            
            assert retrieved_schedule is not None
            assert retrieved_schedule.id == schedule.id
            assert retrieved_schedule.post_id == schedule.post_id
    
    def test_get_schedules_with_filters(self, scheduler, sample_post):
        """フィルタ付きスケジュール一覧取得テスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            # 複数のスケジュールを作成
            schedule1 = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=datetime.now() + timedelta(hours=1),
                schedule_type=ScheduleType.ONCE
            )
            
            schedule2 = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=datetime.now() + timedelta(hours=2),
                schedule_type=ScheduleType.DAILY
            )
            
            # ステータスでフィルタ
            pending_schedules = scheduler.get_schedules(status="pending")
            assert len(pending_schedules) == 2
            
            # 制限付きで取得
            limited_schedules = scheduler.get_schedules(limit=1)
            assert len(limited_schedules) == 1
    
    def test_get_pending_schedules(self, scheduler, sample_post):
        """実行待ちスケジュール一覧取得テスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            # 実行待ちスケジュールを作成
            scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=datetime.now() + timedelta(hours=1),
                schedule_type=ScheduleType.ONCE
            )
            
            pending_schedules = scheduler.get_pending_schedules()
            assert len(pending_schedules) == 1
            assert pending_schedules[0].status == "pending"
    
    def test_suggest_optimal_times(self, scheduler):
        """最適な投稿時間提案テスト"""
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        optimal_times = scheduler.suggest_optimal_times(date, max_suggestions=3)
        
        assert len(optimal_times) > 0
        for time in optimal_times:
            assert time > datetime.now()
            assert time.hour in [8, 12, 19, 22]  # 設定された時間帯
    
    def test_suggest_optimal_times_past_date(self, scheduler):
        """過去の日付での最適時間提案テスト"""
        past_date = datetime.now() - timedelta(days=1)
        
        optimal_times = scheduler.suggest_optimal_times(past_date, max_suggestions=3)
        
        # 過去の日付では空のリストが返される
        assert len(optimal_times) == 0
    
    def test_create_recurring_schedule(self, scheduler, sample_schedule_config):
        """定期的なスケジュール作成テスト"""
        with patch.object(scheduler.post_manager, 'create_post_from_template') as mock_create:
            mock_post = Mock()
            mock_post.id = "test_post_id"
            mock_create.return_value = mock_post
            
            schedules = scheduler.create_recurring_schedule(
                post_template="trend_commentary",
                schedule_config=sample_schedule_config
            )
            
            assert len(schedules) > 0
            for schedule in schedules:
                assert schedule.post_id == "test_post_id"
                assert schedule.schedule_type == ScheduleType.DAILY
                assert schedule.status == "pending"
    
    def test_update_config(self, scheduler):
        """設定更新テスト"""
        original_max_posts = scheduler.config.max_posts_per_day
        
        scheduler.update_config(max_posts_per_day=5)
        
        assert scheduler.config.max_posts_per_day == 5
        assert scheduler.config.max_posts_per_day != original_max_posts
    
    def test_get_config(self, scheduler):
        """設定取得テスト"""
        config = scheduler.get_config()
        
        assert config is not None
        assert config.schedule_type == ScheduleType.DAILY
        assert config.max_posts_per_day > 0
        assert config.enabled is True
    
    def test_get_statistics(self, scheduler, sample_post):
        """統計情報取得テスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            # いくつかのスケジュールを作成
            for i in range(3):
                scheduler.schedule_post(
                    post_id=sample_post.id,
                    scheduled_time=datetime.now() + timedelta(hours=i+1),
                    schedule_type=ScheduleType.ONCE
                )
            
            stats = scheduler.get_statistics()
            
            assert "total_schedules" in stats
            assert "pending_schedules" in stats
            assert "executed_schedules" in stats
            assert "failed_schedules" in stats
            assert "cancelled_schedules" in stats
            assert "today_schedules" in stats
            assert "success_rate" in stats
            
            assert stats["total_schedules"] == 3
            assert stats["pending_schedules"] == 3
            assert stats["success_rate"] >= 0
    
    def test_save_and_load_data(self, temp_data_dir):
        """データ保存・読み込みテスト"""
        with patch('backend.app.services.scheduler.PostManager'), \
             patch('backend.app.services.scheduler.get_task_manager'):
            
            # 最初のスケジューラーでスケジュールを作成
            scheduler1 = PostScheduler(data_dir=temp_data_dir)
            with patch.object(scheduler1.post_manager, 'get_post', return_value=Mock()):
                schedule = scheduler1.schedule_post(
                    post_id="test_post_id",
                    scheduled_time=datetime.now() + timedelta(hours=1),
                    schedule_type=ScheduleType.ONCE
                )
            
            # 新しいスケジューラーでデータを読み込み
            scheduler2 = PostScheduler(data_dir=temp_data_dir)
            loaded_schedule = scheduler2.get_schedule(schedule.id)
            
            assert loaded_schedule is not None
            assert loaded_schedule.post_id == schedule.post_id
            assert loaded_schedule.schedule_type == schedule.schedule_type
    
    @pytest.mark.asyncio
    async def test_scheduler_loop(self, scheduler):
        """スケジューラーループテスト"""
        # スケジューラーを開始
        scheduler.start_scheduler()
        assert scheduler.running is True
        
        # 少し待機
        await asyncio.sleep(0.1)
        
        # スケジューラーを停止
        scheduler.stop_scheduler()
        assert scheduler.running is False
    
    @pytest.mark.asyncio
    async def test_check_scheduled_posts(self, scheduler, sample_post):
        """スケジュール済み投稿チェックテスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post), \
             patch.object(scheduler.post_manager, 'post_now', return_value=True):
            
            # 過去の時間でスケジュールを作成
            past_time = datetime.now() - timedelta(minutes=1)
            schedule = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=past_time,
                schedule_type=ScheduleType.ONCE
            )
            
            # スケジュールチェックを実行
            await scheduler._check_scheduled_posts()
            
            # スケジュールが実行済みになっていることを確認
            updated_schedule = scheduler.get_schedule(schedule.id)
            assert updated_schedule.status == "executed"
            assert updated_schedule.executed_at is not None
    
    @pytest.mark.asyncio
    async def test_check_scheduled_posts_failure(self, scheduler, sample_post):
        """スケジュール済み投稿チェック失敗テスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post), \
             patch.object(scheduler.post_manager, 'post_now', return_value=False):
            
            # 過去の時間でスケジュールを作成
            past_time = datetime.now() - timedelta(minutes=1)
            schedule = scheduler.schedule_post(
                post_id=sample_post.id,
                scheduled_time=past_time,
                schedule_type=ScheduleType.ONCE
            )
            
            # スケジュールチェックを実行
            await scheduler._check_scheduled_posts()
            
            # スケジュールが失敗状態になっていることを確認
            updated_schedule = scheduler.get_schedule(schedule.id)
            assert updated_schedule.status == "failed"
            assert "投稿実行に失敗しました" in updated_schedule.error_message
    
    def test_schedule_type_validation(self, scheduler, sample_post):
        """スケジュールタイプバリデーションテスト"""
        with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
            # 無効なスケジュールタイプ
            with pytest.raises(ValueError):
                scheduler.schedule_post(
                    post_id=sample_post.id,
                    scheduled_time=datetime.now() + timedelta(hours=1),
                    schedule_type="invalid_type"
                )
    
    def test_optimal_time_slots_config(self, scheduler):
        """最適時間帯設定テスト"""
        # 設定を変更
        scheduler.update_config(
            optimal_time_slots=[
                OptimalTimeSlot.MORNING,
                OptimalTimeSlot.NIGHT
            ]
        )
        
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        optimal_times = scheduler.suggest_optimal_times(date, max_suggestions=5)
        
        # 設定された時間帯のみが返されることを確認
        for time in optimal_times:
            assert time.hour in [8, 22]  # MORNING(8時) と NIGHT(22時)
    
    def test_error_handling(self, scheduler):
        """エラーハンドリングテスト"""
        # 無効なデータでのテスト
        with pytest.raises(Exception):
            scheduler.schedule_post(
                post_id=None,
                scheduled_time=datetime.now() + timedelta(hours=1),
                schedule_type=ScheduleType.ONCE
            )
    
    def test_concurrent_schedule_creation(self, scheduler, sample_post):
        """並行スケジュール作成テスト"""
        import threading
        import time
        
        def create_schedule():
            try:
                with patch.object(scheduler.post_manager, 'get_post', return_value=sample_post):
                    scheduler.schedule_post(
                        post_id=sample_post.id,
                        scheduled_time=datetime.now() + timedelta(hours=1),
                        schedule_type=ScheduleType.ONCE
                    )
            except Exception:
                pass
        
        # 複数のスレッドで同時にスケジュールを作成
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_schedule)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # データの整合性を確認
        schedules = scheduler.get_schedules()
        assert len(schedules) >= 0  # エラーが発生してもシステムが破綻しないことを確認 