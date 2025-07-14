"""
Asynchronous task management for Xbot
"""
import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta
from .logging.logger import get_logger
from .error_handling.error_handler import handle_errors

logger = get_logger("async_tasks")

class AsyncTaskManager:
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.running = True
        self.lock = asyncio.Lock()
    
    async def start_task(
        self,
        name: str,
        coro: Callable,
        *args: Any,
        **kwargs: Any
    ) -> asyncio.Task:
        """非同期タスクを開始"""
        async with self.lock:
            if name in self.tasks and not self.tasks[name].done():
                logger.warning(f"Task {name} is already running")
                return self.tasks[name]
            
            task = asyncio.create_task(coro(*args, **kwargs))
            self.tasks[name] = task
            logger.info(f"Started task: {name}")
            return task
    
    async def stop_task(self, name: str) -> bool:
        """非同期タスクを停止"""
        async with self.lock:
            if name not in self.tasks:
                logger.warning(f"Task {name} not found")
                return False
            
            task = self.tasks[name]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            del self.tasks[name]
            logger.info(f"Stopped task: {name}")
            return True
    
    async def schedule_task(
        self,
        name: str,
        coro: Callable,
        interval: Union[int, float],
        *args: Any,
        **kwargs: Any
    ) -> None:
        """定期的なタスクをスケジュール"""
        async with self.lock:
            if name in self.scheduled_tasks:
                logger.warning(f"Scheduled task {name} already exists")
                return
            
            self.scheduled_tasks[name] = {
                "coro": coro,
                "interval": interval,
                "args": args,
                "kwargs": kwargs,
                "last_run": None
            }
            
            await self.start_task(name, self._run_scheduled_task, name)
            logger.info(f"Scheduled task: {name} (interval: {interval}s)")
    
    async def _run_scheduled_task(self, name: str) -> None:
        """スケジュールされたタスクを実行"""
        while self.running:
            try:
                task_info = self.scheduled_tasks[name]
                coro = task_info["coro"]
                args = task_info["args"]
                kwargs = task_info["kwargs"]
                
                await coro(*args, **kwargs)
                self.scheduled_tasks[name]["last_run"] = datetime.now()
                
                await asyncio.sleep(task_info["interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduled task {name}: {str(e)}")
                await asyncio.sleep(task_info["interval"])
    
    async def stop_all_tasks(self) -> None:
        """すべてのタスクを停止"""
        self.running = False
        async with self.lock:
            for name in list(self.tasks.keys()):
                await self.stop_task(name)
            self.scheduled_tasks.clear()
    
    def get_task_status(self, name: str) -> Optional[Dict[str, Any]]:
        """タスクの状態を取得"""
        if name in self.tasks:
            task = self.tasks[name]
            return {
                "running": not task.done(),
                "cancelled": task.cancelled(),
                "exception": task.exception() if task.done() else None
            }
        return None
    
    def get_all_task_statuses(self) -> Dict[str, Dict[str, Any]]:
        """すべてのタスクの状態を取得"""
        return {
            name: self.get_task_status(name)
            for name in self.tasks
        }

# シングルトンインスタンス
_task_manager_instance = None

def get_task_manager() -> AsyncTaskManager:
    """タスクマネージャーのインスタンスを取得"""
    global _task_manager_instance
    if _task_manager_instance is None:
        _task_manager_instance = AsyncTaskManager()
    return _task_manager_instance 